"""Non-destructive structural sanitizer for existing blind bundles.

The sanitizer copies a previously generated bundle into a new output directory,
re-evaluating every manifest artifact for a destination role/stage. It performs
only explicit structural transformations (copy, normalize filename, exclude),
recalculates hashes, validates the manifest, and runs the structural leak
checker before atomic publication. It never edits source bundles, interprets
text, runs OCR/LLMs, or performs semantic redaction.
"""

from __future__ import annotations

import re
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from yaml import YAMLError

from generator.artifact_visibility_policy import ArtifactVisibilityInput, PolicyReport, evaluate_artifact_visibility, evaluate_manifest_visibility
from generator.blind_bundle_generator import (
    MANIFEST_FILENAME,
    SCHEMA_VERSION,
    SEMANTIC_LIMITATIONS_ACKNOWLEDGED,
    _exclusion_category,
    _is_relative_to,
    _neutral_bundle_path,
    _output_contract,
    _publish_tmp_bundle,
    _sha256_file,
    _validate_manifest_schema,
    _visibility_policy,
    _write_manifest,
    ArtifactSpec,
)
from generator.blind_bundle_leak_checker import LeakCheckReport, LeakSeverity, check_blind_bundle

_NEUTRAL_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,63}$")


class BlindBundleSanitizeError(RuntimeError):
    """Raised when a bundle cannot be sanitized safely and atomically."""


@dataclass(frozen=True)
class BlindBundleSanitizeRequest:
    """Structured request for non-destructive bundle sanitization."""

    source_bundle_path: Path
    output_root: Path
    sanitized_bundle_id: str
    created_by: str
    role: str
    stage: str
    neutralize_paths: bool = False
    overwrite: bool = False
    allowed_transformations: tuple[str, ...] = ("copy", "normalize_filename", "exclude_artifact")
    created_at: str | None = None


@dataclass(frozen=True)
class BlindBundleSanitizeResult:
    """Structured result returned by :func:`sanitize_blind_bundle`."""

    source_bundle_path: Path
    output_path: Path
    manifest: dict[str, Any]
    leak_check_report: LeakCheckReport
    copied_count: int
    excluded_count: int
    transformation_count: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _PreparedManifestArtifact:
    artifact: dict[str, Any]
    source_path: Path
    source_relative_path: PurePosixPath
    target_relative_path: PurePosixPath
    source_hash: str
    policy_report: PolicyReport
    index: int


@dataclass(frozen=True)
class _CopiedManifestArtifact:
    prepared: _PreparedManifestArtifact
    target_hash: str


def sanitize_blind_bundle(request: BlindBundleSanitizeRequest) -> BlindBundleSanitizeResult:
    """Create a sanitized copy of an existing bundle without modifying it.

    The sanitizer loads and schema-validates the source manifest, audits the
    source bundle structurally, excludes artifacts denied by the destination
    visibility policy, copies only allowed/warned files, rebuilds a schema-valid
    manifest with recalculated hashes, runs the final leak checker, and publishes
    the temporary directory atomically.
    """

    _validate_request(request)
    source_bundle = Path(request.source_bundle_path)
    output_root = Path(request.output_root)
    _validate_source_bundle_root(source_bundle)
    source_bundle = source_bundle.resolve(strict=True)
    output_root.mkdir(parents=True, exist_ok=True)
    if output_root.is_symlink():
        raise BlindBundleSanitizeError("output_root must not be a symlink")
    output_root = output_root.resolve()

    output_path = _safe_output_dir(output_root, request.sanitized_bundle_id)
    _ensure_can_publish(output_path, request.overwrite)

    source_manifest = _load_and_validate_source_manifest(source_bundle)
    _validate_source_check(source_bundle)

    prepared = [_prepare_artifact(request, source_bundle, artifact, index) for index, artifact in enumerate(source_manifest["included_artifacts"], 1)]
    included = [artifact for artifact in prepared if artifact.policy_report.allowed]
    denied = [artifact for artifact in prepared if not artifact.policy_report.allowed]
    if not included:
        raise BlindBundleSanitizeError("sanitized bundle requires at least one policy-allowed artifact")

    tmp_dir = output_root / f".{request.sanitized_bundle_id}.tmp-{uuid.uuid4().hex}"
    copied: list[_CopiedManifestArtifact] = []
    final_manifest: dict[str, Any] | None = None
    leak_report: LeakCheckReport | None = None

    try:
        tmp_dir.mkdir(mode=0o700)
        for artifact in included:
            copied.append(_copy_artifact(tmp_dir, artifact))

        created_at = request.created_at or "1970-01-01T00:00:00Z"
        final_manifest = _build_manifest(request, source_manifest, copied, denied, created_at)
        manifest_policy_report = evaluate_manifest_visibility(final_manifest)
        final_manifest = _with_manifest_policy_results(final_manifest, manifest_policy_report)
        _validate_manifest_schema(final_manifest)
        if manifest_policy_report.denied_count:
            raise BlindBundleSanitizeError("sanitized manifest is denied by artifact visibility policy")

        _write_manifest(tmp_dir / MANIFEST_FILENAME, final_manifest)
        leak_report = _run_final_leak_check(tmp_dir)
        _publish_tmp_bundle(tmp_dir, output_path, request.overwrite)
        tmp_dir = Path()
    except Exception as exc:
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        if isinstance(exc, BlindBundleSanitizeError):
            raise
        raise BlindBundleSanitizeError(str(exc)) from exc

    assert final_manifest is not None
    assert leak_report is not None
    warnings = _unique_messages(_policy_warning_messages(included) + _leak_warning_messages(leak_report))
    return BlindBundleSanitizeResult(
        source_bundle_path=source_bundle,
        output_path=output_path,
        manifest=final_manifest,
        leak_check_report=leak_report,
        copied_count=len(copied),
        excluded_count=len(denied),
        transformation_count=len(final_manifest["transformations"]),
        warnings=warnings,
    )


def _validate_request(request: BlindBundleSanitizeRequest) -> None:
    _validate_neutral_id(request.sanitized_bundle_id, field_name="sanitized_bundle_id")
    allowed = set(request.allowed_transformations)
    supported = {"copy", "normalize_filename", "exclude_artifact"}
    if not allowed:
        raise BlindBundleSanitizeError("allowed_transformations must not be empty")
    unsupported = sorted(allowed - supported)
    if unsupported:
        raise BlindBundleSanitizeError(f"unsupported sanitizer transformations: {', '.join(unsupported)}")
    if request.neutralize_paths and "normalize_filename" not in allowed:
        raise BlindBundleSanitizeError("neutralize_paths requires normalize_filename transformation")
    if not request.neutralize_paths and "copy" not in allowed:
        raise BlindBundleSanitizeError("copy transformation is required when neutralize_paths is false")
    if "exclude_artifact" not in allowed:
        raise BlindBundleSanitizeError("exclude_artifact transformation must be allowed for policy-denied artifacts")


def _validate_source_bundle_root(source_bundle: Path) -> None:
    if source_bundle.is_symlink():
        raise BlindBundleSanitizeError("source_bundle_path must not be a symlink")
    if not source_bundle.exists():
        raise BlindBundleSanitizeError("source_bundle_path must exist")
    if not source_bundle.is_dir():
        raise BlindBundleSanitizeError("source_bundle_path must be a directory")


def _safe_output_dir(output_root: Path, bundle_id: str) -> Path:
    output_path = output_root / bundle_id
    resolved = output_path.resolve(strict=False)
    if not _is_relative_to(resolved, output_root):
        raise BlindBundleSanitizeError("sanitized_bundle_id escapes output_root")
    return output_path


def _ensure_can_publish(output_path: Path, overwrite: bool) -> None:
    if output_path.is_symlink():
        raise BlindBundleSanitizeError("existing sanitized bundle path must not be a symlink")
    if output_path.exists() and not overwrite:
        raise BlindBundleSanitizeError("sanitized output bundle already exists; pass overwrite=True to replace it")
    if output_path.exists() and not output_path.is_dir():
        raise BlindBundleSanitizeError("existing sanitized bundle path must be a directory")


def _load_and_validate_source_manifest(source_bundle: Path) -> dict[str, Any]:
    manifest_path = source_bundle / MANIFEST_FILENAME
    if manifest_path.is_symlink():
        raise BlindBundleSanitizeError("source manifest must not be a symlink")
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, YAMLError) as exc:
        raise BlindBundleSanitizeError(f"source manifest could not be loaded: {exc}") from exc
    if not isinstance(manifest, dict):
        raise BlindBundleSanitizeError("source manifest must be a YAML object")
    try:
        _validate_manifest_schema(manifest)
    except Exception as exc:
        raise BlindBundleSanitizeError(f"source manifest is invalid: {exc}") from exc
    return manifest


def _validate_source_check(source_bundle: Path) -> None:
    report = check_blind_bundle(source_bundle)
    fatal_codes = {issue.code for issue in report.issues if issue.severity in {LeakSeverity.ERROR, LeakSeverity.CRITICAL}}
    if "LEAK_HASH_MISMATCH" in fatal_codes:
        raise BlindBundleSanitizeError("source bundle has hash mismatch and cannot be sanitized")
    if "LEAK_UNDECLARED_FILE" in fatal_codes:
        raise BlindBundleSanitizeError("source bundle has undeclared files and cannot be sanitized")
    if "LEAK_FILE_SYMLINK" in fatal_codes:
        raise BlindBundleSanitizeError("source bundle contains symlink files and cannot be sanitized")
    if "LEAK_UNSAFE_MANIFEST_PATH" in fatal_codes:
        raise BlindBundleSanitizeError("source bundle has unsafe manifest paths and cannot be sanitized")
    tolerated = {"LEAK_MANIFEST_ISOLATION_FAILED", "LEAK_POLICY_DENIED_INCLUDED_ARTIFACT", "LEAK_MANIFEST_POLICY_CONTRADICTION"}
    remaining = sorted(fatal_codes - tolerated)
    if remaining:
        raise BlindBundleSanitizeError(f"source bundle failed structural leak check: {', '.join(remaining)}")


def _prepare_artifact(
    request: BlindBundleSanitizeRequest,
    source_bundle: Path,
    artifact: dict[str, Any],
    index: int,
) -> _PreparedManifestArtifact:
    source_relative = _validate_relative_posix_path(str(artifact.get("path") or ""), field_name="included_artifacts.path")
    source_path = source_bundle / Path(*source_relative.parts)
    _validate_source_artifact_path(source_bundle, source_path)
    source_hash = _sha256_file(source_path)
    if source_hash != artifact.get("hash"):
        raise BlindBundleSanitizeError("source bundle has hash mismatch and cannot be sanitized")

    target_relative = _neutral_bundle_path(str(source_relative), index) if request.neutralize_paths else source_relative
    _validate_relative_posix_path(str(target_relative), field_name="target artifact path")

    policy_report = evaluate_artifact_visibility(
        ArtifactVisibilityInput(
            role=request.role,
            stage=request.stage,
            artifact_id=str(artifact.get("artifact_id")),
            artifact_type=str(artifact.get("artifact_type")),
            visibility=str(artifact.get("visibility")),
            envelope_scope=str(artifact.get("envelope_scope")),
            contains_solution=_artifact_contains_solution(artifact),
            contains_future_envelopes=_artifact_contains_future(artifact),
            contains_private_author_notes=_artifact_contains_private_notes(artifact),
            contains_other_agents_outputs=_artifact_contains_other_agents(artifact),
        )
    )
    return _PreparedManifestArtifact(
        artifact=artifact,
        source_path=source_path,
        source_relative_path=source_relative,
        target_relative_path=target_relative,
        source_hash=source_hash,
        policy_report=policy_report,
        index=index,
    )


def _validate_source_artifact_path(source_bundle: Path, source_path: Path) -> None:
    if source_path.is_symlink():
        raise BlindBundleSanitizeError("source bundle contains symlink artifacts and cannot be sanitized")
    resolved = source_path.resolve(strict=False)
    if not _is_relative_to(resolved, source_bundle):
        raise BlindBundleSanitizeError("source manifest contains unsafe artifact path")
    if not source_path.exists() or not source_path.is_file():
        raise BlindBundleSanitizeError("source manifest declares a missing artifact file")


def _copy_artifact(tmp_dir: Path, artifact: _PreparedManifestArtifact) -> _CopiedManifestArtifact:
    target = tmp_dir / Path(*artifact.target_relative_path.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artifact.source_path, target, follow_symlinks=False)
    target_hash = _sha256_file(target)
    if target_hash != artifact.source_hash:
        raise BlindBundleSanitizeError("copied artifact hash does not match source hash")
    return _CopiedManifestArtifact(prepared=artifact, target_hash=target_hash)


def _build_manifest(
    request: BlindBundleSanitizeRequest,
    source_manifest: dict[str, Any],
    copied: list[_CopiedManifestArtifact],
    denied: list[_PreparedManifestArtifact],
    created_at: str,
) -> dict[str, Any]:
    transformations = [_transformation(copied_artifact, index, request.neutralize_paths) for index, copied_artifact in enumerate(copied, 1)]
    policy_warnings = [decision for artifact in copied for decision in artifact.prepared.policy_report.decisions if decision.severity == "warn"]
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": f"MANIFEST_{request.sanitized_bundle_id}",
        "run_id": str(source_manifest["run_id"]),
        "bundle_id": request.sanitized_bundle_id,
        "case_id": str(source_manifest["case_id"]),
        "case_version": str(source_manifest["case_version"]),
        "parent_manifest_id": str(source_manifest["manifest_id"]),
        "source_manifest_ids": [str(source_manifest["manifest_id"])],
        "created_at": created_at,
        "created_by": request.created_by,
        "role": request.role,
        "stage": request.stage,
        "bundle_context": {
            "purpose": "Sanitized non-destructive copy of an existing blind bundle.",
            "source_root": "source",
            "bundle_root": request.sanitized_bundle_id,
            "generated_by": request.created_by,
            "generated_at": created_at,
            "generation_mode": "scripted",
            "offline_safe": True,
        },
        "visibility_policy": _visibility_policy_for_copied(request.role, copied),
        "included_artifacts": [_included_artifact(artifact) for artifact in copied],
        "excluded_artifacts": [_excluded_artifact(artifact) for artifact in denied],
        "transformations": transformations,
        "output_contract": _output_contract(request.role),
        "isolation_check": _isolation_check(request, copied, denied, policy_warnings, created_at),
        "integrity": {
            "hash_algorithm": "sha256",
            "artifact_count": len(copied) + len(denied),
            "included_count": len(copied),
            "excluded_count": len(denied),
            "transformation_count": len(transformations),
        },
        "semantic_limitations_acknowledged": SEMANTIC_LIMITATIONS_ACKNOWLEDGED,
    }


def _included_artifact(copied: _CopiedManifestArtifact) -> dict[str, Any]:
    source = copied.prepared.artifact
    return {
        "artifact_id": source["artifact_id"],
        "path": str(copied.prepared.target_relative_path),
        "artifact_type": source["artifact_type"],
        "visibility": source["visibility"],
        "envelope_scope": source["envelope_scope"],
        "hash": copied.target_hash,
        "hash_algorithm": "sha256",
        "source_role": source["source_role"],
        "included_reason": source["included_reason"],
    }


def _excluded_artifact(artifact: _PreparedManifestArtifact) -> dict[str, Any]:
    spec = _artifact_spec_from_manifest_artifact(artifact.artifact, artifact.source_relative_path)
    decision = artifact.policy_report.decisions[0]
    category = _exclusion_category(spec, decision.matched_conditions)
    excluded = {
        "path": str(artifact.source_relative_path),
        "artifact_type": artifact.artifact["artifact_type"],
        "visibility": artifact.artifact["visibility"],
        "exclusion_reason": decision.reason,
        "exclusion_category": category,
    }
    if category == "other":
        excluded["exclusion_notes"] = f"Denied by visibility policy rule {decision.rule_id}."
    return excluded


def _transformation(copied: _CopiedManifestArtifact, index: int, neutralized: bool) -> dict[str, Any]:
    transformation_type = "normalize_filename" if neutralized else "copy"
    description = (
        "Copied the artifact byte-for-byte while replacing the bundle path with a neutral filename."
        if neutralized
        else "Copied the artifact byte-for-byte without changing player-visible content."
    )
    return {
        "transformation_id": f"TRANSFORMATION_{index:03d}",
        "type": transformation_type,
        "source_path": f"source/{copied.prepared.source_relative_path}",
        "target_path": f"bundle/{copied.prepared.target_relative_path}",
        "description": description,
        "preserves_player_visible_content": True,
        "hash_before": copied.prepared.source_hash,
        "hash_after": copied.target_hash,
    }


def _visibility_policy_for_copied(role: str, copied: list[_CopiedManifestArtifact]) -> dict[str, Any]:
    generator_copied = []
    for item in copied:
        spec = _artifact_spec_from_manifest_artifact(item.prepared.artifact, item.prepared.target_relative_path)
        prepared = type("Prepared", (), {"spec": spec})()
        generator_copied.append(type("Copied", (), {"prepared": prepared})())
    # The generator helper only reads copied[*].prepared.spec fields.
    return _visibility_policy(role, generator_copied)  # type: ignore[arg-type]


def _isolation_check(
    request: BlindBundleSanitizeRequest,
    copied: list[_CopiedManifestArtifact],
    denied: list[_PreparedManifestArtifact],
    policy_warnings: list[Any],
    created_at: str,
) -> dict[str, Any]:
    status = "passed_with_warnings" if policy_warnings else "passed"
    checks = [
        _check("CHECK_SOURCE_BUNDLE_AUDITED", "passed", "Ran the structural leak checker on the source bundle before sanitization.", "Fatal source hash, symlink, unsafe path, and undeclared-file issues are rejected."),
        _check("CHECK_POLICY_VISIBILITY_ALLOWED", "passed", "Applied artifact_visibility_policy to each source manifest artifact for the destination role and stage.", "Denied artifacts are excluded from the sanitized bundle."),
        _check("CHECK_NON_DESTRUCTIVE_COPY", "passed", "Copied included artifacts into a temporary output directory without editing source files.", "The sanitizer only writes inside output_root and publishes atomically."),
        _check("CHECK_COPIED_HASH_RECORDED", "passed", "Recalculated sha256 hashes for every included copied artifact.", "hash_before references source content and hash_after references sanitized output content."),
        _check("CHECK_MANIFEST_SCHEMA_VALID", "passed", "Validated sanitized manifest against schemas/blind_bundle_manifest.schema.yaml before publication.", "Draft202012Validator with FormatChecker is run before leak checking and publication."),
        _check("CHECK_FINAL_LEAK_CHECK", "passed", "Ran the structural leak checker on the sanitized bundle before publication.", "Invalid final bundles are not published."),
    ]
    isolation: dict[str, Any] = {"status": status, "checked_at": created_at, "checked_by": request.created_by, "checks": checks}
    if policy_warnings:
        isolation["warnings"] = [_warning(decision, artifact.prepared.artifact["artifact_id"], index) for index, (decision, artifact) in enumerate(_warning_pairs(copied), 1)]
    return isolation


def _check(check_id: str, status: str, description: str, evidence: str) -> dict[str, str]:
    return {"check_id": check_id, "status": status, "description": description, "evidence": evidence}


def _warning(decision: Any, artifact_id: str, index: int) -> dict[str, Any]:
    return {
        "warning_id": f"WARNING_{index:03d}",
        "category": decision.rule_id,
        "description": decision.reason,
        "affected_artifact_ids": [artifact_id],
        "recommended_action": decision.recommended_action,
    }


def _warning_pairs(copied: list[_CopiedManifestArtifact]) -> list[tuple[Any, _CopiedManifestArtifact]]:
    pairs = []
    for artifact in copied:
        for decision in artifact.prepared.policy_report.decisions:
            if decision.severity == "warn":
                pairs.append((decision, artifact))
    return pairs


def _with_manifest_policy_results(manifest: dict[str, Any], report: PolicyReport) -> dict[str, Any]:
    if report.warning_count == 0 and report.denied_count == 0:
        return manifest
    updated = dict(manifest)
    isolation = dict(manifest["isolation_check"])
    warnings = list(isolation.get("warnings", []))
    issues = list(isolation.get("issues", []))
    for decision in report.decisions:
        if decision.severity == "warn" and not any(warning.get("category") == decision.rule_id for warning in warnings):
            warnings.append(
                {
                    "warning_id": f"WARNING_MANIFEST_{len(warnings) + 1:03d}",
                    "category": decision.rule_id,
                    "description": decision.reason,
                    "affected_artifact_ids": [],
                    "recommended_action": decision.recommended_action,
                }
            )
        if decision.severity == "deny":
            issues.append(
                {
                    "issue_id": f"ISSUE_MANIFEST_{len(issues) + 1:03d}",
                    "severity": "critical",
                    "category": decision.rule_id,
                    "description": decision.reason,
                    "affected_artifact_ids": ["MANIFEST_POLICY"],
                    "recommended_action": decision.recommended_action,
                }
            )
    if issues:
        isolation["status"] = "failed"
        isolation["issues"] = issues
    elif warnings and isolation["status"] == "passed":
        isolation["status"] = "passed_with_warnings"
    if warnings:
        isolation["warnings"] = warnings
    updated["isolation_check"] = isolation
    return updated


def _run_final_leak_check(bundle_path: Path) -> LeakCheckReport:
    report = check_blind_bundle(bundle_path)
    if not report.valid:
        codes = ", ".join(sorted({issue.code for issue in report.issues if issue.severity in {LeakSeverity.ERROR, LeakSeverity.CRITICAL}}))
        raise BlindBundleSanitizeError(f"sanitized bundle failed final leak check: {codes}")
    return report


def _validate_neutral_id(value: str, *, field_name: str) -> None:
    if not _NEUTRAL_ID_RE.fullmatch(value):
        raise BlindBundleSanitizeError(f"{field_name} must be a schema-compatible neutral id")
    if len(f"MANIFEST_{value}") > 64:
        raise BlindBundleSanitizeError(f"{field_name} is too long to derive a schema-compatible manifest_id")


def _validate_relative_posix_path(value: str, *, field_name: str) -> PurePosixPath:
    if not value:
        raise BlindBundleSanitizeError(f"{field_name} must not be empty")
    if "\\" in value:
        raise BlindBundleSanitizeError(f"{field_name} must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise BlindBundleSanitizeError(f"{field_name} must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise BlindBundleSanitizeError(f"{field_name} must not contain empty, current, or parent segments")
    return path


def _artifact_spec_from_manifest_artifact(artifact: dict[str, Any], path: PurePosixPath) -> ArtifactSpec:
    return ArtifactSpec(
        artifact_id=str(artifact["artifact_id"]),
        source_path=str(path),
        bundle_path=str(path),
        artifact_type=str(artifact["artifact_type"]),
        visibility=str(artifact["visibility"]),
        envelope_scope=str(artifact["envelope_scope"]),
        source_role=str(artifact["source_role"]),
        included_reason=str(artifact["included_reason"]),
        contains_solution=_artifact_contains_solution(artifact),
        contains_future_envelopes=_artifact_contains_future(artifact),
        contains_private_author_notes=_artifact_contains_private_notes(artifact),
        contains_other_agents_outputs=_artifact_contains_other_agents(artifact),
    )


def _artifact_contains_solution(artifact: dict[str, Any]) -> bool:
    return artifact.get("artifact_type") in {"solution", "answer_key"}


def _artifact_contains_future(artifact: dict[str, Any]) -> bool:
    return artifact.get("envelope_scope") == "future_envelopes"


def _artifact_contains_private_notes(artifact: dict[str, Any]) -> bool:
    return artifact.get("visibility") == "private_author"


def _artifact_contains_other_agents(artifact: dict[str, Any]) -> bool:
    return artifact.get("source_role") not in {"author", "human_operator", "system", "unknown"}


def _policy_warning_messages(included: list[_PreparedManifestArtifact]) -> list[str]:
    return [decision.reason for artifact in included for decision in artifact.policy_report.decisions if decision.severity == "warn"]


def _leak_warning_messages(report: LeakCheckReport) -> list[str]:
    return [issue.message for issue in report.issues if issue.severity == LeakSeverity.WARNING]


def _unique_messages(messages: list[str]) -> list[str]:
    unique: list[str] = []
    for message in messages:
        if message not in unique:
            unique.append(message)
    return unique

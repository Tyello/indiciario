"""Manual, deterministic blind bundle generator.

This module builds role-scoped blind bundles from an explicit list of artifact
specifications. It performs only structural operations: path validation, policy
evaluation from supplied metadata, byte-for-byte copies, sha256 hashing, manifest
assembly, schema validation, and atomic publication. It never executes an LLM,
infers semantic content, sanitizes text, or discovers files automatically.
"""

from __future__ import annotations

import hashlib
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.artifact_visibility_policy import (
    ArtifactVisibilityInput,
    PolicyReport,
    evaluate_artifact_visibility,
    evaluate_manifest_visibility,
)

SCHEMA_VERSION = "1.0"
MANIFEST_FILENAME = "blind_bundle_manifest.yaml"
SEMANTIC_LIMITATIONS_ACKNOWLEDGED = [
    "artifact_paths_exist",
    "artifact_hashes_match_file_content",
    "manifest_hash_matches_content",
    "role_visibility_matrix_complete",
    "allowed_and_prohibited_categories_do_not_overlap",
    "transformation_hash_chain_valid",
    "source_artifacts_exist",
    "target_artifacts_exist",
    "isolation_check_was_actually_run",
    "no_semantic_solution_leak",
    "no_filename_based_solution_leak",
    "no_metadata_leak",
    "no_future_envelope_semantic_leak",
    "output_contract_enforced_by_runner",
    "bundle_root_exists",
    "role_instructions_exist",
    "artifact_count_matches_lists",
    "transformations_are_non_destructive",
    "manifest_id_unique",
    "bundle_id_unique",
    "run_id_exists",
]

ALL_VISIBILITY_CATEGORIES = [
    "public_player",
    "private_author",
    "review_private",
    "facilitator",
    "derived_report",
    "playtest_anonymized",
    "technical_metadata",
]


class BlindBundleBuildError(RuntimeError):
    """Raised when a blind bundle cannot be safely generated."""


@dataclass(frozen=True)
class ArtifactSpec:
    """Explicit artifact metadata supplied by the human/operator."""

    artifact_id: str
    source_path: str
    bundle_path: str | None
    artifact_type: str
    visibility: str
    envelope_scope: str
    source_role: str
    included_reason: str
    contains_solution: bool = False
    contains_future_envelopes: bool = False
    contains_private_author_notes: bool = False
    contains_other_agents_outputs: bool = False


@dataclass(frozen=True)
class BlindBundleBuildRequest:
    """Structured input for building one manual blind bundle."""

    manifest_id: str
    run_id: str
    bundle_id: str
    case_id: str
    case_version: str
    role: str
    stage: str
    source_root: Path
    output_root: Path
    created_by: str
    artifact_specs: list[ArtifactSpec]
    generation_mode: str = "manual"
    offline_safe: bool = True
    neutralize_paths: bool = False
    overwrite: bool = False
    created_at: str | None = None


@dataclass(frozen=True)
class BlindBundleBuildResult:
    """Testable build report returned by :func:`build_blind_bundle`."""

    manifest: dict[str, Any]
    policy_report: PolicyReport
    output_path: Path
    included_count: int
    excluded_count: int
    copied_files: list[Path] = field(default_factory=list)
    denied_files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _PreparedArtifact:
    spec: ArtifactSpec
    source_path: Path
    bundle_path: PurePosixPath
    policy_report: PolicyReport


@dataclass(frozen=True)
class _CopiedArtifact:
    prepared: _PreparedArtifact
    sha256: str


def build_blind_bundle(request: BlindBundleBuildRequest) -> BlindBundleBuildResult:
    """Build one blind bundle from explicitly listed artifact specs.

    The function validates all declared paths, evaluates artifact visibility via
    ``artifact_visibility_policy``, copies only allowed/warned artifacts, writes a
    schema-valid ``blind_bundle_manifest.yaml``, and publishes the final bundle
    atomically from a temporary directory under ``output_root``.
    """

    _validate_request(request)
    source_root = request.source_root.resolve(strict=True)
    output_root = request.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if output_root.is_symlink():
        raise BlindBundleBuildError("output_root must not be a symlink")

    bundle_dir = _safe_bundle_dir(output_root, request.bundle_id)
    _ensure_can_publish(bundle_dir, request.overwrite)

    prepared = [_prepare_artifact(request, source_root, output_root, spec, index) for index, spec in enumerate(request.artifact_specs, 1)]
    included = [artifact for artifact in prepared if artifact.policy_report.allowed]
    denied = [artifact for artifact in prepared if not artifact.policy_report.allowed]
    if not included:
        raise BlindBundleBuildError("blind bundle requires at least one policy-allowed artifact")

    tmp_dir = output_root / f".{request.bundle_id}.tmp-{uuid.uuid4().hex}"
    copied: list[_CopiedArtifact] = []
    manifest: dict[str, Any] | None = None

    try:
        tmp_dir.mkdir(mode=0o700)
        for artifact in included:
            copied.append(_copy_artifact(tmp_dir, artifact))

        manifest = _build_manifest(request, copied, denied, _created_at(request))
        manifest_policy_report = evaluate_manifest_visibility(manifest)
        manifest = _with_manifest_policy_results(manifest, manifest_policy_report)
        _validate_manifest_schema(manifest)
        if manifest_policy_report.denied_count:
            raise BlindBundleBuildError("generated manifest is denied by artifact visibility policy")

        _write_manifest(tmp_dir / MANIFEST_FILENAME, manifest)
        _publish_tmp_bundle(tmp_dir, bundle_dir, request.overwrite)
        tmp_dir = Path()
        policy_report = manifest_policy_report
    except Exception:
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        raise

    copied_paths = [Path(str(artifact.prepared.bundle_path)) for artifact in copied]
    denied_paths = [Path(str(artifact.bundle_path)) for artifact in denied]
    warnings = _unique_messages(_warning_messages(included) + _warning_messages_from_manifest(policy_report))
    assert manifest is not None
    return BlindBundleBuildResult(
        manifest=manifest,
        policy_report=policy_report,
        output_path=bundle_dir,
        included_count=len(copied),
        excluded_count=len(denied),
        copied_files=copied_paths,
        denied_files=denied_paths,
        warnings=warnings,
    )


def _validate_request(request: BlindBundleBuildRequest) -> None:
    if not request.artifact_specs:
        raise BlindBundleBuildError("artifact_specs must contain at least one artifact")
    _validate_relative_posix_path(request.bundle_id, field_name="bundle_id")
    if request.generation_mode not in {"manual", "scripted", "mixed"}:
        raise BlindBundleBuildError("generation_mode must match the blind bundle manifest vocabulary")
    if not request.offline_safe:
        raise BlindBundleBuildError("blind bundle generator only supports offline_safe requests")


def _created_at(request: BlindBundleBuildRequest) -> str:
    if request.created_at:
        return request.created_at
    return "1970-01-01T00:00:00Z"


def _prepare_artifact(
    request: BlindBundleBuildRequest,
    source_root: Path,
    output_root: Path,
    spec: ArtifactSpec,
    index: int,
) -> _PreparedArtifact:
    relative_source = _validate_relative_posix_path(spec.source_path, field_name="source_path")
    source_path = source_root / Path(*relative_source.parts)
    _validate_source_file(source_root, source_path)

    if request.neutralize_paths:
        relative_bundle = _neutral_bundle_path(spec.source_path, index)
    else:
        if not spec.bundle_path:
            raise BlindBundleBuildError("bundle_path is required when neutralize_paths is false")
        relative_bundle = _validate_relative_posix_path(spec.bundle_path, field_name="bundle_path")
    _validate_output_file_path(output_root, request.bundle_id, relative_bundle)

    policy_report = evaluate_artifact_visibility(
        ArtifactVisibilityInput(
            role=request.role,
            stage=request.stage,
            artifact_id=spec.artifact_id,
            artifact_type=spec.artifact_type,
            visibility=spec.visibility,
            envelope_scope=spec.envelope_scope,
            contains_solution=spec.contains_solution,
            contains_future_envelopes=spec.contains_future_envelopes,
            contains_private_author_notes=spec.contains_private_author_notes,
            contains_other_agents_outputs=spec.contains_other_agents_outputs,
        )
    )
    return _PreparedArtifact(spec=spec, source_path=source_path, bundle_path=relative_bundle, policy_report=policy_report)


def _validate_relative_posix_path(value: str, *, field_name: str) -> PurePosixPath:
    if not value:
        raise BlindBundleBuildError(f"{field_name} must not be empty")
    if "\\" in value:
        raise BlindBundleBuildError(f"{field_name} must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise BlindBundleBuildError(f"{field_name} must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise BlindBundleBuildError(f"{field_name} must not contain empty, current, or parent segments")
    return path


def _validate_source_file(source_root: Path, source_path: Path) -> None:
    if source_path.is_symlink():
        raise BlindBundleBuildError("source_path must not be a symlink")
    if not source_path.exists():
        raise BlindBundleBuildError("source_path must exist")
    if not source_path.is_file():
        raise BlindBundleBuildError("source_path must be a file")
    resolved_source = source_path.resolve(strict=True)
    if not _is_relative_to(resolved_source, source_root):
        raise BlindBundleBuildError("source_path escapes source_root")


def _validate_output_file_path(output_root: Path, bundle_id: str, relative_bundle: PurePosixPath) -> None:
    target = output_root / bundle_id / Path(*relative_bundle.parts)
    resolved_parent = target.parent.resolve(strict=False)
    bundle_dir = (output_root / bundle_id).resolve(strict=False)
    if not _is_relative_to(resolved_parent, bundle_dir):
        raise BlindBundleBuildError("bundle_path escapes bundle directory")


def _safe_bundle_dir(output_root: Path, bundle_id: str) -> Path:
    bundle_dir = output_root / bundle_id
    resolved = bundle_dir.resolve(strict=False)
    if not _is_relative_to(resolved, output_root):
        raise BlindBundleBuildError("bundle_id escapes output_root")
    return bundle_dir


def _ensure_can_publish(bundle_dir: Path, overwrite: bool) -> None:
    if bundle_dir.is_symlink():
        raise BlindBundleBuildError("existing bundle path must not be a symlink")
    if bundle_dir.exists() and not overwrite:
        raise BlindBundleBuildError("output bundle already exists; pass overwrite=True to replace it")
    if bundle_dir.exists() and not bundle_dir.is_dir():
        raise BlindBundleBuildError("existing bundle path must be a directory")


def _copy_artifact(tmp_dir: Path, artifact: _PreparedArtifact) -> _CopiedArtifact:
    target = tmp_dir / Path(*artifact.bundle_path.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artifact.source_path, target, follow_symlinks=False)
    source_hash = _sha256_file(artifact.source_path)
    target_hash = _sha256_file(target)
    if source_hash != target_hash:
        raise BlindBundleBuildError("copied artifact hash does not match source hash")
    return _CopiedArtifact(prepared=artifact, sha256=target_hash)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_manifest(
    request: BlindBundleBuildRequest,
    copied: list[_CopiedArtifact],
    denied: list[_PreparedArtifact],
    created_at: str,
) -> dict[str, Any]:
    included_artifacts = [_included_artifact(copied_artifact) for copied_artifact in copied]
    excluded_artifacts = [_excluded_artifact(artifact) for artifact in denied]
    transformations = [_transformation(copied_artifact, index, request.neutralize_paths) for index, copied_artifact in enumerate(copied, 1)]
    policy_warnings = [decision for artifact in copied for decision in artifact.prepared.policy_report.decisions if decision.severity == "warn"]
    isolation = _isolation_check(request, copied, denied, policy_warnings, created_at)

    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": request.manifest_id,
        "run_id": request.run_id,
        "bundle_id": request.bundle_id,
        "case_id": request.case_id,
        "case_version": request.case_version,
        "created_at": created_at,
        "created_by": request.created_by,
        "role": request.role,
        "stage": request.stage,
        "bundle_context": {
            "purpose": "Prepare explicit artifacts for a role-scoped blind bundle.",
            "source_root": "source",
            "bundle_root": request.bundle_id,
            "generated_by": request.created_by,
            "generated_at": created_at,
            "generation_mode": request.generation_mode,
            "offline_safe": request.offline_safe,
        },
        "visibility_policy": _visibility_policy(request.role, copied),
        "included_artifacts": included_artifacts,
        "excluded_artifacts": excluded_artifacts,
        "transformations": transformations,
        "output_contract": _output_contract(request.role),
        "isolation_check": isolation,
        "integrity": {
            "hash_algorithm": "sha256",
            "artifact_count": len(copied) + len(denied),
            "included_count": len(copied),
            "excluded_count": len(denied),
            "transformation_count": len(transformations),
        },
        "semantic_limitations_acknowledged": SEMANTIC_LIMITATIONS_ACKNOWLEDGED,
    }


def _included_artifact(copied_artifact: _CopiedArtifact) -> dict[str, Any]:
    spec = copied_artifact.prepared.spec
    return {
        "artifact_id": spec.artifact_id,
        "path": str(copied_artifact.prepared.bundle_path),
        "artifact_type": spec.artifact_type,
        "visibility": spec.visibility,
        "envelope_scope": spec.envelope_scope,
        "hash": copied_artifact.sha256,
        "hash_algorithm": "sha256",
        "source_role": spec.source_role,
        "included_reason": spec.included_reason,
    }


def _excluded_artifact(artifact: _PreparedArtifact) -> dict[str, Any]:
    decision = artifact.policy_report.decisions[0]
    category = _exclusion_category(artifact.spec, decision.matched_conditions)
    excluded = {
        "path": str(artifact.bundle_path),
        "artifact_type": artifact.spec.artifact_type,
        "visibility": artifact.spec.visibility,
        "exclusion_reason": decision.reason,
        "exclusion_category": category,
    }
    if category == "other":
        excluded["exclusion_notes"] = f"Denied by visibility policy rule {decision.rule_id}."
    return excluded


def _exclusion_category(spec: ArtifactSpec, matched_conditions: list[str]) -> str:
    if spec.artifact_type in {"solution", "answer_key"} or spec.contains_solution:
        return "solution_leak"
    if spec.contains_future_envelopes or spec.envelope_scope == "future_envelopes":
        return "future_envelope"
    if spec.visibility == "private_author" or spec.contains_private_author_notes:
        return "private_author"
    if spec.visibility == "facilitator" or spec.artifact_type == "facilitator_guide":
        return "facilitator_only"
    if spec.contains_other_agents_outputs or "contains_other_agents_outputs=true" in matched_conditions:
        return "other_agent_output"
    if spec.visibility == "technical_metadata":
        return "unsafe_metadata"
    if spec.visibility in {"review_private", "playtest_anonymized"}:
        return "out_of_scope"
    return "other"


def _transformation(copied_artifact: _CopiedArtifact, index: int, neutralized: bool) -> dict[str, Any]:
    source = str(copied_artifact.prepared.spec.source_path)
    target = str(copied_artifact.prepared.bundle_path)
    transformation_type = "normalize_filename" if neutralized else "copy"
    description = (
        "Copied the artifact byte-for-byte while replacing the requested path with a neutral filename."
        if neutralized
        else "Copied the artifact byte-for-byte without changing player-visible content."
    )
    return {
        "transformation_id": f"TRANSFORMATION_{index:03d}",
        "type": transformation_type,
        "source_path": f"source/{source}",
        "target_path": f"bundle/{target}",
        "description": description,
        "preserves_player_visible_content": True,
        "hash_before": copied_artifact.sha256,
        "hash_after": copied_artifact.sha256,
    }


def _visibility_policy(role: str, copied: list[_CopiedArtifact]) -> dict[str, Any]:
    included_categories = sorted({artifact.prepared.spec.visibility for artifact in copied})
    contains_solution = any(artifact.prepared.spec.contains_solution for artifact in copied)
    contains_future = any(artifact.prepared.spec.contains_future_envelopes for artifact in copied)
    contains_private = any(artifact.prepared.spec.contains_private_author_notes for artifact in copied)
    contains_other_agents = any(artifact.prepared.spec.contains_other_agents_outputs for artifact in copied)

    if role == "blind_solver":
        allowed = [category for category in ["public_player", "derived_report"] if category in included_categories]
        if not allowed:
            allowed = ["public_player"]
        prohibited = ["private_author", "facilitator", "review_private", "playtest_anonymized", "technical_metadata"]
        return {
            "allowed_categories": allowed,
            "prohibited_categories": prohibited,
            "allow_solution": False,
            "allow_future_envelopes": False,
            "allow_private_notes": False,
            "allow_other_agents_outputs": False,
            "allow_source_metadata": False,
            "contains_solution": False,
            "contains_future_envelopes": False,
            "contains_private_author_notes": False,
            "contains_other_agents_outputs": False,
            "rationale": "Blind solver bundles are restricted to structurally safe player-visible or sanitized derived artifacts.",
        }

    prohibited = [category for category in ALL_VISIBILITY_CATEGORIES if category not in included_categories]
    if not prohibited:
        prohibited = ["technical_metadata"]
    return {
        "allowed_categories": included_categories or ["public_player"],
        "prohibited_categories": prohibited,
        "allow_solution": contains_solution or role in {"facilitator", "gate_evaluator", "human_operator"},
        "allow_future_envelopes": contains_future or role in {"facilitator", "gate_evaluator", "human_operator"},
        "allow_private_notes": contains_private or role in {"facilitator", "gate_evaluator", "human_operator"},
        "allow_other_agents_outputs": contains_other_agents or role in {"gate_evaluator", "human_operator"},
        "allow_source_metadata": role in {"technical_reviewer", "human_operator"},
        "contains_solution": contains_solution,
        "contains_future_envelopes": contains_future,
        "contains_private_author_notes": contains_private,
        "contains_other_agents_outputs": contains_other_agents,
        "rationale": "Policy summary is derived from artifacts allowed by the explicit visibility policy evaluation.",
    }


def _output_contract(role: str) -> dict[str, Any]:
    if role == "blind_solver":
        return {
            "expected_output_type": "blind_solution",
            "required_sections": ["facts", "hypotheses", "answer"],
            "prohibited_content": ["solution", "future_envelopes", "private_author_notes", "other_agents_outputs"],
            "must_not_reveal": ["solution", "future_envelopes", "private_author_notes", "other_agents_outputs"],
            "output_visibility": "derived_report",
            "instructions": "Return a blind solution using only the bundled artifacts and do not reveal prohibited material.",
        }
    if role == "gate_evaluator":
        return {
            "expected_output_type": "gate_decision",
            "required_sections": ["findings", "rationale", "decision"],
            "prohibited_content": ["personal_data"],
            "must_not_reveal": ["personal_data"],
            "output_visibility": "review_private",
            "instructions": "Return a private gate decision grounded only in the provided bundle artifacts.",
        }
    return {
        "expected_output_type": "review_report",
        "required_sections": ["findings", "rationale", "recommendations"],
        "prohibited_content": ["personal_data"],
        "must_not_reveal": ["personal_data"],
        "output_visibility": "review_private" if role != "human_operator" else "derived_report",
        "instructions": "Return a concise review report using only the explicitly bundled artifacts.",
    }


def _isolation_check(
    request: BlindBundleBuildRequest,
    copied: list[_CopiedArtifact],
    denied: list[_PreparedArtifact],
    policy_warnings: list[Any],
    created_at: str,
) -> dict[str, Any]:
    status = "failed" if denied else "passed_with_warnings" if policy_warnings else "passed"
    checks = [
        _check("CHECK_NO_SYMLINK_SOURCE", "passed", "Confirmed listed source artifacts are not symlinks.", "Each source path was checked with Path.is_symlink before copying."),
        _check("CHECK_SAFE_SOURCE_PATH", "passed", "Confirmed source paths are relative POSIX paths inside source_root.", "Absolute paths, parent traversal, backslashes, missing files, and directories are rejected."),
        _check("CHECK_SAFE_BUNDLE_PATH", "passed", "Confirmed bundle paths are relative POSIX paths inside the bundle root.", "Bundle target parents are resolved and checked for containment under the bundle directory."),
        _check("CHECK_POLICY_VISIBILITY_ALLOWED", "failed" if denied else "passed", "Applied artifact_visibility_policy to every explicit artifact spec.", "Denied artifacts are excluded from included_artifacts and copied files."),
        _check("CHECK_COPIED_HASH_RECORDED", "passed", "Recorded sha256 hashes for every copied artifact.", "Each copied artifact has matching hash_before, hash_after, and included_artifacts hash values."),
        _check("CHECK_MANIFEST_SCHEMA_VALID", "passed", "Validated generated manifest against schemas/blind_bundle_manifest.schema.yaml.", "Draft202012Validator with FormatChecker is run before bundle publication."),
    ]
    isolation: dict[str, Any] = {
        "status": status,
        "checked_at": created_at,
        "checked_by": request.created_by,
        "checks": checks,
    }
    if denied:
        isolation["issues"] = [_issue(artifact, index) for index, artifact in enumerate(denied, 1)]
    if policy_warnings:
        isolation["warnings"] = [_warning(decision, copied_artifact.prepared.spec.artifact_id, index) for index, (decision, copied_artifact) in enumerate(_warning_pairs(copied), 1)]
    return isolation


def _check(check_id: str, status: str, description: str, evidence: str) -> dict[str, str]:
    return {"check_id": check_id, "status": status, "description": description, "evidence": evidence}


def _issue(artifact: _PreparedArtifact, index: int) -> dict[str, Any]:
    decision = artifact.policy_report.decisions[0]
    return {
        "issue_id": f"ISSUE_{index:03d}",
        "severity": "high",
        "category": decision.rule_id,
        "description": decision.reason,
        "affected_artifact_ids": [artifact.spec.artifact_id],
        "recommended_action": decision.recommended_action,
    }


def _warning(decision: Any, artifact_id: str, index: int) -> dict[str, Any]:
    return {
        "warning_id": f"WARNING_{index:03d}",
        "category": decision.rule_id,
        "description": decision.reason,
        "affected_artifact_ids": [artifact_id],
        "recommended_action": decision.recommended_action,
    }


def _warning_pairs(copied: list[_CopiedArtifact]) -> list[tuple[Any, _CopiedArtifact]]:
    pairs = []
    for copied_artifact in copied:
        for decision in copied_artifact.prepared.policy_report.decisions:
            if decision.severity == "warn":
                pairs.append((decision, copied_artifact))
    return pairs


def _unique_messages(messages: list[str]) -> list[str]:
    unique: list[str] = []
    for message in messages:
        if message not in unique:
            unique.append(message)
    return unique


def _warning_messages(included: list[_PreparedArtifact]) -> list[str]:
    return [decision.reason for artifact in included for decision in artifact.policy_report.decisions if decision.severity == "warn"]


def _warning_messages_from_manifest(policy_report: PolicyReport) -> list[str]:
    return [decision.reason for decision in policy_report.decisions if decision.severity == "warn"]


def _with_manifest_policy_results(manifest: dict[str, Any], report: PolicyReport) -> dict[str, Any]:
    if report.warning_count == 0 and report.denied_count == 0:
        return manifest
    updated = dict(manifest)
    isolation = dict(manifest["isolation_check"])
    existing_warnings = list(isolation.get("warnings", []))
    existing_issues = list(isolation.get("issues", []))
    for decision in report.decisions:
        if decision.severity == "warn" and not any(warning.get("category") == decision.rule_id for warning in existing_warnings):
            existing_warnings.append(
                {
                    "warning_id": f"WARNING_MANIFEST_{len(existing_warnings) + 1:03d}",
                    "category": decision.rule_id,
                    "description": decision.reason,
                    "affected_artifact_ids": [],
                    "recommended_action": decision.recommended_action,
                }
            )
        if decision.severity == "deny":
            existing_issues.append(
                {
                    "issue_id": f"ISSUE_MANIFEST_{len(existing_issues) + 1:03d}",
                    "severity": "critical",
                    "category": decision.rule_id,
                    "description": decision.reason,
                    "affected_artifact_ids": ["MANIFEST_POLICY"],
                    "recommended_action": decision.recommended_action,
                }
            )
    if existing_issues:
        isolation["status"] = "failed"
        isolation["issues"] = existing_issues
    elif existing_warnings and isolation["status"] == "passed":
        isolation["status"] = "passed_with_warnings"
    if existing_warnings:
        isolation["warnings"] = existing_warnings
    updated["isolation_check"] = isolation
    return updated


def _validate_manifest_schema(manifest: dict[str, Any]) -> None:
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "blind_bundle_manifest.schema.yaml"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest), key=str)
    if errors:
        details = "; ".join(error.message for error in errors[:3])
        raise BlindBundleBuildError(f"generated blind bundle manifest is invalid: {details}")


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _publish_tmp_bundle(tmp_dir: Path, bundle_dir: Path, overwrite: bool) -> None:
    backup_dir = bundle_dir.with_name(f".{bundle_dir.name}.backup-{uuid.uuid4().hex}")
    if bundle_dir.exists():
        if not overwrite:
            raise BlindBundleBuildError("output bundle already exists; pass overwrite=True to replace it")
        if bundle_dir.is_symlink() or not bundle_dir.is_dir():
            raise BlindBundleBuildError("existing bundle path is unsafe to overwrite")
        bundle_dir.rename(backup_dir)
    try:
        tmp_dir.rename(bundle_dir)
    except Exception:
        if backup_dir.exists() and not bundle_dir.exists():
            backup_dir.rename(bundle_dir)
        raise
    else:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)


def _neutral_bundle_path(source_path: str, index: int) -> PurePosixPath:
    suffix = PurePosixPath(source_path).suffix.lower()
    if not _safe_extension(suffix):
        suffix = ".bin"
    return PurePosixPath("artifacts") / f"ARTIFACT-{index:03d}{suffix}"


def _safe_extension(suffix: str) -> bool:
    return bool(suffix) and len(suffix) <= 12 and suffix.startswith(".") and suffix[1:].isalnum()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True

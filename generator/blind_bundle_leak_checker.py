"""Structural leak checker for already-generated blind bundles.

The checker audits one bundle directory against its ``blind_bundle_manifest.yaml``.
It is deterministic and offline: it validates structured metadata, compares the
manifest with physical files, checks sha256 hashes, and delegates role/category
rules to ``artifact_visibility_policy``. It does not interpret artifact text,
run OCR/LLMs, sanitize files, or modify the bundle.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from yaml import YAMLError

from generator.artifact_visibility_policy import evaluate_manifest_visibility
from generator.blind_bundle_generator import MANIFEST_FILENAME

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "blind_bundle_manifest.schema.yaml"


class LeakSeverity(StrEnum):
    """Stable severity values emitted by the structural leak checker."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class LeakCheckIssue:
    """One deterministic issue found during blind bundle leak checking."""

    issue_id: str
    severity: LeakSeverity
    code: str
    message: str
    path: str | None = None
    artifact_id: str | None = None
    recommended_action: str = "Review the bundle and regenerate it from trusted inputs."


@dataclass(frozen=True)
class LeakCheckReport:
    """Structured report returned by :func:`check_blind_bundle`."""

    bundle_path: Path
    valid: bool
    issues: tuple[LeakCheckIssue, ...]
    error_count: int
    warning_count: int
    critical_count: int
    manifest_loaded: bool
    manifest_schema_valid: bool
    policy_allowed: bool
    checked_file_count: int
    declared_file_count: int


@dataclass(frozen=True)
class _CollectedFiles:
    files: frozenset[str] = field(default_factory=frozenset)
    empty_directories: tuple[str, ...] = ()
    issues: tuple[LeakCheckIssue, ...] = ()


class _IssueBuilder:
    def __init__(self) -> None:
        self._issues: list[LeakCheckIssue] = []

    def add(
        self,
        code: str,
        severity: LeakSeverity,
        message: str,
        *,
        path: str | None = None,
        artifact_id: str | None = None,
        recommended_action: str = "Review the bundle and regenerate it from trusted inputs.",
    ) -> None:
        self._issues.append(
            LeakCheckIssue(
                issue_id="PENDING",
                severity=severity,
                code=code,
                message=message,
                path=path,
                artifact_id=artifact_id,
                recommended_action=recommended_action,
            )
        )

    def extend(self, issues: tuple[LeakCheckIssue, ...]) -> None:
        for issue in issues:
            self.add(
                issue.code,
                issue.severity,
                issue.message,
                path=issue.path,
                artifact_id=issue.artifact_id,
                recommended_action=issue.recommended_action,
            )

    def finalize(self) -> tuple[LeakCheckIssue, ...]:
        ordered = sorted(
            self._issues,
            key=lambda issue: (
                _severity_order(issue.severity),
                issue.code,
                issue.path or "",
                issue.artifact_id or "",
                issue.message,
            ),
        )
        return tuple(
            LeakCheckIssue(
                issue_id=f"LEAK_ISSUE_{index:03d}",
                severity=issue.severity,
                code=issue.code,
                message=issue.message,
                path=issue.path,
                artifact_id=issue.artifact_id,
                recommended_action=issue.recommended_action,
            )
            for index, issue in enumerate(ordered, 1)
        )


def check_blind_bundle(bundle_path: Path) -> LeakCheckReport:
    """Audit one generated blind bundle directory without modifying it."""

    bundle_path = Path(bundle_path)
    issues = _IssueBuilder()
    manifest: dict[str, Any] | None = None
    manifest_loaded = False
    manifest_schema_valid = False
    policy_allowed = False
    checked_file_count = 0
    declared_file_count = 0

    if bundle_path.is_symlink():
        issues.add(
            "LEAK_BUNDLE_PATH_SYMLINK",
            LeakSeverity.CRITICAL,
            "Bundle path is a symlink and cannot be audited safely.",
            path=str(bundle_path),
            recommended_action="Audit only a real bundle directory; do not pass symlink bundle roots.",
        )
        return _build_report(bundle_path, issues, manifest_loaded, manifest_schema_valid, policy_allowed, 0, 0)
    if not bundle_path.exists():
        issues.add(
            "LEAK_BUNDLE_PATH_MISSING",
            LeakSeverity.CRITICAL,
            "Bundle path does not exist.",
            path=str(bundle_path),
            recommended_action="Generate the bundle before running the structural leak checker.",
        )
        return _build_report(bundle_path, issues, manifest_loaded, manifest_schema_valid, policy_allowed, 0, 0)
    if not bundle_path.is_dir():
        issues.add(
            "LEAK_BUNDLE_PATH_NOT_DIRECTORY",
            LeakSeverity.CRITICAL,
            "Bundle path exists but is not a directory.",
            path=str(bundle_path),
            recommended_action="Pass the generated bundle directory, not a file.",
        )
        return _build_report(bundle_path, issues, manifest_loaded, manifest_schema_valid, policy_allowed, 0, 0)

    collected = collect_bundle_files(bundle_path)
    issues.extend(collected.issues)
    checked_file_count = len(collected.files)

    manifest, load_issues = load_manifest_from_bundle(bundle_path)
    issues.extend(load_issues)
    manifest_loaded = isinstance(manifest, dict)

    if manifest_loaded and manifest is not None:
        schema_errors = validate_manifest_schema(manifest)
        if schema_errors:
            for message in schema_errors:
                issues.add(
                    "LEAK_MANIFEST_SCHEMA_INVALID",
                    LeakSeverity.CRITICAL,
                    f"Manifest does not validate against blind bundle schema: {message}",
                    path=MANIFEST_FILENAME,
                    recommended_action="Regenerate the bundle with a schema-valid manifest.",
                )
        else:
            manifest_schema_valid = True

        included = _included_artifacts(manifest)
        declared_file_count = len(included)
        compare_manifest_to_files(bundle_path, manifest, collected.files, issues)
        check_policy(manifest, issues)
        policy_allowed = not any(issue.code == "LEAK_POLICY_DENIED_INCLUDED_ARTIFACT" for issue in issues._issues)
        check_isolation(manifest, issues)
        check_manifest_policy_contradictions(manifest, issues)

    return _build_report(
        bundle_path,
        issues,
        manifest_loaded,
        manifest_schema_valid,
        policy_allowed,
        checked_file_count,
        declared_file_count,
    )


def load_manifest_from_bundle(bundle_path: Path) -> tuple[dict[str, Any] | None, tuple[LeakCheckIssue, ...]]:
    issues = _IssueBuilder()
    manifest_path = bundle_path / MANIFEST_FILENAME
    if manifest_path.is_symlink():
        issues.add(
            "LEAK_MANIFEST_NOT_FILE",
            LeakSeverity.CRITICAL,
            "Manifest path is a symlink, not a trusted regular file.",
            path=MANIFEST_FILENAME,
            recommended_action="Remove the symlink and regenerate the bundle manifest as a regular file.",
        )
        return None, issues.finalize()
    if not manifest_path.exists():
        issues.add(
            "LEAK_MANIFEST_MISSING",
            LeakSeverity.CRITICAL,
            "Bundle manifest is missing.",
            path=MANIFEST_FILENAME,
            recommended_action="Regenerate the bundle so blind_bundle_manifest.yaml is present.",
        )
        return None, issues.finalize()
    if not manifest_path.is_file():
        issues.add(
            "LEAK_MANIFEST_NOT_FILE",
            LeakSeverity.CRITICAL,
            "Bundle manifest exists but is not a regular file.",
            path=MANIFEST_FILENAME,
            recommended_action="Replace the manifest path with a regular YAML manifest file.",
        )
        return None, issues.finalize()

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, YAMLError) as exc:
        issues.add(
            "LEAK_MANIFEST_INVALID_YAML",
            LeakSeverity.CRITICAL,
            f"Bundle manifest could not be parsed as YAML: {exc}",
            path=MANIFEST_FILENAME,
            recommended_action="Regenerate the bundle with a valid YAML manifest.",
        )
        return None, issues.finalize()

    if not isinstance(manifest, dict):
        issues.add(
            "LEAK_MANIFEST_SCHEMA_INVALID",
            LeakSeverity.CRITICAL,
            "Bundle manifest must be a YAML mapping.",
            path=MANIFEST_FILENAME,
            recommended_action="Regenerate the bundle with a mapping/object manifest.",
        )
        return None, issues.finalize()
    return manifest, issues.finalize()


def validate_manifest_schema(manifest: dict[str, Any]) -> tuple[str, ...]:
    schema = yaml.safe_load(_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return tuple(sorted(error.message for error in validator.iter_errors(manifest)))


def collect_bundle_files(bundle_path: Path) -> _CollectedFiles:
    issues = _IssueBuilder()
    files: set[str] = set()
    empty_directories: list[str] = []

    for root, dirs, filenames in os.walk(bundle_path, topdown=True, followlinks=False):
        root_path = Path(root)
        kept_dirs: list[str] = []
        for dirname in sorted(dirs):
            dir_path = root_path / dirname
            rel = _relative_posix(bundle_path, dir_path)
            if dir_path.is_symlink():
                issues.add(
                    "LEAK_FILE_SYMLINK",
                    LeakSeverity.CRITICAL,
                    "Bundle contains a symlink directory, which is not followed.",
                    path=rel,
                    recommended_action="Remove symlinks and regenerate the bundle with regular files only.",
                )
            else:
                kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        if root_path != bundle_path and not dirs and not filenames:
            empty_directories.append(_relative_posix(bundle_path, root_path))

        for filename in sorted(filenames):
            file_path = root_path / filename
            rel = _relative_posix(bundle_path, file_path)
            if file_path.is_symlink():
                issues.add(
                    "LEAK_FILE_SYMLINK",
                    LeakSeverity.CRITICAL,
                    "Bundle contains a symlink file, which is not followed.",
                    path=rel,
                    recommended_action="Remove symlinks and regenerate the bundle with regular files only.",
                )
                continue
            if not file_path.is_file():
                continue
            if rel != MANIFEST_FILENAME:
                files.add(rel)

    for rel in sorted(empty_directories):
        issues.add(
            "LEAK_UNEXPECTED_DIRECTORY_EMPTY",
            LeakSeverity.WARNING,
            "Bundle contains an empty directory not declared by the manifest.",
            path=rel,
            recommended_action="Review whether the empty directory should be removed from the generated bundle.",
        )

    return _CollectedFiles(files=frozenset(files), empty_directories=tuple(sorted(empty_directories)), issues=issues.finalize())


def compare_manifest_to_files(
    bundle_path: Path,
    manifest: dict[str, Any],
    physical_files: frozenset[str],
    issues: _IssueBuilder,
) -> None:
    included = _included_artifacts(manifest)
    excluded = _excluded_artifacts(manifest)
    declared_paths: set[str] = set()
    usable_declared_paths: set[str] = set()
    artifact_ids: set[str] = set()

    for artifact in included:
        artifact_id = _string_or_none(artifact.get("artifact_id"))
        artifact_path = _string_or_none(artifact.get("path"))
        if artifact_id:
            if artifact_id in artifact_ids:
                issues.add(
                    "LEAK_DUPLICATE_ARTIFACT_ID",
                    LeakSeverity.ERROR,
                    "Manifest declares the same artifact_id more than once.",
                    artifact_id=artifact_id,
                    recommended_action="Ensure each included artifact has one unique artifact_id.",
                )
            artifact_ids.add(artifact_id)
        if artifact_path is None:
            continue
        if artifact_path in declared_paths:
            issues.add(
                "LEAK_DUPLICATE_DECLARED_PATH",
                LeakSeverity.ERROR,
                "Manifest declares the same included artifact path more than once.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Ensure each included artifact maps to one unique bundle path.",
            )
        declared_paths.add(artifact_path)

        if not _is_safe_manifest_artifact_path(artifact_path):
            issues.add(
                "LEAK_UNSAFE_MANIFEST_PATH",
                LeakSeverity.ERROR,
                "Manifest included artifact path is absolute, escaping, or structurally unsafe.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Use a non-empty relative POSIX path that stays inside the bundle.",
            )
            continue
        usable_declared_paths.add(artifact_path)
        target = _bundle_child(bundle_path, artifact_path)
        if target is None:
            issues.add(
                "LEAK_UNSAFE_MANIFEST_PATH",
                LeakSeverity.ERROR,
                "Manifest included artifact path escapes the audited bundle.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the manifest with paths inside the bundle root.",
            )
            continue
        if target.is_symlink():
            issues.add(
                "LEAK_FILE_SYMLINK",
                LeakSeverity.CRITICAL,
                "Declared artifact resolves to a symlink in the bundle.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the bundle with regular files only.",
            )
            continue
        if not target.exists():
            issues.add(
                "LEAK_DECLARED_FILE_MISSING",
                LeakSeverity.ERROR,
                "Manifest declares an artifact file that is absent from the bundle.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the bundle so every declared artifact is physically present.",
            )
            continue
        if not target.is_file():
            issues.add(
                "LEAK_DECLARED_FILE_MISSING",
                LeakSeverity.ERROR,
                "Manifest declares an artifact path that is not a regular file.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the bundle so every declared artifact path is a regular file.",
            )
            continue
        expected_hash = _string_or_none(artifact.get("hash"))
        if expected_hash and _sha256_file(target) != expected_hash:
            issues.add(
                "LEAK_HASH_MISMATCH",
                LeakSeverity.CRITICAL,
                "Declared artifact hash does not match the physical file content.",
                path=artifact_path,
                artifact_id=artifact_id,
                recommended_action="Discard this bundle and regenerate it from trusted source artifacts.",
            )

    for physical in sorted(physical_files - usable_declared_paths):
        issues.add(
            "LEAK_UNDECLARED_FILE",
            LeakSeverity.CRITICAL,
            "Bundle contains a physical file not declared in included_artifacts.",
            path=physical,
            recommended_action="Remove undeclared files by regenerating the bundle from the manifest inputs.",
        )

    for artifact in excluded:
        excluded_path = _string_or_none(artifact.get("path"))
        if not excluded_path or not _is_safe_manifest_artifact_path(excluded_path):
            continue
        target = _bundle_child(bundle_path, excluded_path)
        if target is not None and (target.exists() or target.is_symlink()):
            issues.add(
                "LEAK_EXCLUDED_ARTIFACT_PRESENT",
                LeakSeverity.CRITICAL,
                "Manifest excluded_artifacts path is physically present in the bundle.",
                path=excluded_path,
                recommended_action="Discard this bundle and regenerate it without excluded artifacts.",
            )


def check_policy(manifest: dict[str, Any], issues: _IssueBuilder) -> None:
    report = evaluate_manifest_visibility(manifest)
    for decision in report.decisions:
        artifact_id = _artifact_id_from_conditions(decision.matched_conditions)
        if decision.severity == "deny":
            issues.add(
                "LEAK_POLICY_DENIED_INCLUDED_ARTIFACT",
                LeakSeverity.CRITICAL,
                f"Visibility policy denied an included artifact: {decision.rule_id}: {decision.reason}",
                artifact_id=artifact_id,
                recommended_action=decision.recommended_action,
            )
        elif decision.severity == "warn":
            issues.add(
                "LEAK_POLICY_WARNING",
                LeakSeverity.WARNING,
                f"Visibility policy emitted a warning: {decision.rule_id}: {decision.reason}",
                artifact_id=artifact_id,
                recommended_action=decision.recommended_action,
            )


def check_isolation(manifest: dict[str, Any], issues: _IssueBuilder) -> None:
    isolation = manifest.get("isolation_check") or {}
    status = isolation.get("status")
    if status == "failed":
        issues.add(
            "LEAK_MANIFEST_ISOLATION_FAILED",
            LeakSeverity.ERROR,
            "Manifest isolation_check status is failed.",
            recommended_action="Treat the bundle as invalid and resolve the manifest isolation issues before use.",
        )
    elif status == "not_run":
        issues.add(
            "LEAK_MANIFEST_ISOLATION_FAILED",
            LeakSeverity.ERROR,
            "Manifest isolation_check status is not_run; generated bundles must include an isolation check.",
            recommended_action="Regenerate the bundle with isolation checks enabled.",
        )
    elif status == "passed_with_warnings":
        issues.add(
            "LEAK_MANIFEST_ISOLATION_WARNING",
            LeakSeverity.WARNING,
            "Manifest isolation_check passed with warnings.",
            recommended_action="Review the manifest isolation warnings before distributing the bundle.",
        )


def check_manifest_policy_contradictions(manifest: dict[str, Any], issues: _IssueBuilder) -> None:
    visibility_policy = manifest.get("visibility_policy") or {}
    allowed = set(visibility_policy.get("allowed_categories") or [])
    prohibited = set(visibility_policy.get("prohibited_categories") or [])
    for artifact in _included_artifacts(manifest):
        visibility = artifact.get("visibility")
        artifact_id = _string_or_none(artifact.get("artifact_id"))
        path = _string_or_none(artifact.get("path"))
        if visibility in prohibited:
            issues.add(
                "LEAK_MANIFEST_POLICY_CONTRADICTION",
                LeakSeverity.ERROR,
                "Manifest includes an artifact whose visibility is listed in visibility_policy.prohibited_categories.",
                path=path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the bundle with a non-contradictory visibility_policy.",
            )
        if allowed and visibility not in allowed:
            issues.add(
                "LEAK_MANIFEST_POLICY_CONTRADICTION",
                LeakSeverity.ERROR,
                "Manifest includes an artifact whose visibility is absent from visibility_policy.allowed_categories.",
                path=path,
                artifact_id=artifact_id,
                recommended_action="Regenerate the bundle with allowed_categories matching included artifacts.",
            )


def _included_artifacts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = manifest.get("included_artifacts") or []
    return [artifact for artifact in artifacts if isinstance(artifact, dict)]


def _excluded_artifacts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = manifest.get("excluded_artifacts") or []
    return [artifact for artifact in artifacts if isinstance(artifact, dict)]


def _is_safe_manifest_artifact_path(value: str) -> bool:
    if not value or "\\" in value or "//" in value or value == MANIFEST_FILENAME:
        return False
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute()


def _bundle_child(bundle_path: Path, relative_posix: str) -> Path | None:
    if not _is_safe_manifest_artifact_path(relative_posix):
        return None
    child = bundle_path.joinpath(*PurePosixPath(relative_posix).parts)
    bundle_resolved = bundle_path.resolve(strict=False)
    child_resolved = child.resolve(strict=False)
    if not child_resolved.is_relative_to(bundle_resolved):
        return None
    return child


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_posix(root: Path, child: Path) -> str:
    return child.relative_to(root).as_posix()


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _artifact_id_from_conditions(conditions: list[str]) -> str | None:
    for condition in conditions:
        if condition.startswith("artifact_id="):
            return condition.partition("=")[2]
    return None


def _severity_order(severity: LeakSeverity) -> int:
    return {
        LeakSeverity.CRITICAL: 0,
        LeakSeverity.ERROR: 1,
        LeakSeverity.WARNING: 2,
        LeakSeverity.INFO: 3,
    }[severity]


def _build_report(
    bundle_path: Path,
    issues: _IssueBuilder,
    manifest_loaded: bool,
    manifest_schema_valid: bool,
    policy_allowed: bool,
    checked_file_count: int,
    declared_file_count: int,
) -> LeakCheckReport:
    final_issues = issues.finalize()
    critical_count = sum(1 for issue in final_issues if issue.severity == LeakSeverity.CRITICAL)
    error_count = sum(1 for issue in final_issues if issue.severity == LeakSeverity.ERROR)
    warning_count = sum(1 for issue in final_issues if issue.severity == LeakSeverity.WARNING)
    return LeakCheckReport(
        bundle_path=bundle_path,
        valid=critical_count == 0 and error_count == 0,
        issues=final_issues,
        error_count=error_count,
        warning_count=warning_count,
        critical_count=critical_count,
        manifest_loaded=manifest_loaded,
        manifest_schema_valid=manifest_schema_valid,
        policy_allowed=policy_allowed,
        checked_file_count=checked_file_count,
        declared_file_count=declared_file_count,
    )

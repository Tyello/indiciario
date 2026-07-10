"""Offline harness and output contract for a blind solver run (ISSUE-16).

This module simulates running a *blind* solver over an already generated and
sanitized blind bundle. It does not contain any solver intelligence: it only

- validates the bundle structurally with the leak checker;
- loads the manifest and exposes ONLY ``included_artifacts`` to the solver;
- denies every read outside the declared artifact list (excluded artifacts,
  undeclared files, path traversal, files outside the bundle);
- runs a caller-supplied solver object against a controlled read context;
- validates the produced report against ``schemas/blind_solver_report.schema.yaml``
  and a few structural cross-checks against the manifest;
- records which artifacts were read and which accesses were denied.

It never calls an LLM, never accesses the network, never reads files that are
not declared in the bundle, never opens excluded artifacts, never performs OCR,
and never parses PDFs semantically. The actual solver intelligence and any
LLM/provider adapter are explicitly out of scope for this issue.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.blind_bundle_generator import MANIFEST_FILENAME
from generator.blind_bundle_leak_checker import (
    LeakCheckReport,
    _bundle_child,
    check_blind_bundle,
)

SCHEMA_VERSION = "1.0"
DEFAULT_MAX_ARTIFACTS = 100
DEFAULT_MAX_BYTES_PER_ARTIFACT = 1_000_000
_CONFIDENCE_VALUES = ("low", "medium", "high")
_REPORT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "blind_solver_report.schema.yaml"


class BlindSolverHarnessError(RuntimeError):
    """Raised when the blind solver harness cannot run a safe, auditable round."""


@dataclass(frozen=True)
class BlindSolverHarnessRequest:
    """Structured request describing one offline blind solver round."""

    bundle_path: Path
    solver_id: str
    run_id: str
    created_by: str
    created_at: str | None = None
    max_artifacts: int = DEFAULT_MAX_ARTIFACTS
    max_bytes_per_artifact: int = DEFAULT_MAX_BYTES_PER_ARTIFACT


@dataclass(frozen=True)
class ArtifactDescriptor:
    """Read-only view of one included artifact handed to the solver.

    Deliberately carries no filesystem ``Path`` so the solver cannot open files
    directly; it must go through the context read methods.
    """

    artifact_id: str
    path: str
    artifact_type: str
    visibility: str
    envelope_scope: str


@dataclass(frozen=True)
class BlindSolverEvidence:
    """One auditable evidence item referenced by the solver's conclusion."""

    artifact_id: str
    path: str
    quote_or_summary: str
    relevance: str
    confidence: str


@dataclass(frozen=True)
class BlindSolverReport:
    """Structured blind solver output (the contract of ISSUE-16)."""

    schema_version: str
    solver_run_id: str
    solver_id: str
    bundle_id: str
    manifest_id: str
    created_at: str
    conclusion: str
    confidence: str
    reasoning_summary: str
    evidence_used: tuple[BlindSolverEvidence, ...]
    open_questions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class BlindSolverHarnessResult:
    """Auditable result of one offline blind solver round."""

    report: dict[str, Any]
    bundle_report: LeakCheckReport
    accessed_artifacts: tuple[str, ...]
    denied_access_attempts: tuple[str, ...]
    warnings: tuple[str, ...] = ()


@runtime_checkable
class BlindSolver(Protocol):
    """A blind solver consumes a controlled context and returns a report.

    Implementations may return a :class:`BlindSolverReport` or a plain mapping
    with the same fields. No solver intelligence is provided by this module.
    """

    def solve(self, context: "BlindSolverContext") -> "BlindSolverReport | Mapping[str, Any]":
        ...


class BlindSolverContext:
    """Controlled read surface over a bundle's ``included_artifacts``.

    The context exposes artifact metadata and UTF-8 text reads, but never the
    bundle root path or raw file handles. Every read is checked against the
    declared artifact list; denied reads are recorded and raise.
    """

    def __init__(
        self,
        *,
        manifest: Mapping[str, Any] | None = None,
        bundle_path: Path | None = None,
        solver_id: str,
        solver_run_id: str,
        max_bytes_per_artifact: int = DEFAULT_MAX_BYTES_PER_ARTIFACT,
        bundle_root: Path | None = None,
        bundle_id: str | None = None,
        manifest_id: str | None = None,
    ) -> None:
        # Support both old and new call signatures
        # Old: manifest=dict, bundle_path=Path
        # New: bundle_root=Path, bundle_id=str, manifest_id=str (reads manifest internally)
        if bundle_root is not None:
            bundle_path = bundle_root
            manifest_path = bundle_path / MANIFEST_FILENAME
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        elif manifest is None or bundle_path is None:
            raise ValueError("Either (manifest, bundle_path) or bundle_root must be provided")

        self._bundle_path = bundle_path
        self._solver_id = solver_id
        self._solver_run_id = solver_run_id
        self._bundle_id = bundle_id or str(manifest.get("bundle_id"))
        self._manifest_id = manifest_id or str(manifest.get("manifest_id"))
        self._max_bytes_per_artifact = max_bytes_per_artifact
        self._descriptors: tuple[ArtifactDescriptor, ...] = _build_descriptors(manifest)
        self._by_id: dict[str, ArtifactDescriptor] = {d.artifact_id: d for d in self._descriptors}
        self._by_path: dict[str, ArtifactDescriptor] = {d.path: d for d in self._descriptors}
        self._accessed: list[str] = []
        self._denied: list[str] = []

    # -- public read surface ------------------------------------------------ #
    @property
    def solver_id(self) -> str:
        return self._solver_id

    @property
    def solver_run_id(self) -> str:
        return self._solver_run_id

    @property
    def bundle_id(self) -> str:
        return self._bundle_id

    @property
    def manifest_id(self) -> str:
        return self._manifest_id

    @property
    def accessed_artifacts(self) -> tuple[str, ...]:
        return tuple(self._accessed)

    @property
    def denied_access_attempts(self) -> tuple[str, ...]:
        return tuple(self._denied)

    def list_artifacts(self) -> tuple[ArtifactDescriptor, ...]:
        return self._descriptors

    def read_artifact(self, artifact_id: str) -> str:
        """Alias for :meth:`read_artifact_text` (UTF-8 only in this issue)."""

        return self.read_artifact_text(artifact_id)

    def read_artifact_text(self, artifact_id: str) -> str:
        descriptor = self._by_id.get(artifact_id)
        if descriptor is None:
            self._denied.append(f"artifact_id={artifact_id}")
            raise BlindSolverHarnessError(
                f"blind solver attempted to read an artifact_id that is not declared in the bundle: {artifact_id}"
            )
        return self._read_descriptor(descriptor)

    def read_artifact_path(self, path: str) -> str:
        descriptor = self._by_path.get(path)
        if descriptor is None:
            self._denied.append(f"path={path}")
            raise BlindSolverHarnessError(
                f"blind solver attempted to read a path that is not an included artifact: {path}"
            )
        return self._read_descriptor(descriptor)

    # -- internal ----------------------------------------------------------- #
    def _read_descriptor(self, descriptor: ArtifactDescriptor) -> str:
        target = _bundle_child(self._bundle_path, descriptor.path)
        if target is None:
            self._denied.append(f"path={descriptor.path}")
            raise BlindSolverHarnessError(
                f"included artifact path is unsafe or escapes the bundle: {descriptor.path}"
            )
        if target.is_symlink() or not target.is_file():
            self._denied.append(f"path={descriptor.path}")
            raise BlindSolverHarnessError(
                f"included artifact is missing or not a regular file: {descriptor.path}"
            )
        raw = target.read_bytes()
        if len(raw) > self._max_bytes_per_artifact:
            raise BlindSolverHarnessError(
                f"included artifact exceeds max_bytes_per_artifact at read time: {descriptor.path}"
            )
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BlindSolverHarnessError(
                f"included artifact is not valid UTF-8 text and cannot be read: {descriptor.path}: {exc}"
            ) from exc
        self._accessed.append(descriptor.artifact_id)
        return text


def run_blind_solver_harness(request: BlindSolverHarnessRequest, solver: BlindSolver) -> BlindSolverHarnessResult:
    """Run one offline blind solver round and return an auditable result.

    The bundle is validated by the structural leak checker, only declared
    artifacts are exposed to ``solver``, and the produced report is validated
    structurally and cross-checked against the manifest. Any protocol breach
    (invalid bundle, denied access, malformed/contradictory report) raises
    :class:`BlindSolverHarnessError`.
    """

    _validate_request(request)
    bundle_path = Path(request.bundle_path)

    bundle_report = check_blind_bundle(bundle_path)
    if not bundle_report.valid:
        codes = ", ".join(sorted({issue.code for issue in bundle_report.issues if issue.severity in {"error", "critical"}}))
        raise BlindSolverHarnessError(f"blind bundle failed the structural leak check and cannot be solved: {codes}")

    manifest = _load_manifest(bundle_path)
    included = _included_artifacts(manifest)
    _enforce_limits(request, bundle_path, included)

    context = BlindSolverContext(
        manifest=manifest,
        bundle_path=bundle_path.resolve(strict=False),
        solver_id=request.solver_id,
        solver_run_id=request.run_id,
        max_bytes_per_artifact=request.max_bytes_per_artifact,
    )

    raw_report = solver.solve(context)
    report = _coerce_report_dict(raw_report)

    if context.denied_access_attempts:
        raise BlindSolverHarnessError(
            f"blind solver attempted denied accesses during the round: {', '.join(context.denied_access_attempts)}"
        )

    _validate_report_schema(report)
    _validate_report_semantics(report, manifest, request, context)

    warnings = _result_warnings(report, bundle_report, context)
    return BlindSolverHarnessResult(
        report=report,
        bundle_report=bundle_report,
        accessed_artifacts=context.accessed_artifacts,
        denied_access_attempts=context.denied_access_attempts,
        warnings=warnings,
    )


def report_to_dict(report: BlindSolverReport | Mapping[str, Any]) -> dict[str, Any]:
    """Return a plain, JSON-schema-ready dict for a report."""

    if isinstance(report, BlindSolverReport):
        return _report_dataclass_to_dict(report)
    if isinstance(report, Mapping):
        return dict(report)
    raise BlindSolverHarnessError("blind solver must return a BlindSolverReport or a mapping")


def validate_blind_solver_report(report: Mapping[str, Any]) -> tuple[str, ...]:
    """Return structural schema error messages for a report (empty == valid)."""

    schema = yaml.safe_load(_REPORT_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return tuple(sorted(error.message for error in validator.iter_errors(report)))


# --------------------------------------------------------------------------- #
# Internal helpers                                                             #
# --------------------------------------------------------------------------- #
def _validate_request(request: BlindSolverHarnessRequest) -> None:
    if request.max_artifacts < 1:
        raise BlindSolverHarnessError("max_artifacts must be at least 1")
    if request.max_bytes_per_artifact < 1:
        raise BlindSolverHarnessError("max_bytes_per_artifact must be at least 1")
    if not str(request.solver_id):
        raise BlindSolverHarnessError("solver_id must not be empty")
    if not str(request.run_id):
        raise BlindSolverHarnessError("run_id must not be empty")


def _load_manifest(bundle_path: Path) -> dict[str, Any]:
    manifest_path = bundle_path / MANIFEST_FILENAME
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise BlindSolverHarnessError(f"bundle manifest could not be loaded: {exc}") from exc
    if not isinstance(manifest, dict):
        raise BlindSolverHarnessError("bundle manifest must be a YAML mapping")
    return manifest


def _included_artifacts(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    artifacts = manifest.get("included_artifacts") or []
    return [artifact for artifact in artifacts if isinstance(artifact, dict)]


def _enforce_limits(request: BlindSolverHarnessRequest, bundle_path: Path, included: list[dict[str, Any]]) -> None:
    if len(included) > request.max_artifacts:
        raise BlindSolverHarnessError(
            f"bundle exceeds max_artifacts: {len(included)} included artifacts > {request.max_artifacts}"
        )
    for artifact in included:
        path = artifact.get("path")
        if not isinstance(path, str):
            continue
        target = _bundle_child(bundle_path, path)
        if target is None or target.is_symlink() or not target.is_file():
            continue
        size = target.stat().st_size
        if size > request.max_bytes_per_artifact:
            raise BlindSolverHarnessError(
                f"bundle artifact exceeds max_bytes_per_artifact: {path} is {size} bytes > {request.max_bytes_per_artifact}"
            )


def _build_descriptors(manifest: Mapping[str, Any]) -> tuple[ArtifactDescriptor, ...]:
    descriptors: list[ArtifactDescriptor] = []
    for artifact in manifest.get("included_artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        descriptors.append(
            ArtifactDescriptor(
                artifact_id=str(artifact.get("artifact_id")),
                path=str(artifact.get("path")),
                artifact_type=str(artifact.get("artifact_type")),
                visibility=str(artifact.get("visibility")),
                envelope_scope=str(artifact.get("envelope_scope")),
            )
        )
    return tuple(descriptors)


def _coerce_report_dict(raw_report: BlindSolverReport | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(raw_report, BlindSolverReport):
        return _report_dataclass_to_dict(raw_report)
    if isinstance(raw_report, Mapping):
        return dict(raw_report)
    raise BlindSolverHarnessError("blind solver must return a BlindSolverReport or a mapping")


def _report_dataclass_to_dict(report: BlindSolverReport) -> dict[str, Any]:
    data = asdict(report)
    data["evidence_used"] = [dict(item) for item in data["evidence_used"]]
    data["open_questions"] = list(report.open_questions)
    data["assumptions"] = list(report.assumptions)
    data["warnings"] = list(report.warnings)
    return data


def _validate_report_schema(report: Mapping[str, Any]) -> None:
    errors = validate_blind_solver_report(report)
    if errors:
        details = "; ".join(errors[:3])
        raise BlindSolverHarnessError(f"blind solver report is structurally invalid: {details}")


def _validate_report_semantics(
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
    request: BlindSolverHarnessRequest,
    context: BlindSolverContext,
) -> None:
    if report.get("bundle_id") != manifest.get("bundle_id"):
        raise BlindSolverHarnessError("report bundle_id does not match the manifest bundle_id")
    if report.get("manifest_id") != manifest.get("manifest_id"):
        raise BlindSolverHarnessError("report manifest_id does not match the manifest manifest_id")
    if report.get("solver_run_id") != request.run_id:
        raise BlindSolverHarnessError("report solver_run_id does not match the harness request run_id")
    if report.get("solver_id") != request.solver_id:
        raise BlindSolverHarnessError("report solver_id does not match the harness request solver_id")
    if not str(report.get("reasoning_summary") or "").strip():
        raise BlindSolverHarnessError("report reasoning_summary must not be empty")
    if report.get("confidence") not in _CONFIDENCE_VALUES:
        raise BlindSolverHarnessError("report confidence must be one of low/medium/high")

    evidence = list(report.get("evidence_used") or [])
    conclusion = str(report.get("conclusion") or "").strip()
    if conclusion and not evidence:
        raise BlindSolverHarnessError("report has a conclusion but no evidence_used; evidence is required")

    by_id = {descriptor.artifact_id: descriptor for descriptor in context.list_artifacts()}
    for item in evidence:
        artifact_id = item.get("artifact_id")
        descriptor = by_id.get(artifact_id)
        if descriptor is None:
            raise BlindSolverHarnessError(
                f"evidence_used references an artifact_id that is not in the bundle: {artifact_id}"
            )
        if item.get("path") != descriptor.path:
            raise BlindSolverHarnessError(
                f"evidence_used path does not match the declared artifact path for {artifact_id}"
            )


def _result_warnings(
    report: Mapping[str, Any],
    bundle_report: LeakCheckReport,
    context: BlindSolverContext,
) -> tuple[str, ...]:
    messages: list[str] = []
    for warning in report.get("warnings") or []:
        if isinstance(warning, str) and warning not in messages:
            messages.append(warning)
    for issue in bundle_report.issues:
        if issue.severity == "warning" and issue.message not in messages:
            messages.append(issue.message)
    messages.extend(_citation_without_read_warnings(report, context))
    return tuple(messages)


def _citation_without_read_warnings(
    report: Mapping[str, Any],
    context: BlindSolverContext,
) -> tuple[str, ...]:
    """RV_009: flag evidence_used citations for artifacts never read this round.

    Purely auditable warning (RISCO-02, ISSUE-33.6): never blocks the run, never
    changes any gate decision. Today the LLMBlindSolver reads every included
    artifact to build its prompt, so this never fires on the current solver
    (RV_011); it exists for future selective-read solvers.
    """

    accessed = set(context.accessed_artifacts)
    offenders: list[str] = []
    for item in report.get("evidence_used") or []:
        if not isinstance(item, Mapping):
            continue
        artifact_id = item.get("artifact_id")
        if isinstance(artifact_id, str) and artifact_id not in accessed and artifact_id not in offenders:
            offenders.append(artifact_id)
    if not offenders:
        return ()
    return (
        "RV_009: citacao_sem_leitura: evidence_used cita artifact_id(s) fora de "
        f"accessed_artifacts do round: {', '.join(offenders)}",
    )

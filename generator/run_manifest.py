"""Run Manifest — consolidated immutable output of a multiagent run (ISSUE-27).

This module provides the dataclasses, the structural validator
(``validate_run_manifest``) backed by ``schemas/run_manifest.schema.yaml`` and
the serializer (``manifest_to_dict``). It never executes any agent, never
modifies the workspace and only reads the schema file for validation.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.workspace import (
    VALID_ARTIFACT_TYPES,
    VALID_OUTCOMES,
    VALID_STAGES,
)

__all__ = [
    "SCHEMA_VERSION",
    "STATUS_MAP",
    "VALID_ARTIFACT_TYPES",
    "VALID_OUTCOMES",
    "VALID_STAGES",
    "ManifestArtifactSummary",
    "ManifestDecisionSummary",
    "ManifestFinding",
    "ManifestGateOutcome",
    "ManifestSemanticResult",
    "RunManifest",
    "build_run_manifest",
    "manifest_to_dict",
    "validate_run_manifest",
    "validate_run_manifest_semantics",
]

SCHEMA_VERSION = "1.0"

STATUS_MAP = {
    "done": "complete",
    "gate_blocked": "blocked",
    "rolled_back": "rolled_back",
    "initialized": "incomplete",
    "in_progress": "incomplete",
}

# Manifest pipeline stages = workspace stages without the ``initialized`` and
# ``complete`` pseudo-stages. Derived from :data:`generator.workspace.VALID_STAGES`
# to avoid duplicating the canonical stage list.
_MANIFEST_STAGES: tuple[str, ...] = tuple(
    stage for stage in VALID_STAGES if stage not in ("initialized", "complete")
)

_RUN_MANIFEST_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "run_manifest.schema.yaml"
)


@dataclass(frozen=True)
class ManifestFinding:
    source_artifact_id: str
    source_type: str  # "narrative_review" | "evidence_review"
    code: str
    severity: str  # "critical" | "major" | "minor" | "info"
    field: str
    message: str


@dataclass(frozen=True)
class ManifestGateOutcome:
    decision_id: str
    outcome: str  # "approved" | "rejected" | "rollback"
    justification: str


@dataclass(frozen=True)
class ManifestArtifactSummary:
    artifact_id: str
    artifact_type: str
    stage: str
    sha256: str


@dataclass(frozen=True)
class ManifestDecisionSummary:
    decision_id: str
    stage: str
    outcome: str
    decided_by: str
    decided_at: str


@dataclass(frozen=True)
class RunManifest:
    manifest_id: str
    run_id: str
    case_ref: str
    generated_at: str
    generated_by: str
    pipeline_status: str
    stages_completed: tuple[str, ...]
    artifacts_summary: tuple[ManifestArtifactSummary, ...]
    decisions_summary: tuple[ManifestDecisionSummary, ...]
    findings: tuple[ManifestFinding, ...]
    gate_outcome: ManifestGateOutcome | None
    next_steps: tuple[str, ...]
    notes: str
    gate_mode: str = "stub"


@dataclass(frozen=True)
class ManifestSemanticResult:
    manifest: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


def validate_run_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Return schema error messages for a run manifest (empty list == valid)."""

    schema = yaml.safe_load(
        _RUN_MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(manifest)))


_REQUIRED_COMPLETE_STAGES = _MANIFEST_STAGES


def validate_run_manifest_semantics(
    manifest: Mapping[str, Any],
) -> ManifestSemanticResult:
    """Apply semantic rules RM_001-RM_008 to a run manifest.

    Never touches the filesystem and never mutates ``manifest``. ``valid`` is
    ``False`` when any error fires; warnings are always recorded even when
    ``valid`` is ``True``.
    """

    errors: list[str] = []
    warnings: list[str] = []

    manifest_id = manifest.get("manifest_id")
    run_id = manifest.get("run_id")
    pipeline_status = manifest.get("pipeline_status")
    stages_completed = list(manifest.get("stages_completed") or [])
    artifacts_summary = list(manifest.get("artifacts_summary") or [])
    decisions_summary = list(manifest.get("decisions_summary") or [])
    findings = list(manifest.get("findings") or [])
    gate_outcome = manifest.get("gate_outcome")
    next_steps = list(manifest.get("next_steps") or [])

    artifact_ids = {
        artifact.get("artifact_id") for artifact in artifacts_summary
    }
    artifact_stages = {artifact.get("stage") for artifact in artifacts_summary}
    decision_ids = {
        decision.get("decision_id") for decision in decisions_summary
    }

    # RM_001: manifest_id duplicates run_id (same value).
    if manifest_id is not None and manifest_id == run_id:
        errors.append(
            f"RM_001: manifest_id {manifest_id!r} duplicates run_id."
        )

    # RM_002: stage in stages_completed without corresponding artifact.
    for stage in stages_completed:
        if stage not in artifact_stages:
            errors.append(
                f"RM_002: stage {stage!r} in stages_completed has no "
                f"corresponding artifact in artifacts_summary."
            )

    # RM_003: gate_outcome.decision_id absent from decisions_summary.
    if gate_outcome is not None:
        gate_decision_id = gate_outcome.get("decision_id")
        if gate_decision_id not in decision_ids:
            errors.append(
                f"RM_003: gate_outcome.decision_id {gate_decision_id!r} "
                f"not found in decisions_summary."
            )

    # RM_004: pipeline_status complete without all 4 stages.
    if pipeline_status == "complete":
        missing = [
            stage
            for stage in _REQUIRED_COMPLETE_STAGES
            if stage not in stages_completed
        ]
        if missing:
            errors.append(
                f"RM_004: pipeline_status 'complete' but stages_completed is "
                f"missing {missing!r}."
            )

    # RM_005: finding source_artifact_id absent from artifacts_summary.
    for finding in findings:
        source_artifact_id = finding.get("source_artifact_id")
        if source_artifact_id not in artifact_ids:
            errors.append(
                f"RM_005: finding source_artifact_id "
                f"{source_artifact_id!r} not found in artifacts_summary."
            )

    # RM_006: multiple gate_evaluation decisions -> warning.
    gate_decisions = [
        decision
        for decision in decisions_summary
        if decision.get("stage") == "gate_evaluation"
    ]
    if len(gate_decisions) > 1:
        warnings.append(
            f"RM_006: {len(gate_decisions)} decisions in gate_evaluation "
            f"but gate_outcome references only one."
        )

    # RM_007: pipeline_status blocked without any rejected decision -> warning.
    if pipeline_status == "blocked" and not any(
        decision.get("outcome") == "rejected" for decision in decisions_summary
    ):
        warnings.append(
            "RM_007: pipeline_status 'blocked' without any decision with "
            "outcome 'rejected'."
        )

    # RM_008: next_steps empty when pipeline_status is not complete -> warning.
    if pipeline_status != "complete" and not next_steps:
        warnings.append(
            f"RM_008: next_steps is empty but pipeline_status is "
            f"{pipeline_status!r}."
        )

    return ManifestSemanticResult(
        manifest=dict(manifest),
        errors=tuple(errors),
        warnings=tuple(warnings),
        valid=not errors,
    )


def _now_iso() -> str:
    """Return the current UTC instant as an ISO 8601 ``...Z`` timestamp."""

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _derive_pipeline_status(status: Any) -> str:
    """Map a ``WorkspaceRun.status`` to a manifest ``pipeline_status``."""

    return STATUS_MAP.get(status, "incomplete")


def _derive_stages_completed(artifacts: list[Mapping[str, Any]]) -> list[str]:
    """Return manifest stages that have at least one ingested artifact.

    Ordered by :data:`generator.workspace.VALID_STAGES`, excluding the
    ``initialized`` and ``complete`` pseudo-stages.
    """

    present = {artifact.get("stage") for artifact in artifacts}
    return [
        stage
        for stage in VALID_STAGES
        if stage in _MANIFEST_STAGES and stage in present
    ]


def _derive_next_steps(
    pipeline_status: str, stages_completed: list[str]
) -> list[str]:
    """Derive deterministic ``next_steps`` from status and stages."""

    if pipeline_status == "complete":
        return [
            "Pipeline completo. Revisar findings e prosseguir para ISSUE-28.",
        ]
    if pipeline_status == "blocked":
        return [
            "Gate bloqueado. Revisar gate_outcome e registrar decisão de "
            "rollback ou desbloqueio.",
        ]
    if pipeline_status == "rolled_back":
        return ["Run revertida. Reiniciar a partir do stage de rollback."]
    # incomplete: first missing stage in pipeline order.
    if "blind_solve" not in stages_completed:
        return [
            "Ingerir blind_solver_report para avançar para gate_evaluation.",
        ]
    if "gate_evaluation" not in stages_completed:
        return [
            "Ingerir gate_evaluation para avançar para narrative_review.",
        ]
    if "narrative_review" not in stages_completed:
        return [
            "Ingerir narrative_review para avançar para evidence_review.",
        ]
    return ["Ingerir evidence_review para completar a run."]


def build_run_manifest(
    run: Mapping[str, Any],
    manifest_id: str,
    findings_by_artifact: Mapping[str, list[Mapping[str, Any]]] | None = None,
    generated_by: str = "orchestrator",
    notes: str = "",
    generated_at: str | None = None,
    gate_mode: str = "stub",
) -> dict[str, Any]:
    """Build a run manifest dict from a ``WorkspaceRun`` dict.

    ``findings_by_artifact`` maps ``artifact_id`` -> list of finding dicts
    (each with keys ``code``, ``severity``, ``field``, ``message``). The
    ``source_type`` is derived from the artifact's ``artifact_type`` in the
    run. Never mutates ``run`` nor ``findings_by_artifact``.
    """

    run = copy.deepcopy(dict(run))
    findings_by_artifact = copy.deepcopy(dict(findings_by_artifact or {}))

    artifacts = list(run.get("artifacts") or [])
    decisions = list(run.get("decisions") or [])

    pipeline_status = _derive_pipeline_status(run.get("status"))
    stages_completed = _derive_stages_completed(artifacts)

    artifacts_summary = [
        {
            "artifact_id": artifact.get("artifact_id"),
            "artifact_type": artifact.get("artifact_type"),
            "stage": artifact.get("stage"),
            "sha256": artifact.get("sha256"),
        }
        for artifact in artifacts
    ]

    decisions_summary = [
        {
            "decision_id": decision.get("decision_id"),
            "stage": decision.get("stage"),
            "outcome": decision.get("outcome"),
            "decided_by": decision.get("decided_by"),
            "decided_at": decision.get("decided_at"),
        }
        for decision in decisions
    ]

    gate_outcome: dict[str, Any] | None = None
    for decision in decisions:
        if decision.get("stage") == "gate_evaluation":
            gate_outcome = {
                "decision_id": decision.get("decision_id"),
                "outcome": decision.get("outcome"),
                "justification": decision.get("justification"),
            }
            break

    artifact_type_by_id = {
        artifact.get("artifact_id"): artifact.get("artifact_type")
        for artifact in artifacts
    }

    findings: list[dict[str, Any]] = []
    for artifact_id, artifact_findings in findings_by_artifact.items():
        source_type = artifact_type_by_id.get(artifact_id)
        for finding in artifact_findings:
            findings.append(
                {
                    "source_artifact_id": artifact_id,
                    "source_type": source_type,
                    "code": finding.get("code"),
                    "severity": finding.get("severity"),
                    "field": finding.get("field", ""),
                    "message": finding.get("message"),
                }
            )

    next_steps = _derive_next_steps(pipeline_status, stages_completed)

    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "run_id": run.get("run_id"),
        "case_ref": run.get("case_ref"),
        "generated_at": generated_at if generated_at is not None else _now_iso(),
        "generated_by": generated_by,
        "pipeline_status": pipeline_status,
        "stages_completed": stages_completed,
        "artifacts_summary": artifacts_summary,
        "decisions_summary": decisions_summary,
        "findings": findings,
        "gate_outcome": gate_outcome,
        "next_steps": next_steps,
        "notes": notes,
        "gate_mode": gate_mode,
    }


def manifest_to_dict(manifest: RunManifest) -> dict[str, Any]:
    """Serialize a ``RunManifest`` to a dict ready for ``validate_run_manifest``."""

    gate_outcome: dict[str, Any] | None = None
    if manifest.gate_outcome is not None:
        gate_outcome = {
            "decision_id": manifest.gate_outcome.decision_id,
            "outcome": manifest.gate_outcome.outcome,
            "justification": manifest.gate_outcome.justification,
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": manifest.manifest_id,
        "run_id": manifest.run_id,
        "case_ref": manifest.case_ref,
        "generated_at": manifest.generated_at,
        "generated_by": manifest.generated_by,
        "pipeline_status": manifest.pipeline_status,
        "stages_completed": list(manifest.stages_completed),
        "artifacts_summary": [
            {
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "stage": artifact.stage,
                "sha256": artifact.sha256,
            }
            for artifact in manifest.artifacts_summary
        ],
        "decisions_summary": [
            {
                "decision_id": decision.decision_id,
                "stage": decision.stage,
                "outcome": decision.outcome,
                "decided_by": decision.decided_by,
                "decided_at": decision.decided_at,
            }
            for decision in manifest.decisions_summary
        ],
        "findings": [
            {
                "source_artifact_id": finding.source_artifact_id,
                "source_type": finding.source_type,
                "code": finding.code,
                "severity": finding.severity,
                "field": finding.field,
                "message": finding.message,
            }
            for finding in manifest.findings
        ],
        "gate_outcome": gate_outcome,
        "next_steps": list(manifest.next_steps),
        "notes": manifest.notes,
        "gate_mode": manifest.gate_mode,
    }

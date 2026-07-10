"""Multiagent workspace contract (ISSUE-25+26).

This module backs the per-run workspace defined in
``schemas/workspace_run.schema.yaml``. The workspace organizes and tracks one
offline case run without a database: it stores the run identity, status, current
stage, ingested artifacts and human gate decisions. It never executes any agent,
never reads, writes or hashes real files and never mutates the inputs it
receives.

Public surface implemented here:

- :data:`SCHEMA_VERSION`, :data:`VALID_STAGES`, :data:`VALID_STATUSES`,
  :data:`VALID_ARTIFACT_TYPES`, :data:`VALID_OUTCOMES`;
- dataclasses :class:`WorkspaceArtifact`, :class:`WorkspaceDecision`,
  :class:`WorkspaceRun`, :class:`WorkspaceSemanticResult`;
- :func:`validate_workspace_run` — structural validation against the schema;
- :func:`build_workspace_run` — build a minimal initialized run dict;
- :func:`run_to_dict` — serialize a :class:`WorkspaceRun` to a dict;
- :func:`validate_workspace_semantics` — semantic rules WS_001-WS_008.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0"

VALID_STAGES: tuple[str, ...] = (
    "initialized",
    "blind_solve",
    "gate_evaluation",
    "narrative_review",
    "evidence_review",
    "complete",
)

VALID_STATUSES: tuple[str, ...] = (
    "initialized",
    "in_progress",
    "gate_blocked",
    "done",
    "rolled_back",
)

VALID_ARTIFACT_TYPES: tuple[str, ...] = (
    "blind_bundle",
    "blind_solver_report",
    "run_record",
    "gate_evaluation",
    "judge_verdict",
    "narrative_review",
    "evidence_review",
)

VALID_OUTCOMES: tuple[str, ...] = (
    "approved",
    "rejected",
    "rollback",
)

_WORKSPACE_RUN_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "workspace_run.schema.yaml"
)


@dataclass(frozen=True)
class WorkspaceArtifact:
    artifact_id: str
    artifact_type: str
    path: str
    sha256: str
    ingested_at: str
    stage: str
    visible_to: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceDecision:
    decision_id: str
    stage: str
    outcome: str  # "approved" | "rejected" | "rollback"
    justification: str
    decided_at: str
    decided_by: str
    rollback_to_stage: str | None


@dataclass(frozen=True)
class WorkspaceRun:
    run_id: str
    case_ref: str
    created_at: str
    created_by: str
    status: str
    current_stage: str
    artifacts: tuple[WorkspaceArtifact, ...]
    decisions: tuple[WorkspaceDecision, ...]
    notes: str


@dataclass(frozen=True)
class WorkspaceSemanticResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


def _now_iso() -> str:
    """Return the current UTC instant as an ISO 8601 ``...Z`` timestamp."""

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def validate_workspace_run(run: Mapping[str, Any]) -> list[str]:
    """Return schema error messages for a workspace run (empty list == valid)."""

    schema = yaml.safe_load(
        _WORKSPACE_RUN_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(run)))


def build_workspace_run(
    run_id: str,
    case_ref: str,
    created_by: str = "orchestrator",
    notes: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a minimal initialized workspace run dict.

    The run has no artifacts and no decisions; ``status`` and ``current_stage``
    are both ``"initialized"``. ``created_at`` defaults to the current UTC
    instant when not provided.
    """

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "case_ref": case_ref,
        "created_at": created_at if created_at is not None else _now_iso(),
        "created_by": created_by,
        "status": "initialized",
        "current_stage": "initialized",
        "artifacts": [],
        "decisions": [],
        "notes": notes,
    }


def run_to_dict(run: WorkspaceRun) -> dict[str, Any]:
    """Serialize a :class:`WorkspaceRun` to a dict ready for validation."""

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run.run_id,
        "case_ref": run.case_ref,
        "created_at": run.created_at,
        "created_by": run.created_by,
        "status": run.status,
        "current_stage": run.current_stage,
        "artifacts": [
            {
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "path": artifact.path,
                "sha256": artifact.sha256,
                "ingested_at": artifact.ingested_at,
                "stage": artifact.stage,
                "visible_to": list(artifact.visible_to),
            }
            for artifact in run.artifacts
        ],
        "decisions": [
            {
                "decision_id": decision.decision_id,
                "stage": decision.stage,
                "outcome": decision.outcome,
                "justification": decision.justification,
                "decided_at": decision.decided_at,
                "decided_by": decision.decided_by,
                "rollback_to_stage": decision.rollback_to_stage,
            }
            for decision in run.decisions
        ],
        "notes": run.notes,
    }


def validate_workspace_semantics(run: Mapping[str, Any]) -> WorkspaceSemanticResult:
    """Apply semantic rules WS_001-WS_008 to a workspace run.

    Never touches the filesystem and never mutates ``run``. ``valid`` is
    ``False`` when any error fires; warnings are always recorded even when
    ``valid`` is ``True``.
    """

    errors: list[str] = []
    warnings: list[str] = []

    artifacts = list(run.get("artifacts") or [])
    decisions = list(run.get("decisions") or [])

    # WS_001 / WS_002: rollback target consistency per decision.
    for decision in decisions:
        decision_id = decision.get("decision_id")
        outcome = decision.get("outcome")
        rollback_to_stage = decision.get("rollback_to_stage")
        if outcome == "rollback" and rollback_to_stage is None:
            errors.append(
                f"WS_001: decision {decision_id!r} has outcome 'rollback' "
                f"but rollback_to_stage is null."
            )
        if outcome != "rollback" and rollback_to_stage is not None:
            errors.append(
                f"WS_002: decision {decision_id!r} has outcome {outcome!r} "
                f"but rollback_to_stage is {rollback_to_stage!r}."
            )

    # WS_003: duplicate artifact_id.
    seen_artifact_ids: set[str] = set()
    for artifact in artifacts:
        artifact_id = artifact.get("artifact_id")
        if artifact_id in seen_artifact_ids:
            errors.append(
                f"WS_003: duplicate artifact_id {artifact_id!r}."
            )
        else:
            seen_artifact_ids.add(artifact_id)

    # WS_004: duplicate decision_id.
    seen_decision_ids: set[str] = set()
    for decision in decisions:
        decision_id = decision.get("decision_id")
        if decision_id in seen_decision_ids:
            errors.append(
                f"WS_004: duplicate decision_id {decision_id!r}."
            )
        else:
            seen_decision_ids.add(decision_id)

    # WS_005: artifact stage may not be 'initialized' or 'complete'.
    for artifact in artifacts:
        stage = artifact.get("stage")
        if stage in ("initialized", "complete"):
            errors.append(
                f"WS_005: artifact {artifact.get('artifact_id')!r} has "
                f"invalid stage {stage!r}."
            )

    # WS_008: visible_to must not be empty.
    for artifact in artifacts:
        if not (artifact.get("visible_to") or []):
            errors.append(
                f"WS_008: artifact {artifact.get('artifact_id')!r} has empty "
                f"visible_to."
            )

    # WS_006: status done without any approved decision -> warning.
    if run.get("status") == "done" and not any(
        decision.get("outcome") == "approved" for decision in decisions
    ):
        warnings.append(
            "WS_006: status 'done' without any decision with outcome 'approved'."
        )

    # WS_007: status rolled_back with current_stage not 'initialized' -> warning.
    if (
        run.get("status") == "rolled_back"
        and run.get("current_stage") != "initialized"
    ):
        warnings.append(
            f"WS_007: status 'rolled_back' but current_stage is "
            f"{run.get('current_stage')!r}, not 'initialized'."
        )

    return WorkspaceSemanticResult(
        run=dict(run),
        errors=tuple(errors),
        warnings=tuple(warnings),
        valid=not errors,
    )

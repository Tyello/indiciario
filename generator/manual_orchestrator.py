"""Manual Orchestrator for the multiagent workspace (ISSUE-25+26).

This module drives an offline case run step by step on top of the workspace
contract in :mod:`generator.workspace`. It never calls an LLM, never runs an
agent automatically, never reads, writes or hashes real files and never mutates
the inputs it receives. Every public function returns a fresh run dict.

Public surface:

- request dataclasses :class:`IngestRequest`, :class:`TransitionRequest`,
  :class:`DecisionRequest`;
- result dataclasses :class:`OrchestratorResult`, :class:`TransitionResult`;
- :func:`ingest_artifact` — add an artifact (OR_007);
- :func:`record_decision` — record a gate decision (OR_006; status moves to
  ``gate_blocked`` on ``rejected`` and ``rolled_back`` on ``rollback``);
- :func:`transition_stage` — validate and apply a stage transition
  (OR_001-OR_008);
- :func:`validate_orchestrator_transition` — dry-run OR_001-OR_008 check.

The shared dataclasses :class:`WorkspaceArtifact`, :class:`WorkspaceDecision`,
:class:`WorkspaceRun` and :class:`WorkspaceSemanticResult` are imported from
:mod:`generator.workspace` and never duplicated here.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from generator.workspace import (  # noqa: F401  (re-exported shared dataclasses)
    WorkspaceArtifact,
    WorkspaceDecision,
    WorkspaceRun,
    WorkspaceSemanticResult,
)


@dataclass(frozen=True)
class IngestRequest:
    run: Mapping[str, Any]
    artifact_id: str
    artifact_type: str
    path: str
    sha256: str
    stage: str
    visible_to: tuple[str, ...]
    ingested_at: str | None = None


@dataclass(frozen=True)
class TransitionRequest:
    run: Mapping[str, Any]
    from_stage: str
    to_stage: str


@dataclass(frozen=True)
class DecisionRequest:
    run: Mapping[str, Any]
    decision_id: str
    stage: str
    outcome: str  # "approved" | "rejected" | "rollback"
    justification: str
    decided_by: str
    rollback_to_stage: str | None = None
    decided_at: str | None = None


@dataclass(frozen=True)
class OrchestratorResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


@dataclass(frozen=True)
class TransitionResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


# Ordered active stages of the pipeline used to derive transited history.
_STAGE_ORDER: tuple[str, ...] = (
    "initialized",
    "blind_solve",
    "gate_evaluation",
    "narrative_review",
    "evidence_review",
    "complete",
)


def _now_iso() -> str:
    """Return the current UTC instant as an ISO 8601 ``...Z`` timestamp."""

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _copy_run(run: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deep copy of ``run`` so callers' input is never mutated."""

    return copy.deepcopy(dict(run))


def _has_artifact_type(
    run: Mapping[str, Any],
    artifact_type: str,
    stage: str | None = None,
) -> bool:
    """True if any ingested artifact matches ``artifact_type``.

    When ``stage`` is given, the artifact must also sit at that ``stage``.
    """

    return any(
        artifact.get("artifact_type") == artifact_type
        and (stage is None or artifact.get("stage") == stage)
        for artifact in (run.get("artifacts") or [])
    )


def _has_approved_decision_at(run: Mapping[str, Any], stage: str) -> bool:
    """True if a decision with outcome ``approved`` exists at ``stage``."""

    return any(
        decision.get("stage") == stage and decision.get("outcome") == "approved"
        for decision in (run.get("decisions") or [])
    )


def _has_unblock_decision(run: Mapping[str, Any]) -> bool:
    """True if a decision exists that unblocks a ``gate_blocked`` run.

    A run leaves ``gate_blocked`` only through an explicit ``rollback`` decision
    or a fresh ``approved`` decision recorded at ``gate_evaluation``.
    """

    return any(
        decision.get("outcome") in ("rollback", "approved")
        for decision in (run.get("decisions") or [])
    )


def _transited_stages(run: Mapping[str, Any]) -> set[str]:
    """Return the set of stages already transited up to ``current_stage``.

    History is derived from the linear pipeline order: every stage at or before
    ``current_stage`` counts as transited.
    """

    current_stage = run.get("current_stage")
    if current_stage not in _STAGE_ORDER:
        return {current_stage} if current_stage is not None else set()
    cutoff = _STAGE_ORDER.index(current_stage)
    return set(_STAGE_ORDER[: cutoff + 1])


def validate_orchestrator_transition(
    run: Mapping[str, Any],
    from_stage: str,
    to_stage: str,
) -> TransitionResult:
    """Apply OR_001-OR_008 to a proposed transition without mutating ``run``."""

    errors: list[str] = []
    warnings: list[str] = []

    current_stage = run.get("current_stage")

    # OR_001: requested transition must start from current_stage.
    if from_stage != current_stage:
        errors.append(
            f"OR_001: from_stage {from_stage!r} differs from current_stage "
            f"{current_stage!r}."
        )

    # OR_008: leaving gate_blocked requires an explicit rollback/unblock decision.
    if from_stage == "gate_blocked" or run.get("status") == "gate_blocked":
        if not _has_unblock_decision(run):
            errors.append(
                "OR_008: cannot advance from 'gate_blocked' without an explicit "
                "rollback or unblock decision."
            )

    # OR_002: gate_evaluation requires an ingested run_record artifact.
    if to_stage == "gate_evaluation" and not _has_artifact_type(run, "run_record"):
        errors.append(
            "OR_002: cannot advance to 'gate_evaluation' without an ingested "
            "'run_record' artifact."
        )

    # OR_003: narrative_review requires an approved decision at gate_evaluation.
    if to_stage == "narrative_review" and not _has_approved_decision_at(
        run, "gate_evaluation"
    ):
        errors.append(
            "OR_003: cannot advance to 'narrative_review' without an 'approved' "
            "decision at 'gate_evaluation'."
        )

    # OR_004: evidence_review requires an ingested narrative_review artifact.
    if to_stage == "evidence_review" and not _has_artifact_type(
        run, "narrative_review"
    ):
        errors.append(
            "OR_004: cannot advance to 'evidence_review' without an ingested "
            "'narrative_review' artifact."
        )

    # OR_005: complete requires an ingested evidence_review artifact.
    if to_stage == "complete" and not _has_artifact_type(run, "evidence_review"):
        errors.append(
            "OR_005: cannot advance to 'complete' without an ingested "
            "'evidence_review' artifact."
        )

    return TransitionResult(
        run=_copy_run(run),
        errors=tuple(errors),
        warnings=tuple(warnings),
        valid=not errors,
    )


def transition_stage(request: TransitionRequest) -> TransitionResult:
    """Validate and apply a stage transition (OR_001-OR_008).

    Never mutates ``request.run``. When the transition is valid, the returned
    run dict has ``current_stage`` updated to ``to_stage``.
    """

    check = validate_orchestrator_transition(
        request.run, request.from_stage, request.to_stage
    )
    new_run = _copy_run(request.run)
    if check.valid:
        new_run["current_stage"] = request.to_stage

    return TransitionResult(
        run=new_run,
        errors=check.errors,
        warnings=check.warnings,
        valid=check.valid,
    )


def ingest_artifact(request: IngestRequest) -> OrchestratorResult:
    """Add an artifact to the run state (OR_007).

    Never mutates ``request.run``. A duplicate ``artifact_id`` is not re-added;
    ingesting an ``artifact_type`` already present for the same ``stage`` raises
    an OR_007 warning but does not block (``valid`` stays ``True``).
    """

    errors: list[str] = []
    warnings: list[str] = []

    new_run = _copy_run(request.run)
    artifacts = new_run.get("artifacts") or []

    existing_ids = {artifact.get("artifact_id") for artifact in artifacts}

    # OR_007: same artifact_type already present at the same stage -> warning.
    if _has_artifact_type(new_run, request.artifact_type, request.stage):
        warnings.append(
            f"OR_007: artifact_type {request.artifact_type!r} already present "
            f"at stage {request.stage!r}."
        )

    if request.artifact_id not in existing_ids:
        artifacts.append(
            {
                "artifact_id": request.artifact_id,
                "artifact_type": request.artifact_type,
                "path": request.path,
                "sha256": request.sha256,
                "ingested_at": request.ingested_at
                if request.ingested_at is not None
                else _now_iso(),
                "stage": request.stage,
                "visible_to": list(request.visible_to),
            }
        )

    new_run["artifacts"] = artifacts

    if new_run.get("status") == "initialized":
        new_run["status"] = "in_progress"

    return OrchestratorResult(
        run=new_run,
        errors=tuple(errors),
        warnings=tuple(warnings),
        valid=not errors,
    )


def record_decision(request: DecisionRequest) -> OrchestratorResult:
    """Record a gate decision in the run state (OR_006).

    Never mutates ``request.run``. ``status`` moves to ``gate_blocked`` when the
    outcome is ``rejected`` and to ``rolled_back`` when the outcome is
    ``rollback``. Recording a decision at a stage outside the transited history
    raises an OR_006 warning but does not block (``valid`` stays ``True``).
    """

    errors: list[str] = []
    warnings: list[str] = []

    new_run = _copy_run(request.run)
    decisions = new_run.get("decisions") or []

    # OR_006: decision at a stage not in the transited history -> warning.
    if request.stage not in _transited_stages(request.run):
        warnings.append(
            f"OR_006: decision recorded at stage {request.stage!r} which is not "
            f"in the transited stage history."
        )

    decisions.append(
        {
            "decision_id": request.decision_id,
            "stage": request.stage,
            "outcome": request.outcome,
            "justification": request.justification,
            "decided_at": request.decided_at
            if request.decided_at is not None
            else _now_iso(),
            "decided_by": request.decided_by,
            "rollback_to_stage": request.rollback_to_stage,
        }
    )
    new_run["decisions"] = decisions

    if request.outcome == "rejected":
        new_run["status"] = "gate_blocked"
    elif request.outcome == "rollback":
        new_run["status"] = "rolled_back"

    return OrchestratorResult(
        run=new_run,
        errors=tuple(errors),
        warnings=tuple(warnings),
        valid=not errors,
    )

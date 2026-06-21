"""RED tests for the Manual Orchestrator (ISSUE-25+26, STEP-08).

These tests describe cases 51-85 of the ISSUE-25+26 spec:

- 51-58: rules OR_001-OR_008
- 59-68: ``ingest_artifact``
- 69-76: ``record_decision``
- 77-85: ``transition_stage``

They are expected to FAIL (RED) until ``generator/manual_orchestrator.py``
exists. The import of that module at the top of this file makes the whole
module fail to collect with ``ModuleNotFoundError: No module named
'generator.manual_orchestrator'``; that missing module is the RED target of
this step. No implementation is provided here (STEP-09 turns it GREEN).
"""

from __future__ import annotations

import copy
from typing import Any

from generator.manual_orchestrator import (
    DecisionRequest,
    IngestRequest,
    OrchestratorResult,
    TransitionRequest,
    TransitionResult,
    ingest_artifact,
    record_decision,
    transition_stage,
    validate_orchestrator_transition,
)
from generator.workspace import (
    SCHEMA_VERSION,
    validate_workspace_run,
)


def _base_artifact(**overrides: Any) -> dict[str, Any]:
    artifact = {
        "artifact_id": "BUNDLE-001",
        "artifact_type": "blind_bundle",
        "path": "workspace/run-001/artifacts/bundle-001/",
        "sha256": "a" * 64,
        "ingested_at": "2026-06-20T10:05:00Z",
        "stage": "blind_solve",
        "visible_to": ["blind_solver"],
    }
    artifact.update(overrides)
    return artifact


def _base_decision(**overrides: Any) -> dict[str, Any]:
    decision = {
        "decision_id": "DEC-001",
        "stage": "gate_evaluation",
        "outcome": "approved",
        "justification": "Conclusao esperada atingida com evidencia suficiente.",
        "decided_at": "2026-06-20T11:00:00Z",
        "decided_by": "human",
        "rollback_to_stage": None,
    }
    decision.update(overrides)
    return decision


def _run(
    *,
    status: str = "in_progress",
    current_stage: str = "blind_solve",
    artifacts: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "RUN-20260620-001",
        "case_ref": "examples/caso_canonico_intermediario.json",
        "created_at": "2026-06-20T10:00:00Z",
        "created_by": "orchestrator",
        "status": status,
        "current_stage": current_stage,
        "artifacts": artifacts if artifacts is not None else [],
        "decisions": decisions if decisions is not None else [],
        "notes": notes,
    }


def _codes(result: Any) -> list[str]:
    return [
        message.split(":", 1)[0].strip()
        for message in (*result.errors, *result.warnings)
    ]


# === Cases 51-58: rules OR_001-OR_008 ========================================


# --- Case 51: blind_solve -> gate_evaluation without run_record -> OR_002 ----


def test_or_002_advance_to_gate_evaluation_without_run_record() -> None:
    run = _run(current_stage="blind_solve", artifacts=[_base_artifact()])
    result = validate_orchestrator_transition(
        run, "blind_solve", "gate_evaluation"
    )
    assert "OR_002" in " ".join(result.errors)
    assert result.valid is False


# --- Case 52: gate_evaluation -> narrative_review without approved -> OR_003 --


def test_or_003_advance_to_narrative_review_without_approved() -> None:
    run = _run(
        current_stage="gate_evaluation",
        artifacts=[
            _base_artifact(
                artifact_id="RR-001",
                artifact_type="run_record",
                stage="blind_solve",
            ),
        ],
        decisions=[
            _base_decision(stage="gate_evaluation", outcome="rejected"),
        ],
    )
    result = validate_orchestrator_transition(
        run, "gate_evaluation", "narrative_review"
    )
    assert "OR_003" in " ".join(result.errors)
    assert result.valid is False


# --- Case 53: narrative_review -> evidence_review without artifact -> OR_004 --


def test_or_004_advance_to_evidence_review_without_narrative_artifact() -> None:
    run = _run(
        current_stage="narrative_review",
        artifacts=[
            _base_artifact(
                artifact_id="RR-001",
                artifact_type="run_record",
                stage="blind_solve",
            ),
        ],
    )
    result = validate_orchestrator_transition(
        run, "narrative_review", "evidence_review"
    )
    assert "OR_004" in " ".join(result.errors)
    assert result.valid is False


# --- Case 54: evidence_review -> complete without artifact -> OR_005 ---------


def test_or_005_advance_to_complete_without_evidence_artifact() -> None:
    run = _run(
        current_stage="evidence_review",
        artifacts=[
            _base_artifact(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
            ),
        ],
    )
    result = validate_orchestrator_transition(
        run, "evidence_review", "complete"
    )
    assert "OR_005" in " ".join(result.errors)
    assert result.valid is False


# --- Case 55: gate_blocked -> narrative_review without rollback/unblock ------


def test_or_008_advance_from_gate_blocked_without_decision() -> None:
    run = _run(
        status="gate_blocked",
        current_stage="gate_blocked",
    )
    result = validate_orchestrator_transition(
        run, "gate_blocked", "narrative_review"
    )
    assert "OR_008" in " ".join(result.errors)
    assert result.valid is False


# --- Case 56: ingest_artifact with type already present at stage -> OR_007 ----


def test_or_007_ingest_duplicate_type_at_stage_is_warning() -> None:
    run = _run(
        artifacts=[
            _base_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
        ],
    )
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-002",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-002/",
        sha256="b" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    result = ingest_artifact(request)
    assert "OR_007" in " ".join(result.warnings)
    assert result.valid is True


# --- Case 57: record_decision at stage not in transited history -> OR_006 ----


def test_or_006_decision_at_untransited_stage_is_warning() -> None:
    run = _run(current_stage="blind_solve")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="evidence_review",
        outcome="approved",
        justification="Decisao em etapa nao transitada.",
        decided_by="human",
    )
    result = record_decision(request)
    assert "OR_006" in " ".join(result.warnings)
    assert result.valid is True


# --- Case 58: transition_stage with from_stage != current_stage -> OR_001 ----


def test_or_001_transition_with_wrong_from_stage_is_error() -> None:
    run = _run(current_stage="blind_solve")
    request = TransitionRequest(
        run=run,
        from_stage="gate_evaluation",
        to_stage="narrative_review",
    )
    result = transition_stage(request)
    assert "OR_001" in " ".join(result.errors)
    assert result.valid is False


# === Cases 59-68: ingest_artifact ============================================


# --- Case 59: ingest_artifact adds artifact to returned dict -----------------


def test_ingest_artifact_adds_artifact() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    result = ingest_artifact(request)
    ids = [a["artifact_id"] for a in result.run["artifacts"]]
    assert "BUNDLE-001" in ids


# --- Case 60: ingest_artifact moves status initialized -> in_progress --------


def test_ingest_artifact_promotes_status_from_initialized() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    result = ingest_artifact(request)
    assert result.run["status"] == "in_progress"


# --- Case 61: ingest_artifact does not mutate request.run --------------------


def test_ingest_artifact_does_not_mutate_input() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    snapshot = copy.deepcopy(run)
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    ingest_artifact(request)
    assert run == snapshot


# --- Case 62: ingest_artifact auto-generates ingested_at if missing ----------


def test_ingest_artifact_auto_ingested_at() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
        ingested_at=None,
    )
    result = ingest_artifact(request)
    ingested = result.run["artifacts"][-1]["ingested_at"]
    assert isinstance(ingested, str)
    assert ingested != ""


# --- Case 63: ingest_artifact OR_007 returns valid True (warning) ------------


def test_ingest_artifact_or_007_does_not_block() -> None:
    run = _run(
        artifacts=[
            _base_artifact(artifact_id="BUNDLE-001", stage="blind_solve"),
        ],
    )
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-002",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-002/",
        sha256="b" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    result = ingest_artifact(request)
    assert result.valid is True


# --- Case 64: run returned by ingest_artifact passes validate_workspace_run --


def test_ingest_artifact_result_passes_schema() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
        ingested_at="2026-06-20T10:05:00Z",
    )
    result = ingest_artifact(request)
    assert validate_workspace_run(result.run) == []


# --- Case 65: two sequential ingest_artifact accumulate artifacts ------------


def test_two_sequential_ingests_accumulate() -> None:
    run = _run(status="initialized", current_stage="blind_solve", artifacts=[])
    first = ingest_artifact(
        IngestRequest(
            run=run,
            artifact_id="BUNDLE-001",
            artifact_type="blind_bundle",
            path="workspace/run-001/artifacts/bundle-001/",
            sha256="a" * 64,
            stage="blind_solve",
            visible_to=("blind_solver",),
            ingested_at="2026-06-20T10:05:00Z",
        )
    )
    second = ingest_artifact(
        IngestRequest(
            run=first.run,
            artifact_id="RR-001",
            artifact_type="run_record",
            path="workspace/run-001/artifacts/rr-001/",
            sha256="c" * 64,
            stage="blind_solve",
            visible_to=("orchestrator",),
            ingested_at="2026-06-20T10:10:00Z",
        )
    )
    ids = [a["artifact_id"] for a in second.run["artifacts"]]
    assert ids == ["BUNDLE-001", "RR-001"]


# --- Case 66: ingest_artifact preserves existing decisions -------------------


def test_ingest_artifact_preserves_decisions() -> None:
    run = _run(
        current_stage="gate_evaluation",
        decisions=[_base_decision(decision_id="DEC-001")],
    )
    request = IngestRequest(
        run=run,
        artifact_id="GE-001",
        artifact_type="gate_evaluation",
        path="workspace/run-001/artifacts/ge-001/",
        sha256="d" * 64,
        stage="gate_evaluation",
        visible_to=("gate_evaluator",),
    )
    result = ingest_artifact(request)
    decision_ids = [d["decision_id"] for d in result.run["decisions"]]
    assert "DEC-001" in decision_ids


# --- Case 67: ingest_artifact preserves current_stage and run_id ------------


def test_ingest_artifact_preserves_stage_and_run_id() -> None:
    run = _run(current_stage="gate_evaluation")
    request = IngestRequest(
        run=run,
        artifact_id="GE-001",
        artifact_type="gate_evaluation",
        path="workspace/run-001/artifacts/ge-001/",
        sha256="d" * 64,
        stage="gate_evaluation",
        visible_to=("gate_evaluator",),
    )
    result = ingest_artifact(request)
    assert result.run["current_stage"] == "gate_evaluation"
    assert result.run["run_id"] == run["run_id"]


# --- Case 68: duplicate artifact_id -> OR_007 warning, NOT re-added ----------


def test_ingest_duplicate_artifact_id_not_readded() -> None:
    run = _run(
        artifacts=[
            _base_artifact(artifact_id="BUNDLE-001", stage="blind_solve"),
        ],
    )
    request = IngestRequest(
        run=run,
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    result = ingest_artifact(request)
    ids = [a["artifact_id"] for a in result.run["artifacts"]]
    assert ids.count("BUNDLE-001") == 1
    assert "OR_007" in " ".join(result.warnings)


# === Cases 69-76: record_decision ============================================


# --- Case 69: record_decision approved -> decision added ---------------------


def test_record_decision_approved_adds_decision() -> None:
    run = _run(current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao atingida.",
        decided_by="human",
    )
    result = record_decision(request)
    ids = [d["decision_id"] for d in result.run["decisions"]]
    assert "DEC-001" in ids


# --- Case 70: record_decision does not mutate request.run -------------------


def test_record_decision_does_not_mutate_input() -> None:
    run = _run(current_stage="gate_evaluation")
    snapshot = copy.deepcopy(run)
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao atingida.",
        decided_by="human",
    )
    record_decision(request)
    assert run == snapshot


# --- Case 71: record_decision rejected -> status gate_blocked ---------------


def test_record_decision_rejected_sets_gate_blocked() -> None:
    run = _run(status="in_progress", current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="rejected",
        justification="Conclusao nao atingida.",
        decided_by="human",
    )
    result = record_decision(request)
    assert result.run["status"] == "gate_blocked"


# --- Case 72: record_decision approved -> status NOT gate_blocked ------------


def test_record_decision_approved_keeps_status() -> None:
    run = _run(status="in_progress", current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao atingida.",
        decided_by="human",
    )
    result = record_decision(request)
    assert result.run["status"] != "gate_blocked"


# --- Case 73: record_decision rollback -> status rolled_back ----------------


def test_record_decision_rollback_sets_rolled_back() -> None:
    run = _run(status="in_progress", current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="rollback",
        justification="Necessario refazer etapa anterior.",
        decided_by="human",
        rollback_to_stage="blind_solve",
    )
    result = record_decision(request)
    assert result.run["status"] == "rolled_back"


# --- Case 74: record_decision auto-generates decided_at if missing ----------


def test_record_decision_auto_decided_at() -> None:
    run = _run(current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao atingida.",
        decided_by="human",
        decided_at=None,
    )
    result = record_decision(request)
    decided = result.run["decisions"][-1]["decided_at"]
    assert isinstance(decided, str)
    assert decided != ""


# --- Case 75: run returned by record_decision passes validate_workspace_run --


def test_record_decision_result_passes_schema() -> None:
    run = _run(current_stage="gate_evaluation")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao atingida.",
        decided_by="human",
        decided_at="2026-06-20T11:00:00Z",
    )
    result = record_decision(request)
    assert validate_workspace_run(result.run) == []


# --- Case 76: record_decision OR_006 warning does not block (valid=True) -----


def test_record_decision_or_006_does_not_block() -> None:
    run = _run(current_stage="blind_solve")
    request = DecisionRequest(
        run=run,
        decision_id="DEC-001",
        stage="evidence_review",
        outcome="approved",
        justification="Decisao em etapa nao transitada.",
        decided_by="human",
    )
    result = record_decision(request)
    assert "OR_006" in " ".join(result.warnings)
    assert result.valid is True


# === Cases 77-85: transition_stage ===========================================


# --- Case 77: initialized -> blind_solve is valid (no artifact prereq) -------


def test_transition_initialized_to_blind_solve_is_valid() -> None:
    run = _run(status="initialized", current_stage="initialized")
    request = TransitionRequest(
        run=run,
        from_stage="initialized",
        to_stage="blind_solve",
    )
    result = transition_stage(request)
    assert result.valid is True


# --- Case 78: blind_solve -> gate_evaluation with run_record is valid --------


def test_transition_blind_solve_to_gate_evaluation_with_run_record() -> None:
    run = _run(
        current_stage="blind_solve",
        artifacts=[
            _base_artifact(
                artifact_id="RR-001",
                artifact_type="run_record",
                stage="blind_solve",
            ),
        ],
    )
    request = TransitionRequest(
        run=run,
        from_stage="blind_solve",
        to_stage="gate_evaluation",
    )
    result = transition_stage(request)
    assert result.valid is True


# --- Case 79: gate_evaluation -> narrative_review with approved is valid -----


def test_transition_gate_evaluation_to_narrative_review_with_approved() -> None:
    run = _run(
        current_stage="gate_evaluation",
        artifacts=[
            _base_artifact(
                artifact_id="RR-001",
                artifact_type="run_record",
                stage="blind_solve",
            ),
        ],
        decisions=[
            _base_decision(stage="gate_evaluation", outcome="approved"),
        ],
    )
    request = TransitionRequest(
        run=run,
        from_stage="gate_evaluation",
        to_stage="narrative_review",
    )
    result = transition_stage(request)
    assert result.valid is True


# --- Case 80: narrative_review -> evidence_review with artifact is valid -----


def test_transition_narrative_review_to_evidence_review_with_artifact() -> None:
    run = _run(
        current_stage="narrative_review",
        artifacts=[
            _base_artifact(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
            ),
        ],
    )
    request = TransitionRequest(
        run=run,
        from_stage="narrative_review",
        to_stage="evidence_review",
    )
    result = transition_stage(request)
    assert result.valid is True


# --- Case 81: evidence_review -> complete with artifact is valid -------------


def test_transition_evidence_review_to_complete_with_artifact() -> None:
    run = _run(
        current_stage="evidence_review",
        artifacts=[
            _base_artifact(
                artifact_id="ER-001",
                artifact_type="evidence_review",
                stage="evidence_review",
            ),
        ],
    )
    request = TransitionRequest(
        run=run,
        from_stage="evidence_review",
        to_stage="complete",
    )
    result = transition_stage(request)
    assert result.valid is True


# --- Case 82: transition_stage does not mutate request.run ------------------


def test_transition_stage_does_not_mutate_input() -> None:
    run = _run(status="initialized", current_stage="initialized")
    snapshot = copy.deepcopy(run)
    request = TransitionRequest(
        run=run,
        from_stage="initialized",
        to_stage="blind_solve",
    )
    transition_stage(request)
    assert run == snapshot


# --- Case 83: transition_stage with wrong from_stage -> OR_001 error ---------


def test_transition_stage_wrong_from_stage_is_invalid() -> None:
    run = _run(current_stage="blind_solve")
    request = TransitionRequest(
        run=run,
        from_stage="gate_evaluation",
        to_stage="narrative_review",
    )
    result = transition_stage(request)
    assert "OR_001" in " ".join(result.errors)
    assert result.valid is False


# --- Case 84: transition_stage updates current_stage when valid -------------


def test_transition_stage_updates_current_stage() -> None:
    run = _run(status="initialized", current_stage="initialized")
    request = TransitionRequest(
        run=run,
        from_stage="initialized",
        to_stage="blind_solve",
    )
    result = transition_stage(request)
    assert result.run["current_stage"] == "blind_solve"


# --- Case 85: transition_stage result passes validate_workspace_run ---------


def test_transition_stage_result_passes_schema() -> None:
    run = _run(status="initialized", current_stage="initialized")
    request = TransitionRequest(
        run=run,
        from_stage="initialized",
        to_stage="blind_solve",
    )
    result = transition_stage(request)
    assert validate_workspace_run(result.run) == []


# --- guard: result types and dry-run helper are exposed ----------------------


def test_result_types_are_exposed() -> None:
    assert OrchestratorResult is not None
    assert TransitionResult is not None

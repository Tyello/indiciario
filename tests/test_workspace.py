"""RED tests for workspace semantics and helpers (ISSUE-25+26, STEP-06).

These tests describe cases 21-50 of the ISSUE-25+26 spec:

- 21-28: semantic rules WS_001-WS_008
- 29-36: ``validate_workspace_semantics`` result behavior
- 37-44: ``build_workspace_run`` and ``validate_workspace_run``
- 45-50: integration and edge cases

They are expected to FAIL (RED) until ``generator/workspace.py`` provides
``validate_workspace_semantics``. The import of that symbol at module top makes
the whole module fail to collect with ImportError while the function is absent;
that missing symbol is the RED target of this step. The cases that only exercise
``build_workspace_run`` / ``validate_workspace_run`` / ``run_to_dict`` would pass
on their own once the import resolves, which is expected and handled in STEP-07.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.workspace import (
    SCHEMA_VERSION,
    VALID_ARTIFACT_TYPES,
    VALID_OUTCOMES,
    VALID_STAGES,
    VALID_STATUSES,
    WorkspaceArtifact,
    WorkspaceDecision,
    WorkspaceRun,
    WorkspaceSemanticResult,
    build_workspace_run,
    run_to_dict,
    validate_workspace_run,
    validate_workspace_semantics,
)

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "workspace_run"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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


def _codes(result: WorkspaceSemanticResult) -> list[str]:
    return [
        message.split(":", 1)[0].strip()
        for message in (*result.errors, *result.warnings)
    ]


# === Cases 21-28: rules WS_001-WS_008 ========================================


# --- Case 21: rollback decision with null target -> WS_001 error -------------


def test_ws_001_rollback_with_null_target_is_error() -> None:
    run = _run(
        status="rolled_back",
        current_stage="initialized",
        decisions=[
            _base_decision(outcome="rollback", rollback_to_stage=None),
        ],
    )
    result = validate_workspace_semantics(run)
    assert any(code == "WS_001" for code in _codes(result))
    assert "WS_001" in " ".join(result.errors)
    assert result.valid is False


# --- Case 22: non-rollback decision with non-null target -> WS_002 error -----


def test_ws_002_non_rollback_with_target_is_error() -> None:
    run = _run(
        decisions=[
            _base_decision(outcome="approved", rollback_to_stage="blind_solve"),
        ],
    )
    result = validate_workspace_semantics(run)
    assert "WS_002" in " ".join(result.errors)
    assert result.valid is False


# --- Case 23: two artifacts with same artifact_id -> WS_003 error ------------


def test_ws_003_duplicate_artifact_id_is_error() -> None:
    run = _run(
        artifacts=[
            _base_artifact(artifact_id="DUP-001"),
            _base_artifact(
                artifact_id="DUP-001",
                artifact_type="run_record",
                stage="gate_evaluation",
            ),
        ],
    )
    result = validate_workspace_semantics(run)
    assert "WS_003" in " ".join(result.errors)
    assert result.valid is False


# --- Case 24: two decisions with same decision_id -> WS_004 error ------------


def test_ws_004_duplicate_decision_id_is_error() -> None:
    run = _run(
        decisions=[
            _base_decision(decision_id="DEC-DUP"),
            _base_decision(decision_id="DEC-DUP", outcome="rejected"),
        ],
    )
    result = validate_workspace_semantics(run)
    assert "WS_004" in " ".join(result.errors)
    assert result.valid is False


# --- Case 25: artifact with stage "initialized" -> WS_005 error --------------


def test_ws_005_artifact_stage_initialized_is_error() -> None:
    run = _run(artifacts=[_base_artifact(stage="initialized")])
    result = validate_workspace_semantics(run)
    assert "WS_005" in " ".join(result.errors)
    assert result.valid is False


# --- Case 26: artifact with stage "complete" -> WS_005 error -----------------


def test_ws_005_artifact_stage_complete_is_error() -> None:
    run = _run(artifacts=[_base_artifact(stage="complete")])
    result = validate_workspace_semantics(run)
    assert "WS_005" in " ".join(result.errors)
    assert result.valid is False


# --- Case 27: status done without approved decision -> WS_006 warning --------


def test_ws_006_done_without_approved_is_warning() -> None:
    run = _run(
        status="done",
        current_stage="complete",
        decisions=[_base_decision(outcome="rejected")],
    )
    result = validate_workspace_semantics(run)
    assert "WS_006" in " ".join(result.warnings)
    assert result.valid is True


# --- Case 28: status rolled_back, current_stage not initialized -> WS_007 ----


def test_ws_007_rolled_back_non_initialized_is_warning() -> None:
    run = _run(status="rolled_back", current_stage="blind_solve")
    result = validate_workspace_semantics(run)
    assert "WS_007" in " ".join(result.warnings)
    assert result.valid is True


# === Cases 29-36: validate_workspace_semantics result behavior ===============


# --- Case 29: empty visible_to -> WS_008 error (valid=False) -----------------


def test_ws_008_empty_visible_to_is_error() -> None:
    run = _run(artifacts=[_base_artifact(visible_to=[])])
    result = validate_workspace_semantics(run)
    assert "WS_008" in " ".join(result.errors)
    assert result.valid is False


# --- Case 30: run without semantic errors -> valid True, errors empty --------


def test_clean_run_is_valid_with_no_errors() -> None:
    run = _run(
        artifacts=[_base_artifact()],
        decisions=[_base_decision()],
    )
    result = validate_workspace_semantics(run)
    assert result.valid is True
    assert result.errors == ()


# --- Case 31: run with WS_001 error -> valid False ---------------------------


def test_ws_001_makes_run_invalid() -> None:
    run = _run(
        decisions=[_base_decision(outcome="rollback", rollback_to_stage=None)],
    )
    result = validate_workspace_semantics(run)
    assert result.valid is False


# --- Case 32: run with only WS_006 warning -> valid True, warnings non-empty -


def test_only_ws_006_warning_keeps_valid_true() -> None:
    run = _run(
        status="done",
        current_stage="complete",
        decisions=[_base_decision(outcome="rejected")],
    )
    result = validate_workspace_semantics(run)
    assert result.valid is True
    assert result.warnings != ()


# --- Case 33: multiple errors accumulated in one validation ------------------


def test_multiple_errors_accumulate() -> None:
    run = _run(
        artifacts=[
            _base_artifact(artifact_id="DUP", stage="initialized"),
            _base_artifact(
                artifact_id="DUP",
                artifact_type="run_record",
                stage="gate_evaluation",
            ),
        ],
    )
    result = validate_workspace_semantics(run)
    codes = _codes(result)
    assert "WS_003" in codes
    assert "WS_005" in codes
    assert result.valid is False
    assert len(result.errors) >= 2


# --- Case 34: warnings accumulated together with valid True ------------------


def test_warnings_accumulate_with_valid_true() -> None:
    run = _run(
        status="rolled_back",
        current_stage="blind_solve",
        decisions=[_base_decision(outcome="rejected")],
    )
    # rolled_back + non-initialized -> WS_007 warning; no errors expected.
    result = validate_workspace_semantics(run)
    assert "WS_007" in " ".join(result.warnings)
    assert result.valid is True
    assert result.warnings != ()


# --- Case 35: empty run (no artifacts, no decisions) -> semantically valid ---


def test_empty_run_is_semantically_valid() -> None:
    run = _run(status="initialized", current_stage="initialized")
    result = validate_workspace_semantics(run)
    assert result.valid is True
    assert result.errors == ()


# --- Case 36: two different errors in sequence (WS_003 + WS_004) -------------


def test_ws_003_and_ws_004_together() -> None:
    run = _run(
        artifacts=[
            _base_artifact(artifact_id="DUP-A"),
            _base_artifact(
                artifact_id="DUP-A",
                artifact_type="run_record",
                stage="gate_evaluation",
            ),
        ],
        decisions=[
            _base_decision(decision_id="DEC-DUP"),
            _base_decision(decision_id="DEC-DUP", outcome="rejected"),
        ],
    )
    result = validate_workspace_semantics(run)
    codes = _codes(result)
    assert "WS_003" in codes
    assert "WS_004" in codes
    assert result.valid is False


# === Cases 37-44: build_workspace_run and validate_workspace_run =============


# --- Case 37: build_workspace_run -> status initialized ----------------------


def test_build_workspace_run_status_initialized() -> None:
    run = build_workspace_run("RUN-001", "examples/caso.json")
    assert run["status"] == "initialized"


# --- Case 38: build_workspace_run -> current_stage initialized ---------------


def test_build_workspace_run_current_stage_initialized() -> None:
    run = build_workspace_run("RUN-001", "examples/caso.json")
    assert run["current_stage"] == "initialized"


# --- Case 39: build_workspace_run -> empty artifacts and decisions -----------


def test_build_workspace_run_empty_collections() -> None:
    run = build_workspace_run("RUN-001", "examples/caso.json")
    assert run["artifacts"] == []
    assert run["decisions"] == []


# --- Case 40: build_workspace_run passes validate_workspace_run --------------


def test_build_workspace_run_passes_schema() -> None:
    run = build_workspace_run(
        "RUN-001",
        "examples/caso.json",
        created_at="2026-06-20T10:00:00Z",
    )
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 41: validate_workspace_run returns empty list for valid run --------


def test_validate_workspace_run_empty_for_valid() -> None:
    run = _load_fixture("valid", "valid_initialized.yaml")
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 42: validate_workspace_run returns errors for run without run_id ----


def test_validate_workspace_run_errors_without_run_id() -> None:
    run = _load_fixture("valid", "valid_initialized.yaml")
    run.pop("run_id")
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 43: run_to_dict serializes WorkspaceRun with artifacts/decisions ----


def test_run_to_dict_serializes_collections() -> None:
    artifact = WorkspaceArtifact(
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        ingested_at="2026-06-20T10:05:00Z",
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    decision = WorkspaceDecision(
        decision_id="DEC-001",
        stage="gate_evaluation",
        outcome="approved",
        justification="Conclusao esperada atingida.",
        decided_at="2026-06-20T11:00:00Z",
        decided_by="human",
        rollback_to_stage=None,
    )
    run = WorkspaceRun(
        run_id="RUN-001",
        case_ref="examples/caso.json",
        created_at="2026-06-20T10:00:00Z",
        created_by="orchestrator",
        status="in_progress",
        current_stage="gate_evaluation",
        artifacts=(artifact,),
        decisions=(decision,),
        notes="",
    )
    data = run_to_dict(run)
    assert data["artifacts"][0]["artifact_id"] == "BUNDLE-001"
    assert data["artifacts"][0]["visible_to"] == ["blind_solver"]
    assert data["decisions"][0]["decision_id"] == "DEC-001"


# --- Case 44: run_to_dict + validate_workspace_run round-trip with no loss ----


def test_run_to_dict_round_trip_passes_schema() -> None:
    artifact = WorkspaceArtifact(
        artifact_id="BUNDLE-001",
        artifact_type="blind_bundle",
        path="workspace/run-001/artifacts/bundle-001/",
        sha256="a" * 64,
        ingested_at="2026-06-20T10:05:00Z",
        stage="blind_solve",
        visible_to=("blind_solver",),
    )
    run = WorkspaceRun(
        run_id="RUN-001",
        case_ref="examples/caso.json",
        created_at="2026-06-20T10:00:00Z",
        created_by="orchestrator",
        status="in_progress",
        current_stage="blind_solve",
        artifacts=(artifact,),
        decisions=(),
        notes="",
    )
    data = run_to_dict(run)
    errors = validate_workspace_run(data)
    assert errors == []


# === Cases 45-50: integration and edge cases =================================


# --- Case 45: artifact stage behind current_stage is structurally valid ------


def test_retroactive_artifact_stage_is_structurally_valid() -> None:
    run = _run(
        current_stage="gate_evaluation",
        artifacts=[_base_artifact(stage="blind_solve")],
    )
    errors = validate_workspace_run(run)
    assert errors == []
    result = validate_workspace_semantics(run)
    assert result.valid is True


# --- Case 46: visible_to with multiple roles is valid ------------------------


def test_visible_to_multiple_roles_is_valid() -> None:
    run = _run(
        artifacts=[
            _base_artifact(visible_to=["blind_solver", "orchestrator"]),
        ],
    )
    errors = validate_workspace_run(run)
    assert errors == []
    result = validate_workspace_semantics(run)
    assert result.valid is True


# --- Case 47: all valid fixtures pass validate_workspace_run -----------------


def test_all_valid_fixtures_pass_schema() -> None:
    for name in (
        "valid_initialized.yaml",
        "valid_in_progress_with_artifact.yaml",
        "valid_gate_blocked.yaml",
        "valid_done.yaml",
    ):
        run = _load_fixture("valid", name)
        assert validate_workspace_run(run) == [], name


# --- Case 48: invalid fixtures rejected with errors --------------------------


def test_all_invalid_fixtures_fail_schema() -> None:
    for name in (
        "invalid_status.yaml",
        "invalid_stage.yaml",
        "missing_run_id.yaml",
        "missing_case_ref.yaml",
        "invalid_artifact_type.yaml",
        "invalid_outcome.yaml",
        "extra_top_field.yaml",
        "missing_justification.yaml",
    ):
        run = _load_fixture("invalid", name)
        assert validate_workspace_run(run) != [], name


# --- Case 49: WS_005 fires for both stage initialized and stage complete -----


def test_ws_005_fires_for_both_invalid_stages() -> None:
    run_initialized = _run(artifacts=[_base_artifact(stage="initialized")])
    run_complete = _run(artifacts=[_base_artifact(stage="complete")])
    result_initialized = validate_workspace_semantics(run_initialized)
    result_complete = validate_workspace_semantics(run_complete)
    assert "WS_005" in " ".join(result_initialized.errors)
    assert "WS_005" in " ".join(result_complete.errors)
    assert result_initialized.valid is False
    assert result_complete.valid is False


# --- Case 50: validate_workspace_semantics never mutates the input run -------


def test_validate_workspace_semantics_does_not_mutate_input() -> None:
    run = _run(
        artifacts=[_base_artifact()],
        decisions=[_base_decision()],
    )
    snapshot = copy.deepcopy(run)
    validate_workspace_semantics(run)
    assert run == snapshot


# --- guard: enums exposed as expected ----------------------------------------


def test_enums_are_exposed() -> None:
    assert "in_progress" in VALID_STATUSES
    assert "blind_solve" in VALID_STAGES
    assert "run_record" in VALID_ARTIFACT_TYPES
    assert "rollback" in VALID_OUTCOMES

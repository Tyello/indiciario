"""RED tests for the workspace run schema (ISSUE-25+26, STEP-03).

These tests describe cases 1-10 of the ISSUE-25+26 spec for the workspace run
contract: the four valid fixtures pass, and selected structural variations
(run_record / gate_evaluation artifact types, rollback decision with non-null
``rollback_to_stage``, ``visible_to: ["all"]``, ``current_stage: "complete"``,
empty ``notes``) are all structurally valid.

They are expected to FAIL (RED) until ``generator/workspace.py`` provides
``validate_workspace_run`` (and its backing
``schemas/workspace_run.schema.yaml``). The failure must come from the missing
module/schema, NOT from a syntax error in this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.workspace import validate_workspace_run

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "workspace_run"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _valid_run(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid workspace run, mutated by ``overrides``."""

    run = _load_fixture("valid", "valid_initialized.yaml")
    run.update(overrides)
    return run


# --- Case 1: valid initialized fixture passes --------------------------------


def test_valid_initialized_passes() -> None:
    run = _load_fixture("valid", "valid_initialized.yaml")
    assert run["status"] == "initialized"
    assert run["artifacts"] == []
    assert run["decisions"] == []
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 2: valid in_progress_with_artifact fixture passes ------------------


def test_valid_in_progress_with_artifact_passes() -> None:
    run = _load_fixture("valid", "valid_in_progress_with_artifact.yaml")
    assert run["status"] == "in_progress"
    assert len(run["artifacts"]) == 1
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 3: valid gate_blocked fixture passes -------------------------------


def test_valid_gate_blocked_passes() -> None:
    run = _load_fixture("valid", "valid_gate_blocked.yaml")
    assert run["status"] == "gate_blocked"
    assert run["decisions"][0]["outcome"] == "rejected"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 4: valid done fixture passes ---------------------------------------


def test_valid_done_passes() -> None:
    run = _load_fixture("valid", "valid_done.yaml")
    assert run["status"] == "done"
    assert run["decisions"][0]["outcome"] == "approved"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 5: artifact_type "run_record" is valid -----------------------------


def test_artifact_type_run_record_is_valid() -> None:
    run = _load_fixture("valid", "valid_in_progress_with_artifact.yaml")
    run["artifacts"][0]["artifact_type"] = "run_record"
    run["artifacts"][0]["stage"] = "gate_evaluation"
    assert run["artifacts"][0]["artifact_type"] == "run_record"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 6: artifact_type "gate_evaluation" is valid ------------------------


def test_artifact_type_gate_evaluation_is_valid() -> None:
    run = _load_fixture("valid", "valid_in_progress_with_artifact.yaml")
    run["artifacts"][0]["artifact_type"] = "gate_evaluation"
    run["artifacts"][0]["stage"] = "gate_evaluation"
    assert run["artifacts"][0]["artifact_type"] == "gate_evaluation"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 7: decisions[].outcome "rollback" with non-null target is valid ----


def test_decision_rollback_with_target_is_valid() -> None:
    run = _load_fixture("valid", "valid_gate_blocked.yaml")
    run["decisions"][0]["outcome"] = "rollback"
    run["decisions"][0]["rollback_to_stage"] = "blind_solve"
    assert run["decisions"][0]["outcome"] == "rollback"
    assert run["decisions"][0]["rollback_to_stage"] == "blind_solve"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 8: visible_to ["all"] is valid -------------------------------------


def test_visible_to_all_is_valid() -> None:
    run = _load_fixture("valid", "valid_in_progress_with_artifact.yaml")
    run["artifacts"][0]["visible_to"] = ["all"]
    assert run["artifacts"][0]["visible_to"] == ["all"]
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 9: current_stage "complete" is valid -------------------------------


def test_current_stage_complete_is_valid() -> None:
    run = _valid_run()
    run["current_stage"] = "complete"
    assert run["current_stage"] == "complete"
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 10: empty notes is valid -------------------------------------------


def test_empty_notes_is_valid() -> None:
    run = _valid_run()
    run["notes"] = ""
    assert run["notes"] == ""
    errors = validate_workspace_run(run)
    assert errors == []


# --- Case 11: schema_version "2.0" fails -------------------------------------


def test_schema_version_2_0_fails() -> None:
    run = _valid_run()
    run["schema_version"] = "2.0"
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 12: status "running" fails (from invalid_status fixture) -----------


def test_invalid_status_fails() -> None:
    run = _load_fixture("invalid", "invalid_status.yaml")
    assert run["status"] == "running"
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 13: current_stage "review" fails (invalid_stage fixture) -----------


def test_invalid_stage_fails() -> None:
    run = _load_fixture("invalid", "invalid_stage.yaml")
    assert run["current_stage"] == "review"
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 14: missing run_id fails -------------------------------------------


def test_missing_run_id_fails() -> None:
    run = _load_fixture("invalid", "missing_run_id.yaml")
    assert "run_id" not in run
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 15: missing case_ref fails -----------------------------------------


def test_missing_case_ref_fails() -> None:
    run = _load_fixture("invalid", "missing_case_ref.yaml")
    assert "case_ref" not in run
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 16: artifact_type "visual_review" fails ----------------------------


def test_invalid_artifact_type_fails() -> None:
    run = _load_fixture("invalid", "invalid_artifact_type.yaml")
    assert run["artifacts"][0]["artifact_type"] == "visual_review"
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 17: artifacts[].visible_to [] fails (minItems: 1) ------------------


def test_empty_visible_to_fails() -> None:
    run = _load_fixture("valid", "valid_in_progress_with_artifact.yaml")
    run["artifacts"][0]["visible_to"] = []
    assert run["artifacts"][0]["visible_to"] == []
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 18: decisions[].outcome "pending" fails ----------------------------


def test_invalid_outcome_fails() -> None:
    run = _load_fixture("invalid", "invalid_outcome.yaml")
    assert run["decisions"][0]["outcome"] == "pending"
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 19: extra top-level field fails (additionalProperties: false) ------


def test_extra_top_field_fails() -> None:
    run = _load_fixture("invalid", "extra_top_field.yaml")
    assert "unexpected_field" in run
    errors = validate_workspace_run(run)
    assert errors != []


# --- Case 20: missing decisions[].justification fails ------------------------


def test_missing_justification_fails() -> None:
    run = _load_fixture("invalid", "missing_justification.yaml")
    assert "justification" not in run["decisions"][0]
    errors = validate_workspace_run(run)
    assert errors != []


# --- guard: fixtures load and helper does not mutate the source --------------


def test_valid_run_helper_does_not_mutate_fixture() -> None:
    pristine = _load_fixture("valid", "valid_initialized.yaml")
    snapshot = copy.deepcopy(pristine)
    _valid_run(status="in_progress")
    fresh = _load_fixture("valid", "valid_initialized.yaml")
    assert fresh == snapshot

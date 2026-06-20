"""RED tests for the gate evaluation schema (ISSUE-19+20, STEP-03).

These tests describe cases 1-10 of the ISSUE-19 spec for the gate evaluation
contract: valid approved/rejected/rollback/no-gaps/unexpected-hypotheses fixtures
pass; empty ``expected_conclusions``, ``leak_detected: true``,
``evaluator_agreement: "partial"``, empty ``notes`` and ``unexpected_valid_hypotheses``
with strings are all structurally valid.

They are expected to FAIL (RED) until ``generator/gate_evaluator.py`` provides
``validate_gate_evaluation`` (and its backing
``schemas/gate_evaluation.schema.yaml``). The failure must come from the missing
module/schema, NOT from a syntax error in this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.gate_evaluator import validate_gate_evaluation

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "gate_evaluation"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _valid_evaluation(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid gate evaluation, mutated by ``overrides``."""

    evaluation = _load_fixture("valid", "valid_approved.yaml")
    evaluation.update(overrides)
    return evaluation


# --- Case 1: valid approved fixture passes -----------------------------------


def test_valid_approved_passes() -> None:
    evaluation = _load_fixture("valid", "valid_approved.yaml")
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 2: valid rejected fixture passes -----------------------------------


def test_valid_rejected_passes() -> None:
    evaluation = _load_fixture("valid", "valid_rejected.yaml")
    assert evaluation["decision"] == "rejected"
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 3: valid rollback fixture passes -----------------------------------


def test_valid_rollback_passes() -> None:
    evaluation = _load_fixture("valid", "valid_rollback.yaml")
    assert evaluation["decision"] == "rollback"
    assert evaluation["rollback_target"] == "bundle_preparation"
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 4: valid no-gaps fixture passes ------------------------------------


def test_valid_no_gaps_passes() -> None:
    evaluation = _load_fixture("valid", "valid_no_gaps.yaml")
    assert evaluation["gaps"] == []
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 5: valid unexpected-hypotheses fixture passes ----------------------


def test_valid_unexpected_hypotheses_passes() -> None:
    evaluation = _load_fixture("valid", "valid_unexpected_hypotheses.yaml")
    assert evaluation["unexpected_valid_hypotheses"]
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 6: empty expected_conclusions is valid -----------------------------


def test_empty_expected_conclusions_is_valid() -> None:
    evaluation = _valid_evaluation()
    evaluation["expected_conclusions"] = []
    assert evaluation["expected_conclusions"] == []
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 7: leak_detected true is valid in the schema -----------------------


def test_leak_detected_true_is_valid() -> None:
    evaluation = _valid_evaluation()
    evaluation["leak_detected"] = True
    assert evaluation["leak_detected"] is True
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 8: evaluator_agreement "partial" is valid --------------------------


def test_evaluator_agreement_partial_is_valid() -> None:
    evaluation = _valid_evaluation()
    evaluation["confidence_assessment"]["evaluator_agreement"] = "partial"
    assert evaluation["confidence_assessment"]["evaluator_agreement"] == "partial"
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 9: empty notes is valid --------------------------------------------


def test_empty_notes_is_valid() -> None:
    evaluation = _valid_evaluation()
    evaluation["notes"] = ""
    assert evaluation["notes"] == ""
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 10: unexpected_valid_hypotheses with strings is valid --------------


def test_unexpected_valid_hypotheses_with_strings_is_valid() -> None:
    evaluation = _valid_evaluation()
    evaluation["unexpected_valid_hypotheses"] = [
        "Hipotese extra A plausivel",
        "Hipotese extra B plausivel",
    ]
    assert all(
        isinstance(item, str) for item in evaluation["unexpected_valid_hypotheses"]
    )
    errors = validate_gate_evaluation(evaluation)
    assert errors == []


# --- Case 11: schema_version "2.0" fails -------------------------------------


def test_schema_version_2_0_fails() -> None:
    evaluation = _valid_evaluation()
    evaluation["schema_version"] = "2.0"
    assert evaluation["schema_version"] == "2.0"
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 12: decision "pending" fails ---------------------------------------


def test_invalid_decision_pending_fails() -> None:
    evaluation = _load_fixture("invalid", "invalid_decision.yaml")
    assert evaluation["decision"] == "pending"
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 13: missing evaluation_id fails ------------------------------------


def test_missing_evaluation_id_fails() -> None:
    evaluation = _load_fixture("invalid", "missing_evaluation_id.yaml")
    assert "evaluation_id" not in evaluation
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 14: missing run_id fails -------------------------------------------


def test_missing_run_id_fails() -> None:
    evaluation = _valid_evaluation()
    del evaluation["run_id"]
    assert "run_id" not in evaluation
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 15: missing justification fails ------------------------------------


def test_missing_justification_fails() -> None:
    evaluation = _load_fixture("invalid", "missing_justification.yaml")
    assert "justification" not in evaluation
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 16: rollback_target "unknown_stage" fails --------------------------


def test_invalid_rollback_target_fails() -> None:
    evaluation = _load_fixture("invalid", "invalid_rollback_target.yaml")
    assert evaluation["rollback_target"] == "unknown_stage"
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 17: expected_conclusions item without id fails ---------------------


def test_expected_conclusion_without_id_fails() -> None:
    evaluation = _valid_evaluation()
    evaluation["expected_conclusions"] = [
        {
            "description": "Conclusao sem id",
            "required": True,
            "met": True,
            "evidence": "sem id",
        }
    ]
    assert "id" not in evaluation["expected_conclusions"][0]
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 18: gaps item without severity fails -------------------------------


def test_gap_without_severity_fails() -> None:
    evaluation = _valid_evaluation()
    evaluation["gaps"] = [
        {
            "id": "GAP-01",
            "description": "Gap sem severity",
            "required_conclusion_id": None,
            "impact": "Sem severity",
        }
    ]
    assert "severity" not in evaluation["gaps"][0]
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 19: gaps item with severity "trivial" fails ------------------------


def test_invalid_gap_severity_fails() -> None:
    evaluation = _load_fixture("invalid", "invalid_gap_severity.yaml")
    assert evaluation["gaps"][0]["severity"] == "trivial"
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- Case 20: extra top-level field fails ------------------------------------


def test_extra_top_field_fails() -> None:
    evaluation = _load_fixture("invalid", "extra_top_field.yaml")
    assert "campo_extra_proibido" in evaluation
    errors = validate_gate_evaluation(evaluation)
    assert errors != []


# --- guard: fixtures load and helper does not mutate the source --------------


def test_valid_evaluation_helper_does_not_mutate_fixture() -> None:
    pristine = _load_fixture("valid", "valid_approved.yaml")
    snapshot = copy.deepcopy(pristine)
    _valid_evaluation(decision="rejected")
    fresh = _load_fixture("valid", "valid_approved.yaml")
    assert fresh == snapshot

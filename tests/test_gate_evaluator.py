"""RED tests for the gate evaluator semantics and builder (ISSUE-19+20).

STEP-06 added cases 21-30 for the blocking semantic rules GE_001-GE_006 applied
by ``validate_gate_evaluation_semantics``:

- GE_001: ``decision=rollback`` requires non-null ``rollback_target``
- GE_002: ``decision!=rollback`` requires null ``rollback_target``
- GE_003: ``leak_detected=true`` forbids ``decision=approved``
- GE_004/GE_005: ``decision=approved`` requires every ``required=true``
  conclusion to be ``met=true``
- GE_006: a ``severity=critical`` gap forbids ``decision=approved``

STEP-07 adds cases 31-50:

- 31-36: GE_007 (warning when ``solver_confidence`` diverges from
  ``report.confidence``), GE_008 (error when ``run_id`` does not match the run
  record), run_record=None skips both, and the ``valid`` flag.
- 37-50: ``build_gate_evaluation`` returns a dict that passes
  ``validate_gate_evaluation``, links ``evaluation_id``/``run_id``/``bundle_id``,
  stays semantically consistent, preserves list/object/string fields and never
  mutates its inputs.

They are expected to FAIL (RED) until ``generator/gate_evaluator.py`` provides
``validate_gate_evaluation_semantics`` and ``build_gate_evaluation``. The failure
must come from the missing functions (ImportError), NOT from a syntax error in
this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.gate_evaluator import (
    ConfidenceAssessment,
    ExpectedConclusion,
    GapItem,
    GateEvaluationRequest,
    build_gate_evaluation,
    validate_gate_evaluation,
    validate_gate_evaluation_semantics,
)

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "gate_evaluation"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _evaluation(**overrides: Any) -> dict[str, Any]:
    """Return a deep-copied valid gate evaluation, mutated by ``overrides``."""

    evaluation = _load_fixture("valid", "valid_approved.yaml")
    evaluation = copy.deepcopy(evaluation)
    evaluation.update(overrides)
    return evaluation


def _errors(evaluation: dict[str, Any]) -> tuple[str, ...]:
    result = validate_gate_evaluation_semantics(evaluation)
    return tuple(result.semantic_errors)


def _has_code(errors: tuple[str, ...], code: str) -> bool:
    return any(code in error for error in errors)


# --- Case 21: rollback without rollback_target raises GE_001 -----------------


def test_ge001_rollback_without_target() -> None:
    evaluation = _evaluation(decision="rollback", rollback_target=None)
    errors = _errors(evaluation)
    assert _has_code(errors, "GE_001")


# --- Case 22: rollback with rollback_target has no GE_001 --------------------


def test_ge001_rollback_with_target_ok() -> None:
    evaluation = _evaluation(decision="rollback", rollback_target="blind_solve")
    errors = _errors(evaluation)
    assert not _has_code(errors, "GE_001")


# --- Case 23: approved with rollback_target raises GE_002 --------------------


def test_ge002_approved_with_target() -> None:
    evaluation = _evaluation(decision="approved", rollback_target="blind_solve")
    errors = _errors(evaluation)
    assert _has_code(errors, "GE_002")


# --- Case 24: approved with null rollback_target has no GE_002 ---------------


def test_ge002_approved_without_target_ok() -> None:
    evaluation = _evaluation(decision="approved", rollback_target=None)
    errors = _errors(evaluation)
    assert not _has_code(errors, "GE_002")


# --- Case 25: leak_detected true + approved raises GE_003 --------------------


def test_ge003_leak_detected_approved() -> None:
    evaluation = _evaluation(decision="approved", leak_detected=True)
    errors = _errors(evaluation)
    assert _has_code(errors, "GE_003")


# --- Case 26: leak_detected true + rejected has no GE_003 --------------------


def test_ge003_leak_detected_rejected_ok() -> None:
    evaluation = _evaluation(
        decision="rejected",
        leak_detected=True,
        rollback_target=None,
    )
    errors = _errors(evaluation)
    assert not _has_code(errors, "GE_003")


# --- Case 27: approved with required unmet raises GE_004/GE_005 --------------


def test_ge004_ge005_approved_required_unmet() -> None:
    evaluation = _evaluation(decision="approved", rollback_target=None)
    evaluation["expected_conclusions"] = [
        {
            "id": "EC-01",
            "description": "Identificar culpado",
            "required": True,
            "met": False,
            "evidence": "",
        }
    ]
    errors = _errors(evaluation)
    assert _has_code(errors, "GE_004") or _has_code(errors, "GE_005")


# --- Case 28: approved with all required met has no GE_004 -------------------


def test_ge004_approved_all_required_met_ok() -> None:
    evaluation = _evaluation(decision="approved", rollback_target=None)
    evaluation["expected_conclusions"] = [
        {
            "id": "EC-01",
            "description": "Identificar culpado",
            "required": True,
            "met": True,
            "evidence": "",
        },
        {
            "id": "EC-02",
            "description": "Identificar mecanismo",
            "required": True,
            "met": True,
            "evidence": "",
        },
    ]
    errors = _errors(evaluation)
    assert not _has_code(errors, "GE_004")


# --- Case 29: approved with critical gap raises GE_006 ----------------------


def test_ge006_approved_with_critical_gap() -> None:
    evaluation = _evaluation(decision="approved", rollback_target=None)
    evaluation["gaps"] = [
        {
            "id": "GAP-01",
            "description": "Lacuna critica",
            "required_conclusion_id": None,
            "severity": "critical",
            "impact": "Bloqueia aprovacao",
        }
    ]
    errors = _errors(evaluation)
    assert _has_code(errors, "GE_006")


# --- Case 30: rejected with critical gap has no GE_006 ----------------------


def test_ge006_rejected_with_critical_gap_ok() -> None:
    evaluation = _evaluation(decision="rejected", rollback_target=None)
    evaluation["gaps"] = [
        {
            "id": "GAP-01",
            "description": "Lacuna critica",
            "required_conclusion_id": None,
            "severity": "critical",
            "impact": "Bloqueia aprovacao",
        }
    ]
    errors = _errors(evaluation)
    assert not _has_code(errors, "GE_006")


# --------------------------------------------------------------------------- #
# Cases 31-36: GE_007 / GE_008 + valid flag                                   #
# --------------------------------------------------------------------------- #
def _run_record(
    run_id: str = "RUN-AURORA-20260615-001",
    bundle_id: str = "BUNDLE-AURORA-V1",
    confidence: str = "medium",
) -> dict[str, Any]:
    """Minimal run record carrying ``run_id``, ``bundle_id`` and ``report.confidence``."""

    return {
        "run_id": run_id,
        "bundle_id": bundle_id,
        "report": {"confidence": confidence},
    }


def _result(
    evaluation: dict[str, Any],
    run_record: dict[str, Any] | None = None,
):
    return validate_gate_evaluation_semantics(evaluation, run_record)


# --- Case 31: solver_confidence diverges from report.confidence -> GE_007 ----


def test_ge007_confidence_divergence_warns() -> None:
    evaluation = _evaluation()
    evaluation["confidence_assessment"]["solver_confidence"] = "high"
    result = _result(evaluation, _run_record(confidence="medium"))
    warnings = tuple(result.semantic_warnings)
    assert any("GE_007" in warning for warning in warnings)
    # GE_007 is a non-blocking warning, never an error.
    assert not _has_code(tuple(result.semantic_errors), "GE_007")


# --- Case 32: solver_confidence equal to report.confidence -> no GE_007 ------


def test_ge007_confidence_match_no_warning() -> None:
    evaluation = _evaluation()
    evaluation["confidence_assessment"]["solver_confidence"] = "medium"
    result = _result(evaluation, _run_record(confidence="medium"))
    warnings = tuple(result.semantic_warnings)
    assert not any("GE_007" in warning for warning in warnings)


# --- Case 33: run record with matching run_id -> no GE_008 -------------------


def test_ge008_run_id_match_ok() -> None:
    evaluation = _evaluation()
    evaluation["run_id"] = "RUN-AURORA-20260615-001"
    result = _result(evaluation, _run_record(run_id="RUN-AURORA-20260615-001"))
    assert not _has_code(tuple(result.semantic_errors), "GE_008")


# --- Case 34: run record with different run_id -> GE_008 error ---------------


def test_ge008_run_id_mismatch_error() -> None:
    evaluation = _evaluation()
    evaluation["run_id"] = "RUN-AURORA-20260615-001"
    result = _result(evaluation, _run_record(run_id="RUN-OTHER-99999999-999"))
    assert _has_code(tuple(result.semantic_errors), "GE_008")


# --- Case 35: run_record None -> GE_007 and GE_008 skipped -------------------


def test_run_record_none_skips_ge007_ge008() -> None:
    evaluation = _evaluation()
    evaluation["confidence_assessment"]["solver_confidence"] = "high"
    evaluation["run_id"] = "RUN-DOES-NOT-MATTER"
    result = _result(evaluation, None)
    assert not _has_code(tuple(result.semantic_errors), "GE_008")
    assert not any("GE_007" in warning for warning in result.semantic_warnings)


# --- Case 36: valid flag reflects presence of errors ------------------------


def test_valid_flag_reflects_errors() -> None:
    clean = _evaluation(decision="approved", rollback_target=None)
    clean_result = validate_gate_evaluation_semantics(clean)
    assert clean_result.valid is True
    assert clean_result.semantic_errors == ()

    broken = _evaluation(decision="rollback", rollback_target=None)
    broken_result = validate_gate_evaluation_semantics(broken)
    assert broken_result.valid is False
    assert len(broken_result.semantic_errors) >= 1


# --------------------------------------------------------------------------- #
# Cases 37-50: build_gate_evaluation + integration                            #
# --------------------------------------------------------------------------- #
def _build_run_record(
    run_id: str = "RUN-AURORA-20260615-001",
    bundle_id: str = "BUNDLE-AURORA-V1",
    confidence: str = "medium",
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "bundle_id": bundle_id,
        "report": {"confidence": confidence},
    }


def _request(**overrides: Any) -> GateEvaluationRequest:
    kwargs: dict[str, Any] = {
        "run_record": _build_run_record(),
        "private_solution_ref": "examples/caso_canonico_intermediario.json",
        "evaluator_id": "human-marcelo",
        "evaluation_id": "GE-AURORA-20260616-001",
        "created_by": "orchestrator",
        "created_at": "2026-06-16T14:00:00Z",
    }
    kwargs.update(overrides)
    return GateEvaluationRequest(**kwargs)


def _expected(met: bool = True, required: bool = True) -> list[ExpectedConclusion]:
    return [
        ExpectedConclusion(
            id="EC-01",
            description="Identificar culpado",
            required=required,
            met=met,
            evidence="conclusion contem culpado",
        )
    ]


def _confidence(solver_confidence: str = "medium") -> ConfidenceAssessment:
    return ConfidenceAssessment(
        solver_confidence=solver_confidence,
        evaluator_agreement="agree",
        notes="",
    )


def _build(**overrides: Any) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "request": _request(),
        "expected_conclusions": _expected(),
        "unexpected_valid_hypotheses": [],
        "gaps": [],
        "confidence_assessment": _confidence(),
        "decision": "approved",
        "justification": "Solver identificou culpado e mecanismo corretamente.",
        "leak_detected": False,
        "rollback_target": None,
        "notes": "",
    }
    kwargs.update(overrides)
    return build_gate_evaluation(**kwargs)


# --- Case 37: build returns a dict ------------------------------------------


def test_build_returns_dict() -> None:
    assert isinstance(_build(), dict)


# --- Case 38: built dict passes validate_gate_evaluation --------------------


def test_build_passes_schema() -> None:
    evaluation = _build()
    assert validate_gate_evaluation(evaluation) == []


# --- Case 39: evaluation_id matches request.evaluation_id -------------------


def test_build_evaluation_id_matches_request() -> None:
    request = _request(evaluation_id="GE-AURORA-20260616-042")
    evaluation = _build(request=request)
    assert evaluation["evaluation_id"] == "GE-AURORA-20260616-042"


# --- Case 40: run_id matches request.run_record["run_id"] -------------------


def test_build_run_id_matches_run_record() -> None:
    request = _request(run_record=_build_run_record(run_id="RUN-AURORA-XYZ"))
    evaluation = _build(request=request)
    assert evaluation["run_id"] == "RUN-AURORA-XYZ"


# --- Case 41: bundle_id matches request.run_record["bundle_id"] -------------


def test_build_bundle_id_matches_run_record() -> None:
    request = _request(run_record=_build_run_record(bundle_id="BUNDLE-AURORA-V2"))
    evaluation = _build(request=request)
    assert evaluation["bundle_id"] == "BUNDLE-AURORA-V2"


# --- Case 42: approved + valid conclusions + no critical gaps -> no errors --


def test_build_approved_consistent_no_semantic_errors() -> None:
    evaluation = _build(
        decision="approved",
        expected_conclusions=_expected(met=True, required=True),
        gaps=[],
        rollback_target=None,
    )
    result = validate_gate_evaluation_semantics(evaluation)
    assert result.semantic_errors == ()


# --- Case 43: rejected + missing required conclusion -> no errors -----------


def test_build_rejected_missing_required_no_errors() -> None:
    evaluation = _build(
        decision="rejected",
        expected_conclusions=_expected(met=False, required=True),
        rollback_target=None,
    )
    result = validate_gate_evaluation_semantics(evaluation)
    assert result.semantic_errors == ()


# --- Case 44: rollback with rollback_target -> no errors --------------------


def test_build_rollback_with_target_no_errors() -> None:
    evaluation = _build(
        decision="rollback",
        rollback_target="blind_solve",
    )
    result = validate_gate_evaluation_semantics(evaluation)
    assert result.semantic_errors == ()


# --- Case 45: build does not mutate inputs ----------------------------------


def test_build_does_not_mutate_inputs() -> None:
    request = _request()
    expected = _expected()
    unexpected: list[str] = ["hipotese extra"]
    gaps = [
        GapItem(
            id="GAP-01",
            description="Lacuna",
            required_conclusion_id=None,
            severity="minor",
            impact="",
        )
    ]
    confidence = _confidence()

    request_before = copy.deepcopy(request)
    expected_before = copy.deepcopy(expected)
    unexpected_before = copy.deepcopy(unexpected)
    gaps_before = copy.deepcopy(gaps)
    confidence_before = copy.deepcopy(confidence)

    build_gate_evaluation(
        request=request,
        expected_conclusions=expected,
        unexpected_valid_hypotheses=unexpected,
        gaps=gaps,
        confidence_assessment=confidence,
        decision="approved",
        justification="Solver identificou culpado e mecanismo corretamente.",
        leak_detected=False,
        rollback_target=None,
        notes="",
    )

    assert request == request_before
    assert expected == expected_before
    assert unexpected == unexpected_before
    assert gaps == gaps_before
    assert confidence == confidence_before


# --- Case 46: unexpected_valid_hypotheses preserved as list -----------------


def test_build_preserves_unexpected_hypotheses() -> None:
    evaluation = _build(unexpected_valid_hypotheses=["hipotese A", "hipotese B"])
    assert evaluation["unexpected_valid_hypotheses"] == ["hipotese A", "hipotese B"]
    assert isinstance(evaluation["unexpected_valid_hypotheses"], list)


# --- Case 47: gaps preserved as list of objects -----------------------------


def test_build_preserves_gaps_as_objects() -> None:
    gaps = [
        GapItem(
            id="GAP-01",
            description="Lacuna menor",
            required_conclusion_id="EC-01",
            severity="minor",
            impact="Sem bloqueio",
        )
    ]
    evaluation = _build(gaps=gaps)
    assert isinstance(evaluation["gaps"], list)
    assert isinstance(evaluation["gaps"][0], dict)
    gap = evaluation["gaps"][0]
    assert gap["id"] == "GAP-01"
    assert gap["description"] == "Lacuna menor"
    assert gap["required_conclusion_id"] == "EC-01"
    assert gap["severity"] == "minor"
    assert gap["impact"] == "Sem bloqueio"


# --- Case 48: confidence_assessment preserved as object ---------------------


def test_build_preserves_confidence_assessment() -> None:
    confidence = ConfidenceAssessment(
        solver_confidence="high",
        evaluator_agreement="partial",
        notes="alguma nota",
    )
    evaluation = _build(confidence_assessment=confidence)
    assert isinstance(evaluation["confidence_assessment"], dict)
    assessment = evaluation["confidence_assessment"]
    assert assessment["solver_confidence"] == "high"
    assert assessment["evaluator_agreement"] == "partial"
    assert assessment["notes"] == "alguma nota"


# --- Case 49: empty notes preserved as empty string -------------------------


def test_build_preserves_empty_notes() -> None:
    evaluation = _build(notes="")
    assert evaluation["notes"] == ""
    assert isinstance(evaluation["notes"], str)


# --- Case 50: full suite runs without regression ----------------------------


def test_full_suite_placeholder() -> None:
    """Case 50 (``pytest tests/ -q`` without regression) is validated at the
    suite level in STEP-11, not by an in-process pytest invocation. This marker
    keeps the case numbering aligned and documents that the no-regression check
    is a command-level gate, not a unit test."""

    assert True

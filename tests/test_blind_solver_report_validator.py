"""RED tests for the standalone blind solver report validator (ISSUE-17, STEP-03).

These tests describe the blocking semantic codes (RV_001-RV_005, RV_008) and the
RV_008 negative case, using inline report dicts. They are expected to FAIL until
``generator/blind_solver_report_validator.py`` provides ``validate_report``.
"""

from __future__ import annotations

import copy
import dataclasses
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest
import yaml

from generator.blind_solver_report_validator import (
    ReportValidationError,
    ReportValidationErrorKind,
    validate_report,
)

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "blind_solver_report_validator"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _base_report(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid report dict, mutated by ``overrides``."""

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "solver_run_id": "SOLVER_RUN_001",
        "solver_id": "SOLVER_STUB_001",
        "bundle_id": "BUNDLE_TEST_001",
        "manifest_id": "MANIFEST_TEST_001",
        "created_at": "2026-06-14T00:00:00Z",
        "conclusion": "O depoimento publico indica desvio da reserva antes do registro.",
        "confidence": "medium",
        "reasoning_summary": "Cruzou o depoimento publico com o recibo bundleado.",
        "evidence_used": [
            {
                "artifact_id": "ART_PUBLIC_001",
                "path": "player/depoimento.md",
                "quote_or_summary": "Depoimento publico citando o desvio da reserva.",
                "relevance": "Fonte direta da hipotese principal.",
                "confidence": "medium",
            }
        ],
        "open_questions": [],
        "assumptions": [],
        "warnings": [],
    }
    report.update(overrides)
    return report


def _high_evidence(artifact_id: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "path": f"player/{artifact_id.lower()}.md",
        "quote_or_summary": "Trecho publico relevante.",
        "relevance": "Sustenta a conclusao principal.",
        "confidence": "high",
    }


def _codes(result: Any) -> set[str]:
    return {error.code for error in result.errors}


def _warning_codes(result: Any) -> set[str]:
    return {warning.code for warning in result.warnings}


def test_valid_complete_report_is_valid() -> None:
    result = validate_report(_base_report(confidence="high"))
    assert result.valid is True
    assert result.errors == ()


def test_valid_minimal_no_conclusion_is_valid() -> None:
    report = _base_report(
        conclusion="",
        confidence="low",
        evidence_used=[],
        open_questions=["Falta confirmar quem assinou o recibo divergente."],
    )
    result = validate_report(report)
    assert result.valid is True


def test_missing_required_field_yields_rv_001() -> None:
    report = _base_report()
    del report["conclusion"]
    result = validate_report(report)
    assert result.valid is False
    assert "RV_001" in _codes(result)


def test_conclusion_without_evidence_yields_rv_002() -> None:
    report = _base_report(conclusion="Houve desvio da reserva.", evidence_used=[])
    result = validate_report(report)
    assert result.valid is False
    assert "RV_002" in _codes(result)


def test_high_confidence_without_evidence_yields_rv_003() -> None:
    report = _base_report(confidence="high", conclusion="", evidence_used=[], open_questions=["Quem assinou?"])
    result = validate_report(report)
    assert result.valid is False
    assert "RV_003" in _codes(result)


def test_high_confidence_with_open_questions_yields_rv_004() -> None:
    report = _base_report(confidence="high", open_questions=["Falta confirmar a autoria."])
    result = validate_report(report)
    assert result.valid is False
    assert "RV_004" in _codes(result)


def test_no_conclusion_no_open_questions_yields_rv_005() -> None:
    report = _base_report(conclusion="", confidence="low", evidence_used=[], open_questions=[])
    result = validate_report(report)
    assert result.valid is False
    assert "RV_005" in _codes(result)


def test_low_confidence_three_high_evidence_yields_rv_008() -> None:
    report = _base_report(
        confidence="low",
        evidence_used=[_high_evidence("ART_A"), _high_evidence("ART_B"), _high_evidence("ART_C")],
    )
    result = validate_report(report)
    assert result.valid is False
    assert "RV_008" in _codes(result)


def test_medium_confidence_three_high_evidence_does_not_yield_rv_008() -> None:
    report = _base_report(
        confidence="medium",
        evidence_used=[_high_evidence("ART_A"), _high_evidence("ART_B"), _high_evidence("ART_C")],
    )
    result = validate_report(report)
    assert "RV_008" not in _codes(result)
    assert result.valid is True


def test_validate_report_does_not_mutate_input() -> None:
    report = _base_report()
    snapshot = copy.deepcopy(report)
    validate_report(report)
    assert report == snapshot


# --- STEP-04: warnings, multiple errors and negatives (inline) --------------


def test_vague_reasoning_inconclusivo_yields_rv_006_warning() -> None:
    report = _base_report(reasoning_summary="Inconclusivo.")
    result = validate_report(report)
    assert result.valid is True
    assert "RV_006" in _warning_codes(result)
    assert "RV_006" not in _codes(result)


def test_vague_reasoning_na_yields_rv_006_warning() -> None:
    report = _base_report(reasoning_summary="N/A")
    result = validate_report(report)
    assert result.valid is True
    assert "RV_006" in _warning_codes(result)


def test_vague_reasoning_pendente_yields_rv_006_warning() -> None:
    report = _base_report(reasoning_summary="Pendente")
    result = validate_report(report)
    assert result.valid is True
    assert "RV_006" in _warning_codes(result)


def test_evidence_without_conclusion_yields_rv_007_warning() -> None:
    report = _base_report(
        conclusion="",
        open_questions=["Falta confirmar quem assinou o recibo divergente."],
    )
    result = validate_report(report)
    assert result.valid is True
    assert "RV_007" in _warning_codes(result)
    assert "RV_007" not in _codes(result)


def test_report_with_multiple_errors_lists_all_codes() -> None:
    # high confidence + open_questions (RV_004) + no evidence (RV_003).
    report = _base_report(
        confidence="high",
        evidence_used=[],
        open_questions=["Falta confirmar a autoria."],
    )
    result = validate_report(report)
    assert result.valid is False
    codes = _codes(result)
    assert "RV_003" in codes
    assert "RV_004" in codes


def test_real_reasoning_summary_does_not_yield_rv_006() -> None:
    report = _base_report(
        reasoning_summary="A analise indica que o desvio ocorreu antes do registro formal."
    )
    result = validate_report(report)
    assert "RV_006" not in _warning_codes(result)
    assert "RV_006" not in _codes(result)


def test_open_questions_with_items_and_empty_conclusion_no_rv_005() -> None:
    report = _base_report(
        conclusion="",
        confidence="low",
        evidence_used=[],
        open_questions=["Falta confirmar quem assinou o recibo divergente."],
    )
    result = validate_report(report)
    assert "RV_005" not in _codes(result)


def test_valid_with_warnings_is_still_valid() -> None:
    report = _base_report(reasoning_summary="inconclusivo")
    result = validate_report(report)
    assert result.valid is True
    assert result.warnings != ()


# --- STEP-05: API contract and immutability (inline) ------------------------


def test_errors_are_report_validation_error_with_full_fields() -> None:
    # RV_002: conclusion without evidence -> blocking error.
    report = _base_report(conclusion="Houve desvio da reserva.", evidence_used=[])
    result = validate_report(report)
    assert result.errors != ()
    for error in result.errors:
        assert isinstance(error, ReportValidationError)
        assert isinstance(error.kind, ReportValidationErrorKind)
        assert isinstance(error.code, str) and error.code
        assert isinstance(error.field, str)
        assert isinstance(error.message, str) and error.message


def test_warnings_have_quality_kind() -> None:
    report = _base_report(reasoning_summary="inconclusivo")
    result = validate_report(report)
    assert result.warnings != ()
    for warning in result.warnings:
        assert isinstance(warning, ReportValidationError)
        assert warning.kind == ReportValidationErrorKind.QUALITY


def test_quality_kind_does_not_make_result_invalid() -> None:
    report = _base_report(reasoning_summary="inconclusivo")
    result = validate_report(report)
    assert result.valid is True
    assert all(w.kind == ReportValidationErrorKind.QUALITY for w in result.warnings)
    assert all(e.kind != ReportValidationErrorKind.QUALITY for e in result.errors)


def test_validate_report_accepts_dict_and_mapping() -> None:
    plain: dict[str, Any] = _base_report()
    mapping: Mapping[str, Any] = MappingProxyType(_base_report())
    dict_result = validate_report(plain)
    mapping_result = validate_report(mapping)
    assert dict_result.valid is True
    assert mapping_result.valid is True
    assert _codes(dict_result) == _codes(mapping_result)


def test_validate_report_does_not_mutate_mapping_input() -> None:
    base = _base_report()
    snapshot = copy.deepcopy(base)
    validate_report(MappingProxyType(base))
    assert base == snapshot


def test_result_and_errors_are_frozen() -> None:
    report = _base_report(conclusion="Houve desvio da reserva.", evidence_used=[])
    result = validate_report(report)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.valid = False  # type: ignore[misc]
    error = result.errors[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        error.code = "RV_999"  # type: ignore[misc]


# --- STEP-06: fixtures valid + warnings and their tests ---------------------


@pytest.mark.parametrize(
    "fixture_name",
    ["valid_complete.yaml", "valid_no_conclusion.yaml"],
)
def test_valid_fixtures_are_valid_without_warnings(fixture_name: str) -> None:
    report = _load_fixture("valid", fixture_name)
    result = validate_report(report)
    assert result.valid is True
    assert result.errors == ()
    assert result.warnings == ()


def test_vague_reasoning_summary_fixture_yields_rv_006_warning() -> None:
    report = _load_fixture("warnings", "vague_reasoning_summary.yaml")
    result = validate_report(report)
    assert result.valid is True
    assert "RV_006" in _warning_codes(result)
    assert "RV_006" not in _codes(result)


def test_evidence_without_conclusion_fixture_yields_rv_007_warning() -> None:
    report = _load_fixture("warnings", "evidence_without_conclusion.yaml")
    result = validate_report(report)
    assert result.valid is True
    assert "RV_007" in _warning_codes(result)
    assert "RV_007" not in _codes(result)


# --- STEP-07: invalid fixtures (part 1) and parametrized test ---------------


@pytest.mark.parametrize(
    ("fixture_name", "expected_code"),
    [
        ("conclusion_without_evidence.yaml", "RV_002"),
        ("high_confidence_no_evidence.yaml", "RV_003"),
        ("high_confidence_with_open_questions.yaml", "RV_004"),
        ("no_conclusion_no_open_questions.yaml", "RV_005"),
        ("low_confidence_all_high_evidence.yaml", "RV_008"),
        ("missing_required_field.yaml", "RV_001"),
    ],
)
def test_invalid_fixtures_yield_expected_code(
    fixture_name: str, expected_code: str
) -> None:
    report = _load_fixture("invalid", fixture_name)
    result = validate_report(report)
    assert result.valid is False
    assert expected_code in _codes(result)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

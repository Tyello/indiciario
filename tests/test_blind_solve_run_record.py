"""RED tests for the blind solve run record builder (ISSUE-18, STEP-06).

These tests describe ``build_run_record`` (cases 16-23 of the spec): given a real
``BlindSolverHarnessResult`` (produced by running the offline harness over a real
blind bundle), the harness request and a ``ReportValidationResult`` from the
standalone semantic validator, the builder must produce a traceable run record
dict that links the bundle, manifest and solver to the frozen report, reflects
the artifacts accessed, the denied accesses and the harness warnings.

They are expected to FAIL until ``generator/blind_solve_run_record.py`` provides
``build_run_record`` (only ``validate_run_record`` exists so far).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.blind_solver_harness import (
    BlindSolverHarnessRequest,
    BlindSolverHarnessResult,
    run_blind_solver_harness,
)
from generator.blind_solver_report_validator import (
    ReportValidationResult,
    validate_report,
)

# build_run_record does not exist yet (only validate_run_record): this import
# is what makes the STEP-06 tests fail RED until STEP-09 implements the builder.
from generator.blind_solve_run_record import build_run_record

# Reuse the real harness test helpers (bundle building + deterministic stub
# solver) so the run record is built from a genuine harness result, not a mock.
# source_tree / output_root: fixtures vêm de tests/conftest.py (ISSUE-41.1,
# CI_001) — não são importadas aqui para não colidir com os parâmetros de
# mesmo nome nas funções de teste abaixo.
from tests.test_blind_solver_harness import (  # noqa: E402
    DeterministicStubBlindSolver,
    harness_request,
    make_bundle,
)


# --------------------------------------------------------------------------- #
# Helpers: build a real harness result + validator result                      #
# --------------------------------------------------------------------------- #
def _run_harness(source_tree: Path, output_root: Path) -> tuple[
    BlindSolverHarnessResult, BlindSolverHarnessRequest
]:
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)
    result = run_blind_solver_harness(request, DeterministicStubBlindSolver())
    return result, request


def _validator_result(result: BlindSolverHarnessResult) -> ReportValidationResult:
    return validate_report(result.report)


def _build(source_tree: Path, output_root: Path) -> dict:
    result, request = _run_harness(source_tree, output_root)
    validator_result = _validator_result(result)
    return build_run_record(result, request, validator_result)


# --------------------------------------------------------------------------- #
# Tests 16-23                                                                   #
# --------------------------------------------------------------------------- #
def test_build_run_record_returns_dict(source_tree: Path, output_root: Path) -> None:
    # 16. build_run_record com harness_result válido retorna dict
    record = _build(source_tree, output_root)
    assert isinstance(record, dict)


def test_built_record_passes_validate_run_record(source_tree: Path, output_root: Path) -> None:
    # 17. record retornado passa validate_run_record
    from generator.blind_solve_run_record import validate_run_record

    record = _build(source_tree, output_root)
    assert validate_run_record(record) == []


def test_run_id_matches_report_solver_run_id(source_tree: Path, output_root: Path) -> None:
    # 18. run_id do record bate com solver_run_id do report
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["run_id"] == result.report["solver_run_id"]


def test_bundle_id_matches_report_bundle_id(source_tree: Path, output_root: Path) -> None:
    # 19. bundle_id do record bate com bundle_id do report
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["bundle_id"] == result.report["bundle_id"]


def test_manifest_id_matches_report_manifest_id(source_tree: Path, output_root: Path) -> None:
    # 20. manifest_id do record bate com manifest_id do report
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["manifest_id"] == result.report["manifest_id"]


def test_accessed_artifacts_reflect_harness(source_tree: Path, output_root: Path) -> None:
    # 21. accessed_artifacts reflete acessos do harness
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    recorded_ids = [item["artifact_id"] for item in record["accessed_artifacts"]]
    assert recorded_ids == list(result.accessed_artifacts)


def test_denied_access_attempts_reflect_harness(source_tree: Path, output_root: Path) -> None:
    # 22. denied_access_attempts reflete negações do harness
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    # A successful run has no denied accesses; the record must reflect that.
    assert len(record["denied_access_attempts"]) == len(result.denied_access_attempts)


def test_harness_warnings_reflect_harness(source_tree: Path, output_root: Path) -> None:
    # 23. harness_warnings reflete warnings do harness
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["harness_warnings"] == list(result.warnings)


# --------------------------------------------------------------------------- #
# Tests 24-31 (STEP-07)                                                         #
# --------------------------------------------------------------------------- #
def test_validation_report_schema_valid_true(source_tree: Path, output_root: Path) -> None:
    # 24. validation.report_schema_valid é True para report válido.
    # The harness only emits a report after structural validation passes, so a
    # genuine harness result always yields a schema-valid report.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["validation"]["report_schema_valid"] is True


def test_validation_report_semantic_valid_true(source_tree: Path, output_root: Path) -> None:
    # 25. validation.report_semantic_valid é True para report semanticamente válido.
    result, request = _run_harness(source_tree, output_root)
    validator_result = _validator_result(result)
    # Precondition: the deterministic stub solver produces a semantically valid
    # report, so the builder must surface that as report_semantic_valid True.
    assert validator_result.valid is True
    record = build_run_record(result, request, validator_result)
    assert record["validation"]["report_semantic_valid"] is True


def test_validation_semantic_errors_empty_for_clean_report(
    source_tree: Path, output_root: Path
) -> None:
    # 26. validation.semantic_errors é lista vazia para report sem erros.
    result, request = _run_harness(source_tree, output_root)
    validator_result = _validator_result(result)
    assert validator_result.errors == ()
    record = build_run_record(result, request, validator_result)
    assert record["validation"]["semantic_errors"] == []


def test_validation_semantic_warnings_reflect_validator(
    source_tree: Path, output_root: Path
) -> None:
    # 27. validation.semantic_warnings reflete warnings do validator.
    # Build a real ReportValidationResult that carries a warning: a report whose
    # reasoning_summary is only a vague placeholder triggers the RV_006 quality
    # warning while staying semantically valid (warnings never invalidate). This
    # uses the real validator API; no mocking that masks behaviour.
    result, request = _run_harness(source_tree, output_root)
    report_with_warning = dict(result.report)
    report_with_warning["reasoning_summary"] = "inconclusivo"
    validator_result = validate_report(report_with_warning)
    assert validator_result.valid is True
    assert len(validator_result.warnings) >= 1
    warning_codes = [warning.code for warning in validator_result.warnings]
    assert "RV_006" in warning_codes

    record = build_run_record(result, request, validator_result)
    recorded = record["validation"]["semantic_warnings"]
    assert len(recorded) == len(validator_result.warnings)
    recorded_codes = [warning["code"] for warning in recorded]
    assert recorded_codes == warning_codes


def test_environment_offline_default_true(source_tree: Path, output_root: Path) -> None:
    # 28. environment.offline é True por padrão.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["environment"]["offline"] is True


def test_environment_llm_used_default_false(source_tree: Path, output_root: Path) -> None:
    # 29. environment.llm_used é False por padrão.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["environment"]["llm_used"] is False


def test_environment_internet_used_default_false(
    source_tree: Path, output_root: Path
) -> None:
    # 30. environment.internet_used é False por padrão.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["environment"]["internet_used"] is False


def test_gate_decision_default_null(source_tree: Path, output_root: Path) -> None:
    # 31. gate_decision é null por padrão.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["gate_decision"] is None


# --------------------------------------------------------------------------- #
# Tests 32-37 (STEP-08)                                                         #
# --------------------------------------------------------------------------- #
def test_reviewer_findings_default_empty(source_tree: Path, output_root: Path) -> None:
    # 32. reviewer_findings é lista vazia por padrão.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["reviewer_findings"] == []


def test_build_run_record_does_not_mutate_inputs(
    source_tree: Path, output_root: Path
) -> None:
    # 33. build_run_record não muta os inputs.
    result, request = _run_harness(source_tree, output_root)
    validator_result = _validator_result(result)

    report_before = dict(result.report)
    accessed_before = tuple(result.accessed_artifacts)
    denied_before = tuple(result.denied_access_attempts)
    warnings_before = tuple(result.warnings)
    errors_before = tuple(validator_result.errors)
    val_warnings_before = tuple(validator_result.warnings)

    build_run_record(result, request, validator_result)

    assert result.report == report_before
    assert tuple(result.accessed_artifacts) == accessed_before
    assert tuple(result.denied_access_attempts) == denied_before
    assert tuple(result.warnings) == warnings_before
    assert tuple(validator_result.errors) == errors_before
    assert tuple(validator_result.warnings) == val_warnings_before


def test_validate_run_record_returns_empty_for_valid_record(
    source_tree: Path, output_root: Path
) -> None:
    # 34. validate_run_record retorna lista vazia para record válido.
    from generator.blind_solve_run_record import validate_run_record

    record = _build(source_tree, output_root)
    assert validate_run_record(record) == []


def test_validate_run_record_returns_errors_for_invalid_record(
    source_tree: Path, output_root: Path
) -> None:
    # 35. validate_run_record retorna erros para record inválido.
    from generator.blind_solve_run_record import validate_run_record

    record = _build(source_tree, output_root)
    # Removing a required top-level field must make the record invalid.
    del record["run_id"]
    errors = validate_run_record(record)
    assert errors != []


def test_execution_duration_seconds_is_non_negative_int(
    source_tree: Path, output_root: Path
) -> None:
    # 36. execution.duration_seconds é inteiro >= 0.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    duration = record["execution"]["duration_seconds"]
    assert isinstance(duration, int)
    assert not isinstance(duration, bool)
    assert duration >= 0


def test_execution_status_completed_for_normal_run(
    source_tree: Path, output_root: Path
) -> None:
    # 37. execution.status é "completed" para execução normal.
    result, request = _run_harness(source_tree, output_root)
    record = build_run_record(result, request, _validator_result(result))
    assert record["execution"]["status"] == "completed"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

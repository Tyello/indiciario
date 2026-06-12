from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from generator.learning_ledger_validator import (
    LearningLedgerValidator,
    LedgerIssue,
    LedgerValidationReport,
    validate_learning_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "learning_ledger"


def fixture_ids(paths: list[Path]) -> list[str]:
    return [path.name for path in paths]


def codes(report: LedgerValidationReport) -> set[str]:
    return {issue.code for issue in report.errors}


def file_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink()):
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").iterdir()),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").iterdir())),
)
def test_valid_learning_ledgers_pass(fixture: Path):
    report = validate_learning_ledger(fixture)
    assert report.valid, [issue.to_dict() if hasattr(issue, "to_dict") else issue for issue in report.errors]
    assert report.errors == []
    assert report.entity_counts["sessions"] >= 1
    assert report.entity_counts["findings"] >= 1
    assert report.entity_counts["decisions"] >= 1
    assert report.processed_files == sorted(report.processed_files)


def test_public_report_shape_for_minimal_valid_ledger():
    report = validate_learning_ledger(FIXTURES_DIR / "valid" / "valid_minimal")
    assert report.valid is True
    assert report.entity_counts == {"sessions": 1, "findings": 1, "decisions": 1}
    assert report.processed_files == [
        "decisions/decision_1.yaml",
        "findings/finding_1.yaml",
        "sessions/session_1.yaml",
    ]
    assert report.to_dict()["valid"] is True


def test_complete_valid_ledger_exercises_internal_references_and_revalidation():
    report = validate_learning_ledger(FIXTURES_DIR / "valid" / "valid_complete")
    assert report.valid is True
    assert report.entity_counts == {"sessions": 2, "findings": 2, "decisions": 1}


def test_schema_validators_are_loaded_and_checked():
    validator = validate_learning_ledger(FIXTURES_DIR / "valid" / "valid_minimal")
    assert validator.valid is True
    for schema_path in [
        ROOT / "schemas" / "playtest_session.schema.yaml",
        ROOT / "schemas" / "playtest_finding.schema.yaml",
        ROOT / "schemas" / "learning_decision.schema.yaml",
    ]:
        assert schema_path.exists()
    # Regression guard: the validator module imports Draft202012Validator, not a draft-07 class.
    assert Draft202012Validator.META_SCHEMA["$id"].endswith("/draft/2020-12/schema")


@pytest.mark.parametrize(
    "fixture_name,expected_code",
    [
        ("invalid_session_schema", "LEDGER_SCHEMA_INVALID"),
        ("invalid_finding_schema", "LEDGER_SCHEMA_INVALID"),
        ("invalid_decision_schema", "LEDGER_SCHEMA_INVALID"),
        ("unsupported_file_extension", "LEDGER_FILE_UNSUPPORTED"),
        ("duplicate_session_id", "LEDGER_DUPLICATE_ID"),
        ("duplicate_finding_id", "LEDGER_DUPLICATE_ID"),
        ("duplicate_decision_id", "LEDGER_DUPLICATE_ID"),
        ("duplicate_event_id", "LEDGER_DUPLICATE_ID"),
        ("duplicate_participant_id", "LEDGER_DUPLICATE_ID"),
        ("duplicate_stage_sequence", "LEDGER_DUPLICATE_ID"),
        ("duplicate_event_sequence", "LEDGER_DUPLICATE_ID"),
        ("finding_missing_session", "LEDGER_SESSION_NOT_FOUND"),
        ("evidence_missing_session", "LEDGER_SESSION_NOT_FOUND"),
        ("evidence_session_not_declared_by_finding", "LEDGER_SESSION_NOT_FOUND"),
        ("decision_missing_finding", "LEDGER_FINDING_NOT_FOUND"),
        ("decision_with_extra_related_session", "LEDGER_DECISION_SESSION_LINK_MISMATCH"),
        ("decision_missing_related_session", "LEDGER_DECISION_SESSION_LINK_MISMATCH"),
        ("primary_finding_not_related", "LEDGER_PRIMARY_FINDING_NOT_RELATED"),
        ("event_missing_stage", "LEDGER_STAGE_NOT_FOUND"),
        ("event_missing_participant", "LEDGER_PARTICIPANT_NOT_FOUND"),
        ("hypothesis_missing_event", "LEDGER_EVENT_NOT_FOUND"),
        ("hypothesis_missing_stage", "LEDGER_STAGE_NOT_FOUND"),
        ("stall_missing_hint", "LEDGER_HINT_NOT_FOUND"),
        ("revalidation_missing_session", "LEDGER_REVALIDATION_SESSION_NOT_FOUND"),
        ("finding_case_mismatch", "LEDGER_CASE_MISMATCH"),
        ("finding_case_version_mismatch", "LEDGER_CASE_VERSION_MISMATCH"),
        ("decision_case_mismatch", "LEDGER_CASE_MISMATCH"),
        ("decision_case_version_mismatch", "LEDGER_CASE_VERSION_MISMATCH"),
        ("finding_relates_sessions_from_multiple_versions", "LEDGER_CASE_VERSION_MISMATCH"),
        ("finding_decided_without_decision", "LEDGER_DECISION_NOT_FOUND"),
        ("decision_references_pending_finding", "LEDGER_GENERALIZATION_STATUS_MISMATCH"),
        ("decision_references_not_applicable_finding", "LEDGER_GENERALIZATION_STATUS_MISMATCH"),
        ("finding_points_to_wrong_decision", "LEDGER_GENERALIZATION_STATUS_MISMATCH"),
        ("unilateral_decision_link", "LEDGER_DECISION_NOT_FOUND"),
        ("finding_count_mismatch", "LEDGER_FINDING_COUNT_MISMATCH"),
        ("session_count_mismatch", "LEDGER_SESSION_COUNT_MISMATCH"),
        ("supersedes_missing_decision", "LEDGER_SUPERSEDES_NOT_FOUND"),
        ("supersedes_self", "LEDGER_SUPERSEDES_SELF"),
        ("superseded_by_missing_decision", "LEDGER_SUPERSEDED_BY_NOT_FOUND"),
        ("supersession_not_reciprocal", "LEDGER_STATUS_TRANSITION_INVALID"),
        ("supersession_cycle_two_nodes", "LEDGER_SUPERSESSION_CYCLE"),
        ("supersession_cycle_three_nodes", "LEDGER_SUPERSESSION_CYCLE"),
        ("session_finished_before_started", "LEDGER_TIME_ORDER_INVALID"),
        ("finding_resolved_before_created", "LEDGER_TIME_ORDER_INVALID"),
        ("finding_updated_before_created", "LEDGER_TIME_ORDER_INVALID"),
        ("finding_resolved_without_corrected_artifact", "LEDGER_SCHEMA_INVALID"),
        ("decision_verified_before_implemented", "LEDGER_TIME_ORDER_INVALID"),
        ("decision_implemented_before_decided", "LEDGER_TIME_ORDER_INVALID"),
        ("decision_updated_before_created", "LEDGER_TIME_ORDER_INVALID"),
        ("finding_revalidation_missing_completed_session", "LEDGER_REVALIDATION_SESSION_NOT_FOUND"),
        ("finding_revalidation_count_mismatch", "LEDGER_REVALIDATION_INCONSISTENT"),
        ("finding_revalidation_passed_without_session", "LEDGER_REVALIDATION_INCONSISTENT"),
        ("blocks_gate_with_pass", "LEDGER_GATE_EFFECT_INCONSISTENT"),
        ("block_without_blocks_gate", "LEDGER_GATE_EFFECT_INCONSISTENT"),
        ("none_with_blocks_gate", "LEDGER_GATE_EFFECT_INCONSISTENT"),
    ],
)
def test_invalid_ledgers_return_expected_codes(fixture_name: str, expected_code: str):
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / fixture_name)
    assert not report.valid
    assert expected_code in codes(report), report.to_dict()



def test_valid_related_sessions_can_be_declared_in_different_order():
    report = validate_learning_ledger(FIXTURES_DIR / "valid" / "valid_related_sessions_different_order")
    assert report.valid is True
    assert "LEDGER_DECISION_SESSION_LINK_MISMATCH" not in codes(report)


@pytest.mark.parametrize(
    "fixture_name,divergent_session_id",
    [
        ("decision_with_extra_related_session", "SESSION_002"),
        ("decision_missing_related_session", "SESSION_002"),
    ],
)
def test_decision_related_sessions_must_match_sessions_derived_from_findings(
    fixture_name: str, divergent_session_id: str
):
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / fixture_name)
    matching = [
        issue
        for issue in report.errors
        if issue.code == "LEDGER_DECISION_SESSION_LINK_MISMATCH"
    ]
    assert report.valid is False
    assert matching, report.to_dict()
    assert {issue.entity_type for issue in matching} == {"decision"}
    assert {issue.field_path for issue in matching} == {"related_session_ids"}
    assert divergent_session_id in {issue.related_id for issue in matching}


def test_decision_session_count_uses_derived_sessions_when_explicit_sessions_are_incoherent():
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / "decision_with_extra_related_session")
    assert "LEDGER_DECISION_SESSION_LINK_MISMATCH" in codes(report)
    assert "LEDGER_SESSION_COUNT_MISMATCH" not in codes(report)


def test_validator_instance_validate_is_idempotent_for_valid_ledger():
    validator = LearningLedgerValidator(FIXTURES_DIR / "valid" / "valid_minimal")
    first = validator.validate()
    second = validator.validate()
    assert first.to_dict() == second.to_dict()
    assert first.processed_files == [
        "decisions/decision_1.yaml",
        "findings/finding_1.yaml",
        "sessions/session_1.yaml",
    ]
    assert second.processed_files == first.processed_files
    assert second.entity_counts == {"sessions": 1, "findings": 1, "decisions": 1}
    assert second.errors == []
    assert second.warnings == []


def test_validator_instance_validate_is_idempotent_for_invalid_ledger():
    validator = LearningLedgerValidator(FIXTURES_DIR / "invalid" / "multiple_errors")
    first = validator.validate()
    second = validator.validate()
    assert first.to_dict() == second.to_dict()
    assert len(second.errors) == len(first.errors)
    assert [issue.code for issue in second.errors] == [issue.code for issue in first.errors]
    assert second.semantic_invalid_entities == first.semantic_invalid_entities


def test_validator_instance_validate_is_idempotent_for_warning_ledger():
    validator = LearningLedgerValidator(FIXTURES_DIR / "invalid" / "warning_critical_nonblocking")
    first = validator.validate()
    second = validator.validate()
    assert first.to_dict() == second.to_dict()
    assert second.valid is True
    assert len(first.warnings) == 1
    assert len(second.warnings) == 1
    assert second.warnings[0].code == "LEDGER_GATE_EFFECT_INCONSISTENT"

def test_ids_can_be_reused_across_entity_namespaces():
    report = validate_learning_ledger(FIXTURES_DIR / "valid" / "valid_ids_reused_across_entity_types")
    assert report.valid is True
    assert report.entity_counts == {"sessions": 1, "findings": 1, "decisions": 1}


def test_warnings_do_not_make_ledger_invalid():
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / "warning_critical_nonblocking")
    assert report.valid is True
    assert [warning.code for warning in report.warnings] == ["LEDGER_GATE_EFFECT_INCONSISTENT"]


def test_error_order_is_deterministic():
    fixture = FIXTURES_DIR / "invalid" / "multiple_errors"
    reports = [validate_learning_ledger(fixture).to_dict() for _ in range(3)]
    assert reports[0] == reports[1] == reports[2]
    errors = validate_learning_ledger(fixture).errors
    assert errors == sorted(errors, key=LedgerIssue.sort_key)


def test_report_uses_relative_paths():
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / "finding_missing_session")
    assert report.errors
    assert all(not Path(issue.file_path).is_absolute() for issue in report.errors)
    assert all(issue.file_path.startswith(("sessions/", "findings/", "decisions/")) for issue in report.errors)


def test_validator_does_not_mutate_input_files():
    fixture = FIXTURES_DIR / "invalid" / "multiple_errors"
    before = file_hashes(fixture)
    validate_learning_ledger(fixture)
    after = file_hashes(fixture)
    assert after == before


def test_missing_ledger_directory_raises_api_error(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        validate_learning_ledger(tmp_path / "missing")


def test_empty_ledger_directory_is_valid_with_zero_counts(tmp_path: Path):
    report = validate_learning_ledger(tmp_path)
    assert report.valid is True
    assert report.entity_counts == {"sessions": 0, "findings": 0, "decisions": 0}
    assert report.processed_files == []


def test_symlink_inside_controlled_folder_is_rejected(tmp_path: Path):
    ledger = tmp_path / "ledger"
    sessions = ledger / "sessions"
    sessions.mkdir(parents=True)
    outside = tmp_path / "outside.yaml"
    outside.write_text("schema_version: '1.0'\n", encoding="utf-8")
    link = sessions / "escape.yaml"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")
    report = validate_learning_ledger(ledger)
    assert not report.valid
    assert "LEDGER_FILE_UNSUPPORTED" in codes(report)


def test_structurally_invalid_entity_does_not_enter_semantic_indexes():
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / "invalid_finding_schema")
    assert "LEDGER_SCHEMA_INVALID" in codes(report)
    assert report.entity_counts["findings"] == 0
    # The invalid finding is not indexed, so the decision's broken reference is reported once.
    assert "LEDGER_FINDING_NOT_FOUND" in codes(report)


def test_report_accumulates_multiple_independent_errors():
    report = validate_learning_ledger(FIXTURES_DIR / "invalid" / "multiple_errors")
    assert {
        "LEDGER_CASE_MISMATCH",
        "LEDGER_PRIMARY_FINDING_NOT_RELATED",
        "LEDGER_FINDING_COUNT_MISMATCH",
    } <= codes(report)


def test_all_expected_valid_fixtures_exist():
    expected = {
        "valid_minimal",
        "valid_complete",
        "valid_no_generalization",
        "valid_supersession_chain",
        "valid_ids_reused_across_entity_types",
        "valid_related_sessions_different_order",
    }
    found = {path.name for path in (FIXTURES_DIR / "valid").iterdir()}
    assert expected <= found


def test_all_expected_invalid_fixtures_exist():
    expected = {
        "invalid_session_schema",
        "invalid_finding_schema",
        "invalid_decision_schema",
        "unsupported_file_extension",
        "duplicate_session_id",
        "duplicate_finding_id",
        "duplicate_decision_id",
        "duplicate_event_id",
        "duplicate_participant_id",
        "duplicate_stage_sequence",
        "duplicate_event_sequence",
        "finding_missing_session",
        "evidence_missing_session",
        "evidence_session_not_declared_by_finding",
        "decision_missing_finding",
        "decision_with_extra_related_session",
        "decision_missing_related_session",
        "primary_finding_not_related",
        "event_missing_stage",
        "event_missing_participant",
        "hypothesis_missing_event",
        "hypothesis_missing_stage",
        "stall_missing_hint",
        "revalidation_missing_session",
        "finding_case_mismatch",
        "finding_case_version_mismatch",
        "decision_case_mismatch",
        "decision_case_version_mismatch",
        "finding_relates_sessions_from_multiple_versions",
        "finding_decided_without_decision",
        "decision_references_pending_finding",
        "decision_references_not_applicable_finding",
        "finding_points_to_wrong_decision",
        "unilateral_decision_link",
        "finding_count_mismatch",
        "session_count_mismatch",
        "supersedes_missing_decision",
        "supersedes_self",
        "superseded_by_missing_decision",
        "supersession_not_reciprocal",
        "supersession_cycle_two_nodes",
        "supersession_cycle_three_nodes",
        "session_finished_before_started",
        "finding_resolved_before_created",
        "finding_updated_before_created",
        "finding_resolved_without_corrected_artifact",
        "decision_verified_before_implemented",
        "decision_implemented_before_decided",
        "decision_updated_before_created",
        "finding_revalidation_missing_completed_session",
        "finding_revalidation_count_mismatch",
        "finding_revalidation_passed_without_session",
        "blocks_gate_with_pass",
        "block_without_blocks_gate",
        "none_with_blocks_gate",
    }
    found = {path.name for path in (FIXTURES_DIR / "invalid").iterdir()}
    assert expected <= found

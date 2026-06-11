from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "learning_decision.schema.yaml"
FINDING_SCHEMA_PATH = ROOT / "schemas" / "playtest_finding.schema.yaml"
SESSION_SCHEMA_PATH = ROOT / "schemas" / "playtest_session.schema.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "learning_decision"

SCOPE_LEVELS = {
    "case_only",
    "mechanic_family",
    "difficulty_level",
    "global_editorial",
    "technical",
    "visual",
}
RESULTS = {
    "no_generalization",
    "example_only",
    "heuristic",
    "guardrail",
    "validator_candidate",
    "case_review_candidate",
    "regression_test",
}
PAYLOAD_BY_RESULT = {
    "no_generalization": "no_generalization",
    "example_only": "example",
    "heuristic": "heuristic",
    "guardrail": "guardrail",
    "validator_candidate": "validator_candidate",
    "case_review_candidate": "case_review_candidate",
    "regression_test": "regression_test",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), f"{path} must contain a YAML object"
    return data


def load_schema() -> dict[str, Any]:
    return load_yaml(SCHEMA_PATH)


def build_validator() -> Draft202012Validator:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validation_errors(fixture: Path) -> list[ValidationError]:
    validator = build_validator()
    instance = load_yaml(fixture)
    return sorted(validator.iter_errors(instance), key=lambda error: list(error.path))


def format_errors(errors: list[ValidationError]) -> str:
    lines: list[str] = []
    for error in errors:
        instance_path = ".".join(str(part) for part in error.path) or "$"
        schema_path = ".".join(str(part) for part in error.schema_path) or "$schema"
        lines.append(f"{instance_path} [{schema_path}]: {error.message}")
    return "\n".join(lines)


def fixture_ids(paths: list[Path]) -> list[str]:
    return [path.stem for path in paths]


def collect_refs(node: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(node, dict):
        if "$ref" in node:
            refs.append(node["$ref"])
        for value in node.values():
            refs.extend(collect_refs(value))
    elif isinstance(node, list):
        for value in node:
            refs.extend(collect_refs(value))
    return refs


def test_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(load_schema())


def test_schema_declares_draft_id_and_version():
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://indiciario.local/schemas/learning_decision/1.0"
    assert schema["properties"]["schema_version"] == {"const": "1.0"}


def test_internal_schema_references_point_to_defs():
    schema = load_schema()
    defs = schema["$defs"]
    refs = collect_refs(schema)
    assert refs, "schema should use internal reusable definitions"
    for ref in refs:
        assert ref.startswith("#/$defs/")
        assert ref.removeprefix("#/$defs/") in defs


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").glob("*.yaml"))),
)
def test_valid_learning_decision_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors == [], f"{fixture.name} should be valid:\n{format_errors(errors)}"


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_learning_decision_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be rejected by learning_decision schema"


def test_validator_uses_format_checker():
    assert build_validator().format_checker is not None


def test_all_expected_valid_fixtures_exist():
    expected = {
        "valid_no_generalization_minimal",
        "valid_example_only",
        "valid_heuristic",
        "valid_guardrail",
        "valid_validator_candidate",
        "valid_case_review_candidate",
        "valid_regression_test",
        "valid_global_editorial_with_exception",
        "valid_verified_decision",
        "valid_implemented_decision",
        "valid_superseded_after_verification",
        "valid_global_editorial_repeated_pattern",
        "valid_complete",
    }
    found = {path.stem for path in (FIXTURES_DIR / "valid").glob("*.yaml")}
    assert expected <= found


def test_all_expected_invalid_fixtures_exist():
    expected = {
        "missing_schema_version",
        "missing_learning_decision_id",
        "missing_related_finding_ids",
        "empty_related_finding_ids",
        "missing_scope",
        "invalid_scope",
        "missing_result",
        "invalid_result",
        "missing_rationale",
        "rationale_without_evidence_reviewed",
        "missing_evidence_summary",
        "missing_decided_at",
        "invalid_timestamp_without_timezone",
        "missing_decided_by",
        "empty_identifier",
        "unexpected_property",
        "global_editorial_without_applicability_conditions",
        "global_editorial_single_session_without_exception",
        "global_editorial_no_repeated_pattern_without_exception",
        "no_generalization_without_payload",
        "no_generalization_without_reason",
        "example_only_without_example",
        "example_without_reference",
        "heuristic_without_statement",
        "heuristic_without_conditions",
        "guardrail_without_normative_rule",
        "guardrail_without_validation_plan",
        "validator_candidate_without_required_inputs",
        "validator_candidate_without_test_strategy",
        "case_review_candidate_without_target_section",
        "regression_test_without_scenario",
        "regression_test_without_validation_command",
        "heuristic_with_guardrail_payload",
        "guardrail_with_validator_payload",
        "no_generalization_with_heuristic_payload",
        "result_payload_conflict",
        "verified_without_implementation_evidence",
        "verified_without_verified_by",
        "rejected_after_review_without_reason",
        "superseded_without_replacement",
        "revalidation_required_without_method",
        "revalidation_required_without_success_criteria",
        "revalidation_not_required_with_pending_status",
        "enforcement_target_other_without_notes",
        "validation_target_other_without_notes",
        "test_level_other_without_notes",
        "global_scope_without_global_evidence_basis",
        "lowercase_learning_decision_id",
        "learning_decision_id_with_colon",
        "learning_decision_id_with_dot",
        "one_character_learning_decision_id",
        "learning_decision_id_too_long",
        "lowercase_related_finding_id",
        "not_planned_with_verification_payload",
        "proposed_with_implementation_payload",
        "proposed_with_rejection_payload",
        "approved_with_verification_payload",
        "implemented_without_reference",
        "implemented_without_implemented_at",
        "implemented_without_implemented_by",
        "implemented_with_verification_payload",
        "verified_without_implementation_reference",
        "verified_without_implemented_at",
        "verified_without_implemented_by",
        "verified_with_rejection_payload",
        "rejected_after_review_with_implementation_payload",
        "rejected_after_review_with_verification_payload",
        "not_superseded_with_superseded_by",
    }
    found = {path.stem for path in (FIXTURES_DIR / "invalid").glob("*.yaml")}
    assert expected <= found



def test_neutral_id_matches_session_and_finding_schemas():
    decision = load_schema()["$defs"]["neutral_id"]
    finding = load_yaml(FINDING_SCHEMA_PATH)["$defs"]["neutral_id"]
    session = load_yaml(SESSION_SCHEMA_PATH)["$defs"]["neutral_id"]
    keys = {"type", "minLength", "maxLength", "pattern"}
    assert {key: decision.get(key) for key in keys} == {key: finding.get(key) for key in keys}
    assert {key: decision.get(key) for key in keys} == {key: session.get(key) for key in keys}


def test_global_exception_justification_has_single_source_of_truth():
    schema = load_schema()
    scope_properties = schema["$defs"]["scope"]["properties"]
    global_basis_properties = schema["$defs"]["global_evidence_basis"]["properties"]
    assert "explicit_exception_justification" not in scope_properties
    assert "exception_justification" not in scope_properties
    assert "exception_justification" in global_basis_properties


def test_scope_and_result_enums_are_exact():
    schema = load_schema()
    assert set(schema["$defs"]["scope"]["properties"]["level"]["enum"]) == SCOPE_LEVELS
    assert set(schema["properties"]["result"]["enum"]) == RESULTS


def test_payloads_are_exclusive_for_each_result():
    for result, payload in PAYLOAD_BY_RESULT.items():
        fixture = FIXTURES_DIR / "valid" / f"valid_{result if result != 'no_generalization' else 'no_generalization_minimal'}.yaml"
        if not fixture.exists():
            fixture = next((FIXTURES_DIR / "valid").glob(f"*{result}*.yaml"))
        instance = load_yaml(fixture)
        assert instance["result"] == result
        assert payload in instance
        incompatible = set(PAYLOAD_BY_RESULT.values()) - {payload}
        assert incompatible.isdisjoint(instance.keys())


@pytest.mark.parametrize(
    "fixture_name",
    [
        "heuristic_with_guardrail_payload",
        "guardrail_with_validator_payload",
        "no_generalization_with_heuristic_payload",
        "result_payload_conflict",
    ],
)
def test_incompatible_payloads_are_rejected(fixture_name: str):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should reject incompatible payloads"


@pytest.mark.parametrize(
    "fixture_name,expected_path",
    [
        ("global_editorial_without_applicability_conditions", ["scope", "applicability_conditions"]),
        ("global_editorial_single_session_without_exception", ["global_evidence_basis"]),
        ("global_editorial_no_repeated_pattern_without_exception", ["global_evidence_basis"]),
        ("global_scope_without_global_evidence_basis", ["$"]),
    ],
)
def test_global_editorial_conditionals(fixture_name: str, expected_path: list[str]):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    if expected_path != ["$"]:
        assert any(list(error.path)[: len(expected_path)] == expected_path for error in errors), format_errors(errors)


@pytest.mark.parametrize(
    "fixture_name,expected_field",
    [
        ("verified_without_implementation_evidence", "implementation_evidence"),
        ("verified_without_verified_by", "verified_by"),
        ("rejected_after_review_without_reason", "rejection_reason"),
        ("superseded_without_replacement", "superseded_by_decision_id"),
    ],
)
def test_implementation_status_conditionals(fixture_name: str, expected_field: str):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    assert any(expected_field in error.message for error in errors), format_errors(errors)


@pytest.mark.parametrize(
    "fixture_name,expected_field",
    [
        ("revalidation_required_without_method", "method"),
        ("revalidation_required_without_success_criteria", "success_criteria"),
        ("revalidation_not_required_with_pending_status", "not_required"),
    ],
)
def test_revalidation_conditionals(fixture_name: str, expected_field: str):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    assert any(expected_field in error.message or expected_field in str(error.schema_path) for error in errors), format_errors(errors)



def test_global_editorial_repeated_pattern_does_not_require_exception():
    fixture = FIXTURES_DIR / "valid" / "valid_global_editorial_repeated_pattern.yaml"
    instance = load_yaml(fixture)
    assert instance["scope"]["level"] == "global_editorial"
    assert instance["global_evidence_basis"]["multiple_sessions"] is True
    assert instance["global_evidence_basis"]["repeated_pattern"] is True
    assert "exception_justification" not in instance["global_evidence_basis"]
    assert validation_errors(fixture) == []


@pytest.mark.parametrize(
    "fixture_name",
    [
        "not_planned_with_verification_payload",
        "proposed_with_implementation_payload",
        "proposed_with_rejection_payload",
        "approved_with_verification_payload",
        "implemented_with_verification_payload",
        "verified_with_rejection_payload",
        "rejected_after_review_with_implementation_payload",
        "rejected_after_review_with_verification_payload",
        "not_superseded_with_superseded_by",
    ],
)
def test_implementation_status_rejects_incompatible_payloads(fixture_name: str):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should reject incompatible implementation_status payloads"


@pytest.mark.parametrize(
    "fixture_name,expected_field",
    [
        ("implemented_without_reference", "implementation_reference"),
        ("implemented_without_implemented_at", "implemented_at"),
        ("implemented_without_implemented_by", "implemented_by"),
        ("verified_without_implementation_reference", "implementation_reference"),
        ("verified_without_implemented_at", "implemented_at"),
        ("verified_without_implemented_by", "implemented_by"),
    ],
)
def test_implementation_status_requires_own_payload_fields(fixture_name: str, expected_field: str):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    assert any(expected_field in error.message for error in errors), format_errors(errors)


def test_superseded_can_preserve_implementation_and_verification_history():
    fixture = FIXTURES_DIR / "valid" / "valid_superseded_after_verification.yaml"
    instance = load_yaml(fixture)
    assert instance["implementation_status"] == "superseded"
    assert "superseded_by_decision_id" in instance
    assert {"implementation_reference", "implemented_at", "implemented_by"} <= instance.keys()
    assert {"implementation_evidence", "verified_at", "verified_by"} <= instance.keys()
    assert validation_errors(fixture) == []


def test_timestamp_without_timezone_is_rejected_by_format_checked_validator():
    errors = validation_errors(FIXTURES_DIR / "invalid" / "invalid_timestamp_without_timezone.yaml")
    assert errors
    assert any(list(error.path) == ["decided_at"] for error in errors), format_errors(errors)


@pytest.mark.parametrize(
    "fixture_name,limitation",
    [
        ("missing_external_finding_reference", "related_finding_ids_exist"),
        ("supersedes_self", "supersedes_not_self"),
        ("finding_count_mismatch", "finding_count_matches_references"),
        ("primary_finding_not_related", "primary_finding_id_is_related"),
    ],
)
def test_semantic_validation_deferred_to_issue_08_is_explicit(fixture_name: str, limitation: str):
    schema = load_schema()
    assert limitation in schema["x-semantic-limitations-deferred-to-issue-08"]
    fixture = FIXTURES_DIR / "semantic_limitations" / f"{fixture_name}.yaml"
    errors = validation_errors(fixture)
    assert errors == [], f"{fixture.name} should remain structurally valid:\n{format_errors(errors)}"

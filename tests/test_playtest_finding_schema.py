from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "playtest_finding.schema.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "playtest_finding"


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


def test_schema_is_valid_draft_2020_12():
    schema = load_schema()
    Draft202012Validator.check_schema(schema)


def test_schema_declares_draft_id_and_version():
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://indiciario.local/schemas/playtest_finding/1.0"
    assert schema["properties"]["schema_version"] == {"const": "1.0"}


def test_internal_schema_references_point_to_defs():
    schema = load_schema()
    defs = schema["$defs"]
    refs: list[str] = []

    def collect_refs(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                refs.append(node["$ref"])
            for value in node.values():
                collect_refs(value)
        elif isinstance(node, list):
            for value in node:
                collect_refs(value)

    collect_refs(schema)
    assert refs, "schema should use internal reusable definitions"
    for ref in refs:
        assert ref.startswith("#/$defs/")
        assert ref.removeprefix("#/$defs/") in defs


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").glob("*.yaml"))),
)
def test_valid_playtest_finding_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors == [], f"{fixture.name} should be valid:\n{format_errors(errors)}"


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_playtest_finding_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be rejected by playtest_finding schema"


def test_validator_uses_format_checker():
    assert build_validator().format_checker is not None


def test_all_expected_valid_fixtures_exist():
    expected = {
        "valid_accepted_minimal",
        "valid_rejected",
        "valid_deferred",
        "valid_not_applicable",
        "valid_resolved",
        "valid_complete",
    }
    found = {path.stem for path in (FIXTURES_DIR / "valid").glob("*.yaml")}
    assert expected <= found


def test_all_expected_invalid_fixtures_exist():
    expected = {
        "missing_schema_version",
        "missing_finding_id",
        "missing_source_session_ids",
        "empty_source_session_ids",
        "missing_observation",
        "missing_evidence",
        "empty_evidence",
        "missing_causal_hypothesis",
        "invalid_category",
        "category_other_without_notes",
        "invalid_severity",
        "invalid_status",
        "accepted_without_action_expected",
        "accepted_without_assigned_to",
        "rejected_without_reason",
        "rejected_without_rejection_risk",
        "deferred_without_residual_risk",
        "deferred_without_review_condition",
        "not_applicable_without_reason",
        "resolved_without_corrected_artifacts",
        "resolved_without_validation_evidence",
        "resolved_with_failed_validation",
        "rollback_required_without_reason",
        "rollback_not_required_with_non_none_target",
        "rollback_other_without_notes",
        "stage_scope_without_stage_ids",
        "artifact_scope_without_artifact_ids",
        "impact_without_description",
        "decided_generalization_without_decision_id",
        "pending_generalization_with_decision_id",
        "invalid_timestamp_without_timezone",
        "unexpected_property",
        "empty_identifier",
    }
    found = {path.stem for path in (FIXTURES_DIR / "invalid").glob("*.yaml")}
    assert expected <= found


@pytest.mark.parametrize(
    "fixture_name,path",
    [
        ("accepted_without_action_expected", ["action_expected"]),
        ("accepted_without_assigned_to", ["assigned_to"]),
        ("rejected_without_reason", ["rejection"]),
        ("rejected_without_rejection_risk", ["rejection"]),
        ("deferred_without_residual_risk", ["deferral"]),
        ("deferred_without_review_condition", ["deferral"]),
        ("not_applicable_without_reason", ["not_applicable"]),
        ("resolved_without_corrected_artifacts", ["resolution", "corrected_artifact_version_ids"]),
        ("resolved_without_validation_evidence", ["resolution", "validation_evidence"]),
        ("resolved_with_failed_validation", ["resolution", "validation_result"]),
    ],
)
def test_status_conditionals_are_structural(fixture_name: str, path: list[str]):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    expected_field = path[-1]
    assert any(
        list(error.path) == path
        or list(error.path)[: len(path)] == path
        or expected_field in error.message
        for error in errors
    ), format_errors(errors)


@pytest.mark.parametrize(
    "fixture_name,path",
    [
        ("decided_generalization_without_decision_id", ["learning_decision_id"]),
        ("pending_generalization_with_decision_id", ["$"]),
    ],
)
def test_generalization_status_conditionals(fixture_name: str, path: list[str]):
    errors = validation_errors(FIXTURES_DIR / "invalid" / f"{fixture_name}.yaml")
    assert errors, f"{fixture_name} should be invalid"
    if path != ["$"]:
        expected_field = path[-1]
        assert any(
            list(error.path) == path or expected_field in error.message
            for error in errors
        ), format_errors(errors)


def test_timestamp_without_timezone_is_rejected_by_format_checked_validator():
    fixture = FIXTURES_DIR / "invalid" / "invalid_timestamp_without_timezone.yaml"
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be invalid"
    assert any(list(error.path) == ["created_at"] for error in errors), format_errors(errors)


@pytest.mark.parametrize(
    "fixture_name,limitation",
    [
        ("missing_external_session_reference", "source_session_ids_exist"),
        ("duplicate_evidence_id_by_property", "evidence_id_uniqueness_by_property"),
        ("duplicate_of_self", "duplicate_of_not_self"),
    ],
)
def test_semantic_validation_deferred_to_issue_08_is_explicit(
    fixture_name: str, limitation: str
):
    schema = load_schema()
    assert limitation in schema["x-semantic-limitations-deferred-to-issue-08"]
    fixture = FIXTURES_DIR / "semantic_limitations" / f"{fixture_name}.yaml"
    errors = validation_errors(fixture)
    assert (
        errors == []
    ), f"{fixture.name} should remain structurally valid:\n{format_errors(errors)}"

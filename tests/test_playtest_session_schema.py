from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "playtest_session.schema.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "playtest_session"


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
    assert schema["$id"] == "https://indiciario.local/schemas/playtest_session/1.0"
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
def test_valid_playtest_session_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors == [], f"{fixture.name} should be valid:\n{format_errors(errors)}"


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_playtest_session_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be rejected by playtest_session schema"


def test_validator_uses_format_checker():
    assert build_validator().format_checker is not None


def test_timestamp_without_timezone_is_rejected_by_format_checked_validator():
    fixture = FIXTURES_DIR / "invalid" / "invalid_timestamp_without_timezone.yaml"
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be invalid"
    assert any(list(error.path) == ["started_at"] for error in errors), format_errors(
        errors
    )


def test_ratings_not_collected_accepts_missing_numeric_values():
    fixture = FIXTURES_DIR / "valid" / "valid_ratings_not_collected.yaml"
    errors = validation_errors(fixture)
    assert errors == [], f"{fixture.name} should be valid:\n{format_errors(errors)}"


def test_collected_ratings_require_main_numeric_values():
    fixture = FIXTURES_DIR / "invalid" / "ratings_collected_without_values.yaml"
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be invalid"
    assert any(list(error.path) == ["ratings"] for error in errors), format_errors(
        errors
    )


def test_all_expected_valid_fixtures_exist():
    expected = {"valid_minimal", "valid_complete", "valid_ratings_not_collected"}
    found = {path.stem for path in (FIXTURES_DIR / "valid").glob("*.yaml")}
    assert expected <= found


def test_all_expected_invalid_fixtures_exist():
    expected = {
        "missing_schema_version",
        "invalid_schema_version",
        "missing_session_id",
        "missing_case_id",
        "missing_case_version",
        "invalid_timestamp_without_timezone",
        "negative_duration",
        "empty_participants",
        "participant_with_personal_email",
        "event_without_sequence",
        "negative_elapsed_minutes",
        "rating_below_minimum",
        "rating_above_maximum",
        "ratings_collected_without_values",
        "invalid_outcome_enum",
        "unexpected_property",
        "hint_without_temporal_reference",
        "hypothesis_without_stage",
        "hypothesis_without_moment",
        "empty_events",
    }
    found = {path.stem for path in (FIXTURES_DIR / "invalid").glob("*.yaml")}
    assert expected <= found


@pytest.mark.parametrize(
    "fixture_name,limitation",
    [
        ("finished_before_started", "finished_at_after_started_at"),
        ("duplicate_event_sequence", "event_sequence_uniqueness"),
        ("duplicate_participant_id", "participant_id_uniqueness"),
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

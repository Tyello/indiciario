from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "blind_solver_report.schema.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "blind_solver_report"

PROHIBITED_FIELDS = (
    "final_solution_private",
    "answer_key",
    "hidden_notes",
    "future_envelope_notes",
    "private_author_notes",
    "raw_prompt",
    "chain_of_thought",
    "other_agent_outputs",
)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_schema() -> dict[str, Any]:
    return load_yaml(SCHEMA_PATH)


def build_validator() -> Draft202012Validator:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validation_errors(instance: Any) -> list[ValidationError]:
    return sorted(build_validator().iter_errors(instance), key=lambda error: list(error.path))


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


def valid_report() -> dict[str, Any]:
    return load_yaml(FIXTURES_DIR / "valid" / "valid_complete.yaml")


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(load_schema())


def test_schema_declares_draft_id_and_version() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://indiciario.local/schemas/blind_solver_report/1.0"
    assert schema["properties"]["schema_version"] == {"const": "1.0"}
    assert schema["additionalProperties"] is False


def test_internal_schema_references_point_to_defs() -> None:
    schema = load_schema()
    defs = schema["$defs"]
    refs = collect_refs(schema)
    assert refs, "schema should use reusable $defs"
    for ref in refs:
        assert ref.startswith("#/$defs/")
        assert ref.removeprefix("#/$defs/") in defs


def test_confidence_enum_is_low_medium_high() -> None:
    assert set(load_schema()["$defs"]["confidence"]["enum"]) == {"low", "medium", "high"}


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").glob("*.yaml"))),
)
def test_valid_fixtures_pass(fixture: Path) -> None:
    errors = validation_errors(load_yaml(fixture))
    assert errors == [], "; ".join(error.message for error in errors)


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_fixtures_fail(fixture: Path) -> None:
    assert validation_errors(load_yaml(fixture)), f"expected {fixture.name} to be rejected"


@pytest.mark.parametrize("field", PROHIBITED_FIELDS)
def test_prohibited_fields_are_rejected(field: str) -> None:
    report = valid_report()
    report[field] = "conteudo proibido"
    assert validation_errors(report), f"prohibited field {field} must be rejected"


def test_minimal_report_without_conclusion_is_structurally_valid() -> None:
    # The schema is structural only; "evidence required when conclusion present"
    # is a harness-level semantic check, not a schema constraint.
    report = valid_report()
    report["conclusion"] = ""
    report["evidence_used"] = []
    assert validation_errors(report) == []

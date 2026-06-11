from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

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


def resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    assert ref.startswith(
        "#/$defs/"
    ), f"Only local $defs refs are used in this schema test helper: {ref}"
    node: Any = schema
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    assert isinstance(node, dict), f"Reference {ref} did not resolve to an object"
    return node


def validate_instance(
    instance: Any,
    node: dict[str, Any],
    root: dict[str, Any],
    path: str = "$",
    *,
    apply_required: bool = True,
) -> list[str]:
    if "$ref" in node:
        return validate_instance(
            instance,
            resolve_ref(root, node["$ref"]),
            root,
            path,
            apply_required=apply_required,
        )

    errors: list[str] = []

    if "allOf" in node:
        for option in node["allOf"]:
            errors.extend(
                validate_instance(
                    instance, option, root, path, apply_required=apply_required
                )
            )

    if "anyOf" in node:
        branch_errors = [
            validate_instance(
                instance, option, root, path, apply_required=apply_required
            )
            for option in node["anyOf"]
        ]
        if not any(not item for item in branch_errors):
            errors.append(f"{path}: did not match anyOf")

    expected = node.get("type")
    if expected is not None:
        if expected == "object" and not isinstance(instance, dict):
            return [f"{path}: expected object"]
        if expected == "array" and not isinstance(instance, list):
            return [f"{path}: expected array"]
        if expected == "string" and not isinstance(instance, str):
            return [f"{path}: expected string"]
        if expected == "integer" and (
            not isinstance(instance, int) or isinstance(instance, bool)
        ):
            return [f"{path}: expected integer"]
        if expected == "boolean" and not isinstance(instance, bool):
            return [f"{path}: expected boolean"]

    if "const" in node and instance != node["const"]:
        errors.append(f"{path}: expected const {node['const']!r}")
    if "enum" in node and instance not in node["enum"]:
        errors.append(f"{path}: expected one of {node['enum']!r}")

    if isinstance(instance, str):
        if len(instance) < node.get("minLength", 0):
            errors.append(f"{path}: string shorter than minLength")
        if "maxLength" in node and len(instance) > node["maxLength"]:
            errors.append(f"{path}: string longer than maxLength")
        if "pattern" in node:
            import re

            if re.search(node["pattern"], instance) is None:
                errors.append(f"{path}: string does not match pattern")
        if node.get("format") == "date-time":
            import datetime as dt

            text = instance.replace("Z", "+00:00")
            try:
                parsed = dt.datetime.fromisoformat(text)
            except ValueError:
                errors.append(f"{path}: invalid RFC 3339 date-time")
            else:
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    errors.append(f"{path}: date-time must include timezone")

    if isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in node and instance < node["minimum"]:
            errors.append(f"{path}: integer below minimum")
        if "maximum" in node and instance > node["maximum"]:
            errors.append(f"{path}: integer above maximum")

    if isinstance(instance, list):
        if len(instance) < node.get("minItems", 0):
            errors.append(f"{path}: array shorter than minItems")
        if node.get("uniqueItems"):
            seen = []
            for item in instance:
                if item in seen:
                    errors.append(f"{path}: array items are not unique")
                    break
                seen.append(item)
        if "items" in node:
            for idx, item in enumerate(instance):
                errors.extend(
                    validate_instance(item, node["items"], root, f"{path}[{idx}]")
                )

    if isinstance(instance, dict):
        required = node.get("required", []) if apply_required else []
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")
        for key, value in instance.items():
            if key in properties:
                errors.extend(
                    validate_instance(value, properties[key], root, f"{path}.{key}")
                )
    return errors


def validation_errors(fixture: Path) -> list[str]:
    schema = load_schema()
    instance = load_yaml(fixture)
    return validate_instance(instance, schema, schema)


def fixture_ids(paths: list[Path]) -> list[str]:
    return [path.stem for path in paths]


def test_schema_is_loadable_and_declares_draft_and_version():
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://indiciario.local/schemas/playtest_session/1.0"
    assert schema["properties"]["schema_version"] == {"const": "1.0"}


def test_internal_schema_references_resolve():
    schema = load_schema()
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
        resolve_ref(schema, ref)


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").glob("*.yaml"))),
)
def test_valid_playtest_session_fixtures(fixture: Path):
    assert validation_errors(fixture) == []


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_playtest_session_fixtures(fixture: Path):
    errors = validation_errors(fixture)
    assert errors, f"{fixture.name} should be rejected by playtest_session schema"


def test_all_expected_valid_fixtures_exist():
    expected = {"valid_minimal", "valid_complete"}
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
    assert validation_errors(fixture) == []

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "blind_bundle_manifest.schema.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "blind_bundle_manifest"

EXPECTED_ROLES = {
    "blind_solver",
    "logic_reviewer",
    "narrative_reviewer",
    "evidence_reviewer",
    "visual_reviewer",
    "accessibility_reviewer",
    "adversarial_reviewer",
    "gate_evaluator",
    "facilitator",
    "human_operator",
    "technical_reviewer",
}
EXPECTED_STAGES = {
    "case_generation",
    "preflight_review",
    "blind_solve",
    "evidence_review",
    "narrative_review",
    "visual_review",
    "accessibility_review",
    "adversarial_review",
    "gate_evaluation",
    "playtest_analysis",
    "learning_review",
    "technical_validation",
}
EXPECTED_VISIBILITY_CATEGORIES = {
    "public_player",
    "private_author",
    "review_private",
    "facilitator",
    "derived_report",
    "playtest_anonymized",
    "technical_metadata",
}
EXPECTED_SEMANTIC_LIMITATIONS = {
    "artifact_paths_exist",
    "artifact_hashes_match_file_content",
    "manifest_hash_matches_content",
    "role_visibility_matrix_complete",
    "allowed_and_prohibited_categories_do_not_overlap",
    "transformation_hash_chain_valid",
    "source_artifacts_exist",
    "target_artifacts_exist",
    "isolation_check_was_actually_run",
    "no_semantic_solution_leak",
    "no_filename_based_solution_leak",
    "no_metadata_leak",
    "no_future_envelope_semantic_leak",
    "output_contract_enforced_by_runner",
    "bundle_root_exists",
    "role_instructions_exist",
    "artifact_count_matches_lists",
    "transformations_are_non_destructive",
    "manifest_id_unique",
    "bundle_id_unique",
    "run_id_exists",
}


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


def validation_errors_from_fixture(fixture: Path) -> list[ValidationError]:
    return validation_errors(load_yaml(fixture))


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
    assert schema["$id"] == "https://indiciario.local/schemas/blind_bundle_manifest/1.0"
    assert schema["properties"]["schema_version"] == {"const": "1.0"}


def test_internal_schema_references_point_to_defs():
    schema = load_schema()
    defs = schema["$defs"]
    refs = collect_refs(schema)
    assert refs, "schema should use reusable $defs"
    for ref in refs:
        assert ref.startswith("#/$defs/")
        assert ref.removeprefix("#/$defs/") in defs


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "valid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "valid").glob("*.yaml"))),
)
def test_valid_blind_bundle_manifest_fixtures(fixture: Path):
    errors = validation_errors_from_fixture(fixture)
    assert errors == [], f"{fixture.name} should be valid:\n{format_errors(errors)}"


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURES_DIR / "invalid").glob("*.yaml")),
    ids=fixture_ids(sorted((FIXTURES_DIR / "invalid").glob("*.yaml"))),
)
def test_invalid_blind_bundle_manifest_fixtures(fixture: Path):
    errors = validation_errors_from_fixture(fixture)
    assert errors, f"{fixture.name} should be rejected by blind_bundle_manifest schema"


def test_validator_uses_format_checker():
    assert build_validator().format_checker is not None


def test_all_expected_valid_fixtures_exist():
    expected = {
        "valid_minimal_blind_solver",
        "valid_narrative_reviewer",
        "valid_visual_reviewer_with_transformations",
        "valid_gate_evaluator",
        "valid_complete",
    }
    found = {path.stem for path in (FIXTURES_DIR / "valid").glob("*.yaml")}
    assert expected <= found


def test_all_expected_invalid_fixtures_exist():
    expected = {
        "missing_schema_version",
        "invalid_schema_version",
        "missing_manifest_id",
        "missing_run_id",
        "missing_bundle_id",
        "missing_role",
        "invalid_role",
        "missing_stage",
        "invalid_stage",
        "missing_visibility_policy",
        "missing_included_artifacts",
        "empty_included_artifacts",
        "artifact_missing_path",
        "artifact_missing_visibility",
        "artifact_missing_hash",
        "artifact_invalid_hash",
        "artifact_absolute_path",
        "artifact_parent_traversal_path",
        "blind_solver_includes_solution",
        "blind_solver_includes_answer_key",
        "blind_solver_includes_future_envelope",
        "blind_solver_includes_private_author",
        "blind_solver_allows_solution",
        "blind_solver_allows_future_envelopes",
        "blind_solver_allows_private_notes",
        "blind_solver_allows_other_agents_outputs",
        "missing_output_contract",
        "output_contract_without_required_sections",
        "output_contract_without_must_not_reveal",
        "missing_isolation_check",
        "isolation_failed_without_issues",
        "isolation_warning_status_without_warnings",
        "isolation_not_run_without_reason",
        "blind_solver_isolation_not_run",
        "transformation_missing_source",
        "transformation_missing_target",
        "transformation_same_source_target",
        "transformation_other_without_notes",
        "transformation_changes_content_without_rationale",
        "excluded_artifact_missing_reason",
        "excluded_artifact_other_without_notes",
        "unexpected_root_property",
        "unexpected_artifact_property",
        "empty_prohibited_categories",
        "role_with_prohibited_category_included",
        "artifact_visibility_not_allowed_for_role",
    }
    found = {path.stem for path in (FIXTURES_DIR / "invalid").glob("*.yaml")}
    assert expected <= found


def test_role_stage_and_visibility_enums_are_explicit():
    defs = load_schema()["$defs"]
    assert set(defs["role"]["enum"]) == EXPECTED_ROLES
    assert set(defs["stage"]["enum"]) == EXPECTED_STAGES
    assert set(defs["visibility_category"]["enum"]) == EXPECTED_VISIBILITY_CATEGORIES


@pytest.mark.parametrize("path", ["/absolute/file.md", "../secret.md", "docs/../solution.md", "folder//file.md", r"folder\\file.md"])
def test_paths_must_be_relative_posix_and_safe(path: str):
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    instance["included_artifacts"][0]["path"] = path
    errors = validation_errors(instance)
    assert errors, f"unsafe path should be rejected: {path}"


@pytest.mark.parametrize("hash_value", ["A" * 64, "sha256:" + "a" * 64, "a" * 63, "g" * 64])
def test_hashes_must_be_lowercase_sha256_hex(hash_value: str):
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    instance["included_artifacts"][0]["hash"] = hash_value
    errors = validation_errors(instance)
    assert errors, f"invalid hash should be rejected: {hash_value}"


@pytest.mark.parametrize(
    "field,value",
    [
        ("artifact_type", "solution"),
        ("artifact_type", "answer_key"),
        ("envelope_scope", "future_envelopes"),
        ("visibility", "private_author"),
        ("visibility", "facilitator"),
    ],
)
def test_blind_solver_rejects_forbidden_included_artifact_payloads(field: str, value: str):
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    instance["included_artifacts"][0][field] = value
    errors = validation_errors(instance)
    assert errors, f"blind_solver should reject included artifact {field}={value}"


@pytest.mark.parametrize(
    "field",
    [
        "allow_solution",
        "allow_future_envelopes",
        "allow_private_notes",
        "allow_other_agents_outputs",
        "contains_solution",
        "contains_future_envelopes",
        "contains_private_author_notes",
        "contains_other_agents_outputs",
    ],
)
def test_blind_solver_safety_flags_must_be_false(field: str):
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    instance["visibility_policy"][field] = True
    errors = validation_errors(instance)
    assert errors, f"blind_solver should require visibility_policy.{field}=false"


def test_blind_solver_isolation_check_cannot_be_not_run():
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    instance["isolation_check"]["status"] = "not_run"
    instance["isolation_check"]["not_run_reason"] = "Not checked yet."
    errors = validation_errors(instance)
    assert errors, "blind_solver should require an isolation check that has run"


def test_isolation_failed_requires_issues():
    errors = validation_errors_from_fixture(FIXTURES_DIR / "invalid" / "isolation_failed_without_issues.yaml")
    assert errors
    assert any("issues" in error.message or "issues" in str(error.schema_path) for error in errors), format_errors(errors)


def test_isolation_passed_with_warnings_requires_warnings():
    errors = validation_errors_from_fixture(FIXTURES_DIR / "invalid" / "isolation_warning_status_without_warnings.yaml")
    assert errors
    assert any("warnings" in error.message or "warnings" in str(error.schema_path) for error in errors), format_errors(errors)


def test_isolation_not_run_requires_reason():
    errors = validation_errors_from_fixture(FIXTURES_DIR / "invalid" / "isolation_not_run_without_reason.yaml")
    assert errors
    assert any("not_run_reason" in error.message or "not_run_reason" in str(error.schema_path) for error in errors), format_errors(errors)


@pytest.mark.parametrize(
    "mutation,expected_field",
    [
        (lambda item: item.pop("source_path"), "source_path"),
        (lambda item: item.pop("target_path"), "target_path"),
        (lambda item: item.__setitem__("type", "other"), "type_notes"),
        (lambda item: item.__setitem__("preserves_player_visible_content", False), "content_change_rationale"),
    ],
)
def test_transformation_conditionals(mutation, expected_field: str):
    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_visual_reviewer_with_transformations.yaml")
    mutation(instance["transformations"][0])
    errors = validation_errors(instance)
    assert errors
    assert any(expected_field in error.message or expected_field in str(error.schema_path) for error in errors), format_errors(errors)


def test_main_objects_are_closed():
    schema = load_schema()
    object_defs = [
        schema,
        schema["$defs"]["bundle_context"],
        schema["$defs"]["visibility_policy"],
        schema["$defs"]["included_artifact"],
        schema["$defs"]["excluded_artifact"],
        schema["$defs"]["transformation"],
        schema["$defs"]["output_contract"],
        schema["$defs"]["isolation_check"],
        schema["$defs"]["check"],
        schema["$defs"]["issue"],
        schema["$defs"]["warning"],
        schema["$defs"]["integrity"],
    ]
    assert all(definition["additionalProperties"] is False for definition in object_defs)


def test_semantic_limitations_are_declared_and_acknowledged():
    schema = load_schema()
    limitations = set(schema["x-semantic-limitations-deferred-to-issue-12-or-later"])
    assert EXPECTED_SEMANTIC_LIMITATIONS <= limitations

    instance = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    assert EXPECTED_SEMANTIC_LIMITATIONS <= set(instance["semantic_limitations_acknowledged"])


def test_semantic_limitations_fixtures_remain_structurally_valid():
    for fixture in sorted((FIXTURES_DIR / "semantic_limitations").glob("*.yaml")):
        errors = validation_errors_from_fixture(fixture)
        assert errors == [], f"{fixture.name} should remain structurally valid:\n{format_errors(errors)}"

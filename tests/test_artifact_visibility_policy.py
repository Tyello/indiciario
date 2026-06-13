from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from generator.artifact_visibility_policy import (
    ArtifactVisibilityInput,
    PolicyDecision,
    PolicyReport,
    evaluate_artifact_visibility,
    evaluate_manifest_visibility,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "blind_bundle_manifest"


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def artifact_input(**overrides: Any) -> ArtifactVisibilityInput:
    defaults = {
        "role": "blind_solver",
        "stage": "blind_solve",
        "artifact_id": "ART1",
        "artifact_type": "player_document",
        "visibility": "public_player",
        "envelope_scope": "current_envelope",
        "contains_solution": False,
        "contains_future_envelopes": False,
        "contains_private_author_notes": False,
        "contains_other_agents_outputs": False,
    }
    defaults.update(overrides)
    return ArtifactVisibilityInput(**defaults)


def assert_decision_shape(decision: PolicyDecision) -> None:
    assert decision.severity in {"allow", "warn", "deny"}
    assert decision.rule_id
    assert decision.reason
    assert decision.recommended_action
    assert isinstance(decision.matched_conditions, list)
    assert decision.allowed is (decision.severity != "deny")


def assert_report_shape(report: PolicyReport) -> None:
    assert report.decisions
    for decision in report.decisions:
        assert_decision_shape(decision)
    assert report.denied_count == sum(1 for item in report.decisions if item.severity == "deny")
    assert report.warning_count == sum(1 for item in report.decisions if item.severity == "warn")
    assert report.allowed is (report.denied_count == 0)


@pytest.mark.parametrize(
    ("artifact_type", "rule_id"),
    [
        ("solution", "VIS_DENY_BLIND_SOLUTION"),
        ("answer_key", "VIS_DENY_BLIND_SOLUTION"),
        ("facilitator_guide", "VIS_DENY_BLIND_FACILITATOR"),
        ("review_report", "VIS_DENY_BLIND_REVIEW_PRIVATE"),
    ],
)
def test_blind_solver_denies_forbidden_artifact_types(artifact_type: str, rule_id: str):
    report = evaluate_artifact_visibility(artifact_input(artifact_type=artifact_type))
    assert_report_shape(report)
    assert not report.allowed
    assert report.decisions[0].severity == "deny"
    assert report.decisions[0].rule_id == rule_id


def test_blind_solver_allows_safe_public_player_document():
    report = evaluate_artifact_visibility(artifact_input())
    assert_report_shape(report)
    assert report.allowed
    assert report.warning_count == 0
    assert report.decisions[0].rule_id == "VIS_ALLOW_PUBLIC_PLAYER"


@pytest.mark.parametrize(
    ("overrides", "rule_id"),
    [
        ({"envelope_scope": "future_envelopes"}, "VIS_DENY_BLIND_FUTURE_ENVELOPE"),
        ({"visibility": "private_author"}, "VIS_DENY_BLIND_PRIVATE_AUTHOR"),
        ({"visibility": "facilitator"}, "VIS_DENY_BLIND_FACILITATOR"),
        ({"visibility": "review_private"}, "VIS_DENY_BLIND_REVIEW_PRIVATE"),
        ({"contains_solution": True}, "VIS_DENY_BLIND_SENSITIVE_FLAG"),
        ({"contains_future_envelopes": True}, "VIS_DENY_BLIND_SENSITIVE_FLAG"),
        ({"contains_private_author_notes": True}, "VIS_DENY_BLIND_SENSITIVE_FLAG"),
        ({"contains_other_agents_outputs": True}, "VIS_DENY_BLIND_SENSITIVE_FLAG"),
    ],
)
def test_blind_solver_denies_sensitive_visibility_scope_and_flags(overrides: dict[str, Any], rule_id: str):
    report = evaluate_artifact_visibility(artifact_input(**overrides))
    assert_report_shape(report)
    assert not report.allowed
    assert any(decision.rule_id == rule_id for decision in report.decisions)


def test_blind_solver_allows_sanitized_manifest_only_when_public_or_derived():
    public_report = evaluate_artifact_visibility(artifact_input(artifact_type="manifest", visibility="public_player", envelope_scope="none"))
    assert public_report.allowed
    derived_report = evaluate_artifact_visibility(artifact_input(artifact_type="manifest", visibility="derived_report", envelope_scope="none"))
    assert derived_report.allowed
    private_report = evaluate_artifact_visibility(artifact_input(artifact_type="manifest", visibility="technical_metadata", envelope_scope="none"))
    assert not private_report.allowed


def test_narrative_reviewer_allows_private_author_in_narrative_review():
    report = evaluate_artifact_visibility(
        artifact_input(role="narrative_reviewer", stage="narrative_review", visibility="private_author")
    )
    assert_report_shape(report)
    assert report.allowed
    assert report.decisions[0].severity == "allow"


def test_narrative_reviewer_warns_for_solution():
    report = evaluate_artifact_visibility(
        artifact_input(role="narrative_reviewer", stage="narrative_review", artifact_type="solution", visibility="review_private")
    )
    assert_report_shape(report)
    assert report.allowed
    assert report.warning_count == 1
    assert report.decisions[0].rule_id == "VIS_WARN_REVIEWER_SOLUTION"


@pytest.mark.parametrize("artifact_type", ["render_output", "template"])
def test_visual_reviewer_allows_render_outputs_and_templates(artifact_type: str):
    report = evaluate_artifact_visibility(
        artifact_input(role="visual_reviewer", stage="visual_review", artifact_type=artifact_type, visibility="technical_metadata")
    )
    assert_report_shape(report)
    assert report.allowed


def test_visual_reviewer_denies_solution():
    report = evaluate_artifact_visibility(
        artifact_input(role="visual_reviewer", stage="visual_review", artifact_type="solution", visibility="review_private")
    )
    assert_report_shape(report)
    assert not report.allowed
    assert report.decisions[0].rule_id == "VIS_DENY_REVIEWER_SOLUTION"


@pytest.mark.parametrize("artifact_type", ["solution", "answer_key", "learning_record"])
def test_gate_evaluator_allows_private_resolution_artifacts(artifact_type: str):
    report = evaluate_artifact_visibility(
        artifact_input(role="gate_evaluator", stage="gate_evaluation", artifact_type=artifact_type, visibility="private_author")
    )
    assert_report_shape(report)
    assert report.allowed
    assert report.decisions[0].severity == "allow"


def test_playtest_anonymized_outside_analysis_or_learning_is_denied():
    report = evaluate_artifact_visibility(
        artifact_input(role="narrative_reviewer", stage="narrative_review", visibility="playtest_anonymized", artifact_type="playtest_report")
    )
    assert_report_shape(report)
    assert not report.allowed
    assert report.decisions[0].rule_id == "VIS_DENY_PLAYTEST_DATA_OUTSIDE_ANALYSIS"


def test_playtest_anonymized_in_playtest_analysis_is_allowed_for_reviewer():
    report = evaluate_artifact_visibility(
        artifact_input(role="narrative_reviewer", stage="playtest_analysis", visibility="playtest_anonymized", artifact_type="playtest_report")
    )
    assert_report_shape(report)
    assert report.allowed


@pytest.mark.parametrize("artifact_type", ["schema", "template", "render_output"])
def test_technical_reviewer_allows_technical_artifacts(artifact_type: str):
    report = evaluate_artifact_visibility(
        artifact_input(role="technical_reviewer", stage="technical_validation", artifact_type=artifact_type, visibility="technical_metadata")
    )
    assert_report_shape(report)
    assert report.allowed
    assert report.decisions[0].rule_id == "VIS_ALLOW_TECHNICAL_METADATA"


def test_human_operator_warns_for_private_author():
    report = evaluate_artifact_visibility(
        artifact_input(role="human_operator", stage="preflight_review", visibility="private_author")
    )
    assert_report_shape(report)
    assert report.allowed
    assert report.warning_count == 1
    assert report.decisions[0].rule_id == "VIS_WARN_HUMAN_OPERATOR_PRIVATE"


@pytest.mark.parametrize(
    ("field", "value", "rule_id"),
    [
        ("role", "unknown_role", "VIS_DENY_UNKNOWN_ROLE"),
        ("visibility", "unknown_visibility", "VIS_DENY_UNKNOWN_VISIBILITY"),
        ("stage", "unknown_stage", "VIS_DENY_UNKNOWN_STAGE"),
        ("artifact_type", "unknown_type", "VIS_DENY_UNKNOWN_ARTIFACT_TYPE"),
        ("envelope_scope", "unknown_scope", "VIS_DENY_UNKNOWN_ENVELOPE_SCOPE"),
    ],
)
def test_unknown_values_are_denied(field: str, value: str, rule_id: str):
    report = evaluate_artifact_visibility(artifact_input(**{field: value}))
    assert_report_shape(report)
    assert not report.allowed
    assert report.decisions[0].rule_id == rule_id


def test_report_allowed_false_when_any_decision_denies():
    report = PolicyReport(
        decisions=(
            PolicyDecision(True, "allow", "ALLOW", "allowed", "continue", []),
            PolicyDecision(False, "deny", "DENY", "denied", "remove", []),
        )
    )
    assert not report.allowed
    assert report.denied_count == 1
    assert report.warning_count == 0


def test_report_allowed_true_with_warnings_only():
    report = PolicyReport(
        decisions=(PolicyDecision(True, "warn", "WARN", "warning", "review", []),)
    )
    assert report.allowed
    assert report.denied_count == 0
    assert report.warning_count == 1


def test_evaluate_manifest_visibility_returns_one_decision_per_artifact_for_clean_manifest():
    manifest = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    report = evaluate_manifest_visibility(manifest)
    assert_report_shape(report)
    assert len(report.decisions) == len(manifest["included_artifacts"])


def test_evaluate_manifest_visibility_considers_global_flags():
    manifest = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    manifest["visibility_policy"]["contains_solution"] = True
    report = evaluate_manifest_visibility(manifest)
    assert_report_shape(report)
    assert not report.allowed
    assert report.decisions[0].rule_id == "VIS_DENY_BLIND_SENSITIVE_FLAG"


def test_evaluate_manifest_visibility_valid_minimal_blind_solver_is_allowed():
    manifest = load_yaml(FIXTURES_DIR / "valid" / "valid_minimal_blind_solver.yaml")
    report = evaluate_manifest_visibility(manifest)
    assert_report_shape(report)
    assert report.allowed


def test_evaluate_manifest_visibility_blind_solver_includes_solution_is_denied():
    manifest = load_yaml(FIXTURES_DIR / "invalid" / "blind_solver_includes_solution.yaml")
    report = evaluate_manifest_visibility(manifest)
    assert_report_shape(report)
    assert not report.allowed
    assert any(decision.rule_id == "VIS_DENY_BLIND_SOLUTION" for decision in report.decisions)


def test_evaluate_artifact_visibility_is_deterministic():
    input_data = artifact_input(role="human_operator", visibility="private_author", artifact_type="solution")
    first = evaluate_artifact_visibility(input_data)
    second = evaluate_artifact_visibility(input_data)
    assert first == second


def test_policy_does_not_open_files(monkeypatch: pytest.MonkeyPatch):
    def fail_open(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("policy must not read files")

    monkeypatch.setattr("builtins.open", fail_open)
    report = evaluate_artifact_visibility(artifact_input())
    assert report.allowed

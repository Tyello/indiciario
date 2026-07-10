"""Tests for generator.pipeline_runner (ISSUE-28, ISSUE-33.3)."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.blind_solver_harness import validate_blind_solver_report
from generator.conclusion_judge import ExpectedConclusionInput, judge_conclusions
from generator.fake_provider import FakeProvider, ScriptedResponse
from generator.gate_evaluator import validate_gate_evaluation
from generator.llm_provider import ProviderResponseError
from generator.narrative_reviewer import validate_review_report
from generator.pipeline_runner import (
    DefectMatch,
    PipelineRunResult,
    PlaytestDefect,
    compare_to_playtest,
    run_pipeline,
)
from generator.run_manifest import (
    validate_run_manifest,
    validate_run_manifest_semantics,
)
from generator.workspace import VALID_STAGES, validate_workspace_run
from tests.test_narrative_reviewer import _blueprint as minimal_blueprint

_JUDGE_VERDICT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "judge_verdict.schema.yaml"
)
_PIPELINE_RUNNER_SOURCE = (
    Path(__file__).resolve().parents[1] / "generator" / "pipeline_runner.py"
)


def _validate_judge_verdict_schema(verdict: dict[str, Any]) -> list[str]:
    schema = yaml.safe_load(_JUDGE_VERDICT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(verdict))


def _judge_response_text(
    conclusions: list[dict[str, Any]],
    *,
    alternative_solution_detected: bool = False,
    alternative_solution_summary: str | None = None,
) -> str:
    return json.dumps(
        {
            "verdict_id": "VERDICT-001",
            "report_run_id": RUN_ID,
            "prompt_hash": "abcdef0123",
            "conclusions": conclusions,
            "alternative_solution_detected": alternative_solution_detected,
            "alternative_solution_summary": alternative_solution_summary,
        }
    )


FIXED_CREATED_AT = "2026-06-22T12:00:00Z"
RUN_ID = "RUN-PIPELINE-TEST-001"


def _finding(code: str) -> dict[str, Any]:
    return {
        "id": f"F-{code}",
        "code": code,
        "severity": "major",
        "field": "documentos",
        "message": f"finding {code}",
        "recommendation": "ajustar",
    }


def _defect(defect_id: str) -> PlaytestDefect:
    return PlaytestDefect(
        defect_id=defect_id,
        description=f"defect {defect_id}",
        category="objetivo_envelope",
    )


def _write_minimal_blueprint(tmp_path: Path) -> Path:
    blueprint = minimal_blueprint()
    path = tmp_path / "minimal_blueprint.json"
    path.write_text(
        json.dumps(blueprint.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def minimal_blueprint_path(tmp_path: Path) -> Path:
    return _write_minimal_blueprint(tmp_path)


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    root = tmp_path / "pipeline-output"
    root.mkdir()
    return root


# === Cases 1-8: compare_to_playtest ========================================


def test_compare_defect_with_matching_finding_enters_matches() -> None:
    findings = (_finding("NR_001"),)
    defects = (_defect("PD_01"),)
    mapping = {"PD_01": ("NR_001",)}
    result = compare_to_playtest(findings, defects, mapping)
    assert result.matches == (DefectMatch("PD_01", "NR_001"),)


def test_compare_defect_without_finding_enters_unmatched_playtest() -> None:
    result = compare_to_playtest((), (_defect("PD_01"),), {"PD_01": ("NR_001",)})
    assert result.unmatched_playtest == ("PD_01",)
    assert result.matches == ()


def test_compare_finding_without_defect_enters_unmatched_pipeline() -> None:
    result = compare_to_playtest((_finding("ER_002"),), (_defect("PD_01"),), {"PD_01": ()})
    assert result.unmatched_pipeline == ("ER_002",)


def test_compare_does_not_mutate_inputs() -> None:
    findings = [_finding("NR_001")]
    defects = [_defect("PD_01")]
    mapping = {"PD_01": ("NR_001",)}
    findings_snapshot = copy.deepcopy(findings)
    defects_snapshot = copy.deepcopy(defects)
    mapping_snapshot = copy.deepcopy(mapping)
    compare_to_playtest(tuple(findings), tuple(defects), mapping)
    assert findings == findings_snapshot
    assert defects == defects_snapshot
    assert mapping == mapping_snapshot


def test_compare_empty_findings_puts_all_defects_in_unmatched_playtest() -> None:
    defects = (_defect("PD_01"), _defect("PD_02"))
    result = compare_to_playtest((), defects, {"PD_01": (), "PD_02": ()})
    assert set(result.unmatched_playtest) == {"PD_01", "PD_02"}


def test_compare_empty_defects_puts_all_findings_in_unmatched_pipeline() -> None:
    result = compare_to_playtest((_finding("NR_001"), _finding("ER_001")), (), {})
    assert set(result.unmatched_pipeline) == {"NR_001", "ER_001"}


def test_compare_multiple_findings_for_same_defect_all_match() -> None:
    findings = (_finding("NR_001"), _finding("NR_003"))
    defects = (_defect("PD_01"),)
    mapping = {"PD_01": ("NR_001", "NR_003")}
    result = compare_to_playtest(findings, defects, mapping)
    assert len(result.matches) == 2
    assert result.unmatched_playtest == ()


def test_compare_is_deterministic() -> None:
    findings = (_finding("NR_001"),)
    defects = (_defect("PD_01"),)
    mapping = {"PD_01": ("NR_001",)}
    first = compare_to_playtest(findings, defects, mapping)
    second = compare_to_playtest(findings, defects, mapping)
    assert first == second


# === Cases 9-22: run_pipeline on minimal synthetic blueprint =================


def test_run_pipeline_returns_populated_result(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert isinstance(result, PipelineRunResult)
    assert result.manifest
    assert result.workspace_run
    assert result.blind_solver_report
    assert result.gate_evaluation
    assert result.narrative_report
    assert result.evidence_report
    assert isinstance(result.findings, tuple)
    assert result.comparison


def test_run_pipeline_blind_solver_report_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_blind_solver_report(result.blind_solver_report) == ()


def test_run_pipeline_gate_evaluation_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_gate_evaluation(result.gate_evaluation) == []


def test_run_pipeline_narrative_report_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_review_report(result.narrative_report) == []


def test_run_pipeline_evidence_report_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_review_report(result.evidence_report) == []


def test_run_pipeline_workspace_run_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_workspace_run(result.workspace_run) == []


def test_run_pipeline_manifest_schema_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_run_manifest(result.manifest) == []


def test_run_pipeline_manifest_semantics_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    semantics = validate_run_manifest_semantics(result.manifest)
    assert semantics.valid is True


def test_run_pipeline_does_not_mutate_blueprint(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    before = copy.deepcopy(json.loads(minimal_blueprint_path.read_text(encoding="utf-8")))
    run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    after = json.loads(minimal_blueprint_path.read_text(encoding="utf-8"))
    assert after == before


def test_run_pipeline_writes_only_under_output_root(
    minimal_blueprint_path: Path, output_root: Path, tmp_path: Path
) -> None:
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    marker = examples_dir / "marker.txt"
    marker.write_text("untouched", encoding="utf-8")
    canonical_output = tmp_path / "output"
    canonical_output.mkdir()
    run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert marker.read_text(encoding="utf-8") == "untouched"
    assert list(canonical_output.iterdir()) == []
    assert output_root.exists()


def test_run_pipeline_manifest_findings_consolidate_reviewers(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    manifest_codes = {finding["code"] for finding in result.manifest["findings"]}
    narrative_codes = {
        finding["code"] for finding in result.narrative_report.get("findings", [])
    }
    evidence_codes = {
        finding["code"] for finding in result.evidence_report.get("findings", [])
    }
    assert manifest_codes == narrative_codes | evidence_codes


def test_run_pipeline_manifest_stages_completed_has_four_stages(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    expected = [
        stage
        for stage in VALID_STAGES
        if stage
        in {"blind_solve", "gate_evaluation", "narrative_review", "evidence_review"}
    ]
    assert result.manifest["stages_completed"] == expected


def test_run_pipeline_manifest_pipeline_status_complete(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert result.manifest["pipeline_status"] == "complete"
    assert result.gate_evaluation["decision"] == "approved"


def test_run_pipeline_is_deterministic_with_same_created_at(
    minimal_blueprint_path: Path, output_root: Path, tmp_path: Path
) -> None:
    out_a = tmp_path / "out-a"
    out_b = tmp_path / "out-b"
    out_a.mkdir()
    out_b.mkdir()
    result_a = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=out_a,
        created_at=FIXED_CREATED_AT,
    )
    result_b = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=out_b,
        created_at=FIXED_CREATED_AT,
    )
    assert result_a.manifest == result_b.manifest
    assert result_a.comparison == result_b.comparison


# === Cases 23-29: ISSUE-33.3 judge-backed gate (PJ_001-PJ_005) =============


def test_run_pipeline_without_judge_provider_preserves_stub_gate(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """PJ_003: judge_provider=None keeps the pre-33.3 fabricated stub gate."""
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    assert result.manifest["gate_mode"] == "stub"
    assert result.gate_evaluation["decision"] == "approved"
    assert result.gate_evaluation["justification"] == (
        "ISSUE-28 plumbing run: run record schema-valid; explicit approved "
        "decision to exercise reviewers and manifest consolidation."
    )
    gate_decision = next(
        decision
        for decision in result.workspace_run["decisions"]
        if decision["stage"] == "gate_evaluation"
    )
    assert gate_decision["outcome"] == "approved"
    assert gate_decision["justification"] == (
        "ISSUE-28 plumbing run: explicit approved gate decision."
    )
    assert all(
        artifact["artifact_type"] != "judge_verdict"
        for artifact in result.workspace_run["artifacts"]
    )


def test_run_pipeline_judged_happy_path_approves_from_verdict(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """PJ_001/PJ_002: judge confirms all required conclusions -> approved."""
    provider = FakeProvider(
        [
            ScriptedResponse(
                text=_judge_response_text(
                    [
                        {
                            "id": "EC-E1",
                            "met": True,
                            "evidence_cited": ["EV-1"],
                            "rationale": "Conclusion supported by evidence.",
                        }
                    ]
                )
            )
        ]
    )
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
        judge_provider=provider,
    )
    assert result.manifest["gate_mode"] == "judged"
    assert result.gate_evaluation["decision"] == "approved"
    assert all(
        conclusion["met"] is True
        for conclusion in result.gate_evaluation["expected_conclusions"]
    )
    assert validate_gate_evaluation(result.gate_evaluation) == []


def test_run_pipeline_judged_rejects_on_unmet_required_conclusion(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """PJ_002: judge denies a required conclusion -> rejected with a gap."""
    provider = FakeProvider(
        [
            ScriptedResponse(
                text=_judge_response_text(
                    [
                        {
                            "id": "EC-E1",
                            "met": False,
                            "evidence_cited": [],
                            "rationale": "Report never addresses this conclusion.",
                        }
                    ]
                )
            )
        ]
    )
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
        judge_provider=provider,
    )
    assert result.gate_evaluation["decision"] == "rejected"
    gap_ids = {gap["id"] for gap in result.gate_evaluation["gaps"]}
    assert "GAP-EC-E1" in gap_ids
    assert validate_gate_evaluation(result.gate_evaluation) == []


def test_run_pipeline_judged_rejects_on_ambiguous_classification(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """PJ_002: verdict classification 'ambiguo' -> rejected with GAP-AMBIGUOUS."""
    provider = FakeProvider(
        [
            ScriptedResponse(
                text=_judge_response_text(
                    [
                        {
                            "id": "EC-E1",
                            "met": True,
                            "evidence_cited": ["EV-1"],
                            "rationale": "Conclusion supported by evidence.",
                        }
                    ],
                    alternative_solution_detected=True,
                    alternative_solution_summary="Plausible alternative culprit found.",
                )
            )
        ]
    )
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
        judge_provider=provider,
    )
    assert result.gate_evaluation["decision"] == "rejected"
    gap_ids = {gap["id"] for gap in result.gate_evaluation["gaps"]}
    assert "GAP-AMBIGUOUS" in gap_ids
    assert validate_gate_evaluation(result.gate_evaluation) == []


def test_run_pipeline_judged_verdict_artifact_present_and_schema_valid(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """PJ_005: judge_verdict is ingested into the run workspace and schema-valid."""
    conclusions = [
        {
            "id": "EC-E1",
            "met": True,
            "evidence_cited": ["EV-1"],
            "rationale": "Conclusion supported by evidence.",
        }
    ]
    provider = FakeProvider([ScriptedResponse(text=_judge_response_text(conclusions))])
    result = run_pipeline(
        minimal_blueprint_path,
        RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
        judge_provider=provider,
    )
    jv_artifacts = [
        artifact
        for artifact in result.workspace_run["artifacts"]
        if artifact["artifact_type"] == "judge_verdict"
    ]
    assert len(jv_artifacts) == 1
    assert jv_artifacts[0]["artifact_id"] == f"JV-{RUN_ID}"
    assert jv_artifacts[0]["stage"] == "gate_evaluation"
    assert validate_workspace_run(result.workspace_run) == []

    verdict = judge_conclusions(
        result.blind_solver_report,
        [ExpectedConclusionInput(id="EC-E1", statement="stmt", required=True)],
        FakeProvider([ScriptedResponse(text=_judge_response_text(conclusions))]),
    )
    assert _validate_judge_verdict_schema(asdict(verdict)) == []


def test_no_legacy_ec_guia_typo_in_pipeline_runner_source() -> None:
    """PJ_004: the EC-GUia- typo was fixed and never reappears."""
    source = _PIPELINE_RUNNER_SOURCE.read_text(encoding="utf-8")
    assert "EC-GUia" not in source
    assert 'f"EC-GUIA-{index}"' in source


def test_run_pipeline_judge_error_never_approves_silently(
    minimal_blueprint_path: Path, output_root: Path
) -> None:
    """Case 7: a judge provider failure must fail loudly, never fabricate approval."""
    provider = FakeProvider([ProviderResponseError("provider unavailable")])
    with pytest.raises(RuntimeError, match="gate judge failed"):
        run_pipeline(
            minimal_blueprint_path,
            RUN_ID,
            output_root=output_root,
            created_at=FIXED_CREATED_AT,
            judge_provider=provider,
        )

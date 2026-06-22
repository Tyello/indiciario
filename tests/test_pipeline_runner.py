"""Tests for generator.pipeline_runner (ISSUE-28)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from generator.blind_solver_harness import validate_blind_solver_report
from generator.gate_evaluator import validate_gate_evaluation
from generator.narrative_reviewer import validate_review_report
from generator.pipeline_runner import (
    AURORA_PLAYTEST_DEFECTS,
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

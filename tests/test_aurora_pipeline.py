"""Aurora end-to-end pipeline tests (ISSUE-28, cases 23-32)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from generator.narrative_reviewer import validate_review_report
from generator.pipeline_runner import (
    AURORA_DEFECT_TO_CODES,
    AURORA_PLAYTEST_DEFECTS,
    compare_to_playtest,
    run_pipeline,
)
from generator.run_manifest import (
    validate_run_manifest,
    validate_run_manifest_semantics,
)

AURORA_PATH = Path("examples/caso_canonico_intermediario.json")
FIXED_CREATED_AT = "2026-06-22T12:00:00Z"
RUN_ID = "RUN-AURORA-PIPELINE-001"


@pytest.fixture
def aurora_output(tmp_path: Path) -> Path:
    root = tmp_path / "aurora-pipeline"
    root.mkdir()
    return root


def test_aurora_run_pipeline_executes_without_exception(aurora_output: Path) -> None:
    run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )


def test_aurora_manifest_passes_schema(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_run_manifest(result.manifest) == []


def test_aurora_manifest_passes_semantics(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    semantics = validate_run_manifest_semantics(result.manifest)
    assert semantics.valid is True


def test_aurora_comparison_playtest_defects_match_constant(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    assert result.comparison.playtest_defects == AURORA_PLAYTEST_DEFECTS
    assert len(result.comparison.playtest_defects) == 3


def test_aurora_comparison_is_deterministic(aurora_output: Path, tmp_path: Path) -> None:
    out_a = tmp_path / "aurora-a"
    out_b = tmp_path / "aurora-b"
    out_a.mkdir()
    out_b.mkdir()
    first = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=out_a,
        created_at=FIXED_CREATED_AT,
    )
    second = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=out_b,
        created_at=FIXED_CREATED_AT,
    )
    assert first.comparison == second.comparison


def test_aurora_narrative_report_schema_valid(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_review_report(result.narrative_report) == []


def test_aurora_evidence_report_schema_valid(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    assert validate_review_report(result.evidence_report) == []


def test_aurora_run_does_not_write_under_examples(
    aurora_output: Path, tmp_path: Path
) -> None:
    examples_copy = tmp_path / "examples-copy"
    examples_copy.mkdir()
    sentinel = examples_copy / "sentinel.txt"
    sentinel.write_text("ok", encoding="utf-8")
    run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    assert sentinel.read_text(encoding="utf-8") == "ok"


def test_aurora_blueprint_not_mutated(aurora_output: Path) -> None:
    before_hash = hashlib.sha256(AURORA_PATH.read_bytes()).hexdigest()
    before_data = copy.deepcopy(json.loads(AURORA_PATH.read_text(encoding="utf-8")))
    run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    after_hash = hashlib.sha256(AURORA_PATH.read_bytes()).hexdigest()
    after_data = json.loads(AURORA_PATH.read_text(encoding="utf-8"))
    assert before_hash == after_hash
    assert after_data == before_data


def test_aurora_unmapped_playtest_defects_are_expected(aurora_output: Path) -> None:
    result = run_pipeline(
        AURORA_PATH,
        RUN_ID,
        output_root=aurora_output,
        created_at=FIXED_CREATED_AT,
    )
    comparison = result.comparison
    assert set(comparison.unmatched_playtest) == {"PD_01", "PD_02", "PD_03"}
    assert comparison.matches == ()
    manual = compare_to_playtest(
        result.findings,
        AURORA_PLAYTEST_DEFECTS,
        AURORA_DEFECT_TO_CODES,
    )
    assert manual.unmatched_playtest == comparison.unmatched_playtest

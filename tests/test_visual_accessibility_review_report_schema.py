"""Schema tests for visual_accessibility_review_report.schema.yaml.

Casos 1-8: fixtures e valores validos (RED ate o schema novo existir).
Casos 9-16: rejeicoes estruturais (adicionados no STEP-04).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from generator.visual_reviewer import validate_visual_accessibility_review_report

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "visual_accessibility_review_report"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _valid_base() -> dict:
    return _load(VALID_DIR / "valid_visual_approved.yaml")


# Casos 1-4: fixtures validas passam


def test_case01_valid_visual_approved_passes():
    report = _load(VALID_DIR / "valid_visual_approved.yaml")
    assert validate_visual_accessibility_review_report(report) == []


def test_case02_valid_visual_needs_revision_passes():
    report = _load(VALID_DIR / "valid_visual_needs_revision.yaml")
    assert validate_visual_accessibility_review_report(report) == []


def test_case03_valid_accessibility_approved_passes():
    report = _load(VALID_DIR / "valid_accessibility_approved.yaml")
    assert validate_visual_accessibility_review_report(report) == []


def test_case04_valid_accessibility_blocked_passes():
    report = _load(VALID_DIR / "valid_accessibility_blocked.yaml")
    assert validate_visual_accessibility_review_report(report) == []


# Casos 5-8: valores pontuais validos


def test_case05_reviewer_type_visual_is_valid():
    report = _valid_base()
    report["reviewer_type"] = "visual"
    assert validate_visual_accessibility_review_report(report) == []


def test_case06_reviewer_type_accessibility_is_valid():
    report = _valid_base()
    report["reviewer_type"] = "accessibility"
    assert validate_visual_accessibility_review_report(report) == []


def test_case07_empty_findings_is_valid():
    report = _valid_base()
    report["findings"] = []
    assert validate_visual_accessibility_review_report(report) == []


def test_case08_empty_notes_is_valid():
    report = _valid_base()
    report["notes"] = ""
    assert validate_visual_accessibility_review_report(report) == []


# Casos 9-16: rejeicoes estruturais


def test_case09_wrong_schema_version_fails():
    report = _valid_base()
    report["schema_version"] = "2.0"
    assert validate_visual_accessibility_review_report(report) != []


def test_case10_reviewer_type_narrative_fails():
    report = _load(INVALID_DIR / "invalid_reviewer_type_narrative.yaml")
    assert validate_visual_accessibility_review_report(report) != []


def test_case11_reviewer_type_evidence_fails():
    report = _valid_base()
    report["reviewer_type"] = "evidence"
    assert validate_visual_accessibility_review_report(report) != []


def test_case12_invalid_status_fails():
    report = _load(INVALID_DIR / "invalid_status.yaml")
    assert validate_visual_accessibility_review_report(report) != []


def test_case13_invalid_severity_fails():
    report = _load(INVALID_DIR / "invalid_severity.yaml")
    assert validate_visual_accessibility_review_report(report) != []


def test_case14_short_summary_fails():
    report = _load(INVALID_DIR / "short_summary.yaml")
    assert validate_visual_accessibility_review_report(report) != []


def test_case15_extra_top_field_fails():
    report = _load(INVALID_DIR / "extra_top_field.yaml")
    assert validate_visual_accessibility_review_report(report) != []


def test_case16_missing_recommendation_fails():
    report = _load(INVALID_DIR / "missing_recommendation.yaml")
    assert validate_visual_accessibility_review_report(report) != []

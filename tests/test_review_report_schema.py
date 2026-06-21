"""RED tests for the review report schema (ISSUE-21+22, STEP-03).

These tests describe cases 1-10 of the ISSUE-21 spec for the review report
contract shared by the Narrative Reviewer and the Evidence Reviewer: the four
valid fixtures pass; ``reviewer_type: "evidence"``, ``overall_confidence: "low"``,
``findings[].severity: "info"``, empty ``recommendation``, empty ``field`` and
empty ``notes`` are all structurally valid.

They are expected to FAIL (RED) until ``generator/narrative_reviewer.py`` provides
``validate_review_report`` (and its backing ``schemas/review_report.schema.yaml``).
The failure must come from the missing module/schema (ImportError /
ModuleNotFoundError / FileNotFoundError), NOT from a syntax error in this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.narrative_reviewer import validate_review_report

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "review_report"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _valid_report(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid review report, mutated by ``overrides``."""

    report = _load_fixture("valid", "valid_narrative_approved.yaml")
    report.update(overrides)
    return report


# --- Case 1: valid narrative approved fixture passes -------------------------


def test_valid_narrative_approved_passes() -> None:
    report = _load_fixture("valid", "valid_narrative_approved.yaml")
    assert report["reviewer_type"] == "narrative"
    assert report["status"] == "approved"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 2: valid narrative needs_revision fixture passes -------------------


def test_valid_narrative_needs_revision_passes() -> None:
    report = _load_fixture("valid", "valid_narrative_needs_revision.yaml")
    assert report["status"] == "needs_revision"
    assert len(report["findings"]) == 2
    errors = validate_review_report(report)
    assert errors == []


# --- Case 3: valid evidence blocked fixture passes ---------------------------


def test_valid_evidence_blocked_passes() -> None:
    report = _load_fixture("valid", "valid_evidence_blocked.yaml")
    assert report["reviewer_type"] == "evidence"
    assert report["status"] == "blocked"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 4: valid no-findings fixture passes --------------------------------


def test_valid_no_findings_passes() -> None:
    report = _load_fixture("valid", "valid_no_findings.yaml")
    assert report["findings"] == []
    assert report["status"] == "approved"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 5: reviewer_type "evidence" is valid -------------------------------


def test_reviewer_type_evidence_is_valid() -> None:
    report = _valid_report()
    report["reviewer_type"] = "evidence"
    assert report["reviewer_type"] == "evidence"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 6: overall_confidence "low" is valid -------------------------------


def test_overall_confidence_low_is_valid() -> None:
    report = _valid_report()
    report["overall_confidence"] = "low"
    assert report["overall_confidence"] == "low"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 7: finding with severity "info" is valid ---------------------------


def test_finding_severity_info_is_valid() -> None:
    report = _valid_report()
    report["findings"] = [
        {
            "id": "NR-001",
            "code": "NR_002",
            "severity": "info",
            "field": "documentos[0].tipo",
            "message": "Tipo de documento poderia ser mais imersivo.",
            "recommendation": "Considerar renomear o tipo.",
        }
    ]
    assert report["findings"][0]["severity"] == "info"
    errors = validate_review_report(report)
    assert errors == []


# --- Case 8: finding recommendation empty is valid ---------------------------


def test_finding_empty_recommendation_is_valid() -> None:
    report = _valid_report()
    report["findings"] = [
        {
            "id": "NR-001",
            "code": "NR_005",
            "severity": "minor",
            "field": "tom",
            "message": "Divergencia leve de tom.",
            "recommendation": "",
        }
    ]
    assert report["findings"][0]["recommendation"] == ""
    errors = validate_review_report(report)
    assert errors == []


# --- Case 9: finding field empty is valid ------------------------------------


def test_finding_empty_field_is_valid() -> None:
    report = _valid_report()
    report["findings"] = [
        {
            "id": "NR-001",
            "code": "NR_005",
            "severity": "minor",
            "field": "",
            "message": "Observacao geral sem campo especifico.",
            "recommendation": "Revisar.",
        }
    ]
    assert report["findings"][0]["field"] == ""
    errors = validate_review_report(report)
    assert errors == []


# --- Case 10: empty notes is valid -------------------------------------------


def test_empty_notes_is_valid() -> None:
    report = _valid_report()
    report["notes"] = ""
    assert report["notes"] == ""
    errors = validate_review_report(report)
    assert errors == []


# --- Case 11: schema_version "2.0" fails -------------------------------------


def test_schema_version_2_0_fails() -> None:
    report = _valid_report()
    report["schema_version"] = "2.0"
    assert report["schema_version"] == "2.0"
    errors = validate_review_report(report)
    assert errors != []


# --- Case 12: reviewer_type "visual" fails -----------------------------------


def test_reviewer_type_visual_fails() -> None:
    report = _load_fixture("invalid", "invalid_reviewer_type.yaml")
    assert report["reviewer_type"] == "visual"
    errors = validate_review_report(report)
    assert errors != []


# --- Case 13: status "pending" fails -----------------------------------------


def test_status_pending_fails() -> None:
    report = _load_fixture("invalid", "invalid_status.yaml")
    assert report["status"] == "pending"
    errors = validate_review_report(report)
    assert errors != []


# --- Case 14: missing report_id fails ----------------------------------------


def test_missing_report_id_fails() -> None:
    report = _load_fixture("invalid", "missing_report_id.yaml")
    assert "report_id" not in report
    errors = validate_review_report(report)
    assert errors != []


# --- Case 15: missing summary fails ------------------------------------------


def test_missing_summary_fails() -> None:
    report = _load_fixture("invalid", "missing_summary.yaml")
    assert "summary" not in report
    errors = validate_review_report(report)
    assert errors != []


# --- Case 16: overall_confidence "very_high" fails ---------------------------


def test_overall_confidence_very_high_fails() -> None:
    report = _valid_report()
    report["overall_confidence"] = "very_high"
    assert report["overall_confidence"] == "very_high"
    errors = validate_review_report(report)
    assert errors != []


# --- Case 17: findings[].severity "warning" fails ----------------------------


def test_finding_severity_warning_fails() -> None:
    report = _load_fixture("invalid", "invalid_severity.yaml")
    assert report["findings"][0]["severity"] == "warning"
    errors = validate_review_report(report)
    assert errors != []


# --- Case 18: findings[].code missing fails ----------------------------------


def test_finding_missing_code_fails() -> None:
    report = _valid_report()
    report["status"] = "needs_revision"
    report["findings"] = [
        {
            "id": "NR-001",
            "severity": "minor",
            "field": "tom",
            "message": "Finding sem code.",
            "recommendation": "Revisar.",
        }
    ]
    assert "code" not in report["findings"][0]
    errors = validate_review_report(report)
    assert errors != []


# --- Case 19: extra top-level field fails (additionalProperties false) -------


def test_extra_top_field_fails() -> None:
    report = _load_fixture("invalid", "extra_top_field.yaml")
    assert "campo_extra_nao_permitido" in report
    errors = validate_review_report(report)
    assert errors != []


# --- Case 20: findings[].id missing fails ------------------------------------


def test_finding_missing_id_fails() -> None:
    report = _valid_report()
    report["status"] = "needs_revision"
    report["findings"] = [
        {
            "code": "NR_005",
            "severity": "minor",
            "field": "tom",
            "message": "Finding sem id.",
            "recommendation": "Revisar.",
        }
    ]
    assert "id" not in report["findings"][0]
    errors = validate_review_report(report)
    assert errors != []


# --- guard: fixtures load and helper does not mutate the source --------------


def test_valid_report_helper_does_not_mutate_fixture() -> None:
    pristine = _load_fixture("valid", "valid_narrative_approved.yaml")
    snapshot = copy.deepcopy(pristine)
    _valid_report(status="needs_revision")
    fresh = _load_fixture("valid", "valid_narrative_approved.yaml")
    assert fresh == snapshot

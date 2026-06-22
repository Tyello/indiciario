"""RED tests for the run manifest schema (ISSUE-27, STEP-03).

These tests describe cases 1-10 of the ISSUE-27 spec for the run manifest
contract: the four valid fixtures pass, and selected structural variations
(``pipeline_status: rolled_back``, ``findings[].severity: "info"``, empty
``findings[].field``, ``gate_outcome: null``, empty ``next_steps`` and empty
``notes``) are all structurally valid.

They are expected to FAIL (RED) until ``generator/run_manifest.py`` provides
``validate_run_manifest`` (and its backing
``schemas/run_manifest.schema.yaml``). The failure must come from the missing
module/schema, NOT from a syntax error in this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.run_manifest import validate_run_manifest

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "run_manifest"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _valid_manifest(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid manifest, mutated by ``overrides``."""

    manifest = _load_fixture("valid", "valid_complete.yaml")
    manifest.update(overrides)
    return manifest


# --- Case 1: valid_complete fixture passes -----------------------------------


def test_valid_complete_passes() -> None:
    manifest = _load_fixture("valid", "valid_complete.yaml")
    assert manifest["pipeline_status"] == "complete"
    assert len(manifest["stages_completed"]) == 4
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 2: valid_incomplete fixture passes ---------------------------------


def test_valid_incomplete_passes() -> None:
    manifest = _load_fixture("valid", "valid_incomplete.yaml")
    assert manifest["pipeline_status"] == "incomplete"
    assert manifest["stages_completed"] == ["blind_solve"]
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 3: valid_blocked fixture passes ------------------------------------


def test_valid_blocked_passes() -> None:
    manifest = _load_fixture("valid", "valid_blocked.yaml")
    assert manifest["pipeline_status"] == "blocked"
    assert manifest["gate_outcome"]["outcome"] == "rejected"
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 4: valid_no_findings fixture passes --------------------------------


def test_valid_no_findings_passes() -> None:
    manifest = _load_fixture("valid", "valid_no_findings.yaml")
    assert manifest["findings"] == []
    assert manifest["gate_outcome"] is None
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 5: pipeline_status "rolled_back" is valid --------------------------


def test_pipeline_status_rolled_back_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["pipeline_status"] = "rolled_back"
    assert manifest["pipeline_status"] == "rolled_back"
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 6: findings[].severity "info" is valid -----------------------------


def test_finding_severity_info_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["findings"][0]["severity"] = "info"
    assert manifest["findings"][0]["severity"] == "info"
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 7: findings[].field "" is valid (field may be empty) ---------------


def test_finding_empty_field_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["findings"][0]["field"] = ""
    assert manifest["findings"][0]["field"] == ""
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 8: gate_outcome null is valid --------------------------------------


def test_gate_outcome_null_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["gate_outcome"] = None
    assert manifest["gate_outcome"] is None
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 9: next_steps [] is valid ------------------------------------------


def test_empty_next_steps_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["next_steps"] = []
    assert manifest["next_steps"] == []
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 10: empty notes is valid -------------------------------------------


def test_empty_notes_is_valid() -> None:
    manifest = _valid_manifest()
    manifest["notes"] = ""
    assert manifest["notes"] == ""
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- guard: fixtures load and helper does not mutate the source --------------


def test_valid_manifest_helper_does_not_mutate_fixture() -> None:
    pristine = _load_fixture("valid", "valid_complete.yaml")
    snapshot = copy.deepcopy(pristine)
    _valid_manifest(pipeline_status="incomplete")
    fresh = _load_fixture("valid", "valid_complete.yaml")
    assert fresh == snapshot


# --- Cases 11-20: structural rejections --------------------------------------
#
# Each invalid fixture (or override) must produce at least one structural error
# from ``validate_run_manifest``. These remain RED until
# ``generator/run_manifest.py`` and ``schemas/run_manifest.schema.yaml`` exist.


# --- Case 11: schema_version "2.0" fails -------------------------------------


def test_schema_version_mismatch_fails() -> None:
    manifest = _valid_manifest()
    manifest["schema_version"] = "2.0"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 12: pipeline_status "running" fails (invalid enum) ------------------


def test_invalid_pipeline_status_fails() -> None:
    manifest = _load_fixture("invalid", "invalid_pipeline_status.yaml")
    assert manifest["pipeline_status"] == "running"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 13: missing manifest_id fails --------------------------------------


def test_missing_manifest_id_fails() -> None:
    manifest = _load_fixture("invalid", "missing_manifest_id.yaml")
    assert "manifest_id" not in manifest
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 14: missing run_id fails -------------------------------------------


def test_missing_run_id_fails() -> None:
    manifest = _load_fixture("invalid", "missing_run_id.yaml")
    assert "run_id" not in manifest
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 15: findings[].source_type "visual_review" fails -------------------


def test_invalid_finding_source_type_fails() -> None:
    manifest = _load_fixture("invalid", "invalid_source_type.yaml")
    assert manifest["findings"][0]["source_type"] == "visual_review"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 16: findings[].severity "warning" fails ----------------------------


def test_invalid_finding_severity_fails() -> None:
    manifest = _load_fixture("invalid", "invalid_severity.yaml")
    assert manifest["findings"][0]["severity"] == "warning"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 17: artifacts_summary[].artifact_type "visual_review" fails ---------


def test_invalid_artifact_type_fails() -> None:
    manifest = _valid_manifest()
    manifest["artifacts_summary"][0]["artifact_type"] = "visual_review"
    assert manifest["artifacts_summary"][0]["artifact_type"] == "visual_review"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 18: decisions_summary[].outcome "pending" fails --------------------


def test_invalid_decision_outcome_fails() -> None:
    manifest = _load_fixture("invalid", "invalid_outcome.yaml")
    assert manifest["decisions_summary"][0]["outcome"] == "pending"
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 19: extra top-level field fails (additionalProperties: false) -------


def test_extra_top_field_fails() -> None:
    manifest = _load_fixture("invalid", "extra_top_field.yaml")
    assert "unexpected_field" in manifest
    errors = validate_run_manifest(manifest)
    assert errors != []


# --- Case 20: gate_outcome missing decision_id fails -------------------------


def test_gate_outcome_missing_decision_id_fails() -> None:
    manifest = _load_fixture("invalid", "gate_outcome_missing_decision_id.yaml")
    assert "decision_id" not in manifest["gate_outcome"]
    errors = validate_run_manifest(manifest)
    assert errors != []

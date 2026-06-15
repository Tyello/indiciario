"""RED tests for the blind solve run record schema (ISSUE-18, STEP-03).

These tests describe cases 1-8 of the ISSUE-18 spec for the run record contract:
valid complete/no-conclusion/failed runs pass; wrong ``schema_version``, missing
``run_id``/``bundle_id`` and an invalid ``execution.status`` fail.

They are expected to FAIL (RED) until ``generator/blind_solve_run_record.py``
provides ``validate_run_record`` (and its backing
``schemas/blind_solve_run_record.schema.yaml``). The failure must come from the
missing module/schema, NOT from a syntax error in this file.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from generator.blind_solve_run_record import validate_run_record

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "blind_solve_run_record"


def _load_fixture(*parts: str) -> dict[str, Any]:
    with (_FIXTURE_ROOT.joinpath(*parts)).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _valid_record(**overrides: Any) -> dict[str, Any]:
    """Return a structurally valid run record, mutated by ``overrides``."""

    record = _load_fixture("valid", "valid_complete.yaml")
    record.update(overrides)
    return record


# --- Case 1: valid complete fixture passes ----------------------------------


def test_valid_complete_record_passes() -> None:
    record = _load_fixture("valid", "valid_complete.yaml")
    errors = validate_run_record(record)
    assert errors == []


# --- Case 2: valid record with empty denied_access_attempts passes ----------


def test_valid_record_with_empty_denied_access_passes() -> None:
    record = _load_fixture("valid", "valid_no_conclusion.yaml")
    assert record["denied_access_attempts"] == []
    errors = validate_run_record(record)
    assert errors == []


# --- Case 3: status failed with failure_reason filled passes ----------------


def test_failed_status_with_failure_reason_passes() -> None:
    record = _load_fixture("valid", "valid_failed_run.yaml")
    assert record["execution"]["status"] == "failed"
    assert record["execution"]["failure_reason"]
    errors = validate_run_record(record)
    assert errors == []


# --- Case 4: status completed with failure_reason null passes ---------------


def test_completed_status_with_null_failure_reason_passes() -> None:
    record = _load_fixture("valid", "valid_complete.yaml")
    assert record["execution"]["status"] == "completed"
    assert record["execution"]["failure_reason"] is None
    errors = validate_run_record(record)
    assert errors == []


# --- Case 5: wrong schema_version fails --------------------------------------


def test_wrong_schema_version_fails() -> None:
    record = _valid_record(schema_version="2.0")
    errors = validate_run_record(record)
    assert errors != []


# --- Case 6: missing run_id fails -------------------------------------------


def test_missing_run_id_fails() -> None:
    record = _load_fixture("invalid", "missing_run_id.yaml")
    assert "run_id" not in record
    errors = validate_run_record(record)
    assert errors != []


# --- Case 7: missing bundle_id fails ----------------------------------------


def test_missing_bundle_id_fails() -> None:
    record = _valid_record()
    del record["bundle_id"]
    errors = validate_run_record(record)
    assert errors != []


# --- Case 8: invalid execution.status fails ---------------------------------


def test_invalid_execution_status_fails() -> None:
    record = _load_fixture("invalid", "invalid_status.yaml")
    assert record["execution"]["status"] == "aborted_unexpectedly"
    errors = validate_run_record(record)
    assert errors != []


# --- Case 9: execution.status failed without failure_reason fails ------------


def test_failed_execution_status_without_reason_fails() -> None:
    record = _load_fixture("invalid", "failed_without_reason.yaml")
    assert record["execution"]["status"] == "failed"
    assert record["execution"]["failure_reason"] is None
    errors = validate_run_record(record)
    assert errors != []


# --- Case 10: environment.llm_used true is valid -----------------------------


def test_environment_llm_used_true_is_valid() -> None:
    record = _valid_record()
    record["environment"]["llm_used"] = True
    assert record["environment"]["llm_used"] is True
    errors = validate_run_record(record)
    assert errors == []


# --- Case 11: gate_decision null is valid ------------------------------------


def test_gate_decision_null_is_valid() -> None:
    record = _valid_record()
    record["gate_decision"] = None
    assert record["gate_decision"] is None
    errors = validate_run_record(record)
    assert errors == []


# --- Case 12: gate_decision arbitrary object is valid ------------------------


def test_gate_decision_object_is_valid() -> None:
    record = _valid_record()
    record["gate_decision"] = {"decision": "approved", "score": 0.9}
    assert record["gate_decision"]["decision"] == "approved"
    errors = validate_run_record(record)
    assert errors == []


# --- Case 13: extra top-level field fails (additionalProperties: false) -------


def test_extra_top_level_field_fails() -> None:
    record = _load_fixture("invalid", "extra_top_field.yaml")
    assert "private_author_notes" in record
    errors = validate_run_record(record)
    assert errors != []


# --- Case 14: accessed_artifacts item without artifact_id fails ---------------


def test_accessed_artifact_without_artifact_id_fails() -> None:
    record = _valid_record()
    record["accessed_artifacts"] = [
        {"path": "player/depoimento.md", "accessed_at": "2026-06-14T00:00:01Z"},
    ]
    assert "artifact_id" not in record["accessed_artifacts"][0]
    errors = validate_run_record(record)
    assert errors != []


# --- Case 15: denied_access_attempts item without requested_path fails --------


def test_denied_access_attempt_without_requested_path_fails() -> None:
    record = _valid_record()
    record["denied_access_attempts"] = [
        {"reason": "artifact not in bundle", "attempted_at": "2026-06-14T00:00:02Z"},
    ]
    assert "requested_path" not in record["denied_access_attempts"][0]
    errors = validate_run_record(record)
    assert errors != []


# --- guard: fixtures load and helper does not mutate the source --------------


def test_valid_record_helper_does_not_mutate_fixture() -> None:
    pristine = _load_fixture("valid", "valid_complete.yaml")
    snapshot = copy.deepcopy(pristine)
    _valid_record(schema_version="2.0")
    fresh = _load_fixture("valid", "valid_complete.yaml")
    assert fresh == snapshot

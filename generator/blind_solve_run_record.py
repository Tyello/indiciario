"""Schema validator and builder for the blind solve run record (ISSUE-18).

This module backs the traceable run record contract defined in
``schemas/blind_solve_run_record.schema.yaml``. It exposes two public helpers:

- :func:`validate_run_record` — validate a run record mapping against the schema
  and return a list of error messages (empty == valid);
- :func:`build_run_record` — assemble a traceable run record from the offline
  harness result, the harness request and the standalone semantic validator
  result, linking the bundle, manifest and solver to the frozen report.

It never calls an LLM, never accesses the network, never judges whether the
conclusion is correct (that is the Gate Evaluator, ISSUE-19) and never mutates
the inputs it receives.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.blind_solver_harness import (
    BlindSolverHarnessRequest,
    BlindSolverHarnessResult,
)
from generator.blind_solver_report_validator import ReportValidationResult

SCHEMA_VERSION = "1.0"

_RUN_RECORD_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "blind_solve_run_record.schema.yaml"
)


def validate_run_record(record: Mapping[str, Any]) -> list[str]:
    """Return schema error messages for a run record (empty list == valid)."""

    schema = yaml.safe_load(_RUN_RECORD_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(record)))


def build_run_record(
    harness_result: BlindSolverHarnessResult,
    request: BlindSolverHarnessRequest,
    validator_result: ReportValidationResult,
    created_by: str = "orchestrator",
    notes: str = "",
) -> dict:
    """Build a traceable run record from the harness and validator outputs.

    The record links ``bundle_id``/``manifest_id``/``solver_id``/``run_id`` and
    embeds the frozen report. ``accessed_artifacts``, ``denied_access_attempts``
    and ``harness_warnings`` mirror the harness result; ``validation`` mirrors the
    semantic validator result plus the report schema validity. Inputs are never
    mutated (defensive copies are taken throughout).
    """

    # Defensive copy of the report: it is embedded frozen in the record and must
    # not share mutable structure with the harness result.
    report = _deep_copy(harness_result.report)

    # The harness exposes no execution timestamps; derive them honestly from the
    # report's own ``created_at`` and use a zero duration. The harness does not
    # measure wall-clock time, so inventing a non-zero duration would be
    # misleading (see STEP-09 execution report).
    created_at = _report_str(report, "created_at")

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": _report_str(report, "solver_run_id"),
        "bundle_id": _report_str(report, "bundle_id"),
        "manifest_id": _report_str(report, "manifest_id"),
        "solver_id": _report_str(report, "solver_id"),
        "created_at": created_at,
        "created_by": str(created_by),
        "environment": {
            "offline": True,
            "llm_used": False,
            "internet_used": False,
        },
        "execution": {
            "started_at": created_at,
            "finished_at": created_at,
            "duration_seconds": 0,
            "status": "completed",
            "failure_reason": None,
        },
        "report": report,
        "accessed_artifacts": _accessed_artifacts(harness_result, report, created_at),
        "denied_access_attempts": _denied_access_attempts(harness_result, created_at),
        "harness_warnings": list(harness_result.warnings),
        "validation": _validation(validator_result),
        "gate_decision": None,
        "reviewer_findings": [],
        "notes": str(notes),
    }
    return record


# --------------------------------------------------------------------------- #
# Internal helpers                                                             #
# --------------------------------------------------------------------------- #
def _report_str(report: Mapping[str, Any], key: str) -> str:
    """Return ``report[key]`` coerced to ``str`` (``str(None)`` when missing)."""

    return str(report.get(key))


def _deep_copy(value: Any) -> Any:
    """Return a deep, plain-container copy so the record never shares state."""

    if isinstance(value, Mapping):
        return {key: _deep_copy(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_deep_copy(item) for item in value]
    return value


def _evidence_paths(report: Mapping[str, Any]) -> dict[str, str]:
    """Map artifact_id -> declared path using the report's evidence_used."""

    paths: dict[str, str] = {}
    for item in report.get("evidence_used") or []:
        if not isinstance(item, Mapping):
            continue
        artifact_id = item.get("artifact_id")
        path = item.get("path")
        if isinstance(artifact_id, str) and isinstance(path, str) and path:
            paths.setdefault(artifact_id, path)
    return paths


def _accessed_artifacts(
    harness_result: BlindSolverHarnessResult,
    report: Mapping[str, Any],
    accessed_at: str,
) -> list[dict[str, Any]]:
    """Convert the harness' artifact_id tuple into schema-shaped objects.

    The harness only records artifact ids; the declared path is recovered from
    the report's ``evidence_used``. When an accessed artifact is not referenced
    as evidence (so no path is available), the artifact id is used as the path
    so the record stays valid without inventing a fictional file path.
    """

    paths = _evidence_paths(report)
    items: list[dict[str, Any]] = []
    for artifact_id in harness_result.accessed_artifacts:
        items.append(
            {
                "artifact_id": artifact_id,
                "path": paths.get(artifact_id, artifact_id),
                "accessed_at": accessed_at,
            }
        )
    return items


def _denied_access_attempts(
    harness_result: BlindSolverHarnessResult,
    attempted_at: str,
) -> list[dict[str, Any]]:
    """Convert the harness' denied-access strings into schema-shaped objects.

    The harness records each denial as ``"path=<...>"`` or
    ``"artifact_id=<...>"``. In a normal (successful) run this is empty, because
    the harness raises on any denied access; the conversion is provided for
    completeness and future non-raising callers.
    """

    items: list[dict[str, Any]] = []
    for entry in harness_result.denied_access_attempts:
        text = str(entry)
        if text.startswith("path="):
            requested_path = text[len("path="):]
            reason = "read denied: requested path is not an included artifact"
        elif text.startswith("artifact_id="):
            requested_path = text[len("artifact_id="):]
            reason = "read denied: requested artifact_id is not declared in the bundle"
        else:
            requested_path = text
            reason = "read denied by the blind solver harness"
        items.append(
            {
                "requested_path": requested_path or text,
                "reason": reason,
                "attempted_at": attempted_at,
            }
        )
    return items


def _validation(validator_result: ReportValidationResult) -> dict[str, Any]:
    """Mirror the semantic validator result into the run record's validation."""

    errors = [_serialize_finding(error) for error in validator_result.errors]
    warnings = [_serialize_finding(warning) for warning in validator_result.warnings]
    report_schema_valid = not any(
        finding["code"] == "RV_001" for finding in errors
    )
    return {
        "report_schema_valid": report_schema_valid,
        "report_semantic_valid": bool(validator_result.valid),
        "semantic_errors": errors,
        "semantic_warnings": warnings,
    }


def _serialize_finding(finding: Any) -> dict[str, str]:
    """Serialize a ReportValidationError into a plain dict."""

    return {
        "kind": str(getattr(finding.kind, "value", finding.kind)),
        "code": str(finding.code),
        "field": str(finding.field),
        "message": str(finding.message),
    }

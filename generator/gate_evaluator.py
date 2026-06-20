"""Gate Evaluator schema validation (ISSUE-19+20, STEP-05).

This module backs the gate evaluation contract defined in
``schemas/gate_evaluation.schema.yaml``. The Gate Evaluator is the single
component authorised to compare a frozen blind solve run record against the
author's private solution and record a formal decision (approved/rejected/
rollback).

STEP-05 provided the structural validation entry point
:func:`validate_gate_evaluation`. STEP-08 adds the public dataclasses and the
semantic rules (GE_001-GE_008) applied by
:func:`validate_gate_evaluation_semantics`. STEP-09 implements the builder
``build_gate_evaluation``, which links the run record to the private context and
serialises the evaluation.

It never calls an LLM, never accesses the network, never judges whether the
conclusion is correct and never mutates the input it receives.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0"

_GATE_EVALUATION_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "gate_evaluation.schema.yaml"
)


# --------------------------------------------------------------------------- #
# Public dataclasses                                                          #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ExpectedConclusion:
    """A single expected conclusion the author wanted the solver to reach."""

    id: str
    description: str
    required: bool
    met: bool
    evidence: str


@dataclass(frozen=True)
class GapItem:
    """A gap between what was expected and what the solver concluded."""

    id: str
    description: str
    required_conclusion_id: str | None
    severity: str  # "critical" | "major" | "minor"
    impact: str


@dataclass(frozen=True)
class ConfidenceAssessment:
    """Mirror of the solver confidence plus the evaluator's agreement."""

    solver_confidence: str  # "low" | "medium" | "high"
    evaluator_agreement: str  # "agree" | "disagree" | "partial"
    notes: str


@dataclass(frozen=True)
class GateEvaluationRequest:
    """Inputs required to build a gate evaluation against a frozen run record."""

    run_record: Mapping[str, Any]
    private_solution_ref: str
    evaluator_id: str
    evaluation_id: str
    created_by: str = "orchestrator"
    created_at: str | None = None


@dataclass(frozen=True)
class GateEvaluationResult:
    """Outcome of applying the semantic rules GE_001-GE_008."""

    evaluation: dict[str, Any]
    semantic_errors: tuple[str, ...]
    semantic_warnings: tuple[str, ...]
    valid: bool


def validate_gate_evaluation(evaluation: Mapping[str, Any]) -> list[str]:
    """Validate a gate evaluation mapping against the schema.

    Returns a sorted list of error messages (empty list == structurally valid).
    The input mapping is never modified.
    """

    schema = yaml.safe_load(
        _GATE_EVALUATION_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(evaluation)))


def _decision_only_errors(evaluation: Mapping[str, Any]) -> list[str]:
    """Errors for rules GE_001-GE_006 (do not depend on the run record)."""

    decision = evaluation.get("decision")
    rollback_target = evaluation.get("rollback_target")
    leak_detected = evaluation.get("leak_detected")
    expected_conclusions = evaluation.get("expected_conclusions") or []
    gaps = evaluation.get("gaps") or []

    errors: list[str] = []

    # GE_001: rollback decision requires a non-null rollback_target.
    if decision == "rollback" and rollback_target is None:
        errors.append(
            "GE_001: decision='rollback' requires a non-null rollback_target"
        )

    # GE_002: non-rollback decision requires a null rollback_target.
    if decision != "rollback" and rollback_target is not None:
        errors.append(
            "GE_002: decision!='rollback' requires rollback_target to be null"
        )

    # GE_003: a detected leak forbids an approved decision.
    if leak_detected is True and decision == "approved":
        errors.append(
            "GE_003: leak_detected=true forbids decision='approved'"
        )

    # GE_004/GE_005: approved decision requires every required conclusion met.
    has_unmet_required = any(
        item.get("required") is True and item.get("met") is False
        for item in expected_conclusions
    )
    if decision == "approved" and has_unmet_required:
        errors.append(
            "GE_004: decision='approved' requires every required=true "
            "conclusion to be met=true"
        )
        errors.append(
            "GE_005: a required=true conclusion with met=false forbids "
            "decision='approved'"
        )

    # GE_006: a critical gap forbids an approved decision.
    has_critical_gap = any(item.get("severity") == "critical" for item in gaps)
    if decision == "approved" and has_critical_gap:
        errors.append(
            "GE_006: a severity='critical' gap forbids decision='approved'"
        )

    return errors


def _run_record_warning(
    evaluation: Mapping[str, Any],
    run_record: Mapping[str, Any],
) -> str | None:
    """GE_007: confidence assessment should mirror report.confidence (warning)."""

    assessment = evaluation.get("confidence_assessment") or {}
    solver_confidence = assessment.get("solver_confidence")
    report = run_record.get("report") or {}
    report_confidence = report.get("confidence")
    if solver_confidence != report_confidence:
        return (
            "GE_007: solver_confidence "
            f"({solver_confidence!r}) diverges from report.confidence "
            f"({report_confidence!r})"
        )
    return None


def _run_record_error(
    evaluation: Mapping[str, Any],
    run_record: Mapping[str, Any],
) -> str | None:
    """GE_008: run_id must match the run record (blocking)."""

    if evaluation.get("run_id") != run_record.get("run_id"):
        return (
            "GE_008: run_id "
            f"({evaluation.get('run_id')!r}) does not match the run "
            f"record run_id ({run_record.get('run_id')!r})"
        )
    return None


def validate_gate_evaluation_semantics(
    evaluation: Mapping[str, Any],
    run_record: Mapping[str, Any] | None = None,
) -> GateEvaluationResult:
    """Apply the semantic rules GE_001-GE_008 to a gate evaluation.

    GE_001-GE_006 and GE_008 are blocking (errors). GE_007 is a non-blocking
    warning. GE_007 and GE_008 are only evaluated when ``run_record`` is
    provided. The input mappings are never modified.
    """

    errors: list[str] = _decision_only_errors(evaluation)
    warnings: list[str] = []

    if run_record is not None:
        warning = _run_record_warning(evaluation, run_record)
        if warning is not None:
            warnings.append(warning)

        error = _run_record_error(evaluation, run_record)
        if error is not None:
            errors.append(error)

    return GateEvaluationResult(
        evaluation=dict(evaluation),
        semantic_errors=tuple(errors),
        semantic_warnings=tuple(warnings),
        valid=not errors,
    )


def build_gate_evaluation(
    request: GateEvaluationRequest,
    expected_conclusions: list[ExpectedConclusion],
    unexpected_valid_hypotheses: list[str],
    gaps: list[GapItem],
    confidence_assessment: ConfidenceAssessment,
    decision: str,
    justification: str,
    leak_detected: bool = False,
    rollback_target: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build a serialised gate evaluation ready for ``validate_gate_evaluation``.

    Links ``evaluation_id``, ``run_id`` and ``bundle_id`` from
    ``request``/``request.run_record`` and serialises the expected conclusions,
    gaps and confidence assessment. It does not apply the semantic rules (call
    :func:`validate_gate_evaluation_semantics` afterwards) and never mutates its
    inputs.
    """

    created_at = request.created_at
    if created_at is None:
        created_at = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "evaluation_id": request.evaluation_id,
        "run_id": request.run_record["run_id"],
        "bundle_id": request.run_record["bundle_id"],
        "evaluator_id": request.evaluator_id,
        "created_at": created_at,
        "created_by": request.created_by,
        "private_solution_ref": request.private_solution_ref,
        "decision": decision,
        "justification": justification,
        "expected_conclusions": [
            {
                "id": item.id,
                "description": item.description,
                "required": item.required,
                "met": item.met,
                "evidence": item.evidence,
            }
            for item in expected_conclusions
        ],
        "unexpected_valid_hypotheses": list(unexpected_valid_hypotheses),
        "gaps": [
            {
                "id": item.id,
                "description": item.description,
                "required_conclusion_id": item.required_conclusion_id,
                "severity": item.severity,
                "impact": item.impact,
            }
            for item in gaps
        ],
        "leak_detected": leak_detected,
        "rollback_target": rollback_target,
        "confidence_assessment": {
            "solver_confidence": confidence_assessment.solver_confidence,
            "evaluator_agreement": confidence_assessment.evaluator_agreement,
            "notes": confidence_assessment.notes,
        },
        "notes": notes,
    }

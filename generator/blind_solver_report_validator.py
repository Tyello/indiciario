"""Standalone semantic validator for a blind solver report (ISSUE-17).

This module adds a semantic/quality layer on top of the structural schema
validation already provided by
:func:`generator.blind_solver_harness.validate_blind_solver_report`.

It operates only on the report mapping: it requires no bundle, manifest or
context. Structural problems are reported as ``RV_001`` (delegated to the
schema validator) and short-circuit every semantic/quality check, because the
later checks assume a structurally valid report. Semantic incoherences
(``RV_002``-``RV_005``, ``RV_008``) are blocking; quality smells
(``RV_006``, ``RV_007``) are warnings that never make a report invalid.

It never calls an LLM, never accesses the network, never judges whether the
conclusion is *correct*, and never mutates the report it receives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from generator.blind_solver_harness import validate_blind_solver_report

# Vague placeholders that, on their own, make ``reasoning_summary`` useless.
# Matched case-insensitively as substrings (already lowered for comparison).
_VAGUE_PLACEHOLDERS: tuple[str, ...] = tuple(
    placeholder.casefold()
    for placeholder in (
        "inconclusivo",
        "sem conclusão",
        "não foi possível",
        "insuficiente",
        "n/a",
        "pendente",
        "a definir",
    )
)

# Minimum number of ``high``-confidence evidence items that makes a ``low``
# overall confidence incoherent (RV_008).
_HIGH_EVIDENCE_THRESHOLD = 3

# Catalogue of the validation codes this module can emit, mapping each code to
# the report field it points at and the kind of finding it represents. Kept as
# documentation/reference; the checks below build the same (kind, field) pairs.
#   RV_001  <schema>          structural  delegated to the schema validator
#   RV_002  evidence_used     semantic    conclusion present but no evidence
#   RV_003  confidence        semantic    high confidence but no evidence
#   RV_004  open_questions    semantic    high confidence but open questions
#   RV_005  conclusion        semantic    no conclusion and no open questions
#   RV_006  reasoning_summary quality     reasoning_summary only a placeholder
#   RV_007  conclusion        quality     evidence present but conclusion empty
#   RV_008  confidence        semantic    low confidence but evidence mostly high


class ReportValidationErrorKind(str, Enum):
    """Category of a report validation finding."""

    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    QUALITY = "quality"


@dataclass(frozen=True)
class ReportValidationError:
    """A single validation finding (blocking error or quality warning)."""

    kind: ReportValidationErrorKind
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class ReportValidationResult:
    """Outcome of validating a blind solver report."""

    valid: bool
    errors: tuple[ReportValidationError, ...] = field(default=())
    warnings: tuple[ReportValidationError, ...] = field(default=())


@dataclass(frozen=True)
class _ReportFields:
    """Normalised view of the report fields the semantic checks rely on."""

    conclusion: str
    confidence: str
    reasoning_summary: str
    evidence_used: list[Any]
    open_questions: list[Any]

    @property
    def has_conclusion(self) -> bool:
        return bool(self.conclusion)

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence_used)

    @property
    def has_open_questions(self) -> bool:
        return bool(self.open_questions)

    @property
    def high_evidence_count(self) -> int:
        return sum(
            1
            for item in self.evidence_used
            if isinstance(item, Mapping)
            and str(item.get("confidence") or "") == "high"
        )


def _extract_fields(report: Mapping[str, Any]) -> _ReportFields:
    """Pull and normalise the fields used by the semantic/quality checks."""

    return _ReportFields(
        conclusion=str(report.get("conclusion") or "").strip(),
        confidence=str(report.get("confidence") or ""),
        reasoning_summary=str(report.get("reasoning_summary") or ""),
        evidence_used=list(report.get("evidence_used") or []),
        open_questions=list(report.get("open_questions") or []),
    )


def _semantic(code: str, field_name: str, message: str) -> ReportValidationError:
    """Build a blocking semantic finding (RV_002-RV_005, RV_008)."""

    return ReportValidationError(
        kind=ReportValidationErrorKind.SEMANTIC,
        code=code,
        field=field_name,
        message=message,
    )


def _quality(code: str, field_name: str, message: str) -> ReportValidationError:
    """Build a non-blocking quality warning (RV_006, RV_007)."""

    return ReportValidationError(
        kind=ReportValidationErrorKind.QUALITY,
        code=code,
        field=field_name,
        message=message,
    )


def validate_report(report: Mapping[str, Any]) -> ReportValidationResult:
    """Validate a blind solver report mapping without bundle/manifest/context.

    Returns a :class:`ReportValidationResult`. ``RV_001`` (structural) is
    delegated to the schema validator and, when present, short-circuits the
    semantic/quality checks. ``RV_006``/``RV_007`` are warnings and never make
    the result invalid. The input mapping is never modified.
    """

    # The schema validator expects a JSON ``object`` (a plain ``dict``); a
    # read-only ``Mapping`` such as ``MappingProxyType`` is not recognised. Pass
    # a shallow dict copy so any ``Mapping`` is accepted without mutating input.
    schema_errors = validate_blind_solver_report(dict(report))
    if schema_errors:
        error = ReportValidationError(
            kind=ReportValidationErrorKind.STRUCTURAL,
            code="RV_001",
            field="<schema>",
            message="; ".join(schema_errors),
        )
        return ReportValidationResult(valid=False, errors=(error,), warnings=())

    errors: list[ReportValidationError] = []
    warnings: list[ReportValidationError] = []

    fields = _extract_fields(report)

    # RV_002 (semantic): conclusion present but no evidence.
    if fields.has_conclusion and not fields.has_evidence:
        errors.append(
            _semantic(
                "RV_002",
                "evidence_used",
                "conclusion is not empty but evidence_used is empty",
            )
        )

    # RV_003 (semantic): high confidence with no evidence.
    if fields.confidence == "high" and not fields.has_evidence:
        errors.append(
            _semantic(
                "RV_003",
                "confidence",
                "confidence is high but evidence_used is empty",
            )
        )

    # RV_004 (semantic): high confidence with open questions still open.
    if fields.confidence == "high" and fields.has_open_questions:
        errors.append(
            _semantic(
                "RV_004",
                "open_questions",
                "confidence is high but open_questions is not empty",
            )
        )

    # RV_005 (semantic): no conclusion and no open questions.
    if not fields.has_conclusion and not fields.has_open_questions:
        errors.append(
            _semantic(
                "RV_005",
                "conclusion",
                "conclusion is empty and open_questions is empty",
            )
        )

    # RV_008 (semantic): low confidence but evidence is majority high.
    if fields.confidence == "low":
        high_count = fields.high_evidence_count
        if high_count >= _HIGH_EVIDENCE_THRESHOLD:
            errors.append(
                _semantic(
                    "RV_008",
                    "confidence",
                    "confidence is low but evidence_used has "
                    f"{high_count} items with high confidence",
                )
            )

    # RV_006 (quality/warning): reasoning_summary is only a vague placeholder.
    lowered = fields.reasoning_summary.casefold()
    if any(placeholder in lowered for placeholder in _VAGUE_PLACEHOLDERS):
        warnings.append(
            _quality(
                "RV_006",
                "reasoning_summary",
                "reasoning_summary contains only a vague placeholder",
            )
        )

    # RV_007 (quality/warning): evidence present but conclusion empty.
    if fields.has_evidence and not fields.has_conclusion:
        warnings.append(
            _quality(
                "RV_007",
                "conclusion",
                "evidence_used is not empty but conclusion is empty",
            )
        )

    return ReportValidationResult(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )

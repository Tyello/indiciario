"""Review report contract shared by the specialised reviewers (ISSUE-21+22).

This module backs the review report contract defined in
``schemas/review_report.schema.yaml``. The contract is shared by the Narrative
Reviewer (NR_*) and the Evidence Reviewer (ER_*): both produce a
:class:`ReviewReport` made of codified :class:`ReviewFinding` items, a status
derived from the findings' severities and the reviewer's confidence in its own
conclusions.

STEP-05 provides the shared dataclasses, the structural validation entry point
:func:`validate_review_report` and the serialiser :func:`report_to_dict`. The
semantic rule application (``review_narrative``) is added in a later step.

It never calls an LLM, never accesses the network and never mutates the input it
receives.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0"

# Order used to derive status and to sort findings (critical first).
_SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}

# Roles that count as a plausible alternative suspect besides the executor.
_SUSPECT_ROLES = {"red_herring", "intermediario", "cumplice"}

# Interpretive author language that must not appear in raw player documents.
_INTERPRETIVE_TERMS = (
    "portanto",
    "claramente",
    "isso prova",
    "fica provado",
    "obviamente",
    "evidentemente",
    "sem duvida",
    "sem dúvida",
)

# Stopwords stripped from the executor motivation before matching documents.
_MOTIVATION_STOPWORDS = {
    "para",
    "pela",
    "pelo",
    "uma",
    "que",
    "com",
    "por",
    "dos",
    "das",
    "nos",
    "nas",
    "sua",
    "seu",
    "ele",
    "ela",
    "mais",
    "como",
    "sem",
    "ate",
    "até",
    "muito",
    "queria",
    "quer",
    "antiga",
    "antigo",
    "jamais",
}

# Matches a document code such as ``E1-01`` or ``E9-99`` inside free text.
_DOC_CODE_RE = re.compile(r"\bE\d+-\d+\b")

_REVIEW_REPORT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "review_report.schema.yaml"
)


# --------------------------------------------------------------------------- #
# Public dataclasses                                                          #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ReviewFinding:
    """A single codified finding raised by a reviewer (NR_* or ER_*)."""

    id: str
    code: str  # "NR_*" or "ER_*"
    severity: str  # "critical" | "major" | "minor" | "info"
    field: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class ReviewReport:
    """The structured outcome of a specialised reviewer pass over a Blueprint."""

    report_id: str
    reviewer_type: str  # "narrative" | "evidence"
    blueprint_ref: str
    created_at: str
    created_by: str
    status: str  # "approved" | "needs_revision" | "blocked"
    summary: str
    findings: tuple[ReviewFinding, ...]
    overall_confidence: str  # "low" | "medium" | "high"
    notes: str


def validate_review_report(report: Mapping[str, Any]) -> list[str]:
    """Validate a review report mapping against the schema.

    Returns a sorted list of error messages (empty list == structurally valid).
    The input mapping is never modified.
    """

    schema = yaml.safe_load(
        _REVIEW_REPORT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(report)))


def report_to_dict(report: ReviewReport) -> dict[str, Any]:
    """Serialise a :class:`ReviewReport` ready for :func:`validate_review_report`."""

    return {
        "schema_version": SCHEMA_VERSION,
        "report_id": report.report_id,
        "reviewer_type": report.reviewer_type,
        "blueprint_ref": report.blueprint_ref,
        "created_at": report.created_at,
        "created_by": report.created_by,
        "status": report.status,
        "summary": report.summary,
        "findings": [
            {
                "id": finding.id,
                "code": finding.code,
                "severity": finding.severity,
                "field": finding.field,
                "message": finding.message,
                "recommendation": finding.recommendation,
            }
            for finding in report.findings
        ],
        "overall_confidence": report.overall_confidence,
        "notes": report.notes,
    }


# --------------------------------------------------------------------------- #
# Blueprint field helpers (read-only)                                         #
# --------------------------------------------------------------------------- #
def _enum_value(value: Any) -> str:
    """Return the plain string value of an enum or a stringifiable field."""

    return str(getattr(value, "value", value))


def _document_codes(blueprint: Any) -> set[str]:
    """Codes of every document in the blueprint.

    Shared by the Narrative Reviewer and the Evidence Reviewer (imported there);
    centralised here to keep a single source of truth for the read.
    """

    return {_enum_value(document.codigo) for document in (blueprint.documentos or [])}


def _document_text(document: Any) -> str:
    """Concatenate the string values inside ``Documento.conteudo`` (a dict)."""

    conteudo = getattr(document, "conteudo", None) or {}
    parts = [str(value) for value in conteudo.values() if isinstance(value, str)]
    return " ".join(parts)


def _all_documents_text(blueprint: Any) -> str:
    return " ".join(_document_text(document) for document in (blueprint.documentos or []))


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# --------------------------------------------------------------------------- #
# Narrative rules NR_001-NR_008                                               #
# --------------------------------------------------------------------------- #
def _nr_findings(blueprint: Any) -> list[ReviewFinding]:
    findings: list[ReviewFinding] = []
    document_codes = _document_codes(blueprint)
    documentos = list(blueprint.documentos or [])
    personagens = list(blueprint.personagens or [])
    red_herrings = list(blueprint.red_herrings or [])
    dicas = list(blueprint.dicas or [])
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"NR-{counter:03d}"

    # NR_001 — interpretive author language in a player document (major).
    for index, document in enumerate(documentos):
        lowered = _document_text(document).lower()
        if any(term in lowered for term in _INTERPRETIVE_TERMS):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="NR_001",
                    severity="major",
                    field=f"documentos[{index}].conteudo",
                    message=(
                        f"Documento '{document.codigo}' contém linguagem "
                        "interpretativa do autor em vez de evidência bruta."
                    ),
                    recommendation=(
                        "Reescrever como evidência bruta, sem conclusões "
                        "(\"portanto\", \"claramente\", \"isso prova\")."
                    ),
                )
            )

    # NR_003 — no plausible alternative suspect besides the executor (major).
    executor_id = _enum_value(getattr(blueprint, "executor_id", ""))
    has_alternative_suspect = any(
        _enum_value(personagem.papel) in _SUSPECT_ROLES
        and _enum_value(personagem.id) != executor_id
        for personagem in personagens
    )
    if not has_alternative_suspect:
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="NR_003",
                severity="major",
                field="personagens",
                message=(
                    "Nenhum personagem oferece suspeita plausível além do "
                    "executor; o caso fica sem ambiguidade."
                ),
                recommendation=(
                    "Dar a pelo menos um personagem papel de suspeito "
                    "alternativo (red_herring/intermediario/cumplice)."
                ),
            )
        )

    # NR_004 — executor motivation not supported by any document (major).
    motivacao = _enum_value(getattr(blueprint, "motivacao", "")).lower()
    documents_text = _all_documents_text(blueprint).lower()
    motivation_terms = [
        token
        for token in re.findall(r"[a-zà-ú]+", motivacao)
        if len(token) >= 4 and token not in _MOTIVATION_STOPWORDS
    ]
    if motivation_terms and not any(term in documents_text for term in motivation_terms):
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="NR_004",
                severity="major",
                field="motivacao",
                message=(
                    "A motivação do executor não é sustentada por nenhum "
                    "documento da lista."
                ),
                recommendation=(
                    "Ancorar a motivação em ao menos um documento que a torne "
                    "verificável pelo jogador."
                ),
            )
        )

    # NR_006 — hint references a document code that does not exist (critical).
    for dica in dicas:
        text = " ".join(
            _enum_value(getattr(dica, attr, ""))
            for attr in ("texto", "condicao_uso", "o_que_desbloqueia")
        )
        referenced = set(_DOC_CODE_RE.findall(text))
        missing = sorted(referenced - document_codes)
        if missing:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="NR_006",
                    severity="critical",
                    field=f"dicas[{_enum_value(getattr(dica, 'numero', ''))}]",
                    message=(
                        "Dica referencia documento inexistente: "
                        f"{', '.join(missing)}."
                    ),
                    recommendation=(
                        "Corrigir a referência da dica para um documento "
                        "existente na lista."
                    ),
                )
            )

    # NR_008 — red herring without a supporting document (major).
    for red_herring in red_herrings:
        documento_descarte = _enum_value(getattr(red_herring, "documento_descarte", ""))
        if documento_descarte and documento_descarte not in document_codes:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="NR_008",
                    severity="major",
                    field="red_herrings",
                    message=(
                        f"Red herring '{_enum_value(red_herring.personagem_id)}' "
                        "não tem documento associado que o sustente."
                    ),
                    recommendation=(
                        "Associar ao red herring um documento de descarte "
                        "existente na lista."
                    ),
                )
            )

    return findings


def _status_for(findings: list[ReviewFinding]) -> str:
    if any(finding.severity == "critical" for finding in findings):
        return "blocked"
    if any(finding.severity == "major" for finding in findings):
        return "needs_revision"
    return "approved"


def _summary_for(reviewer_type: str, findings: list[ReviewFinding], status: str) -> str:
    if not findings:
        return (
            f"Revisão {reviewer_type}: nenhum problema detectado; "
            f"status {status}."
        )
    return (
        f"Revisão {reviewer_type}: {len(findings)} finding(s) detectado(s); "
        f"status {status}."
    )


def review_narrative(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> ReviewReport:
    """Apply rules NR_001-NR_008 and return a :class:`ReviewReport`.

    Never calls an LLM, never accesses the network and never mutates the
    blueprint. Missing optional collections are treated as empty lists.
    Findings are ordered by severity (critical first).
    """

    findings = _nr_findings(blueprint)
    findings.sort(key=lambda finding: _SEVERITY_ORDER.get(finding.severity, 99))
    status = _status_for(findings)

    return ReviewReport(
        report_id=report_id,
        reviewer_type="narrative",
        blueprint_ref=blueprint_ref,
        created_at=_now_iso(),
        created_by=created_by,
        status=status,
        summary=_summary_for("narrative", findings, status),
        findings=tuple(findings),
        overall_confidence=overall_confidence,
        notes=notes,
    )

"""Visual review report contract (ISSUE-23+24).

This module backs the review report contract defined in
``schemas/visual_accessibility_review_report.schema.yaml``. The contract is
shared by the Visual Reviewer (VR_*) and the Accessibility Reviewer (AR_*),
mirroring the pattern established by ``generator/narrative_reviewer.py`` for
the Narrative/Evidence reviewers: both produce a
:class:`VisualAccessibilityReviewReport` made of codified :class:`ReviewFinding`
items, a status derived from the findings' severities and the reviewer's
confidence in its own conclusions.

STEP-05 provides the shared dataclasses, the structural validation entry
point :func:`validate_visual_accessibility_review_report` and the serialiser
:func:`report_to_dict`. The semantic rule application (``review_visual``) is
added in a later step.

This schema/module pair is independent from
``schemas/review_report.schema.yaml`` and ``generator/narrative_reviewer.py``;
neither is altered here.

It never calls an LLM, never accesses the network and never mutates the input
it receives.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0"

# Order used to derive status and to sort findings (critical first).
_SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}

# VR_001 — maximum concatenated `conteudo` characters for a single document
# before it risks becoming illegible on a single printed/rendered card.
MAX_CONTEUDO_CHARS = 2000

# VR_006 — document `tipo` values with a known visual template.
VISUAL_DOC_TYPES: tuple[str, ...] = (
    "boletim",
    "chat",
    "depoimento",
    "folha_cruzamento",
    "log_acesso",
    "manual",
    "protocolo",
)

_VISUAL_ACCESSIBILITY_REVIEW_REPORT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "visual_accessibility_review_report.schema.yaml"
)


# --------------------------------------------------------------------------- #
# Public dataclasses                                                          #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ReviewFinding:
    """A single codified finding raised by a reviewer (VR_* or AR_*)."""

    id: str
    code: str  # "VR_*" or "AR_*"
    severity: str  # "critical" | "major" | "minor" | "info"
    field: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class VisualAccessibilityReviewReport:
    """The structured outcome of a visual/accessibility reviewer pass."""

    report_id: str
    reviewer_type: str  # "visual" | "accessibility"
    blueprint_ref: str
    created_at: str
    created_by: str
    status: str  # "approved" | "needs_revision" | "blocked"
    summary: str
    findings: tuple[ReviewFinding, ...]
    overall_confidence: str  # "low" | "medium" | "high"
    notes: str


def validate_visual_accessibility_review_report(
    report: Mapping[str, Any],
) -> list[str]:
    """Validate a report mapping against the visual/accessibility schema.

    Returns a sorted list of error messages (empty list == structurally valid).
    The input mapping is never modified.
    """

    schema = yaml.safe_load(
        _VISUAL_ACCESSIBILITY_REVIEW_REPORT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(dict(report)))


def report_to_dict(report: VisualAccessibilityReviewReport) -> dict[str, Any]:
    """Serialise a :class:`VisualAccessibilityReviewReport`.

    Ready for :func:`validate_visual_accessibility_review_report`.
    """

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
# Shared helpers (status/summary/time)                                       #
# --------------------------------------------------------------------------- #
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


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# --------------------------------------------------------------------------- #
# Blueprint field helpers (read-only)                                        #
# --------------------------------------------------------------------------- #
def _enum_value(value: Any) -> str:
    """Return the plain string value of an enum or a stringifiable field."""

    return str(getattr(value, "value", value))


def _document_text(document: Any) -> str:
    """Concatenate the string values inside ``Documento.conteudo`` (a dict)."""

    conteudo = getattr(document, "conteudo", None) or {}
    parts = [str(value) for value in conteudo.values() if isinstance(value, str)]
    return " ".join(parts)


def _exceeds_conteudo_limit(document: Any) -> bool:
    """Whether ``document``'s concatenated ``conteudo`` is above
    :data:`MAX_CONTEUDO_CHARS`. Shared by VR_001 and AR_002."""

    return len(_document_text(document)) > MAX_CONTEUDO_CHARS


# --------------------------------------------------------------------------- #
# Visual rules VR_001-VR_006                                                  #
# --------------------------------------------------------------------------- #
def _vr_findings(blueprint: Any) -> list[ReviewFinding]:
    findings: list[ReviewFinding] = []
    documentos = list(blueprint.documentos or [])
    personagens = list(blueprint.personagens or [])
    printable_cards = list(blueprint.printable_cards or [])
    visual_procedural = getattr(blueprint, "visual_procedural", None)
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"VR-{counter:03d}"

    card_titulos = {_enum_value(card.titulo) for card in printable_cards}

    # VR_001 — document conteudo concatenated above MAX_CONTEUDO_CHARS (major).
    for index, document in enumerate(documentos):
        if _exceeds_conteudo_limit(document):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="VR_001",
                    severity="major",
                    field=f"documentos[{index}].conteudo",
                    message=(
                        f"Documento '{_enum_value(document.codigo)}' tem conteudo "
                        f"acima de {MAX_CONTEUDO_CHARS} caracteres, risco de "
                        "ilegibilidade em um único card."
                    ),
                    recommendation=(
                        "Dividir o conteúdo em mais de um documento ou reduzir "
                        "o texto bruto do card."
                    ),
                )
            )

    # VR_002 — character cited in documents without a matching printable_card
    # (matched by personagem nome against printable_card titulo) (minor).
    personagens_por_id = {_enum_value(personagem.id): personagem for personagem in personagens}
    cited_ids: set[str] = set()
    for document in documentos:
        cited_ids.update(_enum_value(cid) for cid in (document.ids_citados or []))
    for personagem_id in sorted(cited_ids):
        personagem = personagens_por_id.get(personagem_id)
        if personagem is None:
            continue
        if _enum_value(personagem.nome) not in card_titulos:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="VR_002",
                    severity="minor",
                    field="printable_cards",
                    message=(
                        f"Personagem '{_enum_value(personagem.nome)}' é citado em "
                        "documentos mas não tem printable_card correspondente."
                    ),
                    recommendation=(
                        "Criar um printable_card com titulo correspondente ao "
                        "personagem citado."
                    ),
                )
            )

    # VR_003 — two printable_cards share the same codigo_visual (major).
    seen_codigos: dict[str, int] = {}
    duplicated_codigos: set[str] = set()
    for card in printable_cards:
        codigo = card.codigo_visual
        if not codigo:
            continue
        codigo = _enum_value(codigo)
        seen_codigos[codigo] = seen_codigos.get(codigo, 0) + 1
        if seen_codigos[codigo] > 1:
            duplicated_codigos.add(codigo)
    for codigo in sorted(duplicated_codigos):
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="VR_003",
                severity="major",
                field="printable_cards",
                message=f"codigo_visual '{codigo}' duplicado em dois ou mais cards.",
                recommendation="Atribuir códigos visuais únicos por card.",
            )
        )

    # VR_004 — printable_card without tags_visuais (minor).
    for index, card in enumerate(printable_cards):
        if not (card.tags_visuais or []):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="VR_004",
                    severity="minor",
                    field=f"printable_cards[{index}].tags_visuais",
                    message=(
                        f"Card '{_enum_value(card.titulo)}' não tem "
                        "tags_visuais, perde dica visual de agrupamento."
                    ),
                    recommendation="Adicionar ao menos uma tag visual ao card.",
                )
            )

    # VR_005 — case cites locations but visual_procedural.mapas is empty (info,
    # never escalated: Aurora is map-less by validated playtest decision).
    locais = list(getattr(visual_procedural, "locais", None) or []) if visual_procedural else []
    mapas = list(getattr(visual_procedural, "mapas", None) or []) if visual_procedural else []
    if locais and not mapas:
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="VR_005",
                severity="info",
                field="visual_procedural.mapas",
                message=(
                    "O caso cita locais em visual_procedural.locais mas "
                    "visual_procedural.mapas está vazio."
                ),
                recommendation=(
                    "Avaliar se um mapa ajudaria a navegação (opcional; "
                    "ausência de mapa pode ser decisão editorial válida)."
                ),
            )
        )

    # VR_006 — document tipo outside the known visual type set (minor).
    for index, document in enumerate(documentos):
        tipo = _enum_value(document.tipo)
        if tipo not in VISUAL_DOC_TYPES:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="VR_006",
                    severity="minor",
                    field=f"documentos[{index}].tipo",
                    message=(
                        f"Documento '{_enum_value(document.codigo)}' tem tipo "
                        f"'{tipo}' fora do conjunto de tipos com template "
                        "visual conhecido."
                    ),
                    recommendation=(
                        "Mapear um template visual para o tipo ou usar um "
                        "tipo já suportado."
                    ),
                )
            )

    return findings


def review_visual(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> VisualAccessibilityReviewReport:
    """Apply rules VR_001-VR_006 and return a :class:`VisualAccessibilityReviewReport`.

    Never calls an LLM, never accesses the network and never mutates the
    blueprint. Missing optional collections are treated as empty lists.
    Findings are ordered by severity (critical first). VR_005 is always
    ``info`` and never escalates the report's status.
    """

    findings = _vr_findings(blueprint)
    findings.sort(key=lambda finding: _SEVERITY_ORDER.get(finding.severity, 99))
    status = _status_for(findings)

    return VisualAccessibilityReviewReport(
        report_id=report_id,
        reviewer_type="visual",
        blueprint_ref=blueprint_ref,
        created_at=_now_iso(),
        created_by=created_by,
        status=status,
        summary=_summary_for("visual", findings, status),
        findings=tuple(findings),
        overall_confidence=overall_confidence,
        notes=notes,
    )

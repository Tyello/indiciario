"""Accessibility Reviewer (ISSUE-23+24, STEP-11).

Specialised reviewer that operates over a **Blueprint** and produces a
:class:`VisualAccessibilityReviewReport` made of codified :class:`ReviewFinding`
items. It applies the accessibility rules AR_001-AR_006 of the ISSUE-23+24
spec.

The shared contract (:class:`ReviewFinding`, :class:`VisualAccessibilityReviewReport`,
:func:`validate_visual_accessibility_review_report`, :func:`report_to_dict`,
``_SEVERITY_ORDER``, ``_status_for``, ``_summary_for``, ``_now_iso``,
``_enum_value``) is defined in ``generator/visual_reviewer.py`` and imported
here — never duplicated, mirroring the pattern of
``generator/evidence_reviewer.py`` importing from
``generator/narrative_reviewer.py``.

It never calls an LLM, never accesses the network and never mutates the
blueprint it receives. Missing optional collections are treated as empty lists.

Rule table (see ``.ai/issues/ISSUE-23+24_SPEC.md``):

- AR_001 (major): an envelope holds more than ``MAX_DOCS_PER_ENVELOPE``
  documents.
- AR_002 (major): a document's concatenated ``conteudo`` is above
  ``MAX_CONTEUDO_CHARS``.
- AR_003 (minor): a ``printable_card`` has neither ``subtitulo`` nor
  ``descricao_curta``.
- AR_004 (minor): a document cites more than ``MAX_CROSS_REFS`` codes/ids
  combined (``ids_citados`` + ``codigos_citados``).
- AR_005 (info): a document's ``conteudo`` is empty, i.e. has no field at all
  to anchor a title/subject (no hierarchy for the reader to navigate by).
- AR_006 (major): the case has no ``printable_card`` at all (total loss of
  visual anchor).
"""

from __future__ import annotations

from typing import Any

from generator.visual_reviewer import (
    _SEVERITY_ORDER,
    MAX_CONTEUDO_CHARS,
    ReviewFinding,
    VisualAccessibilityReviewReport,
    _exceeds_conteudo_limit,
    _enum_value,
    _now_iso,
    _status_for,
    _summary_for,
    report_to_dict,
    validate_visual_accessibility_review_report,
)

__all__ = [
    "MAX_CROSS_REFS",
    "MAX_DOCS_PER_ENVELOPE",
    "ReviewFinding",
    "VisualAccessibilityReviewReport",
    "report_to_dict",
    "review_accessibility",
    "validate_visual_accessibility_review_report",
]

# AR_001 — maximum documents allowed in a single envelope before it risks
# overwhelming players with reading volume.
MAX_DOCS_PER_ENVELOPE = 8

# AR_004 — maximum combined cross-referenced codes/ids a single document may
# cite before it becomes hard to follow.
MAX_CROSS_REFS = 6

# --------------------------------------------------------------------------- #
# Blueprint field helpers (read-only)                                        #
# --------------------------------------------------------------------------- #
def _has_identifiable_title(document: Any) -> bool:
    """A document has an identifiable title/subject when ``conteudo`` is not
    empty: at least one field exists for the reader to anchor on."""

    conteudo = getattr(document, "conteudo", None) or {}
    return bool(conteudo)


# --------------------------------------------------------------------------- #
# Accessibility rules AR_001-AR_006                                          #
# --------------------------------------------------------------------------- #
def _ar_findings(blueprint: Any) -> list[ReviewFinding]:
    findings: list[ReviewFinding] = []
    documentos = list(blueprint.documentos or [])
    printable_cards = list(blueprint.printable_cards or [])
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"AR-{counter:03d}"

    # AR_001 — envelope with more than MAX_DOCS_PER_ENVELOPE documents (major).
    counts_by_envelope: dict[str, int] = {}
    for document in documentos:
        envelope = _enum_value(getattr(document, "envelope", ""))
        counts_by_envelope[envelope] = counts_by_envelope.get(envelope, 0) + 1
    for envelope in sorted(counts_by_envelope):
        count = counts_by_envelope[envelope]
        if count > MAX_DOCS_PER_ENVELOPE:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="AR_001",
                    severity="major",
                    field="documentos",
                    message=(
                        f"Envelope '{envelope}' tem {count} documentos, acima "
                        f"do limite de {MAX_DOCS_PER_ENVELOPE}."
                    ),
                    recommendation=(
                        "Redistribuir documentos entre envelopes ou reduzir o "
                        "número de documentos do envelope."
                    ),
                )
            )

    # AR_002 — document conteudo above MAX_CONTEUDO_CHARS (major).
    for index, document in enumerate(documentos):
        if _exceeds_conteudo_limit(document):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="AR_002",
                    severity="major",
                    field=f"documentos[{index}].conteudo",
                    message=(
                        f"Documento '{_enum_value(document.codigo)}' tem conteudo "
                        f"acima de {MAX_CONTEUDO_CHARS} caracteres, risco de "
                        "sobrecarga de leitura."
                    ),
                    recommendation=(
                        "Dividir o conteúdo em mais de um documento ou reduzir "
                        "o texto bruto do documento."
                    ),
                )
            )

    # AR_003 — printable_card without subtitulo AND without descricao_curta (minor).
    for index, card in enumerate(printable_cards):
        subtitulo = getattr(card, "subtitulo", None)
        descricao_curta = getattr(card, "descricao_curta", None)
        if not subtitulo and not descricao_curta:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="AR_003",
                    severity="minor",
                    field=f"printable_cards[{index}]",
                    message=(
                        f"Card '{_enum_value(card.titulo)}' não tem subtitulo "
                        "nem descricao_curta, perde contexto de leitura rápida."
                    ),
                    recommendation=(
                        "Adicionar subtitulo ou descricao_curta ao card."
                    ),
                )
            )

    # AR_004 — document with more than MAX_CROSS_REFS cited codes/ids (minor).
    for index, document in enumerate(documentos):
        ids_citados = list(getattr(document, "ids_citados", None) or [])
        codigos_citados = list(getattr(document, "codigos_citados", None) or [])
        total_refs = len(ids_citados) + len(codigos_citados)
        if total_refs > MAX_CROSS_REFS:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="AR_004",
                    severity="minor",
                    field=f"documentos[{index}]",
                    message=(
                        f"Documento '{_enum_value(document.codigo)}' cita "
                        f"{total_refs} códigos/ids, acima do limite de "
                        f"{MAX_CROSS_REFS}."
                    ),
                    recommendation=(
                        "Reduzir o número de referências cruzadas citadas em "
                        "um único documento."
                    ),
                )
            )

    # AR_005 — document conteudo without identifiable title/subject (info).
    for index, document in enumerate(documentos):
        if not _has_identifiable_title(document):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="AR_005",
                    severity="info",
                    field=f"documentos[{index}].conteudo",
                    message=(
                        f"Documento '{_enum_value(document.codigo)}' não tem "
                        "campo de título/assunto identificável no conteudo."
                    ),
                    recommendation=(
                        "Adicionar um campo TITULO ou ASSUNTO ao conteudo para "
                        "facilitar a identificação rápida do documento."
                    ),
                )
            )

    # AR_006 — case without any printable_card (major).
    if not printable_cards:
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="AR_006",
                severity="major",
                field="printable_cards",
                message=(
                    "O caso não tem nenhum printable_card, perda total de "
                    "âncora visual."
                ),
                recommendation=(
                    "Criar ao menos um printable_card para o caso."
                ),
            )
        )

    return findings


def review_accessibility(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> VisualAccessibilityReviewReport:
    """Apply rules AR_001-AR_006 and return a :class:`VisualAccessibilityReviewReport`.

    Never calls an LLM, never accesses the network and never mutates the
    blueprint. Missing optional collections are treated as empty lists.
    Findings are ordered by severity (critical first).
    """

    findings = _ar_findings(blueprint)
    findings.sort(key=lambda finding: _SEVERITY_ORDER.get(finding.severity, 99))
    status = _status_for(findings)

    return VisualAccessibilityReviewReport(
        report_id=report_id,
        reviewer_type="accessibility",
        blueprint_ref=blueprint_ref,
        created_at=_now_iso(),
        created_by=created_by,
        status=status,
        summary=_summary_for("accessibility", findings, status),
        findings=tuple(findings),
        overall_confidence=overall_confidence,
        notes=notes,
    )

"""Evidence Reviewer (ISSUE-21+22, STEP-09).

Specialised reviewer that operates over a **Blueprint** and produces a
:class:`ReviewReport` made of codified :class:`ReviewFinding` items. It applies
the evidence-chain rules ER_001-ER_008 of the ISSUE-21 spec.

The shared contract (:class:`ReviewFinding`, :class:`ReviewReport`,
:func:`validate_review_report`, :func:`report_to_dict`) is defined in
``generator/narrative_reviewer.py`` and imported here — never duplicated.

It never calls an LLM, never accesses the network and never mutates the
blueprint it receives. Missing optional collections are treated as empty lists.

Rule field mapping (see ``.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`` and
DVG-EXEC-004 in ``STEP-08_EXECUTION.md``):

- ER_001 (critical): a ``Pista`` references a document code (``documento`` or
  ``confirmacao``) absent from ``documentos``.
- ER_002 (major): a ``Pilar`` whose documents are not supported by any pista.
- ER_003 (major): ``cadeia_causal`` has fewer than 3 links.
- ER_004 (major): an envelope in ``objetivos_por_envelope`` has no pista whose
  document belongs to that envelope.
- ER_005 (minor): more than 60% of the pistas point at the same document.
- ER_006 (major): a red herring whose ``documento_descarte`` is not referenced
  by any pista (cannot be discarded with available evidence).
- ER_007 (major): a mandatory ``ContratoEvidencia``
  (``obrigatoria_para_avanco`` is True) whose ``prova_principal`` is not an E1
  document — DVG-EXEC-004: ``Pista`` has no ``obrigatoria`` field, the real
  mandatory flag lives on ``ContratoEvidencia``.
- ER_008 (minor): fewer than 40% of the documents contribute to any pista.
"""

from __future__ import annotations

from typing import Any

from generator.narrative_reviewer import (
    _SEVERITY_ORDER,
    ReviewFinding,
    ReviewReport,
    _document_codes,
    _enum_value,
    _now_iso,
    _status_for,
    _summary_for,
    report_to_dict,
    validate_review_report,
)

__all__ = [
    "ReviewFinding",
    "ReviewReport",
    "report_to_dict",
    "review_evidence",
    "validate_review_report",
]

# Concentration threshold for ER_005 (share of pistas on a single document).
_CONCENTRATION_THRESHOLD = 0.60

# Minimum share of documents that must contribute to a pista (ER_008).
_MIN_DOCUMENT_COVERAGE = 0.40


# --------------------------------------------------------------------------- #
# Blueprint field helpers (read-only)                                         #
# --------------------------------------------------------------------------- #
def _envelope_by_document(blueprint: Any) -> dict[str, str]:
    return {
        _enum_value(doc.codigo): _enum_value(getattr(doc, "envelope", ""))
        for doc in (blueprint.documentos or [])
    }


def _pista_documents(pista: Any) -> list[str]:
    """Document codes a pista touches (its own document and its confirmation)."""

    codes: list[str] = []
    for attr in ("documento", "confirmacao"):
        value = _enum_value(getattr(pista, attr, ""))
        if value:
            codes.append(value)
    return codes


def _evidence_documents(blueprint: Any) -> set[str]:
    """All document codes referenced by at least one pista."""

    documents: set[str] = set()
    for pista in (blueprint.matriz_pistas or []):
        documents.update(_pista_documents(pista))
    return documents


# --------------------------------------------------------------------------- #
# Evidence rules ER_001-ER_008                                                #
# --------------------------------------------------------------------------- #
def _er_findings(blueprint: Any) -> list[ReviewFinding]:
    findings: list[ReviewFinding] = []
    document_codes = _document_codes(blueprint)
    envelope_by_document = _envelope_by_document(blueprint)
    documentos = list(blueprint.documentos or [])
    pistas = list(blueprint.matriz_pistas or [])
    pilares = list(blueprint.pilares_validacao or [])
    objetivos = list(blueprint.objetivos_por_envelope or [])
    red_herrings = list(blueprint.red_herrings or [])
    contratos = list(getattr(blueprint, "contratos_evidencia", None) or [])
    cadeia_causal = list(blueprint.cadeia_causal or [])
    evidence_documents = _evidence_documents(blueprint)
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"ER-{counter:03d}"

    # ER_001 — pista references a missing document (critical).
    for index, pista in enumerate(pistas):
        missing = sorted(
            code for code in _pista_documents(pista) if code not in document_codes
        )
        if missing:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_001",
                    severity="critical",
                    field=f"matriz_pistas[{index}]",
                    message=(
                        "Pista referencia documento inexistente: "
                        f"{', '.join(missing)}."
                    ),
                    recommendation=(
                        "Corrigir a referência da pista para um documento "
                        "existente na lista."
                    ),
                )
            )

    # ER_002 — pilar with no supporting pista (major).
    for index, pilar in enumerate(pilares):
        pilar_docs = {
            _enum_value(getattr(pilar, attr, ""))
            for attr in ("documento_principal", "confirmacao")
        }
        pilar_docs.discard("")
        if pilar_docs and not (pilar_docs & evidence_documents):
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_002",
                    severity="major",
                    field=f"pilares_validacao[{index}]",
                    message=(
                        f"Pilar '{_enum_value(getattr(pilar, 'nome', ''))}' não "
                        "tem nenhuma pista que o suporte."
                    ),
                    recommendation=(
                        "Adicionar à matriz_pistas ao menos uma pista que "
                        "aponte para os documentos do pilar."
                    ),
                )
            )

    # ER_003 — causal chain with fewer than 3 links (major).
    if len(cadeia_causal) < 3:
        findings.append(
            ReviewFinding(
                id=_next_id(),
                code="ER_003",
                severity="major",
                field="cadeia_causal",
                message=(
                    "A cadeia causal tem menos de 3 elos "
                    f"({len(cadeia_causal)})."
                ),
                recommendation=(
                    "Expandir a cadeia causal para ao menos 3 elos encadeados."
                ),
            )
        )

    # ER_004 — envelope without a designated pista (major).
    pista_envelopes = {
        envelope_by_document.get(code)
        for pista in pistas
        for code in _pista_documents(pista)
    }
    pista_envelopes.discard(None)
    pista_envelopes.discard("")
    for index, objetivo in enumerate(objetivos):
        envelope = _enum_value(getattr(objetivo, "envelope", ""))
        if envelope and envelope not in pista_envelopes:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_004",
                    severity="major",
                    field=f"objetivos_por_envelope[{index}]",
                    message=(
                        f"Envelope '{envelope}' não tem nenhuma pista designada."
                    ),
                    recommendation=(
                        "Designar ao menos uma pista cujo documento pertença ao "
                        f"envelope '{envelope}'."
                    ),
                )
            )

    # ER_005 — excessive concentration of pistas on one document (minor).
    if pistas:
        counts: dict[str, int] = {}
        for pista in pistas:
            documento = _enum_value(getattr(pista, "documento", ""))
            if documento:
                counts[documento] = counts.get(documento, 0) + 1
        if counts:
            documento_top, top_count = max(counts.items(), key=lambda item: item[1])
            if top_count / len(pistas) > _CONCENTRATION_THRESHOLD:
                findings.append(
                    ReviewFinding(
                        id=_next_id(),
                        code="ER_005",
                        severity="minor",
                        field="matriz_pistas",
                        message=(
                            f"Mais de 60% das pistas apontam para '{documento_top}' "
                            f"({top_count}/{len(pistas)}); concentração excessiva."
                        ),
                        recommendation=(
                            "Distribuir as pistas por mais documentos para evitar "
                            "que a solução fique óbvia demais."
                        ),
                    )
                )

    # ER_006 — red herring not discardable with available evidence (major).
    for index, red_herring in enumerate(red_herrings):
        documento_descarte = _enum_value(getattr(red_herring, "documento_descarte", ""))
        if documento_descarte and documento_descarte not in evidence_documents:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_006",
                    severity="major",
                    field=f"red_herrings[{index}]",
                    message=(
                        f"Red herring '{_enum_value(getattr(red_herring, 'personagem_id', ''))}' "
                        "não pode ser descartado: nenhuma pista contradiz ou "
                        "contextualiza o documento de descarte."
                    ),
                    recommendation=(
                        "Adicionar uma pista que aponte para o documento de "
                        "descarte do red herring."
                    ),
                )
            )

    # ER_007 — mandatory contract evidence not available in E1 (major).
    e1_documents = {
        code for code, envelope in envelope_by_document.items() if envelope == "E1"
    }
    for index, contrato in enumerate(contratos):
        if not getattr(contrato, "obrigatoria_para_avanco", False):
            continue
        prova_principal = _enum_value(getattr(contrato, "prova_principal", "") or "")
        if prova_principal and prova_principal not in e1_documents:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_007",
                    severity="major",
                    field=f"contratos_evidencia[{index}]",
                    message=(
                        f"Contrato obrigatório '{_enum_value(getattr(contrato, 'id', ''))}' "
                        f"depende de prova '{prova_principal}' ausente do E1."
                    ),
                    recommendation=(
                        "Disponibilizar a prova principal obrigatória em um "
                        "documento do E1."
                    ),
                )
            )

    # ER_008 — too few documents contribute to a pista (minor).
    if documentos:
        contributing = len(document_codes & evidence_documents)
        if contributing / len(documentos) < _MIN_DOCUMENT_COVERAGE:
            findings.append(
                ReviewFinding(
                    id=_next_id(),
                    code="ER_008",
                    severity="minor",
                    field="documentos",
                    message=(
                        "Menos de 40% dos documentos contribuem para alguma "
                        f"pista ({contributing}/{len(documentos)})."
                    ),
                    recommendation=(
                        "Aumentar o número de documentos que ancoram pistas na "
                        "matriz_pistas."
                    ),
                )
            )

    return findings


def review_evidence(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> ReviewReport:
    """Apply rules ER_001-ER_008 and return a :class:`ReviewReport`.

    Never calls an LLM, never accesses the network and never mutates the
    blueprint. Missing optional collections are treated as empty lists.
    Findings are ordered by severity (critical first).
    """

    findings = _er_findings(blueprint)
    findings.sort(key=lambda finding: _SEVERITY_ORDER.get(finding.severity, 99))
    status = _status_for(findings)

    return ReviewReport(
        report_id=report_id,
        reviewer_type="evidence",
        blueprint_ref=blueprint_ref,
        created_at=_now_iso(),
        created_by=created_by,
        status=status,
        summary=_summary_for("evidence", findings, status),
        findings=tuple(findings),
        overall_confidence=overall_confidence,
        notes=notes,
    )

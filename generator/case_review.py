"""Relatório editorial heurístico para revisão/playtest de casos.

O Case Review não substitui validator, baseline visual nem playtest humano. Ele
organiza sinais editoriais derivados do Case Kernel e de métricas já existentes
para reduzir achismo antes da revisão humana.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from generator.case_kernel import (
    CaseKernel,
    CaseKernelFinding,
    extract_case_kernel,
    validate_case_kernel,
)
from generator.models import Blueprint
from generator.playtest_metrics import (
    DIFFICULTY_ORDER,
    DOCUMENT_RANGES,
    analyze_playtest,
)

ReviewFormat = Literal["markdown", "json"]
ReviewStatus = Literal[
    "READY_FOR_BASELINE",
    "READY_FOR_PLAYTEST",
    "NEEDS_EDITORIAL_REVIEW",
    "BLOCKED",
]


@dataclass(frozen=True)
class CaseReviewFinding:
    """Finding editorial do Case Review."""

    code: str
    severity: str
    message: str
    section: str
    detail: str = ""


@dataclass(frozen=True)
class CaseReview:
    """Relatório estruturado e serializável do Case Review."""

    title: str
    difficulty_declared: str
    status: ReviewStatus
    kernel: CaseKernel
    kernel_findings: tuple[CaseKernelFinding, ...]
    findings: tuple[CaseReviewFinding, ...]
    playtest_metrics: dict[str, Any]


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return "" if value is None else str(value)


def _finding(
    code: str,
    severity: str,
    message: str,
    section: str,
    detail: str = "",
) -> CaseReviewFinding:
    return CaseReviewFinding(
        code=code,
        severity=severity,
        message=message,
        section=section,
        detail=detail,
    )


def _document_codes(blueprint: Blueprint) -> set[str]:
    return {document.codigo for document in blueprint.documentos}


def _objective_envelopes(blueprint: Blueprint) -> set[str]:
    return {objective.envelope for objective in blueprint.objetivos_por_envelope}


def _required_contracts(blueprint: Blueprint) -> list[Any]:
    return [
        contract
        for contract in blueprint.contratos_evidencia
        if contract.obrigatoria_para_avanco
    ]


def _review_solvability(blueprint: Blueprint, kernel: CaseKernel) -> list[CaseReviewFinding]:
    findings: list[CaseReviewFinding] = []
    required = _required_contracts(blueprint)
    required_refs = [
        reference
        for contract in required
        for reference in [contract.prova_principal, contract.confirmacao_independente]
        if reference
    ]
    document_codes = _document_codes(blueprint)

    if len(required) < 2:
        findings.append(
            _finding(
                "CR_SOLV_001",
                "warning",
                "Poucas evidências obrigatórias para sustentar progressão e solução.",
                "solvabilidade",
                f"Contratos obrigatórios encontrados: {len(required)}.",
            )
        )

    if len(set(required_refs)) <= 1:
        findings.append(
            _finding(
                "CR_SOLV_004",
                "warning",
                "O caso pode depender de uma única pista ou referência documental.",
                "solvabilidade",
                f"Referências documentais únicas em contratos obrigatórios: {len(set(required_refs))}.",
            )
        )

    if required_refs:
        counts = Counter(required_refs)
        dominant_doc, dominant_count = counts.most_common(1)[0]
        if len(required) >= 2 and dominant_count / max(len(required_refs), 1) >= 0.6:
            findings.append(
                _finding(
                    "CR_SOLV_002",
                    "warning",
                    "Risco de documento dominante demais na cadeia de solução.",
                    "solvabilidade",
                    f"{dominant_doc} aparece em {dominant_count} de {len(required_refs)} referências obrigatórias.",
                )
            )

    missing_document_refs = sorted(
        {reference for reference in required_refs if reference not in document_codes}
    )
    if missing_document_refs:
        findings.append(
            _finding(
                "CR_SOLV_003",
                "critical",
                "Evidências obrigatórias referenciam documentos ausentes do caso.",
                "solvabilidade",
                ", ".join(missing_document_refs),
            )
        )

    evidence_without_envelope = [
        evidence.id for evidence in kernel.evidencias_obrigatorias if not evidence.envelope
    ]
    if evidence_without_envelope:
        findings.append(
            _finding(
                "CR_SOLV_003",
                "warning",
                "Evidências obrigatórias sem envelope associado.",
                "solvabilidade",
                ", ".join(evidence_without_envelope),
            )
        )

    return findings


def _text_suggests_final_solution(text: str) -> bool:
    lowered = text.lower()
    final_terms = [
        "solução final",
        "solucao final",
        "culpado",
        "executor",
        "planejador",
        "beneficiário",
        "beneficiario",
        "quem cometeu",
        "quem desviou",
    ]
    guards = [
        "não precisa resolver",
        "nao precisa resolver",
        "sem exigir",
        "hipótese parcial",
        "hipotese parcial",
        "não fecha",
        "nao fecha",
    ]
    return any(term in lowered for term in final_terms) and not any(
        guard in lowered for guard in guards
    )


def _review_progression(blueprint: Blueprint, kernel: CaseKernel) -> list[CaseReviewFinding]:
    findings: list[CaseReviewFinding] = []
    objective_envelopes = _objective_envelopes(blueprint)
    document_envelopes = {document.envelope for document in blueprint.documentos}

    for envelope in kernel.envelopes:
        missing = [
            label
            for label, value in [
                ("pergunta", envelope.pergunta),
                ("resposta esperada", envelope.resposta_esperada),
                ("função narrativa", envelope.funcao_narrativa),
            ]
            if not value.strip()
        ]
        if missing:
            findings.append(
                _finding(
                    "CR_PROG_001",
                    "warning",
                    f"Envelope {envelope.id} sem objetivo claro.",
                    "progressao",
                    ", ".join(missing),
                )
            )

        if not envelope.criterio_avanco.strip():
            findings.append(
                _finding(
                    "CR_PROG_004",
                    "warning",
                    f"Envelope {envelope.id} sem critério de avanço.",
                    "progressao",
                )
            )

        if envelope.id == "E1" and _text_suggests_final_solution(
            f"{envelope.pergunta} {envelope.resposta_esperada} {kernel.hipotese_e1}"
        ):
            findings.append(
                _finding(
                    "CR_PROG_002",
                    "warning",
                    "E1 parece pedir solução final em vez de hipótese parcial.",
                    "progressao",
                )
            )

    envelopes_without_objective = sorted(document_envelopes - objective_envelopes)
    if envelopes_without_objective:
        findings.append(
            _finding(
                "CR_PROG_001",
                "warning",
                "Há envelopes com documentos, mas sem objetivo editorial declarado.",
                "progressao",
                ", ".join(envelopes_without_objective),
            )
        )

    if "E2" in objective_envelopes and not kernel.recontextualizacao_e2.strip():
        findings.append(
            _finding(
                "CR_PROG_003",
                "warning",
                "E2 sem recontextualização aparente.",
                "progressao",
            )
        )

    return findings


def _review_red_herrings(blueprint: Blueprint) -> list[CaseReviewFinding]:
    findings: list[CaseReviewFinding] = []
    if not blueprint.red_herrings:
        return [
            _finding(
                "CR_RH_001",
                "warning",
                "Red herring ausente.",
                "red_herrings",
            )
        ]

    conclusive_terms = [
        "culpado",
        "confessa",
        "confissão",
        "confissao",
        "prova que cometeu",
        "responsável pelo crime",
        "responsavel pelo crime",
        "incriminatório",
        "incriminatorio",
    ]
    document_codes = _document_codes(blueprint)
    for red_herring in blueprint.red_herrings:
        motivo = red_herring.motivo_aparente.lower()
        if any(term in motivo for term in conclusive_terms):
            findings.append(
                _finding(
                    "CR_RH_002",
                    "warning",
                    "Red herring descrito de forma conclusiva ou autoincriminatória demais.",
                    "red_herrings",
                    red_herring.personagem_id,
                )
            )
        if red_herring.documento_descarte not in document_codes:
            findings.append(
                _finding(
                    "CR_RH_003",
                    "warning",
                    "Suspeito alternativo sem função investigativa verificável por documento de descarte.",
                    "red_herrings",
                    f"{red_herring.personagem_id}: {red_herring.documento_descarte}",
                )
            )

    return findings


def _review_difficulty(blueprint: Blueprint, metrics: dict[str, Any]) -> list[CaseReviewFinding]:
    findings: list[CaseReviewFinding] = []
    summary = metrics["summary"]
    declared = summary["difficulty_declared"]
    estimated = summary["difficulty_estimated"]
    documents = int(summary["documents"])

    declared_index = DIFFICULTY_ORDER.index(declared)
    estimated_index = DIFFICULTY_ORDER.index(estimated)
    if estimated_index > declared_index + 1:
        findings.append(
            _finding(
                "CR_DIFF_001",
                "warning",
                "Dificuldade declarada pode estar subestimada.",
                "dificuldade",
                f"Declarada: {declared}; estimada: {estimated}.",
            )
        )
    elif declared_index > estimated_index + 1:
        findings.append(
            _finding(
                "CR_DIFF_002",
                "warning",
                "Dificuldade declarada pode estar superestimada.",
                "dificuldade",
                f"Declarada: {declared}; estimada: {estimated}.",
            )
        )

    minimum, maximum = DOCUMENT_RANGES[declared]
    if documents < minimum or (maximum is not None and documents > maximum):
        findings.append(
            _finding(
                "CR_DIFF_003",
                "warning",
                "Volume documental incompatível com a faixa editorial declarada.",
                "dificuldade",
                f"{declared}: {minimum}–{maximum or '+'} documentos; observado: {documents}.",
            )
        )

    return findings


def _status_for(findings: list[CaseReviewFinding], kernel_findings: list[CaseKernelFinding]) -> ReviewStatus:
    if any(finding.severity == "critical" for finding in findings):
        return "BLOCKED"
    editorial_warnings = [finding for finding in findings if finding.severity == "warning"]
    kernel_warnings = [finding for finding in kernel_findings if finding.severity == "warning"]
    if len(editorial_warnings) + len(kernel_warnings) >= 4:
        return "NEEDS_EDITORIAL_REVIEW"
    if editorial_warnings or kernel_warnings:
        return "READY_FOR_BASELINE"
    return "READY_FOR_PLAYTEST"


def review_case(blueprint: Blueprint) -> CaseReview:
    """Gera o Case Review estruturado para um blueprint já carregado."""
    kernel = extract_case_kernel(blueprint)
    kernel_findings = validate_case_kernel(kernel)
    metrics = analyze_playtest(blueprint)

    findings: list[CaseReviewFinding] = []
    findings.extend(_review_solvability(blueprint, kernel))
    findings.extend(_review_progression(blueprint, kernel))
    findings.extend(_review_red_herrings(blueprint))
    findings.extend(_review_difficulty(blueprint, metrics))

    return CaseReview(
        title=blueprint.titulo,
        difficulty_declared=_enum_value(blueprint.dificuldade),
        status=_status_for(findings, kernel_findings),
        kernel=kernel,
        kernel_findings=tuple(kernel_findings),
        findings=tuple(findings),
        playtest_metrics=metrics,
    )


def load_blueprint(path: str | Path) -> Blueprint:
    """Carrega um blueprint JSON em UTF-8."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Blueprint(**data)


def review_case_file(path: str | Path) -> CaseReview:
    """Carrega e revisa um blueprint JSON."""
    return review_case(load_blueprint(path))


def _severity_count(review: CaseReview, severity: str) -> int:
    return sum(1 for finding in review.findings if finding.severity == severity) + sum(
        1 for finding in review.kernel_findings if finding.severity == severity
    )


def _findings_by_section(review: CaseReview, section: str) -> list[CaseReviewFinding]:
    return [finding for finding in review.findings if finding.section == section]


def _format_findings(findings: list[CaseReviewFinding] | tuple[CaseReviewFinding, ...]) -> str:
    if not findings:
        return "- Nenhum finding específico."
    lines = []
    for finding in findings:
        detail = f" — {finding.detail}" if finding.detail else ""
        lines.append(f"- {finding.code} ({finding.severity}): {finding.message}{detail}")
    return "\n".join(lines)


def _format_kernel_findings(findings: tuple[CaseKernelFinding, ...]) -> str:
    if not findings:
        return "- Nenhum finding CK_* específico."
    return "\n".join(
        f"- {finding.code} ({finding.severity}): {finding.message}" for finding in findings
    )


def review_to_markdown(review: CaseReview) -> str:
    """Renderiza o Case Review em Markdown para leitura editorial."""
    kernel = review.kernel
    metrics = review.playtest_metrics["summary"]
    critical = _severity_count(review, "critical")
    warnings = _severity_count(review, "warning")

    envelope_lines = [
        f"- {envelope.id}: pergunta='{envelope.pergunta}' | resposta='{envelope.resposta_esperada}' | avanço='{envelope.criterio_avanco}'"
        for envelope in kernel.envelopes
    ] or ["- Nenhum envelope extraído."]
    evidence_lines = [
        f"- {evidence.id} ({evidence.envelope or 'sem envelope'}): {evidence.papel} — {evidence.descricao}"
        for evidence in kernel.evidencias_obrigatorias
    ] or ["- Nenhuma evidência obrigatória extraída."]
    red_herring_lines = [f"- {red_herring}" for red_herring in kernel.red_herrings] or [
        "- Nenhum red herring extraído."
    ]

    return "\n".join(
        [
            f"# Case Review — {review.title}",
            "## Resumo",
            f"- Dificuldade declarada: {review.difficulty_declared}",
            f"- Status: {review.status}",
            f"- Findings críticos: {critical}",
            f"- Warnings: {warnings}",
            "## Case Kernel",
            f"- Pergunta pública: {kernel.pergunta_publica}",
            f"- Conflito central: {kernel.conflito_central}",
            f"- Hipótese esperada no E1: {kernel.hipotese_e1}",
            f"- Recontextualização do E2: {kernel.recontextualizacao_e2}",
            f"- Motivação atual: {kernel.motivacao_atual}",
            "### Findings CK_*",
            _format_kernel_findings(review.kernel_findings),
            "### Envelopes extraídos",
            "\n".join(envelope_lines),
            "### Evidências obrigatórias extraídas",
            "\n".join(evidence_lines),
            "## Solvabilidade",
            _format_findings(_findings_by_section(review, "solvabilidade")),
            "## Progressão por envelope",
            _format_findings(_findings_by_section(review, "progressao")),
            "## Red herrings",
            "\n".join(red_herring_lines),
            _format_findings(_findings_by_section(review, "red_herrings")),
            "## Dificuldade",
            f"- Dificuldade declarada: {metrics['difficulty_declared']}",
            f"- Dificuldade estimada: {metrics['difficulty_estimated']}",
            f"- Documentos: {metrics['documents']}",
            f"- Contratos obrigatórios: {metrics['contracts']}",
            f"- Carga cognitiva: {metrics['cognitive_load']}",
            _format_findings(_findings_by_section(review, "dificuldade")),
            "## Prontidão para playtest",
            f"- Status final: {review.status}",
            "- Interpretação: relatório heurístico para revisão humana; playtest continua obrigatório.",
            "",
        ]
    )


def review_to_dict(review: CaseReview) -> dict[str, Any]:
    """Converte o relatório para JSON estruturado."""
    return asdict(review)


def review_to_json(review: CaseReview) -> str:
    """Renderiza o relatório em JSON estruturado."""
    return json.dumps(review_to_dict(review), ensure_ascii=False, indent=2)


def render_review(review: CaseReview, output_format: ReviewFormat = "markdown") -> str:
    """Renderiza o relatório no formato solicitado."""
    if output_format == "markdown":
        return review_to_markdown(review)
    if output_format == "json":
        return review_to_json(review)
    raise ValueError(f"Formato não suportado: {output_format}")


def write_review(review: CaseReview, output_path: str | Path, output_format: ReviewFormat) -> Path:
    """Grava o relatório renderizado em UTF-8."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_review(review, output_format), encoding="utf-8")
    return path

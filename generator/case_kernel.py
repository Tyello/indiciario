"""Extração e validação do Case Kernel do Indiciário.

O Case Kernel é uma camada analítica derivada do ``Blueprint`` atual. Ele não
altera o blueprint, não escreve arquivos e ainda não é obrigatório no contrato
JSON dos casos.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from re import sub
from unicodedata import normalize

try:  # Execução como pacote: python -m generator.case_kernel
    from .models import Blueprint, Dificuldade
except ImportError:  # Execução direta: python generator/case_kernel.py
    from models import Blueprint, Dificuldade  # type: ignore[no-redef]


@dataclass(frozen=True)
class EnvelopeKernel:
    """Pergunta, resposta e avanço esperados para um envelope."""

    id: str
    pergunta: str
    resposta_esperada: str
    funcao_narrativa: str
    criterio_avanco: str


@dataclass(frozen=True)
class EvidenceKernel:
    """Evidência obrigatória ou estruturante no núcleo investigativo."""

    id: str
    descricao: str
    papel: str
    envelope: str | None = None


@dataclass(frozen=True)
class CaseKernel:
    """DNA investigativo de um caso, derivado do blueprint."""

    case_id: str
    titulo: str
    dificuldade: str | None
    pergunta_publica: str
    conflito_central: str
    verdade_final: str
    hipotese_e1: str
    recontextualizacao_e2: str
    motivacao_atual: str
    envelopes: tuple[EnvelopeKernel, ...]
    evidencias_obrigatorias: tuple[EvidenceKernel, ...]
    red_herrings: tuple[str, ...]
    riscos: tuple[str, ...]


@dataclass(frozen=True)
class CaseKernelFinding:
    """Finding de validação não bloqueante do Case Kernel."""

    code: str
    severity: str
    message: str


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if value is None:
        return ""
    return str(value)


def _first_text(*values: object) -> str:
    for value in values:
        text = _enum_value(value).strip()
        if text:
            return text
    return ""


def _join_text(values: list[str] | tuple[str, ...], separator: str = " ") -> str:
    return separator.join(value.strip() for value in values if value and value.strip())


def _slugify(text: str) -> str:
    ascii_text = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    normalized = sub(r"[^a-zA-Z0-9]+", "-", ascii_text.strip().lower()).strip("-")
    return normalized or "case-kernel"


def _conflito_central_text(blueprint: Blueprint) -> str:
    conflito = blueprint.conflito_central
    return _join_text(
        [
            conflito.pergunta_publica,
            conflito.motivo_da_apuracao,
            conflito.risco_concreto,
            conflito.verdade_aparente,
        ]
    )


def _extract_e1_hypothesis(blueprint: Blueprint) -> str:
    contract_text = [
        contract.conclusao
        for contract in blueprint.contratos_evidencia
        if contract.fase == "E1" and contract.tipo == "hipotese_parcial"
    ]
    if contract_text:
        return _join_text(contract_text, " ")

    for objetivo in blueprint.objetivos_por_envelope:
        if objetivo.envelope == "E1":
            return objetivo.resposta_esperada
    return ""


def _extract_e2_recontextualization(blueprint: Blueprint) -> str:
    contract_text = [
        contract.conclusao
        for contract in blueprint.contratos_evidencia
        if contract.fase == "E2" and contract.tipo == "recontextualizacao"
    ]
    if contract_text:
        return _join_text(contract_text, " ")

    for objetivo in blueprint.objetivos_por_envelope:
        if objetivo.envelope == "E2":
            return objetivo.resposta_esperada
    return ""


def _extract_envelopes(blueprint: Blueprint) -> tuple[EnvelopeKernel, ...]:
    envelopes: list[EnvelopeKernel] = []
    for objetivo in blueprint.objetivos_por_envelope:
        funcao = _join_text(
            [
                objetivo.forma_diegetica_de_avanco,
                "Não precisa resolver ainda: " + "; ".join(objetivo.nao_precisa_resolver_ainda)
                if objetivo.nao_precisa_resolver_ainda
                else "",
            ]
        )
        envelopes.append(
            EnvelopeKernel(
                id=objetivo.envelope,
                pergunta=objetivo.pergunta_diegetica,
                resposta_esperada=objetivo.resposta_esperada,
                funcao_narrativa=funcao,
                criterio_avanco=objetivo.criterio_de_avanco,
            )
        )
    return tuple(envelopes)


def _extract_required_evidence(blueprint: Blueprint) -> tuple[EvidenceKernel, ...]:
    evidence: list[EvidenceKernel] = []
    for contract in blueprint.contratos_evidencia:
        if not contract.obrigatoria_para_avanco:
            continue
        references = [contract.prova_principal or "", contract.confirmacao_independente or ""]
        suffix = f" Provas: {', '.join(ref for ref in references if ref)}." if any(references) else ""
        evidence.append(
            EvidenceKernel(
                id=contract.id,
                descricao=f"{contract.conclusao}{suffix}",
                papel=contract.tipo,
                envelope=contract.fase,
            )
        )

    if evidence:
        return tuple(evidence)

    return tuple(
        EvidenceKernel(
            id=pilar.nome,
            descricao=f"{pilar.documento_principal} confirmado por {pilar.confirmacao}",
            papel="pilar_validacao",
            envelope=None,
        )
        for pilar in blueprint.pilares_validacao
    )


def _extract_red_herrings(blueprint: Blueprint) -> tuple[str, ...]:
    return tuple(
        _join_text(
            [
                f"Personagem {red_herring.personagem_id}: {red_herring.motivo_aparente}",
                f"Descarte: {red_herring.como_descartar}",
            ]
        )
        for red_herring in blueprint.red_herrings
    )


def _extract_risks(blueprint: Blueprint) -> tuple[str, ...]:
    risks: list[str] = []
    for contract in blueprint.contratos_evidencia:
        if contract.risco_ambiguidade in {"medio_alto", "alto"}:
            risks.append(
                f"{contract.id}: risco de ambiguidade {contract.risco_ambiguidade} em {contract.fase}."
            )
    for clue in blueprint.matriz_pistas:
        if clue.risco_ambiguidade in {"medio_alto", "alto"}:
            risks.append(
                f"{clue.documento}: risco de ambiguidade {clue.risco_ambiguidade} — {clue.descricao}"
            )
    return tuple(risks)


def extract_case_kernel(blueprint: Blueprint) -> CaseKernel:
    """Deriva o Case Kernel a partir do blueprint atual, sem mutação.

    Campos ausentes ou não representados diretamente no blueprint são tratados de
    forma conservadora, com string vazia ou tupla vazia, para que a validação gere
    findings sem inventar narrativa.
    """

    pergunta_publica = _first_text(
        blueprint.conflito_central.pergunta_publica,
        blueprint.guia_operacional.pergunta_publica,
        blueprint.premissa,
    )
    verdade_final = _first_text(
        blueprint.verdade_real,
        blueprint.conflito_central.verdade_real_resumida,
        _join_text(blueprint.guia_operacional.solucao_em_5_frases),
    )

    return CaseKernel(
        case_id=_slugify(blueprint.titulo),
        titulo=blueprint.titulo,
        dificuldade=_enum_value(blueprint.dificuldade),
        pergunta_publica=pergunta_publica,
        conflito_central=_conflito_central_text(blueprint),
        verdade_final=verdade_final,
        hipotese_e1=_extract_e1_hypothesis(blueprint),
        recontextualizacao_e2=_extract_e2_recontextualization(blueprint),
        motivacao_atual=blueprint.motivacao,
        envelopes=_extract_envelopes(blueprint),
        evidencias_obrigatorias=_extract_required_evidence(blueprint),
        red_herrings=_extract_red_herrings(blueprint),
        riscos=_extract_risks(blueprint),
    )


def _is_missing_or_weak_question(text: str) -> bool:
    clean = text.strip()
    return not clean or len(clean) < 24 or "?" not in clean


def _difficulty_requires_red_herring(dificuldade: str | None) -> bool:
    order = {
        Dificuldade.INICIANTE.value: 0,
        Dificuldade.INTERMEDIARIO.value: 1,
        Dificuldade.AVANCADO.value: 2,
        Dificuldade.ESPECIALISTA.value: 3,
        Dificuldade.MESTRE.value: 4,
    }
    return order.get((dificuldade or "").lower(), 0) >= 1


def _e1_asks_final_solution(kernel: CaseKernel) -> bool:
    e1_text = " ".join(
        [
            kernel.hipotese_e1,
            *(
                f"{envelope.pergunta} {envelope.resposta_esperada}"
                for envelope in kernel.envelopes
                if envelope.id == "E1"
            ),
        ]
    ).lower()
    final_terms = ["solução final", "executor", "planejador", "beneficiário", "beneficiario", "culpado"]
    return any(term in e1_text for term in final_terms) and not any(
        guard in e1_text
        for guard in [
            "não fecha",
            "sem exigir culpado",
            "sem exigir ainda culpado",
            "não precisa resolver",
            "não fecha motivo",
            "não fecha benefício",
            "não fecha beneficio",
            "acusação final",
        ]
    )


def validate_case_kernel(kernel: CaseKernel) -> list[CaseKernelFinding]:
    """Valida o Case Kernel com findings analíticos não bloqueantes."""

    findings: list[CaseKernelFinding] = []

    def warning(code: str, message: str) -> None:
        findings.append(CaseKernelFinding(code=code, severity="warning", message=message))

    if _is_missing_or_weak_question(kernel.pergunta_publica):
        warning("CK_001", "Pergunta pública ausente ou fraca.")
    if not kernel.conflito_central.strip():
        warning("CK_002", "Conflito central ausente.")
    if not kernel.verdade_final.strip():
        warning("CK_003", "Verdade final ausente.")
    if not kernel.hipotese_e1.strip():
        warning("CK_004", "Hipótese parcial do E1 ausente.")
    if len(kernel.envelopes) >= 2 and not kernel.recontextualizacao_e2.strip():
        warning("CK_005", "Recontextualização do E2 ausente em caso com 2+ envelopes.")
    if not kernel.motivacao_atual.strip():
        warning("CK_006", "Motivação atual ausente.")

    for envelope in kernel.envelopes:
        missing_parts = [
            label
            for label, value in [
                ("pergunta", envelope.pergunta),
                ("resposta", envelope.resposta_esperada),
                ("critério de avanço", envelope.criterio_avanco),
            ]
            if not value.strip()
        ]
        if missing_parts:
            warning("CK_007", f"Envelope {envelope.id} sem {', '.join(missing_parts)}.")

    if not kernel.evidencias_obrigatorias:
        warning("CK_008", "Evidências obrigatórias ausentes.")
    if _difficulty_requires_red_herring(kernel.dificuldade) and not kernel.red_herrings:
        warning("CK_009", "Red herrings ausentes em dificuldade intermediária ou maior.")
    if _e1_asks_final_solution(kernel):
        warning("CK_010", "E1 parece pedir solução final em vez de hipótese parcial.")

    return findings

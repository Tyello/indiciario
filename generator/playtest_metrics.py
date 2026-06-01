"""Métricas heurísticas de playtest para blueprints do Indiciário.

Este módulo não chama LLM nem decide se um caso é bom ou ruim. Ele apenas calcula
sinais analíticos de risco de experiência investigativa.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from generator.models import Blueprint, Dificuldade, PapelPersonagem

DIFFICULTY_ORDER = [
    Dificuldade.INICIANTE.value,
    Dificuldade.INTERMEDIARIO.value,
    Dificuldade.AVANCADO.value,
    Dificuldade.ESPECIALISTA.value,
    Dificuldade.MESTRE.value,
]

DOCUMENT_RANGES: dict[str, tuple[int, int | None]] = {
    Dificuldade.INICIANTE.value: (8, 10),
    Dificuldade.INTERMEDIARIO.value: (11, 18),
    Dificuldade.AVANCADO.value: (19, 24),
    Dificuldade.ESPECIALISTA.value: (25, 30),
    Dificuldade.MESTRE.value: (31, None),
}

CONTRACT_LIMITS: dict[str, int] = {
    Dificuldade.INICIANTE.value: 2,
    Dificuldade.INTERMEDIARIO.value: 5,
    Dificuldade.AVANCADO.value: 8,
    Dificuldade.ESPECIALISTA.value: 10,
    Dificuldade.MESTRE.value: 12,
}

SUSPECT_LIMITS: dict[str, int] = {
    Dificuldade.INICIANTE.value: 4,
    Dificuldade.INTERMEDIARIO.value: 6,
    Dificuldade.AVANCADO.value: 7,
    Dificuldade.ESPECIALISTA.value: 8,
    Dificuldade.MESTRE.value: 10,
}


def _difficulty_value(blueprint: Blueprint) -> str:
    return (
        blueprint.dificuldade.value
        if hasattr(blueprint.dificuldade, "value")
        else str(blueprint.dificuldade)
    )


def _envelope_number(envelope: str) -> int:
    text = str(envelope)
    if text.startswith("E") and text[1:].isdigit():
        return int(text[1:])
    return 10**9


def count_required_contracts(blueprint: Blueprint) -> int:
    """Conta contratos obrigatórios para avanço."""
    return sum(
        1
        for contrato in blueprint.contratos_evidencia
        if contrato.obrigatoria_para_avanco
    )


def infer_suspects(blueprint: Blueprint) -> int | None:
    """Infere suspeitos sem criar nova modelagem de elenco.

    A heurística usa personagens envolvidos no jogo investigativo: todos com
    suspeita aparente e papel diferente de narrador. Se não houver dados mínimos,
    retorna ``None`` para evitar falso diagnóstico.
    """
    if not blueprint.personagens:
        return None
    suspects = [
        personagem
        for personagem in blueprint.personagens
        if personagem.papel != PapelPersonagem.NARRADOR
        and personagem.suspeita_aparente.strip()
    ]
    return len(suspects) if suspects else None


def infer_red_herrings(blueprint: Blueprint) -> int | None:
    """Infere red herrings a partir de campos explícitos ou contratos de descarte."""
    if blueprint.red_herrings:
        return len(blueprint.red_herrings)
    contracts = [
        contrato
        for contrato in blueprint.contratos_evidencia
        if contrato.tipo == "descarte_alternativa" or contrato.descarta_alternativas
    ]
    if contracts:
        return len(contracts)
    return None


def estimate_minutes(blueprint: Blueprint) -> int:
    """Estima duração por documentos, contratos obrigatórios e envelopes extras."""
    documents = len(blueprint.documentos)
    contracts = count_required_contracts(blueprint)
    envelopes = len({doc.envelope for doc in blueprint.documentos})
    return round((documents * 4) + (contracts * 3) + (max(envelopes - 1, 0) * 5))


def cognitive_load(documents: int, contracts: int) -> str:
    """Classifica carga cognitiva em low, medium ou high."""
    score = 0 if documents <= 10 else 1 if documents <= 18 else 2
    if contracts >= 8:
        score = min(score + 1, 2)
    elif contracts <= 1 and documents <= 12:
        score = max(score - 1, 0)
    return ["low", "medium", "high"][score]


def estimate_difficulty(documents: int, contracts: int, suspects: int | None) -> str:
    """Estima dificuldade percebida por faixas simples e coerentes."""
    if documents > 30 or contracts > 12:
        return Dificuldade.MESTRE.value

    scores = [
        0 if documents <= 10 else 1 if documents <= 18 else 2 if documents <= 24 else 3,
        0 if contracts <= 2 else 1 if contracts <= 5 else 2 if contracts <= 8 else 3,
    ]
    if suspects is not None:
        scores.append(
            0 if suspects <= 4 else 1 if suspects <= 6 else 2 if suspects <= 8 else 3
        )
    return DIFFICULTY_ORDER[max(scores)]


def _warning(code: str, message: str, detail: str = "") -> dict[str, str]:
    data = {"code": code, "severity": "warning", "message": message}
    if detail:
        data["detail"] = detail
    return data


def _document_warnings(declared: str, documents: int) -> list[dict[str, str]]:
    minimum, maximum = DOCUMENT_RANGES[declared]
    warnings: list[dict[str, str]] = []
    if maximum is not None and documents > maximum:
        warnings.append(
            _warning(
                "PT_001",
                "Documentos acima do recomendado para a dificuldade declarada.",
                f"{declared}: recomendado até {maximum}; observado: {documents}.",
            )
        )
    if documents < minimum:
        warnings.append(
            _warning(
                "PT_002",
                "Documentos abaixo do recomendado para a dificuldade declarada.",
                f"{declared}: recomendado a partir de {minimum}; observado: {documents}.",
            )
        )
    return warnings


def _envelope_balance_warnings(blueprint: Blueprint) -> list[dict[str, str]]:
    total = len(blueprint.documentos)
    if total == 0:
        return []
    counts = Counter(doc.envelope for doc in blueprint.documentos)
    envelope, amount = max(counts.items(), key=lambda item: item[1])
    if len(counts) > 1 and amount / total > 0.75:
        return [
            _warning(
                "PT_004",
                "Envelope desbalanceado.",
                f"{envelope} concentra {amount} de {total} documentos.",
            )
        ]
    return []


def _time_warning(
    declared_minutes: int, estimated_minutes: int
) -> list[dict[str, str]]:
    if declared_minutes <= 0:
        return []
    difference = abs(estimated_minutes - declared_minutes)
    incompatible = difference >= 30 and (
        estimated_minutes >= declared_minutes * 1.5
        or estimated_minutes <= declared_minutes * 0.55
    )
    if not incompatible:
        return []
    return [
        _warning(
            "PT_008",
            "Tempo estimado incompatível com o tempo declarado.",
            f"Declarado: {declared_minutes} min; estimado: {estimated_minutes} min.",
        )
    ]


def _difficulty_warning(declared: str, estimated: str) -> list[dict[str, str]]:
    distance = abs(DIFFICULTY_ORDER.index(declared) - DIFFICULTY_ORDER.index(estimated))
    if distance < 2:
        return []
    return [
        _warning(
            "PT_009",
            "Dificuldade declarada diverge muito da dificuldade estimada.",
            f"Declarada: {declared}; estimada: {estimated}.",
        )
    ]


def analyze_playtest(
    blueprint: Blueprint, graph_report: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Analisa heurísticas de experiência investigativa e retorna JSON serializável."""
    del graph_report
    declared = _difficulty_value(blueprint)
    documents = len(blueprint.documentos)
    envelopes = len({doc.envelope for doc in blueprint.documentos})
    contracts = count_required_contracts(blueprint)
    suspects = infer_suspects(blueprint)
    red_herrings = infer_red_herrings(blueprint)
    estimated_minutes = estimate_minutes(blueprint)
    load = cognitive_load(documents, contracts)
    estimated_difficulty = estimate_difficulty(documents, contracts, suspects)

    warnings: list[dict[str, str]] = []
    warnings.extend(_document_warnings(declared, documents))

    if suspects is not None and suspects > SUSPECT_LIMITS[declared]:
        warnings.append(
            _warning(
                "PT_003",
                "Suspeitos acima do recomendado para a dificuldade declarada.",
                f"{declared}: recomendado até {SUSPECT_LIMITS[declared]}; observado: {suspects}.",
            )
        )

    warnings.extend(_envelope_balance_warnings(blueprint))

    if red_herrings is not None:
        if red_herrings == 0:
            warnings.append(_warning("PT_005", "Nenhum red herring identificado."))
        elif red_herrings > contracts:
            warnings.append(
                _warning(
                    "PT_006",
                    "Red herrings excessivos em relação aos contratos obrigatórios.",
                    f"Red herrings: {red_herrings}; contratos obrigatórios: {contracts}.",
                )
            )

    if contracts > CONTRACT_LIMITS[declared]:
        warnings.append(
            _warning(
                "PT_007",
                "Contratos obrigatórios excessivos para a dificuldade declarada.",
                f"{declared}: recomendado até {CONTRACT_LIMITS[declared]}; observado: {contracts}.",
            )
        )

    warnings.extend(_time_warning(blueprint.tempo_estimado_min, estimated_minutes))
    warnings.extend(_difficulty_warning(declared, estimated_difficulty))

    return {
        "status": "warnings" if warnings else "ok",
        "summary": {
            "difficulty_declared": declared,
            "difficulty_estimated": estimated_difficulty,
            "documents": documents,
            "envelopes": envelopes,
            "contracts": contracts,
            "suspects": suspects,
            "red_herrings": red_herrings,
            "estimated_minutes": estimated_minutes,
            "cognitive_load": load,
        },
        "issues": [],
        "warnings": warnings,
    }


def write_playtest_report(report: dict[str, Any], output_path: Path) -> Path:
    """Escreve playtest_report.json em UTF-8."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path

"""Construção e renderização do guia confidencial do facilitador."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .models import Blueprint, ContratoEvidencia, DicaContextual, Documento
from .renderer import renderizar_documento


def _fase_sort_key(fase: str) -> tuple[int, str]:
    if fase == "final":
        return (10_000, fase)
    if fase.startswith("E") and fase[1:].isdigit():
        return (int(fase[1:]), fase)
    return (9_999, fase)


def _contrato_context(contrato: ContratoEvidencia) -> dict[str, Any]:
    return {
        "id": contrato.id,
        "fase": contrato.fase,
        "conclusao": contrato.conclusao,
        "tipo": contrato.tipo,
        "prova_principal": contrato.prova_principal or "—",
        "confirmacao_independente": contrato.confirmacao_independente or "—",
        "acao_esperada_jogador": contrato.acao_esperada_jogador or "—",
        "obrigatoria_para_avanco": "Sim" if contrato.obrigatoria_para_avanco else "Não",
    }


def _documento_context(documento: Documento) -> dict[str, Any]:
    return {
        "codigo": documento.codigo,
        "titulo": documento.titulo,
        "tipo": documento.tipo.value,
        "envelope": documento.envelope,
    }


def _dica_context(dica: DicaContextual) -> dict[str, Any]:
    return {
        "id": dica.id,
        "categoria": dica.categoria,
        "fase": dica.fase,
        "titulo": dica.titulo or dica.id,
        "condicao_uso": dica.condicao_uso,
        "texto": dica.texto,
        "nivel": dica.nivel,
        "contratos_relacionados": ", ".join(dica.contratos_relacionados) or "—",
        "documentos_relacionados": ", ".join(dica.documentos_relacionados) or "—",
    }


def _contratos_por_fase(contratos: list[ContratoEvidencia]) -> list[dict[str, Any]]:
    agrupados: dict[str, list[ContratoEvidencia]] = defaultdict(list)
    for contrato in contratos:
        agrupados[contrato.fase].append(contrato)
    return [
        {
            "fase": fase,
            "contratos": [_contrato_context(contrato) for contrato in sorted(itens, key=lambda c: c.id)],
        }
        for fase, itens in sorted(agrupados.items(), key=lambda item: _fase_sort_key(item[0]))
    ]


def _dicas_por_fase_categoria(dicas: list[DicaContextual]) -> list[dict[str, Any]]:
    por_fase: dict[str, dict[str, list[DicaContextual]]] = defaultdict(lambda: defaultdict(list))
    for dica in dicas:
        por_fase[dica.fase][dica.categoria].append(dica)

    fases: list[dict[str, Any]] = []
    for fase, categorias in sorted(por_fase.items(), key=lambda item: _fase_sort_key(item[0])):
        fases.append({
            "fase": fase,
            "categorias": [
                {
                    "categoria": categoria,
                    "dicas": [_dica_context(dica) for dica in sorted(itens, key=lambda d: d.id)],
                }
                for categoria, itens in sorted(categorias.items())
            ],
        })
    return fases


def _criterios_avanco(blueprint: Blueprint) -> list[dict[str, Any]]:
    fases = sorted({doc.envelope for doc in blueprint.documentos}, key=lambda fase: _fase_sort_key(fase))
    criterios: list[dict[str, Any]] = []
    for fase in fases:
        obrigatorios = [
            contrato for contrato in blueprint.contratos_evidencia
            if contrato.fase == fase and contrato.obrigatoria_para_avanco
        ]
        criterios.append({
            "fase": fase,
            "criterio": (
                "Liberar o próximo envelope quando o grupo formular as conclusões obrigatórias desta fase "
                "com prova principal e confirmação independente."
            ),
            "contratos": [_contrato_context(contrato) for contrato in sorted(obrigatorios, key=lambda c: c.id)],
            "sem_contratos": not obrigatorios,
        })
    return criterios


def build_facilitator_context(blueprint: Blueprint, graph_report: dict[str, Any] | None = None) -> dict[str, Any]:
    """Monta o contexto usado pelo template do guia do facilitador."""
    documentos_por_envelope: dict[str, list[Documento]] = defaultdict(list)
    for documento in blueprint.documentos:
        documentos_por_envelope[documento.envelope].append(documento)

    graph_status = "não informado"
    graph_summary = "Relatório de grafo não fornecido para esta renderização."
    if graph_report:
        graph_status = str(graph_report.get("status", "não informado"))
        summary = graph_report.get("summary", {})
        graph_summary = ", ".join(f"{chave}: {valor}" for chave, valor in summary.items()) or graph_summary

    return {
        "CASE_TITLE": blueprint.titulo,
        "CASE_SUBTITLE": blueprint.subtitulo,
        "PREMISSA": blueprint.premissa,
        "VERDADE_REAL": blueprint.verdade_real,
        "DIFICULDADE": blueprint.dificuldade.value,
        "TEMPO_ESTIMADO": blueprint.tempo_estimado_min,
        "NUMERO_JOGADORES": blueprint.numero_jogadores,
        "TOTAL_ENVELOPES": blueprint.formato_envelopes,
        "OBJETIVO_JOGADORES": blueprint.erro_que_permite_descobrir,
        "GABARITO_RESUMIDO": (
            f"Executor: {blueprint.executor_id}; planejador: {blueprint.planejador_id}; "
            f"beneficiário: {blueprint.beneficiario_id}. Motivação: {blueprint.motivacao}."
        ),
        "METODO_OCULTACAO": blueprint.metodo_ocultacao,
        "GRAPH_STATUS": graph_status,
        "GRAPH_SUMMARY": graph_summary,
        "DOCUMENTOS_POR_ENVELOPE": [
            {
                "envelope": envelope,
                "documentos": [_documento_context(doc) for doc in sorted(documentos, key=lambda d: d.codigo)],
            }
            for envelope, documentos in sorted(documentos_por_envelope.items(), key=lambda item: _fase_sort_key(item[0]))
        ],
        "CRITERIOS_AVANCO": _criterios_avanco(blueprint),
        "CONTRATOS_POR_FASE": _contratos_por_fase(blueprint.contratos_evidencia),
        "DICAS_POR_FASE": _dicas_por_fase_categoria(blueprint.dicas_contextuais),
        "SEM_DICAS_CONTEXTUAIS": not blueprint.dicas_contextuais,
    }


def render_facilitator_guide(
    blueprint: Blueprint,
    output_path: Path,
    graph_report: dict[str, Any] | None = None,
    strict: bool = True,
) -> Path:
    """Renderiza o guia do facilitador usando o renderer oficial do projeto."""
    return renderizar_documento(
        "facilitator_guide.html",
        build_facilitator_context(blueprint, graph_report=graph_report),
        output_path,
        strict=strict,
    )

"""Construção e renderização do guia confidencial do facilitador."""

from __future__ import annotations

from collections import defaultdict
import re
from pathlib import Path
from typing import Any

from .models import (
    Blueprint,
    ContratoEvidencia,
    DicaContextual,
    Documento,
    EventoLinha,
    RedHerring,
)
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


def _evento_context(evento: EventoLinha) -> dict[str, Any]:
    return {
        "data_hora": evento.data_hora,
        "evento": evento.evento,
        "personagem_id": evento.personagem_id,
        "documento_prova": evento.documento_prova,
        "confirmacao_independente": evento.confirmacao_independente or "—",
    }


def _red_herring_context(red_herring: RedHerring) -> dict[str, Any]:
    return {
        "personagem_id": red_herring.personagem_id,
        "motivo_aparente": red_herring.motivo_aparente,
        "como_descartar": red_herring.como_descartar,
        "documento_descarte": red_herring.documento_descarte,
        "categoria": red_herring.categoria,
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


def _strip_html(texto: str) -> str:
    return re.sub(r"<[^>]+>", " ", texto).replace("  ", " ").strip()


def _pergunta_publica(blueprint: Blueprint) -> str:
    for documento in blueprint.documentos:
        if documento.envelope == "E1" and documento.codigo == "E1-01":
            corpo = _strip_html(str(documento.conteudo.get("CORPO_CARTA", "")))
            marcador = "por que "
            inicio = corpo.lower().find(marcador)
            if inicio >= 0:
                fim = corpo.find("?", inicio)
                if fim >= 0:
                    return corpo[inicio:fim + 1]
    return blueprint.premissa


def _texto_entre(texto: str, inicio: str, fim: str | None = None) -> str:
    if inicio not in texto:
        return ""
    trecho = texto.split(inicio, 1)[1]
    if fim and fim in trecho:
        trecho = trecho.split(fim, 1)[0]
    return trecho.strip()


def _lista_frases(texto: str) -> list[dict[str, str]]:
    partes = [parte.strip(" .") for parte in texto.split(";") if parte.strip(" .")]
    return [{"texto": f"{parte}."} for parte in partes]


def _conclusoes_por_prefixo(blueprint: Blueprint, fase: str, prefixos: tuple[str, ...]) -> list[dict[str, str]]:
    conclusoes: list[dict[str, str]] = []
    for contrato in blueprint.contratos_evidencia:
        if contrato.fase == fase and contrato.id.startswith(prefixos):
            conclusoes.append({"id": contrato.id, "texto": contrato.conclusao})
    return conclusoes


def _guia_operacional_context(blueprint: Blueprint) -> dict[str, Any]:
    observacoes = blueprint.observacoes_producao or ""
    solucao = _texto_entre(observacoes, "solução em 5 frases — ", " Linha do tempo aparente:")
    linha_aparente = _texto_entre(observacoes, "Linha do tempo aparente: ", " Linha do tempo real:")
    linha_real = _texto_entre(observacoes, "Linha do tempo real: ", " Abrir E2")
    liberar_e2 = _texto_entre(observacoes, "Abrir E2 quando ", " Resposta esperada do E2:")
    resposta_e2 = _texto_entre(observacoes, "Resposta esperada do E2: ", " Caio preservou")

    e1_obrigatorios = [
        {"id": contrato.id, "texto": contrato.conclusao}
        for contrato in blueprint.contratos_evidencia
        if contrato.fase == "E1" and contrato.obrigatoria_para_avanco
    ]

    return {
        "pergunta_publica": _pergunta_publica(blueprint),
        "resposta_e1": e1_obrigatorios,
        "quando_liberar_e2": liberar_e2 or "o grupo formular uma resposta parcial sustentada pelas conclusões obrigatórias do E1.",
        "o_que_muda_e2": _conclusoes_por_prefixo(blueprint, "E2", ("C-E2",)),
        "solucao_5_frases": _lista_frases(solucao) or [{"texto": blueprint.verdade_real}],
        "linha_aparente_resumo": linha_aparente or "Ver tabela de linha do tempo aparente.",
        "linha_real_resumo": linha_real or "Ver tabela de linha do tempo real.",
        "resposta_e2": resposta_e2 or "Ver contratos obrigatórios do E2.",
    }


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
        "CADEIA_CAUSAL": [{"item": item} for item in blueprint.cadeia_causal],
        "LINHA_TEMPO_APARENTE": [_evento_context(evento) for evento in blueprint.linha_tempo_percebida],
        "LINHA_TEMPO_REAL": [_evento_context(evento) for evento in blueprint.linha_tempo_real],
        "RED_HERRINGS": [_red_herring_context(item) for item in blueprint.red_herrings],
        "GUIA_OPERACIONAL": _guia_operacional_context(blueprint),
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

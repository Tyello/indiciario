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
    """Retorna a pergunta pública estruturada do blueprint."""

    return blueprint.conflito_central.pergunta_publica


def _contratos_contexto(
    blueprint: Blueprint,
    *,
    fase: str | None = None,
    prefixos: tuple[str, ...] = (),
    obrigatorios: bool | None = None,
) -> list[dict[str, str]]:
    contratos: list[dict[str, str]] = []
    for contrato in blueprint.contratos_evidencia:
        if fase is not None and contrato.fase != fase:
            continue
        if prefixos and not contrato.id.startswith(prefixos):
            continue
        if obrigatorios is not None and contrato.obrigatoria_para_avanco is not obrigatorios:
            continue
        contratos.append({"id": contrato.id, "texto": contrato.conclusao})
    return contratos


def _solucao_em_frases(blueprint: Blueprint) -> list[dict[str, str]]:
    """Monta síntese operacional a partir do guia estruturado."""

    return [{"texto": frase} for frase in blueprint.guia_operacional.solucao_em_5_frases]


def _resumo_linha_tempo(eventos: list[EventoLinha], fallback: str) -> str:
    if not eventos:
        return fallback
    return " ".join(f"{evento.data_hora}: {evento.evento}" for evento in eventos[:3])


def _objetivo_envelope_context(objetivo: Any) -> dict[str, Any]:
    return {
        "envelope": objetivo.envelope,
        "pergunta_diegetica": objetivo.pergunta_diegetica,
        "resposta_esperada": objetivo.resposta_esperada,
        "nao_precisa_resolver_ainda": [{"item": item} for item in objetivo.nao_precisa_resolver_ainda],
        "criterio_de_avanco": objetivo.criterio_de_avanco,
        "forma_diegetica_de_avanco": objetivo.forma_diegetica_de_avanco,
        "documentos_minimos": [{"codigo": codigo} for codigo in objetivo.documentos_minimos],
    }


def _guia_operacional_context(blueprint: Blueprint) -> dict[str, Any]:
    """Monta o guia operacional a partir dos campos estruturados do blueprint."""

    objetivos = sorted(blueprint.objetivos_por_envelope, key=lambda objetivo: _fase_sort_key(objetivo.envelope))
    objetivos_context = [_objetivo_envelope_context(objetivo) for objetivo in objetivos]
    respostas_por_envelope = {item["envelope"]: item for item in objetivos_context}
    e1 = respostas_por_envelope.get("E1")
    e2 = respostas_por_envelope.get("E2")

    return {
        "pergunta_publica": blueprint.guia_operacional.pergunta_publica,
        "objetivos_por_envelope": objetivos_context,
        "resposta_e1": ([{"id": "E1", "texto": e1["resposta_esperada"]}] if e1 else []),
        "quando_liberar_e2": e1["criterio_de_avanco"] if e1 else "Ver objetivo estruturado do envelope atual.",
        "o_que_muda_e2": ([{"id": "E2", "texto": e2["pergunta_diegetica"]}] if e2 else []),
        "solucao_5_frases": _solucao_em_frases(blueprint),
        "linha_aparente_resumo": blueprint.guia_operacional.linha_tempo_aparente_resumo,
        "linha_real_resumo": blueprint.guia_operacional.linha_tempo_real_resumo,
        "resposta_e2": e2["resposta_esperada"] if e2 else "Ver objetivo estruturado do envelope final.",
        "red_herrings_e_descartes": [{"item": item} for item in blueprint.guia_operacional.red_herrings_e_descartes],
        "quando_usar_dicas": [{"item": item} for item in blueprint.guia_operacional.quando_usar_dicas],
    }


def _criterios_avanco(blueprint: Blueprint) -> list[dict[str, Any]]:
    criterios: list[dict[str, Any]] = []
    for objetivo in sorted(blueprint.objetivos_por_envelope, key=lambda item: _fase_sort_key(item.envelope)):
        obrigatorios = [
            contrato for contrato in blueprint.contratos_evidencia
            if contrato.fase == objetivo.envelope and contrato.obrigatoria_para_avanco
        ]
        criterios.append({
            "fase": objetivo.envelope,
            "criterio": objetivo.criterio_de_avanco,
            "forma_diegetica_de_avanco": objetivo.forma_diegetica_de_avanco,
            "resposta_esperada": objetivo.resposta_esperada,
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

    guia_operacional = _guia_operacional_context(blueprint)

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
        "GUIA_OPERACIONAL": guia_operacional,
        "pergunta_publica": guia_operacional["pergunta_publica"],
        "quando_liberar_e2": guia_operacional["quando_liberar_e2"],
        "resposta_e2": guia_operacional["resposta_e2"],
        "linha_aparente_resumo": guia_operacional["linha_aparente_resumo"],
        "linha_real_resumo": guia_operacional["linha_real_resumo"],
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

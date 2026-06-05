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
    """Extrai a pergunta pública do documento de abertura, com fallback seguro.

    O guia operacional não deve depender de texto livre em `observacoes_producao`.
    A pergunta pública vem do documento diegético de abertura porque é exatamente o
    que o facilitador e os jogadores enxergam como missão narrativa.
    """

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
    """Monta síntese operacional a partir de campos estruturados do blueprint."""

    contratos_e1 = _contratos_contexto(blueprint, fase="E1", obrigatorios=True)
    contratos_final = _contratos_contexto(blueprint, fase="final", obrigatorios=True)
    resposta_e1 = contratos_e1[-1]["texto"] if contratos_e1 else blueprint.erro_que_permite_descobrir
    solucao_final = contratos_final[-1]["texto"] if contratos_final else blueprint.verdade_real

    frases = [
        f"Pergunta pública: {_pergunta_publica(blueprint)}",
        f"Resposta esperada do E1: {resposta_e1}",
        f"O que muda no E2: {blueprint.motivacao}",
        f"Solução final: {solucao_final}",
        "Fechamento: os suspeitos fortes devem cair por janela, meio, oportunidade ou qualidade do testemunho.",
    ]
    return [{"texto": frase} for frase in frases]


def _resumo_linha_tempo(eventos: list[EventoLinha], fallback: str) -> str:
    if not eventos:
        return fallback
    return " ".join(f"{evento.data_hora}: {evento.evento}" for evento in eventos[:3])


def _guia_operacional_context(blueprint: Blueprint) -> dict[str, Any]:
    """Monta o guia operacional sem parsear observações textuais livres.

    O contexto deriva de campos estruturados: contratos, linhas do tempo, motivação,
    verdade real e red herrings. Isso evita que o guia quebre quando a redação de
    `observacoes_producao` mudar.
    """

    e1_obrigatorios = _contratos_contexto(blueprint, fase="E1", obrigatorios=True)
    e2_obrigatorios = _contratos_contexto(blueprint, fase="E2", obrigatorios=True)
    e2_recontexto = _contratos_contexto(blueprint, fase="E2", prefixos=("C-E2",))

    return {
        "pergunta_publica": _pergunta_publica(blueprint),
        "resposta_e1": e1_obrigatorios,
        "quando_liberar_e2": (
            "o grupo formular uma resposta parcial sustentada pelos contratos obrigatórios do E1, "
            "sem exigir autoria final antes da remessa complementar."
        ),
        "o_que_muda_e2": e2_recontexto,
        "solucao_5_frases": _solucao_em_frases(blueprint),
        "linha_aparente_resumo": _resumo_linha_tempo(
            blueprint.linha_tempo_percebida,
            "Ver tabela de linha do tempo aparente.",
        ),
        "linha_real_resumo": _resumo_linha_tempo(
            blueprint.linha_tempo_real,
            "Ver tabela de linha do tempo real.",
        ),
        "resposta_e2": (
            e2_obrigatorios[-1]["texto"]
            if e2_obrigatorios
            else "Ver contratos obrigatórios do E2."
        ),
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

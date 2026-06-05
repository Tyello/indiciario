"""
Validador de blueprint do Indiciário.

Mantém a interface pública descrita em AGENTS.md:
- BlueprintValidator(blueprint, strict=False).validar() -> ResultadoValidacao
- CLI: python -m generator.validator <arquivo.json> [--strict] [--json]
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

try:  # Execução como pacote: python -m generator.validator
    from .models import (
        Blueprint,
        Intensidade,
        ModoValidacao,
        PapelPersonagem,
        SaltoFinanceiro,
        TipoDocumento,
    )
except ImportError:  # Execução direta: python generator/validator.py
    from models import (  # type: ignore[no-redef]
        Blueprint,
        Intensidade,
        ModoValidacao,
        PapelPersonagem,
        SaltoFinanceiro,
        TipoDocumento,
    )

try:  # Execução como pacote: python -m generator.validator
    from .schema_loader import get_schema_for_type, load_all_schemas
except ImportError:  # Execução direta: python generator/validator.py
    from schema_loader import get_schema_for_type, load_all_schemas  # type: ignore[no-redef]

try:  # Execução como pacote: python -m generator.validator
    from .clue_graph import analyze_clue_graph, build_clue_graph
    from .playtest_metrics import analyze_playtest
except ImportError:  # Execução direta: python generator/validator.py
    from clue_graph import analyze_clue_graph, build_clue_graph  # type: ignore[no-redef]
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from generator.playtest_metrics import analyze_playtest  # type: ignore[no-redef]


class Severidade(str, Enum):
    CRITICO = "CRÍTICO"
    MODERADO = "MODERADO"
    AVISO = "AVISO"


class NivelRisco(str, Enum):
    BAIXO = "Baixo"
    MEDIO_BAIXO = "Médio-baixo"
    MEDIO = "Médio"
    MEDIO_ALTO = "Médio-alto"
    ALTO = "Alto"


@dataclass
class Erro:
    codigo: str
    severidade: Severidade
    mensagem: str
    detalhe: Optional[str] = None
    documento: Optional[str] = None


@dataclass
class ResultadoValidacao:
    erros: list[Erro] = field(default_factory=list)
    avisos: list[Erro] = field(default_factory=list)
    nivel_risco: NivelRisco = NivelRisco.BAIXO
    pode_gerar: bool = True
    resumo: str = ""

    @property
    def criticos(self) -> list[Erro]:
        return [e for e in self.erros if e.severidade == Severidade.CRITICO]

    @property
    def moderados(self) -> list[Erro]:
        return [e for e in self.erros if e.severidade == Severidade.MODERADO]

    def adicionar(self, erro: Erro) -> None:
        if erro.severidade == Severidade.AVISO:
            self.avisos.append(erro)
        else:
            self.erros.append(erro)


CHAVES_OBRIGATORIAS: dict[str, list[str]] = {
    "email_narrador": [
        "REMETENTE_NOME", "REMETENTE_EMAIL", "DESTINATARIO_EMAIL", "COPIA",
        "DESTINATARIO_LABEL", "DATA_HORA", "ASSUNTO",
        "AVATAR_INICIAL", "AVATAR_COR", "CORPO_EMAIL", "NOTA_RODAPE",
    ],
    "email_institucional": [
        "REMETENTE_NOME", "REMETENTE_EMAIL", "DESTINATARIO_EMAIL", "COPIA",
        "DESTINATARIO_LABEL", "DATA_HORA", "ASSUNTO",
        "AVATAR_INICIAL", "AVATAR_COR", "CORPO_EMAIL", "NOTA_RODAPE",
    ],
    "chat": [
        "HORA_TELA", "CONTADOR_NAOVISTOS", "NOME_GRUPO",
        "MEMBROS_LISTA", "DATA_CONVERSA", "MENSAGENS",
    ],
    "boletim": [
        "ORGAO_NOME", "ORGAO_SUBTITULO", "NUMERO_CASO", "TIPO_DOCUMENTO",
        "TIPO_OCORRENCIA", "DATA", "LOCALIZACAO", "HORA_OCORRENCIA",
        "DESCRICAO_OCORRENCIA", "NOME_RESPONSAVEL",
        "ASSINATURA_RESPONSAVEL", "ASSINATURA_GLIFO", "DATA_HORA_ASSINATURA",
    ],
    "depoimento": [
        "ORGAO_NOME", "ORGAO_SUBTITULO", "NUMERO_CASO", "TIPO_DOCUMENTO",
        "TIPO_OCORRENCIA", "DATA", "LOCALIZACAO", "HORA_OCORRENCIA",
        "DESCRICAO_OCORRENCIA", "NOME_RESPONSAVEL",
        "ASSINATURA_RESPONSAVEL", "ASSINATURA_GLIFO", "DATA_HORA_ASSINATURA",
        "CAMPO_NOME", "NOME_ENVOLVIDO", "DATA_NASC", "CONDICAO",
    ],
    "protocolo": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE", "ASSUNTO",
    ],
    "carta": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE",
    ],
    "manual": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE",
    ],
    "glossario": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE",
    ],
    "folha_cruzamento": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE",
    ],
    "contrato": [
        "NOME_ORGANIZACAO", "SUBTITULO_ORGANIZACAO", "ENDERECO_LINHA1",
        "CONTATO", "CNPJ", "COR_TOPO", "LOCAL_DATA",
        "SAUDACAO", "CORPO_CARTA", "FORMULA_ENCERRAMENTO",
        "ASSINATURA_CURSIVA", "NOME_ASSINANTE", "CARGO_ASSINANTE",
    ],
    "log_acesso": [
        "NOME_SISTEMA", "SUBTITULO_SISTEMA", "COR_SISTEMA", "COR_SISTEMA_DARK",
        "DATA_EXPORTACAO", "HORA_EXPORTACAO", "OPERADOR_EXPORT", "HASH_REGISTRO",
        "PERIODO_INICIO", "PERIODO_FIM", "LOCALIZACAO_SISTEMA", "TOTAL_REGISTROS",
        "COLUNA_NOME", "COLUNA_TERMINAL", "COLUNA_METODO", "COLUNA_OBS",
        "TOTAL_USUARIOS", "TOTAL_ENTRADAS", "TOTAL_NEGADOS", "TOTAL_ANOMALIAS",
        "REGISTROS",
    ],
    "log_sistema": [
        "NOME_SISTEMA", "SUBTITULO_SISTEMA", "COR_SISTEMA", "COR_SISTEMA_DARK",
        "DATA_EXPORTACAO", "HORA_EXPORTACAO", "OPERADOR_EXPORT", "HASH_REGISTRO",
        "PERIODO_INICIO", "PERIODO_FIM", "LOCALIZACAO_SISTEMA", "TOTAL_REGISTROS",
        "COLUNA_NOME", "COLUNA_TERMINAL", "COLUNA_METODO", "COLUNA_OBS",
        "TOTAL_USUARIOS", "TOTAL_ENTRADAS", "TOTAL_NEGADOS", "TOTAL_ANOMALIAS",
        "REGISTROS",
    ],
    "escala": [
        "NOME_SISTEMA", "SUBTITULO_SISTEMA", "COR_SISTEMA", "COR_SISTEMA_DARK",
        "DATA_EXPORTACAO", "HORA_EXPORTACAO", "OPERADOR_EXPORT", "HASH_REGISTRO",
        "PERIODO_INICIO", "PERIODO_FIM", "LOCALIZACAO_SISTEMA", "TOTAL_REGISTROS",
        "COLUNA_NOME", "COLUNA_TERMINAL", "COLUNA_METODO", "COLUNA_OBS",
        "TOTAL_USUARIOS", "TOTAL_ENTRADAS", "TOTAL_NEGADOS", "TOTAL_ANOMALIAS",
        "REGISTROS",
    ],
    "recibo": [
        "NOME_EMPRESA", "TAGLINE_EMPRESA", "CNPJ", "ENDERECO_EMPRESA",
        "CONTATO_EMPRESA", "NUMERO_RECIBO", "WATERMARK_TEXTO", "COR_EMPRESA",
        "NOME_CONTRATANTE", "ENDERECO_CONTRATANTE", "DOC_CONTRATANTE",
        "CONTATO_CONTRATANTE", "DATA_RECIBO", "PERIODO_REFERENCIA",
        "VALOR_TOTAL", "VALOR_POR_EXTENSO", "FORMA_PAGAMENTO",
        "DESCRICAO_PAGAMENTO", "ITENS",
        "ASSINATURA_PRESTADOR", "ASSINATURA_CONTRATANTE", "DATA_ASSINATURA",
    ],
    "orcamento": [
        "NOME_EMPRESA", "TIPO_EMPRESA", "CNPJ", "ENDERECO", "SITE_EMAIL",
        "COR_PRIMARIA", "COR_SECUNDARIA", "NUMERO_ORCAMENTO",
        "DATA_EMISSAO", "DATA_VALIDADE", "REVISAO",
        "NOME_CLIENTE", "ENDERECO_CLIENTE", "DOC_CLIENTE", "CONTATO_CLIENTE",
        "TITULO_PROJETO", "DESCRICAO_REFERENCIA", "VALOR_TOTAL", "ITENS",
        "ASSINATURA_RESPONSAVEL", "NOME_RESPONSAVEL", "CARGO_RESPONSAVEL",
    ],
    "extrato": [
        "LOGO_SIGLA", "NOME_BANCO", "TAGLINE_BANCO", "COR_BANCO",
        "PERIODO_INICIO", "PERIODO_FIM", "DATA_GERACAO", "HORA_GERACAO",
        "NOME_TITULAR", "DOC_TITULAR", "AGENCIA", "NUMERO_CONTA", "TIPO_CONTA",
        "SALDO_INICIAL", "DATA_SALDO_INICIAL", "MOVIMENTACAO_LIQUIDA",
        "COR_MOVIMENTACAO", "SALDO_FINAL", "DATA_SALDO_FINAL", "COR_SALDO_FINAL",
        "TOTAL_CREDITOS", "TOTAL_DEBITOS", "TOTAL_LANCAMENTOS",
        "NOTA_LEGAL", "CNPJ_BANCO", "ENDERECO_BANCO", "LANCAMENTOS",
    ],
}


CHAVES_LISTA: dict[str, str] = {
    "email_narrador": "CADA_ANEXO",
    "email_institucional": "CADA_ANEXO",
    "chat": "MENSAGENS",
    "log_acesso": "REGISTROS",
    "log_sistema": "REGISTROS",
    "escala": "REGISTROS",
    "recibo": "ITENS",
    "orcamento": "ITENS",
    "extrato": "LANCAMENTOS",
}


CATEGORIAS_DICA_CONTEXTUAL = {
    "mapa",
    "personagem",
    "cronologia",
    "financeira",
    "logistica",
    "documento",
    "contrato",
    "descarte",
    "solucao",
}

NIVEIS_DICA_CONTEXTUAL = {"leve", "media", "forte", "quase_gabarito"}


PLACEHOLDERS_INVALIDOS = {
    "...",
    "a preencher",
    "lorem ipsum",
    "placeholder",
    "tbd",
}


E1_SOLUCAO_FINAL_TERMS = {
    "acusacao final",
    "acusacao completa",
    "autoria final",
    "culpado final",
    "descobrir o culpado",
    "descobrir o culpado final",
    "executor planejador beneficiario",
    "executor planejador e beneficiario",
    "fechar o caso",
    "gabarito",
    "identificar o culpado",
    "resolver o caso",
    "solucao completa",
    "solucao final",
}


def _normalizar_progressao_texto(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos.lower()).strip()


class BlueprintValidator:
    """Executa validações narrativas, estruturais e offline sobre um blueprint."""

    def __init__(self, blueprint: Blueprint, strict: bool = False):
        self.bp = blueprint
        self.strict = strict
        self.resultado = ResultadoValidacao()
        self._ids_personagens: set[str] = {p.id for p in blueprint.personagens}
        self._codigos_docs: set[str] = {d.codigo for d in blueprint.documentos}
        self._ids_contratos: set[str] = {c.id for c in blueprint.contratos_evidencia if c.id}
        self._docs_por_codigo = {d.codigo: d for d in blueprint.documentos}
        self._schemas = load_all_schemas()
        self._repo_root = Path(__file__).resolve().parents[1]

    def validar(self) -> ResultadoValidacao:
        self._verificar_elenco()
        self._verificar_documentos()
        self._verificar_progressao_operacional()
        self._verificar_contratos_evidencia()
        self._verificar_grafo_pistas()
        self._verificar_pilares()
        self._verificar_pistas()
        self._verificar_red_herrings()
        self._verificar_codigos()
        self._verificar_cadeia_financeira()
        self._verificar_linha_do_tempo()
        self._verificar_dicas()
        self._verificar_dicas_contextuais()
        self._verificar_visual_procedural()
        self._verificar_autossuficiencia()
        self._verificar_playtest_metrics()
        self._verificar_conteudo_schema()
        self._verificar_obviedade()
        self._calcular_risco()
        self._gerar_resumo()
        return self.resultado

    def _verificar_progressao_operacional(self) -> None:
        """Valida contratos estruturados de progressão e condução do caso."""
        conflito = self.bp.conflito_central
        guia = self.bp.guia_operacional
        objetivos = self.bp.objetivos_por_envelope

        campos_conflito = {
            "pergunta_publica": conflito.pergunta_publica,
            "quem_pede_apuracao": conflito.quem_pede_apuracao,
            "motivo_da_apuracao": conflito.motivo_da_apuracao,
            "risco_concreto": conflito.risco_concreto,
            "verdade_aparente": conflito.verdade_aparente,
            "verdade_real_resumida": conflito.verdade_real_resumida,
        }
        for campo, valor in campos_conflito.items():
            if not valor.strip():
                self.resultado.adicionar(Erro(
                    "PROG_001",
                    Severidade.CRITICO,
                    f"conflito_central.{campo} deve ser preenchido.",
                ))

        if conflito.pergunta_publica.strip() != guia.pergunta_publica.strip():
            self.resultado.adicionar(Erro(
                "PROG_002",
                Severidade.CRITICO,
                "guia_operacional.pergunta_publica deve repetir a pergunta pública do conflito central.",
            ))

        envelopes_esperados = {f"E{numero}" for numero in range(1, self.bp.formato_envelopes + 1)}
        envelopes_documentos = {doc.envelope for doc in self.bp.documentos}
        objetivos_por_envelope: dict[str, Any] = {}
        for objetivo in objetivos:
            if objetivo.envelope in objetivos_por_envelope:
                self.resultado.adicionar(Erro(
                    "PROG_003",
                    Severidade.CRITICO,
                    f"Objetivo duplicado para envelope {objetivo.envelope}.",
                ))
            objetivos_por_envelope[objetivo.envelope] = objetivo

            campos_objetivo = ["pergunta_diegetica", "resposta_esperada", "criterio_de_avanco", "forma_diegetica_de_avanco"]
            for campo in campos_objetivo:
                if not getattr(objetivo, campo).strip():
                    self.resultado.adicionar(Erro(
                        "PROG_004",
                        Severidade.CRITICO,
                        f"objetivos_por_envelope[{objetivo.envelope}].{campo} deve ser preenchido.",
                    ))

            if objetivo.envelope == "E1":
                for campo in campos_objetivo:
                    valor_normalizado = _normalizar_progressao_texto(getattr(objetivo, campo))
                    termo_bloqueado = next(
                        (termo for termo in E1_SOLUCAO_FINAL_TERMS if termo in valor_normalizado),
                        None,
                    )
                    if termo_bloqueado:
                        self.resultado.adicionar(Erro(
                            "PROG_018",
                            Severidade.CRITICO,
                            (
                                "Objetivo do E1 exige solução final; E1 deve gerar hipótese parcial, "
                                "tensão ou recontextualização inicial."
                            ),
                            detalhe=f"Campo: {campo}; termo detectado: {termo_bloqueado}.",
                        ))
                        break

            if objetivo.envelope not in envelopes_esperados:
                self.resultado.adicionar(Erro(
                    "PROG_005",
                    Severidade.CRITICO,
                    f"Objetivo referencia envelope fora do formato_envelopes: {objetivo.envelope}.",
                ))
            if objetivo.envelope not in envelopes_documentos:
                self.resultado.adicionar(Erro(
                    "PROG_006",
                    Severidade.CRITICO,
                    f"Objetivo referencia envelope sem documentos: {objetivo.envelope}.",
                ))
            if not objetivo.documentos_minimos:
                self.resultado.adicionar(Erro(
                    "PROG_007",
                    Severidade.MODERADO,
                    f"Objetivo do {objetivo.envelope} não informa documentos_minimos.",
                ))
            for doc_codigo in objetivo.documentos_minimos:
                doc = self._docs_por_codigo.get(doc_codigo)
                if doc is None:
                    self.resultado.adicionar(Erro(
                        "PROG_008",
                        Severidade.CRITICO,
                        f"Objetivo do {objetivo.envelope} referencia documento mínimo inexistente: {doc_codigo}.",
                        documento=doc_codigo,
                    ))
                elif doc.envelope != objetivo.envelope:
                    self.resultado.adicionar(Erro(
                        "PROG_009",
                        Severidade.CRITICO,
                        f"Objetivo do {objetivo.envelope} usa documento mínimo de outro envelope: {doc_codigo}.",
                        documento=doc_codigo,
                    ))

        ausentes = envelopes_esperados - set(objetivos_por_envelope)
        extras = set(objetivos_por_envelope) - envelopes_esperados
        if ausentes:
            self.resultado.adicionar(Erro(
                "PROG_010",
                Severidade.CRITICO,
                f"Faltam objetivos estruturados para envelopes: {', '.join(sorted(ausentes))}.",
            ))
        if extras:
            self.resultado.adicionar(Erro(
                "PROG_011",
                Severidade.CRITICO,
                f"Há objetivos estruturados excedentes: {', '.join(sorted(extras))}.",
            ))

        respostas_guia = guia.resposta_esperada_por_envelope
        if not respostas_guia:
            self.resultado.adicionar(Erro(
                "PROG_012",
                Severidade.CRITICO,
                "guia_operacional.resposta_esperada_por_envelope deve espelhar os objetivos por envelope.",
            ))
        respostas_por_envelope = {objetivo.envelope: objetivo for objetivo in respostas_guia}
        if set(respostas_por_envelope) != set(objetivos_por_envelope):
            self.resultado.adicionar(Erro(
                "PROG_013",
                Severidade.CRITICO,
                "guia_operacional.resposta_esperada_por_envelope deve cobrir os mesmos envelopes de objetivos_por_envelope.",
            ))
        for envelope, objetivo in objetivos_por_envelope.items():
            resposta_guia = respostas_por_envelope.get(envelope)
            if resposta_guia:
                divergencias = []
                for campo in [
                    "pergunta_diegetica",
                    "resposta_esperada",
                    "criterio_de_avanco",
                    "forma_diegetica_de_avanco",
                ]:
                    if getattr(resposta_guia, campo).strip() != getattr(objetivo, campo).strip():
                        divergencias.append(campo)
                if resposta_guia.nao_precisa_resolver_ainda != objetivo.nao_precisa_resolver_ainda:
                    divergencias.append("nao_precisa_resolver_ainda")
                if resposta_guia.documentos_minimos != objetivo.documentos_minimos:
                    divergencias.append("documentos_minimos")

                if divergencias:
                    self.resultado.adicionar(Erro(
                        "PROG_014",
                        Severidade.CRITICO,
                        f"Resposta operacional do guia diverge do objetivo do {envelope}.",
                        detalhe=f"Campos divergentes: {', '.join(divergencias)}.",
                    ))

        campos_guia = {
            "linha_tempo_aparente_resumo": guia.linha_tempo_aparente_resumo,
            "linha_tempo_real_resumo": guia.linha_tempo_real_resumo,
        }
        for campo, valor in campos_guia.items():
            if not valor.strip():
                self.resultado.adicionar(Erro(
                    "PROG_015",
                    Severidade.CRITICO,
                    f"guia_operacional.{campo} deve ser preenchido.",
                ))
        if len(guia.red_herrings_e_descartes) < len(self.bp.red_herrings):
            self.resultado.adicionar(Erro(
                "PROG_016",
                Severidade.MODERADO,
                "guia_operacional.red_herrings_e_descartes deve cobrir os falsos caminhos principais.",
            ))
        if not guia.quando_usar_dicas:
            self.resultado.adicionar(Erro(
                "PROG_017",
                Severidade.MODERADO,
                "guia_operacional.quando_usar_dicas deve orientar o facilitador.",
            ))

    def _verificar_elenco(self) -> None:
        papeis = {p.papel for p in self.bp.personagens}
        ids_obrigatorios = {
            "executor_id": self.bp.executor_id,
            "planejador_id": self.bp.planejador_id,
            "beneficiario_id": self.bp.beneficiario_id,
        }
        for campo, valor_id in ids_obrigatorios.items():
            if valor_id not in self._ids_personagens:
                self.resultado.adicionar(Erro(
                    codigo="ELENCO_002",
                    severidade=Severidade.CRITICO,
                    mensagem=f"ID '{valor_id}' em '{campo}' não existe no elenco.",
                ))

        ids_unicos = len(set(ids_obrigatorios.values()))
        if ids_unicos == 1:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_001",
                severidade=Severidade.AVISO,
                mensagem="Executor, planejador e beneficiário apontam para o mesmo personagem.",
                detalhe="Caso com culpado único; válido quando a concentração dos papéis for intencional.",
            ))
        elif ids_unicos == 2:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_001",
                severidade=Severidade.AVISO,
                mensagem="Executor, planejador e beneficiário usam apenas dois personagens.",
                detalhe="Verifique se o acúmulo parcial de papéis no gabarito foi intencional.",
            ))

        if PapelPersonagem.NARRADOR not in papeis:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_003",
                severidade=Severidade.MODERADO,
                mensagem="Nenhum personagem com papel 'narrador' definido.",
                detalhe="O primeiro e-mail deve vir de personagem com interesse próprio.",
            ))

        red_herrings = [p for p in self.bp.personagens if p.papel == PapelPersonagem.RED_HERRING]
        if len(red_herrings) < 2:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_004",
                severidade=Severidade.MODERADO,
                mensagem=f"Apenas {len(red_herrings)} red herring(s). Mínimo recomendado: 2.",
            ))

        for personagem in self.bp.personagens:
            if not personagem.documento_ancoragem:
                self.resultado.adicionar(Erro(
                    codigo="ELENCO_005",
                    severidade=Severidade.MODERADO,
                    mensagem=f"Personagem '{personagem.nome}' sem documento de ancoragem.",
                ))
            for codigo in personagem.documento_ancoragem:
                if codigo not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        codigo="ELENCO_006",
                        severidade=Severidade.CRITICO,
                        mensagem=f"Documento de ancoragem '{codigo}' não existe.",
                    ))
            self._verificar_overrides_assinatura(personagem)

    def _verificar_overrides_assinatura(self, personagem: Any) -> None:
        perfil = getattr(personagem, "assinatura", None)
        if perfil is None:
            return
        for campo in ("override_assinatura_svg", "override_rubrica_svg"):
            valor = getattr(perfil, campo, None)
            if not valor:
                continue
            caminho = Path(str(valor))
            if caminho.is_absolute() or ".." in caminho.parts:
                self.resultado.adicionar(Erro(
                    codigo="ASSINATURA_001",
                    severidade=Severidade.CRITICO,
                    mensagem=(
                        f"Override de assinatura de '{personagem.nome}' deve ser caminho "
                        "relativo ao repositório."
                    ),
                ))
                continue
            if caminho.suffix.lower() != ".svg":
                self.resultado.adicionar(Erro(
                    codigo="ASSINATURA_002",
                    severidade=Severidade.CRITICO,
                    mensagem=f"Override de assinatura de '{personagem.nome}' não é SVG: {valor}.",
                ))
                continue
            if not (self._repo_root / caminho).is_file():
                self.resultado.adicionar(Erro(
                    codigo="ASSINATURA_003",
                    severidade=Severidade.CRITICO,
                    mensagem=f"Override de assinatura de '{personagem.nome}' não existe: {valor}.",
                ))

    def _verificar_documentos(self) -> None:
        codigos_vistos: set[str] = set()
        codigos_duplicados: set[str] = set()
        for doc in self.bp.documentos:
            if doc.codigo in codigos_vistos:
                codigos_duplicados.add(doc.codigo)
            codigos_vistos.add(doc.codigo)
        for codigo in sorted(codigos_duplicados):
            self.resultado.adicionar(Erro(
                "DOC_008",
                Severidade.CRITICO,
                f"Documento duplicado no blueprint: '{codigo}'.",
                documento=codigo,
            ))

        envelopes_jogador = sorted({d.envelope for d in self.bp.documentos}, key=self._numero_envelope)
        for envelope in envelopes_jogador:
            if not self._envelope_valido(envelope):
                self.resultado.adicionar(Erro(
                    "ENV_001",
                    Severidade.CRITICO,
                    f"Envelope inválido em documento: '{envelope}'. Use E1, E2, E3...",
                ))
        if self.bp.documentos and "E1" not in envelopes_jogador:
            self.resultado.adicionar(Erro(
                "ENV_002", Severidade.CRITICO, "Documentos de jogador existem, mas o Envelope E1 está ausente."
            ))
        numeros = sorted(self._numero_envelope(e) for e in envelopes_jogador if self._envelope_valido(e))
        if numeros:
            esperado = list(range(1, max(numeros) + 1))
            if numeros != esperado:
                ausentes = [f"E{numero}" for numero in esperado if numero not in numeros]
                self.resultado.adicionar(Erro(
                    "ENV_003",
                    Severidade.CRITICO,
                    f"Sequência de envelopes com buraco; ausente(s): {', '.join(ausentes)}.",
                ))
            maior_envelope_real = max(numeros)
            if self.bp.formato_envelopes > maior_envelope_real:
                self.resultado.adicionar(Erro(
                    "ENV_004",
                    Severidade.CRITICO,
                    (
                        f"formato_envelopes declara E{self.bp.formato_envelopes}, "
                        f"mas só há documentos até E{maior_envelope_real}."
                    ),
                ))
            if self.bp.formato_envelopes < maior_envelope_real:
                self.resultado.adicionar(Erro(
                    "ENV_005",
                    Severidade.CRITICO,
                    (
                        f"formato_envelopes declara apenas E{self.bp.formato_envelopes}, "
                        f"mas há documentos até E{maior_envelope_real}."
                    ),
                ))

        docs_e1 = [d for d in self.bp.documentos if d.envelope == "E1"]
        tipos_e1 = {d.tipo for d in docs_e1}
        if TipoDocumento.PROTO not in tipos_e1:
            self.resultado.adicionar(Erro(
                "DOC_003", Severidade.CRITICO, "Envelope 1 não tem protocolo de investigação."
            ))
        if TipoDocumento.CRUZ not in tipos_e1:
            self.resultado.adicionar(Erro(
                "DOC_004", Severidade.MODERADO, "Folha de cruzamento ausente no Envelope 1."
            ))

        for doc in self.bp.documentos:
            for id_citado in doc.ids_citados:
                if not self._id_tem_correspondencia(id_citado):
                    self.resultado.adicionar(Erro(
                        "DOC_005",
                        Severidade.CRITICO,
                        f"ID '{id_citado}' citado em '{doc.codigo}' não existe na matriz.",
                        documento=doc.codigo,
                    ))
            for ref in doc.confirma + doc.confirmado_por:
                if ref not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        "DOC_007",
                        Severidade.MODERADO,
                        f"Documento '{doc.codigo}' referencia '{ref}' que não existe.",
                        documento=doc.codigo,
                    ))


    @staticmethod
    def _envelope_valido(envelope: str) -> bool:
        return bool(re.fullmatch(r"E[1-9]\d*", str(envelope)))

    @staticmethod
    def _numero_envelope(envelope: str) -> int:
        texto = str(envelope)
        if re.fullmatch(r"E[1-9]\d*", texto):
            return int(texto[1:])
        return 10**9

    def _fase_documento_posterior(self, fase: str, documento_codigo: str) -> bool:
        if fase == "final":
            return False
        doc = self._docs_por_codigo.get(documento_codigo)
        if doc is None:
            return False
        return self._numero_envelope(doc.envelope) > self._numero_envelope(fase)

    def _verificar_contratos_evidencia(self) -> None:
        ids_vistos: set[str] = set()
        usos_obrigatorios_por_doc: dict[str, set[str]] = {}
        limite_usos_obrigatorios = 3
        for contrato in self.bp.contratos_evidencia:
            if not contrato.id:
                self.resultado.adicionar(Erro("CE_001", Severidade.CRITICO, "Contrato de evidência sem id."))
            elif contrato.id in ids_vistos:
                self.resultado.adicionar(Erro("CE_002", Severidade.CRITICO, f"Contrato de evidência duplicado: {contrato.id}."))
            ids_vistos.add(contrato.id)

            prova = contrato.prova_principal
            confirmacao = contrato.confirmacao_independente
            if contrato.obrigatoria_para_avanco and (not prova or not confirmacao):
                self.resultado.adicionar(Erro(
                    "CE_008", Severidade.CRITICO, f"Contrato obrigatório '{contrato.id}' está incompleto."
                ))
            if contrato.obrigatoria_para_avanco:
                for doc_codigo in {codigo for codigo in [prova, confirmacao] if codigo}:
                    usos_obrigatorios_por_doc.setdefault(doc_codigo, set()).add(contrato.id)
            if not prova or prova not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "CE_003", Severidade.CRITICO, f"prova_principal inexistente no contrato '{contrato.id}': {prova}."
                ))
            if not confirmacao or confirmacao not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "CE_004",
                    Severidade.CRITICO,
                    f"confirmacao_independente inexistente no contrato '{contrato.id}': {confirmacao}.",
                ))
            if prova and confirmacao and prova == confirmacao:
                self.resultado.adicionar(Erro(
                    "CE_005", Severidade.CRITICO, f"Contrato '{contrato.id}' usa a mesma prova e confirmação."
                ))

            for doc_codigo in contrato.descarta_alternativas:
                if doc_codigo not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        "CE_006",
                        Severidade.CRITICO,
                        f"descarta_alternativas referencia documento inexistente no contrato '{contrato.id}': {doc_codigo}.",
                    ))

            for doc_codigo in [codigo for codigo in [prova, confirmacao] if codigo]:
                if self._fase_documento_posterior(contrato.fase, doc_codigo):
                    self.resultado.adicionar(Erro(
                        "CE_007",
                        Severidade.CRITICO,
                        f"Contrato '{contrato.id}' de fase {contrato.fase} depende de documento posterior: {doc_codigo}.",
                        documento=doc_codigo,
                    ))

            if contrato.obrigatoria_para_avanco and contrato.risco_ambiguidade == "alto":
                self.resultado.adicionar(Erro(
                    "CE_009", Severidade.MODERADO, f"Contrato obrigatório '{contrato.id}' tem risco de ambiguidade alto."
                ))
            if contrato.obrigatoria_para_avanco and not contrato.acao_esperada_jogador.strip():
                self.resultado.adicionar(Erro(
                    "CE_010", Severidade.MODERADO, f"Contrato obrigatório '{contrato.id}' não define ação esperada do jogador."
                ))

        for doc_codigo, contratos_ids in sorted(usos_obrigatorios_por_doc.items()):
            if len(contratos_ids) > limite_usos_obrigatorios:
                self.resultado.adicionar(Erro(
                    "CE_011",
                    Severidade.AVISO,
                    (
                        f"Documento '{doc_codigo}' aparece em {len(contratos_ids)} contratos obrigatórios; "
                        "verifique se ele não concentra progressão demais."
                    ),
                    detalhe=f"Contratos: {', '.join(sorted(contratos_ids))}",
                    documento=doc_codigo,
                ))

    def _verificar_grafo_pistas(self) -> None:
        graph = build_clue_graph(self.bp)
        report = analyze_clue_graph(graph, self.bp)

        if not self.bp.contratos_evidencia:
            self.resultado.adicionar(Erro(
                "GP_006",
                Severidade.MODERADO,
                "Grafo de pistas não avaliado: nenhum contrato de evidência informado.",
                detalhe="Blueprints antigos continuam aceitos, mas a solvabilidade estrutural exige contratos.",
            ))
            return

        for issue in report["issues"]:
            codigo = str(issue["code"])
            severidade_texto = str(issue["severity"])
            if codigo == "GP_003" or severidade_texto == "warning":
                severidade = Severidade.AVISO
            elif severidade_texto == "critical":
                severidade = Severidade.CRITICO
            else:
                severidade = Severidade.MODERADO

            self.resultado.adicionar(Erro(
                codigo=codigo,
                severidade=severidade,
                mensagem=str(issue["message"]),
                documento=issue.get("document"),
                detalhe=f"Contrato: {issue['contract']}" if issue.get("contract") else None,
            ))

    def _id_tem_correspondencia(self, id_citado: str) -> bool:
        if id_citado in self._ids_personagens:
            return True
        return id_citado.isdigit() and len(id_citado) >= 5

    def _verificar_pilares(self) -> None:
        if len(self.bp.pilares_validacao) != 4:
            self.resultado.adicionar(Erro(
                "PILAR_001",
                Severidade.CRITICO,
                f"O Envelope 1 deve ter exatamente 4 pilares; encontrado: {len(self.bp.pilares_validacao)}.",
            ))
            return

        personagens = {p.personagem_id for p in self.bp.pilares_validacao}
        if len(personagens) > 1:
            self.resultado.adicionar(Erro(
                "PILAR_006",
                Severidade.MODERADO,
                f"Pilares apontam para IDs diferentes: {personagens}.",
            ))

        for pilar in self.bp.pilares_validacao:
            if pilar.documento_principal not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PILAR_002", Severidade.CRITICO, f"Documento principal inexistente: {pilar.documento_principal}."
                ))
            if pilar.confirmacao not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PILAR_003", Severidade.CRITICO, f"Confirmação inexistente: {pilar.confirmacao}."
                ))
            elif pilar.confirmacao == pilar.documento_principal:
                self.resultado.adicionar(Erro(
                    "PILAR_004", Severidade.CRITICO, "Pilar usa o mesmo documento como prova e confirmação."
                ))
            if pilar.personagem_id not in self._ids_personagens:
                self.resultado.adicionar(Erro(
                    "PILAR_005", Severidade.CRITICO, f"Personagem do pilar não existe: {pilar.personagem_id}."
                ))

    def _verificar_pistas(self) -> None:
        for pista in self.bp.matriz_pistas:
            if pista.documento not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PISTA_002", Severidade.CRITICO, f"Pista referencia documento inexistente: {pista.documento}."
                ))
            if pista.confirmacao not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PISTA_003", Severidade.CRITICO, f"Pista sem confirmação existente: {pista.confirmacao}."
                ))
            elif pista.confirmacao == pista.documento:
                self.resultado.adicionar(Erro(
                    "PISTA_004", Severidade.CRITICO, "Pista usa o mesmo documento como prova e confirmação."
                ))

    def _verificar_red_herrings(self) -> None:
        culpados = {self.bp.executor_id, self.bp.planejador_id, self.bp.beneficiario_id}
        for rh in self.bp.red_herrings:
            if rh.personagem_id not in self._ids_personagens:
                self.resultado.adicionar(Erro("RH_001", Severidade.CRITICO, "Red herring aponta para personagem inexistente."))
            if rh.documento_descarte not in self._codigos_docs:
                self.resultado.adicionar(Erro("RH_002", Severidade.CRITICO, "Red herring sem documento de descarte existente."))
            if rh.personagem_id in culpados:
                self.resultado.adicionar(Erro("RH_003", Severidade.CRITICO, "Culpado também foi marcado como red herring."))

    def _verificar_codigos(self) -> None:
        for codigo in self.bp.codigos:
            if codigo.documento not in self._codigos_docs:
                self.resultado.adicionar(Erro("COD_001", Severidade.CRITICO, f"Código em documento inexistente: {codigo.documento}."))
            if codigo.chave_em not in self._codigos_docs:
                self.resultado.adicionar(Erro("COD_002", Severidade.CRITICO, f"Chave de código inexistente: {codigo.chave_em}."))
            if codigo.criterio == "ids_personagens":
                for elemento in codigo.elementos:
                    if elemento not in self._ids_personagens:
                        self.resultado.adicionar(Erro("COD_003", Severidade.CRITICO, f"Elemento de código sem personagem: {elemento}."))
            if codigo.criterio == "misto":
                self.resultado.adicionar(Erro("COD_004", Severidade.MODERADO, "Código com critério misto exige pista documental clara."))

    def _verificar_cadeia_financeira(self) -> None:
        if not self.bp.cadeia_financeira:
            if "fraude" in self.bp.genero.lower() or "roubo" in self.bp.genero.lower():
                self.resultado.adicionar(Erro("FIN_001", Severidade.AVISO, "Caso de fraude/roubo sem cadeia financeira/logística."))
            return

        finais: list[SaltoFinanceiro] = [s for s in self.bp.cadeia_financeira if s.is_salto_final]
        if len(finais) != 1:
            self.resultado.adicionar(Erro("FIN_002", Severidade.CRITICO, "Cadeia deve ter exatamente um salto final marcado."))

        for salto in self.bp.cadeia_financeira:
            if salto.documento_prova not in self._codigos_docs:
                self.resultado.adicionar(Erro("FIN_004", Severidade.CRITICO, f"Salto sem documento existente: {salto.documento_prova}."))
            if salto.is_salto_final:
                if not salto.confirmacao_independente:
                    self.resultado.adicionar(Erro("FIN_005", Severidade.CRITICO, "Salto final sem confirmação independente."))
                elif salto.confirmacao_independente not in self._codigos_docs:
                    self.resultado.adicionar(Erro("FIN_006", Severidade.CRITICO, "Confirmação do salto final não existe."))
                elif salto.confirmacao_independente == salto.documento_prova:
                    self.resultado.adicionar(Erro("FIN_007", Severidade.CRITICO, "Salto final usa o mesmo documento como prova e confirmação."))

    def _verificar_linha_do_tempo(self) -> None:
        if not self.bp.intervalo_critico_inicio or not self.bp.intervalo_critico_fim:
            self.resultado.adicionar(Erro("LT_001", Severidade.CRITICO, "Intervalo crítico não definido."))
        for evento in self.bp.linha_tempo_real:
            if evento.documento_prova not in self._codigos_docs:
                self.resultado.adicionar(Erro("LT_002", Severidade.MODERADO, f"Evento referencia documento inexistente: {evento.documento_prova}."))
            if evento.confirmacao_independente and evento.confirmacao_independente not in self._codigos_docs:
                self.resultado.adicionar(Erro("LT_003", Severidade.MODERADO, f"Evento referencia confirmação inexistente: {evento.confirmacao_independente}."))

    def _verificar_dicas(self) -> None:
        if not any(d.intensidade == Intensidade.QUASE_GABARITO for d in self.bp.dicas):
            self.resultado.adicionar(Erro("DICA_001", Severidade.MODERADO, "Nenhuma dica de quase-gabarito definida."))
        envelopes_docs = {d.envelope for d in self.bp.documentos}
        dicas_por_envelope = {envelope: 0 for envelope in envelopes_docs}
        for dica in self.bp.dicas:
            if dica.envelope in dicas_por_envelope:
                dicas_por_envelope[dica.envelope] += 1
        for envelope, total in dicas_por_envelope.items():
            if self._numero_envelope(envelope) >= 2 and total < 2:
                self.resultado.adicionar(Erro("DICA_002", Severidade.MODERADO, f"{envelope} tem menos de 2 dicas."))
        nomes = {p.nome.lower() for p in self.bp.personagens}
        for dica in self.bp.dicas:
            if dica.intensidade in [Intensidade.LEVE, Intensidade.MEDIA]:
                if any(nome in dica.texto.lower() for nome in nomes):
                    self.resultado.adicionar(Erro("DICA_003", Severidade.AVISO, f"Dica {dica.numero} pode revelar nome diretamente."))

    def _verificar_dicas_contextuais(self) -> None:
        dicas = self.bp.dicas_contextuais
        if self.bp.contratos_evidencia and not dicas:
            self.resultado.adicionar(Erro(
                "DC_000",
                Severidade.MODERADO,
                "Contratos de evidência existem, mas nenhuma dica contextual foi definida.",
                detalhe="O pacote continua gerável; adicione dicas para apoiar o facilitador em travamentos reais.",
            ))
            return

        ids_vistos: set[str] = set()
        for dica in dicas:
            dica_id = dica.id.strip()
            if not dica_id:
                self.resultado.adicionar(Erro("DC_001", Severidade.CRITICO, "Dica contextual sem id."))
            elif dica_id in ids_vistos:
                self.resultado.adicionar(Erro("DC_002", Severidade.CRITICO, f"Dica contextual duplicada: {dica_id}."))
            ids_vistos.add(dica_id)

            fase = dica.fase.strip()
            if fase != "final" and not self._envelope_valido(fase):
                self.resultado.adicionar(Erro("DC_003", Severidade.CRITICO, f"Fase inválida em dica contextual '{dica_id}': {dica.fase}."))

            if not dica.texto.strip():
                self.resultado.adicionar(Erro("DC_004", Severidade.CRITICO, f"Dica contextual '{dica_id}' sem texto."))
            if not dica.condicao_uso.strip():
                self.resultado.adicionar(Erro("DC_005", Severidade.CRITICO, f"Dica contextual '{dica_id}' sem condicao_uso."))

            for contrato_id in dica.contratos_relacionados:
                if contrato_id not in self._ids_contratos:
                    self.resultado.adicionar(Erro(
                        "DC_006",
                        Severidade.CRITICO,
                        f"Dica contextual '{dica_id}' referencia contrato inexistente: {contrato_id}.",
                    ))
            for documento_codigo in dica.documentos_relacionados:
                if documento_codigo not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        "DC_007",
                        Severidade.CRITICO,
                        f"Dica contextual '{dica_id}' referencia documento inexistente: {documento_codigo}.",
                        documento=documento_codigo,
                    ))

            if dica.nivel not in NIVEIS_DICA_CONTEXTUAL:
                self.resultado.adicionar(Erro("DC_008", Severidade.CRITICO, f"Nível inválido em dica contextual '{dica_id}': {dica.nivel}."))
            if dica.categoria not in CATEGORIAS_DICA_CONTEXTUAL:
                self.resultado.adicionar(Erro("DC_009", Severidade.CRITICO, f"Categoria inválida em dica contextual '{dica_id}': {dica.categoria}."))



    def _verificar_visual_procedural(self) -> None:
        visual = self.bp.visual_procedural
        if visual is None:
            return

        tem_funcao_narrativa = False
        for mapa in visual.mapas:
            mapa_id = mapa.id.strip()
            if not mapa_id:
                self.resultado.adicionar(Erro("VP_001", Severidade.CRITICO, "Mapa procedural sem id."))
            if mapa.orientacao != "landscape":
                self.resultado.adicionar(Erro(
                    "VP_002",
                    Severidade.CRITICO,
                    f"Mapa procedural '{mapa_id or mapa.titulo}' deve usar orientacao landscape.",
                ))
            if mapa.largura <= 0 or mapa.altura <= 0:
                self.resultado.adicionar(Erro(
                    "VP_004",
                    Severidade.CRITICO,
                    f"Mapa procedural '{mapa_id or mapa.titulo}' tem largura/altura inválidas.",
                ))

            area_ids: set[str] = set()
            for area in mapa.areas:
                area_id = area.id.strip()
                if not area_id:
                    self.resultado.adicionar(Erro(
                        "VP_003",
                        Severidade.CRITICO,
                        f"Área sem id no mapa procedural '{mapa_id or mapa.titulo}'.",
                    ))
                else:
                    area_ids.add(area_id)
                fora_canvas = mapa.largura > 0 and mapa.altura > 0 and (
                    area.x + area.w > mapa.largura or area.y + area.h > mapa.altura
                )
                if area.x < 0 or area.y < 0 or area.w <= 0 or area.h <= 0 or fora_canvas:
                    self.resultado.adicionar(Erro(
                        "VP_004",
                        Severidade.CRITICO,
                        f"Área '{area_id or area.nome}' tem dimensões inválidas no mapa '{mapa_id or mapa.titulo}'.",
                    ))

            for conexao in mapa.conexoes:
                if conexao.origem not in area_ids or conexao.destino not in area_ids:
                    self.resultado.adicionar(Erro(
                        "VP_005",
                        Severidade.CRITICO,
                        f"Conexão do mapa '{mapa_id or mapa.titulo}' referencia área inexistente.",
                    ))

            for marcador in mapa.marcadores:
                if marcador.documento_relacionado:
                    tem_funcao_narrativa = True
                    if marcador.documento_relacionado not in self._codigos_docs:
                        self.resultado.adicionar(Erro(
                            "VP_006",
                            Severidade.CRITICO,
                            f"Marcador '{marcador.id}' referencia documento inexistente: {marcador.documento_relacionado}.",
                            documento=marcador.documento_relacionado,
                        ))
                if marcador.contrato_relacionado:
                    tem_funcao_narrativa = True
                    if marcador.contrato_relacionado not in self._ids_contratos:
                        self.resultado.adicionar(Erro(
                            "VP_007",
                            Severidade.CRITICO,
                            f"Marcador '{marcador.id}' referencia contrato inexistente: {marcador.contrato_relacionado}.",
                        ))

        for personagem_visual in visual.personagens:
            if personagem_visual.personagem_id in self._ids_personagens:
                tem_funcao_narrativa = True
            else:
                self.resultado.adicionar(Erro(
                    "VP_008",
                    Severidade.CRITICO,
                    f"Personagem visual referencia personagem inexistente: {personagem_visual.personagem_id}.",
                ))

        for local in visual.locais:
            for codigo in local.documentos_relacionados:
                tem_funcao_narrativa = True
                if codigo not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        "VP_009",
                        Severidade.CRITICO,
                        f"Local visual '{local.id}' referencia documento inexistente: {codigo}.",
                        documento=codigo,
                    ))

        if (visual.mapas or visual.personagens or visual.locais) and not tem_funcao_narrativa:
            self.resultado.adicionar(Erro(
                "VP_010",
                Severidade.MODERADO,
                "Visual procedural existe, mas nenhum elemento tem função narrativa relacionada.",
            ))

    def _verificar_playtest_metrics(self) -> None:
        """Registra warnings heurísticos de playtest sem bloquear geração."""
        report = analyze_playtest(self.bp)
        for warning in report.get("warnings", []):
            code = str(warning.get("code", "PT_000"))
            message = str(warning.get("message", "Métrica de playtest requer revisão."))
            detail = warning.get("detail")
            self.resultado.adicionar(Erro(
                codigo=code,
                severidade=Severidade.AVISO,
                mensagem=message,
                detalhe=str(detail) if detail else None,
            ))

    def _verificar_autossuficiencia(self) -> None:
        tem_log = any(d.tipo in [TipoDocumento.LOG_ACESSO, TipoDocumento.LOG_SISTEMA] for d in self.bp.documentos)
        tem_glossario = any(d.tipo == TipoDocumento.GLOSS for d in self.bp.documentos)
        if tem_log and not tem_glossario:
            self.resultado.adicionar(Erro("AUTO_001", Severidade.AVISO, "Caso tem logs técnicos mas nenhum glossário."))
        if self.bp.modo_validacao == ModoValidacao.OFFLINE_PURO:
            for doc in self.bp.documentos:
                texto = f"{doc.titulo} {doc.objetivo_narrativo}".lower()
                if "qr" in texto or "link" in texto or "url" in texto:
                    self.resultado.adicionar(Erro(
                        "AUTO_002",
                        Severidade.MODERADO,
                        f"Documento '{doc.codigo}' menciona QR/link/url em modo offline puro.",
                        documento=doc.codigo,
                    ))

    @staticmethod
    def _valor_conteudo_incompleto(valor: object) -> bool:
        if valor is None:
            return True
        if isinstance(valor, str):
            texto = " ".join(valor.strip().lower().split())
            return (
                not texto
                or texto in PLACEHOLDERS_INVALIDOS
                or texto.startswith("lorem ipsum")
            )
        if isinstance(valor, (list, tuple, set)):
            return len(valor) == 0
        if isinstance(valor, dict):
            return len(valor) == 0
        return False

    @staticmethod
    def _normalizar_bool(valor: object) -> bool:
        if valor is None:
            return False
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, int) and not isinstance(valor, bool):
            return valor != 0
        if isinstance(valor, str):
            texto = valor.strip().lower()
            if texto in {"true", "sim", "yes", "1"}:
                return True
            if texto in {"false", "não", "nao", "no", "0", ""}:
                return False
        return bool(valor)

    @classmethod
    def _condicao_verdadeira(cls, conteudo: dict[str, Any], condicao: dict[str, Any]) -> bool:
        campo = condicao.get("field")
        esperado = condicao.get("equals", True)
        valor = conteudo.get(campo)
        if isinstance(esperado, bool):
            return cls._normalizar_bool(valor) is esperado
        return valor == esperado

    @staticmethod
    def _tem_html_minimo(valor: str) -> bool:
        return any(tag in valor.lower() for tag in ("<p", "<table", "<ul", "<ol", "<div", "<br"))

    @classmethod
    def _valor_tem_lixo_tecnico(cls, valor: object) -> bool:
        if isinstance(valor, str):
            texto = " ".join(valor.strip().lower().split())
            return (
                "conteudo_generico" in texto
                or "conteúdo genérico" in texto
                or "placeholder" in texto
                or "lorem ipsum" in texto
                or texto in {"tbd", "todo", "undefined", "none", "null"}
            )
        if isinstance(valor, dict):
            return any(cls._valor_tem_lixo_tecnico(v) for v in valor.values())
        if isinstance(valor, list):
            return any(cls._valor_tem_lixo_tecnico(v) for v in valor)
        return False

    def _registrar_campos_incompletos(
        self,
        doc_codigo: str,
        tipo: str,
        conteudo: dict[str, Any],
        campos: list[str],
        codigo: str = "CONT_003",
    ) -> None:
        incompletos = [
            campo
            for campo in campos
            if campo not in conteudo
            or self._valor_conteudo_incompleto(conteudo[campo])
            or self._valor_tem_lixo_tecnico(conteudo[campo])
        ]
        if incompletos:
            self.resultado.adicionar(Erro(
                codigo=codigo,
                severidade=Severidade.CRITICO,
                mensagem=(
                    f"'{doc_codigo}' ({tipo}) — {len(incompletos)} campo(s) obrigatório(s) "
                    f"ausente(s), vazio(s) ou técnico(s): {', '.join(incompletos[:5])}"
                    f"{'...' if len(incompletos) > 5 else ''}."
                ),
                detalhe="Consulte framework/CONTEUDO_SCHEMA.md e generator/schemas/*.yaml.",
                documento=doc_codigo,
            ))

    def _verificar_lista_schema(
        self,
        doc_codigo: str,
        tipo: str,
        conteudo: dict[str, Any],
        nome_lista: str,
        regra: dict[str, Any],
    ) -> None:
        obrigatoria = bool(regra.get("required"))
        if not obrigatoria and "required_when" in regra:
            obrigatoria = self._condicao_verdadeira(conteudo, regra["required_when"])
        if not obrigatoria and nome_lista not in conteudo:
            return

        lista = conteudo.get(nome_lista)
        if not isinstance(lista, list) or not lista:
            self.resultado.adicionar(Erro(
                codigo="CONT_004",
                severidade=Severidade.CRITICO,
                mensagem=f"'{doc_codigo}' — '{nome_lista}' deve ser lista com ao menos 1 item.",
                documento=doc_codigo,
            ))
            return

        item_required = regra.get("item_required", [])
        for index, item in enumerate(lista, start=1):
            if not isinstance(item, dict):
                self.resultado.adicionar(Erro(
                    codigo="CONT_ITEM_001",
                    severidade=Severidade.CRITICO,
                    mensagem=f"'{doc_codigo}' — item {index} de '{nome_lista}' deve ser objeto.",
                    documento=doc_codigo,
                ))
                continue
            faltantes = [
                campo
                for campo in item_required
                if campo not in item
                or self._valor_conteudo_incompleto(item[campo])
                or self._valor_tem_lixo_tecnico(item[campo])
            ]
            for condicional in regra.get("item_required_when", []):
                if self._condicao_verdadeira(item, condicional.get("when", {})):
                    faltantes.extend(
                        campo
                        for campo in condicional.get("required", [])
                        if campo not in item
                        or self._valor_conteudo_incompleto(item[campo])
                        or self._valor_tem_lixo_tecnico(item[campo])
                    )
            if faltantes:
                self.resultado.adicionar(Erro(
                    codigo="CONT_ITEM_001",
                    severidade=Severidade.CRITICO,
                    mensagem=(
                        f"'{doc_codigo}' — item {index} de '{nome_lista}' sem campo(s) "
                        f"obrigatório(s): {', '.join(sorted(set(faltantes)))}."
                    ),
                    documento=doc_codigo,
                ))

    def _verificar_conteudo_schema(self) -> None:
        """Verifica o contrato técnico de renderização a partir de schemas YAML."""
        for doc in self.bp.documentos:
            tipo = doc.tipo.value if hasattr(doc.tipo, "value") else str(doc.tipo)
            conteudo = getattr(doc, "conteudo", None)

            if not isinstance(conteudo, dict) or not conteudo:
                self.resultado.adicionar(Erro(
                    codigo="CONT_001",
                    severidade=Severidade.CRITICO,
                    mensagem=f"'{doc.codigo}' — campo 'conteudo' ausente ou vazio.",
                    detalhe=f"Tipo '{tipo}' requer conteudo preenchido para renderização.",
                    documento=doc.codigo,
                ))
                continue

            if tipo == "outro":
                self.resultado.adicionar(Erro(
                    codigo="CONT_002",
                    severidade=Severidade.AVISO,
                    mensagem=f"'{doc.codigo}' — tipo 'outro' usa fallback controlado de conteúdo.",
                    detalhe="Prefira um tipo especializado antes de produção estrita.",
                    documento=doc.codigo,
                ))

            schema = get_schema_for_type(tipo, self._schemas)
            if schema is None:
                self.resultado.adicionar(Erro(
                    codigo="CONT_002",
                    severidade=Severidade.AVISO,
                    mensagem=f"'{doc.codigo}' — tipo '{tipo}' sem schema técnico de conteúdo definido.",
                    detalhe="Tipo ainda cai em fallback controlado; crie schema antes de produção estrita.",
                    documento=doc.codigo,
                ))
                continue

            self._registrar_campos_incompletos(doc.codigo, tipo, conteudo, schema.get("required", []))

            for regra in schema.get("required_when", []):
                if self._condicao_verdadeira(conteudo, regra.get("when", {})):
                    self._registrar_campos_incompletos(
                        doc.codigo,
                        tipo,
                        conteudo,
                        regra.get("required", []),
                        codigo="CONT_REQUIRED_WHEN_001",
                    )

            for nome_lista, regra_lista in schema.get("lists", {}).items():
                self._verificar_lista_schema(doc.codigo, tipo, conteudo, nome_lista, regra_lista)

            required = set(schema.get("required", []))
            optional = set(schema.get("optional", []))
            hidden_allowed = set(schema.get("hidden_allowed", [])) - required
            list_names = set(schema.get("lists", {}).keys())
            for campo, valor in conteudo.items():
                if campo in required or campo in optional or campo in hidden_allowed or campo in list_names:
                    continue
                if self._valor_tem_lixo_tecnico(valor):
                    self.resultado.adicionar(Erro(
                        codigo="CONT_SCHEMA_002",
                        severidade=Severidade.AVISO,
                        mensagem=f"'{doc.codigo}' — campo extra '{campo}' contém lixo técnico.",
                        documento=doc.codigo,
                    ))

            for campo in optional | hidden_allowed:
                if campo in conteudo and self._valor_tem_lixo_tecnico(conteudo[campo]):
                    self.resultado.adicionar(Erro(
                        codigo="CONT_SCHEMA_002",
                        severidade=Severidade.AVISO,
                        mensagem=f"'{doc.codigo}' — campo opcional/ocultável '{campo}' contém lixo técnico.",
                        documento=doc.codigo,
                    ))

            for campo_html in schema.get("html_fields", []):
                valor = conteudo.get(campo_html, "")
                if valor and isinstance(valor, str) and not self._tem_html_minimo(valor):
                    self.resultado.adicionar(Erro(
                        codigo="CONT_005",
                        severidade=Severidade.AVISO,
                        mensagem=(
                            f"'{doc.codigo}' — '{campo_html}' não contém HTML mínimo "
                            "(<p>, <table>, <ul>, <ol>, <div> ou <br>)."
                        ),
                        documento=doc.codigo,
                    ))

    def _verificar_obviedade(self) -> None:
        """Integra o guardrail anti-obviedade ao resultado do validator."""
        try:
            if __package__:
                obviousness_module = importlib.import_module(".obviousness_checker", __package__)
            else:
                obviousness_module = importlib.import_module("obviousness_checker")
            check_obviousness = obviousness_module.check_obviousness
            obviousness_severity = obviousness_module.ObviousnessSeverity
            report = check_obviousness(self.bp.model_dump(mode="json"))
        except Exception as exc:  # noqa: BLE001 - validator deve reportar falha interna sem traceback.
            self.resultado.adicionar(Erro(
                codigo="OBV_CHECKER_001",
                severidade=Severidade.CRITICO,
                mensagem="Falha interna ao executar o checker anti-obviedade.",
                detalhe=str(exc),
            ))
            return

        severity_map = {
            obviousness_severity.CRITICAL: Severidade.CRITICO,
            obviousness_severity.MODERATE: Severidade.MODERADO,
            obviousness_severity.WARNING: Severidade.AVISO,
        }
        for finding in report.findings:
            detail_parts = [part for part in [finding.detail, finding.path] if part]
            self.resultado.adicionar(Erro(
                codigo=finding.code,
                severidade=severity_map[finding.severity],
                mensagem=finding.message,
                detalhe=" | ".join(detail_parts) if detail_parts else None,
                documento=finding.document,
            ))

    def _calcular_risco(self) -> None:
        criticos = len(self.resultado.criticos)
        moderados = len(self.resultado.moderados)
        if criticos > 0:
            self.resultado.nivel_risco = NivelRisco.ALTO
            self.resultado.pode_gerar = False
        elif moderados >= 4:
            self.resultado.nivel_risco = NivelRisco.MEDIO_ALTO
            self.resultado.pode_gerar = False
        elif moderados >= 2:
            self.resultado.nivel_risco = NivelRisco.MEDIO
            self.resultado.pode_gerar = not self.strict
        elif moderados == 1:
            self.resultado.nivel_risco = NivelRisco.MEDIO_BAIXO
            self.resultado.pode_gerar = True
        else:
            self.resultado.nivel_risco = NivelRisco.BAIXO
            self.resultado.pode_gerar = True

    def _gerar_resumo(self) -> None:
        linhas = [
            "=" * 60,
            f"VALIDAÇÃO DE BLUEPRINT — {self.bp.titulo}",
            "=" * 60,
            f"Risco: {self.resultado.nivel_risco.value}",
            f"Pode gerar: {'SIM' if self.resultado.pode_gerar else 'NÃO'}",
            f"Críticos: {len(self.resultado.criticos)}",
            f"Moderados: {len(self.resultado.moderados)}",
            f"Avisos: {len(self.resultado.avisos)}",
        ]
        for grupo, itens in [
            ("CRÍTICOS", self.resultado.criticos),
            ("MODERADOS", self.resultado.moderados),
            ("AVISOS", self.resultado.avisos),
        ]:
            if itens:
                linhas.append(f"\n{grupo}")
                for item in itens:
                    linhas.append(f"[{item.codigo}] {item.mensagem}")
                    if item.detalhe:
                        linhas.append(f"  - {item.detalhe}")
        self.resultado.resumo = "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida um blueprint de caso antes de gerar documentos.")
    parser.add_argument("arquivo", help="Caminho para o blueprint em JSON")
    parser.add_argument("--strict", action="store_true", help="Falha também em risco Médio")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--llm-feedback", type=Path, help="Caminho para escrever llm_feedback.json")
    args = parser.parse_args()

    path = Path(args.arquivo)
    if not path.exists():
        print(f"Arquivo não encontrado: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        blueprint = Blueprint(**json.loads(path.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001 - CLI deve exibir erro de parse claro.
        print(f"Erro ao parsear blueprint: {exc}", file=sys.stderr)
        sys.exit(2)

    resultado = BlueprintValidator(blueprint, strict=args.strict).validar()
    if args.llm_feedback:
        feedback_module = importlib.import_module(".llm_feedback", __package__) if __package__ else importlib.import_module("llm_feedback")
        write_llm_feedback = feedback_module.write_llm_feedback
        build_llm_feedback = feedback_module.build_llm_feedback
        write_llm_feedback(build_llm_feedback(resultado), args.llm_feedback)

    if args.json:
        print(json.dumps({
            "nivel_risco": resultado.nivel_risco.value,
            "pode_gerar": resultado.pode_gerar,
            "criticos": [e.__dict__ for e in resultado.criticos],
            "moderados": [e.__dict__ for e in resultado.moderados],
            "avisos": [e.__dict__ for e in resultado.avisos],
        }, ensure_ascii=False, indent=2, default=str))
    else:
        print(resultado.resumo)

    sys.exit(0 if resultado.pode_gerar else 1)


if __name__ == "__main__":
    main()

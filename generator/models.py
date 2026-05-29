"""
Modelos de dados do blueprint de caso.

Define as estruturas esperadas no JSON/YAML retornado pelo LLM e consumidas pelo
validador e pelo futuro renderizador.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Dificuldade(str, Enum):
    FACIL = "facil"
    MEDIO = "medio"
    MEDIO_ALTO = "medio_alto"
    DIFICIL = "dificil"


class ModoValidacao(str, Enum):
    OFFLINE_PURO = "offline_puro"
    HIBRIDO = "hibrido"


class Intensidade(str, Enum):
    LEVE = "leve"
    MEDIA = "media"
    FORTE = "forte"
    QUASE_GABARITO = "quase_gabarito"


class TipoDocumento(str, Enum):
    PROTO = "protocolo"
    EMAIL_N = "email_narrador"
    EMAIL_I = "email_institucional"
    CHAT = "chat"
    MAPA = "mapa"
    LOG_ACESSO = "log_acesso"
    LOG_SISTEMA = "log_sistema"
    ESCALA = "escala"
    MANUAL = "manual"
    CONTR = "contrato"
    BOL = "boletim"
    DEPO = "depoimento"
    CARTAO = "cartao"
    CADAS = "cadastro_terceiros"
    EXTRA = "extrato"
    ORCAM = "orcamento"
    AUDIT = "auditoria"
    LTFECH = "linha_tempo_fechamento"
    GLOSS = "glossario"
    CRUZ = "folha_cruzamento"
    RECIBO = "recibo"
    OUTRO = "outro"


class Envelope(str, Enum):
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"


class PapelPersonagem(str, Enum):
    EXECUTOR = "executor"
    PLANEJADOR = "planejador"
    BENEFICIARIO = "beneficiario"
    NARRADOR = "narrador"
    RED_HERRING = "red_herring"
    TESTEMUNHA = "testemunha"
    CUMPLICE = "cumplice"
    INTERMEDIARIO = "intermediario"


class DirecaoEvento(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    NEGADO = "negado"
    OPERACAO = "operacao"


class Personagem(BaseModel):
    id: str = Field(..., description="ID único do personagem, ex.: '09' ou 'T-10001'.")
    nome: str
    funcao: str
    papel: PapelPersonagem
    suspeita_aparente: str = Field(..., description="Por que parece suspeito.")
    verdade: str = Field(..., description="Papel real no caso.")
    documento_ancoragem: list[str] = Field(
        default_factory=list,
        description="Códigos dos documentos que comprovam existência/papel.",
    )


class EventoLinha(BaseModel):
    data_hora: str
    evento: str
    personagem_id: Optional[str] = None
    documento_prova: str = Field(..., description="Código do documento que prova o evento.")
    confirmacao_independente: Optional[str] = Field(
        None,
        description="Código de outro documento que confirma independentemente.",
    )


class Pilar(BaseModel):
    nome: str = Field(..., description="Ex.: presença física, credencial, terminal, ação.")
    documento_principal: str = Field(..., description="Código do documento principal.")
    confirmacao: str = Field(..., description="Código do documento de confirmação.")
    personagem_id: str = Field(..., description="ID do personagem conectado ao pilar.")


class RedHerring(BaseModel):
    personagem_id: str
    motivo_aparente: str
    como_descartar: str
    documento_descarte: str = Field(..., description="Código do documento que descarta.")
    categoria: str = Field(..., description="Ex.: motivo_sem_oportunidade.")


class SaltoFinanceiro(BaseModel):
    de: str = Field(..., description="Origem, pessoa ou entidade.")
    para: str = Field(..., description="Destino, pessoa ou entidade.")
    valor_ou_item: str
    documento_prova: str = Field(..., description="Código do documento que prova o salto.")
    confirmacao_independente: Optional[str] = Field(
        None,
        description="Obrigatório no salto final.",
    )
    is_salto_final: bool = False


class Pista(BaseModel):
    descricao: str
    documento: str = Field(..., description="Código do documento.")
    o_que_sugere: str
    o_que_prova: str
    confirmacao: str = Field(..., description="Código do documento de confirmação.")
    risco_ambiguidade: str = Field(..., description="baixo | medio | alto")
    emocao_esperada: str


class Documento(BaseModel):
    codigo: str = Field(..., description="Ex.: E1-01, E2-05.")
    titulo: str
    envelope: Envelope
    tipo: TipoDocumento
    emocao_esperada: str
    objetivo_narrativo: str
    pistas_contidas: list[str] = Field(default_factory=list)
    confirma: list[str] = Field(
        default_factory=list,
        description="Códigos de documentos que este confirma.",
    )
    confirmado_por: list[str] = Field(
        default_factory=list,
        description="Códigos de documentos que confirmam este.",
    )
    red_herring_potencial: Optional[str] = None
    risco_ambiguidade: Optional[str] = None
    ids_citados: list[str] = Field(
        default_factory=list,
        description="Todos os IDs de personagens citados neste documento.",
    )
    codigos_citados: list[str] = Field(
        default_factory=list,
        description="Números/letras usados em códigos/puzzles neste documento.",
    )
    conteudo: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Dados reais que preenchem os placeholders {{VARIAVEL}} do template HTML. "
            "As chaves devem corresponder exatamente aos placeholders do template usado. "
            "Ex: {'REMETENTE_NOME': 'Helena Moraes', 'ASSUNTO': 'Urgente: sumiu...'}.",
        ),
    )


class Codigo(BaseModel):
    """Representa um código/puzzle presente nos documentos."""

    documento: str = Field(..., description="Código do documento onde aparece.")
    criterio: str = Field(..., description="Ex.: ids_personagens, datas, misto.")
    elementos: list[str] = Field(..., description="Todos os números/letras do código.")
    chave_em: str = Field(..., description="Código do documento onde está a chave.")


class Dica(BaseModel):
    numero: int
    intensidade: Intensidade
    envelope: Envelope
    condicao_uso: str
    texto: str
    o_que_desbloqueia: str


class Blueprint(BaseModel):
    """Estrutura completa do planejamento de um caso."""

    titulo: str
    subtitulo: str
    genero: str
    tom: str
    modo_validacao: ModoValidacao
    dificuldade: Dificuldade
    tempo_estimado_min: int
    numero_jogadores: str
    formato_envelopes: int = Field(..., ge=2, le=3)

    premissa: str = Field(..., description="Versão do jogador.")
    verdade_real: str = Field(..., description="O que realmente aconteceu; interno.")
    executor_id: str
    planejador_id: str
    beneficiario_id: str
    motivacao: str
    metodo_ocultacao: str
    erro_que_permite_descobrir: str
    cadeia_causal: list[str] = Field(..., min_length=3)

    personagens: list[Personagem] = Field(..., min_length=4)

    linha_tempo_real: list[EventoLinha] = Field(..., min_length=3)
    linha_tempo_percebida: list[EventoLinha] = Field(default_factory=list)
    linha_tempo_documental: list[EventoLinha] = Field(default_factory=list)

    pilares_validacao: list[Pilar] = Field(..., min_length=4, max_length=4)
    intervalo_critico_inicio: str
    intervalo_critico_fim: str

    documentos: list[Documento] = Field(..., min_length=8)

    matriz_pistas: list[Pista] = Field(..., min_length=3)
    red_herrings: list[RedHerring] = Field(..., min_length=2)

    cadeia_financeira: list[SaltoFinanceiro] = Field(default_factory=list)
    codigos: list[Codigo] = Field(default_factory=list)
    dicas: list[Dica] = Field(..., min_length=6)

    versao: str = "0.1"
    observacoes_producao: Optional[str] = None

"""
Modelos de dados do blueprint de caso.

Define as estruturas esperadas no JSON/YAML retornado pelo LLM e consumidas pelo
validador e pelo futuro renderizador.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class Dificuldade(str, Enum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"
    ESPECIALISTA = "especialista"
    MESTRE = "mestre"

    # Aliases legados normalizados para a nova escala.
    FACIL = "iniciante"
    MEDIO = "intermediario"
    MEDIO_ALTO = "avancado"
    DIFICIL = "especialista"


DIFICULDADE_ALIASES: dict[str, str] = {
    "facil": Dificuldade.INICIANTE.value,
    "medio": Dificuldade.INTERMEDIARIO.value,
    "medio_alto": Dificuldade.AVANCADO.value,
    "dificil": Dificuldade.ESPECIALISTA.value,
}


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


def normalizar_envelope(valor: object) -> str:
    envelope = valor.value if isinstance(valor, Enum) else str(valor)
    if not envelope.startswith("E") or not envelope[1:].isdigit() or int(envelope[1:]) < 1:
        raise ValueError("Envelope deve seguir o padrão E + inteiro positivo, ex.: E1, E2, E3.")
    return envelope


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


class EstiloAssinatura(str, Enum):
    FORMAL = "formal"
    ADMINISTRATIVA = "administrativa"
    COMERCIAL = "comercial"
    CURTA = "curta"
    RUBRICA = "rubrica"
    LEVE = "leve"


class RubricaEstilo(str, Enum):
    CURTA = "curta"
    SECA = "seca"
    FLUIDA = "fluida"
    MONOGRAMA = "monograma"
    ADMINISTRATIVA = "administrativa"


class LegibilidadeAssinatura(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class OrnamentoAssinatura(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


class InclinacaoAssinatura(str, Enum):
    ESQUERDA = "esquerda"
    RETA = "reta"
    DIREITA = "direita"


class PressaoAssinatura(str, Enum):
    LEVE = "leve"
    MEDIA = "media"
    FORTE = "forte"


class FluidezAssinatura(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class PerfilAssinatura(BaseModel):
    """Características editoriais de assinatura/rubrica de um personagem."""

    estilo: Optional[EstiloAssinatura] = None
    rubrica_estilo: Optional[RubricaEstilo] = None
    legibilidade: Optional[LegibilidadeAssinatura] = None
    ornamento: Optional[OrnamentoAssinatura] = None
    inclinacao: Optional[InclinacaoAssinatura] = None
    pressao: Optional[PressaoAssinatura] = None
    fluidez: Optional[FluidezAssinatura] = None
    variacao: Optional[int] = None
    override_assinatura_svg: Optional[str] = None
    override_rubrica_svg: Optional[str] = None


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
    assinatura: Optional[PerfilAssinatura] = Field(
        default=None,
        description="Perfil editorial opcional para assinatura completa e rubrica do personagem.",
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
    envelope: str

    @field_validator("envelope", mode="before")
    @classmethod
    def _normalizar_envelope(cls, valor: object) -> str:
        return valor.value if isinstance(valor, Enum) else str(valor)
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
    envelope: str

    @field_validator("envelope", mode="before")
    @classmethod
    def _normalizar_envelope(cls, valor: object) -> str:
        return valor.value if isinstance(valor, Enum) else str(valor)
    condicao_uso: str
    texto: str
    o_que_desbloqueia: str


class DicaContextual(BaseModel):
    """Dica contextual para uso interno do facilitador durante a sessão."""

    id: str = ""
    categoria: str
    fase: str
    titulo: str = ""
    condicao_uso: str = ""
    texto: str = ""
    nivel: str
    contratos_relacionados: list[str] = Field(default_factory=list)
    documentos_relacionados: list[str] = Field(default_factory=list)

    @field_validator("fase", mode="before")
    @classmethod
    def _normalizar_fase(cls, valor: object) -> str:
        return valor.value if isinstance(valor, Enum) else str(valor)


class ContratoEvidencia(BaseModel):
    id: str
    conclusao: str
    fase: str
    tipo: str
    prova_principal: Optional[str] = None
    confirmacao_independente: Optional[str] = None
    descarta_alternativas: list[str] = Field(default_factory=list)
    personagens_afetados: list[str] = Field(default_factory=list)
    acao_esperada_jogador: str = ""
    risco_ambiguidade: str
    obrigatoria_para_avanco: bool = False

    @field_validator("fase", mode="before")
    @classmethod
    def _validar_fase(cls, valor: object) -> str:
        fase = str(valor).strip()
        if fase.lower() == "final":
            return "final"
        return normalizar_envelope(fase)

    @field_validator("risco_ambiguidade")
    @classmethod
    def _validar_risco_ambiguidade(cls, valor: str) -> str:
        if valor not in {"baixo", "medio_baixo", "medio", "medio_alto", "alto"}:
            raise ValueError("risco_ambiguidade deve ser baixo, medio_baixo, medio, medio_alto ou alto")
        return valor


class AreaMapa(BaseModel):
    id: str = ""
    nome: str
    x: float
    y: float
    w: float
    h: float
    tipo: str
    acessivel: bool = True
    observacao: str = ""


class ConexaoMapa(BaseModel):
    origem: str
    destino: str
    tipo: str = "porta"
    observacao: str = ""


class MarcadorMapa(BaseModel):
    id: str
    label: str
    x: float
    y: float
    tipo: str
    documento_relacionado: str = ""
    contrato_relacionado: str = ""


class ItemLegenda(BaseModel):
    simbolo: str
    descricao: str


class MapaProcedural(BaseModel):
    id: str = ""
    titulo: str
    fase: str = "E1"
    orientacao: str = "landscape"
    largura: float
    altura: float
    areas: list[AreaMapa] = Field(default_factory=list)
    conexoes: list[ConexaoMapa] = Field(default_factory=list)
    marcadores: list[MarcadorMapa] = Field(default_factory=list)
    legenda: list[ItemLegenda] = Field(default_factory=list)

    @field_validator("fase", mode="before")
    @classmethod
    def _normalizar_fase(cls, valor: object) -> str:
        return valor.value if isinstance(valor, Enum) else str(valor)


class PersonagemVisual(BaseModel):
    personagem_id: str
    silhueta: str
    icone: str
    cor: str
    detalhes: list[str] = Field(default_factory=list)


class LocalVisual(BaseModel):
    id: str
    nome: str
    tipo: str
    icone: str
    descricao: str
    documentos_relacionados: list[str] = Field(default_factory=list)


class VisualProcedural(BaseModel):
    mapas: list[MapaProcedural] = Field(default_factory=list)
    personagens: list[PersonagemVisual] = Field(default_factory=list)
    locais: list[LocalVisual] = Field(default_factory=list)


class PlaytestMetadata(BaseModel):
    status: str = "simulado"
    rodadas: int = 0
    observacoes: list[str] = Field(default_factory=list)


class Blueprint(BaseModel):
    """Estrutura completa do planejamento de um caso."""

    titulo: str
    subtitulo: str
    genero: str
    tom: str
    modo_validacao: ModoValidacao
    dificuldade: Dificuldade

    @field_validator("dificuldade", mode="before")
    @classmethod
    def _normalizar_dificuldade(cls, valor: object) -> object:
        if isinstance(valor, str):
            return DIFICULDADE_ALIASES.get(valor.strip().lower(), valor)
        return valor
    tempo_estimado_min: int
    numero_jogadores: str
    formato_envelopes: int = Field(..., ge=1)

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
    dicas_contextuais: list[DicaContextual] = Field(default_factory=list)
    contratos_evidencia: list[ContratoEvidencia] = Field(default_factory=list)
    visual_procedural: VisualProcedural | None = None
    playtest: PlaytestMetadata | None = None

    versao: str = "0.1"
    observacoes_producao: Optional[str] = None

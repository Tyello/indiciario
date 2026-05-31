import json
import subprocess
import sys
from pathlib import Path

from generator.models import (
    Blueprint,
    Dica,
    Dificuldade,
    Documento,
    Envelope,
    EventoLinha,
    Intensidade,
    ModoValidacao,
    PapelPersonagem,
    Personagem,
    Pilar,
    Pista,
    RedHerring,
    TipoDocumento,
)
from generator.validator import BlueprintValidator, NivelRisco


ROOT = Path(__file__).resolve().parents[1]


CONTEUDO_EMAIL_VALIDO = {
    "REMETENTE_NOME": "Bruno Narrador",
    "REMETENTE_EMAIL": "bruno@ficcional.test",
    "DESTINATARIO_EMAIL": "investigacao@ficcional.test",
    "DESTINATARIO_LABEL": "Equipe de investigação",
    "DATA_HORA": "01/01/2026 10:00",
    "ASSUNTO": "Registro do incidente",
    "AVATAR_INICIAL": "B",
    "AVATAR_COR": "#1A2E4A",
    "CORPO_EMAIL": "<p>Mensagem fictícia para validação.</p>",
    "NOTA_RODAPE": "Documento fictício",
}

CONTEUDO_CARTA_VALIDO = {
    "NOME_ORGANIZACAO": "Organização Fictícia",
    "SUBTITULO_ORGANIZACAO": "Setor de Registros",
    "ENDERECO_LINHA1": "Rua Inventada, 123",
    "CONTATO": "contato@ficcional.test",
    "CNPJ": "00.000.000/0001-00",
    "COR_TOPO": "#1A2E4A",
    "LOCAL_DATA": "São Paulo, 01 de janeiro de 2026",
    "SAUDACAO": "À equipe",
    "CORPO_CARTA": "<p>Texto fictício para validação.</p>",
    "FORMULA_ENCERRAMENTO": "Atenciosamente",
    "ASSINATURA_CURSIVA": "Assinatura Fictícia",
    "NOME_ASSINANTE": "Responsável Fictício",
    "CARGO_ASSINANTE": "Coordenação",
}

CONTEUDO_PROTOCOLO_VALIDO = {**CONTEUDO_CARTA_VALIDO, "ASSUNTO": "Abertura de investigação"}

CONTEUDO_LOG_VALIDO = {
    "NOME_SISTEMA": "Sistema Fictício",
    "SUBTITULO_SISTEMA": "Exportação auditada",
    "COR_SISTEMA": "#1A2E4A",
    "COR_SISTEMA_DARK": "#0D1A2E",
    "DATA_EXPORTACAO": "01/01/2026",
    "HORA_EXPORTACAO": "10:05",
    "OPERADOR_EXPORT": "Operador Fictício",
    "HASH_REGISTRO": "abc123",
    "PERIODO_INICIO": "01/01/2026 09:00",
    "PERIODO_FIM": "01/01/2026 10:00",
    "LOCALIZACAO_SISTEMA": "Sala Fictícia",
    "TOTAL_REGISTROS": "1",
    "COLUNA_NOME": True,
    "COLUNA_TERMINAL": True,
    "COLUNA_METODO": True,
    "COLUNA_OBS": True,
    "TOTAL_USUARIOS": "1",
    "TOTAL_ENTRADAS": "1",
    "TOTAL_NEGADOS": "0",
    "TOTAL_ANOMALIAS": "0",
    "REGISTROS": [{"CLASSE_LINHA": "normal", "DATA": "01/01/2026", "HORA": "10:00", "PORTA": "A1", "ID_USUARIO": "01", "NOME_USUARIO": "Ana Operadora", "TIPO_EVENTO": "entrada", "EVENTO": "ENTRADA", "TERMINAL": "T-01", "METODO": "crachá", "OBSERVACAO": "Registro aceito"}],
}

CONTEUDO_EXTRATO_VALIDO = {
    "LOGO_SIGLA": "BF",
    "NOME_BANCO": "Banco Fictício",
    "TAGLINE_BANCO": "Extrato demonstrativo",
    "COR_BANCO": "#1A2E4A",
    "PERIODO_INICIO": "01/01/2026",
    "PERIODO_FIM": "31/01/2026",
    "DATA_GERACAO": "31/01/2026",
    "HORA_GERACAO": "10:00",
    "NOME_TITULAR": "Carla Beneficiária",
    "DOC_TITULAR": "000.000.000-00",
    "AGENCIA": "0001",
    "NUMERO_CONTA": "12345-6",
    "TIPO_CONTA": "Conta corrente",
    "SALDO_INICIAL": "R$ 0,00",
    "DATA_SALDO_INICIAL": "01/01/2026",
    "MOVIMENTACAO_LIQUIDA": "R$ 100,00",
    "COR_MOVIMENTACAO": "#14532D",
    "SALDO_FINAL": "R$ 100,00",
    "DATA_SALDO_FINAL": "31/01/2026",
    "COR_SALDO_FINAL": "#14532D",
    "TOTAL_CREDITOS": "R$ 100,00",
    "TOTAL_DEBITOS": "R$ 0,00",
    "TOTAL_LANCAMENTOS": "1",
    "NOTA_LEGAL": "Documento fictício",
    "CNPJ_BANCO": "00.000.000/0001-00",
    "ENDERECO_BANCO": "Rua Inventada, 123",
    "LANCAMENTOS": [{"CLASSE_LINHA": "credito", "DATA": "02/01/2026", "DESCRICAO": "Crédito fictício", "DETALHE": "Contrato interno", "TIPO_LOWER": "credito", "TIPO": "CRÉDITO", "DIRECAO": "entrada", "VALOR": "R$ 100,00", "COR_SALDO": "positivo", "SALDO_ACUMULADO": "R$ 100,00"}],
}


def conteudo_para_tipo(tipo: TipoDocumento) -> dict[str, object]:
    if tipo == TipoDocumento.EMAIL_N:
        return dict(CONTEUDO_EMAIL_VALIDO)
    if tipo == TipoDocumento.PROTO:
        return dict(CONTEUDO_PROTOCOLO_VALIDO)
    if tipo in {TipoDocumento.CRUZ, TipoDocumento.CONTR}:
        return dict(CONTEUDO_CARTA_VALIDO)
    if tipo in {TipoDocumento.LOG_ACESSO, TipoDocumento.LOG_SISTEMA}:
        return dict(CONTEUDO_LOG_VALIDO)
    if tipo == TipoDocumento.EXTRA:
        return dict(CONTEUDO_EXTRATO_VALIDO)
    return {"CONTEUDO_GENERICO": "Conteúdo fictício para tipo sem schema específico"}


def _personagem(id_: str, nome: str, papel: PapelPersonagem, docs: list[str] | None = None) -> Personagem:
    return Personagem(
        id=id_,
        nome=nome,
        funcao="Função fictícia",
        papel=papel,
        suspeita_aparente="Motivo aparente documentado",
        verdade="Papel real documentado",
        documento_ancoragem=docs or ["E1-02"],
    )


def _documento(codigo: str, envelope: Envelope, tipo: TipoDocumento, ids: list[str] | None = None) -> Documento:
    return Documento(
        codigo=codigo,
        titulo=f"Documento {codigo}",
        envelope=envelope,
        tipo=tipo,
        emocao_esperada="cruzamento",
        objetivo_narrativo="Documento fictício autossuficiente e offline.",
        ids_citados=ids or [],
        conteudo=conteudo_para_tipo(tipo),
    )


def blueprint_valido() -> Blueprint:
    documentos = [
        _documento("E1-01", Envelope.E1, TipoDocumento.PROTO),
        _documento("E1-02", Envelope.E1, TipoDocumento.EMAIL_N, ["01", "02"]),
        _documento("E1-03", Envelope.E1, TipoDocumento.CRUZ),
        _documento("E1-04", Envelope.E1, TipoDocumento.LOG_ACESSO, ["01"]),
        _documento("E1-05", Envelope.E1, TipoDocumento.LOG_SISTEMA, ["01"]),
        _documento("E1-06", Envelope.E1, TipoDocumento.MAPA),
        _documento("E2-01", Envelope.E2, TipoDocumento.PROTO),
        _documento("E2-02", Envelope.E2, TipoDocumento.EXTRA),
        _documento("E2-03", Envelope.E2, TipoDocumento.AUDIT),
        _documento("E2-04", Envelope.E2, TipoDocumento.CONTR),
        _documento("E2-05", Envelope.E2, TipoDocumento.CADAS),
        _documento("E2-06", Envelope.E2, TipoDocumento.LTFECH),
    ]

    return Blueprint(
        titulo="Caso Teste",
        subtitulo="Validação base",
        genero="fraude corporativa",
        tom="corporativo",
        modo_validacao=ModoValidacao.OFFLINE_PURO,
        dificuldade=Dificuldade.MEDIO,
        tempo_estimado_min=60,
        numero_jogadores="4",
        formato_envelopes=2,
        premissa="Um incidente precisa ser investigado.",
        verdade_real="A operação foi planejada e executada por personagens fictícios.",
        executor_id="01",
        planejador_id="02",
        beneficiario_id="03",
        motivacao="Benefício financeiro fictício.",
        metodo_ocultacao="Uso de exceção operacional.",
        erro_que_permite_descobrir="Registro cruzado deixou trilha.",
        cadeia_causal=["preparação", "execução", "ocultação"],
        personagens=[
            _personagem("01", "Ana Operadora", PapelPersonagem.EXECUTOR, ["E1-04", "E1-05"]),
            _personagem("02", "Bruno Narrador", PapelPersonagem.NARRADOR, ["E1-02"]),
            _personagem("03", "Carla Beneficiária", PapelPersonagem.BENEFICIARIO, ["E2-02"]),
            _personagem("04", "Diego Planejador", PapelPersonagem.PLANEJADOR, ["E2-04"]),
            _personagem("05", "Eva Suspeita", PapelPersonagem.RED_HERRING, ["E1-02"]),
            _personagem("06", "Fábio Suspeito", PapelPersonagem.RED_HERRING, ["E2-03"]),
        ],
        linha_tempo_real=[
            EventoLinha(data_hora="2026-01-01 10:00", evento="Preparação", documento_prova="E2-04", confirmacao_independente="E2-05"),
            EventoLinha(data_hora="2026-01-02 10:00", evento="Execução", documento_prova="E1-05", confirmacao_independente="E1-04"),
            EventoLinha(data_hora="2026-01-03 10:00", evento="Benefício", documento_prova="E2-02", confirmacao_independente="E2-03"),
        ],
        pilares_validacao=[
            Pilar(nome="Presença física", documento_principal="E1-04", confirmacao="E1-06", personagem_id="01"),
            Pilar(nome="Credencial", documento_principal="E1-05", confirmacao="E1-04", personagem_id="01"),
            Pilar(nome="Terminal", documento_principal="E1-05", confirmacao="E1-06", personagem_id="01"),
            Pilar(nome="Ação crítica", documento_principal="E1-05", confirmacao="E2-03", personagem_id="01"),
        ],
        intervalo_critico_inicio="2026-01-02 09:30",
        intervalo_critico_fim="2026-01-02 10:30",
        documentos=documentos,
        matriz_pistas=[
            Pista(descricao="Acesso", documento="E1-04", o_que_sugere="presença", o_que_prova="presença", confirmacao="E1-06", risco_ambiguidade="baixo", emocao_esperada="descoberta"),
            Pista(descricao="Log", documento="E1-05", o_que_sugere="ação", o_que_prova="ação", confirmacao="E1-04", risco_ambiguidade="baixo", emocao_esperada="certeza"),
            Pista(descricao="Repasse", documento="E2-02", o_que_sugere="benefício", o_que_prova="benefício", confirmacao="E2-03", risco_ambiguidade="baixo", emocao_esperada="fechamento"),
        ],
        red_herrings=[
            RedHerring(personagem_id="05", motivo_aparente="motivo plausível", como_descartar="sem oportunidade", documento_descarte="E1-04", categoria="motivo_sem_oportunidade"),
            RedHerring(personagem_id="06", motivo_aparente="oportunidade parcial", como_descartar="sem benefício", documento_descarte="E2-03", categoria="oportunidade_sem_beneficio"),
        ],
        dicas=[
            Dica(numero=1, intensidade=Intensidade.LEVE, envelope=Envelope.E1, condicao_uso="travou", texto="Compare presença com ação.", o_que_desbloqueia="pilar"),
            Dica(numero=2, intensidade=Intensidade.MEDIA, envelope=Envelope.E1, condicao_uso="travou", texto="Cruze log e mapa.", o_que_desbloqueia="pilar"),
            Dica(numero=3, intensidade=Intensidade.FORTE, envelope=Envelope.E1, condicao_uso="travou", texto="Os quatro pilares convergem.", o_que_desbloqueia="E1"),
            Dica(numero=4, intensidade=Intensidade.LEVE, envelope=Envelope.E2, condicao_uso="travou", texto="Siga o benefício.", o_que_desbloqueia="cadeia"),
            Dica(numero=5, intensidade=Intensidade.MEDIA, envelope=Envelope.E2, condicao_uso="travou", texto="Contrato e extrato conversam.", o_que_desbloqueia="planejamento"),
            Dica(numero=6, intensidade=Intensidade.QUASE_GABARITO, envelope=Envelope.E2, condicao_uso="fim", texto="Feche executor, planejador e beneficiário com documentos.", o_que_desbloqueia="gabarito"),
        ],
    )


def test_blueprint_validator_accepts_minimum_valid_blueprint():
    resultado = BlueprintValidator(blueprint_valido()).validar()
    assert resultado.nivel_risco in {NivelRisco.BAIXO, NivelRisco.MEDIO_BAIXO}
    assert resultado.pode_gerar is True


def test_blueprint_validator_accepts_single_culprit_for_all_required_roles():
    blueprint = blueprint_valido()
    blueprint.executor_id = "01"
    blueprint.planejador_id = "01"
    blueprint.beneficiario_id = "01"
    blueprint.personagens[2].papel = PapelPersonagem.TESTEMUNHA
    blueprint.personagens[3].papel = PapelPersonagem.TESTEMUNHA

    resultado = BlueprintValidator(blueprint).validar()

    assert not any(e.codigo == "ELENCO_001" for e in resultado.criticos)
    assert any(e.codigo == "ELENCO_001" for e in resultado.avisos)
    assert resultado.pode_gerar is True


def test_blueprint_validator_blocks_missing_executor():
    blueprint = blueprint_valido()
    blueprint.executor_id = "99"
    resultado = BlueprintValidator(blueprint).validar()
    assert resultado.pode_gerar is False
    assert any(e.codigo == "ELENCO_002" for e in resultado.criticos)


def test_validator_cli_json_output(tmp_path):
    path = tmp_path / "blueprint.json"
    path.write_text(blueprint_valido().model_dump_json(), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "generator.validator", str(path), "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["pode_gerar"] is True


def test_validator_cli_accepts_example_blueprint_from_examples_folder():
    exemplo_path = ROOT / "examples" / "exemplo_blueprint.json"
    assert exemplo_path.exists(), "Arquivo de exemplo esperado em examples/exemplo_blueprint.json"

    result = subprocess.run(
        [sys.executable, "generator/validator.py", str(exemplo_path)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Risco: Baixo" in result.stdout or "Risco: Médio-baixo" in result.stdout

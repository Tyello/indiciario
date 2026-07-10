import json
import subprocess
import sys
from pathlib import Path

from generator.models import (
    Blueprint,
    ConflitoCentral,
    Dica,
    Dificuldade,
    Documento,
    Envelope,
    EventoLinha,
    GuiaOperacional,
    Intensidade,
    ModoValidacao,
    ObjetivoEnvelope,
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
    "COPIA": "arquivo@ficcional.test",
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
        conflito_central=ConflitoCentral(
            pergunta_publica="Por que o incidente operacional ocorreu e quem precisa responder por ele?",
            quem_pede_apuracao="Direção fictícia",
            motivo_da_apuracao="Um registro operacional contradiz a versão inicial.",
            risco_concreto="A decisão administrativa fica suspensa até a apuração.",
            verdade_aparente="Um erro de rotina parece explicar o incidente.",
            verdade_real_resumida="A operação combinou executor, planejamento e benefício financeiro.",
        ),
        objetivos_por_envelope=[
            ObjetivoEnvelope(
                envelope="E1",
                pergunta_diegetica="Qual janela operacional explica o incidente?",
                resposta_esperada="A janela crítica converge para a credencial operacional e para registros de acesso.",
                nao_precisa_resolver_ainda=["benefício financeiro final"],
                criterio_de_avanco="Liberar E2 quando o grupo sustentar presença e ação crítica com prova e confirmação.",
                forma_diegetica_de_avanco="A direção encaminha complemento administrativo após a primeira triagem.",
                documentos_minimos=["E1-04", "E1-05"],
            ),
            ObjetivoEnvelope(
                envelope="E2",
                pergunta_diegetica="Quem planejou e se beneficiou da operação?",
                resposta_esperada="O E2 liga planejamento e benefício à cadeia documental, fechando executor, planejador e beneficiário.",
                nao_precisa_resolver_ainda=[],
                criterio_de_avanco="Encerrar quando a acusação explicar executor, planejador e beneficiário com confirmação independente.",
                forma_diegetica_de_avanco="O facilitador abre o gabarito confidencial apenas após consenso final.",
                documentos_minimos=["E2-02", "E2-03", "E2-04"],
            ),
        ],
        guia_operacional=GuiaOperacional(
            pergunta_publica="Por que o incidente operacional ocorreu e quem precisa responder por ele?",
            resposta_esperada_por_envelope=[
                ObjetivoEnvelope(
                    envelope="E1",
                    pergunta_diegetica="Qual janela operacional explica o incidente?",
                    resposta_esperada="A janela crítica converge para a credencial operacional e para registros de acesso.",
                    nao_precisa_resolver_ainda=["benefício financeiro final"],
                    criterio_de_avanco="Liberar E2 quando o grupo sustentar presença e ação crítica com prova e confirmação.",
                    forma_diegetica_de_avanco="A direção encaminha complemento administrativo após a primeira triagem.",
                    documentos_minimos=["E1-04", "E1-05"],
                ),
                ObjetivoEnvelope(
                    envelope="E2",
                    pergunta_diegetica="Quem planejou e se beneficiou da operação?",
                    resposta_esperada="O E2 liga planejamento e benefício à cadeia documental, fechando executor, planejador e beneficiário.",
                    nao_precisa_resolver_ainda=[],
                    criterio_de_avanco="Encerrar quando a acusação explicar executor, planejador e beneficiário com confirmação independente.",
                    forma_diegetica_de_avanco="O facilitador abre o gabarito confidencial apenas após consenso final.",
                    documentos_minimos=["E2-02", "E2-03", "E2-04"],
                ),
            ],
            solucao_em_5_frases=[
                "A pergunta pública é explicar o incidente e seus responsáveis.",
                "O E1 localiza a janela crítica e a credencial operacional.",
                "O E2 mostra que a cadeia documental foi planejada.",
                "A solução combina executor, planejador e beneficiário.",
                "Falsos caminhos caem por ausência de oportunidade ou benefício.",
            ],
            linha_tempo_aparente_resumo="A rotina parece ter sido apenas irregular.",
            linha_tempo_real_resumo="A preparação, execução e benefício formam uma cadeia deliberada.",
            red_herrings_e_descartes=["Eva cai por falta de oportunidade.", "Fábio cai por falta de benefício."],
            quando_usar_dicas=["Use dicas leves após travamento de leitura.", "Use dicas fortes antes do gabarito final."],
        ),
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


def test_validator_cli_writes_llm_feedback(tmp_path):
    path = tmp_path / "blueprint.json"
    feedback_path = tmp_path / "llm_feedback.json"
    path.write_text(blueprint_valido().model_dump_json(), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "generator.validator", str(path), "--llm-feedback", str(feedback_path)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
    assert feedback["status"] == "passed"


def test_validator_cli_accepts_example_blueprint_from_examples_folder():
    exemplo_path = ROOT / "examples" / "exemplo_blueprint.json"
    assert exemplo_path.exists(), "Arquivo de exemplo esperado em examples/exemplo_blueprint.json"

    result = subprocess.run(
        [sys.executable, "generator/validator.py", str(exemplo_path)],
        cwd=ROOT,
        check=False,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Risco: Baixo" in result.stdout or "Risco: Médio-baixo" in result.stdout


def test_blueprint_validator_blocks_duplicate_document_codes():
    blueprint = blueprint_valido()
    blueprint.documentos[1].codigo = blueprint.documentos[0].codigo

    resultado = BlueprintValidator(blueprint).validar()

    assert resultado.pode_gerar is False
    assert any(e.codigo == "DOC_008" for e in resultado.criticos)


def test_blueprint_aceita_dificuldade_nova_e_alias_legado():
    novo = blueprint_valido().model_dump(mode="json")
    novo["dificuldade"] = "mestre"
    assert Blueprint(**novo).dificuldade == Dificuldade.MESTRE

    legado = blueprint_valido().model_dump(mode="json")
    legado["dificuldade"] = "medio_alto"
    assert Blueprint(**legado).dificuldade == Dificuldade.AVANCADO


def test_blueprint_rejeita_dificuldade_desconhecida():
    data = blueprint_valido().model_dump(mode="json")
    data["dificuldade"] = "impossivel"
    try:
        Blueprint(**data)
    except Exception as exc:  # noqa: BLE001 - teste verifica mensagem clara do Pydantic.
        assert "dificuldade" in str(exc)
        assert "impossivel" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Dificuldade inválida deveria falhar")


def _codigos(resultado):
    return {erro.codigo for erro in resultado.erros + resultado.avisos}


def test_validator_permite_um_envelope_sem_bloqueio_por_tamanho_esperado():
    blueprint = blueprint_valido()
    blueprint.documentos = [doc for doc in blueprint.documentos if doc.envelope == "E1"] + [
        _documento("E1-07", Envelope.E1, TipoDocumento.CRUZ),
        _documento("E1-08", Envelope.E1, TipoDocumento.CONTR),
    ]
    for personagem in blueprint.personagens:
        personagem.documento_ancoragem = ["E1-02"]
    blueprint.linha_tempo_real[0].documento_prova = "E1-04"
    blueprint.linha_tempo_real[0].confirmacao_independente = "E1-05"
    blueprint.linha_tempo_real[2].documento_prova = "E1-08"
    blueprint.linha_tempo_real[2].confirmacao_independente = "E1-03"
    for pilar in blueprint.pilares_validacao:
        if pilar.confirmacao.startswith("E2"):
            pilar.confirmacao = "E1-03"
    blueprint.matriz_pistas[2].documento = "E1-08"
    blueprint.matriz_pistas[2].confirmacao = "E1-03"
    blueprint.red_herrings[1].documento_descarte = "E1-04"
    blueprint.dificuldade = Dificuldade.INICIANTE
    blueprint.formato_envelopes = 1
    blueprint.objetivos_por_envelope = blueprint.objetivos_por_envelope[:1]
    blueprint.guia_operacional.resposta_esperada_por_envelope = blueprint.guia_operacional.resposta_esperada_por_envelope[:1]

    resultado = BlueprintValidator(blueprint, strict=True).validar()

    assert "ENV_003" not in _codigos(resultado)
    assert resultado.pode_gerar is True


def test_validator_formato_envelopes_deve_bater_com_maior_envelope_real():
    blueprint = blueprint_valido()
    resultado = BlueprintValidator(blueprint).validar()
    codigos = _codigos(resultado)
    assert "ENV_004" not in codigos
    assert "ENV_005" not in codigos

    blueprint_menor_que_real = blueprint_valido()
    blueprint_menor_que_real.formato_envelopes = 1
    resultado_menor_que_real = BlueprintValidator(blueprint_menor_que_real).validar()
    assert "ENV_005" in _codigos(resultado_menor_que_real)

    blueprint_maior_que_real = blueprint_valido()
    blueprint_maior_que_real.documentos = [
        doc for doc in blueprint_maior_que_real.documentos if doc.envelope == "E1"
    ]
    blueprint_maior_que_real.formato_envelopes = 2
    resultado_maior_que_real = BlueprintValidator(blueprint_maior_que_real).validar()
    assert "ENV_004" in _codigos(resultado_maior_que_real)


def test_validator_permite_tres_envelopes_sequenciais_e_rejeita_buraco():
    blueprint = blueprint_valido()
    blueprint.formato_envelopes = 3
    blueprint.documentos.extend([
        _documento("E3-01", "E3", TipoDocumento.PROTO),
        _documento("E3-02", "E3", TipoDocumento.CONTR),
    ])
    resultado = BlueprintValidator(blueprint).validar()
    assert "ENV_003" not in _codigos(resultado)

    blueprint_sem_e2 = blueprint_valido()
    for doc in blueprint_sem_e2.documentos:
        if doc.envelope == "E2":
            doc.envelope = "E3"
            doc.codigo = doc.codigo.replace("E2", "E3")
    resultado_sem_e2 = BlueprintValidator(blueprint_sem_e2).validar()
    assert "ENV_003" in _codigos(resultado_sem_e2)


def test_validator_rejeita_envelope_invalido_e_e0():
    blueprint = blueprint_valido()
    blueprint.documentos[0].envelope = "E0"
    resultado = BlueprintValidator(blueprint).validar()
    assert "ENV_001" in _codigos(resultado)

    blueprint = blueprint_valido()
    blueprint.documentos[0].envelope = "Envelope A"
    resultado = BlueprintValidator(blueprint).validar()
    assert "ENV_001" in _codigos(resultado)


def test_contrato_evidencia_valido_e_blueprint_antigo_sem_contratos_passam():
    antigo = blueprint_valido()
    assert antigo.contratos_evidencia == []
    assert BlueprintValidator(antigo).validar().pode_gerar is True

    blueprint = blueprint_valido()
    data = blueprint.model_dump(mode="json")
    data["contratos_evidencia"] = [{
        "id": "C-E1-01",
        "conclusao": "A presença foi confirmada por dois registros independentes.",
        "fase": "final",
        "tipo": "solucao_final",
        "prova_principal": "E1-04",
        "confirmacao_independente": "E1-06",
        "descarta_alternativas": ["E1-05"],
        "personagens_afetados": ["01"],
        "acao_esperada_jogador": "cruzar log de acesso e mapa",
        "risco_ambiguidade": "baixo",
        "obrigatoria_para_avanco": True,
    }]
    blueprint = Blueprint(**data)

    resultado = BlueprintValidator(blueprint).validar()
    assert not any(codigo.startswith("CE_") for codigo in _codigos(resultado))


def test_contrato_evidencia_erros_criticos_e_alertas():
    blueprint = blueprint_valido()
    data = blueprint.model_dump(mode="json")
    data["contratos_evidencia"] = [
        {
            "id": "C-1",
            "conclusao": "Conclusão inválida.",
            "fase": "E1",
            "tipo": "oportunidade",
            "prova_principal": "E9-99",
            "confirmacao_independente": "E1-04",
            "descarta_alternativas": ["E9-98"],
            "personagens_afetados": [],
            "acao_esperada_jogador": "comparar registros",
            "risco_ambiguidade": "baixo",
            "obrigatoria_para_avanco": True,
        },
        {
            "id": "C-2",
            "conclusao": "Conclusão inválida.",
            "fase": "E1",
            "tipo": "oportunidade",
            "prova_principal": "E1-04",
            "confirmacao_independente": "E1-04",
            "descarta_alternativas": [],
            "personagens_afetados": [],
            "acao_esperada_jogador": "",
            "risco_ambiguidade": "alto",
            "obrigatoria_para_avanco": True,
        },
        {
            "id": "C-2",
            "conclusao": "E1 não deve depender de E2.",
            "fase": "E1",
            "tipo": "criterio_avanco",
            "prova_principal": "E1-04",
            "confirmacao_independente": "E2-02",
            "descarta_alternativas": [],
            "personagens_afetados": [],
            "acao_esperada_jogador": "comparar fases",
            "risco_ambiguidade": "baixo",
            "obrigatoria_para_avanco": True,
        },
        {
            "id": "C-final",
            "conclusao": "Contrato final pode usar qualquer envelope existente.",
            "fase": "final",
            "tipo": "solucao_final",
            "prova_principal": "E1-04",
            "confirmacao_independente": "E2-02",
            "descarta_alternativas": [],
            "personagens_afetados": [],
            "acao_esperada_jogador": "integrar todas as fases",
            "risco_ambiguidade": "baixo",
            "obrigatoria_para_avanco": True,
        },
    ]
    blueprint = Blueprint(**data)

    codigos = _codigos(BlueprintValidator(blueprint).validar())

    assert {"CE_002", "CE_003", "CE_005", "CE_006", "CE_007", "CE_009", "CE_010"}.issubset(codigos)
    assert "CE_004" not in codigos


def test_validator_blueprint_sem_contratos_gera_gp_006_moderado_sem_bloquear():
    blueprint = blueprint_valido()

    resultado = BlueprintValidator(blueprint).validar()

    assert resultado.pode_gerar is True
    assert any(erro.codigo == "GP_006" for erro in resultado.moderados)


def test_validator_contratos_sem_solucao_final_gera_gp_006_critico():
    blueprint = blueprint_valido()
    data = blueprint.model_dump(mode="json")
    data["contratos_evidencia"] = [{
        "id": "C-E1-01",
        "conclusao": "A presença foi confirmada.",
        "fase": "E1",
        "tipo": "oportunidade",
        "prova_principal": "E1-04",
        "confirmacao_independente": "E1-06",
        "descarta_alternativas": [],
        "personagens_afetados": ["01"],
        "acao_esperada_jogador": "comparar registros",
        "risco_ambiguidade": "baixo",
        "obrigatoria_para_avanco": True,
    }]

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert any(erro.codigo == "GP_006" for erro in resultado.criticos)


def test_validator_documento_orfao_gera_gp_003_como_aviso():
    blueprint = blueprint_valido()
    data = blueprint.model_dump(mode="json")
    data["contratos_evidencia"] = [{
        "id": "C-FINAL-01",
        "conclusao": "A solução final foi confirmada.",
        "fase": "final",
        "tipo": "solucao_final",
        "prova_principal": "E1-04",
        "confirmacao_independente": "E1-06",
        "descarta_alternativas": [],
        "personagens_afetados": ["01"],
        "acao_esperada_jogador": "comparar registros",
        "risco_ambiguidade": "baixo",
        "obrigatoria_para_avanco": True,
    }]

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert any(erro.codigo == "GP_003" for erro in resultado.avisos)
    assert not any(erro.codigo == "GP_003" for erro in resultado.criticos)


def test_validator_showcase_tecnico_nao_gera_gp_critico():
    data = json.loads((ROOT / "examples" / "showcase_tecnico.json").read_text(encoding="utf-8"))

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert not any(erro.codigo.startswith("GP_") for erro in resultado.criticos)


def test_validador_rejeita_override_assinatura_svg_inexistente() -> None:
    data = json.loads(blueprint_valido().model_dump_json())
    data["personagens"][0]["assinatura"] = {
        "estilo": "formal",
        "override_assinatura_svg": "assets/signatures/nao_existe/assinatura.svg",
    }

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert any(erro.codigo == "ASSINATURA_003" for erro in resultado.erros)


def test_validador_rejeita_override_assinatura_absoluto_ou_nao_svg() -> None:
    data = json.loads(blueprint_valido().model_dump_json())
    data["personagens"][0]["assinatura"] = {
        "estilo": "formal",
        "override_assinatura_svg": "/tmp/assinatura.svg",
        "override_rubrica_svg": "assets/signatures/vera_matos/rubrica.txt",
    }

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    codigos = {erro.codigo for erro in resultado.erros}
    assert "ASSINATURA_001" in codigos
    assert "ASSINATURA_002" in codigos


def test_validator_exige_guia_operacional_consistente_com_conflito():
    blueprint = blueprint_valido()
    blueprint.guia_operacional.pergunta_publica = "Pergunta divergente."

    resultado = BlueprintValidator(blueprint).validar()

    assert "PROG_002" in _codigos(resultado)


def test_validator_rejeita_objetivo_com_documento_de_outro_envelope():
    blueprint = blueprint_valido()
    blueprint.objetivos_por_envelope[0].documentos_minimos = ["E2-02"]

    resultado = BlueprintValidator(blueprint).validar()

    assert "PROG_009" in _codigos(resultado)


def test_validator_exige_respostas_do_guia_para_os_mesmos_envelopes():
    blueprint = blueprint_valido()
    blueprint.guia_operacional.resposta_esperada_por_envelope = blueprint.guia_operacional.resposta_esperada_por_envelope[:1]

    resultado = BlueprintValidator(blueprint).validar()

    assert "PROG_013" in _codigos(resultado)


def test_validator_bloqueia_e1_pedindo_solucao_final():
    blueprint = blueprint_valido()
    blueprint.objetivos_por_envelope[0].pergunta_diegetica = "Como descobrir o culpado final?"

    resultado = BlueprintValidator(blueprint).validar()

    assert "PROG_018" in _codigos(resultado)


def test_validator_bloqueia_e1_pedindo_solucao_completa_no_criterio():
    blueprint = blueprint_valido()
    blueprint.objetivos_por_envelope[0].criterio_de_avanco = "Liberar E2 quando o grupo formular solução completa."

    resultado = BlueprintValidator(blueprint).validar()

    assert "PROG_018" in _codigos(resultado)


def test_validator_exige_paridade_operacional_completa_no_guia():
    blueprint = blueprint_valido()
    resposta_e1 = blueprint.guia_operacional.resposta_esperada_por_envelope[0]
    resposta_e1.pergunta_diegetica = "Pergunta divergente no guia."
    resposta_e1.criterio_de_avanco = "Critério divergente no guia."
    resposta_e1.forma_diegetica_de_avanco = "Forma diegética divergente no guia."
    resposta_e1.documentos_minimos = ["E1-04"]

    resultado = BlueprintValidator(blueprint).validar()

    codigos = _codigos(resultado)
    assert "PROG_014" in codigos
    prog_014 = next(erro for erro in resultado.erros if erro.codigo == "PROG_014")
    assert "pergunta_diegetica" in (prog_014.detalhe or "")
    assert "criterio_de_avanco" in (prog_014.detalhe or "")
    assert "forma_diegetica_de_avanco" in (prog_014.detalhe or "")
    assert "documentos_minimos" in (prog_014.detalhe or "")


def test_exemplos_de_demonstracao_nao_usam_progressao_generica_ou_truncada():
    forbidden_snippets = [
        "Qual pergunta pública move",
        "Solicitante diegético definido",
        "Há inconsistências documentais",
        "A pergunta pública dá ao grupo",
        "A sequência real deve ser lida",
        "vendido pa",
        "Bruno executou a alteracao ",
    ]
    for path in [
        ROOT / "examples" / "exemplo_blueprint.json",
        ROOT / "examples" / "sinal_verde_demo_blueprint.json",
        ROOT / "examples" / "showcase_tecnico.json",
    ]:
        data = json.loads(path.read_text(encoding="utf-8"))
        structured_text = json.dumps(
            {
                "conflito_central": data["conflito_central"],
                "objetivos_por_envelope": data["objetivos_por_envelope"],
                "guia_operacional": data["guia_operacional"],
            },
            ensure_ascii=False,
        )
        for snippet in forbidden_snippets:
            assert snippet not in structured_text, path
        for value in data["conflito_central"].values():
            assert value == value.strip(), path
            assert value.endswith(".") or value.endswith("?") or value.endswith("!"), path


def test_validator_avisa_manuscrito_longo_demais() -> None:
    data = json.loads(blueprint_valido().model_dump_json())
    data["documentos"][0]["conteudo"]["ANOTACAO"] = "x" * 121
    data["documentos"][0]["conteudo"]["ANOTACAO_PERSONAGEM_ID"] = data["personagens"][0]["id"]

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert any(erro.codigo == "HAND_001" for erro in resultado.avisos)


def test_validator_bloqueia_manuscrito_com_linguagem_de_solucao() -> None:
    data = json.loads(blueprint_valido().model_dump_json())
    data["documentos"][0]["conteudo"]["ANOTACAO"] = "culpado confirmado no gabarito"
    data["documentos"][0]["conteudo"]["ANOTACAO_PERSONAGEM_ID"] = data["personagens"][0]["id"]

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert any(erro.codigo == "HAND_003" for erro in resultado.criticos)


def test_validator_assinatura_e_rubrica_procedurais_nao_sao_identicas() -> None:
    data = json.loads(blueprint_valido().model_dump_json())
    data["personagens"][0]["assinatura"] = {"estilo": "fluida", "seed": "sig-test"}

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert not any(erro.codigo == "SIG_001" for erro in resultado.erros)

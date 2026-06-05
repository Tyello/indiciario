import json
from pathlib import Path

from generator.clue_graph import analyze_clue_graph, build_clue_graph
from generator.llm_feedback import build_llm_feedback
from generator.models import Blueprint
from generator.validator import BlueprintValidator

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CASE = ROOT / "examples" / "caso_canonico_iniciante.json"


def _raw_text() -> str:
    return CANONICAL_CASE.read_text(encoding="utf-8")


def _blueprint() -> Blueprint:
    return Blueprint(**json.loads(_raw_text()))


def test_caso_canonico_carrega_como_blueprint():
    blueprint = _blueprint()

    assert blueprint.titulo == "O Desvio da Reserva Mirante"
    assert len(blueprint.documentos) == 20


def test_caso_canonico_validator_nao_gera_criticos():
    resultado = BlueprintValidator(_blueprint()).validar()

    assert resultado.criticos == []
    assert resultado.pode_gerar is True


def test_caso_canonico_nao_contem_lixo_tecnico_ou_placeholder():
    text = _raw_text()

    assert "CONTEUDO_GENERICO" not in text
    assert "{{" not in text
    assert "lorem ipsum" not in text.lower()


def test_caso_canonico_nao_depende_de_qr_link_internet_ou_app():
    text = _raw_text().lower()

    for forbidden in ["qr code", "http://", "https://", "acesse", "aplicativo"]:
        assert forbidden not in text


def test_caso_canonico_metadados_de_experiencia():
    blueprint = _blueprint()

    assert blueprint.dificuldade.value == "iniciante"
    assert blueprint.formato_envelopes == 2
    assert blueprint.modo_validacao.value == "offline_puro"
    assert blueprint.tempo_estimado_min == 70
    assert blueprint.numero_jogadores == "3 a 5"


def test_caso_canonico_tem_contratos_e_contrato_final():
    blueprint = _blueprint()

    assert blueprint.contratos_evidencia
    assert any(contrato.fase == "final" for contrato in blueprint.contratos_evidencia)


def test_caso_canonico_pilares_e1_usam_apenas_documentos_e1():
    blueprint = _blueprint()

    for pilar in blueprint.pilares_validacao:
        assert pilar.documento_principal.startswith("E1-")
        assert pilar.confirmacao.startswith("E1-")


def test_caso_canonico_contratos_obrigatorios_preservam_dificuldade_iniciante():
    blueprint = _blueprint()
    contrato_abertura = next(
        contrato
        for contrato in blueprint.contratos_evidencia
        if contrato.id == "C-E1-ABERTURA"
    )
    contratos_obrigatorios = [
        contrato
        for contrato in blueprint.contratos_evidencia
        if contrato.obrigatoria_para_avanco
    ]

    assert contrato_abertura.obrigatoria_para_avanco is False
    assert len(contratos_obrigatorios) <= 5


def test_caso_canonico_playtest_ainda_e_rascunho_pre_playtest():
    blueprint = _blueprint()

    assert blueprint.playtest is not None
    assert blueprint.playtest.status == "rascunho_pre_playtest"
    assert blueprint.playtest.rodadas == 0
    assert blueprint.playtest.observacoes == []


def test_caso_canonico_graph_report_nao_falha():
    blueprint = _blueprint()
    report = analyze_clue_graph(build_clue_graph(blueprint), blueprint)

    assert report["status"] != "failed"
    assert not any(issue["severity"] == "critical" for issue in report["issues"])


def test_caso_canonico_llm_feedback_nao_exige_revisao_por_critico():
    blueprint = _blueprint()
    validation = BlueprintValidator(blueprint).validar()
    graph_report = analyze_clue_graph(build_clue_graph(blueprint), blueprint)

    feedback = build_llm_feedback(validation, graph_report=graph_report)

    assert feedback["status"] != "needs_revision"
    assert feedback["critical_count"] == 0


def test_caso_canonico_hardening_editorial_pre_playtest():
    blueprint = _blueprint()
    e101 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-01")
    e106 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-06")
    e106 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-06")
    e108 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-08")
    e207 = next(doc for doc in blueprint.documentos if doc.codigo == "E2-07")

    assert "para abrir o segundo envelope" not in str(e101.conteudo).lower()
    assert "a inversão torna" not in str(e106.conteudo).lower()
    assert e108.tipo.value == "manual"
    assert "USR-022" in str(e108.conteudo)
    assert "USR-MA-022" not in str(e108.conteudo)
    assert "TERM-ADM-03" in str(e108.conteudo)
    assert "SETOR-06" not in str(e108.conteudo)
    assert "SETOR-08 — Galeria / Vitrine interna" in str(e108.conteudo)
    assert "SETOR-06 Administração/terminal" not in str(e108.conteudo)
    assert "conclusão técnica" not in str(e207.conteudo).lower()
    assert "fechar a solução" not in e207.objetivo_narrativo.lower()
    assert "sem apontar autoria" in e207.objetivo_narrativo.lower()

    for documento in blueprint.documentos:
        if documento.codigo in {"E1-04", "E1-05"}:
            for registro in documento.conteudo["REGISTROS"]:
                assert registro["CLASSE_LINHA"] != "highlight"

    assert any(personagem.nome == "Vera Matos" for personagem in blueprint.personagens)
    visual_ids = {card.personagem_id for card in blueprint.visual_procedural.personagens}  # type: ignore[union-attr]
    assert {"03", "04", "05", "06", "07"}.issubset(visual_ids)
    local_ids = {local.id for local in blueprint.visual_procedural.locais}  # type: ignore[union-attr]
    assert {
        "guarita",
        "doca_servico",
        "reserva_tecnica_a",
        "reserva_tecnica_b",
        "sala_seguranca",
    }.issubset(local_ids)


def test_caso_canonico_e1_distribui_suspeitas_sem_cravar_marina():
    blueprint = _blueprint()
    e104 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-04")
    e105 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-05")

    registros_log = {
        registro["HORA"]: registro for registro in e104.conteudo["REGISTROS"]
    }
    saida_doca = registros_log["19h57"]

    assert saida_doca["PORTA"] == "P-04"
    assert saida_doca["TIPO_EVENTO"] == "SAIDA"
    assert saida_doca["ID_USUARIO"] == "OS-0147/2026"
    consulta_os = registros_log["20h08"]
    assert consulta_os["ID_USUARIO"] == "TERM-ADM-03"
    assert "Sensor" in saida_doca["TERMINAL"]
    assert "usuário nominal" in saida_doca["OBSERVACAO"]

    texto_e1 = f"{e104.objetivo_narrativo} {e105.objetivo_narrativo} {e104.pistas_contidas} {e105.pistas_contidas}"
    for suspeito in ["Marina", "Otávio", "Lia", "Tadeu"]:
        assert suspeito not in str(e104.conteudo)
    assert "OS 0147/2026" in texto_e1

    assert "sem tradução nominal" in e104.objetivo_narrativo
    assert "escala não explica sozinha" not in str(e105.conteudo)
    assert "Cobertura de suportes anotada" in str(e105.conteudo)


def test_caso_canonico_e1_falsos_caminhos_tem_limites_justos():
    blueprint = _blueprint()
    e104 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-04")
    e105 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-05")
    e106 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-06")
    e108 = next(doc for doc in blueprint.documentos if doc.codigo == "E1-08")

    assert any(
        registro["ID_USUARIO"] == "USR-066" and registro["TIPO_EVENTO"] == "NEGADO"
        for registro in e104.conteudo["REGISTROS"]
    )
    assert (
        "NEGADO</strong> registra tentativa sem abertura"
        in e108.conteudo["CORPO_CARTA"]
    )
    assert "não autoriza Reserva Técnica B" not in str(e105.conteudo)
    assert "não movimentar acervo sozinho" not in str(e105.conteudo)
    assert "Consulta administrativa vinculada à OS 0147/2026" in str(e105.conteudo)
    assert "BANC-REG-01" in str(e106.conteudo)
    assert "Divergências registradas para nova vistoria técnica." in str(e106.conteudo)
    assert "estrutura de leitura de E1-05" not in str(e106.conteudo)
    assert "não comprova abertura de porta" not in str(e106.conteudo)


def test_caso_canonico_e2_remove_mapa_interno_e_mantem_propostas_individuais():
    blueprint = _blueprint()
    codigos = {doc.codigo for doc in blueprint.documentos}
    e201 = next(doc for doc in blueprint.documentos if doc.codigo == "E2-01")
    e204 = next(doc for doc in blueprint.documentos if doc.codigo == "E2-04")

    assert "E2-03" not in codigos
    assert e201.confirma == ["E2-02", "E2-04"]
    assert e201.confirmado_por == ["E2-02", "E2-04"]
    assert "aprovado como pacote único" not in e201.conteudo["CORPO_CARTA"]
    assert "aprovado por Otávio Salles às 16h05" not in e201.conteudo["CORPO_CARTA"]

    propostas = {
        doc.titulo
        for doc in blueprint.documentos
        if doc.codigo in {"E2-09", "E2-10", "E2-11", "E2-12"}
    }
    assert propostas == {
        "Orçamento Ateliê Pedra Clara",
        "Orçamento Conserva Sul Restauro",
        "Proposta LogisArte Transportes",
        "Proposta Mirante Norte Consultoria",
    }
    for proposta in [
        doc
        for doc in blueprint.documentos
        if doc.codigo in {"E2-09", "E2-10", "E2-11", "E2-12"}
    ]:
        assert len(proposta.conteudo["ITENS"]) == 1
        assert not proposta.conteudo.get("HAS_QUADRO_EMPRESAS")
        assert proposta.confirma == []
        texto = str(proposta.conteudo).lower()
        assert "mapa" not in texto
        assert "comparação administrativa" not in texto
        assert "documento interno separado" not in texto

    assert e204.conteudo["TOTAL_LANCAMENTOS"] == "6"
    assert len(e204.conteudo["LANCAMENTOS"]) == 6
    descricoes = " ".join(
        lancamento["DESCRICAO"] for lancamento in e204.conteudo["LANCAMENTOS"]
    )
    assert "Conserva Sul Restauro" in descricoes
    assert "Ateliê Pedra Clara" in descricoes
    assert "LogisArte Transportes" in descricoes
    assert "Mirante Norte Consultoria" in descricoes


def test_caso_canonico_documentos_de_jogador_nao_tem_handholding_comercial():
    text = _raw_text().lower()

    for forbidden in [
        "mapa interno de propostas",
        "comparação exige",
        "recibo, extrato e conversa interna",
        "preço isolado não decide",
        "documento interno separado",
        "aprovado por otávio salles às 16h05",
    ]:
        assert forbidden not in text


INTERMEDIATE_CASE = ROOT / "examples" / "caso_canonico_intermediario.json"


def _raw_intermediate_text() -> str:
    return INTERMEDIATE_CASE.read_text(encoding="utf-8")


def _intermediate_blueprint() -> Blueprint:
    return Blueprint(**json.loads(_raw_intermediate_text()))


def test_caso_canonico_intermediario_existe_e_valida_strict():
    assert INTERMEDIATE_CASE.exists()

    resultado = BlueprintValidator(_intermediate_blueprint(), strict=True).validar()

    assert resultado.criticos == []
    assert resultado.moderados == []
    assert resultado.pode_gerar is True


def test_caso_canonico_intermediario_metadados_publicos():
    blueprint = _intermediate_blueprint()

    assert blueprint.titulo == "O Último Brinde do Hotel Aurora"
    assert blueprint.dificuldade.value == "intermediario"
    assert blueprint.formato_envelopes == 2
    assert blueprint.modo_validacao.value == "offline_puro"
    assert len({doc.envelope for doc in blueprint.documentos}) == 2
    assert len([doc for doc in blueprint.documentos if doc.envelope == "E1"]) == 9
    assert len([doc for doc in blueprint.documentos if doc.envelope == "E2"]) == 8


def test_caso_canonico_intermediario_nao_usa_mapa_ou_planta():
    blueprint = _intermediate_blueprint()

    assert all(doc.tipo.value != "mapa" for doc in blueprint.documentos)
    assert blueprint.visual_procedural is not None
    assert blueprint.visual_procedural.mapas == []
    assert "planta" not in _raw_intermediate_text().lower()


def test_caso_canonico_intermediario_nao_substitui_iniciante():
    iniciante = _blueprint()
    intermediario = _intermediate_blueprint()

    assert iniciante.titulo == "O Desvio da Reserva Mirante"
    assert iniciante.dificuldade.value == "iniciante"
    assert intermediario.titulo != iniciante.titulo


def test_caso_canonico_intermediario_jogador_sem_voz_de_autor():
    blueprint = _intermediate_blueprint()
    forbidden = [
        "compare com",
        "a confirmação depende",
        "isso prova que",
        "não decide sozinho",
        "a solução é",
        "o culpado",
        "red herring",
        "gabarito",
    ]

    for documento in blueprint.documentos:
        texto = f"{documento.titulo} {documento.conteudo}".lower()
        for termo in forbidden:
            assert termo not in texto, documento.codigo


def test_casos_canonicos_declaram_progressao_estruturada():
    for blueprint in [_blueprint(), _intermediate_blueprint()]:
        assert blueprint.conflito_central.pergunta_publica
        assert blueprint.guia_operacional.pergunta_publica == blueprint.conflito_central.pergunta_publica
        assert len(blueprint.objetivos_por_envelope) == blueprint.formato_envelopes
        assert {objetivo.envelope for objetivo in blueprint.objetivos_por_envelope} == {"E1", "E2"}
        for objetivo in blueprint.objetivos_por_envelope:
            assert objetivo.pergunta_diegetica
            assert objetivo.resposta_esperada
            assert objetivo.criterio_de_avanco
            assert objetivo.forma_diegetica_de_avanco
            assert objetivo.documentos_minimos
        assert len(blueprint.guia_operacional.solucao_em_5_frases) == 5

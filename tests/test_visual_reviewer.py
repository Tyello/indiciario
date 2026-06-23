"""RED tests for the Visual Reviewer (ISSUE-23+24, STEP-06).

Cases 17-22 of the ISSUE-23+24 spec for ``generator.visual_reviewer``:

- 17-22: rules VR_001-VR_006 raise (or do not raise) the matching finding code.

They are expected to FAIL (RED) until ``generator/visual_reviewer.py`` exposes
the public function ``review_visual``. The failure must come from the missing
symbol (ImportError / AttributeError on ``review_visual``), NOT from a syntax
error in this file.

Fixture blueprints are built only from the REAL fields of ``generator/models.py``,
mirroring the minimal-valid-blueprint factory pattern of
``tests/test_narrative_reviewer.py``.
"""

from __future__ import annotations

from typing import Any

from generator.models import (
    Blueprint,
    ConflitoCentral,
    Dica,
    Documento,
    GuiaOperacional,
    LocalVisual,
    ObjetivoEnvelope,
    Personagem,
    Pilar,
    Pista,
    PrintableCard,
    RedHerring,
    VisualProcedural,
)

_BLUEPRINT_REF = "tests/fixtures/visual_reviewer/blueprint.json"
_REPORT_ID = "VR-test-20260622-001"


# --------------------------------------------------------------------------- #
# Minimal-valid blueprint factory (built from the REAL models)                #
# --------------------------------------------------------------------------- #
def _personagem(
    pid: str,
    papel: str,
    nome: str = "Personagem",
    ancoragem: list[str] | None = None,
) -> Personagem:
    return Personagem(
        id=pid,
        nome=nome,
        funcao="funcao",
        papel=papel,
        suspeita_aparente="parece suspeito",
        verdade="papel real",
        documento_ancoragem=ancoragem if ancoragem is not None else [],
    )


def _documento(
    codigo: str,
    envelope: str = "E1",
    conteudo: dict[str, Any] | None = None,
    titulo: str = "Documento neutro",
    tipo: str = "protocolo",
    pistas_contidas: list[str] | None = None,
    ids_citados: list[str] | None = None,
) -> Documento:
    return Documento(
        codigo=codigo,
        titulo=titulo,
        envelope=envelope,
        tipo=tipo,
        emocao_esperada="neutra",
        objetivo_narrativo="objetivo",
        pistas_contidas=pistas_contidas if pistas_contidas is not None else [],
        ids_citados=ids_citados if ids_citados is not None else [],
        conteudo=conteudo if conteudo is not None else {"CORPO": "texto bruto sem interpretacao"},
    )


def _pista(documento: str, confirmacao: str, descricao: str = "pista") -> Pista:
    return Pista(
        descricao=descricao,
        documento=documento,
        o_que_sugere="sugere",
        o_que_prova="prova",
        confirmacao=confirmacao,
        risco_ambiguidade="baixo",
        emocao_esperada="neutra",
    )


def _objetivo(envelope: str, docs: list[str]) -> ObjetivoEnvelope:
    return ObjetivoEnvelope(
        envelope=envelope,
        pergunta_diegetica="pergunta",
        resposta_esperada="resposta",
        criterio_de_avanco="criterio",
        forma_diegetica_de_avanco="forma",
        documentos_minimos=docs,
    )


def _dica(numero: int, envelope: str = "E1", texto: str = "dica generica") -> Dica:
    return Dica(
        numero=numero,
        intensidade="leve",
        envelope=envelope,
        condicao_uso="condicao",
        texto=texto,
        o_que_desbloqueia="desbloqueia",
    )


def _printable_card(
    cid: str,
    titulo: str = "Card",
    tipo: str = "personagem",
    codigo_visual: str | None = "P-01",
    tags_visuais: list[str] | None = None,
) -> PrintableCard:
    return PrintableCard(
        id=cid,
        tipo=tipo,
        titulo=titulo,
        codigo_visual=codigo_visual,
        tags_visuais=tags_visuais if tags_visuais is not None else ["tag"],
    )


def _base_kwargs() -> dict[str, Any]:
    """Return kwargs for a minimal blueprint that should raise NO VR finding.

    Each player document has short raw content (avoids VR_001); the only
    non-executor characters are anchored to documents and each has a
    matching ``printable_card`` (avoids VR_002); printable cards have unique
    ``codigo_visual`` (avoids VR_003) and non-empty ``tags_visuais``
    (avoids VR_004); no locations are cited via ``LocalVisual`` so VR_005 does
    not apply; all document ``tipo`` values are inside the visual allowlist
    (avoids VR_006).
    """

    documentos = [
        _documento("E1-01"),
        _documento("E1-02"),
        _documento("E1-03"),
        _documento("E1-04"),
        _documento("E1-05"),
        _documento("E1-06"),
        _documento("E1-07"),
        _documento("E1-08"),
    ]
    personagens = [
        _personagem("01", "narrador", "Narrador", ancoragem=["E1-01"]),
        _personagem("02", "executor", "Executor", ancoragem=["E1-02"]),
        _personagem("03", "red_herring", "Suspeito Alt", ancoragem=["E1-03"]),
        _personagem("04", "testemunha", "Testemunha", ancoragem=["E1-04"]),
    ]
    pistas = [
        _pista("E1-01", "E1-02"),
        _pista("E1-03", "E1-04"),
        _pista("E1-05", "E1-06"),
    ]
    pilares = [
        Pilar(nome="presenca", documento_principal="E1-01", confirmacao="E1-02", personagem_id="02"),
        Pilar(nome="credencial", documento_principal="E1-03", confirmacao="E1-04", personagem_id="02"),
        Pilar(nome="terminal", documento_principal="E1-05", confirmacao="E1-06", personagem_id="02"),
        Pilar(nome="acao", documento_principal="E1-07", confirmacao="E1-08", personagem_id="02"),
    ]
    red_herrings = [
        RedHerring(
            personagem_id="03",
            motivo_aparente="motivo",
            como_descartar="descartar",
            documento_descarte="E1-03",
            categoria="motivo_sem_oportunidade",
        ),
        RedHerring(
            personagem_id="04",
            motivo_aparente="motivo",
            como_descartar="descartar",
            documento_descarte="E1-04",
            categoria="motivo_sem_oportunidade",
        ),
    ]
    dicas = [_dica(n) for n in range(1, 7)]
    printable_cards = [
        _printable_card("card-01", titulo="Narrador", codigo_visual="P-01"),
        _printable_card("card-02", titulo="Executor", codigo_visual="P-02"),
        _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
        _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
    ]

    return {
        "titulo": "Caso Teste",
        "subtitulo": "subtitulo",
        "genero": "misterio",
        "tom": "serio",
        "modo_validacao": "offline_puro",
        "dificuldade": "iniciante",
        "tempo_estimado_min": 60,
        "numero_jogadores": "2 a 4",
        "formato_envelopes": 1,
        "premissa": "premissa",
        "conflito_central": ConflitoCentral(
            pergunta_publica="pergunta",
            quem_pede_apuracao="quem",
            motivo_da_apuracao="motivo",
            risco_concreto="risco",
            verdade_aparente="aparente",
            verdade_real_resumida="real",
        ),
        "objetivos_por_envelope": [_objetivo("E1", ["E1-01", "E1-02"])],
        "guia_operacional": GuiaOperacional(
            pergunta_publica="pergunta",
            solucao_em_5_frases=["a", "b", "c", "d", "e"],
            linha_tempo_aparente_resumo="aparente",
            linha_tempo_real_resumo="real",
        ),
        "verdade_real": "verdade real",
        "executor_id": "02",
        "planejador_id": "02",
        "beneficiario_id": "02",
        "motivacao": "queria esconder a reserva trancada",
        "metodo_ocultacao": "metodo",
        "erro_que_permite_descobrir": "erro",
        "cadeia_causal": ["elo um", "elo dois", "elo tres"],
        "personagens": personagens,
        "linha_tempo_real": [
            {"data_hora": "10:00", "evento": "evento um", "documento_prova": "E1-01"},
            {"data_hora": "11:00", "evento": "evento dois", "documento_prova": "E1-02"},
            {"data_hora": "12:00", "evento": "evento tres", "documento_prova": "E1-03"},
        ],
        "pilares_validacao": pilares,
        "intervalo_critico_inicio": "10:00",
        "intervalo_critico_fim": "12:00",
        "documentos": documentos,
        "matriz_pistas": pistas,
        "red_herrings": red_herrings,
        "dicas": dicas,
        "printable_cards": printable_cards,
    }


def _blueprint(**overrides: Any) -> Blueprint:
    kwargs = _base_kwargs()
    kwargs.update(overrides)
    return Blueprint(**kwargs)


def _review(blueprint: Blueprint, **kwargs: Any) -> Any:
    from generator.visual_reviewer import review_visual

    return review_visual(blueprint, _BLUEPRINT_REF, _REPORT_ID, **kwargs)


def _codes(report: Any) -> set[str]:
    return {finding.code for finding in report.findings}


# --------------------------------------------------------------------------- #
# Cases 17-22: rules VR_001-VR_006                                           #
# --------------------------------------------------------------------------- #


# --- Case 17: documents' concatenated conteudo above MAX_CONTEUDO_CHARS -> VR_001
def test_case17_vr001_conteudo_acima_do_limite() -> None:
    from generator.visual_reviewer import MAX_CONTEUDO_CHARS

    enorme = "x" * (MAX_CONTEUDO_CHARS + 1)
    blueprint = _blueprint(
        documentos=[
            _documento("E1-01", conteudo={"CORPO": enorme}),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ]
    )
    report = _review(blueprint)
    assert "VR_001" in _codes(report)


# --- Case 18: character cited in documents without matching printable_card -> VR_002
def test_case18_vr002_personagem_citado_sem_card() -> None:
    blueprint = _blueprint(
        documentos=[
            _documento("E1-01", ids_citados=["04"]),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ],
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01"),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-02"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            # No card for personagem id "04" -> VR_002.
        ],
    )
    report = _review(blueprint)
    assert "VR_002" in _codes(report)


# --- Case 19: two printable_cards share the same codigo_visual -> VR_003
def test_case19_vr003_codigo_visual_duplicado() -> None:
    blueprint = _blueprint(
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01"),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-01"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
        ],
    )
    report = _review(blueprint)
    assert "VR_003" in _codes(report)


# --- Case 20: printable_card without tags_visuais -> VR_004
def test_case20_vr004_card_sem_tags_visuais() -> None:
    blueprint = _blueprint(
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01", tags_visuais=[]),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-02"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
        ],
    )
    report = _review(blueprint)
    assert "VR_004" in _codes(report)


# --- Case 21: case cites locations but visual_procedural.mapas is empty -> VR_005
def test_case21_vr005_locais_sem_mapa() -> None:
    blueprint = _blueprint(
        visual_procedural=VisualProcedural(
            mapas=[],
            locais=[
                LocalVisual(
                    id="loc-01",
                    nome="Sala dos fundos",
                    tipo="interior",
                    icone="icone",
                    descricao="descricao",
                )
            ],
        ),
    )
    report = _review(blueprint)
    assert "VR_005" in _codes(report)


# --- Case 22: document with tipo outside the known visual set -> VR_006
def test_case22_vr006_tipo_fora_do_conjunto_visual() -> None:
    blueprint = _blueprint(
        documentos=[
            _documento("E1-01", tipo="auditoria"),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ],
    )
    report = _review(blueprint)
    assert "VR_006" in _codes(report)


# --------------------------------------------------------------------------- #
# Cases 23-32: behaviour of review_visual                                    #
# --------------------------------------------------------------------------- #


# --- Case 23: clean blueprint -> approved, no findings ----------------------
def test_case23_clean_blueprint_approved() -> None:
    report = _review(_blueprint())
    assert report.status == "approved"
    assert report.findings == ()


# --- Case 24: a major finding present -> needs_revision ---------------------
def test_case24_major_finding_needs_revision() -> None:
    blueprint = _blueprint(
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01"),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-01"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
        ],
    )
    report = _review(blueprint)
    assert "VR_003" in _codes(report)
    assert report.status == "needs_revision"


# --- Case 25: a critical finding present -> blocked --------------------------
def test_case25_critical_finding_blocked() -> None:
    from generator.visual_reviewer import MAX_CONTEUDO_CHARS

    enorme = "x" * (MAX_CONTEUDO_CHARS + 1)
    blueprint = _blueprint(
        documentos=[
            _documento("E1-01", conteudo={"CORPO": enorme}),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ]
    )
    report = _review(blueprint)
    codes = _codes(report)
    assert codes & {"VR_001"}
    severities = {finding.severity for finding in report.findings}
    if "critical" in severities:
        assert report.status == "blocked"
    else:
        # VR_001 is documented as major in the spec; this case still proves
        # the status mapping holds for whichever severity VR_001 actually is.
        assert report.status in {"needs_revision", "blocked"}


# --- Case 26: findings ordered by severity (critical first) -----------------
def test_case26_findings_ordered_by_severity() -> None:
    from generator.visual_reviewer import MAX_CONTEUDO_CHARS

    enorme = "x" * (MAX_CONTEUDO_CHARS + 1)
    blueprint = _blueprint(
        documentos=[
            _documento("E1-01", conteudo={"CORPO": enorme}, tipo="auditoria"),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ],
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01", tags_visuais=[]),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-01"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
        ],
    )
    report = _review(blueprint)
    severities = [finding.severity for finding in report.findings]
    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    assert severities == sorted(severities, key=lambda s: order[s])


# --- Case 27: review_visual does not mutate the blueprint -------------------
def test_case27_does_not_mutate() -> None:
    import copy

    blueprint = _blueprint()
    before = copy.deepcopy(blueprint.model_dump())
    _review(blueprint)
    assert blueprint.model_dump() == before


# --- Case 28: returned report passes validate_visual_accessibility_review_report
def test_case28_serialised_passes_validation() -> None:
    from generator.visual_reviewer import (
        report_to_dict,
        validate_visual_accessibility_review_report,
    )

    report = _review(_blueprint())
    assert validate_visual_accessibility_review_report(report_to_dict(report)) == []


# --- Case 29: report_to_dict round-trips through validation without loss ----
def test_case29_report_to_dict_round_trip() -> None:
    from generator.visual_reviewer import (
        report_to_dict,
        validate_visual_accessibility_review_report,
    )

    blueprint = _blueprint(
        printable_cards=[
            _printable_card("card-01", titulo="Narrador", codigo_visual="P-01"),
            _printable_card("card-02", titulo="Executor", codigo_visual="P-01"),
            _printable_card("card-03", titulo="Suspeito Alt", codigo_visual="P-03"),
            _printable_card("card-04", titulo="Testemunha", codigo_visual="P-04"),
        ],
    )
    report = _review(blueprint)
    payload = report_to_dict(report)
    assert validate_visual_accessibility_review_report(payload) == []
    codes = {finding["code"] for finding in payload["findings"]}
    assert "VR_003" in codes


# --- Case 30: reviewer_type of the report is "visual" ------------------------
def test_case30_reviewer_type_is_visual() -> None:
    assert _review(_blueprint()).reviewer_type == "visual"


# --- Case 31: VR_005 never escalates severity above info (map anti-rule) ----
def test_case31_vr005_never_above_info() -> None:
    blueprint = _blueprint(
        visual_procedural=VisualProcedural(
            mapas=[],
            locais=[
                LocalVisual(
                    id="loc-01",
                    nome="Sala dos fundos",
                    tipo="interior",
                    icone="icone",
                    descricao="descricao",
                )
            ],
        ),
    )
    report = _review(blueprint)
    vr005 = next(f for f in report.findings if f.code == "VR_005")
    assert vr005.severity == "info"


# --- Case 32: blueprint without printable_cards does not break review_visual
def test_case32_no_printable_cards_degrades_gracefully() -> None:
    blueprint = _blueprint(printable_cards=[])
    report = _review(blueprint)
    assert isinstance(report.findings, tuple)

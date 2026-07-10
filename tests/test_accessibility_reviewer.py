"""RED tests for the Accessibility Reviewer (ISSUE-23+24, STEP-09).

Cases 33-38 of the ISSUE-23 spec for ``generator.accessibility_reviewer``:

- 33: AR_001 (major) — envelope com mais de ``MAX_DOCS_PER_ENVELOPE`` documentos.
- 34: AR_002 (major) — documento com ``conteudo`` acima de ``MAX_CONTEUDO_CHARS``.
- 35: AR_003 (minor) — printable_card sem ``subtitulo`` E sem ``descricao_curta``.
- 36: AR_004 (minor) — documento com mais de ``MAX_CROSS_REFS`` códigos/ids citados.
- 37: AR_005 (info) — documento sem título/assunto identificável no ``conteudo``.
- 38: AR_006 (major) — caso sem nenhum ``printable_card``.

They are expected to FAIL (RED) until ``generator/accessibility_reviewer.py``
exists and exposes ``review_accessibility``. The failure must come from the
missing module (ModuleNotFoundError: generator.accessibility_reviewer), NOT
from a syntax error in this file.

Construction notes (REAL fields of ``generator/models.py`` only):

- ``Documento`` requires ``codigo``, ``titulo``, ``envelope``, ``tipo``
  (``TipoDocumento``), ``emocao_esperada``, ``objetivo_narrativo``. Optional
  ``ids_citados``, ``codigos_citados``, ``conteudo`` default to empty.
- ``PrintableCard`` requires ``id``, ``tipo`` (``TipoPrintableCard``),
  ``titulo``. ``subtitulo``/``descricao_curta``/``codigo_visual`` are
  ``Optional[str] = None``.
- ``Blueprint.printable_cards`` defaults to an empty list.
- This module reuses the minimal-valid blueprint factory pattern from
  ``tests/test_evidence_reviewer.py`` (cases 46-70), adapted to also carry
  ``printable_cards`` for AR_003/AR_006.
"""

from __future__ import annotations

from typing import Any


from generator.models import (
    Blueprint,
    ConflitoCentral,
    Dica,
    Documento,
    GuiaOperacional,
    ObjetivoEnvelope,
    Personagem,
    Pilar,
    Pista,
    PrintableCard,
    RedHerring,
)

_BLUEPRINT_REF = "tests/fixtures/accessibility_reviewer/blueprint.json"
_REPORT_ID = "AR-test-20260620-001"


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
    ids_citados: list[str] | None = None,
    codigos_citados: list[str] | None = None,
) -> Documento:
    return Documento(
        codigo=codigo,
        titulo=titulo,
        envelope=envelope,
        tipo=tipo,
        emocao_esperada="neutra",
        objetivo_narrativo="objetivo",
        pistas_contidas=[],
        ids_citados=ids_citados if ids_citados is not None else [],
        codigos_citados=codigos_citados if codigos_citados is not None else [],
        conteudo=conteudo if conteudo is not None else {"CORPO": "texto bruto"},
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
    subtitulo: str | None = "subtitulo",
    descricao_curta: str | None = "descricao curta",
    titulo: str = "Card",
    tipo: str = "personagem",
) -> PrintableCard:
    return PrintableCard(
        id=cid,
        tipo=tipo,
        titulo=titulo,
        subtitulo=subtitulo,
        descricao_curta=descricao_curta,
    )


def _base_kwargs() -> dict[str, Any]:
    """Return kwargs for a minimal blueprint that should raise NO AR finding."""

    documentos = [_documento(f"E1-0{n}") for n in range(1, 9)]
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
        _pista("E1-07", "E1-08"),
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
    printable_cards = [_printable_card("CARD-01")]

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
        "motivacao": "queria esconder a reserva",
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
        "contratos_evidencia": [],
        "printable_cards": printable_cards,
    }


def _blueprint(**overrides: Any) -> Blueprint:
    kwargs = _base_kwargs()
    kwargs.update(overrides)
    return Blueprint(**kwargs)


# --------------------------------------------------------------------------- #
# Cases 33-38: rules AR_001-AR_006                                            #
#                                                                              #
# All assertions below import ``review_accessibility`` lazily inside the test #
# body so the module-level import above can assert the RED precondition      #
# (module does not exist yet) without aborting collection of this file.      #
# --------------------------------------------------------------------------- #


# --- Case 33: envelope with more than MAX_DOCS_PER_ENVELOPE docs -> AR_001 --
def test_case33_ar001_envelope_too_many_docs() -> None:
    from generator.accessibility_reviewer import MAX_DOCS_PER_ENVELOPE, review_accessibility

    documentos = [_documento(f"E1-{n:02d}") for n in range(1, MAX_DOCS_PER_ENVELOPE + 2)]
    blueprint = _blueprint(documentos=documentos)
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_001" in codes
    ar001 = next(f for f in report.findings if f.code == "AR_001")
    assert ar001.severity == "major"


# --- Case 34: documento with conteudo above MAX_CONTEUDO_CHARS -> AR_002 ----
def test_case34_ar002_conteudo_too_long() -> None:
    from generator.accessibility_reviewer import MAX_CONTEUDO_CHARS, review_accessibility

    documentos = [_documento(f"E1-0{n}") for n in range(1, 9)]
    documentos[0] = _documento(
        "E1-01", conteudo={"CORPO": "x" * (MAX_CONTEUDO_CHARS + 1)}
    )
    blueprint = _blueprint(documentos=documentos)
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_002" in codes
    ar002 = next(f for f in report.findings if f.code == "AR_002")
    assert ar002.severity == "major"


# --- Case 35: printable_card without subtitulo AND without descricao_curta --
def test_case35_ar003_card_without_subtitulo_and_descricao() -> None:
    from generator.accessibility_reviewer import review_accessibility

    blueprint = _blueprint(
        printable_cards=[
            _printable_card("CARD-01", subtitulo=None, descricao_curta=None)
        ]
    )
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_003" in codes
    ar003 = next(f for f in report.findings if f.code == "AR_003")
    assert ar003.severity == "minor"


# --- Case 36: documento with more than MAX_CROSS_REFS cited codes/ids -------
def test_case36_ar004_too_many_cross_refs() -> None:
    from generator.accessibility_reviewer import MAX_CROSS_REFS, review_accessibility

    documentos = [_documento(f"E1-0{n}") for n in range(1, 9)]
    documentos[0] = _documento(
        "E1-01",
        ids_citados=[f"id-{n}" for n in range(MAX_CROSS_REFS + 1)],
    )
    blueprint = _blueprint(documentos=documentos)
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_004" in codes
    ar004 = next(f for f in report.findings if f.code == "AR_004")
    assert ar004.severity == "minor"


# --- Case 37: documento without identifiable title/subject in conteudo -----
def test_case37_ar005_conteudo_without_title() -> None:
    from generator.accessibility_reviewer import review_accessibility

    documentos = [_documento(f"E1-0{n}") for n in range(1, 9)]
    documentos[0] = _documento("E1-01", conteudo={})
    blueprint = _blueprint(documentos=documentos)
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_005" in codes
    ar005 = next(f for f in report.findings if f.code == "AR_005")
    assert ar005.severity == "info"


# --- Case 38: case without any printable_card -> AR_006 ---------------------
def test_case38_ar006_no_printable_cards() -> None:
    from generator.accessibility_reviewer import review_accessibility

    blueprint = _blueprint(printable_cards=[])
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_006" in codes
    ar006 = next(f for f in report.findings if f.code == "AR_006")
    assert ar006.severity == "major"


# --------------------------------------------------------------------------- #
# Cases 39-48: behaviour of review_accessibility                             #
# --------------------------------------------------------------------------- #


# --- Case 39: clean blueprint -> approved ------------------------------------
def test_case39_clean_blueprint_approved() -> None:
    from generator.accessibility_reviewer import review_accessibility

    report = review_accessibility(_blueprint(), _BLUEPRINT_REF, _REPORT_ID)
    assert report.status == "approved"
    assert report.findings == ()


# --- Case 40: a major finding present -> needs_revision ---------------------
def test_case40_major_finding_needs_revision() -> None:
    from generator.accessibility_reviewer import review_accessibility

    blueprint = _blueprint(printable_cards=[])
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    codes = {finding.code for finding in report.findings}
    assert "AR_006" in codes
    assert report.status == "needs_revision"


# --- Case 41: review_accessibility imports ReviewFinding/helpers from
# visual_reviewer.py without duplicating them --------------------------------
def test_case41_imports_from_visual_reviewer_without_duplicating() -> None:
    import generator.accessibility_reviewer as accessibility_reviewer
    import generator.visual_reviewer as visual_reviewer

    assert accessibility_reviewer.ReviewFinding is visual_reviewer.ReviewFinding
    assert (
        accessibility_reviewer.VisualAccessibilityReviewReport
        is visual_reviewer.VisualAccessibilityReviewReport
    )
    assert (
        accessibility_reviewer.validate_visual_accessibility_review_report
        is visual_reviewer.validate_visual_accessibility_review_report
    )
    assert accessibility_reviewer.report_to_dict is visual_reviewer.report_to_dict


# --- Case 42: review_accessibility does not mutate the blueprint ------------
def test_case42_does_not_mutate() -> None:
    import copy

    from generator.accessibility_reviewer import review_accessibility

    blueprint = _blueprint()
    before = copy.deepcopy(blueprint.model_dump())
    review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    assert blueprint.model_dump() == before


# --- Case 43: returned report passes validate_visual_accessibility_review_report
def test_case43_serialised_passes_validation() -> None:
    from generator.accessibility_reviewer import review_accessibility
    from generator.visual_reviewer import (
        report_to_dict,
        validate_visual_accessibility_review_report,
    )

    report = review_accessibility(_blueprint(), _BLUEPRINT_REF, _REPORT_ID)
    assert validate_visual_accessibility_review_report(report_to_dict(report)) == []


# --- Case 44: reviewer_type of the report is "accessibility" ----------------
def test_case44_reviewer_type_is_accessibility() -> None:
    from generator.accessibility_reviewer import review_accessibility

    report = review_accessibility(_blueprint(), _BLUEPRINT_REF, _REPORT_ID)
    assert report.reviewer_type == "accessibility"


# --- Case 45: findings ordered by severity (critical first) -----------------
def test_case45_findings_ordered_by_severity() -> None:
    from generator.accessibility_reviewer import (
        MAX_CONTEUDO_CHARS,
        MAX_CROSS_REFS,
        review_accessibility,
    )

    documentos = [_documento(f"E1-0{n}") for n in range(1, 9)]
    documentos[0] = _documento(
        "E1-01",
        conteudo={"CORPO": "x" * (MAX_CONTEUDO_CHARS + 1)},
        ids_citados=[f"id-{n}" for n in range(MAX_CROSS_REFS + 1)],
    )
    blueprint = _blueprint(
        documentos=documentos,
        printable_cards=[
            _printable_card("CARD-01", subtitulo=None, descricao_curta=None)
        ],
    )
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    severities = [finding.severity for finding in report.findings]
    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    assert severities == sorted(severities, key=lambda s: order[s])


# --- Case 46: report_to_dict round-trips through validation without loss ----
def test_case46_report_to_dict_round_trip() -> None:
    from generator.accessibility_reviewer import review_accessibility
    from generator.visual_reviewer import (
        report_to_dict,
        validate_visual_accessibility_review_report,
    )

    blueprint = _blueprint(printable_cards=[])
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    payload = report_to_dict(report)
    assert validate_visual_accessibility_review_report(payload) == []
    codes = {finding["code"] for finding in payload["findings"]}
    assert "AR_006" in codes


# --- Case 47: thresholds are named, importable constants --------------------
def test_case47_thresholds_are_named_constants() -> None:
    from generator.accessibility_reviewer import MAX_CROSS_REFS, MAX_DOCS_PER_ENVELOPE

    assert isinstance(MAX_DOCS_PER_ENVELOPE, int)
    assert isinstance(MAX_CROSS_REFS, int)


# --- Case 48: Aurora blueprint -> review_accessibility returns a
# schema-valid report (with or without findings) -----------------------------
def test_case48_aurora_blueprint_schema_valid_report() -> None:
    import json
    from pathlib import Path

    from generator.accessibility_reviewer import review_accessibility
    from generator.visual_reviewer import (
        report_to_dict,
        validate_visual_accessibility_review_report,
    )

    caso_path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "caso_canonico_intermediario.json"
    )
    blueprint = Blueprint(**json.loads(caso_path.read_text(encoding="utf-8")))
    report = review_accessibility(blueprint, _BLUEPRINT_REF, _REPORT_ID)
    assert validate_visual_accessibility_review_report(report_to_dict(report)) == []

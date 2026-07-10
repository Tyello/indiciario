"""RED tests for the Narrative Reviewer (ISSUE-21+22, STEP-06).

Cases 21-45 of the ISSUE-21 spec for ``generator.narrative_reviewer``:

- 21-28: rules NR_001-NR_008 raise (or do not raise) the matching finding code.
- 29-38: ``review_narrative`` returns a ``ReviewReport``, derives ``status`` from
  finding severities, never mutates the blueprint, and echoes ``report_id`` /
  ``reviewer_type`` / ``blueprint_ref``.
- 39-45: ``validate_review_report`` and serialisation/ordering integration.

They are expected to FAIL (RED) until ``generator/narrative_reviewer.py`` exposes
the public function ``review_narrative``. The failure must come from the missing
symbol (ImportError / AttributeError on ``review_narrative``), NOT from a syntax
error in this file.

Construction notes (divergences carried from STEP-01, DVG-EXEC-001/002/003):

- ``PapelPersonagem`` has NO literal ``suspeito`` / ``vitima`` values. NR_003
  ("nenhum personagem suspeito além do executor") and NR_007 ("documentos de
  personagens que não são executor nem vítima") are tested at the behavioural
  level: a blueprint whose only non-executor characters are ``narrador`` /
  ``testemunha`` (no plausible alternative suspect such as ``red_herring`` /
  ``intermediario`` / ``cumplice``) must raise NR_003; a blueprint that does have
  one must not. Fixture blueprints are built only from the REAL fields of
  ``generator/models.py``.
- ``Documento.conteudo`` is ``dict[str, Any]`` (placeholder values), not a flat
  string. NR_001/NR_004/NR_005 text is therefore placed inside the dict values.
- ``Pista`` has NO ``obrigatoria`` field (that is ER_007, STEP-08), so it is not
  exercised here.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

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
    RedHerring,
)
from generator.narrative_reviewer import (
    ReviewReport,
    _now_iso,
    report_to_dict,
    review_narrative,
    validate_review_report,
)

_BLUEPRINT_REF = "tests/fixtures/narrative_reviewer/blueprint.json"
_REPORT_ID = "NR-test-20260620-001"


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


def _base_kwargs() -> dict[str, Any]:
    """Return kwargs for a minimal blueprint that should raise NO NR finding.

    The non-executor cast includes a ``red_herring`` plausible alternative
    suspect (avoids NR_003); the executor's motivation term ("reserva") appears
    in a document (avoids NR_004); dicas reference no document code; red herrings
    have a ``documento_descarte`` that exists (avoids NR_008).
    """

    documentos = [
        _documento(
            "E1-01",
            conteudo={"CORPO": "Registro da reserva trancada na sala dos fundos."},
        ),
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
    }


def _blueprint(**overrides: Any) -> Blueprint:
    kwargs = _base_kwargs()
    kwargs.update(overrides)
    return Blueprint(**kwargs)


def _review(blueprint: Blueprint, **kwargs: Any) -> ReviewReport:
    return review_narrative(blueprint, _BLUEPRINT_REF, _REPORT_ID, **kwargs)


def _codes(report: ReviewReport) -> set[str]:
    return {finding.code for finding in report.findings}


# --------------------------------------------------------------------------- #
# Cases 21-28: rules NR_001-NR_008                                            #
# --------------------------------------------------------------------------- #


# --- Case 21: interpretive author language -> NR_001 ------------------------
def test_case21_nr001_interpretive_language() -> None:
    blueprint = _blueprint(
        documentos=[
            _documento(
                "E1-01",
                conteudo={"CORPO": "Portanto isso prova claramente que ele mentiu."},
            ),
            *[_documento(f"E1-0{n}") for n in range(2, 9)],
        ]
    )
    report = _review(blueprint)
    assert "NR_001" in _codes(report)


# --- Case 22: no interpretive language -> no NR_001 -------------------------
def test_case22_no_nr001_when_raw() -> None:
    report = _review(_blueprint())
    assert "NR_001" not in _codes(report)


# --- Case 23: no alternative suspect besides executor -> NR_003 -------------
def test_case23_nr003_no_alternative_suspect() -> None:
    blueprint = _blueprint(
        personagens=[
            _personagem("01", "narrador", "Narrador", ancoragem=["E1-01"]),
            _personagem("02", "executor", "Executor", ancoragem=["E1-02"]),
            _personagem("05", "testemunha", "Testemunha A", ancoragem=["E1-05"]),
            _personagem("06", "testemunha", "Testemunha B", ancoragem=["E1-06"]),
        ],
        red_herrings=[
            RedHerring(
                personagem_id="05",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-05",
                categoria="cat",
            ),
            RedHerring(
                personagem_id="06",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-06",
                categoria="cat",
            ),
        ],
    )
    report = _review(blueprint)
    assert "NR_003" in _codes(report)


# --- Case 24: at least one alternative suspect -> no NR_003 -----------------
def test_case24_no_nr003_with_suspect() -> None:
    report = _review(_blueprint())
    assert "NR_003" not in _codes(report)


# --- Case 25: motivation unsupported by any document -> NR_004 --------------
def test_case25_nr004_motivation_unsupported() -> None:
    blueprint = _blueprint(
        motivacao="vinganca por uma traicao antiga jamais documentada",
        documentos=[_documento(f"E1-0{n}", conteudo={"CORPO": "texto neutro"}) for n in range(1, 9)],
    )
    report = _review(blueprint)
    assert "NR_004" in _codes(report)


# --- Case 26: hint references a missing document -> NR_006 (critical) -------
def test_case26_nr006_hint_missing_document() -> None:
    blueprint = _blueprint(
        dicas=[
            _dica(1, texto="Releia o documento E9-99 com atencao."),
            *[_dica(n) for n in range(2, 7)],
        ]
    )
    report = _review(blueprint)
    assert "NR_006" in _codes(report)
    nr006 = next(f for f in report.findings if f.code == "NR_006")
    assert nr006.severity == "critical"


# --- Case 27: red herring without a supporting document -> NR_008 ----------
def test_case27_nr008_red_herring_without_document() -> None:
    blueprint = _blueprint(
        red_herrings=[
            RedHerring(
                personagem_id="03",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E9-99",
                categoria="cat",
            ),
            RedHerring(
                personagem_id="04",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-04",
                categoria="cat",
            ),
        ]
    )
    report = _review(blueprint)
    assert "NR_008" in _codes(report)


# --- Case 28: all player documents are raw evidence -> no NR_001 -----------
def test_case28_no_nr001_all_raw() -> None:
    blueprint = _blueprint(
        documentos=[
            _documento(f"E1-0{n}", conteudo={"CORPO": f"Registro bruto numero {n}."})
            for n in range(1, 9)
        ]
    )
    report = _review(blueprint)
    assert "NR_001" not in _codes(report)


# --------------------------------------------------------------------------- #
# Cases 29-38: review_narrative and status                                    #
# --------------------------------------------------------------------------- #


# --- Case 29: review_narrative returns a ReviewReport -----------------------
def test_case29_returns_review_report() -> None:
    assert isinstance(_review(_blueprint()), ReviewReport)


# --- Case 30: serialised report passes validate_review_report ---------------
def test_case30_serialised_passes_validation() -> None:
    report = _review(_blueprint())
    assert validate_review_report(report_to_dict(report)) == []


# --- Case 31: NR_006 (critical) -> status blocked ---------------------------
def test_case31_critical_blocks() -> None:
    blueprint = _blueprint(
        dicas=[
            _dica(1, texto="Veja o documento E9-99."),
            *[_dica(n) for n in range(2, 7)],
        ]
    )
    report = _review(blueprint)
    assert report.status == "blocked"


# --- Case 32: NR_003 (major) without critical -> needs_revision -------------
def test_case32_major_needs_revision() -> None:
    blueprint = _blueprint(
        personagens=[
            _personagem("01", "narrador", "Narrador", ancoragem=["E1-01"]),
            _personagem("02", "executor", "Executor", ancoragem=["E1-02"]),
            _personagem("05", "testemunha", "Testemunha A", ancoragem=["E1-05"]),
            _personagem("06", "testemunha", "Testemunha B", ancoragem=["E1-06"]),
        ],
        red_herrings=[
            RedHerring(
                personagem_id="05",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-05",
                categoria="cat",
            ),
            RedHerring(
                personagem_id="06",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-06",
                categoria="cat",
            ),
        ],
    )
    report = _review(blueprint)
    assert "NR_006" not in _codes(report)
    assert "NR_003" in _codes(report)
    assert report.status == "needs_revision"


# --- Case 33: no major/critical finding -> approved -------------------------
def test_case33_clean_approved() -> None:
    report = _review(_blueprint())
    assert not any(f.severity in {"critical", "major"} for f in report.findings)
    assert report.status == "approved"


# --- Case 34: report_to_dict has all required fields ------------------------
def test_case34_report_to_dict_fields() -> None:
    payload = report_to_dict(_review(_blueprint()))
    for key in (
        "schema_version",
        "report_id",
        "reviewer_type",
        "blueprint_ref",
        "created_at",
        "created_by",
        "status",
        "summary",
        "findings",
        "overall_confidence",
        "notes",
    ):
        assert key in payload


# --- Case 35: review_narrative does not mutate the blueprint ----------------
def test_case35_does_not_mutate() -> None:
    blueprint = _blueprint()
    before = copy.deepcopy(blueprint.model_dump())
    _review(blueprint)
    assert blueprint.model_dump() == before


# --- Case 36: report_id echoes the argument ---------------------------------
def test_case36_report_id_echo() -> None:
    report = review_narrative(_blueprint(), _BLUEPRINT_REF, "NR-echo-001")
    assert report.report_id == "NR-echo-001"


# --- Case 37: reviewer_type is "narrative" ----------------------------------
def test_case37_reviewer_type() -> None:
    assert _review(_blueprint()).reviewer_type == "narrative"


# --- Case 38: blueprint_ref echoes the argument -----------------------------
def test_case38_blueprint_ref_echo() -> None:
    report = review_narrative(_blueprint(), "some/other/ref.json", _REPORT_ID)
    assert report.blueprint_ref == "some/other/ref.json"


# --------------------------------------------------------------------------- #
# Cases 39-45: validate_review_report and integration                         #
# --------------------------------------------------------------------------- #


# --- Case 39: validate_review_report empty for a valid report ---------------
def test_case39_validate_empty_for_valid() -> None:
    assert validate_review_report(report_to_dict(_review(_blueprint()))) == []


# --- Case 40: validate_review_report reports errors when status missing ------
def test_case40_validate_errors_when_status_missing() -> None:
    payload = report_to_dict(_review(_blueprint()))
    del payload["status"]
    assert validate_review_report(payload) != []


# --- Case 41: NR_* codes preserved through serialisation --------------------
def test_case41_codes_preserved() -> None:
    blueprint = _blueprint(
        dicas=[
            _dica(1, texto="Veja o documento E9-99."),
            *[_dica(n) for n in range(2, 7)],
        ]
    )
    payload = report_to_dict(_review(blueprint))
    codes = {finding["code"] for finding in payload["findings"]}
    assert "NR_006" in codes


# --- Case 42: overall_confidence default is "medium" ------------------------
def test_case42_default_confidence() -> None:
    assert _review(_blueprint()).overall_confidence == "medium"


# --- Case 43: notes default is "" -------------------------------------------
def test_case43_default_notes() -> None:
    assert _review(_blueprint()).notes == ""


# --- Case 44: findings ordered by severity (critical first) -----------------
def test_case44_findings_ordered_by_severity() -> None:
    blueprint = _blueprint(
        personagens=[
            _personagem("01", "narrador", "Narrador", ancoragem=["E1-01"]),
            _personagem("02", "executor", "Executor", ancoragem=["E1-02"]),
            _personagem("05", "testemunha", "Testemunha A", ancoragem=["E1-05"]),
            _personagem("06", "testemunha", "Testemunha B", ancoragem=["E1-06"]),
        ],
        red_herrings=[
            RedHerring(
                personagem_id="05",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-05",
                categoria="cat",
            ),
            RedHerring(
                personagem_id="06",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-06",
                categoria="cat",
            ),
        ],
        dicas=[
            _dica(1, texto="Veja o documento E9-99."),
            *[_dica(n) for n in range(2, 7)],
        ],
    )
    report = _review(blueprint)
    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    ranks = [order[f.severity] for f in report.findings]
    assert ranks == sorted(ranks)
    assert report.findings[0].severity == "critical"


# --- Case 45: canonical blueprint does not raise in review_narrative --------
def test_case45_smoke_does_not_raise() -> None:
    try:
        _review(_blueprint())
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"review_narrative raised unexpectedly: {exc!r}")


# --- Case 46: explicit created_at is used literally -------------------------
def test_case46_explicit_created_at_used_literally() -> None:
    report = _review(_blueprint(), created_at="2026-01-01T00:00:00Z")
    assert report.created_at == "2026-01-01T00:00:00Z"


# --- Case 47: omitted created_at preserves current _now_iso() behaviour -----
def test_case47_default_created_at_preserved() -> None:
    before = _now_iso()
    report = _review(_blueprint())
    after = _now_iso()
    assert before <= report.created_at <= after

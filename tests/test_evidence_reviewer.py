"""RED tests for the Evidence Reviewer (ISSUE-21+22, STEP-08).

Cases 46-70 of the ISSUE-21 spec for ``generator.evidence_reviewer``:

- 46-53: rules ER_001-ER_008 raise (or do not raise) the matching finding code.
- 54-63: ``review_evidence`` returns a ``ReviewReport``, derives ``status`` from
  finding severities, never mutates the blueprint, and echoes ``report_id`` /
  ``reviewer_type`` / ``blueprint_ref``.
- 64-70: integration and edge cases (canonical Aurora blueprint, minimal
  blueprint, shared dataclasses module, round-trip).

They are expected to FAIL (RED) until ``generator/evidence_reviewer.py`` exists
and exposes ``review_evidence``. The failure must come from the missing module
(ModuleNotFoundError: generator.evidence_reviewer), NOT from a syntax error in
this file.

Construction notes (REAL fields of ``generator/models.py`` only):

- ``Pista`` has NO ``obrigatoria`` field. The spec's ER_007 ("pista obrigatória
  não disponível no E1") is described against a field that does not exist on
  ``Pista``. The REAL mandatory flag lives on ``ContratoEvidencia`` as
  ``obrigatoria_para_avanco: bool``. DVG-EXEC-004 is recorded in the STEP-08
  execution report. ER_007 is therefore tested at the behavioural level using a
  ``ContratoEvidencia`` whose ``obrigatoria_para_avanco`` is True and whose
  ``prova_principal`` document is NOT in any E1 document — no field is invented
  on ``Pista``.
- ``cadeia_causal`` enforces ``min_length=3`` on the real ``Blueprint``. ER_003
  ("cadeia causal com menos de 3 elos") therefore cannot be exercised through a
  full ``Blueprint`` instance; it is tested through a lightweight stand-in object
  (``SimpleNamespace``) carrying only the fields the reviewer reads, mirroring the
  ``blueprint: Any`` contract of the reviewer.
- ``Documento.conteudo`` is ``dict[str, Any]``; placeholder values are placed in
  the dict.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from generator.models import (
    Blueprint,
    ConflitoCentral,
    ContratoEvidencia,
    Dica,
    Documento,
    GuiaOperacional,
    ObjetivoEnvelope,
    Personagem,
    Pilar,
    Pista,
    RedHerring,
)
from generator.evidence_reviewer import review_evidence
from generator.narrative_reviewer import (
    ReviewReport,
    report_to_dict,
    review_narrative,
    validate_review_report,
)

_BLUEPRINT_REF = "tests/fixtures/evidence_reviewer/blueprint.json"
_REPORT_ID = "ER-test-20260620-001"
_AURORA = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "caso_canonico_intermediario.json"
)


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
) -> Documento:
    return Documento(
        codigo=codigo,
        titulo=titulo,
        envelope=envelope,
        tipo=tipo,
        emocao_esperada="neutra",
        objetivo_narrativo="objetivo",
        pistas_contidas=[],
        ids_citados=[],
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


def _base_kwargs() -> dict[str, Any]:
    """Return kwargs for a minimal blueprint that should raise NO ER finding.

    - Every pilar's documents are covered by a pista (avoids ER_002).
    - Every envelope in ``objetivos_por_envelope`` has a pista whose document
      belongs to that envelope (avoids ER_004).
    - Pistas spread across distinct documents (avoids ER_005 concentration and
      ER_008 low coverage).
    - Every red herring has a pista whose document equals its
      ``documento_descarte`` (avoids ER_006).
    - No mandatory contract pointing outside E1 (avoids ER_007).
    """

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
    }


def _blueprint(**overrides: Any) -> Blueprint:
    kwargs = _base_kwargs()
    kwargs.update(overrides)
    return Blueprint(**kwargs)


def _review(blueprint: Any, **kwargs: Any) -> ReviewReport:
    return review_evidence(blueprint, _BLUEPRINT_REF, _REPORT_ID, **kwargs)


def _codes(report: ReviewReport) -> set[str]:
    return {finding.code for finding in report.findings}


def _load_aurora() -> Blueprint:
    return Blueprint.model_validate(json.loads(_AURORA.read_text(encoding="utf-8")))


# --------------------------------------------------------------------------- #
# Cases 46-53: rules ER_001-ER_008                                            #
# --------------------------------------------------------------------------- #


# --- Case 46: pista referencing a missing document -> ER_001 (critical) -----
def test_case46_er001_pista_missing_document() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E9-99", "E1-02"),
            _pista("E1-03", "E1-04"),
            _pista("E1-05", "E1-06"),
            _pista("E1-07", "E1-08"),
        ]
    )
    report = _review(blueprint)
    assert "ER_001" in _codes(report)
    er001 = next(f for f in report.findings if f.code == "ER_001")
    assert er001.severity == "critical"


# --- Case 47: pista with an existing document -> no ER_001 ------------------
def test_case47_no_er001_when_document_exists() -> None:
    report = _review(_blueprint())
    assert "ER_001" not in _codes(report)


# --- Case 48: pilar with no supporting pista -> ER_002 ----------------------
def test_case48_er002_pilar_without_pista() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E1-01", "E1-02"),
            _pista("E1-03", "E1-04"),
            _pista("E1-05", "E1-06"),
        ],
        pilares_validacao=[
            Pilar(nome="presenca", documento_principal="E1-01", confirmacao="E1-02", personagem_id="02"),
            Pilar(nome="credencial", documento_principal="E1-03", confirmacao="E1-04", personagem_id="02"),
            Pilar(nome="terminal", documento_principal="E1-05", confirmacao="E1-06", personagem_id="02"),
            Pilar(nome="acao", documento_principal="E1-07", confirmacao="E1-08", personagem_id="02"),
        ],
    )
    report = _review(blueprint)
    assert "ER_002" in _codes(report)


# --- Case 49: every pilar covered by a pista -> no ER_002 -------------------
def test_case49_no_er002_when_all_pillars_supported() -> None:
    report = _review(_blueprint())
    assert "ER_002" not in _codes(report)


# --- Case 50: envelope without a designated pista -> ER_004 -----------------
def test_case50_er004_envelope_without_pista() -> None:
    blueprint = _blueprint(
        objetivos_por_envelope=[
            _objetivo("E1", ["E1-01", "E1-02"]),
            _objetivo("E2", ["E2-01"]),
        ],
        documentos=[*[_documento(f"E1-0{n}") for n in range(1, 9)], _documento("E2-01", envelope="E2")],
    )
    report = _review(blueprint)
    assert "ER_004" in _codes(report)


# --- Case 51: red herring with no pista to discard it -> ER_006 -------------
def test_case51_er006_red_herring_not_discardable() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E1-01", "E1-02"),
            _pista("E1-05", "E1-06"),
            _pista("E1-07", "E1-08"),
        ],
        red_herrings=[
            RedHerring(
                personagem_id="03",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-03",
                categoria="cat",
            ),
            RedHerring(
                personagem_id="04",
                motivo_aparente="motivo",
                como_descartar="descartar",
                documento_descarte="E1-04",
                categoria="cat",
            ),
        ],
    )
    report = _review(blueprint)
    assert "ER_006" in _codes(report)


# --- Case 52: mandatory contract evidence not available in E1 -> ER_007 -----
# DVG-EXEC-004: spec ER_007 names a non-existent ``Pista.obrigatoria`` field.
# Tested via the REAL mandatory flag ``ContratoEvidencia.obrigatoria_para_avanco``
# whose ``prova_principal`` document is absent from E1.
def test_case52_er007_mandatory_evidence_missing_in_e1() -> None:
    blueprint = _blueprint(
        contratos_evidencia=[
            ContratoEvidencia(
                id="C1",
                conclusao="conclusao",
                fase="E1",
                tipo="presenca",
                prova_principal="E9-99",
                risco_ambiguidade="baixo",
                obrigatoria_para_avanco=True,
            )
        ]
    )
    report = _review(blueprint)
    assert "ER_007" in _codes(report)


# --- Case 53: more than 60% of pistas on the same document -> ER_005 (minor) -
def test_case53_er005_concentration() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E1-01", "E1-02", descricao="a"),
            _pista("E1-01", "E1-03", descricao="b"),
            _pista("E1-01", "E1-04", descricao="c"),
            _pista("E1-05", "E1-06", descricao="d"),
        ]
    )
    report = _review(blueprint)
    assert "ER_005" in _codes(report)
    er005 = next(f for f in report.findings if f.code == "ER_005")
    assert er005.severity == "minor"


# --------------------------------------------------------------------------- #
# Cases 54-63: review_evidence and status                                     #
# --------------------------------------------------------------------------- #


# --- Case 54: review_evidence returns a ReviewReport ------------------------
def test_case54_returns_review_report() -> None:
    assert isinstance(_review(_blueprint()), ReviewReport)


# --- Case 55: serialised report passes validate_review_report ---------------
def test_case55_serialised_passes_validation() -> None:
    report = _review(_blueprint())
    assert validate_review_report(report_to_dict(report)) == []


# --- Case 56: ER_001 (critical) -> status blocked ---------------------------
def test_case56_critical_blocks() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E9-99", "E1-02"),
            _pista("E1-03", "E1-04"),
            _pista("E1-05", "E1-06"),
            _pista("E1-07", "E1-08"),
        ]
    )
    report = _review(blueprint)
    assert report.status == "blocked"


# --- Case 57: ER_002 (major) without critical -> needs_revision -------------
def test_case57_major_needs_revision() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E1-01", "E1-02"),
            _pista("E1-03", "E1-04"),
            _pista("E1-05", "E1-06"),
        ],
        pilares_validacao=[
            Pilar(nome="presenca", documento_principal="E1-01", confirmacao="E1-02", personagem_id="02"),
            Pilar(nome="credencial", documento_principal="E1-03", confirmacao="E1-04", personagem_id="02"),
            Pilar(nome="terminal", documento_principal="E1-05", confirmacao="E1-06", personagem_id="02"),
            Pilar(nome="acao", documento_principal="E1-07", confirmacao="E1-08", personagem_id="02"),
        ],
    )
    report = _review(blueprint)
    assert not any(f.severity == "critical" for f in report.findings)
    assert "ER_002" in _codes(report)
    assert report.status == "needs_revision"


# --- Case 58: no major/critical finding -> approved -------------------------
def test_case58_clean_approved() -> None:
    report = _review(_blueprint())
    assert not any(f.severity in {"critical", "major"} for f in report.findings)
    assert report.status == "approved"


# --- Case 59: report_to_dict has all required fields ------------------------
def test_case59_report_to_dict_fields() -> None:
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


# --- Case 60: review_evidence does not mutate the blueprint -----------------
def test_case60_does_not_mutate() -> None:
    blueprint = _blueprint()
    before = copy.deepcopy(blueprint.model_dump())
    _review(blueprint)
    assert blueprint.model_dump() == before


# --- Case 61: report_id echoes the argument ---------------------------------
def test_case61_report_id_echo() -> None:
    report = review_evidence(_blueprint(), _BLUEPRINT_REF, "ER-echo-001")
    assert report.report_id == "ER-echo-001"


# --- Case 62: reviewer_type is "evidence" -----------------------------------
def test_case62_reviewer_type() -> None:
    assert _review(_blueprint()).reviewer_type == "evidence"


# --- Case 63: blueprint_ref echoes the argument -----------------------------
def test_case63_blueprint_ref_echo() -> None:
    report = review_evidence(_blueprint(), "some/other/ref.json", _REPORT_ID)
    assert report.blueprint_ref == "some/other/ref.json"


# --------------------------------------------------------------------------- #
# Cases 64-70: integration and edge cases                                     #
# --------------------------------------------------------------------------- #


# --- Case 64: validate_review_report works for an evidence report -----------
def test_case64_validate_for_evidence_report() -> None:
    report = _review(_load_aurora())
    assert validate_review_report(report_to_dict(report)) == []


# --- Case 65: ER_* codes preserved through serialisation --------------------
def test_case65_codes_preserved() -> None:
    blueprint = _blueprint(
        matriz_pistas=[
            _pista("E9-99", "E1-02"),
            _pista("E1-03", "E1-04"),
            _pista("E1-05", "E1-06"),
            _pista("E1-07", "E1-08"),
        ]
    )
    payload = report_to_dict(_review(blueprint))
    codes = {finding["code"] for finding in payload["findings"]}
    assert "ER_001" in codes


# --- Case 66: minimal blueprint (no red_herrings, no dicas read) ------------
# ER_003 (cadeia_causal < 3 elos) cannot be built via the strict Blueprint
# (min_length=3), so it is exercised through a lightweight stand-in mirroring
# the ``blueprint: Any`` contract, with all optional collections empty.
def test_case66_minimal_blueprint_no_exception() -> None:
    stub = SimpleNamespace(
        documentos=[],
        personagens=[],
        matriz_pistas=[],
        pilares_validacao=[],
        objetivos_por_envelope=[],
        red_herrings=[],
        dicas=[],
        cadeia_causal=["unico elo"],
        contratos_evidencia=[],
        executor_id="",
        motivacao="",
        tom="serio",
    )
    try:
        report = _review(stub)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"review_evidence raised on minimal stub: {exc!r}")
    assert "ER_003" in _codes(report)


# --- Case 67: canonical Aurora blueprint does not raise in either reviewer --
def test_case67_canonical_no_exception() -> None:
    aurora = _load_aurora()
    try:
        review_evidence(aurora, str(_AURORA), "ER-aurora-001")
        review_narrative(aurora, str(_AURORA), "NR-aurora-001")
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"reviewer raised on Aurora: {exc!r}")


# --- Case 68: both reviewers import dataclasses from the same module --------
def test_case68_shared_dataclasses_module() -> None:
    import generator.evidence_reviewer as er
    import generator.narrative_reviewer as nr

    assert er.ReviewReport is nr.ReviewReport
    assert er.ReviewFinding is nr.ReviewFinding


# --- Case 69: report_to_dict + validate_review_report round-trip ------------
def test_case69_round_trip() -> None:
    report = _review(_load_aurora())
    payload = report_to_dict(report)
    assert validate_review_report(payload) == []
    assert payload["reviewer_type"] == "evidence"
    assert payload["report_id"] == _REPORT_ID


# --- Case 70: full suite regression placeholder (confirmed in validation) ---
def test_case70_smoke_does_not_raise() -> None:
    try:
        _review(_blueprint())
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"review_evidence raised unexpectedly: {exc!r}")

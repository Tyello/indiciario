import json
from pathlib import Path

from generator.models import Blueprint
from generator.playtest_metrics import analyze_playtest, write_playtest_report
from generator.validator import BlueprintValidator, Severidade

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "examples" / "caso_canonico_iniciante.json"
INICIANTE_B = ROOT / "examples" / "caso_canonico_iniciante_b.json"
AURORA = ROOT / "examples" / "caso_canonico_intermediario.json"
FINTECH = ROOT / "examples" / "caso_fintech.json"


def blueprint_data() -> dict:
    return json.loads(CANONICAL.read_text(encoding="utf-8"))


def blueprint_with(**updates) -> Blueprint:
    data = blueprint_data()
    data.update(updates)
    return Blueprint(**data)


def warning_codes(report: dict) -> set[str]:
    return {warning["code"] for warning in report["warnings"]}


def test_analyze_playtest_gera_report_valido_serializavel(tmp_path):
    report = analyze_playtest(blueprint_with())

    assert report["status"] in {"ok", "warnings"}
    assert report["summary"]["difficulty_declared"] == "iniciante"
    assert report["issues"] == []

    output = write_playtest_report(report, tmp_path / "playtest_report.json")
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["summary"]["documents"] == 20


def test_tempo_estimado_eh_calculado_por_documentos_contratos_e_envelopes():
    report = analyze_playtest(blueprint_with())

    assert report["summary"]["estimated_minutes"] == 100


def test_carga_cognitiva_baixa():
    data = blueprint_data()
    data["documentos"] = data["documentos"][:8]
    data["contratos_evidencia"] = data["contratos_evidencia"][:1]

    report = analyze_playtest(Blueprint(**data))

    assert report["summary"]["cognitive_load"] == "low"


def test_carga_cognitiva_media():
    report = analyze_playtest(
        blueprint_with(
            dificuldade="intermediario", documentos=blueprint_data()["documentos"][:17]
        )
    )

    assert report["summary"]["cognitive_load"] == "medium"


def test_carga_cognitiva_alta():
    data = blueprint_data()
    original = data["documentos"]
    data["documentos"] = [
        dict(doc, codigo=f"E1-{index + 1:02d}")
        for index, doc in enumerate((original * 2)[:20])
    ]

    report = analyze_playtest(Blueprint(**data))

    assert report["summary"]["cognitive_load"] == "high"


def test_dificuldade_estimada_eh_preenchida():
    report = analyze_playtest(blueprint_with())

    assert report["summary"]["difficulty_estimated"] in {
        "iniciante",
        "intermediario",
        "avancado",
        "especialista",
        "mestre",
    }


def test_pt_001_dispara_quando_excesso_de_documentos():
    report = analyze_playtest(blueprint_with(dificuldade="iniciante"))

    assert "PT_001" in warning_codes(report)


def test_pt_002_dispara_quando_poucos_documentos():
    report = analyze_playtest(blueprint_with(dificuldade="mestre"))

    assert "PT_002" in warning_codes(report)


def test_pt_004_dispara_quando_envelope_desbalanceado():
    data = blueprint_data()
    for index, doc in enumerate(data["documentos"]):
        doc["envelope"] = "E2" if index == len(data["documentos"]) - 1 else "E1"

    report = analyze_playtest(Blueprint(**data))

    assert "PT_004" in warning_codes(report)


def test_pt_009_dispara_quando_dificuldade_diverge():
    data = blueprint_data()
    original = data["documentos"]
    data["dificuldade"] = "iniciante"
    data["documentos"] = [
        dict(doc, codigo=f"E1-{index + 1:02d}")
        for index, doc in enumerate((original * 2)[:24])
    ]
    data["contratos_evidencia"] = [
        dict(contrato, id=f"C-PT-{index}")
        for index, contrato in enumerate(data["contratos_evidencia"] * 2)
    ]

    report = analyze_playtest(Blueprint(**data))

    assert "PT_009" in warning_codes(report)


# ---------------------------------------------------------------------------
# ISSUE-30.7 — Âncoras de regressão: estimador por profundidade (STEP-02 RED)
# ---------------------------------------------------------------------------


def test_iniciante_b_estimated_iniciante():
    """Iniciante B deve estimar iniciante (hoje: iniciante — GREEN já antes do fix)."""
    data = json.loads(INICIANTE_B.read_text(encoding="utf-8"))
    report = analyze_playtest(Blueprint(**data))
    assert report["summary"]["difficulty_estimated"] == "iniciante"


def test_aurora_estimated_intermediario():
    """Aurora deve estimar intermediario (hoje: intermediario — GREEN já antes do fix)."""
    data = json.loads(AURORA.read_text(encoding="utf-8"))
    report = analyze_playtest(Blueprint(**data))
    assert report["summary"]["difficulty_estimated"] == "intermediario"


def test_fintech_estimated_avancado():
    """Fintech deve estimar avancado (hoje: intermediario — RED; trava regressão pós-fix)."""
    data = json.loads(FINTECH.read_text(encoding="utf-8"))
    report = analyze_playtest(Blueprint(**data))
    assert report["summary"]["difficulty_estimated"] == "avancado"


def test_mirante_not_estimated_avancado():
    """Mirante não deve estimar avancado (hoje: avancado — RED; deve ser iniciante ou intermediario)."""
    data = json.loads(CANONICAL.read_text(encoding="utf-8"))
    report = analyze_playtest(Blueprint(**data))
    assert report["summary"]["difficulty_estimated"] in {"iniciante", "intermediario"}


def test_estimator_discriminates_roster():
    """Estimador deve discriminar o roster: ≥3 valores distintos OU cobre iniciante+avancado.

    Hoje: {iniciante, intermediario, intermediario} → 2 distintos, sem avancado → RED.
    Após fix: {iniciante, intermediario, avancado} → 3 distintos → GREEN.
    """
    ib_data = json.loads(INICIANTE_B.read_text(encoding="utf-8"))
    aurora_data = json.loads(AURORA.read_text(encoding="utf-8"))
    fintech_data = json.loads(FINTECH.read_text(encoding="utf-8"))

    ib_est = analyze_playtest(Blueprint(**ib_data))["summary"]["difficulty_estimated"]
    aurora_est = analyze_playtest(Blueprint(**aurora_data))["summary"]["difficulty_estimated"]
    fintech_est = analyze_playtest(Blueprint(**fintech_data))["summary"]["difficulty_estimated"]

    estimates = {ib_est, aurora_est, fintech_est}
    # Prova de poder discriminativo: 3 valores distintos OU cobre iniciante→avancado
    assert len(estimates) >= 3 or ("iniciante" in estimates and "avancado" in estimates)


def test_document_count_does_not_dominate():
    """Muitos documentos curtos + profundidade rasa devem estimar ≤ intermediario (DF-02).

    Hoje: 22 docs → banda 2 → max=2 → avancado — RED.
    Após fix: contagem é sinal informativo; densidade/profundidade rasas → ≤ intermediario.
    """
    data = json.loads(CANONICAL.read_text(encoding="utf-8"))
    # 22 documentos todos com conteúdo vazio (densidade mínima)
    template_doc = dict(data["documentos"][0])
    template_doc["conteudo"] = {}  # dict vazio → len(str({}))=2 → densidade quase zero
    data["documentos"] = [
        dict(template_doc, codigo=f"E1-{i + 1:02d}")
        for i in range(22)
    ]
    # Contratos todos não-obrigatórios → profundidade de solução = 0
    data["contratos_evidencia"] = [
        dict(c, obrigatoria_para_avanco=False)
        for c in data["contratos_evidencia"][:1]
    ]
    report = analyze_playtest(Blueprint(**data))
    assert report["summary"]["difficulty_estimated"] in {"iniciante", "intermediario"}


def test_pt009_uses_depth_estimator():
    """PT_009 não deve disparar para Iniciante B nem Aurora (declarada ≈ estimada pós-fix).

    Hoje: InicianteB estimada=iniciante e Aurora estimada=intermediario → distância 0 → não dispara.
    Já é GREEN antes do fix; após fix deve continuar GREEN.
    """
    ib_data = json.loads(INICIANTE_B.read_text(encoding="utf-8"))
    aurora_data = json.loads(AURORA.read_text(encoding="utf-8"))

    ib_report = analyze_playtest(Blueprint(**ib_data))
    aurora_report = analyze_playtest(Blueprint(**aurora_data))

    assert "PT_009" not in warning_codes(ib_report), (
        f"PT_009 disparou para Iniciante B: {ib_report['summary']}"
    )
    assert "PT_009" not in warning_codes(aurora_report), (
        f"PT_009 disparou para Aurora: {aurora_report['summary']}"
    )


# ---------------------------------------------------------------------------
# fim dos testes ISSUE-30.7
# ---------------------------------------------------------------------------


def test_validator_registra_pt_como_aviso_nao_critico():
    resultado = BlueprintValidator(
        blueprint_with(dificuldade="iniciante"), strict=True
    ).validar()

    pt_warnings = [
        aviso for aviso in resultado.avisos if aviso.codigo.startswith("PT_")
    ]
    assert any(aviso.codigo == "PT_001" for aviso in pt_warnings)
    assert all(aviso.severidade == Severidade.AVISO for aviso in pt_warnings)
    assert not any(erro.codigo.startswith("PT_") for erro in resultado.erros)

import json
from pathlib import Path

from generator.models import Blueprint
from generator.playtest_metrics import analyze_playtest, write_playtest_report
from generator.validator import BlueprintValidator, Severidade

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "examples" / "caso_canonico_intermediario.json"


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
    assert report["summary"]["difficulty_declared"] == "intermediario"
    assert report["issues"] == []

    output = write_playtest_report(report, tmp_path / "playtest_report.json")
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["summary"]["documents"] == 15


def test_tempo_estimado_eh_calculado_por_documentos_contratos_e_envelopes():
    report = analyze_playtest(blueprint_with())

    assert report["summary"]["estimated_minutes"] == 83


def test_carga_cognitiva_baixa():
    data = blueprint_data()
    data["documentos"] = data["documentos"][:8]
    data["contratos_evidencia"] = data["contratos_evidencia"][:1]

    report = analyze_playtest(Blueprint(**data))

    assert report["summary"]["cognitive_load"] == "low"


def test_carga_cognitiva_media():
    report = analyze_playtest(blueprint_with())

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

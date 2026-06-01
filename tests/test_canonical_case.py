import json
from pathlib import Path

from generator.clue_graph import analyze_clue_graph, build_clue_graph
from generator.llm_feedback import build_llm_feedback
from generator.models import Blueprint
from generator.validator import BlueprintValidator

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CASE = ROOT / "examples" / "caso_canonico_intermediario.json"


def _raw_text() -> str:
    return CANONICAL_CASE.read_text(encoding="utf-8")


def _blueprint() -> Blueprint:
    return Blueprint(**json.loads(_raw_text()))


def test_caso_canonico_carrega_como_blueprint():
    blueprint = _blueprint()

    assert blueprint.titulo == "O Desvio da Reserva Mirante"
    assert len(blueprint.documentos) == 15


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

    assert blueprint.dificuldade.value == "intermediario"
    assert blueprint.formato_envelopes == 2
    assert blueprint.modo_validacao.value == "offline_puro"
    assert blueprint.tempo_estimado_min == 70
    assert blueprint.numero_jogadores == "3 a 5"


def test_caso_canonico_tem_contratos_e_contrato_final():
    blueprint = _blueprint()

    assert blueprint.contratos_evidencia
    assert any(contrato.fase == "final" for contrato in blueprint.contratos_evidencia)


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

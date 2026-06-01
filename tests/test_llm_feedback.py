import json

from generator.llm_feedback import (
    build_llm_feedback,
    instruction_from_graph_issue,
    instruction_from_validation_error,
    write_llm_feedback,
)
from generator.validator import Erro, ResultadoValidacao, Severidade


def resultado_com(erro: Erro | None = None) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    if erro is not None:
        resultado.adicionar(erro)
    return resultado


def primeira_instrucao(feedback: dict) -> dict:
    return feedback["instructions"][0]


def test_build_llm_feedback_sem_criticos_retorna_passed():
    feedback = build_llm_feedback(ResultadoValidacao())

    assert feedback["status"] == "passed"
    assert feedback["critical_count"] == 0


def test_erro_ce_005_vira_high_evidence_contract():
    feedback = build_llm_feedback(resultado_com(Erro("CE_005", Severidade.CRITICO, "Mesmo documento.")))

    instruction = primeira_instrucao(feedback)
    assert instruction["priority"] == "high"
    assert instruction["category"] == "evidence_contract"
    assert instruction["source"] == "validator"


def test_erro_env_005_vira_high_envelope_structure():
    feedback = build_llm_feedback(resultado_com(Erro("ENV_005", Severidade.CRITICO, "Envelope excedente.")))

    instruction = primeira_instrucao(feedback)
    assert instruction["priority"] == "high"
    assert instruction["category"] == "envelope_structure"


def test_erro_cont_003_vira_high_content_schema():
    feedback = build_llm_feedback(resultado_com(Erro("CONT_003", Severidade.CRITICO, "Campo ausente.")))

    instruction = primeira_instrucao(feedback)
    assert instruction["priority"] == "high"
    assert instruction["category"] == "content_schema"


def test_issue_gp_003_vira_medium_clue_graph():
    instruction = instruction_from_graph_issue({"code": "GP_003", "severity": "warning", "message": "Órfão."})

    assert instruction["priority"] == "medium"
    assert instruction["category"] == "clue_graph"


def test_issue_gp_006_critical_vira_high_clue_graph():
    instruction = instruction_from_graph_issue({"code": "GP_006", "severity": "critical", "message": "Sem final."})

    assert instruction["priority"] == "high"
    assert instruction["category"] == "clue_graph"


def test_issue_gp_006_warning_vira_medium_clue_graph():
    instruction = instruction_from_graph_issue({"code": "GP_006", "severity": "warning", "message": "Sem contratos."})

    assert instruction["priority"] == "medium"
    assert instruction["category"] == "clue_graph"


def test_issue_qa_file_001_vira_high_qa_package():
    feedback = build_llm_feedback(
        ResultadoValidacao(),
        qa_report={"errors": [{"code": "QA_FILE_001", "severity": "error", "message": "Ausente."}], "warnings": []},
    )

    instruction = primeira_instrucao(feedback)
    assert instruction["priority"] == "high"
    assert instruction["category"] == "qa_package"
    assert instruction["source"] == "qa"


def test_fallback_codigo_desconhecido_usa_categoria_unknown():
    feedback = build_llm_feedback(resultado_com(Erro("XYZ_999", Severidade.MODERADO, "Mensagem original.")))

    instruction = primeira_instrucao(feedback)
    assert instruction["category"] == "unknown"
    assert instruction["priority"] == "medium"
    assert instruction["instruction"] == "Mensagem original."


def test_target_extraido_de_documento_quando_disponivel():
    instruction = instruction_from_validation_error(
        Erro("CONT_003", Severidade.CRITICO, "Campo ausente.", documento="E1-01")
    )

    assert instruction["target"] == "E1-01"


def test_target_extraido_de_contrato_no_detalhe():
    instruction = instruction_from_validation_error(
        Erro("CE_005", Severidade.CRITICO, "Mesmo documento.", detalhe="Contrato: C-E1-01 usa E1-01 duas vezes.")
    )

    assert instruction["target"] == "C-E1-01"


def test_write_llm_feedback_escreve_json_valido(tmp_path):
    output = tmp_path / "llm_feedback.json"
    feedback = build_llm_feedback(ResultadoValidacao())

    returned = write_llm_feedback(feedback, output)

    assert returned == output
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


def test_pt_warnings_geram_instrucoes_medium_playtest():
    for code in ["PT_001", "PT_002", "PT_003", "PT_004", "PT_005", "PT_006", "PT_007", "PT_008", "PT_009"]:
        feedback = build_llm_feedback(resultado_com(Erro(code, Severidade.AVISO, "Warning de playtest.")))

        instruction = primeira_instrucao(feedback)
        assert instruction["priority"] == "medium"
        assert instruction["category"] == "playtest_metrics"

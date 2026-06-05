import copy
import json
import types
from pathlib import Path

from generator.models import Blueprint
from generator.obviousness_checker import check_obviousness
import generator.validator as validator_module
from generator.validator import BlueprintValidator

ROOT = Path(__file__).resolve().parents[1]
BEGINNER_CASE = ROOT / "examples" / "caso_canonico_iniciante.json"
INTERMEDIATE_CASE = ROOT / "examples" / "caso_canonico_intermediario.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_obviousness_checker_preserva_canonicos_atuais():
    for path in [BEGINNER_CASE, INTERMEDIATE_CASE]:
        report = check_obviousness(_load(path))

        assert report.findings == []


def test_obviousness_checker_detecta_confissao_em_documento_de_jogador():
    blueprint = _load(BEGINNER_CASE)
    doc = copy.deepcopy(blueprint["documentos"][0])
    doc["codigo"] = "E1-99"
    doc["conteudo"]["CORPO_CARTA"] = "<p>Fui eu que desviei a peça. Eu planejei tudo.</p>"
    blueprint["documentos"].append(doc)

    report = check_obviousness(blueprint)

    assert any(finding.code == "OBV_003" for finding in report.critical)


def test_obviousness_checker_exige_nome_acao_incriminadora_e_contexto_critico():
    blueprint = _load(INTERMEDIATE_CASE)
    doc = next(document for document in blueprint["documentos"] if document["codigo"] == "E1-04")
    doc["conteudo"]["DESCRICAO_OCORRENCIA"] = "Marta levou toalhas para a rouparia durante o turno."

    cotidiano = check_obviousness(blueprint)

    assert not any(finding.code == "OBV_002" for finding in cotidiano.findings)

    doc["conteudo"]["DESCRICAO_OCORRENCIA"] = "Marta tirou Helena do salão para impedir o brinde."
    obvio = check_obviousness(blueprint)

    assert any(finding.code == "OBV_002" for finding in obvio.moderate)


def test_validator_integra_guardrail_anti_obviedade():
    blueprint_dict = _load(BEGINNER_CASE)
    blueprint_dict["documentos"][1]["conteudo"]["CORPO_EMAIL"] = "<p>Claramente foi Marina quem desviou a peça.</p>"
    blueprint = Blueprint(**blueprint_dict)

    resultado = BlueprintValidator(blueprint).validar()

    assert any(erro.codigo == "OBV_002" for erro in resultado.moderados)


def test_obviousness_checker_detecta_chat_confessional():
    blueprint = _load(INTERMEDIATE_CASE)
    chat = next(document for document in blueprint["documentos"] if document["tipo"] == "chat")
    chat["conteudo"]["MENSAGENS"][0]["TEXTO_MENSAGEM"] = "Troquei a taça e ninguém vai descobrir."

    report = check_obviousness(blueprint)

    assert any(finding.code == "OBV_007" for finding in report.critical)


def test_obviousness_checker_detecta_vazamento_de_campo_e_valor_interno():
    blueprint = _load(BEGINNER_CASE)
    document = blueprint["documentos"][1]
    document["conteudo"]["CORPO_EMAIL"] = (
        f"<p>verdade_real: {blueprint['verdade_real']}</p>"
        f"<p>{blueprint['metodo_ocultacao']}</p>"
    )

    report = check_obviousness(blueprint)
    details = "\n".join(str(finding.detail) for finding in report.critical if finding.code == "OBV_010")

    assert any(finding.code == "OBV_010" for finding in report.critical)
    assert "verdade_real" in details
    assert "metodo_ocultacao" in details


def test_validator_detecta_prova_e_confirmacao_iguais_no_mesmo_contrato():
    blueprint_dict = _load(BEGINNER_CASE)
    contract = blueprint_dict["contratos_evidencia"][0]
    contract["confirmacao_independente"] = contract["prova_principal"]
    blueprint = Blueprint(**blueprint_dict)

    resultado = BlueprintValidator(blueprint).validar()

    assert any(erro.codigo == "CE_005" for erro in resultado.criticos)


def test_validator_avisa_documento_usado_em_muitos_contratos_obrigatorios():
    blueprint_dict = _load(INTERMEDIATE_CASE)
    base_contract = copy.deepcopy(blueprint_dict["contratos_evidencia"][0])
    required_contracts = []
    for index in range(4):
        contract = copy.deepcopy(base_contract)
        contract["id"] = f"C-TEST-USO-{index}"
        contract["fase"] = "E1"
        contract["prova_principal"] = "E1-01"
        contract["confirmacao_independente"] = "E1-03"
        contract["obrigatoria_para_avanco"] = True
        required_contracts.append(contract)
    blueprint_dict["contratos_evidencia"] = required_contracts
    blueprint = Blueprint(**blueprint_dict)

    resultado = BlueprintValidator(blueprint).validar()

    assert any(erro.codigo == "CE_011" and erro.documento == "E1-01" for erro in resultado.avisos)


def test_obviousness_checker_avisa_objetivo_narrativo_com_culpado_e_acao():
    blueprint = _load(INTERMEDIATE_CASE)
    document = next(item for item in blueprint["documentos"] if item["codigo"] == "E1-04")
    document["objetivo_narrativo"] = "Mostrar que Marta sabotou o brinde."

    report = check_obviousness(blueprint)

    assert any(finding.code == "OBV_004" for finding in report.warnings)


def test_obviousness_checker_sinaliza_e1_antecipando_solucao_final():
    blueprint = _load(INTERMEDIATE_CASE)
    document = next(item for item in blueprint["documentos"] if item["envelope"] == "E1")
    document["conteudo"]["CORPO_CARTA"] = "<p>A solução final aponta Marta como culpada.</p>"

    report = check_obviousness(blueprint)

    assert any(finding.code == "OBV_005" for finding in report.moderate)


def test_validator_reporta_falha_interna_do_checker_sem_traceback(monkeypatch):
    blueprint = Blueprint(**_load(BEGINNER_CASE))

    def fake_import_module(name, package=None):
        if "obviousness_checker" in name:
            return types.SimpleNamespace(
                ObviousnessSeverity=types.SimpleNamespace(CRITICAL="critical", MODERATE="moderate", WARNING="warning"),
                check_obviousness=lambda _blueprint: (_ for _ in ()).throw(RuntimeError("boom")),
            )
        return validator_module.importlib.import_module(name, package)

    monkeypatch.setattr(validator_module.importlib, "import_module", fake_import_module)

    resultado = BlueprintValidator(blueprint).validar()

    assert any(erro.codigo == "OBV_CHECKER_001" for erro in resultado.criticos)

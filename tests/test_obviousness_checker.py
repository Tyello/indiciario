import copy
import json
from pathlib import Path

from generator.models import Blueprint
from generator.obviousness_checker import check_obviousness
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

import copy
import json
from pathlib import Path

from generator.llm_feedback import build_llm_feedback
from generator.models import Blueprint
from generator.validator import BlueprintValidator

CANONICAL = Path("examples/caso_canonico_intermediario.json")
LEGACY = Path("examples/exemplo_blueprint.json")


def _load(path: Path = CANONICAL) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _codes(resultado):
    return {item.codigo for item in resultado.erros + resultado.avisos}


def _valid_hint() -> dict:
    return {
        "id": "DC-TEST-01",
        "categoria": "documento",
        "fase": "E1",
        "titulo": "Comparação inicial",
        "condicao_uso": "Quando o grupo leu E1-04, mas ainda não comparou com E1-05.",
        "texto": "Peça para comparar o horário do log com a escala.",
        "nivel": "leve",
        "contratos_relacionados": ["C-E1-OPORTUNIDADE"],
        "documentos_relacionados": ["E1-04", "E1-05"],
    }


def _blueprint_with_hint(mutator=None) -> Blueprint:
    data = _load()
    hint = _valid_hint()
    if mutator:
        mutator(hint, data)
    data["dicas_contextuais"] = [hint]
    return Blueprint(**data)


def test_blueprint_antigo_sem_dicas_contextuais_continua_parseavel_e_validavel():
    data = _load(LEGACY)
    data.pop("dicas_contextuais", None)

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert "DC_001" not in _codes(resultado)
    assert "DC_002" not in _codes(resultado)


def test_dica_contextual_valida_passa_sem_dc_errors():
    resultado = BlueprintValidator(_blueprint_with_hint()).validar()

    assert not any(codigo.startswith("DC_") for codigo in _codes(resultado))


def test_dica_contextual_id_duplicado_gera_dc_002():
    data = _load()
    hint = _valid_hint()
    data["dicas_contextuais"] = [hint, copy.deepcopy(hint)]

    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert "DC_002" in _codes(resultado)


def test_dica_contextual_fase_invalida_gera_dc_003():
    resultado = BlueprintValidator(_blueprint_with_hint(lambda hint, _data: hint.update(fase="ato1"))).validar()

    assert "DC_003" in _codes(resultado)


def test_dica_contextual_texto_vazio_gera_dc_004():
    resultado = BlueprintValidator(_blueprint_with_hint(lambda hint, _data: hint.update(texto="  "))).validar()

    assert "DC_004" in _codes(resultado)


def test_dica_contextual_condicao_vazia_gera_dc_005():
    resultado = BlueprintValidator(_blueprint_with_hint(lambda hint, _data: hint.update(condicao_uso=""))).validar()

    assert "DC_005" in _codes(resultado)


def test_dica_contextual_contrato_inexistente_gera_dc_006():
    resultado = BlueprintValidator(
        _blueprint_with_hint(lambda hint, _data: hint.update(contratos_relacionados=["C-INEXISTENTE"]))
    ).validar()

    assert "DC_006" in _codes(resultado)


def test_dica_contextual_documento_inexistente_gera_dc_007():
    resultado = BlueprintValidator(
        _blueprint_with_hint(lambda hint, _data: hint.update(documentos_relacionados=["E9-99"]))
    ).validar()

    assert "DC_007" in _codes(resultado)


def test_dica_contextual_nivel_invalido_gera_dc_008():
    resultado = BlueprintValidator(_blueprint_with_hint(lambda hint, _data: hint.update(nivel="baixo"))).validar()

    assert "DC_008" in _codes(resultado)


def test_dica_contextual_categoria_invalida_gera_dc_009():
    resultado = BlueprintValidator(_blueprint_with_hint(lambda hint, _data: hint.update(categoria="misterio"))).validar()

    assert "DC_009" in _codes(resultado)


def test_caso_canonico_tem_dicas_contextuais():
    blueprint = Blueprint(**_load())

    assert len(blueprint.dicas_contextuais) >= 5
    assert sum(1 for dica in blueprint.dicas_contextuais if dica.fase == "E1") >= 2
    assert sum(1 for dica in blueprint.dicas_contextuais if dica.fase == "E2") >= 2
    assert any(dica.fase == "final" and dica.nivel == "quase_gabarito" for dica in blueprint.dicas_contextuais)


def test_llm_feedback_nao_trata_dc_warning_como_critico():
    data = _load()
    data["dicas_contextuais"] = []
    resultado = BlueprintValidator(Blueprint(**data)).validar()
    feedback = build_llm_feedback(resultado)

    warning = next(item for item in feedback["instructions"] if item["code"] == "DC_000")
    assert warning["priority"] == "medium"
    assert feedback["critical_count"] == 0

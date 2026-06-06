import json
from pathlib import Path

from generator.models import Blueprint
from generator.validator import BlueprintValidator


def load_data() -> dict:
    return json.loads(Path("examples/caso_canonico_iniciante.json").read_text(encoding="utf-8"))


def codes(data: dict) -> set[str]:
    result = BlueprintValidator(Blueprint(**data)).validar()
    return {erro.codigo for erro in result.erros + result.avisos}


def test_mapa_p2_canonico_nao_emite_map() -> None:
    assert not {code for code in codes(load_data()) if code.startswith("MAP_")}


def test_porta_area_inexistente_gera_map_002() -> None:
    data = load_data()
    data["visual_procedural"]["mapas"][0]["portas"][0]["area_b"] = "fantasma"
    assert "MAP_002" in codes(data)


def test_janela_area_inexistente_gera_map_003() -> None:
    data = load_data()
    data["visual_procedural"]["mapas"][0]["janelas"][0]["area"] = "fantasma"
    assert "MAP_003" in codes(data)


def test_camera_area_inexistente_e_sem_parede_gera_map_004_007() -> None:
    data = load_data()
    data["visual_procedural"]["mapas"][0]["cameras"][0]["area"] = "fantasma"
    data["visual_procedural"]["mapas"][0]["cameras"][0]["parede"] = ""
    data["visual_procedural"]["mapas"][0]["cameras"][0]["posicao"] = None
    found = codes(data)
    assert "MAP_004" in found
    assert "MAP_007" in found


def test_posicao_invalida_gera_map_005_006() -> None:
    data = load_data()
    data["visual_procedural"]["mapas"][0]["portas"][0]["posicao"] = 999
    data["visual_procedural"]["mapas"][0]["janelas"][0]["posicao"] = 999
    found = codes(data)
    assert "MAP_005" in found
    assert "MAP_006" in found


def test_termos_proibidos_geram_map_008_010() -> None:
    data = load_data()
    data["visual_procedural"]["mapas"][0]["legenda"].append({"simbolo": "X", "descricao": "rota provável"})
    found = codes(data)
    assert "MAP_008" in found
    assert "MAP_010" in found


def test_hotel_aurora_continua_sem_mapa() -> None:
    data = json.loads(Path("examples/caso_canonico_intermediario.json").read_text(encoding="utf-8"))
    blueprint = Blueprint(**data)
    assert blueprint.visual_procedural is not None
    assert blueprint.visual_procedural.mapas == []
    assert not {code for code in codes(data) if code.startswith("MAP_")}

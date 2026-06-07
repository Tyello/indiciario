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


def _areas_by_id(data: dict) -> dict:
    return {area["id"]: area for area in data["visual_procedural"]["mapas"][0]["areas"]}


def _wall_coordinate(area: dict, wall: str) -> float:
    if wall == "norte":
        return area["y"]
    if wall == "sul":
        return area["y"] + area["h"]
    if wall == "oeste":
        return area["x"]
    return area["x"] + area["w"]


def _wall_axis_start(area: dict, wall: str) -> float:
    return area["x"] if wall in {"norte", "sul"} else area["y"]


def _wall_length(area: dict, wall: str) -> float:
    return area["w"] if wall in {"norte", "sul"} else area["h"]


def _door_is_on_shared_wall(porta: dict, areas: dict) -> bool:
    opposite = {"norte": "sul", "sul": "norte", "leste": "oeste", "oeste": "leste"}
    area_a = areas[porta["area_a"]]
    area_b = areas[porta["area_b"]]
    wall_a = porta["parede"]
    wall_b = opposite[wall_a]
    if abs(_wall_coordinate(area_a, wall_a) - _wall_coordinate(area_b, wall_b)) > 0.01:
        return False

    door_start = _wall_axis_start(area_a, wall_a) + porta["posicao"]
    door_end = door_start + porta["largura"]
    wall_start = _wall_axis_start(area_b, wall_b)
    wall_end = wall_start + _wall_length(area_b, wall_b)
    return wall_start - 0.01 <= door_start and door_end <= wall_end + 0.01


def test_mapa_iniciante_renderiza_com_geometria_compartilhada() -> None:
    from generator.models import Blueprint
    from generator.visual_procedural import build_map_svg

    data = load_data()
    blueprint = Blueprint(**data)
    mapa = blueprint.visual_procedural.mapas[0]  # type: ignore[union-attr]
    svg = build_map_svg(mapa)
    areas = _areas_by_id(data)

    assert svg.startswith("<svg")
    assert 'class="door"' in svg
    assert 'class="window"' in svg
    assert 'class="camera"' in svg
    assert {porta["area_a"] for porta in data["visual_procedural"]["mapas"][0]["portas"]} <= set(areas)
    assert {porta["area_b"] for porta in data["visual_procedural"]["mapas"][0]["portas"] if porta.get("area_b")} <= set(areas)
    assert all(
        _door_is_on_shared_wall(porta, areas)
        for porta in data["visual_procedural"]["mapas"][0]["portas"]
        if porta.get("area_b")
    )


def test_mapa_iniciante_tem_adjacencias_principais_sem_conectores() -> None:
    from generator.models import Blueprint
    from generator.visual_procedural import build_map_svg

    data = load_data()
    areas = _areas_by_id(data)
    portas = data["visual_procedural"]["mapas"][0]["portas"]
    pares = {frozenset((porta["area_a"], porta["area_b"])) for porta in portas if porta.get("area_b")}

    assert frozenset(("corredor_tecnico", "guarita")) in pares
    assert frozenset(("corredor_tecnico", "administracao")) in pares
    assert frozenset(("corredor_tecnico", "sala_seguranca")) in pares
    assert frozenset(("corredor_tecnico", "reserva_a")) in pares
    assert frozenset(("corredor_tecnico", "reserva_b")) in pares
    assert frozenset(("corredor_tecnico", "vitrine")) in pares
    assert all(_door_is_on_shared_wall(porta, areas) for porta in portas if porta.get("area_b"))

    blueprint = Blueprint(**data)
    mapa = blueprint.visual_procedural.mapas[0]  # type: ignore[union-attr]
    svg = build_map_svg(mapa).lower()
    forbidden = [
        "rota provável",
        ">rota",
        "solução",
        "solucao",
        "caminho",
        "área crítica",
        "area critica",
        "conector",
        "connector",
        "stroke-dasharray",
        "#1d4ed8",
    ]
    assert not any(term in svg for term in forbidden)

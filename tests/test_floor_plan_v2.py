import json
from pathlib import Path

from generator.floor_plan import (
    TERMOS_PROIBIDOS_JOGADOR,
    build_mirante_planta,
    render_floor_plan_svg,
    validar_planta,
)
from generator.models import Blueprint
from generator.visual_procedural import build_map_svg


def test_build_mirante_planta_retorna_planta_valida() -> None:
    planta = build_mirante_planta()

    assert planta.id == "casa_acervo_mirante_v2"
    assert planta.largura > planta.altura
    assert validar_planta(planta) == []


def test_render_floor_plan_svg_mirante_v2_gera_svg_com_ambientes() -> None:
    svg = render_floor_plan_svg(build_mirante_planta())

    assert svg.startswith("<svg")
    assert "Recepção / Controle" in svg
    assert "Galeria / Vitrine" in svg
    assert "Corredor Técnico" in svg
    assert "Reserva Técnica A" in svg
    assert "Reserva Técnica B" in svg
    assert "Segurança" in svg
    assert "Doca / Serviço" in svg
    assert "Administração" in svg


def test_svg_jogador_mirante_v2_nao_contem_linguagem_de_solucao() -> None:
    svg = render_floor_plan_svg(build_mirante_planta()).lower()

    for termo in TERMOS_PROIBIDOS_JOGADOR:
        assert termo not in svg


def test_elementos_mirante_v2_referenciam_areas_existentes() -> None:
    planta = build_mirante_planta()
    area_ids = {area.id for area in planta.areas}

    for porta in planta.portas:
        assert all(ref in area_ids or ref == "exterior" for ref in porta.entre)
    for janela in planta.janelas:
        assert janela.area in area_ids
    for camera in planta.cameras:
        assert camera.area in area_ids


def test_hotel_aurora_continua_sem_mapa() -> None:
    data = json.loads(Path("examples/caso_canonico_intermediario.json").read_text(encoding="utf-8"))
    blueprint = Blueprint(**data)

    assert blueprint.visual_procedural is not None
    assert blueprint.visual_procedural.mapas == []


def test_pipeline_atual_renderiza_documento_visual_do_mirante_com_planta_v2() -> None:
    data = json.loads(Path("examples/caso_canonico_iniciante.json").read_text(encoding="utf-8"))
    blueprint = Blueprint(**data)
    mapa = blueprint.visual_procedural.mapas[0]  # type: ignore[union-attr]

    svg = build_map_svg(mapa)

    assert "casa_acervo_mirante_v2" not in svg  # modelo interno não vaza como rótulo de sala
    assert "Recepção / Controle" in svg
    assert "Guarita" not in svg
    assert "Doca / Serviço" in svg

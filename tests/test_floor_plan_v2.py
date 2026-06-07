import json
from pathlib import Path

from generator.floor_plan import (
    TERMOS_PROIBIDOS_JOGADOR,
    AreaPlanta,
    PlantaBaixa,
    _building_bounds,
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


def test_mirante_v2_separa_codigos_de_ambiente_e_porta() -> None:
    planta = build_mirante_planta()
    codigos_ambiente = {area.codigo for area in planta.areas}
    codigos_porta = {porta.id for porta in planta.portas}

    assert "A-01" in codigos_ambiente
    assert "P-01" in codigos_porta
    assert all(codigo.startswith("A-") for codigo in codigos_ambiente)
    assert all(not codigo.startswith("P-") for codigo in codigos_ambiente)
    assert all(codigo.startswith("P-") for codigo in codigos_porta)
    assert all(not codigo.startswith("A-") for codigo in codigos_porta)
    assert codigos_ambiente.isdisjoint(codigos_porta)


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


def test_svg_mirante_v2_exibe_codigos_distintos_de_ambiente_e_porta() -> None:
    svg = render_floor_plan_svg(build_mirante_planta())

    assert ">A-01</text>" in svg
    assert ">P-01</text>" in svg


def test_footprint_do_svg_deriva_da_geometria_da_planta() -> None:
    planta = build_mirante_planta()
    bx, by, bw, bh = _building_bounds(planta)
    svg = render_floor_plan_svg(planta)
    source = Path("generator/floor_plan.py").read_text(encoding="utf-8")

    assert f'<rect x="{bx:g}" y="{by:g}" width="{bw:g}" height="{bh:g}" fill="url(#wall-hatch)"' in svg
    assert '<rect x="60" y="60" width="880" height="410" fill="url(#wall-hatch)"' not in source


def test_footprint_muda_quando_geometria_da_planta_muda() -> None:
    planta = PlantaBaixa(
        id="teste_footprint",
        titulo="Planta de teste",
        largura=300,
        altura=200,
        areas=(AreaPlanta("sala_teste", "Sala Teste", 30, 40, 50, 60, codigo="A-01"),),
        portas=(),
        janelas=(),
        cameras=(),
    )

    svg = render_floor_plan_svg(planta)

    assert '<rect x="10" y="20" width="90" height="100" fill="url(#wall-hatch)"' in svg
    assert '<rect x="60" y="60" width="880" height="410" fill="url(#wall-hatch)"' not in svg


def test_svg_jogador_mirante_v2_nao_contem_linguagem_de_solucao() -> None:
    svg = render_floor_plan_svg(build_mirante_planta()).lower()

    termos_proibidos = (*TERMOS_PROIBIDOS_JOGADOR, "debug", "facilitador", "casa_acervo_mirante_v2")
    for termo in termos_proibidos:
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
    assert "A-01" in svg
    assert "P-01" in svg
    assert "Recepção / Controle" in svg
    assert "Guarita" not in svg
    assert "Doca / Serviço" in svg

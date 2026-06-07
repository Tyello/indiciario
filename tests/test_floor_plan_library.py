from generator.floor_plan import PlantaBaixa, render_floor_plan_svg, validar_planta
from generator.floor_plan_library import build_escritorio_planta_base, build_hotel_planta_base


FORBIDDEN_VISUAL_TERMS = ("rota", "solução", "área crítica", "offline", "culpado", "caminho")


def _assert_valid_base_planta(planta: PlantaBaixa) -> None:
    assert isinstance(planta, PlantaBaixa)
    assert validar_planta(planta) == []
    assert planta.areas
    assert planta.portas
    assert planta.janelas
    assert planta.cameras
    assert all(area.codigo.startswith("A-") for area in planta.areas)
    assert all(porta.id.startswith("P-") for porta in planta.portas)
    assert len({area.id for area in planta.areas}) == len(planta.areas)
    assert len({porta.id for porta in planta.portas}) == len(planta.portas)

    svg = render_floor_plan_svg(planta).lower()
    assert svg.startswith("<svg")
    assert "<image" not in svg
    assert "<script" not in svg
    assert "qr" not in svg
    for term in FORBIDDEN_VISUAL_TERMS:
        assert term not in svg


def test_build_hotel_planta_base_is_valid_structured_floor_plan() -> None:
    planta = build_hotel_planta_base()

    _assert_valid_base_planta(planta)
    assert planta.id == "hotel_planta_base_v1"
    assert "Aurora" not in planta.titulo
    assert planta.areas_externas
    assert planta.portoes
    assert any(porta.controle_acesso for porta in planta.portas)


def test_build_escritorio_planta_base_is_valid_structured_floor_plan() -> None:
    planta = build_escritorio_planta_base()

    _assert_valid_base_planta(planta)
    assert planta.id == "escritorio_planta_base_v1"
    assert not planta.areas_externas
    assert any(porta.controle_acesso for porta in planta.portas)


def test_floor_plan_library_reuses_existing_renderer_contract() -> None:
    hotel_svg = render_floor_plan_svg(build_hotel_planta_base())
    escritorio_svg = render_floor_plan_svg(build_escritorio_planta_base())

    assert "site-perimeter" in hotel_svg
    assert "class=\"outer\"" in hotel_svg
    assert "class=\"inner\"" in hotel_svg
    assert "class=\"door\"" in escritorio_svg
    assert "CAM-" in escritorio_svg

from generator.floorplan_renderer import render_floorplan_svg
from generator.models import MapaProcedural


def _mapa() -> MapaProcedural:
    return MapaProcedural(
        id="m1",
        titulo="Planta teste",
        orientacao="landscape",
        largura=300,
        altura=180,
        areas=[
            {"id": "sala", "nome": "Sala", "x": 30, "y": 30, "w": 100, "h": 80, "tipo": "sala", "observacao": "A-01"},
            {"id": "corredor", "nome": "Corredor", "x": 130, "y": 30, "w": 120, "h": 80, "tipo": "corredor", "observacao": "A-02"},
        ],
        portas=[{"id": "P-01", "area_a": "sala", "area_b": "corredor", "parede": "leste", "posicao": 25, "largura": 25}],
        janelas=[{"id": "J-01", "area": "sala", "parede": "norte", "posicao": 20, "largura": 40}],
        cameras=[{"id": "C-01", "area": "corredor", "parede": "sul", "posicao": 40}],
    )


def test_floorplan_svg_p2_pb_sem_residuos_tecnicos() -> None:
    svg = render_floorplan_svg(_mapa())

    assert svg.startswith("<svg")
    assert 'fill="#fff"' in svg
    assert 'class="door"' in svg
    assert 'class="window"' in svg
    assert 'class="camera"' in svg
    assert "Planta operacional simplificada" in svg
    assert ">rota<" not in svg.lower()
    assert "offline" not in svg.lower()
    assert "#1d4ed8" not in svg

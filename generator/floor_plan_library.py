"""Biblioteca mínima de plantas baixas estruturadas reutilizáveis.

A Visual Library 2.0 começa com bases genéricas de planta baixa, sem vínculo
com casos canônicos. Os builders abaixo reutilizam o mesmo modelo e renderer da
planta v2 do Mirante para manter assets offline, P&B first e compatíveis com
PDF via Playwright.
"""

from __future__ import annotations

from .floor_plan import (
    EXTERIOR,
    AreaExternaPlanta,
    AreaPlanta,
    CameraPlanta,
    JanelaPlanta,
    PlantaBaixa,
    PortaPlanta,
    PortaoPlanta,
    render_floor_plan_svg,
)

__all__ = [
    "build_escritorio_planta_base",
    "build_hotel_planta_base",
    "render_floor_plan_svg",
]


def build_hotel_planta_base() -> PlantaBaixa:
    """Cria uma planta-base genérica de hotel para casos futuros.

    A base representa um térreo operacional plausível: lobby, recepção,
    circulação, quartos simples, administração, áreas de serviço e pátio. Ela
    não corresponde ao Hotel Aurora canônico e não deve ser integrada
    automaticamente a nenhum caso.
    """
    areas = (
        AreaPlanta("lobby", "Lobby", 80, 90, 260, 150, "publico", "A-01"),
        AreaPlanta("recepcao", "Recepção", 340, 90, 120, 150, "controle", "A-02"),
        AreaPlanta("corredor_servico", "Corredor de Serviço", 80, 240, 780, 90, "circulacao", "A-03"),
        AreaPlanta("quarto_101", "Quarto 101", 80, 330, 110, 150, "hospedagem", "A-04"),
        AreaPlanta("quarto_102", "Quarto 102", 190, 330, 110, 150, "hospedagem", "A-05"),
        AreaPlanta("administracao", "Administração", 300, 330, 160, 150, "administrativo", "A-06"),
        AreaPlanta("elevadores", "Elevadores", 460, 330, 120, 150, "circulacao", "A-07"),
        AreaPlanta("servico", "Serviço", 580, 330, 160, 150, "servico", "A-08"),
        AreaPlanta("deposito", "Depósito", 740, 330, 120, 150, "apoio", "A-09"),
    )
    areas_externas = (
        AreaExternaPlanta("patio_servico", "Pátio de Serviço", 560, 482, 240, 66, "servico", "EXT-01"),
        AreaExternaPlanta("guarita", "Guarita", 820, 470, 56, 46, "controle", "PC-01"),
    )
    portas = (
        PortaPlanta("P-01", ("lobby", EXTERIOR), "H", 170, 90, 54),
        PortaPlanta("P-02", ("lobby", "corredor_servico"), "H", 178, 240, 42),
        PortaPlanta("P-03", ("recepcao", "corredor_servico"), "H", 382, 240, 36, True),
        PortaPlanta("P-04", ("quarto_101", "corredor_servico"), "H", 118, 330, 32, True),
        PortaPlanta("P-05", ("quarto_102", "corredor_servico"), "H", 228, 330, 32, True),
        PortaPlanta("P-06", ("administracao", "corredor_servico"), "H", 356, 330, 34, True),
        PortaPlanta("P-07", ("elevadores", "corredor_servico"), "H", 502, 330, 38),
        PortaPlanta("P-08", ("servico", "corredor_servico"), "H", 636, 330, 40, True),
        PortaPlanta("P-09", ("deposito", "corredor_servico"), "H", 786, 330, 34, True),
        PortaPlanta("P-10", ("servico", EXTERIOR), "H", 626, 480, 52, True),
        PortaPlanta("P-11", ("lobby", "recepcao"), "V", 340, 146, 34),
    )
    janelas = (
        JanelaPlanta("J-01", "lobby", "H", 110, 90, 70),
        JanelaPlanta("J-02", "lobby", "H", 240, 90, 60),
        JanelaPlanta("J-03", "recepcao", "H", 368, 90, 54),
        JanelaPlanta("J-04", "quarto_101", "V", 80, 372, 56),
        JanelaPlanta("J-05", "quarto_102", "H", 218, 480, 46),
        JanelaPlanta("J-06", "administracao", "H", 336, 480, 54),
        JanelaPlanta("J-07", "deposito", "V", 860, 376, 46),
    )
    cameras = (
        CameraPlanta("CAM-01", "lobby", 340, 240, "NO"),
        CameraPlanta("CAM-02", "corredor_servico", 860, 285, "O"),
        CameraPlanta("CAM-03", "servico", 580, 330, "SE"),
        CameraPlanta("CAM-04", "quarto_102", 300, 330, "SO"),
    )
    portoes = (
        PortaoPlanta("G-01", 900, 496, 54, "V"),
    )
    return PlantaBaixa(
        id="hotel_planta_base_v1",
        titulo="Hotel — planta baixa operacional base",
        largura=980,
        altura=610,
        areas=areas,
        portas=portas,
        janelas=janelas,
        cameras=cameras,
        areas_externas=areas_externas,
        portoes=portoes,
    )


def build_escritorio_planta_base() -> PlantaBaixa:
    """Cria uma planta-base genérica de escritório para casos futuros.

    A base prioriza leitura operacional: recepção, sala de reunião, estação de
    trabalho, diretoria, arquivo, TI e apoios internos. O asset é neutro e não
    contém rota, destaque ou camada interpretativa.
    """
    areas = (
        AreaPlanta("recepcao", "Recepção", 80, 80, 180, 120, "publico", "A-01"),
        AreaPlanta("sala_reuniao", "Sala de Reunião", 260, 80, 220, 120, "reuniao", "A-02"),
        AreaPlanta("area_trabalho", "Área de Trabalho", 480, 80, 300, 250, "operacional", "A-03"),
        AreaPlanta("corredor", "Corredor", 80, 200, 400, 80, "circulacao", "A-04"),
        AreaPlanta("diretoria", "Diretoria", 80, 280, 180, 130, "administrativo", "A-05"),
        AreaPlanta("arquivo", "Arquivo", 260, 280, 110, 130, "arquivo", "A-06"),
        AreaPlanta("ti", "TI", 370, 280, 110, 130, "tecnico", "A-07"),
        AreaPlanta("copa", "Copa", 480, 330, 150, 80, "apoio", "A-08"),
        AreaPlanta("apoio", "Apoio", 630, 330, 150, 80, "apoio", "A-09"),
    )
    portas = (
        PortaPlanta("P-01", ("recepcao", EXTERIOR), "H", 132, 80, 48),
        PortaPlanta("P-02", ("recepcao", "corredor"), "H", 150, 200, 38),
        PortaPlanta("P-03", ("sala_reuniao", "corredor"), "H", 338, 200, 42),
        PortaPlanta("P-04", ("area_trabalho", "corredor"), "V", 480, 222, 38, True),
        PortaPlanta("P-05", ("diretoria", "corredor"), "H", 150, 280, 34, True),
        PortaPlanta("P-06", ("arquivo", "corredor"), "H", 298, 280, 32, True),
        PortaPlanta("P-07", ("ti", "corredor"), "H", 408, 280, 32, True),
        PortaPlanta("P-08", ("area_trabalho", "copa"), "H", 526, 330, 34),
        PortaPlanta("P-09", ("area_trabalho", "apoio"), "H", 682, 330, 34),
        PortaPlanta("P-10", ("sala_reuniao", "area_trabalho"), "V", 480, 122, 36),
    )
    janelas = (
        JanelaPlanta("J-01", "recepcao", "H", 96, 80, 54),
        JanelaPlanta("J-02", "sala_reuniao", "H", 306, 80, 82),
        JanelaPlanta("J-03", "area_trabalho", "H", 540, 80, 100),
        JanelaPlanta("J-04", "area_trabalho", "V", 780, 168, 72),
        JanelaPlanta("J-05", "diretoria", "H", 126, 410, 56),
        JanelaPlanta("J-06", "apoio", "H", 670, 410, 52),
    )
    cameras = (
        CameraPlanta("CAM-01", "recepcao", 260, 200, "NO"),
        CameraPlanta("CAM-02", "corredor", 480, 240, "O"),
        CameraPlanta("CAM-03", "area_trabalho", 780, 80, "SO"),
        CameraPlanta("CAM-04", "arquivo", 370, 280, "SO"),
    )
    return PlantaBaixa(
        id="escritorio_planta_base_v1",
        titulo="Escritório — planta baixa operacional base",
        largura=900,
        altura=560,
        areas=areas,
        portas=portas,
        janelas=janelas,
        cameras=cameras,
    )

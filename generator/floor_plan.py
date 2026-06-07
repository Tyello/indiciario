"""Plantas baixas v2 modeladas por geometria estruturada.

Este módulo representa plantas como dados arquitetônicos simples e renderiza SVG
P&B sem depender de imagens de fundo ou diagramas hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import isclose

ORIENTACOES = {"H", "V"}
EXTERIOR = "exterior"
TERMOS_PROIBIDOS_JOGADOR = (
    "rota",
    "solução",
    "área crítica",
    "offline",
    "culpado",
    "caminho",
)
EPSILON = 0.01
SITE_PADDING = 24


@dataclass(frozen=True)
class AreaPlanta:
    id: str
    nome: str
    x: float
    y: float
    w: float
    h: float
    tipo: str = "ambiente"
    codigo: str = ""


@dataclass(frozen=True)
class PortaPlanta:
    id: str
    entre: tuple[str, str]
    orientacao: str  # "H" ou "V"
    x: float
    y: float
    largura: float = 28
    controle_acesso: bool = False


@dataclass(frozen=True)
class AreaExternaPlanta:
    id: str
    nome: str
    x: float
    y: float
    w: float
    h: float
    tipo: str = "externo"
    codigo: str = ""


@dataclass(frozen=True)
class PortaoPlanta:
    id: str
    x: float
    y: float
    largura: float
    orientacao: str = "H"


@dataclass(frozen=True)
class JanelaPlanta:
    id: str
    area: str
    orientacao: str
    x: float
    y: float
    largura: float = 32


@dataclass(frozen=True)
class CameraPlanta:
    id: str
    area: str
    x: float
    y: float
    orientacao: str


@dataclass(frozen=True)
class PlantaBaixa:
    id: str
    titulo: str
    largura: float
    altura: float
    areas: tuple[AreaPlanta, ...]
    portas: tuple[PortaPlanta, ...]
    janelas: tuple[JanelaPlanta, ...]
    cameras: tuple[CameraPlanta, ...]
    areas_externas: tuple[AreaExternaPlanta, ...] = ()
    portoes: tuple[PortaoPlanta, ...] = ()


@dataclass(frozen=True)
class SegmentoParede:
    orientacao: str
    coord: float
    inicio: float
    fim: float
    externa: bool


def build_mirante_planta() -> PlantaBaixa:
    """Cria a planta v2 canônica da Casa de Acervo Mirante.

    A geometria usa salas retangulares adjacentes a um corredor técnico contínuo,
    formando um pequeno museu/acervo operacional sem rotas, destaques ou camadas
    de solução no mapa do jogador.
    """
    areas = (
        AreaPlanta("recepcao_controle", "Recepção / Controle", 80, 80, 180, 140, "controle", "A-01"),
        AreaPlanta("galeria_vitrine", "Galeria / Vitrine", 260, 80, 250, 140, "exposicao", "A-02"),
        AreaPlanta("reserva_a", "Reserva Técnica A", 510, 80, 170, 140, "reserva", "A-03"),
        AreaPlanta("reserva_b", "Reserva Técnica B", 680, 80, 160, 140, "reserva", "A-04"),
        AreaPlanta("corredor_tecnico", "Corredor Técnico", 80, 220, 840, 95, "circulacao", "A-05"),
        AreaPlanta("administracao", "Administração", 80, 315, 180, 135, "administrativo", "A-06"),
        AreaPlanta("monitoramento", "Monitoramento", 260, 315, 120, 86, "controle", "A-07"),
        AreaPlanta("apoio", "Apoio / Arquivo", 380, 315, 210, 135, "apoio", "A-08"),
        AreaPlanta("doca_servico", "Doca / Serviço", 590, 315, 250, 135, "servico", "A-09"),
    )
    areas_externas = (
        AreaExternaPlanta("acesso_publico", "Calçada / Acesso Público", 82, 24, 170, 42, "publico", "EXT-02"),
        AreaExternaPlanta("patio_operacional", "Pátio Operacional", 570, 452, 310, 72, "servico", "EXT-01"),
        AreaExternaPlanta("posto_controle", "Posto de Controle", 858, 395, 62, 48, "controle", "PC-01"),
    )
    portas = (
        PortaPlanta("P-01", ("recepcao_controle", EXTERIOR), "H", 142, 80, 34),
        PortaPlanta("P-02", ("recepcao_controle", "corredor_tecnico"), "H", 168, 220, 34),
        PortaPlanta("P-03", ("galeria_vitrine", "corredor_tecnico"), "H", 350, 220, 42),
        PortaPlanta("P-04", ("reserva_a", "corredor_tecnico"), "H", 580, 220, 34, True),
        PortaPlanta("P-05", ("reserva_b", "corredor_tecnico"), "H", 734, 220, 34, True),
        PortaPlanta("P-06", ("administracao", "corredor_tecnico"), "H", 156, 315, 34),
        PortaPlanta("P-07", ("monitoramento", "corredor_tecnico"), "H", 303, 315, 30, True),
        PortaPlanta("P-08", ("apoio", "corredor_tecnico"), "H", 486, 315, 32),
        PortaPlanta("P-09", ("doca_servico", "corredor_tecnico"), "H", 684, 315, 42, True),
        PortaPlanta("P-10", ("doca_servico", EXTERIOR), "H", 760, 450, 56, True),
        PortaPlanta("P-11", ("galeria_vitrine", "reserva_a"), "V", 510, 132, 34),
    )
    janelas = (
        JanelaPlanta("J-01", "recepcao_controle", "H", 94, 80, 48),
        JanelaPlanta("J-02", "galeria_vitrine", "H", 312, 80, 88),
        JanelaPlanta("J-03", "reserva_a", "H", 548, 80, 50),
        JanelaPlanta("J-04", "reserva_b", "H", 720, 80, 54),
        JanelaPlanta("J-05", "administracao", "H", 118, 450, 58),
        JanelaPlanta("J-06", "doca_servico", "V", 840, 350, 50),
    )
    cameras = (
        CameraPlanta("CAM-01", "recepcao_controle", 260, 220, "SO"),
        CameraPlanta("CAM-02", "corredor_tecnico", 920, 260, "O"),
        CameraPlanta("CAM-03", "monitoramento", 260, 315, "NE"),
        CameraPlanta("CAM-04", "galeria_vitrine", 510, 220, "NO"),
    )
    portoes = (
        PortaoPlanta("G-01", 944, 464, 56, "V"),
        PortaoPlanta("G-02", 130, 0, 74, "H"),
    )
    return PlantaBaixa(
        id="casa_acervo_mirante_v2",
        titulo="Casa de Acervo Mirante — planta baixa operacional",
        largura=1000,
        altura=620,
        areas=areas,
        portas=portas,
        janelas=janelas,
        cameras=cameras,
        areas_externas=areas_externas,
        portoes=portoes,
    )


def _area_ids(planta: PlantaBaixa) -> set[str]:
    return {area.id for area in planta.areas}


def _area_by_id(planta: PlantaBaixa) -> dict[str, AreaPlanta]:
    return {area.id: area for area in planta.areas}


def _inside(area: AreaPlanta, planta: PlantaBaixa) -> bool:
    return area.x >= 0 and area.y >= 0 and area.w > 0 and area.h > 0 and area.x + area.w <= planta.largura and area.y + area.h <= planta.altura



def _site_bounds(planta: PlantaBaixa, padding: float = SITE_PADDING) -> tuple[float, float, float, float]:
    """Calcula o perímetro controlado do terreno/lote da planta."""
    elementos = [*planta.areas, *planta.areas_externas]
    if not elementos:
        return 0, 0, planta.largura, planta.altura

    min_x = min(area.x for area in elementos)
    min_y = min(area.y for area in elementos)
    max_x = max(area.x + area.w for area in elementos)
    max_y = max(area.y + area.h for area in elementos)
    safe_padding = min(padding, min_x, min_y, planta.largura - max_x, planta.altura - max_y)
    safe_padding = max(0.0, safe_padding)
    return (
        min_x - safe_padding,
        min_y - safe_padding,
        (max_x - min_x) + safe_padding * 2,
        (max_y - min_y) + safe_padding * 2,
    )


def _site_perimeter_svg(planta: PlantaBaixa) -> str:
    """Renderiza o muro externo do terreno com rupturas nos portões."""
    x, y, w, h = _site_bounds(planta)
    right = x + w
    bottom = y + h
    segments = {
        ("H", y): [[x, right]],
        ("H", bottom): [[x, right]],
        ("V", x): [[y, bottom]],
        ("V", right): [[y, bottom]],
    }
    gaps: dict[tuple[str, float], list[tuple[float, float]]] = {}
    for portao in planta.portoes:
        line_coord = portao.y if portao.orientacao == "H" else portao.x
        start = portao.x if portao.orientacao == "H" else portao.y
        end = start + portao.largura
        for key in segments:
            if key[0] == portao.orientacao and isclose(key[1], line_coord, abs_tol=EPSILON):
                gaps.setdefault(key, []).append((start, end))

    parts = [f'<rect class="site-fill" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>']
    for (orientacao, coord), intervalos in segments.items():
        for inicio, fim in intervalos:
            for part_start, part_end in _cut_segment(inicio, fim, gaps.get((orientacao, coord), [])):
                if orientacao == "H":
                    parts.append(f'<line x1="{part_start:g}" y1="{coord:g}" x2="{part_end:g}" y2="{coord:g}"/>')
                else:
                    parts.append(f'<line x1="{coord:g}" y1="{part_start:g}" x2="{coord:g}" y2="{part_end:g}"/>')
    return '<g class="site-perimeter">' + ''.join(parts) + '</g>'

def _building_bounds(planta: PlantaBaixa, padding: float = 20) -> tuple[float, float, float, float]:
    """Calcula a massa externa da edificação a partir das áreas da planta."""
    if not planta.areas:
        return 0, 0, planta.largura, planta.altura

    min_x = min(area.x for area in planta.areas)
    min_y = min(area.y for area in planta.areas)
    max_x = max(area.x + area.w for area in planta.areas)
    max_y = max(area.y + area.h for area in planta.areas)
    safe_padding = min(padding, min_x, min_y, planta.largura - max_x, planta.altura - max_y)
    safe_padding = max(0.0, safe_padding)
    return (
        min_x - safe_padding,
        min_y - safe_padding,
        (max_x - min_x) + safe_padding * 2,
        (max_y - min_y) + safe_padding * 2,
    )


def _interval_overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def _areas_adjacentes(a: AreaPlanta, b: AreaPlanta) -> bool:
    vertical = (isclose(a.x + a.w, b.x, abs_tol=EPSILON) or isclose(b.x + b.w, a.x, abs_tol=EPSILON)) and _interval_overlap(a.y, a.y + a.h, b.y, b.y + b.h) > 0
    horizontal = (isclose(a.y + a.h, b.y, abs_tol=EPSILON) or isclose(b.y + b.h, a.y, abs_tol=EPSILON)) and _interval_overlap(a.x, a.x + a.w, b.x, b.x + b.w) > 0
    return vertical or horizontal


def validar_planta(planta: PlantaBaixa) -> list[str]:
    """Retorna mensagens de validação geométrica simples para a planta v2."""
    erros: list[str] = []
    ids = _area_ids(planta)
    areas = _area_by_id(planta)
    for area in planta.areas:
        if not _inside(area, planta):
            erros.append(f"Área '{area.id}' fora do footprint.")
    for porta in planta.portas:
        if porta.orientacao not in ORIENTACOES:
            erros.append(f"Porta '{porta.id}' com orientação inválida.")
        refs = [item for item in porta.entre if item != EXTERIOR]
        if any(ref not in ids for ref in refs):
            erros.append(f"Porta '{porta.id}' referencia área inexistente.")
            continue
        if len(refs) == 2 and not _areas_adjacentes(areas[refs[0]], areas[refs[1]]):
            erros.append(f"Porta '{porta.id}' não está entre áreas adjacentes.")
        if not _porta_sobre_parede(planta, porta):
            erros.append(f"Porta '{porta.id}' fora de uma parede plausível.")
    for janela in planta.janelas:
        if janela.area not in ids:
            erros.append(f"Janela '{janela.id}' referencia área inexistente.")
        elif janela.orientacao not in ORIENTACOES or not _abertura_sobre_area(areas[janela.area], janela.orientacao, janela.x, janela.y, janela.largura):
            erros.append(f"Janela '{janela.id}' fora de uma parede plausível.")
    for camera in planta.cameras:
        if camera.area not in ids:
            erros.append(f"Câmera '{camera.id}' referencia área inexistente.")
        elif not _ponto_em_borda(areas[camera.area], camera.x, camera.y):
            erros.append(f"Câmera '{camera.id}' não está presa a parede/canto.")
    if planta.id == "casa_acervo_mirante_v2":
        corredor = areas.get("corredor_tecnico")
        if corredor is None:
            erros.append("Planta do Mirante sem corredor técnico contínuo.")
        else:
            soltas = [area.id for area in planta.areas if area.id != corredor.id and not _areas_adjacentes(area, corredor)]
            permitidas = {"galeria_vitrine"}  # Também adjacente à reserva e com porta direta ao corredor.
            if any(area_id not in permitidas for area_id in soltas):
                erros.append("Planta do Mirante contém áreas soltas sem relação de circulação.")
    return erros


def _abertura_sobre_area(area: AreaPlanta, orientacao: str, x: float, y: float, largura: float) -> bool:
    if largura <= 0:
        return False
    if orientacao == "H":
        return (isclose(y, area.y, abs_tol=EPSILON) or isclose(y, area.y + area.h, abs_tol=EPSILON)) and x >= area.x - EPSILON and x + largura <= area.x + area.w + EPSILON
    if orientacao == "V":
        return (isclose(x, area.x, abs_tol=EPSILON) or isclose(x, area.x + area.w, abs_tol=EPSILON)) and y >= area.y - EPSILON and y + largura <= area.y + area.h + EPSILON
    return False


def _porta_sobre_parede(planta: PlantaBaixa, porta: PortaPlanta) -> bool:
    areas = _area_by_id(planta)
    refs = [areas[item] for item in porta.entre if item in areas]
    return any(_abertura_sobre_area(area, porta.orientacao, porta.x, porta.y, porta.largura) for area in refs)


def _ponto_em_borda(area: AreaPlanta, x: float, y: float) -> bool:
    em_vertical = (isclose(x, area.x, abs_tol=EPSILON) or isclose(x, area.x + area.w, abs_tol=EPSILON)) and area.y - EPSILON <= y <= area.y + area.h + EPSILON
    em_horizontal = (isclose(y, area.y, abs_tol=EPSILON) or isclose(y, area.y + area.h, abs_tol=EPSILON)) and area.x - EPSILON <= x <= area.x + area.w + EPSILON
    return em_vertical or em_horizontal


def _wall_segments(planta: PlantaBaixa) -> list[SegmentoParede]:
    raw: list[tuple[str, float, float, float]] = []
    for area in planta.areas:
        raw.extend((
            ("H", area.y, area.x, area.x + area.w),
            ("H", area.y + area.h, area.x, area.x + area.w),
            ("V", area.x, area.y, area.y + area.h),
            ("V", area.x + area.w, area.y, area.y + area.h),
        ))

    grouped: dict[tuple[str, float], list[tuple[float, float]]] = {}
    for orientacao, coord, inicio, fim in raw:
        grouped.setdefault((orientacao, coord), []).append((inicio, fim))

    segmentos: list[SegmentoParede] = []
    for (orientacao, coord), intervals in grouped.items():
        cortes = sorted({value for interval in intervals for value in interval})
        for inicio, fim in zip(cortes, cortes[1:]):
            if fim - inicio <= 0.5:
                continue
            cobertura = sum(1 for a, b in intervals if a <= inicio + EPSILON and b >= fim - EPSILON)
            if cobertura:
                segmentos.append(SegmentoParede(orientacao, coord, inicio, fim, cobertura == 1))
    return segmentos


def _gaps_for_segment(segment: SegmentoParede, planta: PlantaBaixa) -> list[tuple[float, float]]:
    gaps: list[tuple[float, float]] = []
    for porta in planta.portas:
        if porta.orientacao != segment.orientacao:
            continue
        if not isclose(porta.y if porta.orientacao == "H" else porta.x, segment.coord, abs_tol=EPSILON):
            continue
        inicio = porta.x if porta.orientacao == "H" else porta.y
        fim = inicio + porta.largura
        if inicio >= segment.inicio - EPSILON and fim <= segment.fim + EPSILON:
            gaps.append((inicio, fim))
    for janela in planta.janelas:
        if janela.orientacao != segment.orientacao:
            continue
        if not isclose(janela.y if janela.orientacao == "H" else janela.x, segment.coord, abs_tol=EPSILON):
            continue
        inicio = janela.x if janela.orientacao == "H" else janela.y
        fim = inicio + janela.largura
        if inicio >= segment.inicio - EPSILON and fim <= segment.fim + EPSILON:
            gaps.append((inicio, fim))
    return gaps


def _cut_segment(inicio: float, fim: float, gaps: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cursor = inicio
    parts: list[tuple[float, float]] = []
    for gap_start, gap_end in sorted(gaps):
        gap_start = max(inicio, min(fim, gap_start))
        gap_end = max(inicio, min(fim, gap_end))
        if gap_start > cursor:
            parts.append((cursor, gap_start))
        cursor = max(cursor, gap_end)
    if cursor < fim:
        parts.append((cursor, fim))
    return [(a, b) for a, b in parts if b - a > 0.5]


def _line(segment: SegmentoParede, inicio: float, fim: float) -> str:
    if segment.orientacao == "H":
        return f'<line x1="{inicio:g}" y1="{segment.coord:g}" x2="{fim:g}" y2="{segment.coord:g}" />'
    return f'<line x1="{segment.coord:g}" y1="{inicio:g}" x2="{segment.coord:g}" y2="{fim:g}" />'


def _porta_svg(porta: PortaPlanta) -> str:
    label = escape(porta.id)
    if porta.orientacao == "H":
        x1, x2, y = porta.x, porta.x + porta.largura, porta.y
        jamb = 7
        label_above = y > 260
        tx, ty = (x1 + x2) / 2, y - 7 if label_above else y + 16
        parts = [
            f'<line class="threshold" x1="{x1:g}" y1="{y:g}" x2="{x2:g}" y2="{y:g}"/>',
            f'<line x1="{x1:g}" y1="{y - jamb:g}" x2="{x1:g}" y2="{y + jamb:g}"/>',
            f'<line x1="{x2:g}" y1="{y - jamb:g}" x2="{x2:g}" y2="{y + jamb:g}"/>',
            f'<text x="{tx:g}" y="{ty:g}">{label}</text>',
        ]
        if porta.controle_acesso:
            icon_y = y - 17 if label_above else y + 25
            parts.append(_card_reader_svg((x1 + x2) / 2 + 18, icon_y))
    else:
        y1, y2, x = porta.y, porta.y + porta.largura, porta.x
        jamb = 7
        label_left = x >= 510
        tx, ty = x - 15 if label_left else x + 15, (y1 + y2) / 2
        parts = [
            f'<line class="threshold" x1="{x:g}" y1="{y1:g}" x2="{x:g}" y2="{y2:g}"/>',
            f'<line x1="{x - jamb:g}" y1="{y1:g}" x2="{x + jamb:g}" y2="{y1:g}"/>',
            f'<line x1="{x - jamb:g}" y1="{y2:g}" x2="{x + jamb:g}" y2="{y2:g}"/>',
            f'<text x="{tx:g}" y="{ty:g}">{label}</text>',
        ]
        if porta.controle_acesso:
            icon_x = x - 24 if label_left else x + 24
            parts.append(_card_reader_svg(icon_x, (y1 + y2) / 2 + 12))
    return '<g class="door">' + ''.join(parts) + '</g>'


def _card_reader_svg(x: float, y: float) -> str:
    return (
        f'<g class="card-reader" transform="translate({x:g} {y:g})">'
        '<rect x="-5" y="-3.5" width="10" height="7" rx="1"/>'
        '<line x1="-2.5" y1="-1" x2="2.5" y2="-1"/>'
        '<line x1="-2.5" y1="1.5" x2="1.5" y2="1.5"/></g>'
    )


def _janela_svg(janela: JanelaPlanta) -> str:
    if janela.orientacao == "H":
        x1, x2, y = janela.x, janela.x + janela.largura, janela.y
        return f'<g class="window"><line x1="{x1:g}" y1="{y - 5:g}" x2="{x2:g}" y2="{y - 5:g}"/><line x1="{x1:g}" y1="{y + 5:g}" x2="{x2:g}" y2="{y + 5:g}"/></g>'
    y1, y2, x = janela.y, janela.y + janela.largura, janela.x
    return f'<g class="window"><line x1="{x - 5:g}" y1="{y1:g}" x2="{x - 5:g}" y2="{y2:g}"/><line x1="{x + 5:g}" y1="{y1:g}" x2="{x + 5:g}" y2="{y2:g}"/></g>'


def _camera_svg(camera: CameraPlanta) -> str:
    return (
        f'<g class="camera" transform="translate({camera.x:g} {camera.y:g})">'
        '<rect x="-7" y="-4" width="14" height="8" rx="1"/><circle cx="0" cy="0" r="2"/>'
        f'<text x="0" y="22">{escape(camera.id)}</text></g>'
    )



def _area_externa_svg(area: AreaExternaPlanta) -> str:
    cx = area.x + area.w / 2
    cy = area.y + area.h / 2
    codigo = escape(area.codigo or area.id)
    nome = escape(area.nome)
    if area.tipo == "controle":
        return (
            f'<g class="external-control"><rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" rx="2"/>'
            f'<text class="external-code" x="{cx:g}" y="{cy - 5:g}">{codigo}</text>'
            f'<text class="external-name" x="{cx:g}" y="{cy + 10:g}">{nome}</text></g>'
        )
    if area.tipo == "publico":
        return (
            f'<g class="external-public"><rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" rx="2"/>'
            f'<line x1="{area.x + 18:g}" y1="{cy:g}" x2="{area.x + area.w - 18:g}" y2="{cy:g}"/>'
            f'<text class="external-code" x="{cx:g}" y="{area.y + 16:g}">{codigo}</text>'
            f'<text class="external-name" x="{cx:g}" y="{area.y + 31:g}">{nome}</text></g>'
        )
    return (
        f'<g class="external-yard"><rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}"/>'
        f'<path d="M{area.x + 34:g},{area.y + 14:g} h106 v38 h-106 z"/>'
        f'<line x1="{area.x + 46:g}" y1="{area.y + 52:g}" x2="{area.x + 46:g}" y2="{area.y + 60:g}"/>'
        f'<line x1="{area.x + 122:g}" y1="{area.y + 52:g}" x2="{area.x + 122:g}" y2="{area.y + 60:g}"/>'
        f'<text class="external-code" x="{cx:g}" y="{area.y + 24:g}">{codigo}</text>'
        f'<text class="external-name" x="{cx:g}" y="{area.y + 40:g}">{nome}</text></g>'
    )


def _portao_svg(portao: PortaoPlanta) -> str:
    label = escape(portao.id)
    if portao.orientacao == "H":
        x1, x2, y = portao.x, portao.x + portao.largura, portao.y
        mid = (x1 + x2) / 2
        return (
            f'<g class="gate"><line x1="{x1:g}" y1="{y:g}" x2="{mid - 4:g}" y2="{y:g}"/>'
            f'<line x1="{mid + 4:g}" y1="{y:g}" x2="{x2:g}" y2="{y:g}"/>'
            f'<line x1="{x1:g}" y1="{y - 10:g}" x2="{x1:g}" y2="{y + 10:g}"/>'
            f'<line x1="{x2:g}" y1="{y - 10:g}" x2="{x2:g}" y2="{y + 10:g}"/>'
            f'<path d="M{x1:g},{y:g} L{mid - 4:g},{y - 12:g} M{x2:g},{y:g} L{mid + 4:g},{y - 12:g}"/>'
            f'<text x="{mid:g}" y="{y + 20:g}">{label}</text></g>'
        )
    y1, y2, x = portao.y, portao.y + portao.largura, portao.x
    mid = (y1 + y2) / 2
    return (
        f'<g class="gate"><line x1="{x:g}" y1="{y1:g}" x2="{x:g}" y2="{mid - 4:g}"/>'
        f'<line x1="{x:g}" y1="{mid + 4:g}" x2="{x:g}" y2="{y2:g}"/>'
        f'<line x1="{x - 10:g}" y1="{y1:g}" x2="{x + 10:g}" y2="{y1:g}"/>'
        f'<line x1="{x - 10:g}" y1="{y2:g}" x2="{x + 10:g}" y2="{y2:g}"/>'
        f'<path d="M{x:g},{y1:g} L{x - 12:g},{mid - 4:g} M{x:g},{y2:g} L{x - 12:g},{mid + 4:g}"/>'
        f'<text x="{x + 20:g}" y="{mid:g}">{label}</text></g>'
    )


def render_floor_plan_svg(planta: PlantaBaixa, versao: str = "jogador") -> str:
    """Renderiza uma planta baixa v2 em SVG inline.

    A versão de jogador é neutra: sem rotas, setas, campos de visão ou destaques
    investigativos. O parâmetro ``versao`` fica reservado para futuras camadas.
    """
    if versao != "jogador":
        versao = "jogador"
    style = (
        'text{font-family:Arial,Helvetica,sans-serif}.room-code{font-family:"Courier New",monospace;font-size:12px;font-weight:700;fill:#111;text-anchor:middle}.room-name{font-size:9px;fill:#333;text-anchor:middle}.outer line{stroke:#111;stroke-width:7;stroke-linecap:square}.inner line{stroke:#222;stroke-width:3.2;stroke-linecap:square}.door line{stroke:#333;stroke-width:1.35;stroke-linecap:square}.door .threshold{stroke:#777;stroke-width:1;stroke-opacity:.55}.door text{font-family:"Courier New",monospace;font-size:8px;fill:#111;text-anchor:middle}.card-reader rect{fill:#fff;stroke:#111;stroke-width:1}.card-reader line{stroke:#111;stroke-width:.75}.window line{stroke:#111;stroke-width:1.4}.camera rect{fill:#fff;stroke:#111;stroke-width:1.3}.camera circle{fill:#111}.camera text{font-family:"Courier New",monospace;font-size:8px;fill:#111;text-anchor:middle}.site-perimeter .site-fill{fill:none;stroke:none}.site-perimeter line{stroke:#111;stroke-width:2.4;stroke-linecap:square}.external-yard rect{fill:#f8f8f8;stroke:#555;stroke-width:1.2;stroke-opacity:.8}.external-yard path{fill:none;stroke:#777;stroke-width:1.2;stroke-opacity:.55}.external-yard line{stroke:#777;stroke-width:1}.external-public rect{fill:#fff;stroke:#666;stroke-width:1.1;stroke-opacity:.75}.external-public line{stroke:#777;stroke-width:1}.external-control rect{fill:#fff;stroke:#111;stroke-width:1.5}.external-code{font-family:"Courier New",monospace;font-size:10px;font-weight:700;fill:#111;text-anchor:middle}.external-name{font-size:8.5px;fill:#333;text-anchor:middle}.gate line,.gate path{fill:none;stroke:#111;stroke-width:1.7;stroke-linecap:square}.gate text{font-family:"Courier New",monospace;font-size:8px;fill:#111;text-anchor:middle}.stamp{font-size:9px;fill:#444}.hatch{stroke:#ddd;stroke-width:1}'
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {planta.largura:g} {planta.altura:g}" role="img" aria-label="{escape(planta.titulo)}">',
        f'<defs><style>{style}</style><pattern id="wall-hatch" width="8" height="8" patternUnits="userSpaceOnUse"><path class="hatch" d="M0 8 L8 0"/></pattern></defs>',
        '<rect x="0" y="0" width="100%" height="100%" fill="#fff"/>',
    ]
    bx, by, bw, bh = _building_bounds(planta)
    parts.append(_site_perimeter_svg(planta))
    parts.extend(_area_externa_svg(area) for area in planta.areas_externas)
    parts.extend(_portao_svg(portao) for portao in planta.portoes)
    parts.append(f'<rect x="{bx:g}" y="{by:g}" width="{bw:g}" height="{bh:g}" fill="url(#wall-hatch)" opacity="0.28"/>')
    for area in planta.areas:
        parts.append(f'<rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" fill="#fff" stroke="none"/>')
    for external in (True, False):
        parts.append(f'<g class="{"outer" if external else "inner"}">')
        for segment in _wall_segments(planta):
            if segment.externa != external:
                continue
            for inicio, fim in _cut_segment(segment.inicio, segment.fim, _gaps_for_segment(segment, planta)):
                parts.append(_line(segment, inicio, fim))
        parts.append('</g>')
    parts.extend(_janela_svg(janela) for janela in planta.janelas)
    parts.extend(_porta_svg(porta) for porta in planta.portas)
    parts.extend(_camera_svg(camera) for camera in planta.cameras)
    for area in planta.areas:
        cx = area.x + area.w / 2
        cy = area.y + area.h / 2
        parts.append(f'<text class="room-code" x="{cx:g}" y="{cy - 6:g}">{escape(area.codigo or area.id)}</text>')
        parts.append(f'<text class="room-name" x="{cx:g}" y="{cy + 10:g}">{escape(area.nome)}</text>')
    parts.append('<g transform="translate(42 548)"><path d="M0 26 L8 0 L16 26 Z" fill="#111"/><text x="8" y="40" class="stamp" text-anchor="middle">N</text></g>')
    parts.append('<g transform="translate(760 564)"><line x1="0" y1="0" x2="120" y2="0" stroke="#111" stroke-width="2"/><line x1="0" y1="-4" x2="0" y2="4" stroke="#111"/><line x1="60" y1="-3" x2="60" y2="3" stroke="#111"/><line x1="120" y1="-4" x2="120" y2="4" stroke="#111"/><text x="60" y="16" class="stamp" text-anchor="middle">escala esquemática</text></g>')
    parts.append('</svg>')
    svg = ''.join(parts)
    if versao == "jogador" and any(termo in svg.lower() for termo in TERMOS_PROIBIDOS_JOGADOR):
        raise ValueError("SVG de jogador contém termo proibido para mapa.")
    return svg

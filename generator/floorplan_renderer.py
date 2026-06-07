"""Renderizador P2 de plantas baixas procedurais em SVG P&B."""

from __future__ import annotations

from html import escape
from typing import NamedTuple

from .models import AreaMapa, CameraMapa, JanelaMapa, MapaProcedural, PortaMapa

WALLS = {"norte", "sul", "leste", "oeste"}
OPPOSITE_WALL = {"norte": "sul", "sul": "norte", "leste": "oeste", "oeste": "leste"}
EPSILON = 0.01


class Segment(NamedTuple):
    start: float
    end: float


def _short(text: str, limit: int = 24) -> str:
    value = " ".join(str(text).split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _area_by_id(mapa: MapaProcedural) -> dict[str, AreaMapa]:
    return {area.id: area for area in mapa.areas if area.id}


def _wall_length(area: AreaMapa, parede: str) -> float:
    return area.w if parede in {"norte", "sul"} else area.h


def _wall_coordinate(area: AreaMapa, parede: str) -> float:
    if parede == "norte":
        return area.y
    if parede == "sul":
        return area.y + area.h
    if parede == "oeste":
        return area.x
    return area.x + area.w


def _wall_axis_start(area: AreaMapa, parede: str) -> float:
    return area.x if parede in {"norte", "sul"} else area.y


def _mirrored_door_gap(area_a: AreaMapa, area_b: AreaMapa, porta: PortaMapa) -> tuple[str, float, float] | None:
    """Retorna o gap equivalente na parede oposta de area_b quando há adjacência real."""
    opposite = OPPOSITE_WALL.get(porta.parede)
    if opposite is None:
        return None
    if abs(_wall_coordinate(area_a, porta.parede) - _wall_coordinate(area_b, opposite)) > EPSILON:
        return None

    door_start = _wall_axis_start(area_a, porta.parede) + porta.posicao
    door_end = door_start + porta.largura
    b_start = _wall_axis_start(area_b, opposite)
    b_end = b_start + _wall_length(area_b, opposite)
    if door_start < b_start - EPSILON or door_end > b_end + EPSILON:
        return None
    return opposite, max(0.0, door_start - b_start), porta.largura


def _gap_segments(length: float, gaps: list[tuple[float, float]]) -> list[Segment]:
    cursor = 0.0
    segments: list[Segment] = []
    for start, end in sorted(gaps):
        start = max(0.0, min(length, start))
        end = max(0.0, min(length, end))
        if start > cursor:
            segments.append(Segment(cursor, start))
        cursor = max(cursor, end)
    if cursor < length:
        segments.append(Segment(cursor, length))
    return [item for item in segments if item.end - item.start > 0.5]


def _line_for_wall(area: AreaMapa, parede: str, segment: Segment) -> str:
    if parede == "norte":
        return f'<line x1="{area.x + segment.start:g}" y1="{area.y:g}" x2="{area.x + segment.end:g}" y2="{area.y:g}" />'
    if parede == "sul":
        y = area.y + area.h
        return f'<line x1="{area.x + segment.start:g}" y1="{y:g}" x2="{area.x + segment.end:g}" y2="{y:g}" />'
    if parede == "oeste":
        return f'<line x1="{area.x:g}" y1="{area.y + segment.start:g}" x2="{area.x:g}" y2="{area.y + segment.end:g}" />'
    x = area.x + area.w
    return f'<line x1="{x:g}" y1="{area.y + segment.start:g}" x2="{x:g}" y2="{area.y + segment.end:g}" />'


def _point_on_wall(area: AreaMapa, parede: str, pos: float) -> tuple[float, float]:
    if parede == "norte":
        return area.x + pos, area.y
    if parede == "sul":
        return area.x + pos, area.y + area.h
    if parede == "oeste":
        return area.x, area.y + pos
    return area.x + area.w, area.y + pos


def _door_symbol(area: AreaMapa, porta: PortaMapa) -> str:
    length = max(1.0, porta.largura)
    start = porta.posicao
    end = porta.posicao + length
    x1, y1 = _point_on_wall(area, porta.parede, start)
    x2, y2 = _point_on_wall(area, porta.parede, end)
    r = length
    if porta.parede == "norte":
        d = f"M{x1:g},{y1:g} L{x1:g},{y1 + r:g} A{r:g},{r:g} 0 0 1 {x2:g},{y2:g}"
    elif porta.parede == "sul":
        d = f"M{x1:g},{y1:g} L{x1:g},{y1 - r:g} A{r:g},{r:g} 0 0 0 {x2:g},{y2:g}"
    elif porta.parede == "oeste":
        d = f"M{x1:g},{y1:g} L{x1 + r:g},{y1:g} A{r:g},{r:g} 0 0 0 {x2:g},{y2:g}"
    else:
        d = f"M{x1:g},{y1:g} L{x1 - r:g},{y1:g} A{r:g},{r:g} 0 0 1 {x2:g},{y2:g}"
    label = escape(porta.controle_acesso or porta.id)
    midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
    return f'<g class="door"><path d="{d}"/><text x="{midx:g}" y="{midy - 5:g}">{label}</text></g>'


def _window_symbol(area: AreaMapa, janela: JanelaMapa) -> str:
    start = janela.posicao
    end = janela.posicao + janela.largura
    x1, y1 = _point_on_wall(area, janela.parede, start)
    x2, y2 = _point_on_wall(area, janela.parede, end)
    if janela.parede in {"norte", "sul"}:
        return f'<g class="window"><line x1="{x1:g}" y1="{y1 - 4:g}" x2="{x2:g}" y2="{y2 - 4:g}"/><line x1="{x1:g}" y1="{y1 + 4:g}" x2="{x2:g}" y2="{y2 + 4:g}"/></g>'
    return f'<g class="window"><line x1="{x1 - 4:g}" y1="{y1:g}" x2="{x2 - 4:g}" y2="{y2:g}"/><line x1="{x1 + 4:g}" y1="{y1:g}" x2="{x2 + 4:g}" y2="{y2:g}"/></g>'


def _camera_symbol(area: AreaMapa, camera: CameraMapa) -> str:
    pos = camera.posicao if camera.posicao is not None else _wall_length(area, camera.parede) / 2
    x, y = _point_on_wall(area, camera.parede, pos)
    rotations = {"norte": 180, "sul": 0, "leste": 90, "oeste": -90}
    return (
        f'<g class="camera" transform="translate({x:g} {y:g}) rotate({rotations.get(camera.parede, 0)})">'
        '<rect x="-7" y="0" width="14" height="7"/><polygon points="-5,7 5,7 0,16"/>'
        f'<text x="0" y="29">{escape(camera.id)}</text></g>'
    )


def render_floorplan_svg(mapa: MapaProcedural) -> str:
    """Gera SVG inline de planta baixa profissional, neutra e P&B."""
    largura = max(mapa.largura, 1)
    altura = max(mapa.altura, 1)
    areas = _area_by_id(mapa)
    gaps: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for porta in mapa.portas:
        area_a = areas.get(porta.area_a)
        if area_a is not None and porta.parede in WALLS:
            gaps.setdefault((porta.area_a, porta.parede), []).append((porta.posicao, porta.posicao + porta.largura))
            area_b = areas.get(porta.area_b or "")
            if area_b is not None:
                mirrored_gap = _mirrored_door_gap(area_a, area_b, porta)
                if mirrored_gap is not None:
                    parede_b, posicao_b, largura_b = mirrored_gap
                    gaps.setdefault((area_b.id, parede_b), []).append((posicao_b, posicao_b + largura_b))
    for janela in mapa.janelas:
        if janela.area in areas and janela.parede in WALLS:
            gaps.setdefault((janela.area, janela.parede), []).append((janela.posicao, janela.posicao + janela.largura))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:g} {altura:g}" role="img" aria-label="{escape(mapa.titulo)}">',
        '<defs><style>text{font-family:Arial,Helvetica,sans-serif}.room-label{font-family:"Courier New",monospace;font-size:13px;font-weight:700;fill:#111;text-anchor:middle;dominant-baseline:middle}.room-name{font-size:10px;fill:#333;text-anchor:middle}.wall line{stroke:#111;stroke-width:5;stroke-linecap:square}.partition line{stroke:#222;stroke-width:3;stroke-linecap:square}.door path{fill:none;stroke:#333;stroke-width:1.6}.door text{font-family:"Courier New",monospace;font-size:8px;fill:#111;text-anchor:middle}.window line{stroke:#111;stroke-width:1.4}.camera rect,.camera polygon{fill:#111}.camera text{font-family:"Courier New",monospace;font-size:8px;fill:#111;text-anchor:middle}.stamp{font-size:9px;fill:#444}.north{stroke:#111;fill:#111}</style></defs>',
        '<rect x="0" y="0" width="100%" height="100%" fill="#fff"/>',
        f'<rect x="10" y="10" width="{max(largura - 20, 1):g}" height="{max(altura - 20, 1):g}" fill="none" stroke="#111" stroke-width="1"/>',
    ]
    for area in mapa.areas:
        parts.append(f'<rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" fill="#fff" stroke="none"/>')
    for area in mapa.areas:
        css = "wall" if area.tipo in {"externo", "area_externa"} else "partition"
        parts.append(f'<g class="{css}" id="walls-{escape(area.id)}">')
        for parede in ("norte", "sul", "leste", "oeste"):
            for segment in _gap_segments(_wall_length(area, parede), gaps.get((area.id, parede), [])):
                parts.append(_line_for_wall(area, parede, segment))
        parts.append('</g>')
    for porta in mapa.portas:
        area = areas.get(porta.area_a)
        if area:
            parts.append(_door_symbol(area, porta))
    for janela in mapa.janelas:
        area = areas.get(janela.area)
        if area:
            parts.append(_window_symbol(area, janela))
    for camera in mapa.cameras:
        area = areas.get(camera.area)
        if area and camera.parede in WALLS:
            parts.append(_camera_symbol(area, camera))
    use_codes = bool(mapa.legenda)
    for area in mapa.areas:
        cx = area.x + area.w / 2
        cy = area.y + area.h / 2
        code = area.observacao if use_codes and area.observacao.startswith("P-") else area.nome
        parts.append(f'<text class="room-label" x="{cx:g}" y="{cy:g}">{escape(_short(code, 22))}</text>')
        if not use_codes and area.observacao and area.observacao.startswith("P-"):
            parts.append(f'<text class="room-name" x="{cx:g}" y="{cy + 15:g}">{escape(area.observacao)}</text>')
    if mapa.legenda:
        x = largura - 230
        y = 36
        height = 24 + 15 * len(mapa.legenda)
        parts.append(f'<g class="legend"><rect x="{x:g}" y="{y:g}" width="200" height="{height:g}" fill="#fff" stroke="#111" stroke-width="1"/>')
        parts.append(f'<text x="{x + 10:g}" y="{y + 16:g}" class="stamp">Áreas</text>')
        for idx, item in enumerate(mapa.legenda):
            parts.append(f'<text x="{x + 10:g}" y="{y + 34 + idx * 15:g}" class="stamp">{escape(item.simbolo)} — {escape(_short(item.descricao, 28))}</text>')
        parts.append('</g>')
    parts.append(f'<g transform="translate(36 {altura - 54:g})"><path class="north" d="M0 24 L8 0 L16 24 Z"/><text x="8" y="38" class="stamp" text-anchor="middle">N</text></g>')
    parts.append(f'<text x="{largura - 260:g}" y="{altura - 26:g}" class="stamp">Planta operacional simplificada · P&B · A4 paisagem</text>')
    parts.append('</svg>')
    return ''.join(parts)

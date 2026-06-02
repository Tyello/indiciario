"""Renderização procedural controlada de mapas e cartões visuais."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from .models import Blueprint, LocalVisual, MapaProcedural, PersonagemVisual
from .renderer import renderizar_documento


def _safe_id(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return slug.strip("_") or "sem_id"


def _safe_color(value: str) -> str:
    text = value.strip()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", text):
        return text
    return "#4b5563"


def _short_label(value: str, limit: int = 28) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _personagem_nome(personagem: PersonagemVisual, blueprint: Blueprint) -> str:
    for item in blueprint.personagens:
        if item.id == personagem.personagem_id:
            return item.nome
    return personagem.personagem_id


def _build_mirante_floor_plan_svg(mapa: MapaProcedural) -> str:
    """Monta a planta dedicada do caso canônico Casa de Acervo Mirante."""
    marker_labels = [
        escape(_short_label(marcador.label, 24)) for marcador in mapa.marcadores
    ]
    while len(marker_labels) < 3:
        marker_labels.append("Marcador")
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="Planta logística térrea da Casa de Acervo Mirante">
  <desc>Áreas: Portaria principal; Vitrine / área pública; Corredor de carga; Doca lateral; Reserva técnica B; Administração.</desc>
  <defs>
    <style>
      .wall{fill:none;stroke:#111827;stroke-width:10;stroke-linecap:square;stroke-linejoin:miter}
      .thin-wall{fill:none;stroke:#111827;stroke-width:6;stroke-linecap:square;stroke-linejoin:miter}
      .room{fill:#f8fafc;stroke:#334155;stroke-width:1.5}
      .public{fill:#dcfce7}.access{fill:#dbeafe}.cargo{fill:#fef3c7}.reserve{fill:#ede9fe}.admin{fill:#fce7f3}.corridor{fill:#e0f2fe}
      .label{font-family:Arial,sans-serif;font-size:18px;font-weight:700;fill:#111827;text-anchor:middle}
      .small{font-family:Arial,sans-serif;font-size:12px;fill:#475569;text-anchor:middle}
      .door{fill:none;stroke:#b45309;stroke-width:5;stroke-linecap:round}
      .marker{fill:#111827;stroke:#ffffff;stroke-width:4}
      .marker-text{font-family:Arial,sans-serif;font-size:16px;font-weight:700;fill:#ffffff;text-anchor:middle}
      .legend{font-family:Arial,sans-serif;font-size:13px;fill:#111827}
      .legend-title{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#111827}
      .route{fill:none;stroke:#2563eb;stroke-width:4;stroke-dasharray:10 8;stroke-linecap:round;opacity:.75}
    </style>
  </defs>
  <rect x="0" y="0" width="960" height="540" fill="#f8fafc"/>
  <text x="42" y="38" font-family="Arial,sans-serif" font-size="19" font-weight="700" fill="#111827">Planta baixa operacional — térreo</text>
  <text x="42" y="60" font-family="Arial,sans-serif" font-size="12" fill="#475569">Rota logística entre portaria, doca e Reserva Técnica B</text>

  <rect x="54" y="82" width="720" height="390" class="room"/>
  <rect x="64" y="92" width="205" height="145" class="room public"/>
  <rect x="64" y="237" width="205" height="95" class="room access"/>
  <rect x="64" y="332" width="205" height="130" class="room cargo"/>
  <rect x="269" y="237" width="250" height="95" class="room corridor"/>
  <rect x="519" y="92" width="245" height="240" class="room reserve"/>
  <rect x="269" y="92" width="250" height="145" class="room admin"/>
  <rect x="269" y="332" width="250" height="130" class="room cargo" opacity=".62"/>

  <path d="M54 82 H774 V472 H54 Z" class="wall"/>
  <path d="M269 82 V472" class="thin-wall"/>
  <path d="M519 82 V332" class="thin-wall"/>
  <path d="M64 237 H519" class="thin-wall"/>
  <path d="M64 332 H519" class="thin-wall"/>

  <path d="M270 276 h-28" class="door"/>
  <path d="M520 276 h-34" class="door"/>
  <path d="M163 333 v-32" class="door"/>
  <path d="M774 206 q42 18 0 62" class="door"/>
  <path d="M54 382 q-34 22 0 52" class="door"/>

  <text x="166" y="160" class="label"><tspan x="166" dy="0">Vitrine /</tspan><tspan x="166" dy="22">área pública</tspan></text>
  <text x="166" y="282" class="label"><tspan x="166" dy="0">Portaria</tspan><tspan x="166" dy="22">principal</tspan></text>
  <text x="166" y="402" class="label"><tspan x="166" dy="0">Doca</tspan><tspan x="166" dy="22">lateral</tspan></text>
  <text x="394" y="282" class="label"><tspan x="394" dy="0">Corredor</tspan><tspan x="394" dy="22">de carga</tspan></text>
  <text x="641" y="202" class="label"><tspan x="641" dy="0">Reserva</tspan><tspan x="641" dy="22">técnica B</tspan></text>
  <text x="394" y="164" class="label">Administração</text>
  <text x="394" y="399" class="small"><tspan x="394" dy="0">área de preparo</tspan><tspan x="394" dy="17">sem pista nova</tspan></text>

  <path d="M166 382 H394 V284 H641" class="route"/>
  <circle cx="394" cy="284" r="17" class="marker"/><text x="394" y="290" class="marker-text">1</text>
  <circle cx="520" cy="284" r="17" class="marker"/><text x="520" y="290" class="marker-text">2</text>
  <circle cx="641" cy="262" r="17" class="marker"/><text x="641" y="268" class="marker-text">3</text>

  <g transform="translate(802 116)">
    <rect x="0" y="0" width="130" height="182" rx="10" fill="#ffffff" stroke="#94a3b8"/>
    <text x="14" y="28" class="legend-title">Legenda</text>
    <text x="14" y="58" class="legend">1. {label_1}</text>
    <text x="14" y="84" class="legend">2. {label_2}</text>
    <text x="14" y="110" class="legend">3. {label_3}</text>
    <line x1="14" y1="137" x2="56" y2="137" class="route"/>
    <text x="14" y="164" class="legend">rota provável</text>
  </g>
</svg>"""
    return (
        svg.replace("{label_1}", marker_labels[0])
        .replace("{label_2}", marker_labels[1])
        .replace("{label_3}", marker_labels[2])
    )


def build_map_svg(mapa: MapaProcedural) -> str:
    """Monta SVG local para uma planta esquemática simples de um andar."""
    if mapa.id == "casa_acervo_mirante_andar_1":
        return _build_mirante_floor_plan_svg(mapa)

    largura = max(mapa.largura, 1)
    altura = max(mapa.altura, 1)
    centers = {
        area.id: (area.x + area.w / 2, area.y + area.h / 2)
        for area in mapa.areas
        if area.id
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:g} {altura:g}" role="img" aria-label="{escape(mapa.titulo)}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc" stroke="#111827" stroke-width="2"/>',
        '<text x="28" y="36" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">Planta esquemática</text>',
    ]

    for conexao in mapa.conexoes:
        origem = centers.get(conexao.origem)
        destino = centers.get(conexao.destino)
        if not origem or not destino:
            continue
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#bfdbfe" stroke-width="18" stroke-linecap="round"/>'
        )
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#1d4ed8" stroke-width="3" stroke-linecap="round" stroke-dasharray="9 7"/>'
        )

    palette = {
        "controle_acesso": "#dbeafe",
        "circulacao": "#e0f2fe",
        "carga": "#fef3c7",
        "reserva": "#ede9fe",
        "exposicao": "#dcfce7",
        "administrativo": "#fce7f3",
    }
    for area in mapa.areas:
        fill = palette.get(area.tipo, "#ffffff") if area.acessivel else "#e5e7eb"
        stroke_dash = "" if area.acessivel else ' stroke-dasharray="8 5"'
        parts.append(
            f'<rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" rx="12" '
            f'fill="{fill}" stroke="#334155" stroke-width="2.5"{stroke_dash}/>'
        )
        label = escape(_short_label(area.nome, 20))
        text_x = area.x + area.w / 2
        text_y = area.y + area.h / 2 - (8 if area.observacao else 0)
        parts.append(
            f'<text x="{text_x:g}" y="{text_y:g}" text-anchor="middle" font-family="Arial, sans-serif" '
            f'font-size="16" font-weight="700" fill="#111827">{label}</text>'
        )
        if area.observacao:
            parts.append(
                f'<text x="{text_x:g}" y="{text_y + 22:g}" text-anchor="middle" font-family="Arial, sans-serif" '
                f'font-size="11" fill="#475569">{escape(_short_label(area.observacao, 24))}</text>'
            )

    marker_items: list[str] = []
    for index, marcador in enumerate(mapa.marcadores, start=1):
        label = escape(_short_label(marcador.label, 24))
        marker_items.append(f"{index}. {label}")
        parts.append(
            f'<circle cx="{marcador.x:g}" cy="{marcador.y:g}" r="15" fill="#111827"/>'
        )
        parts.append(
            f'<text x="{marcador.x:g}" y="{marcador.y + 5:g}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#ffffff">{index}</text>'
        )

    legend_items = marker_items or [
        f"{item.simbolo}: {_short_label(item.descricao, 28)}" for item in mapa.legenda
    ]
    if legend_items:
        legend_width = 300
        legend_height = 34 + 22 * len(legend_items)
        x = max(12, largura - legend_width - 24)
        y = 24
        parts.append(f'<g transform="translate({x:g} {y:g})">')
        parts.append(
            f'<rect x="0" y="0" width="{legend_width}" height="{legend_height}" rx="10" '
            'fill="#ffffff" fill-opacity="0.96" stroke="#94a3b8"/>'
        )
        parts.append(
            '<text x="16" y="22" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#111827">Marcadores</text>'
        )
        for index, item in enumerate(legend_items):
            line_y = 46 + index * 22
            parts.append(
                f'<text x="16" y="{line_y}" font-family="Arial, sans-serif" font-size="12" fill="#111827">'
                f"{escape(_short_label(item, 36))}</text>"
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "".join(parts)


def build_character_card_svg(personagem: PersonagemVisual, blueprint: Blueprint) -> str:
    """Monta SVG local para um cartão visual de personagem."""
    nome = escape(_personagem_nome(personagem, blueprint))
    cor = _safe_color(personagem.cor)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 560" role="img">',
        '<rect x="0" y="0" width="420" height="560" rx="18" fill="#ffffff" stroke="#111827" stroke-width="3"/>',
        f'<rect x="0" y="0" width="420" height="96" rx="18" fill="{cor}"/>',
        f'<text x="32" y="58" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#ffffff">{nome}</text>',
        f'<circle cx="210" cy="230" r="86" fill="{cor}" opacity="0.15" stroke="{cor}" stroke-width="4"/>',
        f'<text x="210" y="244" text-anchor="middle" font-family="Arial, sans-serif" font-size="64" fill="{cor}">{escape(personagem.icone)}</text>',
        f'<text x="210" y="344" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#374151">{escape(personagem.silhueta)}</text>',
    ]
    for index, detalhe in enumerate(personagem.detalhes[:6]):
        y = 392 + index * 26
        parts.append(
            f'<text x="44" y="{y}" font-family="Arial, sans-serif" font-size="15" fill="#111827">• {escape(detalhe)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def build_location_card_svg(local: LocalVisual) -> str:
    """Monta SVG local para um cartão/placa visual de local."""
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 300" role="img">',
        '<rect x="0" y="0" width="420" height="300" rx="16" fill="#ffffff" stroke="#111827" stroke-width="3"/>',
        '<rect x="0" y="0" width="420" height="72" rx="16" fill="#1f2937"/>',
        f'<text x="28" y="46" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#ffffff">{escape(local.nome)}</text>',
        f'<text x="34" y="136" font-family="Arial, sans-serif" font-size="52" fill="#111827">{escape(local.icone)}</text>',
        f'<text x="104" y="118" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">{escape(local.tipo)}</text>',
        f'<foreignObject x="104" y="132" width="280" height="100"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'style="font-family:Arial,sans-serif;font-size:14px;color:#374151;line-height:1.35">{escape(local.descricao)}</div></foreignObject>',
    ]
    if local.documentos_relacionados:
        docs = ", ".join(local.documentos_relacionados)
        parts.append(
            f'<text x="28" y="260" font-family="Arial, sans-serif" font-size="13" fill="#111827">Documentos: {escape(docs)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def visual_document_code(kind: str, identifier: str) -> str:
    prefixes = {"map": "VP-MAPA", "character": "VP-PERSONAGEM", "location": "VP-LOCAL"}
    return f"{prefixes[kind]}-{identifier}"


def visual_document_path(kind: str, identifier: str, output_dir: Path) -> Path:
    names = {
        "map": "visual_map",
        "character": "visual_personagem",
        "location": "visual_local",
    }
    return output_dir / f"{names[kind]}_{_safe_id(identifier)}.pdf"


def build_visual_documents(
    blueprint: Blueprint,
    output_dir: Path,
    strict: bool = True,
    html_debug_dir: Path | None = None,
) -> dict[str, list[Path]]:
    """Renderiza PDFs visuais e agrupa por envelope/fase para o pacote final."""
    visual = blueprint.visual_procedural
    grupos: dict[str, list[Path]] = {}
    if visual is None:
        return grupos

    output_dir.mkdir(parents=True, exist_ok=True)
    for mapa in visual.mapas:
        svg = build_map_svg(mapa)
        output_path = visual_document_path("map", mapa.id, output_dir)
        dados = {
            "TITULO": mapa.titulo,
            "SUBTITULO": f"Mapa procedural — {mapa.fase}",
            "SVG": svg,
        }
        render_kwargs = {"strict": strict, "landscape": True}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_map.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault(mapa.fase or "E1", []).append(caminho)

    for personagem in visual.personagens:
        svg = build_character_card_svg(personagem, blueprint)
        output_path = visual_document_path(
            "character", personagem.personagem_id, output_dir
        )
        nome = _personagem_nome(personagem, blueprint)
        dados = {"TITULO": f"Cartão de personagem — {nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_character_card.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault("E1", []).append(caminho)

    for local in visual.locais:
        svg = build_location_card_svg(local)
        output_path = visual_document_path("location", local.id, output_dir)
        dados = {"TITULO": f"Cartão de local — {local.nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_location_card.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault("E1", []).append(caminho)

    return grupos

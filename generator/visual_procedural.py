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
        escape(_short_label(marcador.label, 28)) for marcador in mapa.marcadores
    ]
    while len(marker_labels) < 3:
        marker_labels.append("Marcador")
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="Planta operacional térrea da Casa de Acervo Mirante">
  <desc>Áreas: Portaria principal; Vitrine / área pública; Corredor de carga; Doca lateral; Reserva técnica B; Administração. Marcadores 1, 2 e 3 indicam pontos de leitura investigativa.</desc>
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M20 0H0V20" fill="none" stroke="#e5e7eb" stroke-width="1"/>
    </pattern>
    <style>
      .outer{fill:#f8fafc;stroke:#111827;stroke-width:12;stroke-linejoin:miter}
      .wall{stroke:#111827;stroke-width:8;stroke-linecap:square;stroke-linejoin:miter}
      .partition{stroke:#111827;stroke-width:5;stroke-linecap:square;stroke-linejoin:miter}
      .room{stroke:#334155;stroke-width:1.4}
      .public{fill:#e8f7ec}.access{fill:#eaf2ff}.cargo{fill:#fff4d6}.reserve{fill:#eeeafd}.admin{fill:#fdebf5}.service{fill:#eef6fb}
      .label{font-family:Arial,sans-serif;font-size:17px;font-weight:700;fill:#111827;text-anchor:middle}
      .small{font-family:Arial,sans-serif;font-size:11.5px;fill:#475569;text-anchor:middle}
      .micro{font-family:Arial,sans-serif;font-size:10px;fill:#64748b}
      .door{fill:none;stroke:#92400e;stroke-width:4.5;stroke-linecap:round}
      .door-gap{stroke:#f8fafc;stroke-width:10;stroke-linecap:square}
      .route{fill:none;stroke:#1d4ed8;stroke-width:3;stroke-dasharray:8 8;stroke-linecap:round;opacity:.58}
      .route-soft{fill:none;stroke:#60a5fa;stroke-width:13;stroke-linecap:round;opacity:.18}
      .marker{fill:#111827;stroke:#ffffff;stroke-width:4}
      .marker-text{font-family:Arial,sans-serif;font-size:16px;font-weight:700;fill:#ffffff;text-anchor:middle}
      .legend{font-family:Arial,sans-serif;font-size:12.5px;fill:#111827}
      .legend-title{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#111827}
      .stamp{font-family:Arial,sans-serif;font-size:10px;fill:#111827;text-transform:uppercase;letter-spacing:.05em}
    </style>
  </defs>
  <rect x="0" y="0" width="960" height="540" fill="#ffffff"/>
  <rect x="18" y="18" width="924" height="504" fill="url(#grid)" stroke="#cbd5e1"/>

  <text x="42" y="42" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#111827">Planta operacional — térreo</text>
  <text x="42" y="63" font-family="Arial,sans-serif" font-size="11.5" fill="#475569">Casa de Acervo Mirante · planta operacional simplificada para leitura de rota logística</text>

  <rect x="46" y="82" width="732" height="388" class="outer"/>
  <rect x="58" y="94" width="218" height="150" class="room public"/>
  <rect x="58" y="244" width="218" height="92" class="room access"/>
  <rect x="58" y="336" width="218" height="122" class="room cargo"/>
  <rect x="276" y="94" width="248" height="150" class="room admin"/>
  <rect x="276" y="244" width="248" height="92" class="room service"/>
  <rect x="276" y="336" width="248" height="122" class="room cargo" opacity=".62"/>
  <rect x="524" y="94" width="254" height="242" class="room reserve"/>
  <rect x="524" y="336" width="254" height="122" fill="#f8fafc" stroke="#334155" stroke-width="1.4" stroke-dasharray="7 5"/>

  <line x1="276" y1="82" x2="276" y2="470" class="wall"/>
  <line x1="524" y1="82" x2="524" y2="470" class="wall"/>
  <line x1="58" y1="244" x2="524" y2="244" class="partition"/>
  <line x1="58" y1="336" x2="778" y2="336" class="partition"/>

  <line x1="276" y1="278" x2="276" y2="314" class="door-gap"/>
  <path d="M276 278 q34 0 34 34" class="door"/>
  <line x1="524" y1="274" x2="524" y2="314" class="door-gap"/>
  <path d="M524 274 q-40 0 -40 40" class="door"/>
  <line x1="166" y1="336" x2="206" y2="336" class="door-gap"/>
  <path d="M166 336 q0 -36 36 -36" class="door"/>
  <line x1="778" y1="184" x2="778" y2="258" class="door-gap"/>
  <path d="M778 184 q48 18 0 74" class="door"/>
  <line x1="46" y1="382" x2="46" y2="432" class="door-gap"/>
  <path d="M46 382 q-38 18 0 50" class="door"/>

  <text x="167" y="164" class="label"><tspan x="167" dy="0">Vitrine /</tspan><tspan x="167" dy="21">área pública</tspan></text>
  <text x="167" y="283" class="label"><tspan x="167" dy="0">Portaria</tspan><tspan x="167" dy="21">principal</tspan></text>
  <text x="167" y="404" class="label"><tspan x="167" dy="0">Doca</tspan><tspan x="167" dy="21">lateral</tspan></text>
  <text x="400" y="283" class="label"><tspan x="400" dy="0">Corredor</tspan><tspan x="400" dy="21">de carga</tspan></text>
  <text x="647" y="198" class="label"><tspan x="647" dy="0">Reserva</tspan><tspan x="647" dy="21">técnica B</tspan></text>
  <text x="400" y="166" class="label">Administração</text>
  <text x="400" y="399" class="small"><tspan x="400" dy="0">área de preparo</tspan><tspan x="400" dy="16">sem pista nova</tspan></text>
  <text x="647" y="397" class="small"><tspan x="647" dy="0">parede cega /</tspan><tspan x="647" dy="16">armazenagem</tspan></text>

  <path d="M168 390 C235 390 246 292 305 292 H400 V292 H647" class="route-soft"/>
  <path d="M168 390 C235 390 246 292 305 292 H400 V292 H647" class="route"/>
  <circle cx="400" cy="292" r="17" class="marker"/><text x="400" y="298" class="marker-text">1</text>
  <circle cx="524" cy="292" r="17" class="marker"/><text x="524" y="298" class="marker-text">2</text>
  <circle cx="647" cy="258" r="17" class="marker"/><text x="647" y="264" class="marker-text">3</text>

  <g transform="translate(806 92)">
    <rect x="0" y="0" width="142" height="196" rx="9" fill="#ffffff" stroke="#94a3b8"/>
    <text x="14" y="27" class="legend-title">Legenda</text>
    <circle cx="20" cy="55" r="9" class="marker"/><text x="20" y="59" class="marker-text" font-size="10">1</text>
    <text x="34" y="59" class="legend">{label_1}</text>
    <circle cx="20" cy="83" r="9" class="marker"/><text x="20" y="87" class="marker-text" font-size="10">2</text>
    <text x="34" y="87" class="legend">{label_2}</text>
    <circle cx="20" cy="111" r="9" class="marker"/><text x="20" y="115" class="marker-text" font-size="10">3</text>
    <text x="34" y="115" class="legend">{label_3}</text>
    <line x1="14" y1="143" x2="64" y2="143" class="route"/>
    <text x="14" y="166" class="legend">rota provável</text>
    <text x="14" y="184" class="micro">linhas não representam medidas reais</text>
  </g>

  <g transform="translate(806 330)">
    <rect x="0" y="0" width="142" height="84" fill="#ffffff" stroke="#64748b"/>
    <text x="10" y="19" class="stamp">Carimbo técnico</text>
    <line x1="10" y1="30" x2="132" y2="30" stroke="#94a3b8"/>
    <text x="10" y="48" class="micro">Uso: facilitador / E1</text>
    <text x="10" y="64" class="micro">Revisão: playtest 01</text>
  </g>

  <g transform="translate(806 444)">
    <text x="0" y="0" class="micro">Escala visual aproximada</text>
    <line x1="0" y1="18" x2="108" y2="18" stroke="#111827" stroke-width="3"/>
    <line x1="0" y1="12" x2="0" y2="24" stroke="#111827" stroke-width="3"/>
    <line x1="54" y1="12" x2="54" y2="24" stroke="#111827" stroke-width="3"/>
    <line x1="108" y1="12" x2="108" y2="24" stroke="#111827" stroke-width="3"/>
    <text x="0" y="38" class="micro">0</text><text x="47" y="38" class="micro">5m</text><text x="94" y="38" class="micro">10m</text>
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
            "SUBTITULO": f"Planta operacional simplificada — {mapa.fase}",
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

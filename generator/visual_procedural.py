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
    del mapa
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="Planta baixa técnica térrea da Casa de Acervo Mirante">
  <desc>Planta baixa em tons de cinza com guarita, pátio, administração, sala de segurança, doca, depósito, reservas técnicas A e B, vitrine, paredes, janelas e portas P-01 a P-09. Não há marcação de rota ou sequência de solução.</desc>
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#eeeeee" stroke-width="1"/></pattern>
    <style>
      .outer{fill:#fbfbfb;stroke:#111;stroke-width:8;stroke-linejoin:miter}.wall{stroke:#111;stroke-width:6;stroke-linecap:square}.partition{stroke:#111;stroke-width:4;stroke-linecap:square}.room{fill:#f7f7f7;stroke:#666;stroke-width:1.4}.service-room{fill:#f1f1f1;stroke:#555;stroke-width:1.4}.reserve-room{fill:#eeeeee;stroke:#444;stroke-width:1.4}.public-room{fill:#fafafa;stroke:#555;stroke-width:1.4}.external-room{fill:#f4f4f4;stroke:#777;stroke-width:1.2;stroke-dasharray:5 4}.label{font-family:Arial,sans-serif;font-size:15px;font-weight:700;fill:#111;text-anchor:middle}.small{font-family:Arial,sans-serif;font-size:10.5px;fill:#555;text-anchor:middle}.micro{font-family:Arial,sans-serif;font-size:10px;fill:#666}.door{fill:none;stroke:#111;stroke-width:2.5;stroke-linecap:round}.door-gap{stroke:#fbfbfb;stroke-width:10;stroke-linecap:square}.window{stroke:#111;stroke-width:2.2;stroke-linecap:square}.window-glass{stroke:#777;stroke-width:1}.legend{font-family:Arial,sans-serif;font-size:11.5px;fill:#111}.legend-title{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#111}.stamp{font-family:Arial,sans-serif;font-size:10px;fill:#111;text-transform:uppercase;letter-spacing:.05em}.door-label{font-family:Arial,sans-serif;font-size:10px;font-weight:700;fill:#111;text-anchor:middle}
    </style>
  </defs>
  <rect x="0" y="0" width="960" height="540" fill="#fff"/>
  <rect x="18" y="18" width="924" height="504" fill="url(#grid)" stroke="#d4d4d4"/>
  <text x="42" y="42" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#111">Planta baixa técnica — térreo</text>
  <text x="42" y="63" font-family="Arial,sans-serif" font-size="11.5" fill="#555">Casa de Acervo Mirante · setores e portas para cruzamento documental · escala gráfica aproximada</text>

  <rect x="44" y="86" width="730" height="398" class="outer"/>
  <rect x="58" y="104" width="138" height="92" class="room"/><text x="127" y="145" class="label">Guarita</text><text x="127" y="163" class="small">SETOR-01</text>
  <rect x="58" y="214" width="180" height="150" class="external-room"/><text x="148" y="283" class="label"><tspan x="148" dy="0">Área externa</tspan><tspan x="148" dy="18">/ pátio</tspan></text>
  <rect x="254" y="104" width="170" height="108" class="room"/><text x="339" y="151" class="label">Administração</text><text x="339" y="170" class="small">SETOR-03</text>
  <rect x="434" y="104" width="142" height="108" class="room"/><text x="505" y="145" class="label"><tspan x="505" dy="0">Sala de</tspan><tspan x="505" dy="18">Segurança</tspan></text><text x="505" y="184" class="small">SETOR-06</text>
  <rect x="254" y="230" width="322" height="86" class="service-room"/><text x="415" y="268" class="label">Corredor técnico</text><text x="415" y="286" class="small">SETOR-02</text>
  <rect x="254" y="338" width="160" height="108" class="service-room"/><text x="334" y="384" class="label"><tspan x="334" dy="0">Doca de</tspan><tspan x="334" dy="18">Serviço</tspan></text>
  <rect x="434" y="338" width="142" height="108" class="service-room"/><text x="505" y="384" class="label">Depósito</text><text x="505" y="402" class="small">SETOR-05</text>
  <rect x="608" y="104" width="154" height="116" class="reserve-room"/><text x="685" y="154" class="label"><tspan x="685" dy="0">Reserva</tspan><tspan x="685" dy="18">Técnica A</tspan></text>
  <rect x="608" y="246" width="154" height="116" class="reserve-room"/><text x="685" y="296" class="label"><tspan x="685" dy="0">Reserva</tspan><tspan x="685" dy="18">Técnica B</tspan></text>
  <rect x="608" y="386" width="154" height="58" class="public-room"/><text x="685" y="411" class="label">Vitrine</text><text x="685" y="428" class="small">área pública</text>

  <line x1="238" y1="86" x2="238" y2="484" class="wall"/><line x1="592" y1="86" x2="592" y2="484" class="wall"/>
  <line x1="424" y1="86" x2="424" y2="224" class="partition"/>
  <line x1="424" y1="330" x2="424" y2="484" class="partition"/>
  <line x1="238" y1="224" x2="592" y2="224" class="partition"/><line x1="238" y1="330" x2="592" y2="330" class="partition"/>
  <line x1="592" y1="232" x2="774" y2="232" class="partition"/><line x1="592" y1="374" x2="774" y2="374" class="partition"/>

  <line x1="126" y1="86" x2="164" y2="86" class="door-gap"/><path d="M126 86 q0 -28 34 -28" class="door"/><text x="145" y="82" class="door-label">P-01</text>
  <line x1="196" y1="150" x2="238" y2="150" class="door-gap"/><path d="M196 150 q34 0 34 34" class="door"/><text x="220" y="145" class="door-label">P-02</text>
  <line x1="330" y1="224" x2="372" y2="224" class="door-gap"/><path d="M330 224 q0 -30 38 -30" class="door"/><text x="351" y="220" class="door-label">P-03</text>
  <line x1="238" y1="382" x2="238" y2="430" class="door-gap"/><path d="M238 382 q-34 12 0 48" class="door"/><text x="224" y="408" class="door-label">P-04</text>
  <line x1="424" y1="386" x2="424" y2="426" class="door-gap"/><path d="M424 386 q-30 0 -30 36" class="door"/><text x="408" y="408" class="door-label">P-05</text>
  <line x1="592" y1="276" x2="592" y2="316" class="door-gap"/><path d="M592 276 q-36 0 -36 36" class="door"/><text x="580" y="299" class="door-label">P-06</text>
  <line x1="592" y1="134" x2="592" y2="174" class="door-gap"/><path d="M592 134 q-36 0 -36 36" class="door"/><text x="580" y="157" class="door-label">P-07</text>
  <line x1="486" y1="224" x2="526" y2="224" class="door-gap"/><path d="M486 224 q0 -30 36 -30" class="door"/><text x="506" y="220" class="door-label">P-08</text>
  <line x1="674" y1="374" x2="716" y2="374" class="door-gap"/><path d="M674 374 q0 -28 36 -28" class="door"/><text x="695" y="370" class="door-label">P-09</text>

  <line x1="280" y1="86" x2="400" y2="86" class="window"/><line x1="280" y1="92" x2="400" y2="92" class="window-glass"/>
  <line x1="454" y1="86" x2="552" y2="86" class="window"/><line x1="454" y1="92" x2="552" y2="92" class="window-glass"/>
  <line x1="774" y1="130" x2="774" y2="196" class="window"/><line x1="768" y1="130" x2="768" y2="196" class="window-glass"/>
  <line x1="774" y1="394" x2="774" y2="438" class="window"/><line x1="768" y1="394" x2="768" y2="438" class="window-glass"/>
  <line x1="80" y1="484" x2="180" y2="484" class="window"/><line x1="80" y1="478" x2="180" y2="478" class="window-glass"/>

  <g transform="translate(800 92)"><rect x="0" y="0" width="148" height="274" rx="4" fill="#fff" stroke="#888"/><text x="14" y="27" class="legend-title">Legenda</text><text x="14" y="52" class="legend">P-01 Guarita</text><text x="14" y="75" class="legend">P-02 Corredor técnico</text><text x="14" y="98" class="legend">P-03 Administração</text><text x="14" y="121" class="legend">P-04 Doca de serviço</text><text x="14" y="144" class="legend">P-05 Depósito</text><text x="14" y="167" class="legend">P-06 Reserva Técnica B</text><text x="14" y="190" class="legend">P-07 Reserva Técnica A</text><text x="14" y="213" class="legend">P-08 Sala de Segurança</text><text x="14" y="236" class="legend">P-09 Vitrine</text><text x="14" y="259" class="micro">Linhas e escala são aproximadas.</text></g>
  <g transform="translate(800 392)"><rect x="0" y="0" width="148" height="72" fill="#fff" stroke="#777"/><text x="10" y="19" class="stamp">Carimbo técnico</text><line x1="10" y1="30" x2="138" y2="30" stroke="#999"/><text x="10" y="48" class="micro">Uso: apuração interna / E1</text><text x="10" y="62" class="micro">Rotas não registradas</text></g>
</svg>"""


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
    """Renderiza PDFs visuais e agrupa mapas por fase e cartões em apoio visual."""
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
        grupos.setdefault("apoio_visual", []).append(caminho)

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
        grupos.setdefault("apoio_visual", []).append(caminho)

    return grupos

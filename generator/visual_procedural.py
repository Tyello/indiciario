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
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="Planta baixa do térreo da Casa de Acervo Mirante">
  <desc>Planta baixa em tons de cinza com Guarita, Pátio externo, Administração, Sala de Segurança, Doca de Serviço, Depósito, Reserva Técnica A, Reserva Técnica B, Vitrine / área pública, paredes, janelas e portas codificadas P-01 a P-09 para cruzamento documental.</desc>
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#f0f0f0" stroke-width="1"/></pattern>
    <style>
      .wall{fill:#fbfbfb;stroke:#111;stroke-width:7;stroke-linejoin:miter}.partition{stroke:#111;stroke-width:4.5;stroke-linecap:square}.room{fill:#f8f8f8;stroke:#5f5f5f;stroke-width:1.2}.service{fill:#f0f0f0;stroke:#555;stroke-width:1.2}.reserve{fill:#e9e9e9;stroke:#444;stroke-width:1.3}.public{fill:#fcfcfc;stroke:#555;stroke-width:1.2}.outside{fill:#f6f6f6;stroke:#777;stroke-width:1.1;stroke-dasharray:6 5}.label{font-family:Arial,sans-serif;font-size:15px;font-weight:700;fill:#111;text-anchor:middle}.small{font-family:Arial,sans-serif;font-size:11px;fill:#565656;text-anchor:middle}.micro{font-family:Arial,sans-serif;font-size:10px;fill:#555}.door-gap{stroke:#fbfbfb;stroke-width:12;stroke-linecap:square}.door{fill:none;stroke:#111;stroke-width:2.4;stroke-linecap:round}.door-label{font-family:Arial,sans-serif;font-size:10px;font-weight:700;fill:#111;text-anchor:middle}.window{stroke:#111;stroke-width:2.1;stroke-linecap:square}.window-glass{stroke:#787878;stroke-width:1}.north{font-family:Arial,sans-serif;font-size:11px;fill:#111;text-anchor:middle}
    </style>
  </defs>
  <rect x="0" y="0" width="960" height="540" fill="#fff"/>
  <rect x="18" y="18" width="924" height="504" fill="url(#grid)" stroke="#d8d8d8"/>
  <text x="42" y="42" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#111">Planta baixa — Casa de Acervo Mirante</text>
  <text x="42" y="63" font-family="Arial,sans-serif" font-size="11.5" fill="#555">Ambientes nomeados na planta; códigos usados apenas nas portas P-01 a P-09.</text>

  <rect x="172" y="84" width="650" height="404" class="wall"/>
  <rect x="62" y="118" width="86" height="72" class="outside"/><text x="105" y="151" class="label">Guarita</text><text x="105" y="168" class="small">controle externo</text>
  <rect x="62" y="228" width="112" height="126" class="outside"/><text x="118" y="284" class="label"><tspan x="118" dy="0">Pátio</tspan><tspan x="118" dy="18">externo</tspan></text>

  <rect x="190" y="102" width="156" height="106" class="room"/><text x="268" y="149" class="label">Administração</text><text x="268" y="167" class="small">terminal interno</text>
  <rect x="364" y="102" width="150" height="106" class="room"/><text x="439" y="145" class="label"><tspan x="439" dy="0">Sala de</tspan><tspan x="439" dy="18">Segurança</tspan></text>
  <rect x="190" y="232" width="324" height="78" class="service"/><text x="352" y="266" class="label">Corredor técnico</text><text x="352" y="284" class="small">circulação restrita</text>
  <rect x="190" y="334" width="158" height="112" class="service"/><text x="269" y="383" class="label"><tspan x="269" dy="0">Doca de</tspan><tspan x="269" dy="18">Serviço</tspan></text>
  <rect x="366" y="334" width="148" height="112" class="service"/><text x="440" y="384" class="label">Depósito</text><text x="440" y="402" class="small">materiais</text>

  <rect x="548" y="102" width="250" height="98" class="reserve"/><text x="673" y="145" class="label">Reserva Técnica A</text><text x="673" y="164" class="small">acervo embalado</text>
  <rect x="548" y="234" width="250" height="112" class="reserve"/><text x="673" y="284" class="label">Reserva Técnica B</text><text x="673" y="303" class="small">controle de acesso P-06</text>
  <rect x="548" y="382" width="250" height="64" class="public"/><text x="673" y="408" class="label">Vitrine / área pública</text><text x="673" y="426" class="small">acesso controlado</text>

  <line x1="180" y1="218" x2="522" y2="218" class="partition"/><line x1="180" y1="322" x2="522" y2="322" class="partition"/>
  <line x1="356" y1="84" x2="356" y2="218" class="partition"/><line x1="356" y1="322" x2="356" y2="488" class="partition"/>
  <line x1="530" y1="84" x2="530" y2="488" class="partition"/>
  <line x1="530" y1="218" x2="822" y2="218" class="partition"/><line x1="530" y1="364" x2="822" y2="364" class="partition"/>

  <line x1="112" y1="118" x2="132" y2="118" class="door-gap"/><path d="M112 118 q0 -22 28 -22" class="door"/><text x="121" y="113" class="door-label">P-01</text>
  <line x1="172" y1="248" x2="172" y2="288" class="door-gap"/><path d="M172 248 q-30 0 -30 36" class="door"/><text x="158" y="270" class="door-label">P-02</text>
  <line x1="250" y1="218" x2="294" y2="218" class="door-gap"/><path d="M250 218 q0 -28 36 -28" class="door"/><text x="272" y="214" class="door-label">P-03</text>
  <line x1="190" y1="372" x2="190" y2="420" class="door-gap"/><path d="M190 372 q-36 10 0 48" class="door"/><text x="176" y="398" class="door-label">P-04</text>
  <line x1="356" y1="374" x2="356" y2="420" class="door-gap"/><path d="M356 374 q-30 0 -30 36" class="door"/><text x="342" y="397" class="door-label">P-05</text>
  <line x1="530" y1="272" x2="530" y2="316" class="door-gap"/><path d="M530 272 q-36 0 -36 36" class="door"/><text x="516" y="296" class="door-label">P-06</text>
  <line x1="530" y1="132" x2="530" y2="174" class="door-gap"/><path d="M530 132 q-36 0 -36 36" class="door"/><text x="516" y="155" class="door-label">P-07</text>
  <line x1="420" y1="218" x2="466" y2="218" class="door-gap"/><path d="M420 218 q0 -28 36 -28" class="door"/><text x="443" y="214" class="door-label">P-08</text>
  <line x1="642" y1="364" x2="696" y2="364" class="door-gap"/><path d="M642 364 q0 -28 40 -28" class="door"/><text x="669" y="360" class="door-label">P-09</text>

  <line x1="224" y1="84" x2="324" y2="84" class="window"/><line x1="224" y1="91" x2="324" y2="91" class="window-glass"/>
  <line x1="394" y1="84" x2="488" y2="84" class="window"/><line x1="394" y1="91" x2="488" y2="91" class="window-glass"/>
  <line x1="822" y1="124" x2="822" y2="188" class="window"/><line x1="815" y1="124" x2="815" y2="188" class="window-glass"/>
  <line x1="822" y1="392" x2="822" y2="436" class="window"/><line x1="815" y1="392" x2="815" y2="436" class="window-glass"/>
  <line x1="78" y1="190" x2="138" y2="190" class="window"/><line x1="78" y1="196" x2="138" y2="196" class="window-glass"/>

  <g transform="translate(872 84)"><path d="M20 0 L32 54 L20 43 L8 54 Z" fill="#fff" stroke="#111"/><text x="20" y="72" class="north">N</text></g>
  <g transform="translate(72 458)"><line x1="0" y1="0" x2="100" y2="0" stroke="#111" stroke-width="3"/><line x1="0" y1="-5" x2="0" y2="5" stroke="#111"/><line x1="100" y1="-5" x2="100" y2="5" stroke="#111"/><text x="50" y="18" class="micro" text-anchor="middle">escala aproximada</text></g>
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

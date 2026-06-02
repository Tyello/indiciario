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


def build_map_svg(mapa: MapaProcedural) -> str:
    """Monta SVG local para um mapa procedural simples de um andar."""
    largura = max(mapa.largura, 1)
    altura = max(mapa.altura, 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:g} {altura:g}" role="img" aria-label="{escape(mapa.titulo)}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc" stroke="#111827" stroke-width="2"/>',
    ]

    for area in mapa.areas:
        fill = "#ffffff" if area.acessivel else "#e5e7eb"
        stroke_dash = "" if area.acessivel else ' stroke-dasharray="8 5"'
        parts.append(
            f'<rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" '
            f'fill="{fill}" stroke="#374151" stroke-width="2"{stroke_dash}/>'
        )

    centers = {area.id: (area.x + area.w / 2, area.y + area.h / 2) for area in mapa.areas if area.id}
    for conexao in mapa.conexoes:
        origem = centers.get(conexao.origem)
        destino = centers.get(conexao.destino)
        if not origem or not destino:
            continue
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#111827" stroke-width="3" stroke-opacity="0.55" stroke-dasharray="6 5"/>'
        )

    for area in mapa.areas:
        label = escape(_short_label(area.nome, 24))
        parts.append(
            f'<rect x="{area.x + 6:g}" y="{area.y + 8:g}" width="{min(area.w - 12, 150):g}" height="24" '
            'rx="3" fill="#ffffff" fill-opacity="0.88"/>'
        )
        parts.append(
            f'<text x="{area.x + 12:g}" y="{area.y + 25:g}" font-family="Arial, sans-serif" '
            f'font-size="13" font-weight="700" fill="#111827">{label}</text>'
        )
        if area.observacao:
            parts.append(
                f'<text x="{area.x + 12:g}" y="{area.y + 45:g}" font-family="Arial, sans-serif" '
                f'font-size="10" fill="#4b5563">{escape(_short_label(area.observacao, 30))}</text>'
            )

    marker_offsets = [(14, -14), (14, 18), (-128, -14), (-128, 18)]
    for index, marcador in enumerate(mapa.marcadores):
        dx, dy = marker_offsets[index % len(marker_offsets)]
        label = escape(_short_label(marcador.label, 30))
        label_x = max(8, min(marcador.x + dx, largura - 178))
        label_y = max(18, min(marcador.y + dy, altura - 28))
        parts.append(f'<circle cx="{marcador.x:g}" cy="{marcador.y:g}" r="11" fill="#111827"/>')
        parts.append(
            f'<text x="{marcador.x:g}" y="{marcador.y + 4:g}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="9" font-weight="700" fill="#ffffff">{escape(marcador.tipo[:2].upper())}</text>'
        )
        parts.append(
            f'<rect x="{label_x:g}" y="{label_y - 14:g}" width="170" height="22" rx="4" '
            'fill="#ffffff" fill-opacity="0.92" stroke="#9ca3af"/>'
        )
        parts.append(
            f'<text x="{label_x + 6:g}" y="{label_y + 1:g}" font-family="Arial, sans-serif" '
            f'font-size="11" fill="#111827">{label}</text>'
        )

    if mapa.legenda:
        legend_height = 18 * len(mapa.legenda) + 16
        legend_width = 300
        y = max(12, altura - legend_height - 12)
        x = max(12, largura - legend_width - 12)
        parts.append(f'<g transform="translate({x:g} {y:g})">')
        parts.append(
            f'<rect x="0" y="0" width="{legend_width}" height="{legend_height}" rx="5" '
            'fill="#ffffff" fill-opacity="0.95" stroke="#9ca3af"/>'
        )
        for index, item in enumerate(mapa.legenda):
            line_y = 20 + index * 18
            parts.append(
                f'<text x="10" y="{line_y}" font-family="Arial, sans-serif" font-size="11" fill="#111827">'
                f'{escape(item.simbolo)} — {escape(_short_label(item.descricao, 36))}</text>'
            )
        parts.append('</g>')

    parts.append('</svg>')
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
    parts.append('</svg>')
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
    parts.append('</svg>')
    return "".join(parts)


def visual_document_code(kind: str, identifier: str) -> str:
    prefixes = {"map": "VP-MAPA", "character": "VP-PERSONAGEM", "location": "VP-LOCAL"}
    return f"{prefixes[kind]}-{identifier}"


def visual_document_path(kind: str, identifier: str, output_dir: Path) -> Path:
    names = {"map": "visual_map", "character": "visual_personagem", "location": "visual_local"}
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
        dados = {"TITULO": mapa.titulo, "SUBTITULO": f"Mapa procedural — {mapa.fase}", "SVG": svg}
        render_kwargs = {"strict": strict, "landscape": True}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = html_debug_dir / f"{output_path.stem}.html"
        caminho = renderizar_documento("visual_map.html", dados, output_path, **render_kwargs)
        grupos.setdefault(mapa.fase or "E1", []).append(caminho)

    for personagem in visual.personagens:
        svg = build_character_card_svg(personagem, blueprint)
        output_path = visual_document_path("character", personagem.personagem_id, output_dir)
        nome = _personagem_nome(personagem, blueprint)
        dados = {"TITULO": f"Cartão de personagem — {nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = html_debug_dir / f"{output_path.stem}.html"
        caminho = renderizar_documento("visual_character_card.html", dados, output_path, **render_kwargs)
        grupos.setdefault("E1", []).append(caminho)

    for local in visual.locais:
        svg = build_location_card_svg(local)
        output_path = visual_document_path("location", local.id, output_dir)
        dados = {"TITULO": f"Cartão de local — {local.nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = html_debug_dir / f"{output_path.stem}.html"
        caminho = renderizar_documento("visual_location_card.html", dados, output_path, **render_kwargs)
        grupos.setdefault("E1", []).append(caminho)

    return grupos

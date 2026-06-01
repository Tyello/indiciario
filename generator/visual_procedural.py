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
        parts.append(
            f'<text x="{area.x + 8:g}" y="{area.y + 22:g}" font-family="Arial, sans-serif" '
            f'font-size="14" fill="#111827">{escape(area.nome)}</text>'
        )
        if area.observacao:
            parts.append(
                f'<text x="{area.x + 8:g}" y="{area.y + 42:g}" font-family="Arial, sans-serif" '
                f'font-size="10" fill="#4b5563">{escape(area.observacao)}</text>'
            )

    centers = {area.id: (area.x + area.w / 2, area.y + area.h / 2) for area in mapa.areas if area.id}
    for conexao in mapa.conexoes:
        origem = centers.get(conexao.origem)
        destino = centers.get(conexao.destino)
        if not origem or not destino:
            continue
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#111827" stroke-width="3" stroke-dasharray="6 4"/>'
        )

    for marcador in mapa.marcadores:
        parts.append(f'<circle cx="{marcador.x:g}" cy="{marcador.y:g}" r="10" fill="#111827"/>')
        parts.append(
            f'<text x="{marcador.x:g}" y="{marcador.y + 4:g}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="9" fill="#ffffff">{escape(marcador.tipo[:2].upper())}</text>'
        )
        parts.append(
            f'<text x="{marcador.x + 14:g}" y="{marcador.y + 4:g}" font-family="Arial, sans-serif" '
            f'font-size="12" fill="#111827">{escape(marcador.label)}</text>'
        )

    if mapa.legenda:
        y = altura - 18 * len(mapa.legenda) - 10
        parts.append(f'<g transform="translate(12 {max(y, 12):g})">')
        parts.append('<rect x="0" y="0" width="260" height="100%" fill="#ffffff" stroke="#9ca3af"/>')
        for index, item in enumerate(mapa.legenda):
            line_y = 20 + index * 18
            parts.append(
                f'<text x="10" y="{line_y}" font-family="Arial, sans-serif" font-size="11" fill="#111827">'
                f'{escape(item.simbolo)} — {escape(item.descricao)}</text>'
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


def build_visual_documents(blueprint: Blueprint, output_dir: Path, strict: bool = True) -> dict[str, list[Path]]:
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
        caminho = renderizar_documento("visual_map.html", dados, output_path, strict=strict, landscape=True)
        grupos.setdefault(mapa.fase or "E1", []).append(caminho)

    for personagem in visual.personagens:
        svg = build_character_card_svg(personagem, blueprint)
        output_path = visual_document_path("character", personagem.personagem_id, output_dir)
        nome = _personagem_nome(personagem, blueprint)
        dados = {"TITULO": f"Cartão de personagem — {nome}", "SVG": svg}
        caminho = renderizar_documento("visual_character_card.html", dados, output_path, strict=strict)
        grupos.setdefault("E1", []).append(caminho)

    for local in visual.locais:
        svg = build_location_card_svg(local)
        output_path = visual_document_path("location", local.id, output_dir)
        dados = {"TITULO": f"Cartão de local — {local.nome}", "SVG": svg}
        caminho = renderizar_documento("visual_location_card.html", dados, output_path, strict=strict)
        grupos.setdefault("E1", []).append(caminho)

    return grupos

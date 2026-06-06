"""Renderização de printables apartados para apoio de mesa."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Callable

from .models import Blueprint, PrintableCard, TipoPrintableCard
from .renderer import renderizar_documento


_CARD_TYPE_LABELS = {
    TipoPrintableCard.PERSONAGEM: "Personagem",
    TipoPrintableCard.LOCAL: "Local",
    TipoPrintableCard.OBJETO: "Objeto",
}

_CARD_TYPE_PLURALS = {
    TipoPrintableCard.PERSONAGEM: "personagens",
    TipoPrintableCard.LOCAL: "locais",
    TipoPrintableCard.OBJETO: "objetos",
}

_CARD_TYPE_SYMBOLS = {
    TipoPrintableCard.PERSONAGEM: "P",
    TipoPrintableCard.LOCAL: "L",
    TipoPrintableCard.OBJETO: "O",
}


def _text(value: str | None) -> str:
    return " ".join((value or "").split())


def _card_code(card: PrintableCard) -> str:
    return _text(card.codigo_visual) or card.id


def _simple_svg(card: PrintableCard) -> str:
    """Monta um marcador SVG P&B simples, sem imagem externa."""
    label = _CARD_TYPE_SYMBOLS.get(card.tipo, "C")
    code = escape(_card_code(card)[:12])
    return (
        '<svg class="printable-card-icon-svg" xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 120 120" role="img" aria-label="Marcador visual do cartão">'
        '<rect x="8" y="8" width="104" height="104" rx="14" fill="#fff" '
        'stroke="#111" stroke-width="4"/>'
        '<circle cx="60" cy="48" r="24" fill="#f5f5f5" stroke="#111" stroke-width="3"/>'
        f'<text x="60" y="57" text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="30" font-weight="700" fill="#111">{label}</text>'
        f'<text x="60" y="88" text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="13" font-weight="700" fill="#111">{code}</text>'
        '</svg>'
    )


def _card_context(card: PrintableCard, case_title: str) -> dict[str, Any]:
    tags = [_text(tag) for tag in card.tags_visuais if _text(tag)]
    return {
        "id": card.id,
        "code": _card_code(card),
        "title": _text(card.titulo),
        "subtitle": _text(card.subtitulo),
        "description": _text(card.descricao_curta),
        "public_note": _text(card.observacao_publica),
        "type": card.tipo.value,
        "type_label": _CARD_TYPE_LABELS.get(card.tipo, card.tipo.value),
        "type_class": card.tipo.value,
        "category_marker": _CARD_TYPE_SYMBOLS.get(card.tipo, "C"),
        "recommended_envelope": _text(card.envelope_recomendado),
        "has_recommended_envelope": bool(_text(card.envelope_recomendado)),
        "tags": [{"tag": tag} for tag in tags],
        "has_tags": bool(tags),
        "svg": _simple_svg(card),
        "case_title": case_title,
    }


RenderFunc = Callable[..., Path]


def _render_sheet(
    blueprint: Blueprint,
    cards: list[PrintableCard],
    output_path: Path,
    strict: bool = True,
    html_debug_dir: Path | None = None,
    render_func: RenderFunc | None = None,
) -> Path:
    dados = {
        "TITULO": "Cartões recortáveis — apoio de mesa",
        "NOME_CASO": blueprint.titulo,
        "CARDS": [_card_context(card, blueprint.titulo) for card in cards],
        "CARD_COUNT": len(cards),
    }
    render_kwargs: dict[str, Any] = {"strict": strict}
    if html_debug_dir is not None:
        render_kwargs["html_debug_path"] = html_debug_dir / f"{output_path.stem}.html"
    selected_render = render_func or renderizar_documento
    return selected_render("printable_cards.html", dados, output_path, **render_kwargs)


def build_printable_card_documents(
    blueprint: Blueprint,
    package_dir: Path,
    strict: bool = True,
    html_debug_dir: Path | None = None,
    render_func: RenderFunc | None = None,
) -> list[Path]:
    """Renderiza PDFs de cartões em ``printables/`` e retorna os caminhos criados."""
    cards = [card for card in blueprint.printable_cards if card.entregar_apartado]
    if not cards:
        return []

    output_dir = package_dir / "printables"
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []

    for tipo in TipoPrintableCard:
        type_cards = [card for card in cards if card.tipo == tipo]
        if not type_cards:
            continue
        rendered.append(
            _render_sheet(
                blueprint,
                type_cards,
                output_dir / f"cards_{_CARD_TYPE_PLURALS[tipo]}.pdf",
                strict=strict,
                html_debug_dir=html_debug_dir,
                render_func=render_func,
            )
        )

    rendered.append(
        _render_sheet(
            blueprint,
            cards,
            output_dir / "cards_todos.pdf",
            strict=strict,
            html_debug_dir=html_debug_dir,
            render_func=render_func,
        )
    )

    return rendered

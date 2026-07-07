"""generator/font_fidelity.py

Helpers de medição de fidelidade de fonte, extraídos de
`tests/test_font_vendoring.py` (ISSUE-40.1, STEP-02) no STEP-01 da
ISSUE-40.2 para serem reusados tanto pelos testes de regressão da 40.1
quanto pelo Canonical Quality Gate (`generator.canonical_quality_gate`,
critério `font_fidelity`, ISSUE-40.2).

Técnica: `canvas.measureText` comparando a largura do texto renderizado com
a fonte pedida (+ fallback `monospace`) contra a largura com `monospace`
puro. `getComputedStyle`/`document.fonts.check` já foram descartados na
40.1 por não detectarem fallback silencioso (o navegador reporta a fonte
pedida como "aplicada" mesmo caindo em fallback).
"""

from __future__ import annotations

from typing import Any

from generator.renderer import (
    TEMPLATES_DIR,
    _injetar_cabecalho_rodape_documental,
    _injetar_classes_body,
    _injetar_css_documental,
    _preparar_dados_documentais,
    renderizar_html,
)

__all__ = ["CUSTOM_FONTS", "_MEDIR_FONTE_JS", "_montar_html", "fonte_aplicada"]

# Inventário corrigido pós-STEP-01 (ver ISSUE-40.1.md, nota de decisão do
# orquestrador). `Inter` (03_twitter.html) fica FORA de escopo: mimetismo
# intencional de UI nativa do SO no template estilo Twitter, não identidade
# de marca -- vendorizar quebraria o propósito visual do template.
CUSTOM_FONTS: dict[str, list[str]] = {
    "01_email.html": ["DM Sans"],
    "04_boletim.html": ["Source Serif 4"],
    "06_log_acesso.html": ["JetBrains Mono"],
    "07_recibo.html": ["DM Sans", "Caveat"],
    "08_orcamento.html": ["DM Sans"],
    "09_extrato.html": ["DM Sans", "JetBrains Mono"],
    "10_bilhete.html": ["Caveat"],
    "11_testamento_rascunho.html": ["Caveat", "Libre Baskerville", "Playfair Display"],
}


def _montar_html(template_nome: str) -> str:
    """Reproduz o pipeline de injeção de `renderer.renderizar_documento` até o
    HTML final, sem passar pela etapa de PDF, para inspecionar a fonte
    computada com o Chromium do Playwright diretamente."""
    template_path = TEMPLATES_DIR / template_nome
    dados = _preparar_dados_documentais(template_nome, {})
    html_raw = template_path.read_text(encoding="utf-8")
    html_raw = _injetar_css_documental(html_raw)
    html_raw = _injetar_classes_body(html_raw, template_nome, dados)
    html_raw = _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
    return renderizar_html(html_raw, dados)


_MEDIR_FONTE_JS = """
(fontName) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const texto = 'mmmmmmmmmmlliWQOX0123456789';
  ctx.font = `48px '${fontName}', monospace`;
  const larguraComFonte = ctx.measureText(texto).width;
  ctx.font = '48px monospace';
  const larguraFallback = ctx.measureText(texto).width;
  return larguraComFonte !== larguraFallback;
}
"""


def fonte_aplicada(browser: Any, template_nome: str, fonte: str) -> bool:
    """Mede (via Chromium real, técnica `canvas.measureText`) se `fonte` foi
    de fato aplicada ao renderizar `template_nome` -- ou se caiu em fallback
    silencioso para fonte de sistema."""
    html = _montar_html(template_nome)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        page.evaluate("document.fonts.ready")
        return page.evaluate(_MEDIR_FONTE_JS, fonte)
    finally:
        page.close()

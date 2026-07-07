"""
tests/test_font_vendoring.py

RED (ISSUE-40.1, STEP-02): comprova que templates com font-family custom
(DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville,
Playfair Display) não têm garantia de fonte hoje — `document_system.css`
v1 não declara `@font-face` local para nenhuma delas, então o Chromium só
renderiza a família correta se ela por acaso estiver instalada no SO.

Duas APIs óbvias NÃO servem para detectar esse fallback, e foram testadas e
descartadas antes de fechar este teste:

- `getComputedStyle(el).fontFamily` devolve a pilha de fontes tal como
  declarada no CSS (a string), não a fonte de fato usada para desenhar o
  texto — nunca detectaria um fallback silencioso.
- `document.fonts.check("16px 'X'")` foi testado empiricamente neste
  Chromium (via Playwright, versão 148.0.7778.96) e retorna `True` mesmo
  para uma família inexistente (`'ThisFontDoesNotExist12345'`) — o método
  aparentemente considera "disponível" qualquer família que resolva para
  *algum* glifo renderizável via fallback, o que o torna inútil para este
  teste.

Em vez disso, o teste usa a técnica clássica de detecção de fonte via
`canvas.measureText`: mede a largura de um texto de amostra com
`font-family: '<Fonte>', monospace` e compara com a largura do mesmo texto
usando só `monospace`. Se as larguras forem iguais, o navegador caiu no
fallback (`monospace`) — a fonte não está de fato disponível. Se forem
diferentes, a fonte customizada foi de fato aplicada. Validado
manualmente: `Arial`/`Times New Roman` (fontes reais do SO) produzem
larguras diferentes de `monospace`; `DM Sans`, `JetBrains Mono` e uma
família inexistente produzem a mesma largura de `monospace` no estado
atual do repo (sem `@font-face`).

Depois da vendorização (STEP-03: @font-face local + font-display: block +
espera por document.fonts.ready antes do screenshot), este teste deve
ficar GREEN mesmo em ambiente sem nenhuma das fontes instaladas no SO.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from generator.renderer import (
    TEMPLATES_DIR,
    _injetar_cabecalho_rodape_documental,
    _injetar_classes_body,
    _injetar_css_documental,
    _preparar_dados_documentais,
    renderizar_html,
)

# Inventário corrigido pós-STEP-01 (ver ISSUE-40.1.md, nota de decisão do
# orquestrador). `Inter` (03_twitter.html) fica FORA de escopo: mimetismo
# intencional de UI nativa do SO no template estilo Twitter, não identidade
# de marca — vendorizar quebraria o propósito visual do template.
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


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


@pytest.mark.parametrize("template_nome,fontes", CUSTOM_FONTS.items())
def test_template_nao_cai_em_fallback_de_fonte_de_sistema(template_nome, fontes, browser):
    """Cada fonte custom declarada no template precisa estar realmente
    disponível para o Chromium (via @font-face local, quando existir).
    Falha hoje (v1, sem @font-face) porque nenhuma família está vendorizada
    — o canvas mede a mesma largura com a fonte pedida ou com o fallback
    'monospace' puro, ou seja, o navegador está caindo em fallback."""
    html = _montar_html(template_nome)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        page.evaluate("document.fonts.ready")
        for fonte in fontes:
            fonte_aplicada = page.evaluate(_MEDIR_FONTE_JS, fonte)
            assert fonte_aplicada, (
                f"{template_nome}: fonte '{fonte}' não foi de fato aplicada pelo "
                f"Chromium — fallback silencioso para fonte de sistema "
                f"(sem @font-face local declarado ainda, ISSUE-40.1)"
            )
    finally:
        page.close()

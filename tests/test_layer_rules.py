"""
tests/test_layer_rules.py

RED (ISSUE-40.3, STEP-02): comprova a mistura de vocabulário visual entre
Camada 1 (tela — prints de e-mail/WhatsApp/rede social, onde sombra,
`border-radius` e chrome de app são corretos) e Camada 2 (papel — boletim,
carta, recibo, orçamento etc., onde a superfície não projeta sombra de si
mesma, não tem `border-radius` nem gradiente).

Inventário e classificação extraídos de
`.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md` (Glob completo de `templates/*.html`
+ Grep de `box-shadow|border-radius|linear-gradient|radial-gradient` e de
`Envelope|DOC-|doc-code`). Achado central do STEP-01: nenhum template
`{% extends %}` `base.html` — o motor de render é `generator/renderer.py`
(substituição por string, via `_montar_html`, já usado por
`tests/test_font_vendoring.py`), não Jinja2 com herança. `base.html` é órfão,
não instanciado por nenhum template ativo, portanto fora da parametrização
abaixo (decisão registrada no STEP-01, a ser tratada como decisão explícita
de arquitetura no STEP-03).

Teste 1 (`test_paper_layer_has_no_screen_chrome`) é o RED real: os 8
templates de papel (`04_boletim.html` .. `11_testamento_rascunho.html`) têm
`box-shadow`/`border-radius`/gradiente em `<style>` inline hoje (ex.:
`.page` de `08_orcamento.html` com `box-shadow: 0 2px 16px rgba(0,0,0,.1)` e
`border-radius: 2px`; `.accent-bar` com `linear-gradient`). `floorplan.html`,
`visual_map.html`, `visual_character_card.html` e `visual_location_card.html`
já estão conformes (STEP-01), mas continuam parametrizados como rede de
regressão.

Teste 2 (`test_diegetic_view_has_no_game_chrome`) é guarda de regressão: o
STEP-01 já confirmou 0 ocorrências de `Envelope N`/`DOC-`/`.doc-code` nos
templates diegéticos reais (Camada 1 e 2) — não se espera falha nele hoje,
mas ele fecha o critério de aceite #3 (chrome de jogo ausente do DOM, não só
oculto via CSS) contra regressão futura.
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright

from generator.font_fidelity import _montar_html

# Parametrização herdada de .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md
# (seção "Parametrização recomendada para tests/test_layer_rules.py").
PAPER_LAYER_TEMPLATES = [
    "04_boletim.html",
    "05_carta.html",
    "06_log_acesso.html",
    "07_recibo.html",
    "08_orcamento.html",
    "09_extrato.html",
    "10_bilhete.html",
    "11_testamento_rascunho.html",
    "floorplan.html",
    "visual_map.html",
    "visual_character_card.html",
    "visual_location_card.html",
]

SCREEN_LAYER_TEMPLATES = [
    "01_email.html",
    "02_whatsapp.html",
    "02_whatsapp2.html",
    "03_twitter.html",
]

DIEGETIC_TEMPLATES = PAPER_LAYER_TEMPLATES + SCREEN_LAYER_TEMPLATES


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


# Varre todo elemento visível de `document.body` e reporta qualquer um que
# use vocabulário de card web (sombra própria, cantos arredondados,
# gradiente de fundo). Não confia em `getComputedStyle(el).boxShadow` etc.
# em uma única string do shorthand — cada canto de `border-radius` é
# checado individualmente para não deixar passar `border-top-left-radius`
# isolado.
_PAPER_SURFACE_VIOLATIONS_JS = """
() => {
  const violacoes = [];
  const elementos = document.body.querySelectorAll('*');
  elementos.forEach((el) => {
    const cs = getComputedStyle(el);
    const boxShadow = cs.boxShadow;
    const cantos = [
      cs.borderTopLeftRadius,
      cs.borderTopRightRadius,
      cs.borderBottomLeftRadius,
      cs.borderBottomRightRadius,
    ];
    const temRaio = cantos.some((c) => c && c !== '0px');
    const bgImage = cs.backgroundImage || '';
    const temGradiente = bgImage.includes('gradient');
    const temSombra = !!boxShadow && boxShadow !== 'none';
    if (temSombra || temRaio || temGradiente) {
      let classe = '';
      try {
        classe = el.getAttribute('class') || '';
      } catch (e) {
        classe = '';
      }
      violacoes.push({
        tag: el.tagName,
        classe,
        boxShadow,
        cantos,
        bgImage,
      });
    }
  });
  return violacoes;
}
"""


@pytest.mark.parametrize("template_nome", PAPER_LAYER_TEMPLATES)
def test_paper_layer_has_no_screen_chrome(template_nome, browser):
    """Camada 2 (papel) não pode usar box-shadow/border-radius/gradiente em
    nenhum elemento da superfície do documento — papel não projeta sombra de
    si mesmo, não tem cantos arredondados nem gradiente. Falha hoje para os
    8 templates de papel citados no diagnóstico (`.page`, `.accent-bar`,
    `.orcamento-dates` e equivalentes usam vocabulário de card web)."""
    html = _montar_html(template_nome)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        violacoes = page.evaluate(_PAPER_SURFACE_VIOLATIONS_JS)
        assert violacoes == [], (
            f"{template_nome}: superfície de papel usa vocabulário de "
            f"Camada 1 (tela) -- box-shadow/border-radius/gradiente "
            f"encontrados em: {violacoes}"
        )
    finally:
        page.close()


# Critério de aceite #3: `doc-code`, título de jogo (`DOC-...`) e
# "Envelope N" não podem aparecer no DOM visível da view do jogador —
# ausentes de fato, não apenas escondidos via `display:none` (que ainda
# deixaria o texto acessível via `innerText`/leitor de tela/inspeção).
_CHROME_DE_JOGO_PATTERNS = [
    re.compile(r"DOC-\S"),
    re.compile(r"Envelope\s+\d"),
]


@pytest.mark.parametrize("template_nome", DIEGETIC_TEMPLATES)
def test_diegetic_view_has_no_game_chrome(template_nome, browser):
    """View do jogador (Camada 1 e 2) não pode renderizar `doc-code`,
    título de jogo (`DOC-...`) nem "Envelope N" -- nem como texto visível
    nem como elemento presente no DOM (mesmo oculto)."""
    html = _montar_html(template_nome)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")

        doc_code_el = page.query_selector(".doc-code")
        assert doc_code_el is None, (
            f"{template_nome}: elemento .doc-code presente no DOM da view "
            f"do jogador"
        )

        texto_visivel = page.evaluate("document.body.innerText")
        for padrao in _CHROME_DE_JOGO_PATTERNS:
            assert not padrao.search(texto_visivel), (
                f"{template_nome}: chrome de jogo ('{padrao.pattern}') "
                f"vazou para o texto visível da view do jogador"
            )
    finally:
        page.close()

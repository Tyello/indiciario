"""
tests/test_paper_color_taxonomy.py

RED (ISSUE-40.4, STEP-02): comprova a taxonomia de cor papel-por-tipo para
`04_boletim.html` -- boletim e depoimento são o MESMO arquivo físico,
diferenciado em runtime por `TIPO_DOCUMENTAL_SLUG` / classe `doc-type-*`
(achado do STEP-01, `.ai/runs/ISSUE-40.4/STEP-01_EXECUTION.md`). Ambos caem
hoje na mesma família CSS `admin` (`.doc-family-admin .page`), então a
diferenciação de cor só pode vir de regras `.doc-type-boletim .page` /
`.doc-type-depoimento .page` -- daí os testes forçarem
`TIPO_DOCUMENTAL_SLUG` explicitamente, no mesmo template, em vez de assumir
dois arquivos separados.

`generator.font_fidelity._montar_html` não aceita override de dados (só
`template_nome`) -- por isso este arquivo replica localmente o mesmo
pipeline (`_preparar_dados_documentais` -> `_injetar_css_documental` ->
`_injetar_classes_body` -> `_injetar_cabecalho_rodape_documental` ->
`renderizar_html`), injetando `{"TIPO_DOCUMENTAL_SLUG": tipo_slug}` como
dados iniciais para forçar boletim/depoimento no mesmo arquivo físico.

Teste 1 (`test_boletim_has_no_aging_texture`) é guarda de regressão: o
STEP-01 confirmou que a textura de envelhecimento (`radial-gradient` +
`box-shadow: inset`) já foi removida de `04_boletim.html` pela 40.3-- este
teste nasce GREEN hoje (documentado no STEP-01_EXECUTION.md), não é RED
artificial.

Testes 2 e 3 (`test_boletim_uses_taxonomy_color`,
`test_depoimento_uses_taxonomy_color`) são RED real hoje: os tokens
`--paper-boletim`/`--paper-depoimento` e as regras `.doc-type-boletim .page`
/ `.doc-type-depoimento .page` ainda não existem em `document_system.css` --
`.page` herda `background: var(--ind-paper-cool)` de `.doc-family-admin`
para os dois tipos, cor idêntica.

Teste 4 (`test_paper_laudo_token_exists`) é RED real hoje: `--paper-laudo`
ainda não está declarado em `:root` de `document_system.css` (critério de
aceite #3 -- token existe mesmo sem template consumindo ainda).
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright

from generator.renderer import (
    DOCUMENT_SYSTEM_CSS_PATH,
    TEMPLATES_DIR,
    _injetar_cabecalho_rodape_documental,
    _injetar_classes_body,
    _injetar_css_documental,
    _preparar_dados_documentais,
    renderizar_html,
)

TEMPLATE_BOLETIM = "04_boletim.html"

# Cores-alvo da taxonomia (ISSUE-40.4, item 2 do Objetivo) convertidas para
# o formato `rgb(...)` que `getComputedStyle` devolve no navegador.
_COR_BOLETIM_HEX = "#e4f2e4"
_COR_BOLETIM_RGB = "rgb(228, 242, 228)"
_COR_DEPOIMENTO_HEX = "#fdf7d8"
_COR_DEPOIMENTO_RGB = "rgb(253, 247, 216)"
_COR_LAUDO_HEX = "#eef0f6"


def _montar_html_com_tipo(template_nome: str, tipo_slug: str) -> str:
    """Réplica local de `generator.font_fidelity._montar_html`, mas
    aceitando override de `TIPO_DOCUMENTAL_SLUG` -- necessário porque
    boletim e depoimento são o mesmo arquivo físico, diferenciado só em
    runtime pelos dados injetados (ver achado do STEP-01)."""
    template_path = TEMPLATES_DIR / template_nome
    dados = _preparar_dados_documentais(
        template_nome, {"TIPO_DOCUMENTAL_SLUG": tipo_slug}
    )
    html_raw = template_path.read_text(encoding="utf-8")
    html_raw = _injetar_css_documental(html_raw)
    html_raw = _injetar_classes_body(html_raw, template_nome, dados)
    html_raw = _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
    return renderizar_html(html_raw, dados)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


def _computed_style_da_page(html: str, browser) -> dict[str, str]:
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        return page.evaluate(
            """
            () => {
              const el = document.querySelector('.page');
              if (!el) return null;
              const cs = getComputedStyle(el);
              return {
                backgroundImage: cs.backgroundImage,
                boxShadow: cs.boxShadow,
                backgroundColor: cs.backgroundColor,
              };
            }
            """
        )
    finally:
        page.close()


def test_boletim_has_no_aging_texture(browser):
    """`.page` do boletim não pode ter `background-image` (textura de
    envelhecimento via `radial-gradient`) nem `box-shadow` com `inset`.
    Guarda de regressão: a 40.3 já removeu essa textura -- espera-se GREEN
    hoje (ver STEP-01_EXECUTION.md)."""
    html = _montar_html_com_tipo(TEMPLATE_BOLETIM, "boletim")
    estilo = _computed_style_da_page(html, browser)
    assert estilo is not None, f"{TEMPLATE_BOLETIM}: elemento .page não encontrado"
    assert estilo["backgroundImage"] == "none", (
        f"{TEMPLATE_BOLETIM}: .page tem background-image "
        f"(esperado 'none', textura de envelhecimento residual): "
        f"{estilo['backgroundImage']}"
    )
    assert "inset" not in estilo["boxShadow"], (
        f"{TEMPLATE_BOLETIM}: .page tem box-shadow com inset "
        f"(textura de envelhecimento residual): {estilo['boxShadow']}"
    )


def test_boletim_uses_taxonomy_color(browser):
    """Boletim (`TIPO_DOCUMENTAL_SLUG='boletim'`) deve renderizar `.page`
    com `background-color` = {_COR_BOLETIM_HEX} (verde). RED hoje: token
    `--paper-boletim` e regra `.doc-type-boletim .page` ainda não
    existem."""
    html = _montar_html_com_tipo(TEMPLATE_BOLETIM, "boletim")
    estilo = _computed_style_da_page(html, browser)
    assert estilo is not None, f"{TEMPLATE_BOLETIM}: elemento .page não encontrado"
    assert estilo["backgroundColor"] == _COR_BOLETIM_RGB, (
        f"{TEMPLATE_BOLETIM} (boletim): .page background-color esperado "
        f"{_COR_BOLETIM_RGB} ({_COR_BOLETIM_HEX}), obtido "
        f"{estilo['backgroundColor']}"
    )


def test_depoimento_uses_taxonomy_color(browser):
    """Depoimento (`TIPO_DOCUMENTAL_SLUG='depoimento'`, MESMO arquivo físico
    `04_boletim.html`) deve renderizar `.page` com `background-color` =
    {_COR_DEPOIMENTO_HEX} (amarelo), diferente do boletim. RED hoje: os dois
    tipos caem na mesma família CSS `admin` e herdam a mesma cor de
    `--ind-paper-cool`."""
    html = _montar_html_com_tipo(TEMPLATE_BOLETIM, "depoimento")
    estilo = _computed_style_da_page(html, browser)
    assert estilo is not None, f"{TEMPLATE_BOLETIM}: elemento .page não encontrado"
    assert estilo["backgroundColor"] == _COR_DEPOIMENTO_RGB, (
        f"{TEMPLATE_BOLETIM} (depoimento): .page background-color esperado "
        f"{_COR_DEPOIMENTO_RGB} ({_COR_DEPOIMENTO_HEX}), obtido "
        f"{estilo['backgroundColor']}"
    )


def test_paper_laudo_token_exists():
    """`--paper-laudo: #eef0f6` deve estar declarado em `:root` de
    `document_system.css`, mesmo sem template consumindo ainda (critério de
    aceite #3, laudo pericial fica para P3). RED hoje: token não existe."""
    css = DOCUMENT_SYSTEM_CSS_PATH.read_text(encoding="utf-8")
    root_match = re.search(r":root\s*\{(.*?)\}", css, re.DOTALL)
    assert root_match is not None, "document_system.css: bloco :root não encontrado"
    root_bloco = root_match.group(1)
    padrao = re.compile(
        r"--paper-laudo\s*:\s*" + re.escape(_COR_LAUDO_HEX) + r"\s*;"
    )
    assert padrao.search(root_bloco), (
        f"document_system.css :root não declara "
        f"--paper-laudo: {_COR_LAUDO_HEX};"
    )

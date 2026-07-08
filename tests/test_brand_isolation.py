"""
tests/test_brand_isolation.py

RED (ISSUE-40.5, STEP-02): comprova o isolamento da marca Indiciário
(`--accent: #8b1a1a`) na Camada 0 (envelope, protocolo, dicas, gabarito).

Hoje `--accent` é declarado em `:root` global dentro de `templates/base.html`
(`.ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md`). `base.html` é órfão -- nenhum
template `{% extends %}` este arquivo e `generator/renderer.py` não o carrega
(achado herdado da 40.3, reconfirmado pela 40.5/STEP-01) -- portanto
`--accent` **não vaza hoje** para nenhum dos 16 templates diegéticos de
Camada 1/2 (`PAPER_LAYER_TEMPLATES` + `SCREEN_LAYER_TEMPLATES` de
`.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md`, reproduzidos aqui como
`NON_LAYER0_TEMPLATES`).

Teste 1 (`test_diegetic_template_does_not_inherit_brand_accent`) nasce
**GREEN por desenho** -- guarda de regressão, mesmo precedente aceito na
40.4/STEP-02 (teste de aging texture): nenhum dos 16 templates referencia
`--accent` hoje (confirmado por grep no STEP-01), então o teste não tem nada
para pegar ainda, mas garante que isso continua verdade se `base.html`
deixar de ser órfão no futuro ou se algum template passar a herdar a
variável.

Teste 2 (`test_accent_variable_scoped_to_camada_0`) é **RED real hoje**:
`templates/base.html` ainda declara `--accent: #8b1a1a` dentro de `:root`
global (linha ~24), não dentro de um seletor `.camada-0`. O STEP-03 (GREEN)
move essa declaração para `.camada-0 { --accent: #8b1a1a; }`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from generator.font_fidelity import _montar_html

# Reaproveitado de tests/test_layer_rules.py, que por sua vez reaproveita
# .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md. Confirmado de novo pela
# 40.5/STEP-01 (.ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md): os 16 templates
# diegéticos (Camada 1 + Camada 2) não referenciam `--accent` hoje.
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

NON_LAYER0_TEMPLATES = PAPER_LAYER_TEMPLATES + SCREEN_LAYER_TEMPLATES

# rgb(139, 26, 26) == #8b1a1a computado.
_ACCENT_RGB = "rgb(139, 26, 26)"

BASE_HTML_PATH = Path(__file__).resolve().parent.parent / "templates" / "base.html"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


# Varre todo elemento visível de `document.body` e reporta qualquer um cujo
# `color`, `background-color` ou `border-color` computado resolva para a cor
# de marca (#8b1a1a / rgb(139, 26, 26)). Checa cada propriedade
# individualmente, não um shorthand, para não deixar passar
# `border-top-color` isolado. Também checa se `--accent` está definido e
# não-vazio no escopo do `documentElement`.
_BRAND_ACCENT_VIOLATIONS_JS = """
(accentRgb) => {
  const violacoes = [];
  const elementos = document.body.querySelectorAll('*');
  elementos.forEach((el) => {
    const cs = getComputedStyle(el);
    const cores = {
      color: cs.color,
      backgroundColor: cs.backgroundColor,
      borderTopColor: cs.borderTopColor,
      borderRightColor: cs.borderRightColor,
      borderBottomColor: cs.borderBottomColor,
      borderLeftColor: cs.borderLeftColor,
    };
    const propsComMarca = Object.entries(cores)
      .filter(([, valor]) => valor === accentRgb)
      .map(([prop]) => prop);
    if (propsComMarca.length > 0) {
      let classe = '';
      try {
        classe = el.getAttribute('class') || '';
      } catch (e) {
        classe = '';
      }
      violacoes.push({ tag: el.tagName, classe, propsComMarca });
    }
  });
  const accentVar = getComputedStyle(document.documentElement)
    .getPropertyValue('--accent')
    .trim();
  return { violacoes, accentVar };
}
"""


@pytest.mark.parametrize("template_nome", NON_LAYER0_TEMPLATES)
def test_diegetic_template_does_not_inherit_brand_accent(template_nome, browser):
    """Templates de Camada 1 (tela) e Camada 2 (papel) não podem herdar
    `--accent` (#8b1a1a / rgb(139, 26, 26)) da marca Indiciário -- nem via
    `color`/`background-color`/`border-*-color` computado em nenhum
    elemento, nem via `--accent` resolvida em `document.documentElement`.
    Nasce GREEN por desenho (ISSUE-40.5/STEP-01: `base.html` é órfão, nenhum
    dos 16 templates referencia `--accent` hoje) -- guarda de regressão."""
    html = _montar_html(template_nome)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        resultado = page.evaluate(_BRAND_ACCENT_VIOLATIONS_JS, _ACCENT_RGB)
        assert resultado["violacoes"] == [], (
            f"{template_nome}: elemento(s) herdaram a cor de marca "
            f"Indiciário ({_ACCENT_RGB}) fora da Camada 0: "
            f"{resultado['violacoes']}"
        )
        assert resultado["accentVar"] == "", (
            f"{template_nome}: --accent resolvida como "
            f"'{resultado['accentVar']}' no documentElement -- deveria "
            f"estar vazia fora do escopo .camada-0"
        )
    finally:
        page.close()


def test_accent_variable_scoped_to_camada_0():
    """`--accent` só pode ser declarada dentro de um seletor `.camada-0`
    em `templates/base.html` -- não em `:root` global. RED real hoje: a
    declaração ainda está em `:root` (linha ~24). O STEP-03 move para
    `.camada-0 { --accent: #8b1a1a; }`."""
    css = BASE_HTML_PATH.read_text(encoding="utf-8")

    escopo_camada_0 = re.search(r"\.camada-0\s*\{([^}]*)\}", css, re.DOTALL)
    assert escopo_camada_0 is not None, (
        "templates/base.html: nenhum seletor .camada-0 encontrado -- "
        "--accent precisa estar escopado a .camada-0, não em :root global"
    )
    assert "--accent" in escopo_camada_0.group(1), (
        "templates/base.html: seletor .camada-0 existe mas não declara "
        "--accent dentro dele"
    )

    root_bloco = re.search(r":root\s*\{([^}]*)\}", css, re.DOTALL)
    if root_bloco is not None:
        assert "--accent" not in root_bloco.group(1), (
            "templates/base.html: --accent ainda declarada em :root global "
            "-- deveria estar só em .camada-0"
        )

"""
tests/test_institution_identity.py

RED (ISSUE-40.6, STEP-02): comprova a ausência do sistema de microidentidade
institucional (`--inst-color`, `--inst-font-display`, `--inst-header-shape`)
descrito em `.ai/issues/ISSUE-40.6_SPEC.md`. Hoje nenhum template tem um
elemento `.institution .header`: documentos da mesma instituição fictícia
não compartilham cor/fonte/forma de header, e instituições diferentes não
produzem identidades visuais distintas -- porque a identidade simplesmente
não existe ainda.

Achado STEP-01 (`.ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md`): o helper
`generator.font_fidelity._montar_html` hardcoda
`_preparar_dados_documentais(template_nome, {})` (contexto vazio) e não
aceita dados de instituição -- não serve para este teste. Este módulo
replica o mesmo pipeline usado por `_montar_html`
(`_preparar_dados_documentais` -> `_injetar_css_documental` ->
`_injetar_classes_body` -> `_injetar_cabecalho_rodape_documental` ->
`renderizar_html`, todos de `generator/renderer.py`), mas injeta um
contexto de dados de instituição no lugar do dicionário vazio.

`INSTITUTION_TEST_DATA` é literal de `ISSUE-40.6_SPEC.md`, STEP-02.

`manual.html` e `cadastro.html` não existem em `templates/*.html` hoje
(confirmado no STEP-01) -- nascem no STEP-03 (GREEN). Até lá, todo teste que
depende deles falha por `FileNotFoundError` na leitura do template (RED por
ausência de arquivo, precedente aceito pela issue/spec, seção STEP-02:
"pode nascer RED por ausência de arquivo até o GREEN"). `06_log_acesso.html`
já existe e produz RED "de verdade": não tem `.institution .header`, e seu
carimbo de exportação é "EXPORTADO EM {{DATA_EXPORTACAO}} ÀS
{{HORA_EXPORTACAO}}" -- singular, sem segundos (dado real de exemplo usa
formato "HH:MM", ex. `examples/sinal_verde_demo_blueprint.json:621`,
`"10:10"`).
"""
from __future__ import annotations

import re
from typing import Any

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

# Dados de teste literais de ISSUE-40.6_SPEC.md (STEP-02).
INSTITUTION_TEST_DATA = {
    "museu_teste": {
        "inst_color": "#7a1f1f",
        "inst_font_display": "Libre Baskerville",
        "inst_header_shape": "diagonal",
        "templates": ["manual.html", "06_log_acesso.html", "cadastro.html"],
    },
    "empresa_teste": {
        "inst_color": "#1f4a7a",
        "inst_font_display": "DM Sans",
        "inst_header_shape": "reto",
        "templates": ["manual.html", "06_log_acesso.html", "cadastro.html"],
    },
}


def _dados_institucionais(inst: dict[str, Any]) -> dict[str, Any]:
    """Contexto de dados de uma instituição de teste: tokens de
    microidentidade (INST_*) + campos dos critérios de aceite #4 (revisão +
    assinatura no manual) e #5 (carimbo com segundos no log de acesso).

    `HORA_EXPORTACAO` usa formato realista sem segundos (ver
    `examples/sinal_verde_demo_blueprint.json:621`, `"10:10"`) -- de
    propósito, para que o teste do carimbo com segundos nasça RED de
    verdade contra o template atual, e não passe por acidente por já
    receber um valor com segundos. `HORA_COM_SEGUNDOS` é o dado que o
    STEP-03 deve efetivamente usar no carimbo novo.
    """
    return {
        "INST_COLOR": inst["inst_color"],
        "INST_FONT_DISPLAY": inst["inst_font_display"],
        "INST_HEADER_SHAPE": inst["inst_header_shape"],
        "INST_REVISAO": "Revisão 2",
        "INST_REVISAO_DATA": "06/08/2024",
        "ASSINATURA_RESPONSAVEL_NOME": "Responsável de Teste",
        "DATA_EXPORTACAO": "06/08/2024",
        "HORA_EXPORTACAO": "17:04",
        "HORA_COM_SEGUNDOS": "17:04:07",
    }


def _montar_html_institucional(template_nome: str, inst: dict[str, Any]) -> str:
    """Réplica de `generator.font_fidelity._montar_html`, injetando dados de
    instituição no contexto de renderização em vez do contexto vazio
    hardcoded (achado STEP-01)."""
    template_path = TEMPLATES_DIR / template_nome
    dados = _preparar_dados_documentais(template_nome, _dados_institucionais(inst))
    html_raw = template_path.read_text(encoding="utf-8")
    html_raw = _injetar_css_documental(html_raw)
    html_raw = _injetar_classes_body(html_raw, template_nome, dados)
    html_raw = _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
    return renderizar_html(html_raw, dados)


# Lê o elemento `.institution .header` esperado pelo esqueleto de CSS da
# spec (`styles/institution_identity.css` -> `templates/styles/
# institution_identity.css`, path confirmado no STEP-01) e reporta cor de
# fundo, fonte e "assinatura" de forma de header (clip-path para diagonal,
# largura de borda para faixa-dupla) resolvidos via `getComputedStyle` --
# não grep de string no HTML-fonte.
_INSTITUTION_HEADER_JS = """
() => {
  const header = document.querySelector('.institution .header');
  if (!header) return null;
  const cs = getComputedStyle(header);
  return {
    backgroundColor: cs.backgroundColor,
    fontFamily: cs.fontFamily,
    clipPath: cs.clipPath,
    borderTopWidth: cs.borderTopWidth,
    borderBottomWidth: cs.borderBottomWidth,
  };
}
"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


def _identidade_renderizada(
    browser: Any, template_nome: str, inst: dict[str, Any]
) -> dict[str, Any] | None:
    html = _montar_html_institucional(template_nome, inst)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        return page.evaluate(_INSTITUTION_HEADER_JS)
    finally:
        page.close()


def test_documents_of_same_institution_share_identity(browser):
    """Renderiza os 3 templates de `museu_teste` e falha se
    `.institution .header` não existir, ou se a cor/fonte/forma de header
    computada divergir entre os documentos da mesma instituição."""
    inst = INSTITUTION_TEST_DATA["museu_teste"]
    identidades: dict[str, Any] = {}
    for template_nome in inst["templates"]:
        identidade = _identidade_renderizada(browser, template_nome, inst)
        assert identidade is not None, (
            f"{template_nome}: elemento '.institution .header' ausente do "
            f"DOM -- microidentidade institucional não aplicada"
        )
        identidades[template_nome] = identidade

    primeiro_nome, primeira_identidade = next(iter(identidades.items()))
    for template_nome, identidade in identidades.items():
        assert identidade == primeira_identidade, (
            f"{template_nome}: identidade visual ({identidade}) diverge da "
            f"de {primeiro_nome} ({primeira_identidade}) -- documentos da "
            f"mesma instituição (museu_teste) não estão coesos"
        )


def test_documents_of_different_institutions_do_not_share_identity(browser):
    """Confirma que `museu_teste` e `empresa_teste` produzem identidades
    visuais distintas nos mesmos templates."""
    museu = INSTITUTION_TEST_DATA["museu_teste"]
    empresa = INSTITUTION_TEST_DATA["empresa_teste"]
    for template_nome in museu["templates"]:
        identidade_museu = _identidade_renderizada(browser, template_nome, museu)
        identidade_empresa = _identidade_renderizada(browser, template_nome, empresa)
        assert identidade_museu is not None, (
            f"{template_nome}: '.institution .header' ausente "
            f"(museu_teste)"
        )
        assert identidade_empresa is not None, (
            f"{template_nome}: '.institution .header' ausente "
            f"(empresa_teste)"
        )
        assert identidade_museu != identidade_empresa, (
            f"{template_nome}: museu_teste e empresa_teste produziram a "
            f"mesma identidade visual ({identidade_museu}) -- variação "
            f"inter-instituição ausente"
        )


_REVISAO_RE = re.compile(r"Revis[ãa]o\s+\d+\s*[—-]\s*\d{2}/\d{2}/\d{4}")


def test_manual_has_revision_and_signature(browser):
    """Falha se `manual.html` não tiver 'Revisão N — data' no header e
    assinatura do responsável (SVG, via `generator.signature_renderer`) no
    rodapé."""
    inst = INSTITUTION_TEST_DATA["museu_teste"]
    html = _montar_html_institucional("manual.html", inst)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        texto = page.evaluate("document.body.innerText")
        assert _REVISAO_RE.search(texto), (
            f"manual.html: header sem 'Revisão N — data' -- texto: "
            f"{texto!r}"
        )
        assinatura = page.query_selector(
            "svg.signature, .signature svg, .assinatura svg, "
            "[class*='assinatura'] svg"
        )
        assert assinatura is not None, (
            "manual.html: nenhum elemento de assinatura (svg) encontrado "
            "no rodapé -- assinatura do responsável ausente"
        )
    finally:
        page.close()


_EXPORT_STAMP_RE = re.compile(
    r"EXPORTADOS?\s+EM\s+\d{2}/\d{2}/\d{4}\s+ÀS\s+\d{2}:\d{2}:\d{2}"
)


def test_access_log_has_export_stamp_with_seconds(browser):
    """Falha se `06_log_acesso.html` não tiver carimbo de exportação com
    timestamp incluindo segundos (ex.: 'EXPORTADOS EM DD/MM/AAAA ÀS
    HH:MM:SS'). Hoje o carimbo é 'EXPORTADO EM {{DATA_EXPORTACAO}} ÀS
    {{HORA_EXPORTACAO}}' e `HORA_EXPORTACAO` de teste é "17:04" (sem
    segundos, formato realista de dado de exemplo) -- RED real."""
    inst = INSTITUTION_TEST_DATA["museu_teste"]
    html = _montar_html_institucional("06_log_acesso.html", inst)
    page = browser.new_page()
    try:
        page.set_content(html, wait_until="load")
        texto = page.evaluate("document.body.innerText")
        assert _EXPORT_STAMP_RE.search(texto), (
            f"06_log_acesso.html: carimbo de exportação com segundos "
            f"ausente -- texto: {texto!r}"
        )
    finally:
        page.close()

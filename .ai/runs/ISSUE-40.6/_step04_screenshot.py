"""Script auxiliar temporário para STEP-04 da ISSUE-40.6.

Renderiza manual.html, 06_log_acesso.html e cadastro.html para
museu_teste e empresa_teste (INSTITUTION_TEST_DATA de
tests/test_institution_identity.py) e captura screenshot de
.institution (ou .page se .institution não existir) de cada um,
lado a lado por instituicao, para verificacao visual manual.

Nao faz parte da suite; apagado ao final do step.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from playwright.sync_api import sync_playwright

from generator.renderer import (
    TEMPLATES_DIR,
    _injetar_cabecalho_rodape_documental,
    _injetar_classes_body,
    _injetar_css_documental,
    _preparar_dados_documentais,
    renderizar_html,
)

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


def _dados_institucionais(inst):
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


def _montar_html_institucional(template_nome, inst):
    template_path = TEMPLATES_DIR / template_nome
    dados = _preparar_dados_documentais(template_nome, _dados_institucionais(inst))
    html_raw = template_path.read_text(encoding="utf-8")
    html_raw = _injetar_css_documental(html_raw)
    html_raw = _injetar_classes_body(html_raw, template_nome, dados)
    html_raw = _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
    return renderizar_html(html_raw, dados)


OUT_DIR = Path(__file__).resolve().parent


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for inst_nome, inst in INSTITUTION_TEST_DATA.items():
            for template_nome in inst["templates"]:
                html = _montar_html_institucional(template_nome, inst)
                page = browser.new_page(viewport={"width": 900, "height": 1200})
                page.set_content(html, wait_until="load")
                elemento = page.query_selector(".institution") or page.query_selector(".page") or page.query_selector("body")
                out_name = f"{inst_nome}_{template_nome.replace('.html', '')}.png"
                elemento.screenshot(path=str(OUT_DIR / out_name))
                page.close()
                print(f"gerado: {out_name}")
        browser.close()


if __name__ == "__main__":
    main()

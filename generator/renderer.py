"""
renderer.py — Converte templates HTML em PDF via Playwright

Uso:
    from generator.renderer import renderizar_caso
    pdfs = renderizar_caso(blueprint, "output/caso_01")
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


# ─────────────────────────────────────────
# Injeção de dados no template
# ─────────────────────────────────────────

def injetar_dados(html: str, dados: dict[str, Any]) -> str:
    """
    Substitui {{VARIAVEL}} pelo valor correspondente em dados.
    Ignora chaves não encontradas (mantém o placeholder).
    """
    def substituir(match):
        chave = match.group(1).strip()
        return str(dados.get(chave, match.group(0)))

    return re.sub(r"\{\{(.+?)\}\}", substituir, html)


# ─────────────────────────────────────────
# Renderização de um documento
# ─────────────────────────────────────────

async def _renderizar_html_para_pdf(
    html: str,
    output_path: Path,
) -> Path:
    """Renderiza uma string HTML como PDF usando Playwright."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content(html, wait_until="networkidle")

        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "bottom": "15mm",
                "left": "15mm",
                "right": "15mm",
            },
        )

        await browser.close()

    return output_path


def renderizar_documento(
    template_nome: str,
    dados: dict[str, Any],
    output_path: Path,
) -> Path:
    """
    Carrega o template, injeta os dados e gera o PDF.

    Args:
        template_nome: nome do arquivo HTML em /templates (ex: "01_email.html")
        dados: dicionário com os valores dos placeholders {{VARIAVEL}}
        output_path: caminho de saída do PDF
    """
    template_path = TEMPLATES_DIR / template_nome
    if not template_path.exists():
        raise FileNotFoundError(f"Template não encontrado: {template_path}")

    html = template_path.read_text(encoding="utf-8")
    html_preenchido = injetar_dados(html, dados)

    return asyncio.run(
        _renderizar_html_para_pdf(html_preenchido, output_path)
    )


# ─────────────────────────────────────────
# Mapeamento tipo → template
# ─────────────────────────────────────────

TIPO_PARA_TEMPLATE = {
    "email_narrador":      "01_email.html",
    "email_institucional": "01_email.html",
    "chat":                "02_whatsapp.html",
    "log_acesso":          "06_log_acesso.html",
    "log_sistema":         "06_log_acesso.html",
    "boletim":             "04_boletim.html",
    "depoimento":          "04_boletim.html",
    "contrato":            "05_carta.html",
    "carta":               "05_carta.html",
    "recibo":              "07_recibo.html",
    "orcamento":           "08_orcamento.html",
    "extrato":             "09_extrato.html",
    "protocolo":           "05_carta.html",
    "glossario":           "05_carta.html",
    "folha_cruzamento":    "05_carta.html",
    "outro":               "05_carta.html",
}


# ─────────────────────────────────────────
# Renderização de um caso completo
# ─────────────────────────────────────────

def renderizar_caso(
    blueprint_path: Path,
    output_dir: Path | None = None,
) -> dict[str, list[Path]]:
    """
    Lê um blueprint validado e renderiza todos os documentos.
    Agrupa os PDFs por envelope.

    Retorna:
        {
          "E1": [path_doc1, path_doc2, ...],
          "E2": [...],
          "dicas": [...],
          "gabarito": [...],
        }
    """
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    titulo_slug = blueprint["titulo"].lower().replace(" ", "_")

    if output_dir is None:
        output_dir = OUTPUT_DIR / titulo_slug

    output_dir.mkdir(parents=True, exist_ok=True)

    grupos: dict[str, list[Path]] = {
        "E1": [], "E2": [], "E3": [], "dicas": [], "gabarito": []
    }

    for doc in blueprint.get("documentos", []):
        codigo = doc["codigo"]
        tipo = doc.get("tipo", "outro")
        envelope = doc.get("envelope", "E1")
        template = TIPO_PARA_TEMPLATE.get(tipo, "05_carta.html")

        conteudo = doc.get("conteudo", {})

        if not conteudo:
            print(f"  ⚠️  {codigo} — campo 'conteudo' vazio, PDF não gerado")
            continue

        dados = {
            "TITULO_DOCUMENTO": doc.get("titulo", codigo),
            "CODIGO_DOCUMENTO": codigo,
            "NOME_CASO": blueprint["titulo"],
            "ENVELOPE": envelope,
            **conteudo,
        }

        pdf_path = output_dir / f"{codigo}.pdf"
        try:
            caminho = renderizar_documento(template, dados, pdf_path)
            grupos[envelope].append(caminho)
            print(f"  ✅ {codigo} → {caminho.name}")
        except Exception as e:
            print(f"  ❌ {codigo} — erro: {e}")

    dicas_por_envelope = sorted(
        {dica.get("envelope") for dica in blueprint.get("dicas", []) if dica.get("envelope")}
    )
    for envelope_dica in dicas_por_envelope:
        dados_capa = {
            "NOME_CASO": blueprint["titulo"],
            "ENVELOPE": envelope_dica,
            "case_name": blueprint["titulo"],
            "section_label": "DICAS",
            "section_ref": "Material de apoio ao facilitador",
            "warning_label": "ABRIR SOMENTE QUANDO NECESSÁRIO",
        }
        pdf_path = output_dir / f"DICAS-{envelope_dica}-00_CAPA.pdf"
        try:
            caminho = renderizar_documento("00_envelope_capa.html", dados_capa, pdf_path)
            grupos["dicas"].append(caminho)
            print(f"  ✅ DICAS-{envelope_dica}-CAPA → {caminho.name}")
        except Exception as e:
            print(f"  ❌ DICAS-{envelope_dica}-CAPA — erro: {e}")

    return grupos



# ─────────────────────────────────────────
# CLI básico
# ─────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python renderer.py <blueprint.json> [pasta_output]")
        sys.exit(1)

    bp_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"\n📄 Renderizando: {bp_path.name}\n")
    resultado = renderizar_caso(bp_path, out_dir)

    print("\n📦 Arquivos gerados:")
    for envelope, arquivos in resultado.items():
        if arquivos:
            print(f"\n  {envelope}:")
            for a in arquivos:
                print(f"    {a}")

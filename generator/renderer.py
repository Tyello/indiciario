"""
renderer.py — Converte templates HTML em PDF via Playwright.

Motor de injeção suporta:
- {{VARIAVEL}} → substitui pelo valor escalar
- {{#LISTA}}...{{/LISTA}} → itera lista de dicts, repete o bloco por item
- {{#BOOL}}...{{/BOOL}} → renderiza bloco somente se valor for truthy
- {{^BOOL}}...{{/BOOL}} → renderiza bloco somente se valor for falsy (seção inversa)

Interface pública (ver AGENTS.md):
    renderizar_documento(template_nome, dados, output_path) -> Path
    renderizar_caso(blueprint_path, output_dir) -> dict[str, list[Path]]
"""

from __future__ import annotations

import asyncio
import importlib
import os
import json
import re
import warnings
from pathlib import Path
from typing import Any


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR    = Path(__file__).parent.parent / "output"


# ──────────────────────────────────────────────────────────────────────────────
# Motor de template (Mustache-lite)
# ──────────────────────────────────────────────────────────────────────────────

def _injetar_escalares(html: str, dados: dict[str, Any]) -> str:
    """Substitui {{VARIAVEL}} simples por valor escalar."""
    def sub(match: re.Match) -> str:
        chave = match.group(1).strip()
        valor = dados.get(chave, match.group(0))
        # Listas e dicts não são injetados como escalares — deixa o placeholder
        if isinstance(valor, (list, dict)):
            return match.group(0)
        return str(valor) if valor is not None else ""
    return re.sub(r"\{\{([^#/\^].*?)\}\}", sub, html)


def _processar_secao(bloco: str, dados: dict[str, Any]) -> str:
    """Processa um bloco de seção (lista ou bool) recursivamente."""
    return renderizar_html(bloco, dados)


def renderizar_html(template: str, dados: dict[str, Any]) -> str:
    """
    Processa o template HTML completo com suporte a seções e escalares.

    Ordem:
      1. Seções de lista  {{#CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é list
      2. Seções booleanas {{#CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é truthy
      3. Seções inversas  {{^CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é falsy
      4. Escalares simples {{CHAVE}}
    """
    # Padrão: captura nome da seção e conteúdo (não-greedy, DOTALL)
    SECAO_RE = re.compile(r"\{\{([#\^])(\w+)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)

    def processar_match(m: re.Match) -> str:
        tipo_secao = m.group(1)   # '#' ou '^'
        chave      = m.group(2)
        conteudo   = m.group(3)
        valor      = dados.get(chave)

        if tipo_secao == "#":
            if isinstance(valor, list):
                # Itera: renderiza o bloco para cada item da lista
                partes = []
                for item in valor:
                    contexto = {**dados, **item} if isinstance(item, dict) else {**dados, "ITEM": item}
                    partes.append(renderizar_html(conteudo, contexto))
                return "".join(partes)
            elif valor:
                # Bool truthy: renderiza uma vez com o contexto atual
                return renderizar_html(conteudo, dados)
            else:
                return ""
        else:  # '^' — seção inversa
            if not valor:
                return renderizar_html(conteudo, dados)
            return ""

    # Processa seções de dentro para fora (re.sub com DOTALL)
    resultado = SECAO_RE.sub(processar_match, template)
    # Por fim, substitui escalares simples
    resultado = _injetar_escalares(resultado, dados)
    return resultado


def injetar_dados(html: str, dados: dict[str, Any]) -> str:
    """API de compatibilidade — delega para renderizar_html."""
    return renderizar_html(html, dados)


# ──────────────────────────────────────────────────────────────────────────────
# Verificação de placeholders residuais
# ──────────────────────────────────────────────────────────────────────────────

PLACEHOLDER_RE = re.compile(r"\{\{\s*[#\^/]?\s*[^{}]+?\s*\}\}")
LIXO_TECNICO_RE = re.compile(
    r"\bNone\b|(?i:\b(undefined|CONTEUDO_GENERICO)\b|placeholder|lorem\s+ipsum)",
)


class PlaceholderResidualError(RuntimeError):
    """Erro lançado quando o HTML final ainda contém placeholders/lixo técnico."""


class RenderCaseError(RuntimeError):
    """Erro lançado quando a renderização strict de um caso falha."""


def detectar_placeholders(html: str) -> list[str]:
    """Retorna lista de placeholders Mustache não substituídos no HTML final."""
    return PLACEHOLDER_RE.findall(html)


def detectar_residuos_tecnicos(html: str) -> list[str]:
    """Detecta placeholders residuais e termos técnicos proibidos no HTML final."""
    residuos = detectar_placeholders(html)
    residuos.extend(match.group(0) for match in LIXO_TECNICO_RE.finditer(html))
    return residuos


# ──────────────────────────────────────────────────────────────────────────────
# Renderização HTML → PDF
# ──────────────────────────────────────────────────────────────────────────────

def _playwright_disponivel() -> bool:
    try:
        return importlib.util.find_spec("playwright") is not None
    except ValueError:
        return False


def _fake_pdf_permitido() -> bool:
    return os.getenv("INDICIARIO_ALLOW_FAKE_PDF") == "1"


def _gerar_pdf_fake_para_teste(output_path: Path, landscape: bool = False) -> Path:
    backend_name = "generator.pdf_backend" if __package__ else "pdf_backend"
    PdfWriter = importlib.import_module(backend_name).PdfWriter

    width, height = (842, 595) if landscape else (595, 842)
    writer = PdfWriter()
    writer.add_blank_page(width=width, height=height)
    with output_path.open("wb") as fp:
        writer.write(fp)
    return output_path


async def _html_para_pdf(html: str, output_path: Path, landscape: bool = False) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not _playwright_disponivel():
        if _fake_pdf_permitido():
            return _gerar_pdf_fake_para_teste(output_path, landscape=landscape)
        raise RuntimeError(
            "Playwright não está instalado. Rode: "
            "pip install -r requirements.txt && python -m playwright install chromium"
        )

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            landscape=landscape,
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
        )
        await browser.close()
    return output_path


def renderizar_documento(
    template_nome: str,
    dados: dict[str, Any],
    output_path: Path,
    strict: bool = False,
    landscape: bool = False,
) -> Path:
    template_path = TEMPLATES_DIR / template_nome
    if not template_path.exists():
        raise FileNotFoundError(f"Template não encontrado: {template_path}")

    html_raw      = template_path.read_text(encoding="utf-8")
    html_final    = renderizar_html(html_raw, dados)

    residuais = detectar_residuos_tecnicos(html_final)
    if residuais:
        unicos = sorted(set(residuais))
        mensagem = (
            f"{output_path.name} — {len(unicos)} resíduo(s) técnico(s): "
            f"{', '.join(unicos[:5])}{'...' if len(unicos) > 5 else ''}"
        )
        if strict:
            raise PlaceholderResidualError(mensagem)
        warnings.warn(mensagem, RuntimeWarning, stacklevel=2)

    return asyncio.run(_html_para_pdf(html_final, output_path, landscape=landscape))


# ──────────────────────────────────────────────────────────────────────────────
# Mapeamento tipo → template
# ──────────────────────────────────────────────────────────────────────────────

TIPO_PARA_TEMPLATE: dict[str, str] = {
    "email_narrador":      "01_email.html",
    "email_institucional": "01_email.html",
    "chat":                "02_whatsapp.html",
    "log_acesso":          "06_log_acesso.html",
    "log_sistema":         "06_log_acesso.html",
    "escala":              "06_log_acesso.html",
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
    "manual":              "05_carta.html",
    "outro":               "05_carta.html",
}


# ──────────────────────────────────────────────────────────────────────────────
# Renderização de caso completo
# ──────────────────────────────────────────────────────────────────────────────

def renderizar_caso(
    blueprint_path: Path,
    output_dir: Path | None = None,
    strict: bool = True,
) -> dict[str, list[Path]]:
    """
    Lê um blueprint validado e renderiza todos os documentos.
    Agrupa os PDFs por envelope.
    """
    blueprint  = json.loads(blueprint_path.read_text(encoding="utf-8"))
    titulo_slug = re.sub(r"[^\w]", "_", blueprint["titulo"].lower())

    if output_dir is None:
        output_dir = OUTPUT_DIR / titulo_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    grupos: dict[str, list[Path]] = {
        "E1": [], "E2": [], "E3": [], "dicas": [], "gabarito": [],
    }

    for doc in blueprint.get("documentos", []):
        codigo   = doc["codigo"]
        tipo     = doc.get("tipo", "outro")
        envelope = doc.get("envelope", "E1")
        template = TIPO_PARA_TEMPLATE.get(tipo, "05_carta.html")
        conteudo = doc.get("conteudo", {})

        if not conteudo:
            mensagem = f"{codigo} ({template}) — 'conteudo' vazio, PDF ignorado"
            if strict:
                raise RenderCaseError(mensagem)
            print(f"  ⚠️  {mensagem}")
            continue

        dados = {
            "TITULO_DOCUMENTO": doc.get("titulo", codigo),
            "CODIGO_DOCUMENTO": codigo,
            "NOME_CASO":        blueprint["titulo"],
            "ENVELOPE":         envelope,
            **conteudo,
        }

        pdf_path = output_dir / f"{codigo}.pdf"
        try:
            caminho = renderizar_documento(template, dados, pdf_path, strict=strict)
            grupos[envelope].append(caminho)
            print(f"  ✅ {codigo} → {caminho.name}")
        except Exception as exc:
            mensagem = f"{codigo} ({template}) — falha ao renderizar: {exc}"
            if strict:
                raise RenderCaseError(mensagem) from exc
            print(f"  ❌ {mensagem}")

    # Capa de dicas por envelope
    for envelope_dica in sorted(
        {d.get("envelope") for d in blueprint.get("dicas", []) if d.get("envelope")}
    ):
        dados_capa = {
            "NOME_CASO":     blueprint["titulo"],
            "ENVELOPE":      envelope_dica,
            "case_name":     blueprint["titulo"],
            "section_label": "DICAS",
            "section_ref":   "Material de apoio ao facilitador",
            "warning_label": "ABRIR SOMENTE QUANDO NECESSÁRIO",
        }
        pdf_path = output_dir / f"DICAS-{envelope_dica}-00_CAPA.pdf"
        try:
            caminho = renderizar_documento("00_envelope_capa.html", dados_capa, pdf_path, strict=strict)
            grupos["dicas"].append(caminho)
            print(f"  ✅ DICAS-{envelope_dica}-CAPA → {caminho.name}")
        except Exception as exc:
            mensagem = f"DICAS-{envelope_dica}-CAPA (00_envelope_capa.html) — falha ao renderizar: {exc}"
            if strict:
                raise RenderCaseError(mensagem) from exc
            print(f"  ❌ {mensagem}")

    return grupos


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python renderer.py <blueprint.json> [pasta_output]")
        sys.exit(1)

    bp_path  = Path(sys.argv[1])
    out_dir  = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    print(f"\n📄 Renderizando: {bp_path.name}\n")
    resultado = renderizar_caso(bp_path, out_dir)
    print("\n📦 Arquivos gerados:")
    for env, arqs in resultado.items():
        if arqs:
            print(f"\n  {env}:")
            for a in arqs:
                print(f"    {a}")

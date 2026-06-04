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
import json
import logging
import os
import re
import unicodedata
import warnings
from html import escape
from pathlib import Path
from typing import Any

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
SIGNATURES_DIR = ASSETS_DIR / "signatures"

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Assinaturas visuais
# ──────────────────────────────────────────────────────────────────────────────

ASSINATURA_KEYS = (
    "ASSINATURA_CURSIVA",
    "ASSINATURA_RESPONSAVEL",
    "ASSINATURA_GLIFO",
    "ASSINATURA_PRESTADOR",
    "ASSINATURA_CONTRATANTE",
    "ASSINATURA_CLIENTE",
    "ASSINATURA_TESTADOR",
    "ASSINATURA_ADVOGADO",
    "ASSINATURA_TESTEMUNHA",
    "ASSINATURA_RASCUNHO",
)


def _perfil_assinatura(chave: str) -> str:
    """Classifica o uso visual da assinatura para variar gesto e composição."""
    if chave in {"ASSINATURA_GLIFO", "ASSINATURA_TESTEMUNHA", "ASSINATURA_RASCUNHO"}:
        return "rubrica_curta"
    if chave in {
        "ASSINATURA_RESPONSAVEL",
        "ASSINATURA_PRESTADOR",
        "ASSINATURA_CLIENTE",
    }:
        return "assinatura_comercial"
    if chave in {"ASSINATURA_CONTRATANTE", "ASSINATURA_ADVOGADO"}:
        return "assinatura_administrativa"
    return "assinatura_formal"


def _slug_assinatura(texto: str) -> str:
    """Normaliza nome de personagem para pasta de asset de assinatura."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(
        char for char in normalizado if not unicodedata.combining(char)
    )
    slug = re.sub(r"[^a-z0-9]+", "_", sem_acentos.lower()).strip("_")
    return slug or "sem_nome"


def _asset_assinatura_svg(texto: str, perfil: str) -> str | None:
    """Carrega assinatura/rubrica individual quando houver asset do personagem."""
    tipo_asset = "rubrica.svg" if perfil == "rubrica_curta" else "assinatura.svg"
    asset_path = SIGNATURES_DIR / _slug_assinatura(texto) / tipo_asset
    if not asset_path.is_file():
        return None
    return asset_path.read_text(encoding="utf-8")


def _assinatura_svg(texto: str, perfil: str = "assinatura_formal") -> str:
    """Gera assinatura SVG fina e determinística com perfis visuais distintos."""
    nome = " ".join(str(texto).split())
    if not nome or nome == "—":
        return ""

    seed = sum((index + 1) * ord(char) for index, char in enumerate(nome + perfil))
    partes_nome = nome.replace(".", " ").split()
    iniciais = "".join(parte[0] for parte in partes_nome[:3]).upper()
    primeiro = partes_nome[0] if partes_nome else nome
    ultimo = partes_nome[-1] if len(partes_nome) > 1 else ""
    cor = "#1d2733"

    if perfil == "rubrica_curta":
        largura, altura, base_y = 150, 42, 28
        texto_principal = iniciais[:3]
        tamanho = 20 + seed % 3
        caminhos = [
            f"M10 {base_y + seed % 3} C 28 {base_y - 15}, 42 {base_y + 12}, 58 {base_y - 2} S 86 {base_y - 16}, 104 {base_y - 1}",
            f"M36 {base_y + 8} C 58 {base_y + 16}, 86 {base_y + 7}, 132 {base_y + 10}",
            f"M112 {base_y - 2} l18 {-6 + seed % 5} m-7 {-2} l10 {9 - seed % 4}",
        ]
    elif perfil == "assinatura_comercial":
        largura, altura, base_y = 245, 58, 38
        texto_principal = f"{primeiro[0]}. {ultimo}" if ultimo else primeiro
        tamanho = 21 + seed % 4
        caminhos = [
            f"M8 {base_y - 4} C 42 {base_y - 24}, 64 {base_y + 12}, 91 {base_y - 8} S 145 {base_y - 24}, 178 {base_y - 4} S 216 {base_y + 8}, 234 {base_y - 8}",
            f"M22 {base_y + 8} C 62 {base_y + 17}, 123 {base_y + 8}, 224 {base_y + 11}",
            f"M184 {base_y - 18} C 196 {base_y - 1}, 207 {base_y - 1}, 218 {base_y - 18}",
        ]
    elif perfil == "assinatura_administrativa":
        largura, altura, base_y = 225, 52, 34
        texto_principal = iniciais if seed % 2 else nome
        tamanho = 18 + seed % 3
        caminhos = [
            f"M12 {base_y - 7} C 47 {base_y - 11}, 68 {base_y + 8}, 102 {base_y - 4} S 158 {base_y - 16}, 210 {base_y - 7}",
            f"M18 {base_y + 7} L 206 {base_y + 7 + seed % 3}",
            f"M32 {base_y - 18} C 44 {base_y + 0}, 55 {base_y + 0}, 66 {base_y - 18}",
        ]
    else:
        largura, altura, base_y = 255, 62, 40
        texto_principal = nome
        tamanho = 22 + seed % 5
        caminhos = [
            f"M10 {base_y - 3} C 45 {base_y - 30}, 73 {base_y + 16}, 104 {base_y - 8} S 157 {base_y - 26}, 190 {base_y - 6} S 226 {base_y + 8}, 242 {base_y - 10}",
            f"M20 {base_y + 9} C 62 {base_y + 19}, 128 {base_y + 5}, 238 {base_y + 12}",
            f"M72 {base_y - 24} C 83 {base_y - 2}, 96 {base_y - 1}, 106 {base_y - 23} M184 {base_y - 21} c10 18 22 18 32 0",
        ]

    rotacao = -6 + seed % 13
    escala_y = 0.92 + (seed % 9) / 100
    paths = []
    for index, caminho in enumerate(caminhos):
        stroke = 1.45 if index == 0 else 0.9 if index == 1 else 1.05
        opacity = 0.78 if index == 0 else 0.42 if index == 1 else 0.62
        paths.append(
            f'<path d="{caminho}" fill="none" stroke="{cor}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>'
        )

    return "".join(
        [
            f'<svg class="signature-svg signature-{perfil}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
            f'aria-label="assinatura manuscrita {perfil.replace("_", " ")}" role="img">',
            f'<g transform="rotate({rotacao} {largura / 2:g} {altura / 2:g}) scale(1 {escala_y:.2f})">',
            *paths,
            f'<text x="{14 + seed % 11}" y="{base_y - 3}" font-family="Segoe Script, Lucida Handwriting, Brush Script MT, cursive" '
            f'font-size="{tamanho}" fill="{cor}" opacity="0.56">{escape(texto_principal)}</text>',
            "</g></svg>",
        ]
    )


def preparar_assinaturas_visuais(dados: dict[str, Any]) -> dict[str, Any]:
    """Acrescenta campos *_VISUAL para templates que exigem assinatura real."""
    enriquecidos = dict(dados)
    for chave in ASSINATURA_KEYS:
        valor = enriquecidos.get(chave)
        if isinstance(valor, str) and valor.strip():
            perfil = _perfil_assinatura(chave)
            enriquecidos[f"{chave}_VISUAL"] = _asset_assinatura_svg(
                valor, perfil
            ) or _assinatura_svg(valor, perfil=perfil)
    return enriquecidos


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
    dados = preparar_assinaturas_visuais(dados)

    # Padrão: captura nome da seção e conteúdo (não-greedy, DOTALL)
    SECAO_RE = re.compile(r"\{\{([#\^])(\w+)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)

    def processar_match(m: re.Match) -> str:
        tipo_secao = m.group(1)  # '#' ou '^'
        chave = m.group(2)
        conteudo = m.group(3)
        valor = dados.get(chave)

        if tipo_secao == "#":
            if isinstance(valor, list):
                # Itera: renderiza o bloco para cada item da lista
                partes = []
                for item in valor:
                    contexto = (
                        {**dados, **item}
                        if isinstance(item, dict)
                        else {**dados, "ITEM": item}
                    )
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
    if _fake_pdf_permitido():
        return _gerar_pdf_fake_para_teste(output_path, landscape=landscape)
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
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            landscape=landscape,
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
    strict: bool = False,
    landscape: bool = False,
    html_debug_path: Path | None = None,
) -> Path:
    template_path = TEMPLATES_DIR / template_nome
    if not template_path.exists():
        raise FileNotFoundError(f"Template não encontrado: {template_path}")

    html_raw = template_path.read_text(encoding="utf-8")
    html_final = renderizar_html(html_raw, dados)

    if html_debug_path is not None:
        html_debug_path.parent.mkdir(parents=True, exist_ok=True)
        html_debug_path.write_text(html_final, encoding="utf-8")

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

LANDSCAPE_TEMPLATES: set[str] = {"06_log_acesso.html"}


def template_usa_landscape(template_nome: str) -> bool:
    """Indica se um template deve ser renderizado em A4 landscape."""
    return template_nome in LANDSCAPE_TEMPLATES


TIPO_PARA_TEMPLATE: dict[str, str] = {
    "email_narrador": "01_email.html",
    "email_institucional": "01_email.html",
    "chat": "02_whatsapp.html",
    "log_acesso": "06_log_acesso.html",
    "log_sistema": "06_log_acesso.html",
    "escala": "06_log_acesso.html",
    "boletim": "04_boletim.html",
    "depoimento": "04_boletim.html",
    "contrato": "05_carta.html",
    "carta": "05_carta.html",
    "recibo": "07_recibo.html",
    "orcamento": "08_orcamento.html",
    "extrato": "09_extrato.html",
    "protocolo": "05_carta.html",
    "glossario": "05_carta.html",
    "folha_cruzamento": "05_carta.html",
    "manual": "05_carta.html",
    "outro": "05_carta.html",
}


# ──────────────────────────────────────────────────────────────────────────────
# Dicas do facilitador
# ──────────────────────────────────────────────────────────────────────────────


def _fase_sort_key(fase: str) -> tuple[int, str]:
    match = re.fullmatch(r"E(\d+)", fase)
    if match:
        return (int(match.group(1)), "")
    if fase == "final":
        return (10_000, fase)
    return (9_000, fase)


def _normalizar_lista_texto(valor: object) -> str:
    if isinstance(valor, list):
        return ", ".join(str(item) for item in valor) or "—"
    if valor:
        return str(valor)
    return "—"


def _fase_para_envelope(fase: str, envelopes_disponiveis: list[str]) -> str:
    if re.fullmatch(r"E\d+", fase):
        return fase
    if envelopes_disponiveis:
        return envelopes_disponiveis[-1]
    return "E1"


def _dicas_contextuais_por_envelope(
    blueprint: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    dicas_contextuais = blueprint.get("dicas_contextuais") or []
    fases_envelope = sorted(
        {
            str(dica.get("fase"))
            for dica in dicas_contextuais
            if re.fullmatch(r"E\d+", str(dica.get("fase")))
        },
        key=_fase_sort_key,
    )
    resultado: dict[str, list[dict[str, Any]]] = {}
    for dica in dicas_contextuais:
        fase = str(dica.get("fase", "E1"))
        envelope = _fase_para_envelope(fase, fases_envelope)
        resultado.setdefault(envelope, []).append(
            {
                "id": str(dica.get("id") or ""),
                "categoria": str(dica.get("categoria") or "geral"),
                "titulo": str(
                    dica.get("titulo") or dica.get("id") or "Dica contextual"
                ),
                "nivel": str(dica.get("nivel") or "—"),
                "condicao_uso": str(
                    dica.get("condicao_uso")
                    or "Usar quando o grupo estiver travado neste ponto."
                ),
                "texto": str(dica.get("texto") or ""),
                "documentos_relacionados": _normalizar_lista_texto(
                    dica.get("documentos_relacionados")
                ),
                "contratos_relacionados": _normalizar_lista_texto(
                    dica.get("contratos_relacionados")
                ),
                "o_que_desbloqueia": "",
                "HAS_DESBLOQUEIO": False,
            }
        )
    return resultado


def _dicas_legadas_por_envelope(
    blueprint: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    resultado: dict[str, list[dict[str, Any]]] = {}
    for dica in blueprint.get("dicas", []) or []:
        envelope = str(dica.get("envelope") or "E1")
        numero = dica.get("numero")
        o_que_desbloqueia = str(dica.get("o_que_desbloqueia") or "")
        resultado.setdefault(envelope, []).append(
            {
                "id": (
                    f"DICA-{envelope}-{numero}"
                    if numero is not None
                    else f"DICA-{envelope}"
                ),
                "categoria": "geral",
                "titulo": (
                    f"Dica {numero}" if numero is not None else "Dica operacional"
                ),
                "nivel": str(dica.get("intensidade") or dica.get("nivel") or "—"),
                "condicao_uso": str(
                    dica.get("condicao_uso")
                    or "Usar quando o grupo estiver travado neste envelope."
                ),
                "texto": str(dica.get("texto") or ""),
                "documentos_relacionados": "—",
                "contratos_relacionados": "—",
                "o_que_desbloqueia": o_que_desbloqueia,
                "HAS_DESBLOQUEIO": bool(o_que_desbloqueia),
            }
        )
    return resultado


def _dicas_por_envelope(blueprint: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Retorna dicas operacionais por envelope, priorizando dicas_contextuais."""
    contextuais = _dicas_contextuais_por_envelope(blueprint)
    return contextuais or _dicas_legadas_por_envelope(blueprint)


def _contextos_dicas(dicas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    agrupadas: dict[str, list[dict[str, Any]]] = {}
    for dica in dicas:
        agrupadas.setdefault(dica["categoria"], []).append(dica)
    return [
        {
            "categoria": categoria,
            "dicas": sorted(itens, key=lambda item: item.get("id", "")),
        }
        for categoria, itens in sorted(agrupadas.items())
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Renderização de caso completo
# ──────────────────────────────────────────────────────────────────────────────


def renderizar_caso(
    blueprint_path: Path,
    output_dir: Path | None = None,
    strict: bool = True,
    html_debug_dir: Path | None = None,
) -> dict[str, list[Path]]:
    """
    Lê um blueprint validado e renderiza todos os documentos.
    Agrupa os PDFs por envelope.
    """
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    titulo_slug = re.sub(r"[^\w]", "_", blueprint["titulo"].lower())

    if output_dir is None:
        output_dir = OUTPUT_DIR / titulo_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    grupos: dict[str, list[Path]] = {"dicas": [], "gabarito": []}

    for doc in blueprint.get("documentos", []):
        codigo = doc["codigo"]
        tipo = doc.get("tipo", "outro")
        envelope = doc.get("envelope", "E1")
        template = TIPO_PARA_TEMPLATE.get(tipo, "05_carta.html")
        conteudo = doc.get("conteudo", {})

        if not conteudo:
            mensagem = f"{codigo} ({template}) — 'conteudo' vazio, PDF ignorado"
            if strict:
                raise RenderCaseError(mensagem)
            logger.warning("%s", mensagem)
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
            render_kwargs: dict[str, Any] = {"strict": strict}
            if template_usa_landscape(template):
                render_kwargs["landscape"] = True
            if html_debug_dir is not None:
                render_kwargs["html_debug_path"] = html_debug_dir / f"{codigo}.html"
            caminho = renderizar_documento(template, dados, pdf_path, **render_kwargs)
            grupos.setdefault(envelope, []).append(caminho)
            logger.info("Documento renderizado: %s → %s", codigo, caminho.name)
        except Exception as exc:
            mensagem = f"{codigo} ({template}) — falha ao renderizar: {exc}"
            if strict:
                raise RenderCaseError(mensagem) from exc
            logger.error("%s", mensagem)

    # Capa e conteúdo operacional de dicas por envelope
    for envelope_dica, dicas in sorted(
        _dicas_por_envelope(blueprint).items(), key=lambda item: _fase_sort_key(item[0])
    ):
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
            render_kwargs: dict[str, Any] = {"strict": strict}
            if html_debug_dir is not None:
                render_kwargs["html_debug_path"] = (
                    html_debug_dir / f"DICAS-{envelope_dica}-00_CAPA.html"
                )
            caminho = renderizar_documento(
                "00_envelope_capa.html", dados_capa, pdf_path, **render_kwargs
            )
            grupos["dicas"].append(caminho)
            logger.info(
                "Capa de dicas renderizada: DICAS-%s-CAPA → %s",
                envelope_dica,
                caminho.name,
            )
        except Exception as exc:
            mensagem = f"DICAS-{envelope_dica}-CAPA (00_envelope_capa.html) — falha ao renderizar: {exc}"
            if strict:
                raise RenderCaseError(mensagem) from exc
            logger.error("%s", mensagem)

        dados_dicas = {
            "NOME_CASO": blueprint["titulo"],
            "ENVELOPE": envelope_dica,
            "CONTEXTOS": _contextos_dicas(dicas),
        }
        pdf_path = output_dir / f"DICAS-{envelope_dica}-01_CONTEUDO.pdf"
        try:
            render_kwargs = {"strict": strict}
            if html_debug_dir is not None:
                render_kwargs["html_debug_path"] = (
                    html_debug_dir / f"DICAS-{envelope_dica}-01_CONTEUDO.html"
                )
            caminho = renderizar_documento(
                "dicas_contextuais.html", dados_dicas, pdf_path, **render_kwargs
            )
            grupos["dicas"].append(caminho)
            logger.info(
                "Conteúdo de dicas renderizado: DICAS-%s-CONTEUDO → %s",
                envelope_dica,
                caminho.name,
            )
        except Exception as exc:
            mensagem = f"DICAS-{envelope_dica}-CONTEUDO (dicas_contextuais.html) — falha ao renderizar: {exc}"
            if strict:
                raise RenderCaseError(mensagem) from exc
            logger.error("%s", mensagem)

    return grupos


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

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
    for env, arqs in resultado.items():
        if arqs:
            print(f"\n  {env}:")
            for a in arqs:
                print(f"    {a}")

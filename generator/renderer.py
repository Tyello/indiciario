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
import base64
import importlib
import json
import logging
import os
import re
import unicodedata
import warnings
from pathlib import Path
from typing import Any

try:
    from .signature_renderer import build_handwritten_note_svg, build_signature_svg
except ImportError:  # Execução direta em scripts legados.
    from signature_renderer import build_handwritten_note_svg, build_signature_svg  # type: ignore[no-redef]

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
SIGNATURES_DIR = ASSETS_DIR / "signatures"
DOCUMENT_SYSTEM_CSS_PATH = TEMPLATES_DIR / "styles" / "document_system.css"
FONTS_DIR = ASSETS_DIR / "fonts"


logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Sistema visual documental v1
# ──────────────────────────────────────────────────────────────────────────────

DOCUMENT_PLAYER_TEMPLATES = {
    "01_email.html",
    "02_whatsapp.html",
    "04_boletim.html",
    "05_carta.html",
    "06_log_acesso.html",
    "07_recibo.html",
    "08_orcamento.html",
    "09_extrato.html",
}

TEMPLATE_DOCUMENT_CLASS = {
    "01_email.html": "email",
    "02_whatsapp.html": "chat",
    "04_boletim.html": "depoimento",
    "05_carta.html": "carta",
    "06_log_acesso.html": "log_sistema",
    "07_recibo.html": "recibo",
    "08_orcamento.html": "orcamento",
    "09_extrato.html": "extrato",
    "facilitator_guide.html": "facilitator",
    "dicas_contextuais.html": "facilitator",
    "print_guide.html": "facilitator",
}

# Sistema de Camadas (ISSUE-40.3): Camada 1 (tela, prints de app — sombra/
# radius/gradiente são vocabulário correto) vs. Camada 2 (papel, documento
# impresso — não projeta sombra de si mesmo, sem cantos arredondados, sem
# gradiente). Injetado via `_injetar_classes_body` (mesmo mecanismo de
# `doc-type-*`/`doc-family-*`), não por edição manual do `<body>` de cada
# template — o motor de render não é Jinja2 com herança, é substituição por
# string sobre cada `.html` standalone (achado do STEP-01).
TEMPLATE_LAYER_SCREEN = {
    "01_email.html",
    "02_whatsapp.html",
    "02_whatsapp2.html",
    "03_twitter.html",
}

TEMPLATE_LAYER_PAPER = {
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
}

DOCUMENT_TYPE_FAMILIES = {
    "email_narrador": "email",
    "email_institucional": "email",
    "email": "email",
    "chat": "chat",
    "log_acesso": "log",
    "log_sistema": "log",
    "escala": "log",
    "boletim": "admin",
    "depoimento": "admin",
    "contrato": "commercial",
    "orcamento": "commercial",
    "recibo": "commercial",
    "extrato": "finance",
    "carta": "letter",
    "protocolo": "letter",
    "glossario": "letter",
    "folha_cruzamento": "letter",
    "manual": "letter",
    "outro": "letter",
    "facilitator": "facilitator",
}


_FONTFACE_URL_RE = re.compile(r"url\('\.\./\.\./assets/fonts/([^']+\.woff2)'\)")


def _inline_fontface_urls(css: str) -> str:
    """Substitui os `url('../../assets/fonts/X.woff2')` do CSS por data URIs
    base64 embutidos, lendo os arquivos reais em `assets/fonts/`.

    `page.set_content()` do Playwright (usado pelo renderer e pelos testes de
    fonte) não define uma base URL `file://` para a página — um caminho
    relativo/absoluto de disco no `@font-face` simplesmente não carregaria.
    Embutir como data URI garante fonte local, sem depender de base URL nem
    de rede, e sem exigir servir os assets via HTTP."""

    def sub(match: re.Match) -> str:
        nome_arquivo = match.group(1)
        font_path = FONTS_DIR / nome_arquivo
        if not font_path.is_file():
            logger.warning("Fonte vendorizada não encontrada: %s", font_path)
            return match.group(0)
        dados_b64 = base64.b64encode(font_path.read_bytes()).decode("ascii")
        return f"url('data:font/woff2;base64,{dados_b64}')"

    return _FONTFACE_URL_RE.sub(sub, css)


def _document_system_css() -> str:
    if not DOCUMENT_SYSTEM_CSS_PATH.is_file():
        return ""
    css = DOCUMENT_SYSTEM_CSS_PATH.read_text(encoding="utf-8")
    css = _inline_fontface_urls(css)
    return f"\n<style data-indiciario-visual-system>\n{css}\n</style>\n"


def _injetar_css_documental(html: str) -> str:
    css = _document_system_css()
    if css and "</head>" in html:
        html = html.replace("</head>", f"{css}</head>", 1)
    return html


def _classe_tipo_documental(template_nome: str, dados: dict[str, Any]) -> str:
    tipo = str(dados.get("TIPO_DOCUMENTAL_SLUG") or "").strip()
    if not tipo:
        tipo = TEMPLATE_DOCUMENT_CLASS.get(template_nome, "documento")
    tipo = re.sub(r"[^a-z0-9_-]+", "_", tipo.lower()).strip("_") or "documento"
    return tipo


def _familia_visual_documental(template_nome: str, tipo: str) -> str:
    familia = DOCUMENT_TYPE_FAMILIES.get(tipo)
    if not familia:
        familia = DOCUMENT_TYPE_FAMILIES.get(
            TEMPLATE_DOCUMENT_CLASS.get(template_nome, "")
        )
    return familia or "document"


def _injetar_classes_body(html: str, template_nome: str, dados: dict[str, Any]) -> str:
    tipo = _classe_tipo_documental(template_nome, dados)
    familia = _familia_visual_documental(template_nome, tipo)
    classes = ["doc-system", f"doc-type-{tipo}", f"doc-family-{familia}"]
    if template_nome in DOCUMENT_PLAYER_TEMPLATES:
        classes.append("doc-player")
    if familia == "facilitator":
        classes.append("facilitator-doc")
    if template_nome in TEMPLATE_LAYER_SCREEN:
        classes.append("layer-screen")
    elif template_nome in TEMPLATE_LAYER_PAPER:
        classes.append("layer-paper")

    def sub(match: re.Match) -> str:
        attrs = match.group(1) or ""
        class_match = re.search(r'class=["\']([^"\']*)["\']', attrs)
        if class_match:
            existentes = class_match.group(1).split()
            combinadas = " ".join(dict.fromkeys([*existentes, *classes]))
            attrs_novo = (
                attrs[: class_match.start(1)]
                + combinadas
                + attrs[class_match.end(1) :]
            )
        else:
            attrs_novo = f'{attrs} class="{" ".join(classes)}"'
        return f"<body{attrs_novo}>"

    return re.sub(r"<body([^>]*)>", sub, html, count=1, flags=re.IGNORECASE)


def _injetar_cabecalho_rodape_documental(
    html: str, template_nome: str, dados: dict[str, Any]
) -> str:
    # Documentos diegéticos do jogador não exibem códigos, envelope, paginação
    # ou controle técnico. A rastreabilidade permanece em manifests, guia e
    # HTML de debug gerado fora da área visível.
    if template_nome in DOCUMENT_PLAYER_TEMPLATES:
        return html
    return html


def _primeiro_campo_documental(
    dados: dict[str, Any], *campos: str, padrao: str
) -> str:
    for campo in campos:
        valor = dados.get(campo)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
        if valor is not None and not isinstance(valor, (list, dict)):
            texto = str(valor).strip()
            if texto:
                return texto
    return padrao


def _preparar_dados_documentais(
    template_nome: str, dados: dict[str, Any]
) -> dict[str, Any]:
    preparados = dict(dados)
    tipo_slug = _classe_tipo_documental(template_nome, preparados)
    tipo_label = str(
        preparados.get("TIPO_DOCUMENTO")
        or preparados.get("TIPO_DOCUMENTAL_LABEL")
        or tipo_slug.replace("_", " ").title()
    )
    preparados.setdefault("TIPO_DOCUMENTAL_SLUG", tipo_slug)
    preparados.setdefault("DOC_TIPO_LABEL", tipo_label)
    preparados.setdefault(
        "DOC_EMISSOR",
        _primeiro_campo_documental(
            preparados,
            "EMISSOR",
            "REMETENTE_NOME",
            "NOME_ORGANIZACAO",
            "ORGAO_EMISSOR",
            "ÓRGÃO_EMISSOR",
            "NOME_EMPRESA",
            "NOME_SISTEMA",
            "NOME_BANCO",
            "INSTITUICAO",
            "NOME_INSTITUICAO",
            "SETOR",
            "DEPARTAMENTO",
            padrao="Arquivo documental",
        ),
    )
    preparados.setdefault("DOC_REFERENCIA", preparados.get("DATA") or preparados.get("DATA_HORA") or preparados.get("PERIODO") or preparados.get("DATA_EMISSAO") or "Referência interna")
    preparados.setdefault("DOC_STATUS", preparados.get("STATUS_DOCUMENTAL") or "registro")
    preparados.setdefault("DOC_CONTROLE", preparados.get("CONTROLE_DOCUMENTAL") or "controle de dossiê")
    preparados.setdefault("DOC_STAMP_LABEL", preparados.get("CARIMBO_DOCUMENTAL") or "")
    preparados.setdefault("CODIGO_DOCUMENTO", preparados.get("CODIGO_DOCUMENTO") or "DOC-S/C")
    preparados.setdefault("NOME_CASO", preparados.get("NOME_CASO") or "Indiciário")
    preparados.setdefault("ENVELOPE", preparados.get("ENVELOPE") or "Envelope")
    return preparados


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

RUBRICA_KEYS = {"ASSINATURA_GLIFO", "ASSINATURA_RASCUNHO"}
ASSINATURA_CURTA_OU_RUBRICA_KEYS = {"ASSINATURA_TESTEMUNHA"}
MANUSCRITO_KEYS = ("ANOTACAO", "NOTA_MANUSCRITA")
REPO_ROOT = Path(__file__).resolve().parents[1]


def _valor_enum(valor: Any, padrao: str) -> str:
    if valor is None:
        return padrao
    return str(getattr(valor, "value", valor))


def _personagem_get(personagem: Any, campo: str, padrao: Any = None) -> Any:
    if isinstance(personagem, dict):
        return personagem.get(campo, padrao)
    return getattr(personagem, campo, padrao)


def _perfil_get(perfil: Any, campo: str, padrao: Any = None) -> Any:
    if perfil is None:
        return padrao
    if isinstance(perfil, dict):
        return perfil.get(campo, padrao)
    return getattr(perfil, campo, padrao)


def _perfil_assinatura(chave: str) -> str:
    """Classifica o uso visual legado da assinatura para fallback compatível."""
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


def _tipo_uso_assinatura(chave: str, perfil: Any = None) -> str:
    """Diferencia assinatura completa de rubrica/visto por chave e perfil."""
    if chave in RUBRICA_KEYS:
        return "rubrica"
    estilo = _valor_enum(_perfil_get(perfil, "estilo"), "")
    rubrica_estilo = _valor_enum(_perfil_get(perfil, "rubrica_estilo"), "")
    if chave in ASSINATURA_CURTA_OU_RUBRICA_KEYS and (
        estilo == "rubrica" or rubrica_estilo in {"seca", "monograma"}
    ):
        return "rubrica"
    return "assinatura"


def _slug_assinatura(texto: str) -> str:
    """Normaliza nome de personagem para pasta de asset de assinatura."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(
        char for char in normalizado if not unicodedata.combining(char)
    )
    slug = re.sub(r"[^a-z0-9]+", "_", sem_acentos.lower()).strip("_")
    return slug or "sem_nome"


def _asset_assinatura_svg(texto: str, perfil: str) -> str | None:
    """Carrega asset legado por slug quando houver assinatura/rubrica individual."""
    tipo_asset = "rubrica.svg" if perfil == "rubrica_curta" else "assinatura.svg"
    asset_path = SIGNATURES_DIR / _slug_assinatura(texto) / tipo_asset
    if not asset_path.is_file():
        return None
    return asset_path.read_text(encoding="utf-8")


def _override_assinatura_svg(perfil: Any, tipo_uso: str, repo_root: Path = REPO_ROOT) -> str | None:
    campos = (
        ("override_rubrica_svg", "rubrica_svg_override")
        if tipo_uso == "rubrica"
        else ("override_assinatura_svg", "assinatura_svg_override")
    )
    for campo in campos:
        caminho = _perfil_get(perfil, campo)
        if not isinstance(caminho, str) or not caminho.strip():
            continue
        asset_path = repo_root / caminho
        if asset_path.is_file():
            return asset_path.read_text(encoding="utf-8")
        logger.warning("Override de assinatura não encontrado em %s: %s", campo, caminho)
    return None


def _resolver_personagem_assinatura(
    chave: str,
    valor: str,
    dados: dict[str, Any],
    personagens: list[Any] | None,
) -> Any | None:
    """Resolve documento → personagem por ID explícito e depois por nome exato."""
    if not personagens:
        return None
    por_id = {str(_personagem_get(p, "id")): p for p in personagens}
    id_explicito = dados.get(f"{chave}_PERSONAGEM_ID") or dados.get("PERSONAGEM_ID")
    if id_explicito is not None and str(id_explicito) in por_id:
        return por_id[str(id_explicito)]

    valor_normalizado = " ".join(valor.split()).casefold()
    for personagem in personagens:
        nome = _personagem_get(personagem, "nome")
        if isinstance(nome, str) and " ".join(nome.split()).casefold() == valor_normalizado:
            return personagem
    return None


def _texto_principal_assinatura(nome: str, tipo_uso: str, estilo: str, legibilidade: str) -> str:
    partes_nome = nome.replace(".", " ").split()
    iniciais = "".join(parte[0] for parte in partes_nome[:3]).upper()
    primeiro = partes_nome[0] if partes_nome else nome
    ultimo = partes_nome[-1] if len(partes_nome) > 1 else ""
    if tipo_uso == "rubrica":
        return iniciais[:3]
    if legibilidade == "baixa" or estilo in {"curta", "rubrica"}:
        return f"{primeiro[0]}. {ultimo}" if ultimo else primeiro[:3]
    if estilo in {"administrativa", "comercial"} and ultimo:
        return f"{primeiro[0]}. {ultimo}"
    return nome


def _assinatura_svg_por_perfil(nome: str, perfil: Any, tipo_uso: str) -> str:
    """Gera assinatura/rubrica P3 por perfil editorial, sem fontes externas."""
    personagem = {"id": _perfil_get(perfil, "seed", _slug_assinatura(nome)), "nome": nome, "assinatura": perfil}
    return build_signature_svg(personagem, modo=tipo_uso)

def _assinatura_svg(texto: str, perfil: str = "assinatura_formal") -> str:
    """Fallback procedural compatível, agora roteado para o gerador P3."""
    nome = str(texto or "").strip()
    if not nome or nome == "—":
        return ""
    modo = "rubrica" if perfil == "rubrica_curta" else "assinatura"
    estilo = {
        "rubrica_curta": "minimalista",
        "assinatura_comercial": "fluida",
        "assinatura_administrativa": "formal",
        "assinatura_formal": "formal",
    }.get(perfil, "formal")
    personagem = {
        "id": _slug_assinatura(nome),
        "nome": nome,
        "assinatura": {"estilo": estilo, "seed": f"legacy:{perfil}:{nome}"},
    }
    return build_signature_svg(personagem, modo=modo)

def preparar_assinaturas_visuais(
    dados: dict[str, Any],
    personagens: list[Any] | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Acrescenta campos *_VISUAL para templates que exigem assinatura real."""
    enriquecidos = dict(dados)
    for chave in ASSINATURA_KEYS:
        valor = enriquecidos.get(chave)
        if not isinstance(valor, str) or not valor.strip():
            continue

        personagem = _resolver_personagem_assinatura(chave, valor, enriquecidos, personagens)
        perfil_personagem = (
            _personagem_get(personagem, "assinatura_visual")
            or _personagem_get(personagem, "assinatura")
            if personagem
            else None
        )
        tipo_uso = _tipo_uso_assinatura(chave, perfil_personagem)

        if perfil_personagem is not None:
            override = _override_assinatura_svg(perfil_personagem, tipo_uso, repo_root=repo_root)
            if override is not None:
                enriquecidos[f"{chave}_VISUAL"] = override
                continue
            enriquecidos[f"{chave}_VISUAL"] = _assinatura_svg_por_perfil(
                _personagem_get(personagem, "nome", valor), perfil_personagem, tipo_uso
            )
            continue

        perfil_legado = _perfil_assinatura(chave)
        enriquecidos[f"{chave}_VISUAL"] = _asset_assinatura_svg(
            valor, perfil_legado
        ) or _assinatura_svg(valor, perfil=perfil_legado)
    return enriquecidos


def preparar_manuscritos_visuais(
    dados: dict[str, Any],
    personagens: list[Any] | None = None,
) -> dict[str, Any]:
    """Acrescenta campos *_VISUAL para anotações manuscritas curtas."""
    enriquecidos = dict(dados)
    for chave in MANUSCRITO_KEYS:
        valor = enriquecidos.get(chave)
        if not isinstance(valor, str) or not valor.strip():
            continue
        personagem = _resolver_personagem_assinatura(chave, valor, enriquecidos, personagens)
        if personagem is None:
            personagem = {"id": f"manuscrito-{chave.lower()}", "nome": str(enriquecidos.get("NOME_ASSINANTE") or enriquecidos.get("NOME_RESPONSAVEL") or valor[:24] or chave)}
        enriquecidos[f"{chave}_VISUAL"] = build_handwritten_note_svg(valor, personagem, largura_maxima=360)
    return enriquecidos


# ──────────────────────────────────────────────────────────────────────────────
# Motor de template (Mustache-lite)
# ──────────────────────────────────────────────────────────────────────────────



def _normalizar_horario_visual(valor: Any) -> Any:
    """Padroniza horários HHhmm em escalares renderizados para HH:mm."""
    if not isinstance(valor, str):
        return valor

    def sub(match: re.Match) -> str:
        hora = int(match.group(1))
        minuto = match.group(2)
        segundo = match.group(3)
        if hora > 23 or int(minuto) > 59:
            return match.group(0)
        if segundo is not None and int(segundo) > 59:
            return match.group(0)
        return f"{hora:02d}:{minuto}" + (f":{segundo}" if segundo is not None else "")

    return re.sub(r"(?<![\w:])(\d{1,2})h(\d{2})(?::(\d{2}))?(?![\w:])", sub, valor)


def _injetar_escalares(html: str, dados: dict[str, Any]) -> str:
    """Substitui {{VARIAVEL}} simples por valor escalar."""

    def sub(match: re.Match) -> str:
        chave = match.group(1).strip()
        valor = dados.get(chave, match.group(0))
        # Listas e dicts não são injetados como escalares — deixa o placeholder
        if isinstance(valor, (list, dict)):
            return match.group(0)
        valor = _normalizar_horario_visual(valor)
        return str(valor) if valor is not None else ""

    return re.sub(r"\{\{([^#/\^].*?)\}\}", sub, html)


def _processar_secao(
    bloco: str, dados: dict[str, Any], personagens: list[Any] | None = None
) -> str:
    """Processa um bloco de seção (lista ou bool) recursivamente."""
    return renderizar_html(bloco, dados, personagens=personagens)


def renderizar_html(
    template: str, dados: dict[str, Any], personagens: list[Any] | None = None
) -> str:
    """
    Processa o template HTML completo com suporte a seções e escalares.

    Ordem:
      1. Seções de lista  {{#CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é list
      2. Seções booleanas {{#CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é truthy
      3. Seções inversas  {{^CHAVE}}...{{/CHAVE}} onde dados[CHAVE] é falsy
      4. Escalares simples {{CHAVE}}
    """
    dados = preparar_assinaturas_visuais(dados, personagens=personagens)
    dados = preparar_manuscritos_visuais(dados, personagens=personagens)

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
                    partes.append(renderizar_html(conteudo, contexto, personagens=personagens))
                return "".join(partes)
            elif valor:
                # Bool truthy: renderiza uma vez com o contexto atual
                return renderizar_html(conteudo, dados, personagens=personagens)
            else:
                return ""
        else:  # '^' — seção inversa
            if not valor:
                return renderizar_html(conteudo, dados, personagens=personagens)
            return ""

    # Processa seções de dentro para fora (re.sub com DOTALL)
    resultado = SECAO_RE.sub(processar_match, template)
    # Por fim, substitui escalares simples
    resultado = _injetar_escalares(resultado, dados)
    return resultado


def injetar_dados(
    html: str, dados: dict[str, Any], personagens: list[Any] | None = None
) -> str:
    """API de compatibilidade — delega para renderizar_html."""
    return renderizar_html(html, dados, personagens=personagens)


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
        # Garante que as fontes vendorizadas (@font-face local, ISSUE-40.1)
        # terminaram de carregar/decodificar antes do screenshot/PDF —
        # sem isso, o Chromium pode capturar um frame ainda em fallback.
        await page.evaluate("document.fonts.ready")
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
    personagens: list[Any] | None = None,
) -> Path:
    template_path = TEMPLATES_DIR / template_nome
    if not template_path.exists():
        raise FileNotFoundError(f"Template não encontrado: {template_path}")

    dados = _preparar_dados_documentais(template_nome, dados)
    personagens_contexto = personagens or dados.get("__PERSONAGENS_ASSINATURA")
    html_raw = template_path.read_text(encoding="utf-8")
    html_raw = _injetar_css_documental(html_raw)
    html_raw = _injetar_classes_body(html_raw, template_nome, dados)
    html_raw = _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
    html_final = renderizar_html(html_raw, dados, personagens=personagens_contexto)

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

LANDSCAPE_TEMPLATES: set[str] = {"06_log_acesso.html", "09_extrato.html"}
LANDSCAPE_DOCUMENT_TYPES: set[str] = {"folha_cruzamento"}


def template_usa_landscape(template_nome: str) -> bool:
    """Indica se um template deve ser renderizado em A4 landscape."""
    return template_nome in LANDSCAPE_TEMPLATES


def documento_usa_landscape(
    template_nome: str, tipo: str, conteudo: dict[str, Any]
) -> bool:
    """Decide orientação A4 landscape para registros tabulares de jogador."""
    if template_usa_landscape(template_nome) or tipo in LANDSCAPE_DOCUMENT_TYPES:
        return True
    corpo_carta = str(conteudo.get("CORPO_CARTA") or "").lower()
    return tipo == "manual" and "<table" in corpo_carta


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
            "TIPO_DOCUMENTAL_SLUG": tipo,
            "TIPO_DOCUMENTAL_LABEL": tipo.replace("_", " ").title(),
            **conteudo,
        }

        pdf_path = output_dir / f"{codigo}.pdf"
        try:
            render_kwargs: dict[str, Any] = {"strict": strict}
            if documento_usa_landscape(template, tipo, conteudo):
                render_kwargs["landscape"] = True
            if html_debug_dir is not None:
                render_kwargs["html_debug_path"] = html_debug_dir / f"{codigo}.html"
            dados["__PERSONAGENS_ASSINATURA"] = blueprint.get("personagens", [])
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

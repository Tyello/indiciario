"""
tests/test_renderer_engine.py — Testes do motor de template Mustache-lite

Cobre:
- substituição de escalares
- loop de lista
- condicional booleana truthy/falsy
- seção inversa ^
- placeholders residuais detectados
- renderização aninhada (lista dentro de condicional)
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.renderer import renderizar_html, detectar_placeholders


# ── Escalares ─────────────────────────────────────────────────────────────────

def test_escalar_simples():
    assert renderizar_html("Olá {{NOME}}!", {"NOME": "Mundo"}) == "Olá Mundo!"


def test_escalar_ausente_mantem_placeholder():
    result = renderizar_html("{{FALTOU}}", {})
    assert "{{FALTOU}}" in result


def test_escalar_none_vira_string_vazia():
    result = renderizar_html("{{VAZIO}}", {"VAZIO": None})
    assert result == ""


# ── Loops de lista ────────────────────────────────────────────────────────────

def test_loop_lista_dois_itens():
    tmpl = "{{#ITENS}}<li>{{NOME}}</li>{{/ITENS}}"
    dados = {"ITENS": [{"NOME": "A"}, {"NOME": "B"}]}
    result = renderizar_html(tmpl, dados)
    assert "<li>A</li>" in result
    assert "<li>B</li>" in result


def test_loop_lista_vazia_sem_saida():
    tmpl = "X{{#ITENS}}<li>{{NOME}}</li>{{/ITENS}}Y"
    result = renderizar_html(tmpl, {"ITENS": []})
    assert result == "XY"


def test_loop_herda_contexto_pai():
    tmpl = "{{#ITENS}}{{NOME}}-{{CASO}}|{{/ITENS}}"
    dados = {"CASO": "Teste", "ITENS": [{"NOME": "A"}, {"NOME": "B"}]}
    result = renderizar_html(tmpl, dados)
    assert result == "A-Teste|B-Teste|"


# ── Condicionais booleanas ────────────────────────────────────────────────────

def test_condicional_truthy_renderiza():
    tmpl = "{{#MOSTRAR}}visível{{/MOSTRAR}}"
    assert renderizar_html(tmpl, {"MOSTRAR": True}) == "visível"


def test_condicional_falsy_oculta():
    tmpl = "{{#MOSTRAR}}visível{{/MOSTRAR}}"
    assert renderizar_html(tmpl, {"MOSTRAR": False}) == ""


def test_condicional_ausente_oculta():
    tmpl = "{{#MOSTRAR}}visível{{/MOSTRAR}}"
    assert renderizar_html(tmpl, {}) == ""


def test_condicional_string_vazia_oculta():
    tmpl = "{{#NOTA}}{{NOTA}}{{/NOTA}}"
    assert renderizar_html(tmpl, {"NOTA": ""}) == ""


# ── Seção inversa ^ ───────────────────────────────────────────────────────────

def test_secao_inversa_renderiza_quando_falso():
    tmpl = "{{^ANEXOS}}sem anexos{{/ANEXOS}}"
    assert renderizar_html(tmpl, {"ANEXOS": False}) == "sem anexos"


def test_secao_inversa_oculta_quando_verdadeiro():
    tmpl = "{{^ANEXOS}}sem anexos{{/ANEXOS}}"
    assert renderizar_html(tmpl, {"ANEXOS": True}) == ""


# ── Renderização aninhada ─────────────────────────────────────────────────────

def test_loop_dentro_de_condicional():
    tmpl = "{{#MOSTRAR}}{{#ITENS}}[{{X}}]{{/ITENS}}{{/MOSTRAR}}"
    dados = {"MOSTRAR": True, "ITENS": [{"X": "1"}, {"X": "2"}]}
    assert renderizar_html(tmpl, dados) == "[1][2]"


def test_condicional_dentro_de_loop():
    tmpl = "{{#ROWS}}{{#DESTAQUE}}*{{/DESTAQUE}}{{VAL}}|{{/ROWS}}"
    dados = {"ROWS": [
        {"VAL": "A", "DESTAQUE": True},
        {"VAL": "B", "DESTAQUE": False},
    ]}
    assert renderizar_html(tmpl, dados) == "*A|B|"


# ── Detecção de placeholders ──────────────────────────────────────────────────

def test_detectar_placeholder_simples():
    html = "<p>{{NAO_PREENCHIDO}}</p>"
    result = detectar_placeholders(html)
    assert "{{NAO_PREENCHIDO}}" in result


def test_sem_placeholder_retorna_vazio():
    html = "<p>Tudo preenchido.</p>"
    assert detectar_placeholders(html) == []


def test_placeholder_residual_apos_renderizacao():
    tmpl = "{{PRESENTE}} {{AUSENTE}}"
    html = renderizar_html(tmpl, {"PRESENTE": "ok"})
    residuais = detectar_placeholders(html)
    assert "{{AUSENTE}}" in residuais
    assert "{{PRESENTE}}" not in residuais


# ── Templates reais — smoke tests ─────────────────────────────────────────────

def test_email_template_sem_residuais_com_dados_completos():
    tmpl_path = Path(__file__).parent.parent / "templates" / "01_email.html"
    if not tmpl_path.exists():
        return  # skip se template não disponível

    html = tmpl_path.read_text(encoding="utf-8")
    dados = {
        "REMETENTE_NOME": "João Silva",
        "REMETENTE_EMAIL": "joao@ficticio.com",
        "DESTINATARIO_EMAIL": "detetive@indiciarios.com",
        "DESTINATARIO_LABEL": "Investigação",
        "DATA_HORA": "01 de março de 2026 às 17:05",
        "ASSUNTO": "Urgente",
        "AVATAR_INICIAL": "J",
        "AVATAR_COR": "#1A2E4A",
        "CORPO_EMAIL": "<p>Texto.</p>",
        "NOTA_RODAPE": "CONFIDENCIAL",
        "COPIA": "arquivo@indiciarios.com",
        "TOTAL_ANEXOS": "2",
        "ANEXOS": True,
        "CADA_ANEXO": [
            {"NOME_ARQUIVO": "log.pdf", "TAMANHO_KB": "88"},
            {"NOME_ARQUIVO": "mapa.pdf", "TAMANHO_KB": "120"},
        ],
    }
    result = renderizar_html(html, dados)
    residuais = detectar_placeholders(result)
    assert residuais == [], f"Placeholders residuais: {residuais}"


def test_email_canonico_e1_02_renderiza_sem_copia_residual():
    root = Path(__file__).parent.parent
    template = (root / "templates" / "01_email.html").read_text(encoding="utf-8")
    blueprint_path = root / "examples" / "caso_canonico_intermediario.json"
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    doc = next(
        documento for documento in blueprint["documentos"]
        if documento["codigo"] == "E1-02"
    )

    html = renderizar_html(template, doc["conteudo"])
    residuais = detectar_placeholders(html)

    assert "{{COPIA}}" not in residuais
    assert residuais == [], f"Placeholders residuais em E1-02: {residuais}"
    assert "coord.reservas@acervomirante.local" in html


def test_log_template_expande_multiplos_registros():
    tmpl_path = Path(__file__).parent.parent / "templates" / "06_log_acesso.html"
    if not tmpl_path.exists():
        return

    html = tmpl_path.read_text(encoding="utf-8")
    registros = [
        {"CLASSE_LINHA": "", "DATA": "01/03/2026", "HORA": "09:58",
         "PORTA": "1A", "ID_USUARIO": "27", "NOME_USUARIO": "João",
         "TIPO_EVENTO": "in", "EVENTO": "ENTRADA",
         "TERMINAL": "", "METODO": "", "OBSERVACAO": ""},
        {"CLASSE_LINHA": "anomaly", "DATA": "01/03/2026", "HORA": "15:22",
         "PORTA": "4A", "ID_USUARIO": "09", "NOME_USUARIO": "Maria",
         "TIPO_EVENTO": "in", "EVENTO": "ENTRADA",
         "TERMINAL": "", "METODO": "", "OBSERVACAO": "sem saída"},
    ]
    dados = {
        "NOME_SISTEMA": "CONTROLE DE ACESSOS",
        "SUBTITULO_SISTEMA": "Exportação auditada",
        "COR_SISTEMA": "#1A2E4A", "COR_SISTEMA_DARK": "#0d1a2e",
        "DATA_EXPORTACAO": "01/03/2026", "HORA_EXPORTACAO": "17:04",
        "OPERADOR_EXPORT": "SISTEMA", "HASH_REGISTRO": "abc123",
        "PERIODO_INICIO": "01/03/2026 09:00", "PERIODO_FIM": "01/03/2026 17:04",
        "LOCALIZACAO_SISTEMA": "Sala N3",
        "TOTAL_REGISTROS": "2", "TOTAL_USUARIOS": "2",
        "TOTAL_ENTRADAS": "2", "TOTAL_NEGADOS": "0", "TOTAL_ANOMALIAS": "1",
        "COLUNA_NOME": True, "COLUNA_TERMINAL": False,
        "COLUNA_METODO": False, "COLUNA_OBS": True,
        "REGISTROS": registros,
    }
    result = renderizar_html(html, dados)
    # Ambos os registros devem aparecer
    assert "João" in result
    assert "Maria" in result
    assert result.count("ENTRADA") >= 2


def test_detectar_residuos_tecnicos_inclui_secoes_e_lixo():
    from generator.renderer import detectar_residuos_tecnicos

    html = "{{CAMPO}} {{#SECAO}}x{{/SECAO}} None undefined CONTEUDO_GENERICO lorem ipsum"
    residuos = detectar_residuos_tecnicos(html)
    assert "{{CAMPO}}" in residuos
    assert "{{#SECAO}}" in residuos
    assert "{{/SECAO}}" in residuos
    assert "CONTEUDO_GENERICO" in residuos


def test_renderizacao_strict_falha_com_placeholder_residual(tmp_path, monkeypatch):
    from generator import renderer

    template = tmp_path / "template.html"
    template.write_text("Olá {{NOME}} {{FALTA}}", encoding="utf-8")
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", tmp_path)

    def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    try:
        renderer.renderizar_documento("template.html", {"NOME": "Mundo"}, tmp_path / "out.pdf", strict=True)
    except renderer.PlaceholderResidualError:
        pass
    else:
        raise AssertionError("strict deveria bloquear placeholder residual")


def test_renderizacao_non_strict_alerta_sem_lancar(tmp_path, monkeypatch):
    from generator import renderer

    template = tmp_path / "template.html"
    template.write_text("Olá {{NOME}} {{FALTA}}", encoding="utf-8")
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", tmp_path)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    with pytest.warns(RuntimeWarning):
        renderer.renderizar_documento("template.html", {"NOME": "Mundo"}, tmp_path / "out.pdf", strict=False)


def test_template_com_secao_condicional_omitida_nao_deixa_placeholder():
    html = renderizar_html("A{{#MOSTRA}} {{CAMPO}}{{/MOSTRA}}B", {"MOSTRA": False})
    assert detectar_placeholders(html) == []

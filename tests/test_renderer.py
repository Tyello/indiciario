import json
import sys
import types

import pytest
from pathlib import Path


def _import_renderer_module():
    fake_async_api = types.SimpleNamespace(async_playwright=None)
    fake_playwright = types.SimpleNamespace(async_api=fake_async_api)
    sys.modules.setdefault("playwright", fake_playwright)
    sys.modules.setdefault("playwright.async_api", fake_async_api)
    from generator import renderer

    return renderer


def _blueprint_base(tmp_path: Path) -> Path:
    payload = {
        "titulo": "Caso da Biblioteca",
        "documentos": [
            {
                "codigo": "E1-01",
                "tipo": "carta",
                "envelope": "E1",
                "conteudo": {"CORPO": "texto"},
            }
        ],
        "dicas": [],
    }
    path = tmp_path / "blueprint.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_renderizar_caso_gera_capa_por_envelope_de_dicas(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    blueprint_path = _blueprint_base(tmp_path)
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    blueprint["dicas"] = [
        {"envelope": "E1", "texto": "d1"},
        {"envelope": "E1", "texto": "d2"},
        {"envelope": "E2", "texto": "d3"},
    ]
    blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")

    chamadas = []

    def fake_render(template_nome, dados, output_path, strict=False):
        chamadas.append((template_nome, dados, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("pdf", encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "renderizar_documento", fake_render)

    grupos = renderer.renderizar_caso(blueprint_path, tmp_path / "out")

    capas = [c for c in chamadas if c[0] == "00_envelope_capa.html"]
    assert len(capas) == 2
    assert [c[1]["section_label"] for c in capas] == ["DICAS", "DICAS"]
    assert all(c[1]["section_ref"] == "Material de apoio ao facilitador" for c in capas)
    assert all("envelope_number" not in c[1] for c in capas)
    assert len(grupos["dicas"]) == 4


def test_renderizar_caso_gera_tres_capas_com_envelope_3(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    blueprint_path = _blueprint_base(tmp_path)
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    blueprint["dicas"] = [
        {"envelope": "E1", "texto": "d1"},
        {"envelope": "E2", "texto": "d2"},
        {"envelope": "E3", "texto": "d3"},
    ]
    blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")

    chamadas = []

    def fake_render(template_nome, dados, output_path, strict=False):
        chamadas.append((template_nome, dados, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("pdf", encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "renderizar_documento", fake_render)

    renderer.renderizar_caso(blueprint_path, tmp_path / "out")

    capas = [c for c in chamadas if c[0] == "00_envelope_capa.html"]
    assert len(capas) == 3
    assert [c[1]["section_label"] for c in capas] == ["DICAS", "DICAS", "DICAS"]
    assert all(c[1]["section_ref"] == "Material de apoio ao facilitador" for c in capas)
    assert all("envelope_number" not in c[1] for c in capas)


def test_renderizar_caso_gera_conteudo_real_de_dicas_contextuais(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "Documento {{CODIGO_DOCUMENTO}} {{CORPO}}", encoding="utf-8"
    )
    (template_dir / "00_envelope_capa.html").write_text(
        "Capa {{section_label}} {{ENVELOPE}}", encoding="utf-8"
    )
    (template_dir / "dicas_contextuais.html").write_text(
        "{{NOME_CASO}} {{ENVELOPE}} {{#CONTEXTOS}}Contexto {{categoria}} {{#dicas}}{{titulo}} {{nivel}} {{condicao_uso}} {{texto}} {{documentos_relacionados}} {{contratos_relacionados}}{{/dicas}}{{/CONTEXTOS}}",
        encoding="utf-8",
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    blueprint_path = _blueprint_base(tmp_path)
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    blueprint["dicas"] = [{"envelope": "E1", "numero": 1, "texto": "Dica antiga"}]
    blueprint["dicas_contextuais"] = [
        {
            "id": "DC-E1-MAPA-01",
            "categoria": "mapa",
            "fase": "E1",
            "titulo": "Começar pela área bloqueada",
            "condicao_uso": "Use após leitura do protocolo.",
            "texto": "Separar documentos que mencionam reserva técnica B ou doca lateral.",
            "nivel": "leve",
            "contratos_relacionados": ["C-E1-ABERTURA"],
            "documentos_relacionados": ["E1-01", "E1-07"],
        },
        {
            "id": "DC-FINAL-SOL-01",
            "categoria": "solucao",
            "fase": "final",
            "titulo": "Fechamento da cadeia completa",
            "condicao_uso": "Use ao final.",
            "texto": "Peça que citem um documento operacional e um financeiro.",
            "nivel": "quase_gabarito",
            "contratos_relacionados": ["C-FINAL-SOLUCAO"],
            "documentos_relacionados": ["E2-06"],
        },
    ]
    blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")

    grupos = renderer.renderizar_caso(
        blueprint_path,
        tmp_path / "out",
        strict=True,
        html_debug_dir=tmp_path / "html_debug",
    )

    assert len(grupos["dicas"]) == 2
    conteudo = (tmp_path / "html_debug" / "DICAS-E1-01_CONTEUDO.html").read_text(
        encoding="utf-8"
    )
    assert "Começar pela área bloqueada" in conteudo
    assert (
        "Separar documentos que mencionam reserva técnica B ou doca lateral" in conteudo
    )
    assert "C-E1-ABERTURA" in conteudo
    assert "Dica antiga" not in conteudo
    assert "Fechamento da cadeia completa" in conteudo


def test_caso_canonico_dicas_contextuais_aparecem_no_html_debug(tmp_path, monkeypatch):
    renderer = _import_renderer_module()

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)

    grupos = renderer.renderizar_caso(
        Path("examples/caso_canonico_iniciante.json"),
        tmp_path / "out",
        strict=True,
        html_debug_dir=tmp_path / "html_debug",
    )

    assert len(grupos["dicas"]) > 2
    e1 = (tmp_path / "html_debug" / "DICAS-E1-01_CONTEUDO.html").read_text(
        encoding="utf-8"
    )
    e2 = (tmp_path / "html_debug" / "DICAS-E2-01_CONTEUDO.html").read_text(
        encoding="utf-8"
    )
    assert "Começar pela área bloqueada" in e1
    assert "Comparar log e escala" in e1
    assert "Seguir a trilha do pagamento" in e2
    assert "Cobertura operacional" in e2
    assert "Fechamento da cadeia completa" in e2
    assert "Confidencial" in e1


def test_template_capa_usa_rotulo_apropriado_para_jogo_dicas_e_gabarito():
    renderer = _import_renderer_module()
    template = Path("templates/00_envelope_capa.html").read_text(encoding="utf-8")

    capa_jogo = renderer.injetar_dados(
        template,
        {
            "case_name": "Caso da Biblioteca",
            "section_label": "Envelope 2",
            "section_ref": "Material do jogador",
            "warning_label": "ABRIR APENAS QUANDO AUTORIZADO",
        },
    )
    capa_dicas = renderer.injetar_dados(
        template,
        {
            "case_name": "Caso da Biblioteca",
            "section_label": "Dicas",
            "section_ref": "Material de apoio ao facilitador",
            "warning_label": "ABRIR SOMENTE QUANDO NECESSÁRIO",
        },
    )
    capa_gabarito = renderer.injetar_dados(
        template,
        {
            "case_name": "Caso da Biblioteca",
            "section_label": "Gabarito",
            "section_ref": "Confidencial — facilitador",
            "warning_label": "NÃO ENTREGAR AOS JOGADORES",
        },
    )

    assert "Envelope 2" in capa_jogo
    assert "Dicas" in capa_dicas
    assert "Envelope 2" not in capa_dicas
    assert "Gabarito" in capa_gabarito
    assert "Envelope 2" not in capa_gabarito


def test_renderizar_caso_strict_aborta_em_placeholder_residual(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "Documento {{CORPO}} {{FALTA}}", encoding="utf-8"
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    blueprint_path = _blueprint_base(tmp_path)

    with pytest.raises(renderer.RenderCaseError) as excinfo:
        renderer.renderizar_caso(blueprint_path, tmp_path / "out", strict=True)

    assert "E1-01" in str(excinfo.value)
    assert "05_carta.html" in str(excinfo.value)
    assert "FALTA" in str(excinfo.value)


def test_renderizar_caso_non_strict_continua_em_placeholder_residual(
    tmp_path, monkeypatch
):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "Documento {{CORPO}} {{FALTA}}", encoding="utf-8"
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    blueprint_path = _blueprint_base(tmp_path)

    with pytest.warns(RuntimeWarning):
        grupos = renderer.renderizar_caso(
            blueprint_path, tmp_path / "out", strict=False
        )

    assert len(grupos["E1"]) == 1


def test_html_para_pdf_sem_playwright_falha_sem_env(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    monkeypatch.setattr(renderer, "_playwright_disponivel", lambda: False)
    monkeypatch.delenv("INDICIARIO_ALLOW_FAKE_PDF", raising=False)

    with pytest.raises(RuntimeError) as excinfo:
        import asyncio

        asyncio.run(renderer._html_para_pdf("<html></html>", tmp_path / "out.pdf"))

    assert "Playwright não está instalado" in str(excinfo.value)
    assert "python -m playwright install chromium" in str(excinfo.value)


def test_html_para_pdf_fake_exige_env_explicito(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    monkeypatch.setattr(renderer, "_playwright_disponivel", lambda: False)
    monkeypatch.setenv("INDICIARIO_ALLOW_FAKE_PDF", "1")

    import asyncio

    output = asyncio.run(renderer._html_para_pdf("<html></html>", tmp_path / "out.pdf"))

    assert output.exists()


def test_renderizar_documento_salva_html_debug_pos_template(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "<html>Documento {{CORPO}}</html>", encoding="utf-8"
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    debug_path = tmp_path / "html_debug" / "E1-01.html"

    renderer.renderizar_documento(
        "05_carta.html",
        {"CORPO": "final"},
        tmp_path / "E1-01.pdf",
        strict=True,
        html_debug_path=debug_path,
    )

    assert debug_path.read_text(encoding="utf-8") == "<html>Documento final</html>"


def test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "<html><head></head><body><main>{{CORPO}}</main></body></html>",
        encoding="utf-8",
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    debug_path = tmp_path / "html_debug" / "E1-01.html"

    renderer.renderizar_documento(
        "05_carta.html",
        {
            "CORPO": "final",
            "CODIGO_DOCUMENTO": "E1-01",
            "NOME_CASO": "Caso da Biblioteca",
            "ENVELOPE": "E1",
            "TIPO_DOCUMENTAL_SLUG": "carta",
        },
        tmp_path / "E1-01.pdf",
        strict=True,
        html_debug_path=debug_path,
    )

    html = debug_path.read_text(encoding="utf-8")
    assert "data-indiciario-visual-system" in html
    assert "doc-system doc-type-carta doc-family-letter doc-player" in html
    assert "ind-doc-meta-header" in html
    assert "E1-01" in html


def test_renderizar_documento_usa_familia_visual_e_emissor_de_email(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "01_email.html").write_text(
        "<html><head></head><body><main>{{CORPO}}</main></body></html>",
        encoding="utf-8",
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    debug_path = tmp_path / "html_debug" / "E1-02.html"

    renderer.renderizar_documento(
        "01_email.html",
        {
            "CORPO": "final",
            "CODIGO_DOCUMENTO": "E1-02",
            "NOME_CASO": "Caso da Biblioteca",
            "ENVELOPE": "E1",
            "TIPO_DOCUMENTAL_SLUG": "email_institucional",
            "REMETENTE_NOME": "Arquivo Central",
        },
        tmp_path / "E1-02.pdf",
        strict=True,
        html_debug_path=debug_path,
    )

    html = debug_path.read_text(encoding="utf-8")
    assert "doc-type-email_institucional" in html
    assert "doc-family-email" in html
    assert "Arquivo Central" in html
    assert "Arquivo documental" not in html


def test_renderizar_caso_preenche_html_debug_para_documentos(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text(
        "Documento {{CODIGO_DOCUMENTO}} {{CORPO}}", encoding="utf-8"
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    blueprint_path = _blueprint_base(tmp_path)

    renderer.renderizar_caso(
        blueprint_path,
        tmp_path / "out",
        strict=True,
        html_debug_dir=tmp_path / "html_debug",
    )

    debug_file = tmp_path / "html_debug" / "E1-01.html"
    assert debug_file.exists()
    assert "Documento E1-01" in debug_file.read_text(encoding="utf-8")


def test_log_template_permite_quebra_na_coluna_evento():
    template = Path("templates/06_log_acesso.html").read_text(encoding="utf-8")

    assert "table-layout: fixed" in template
    assert "overflow-wrap: anywhere" in template
    assert "th:nth-child(6)" in template
    assert "width: 22%" in template
    assert "width: 16%" in template


def test_templates_problematicos_usam_pagina_a4_compacta_ou_landscape_tabular():
    carta = Path("templates/05_carta.html").read_text(encoding="utf-8")
    extrato = Path("templates/09_extrato.html").read_text(encoding="utf-8")
    email = Path("templates/01_email.html").read_text(encoding="utf-8")

    assert "@page { size: A4; margin: 12mm; }" in carta
    assert "min-height: auto" in carta
    assert "@page { size: A4 landscape; margin: 10mm; }" in extrato
    assert "@page { size: A4; margin: 12mm; }" in email


def test_templates_tabulares_usam_landscape_no_renderer(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "06_log_acesso.html").write_text(
        "<html>{{NOME_SISTEMA}}</html>", encoding="utf-8"
    )
    (template_dir / "09_extrato.html").write_text(
        "<html>{{NOME_BANCO}}</html>", encoding="utf-8"
    )
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)
    blueprint_path = tmp_path / "blueprint.json"
    blueprint_path.write_text(
        json.dumps(
            {
                "titulo": "Caso de Logs",
                "documentos": [
                    {
                        "codigo": "E1-04",
                        "tipo": "log_acesso",
                        "envelope": "E1",
                        "conteudo": {"NOME_SISTEMA": "Acesso"},
                    },
                    {
                        "codigo": "E1-05",
                        "tipo": "escala",
                        "envelope": "E1",
                        "conteudo": {"NOME_SISTEMA": "Escala"},
                    },
                    {
                        "codigo": "E1-06",
                        "tipo": "extrato",
                        "envelope": "E1",
                        "conteudo": {"NOME_BANCO": "Banco"},
                    },
                ],
                "dicas": [],
            }
        ),
        encoding="utf-8",
    )
    chamadas = []

    async def fake_pdf(html, output_path, landscape=False):
        chamadas.append((output_path.name, landscape))
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)

    renderer.renderizar_caso(blueprint_path, tmp_path / "out", strict=True)

    assert chamadas == [("E1-04.pdf", True), ("E1-05.pdf", True), ("E1-06.pdf", True)]
    assert renderer.template_usa_landscape("06_log_acesso.html") is True
    assert renderer.template_usa_landscape("09_extrato.html") is True


def test_caso_canonico_e1_08_nao_tem_texto_meta() -> None:
    blueprint = json.loads(
        Path("examples/caso_canonico_iniciante.json").read_text(encoding="utf-8")
    )
    doc = next(item for item in blueprint["documentos"] if item["codigo"] == "E1-08")
    corpo = doc["conteudo"]["CORPO_CARTA"]

    assert "Essas definições devem ser usadas" not in corpo
    assert "cruzar E1-04" not in corpo
    assert "interpretação técnica externa" not in corpo
    assert "Trecho extraído do treinamento" in corpo
    assert "ID operacional" in corpo


def test_template_orcamento_esta_compacto_para_e2_03() -> None:
    template = Path("templates/08_orcamento.html").read_text(encoding="utf-8")

    assert "@page { size: A4; margin: 8mm; }" in template
    assert "padding: 0;" in template
    assert "min-height: 28px" in template


def test_renderer_injeta_manuscrito_visual_sem_residuo_tecnico() -> None:
    renderer = _import_renderer_module()
    html = renderer.renderizar_html(
        "{{#ANOTACAO}}<div>{{ANOTACAO_VISUAL}}</div>{{/ANOTACAO}}",
        {
            "ANOTACAO": "conferir lacre azul",
            "ANOTACAO_PERSONAGEM_ID": "P1",
        },
        personagens=[
            {
                "id": "P1",
                "nome": "Iara Nunes",
                "assinatura": {"estilo": "fluida", "seed": "iara"},
            }
        ],
    )

    assert "handwritten-note-svg" in html
    assert "{{" not in html
    assert "font-family" not in html

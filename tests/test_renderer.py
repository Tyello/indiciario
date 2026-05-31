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
    assert len(grupos["dicas"]) == 2


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
    (template_dir / "05_carta.html").write_text("Documento {{CORPO}} {{FALTA}}", encoding="utf-8")
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


def test_renderizar_caso_non_strict_continua_em_placeholder_residual(tmp_path, monkeypatch):
    renderer = _import_renderer_module()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "05_carta.html").write_text("Documento {{CORPO}} {{FALTA}}", encoding="utf-8")
    monkeypatch.setattr(renderer, "TEMPLATES_DIR", template_dir)

    async def fake_pdf(html, output_path, landscape=False):
        output_path.write_text(html, encoding="utf-8")
        return output_path

    monkeypatch.setattr(renderer, "_html_para_pdf", fake_pdf)
    blueprint_path = _blueprint_base(tmp_path)

    with pytest.warns(RuntimeWarning):
        grupos = renderer.renderizar_caso(blueprint_path, tmp_path / "out", strict=False)

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


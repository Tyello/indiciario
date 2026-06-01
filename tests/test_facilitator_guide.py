import json
from pathlib import Path

from generator.facilitator_guide import build_facilitator_context, render_facilitator_guide
from generator.models import Blueprint
from generator.pdf_backend import PdfWriter


def _make_pdf(path: Path) -> Path:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def _canonical() -> Blueprint:
    return Blueprint(**json.loads(Path("examples/caso_canonico_intermediario.json").read_text(encoding="utf-8")))


def test_build_facilitator_context_agrupa_contratos_e_dicas():
    context = build_facilitator_context(_canonical(), graph_report={"status": "passed", "summary": {"contracts": 6}})

    assert context["CASE_TITLE"]
    assert context["DICAS_POR_FASE"]
    assert any(grupo["fase"] == "E1" for grupo in context["DICAS_POR_FASE"])
    assert any(grupo["fase"] == "final" for grupo in context["CONTRATOS_POR_FASE"])
    assert context["GRAPH_STATUS"] == "passed"


def test_render_facilitator_guide_usa_renderer_oficial(tmp_path, monkeypatch):
    from generator import facilitator_guide

    chamadas = {}

    def fake_renderizar_documento(template_nome, dados, output_path, strict=True):
        chamadas["template"] = template_nome
        chamadas["dados"] = dados
        chamadas["strict"] = strict
        return _make_pdf(output_path)

    monkeypatch.setattr(facilitator_guide, "renderizar_documento", fake_renderizar_documento)

    output = render_facilitator_guide(_canonical(), tmp_path / "guia_facilitador.pdf", strict=True)

    assert output.exists()
    assert chamadas["template"] == "facilitator_guide.html"
    assert chamadas["strict"] is True
    assert chamadas["dados"]["DICAS_POR_FASE"]

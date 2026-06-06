import json
from pathlib import Path

from generator.models import Blueprint
from generator.print_guide import build_print_manifest
from generator.printable_cards import build_printable_card_documents
from generator.renderer import detectar_residuos_tecnicos
from generator.validator import BlueprintValidator
from generator.package_builder import build_package
from generator.pdf_backend import PdfWriter
from generator.qa import QAReport


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def load_iniciante() -> dict:
    return json.loads(Path("examples/caso_canonico_iniciante.json").read_text(encoding="utf-8"))


def test_printable_cards_renderiza_html_sem_residuos_e_classe_por_tipo(tmp_path, monkeypatch):
    from generator import printable_cards

    blueprint = Blueprint(**load_iniciante())
    captured: dict[str, str] = {}

    def fake_renderizar_documento(template_nome, dados, output_path, strict=True, html_debug_path=None):
        assert template_nome == "printable_cards.html"
        html = Path("templates/printable_cards.html").read_text(encoding="utf-8")
        from generator.renderer import renderizar_html

        final = renderizar_html(html, dados)
        captured[output_path.name] = final
        if html_debug_path:
            html_debug_path.parent.mkdir(parents=True, exist_ok=True)
            html_debug_path.write_text(final, encoding="utf-8")
        return make_pdf(output_path)

    monkeypatch.setattr(printable_cards, "renderizar_documento", fake_renderizar_documento)

    paths = build_printable_card_documents(blueprint, tmp_path, strict=True, html_debug_dir=tmp_path / "html")

    assert {path.name for path in paths} == {
        "cards_personagens.pdf",
        "cards_locais.pdf",
        "cards_objetos.pdf",
        "cards_todos.pdf",
    }
    todos_html = captured["cards_todos.pdf"]
    assert "printable-card--personagem" in todos_html
    assert "printable-card--local" in todos_html
    assert "printable-card--objeto" in todos_html
    assert "gabarito" not in todos_html.lower()
    assert detectar_residuos_tecnicos(todos_html) == []


def test_validator_bloqueia_linguagem_de_solucao_em_cartao():
    data = load_iniciante()
    data["printable_cards"][0]["descricao_curta"] = "Culpado final do caso."
    blueprint = Blueprint(**data)

    result = BlueprintValidator(blueprint, strict=True).validar()

    assert any(error.codigo == "CARD_001" for error in result.criticos)
    assert not result.pode_gerar


def test_print_manifest_marca_cartoes_como_apoio_recortavel(tmp_path):
    make_pdf(tmp_path / "printables" / "cards_todos.pdf")
    manifest = {
        "case": {"title": "Caso Teste"},
        "generated_at": "2026-06-06T00:00:00Z",
        "files": [
            {
                "id": "printable_cards_todos",
                "label": "Cartões — todos",
                "path": "printables/cards_todos.pdf",
                "category": "printable_support",
                "confidential": False,
                "page_count": 1,
                "cut_required": True,
            }
        ],
    }

    print_manifest = build_print_manifest(manifest, tmp_path)

    entry = print_manifest["files"][0]
    assert entry["deliver_to"] == "Apoio de mesa"
    assert entry["cut_required"] is True
    assert "printables/cards_todos.pdf" in print_manifest["visual_support_files"]


def test_build_package_registra_printables_no_manifest_e_print_manifest(tmp_path, monkeypatch):
    from generator import package_builder, printable_cards

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True, html_debug_dir=None):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [make_pdf(output_dir / "E2-01.pdf")],
            "dicas": [make_pdf(output_dir / "DICAS-E1.pdf")],
            "gabarito": [],
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    def fake_render_doc(_template, _dados, output_path, **_kwargs):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)
    monkeypatch.setattr(package_builder, "renderizar_documento", fake_render_doc)
    monkeypatch.setattr(package_builder, "build_visual_documents", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(printable_cards, "renderizar_documento", fake_render_doc)
    monkeypatch.setattr(
        package_builder,
        "run_qa",
        lambda _package_dir, _manifest, strict=True: QAReport(status="passed"),
    )

    result = build_package(Path("examples/caso_canonico_iniciante.json"), tmp_path, strict=True)
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    print_manifest = json.loads(Path(result["print_manifest_path"]).read_text(encoding="utf-8"))

    assert {item["path"] for item in manifest["printables"]} >= {
        "printables/cards_personagens.pdf",
        "printables/cards_locais.pdf",
        "printables/cards_objetos.pdf",
        "printables/cards_todos.pdf",
    }
    printable_files = [entry for entry in manifest["files"] if entry["category"] == "printable_support"]
    assert printable_files
    assert all(entry["cut_required"] for entry in printable_files)
    assert "printables/cards_todos.pdf" in print_manifest["visual_support_files"]

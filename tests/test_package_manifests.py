import json
from pathlib import Path

from generator.package_builder import build_package
from generator.pdf_backend import PdfWriter
from generator.print_guide import build_print_manifest
from generator.qa import run_qa


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def minimal_manifest(tmp_path: Path) -> dict:
    make_pdf(tmp_path / "01_envelope_1.pdf", 2)
    make_pdf(tmp_path / "03_dicas_facilitador.pdf", 1)
    return {
        "case": {"title": "Caso Teste", "slug": "caso-teste"},
        "generated_at": "2026-05-31T00:00:00Z",
        "status": "generated",
        "files": [
            {"id": "envelope_1", "label": "Envelope 1", "path": "01_envelope_1.pdf", "category": "player", "confidential": False, "page_count": 2},
            {"id": "dicas_facilitador", "label": "Dicas do Facilitador", "path": "03_dicas_facilitador.pdf", "category": "facilitator", "confidential": True, "page_count": 1},
        ],
        "documents": [
            {"codigo": "E1-01", "titulo": "Doc", "tipo": "carta", "envelope": "E1", "source_pdf": "rendered/E1-01.pdf", "final_file": "01_envelope_1.pdf", "page_start": 1, "page_end": 1}
        ],
        "warnings": [],
    }


def test_manifest_contem_arquivos_paths_relativos_e_docs_validos(tmp_path, monkeypatch):
    from generator import package_builder

    blueprint_path = Path("examples/showcase_tecnico.json")

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [make_pdf(output_dir / "E2-01.pdf")],
            "E3": [],
            "dicas": [make_pdf(output_dir / "DICAS-E1-00_CAPA.pdf")],
            "gabarito": [],
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)

    result = build_package(blueprint_path, tmp_path, strict=True)
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))

    paths = {entry["path"] for entry in manifest["files"]}
    assert {"01_envelope_1.pdf", "02_envelope_2.pdf", "03_dicas_facilitador.pdf", "05_guia_de_impressao.pdf"}.issubset(paths)
    assert all(not Path(path).is_absolute() for path in paths)
    assert all(entry["category"] != "player" for entry in manifest["files"] if "dicas" in entry["id"] or "gabarito" in entry["id"])
    assert all(doc["final_file"] in paths for doc in manifest["documents"])


def test_documentos_duplicados_no_manifest_geram_qa_error(tmp_path):
    manifest = minimal_manifest(tmp_path)
    manifest["documents"].append(dict(manifest["documents"][0]))
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "print_manifest.json").write_text("{}", encoding="utf-8")

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_DOC_004" for error in report.errors)


def test_print_manifest_calcula_paginas_confidencialidade_duplex_e_perfis(tmp_path):
    manifest = minimal_manifest(tmp_path)

    print_manifest = build_print_manifest(manifest, tmp_path)

    assert print_manifest["total_pages"] == 3
    assert set(print_manifest["profiles"]) == {"economico", "padrao", "premium"}
    by_file = {entry["file"]: entry for entry in print_manifest["files"]}
    assert by_file["01_envelope_1.pdf"]["confidential"] is False
    assert by_file["03_dicas_facilitador.pdf"]["confidential"] is True
    assert all(entry["duplex"] is False for entry in print_manifest["files"])

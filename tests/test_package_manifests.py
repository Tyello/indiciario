import json
from pathlib import Path

import pytest

from generator.merger import count_pdf_pages
from generator.package_builder import PackageBuildError, build_package
from generator.pdf_backend import PdfWriter
from generator.print_guide import build_print_manifest
from generator.qa import QAReport, run_qa


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

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)

    result = build_package(blueprint_path, tmp_path, strict=True)
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))

    paths = {entry["path"] for entry in manifest["files"]}
    assert {"01_envelope_1.pdf", "02_envelope_2.pdf", "03_dicas_facilitador.pdf", "04_guia_facilitador.pdf", "05_guia_de_impressao.pdf"}.issubset(paths)
    assert all(not Path(path).is_absolute() for path in paths)
    assert all(entry["category"] != "player" for entry in manifest["files"] if "dicas" in entry["id"] or "gabarito" in entry["id"])
    assert all(doc["final_file"] in paths for doc in manifest["documents"])
    assert result["graph_report_path"].endswith("graph_report.json")
    assert Path(result["graph_report_path"]).exists()
    assert Path(result["llm_feedback_path"]).exists()
    assert result["llm_feedback_path"].endswith("llm_feedback.json")
    assert Path(result["llm_feedback_path"]).exists()
    assert result["playtest_report_path"].endswith("playtest_report.json")
    assert Path(result["playtest_report_path"]).exists()
    assert manifest["reports"] == {"qa": "qa_report.json", "graph": "graph_report.json", "llm_feedback": "llm_feedback.json", "playtest": "playtest_report.json"}
    assert "graph_report.json" not in paths
    assert "llm_feedback.json" not in paths
    assert "playtest_report.json" not in paths


def test_build_package_blueprint_legado_sem_contratos_nao_falha_por_graph_skipped(tmp_path, monkeypatch):
    from generator import package_builder

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [make_pdf(output_dir / "E2-01.pdf")],
            "E3": [],
            "dicas": [],
            "gabarito": [],
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)
    monkeypatch.setattr(package_builder, "run_qa", lambda _package_dir, _manifest, strict=True: QAReport(status="passed"))

    result = build_package(Path("examples/exemplo_blueprint.json"), tmp_path, strict=True)
    graph_report = json.loads(Path(result["graph_report_path"]).read_text(encoding="utf-8"))

    assert result["status"] == "passed"
    assert result["graph_status"] == "skipped"
    assert graph_report["status"] == "skipped"
    assert graph_report["summary"]["contracts"] == 0
    assert any(issue["code"] == "GP_006" and issue["severity"] == "warning" for issue in graph_report["issues"])


def test_build_package_strict_falha_quando_e3_sem_e2(tmp_path, monkeypatch):
    from generator import package_builder

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [],
            "E3": [make_pdf(output_dir / "E3-01.pdf")],
            "dicas": [],
            "gabarito": [],
        }

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)

    with pytest.raises(PackageBuildError) as excinfo:
        build_package(Path("examples/showcase_tecnico.json"), tmp_path, strict=True)

    assert "Sequência de envelopes com buraco" in str(excinfo.value)


def test_build_package_empacota_tres_envelopes_e_desloca_auxiliares(tmp_path, monkeypatch):
    from generator import package_builder

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [make_pdf(output_dir / "E2-01.pdf")],
            "E3": [make_pdf(output_dir / "E3-01.pdf")],
            "dicas": [make_pdf(output_dir / "DICAS-E1-00_CAPA.pdf")],
            "gabarito": [make_pdf(output_dir / "GABARITO.pdf")],
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)

    result = build_package(Path("examples/showcase_tecnico.json"), tmp_path, strict=True)
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    print_manifest = json.loads(Path(result["print_manifest_path"]).read_text(encoding="utf-8"))

    paths = [entry["path"] for entry in manifest["files"]]
    assert "03_envelope_3.pdf" in paths
    assert "04_dicas_facilitador.pdf" in paths
    assert "05_gabarito_mestre.pdf" in paths
    assert "06_guia_facilitador.pdf" in paths
    assert "07_guia_de_impressao.pdf" in paths
    assert {entry["file"] for entry in print_manifest["files"]} == set(paths)
    assert "llm_feedback.json" not in {entry["file"] for entry in print_manifest["files"]}
    assert "playtest_report.json" not in {entry["file"] for entry in print_manifest["files"]}
    assert result["status"] == "passed"
    assert result["graph_status"] == "passed"
    assert Path(result["graph_report_path"]).exists()


def test_print_manifest_final_usa_page_count_final_do_guia(tmp_path, monkeypatch):
    from generator import package_builder

    chamadas = {"count": 0}

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [],
            "E3": [],
            "dicas": [],
            "gabarito": [],
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        chamadas["count"] += 1
        pages = 1 if chamadas["count"] == 1 else 2
        return make_pdf(output_path, pages=pages)

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)

    result = build_package(Path("examples/showcase_tecnico.json"), tmp_path, strict=True)
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    print_manifest = json.loads(Path(result["print_manifest_path"]).read_text(encoding="utf-8"))

    manifest_guide = next(item for item in manifest["files"] if item["id"] == "guia_de_impressao")
    print_guide = next(item for item in print_manifest["files"] if item["file"] == "03_guia_de_impressao.pdf")

    assert chamadas["count"] == 2
    assert count_pdf_pages(Path(result["output_dir"]) / "03_guia_de_impressao.pdf") == 2
    assert manifest_guide["page_count"] == 2
    assert print_guide["page_count"] == 2


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


def test_guia_facilitador_no_manifest_print_manifest_e_qa(tmp_path, monkeypatch):
    from generator import package_builder

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

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "build_visual_documents", lambda _blueprint, _output_dir, strict=True: {})
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)

    result = build_package(Path("examples/caso_canonico_intermediario.json"), tmp_path, strict=True)
    package_dir = Path(result["output_dir"])
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    print_manifest = json.loads(Path(result["print_manifest_path"]).read_text(encoding="utf-8"))

    guia = next(entry for entry in manifest["files"] if entry["id"] == "guia_facilitador")
    assert guia["category"] == "facilitator"
    assert guia["confidential"] is True
    assert guia["path"] == "04_guia_facilitador.pdf"
    assert guia["path"] in print_manifest["facilitator_files"]
    assert guia["path"] not in print_manifest["player_files"]
    assert all(doc["final_file"] != guia["path"] for doc in manifest["documents"])

    qa_report = run_qa(package_dir, manifest)
    assert qa_report.status == "passed"


def test_build_package_strict_nao_gera_pdf_fake_sem_env(tmp_path, monkeypatch):
    from generator import renderer

    monkeypatch.setattr(renderer, "_playwright_disponivel", lambda: False)
    monkeypatch.delenv("INDICIARIO_ALLOW_FAKE_PDF", raising=False)

    with pytest.raises(RuntimeError) as excinfo:
        build_package(Path("examples/showcase_tecnico.json"), tmp_path, strict=True)

    assert "Playwright não está instalado" in str(excinfo.value)
    assert "python -m playwright install chromium" in str(excinfo.value)



def test_build_package_passa_html_debug_dir_sem_incluir_no_print_manifest(tmp_path, monkeypatch):
    from generator import package_builder

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True, html_debug_dir=None):
        assert html_debug_dir is not None
        html_debug_dir.mkdir(parents=True, exist_ok=True)
        (html_debug_dir / "E1-01.html").write_text("<html>debug narrativo</html>", encoding="utf-8")
        return {"E1": [make_pdf(output_dir / "E1-01.pdf")], "dicas": [], "gabarito": []}

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    def fake_render_facilitator_guide(_blueprint, output_path, graph_report=None, strict=True):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(package_builder, "build_visual_documents", lambda _blueprint, output_dir, strict=True: {})
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(package_builder, "render_facilitator_guide", fake_render_facilitator_guide)

    result = build_package(Path("examples/showcase_tecnico.json"), tmp_path, strict=True)
    package_dir = Path(result["output_dir"])
    print_manifest = json.loads(Path(result["print_manifest_path"]).read_text(encoding="utf-8"))

    assert (package_dir / "html_debug" / "E1-01.html").exists()
    assert all("html_debug" not in json.dumps(entry, ensure_ascii=False) for entry in print_manifest["files"])

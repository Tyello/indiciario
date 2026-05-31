import json
from pathlib import Path

from generator.pdf_backend import PdfWriter
from generator.qa import run_qa, write_qa_report


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def valid_manifest(package_dir: Path) -> dict:
    make_pdf(package_dir / "01_envelope_1.pdf", 1)
    manifest = {
        "case": {"title": "Caso QA", "slug": "caso-qa"},
        "generated_at": "2026-05-31T00:00:00Z",
        "status": "generated",
        "files": [
            {"id": "envelope_1", "label": "Envelope 1", "path": "01_envelope_1.pdf", "category": "player", "confidential": False, "page_count": 1}
        ],
        "documents": [
            {"codigo": "E1-01", "titulo": "Doc", "tipo": "carta", "envelope": "E1", "source_pdf": "rendered/E1-01.pdf", "final_file": "01_envelope_1.pdf", "page_start": 1, "page_end": 1}
        ],
        "warnings": [],
    }
    (package_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (package_dir / "print_manifest.json").write_text("{}", encoding="utf-8")
    return manifest


def test_qa_passa_com_pacote_minimo_valido(tmp_path):
    report = run_qa(tmp_path, valid_manifest(tmp_path))

    assert report.status == "passed"
    assert report.files_checked == ["01_envelope_1.pdf"]
    assert report.documents_checked == ["E1-01"]


def test_qa_falha_se_arquivo_listado_nao_existe(tmp_path):
    manifest = valid_manifest(tmp_path)
    Path(tmp_path / "01_envelope_1.pdf").unlink()

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_FILE_001" for error in report.errors)


def test_qa_falha_se_pdf_nao_abre(tmp_path):
    manifest = valid_manifest(tmp_path)
    (tmp_path / "01_envelope_1.pdf").write_text("não é pdf", encoding="utf-8")

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_FILE_002" for error in report.errors)


def test_qa_falha_se_pdf_tem_zero_paginas(tmp_path):
    manifest = valid_manifest(tmp_path)
    writer = PdfWriter()
    with (tmp_path / "01_envelope_1.pdf").open("wb") as fp:
        writer.write(fp)

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_FILE_002" for error in report.errors)


def test_qa_falha_se_page_count_diverge(tmp_path):
    manifest = valid_manifest(tmp_path)
    manifest["files"][0]["page_count"] = 2

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_FILE_003" for error in report.errors)


def test_qa_falha_se_gabarito_esta_como_player(tmp_path):
    manifest = valid_manifest(tmp_path)
    make_pdf(tmp_path / "04_gabarito_mestre.pdf", 1)
    manifest["files"].append({"id": "gabarito_mestre", "label": "Gabarito Mestre", "path": "04_gabarito_mestre.pdf", "category": "player", "confidential": False, "page_count": 1})

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_CONF_001" for error in report.errors)
    assert any(error.code == "QA_CONF_002" for error in report.errors)


def test_qa_detecta_residuo_tecnico_em_html_debug(tmp_path):
    manifest = valid_manifest(tmp_path)
    debug = tmp_path / "html_debug"
    debug.mkdir()
    (debug / "doc.html").write_text("Olá {{NOME}} placeholder", encoding="utf-8")

    report = run_qa(tmp_path, manifest)

    assert report.status == "failed"
    assert any(error.code == "QA_HTML_001" for error in report.errors)


def test_qa_escreve_qa_report_json(tmp_path):
    report = run_qa(tmp_path, valid_manifest(tmp_path))
    path = write_qa_report(report, tmp_path / "qa_report.json")

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "passed"
    assert data["errors"] == []

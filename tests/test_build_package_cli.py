from pathlib import Path

from generator.pdf_backend import PdfWriter
from scripts import build_package as cli


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def test_build_package_cli_smoke_sem_chromium(tmp_path, monkeypatch, capsys):
    def fake_build_package(blueprint_path, output_root, strict):
        assert blueprint_path == Path("examples/showcase_tecnico.json")
        assert output_root == tmp_path
        assert strict is True
        return {
            "status": "passed",
            "case_slug": "showcase-tecnico-do-indiciario",
            "output_dir": str(tmp_path / "showcase-tecnico-do-indiciario"),
            "manifest_path": str(tmp_path / "showcase-tecnico-do-indiciario" / "manifest.json"),
            "print_manifest_path": str(tmp_path / "showcase-tecnico-do-indiciario" / "print_manifest.json"),
            "qa_report_path": str(tmp_path / "showcase-tecnico-do-indiciario" / "qa_report.json"),
            "graph_report_path": str(tmp_path / "showcase-tecnico-do-indiciario" / "graph_report.json"),
            "qa_status": "passed",
            "graph_status": "passed",
        }

    monkeypatch.setattr(cli, "build_package", fake_build_package)
    monkeypatch.setattr(
        "sys.argv",
        ["build_package", "examples/showcase_tecnico.json", "--output", str(tmp_path), "--strict"],
    )

    cli.main()

    out = capsys.readouterr().out
    assert "Validando blueprint..." in out
    assert "Pacote gerado em:" in out
    assert "QA: passed" in out
    assert "Graph: passed" in out

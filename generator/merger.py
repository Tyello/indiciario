"""Utilitários para juntar e inspecionar PDFs do pacote final."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, TypedDict

from .pdf_backend import PdfReader, PdfWriter


class OutputPaths(TypedDict, total=False):
    case_slug: str
    output_dir: Path
    rendered_dir: Path
    html_debug_dir: Path
    envelope_1: Path
    envelope_2: Path
    dicas_facilitador: Path
    gabarito_mestre: Path
    guia_de_impressao: Path
    manifest: Path
    print_manifest: Path
    qa_report: Path
    graph_report: Path
    llm_feedback: Path
    playtest_report: Path


class PDFMergeError(RuntimeError):
    """Erro claro para PDFs ausentes, vazios ou ilegíveis."""


def _validar_pdf_entrada(pdf_path: Path) -> PdfReader:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF de entrada não encontrado: {pdf_path}")
    try:
        reader = PdfReader(str(pdf_path))
        if len(reader.pages) < 1:
            raise PDFMergeError(f"PDF sem páginas: {pdf_path}")
        return reader
    except PDFMergeError:
        raise
    except Exception as exc:  # noqa: BLE001 - pypdf levanta exceções variadas para PDFs inválidos.
        raise PDFMergeError(f"PDF ilegível: {pdf_path}") from exc


def merge_pdfs(pdf_paths: list[Path], output_path: Path) -> Path:
    """Junta PDFs na ordem recebida e valida que cada entrada tem ao menos 1 página."""
    if not pdf_paths:
        raise PDFMergeError("Nenhum PDF informado para merge.")

    writer = PdfWriter()
    for pdf_path in pdf_paths:
        reader = _validar_pdf_entrada(pdf_path)
        if hasattr(writer, "append"):
            writer.append(reader)
        else:  # pragma: no cover - fallback mínimo sem pypdf instalado.
            for page in reader.pages:
                writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as fp:
        writer.write(fp)

    count_pdf_pages(output_path)
    return output_path


def count_pdf_pages(pdf_path: Path) -> int:
    """Conta páginas de um PDF existente, falhando para arquivo vazio ou ilegível."""
    reader = _validar_pdf_entrada(pdf_path)
    return len(reader.pages)


def get_pdf_orientation_summary(pdf_path: Path) -> dict[str, Any]:
    """Retorna resumo simples de orientação das páginas do PDF."""
    reader = _validar_pdf_entrada(pdf_path)
    portrait = 0
    landscape = 0
    square = 0
    for page in reader.pages:
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)
        if width > height:
            landscape += 1
        elif height > width:
            portrait += 1
        else:
            square += 1
    total = portrait + landscape + square
    if landscape and not portrait and not square:
        dominant = "landscape"
    elif portrait and not landscape and not square:
        dominant = "portrait"
    elif square and not portrait and not landscape:
        dominant = "square"
    else:
        dominant = "mixed"
    return {
        "page_count": total,
        "portrait": portrait,
        "landscape": landscape,
        "square": square,
        "dominant": dominant,
    }


def safe_slug(value: str) -> str:
    """Normaliza texto para slug ASCII estável."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "caso-sem-titulo"


def build_output_paths(case_title: str, output_root: Path) -> OutputPaths:
    """Monta caminhos padronizados para o pacote final."""
    case_slug = safe_slug(case_title)
    output_dir = output_root / case_slug
    return {
        "case_slug": case_slug,
        "output_dir": output_dir,
        "rendered_dir": output_dir / "rendered",
        "html_debug_dir": output_dir / "html_debug",
        "envelope_1": output_dir / "01_envelope_1.pdf",
        "envelope_2": output_dir / "02_envelope_2.pdf",
        "dicas_facilitador": output_dir / "03_dicas_facilitador.pdf",
        "gabarito_mestre": output_dir / "04_gabarito_mestre.pdf",
        "guia_de_impressao": output_dir / "05_guia_de_impressao.pdf",
        "manifest": output_dir / "manifest.json",
        "print_manifest": output_dir / "print_manifest.json",
        "qa_report": output_dir / "qa_report.json",
        "graph_report": output_dir / "graph_report.json",
        "llm_feedback": output_dir / "llm_feedback.json",
        "playtest_report": output_dir / "playtest_report.json",
    }

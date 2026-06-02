from pathlib import Path

import pytest
from pypdf.generic import DecodedStreamObject, NameObject

from generator.merger import build_output_paths, count_pdf_pages, get_pdf_orientation_summary, merge_pdfs, safe_slug
from generator.pdf_backend import PdfReader, PdfWriter




def make_pdf_with_content(path: Path, text: str) -> Path:
    writer = PdfWriter()
    page = writer.add_blank_page(width=595, height=842)
    stream = DecodedStreamObject()
    safe_text = text.replace("(", "").replace(")", "")
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode("latin-1"))
    page[NameObject("/Contents")] = stream
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def page_has_content_stream(pdf_path: Path, page_index: int) -> bool:
    contents = PdfReader(str(pdf_path)).pages[page_index].get_contents()
    return contents is not None and bool(contents.get_data())

def make_pdf(path: Path, pages: list[tuple[int, int]]) -> Path:
    writer = PdfWriter()
    for width, height in pages:
        writer.add_blank_page(width=width, height=height)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def test_merge_pdfs_junta_dois_pdfs_simples(tmp_path):
    pdf1 = make_pdf(tmp_path / "a.pdf", [(595, 842)])
    pdf2 = make_pdf(tmp_path / "b.pdf", [(595, 842)])

    merged = merge_pdfs([pdf1, pdf2], tmp_path / "merged.pdf")

    assert merged.exists()
    assert count_pdf_pages(merged) == 2


def test_count_pdf_pages_retorna_numero_correto(tmp_path):
    pdf = make_pdf(tmp_path / "three.pdf", [(595, 842), (595, 842), (842, 595)])

    assert count_pdf_pages(pdf) == 3


def test_safe_slug_normaliza_titulo_com_acentos_espacos():
    assert safe_slug("Showcase Técnico do Indiciário!") == "showcase-tecnico-do-indiciario"


def test_merge_pdfs_erro_quando_entrada_nao_existe(tmp_path):
    with pytest.raises(FileNotFoundError):
        merge_pdfs([tmp_path / "ausente.pdf"], tmp_path / "out.pdf")


def test_merge_preserva_orientacoes_por_pagina(tmp_path):
    portrait = make_pdf(tmp_path / "portrait.pdf", [(595, 842)])
    landscape = make_pdf(tmp_path / "landscape.pdf", [(842, 595)])

    merged = merge_pdfs([portrait, landscape], tmp_path / "mixed.pdf")
    summary = get_pdf_orientation_summary(merged)

    assert summary["page_count"] == 2
    assert summary["portrait"] == 1
    assert summary["landscape"] == 1
    assert summary["dominant"] == "mixed"

def test_build_output_paths_retorna_slug_string_e_output_dir_path(tmp_path):
    paths = build_output_paths("Caso Técnico do Indiciário", tmp_path)

    assert paths["case_slug"] == "caso-tecnico-do-indiciario"
    assert paths["output_dir"] == tmp_path / "caso-tecnico-do-indiciario"
    assert paths["guia_de_impressao"] == tmp_path / "caso-tecnico-do-indiciario" / "05_guia_de_impressao.pdf"



def test_merge_pdfs_copia_streams_de_conteudo_reais(tmp_path):
    pdf1 = make_pdf_with_content(tmp_path / "a_texto.pdf", "Documento A visivel")
    pdf2 = make_pdf_with_content(tmp_path / "b_texto.pdf", "Documento B visivel")

    merged = merge_pdfs([pdf1, pdf2], tmp_path / "merged_texto.pdf")

    assert count_pdf_pages(merged) == 2
    assert page_has_content_stream(merged, 0)
    assert page_has_content_stream(merged, 1)

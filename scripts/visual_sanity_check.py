"""Sanity checks visuais/editoriais para blueprints e PDFs renderizados.

O objetivo deste script não é provar que o layout está perfeito. Ele procura
sintomas conhecidos de regressão antes do playtest: tabelas sem estrutura visual
mínima, termos artificiais em material do jogador e texto extraído de PDF com
palavras coladas por falha de renderização.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - import opcional só afeta --pdf.
    PdfReader = None  # type: ignore[assignment]

TABLE_CLASSES_REQUIRING_COLGROUP = {
    "table-admin",
    "table-comparison",
    "table-support",
}
SPECIAL_WIDE_TABLE_CLASSES = {
    "table-wide",
    "table-a4-wide",
    "table-visual-reviewed",
    "table-layout-reviewed",
}
FORBIDDEN_ARTIFICIAL_TERMS = {
    "VIS_TEXT_001": [
        re.compile(r"\bpersona\b", re.IGNORECASE),
        re.compile(r"Registro\s+interno\s*/\s*persona", re.IGNORECASE),
        re.compile(r"\bplaceholder\b", re.IGNORECASE),
        re.compile(r"\bCOPIA\b"),
        re.compile(r"\bTODO\b", re.IGNORECASE),
        re.compile(r"Lorem\s+ipsum", re.IGNORECASE),
    ]
}
METAGAME_TERMS = [
    re.compile(r"\bculpado\b", re.IGNORECASE),
    re.compile(r"\bgabarito\b", re.IGNORECASE),
    re.compile(r"compare\s+este\s+documento", re.IGNORECASE),
    re.compile(r"\bdica\b", re.IGNORECASE),
    re.compile(r"\bsolu[cç][aã]o\b", re.IGNORECASE),
    re.compile(r"vers[aã]o\s+usada\s+no\s+golpe", re.IGNORECASE),
    re.compile(r"recado\s+falso", re.IGNORECASE),
]
PDF_GLUED_TEXT_PATTERNS = [
    re.compile(r"[a-záéíóúâêôãõàüç][A-ZÁÉÍÓÚÂÊÔÃÕÀÜÇ][a-záéíóúâêôãõàüç]"),
    re.compile(r"[A-ZÁÉÍÓÚÂÊÔÃÕÀÜÇ]{3,}[A-ZÁÉÍÓÚÂÊÔÃÕÀÜÇ][a-záéíóúâêôãõàüç]{2,}"),
    re.compile(r"[A-Za-zÁÉÍÓÚÂÊÔÃÕÀÜÇáéíóúâêôãõàüç](?:\d{1,2}h\d{2}|\d{1,2}:\d{2})"),
]


@dataclass(frozen=True)
class Issue:
    code: str
    severity: str
    message: str
    location: str
    sample: str = ""

    def render(self) -> str:
        sample = f" — {self.sample}" if self.sample else ""
        return f"{self.severity.upper()} {self.code} {self.location}: {self.message}{sample}"


@dataclass
class HtmlTable:
    classes: set[str]
    has_colgroup: bool
    col_count: int
    headers: list[str]
    rows: list[list[str]]


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[HtmlTable] = []
        self._table: dict[str, Any] | None = None
        self._row: list[str] | None = None
        self._cell_parts: list[str] | None = None
        self._cell_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag == "table":
            classes = set(attrs_dict.get("class", "").split())
            self._table = {
                "classes": classes,
                "has_colgroup": False,
                "cols": 0,
                "headers": [],
                "rows": [],
            }
        elif tag == "colgroup" and self._table is not None:
            self._table["has_colgroup"] = True
        elif tag == "col" and self._table is not None:
            self._table["cols"] += 1
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"th", "td"} and self._table is not None and self._row is not None:
            self._cell_tag = tag
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self._cell_parts is not None and self._row is not None:
            text = _normalize_text("".join(self._cell_parts))
            self._row.append(text)
            if tag == "th" and self._table is not None:
                self._table["headers"].append(text)
            self._cell_parts = None
            self._cell_tag = None
        elif tag == "tr" and self._table is not None and self._row is not None:
            self._table["rows"].append(self._row)
            if not self._table["cols"]:
                self._table["cols"] = max(self._table["cols"], len(self._row))
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(
                HtmlTable(
                    classes=set(self._table["classes"]),
                    has_colgroup=bool(self._table["has_colgroup"]),
                    col_count=int(self._table["cols"]),
                    headers=list(self._table["headers"]),
                    rows=list(self._table["rows"]),
                )
            )
            self._table = None


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return _normalize_text(" ".join(self.parts))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text).replace("\xa0", " ")).strip()


def _parse_tables(html: str) -> list[HtmlTable]:
    parser = _TableParser()
    parser.feed(html)
    return parser.tables


def _html_to_text(html: str) -> str:
    parser = _TextParser()
    parser.feed(html)
    return parser.text()


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_strings(child)


def _iter_player_documents(blueprint: dict[str, Any]) -> Iterable[dict[str, Any]]:
    # Os documentos em blueprint são material dos jogadores; guia, dicas e
    # metadados internos vivem em chaves próprias e não são inspecionados aqui.
    yield from blueprint.get("documentos", [])


def _document_html_fields(document: dict[str, Any]) -> Iterable[tuple[str, str]]:
    content = document.get("conteudo", {})
    if not isinstance(content, dict):
        return
    for key, value in content.items():
        if isinstance(value, str) and ("<" in value and ">" in value):
            yield key, value


def _table_location(document: dict[str, Any], field: str, index: int) -> str:
    return f"{document.get('codigo', '<sem-codigo>')}.{field}.table[{index}]"


def _blank_rows(table: HtmlTable) -> int:
    return sum(1 for row in table.rows if row and all(not cell for cell in row))


def _has_special_wide_class(table: HtmlTable) -> bool:
    return bool(table.classes & SPECIAL_WIDE_TABLE_CLASSES)


def _is_support_table(document: dict[str, Any], table: HtmlTable) -> bool:
    title = str(document.get("titulo", "")).lower()
    return (
        "table-support" in table.classes
        or "folha de apoio" in title
        or "apoio" in title
    )


def _check_table(document: dict[str, Any], field: str, table: HtmlTable, index: int) -> list[Issue]:
    issues: list[Issue] = []
    location = _table_location(document, field, index)
    table_class_label = ", ".join(sorted(table.classes)) or "sem classe"

    if table.classes & TABLE_CLASSES_REQUIRING_COLGROUP and not table.has_colgroup:
        issues.append(
            Issue(
                "VIS_TABLE_001",
                "warning",
                "table-admin/table-comparison/table-support deve declarar colgroup para estabilizar larguras no PDF",
                location,
                table_class_label,
            )
        )

    if table.col_count > 4 and not _has_special_wide_class(table):
        issues.append(
            Issue(
                "VIS_TABLE_002",
                "warning",
                "tabela de documento do jogador tem mais de 4 colunas sem classe especial/justificativa visual",
                location,
                f"{table.col_count} colunas",
            )
        )

    if _is_support_table(document, table):
        if _blank_rows(table) < 4:
            issues.append(
                Issue(
                    "VIS_TABLE_003",
                    "warning",
                    "folha de apoio/preenchimento precisa de pelo menos 4 linhas em branco reais",
                    location,
                    f"{_blank_rows(table)} linhas em branco",
                )
            )
        if table.col_count > 4 and not _has_special_wide_class(table):
            issues.append(
                Issue(
                    "VIS_TABLE_004",
                    "warning",
                    "folha de apoio tem colunas demais para uso confortável em A4",
                    location,
                    f"{table.col_count} colunas",
                )
            )

    header_limit = 28 if table.col_count >= 4 else 44
    for header in table.headers:
        if len(header) > header_limit:
            issues.append(
                Issue(
                    "VIS_TABLE_005",
                    "warning",
                    "cabeçalho longo demais para coluna potencialmente estreita",
                    location,
                    header[:80],
                )
            )
            break

    has_note_column = any(
        "observ" in header.lower() or "anota" in header.lower() or "nota" in header.lower()
        for header in table.headers
    )
    has_note_class = bool(table.classes & {"table-notes", "table-with-notes"}) or any(
        class_name in table.classes for class_name in {"col-note", "col-notes"}
    )
    long_cells = [cell for row in table.rows for cell in row if len(cell) > 90]
    if long_cells and not (has_note_column or has_note_class):
        issues.append(
            Issue(
                "VIS_TABLE_006",
                "warning",
                "observação/texto longo em tabela sem coluna/classe apropriada para notas",
                location,
                long_cells[0][:90],
            )
        )

    return issues


def check_blueprint(blueprint: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    for document in _iter_player_documents(blueprint):
        doc_location = str(document.get("codigo", "<sem-codigo>"))
        rendered_text_parts: list[str] = []
        for raw in _iter_strings(document.get("conteudo", {})):
            rendered_text_parts.append(_html_to_text(raw) if "<" in raw and ">" in raw else raw)
        rendered_text = _normalize_text(" ".join(rendered_text_parts))

        for pattern in FORBIDDEN_ARTIFICIAL_TERMS["VIS_TEXT_001"]:
            match = pattern.search(rendered_text)
            if match:
                issues.append(
                    Issue(
                        "VIS_TEXT_001",
                        "error",
                        "termo artificial proibido em material do jogador",
                        doc_location,
                        match.group(0),
                    )
                )

        for pattern in METAGAME_TERMS:
            match = pattern.search(rendered_text)
            if match:
                issues.append(
                    Issue(
                        "VIS_META_001",
                        "warning",
                        "possível linguagem de metajogo em documento do jogador",
                        doc_location,
                        match.group(0),
                    )
                )

        for field, html in _document_html_fields(document):
            for index, table in enumerate(_parse_tables(html), start=1):
                issues.extend(_check_table(document, field, table, index))
    return issues


def check_pdf_text(text: str, location: str = "pdf") -> list[Issue]:
    normalized = _normalize_text(text)
    issues: list[Issue] = []
    seen: set[str] = set()
    for pattern in PDF_GLUED_TEXT_PATTERNS:
        for match in pattern.finditer(normalized):
            sample = match.group(0)
            if sample in seen:
                continue
            seen.add(sample)
            issues.append(
                Issue(
                    "VIS_TEXT_002",
                    "warning",
                    "possível texto colado no PDF extraído; revisar renderização visual",
                    location,
                    sample[:80],
                )
            )
            if len(issues) >= 10:
                return issues
    return issues


def check_pdf(path: Path) -> list[Issue]:
    if PdfReader is None:
        return [
            Issue(
                "VIS_PDF_001",
                "error",
                "pypdf não está instalado; não foi possível extrair texto do PDF",
                str(path),
            )
        ]
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return check_pdf_text("\n".join(pages), str(path))


def load_blueprint(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Blueprint JSON deve conter um objeto na raiz.")
    return data


def summarize(issues: list[Issue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "ERROR"
    if issues:
        return "WARNING"
    return "OK"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sanity check visual/editorial para blueprint e PDF.")
    parser.add_argument("blueprint", type=Path, help="Caminho do blueprint JSON.")
    parser.add_argument("--pdf", type=Path, help="PDF renderizado opcional para heurísticas de texto colado.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    issues = check_blueprint(load_blueprint(args.blueprint))
    if args.pdf:
        issues.extend(check_pdf(args.pdf))

    print(summarize(issues))
    for issue in issues:
        print(issue.render())
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

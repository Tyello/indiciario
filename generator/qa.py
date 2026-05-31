"""QA técnico do pacote final do Indiciário."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .merger import PDFMergeError, count_pdf_pages

RESIDUO_RE = re.compile(r"\{\{.*?\}\}|\bNone\b|(?i:\b(undefined|CONTEUDO_GENERICO)\b|placeholder|lorem\s+ipsum)", re.DOTALL)


@dataclass
class QAIssue:
    code: str
    severity: str
    message: str
    file: str | None = None
    document: str | None = None


@dataclass
class QAReport:
    status: str
    errors: list[QAIssue] = field(default_factory=list)
    warnings: list[QAIssue] = field(default_factory=list)
    files_checked: list[str] = field(default_factory=list)
    documents_checked: list[str] = field(default_factory=list)


def _issue(code: str, message: str, file: str | None = None, document: str | None = None) -> QAIssue:
    return QAIssue(code=code, severity="error", message=message, file=file, document=document)


def _warn(code: str, message: str, file: str | None = None, document: str | None = None) -> QAIssue:
    return QAIssue(code=code, severity="warning", message=message, file=file, document=document)


def report_to_dict(report: QAReport) -> dict[str, Any]:
    return asdict(report)


def write_qa_report(report: QAReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def run_qa(package_dir: Path, manifest: dict[str, Any], strict: bool = True) -> QAReport:
    """Executa checks técnicos do pacote final."""
    report = QAReport(status="passed")
    file_entries = manifest.get("files", [])
    manifest_files = {entry.get("path") for entry in file_entries if entry.get("path")}

    if not (package_dir / "manifest.json").exists():
        report.errors.append(_issue("QA_MANIFEST_001", "manifest.json não existe.", "manifest.json"))
    if not (package_dir / "print_manifest.json").exists():
        report.errors.append(_issue("QA_MANIFEST_002", "print_manifest.json não existe.", "print_manifest.json"))

    categories_by_file: dict[str, str] = {}
    for entry in file_entries:
        path = entry.get("path")
        if not path:
            report.errors.append(_issue("QA_FILE_000", "Arquivo no manifest não possui path."))
            continue
        report.files_checked.append(path)
        category = entry.get("category")
        if path in categories_by_file and categories_by_file[path] != category:
            report.errors.append(_issue("QA_MANIFEST_006", "Arquivo final duplicado com categoria conflitante.", path))
        categories_by_file[path] = str(category)

        final_path = package_dir / path
        if not final_path.exists():
            report.errors.append(_issue("QA_FILE_001", "Arquivo listado no manifest não existe.", path))
            continue
        try:
            real_pages = count_pdf_pages(final_path)
        except (FileNotFoundError, PDFMergeError, Exception) as exc:  # noqa: BLE001 - QA deve agregar falhas técnicas.
            report.errors.append(_issue("QA_FILE_002", f"PDF não abre ou está vazio: {exc}", path))
            continue
        expected_pages = entry.get("page_count")
        if expected_pages != real_pages:
            report.errors.append(_issue("QA_FILE_003", "page_count do manifest diverge do PDF real.", path))

        file_id = str(entry.get("id", ""))
        label = str(entry.get("label", ""))
        confidential = entry.get("confidential")
        is_facilitator_secret = any(token in file_id or token in label.lower() for token in ["dicas", "gabarito"])
        if is_facilitator_secret and confidential is not True:
            report.errors.append(_issue("QA_CONF_001", "Dicas/gabarito devem ser confidential: true.", path))
        if is_facilitator_secret and category == "player":
            report.errors.append(_issue("QA_CONF_002", "Dicas/gabarito não podem estar em category: player.", path))
        if str(file_id).startswith("envelope_") and confidential is not False:
            report.errors.append(_issue("QA_CONF_003", "Envelopes de jogador devem ser confidential: false.", path))

    seen_docs: set[str] = set()
    for doc in manifest.get("documents", []):
        codigo = doc.get("codigo")
        report.documents_checked.append(str(codigo) if codigo else "")
        if not codigo:
            report.errors.append(_issue("QA_DOC_001", "Documento do manifest não possui codigo."))
        elif codigo in seen_docs:
            report.errors.append(_issue("QA_DOC_004", "Documento duplicado no manifest.", document=str(codigo)))
        seen_docs.add(str(codigo))

        final_file = doc.get("final_file")
        if not final_file:
            report.errors.append(_issue("QA_DOC_002", "Documento não aponta para final_file.", document=str(codigo)))
        elif final_file not in manifest_files:
            report.errors.append(_issue("QA_DOC_003", "final_file do documento não existe na lista de arquivos.", str(final_file), str(codigo)))

    html_debug_dir = package_dir / "html_debug"
    if html_debug_dir.exists():
        for html_path in sorted(html_debug_dir.glob("*.html")):
            rel = html_path.relative_to(package_dir).as_posix()
            conteudo = html_path.read_text(encoding="utf-8", errors="ignore")
            if RESIDUO_RE.search(conteudo):
                report.errors.append(_issue("QA_HTML_001", "HTML debug contém resíduo técnico.", rel))

    if not file_entries:
        report.warnings.append(_warn("QA_WARN_001", "Manifest não lista arquivos finais."))

    report.status = "failed" if report.errors else "passed"
    return report

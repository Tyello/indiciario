"""Manifesto de impressão e renderização do guia de impressão."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .merger import get_pdf_orientation_summary
from .renderer import renderizar_documento

PROFILES: dict[str, dict[str, str]] = {
    "economico": {"description": "Sulfite A4 comum, P&B, sem frente e verso."},
    "padrao": {"description": "A4 90g/120g, colorido recomendado nos documentos visuais."},
    "premium": {"description": "Capas em papel kraft, cartões em papel 180g, imagens em papel fotográfico quando houver."},
}


def _pages_text(page_count: int) -> str:
    return "1" if page_count == 1 else f"1-{page_count}"


def _orientation_label(summary: dict[str, Any]) -> str:
    dominant = summary.get("dominant")
    if dominant == "landscape":
        return "Paisagem"
    if dominant == "portrait":
        return "Retrato"
    if dominant == "mixed":
        return "Misto — conferir páginas paisagem"
    return "Conforme arquivo"


def _file_instruction(file_entry: dict[str, Any]) -> dict[str, Any]:
    category = file_entry.get("category")
    file_id = str(file_entry.get("id", ""))
    confidential = bool(file_entry.get("confidential"))
    if category == "player":
        return {
            "paper": "A4 90g ou 120g",
            "color": "Colorido recomendado; P&B aceitável",
            "deliver_to": "Jogadores",
            "instructions": "Entregar no envelope indicado, sem misturar com material confidencial.",
        }
    if file_id == "guia_de_impressao":
        return {
            "paper": "A4 comum",
            "color": "P&B suficiente",
            "deliver_to": "Gráfica/Papelaria",
            "instructions": "Usar como referência de produção do pacote.",
        }
    label = "Não entregar aos jogadores." if confidential else "Separar do material dos jogadores."
    return {
        "paper": "A4 comum",
        "color": "P&B suficiente",
        "deliver_to": "Facilitador",
        "instructions": label,
    }


def build_print_manifest(manifest: dict[str, Any], package_dir: Path | None = None) -> dict[str, Any]:
    """Cria print_manifest.json a partir do manifest do pacote."""
    files = []
    total_pages = 0
    for file_entry in manifest.get("files", []):
        page_count = int(file_entry.get("page_count", 0))
        total_pages += page_count
        orientation = "Conforme arquivo"
        if package_dir is not None:
            pdf_path = package_dir / str(file_entry.get("path", ""))
            if pdf_path.exists():
                orientation = _orientation_label(get_pdf_orientation_summary(pdf_path))
        instructions = _file_instruction(file_entry)
        files.append({
            "file": file_entry.get("path"),
            "label": file_entry.get("label"),
            "pages": _pages_text(page_count),
            "page_count": page_count,
            "copies": 1,
            "paper": instructions["paper"],
            "color": instructions["color"],
            "orientation": orientation,
            "duplex": False,
            "cut_required": False,
            "confidential": bool(file_entry.get("confidential")),
            "deliver_to": instructions["deliver_to"],
            "instructions": instructions["instructions"],
        })

    player_files = [entry["file"] for entry in files if entry["deliver_to"] == "Jogadores"]
    facilitator_files = [entry["file"] for entry in files if entry["deliver_to"] == "Facilitador"]
    return {
        "case_title": manifest.get("case", {}).get("title", "Caso sem título"),
        "generated_at": manifest.get("generated_at") or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "total_files": len(files),
        "total_pages": total_pages,
        "player_files": player_files,
        "facilitator_files": facilitator_files,
        "profiles": PROFILES,
        "files": files,
    }


def write_print_manifest(print_manifest: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(print_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _template_context(print_manifest: dict[str, Any]) -> dict[str, Any]:
    files = []
    for entry in print_manifest.get("files", []):
        files.append({
            **entry,
            "duplex_label": "Sim" if entry.get("duplex") else "Não",
            "cut_label": "Sim" if entry.get("cut_required") else "Não",
            "confidential_label": "Sim" if entry.get("confidential") else "Não",
        })
    profiles = [
        {"name": name.capitalize(), "description": data["description"]}
        for name, data in print_manifest.get("profiles", {}).items()
    ]
    return {
        "CASE_TITLE": print_manifest.get("case_title", "Caso sem título"),
        "GENERATED_AT": print_manifest.get("generated_at", ""),
        "TOTAL_FILES": print_manifest.get("total_files", 0),
        "TOTAL_PAGES": print_manifest.get("total_pages", 0),
        "PLAYER_FILES": ", ".join(print_manifest.get("player_files", [])) or "Nenhum",
        "FACILITATOR_FILES": ", ".join(print_manifest.get("facilitator_files", [])) or "Nenhum",
        "FILES": files,
        "PROFILES": profiles,
    }


def render_print_guide(print_manifest: dict[str, Any], output_path: Path, strict: bool = True) -> Path:
    """Renderiza 05_guia_de_impressao.pdf usando o renderer oficial."""
    return renderizar_documento(
        "print_guide.html",
        _template_context(print_manifest),
        output_path,
        strict=strict,
    )

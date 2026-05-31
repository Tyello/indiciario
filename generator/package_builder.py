"""Orquestrador do pacote final do Indiciário."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .merger import OutputPaths, build_output_paths, count_pdf_pages, merge_pdfs, safe_slug
from .models import Blueprint
from .print_guide import build_print_manifest, render_print_guide, write_print_manifest
from .qa import run_qa, write_qa_report
from .renderer import renderizar_caso
from .validator import BlueprintValidator

class PackageBuildError(RuntimeError):
    """Erro claro para pacotes incompletos ou inconsistentes."""


AUXILIARY_CONFIG: dict[str, dict[str, str | bool]] = {
    "dicas": {
        "id": "dicas_facilitador",
        "label": "Dicas do Facilitador",
        "filename": "dicas_facilitador.pdf",
        "category": "facilitator",
        "confidential": True,
    },
    "gabarito": {
        "id": "gabarito_mestre",
        "label": "Gabarito Mestre",
        "filename": "gabarito_mestre.pdf",
        "category": "facilitator",
        "confidential": True,
    },
}


def _is_envelope_group(group: str) -> bool:
    return bool(re.fullmatch(r"E[1-9]\d*", group))


def _envelope_number(group: str) -> int:
    return int(group[1:])


def _sequenced_envelope_groups(rendered_groups: dict[str, list[Path]]) -> list[str]:
    groups = sorted(
        [group for group, pdfs in rendered_groups.items() if pdfs and _is_envelope_group(group)],
        key=_envelope_number,
    )
    if not groups:
        return []
    numeros = [_envelope_number(group) for group in groups]
    esperado = list(range(1, max(numeros) + 1))
    if numeros != esperado:
        ausentes = [f"E{numero}" for numero in esperado if numero not in numeros]
        raise PackageBuildError(f"Sequência de envelopes com buraco; ausente(s): {', '.join(ausentes)}.")
    return groups


def _numbered_output(package_dir: Path, index: int, basename: str) -> Path:
    return package_dir / f"{index:02d}_{basename}"


def _relative(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _write_manifest(manifest: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _case_metadata(blueprint: Blueprint, case_slug: str) -> dict[str, Any]:
    return {
        "title": blueprint.titulo,
        "slug": case_slug,
        "difficulty": blueprint.dificuldade.value,
        "estimated_minutes": blueprint.tempo_estimado_min,
        "players": blueprint.numero_jogadores,
        "validation_mode": blueprint.modo_validacao.value,
    }


def _build_documents_manifest(
    blueprint: Blueprint,
    rendered_by_code: dict[str, Path],
    final_by_envelope: dict[str, Path],
    package_dir: Path,
) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    current_page_by_file: dict[str, int] = {}
    for doc in blueprint.documentos:
        envelope = doc.envelope
        final_file_path = final_by_envelope.get(envelope)
        source_pdf = rendered_by_code.get(doc.codigo)
        if final_file_path is None or source_pdf is None:
            continue
        final_file = _relative(final_file_path, package_dir)
        source_pages = count_pdf_pages(source_pdf)
        page_start = current_page_by_file.get(final_file, 1)
        page_end = page_start + source_pages - 1
        current_page_by_file[final_file] = page_end + 1
        documents.append({
            "codigo": doc.codigo,
            "titulo": doc.titulo,
            "tipo": doc.tipo.value,
            "envelope": envelope,
            "source_pdf": _relative(source_pdf, package_dir),
            "final_file": final_file,
            "page_start": page_start,
            "page_end": page_end,
        })
    return documents


def _merge_groups(
    rendered_groups: dict[str, list[Path]],
    paths: OutputPaths,
    strict: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Path], list[str]]:
    del strict
    files: list[dict[str, Any]] = []
    final_by_envelope: dict[str, Path] = {}
    warnings: list[str] = []
    package_dir = paths["output_dir"]

    index = 1
    for group in _sequenced_envelope_groups(rendered_groups):
        numero = _envelope_number(group)
        output_path = _numbered_output(package_dir, index, f"envelope_{numero}.pdf")
        paths[f"envelope_{numero}"] = output_path
        merged = merge_pdfs(rendered_groups[group], output_path)
        files.append({
            "id": f"envelope_{numero}",
            "label": f"Envelope {numero}",
            "path": _relative(merged, package_dir),
            "category": "player",
            "confidential": False,
            "page_count": count_pdf_pages(merged),
        })
        final_by_envelope[group] = merged
        index += 1

    for group in ["dicas", "gabarito"]:
        pdfs = rendered_groups.get(group, [])
        config = AUXILIARY_CONFIG[group]
        if not pdfs:
            warnings.append(f"Material '{config['label']}' ausente; arquivo final não gerado.")
            continue
        output_path = _numbered_output(package_dir, index, str(config["filename"]))
        paths[group] = output_path
        merged = merge_pdfs(pdfs, output_path)
        files.append({
            "id": config["id"],
            "label": config["label"],
            "path": _relative(merged, package_dir),
            "category": config["category"],
            "confidential": config["confidential"],
            "page_count": count_pdf_pages(merged),
        })
        index += 1

    paths["guia_de_impressao"] = _numbered_output(package_dir, index, "guia_de_impressao.pdf")
    return files, final_by_envelope, warnings


def _append_print_guide_file(manifest: dict[str, Any], guide_path: Path, package_dir: Path) -> None:
    entry = {
        "id": "guia_de_impressao",
        "label": "Guia de Impressão",
        "path": _relative(guide_path, package_dir),
        "category": "production",
        "confidential": False,
        "page_count": count_pdf_pages(guide_path),
    }
    manifest["files"] = [file for file in manifest.get("files", []) if file.get("id") != "guia_de_impressao"]
    manifest["files"].append(entry)


def build_package(
    blueprint_path: Path,
    output_root: Path = Path("output"),
    strict: bool = True,
) -> dict[str, Any]:
    """Gera pacote final completo a partir de um blueprint válido."""
    blueprint = Blueprint(**json.loads(blueprint_path.read_text(encoding="utf-8")))
    validation = BlueprintValidator(blueprint, strict=strict).validar()
    if not validation.pode_gerar:
        raise RuntimeError(f"Blueprint inválido para geração: {validation.nivel_risco.value}")

    paths = build_output_paths(blueprint.titulo, output_root)
    package_dir = paths["output_dir"]
    paths["rendered_dir"].mkdir(parents=True, exist_ok=True)
    paths["html_debug_dir"].mkdir(parents=True, exist_ok=True)

    rendered_groups = renderizar_caso(blueprint_path, paths["rendered_dir"], strict=strict)
    files, final_by_envelope, warnings = _merge_groups(rendered_groups, paths, strict=strict)
    rendered_by_code = {path.stem: path for group in rendered_groups.values() for path in group}

    manifest: dict[str, Any] = {
        "case": _case_metadata(blueprint, safe_slug(blueprint.titulo)),
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "generated",
        "files": files,
        "documents": _build_documents_manifest(blueprint, rendered_by_code, final_by_envelope, package_dir),
        "warnings": warnings,
    }

    preliminary_print_manifest = build_print_manifest(manifest, package_dir)
    render_print_guide(preliminary_print_manifest, paths["guia_de_impressao"], strict=strict)
    _append_print_guide_file(manifest, paths["guia_de_impressao"], package_dir)

    intermediate_print_manifest = build_print_manifest(manifest, package_dir)
    render_print_guide(intermediate_print_manifest, paths["guia_de_impressao"], strict=strict)
    _append_print_guide_file(manifest, paths["guia_de_impressao"], package_dir)

    final_print_manifest = build_print_manifest(manifest, package_dir)
    write_print_manifest(final_print_manifest, paths["print_manifest"])
    _write_manifest(manifest, paths["manifest"])

    qa_report = run_qa(package_dir, manifest, strict=strict)
    write_qa_report(qa_report, paths["qa_report"])
    if strict and qa_report.status != "passed":
        return {
            "status": "failed",
            "case_slug": manifest["case"]["slug"],
            "output_dir": str(package_dir),
            "manifest_path": str(paths["manifest"]),
            "print_manifest_path": str(paths["print_manifest"]),
            "qa_report_path": str(paths["qa_report"]),
        }

    return {
        "status": qa_report.status,
        "case_slug": manifest["case"]["slug"],
        "output_dir": str(package_dir),
        "manifest_path": str(paths["manifest"]),
        "print_manifest_path": str(paths["print_manifest"]),
        "qa_report_path": str(paths["qa_report"]),
    }

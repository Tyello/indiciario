"""Orquestrador do pacote final do Indiciário."""

from __future__ import annotations

import inspect
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .clue_graph import analyze_clue_graph, build_clue_graph, write_graph_report
from .facilitator_guide import render_facilitator_guide
from .llm_feedback import build_llm_feedback, write_llm_feedback
from .merger import (
    OutputPaths,
    build_output_paths,
    count_pdf_pages,
    merge_pdfs,
    safe_slug,
)
from .playtest_metrics import analyze_playtest, write_playtest_report
from .models import Blueprint
from .printable_cards import build_printable_card_documents
from .print_guide import build_print_manifest, render_print_guide, write_print_manifest
from .qa import report_to_dict, run_qa, write_qa_report
from .renderer import renderizar_caso, renderizar_documento
from .validator import BlueprintValidator
from .visual_procedural import (
    build_visual_documents,
    visual_document_code,
    visual_document_path,
)


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
        [
            group
            for group, pdfs in rendered_groups.items()
            if pdfs and _is_envelope_group(group)
        ],
        key=_envelope_number,
    )
    if not groups:
        return []
    numeros = [_envelope_number(group) for group in groups]
    esperado = list(range(1, max(numeros) + 1))
    if numeros != esperado:
        ausentes = [f"E{numero}" for numero in esperado if numero not in numeros]
        raise PackageBuildError(
            f"Sequência de envelopes com buraco; ausente(s): {', '.join(ausentes)}."
        )
    return groups


def _numbered_output(package_dir: Path, index: int, basename: str) -> Path:
    return package_dir / f"{index:02d}_{basename}"


def _relative(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _write_manifest(manifest: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
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


def _append_document_manifest_entry(
    documents: list[dict[str, Any]],
    current_page_by_file: dict[str, int],
    package_dir: Path,
    final_file_path: Path,
    source_pdf: Path,
    codigo: str,
    titulo: str,
    tipo: str,
    envelope: str,
) -> None:
    final_file = _relative(final_file_path, package_dir)
    source_pages = count_pdf_pages(source_pdf)
    page_start = current_page_by_file.get(final_file, 1)
    page_end = page_start + source_pages - 1
    current_page_by_file[final_file] = page_end + 1
    documents.append(
        {
            "codigo": codigo,
            "titulo": titulo,
            "tipo": tipo,
            "envelope": envelope,
            "source_pdf": _relative(source_pdf, package_dir),
            "final_file": final_file,
            "page_start": page_start,
            "page_end": page_end,
        }
    )


def _build_documents_manifest(
    blueprint: Blueprint,
    rendered_by_code: dict[str, Path],
    final_by_envelope: dict[str, Path],
    package_dir: Path,
    cover_pages_by_envelope: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    cover_pages_by_envelope = cover_pages_by_envelope or {}
    current_page_by_file: dict[str, int] = {}
    for envelope, final_file_path in final_by_envelope.items():
        cover_pages = cover_pages_by_envelope.get(envelope, 0)
        if cover_pages > 0:
            current_page_by_file[_relative(final_file_path, package_dir)] = (
                cover_pages + 1
            )
    for doc in blueprint.documentos:
        envelope = doc.envelope
        final_file_path = final_by_envelope.get(envelope)
        source_pdf = rendered_by_code.get(doc.codigo)
        if final_file_path is None or source_pdf is None:
            continue
        _append_document_manifest_entry(
            documents,
            current_page_by_file,
            package_dir,
            final_file_path,
            source_pdf,
            doc.codigo,
            doc.titulo,
            doc.tipo.value,
            envelope,
        )

    visual = blueprint.visual_procedural
    if visual is None:
        return documents

    rendered_by_name = {path.name: path for path in rendered_by_code.values()}
    for mapa in visual.mapas:
        envelope = mapa.fase or "E1"
        final_file_path = final_by_envelope.get(envelope)
        source_pdf = rendered_by_name.get(
            visual_document_path("map", mapa.id, package_dir).name
        )
        if final_file_path is None or source_pdf is None:
            continue
        _append_document_manifest_entry(
            documents,
            current_page_by_file,
            package_dir,
            final_file_path,
            source_pdf,
            visual_document_code("map", mapa.id),
            mapa.titulo,
            "visual_procedural",
            envelope,
        )
        documents[-1]["orientation"] = mapa.orientacao
        documents[-1]["map_category"] = mapa.categoria
        documents[-1]["print_instructions"] = "Imprimir em A4 paisagem; P&B suficiente."

    return documents


def _envelope_title(group: str) -> str:
    titles = {
        "E1": "Apuração inicial",
        "E2": "Contradições e fechamento",
        "E3": "Material complementar",
    }
    return titles.get(group, "Evidências do envelope")


def _render_envelope_cover(
    blueprint: Blueprint, group: str, paths: OutputPaths, strict: bool = True
) -> Path:
    numero = _envelope_number(group)
    output_path = paths["rendered_dir"] / f"{group}-00_CAPA.pdf"
    dados = {
        "case_name": blueprint.titulo,
        "section_label": f"Envelope {numero}",
        "section_ref": _envelope_title(group),
        "warning_label": "CUSTÓDIA INTERNA",
    }
    html_debug_dir = paths.get("html_debug_dir")
    render_kwargs: dict[str, Any] = {"strict": strict}
    if isinstance(html_debug_dir, Path):
        render_kwargs["html_debug_path"] = html_debug_dir / f"{group}-00_CAPA.html"
    return renderizar_documento(
        "00_envelope_capa.html", dados, output_path, **render_kwargs
    )


def _merge_groups(
    rendered_groups: dict[str, list[Path]],
    paths: OutputPaths,
    blueprint: Blueprint,
    strict: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, int], list[str]]:
    files: list[dict[str, Any]] = []
    final_by_envelope: dict[str, Path] = {}
    cover_pages_by_envelope: dict[str, int] = {}
    warnings: list[str] = []
    package_dir = paths["output_dir"]

    index = 1
    for group in _sequenced_envelope_groups(rendered_groups):
        numero = _envelope_number(group)
        output_path = _numbered_output(package_dir, index, f"envelope_{numero}.pdf")
        paths[f"envelope_{numero}"] = output_path
        cover_path = _render_envelope_cover(blueprint, group, paths, strict=strict)
        cover_pages_by_envelope[group] = count_pdf_pages(cover_path)
        merged = merge_pdfs([cover_path, *rendered_groups[group]], output_path)
        files.append(
            {
                "id": f"envelope_{numero}",
                "label": f"Envelope {numero}",
                "path": _relative(merged, package_dir),
                "category": "player",
                "confidential": False,
                "page_count": count_pdf_pages(merged),
            }
        )
        final_by_envelope[group] = merged
        index += 1

    support_pdfs = rendered_groups.get("apoio_visual", [])
    if support_pdfs:
        output_path = _numbered_output(package_dir, index, "apoio_visual.pdf")
        paths["apoio_visual"] = output_path
        merged = merge_pdfs(support_pdfs, output_path)
        files.append(
            {
                "id": "apoio_visual",
                "label": "Apoio visual — cartões",
                "path": _relative(merged, package_dir),
                "category": "visual_support",
                "confidential": False,
                "page_count": count_pdf_pages(merged),
            }
        )
        index += 1

    for group in ["dicas", "gabarito"]:
        pdfs = rendered_groups.get(group, [])
        config = AUXILIARY_CONFIG[group]
        if not pdfs:
            warnings.append(
                f"Material '{config['label']}' ausente; arquivo final não gerado."
            )
            continue
        output_path = _numbered_output(package_dir, index, str(config["filename"]))
        paths[group] = output_path
        merged = merge_pdfs(pdfs, output_path)
        files.append(
            {
                "id": config["id"],
                "label": config["label"],
                "path": _relative(merged, package_dir),
                "category": config["category"],
                "confidential": config["confidential"],
                "page_count": count_pdf_pages(merged),
            }
        )
        index += 1

    paths["guia_de_impressao"] = _numbered_output(
        package_dir, index, "guia_de_impressao.pdf"
    )
    return files, final_by_envelope, cover_pages_by_envelope, warnings


def _append_facilitator_guide_file(
    manifest: dict[str, Any], guide_path: Path, package_dir: Path
) -> None:
    entry = {
        "id": "guia_facilitador",
        "label": "Guia do Facilitador",
        "path": _relative(guide_path, package_dir),
        "category": "facilitator",
        "confidential": True,
        "page_count": count_pdf_pages(guide_path),
    }
    manifest["files"] = [
        file
        for file in manifest.get("files", [])
        if file.get("id") != "guia_facilitador"
    ]
    manifest["files"].append(entry)



def _append_printable_card_files(
    manifest: dict[str, Any], card_paths: list[Path], package_dir: Path
) -> None:
    existing = {file.get("path") for file in manifest.get("files", [])}
    for path in card_paths:
        relative_path = _relative(path, package_dir)
        if relative_path in existing:
            continue
        label_base = path.stem.replace("cards_", "Cartões — ").replace("_", " ")
        manifest["files"].append(
            {
                "id": f"printable_{path.stem}",
                "label": label_base.capitalize(),
                "path": relative_path,
                "category": "printable_support",
                "confidential": False,
                "page_count": count_pdf_pages(path),
                "cut_required": True,
            }
        )


def _next_file_index(files: list[dict[str, Any]]) -> int:
    return len(files) + 1


def _append_print_guide_file(
    manifest: dict[str, Any], guide_path: Path, package_dir: Path
) -> None:
    entry = {
        "id": "guia_de_impressao",
        "label": "Guia de Impressão",
        "path": _relative(guide_path, package_dir),
        "category": "production",
        "confidential": False,
        "page_count": count_pdf_pages(guide_path),
    }
    manifest["files"] = [
        file
        for file in manifest.get("files", [])
        if file.get("id") != "guia_de_impressao"
    ]
    manifest["files"].append(entry)


def build_package(
    blueprint_path: Path,
    output_root: Path = Path("output"),
    strict: bool = True,
) -> dict[str, Any]:
    """Gera pacote final completo a partir de um blueprint válido."""
    blueprint = Blueprint(**json.loads(blueprint_path.read_text(encoding="utf-8")))
    validation = BlueprintValidator(blueprint, strict=strict).validar()
    paths = build_output_paths(blueprint.titulo, output_root)
    if not validation.pode_gerar:
        feedback = build_llm_feedback(validation)
        write_llm_feedback(feedback, paths["llm_feedback"])
        raise RuntimeError(
            f"Blueprint inválido para geração: {validation.nivel_risco.value}"
        )

    package_dir = paths["output_dir"]
    paths["rendered_dir"].mkdir(parents=True, exist_ok=True)
    paths["html_debug_dir"].mkdir(parents=True, exist_ok=True)

    renderizar_caso_kwargs: dict[str, Any] = {"strict": strict}
    if "html_debug_dir" in inspect.signature(renderizar_caso).parameters:
        renderizar_caso_kwargs["html_debug_dir"] = paths["html_debug_dir"]
    rendered_groups = renderizar_caso(
        blueprint_path, paths["rendered_dir"], **renderizar_caso_kwargs
    )
    build_visual_kwargs: dict[str, Any] = {"strict": strict}
    if "html_debug_dir" in inspect.signature(build_visual_documents).parameters:
        build_visual_kwargs["html_debug_dir"] = paths["html_debug_dir"]
    visual_groups = build_visual_documents(
        blueprint, paths["rendered_dir"], **build_visual_kwargs
    )
    for group, pdfs in visual_groups.items():
        rendered_groups.setdefault(group, []).extend(pdfs)
    files, final_by_envelope, cover_pages_by_envelope, warnings = _merge_groups(
        rendered_groups, paths, blueprint, strict=strict
    )
    rendered_by_code = {
        path.stem: path for group in rendered_groups.values() for path in group
    }
    graph = build_clue_graph(blueprint)
    graph_report = analyze_clue_graph(graph, blueprint)

    printable_card_paths = build_printable_card_documents(
        blueprint,
        package_dir,
        strict=strict,
        html_debug_dir=paths["html_debug_dir"],
        render_func=renderizar_documento,
    )

    manifest: dict[str, Any] = {
        "case": _case_metadata(blueprint, safe_slug(blueprint.titulo)),
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "generated",
        "files": files,
        "documents": _build_documents_manifest(
            blueprint,
            rendered_by_code,
            final_by_envelope,
            package_dir,
            cover_pages_by_envelope,
        ),
        "warnings": warnings,
        "printables": [
            {
                "id": path.stem,
                "path": _relative(path, package_dir),
                "kind": "cards",
                "cut_required": True,
            }
            for path in printable_card_paths
        ],
        "reports": {
            "qa": "qa_report.json",
            "graph": "graph_report.json",
            "llm_feedback": "llm_feedback.json",
            "playtest": "playtest_report.json",
        },
    }

    paths["guia_facilitador"] = _numbered_output(
        package_dir, _next_file_index(manifest["files"]), "guia_facilitador.pdf"
    )
    render_facilitator_guide(
        blueprint, paths["guia_facilitador"], graph_report=graph_report, strict=strict
    )
    _append_facilitator_guide_file(manifest, paths["guia_facilitador"], package_dir)

    paths["guia_de_impressao"] = _numbered_output(
        package_dir, _next_file_index(manifest["files"]), "guia_de_impressao.pdf"
    )
    _append_printable_card_files(manifest, printable_card_paths, package_dir)
    preliminary_print_manifest = build_print_manifest(manifest, package_dir)
    render_print_guide(
        preliminary_print_manifest, paths["guia_de_impressao"], strict=strict
    )
    _append_print_guide_file(manifest, paths["guia_de_impressao"], package_dir)

    intermediate_print_manifest = build_print_manifest(manifest, package_dir)
    render_print_guide(
        intermediate_print_manifest, paths["guia_de_impressao"], strict=strict
    )
    _append_print_guide_file(manifest, paths["guia_de_impressao"], package_dir)

    final_print_manifest = build_print_manifest(manifest, package_dir)
    write_print_manifest(final_print_manifest, paths["print_manifest"])
    _write_manifest(manifest, paths["manifest"])

    write_graph_report(graph_report, paths["graph_report"])

    playtest_report = analyze_playtest(blueprint, graph_report=graph_report)
    write_playtest_report(playtest_report, paths["playtest_report"])

    qa_report = run_qa(package_dir, manifest, strict=strict)
    write_qa_report(qa_report, paths["qa_report"])

    llm_feedback = build_llm_feedback(
        validation, report_to_dict(qa_report), graph_report
    )
    write_llm_feedback(llm_feedback, paths["llm_feedback"])

    qa_ok = qa_report.status == "passed"
    graph_ok = graph_report["status"] in {"passed", "skipped"}

    result = {
        "status": "passed" if qa_ok and graph_ok else "failed",
        "case_slug": manifest["case"]["slug"],
        "output_dir": str(package_dir),
        "manifest_path": str(paths["manifest"]),
        "print_manifest_path": str(paths["print_manifest"]),
        "qa_report_path": str(paths["qa_report"]),
        "graph_report_path": str(paths["graph_report"]),
        "llm_feedback_path": str(paths["llm_feedback"]),
        "playtest_report_path": str(paths["playtest_report"]),
        "qa_status": qa_report.status,
        "graph_status": graph_report["status"],
        "playtest_status": playtest_report["status"],
    }
    if strict and (not qa_ok or not graph_ok):
        return result

    return result

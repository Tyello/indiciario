"""Tests for generator.canonical_quality_gate (ISSUE-30.5).

RED phase: o modulo generator.canonical_quality_gate ainda nao existe -- a
falha esperada nesta fase e ImportError. Ver .ai/issues/ISSUE-30.5_SPEC.md
para a lista de testes obrigatorios e a fonte de calibracao
(docs/DIFFICULTY_FRAMEWORK.md).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from generator.pipeline_runner import run_pipeline

from generator.canonical_quality_gate import (
    CANONICAL_CRITERIA,
    CanonicalQualification,
    CuratorQualification,
    evaluate_for_canonical,
    get_canonical_criteria,
)


AURORA_BLUEPRINT_PATH = Path("examples/caso_canonico_intermediario.json")
FINTECH_BLUEPRINT_PATH = Path("examples/caso_fintech.json")
INICIANTE_B_BLUEPRINT_PATH = Path("examples/caso_canonico_iniciante_b.json")
MIRANTE_BLUEPRINT_PATH = Path("examples/caso_canonico_iniciante.json")

FIXED_CREATED_AT = "2026-06-24T10:00:00Z"


def _load_blueprint_dict(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(path: Path, run_id: str, output_root: Path) -> dict[str, Any]:
    result = run_pipeline(path, run_id, output_root=output_root, created_at=FIXED_CREATED_AT)
    return result.manifest


@pytest.fixture(scope="module")
def aurora_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(AURORA_BLUEPRINT_PATH)


@pytest.fixture(scope="module")
def fintech_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(FINTECH_BLUEPRINT_PATH)


@pytest.fixture(scope="module")
def iniciante_b_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(INICIANTE_B_BLUEPRINT_PATH)


@pytest.fixture(scope="module")
def mirante_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(MIRANTE_BLUEPRINT_PATH)


@pytest.fixture(scope="module")
def aurora_manifest(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("cqg-aurora")
    return _run(AURORA_BLUEPRINT_PATH, "RUN-CQG-AURORA-001", output_root)


@pytest.fixture(scope="module")
def fintech_manifest(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("cqg-fintech")
    return _run(FINTECH_BLUEPRINT_PATH, "RUN-CQG-FINTECH-001", output_root)


@pytest.fixture(scope="module")
def iniciante_b_manifest(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("cqg-iniciante-b")
    return _run(INICIANTE_B_BLUEPRINT_PATH, "RUN-CQG-INICIANTE-B-001", output_root)


@pytest.fixture(scope="module")
def mirante_manifest(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("cqg-mirante")
    return _run(MIRANTE_BLUEPRINT_PATH, "RUN-CQG-MIRANTE-001", output_root)


# === Casos 1-4: qualificacoes reais dos canonicos ===========================


def test_aurora_qualifies_approved_as_intermediario(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    result = evaluate_for_canonical(aurora_blueprint, aurora_manifest, "intermediario")
    assert isinstance(result, CanonicalQualification)
    assert result.qualification == CuratorQualification.APPROVED


def test_fintech_qualifies_approved_as_avancado_despite_low_document_count(
    fintech_blueprint: dict[str, Any], fintech_manifest: dict[str, Any]
) -> None:
    """Fintech tem 16 documentos, fora da faixa informativa avancado (19-24).

    Isso NAO deve bloquear a aprovacao: contagem de documentos e sinal
    informativo, nao criterio duro (ver DIFFICULTY_FRAMEWORK.md)."""
    result = evaluate_for_canonical(fintech_blueprint, fintech_manifest, "avancado")
    assert result.qualification == CuratorQualification.APPROVED
    assert any("documento" in obs.lower() for obs in result.observations)


def test_iniciante_b_qualifies_approved_as_iniciante(
    iniciante_b_blueprint: dict[str, Any], iniciante_b_manifest: dict[str, Any]
) -> None:
    result = evaluate_for_canonical(iniciante_b_blueprint, iniciante_b_manifest, "iniciante")
    assert result.qualification == CuratorQualification.APPROVED


def test_mirante_evaluated_as_iniciante_needs_refinement_documented_exception(
    mirante_blueprint: dict[str, Any], mirante_manifest: dict[str, Any]
) -> None:
    """Mirante (36.568 chars) excede a faixa de densidade de Iniciante.

    Mirante e uma exceção histórica (foi concebido como Intermediário e
    rebaixado por decisão editorial, ja validado como canonico por playtest
    antes deste gate existir). O gate nao decanoniza o Mirante -- so sinaliza
    que um caso *novo* com essa densidade nao se qualificaria automaticamente.
    """
    result = evaluate_for_canonical(mirante_blueprint, mirante_manifest, "iniciante")
    assert result.qualification == CuratorQualification.NEEDS_REFINEMENT
    density_criterion = next(
        c for c in result.criteria_results if c.name == "density_chars"
    )
    assert density_criterion.status == "exceeds_max"


# === Casos 5-8: thresholds sinteticos =======================================


def test_density_exceeding_max_yields_needs_refinement(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    bloated_blueprint = copy.deepcopy(aurora_blueprint)
    huge_doc = {"conteudo": "x" * 100_000}
    bloated_blueprint["documentos"] = list(bloated_blueprint.get("documentos") or []) + [huge_doc]

    result = evaluate_for_canonical(bloated_blueprint, aurora_manifest, "intermediario")
    assert result.qualification == CuratorQualification.NEEDS_REFINEMENT
    density_criterion = next(c for c in result.criteria_results if c.name == "density_chars")
    assert density_criterion.status == "exceeds_max"
    assert density_criterion.recommendation


def test_documents_out_of_informational_range_does_not_block_approval(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    trimmed_blueprint = copy.deepcopy(aurora_blueprint)
    docs = list(trimmed_blueprint.get("documentos") or [])
    trimmed_blueprint["documentos"] = docs[:1]

    result = evaluate_for_canonical(trimmed_blueprint, aurora_manifest, "intermediario")
    # Documentos fora da faixa informativa nao deve, por si so, impedir APPROVED
    # quando os criterios duros (densidade, findings, stages, bloqueios) seguem ok.
    criteria = get_canonical_criteria("intermediario")
    assert len(trimmed_blueprint["documentos"]) < criteria["documents_informational_min"]
    assert result.qualification != CuratorQualification.NOT_READY
    assert any("documento" in obs.lower() for obs in result.observations)


def test_pipeline_status_blocked_yields_not_ready(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    blocked_manifest = copy.deepcopy(aurora_manifest)
    blocked_manifest["pipeline_status"] = "blocked"
    blocked_manifest["gate_outcome"] = {"justification": "GATE_001: bloqueio sintetico."}

    result = evaluate_for_canonical(aurora_blueprint, blocked_manifest, "intermediario")
    assert result.qualification == CuratorQualification.NOT_READY
    pipeline_criterion = next(c for c in result.criteria_results if c.name == "pipeline_status")
    assert pipeline_criterion.status == "blocker"


def test_er_findings_above_max_yields_needs_refinement(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    criteria = get_canonical_criteria("intermediario")
    extra_findings_needed = criteria["findings_er_max"] + 1
    noisy_manifest = copy.deepcopy(aurora_manifest)
    noisy_manifest["findings"] = list(noisy_manifest.get("findings") or []) + [
        {"code": "ER_999", "description": "finding sintetico de teste"}
        for _ in range(extra_findings_needed)
    ]

    result = evaluate_for_canonical(aurora_blueprint, noisy_manifest, "intermediario")
    assert result.qualification == CuratorQualification.NEEDS_REFINEMENT
    er_criterion = next(c for c in result.criteria_results if c.name == "findings_er")
    assert er_criterion.status == "exceeds_max"


# === Casos 9-13: API e dataclasses ==========================================


def test_get_canonical_criteria_returns_correct_thresholds_for_intermediario() -> None:
    criteria = get_canonical_criteria("intermediario")
    assert criteria == CANONICAL_CRITERIA["intermediario"]
    assert criteria["density_chars_min"] < criteria["density_chars_max"]
    assert criteria["stages_completed_min"] == 4


def test_criterion_with_status_ok_is_satisfied(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    result = evaluate_for_canonical(aurora_blueprint, aurora_manifest, "intermediario")
    ok_criteria = [c for c in result.criteria_results if c.status == "ok"]
    assert ok_criteria
    assert all(c.is_satisfied for c in ok_criteria)


def test_criterion_with_status_exceeds_max_has_nonempty_recommendation(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    bloated_blueprint = copy.deepcopy(aurora_blueprint)
    bloated_blueprint["documentos"] = list(bloated_blueprint.get("documentos") or []) + [
        {"conteudo": "x" * 100_000}
    ]
    result = evaluate_for_canonical(bloated_blueprint, aurora_manifest, "intermediario")
    exceeding = [c for c in result.criteria_results if c.status == "exceeds_max"]
    assert exceeding
    assert all(c.recommendation for c in exceeding)


def test_approved_qualification_has_action_if_approved_filled(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    result = evaluate_for_canonical(aurora_blueprint, aurora_manifest, "intermediario")
    assert result.qualification == CuratorQualification.APPROVED
    assert result.action_if_approved


def test_needs_refinement_qualification_has_nonempty_refinement_steps(
    aurora_blueprint: dict[str, Any], aurora_manifest: dict[str, Any]
) -> None:
    bloated_blueprint = copy.deepcopy(aurora_blueprint)
    bloated_blueprint["documentos"] = list(bloated_blueprint.get("documentos") or []) + [
        {"conteudo": "x" * 100_000}
    ]
    result = evaluate_for_canonical(bloated_blueprint, aurora_manifest, "intermediario")
    assert result.qualification == CuratorQualification.NEEDS_REFINEMENT
    assert result.refinement_steps


def test_full_suite_runs_without_collection_errors() -> None:
    """Sentinela de import: garante que o modulo carrega sem efeitos colaterais."""
    assert set(CANONICAL_CRITERIA) == {"iniciante", "intermediario", "avancado"}

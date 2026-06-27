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
    # Pipeline real nao invoca visual_review/accessibility_review: resultado honesto e
    # INCOMPLETE_EVALUATION (nao APPROVED com evidencia nao coletada).
    result = evaluate_for_canonical(aurora_blueprint, aurora_manifest, "intermediario")
    assert isinstance(result, CanonicalQualification)
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION


def test_fintech_qualifies_approved_as_avancado_despite_low_document_count(
    fintech_blueprint: dict[str, Any], fintech_manifest: dict[str, Any]
) -> None:
    """Fintech tem 16 documentos, fora da faixa informativa avancado (19-24).

    Pipeline real nao invoca visual_review/accessibility_review: resultado
    honesto e INCOMPLETE_EVALUATION. Contagem de documentos ainda gera
    observacao informativa (nao bloqueia)."""
    result = evaluate_for_canonical(fintech_blueprint, fintech_manifest, "avancado")
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION
    assert any("documento" in obs.lower() for obs in result.observations)


def test_iniciante_b_qualifies_approved_as_iniciante(
    iniciante_b_blueprint: dict[str, Any], iniciante_b_manifest: dict[str, Any]
) -> None:
    # Pipeline real nao invoca visual_review/accessibility_review: resultado honesto e
    # INCOMPLETE_EVALUATION (nao APPROVED com evidencia nao coletada).
    result = evaluate_for_canonical(iniciante_b_blueprint, iniciante_b_manifest, "iniciante")
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION


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


def test_approved_qualification_has_action_if_approved_filled() -> None:
    # Manifest sintetico completo (com visual_review e accessibility_review)
    # para obter APPROVED legitimo — pipeline real nao invoca esses stages.
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _FULL_MANIFEST, "intermediario")
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


# === ISSUE-30.6: Honestidade de critérios não avaliados =====================
#
# Manifests sintéticos usados pelos testes 1-7.
# Parcial: stages sem visual_review/accessibility_review (pipeline real atual).
# Completo: stages incluem visual_review e accessibility_review.

_PARTIAL_MANIFEST: dict[str, Any] = {
    "pipeline_status": "complete",
    "stages_completed": [
        "blind_solve",
        "gate_evaluation",
        "narrative_review",
        "evidence_review",
    ],
    "findings": [],
    "gate_outcome": {"justification": "ok"},
    "case_ref": "SYNTH-PARTIAL-001",
}

_FULL_MANIFEST: dict[str, Any] = {
    "pipeline_status": "complete",
    "stages_completed": [
        "blind_solve",
        "gate_evaluation",
        "narrative_review",
        "evidence_review",
        "visual_review",
        "accessibility_review",
    ],
    "findings": [],
    "gate_outcome": {"justification": "ok"},
    "case_ref": "SYNTH-FULL-001",
}

# Blueprint sintético com densidade dentro da faixa intermediário [22500, 30500].
_SYNTH_BLUEPRINT: dict[str, Any] = {
    "titulo": "Caso Sintético ISSUE-30.6",
    "dificuldade": "intermediario",
    "documentos": [{"conteudo": "x" * 25000}],
}


def test_vr_criterion_not_evaluated_when_visual_review_absent() -> None:
    """findings_vr_major deve ter status 'not_evaluated' quando visual_review ausente."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _PARTIAL_MANIFEST, "intermediario")
    vr_criterion = next(c for c in result.criteria_results if c.name == "findings_vr_major")
    # Com implementação atual, status é 'ok' (falsa confiança); deve ser 'not_evaluated'.
    assert vr_criterion.status == "not_evaluated"


def test_ar_criterion_not_evaluated_when_accessibility_review_absent() -> None:
    """findings_ar_major deve ter status 'not_evaluated' quando accessibility_review ausente."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _PARTIAL_MANIFEST, "intermediario")
    ar_criterion = next(c for c in result.criteria_results if c.name == "findings_ar_major")
    # Com implementação atual, status é 'ok' (falsa confiança); deve ser 'not_evaluated'.
    assert ar_criterion.status == "not_evaluated"


def test_partial_manifest_yields_incomplete_evaluation() -> None:
    """Manifest sem visual_review/accessibility_review deve produzir INCOMPLETE_EVALUATION."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _PARTIAL_MANIFEST, "intermediario")
    # CuratorQualification.INCOMPLETE_EVALUATION ainda não existe → AttributeError.
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION


def test_incomplete_evaluation_names_unevaluated_criteria() -> None:
    """INCOMPLETE_EVALUATION enumera os critérios não avaliados no feedback."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _PARTIAL_MANIFEST, "intermediario")
    # CuratorQualification.INCOMPLETE_EVALUATION ainda não existe → AttributeError.
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION
    feedback = result.detailed_feedback + result.summary
    assert "not_evaluated" in feedback or "visual" in feedback or "accessibility" in feedback


def test_full_manifest_can_still_be_approved() -> None:
    """Manifest completo (com visual_review e accessibility_review) pode ser APPROVED."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _FULL_MANIFEST, "intermediario")
    assert result.qualification == CuratorQualification.APPROVED
    # Referência ao enum novo (ainda ausente) → AttributeError.
    assert result.qualification != CuratorQualification.INCOMPLETE_EVALUATION


def test_not_evaluated_does_not_count_as_out_of_range() -> None:
    """Critério not_evaluated não gera NEEDS_REFINEMENT (não é out_of_range)."""
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, _PARTIAL_MANIFEST, "intermediario")
    # Não deve confundir 'not_evaluated' com 'exceeds_max/below_min'.
    assert result.qualification != CuratorQualification.NEEDS_REFINEMENT
    # Deve ser INCOMPLETE_EVALUATION — referência ao enum novo → AttributeError.
    assert result.qualification == CuratorQualification.INCOMPLETE_EVALUATION


def test_blocker_precedes_incomplete_evaluation() -> None:
    """Pipeline bloqueada tem precedência: NOT_READY supera INCOMPLETE_EVALUATION."""
    blocked_partial: dict[str, Any] = {
        "pipeline_status": "blocked",
        "stages_completed": ["blind_solve", "gate_evaluation"],
        "findings": [],
        "gate_outcome": {"justification": "GATE_001: bloqueio sintetico."},
        "case_ref": "SYNTH-BLOCKED-001",
    }
    result = evaluate_for_canonical(_SYNTH_BLUEPRINT, blocked_partial, "intermediario")
    assert result.qualification == CuratorQualification.NOT_READY
    # INCOMPLETE_EVALUATION não deve surgir quando há bloqueio.
    # Referência ao enum novo → AttributeError se ainda não implementado.
    assert result.qualification != CuratorQualification.INCOMPLETE_EVALUATION

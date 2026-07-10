"""Tests for generator.quality_comparative_reviewer (ISSUE-29+30, STEP-05).

RED phase: casos 1-8 da spec (.ai/issues/ISSUE-29+30_SPEC.md, secao "Testes
obrigatorios"). O modulo generator.quality_comparative_reviewer ainda nao
existe -- a falha esperada nesta fase e ImportError.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from generator.pipeline_runner import run_pipeline

# Modulo sob teste -- ainda nao existe (RED esperado: ImportError).
from generator.quality_comparative_reviewer import (
    CaseMetrics,
    QualityComparativeReport,
    generate_quality_report,
    validate_quality_comparative_report,
)


AURORA_BLUEPRINT_PATH = Path("examples/caso_canonico_intermediario.json")
FINTECH_BLUEPRINT_PATH = Path("examples/caso_fintech.json")

AURORA_RUN_ID = "RUN-QUALITY-AURORA-TEST-001"
FINTECH_RUN_ID = "RUN-QUALITY-FINTECH-TEST-001"
FIXED_CREATED_AT = "2026-06-23T10:00:00Z"


def _load_blueprint_dict(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def aurora_run(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("aurora-pipeline-output")
    result = run_pipeline(
        AURORA_BLUEPRINT_PATH,
        AURORA_RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    return result.manifest


@pytest.fixture(scope="module")
def fintech_run(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    output_root = tmp_path_factory.mktemp("fintech-pipeline-output")
    result = run_pipeline(
        FINTECH_BLUEPRINT_PATH,
        FINTECH_RUN_ID,
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )
    return result.manifest


@pytest.fixture(scope="module")
def aurora_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(AURORA_BLUEPRINT_PATH)


@pytest.fixture(scope="module")
def fintech_blueprint() -> dict[str, Any]:
    return _load_blueprint_dict(FINTECH_BLUEPRINT_PATH)


# === Casos 1-8: derivacao de metricas =======================================


def test_case_metrics_derived_from_aurora_manifest_has_all_fields(
    aurora_run: dict[str, Any], aurora_blueprint: dict[str, Any]
) -> None:
    """Caso 1: CaseMetrics derivado de RunManifest Aurora -- todos os campos
    preenchidos corretamente."""
    report = generate_quality_report(
        aurora_run, aurora_run, aurora_blueprint, aurora_blueprint
    )
    metrics = report.aurora_metrics

    assert isinstance(metrics, CaseMetrics)
    assert metrics.case_name == aurora_blueprint["titulo"]
    assert metrics.case_ref == aurora_run["case_ref"]
    assert metrics.dificuldade_esperada == aurora_blueprint["dificuldade"]
    assert metrics.pipeline_status == aurora_run["pipeline_status"]
    assert metrics.stages_completed == len(aurora_run["stages_completed"])
    assert metrics.findings_count == len(aurora_run["findings"])
    assert isinstance(metrics.findings_by_type, dict)
    assert isinstance(metrics.notes, str)


def test_case_metrics_derived_from_fintech_manifest_has_all_fields(
    fintech_run: dict[str, Any], fintech_blueprint: dict[str, Any]
) -> None:
    """Caso 2: CaseMetrics derivado de RunManifest Fintech -- corretamente."""
    report = generate_quality_report(
        fintech_run, fintech_run, fintech_blueprint, fintech_blueprint
    )
    metrics = report.fintech_metrics

    assert isinstance(metrics, CaseMetrics)
    assert metrics.case_name == fintech_blueprint["titulo"]
    assert metrics.case_ref == fintech_run["case_ref"]
    assert metrics.dificuldade_esperada == fintech_blueprint["dificuldade"]
    assert metrics.pipeline_status == fintech_run["pipeline_status"]
    assert metrics.stages_completed == len(fintech_run["stages_completed"])
    assert metrics.findings_count == len(fintech_run["findings"])
    assert isinstance(metrics.findings_by_type, dict)
    assert isinstance(metrics.notes, str)


def test_findings_by_type_groups_by_code_prefix(
    fintech_run: dict[str, Any], fintech_blueprint: dict[str, Any]
) -> None:
    """Caso 3: findings_by_type agrupa corretamente NR_*, ER_*, VR_*, AR_*.

    O manifest Fintech real (STEP-04) tem 0 NR e 4 ER (ER_006 x2, ER_007 x2).
    """
    report = generate_quality_report(
        fintech_run, fintech_run, fintech_blueprint, fintech_blueprint
    )
    metrics = report.fintech_metrics

    assert set(metrics.findings_by_type) <= {"NR_*", "ER_*", "VR_*", "AR_*"}
    assert metrics.findings_by_type.get("NR_*", 0) == 0
    assert metrics.findings_by_type.get("ER_*", 0) == 4
    assert metrics.findings_by_type.get("VR_*", 0) == 0
    assert metrics.findings_by_type.get("AR_*", 0) == 0
    assert sum(metrics.findings_by_type.values()) == metrics.findings_count


def test_density_documental_equals_sum_of_content_lengths(
    aurora_run: dict[str, Any], aurora_blueprint: dict[str, Any]
) -> None:
    """Caso 4: density_documental == soma de len(conteudo) de todos docs."""
    report = generate_quality_report(
        aurora_run, aurora_run, aurora_blueprint, aurora_blueprint
    )

    expected_density = sum(
        len(str(doc["conteudo"])) for doc in aurora_blueprint["documentos"]
    )

    density_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "densidade_documental"
    ]
    assert density_comparisons, "esperado comparison 'densidade_documental'"
    assert density_comparisons[0].aurora_value == expected_density


def test_blocked_by_is_none_when_pipeline_status_complete(
    aurora_run: dict[str, Any], aurora_blueprint: dict[str, Any]
) -> None:
    """Caso 5: blocked_by == null se pipeline_status: complete, senao rule."""
    assert aurora_run["pipeline_status"] == "complete"

    report = generate_quality_report(
        aurora_run, aurora_run, aurora_blueprint, aurora_blueprint
    )
    assert report.aurora_metrics.blocked_by is None


def test_blocked_by_is_rule_when_pipeline_status_blocked(
    aurora_run: dict[str, Any], aurora_blueprint: dict[str, Any]
) -> None:
    """Caso 5 (complemento): pipeline_status != complete -> blocked_by preenchido."""
    blocked_manifest = copy.deepcopy(aurora_run)
    blocked_manifest["pipeline_status"] = "blocked"
    blocked_manifest["gate_outcome"] = {
        "decision_id": "DEC-BLOCKED-TEST-001",
        "outcome": "rejected",
        "justification": "GATE_001: bloqueio sintetico para teste.",
    }

    report = generate_quality_report(
        blocked_manifest, aurora_run, aurora_blueprint, aurora_blueprint
    )
    assert report.aurora_metrics.pipeline_status == "blocked"
    assert report.aurora_metrics.blocked_by is not None
    assert isinstance(report.aurora_metrics.blocked_by, str)


def test_dificuldade_vs_esperada_derived_from_expected_vs_actual(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 6: dificuldade_vs_esperada derivado comparando expected vs actual."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    dificuldade_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "dificuldade_vs_esperada"
    ]
    assert dificuldade_comparisons, "esperado comparison 'dificuldade_vs_esperada'"
    comparison = dificuldade_comparisons[0]
    assert comparison.aurora_value in ("alinhada", "mais_facil", "mais_dificil")
    assert comparison.fintech_value in ("alinhada", "mais_facil", "mais_dificil")


def test_generate_quality_report_does_not_mutate_inputs(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 7: generate_quality_report nao muta as entradas (deepcopy check)."""
    aurora_run_before = copy.deepcopy(aurora_run)
    aurora_blueprint_before = copy.deepcopy(aurora_blueprint)
    fintech_run_before = copy.deepcopy(fintech_run)
    fintech_blueprint_before = copy.deepcopy(fintech_blueprint)

    generate_quality_report(aurora_run, fintech_run, aurora_blueprint, fintech_blueprint)

    assert aurora_run == aurora_run_before
    assert aurora_blueprint == aurora_blueprint_before
    assert fintech_run == fintech_run_before
    assert fintech_blueprint == fintech_blueprint_before


def test_generated_report_passes_validate_quality_comparative_report(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 8: relatorio gerado passa validate_quality_comparative_report."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )
    assert isinstance(report, QualityComparativeReport)

    errors = validate_quality_comparative_report(report)
    assert errors == []


# === Casos 9-14: comparacao entre dois casos ================================
#
# Codigos de vazamento de informacao (ER_006/ER_007/ER_008) conforme spec
# (.ai/issues/ISSUE-29+30_SPEC.md, tabela "MetricComparison").
_VAZAMENTO_INFO_CODES = ("ER_006", "ER_007", "ER_008")


def _count_vazamento_info(manifest: dict[str, Any]) -> int:
    """Conta findings cujo code esta em _VAZAMENTO_INFO_CODES."""
    findings = manifest.get("findings") or []
    return sum(
        1 for finding in findings if finding.get("code") in _VAZAMENTO_INFO_CODES
    )


def test_metric_comparison_densidade_documental_direction_lower_is_better(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 9: MetricComparison para densidade_documental -- direction
    'lower_is_better' (menos texto compacto = melhor jogabilidade)."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    density_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "densidade_documental"
    ]
    assert density_comparisons, "esperado comparison 'densidade_documental'"
    comparison = density_comparisons[0]
    assert comparison.direction == "lower_is_better"


def test_metric_comparison_vazamento_info_matches_real_finding_counts(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 10: MetricComparison para vazamento_info -- contagem real de
    findings ER_006/ER_007/ER_008 em cada manifest (STEP-04: Fintech tem 4
    findings ER_006/ER_007; Aurora tem 3 findings ER_007, conforme
    docs/AURORA_PIPELINE_RUN.md). A spec usa "Aurora 3, Fintech 2" como
    exemplo ilustrativo -- este teste confere os valores reais observados,
    nao o exemplo da spec.
    """
    expected_aurora = _count_vazamento_info(aurora_run)
    expected_fintech = _count_vazamento_info(fintech_run)

    # Valores reais documentados: Aurora 3 (ER_007 x3), Fintech 4
    # (ER_006 x2 + ER_007 x2). Confirma que a contagem derivada do manifest
    # bate com a documentacao existente antes de exigi-la do relatorio.
    assert expected_aurora == 3
    assert expected_fintech == 4

    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    vazamento_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "vazamento_info"
    ]
    assert vazamento_comparisons, "esperado comparison 'vazamento_info'"
    comparison = vazamento_comparisons[0]
    assert comparison.aurora_value == expected_aurora
    assert comparison.fintech_value == expected_fintech
    assert comparison.direction == "lower_is_better"


def test_metric_comparison_visual_score_present_and_comparable(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 11: MetricComparison para visual_score -- ambos comparaveis.

    pipeline_runner.py nao chama o visual reviewer (confirmado em
    STEP-01_EXECUTION.md), logo VR_* sempre sera 0 em ambos os manifests
    reais. O teste reflete essa limitacao real da pipeline (nao o exemplo
    hipotetico "ambos positivos" da spec): valor 0/0 e o resultado correto
    e esperado, nao uma falha de cobertura.
    """
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    visual_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "visual_score"
    ]
    assert visual_comparisons, "esperado comparison 'visual_score'"
    comparison = visual_comparisons[0]
    assert isinstance(comparison.aurora_value, (int, float))
    assert isinstance(comparison.fintech_value, (int, float))
    assert comparison.aurora_value == 0
    assert comparison.fintech_value == 0


def test_metric_comparison_pacing_both_complete_aligned(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 12: MetricComparison para pacing -- ambos completaram (4/4
    stages), espera-se 'alinhada' na interpretacao."""
    assert len(aurora_run["stages_completed"]) == 4
    assert len(fintech_run["stages_completed"]) == 4

    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    pacing_comparisons = [
        comparison
        for comparison in report.comparisons
        if comparison.metric_name == "pacing"
    ]
    assert pacing_comparisons, "esperado comparison 'pacing'"
    comparison = pacing_comparisons[0]
    assert comparison.aurora_value == pytest.approx(1.0)
    assert comparison.fintech_value == pytest.approx(1.0)
    assert "alinhada" in comparison.interpretation.lower()


def test_report_consolidates_at_least_six_comparisons(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 13: relatorio consolida ~6-8 metricas de comparacao."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )
    assert len(report.comparisons) >= 6


def test_observations_and_recommendations_are_non_empty(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 14: observations e recommendations sao strings/tuplas nao vazias."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    assert isinstance(report.observations, str)
    assert report.observations.strip() != ""

    assert isinstance(report.recommendations, tuple)
    assert len(report.recommendations) > 0
    assert all(isinstance(item, str) and item.strip() for item in report.recommendations)


# === Casos 15-17: integracao Aurora+Fintech ==================================


def test_running_both_pipelines_then_generating_report_raises_no_exception(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 15: rodar Aurora + rodar Fintech, depois generate_quality_report
    -- sem excecao. As fixtures aurora_run/fintech_run ja executam
    run_pipeline (generator.pipeline_runner.run_pipeline) sobre os dois
    blueprints reais; este teste confirma que o encadeamento completo
    (duas pipelines + geracao do relatorio) nao levanta excecao.
    """
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )
    assert isinstance(report, QualityComparativeReport)


def test_report_mentions_aurora_and_fintech_case_names(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 16: relatorio menciona caso Aurora e Fintech por nome
    (case_name nas metricas de cada lado)."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )

    assert report.aurora_metrics.case_name == aurora_blueprint["titulo"]
    assert report.fintech_metrics.case_name == fintech_blueprint["titulo"]
    assert report.aurora_metrics.case_name in report.observations
    assert report.fintech_metrics.case_name in report.observations


def test_comparisons_has_at_least_five_metrics(
    aurora_run: dict[str, Any],
    aurora_blueprint: dict[str, Any],
    fintech_run: dict[str, Any],
    fintech_blueprint: dict[str, Any],
) -> None:
    """Caso 17: comparisons tem pelo menos 5 metricas (complementar ao
    caso 13, que exige >= 6 -- mantido como assert independente conforme
    a spec lista os dois criterios separadamente)."""
    report = generate_quality_report(
        aurora_run, fintech_run, aurora_blueprint, fintech_blueprint
    )
    assert len(report.comparisons) >= 5


# Caso 18 ("pytest tests/ -q sem regressao, 1295+ testes") e um criterio de
# aceitacao da spec verificado externamente no STEP-11 (suite completa), nao
# um teste unitario deste arquivo. Roda-lo aqui como
# subprocess.run(["pytest", "tests/", "-q"]) dentro de um teste seria
# recursivo (a propria execucao de "pytest tests/ -q" inclui este arquivo) e
# nao agrega cobertura nova -- por isso nao ha funcao de teste para o caso 18
# neste arquivo.

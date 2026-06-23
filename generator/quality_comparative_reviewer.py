"""Quality Comparative Reviewer (ISSUE-29+30).

Builds a :class:`QualityComparativeReport` comparing the Aurora canonical
case against the Fintech case, deriving per-case metrics from a
``RunManifest`` dict (see ``generator.run_manifest``) and a Blueprint dict
(see ``generator.models``). Never mutates its inputs.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

__all__ = [
    "CaseMetrics",
    "MetricComparison",
    "QualityComparativeReport",
    "generate_quality_report",
    "validate_quality_comparative_report",
]

# Length of the finding code prefix used to group findings_by_type
# (e.g. "ER_006" -> "ER", grouped as "ER_*"). Codes follow the
# <PREFIX>_<NNN> convention established by the existing reviewers
# (narrative_reviewer, evidence_reviewer, visual_reviewer,
# accessibility_reviewer).
_FINDING_CODE_PREFIX_LEN = 2

_FINDING_TYPE_KEYS: tuple[str, ...] = ("NR_*", "ER_*", "VR_*", "AR_*")

_PIPELINE_STATUS_COMPLETE = "complete"

_DIFICULDADE_ALINHADA = "alinhada"
_DIFICULDADE_MAIS_FACIL = "mais_facil"
_DIFICULDADE_MAIS_DIFICIL = "mais_dificil"

# Ordering used to compare dificuldade_esperada (expected) vs the case's own
# expected value when contrasting Aurora against Fintech.
_DIFICULDADE_ORDER: dict[str, int] = {
    "iniciante": 0,
    "intermediario": 1,
    "avancado": 2,
}

# Codigos de finding que indicam vazamento de informacao do gabarito
# (ER_006/ER_007/ER_008), conforme ISSUE-29+30_SPEC.md tabela
# "MetricComparison".
_VAZAMENTO_INFO_CODES = ("ER_006", "ER_007", "ER_008")

# Prefixo do code usado pelo visual reviewer (VR_*).
_VISUAL_FINDING_PREFIX = "VR"

# Numero de stages que uma pipeline completa precisa percorrer
# (run_manifest.py: blind_solve, gate_evaluate, narrative_review,
# evidence_review).
_TOTAL_PIPELINE_STAGES = 4


@dataclass(frozen=True)
class CaseMetrics:
    case_name: str
    case_ref: str
    dificuldade_esperada: str
    pipeline_status: str
    stages_completed: int
    findings_count: int
    findings_by_type: dict[str, int]
    blocked_by: str | None
    notes: str


@dataclass(frozen=True)
class MetricComparison:
    metric_name: str
    aurora_value: str | int | float
    fintech_value: str | int | float
    direction: str
    interpretation: str


@dataclass(frozen=True)
class QualityComparativeReport:
    generated_at: str
    aurora_metrics: CaseMetrics
    fintech_metrics: CaseMetrics
    comparisons: tuple[MetricComparison, ...]
    observations: str
    recommendations: tuple[str, ...]


def _now_iso() -> str:
    """Return the current UTC instant as an ISO 8601 ``...Z`` timestamp."""

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _findings_by_type(findings: list[Mapping[str, Any]]) -> dict[str, int]:
    """Group findings by their code prefix (e.g. ``ER_006`` -> ``ER_*``)."""

    counts: dict[str, int] = {key: 0 for key in _FINDING_TYPE_KEYS}
    for finding in findings:
        code = str(finding.get("code") or "")
        prefix = code[:_FINDING_CODE_PREFIX_LEN]
        type_key = f"{prefix}_*"
        if type_key in counts:
            counts[type_key] += 1
        else:
            counts[type_key] = counts.get(type_key, 0) + 1
    return counts


def _blocked_by(manifest: Mapping[str, Any]) -> str | None:
    """Derive ``blocked_by`` from a manifest's pipeline_status/gate_outcome.

    ``None`` when pipeline_status is ``complete``. Otherwise extracts the
    rule code from ``gate_outcome.justification`` (format ``"RULE: text"``,
    e.g. ``"GATE_001: bloqueio sintetico."``). Falls back to the raw
    justification, or to the pipeline_status itself when no gate_outcome is
    available.
    """

    if manifest.get("pipeline_status") == _PIPELINE_STATUS_COMPLETE:
        return None

    gate_outcome = manifest.get("gate_outcome")
    if gate_outcome:
        justification = gate_outcome.get("justification")
        if justification:
            rule, _, _rest = str(justification).partition(":")
            return rule.strip() if rule else str(justification)

    return str(manifest.get("pipeline_status"))


def _case_metrics(
    manifest: Mapping[str, Any], blueprint: Mapping[str, Any]
) -> CaseMetrics:
    findings = list(manifest.get("findings") or [])
    stages_completed = list(manifest.get("stages_completed") or [])

    return CaseMetrics(
        case_name=blueprint.get("titulo", ""),
        case_ref=manifest.get("case_ref", ""),
        dificuldade_esperada=blueprint.get("dificuldade", ""),
        pipeline_status=manifest.get("pipeline_status", ""),
        stages_completed=len(stages_completed),
        findings_count=len(findings),
        findings_by_type=_findings_by_type(findings),
        blocked_by=_blocked_by(manifest),
        notes="",
    )


def _densidade_documental_comparison(
    aurora_blueprint: Mapping[str, Any], fintech_blueprint: Mapping[str, Any]
) -> MetricComparison:
    aurora_value = sum(
        len(str(doc["conteudo"])) for doc in aurora_blueprint.get("documentos") or []
    )
    fintech_value = sum(
        len(str(doc["conteudo"])) for doc in fintech_blueprint.get("documentos") or []
    )
    return MetricComparison(
        metric_name="densidade_documental",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="lower_is_better",
        interpretation=(
            "Soma dos comprimentos de conteudo dos documentos de cada caso. "
            "Menos texto compacto favorece a jogabilidade."
        ),
    )


def _dificuldade_vs_esperada(
    blueprint: Mapping[str, Any], outro_blueprint: Mapping[str, Any]
) -> str:
    """Compare a case's expected difficulty against the other case's.

    Returns ``"alinhada"`` when both blueprints declare the same
    dificuldade, ``"mais_facil"`` when this case's dificuldade ranks below
    the other case's, ``"mais_dificil"`` when it ranks above.
    """

    own_rank = _DIFICULDADE_ORDER.get(blueprint.get("dificuldade", ""), -1)
    other_rank = _DIFICULDADE_ORDER.get(outro_blueprint.get("dificuldade", ""), -1)

    if own_rank == other_rank:
        return _DIFICULDADE_ALINHADA
    if own_rank < other_rank:
        return _DIFICULDADE_MAIS_FACIL
    return _DIFICULDADE_MAIS_DIFICIL


def _dificuldade_vs_esperada_comparison(
    aurora_blueprint: Mapping[str, Any], fintech_blueprint: Mapping[str, Any]
) -> MetricComparison:
    aurora_value = _dificuldade_vs_esperada(aurora_blueprint, fintech_blueprint)
    fintech_value = _dificuldade_vs_esperada(fintech_blueprint, aurora_blueprint)
    return MetricComparison(
        metric_name="dificuldade_vs_esperada",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="neutral",
        interpretation=(
            "Dificuldade declarada de cada caso comparada com a do outro caso."
        ),
    )


def _count_findings_matching(
    manifest: Mapping[str, Any], predicate: Callable[[str], bool]
) -> int:
    """Count findings in ``manifest`` whose ``code`` satisfies ``predicate``."""

    findings = list(manifest.get("findings") or [])
    return sum(
        1 for finding in findings if predicate(str(finding.get("code") or ""))
    )


def _count_vazamento_info(manifest: Mapping[str, Any]) -> int:
    """Count findings whose code is ER_006, ER_007 or ER_008.

    These codes flag vazamento de informacao do gabarito para o jogador
    (ISSUE-29+30_SPEC.md, tabela "MetricComparison").
    """

    return _count_findings_matching(
        manifest, lambda code: code in _VAZAMENTO_INFO_CODES
    )


def _vazamento_info_comparison(
    aurora_manifest: Mapping[str, Any], fintech_manifest: Mapping[str, Any]
) -> MetricComparison:
    aurora_value = _count_vazamento_info(aurora_manifest)
    fintech_value = _count_vazamento_info(fintech_manifest)
    return MetricComparison(
        metric_name="vazamento_info",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="lower_is_better",
        interpretation=(
            "Quantidade de findings ER_006/ER_007/ER_008 (vazamento de "
            "informacao do gabarito) detectados em cada caso."
        ),
    )


def _count_visual_score(manifest: Mapping[str, Any]) -> int:
    """Count findings whose code starts with the visual reviewer prefix."""

    return _count_findings_matching(
        manifest, lambda code: code.startswith(_VISUAL_FINDING_PREFIX)
    )


def _visual_score_comparison(
    aurora_manifest: Mapping[str, Any], fintech_manifest: Mapping[str, Any]
) -> MetricComparison:
    aurora_value = _count_visual_score(aurora_manifest)
    fintech_value = _count_visual_score(fintech_manifest)
    return MetricComparison(
        metric_name="visual_score",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="lower_is_better",
        interpretation=(
            "Quantidade de findings VR_* (visual reviewer) detectados em "
            "cada caso. pipeline_runner.py nao invoca o visual reviewer "
            "hoje, logo 0/0 e o resultado real e esperado."
        ),
    )


def _pacing_comparison(
    aurora_metrics: CaseMetrics, fintech_metrics: CaseMetrics
) -> MetricComparison:
    aurora_value = aurora_metrics.stages_completed / _TOTAL_PIPELINE_STAGES
    fintech_value = fintech_metrics.stages_completed / _TOTAL_PIPELINE_STAGES

    if aurora_value == fintech_value:
        alinhamento = _DIFICULDADE_ALINHADA
    elif aurora_value < fintech_value:
        alinhamento = _DIFICULDADE_MAIS_FACIL
    else:
        alinhamento = _DIFICULDADE_MAIS_DIFICIL

    return MetricComparison(
        metric_name="pacing",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="neutral",
        interpretation=(
            f"Fracao de stages completados (stages_completed / "
            f"{_TOTAL_PIPELINE_STAGES}) em cada caso: progressao "
            f"{alinhamento}."
        ),
    )


def _num_documentos_total_comparison(
    aurora_blueprint: Mapping[str, Any], fintech_blueprint: Mapping[str, Any]
) -> MetricComparison:
    aurora_value = len(aurora_blueprint.get("documentos") or [])
    fintech_value = len(fintech_blueprint.get("documentos") or [])
    return MetricComparison(
        metric_name="num_documentos_total",
        aurora_value=aurora_value,
        fintech_value=fintech_value,
        direction="neutral",
        interpretation=(
            "Numero total de documentos presentes no blueprint de cada "
            "caso."
        ),
    )


def _comparison_by_name(
    comparisons: tuple[MetricComparison, ...], metric_name: str
) -> MetricComparison | None:
    for comparison in comparisons:
        if comparison.metric_name == metric_name:
            return comparison
    return None


def _build_observations(
    aurora_metrics: CaseMetrics,
    fintech_metrics: CaseMetrics,
    comparisons: tuple[MetricComparison, ...],
) -> str:
    """Build a narrative summary grounded in the computed metrics/values."""

    vazamento = _comparison_by_name(comparisons, "vazamento_info")
    densidade = _comparison_by_name(comparisons, "densidade_documental")
    pacing = _comparison_by_name(comparisons, "pacing")

    parts = [
        f"Comparativo entre '{aurora_metrics.case_name}' (Aurora, dificuldade "
        f"{aurora_metrics.dificuldade_esperada}) e '{fintech_metrics.case_name}' "
        f"(Fintech, dificuldade {fintech_metrics.dificuldade_esperada}).",
        f"Aurora completou pipeline_status='{aurora_metrics.pipeline_status}' "
        f"com {aurora_metrics.findings_count} findings; Fintech completou "
        f"pipeline_status='{fintech_metrics.pipeline_status}' com "
        f"{fintech_metrics.findings_count} findings.",
    ]

    if vazamento is not None:
        parts.append(
            f"Vazamento de informacao (ER_006/ER_007/ER_008): Aurora "
            f"{vazamento.aurora_value}, Fintech {vazamento.fintech_value}."
        )
    if densidade is not None:
        parts.append(
            f"Densidade documental: Aurora {densidade.aurora_value} "
            f"caracteres, Fintech {densidade.fintech_value} caracteres."
        )
    if pacing is not None:
        parts.append(
            f"Pacing (stages completados): Aurora {pacing.aurora_value:.2f}, "
            f"Fintech {pacing.fintech_value:.2f}."
        )

    return " ".join(parts)


def _build_recommendations(
    aurora_metrics: CaseMetrics,
    fintech_metrics: CaseMetrics,
    comparisons: tuple[MetricComparison, ...],
) -> tuple[str, ...]:
    """Build actionable recommendations derived from the comparisons."""

    recommendations: list[str] = []

    vazamento = _comparison_by_name(comparisons, "vazamento_info")
    if vazamento is not None:
        maior_caso, maior_valor = (
            (fintech_metrics.case_name, vazamento.fintech_value)
            if vazamento.fintech_value > vazamento.aurora_value
            else (aurora_metrics.case_name, vazamento.aurora_value)
        )
        if maior_valor > 0:
            recommendations.append(
                f"Revisar vazamentos de informacao (ER_006/ER_007/ER_008) "
                f"em '{maior_caso}', caso com maior incidencia "
                f"({maior_valor})."
            )

    densidade = _comparison_by_name(comparisons, "densidade_documental")
    if densidade is not None and densidade.aurora_value != densidade.fintech_value:
        mais_denso = (
            aurora_metrics.case_name
            if densidade.aurora_value > densidade.fintech_value
            else fintech_metrics.case_name
        )
        recommendations.append(
            f"Considerar reduzir a densidade documental de '{mais_denso}' "
            f"para manter a leitura acessivel em mesa."
        )

    if aurora_metrics.blocked_by is not None:
        recommendations.append(
            f"Investigar bloqueio em '{aurora_metrics.case_name}': "
            f"{aurora_metrics.blocked_by}."
        )
    if fintech_metrics.blocked_by is not None:
        recommendations.append(
            f"Investigar bloqueio em '{fintech_metrics.case_name}': "
            f"{fintech_metrics.blocked_by}."
        )

    if not recommendations:
        recommendations.append(
            "Nenhuma acao corretiva critica identificada; manter "
            "monitoramento das metricas em proximas runs."
        )

    return tuple(recommendations)


def generate_quality_report(
    aurora_manifest: Mapping[str, Any],
    fintech_manifest: Mapping[str, Any],
    aurora_blueprint: Mapping[str, Any],
    fintech_blueprint: Mapping[str, Any],
) -> QualityComparativeReport:
    """Build a :class:`QualityComparativeReport` from manifests/blueprints.

    Never mutates any of its inputs (deep-copies them internally first).
    """

    aurora_manifest = copy.deepcopy(dict(aurora_manifest))
    fintech_manifest = copy.deepcopy(dict(fintech_manifest))
    aurora_blueprint = copy.deepcopy(dict(aurora_blueprint))
    fintech_blueprint = copy.deepcopy(dict(fintech_blueprint))

    aurora_metrics = _case_metrics(aurora_manifest, aurora_blueprint)
    fintech_metrics = _case_metrics(fintech_manifest, fintech_blueprint)

    comparisons = (
        _densidade_documental_comparison(aurora_blueprint, fintech_blueprint),
        _dificuldade_vs_esperada_comparison(aurora_blueprint, fintech_blueprint),
        _vazamento_info_comparison(aurora_manifest, fintech_manifest),
        _visual_score_comparison(aurora_manifest, fintech_manifest),
        _pacing_comparison(aurora_metrics, fintech_metrics),
        _num_documentos_total_comparison(aurora_blueprint, fintech_blueprint),
    )

    observations = _build_observations(aurora_metrics, fintech_metrics, comparisons)
    recommendations = _build_recommendations(aurora_metrics, fintech_metrics, comparisons)

    return QualityComparativeReport(
        generated_at=_now_iso(),
        aurora_metrics=aurora_metrics,
        fintech_metrics=fintech_metrics,
        comparisons=comparisons,
        observations=observations,
        recommendations=recommendations,
    )


def validate_quality_comparative_report(
    report: QualityComparativeReport,
) -> list[str]:
    """Return structural error messages for a report (empty == valid)."""

    errors: list[str] = []

    for label, metrics in (
        ("aurora_metrics", report.aurora_metrics),
        ("fintech_metrics", report.fintech_metrics),
    ):
        if not isinstance(metrics, CaseMetrics):
            errors.append(f"{label} must be a CaseMetrics instance.")
            continue
        if not metrics.case_name:
            errors.append(f"{label}.case_name must not be empty.")
        if not metrics.case_ref:
            errors.append(f"{label}.case_ref must not be empty.")
        if metrics.findings_count != sum(metrics.findings_by_type.values()):
            errors.append(
                f"{label}.findings_count does not match sum of "
                f"findings_by_type values."
            )
        if (
            metrics.pipeline_status == _PIPELINE_STATUS_COMPLETE
            and metrics.blocked_by is not None
        ):
            errors.append(
                f"{label}.blocked_by must be None when pipeline_status is "
                f"'{_PIPELINE_STATUS_COMPLETE}'."
            )
        if (
            metrics.pipeline_status != _PIPELINE_STATUS_COMPLETE
            and metrics.blocked_by is None
        ):
            errors.append(
                f"{label}.blocked_by must not be None when pipeline_status "
                f"is not '{_PIPELINE_STATUS_COMPLETE}'."
            )

    for comparison in report.comparisons:
        if not isinstance(comparison, MetricComparison):
            errors.append("comparisons entries must be MetricComparison instances.")
            continue
        if not comparison.metric_name:
            errors.append("MetricComparison.metric_name must not be empty.")

    return errors

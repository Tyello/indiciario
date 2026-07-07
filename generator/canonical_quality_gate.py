"""Canonical Quality Gate (ISSUE-30.5).

Avalia se um caso (blueprint + resultado de pipeline) e estruturalmente
elegivel para promocao a canonico em um nivel de dificuldade. Os thresholds
em ``CANONICAL_CRITERIA`` derivam de ``docs/DIFFICULTY_FRAMEWORK.md``
(secao "Metricas reais dos casos e excecoes"); ver ``docs/CANONICAL_CRITERIA.md``
para o racional completo.

Necessario, nao suficiente: ``APPROVED`` significa "estruturalmente elegivel
ao nivel", nao "canonico". Promover um caso a canonico ainda exige teste
cego humano registrado.

Contagem de documentos e numero de envelopes sao sinais informativos, nao
criterios duros: Mirante (20 docs, Iniciante) e Fintech (16 docs, Avancado)
provam que volume documental isolado nao classifica dificuldade.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from generator.quality_comparative_reviewer import (
    _case_metrics,
    _densidade_documental_comparison,
    _num_documentos_total_comparison,
)

__all__ = [
    "CANONICAL_CRITERIA",
    "CanonicalQualification",
    "CuratorQualification",
    "QualificationCriterion",
    "evaluate_font_fidelity",
    "evaluate_for_canonical",
    "get_canonical_criteria",
]


CANONICAL_CRITERIA: dict[str, dict[str, Any]] = {
    "iniciante": {
        "description": (
            "Caso com duracao esperada 45-70 min, documentos poucos, muito claros."
        ),
        "density_chars_min": 11000,
        "density_chars_max": 15000,
        "findings_er_max": 2,
        "findings_vr_major_max": 2,
        "findings_ar_major_max": 2,
        "stages_completed_min": 4,
        # Sinal informativo (nao bloqueia): faixa da tabela de calibracao em
        # docs/DIFFICULTY_FRAMEWORK.md.
        "documents_informational_min": 8,
        "documents_informational_max": 10,
    },
    "intermediario": {
        "description": (
            "Caso com duracao esperada 75-110 min, documentos medios, mistura "
            "clareza com ambiguidade controlada."
        ),
        "density_chars_min": 22500,
        "density_chars_max": 30500,
        "findings_er_max": 5,
        "findings_vr_major_max": 3,
        "findings_ar_major_max": 3,
        "stages_completed_min": 4,
        "documents_informational_min": 11,
        "documents_informational_max": 18,
    },
    "avancado": {
        "description": (
            "Caso com duracao esperada 110-150 min, documentos densos, pistas "
            "ambiguas e red herrings fortes."
        ),
        "density_chars_min": 25000,
        "density_chars_max": 45000,
        "findings_er_max": 8,
        "findings_vr_major_max": 5,
        "findings_ar_major_max": 5,
        "stages_completed_min": 4,
        "documents_informational_min": 19,
        "documents_informational_max": 24,
    },
}


class CuratorQualification(str, Enum):
    APPROVED = "approved"
    NEEDS_REFINEMENT = "needs_refinement"
    NOT_READY = "not_ready"
    INCOMPLETE_EVALUATION = "incomplete_evaluation"


@dataclass(frozen=True)
class QualificationCriterion:
    name: str
    actual_value: Any
    min_threshold: Any
    max_threshold: Any
    is_satisfied: bool
    status: str  # "ok" | "exceeds_max" | "below_min" | "blocker" | "not_evaluated"
    recommendation: str


@dataclass(frozen=True)
class CanonicalQualification:
    blueprint_ref: str
    difficulty_level: str
    qualification: CuratorQualification
    criteria_results: tuple[QualificationCriterion, ...]
    observations: tuple[str, ...]
    summary: str
    detailed_feedback: str
    action_if_approved: str
    refinement_steps: tuple[str, ...]


def get_canonical_criteria(difficulty_level: str) -> dict[str, Any]:
    """Return a copy of the criteria dict for ``difficulty_level``."""

    try:
        return dict(CANONICAL_CRITERIA[difficulty_level])
    except KeyError as exc:
        raise ValueError(
            f"Nivel de dificuldade desconhecido: {difficulty_level!r}. "
            f"Niveis validos: {sorted(CANONICAL_CRITERIA)}."
        ) from exc


def evaluate_font_fidelity(
    *,
    templates: list[str] | None = None,
    browser: Any,
) -> QualificationCriterion:
    """Check de fidelidade de fonte (ISSUE-40.2): falha explicitamente se
    algum template renderizado usa uma fonte custom que caiu em fallback
    silencioso de fonte de sistema (``@font-face`` ausente/quebrado em
    ``templates/styles/document_system.css``).

    Reusa a técnica de medição (``canvas.measureText`` via Chromium real)
    extraída em ``generator.font_fidelity`` (ISSUE-40.1). ``templates``
    restringe a checagem a um subconjunto do inventário
    ``generator.font_fidelity.CUSTOM_FONTS``; por padrão checa todos os
    templates do inventário.

    A ``recommendation`` nomeia cada par template+fonte que falhou (critério
    de aceite #2 da ISSUE-40.2) -- nunca um booleano agregado.
    """
    from generator.font_fidelity import CUSTOM_FONTS, fonte_aplicada

    template_names = templates if templates is not None else list(CUSTOM_FONTS)

    fallbacks: list[str] = []
    for template_nome in template_names:
        for fonte in CUSTOM_FONTS.get(template_nome, []):
            if not fonte_aplicada(browser, template_nome, fonte):
                fallbacks.append(f"{template_nome}: '{fonte}'")

    is_satisfied = not fallbacks
    recommendation = (
        ""
        if is_satisfied
        else (
            "font_fidelity: fallback silencioso de fonte custom para fonte de "
            "sistema em -- " + "; ".join(fallbacks) + ". Confirme o bloco "
            "@font-face correspondente em templates/styles/document_system.css."
        )
    )

    return QualificationCriterion(
        name="font_fidelity",
        actual_value=fallbacks,
        min_threshold=None,
        max_threshold=None,
        is_satisfied=is_satisfied,
        status="blocker" if fallbacks else "ok",
        recommendation=recommendation,
    )


def _density_and_document_count(blueprint: Mapping[str, Any]) -> tuple[int, int]:
    """Derive density (chars) and document count, reusing the existing helpers
    from ``quality_comparative_reviewer`` instead of duplicating the formula."""

    density = _densidade_documental_comparison(blueprint, blueprint).aurora_value
    documents = _num_documentos_total_comparison(blueprint, blueprint).aurora_value
    return density, documents


def _range_criterion(
    name: str, actual_value: int | float, min_threshold: int | float, max_threshold: int | float
) -> QualificationCriterion:
    if actual_value > max_threshold:
        status = "exceeds_max"
    elif actual_value < min_threshold:
        status = "below_min"
    else:
        status = "ok"
    recommendation = (
        ""
        if status == "ok"
        else (
            f"{name}={actual_value} fora da faixa [{min_threshold}, {max_threshold}]."
        )
    )
    return QualificationCriterion(
        name=name,
        actual_value=actual_value,
        min_threshold=min_threshold,
        max_threshold=max_threshold,
        is_satisfied=status == "ok",
        status=status,
        recommendation=recommendation,
    )


def _not_evaluated_criterion(
    name: str, max_threshold: Any, stage_name: str
) -> QualificationCriterion:
    """Criterion that could not be evaluated because its review stage did not run."""
    return QualificationCriterion(
        name=name,
        actual_value=None,
        min_threshold=None,
        max_threshold=max_threshold,
        is_satisfied=False,
        status="not_evaluated",
        recommendation=(
            f"{name}: stage '{stage_name}' ausente no pipeline_result. "
            "Execute o pipeline completo para avaliar este criterio."
        ),
    )


def _ceiling_criterion(
    name: str, actual_value: int | float, max_threshold: int | float
) -> QualificationCriterion:
    status = "exceeds_max" if actual_value > max_threshold else "ok"
    recommendation = (
        ""
        if status == "ok"
        else f"{name}={actual_value} excede o teto ({max_threshold})."
    )
    return QualificationCriterion(
        name=name,
        actual_value=actual_value,
        min_threshold=0,
        max_threshold=max_threshold,
        is_satisfied=status == "ok",
        status=status,
        recommendation=recommendation,
    )


def evaluate_for_canonical(
    blueprint: Mapping[str, Any],
    pipeline_result: Mapping[str, Any],
    difficulty_level: str,
    *,
    font_fidelity_criterion: QualificationCriterion | None = None,
) -> CanonicalQualification:
    """Evaluate whether ``blueprint``/``pipeline_result`` is structurally
    eligible for canonization at ``difficulty_level``.

    ``pipeline_result`` is a run manifest dict (the shape produced by
    ``generator.run_manifest`` / ``PipelineRunResult.manifest``).

    ``font_fidelity_criterion`` (ISSUE-40.2, STEP-03_FIX-01): critério opcional
    já construído por quem invoca o gate (ex. ``pipeline_runner`` chamando
    ``evaluate_font_fidelity`` com um ``Browser`` do Playwright vivo). Este
    módulo não invoca Playwright diretamente -- quando fornecido, o critério
    é apenas anexado a ``criteria_results`` e participa normalmente do
    cálculo de ``qualification`` via ``has_blocker``/status, igual aos
    demais critérios. Chamadas sem esse parâmetro mantêm o comportamento
    anterior inalterado.

    Returns a :class:`CanonicalQualification`. ``APPROVED`` here means
    "structurally eligible", not "canonical" -- promotion still requires a
    recorded blind human playtest.
    """

    criteria = get_canonical_criteria(difficulty_level)
    density, documents = _density_and_document_count(blueprint)
    metrics = _case_metrics(pipeline_result, blueprint)
    stages_completed_list = list(pipeline_result.get("stages_completed") or [])

    blueprint_ref = str(blueprint.get("titulo") or metrics.case_ref or "<sem-titulo>")

    criteria_results: list[QualificationCriterion] = [
        _range_criterion(
            "density_chars",
            density,
            criteria["density_chars_min"],
            criteria["density_chars_max"],
        ),
        _ceiling_criterion(
            "findings_er",
            metrics.findings_by_type.get("ER_*", 0),
            criteria["findings_er_max"],
        ),
        (
            _ceiling_criterion(
                "findings_vr_major",
                metrics.findings_by_type.get("VR_*", 0),
                criteria["findings_vr_major_max"],
            )
            if "visual_review" in stages_completed_list
            else _not_evaluated_criterion(
                "findings_vr_major",
                criteria["findings_vr_major_max"],
                "visual_review",
            )
        ),
        (
            _ceiling_criterion(
                "findings_ar_major",
                metrics.findings_by_type.get("AR_*", 0),
                criteria["findings_ar_major_max"],
            )
            if "accessibility_review" in stages_completed_list
            else _not_evaluated_criterion(
                "findings_ar_major",
                criteria["findings_ar_major_max"],
                "accessibility_review",
            )
        ),
    ]

    stages_status = (
        "ok" if metrics.stages_completed >= criteria["stages_completed_min"] else "below_min"
    )
    criteria_results.append(
        QualificationCriterion(
            name="stages_completed",
            actual_value=metrics.stages_completed,
            min_threshold=criteria["stages_completed_min"],
            max_threshold=None,
            is_satisfied=stages_status == "ok",
            status=stages_status,
            recommendation=(
                ""
                if stages_status == "ok"
                else (
                    f"stages_completed={metrics.stages_completed} abaixo do minimo "
                    f"({criteria['stages_completed_min']})."
                )
            ),
        )
    )

    is_blocked = metrics.blocked_by is not None
    criteria_results.append(
        QualificationCriterion(
            name="pipeline_status",
            actual_value=metrics.pipeline_status,
            min_threshold=None,
            max_threshold=None,
            is_satisfied=not is_blocked,
            status="blocker" if is_blocked else "ok",
            recommendation=(
                ""
                if not is_blocked
                else (
                    f"pipeline_status bloqueado ({metrics.blocked_by}). "
                    "Resolver o gate antes de reavaliar."
                )
            ),
        )
    )

    if font_fidelity_criterion is not None:
        criteria_results.append(font_fidelity_criterion)

    observations: list[str] = []
    doc_min = criteria["documents_informational_min"]
    doc_max = criteria["documents_informational_max"]
    if documents < doc_min or documents > doc_max:
        observations.append(
            f"Documentos ({documents}) fora da faixa informativa [{doc_min}, {doc_max}] "
            f"do nivel '{difficulty_level}'. Sinal informativo: nao bloqueia a "
            "qualificacao (contagem de documentos nao classifica dificuldade de forma "
            "confiavel -- ver docs/DIFFICULTY_FRAMEWORK.md)."
        )

    has_blocker = any(c.status == "blocker" for c in criteria_results)
    has_out_of_range = any(c.status in ("exceeds_max", "below_min") for c in criteria_results)
    has_unevaluated = any(c.status == "not_evaluated" for c in criteria_results)

    if has_blocker:
        qualification = CuratorQualification.NOT_READY
    elif has_out_of_range:
        qualification = CuratorQualification.NEEDS_REFINEMENT
    elif has_unevaluated:
        qualification = CuratorQualification.INCOMPLETE_EVALUATION
    else:
        qualification = CuratorQualification.APPROVED

    if has_unevaluated:
        unevaluated_names = ", ".join(
            c.name for c in criteria_results if c.status == "not_evaluated"
        )
        observations.append(
            f"Criterios nao avaliados: {unevaluated_names}. "
            "Pipeline executado sem visual_review e/ou accessibility_review. "
            "Execute o pipeline completo para obter avaliacao definitiva."
        )

    refinement_steps = tuple(
        c.recommendation
        for c in criteria_results
        if c.status in ("exceeds_max", "below_min") and c.recommendation
    )

    summary = (
        f"{blueprint_ref}: {qualification.value} como '{difficulty_level}'."
    )
    feedback_lines = [summary]
    for criterion in criteria_results:
        feedback_lines.append(
            f"- {criterion.name}={criterion.actual_value} [{criterion.status}]"
            + (f" -- {criterion.recommendation}" if criterion.recommendation else "")
        )
    for observation in observations:
        feedback_lines.append(f"- observacao: {observation}")
    detailed_feedback = "\n".join(feedback_lines)

    if qualification == CuratorQualification.APPROVED:
        action_if_approved = (
            f"Caso estruturalmente elegivel para canonizacao como '{difficulty_level}'. "
            "Promocao final ainda exige teste cego humano registrado "
            "(ver docs/DIFFICULTY_FRAMEWORK.md e Learning Ledger)."
        )
    else:
        action_if_approved = ""

    return CanonicalQualification(
        blueprint_ref=blueprint_ref,
        difficulty_level=difficulty_level,
        qualification=qualification,
        criteria_results=tuple(criteria_results),
        observations=tuple(observations),
        summary=summary,
        detailed_feedback=detailed_feedback,
        action_if_approved=action_if_approved,
        refinement_steps=refinement_steps,
    )

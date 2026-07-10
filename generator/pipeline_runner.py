"""Deterministic multiagent pipeline runner (ISSUE-28).

Chains existing public APIs — bundle, blind solve, run record, gate, narrative
review, evidence review, workspace orchestrator and run manifest — over a real
blueprint without LLM, network access or blueprint mutation.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    build_blind_bundle,
)
from generator.blind_solve_run_record import build_run_record
from generator.blind_solver_harness import (
    BlindSolver,
    BlindSolverContext,
    BlindSolverEvidence,
    BlindSolverHarnessRequest,
    BlindSolverReport,
    run_blind_solver_harness,
)
from generator.blind_solver_report_validator import validate_report
from generator.case_review import load_blueprint
from generator.conclusion_judge import (
    ConclusionJudgeError,
    ExpectedConclusionInput,
    JudgeVerdict,
    judge_conclusions,
)
from generator.evidence_reviewer import report_to_dict as evidence_report_to_dict
from generator.evidence_reviewer import review_evidence
from generator.gate_evaluator import (
    ConfidenceAssessment,
    ExpectedConclusion,
    GapItem,
    GateEvaluationRequest,
    build_gate_evaluation,
)
from generator.llm_provider import LLMProvider
from generator.manual_orchestrator import (
    DecisionRequest,
    IngestRequest,
    TransitionRequest,
    ingest_artifact,
    record_decision,
    transition_stage,
)
from generator.narrative_reviewer import report_to_dict as narrative_report_to_dict
from generator.narrative_reviewer import review_narrative
from generator.run_manifest import build_run_manifest
from generator.workspace import VALID_ARTIFACT_TYPES, VALID_OUTCOMES, VALID_STAGES, build_workspace_run

__all__ = [
    "AURORA_DEFECT_TO_CODES",
    "AURORA_PLAYTEST_DEFECTS",
    "DefectMatch",
    "DeterministicPipelineSolver",
    "PipelineRunResult",
    "PlaytestComparison",
    "PlaytestDefect",
    "VALID_ARTIFACT_TYPES",
    "VALID_OUTCOMES",
    "VALID_STAGES",
    "compare_to_playtest",
    "run_pipeline",
]

FIXED_PIPELINE_CREATED_AT = "2026-06-22T12:00:00Z"


@dataclass(frozen=True)
class PlaytestDefect:
    defect_id: str
    description: str
    category: str


@dataclass(frozen=True)
class DefectMatch:
    defect_id: str
    finding_code: str


@dataclass(frozen=True)
class PlaytestComparison:
    playtest_defects: tuple[PlaytestDefect, ...]
    pipeline_findings: tuple[str, ...]
    matches: tuple[DefectMatch, ...]
    unmatched_playtest: tuple[str, ...]
    unmatched_pipeline: tuple[str, ...]


@dataclass(frozen=True)
class PipelineRunResult:
    manifest: dict[str, Any]
    workspace_run: dict[str, Any]
    blind_solver_report: dict[str, Any]
    gate_evaluation: dict[str, Any]
    narrative_report: dict[str, Any]
    evidence_report: dict[str, Any]
    findings: tuple[dict[str, Any], ...]
    comparison: PlaytestComparison


AURORA_PLAYTEST_DEFECTS: tuple[PlaytestDefect, ...] = (
    PlaytestDefect(
        defect_id="PD_01",
        description="Não ficou claro o que resolver no E1",
        category="objetivo_envelope",
    ),
    PlaytestDefect(
        defect_id="PD_02",
        description="Não ficou claro quando receber o E2",
        category="progressao",
    ),
    PlaytestDefect(
        defect_id="PD_03",
        description="Não ficou claro quais perguntas responder no E2",
        category="objetivo_envelope",
    ),
)

# No current NR/ER rule maps to envelope-clarity playtest defects (backlog NR_002/005/007).
AURORA_DEFECT_TO_CODES: dict[str, tuple[str, ...]] = {
    "PD_01": (),
    "PD_02": (),
    "PD_03": (),
}


class DeterministicPipelineSolver:
    """Offline, no-LLM stub solver reused for pipeline runs."""

    def __init__(self, created_at: str = FIXED_PIPELINE_CREATED_AT) -> None:
        self.created_at = created_at

    def solve(self, context: BlindSolverContext) -> BlindSolverReport:
        artifacts = context.list_artifacts()
        first = artifacts[0]
        text = context.read_artifact_text(first.artifact_id)
        return BlindSolverReport(
            schema_version="1.0",
            solver_run_id=context.solver_run_id,
            solver_id=context.solver_id,
            bundle_id=context.bundle_id,
            manifest_id=context.manifest_id,
            created_at=self.created_at,
            conclusion=f"Read {len(artifacts)} artifact(s); first has {len(text)} chars.",
            confidence="low",
            reasoning_summary="Deterministic stub: inspected only the first bundled artifact.",
            evidence_used=(
                BlindSolverEvidence(
                    artifact_id=first.artifact_id,
                    path=first.path,
                    quote_or_summary=text.strip()[:60],
                    relevance="First declared artifact in the bundle.",
                    confidence="low",
                ),
            ),
            open_questions=(),
            assumptions=(),
            warnings=(),
        )


def compare_to_playtest(
    findings: tuple[Mapping[str, Any], ...],
    playtest_defects: tuple[PlaytestDefect, ...],
    defect_to_codes: Mapping[str, tuple[str, ...]],
) -> PlaytestComparison:
    """Cross-reference pipeline findings against declared playtest defects."""

    finding_codes = tuple(
        dict(finding).get("code")
        for finding in findings
        if dict(finding).get("code")
    )
    matches: list[DefectMatch] = []
    unmatched_playtest: list[str] = []
    matched_codes: set[str] = set()

    for defect in playtest_defects:
        expected_codes = defect_to_codes.get(defect.defect_id, ())
        defect_matches = [
            code for code in finding_codes if code in expected_codes
        ]
        if defect_matches:
            for code in defect_matches:
                matches.append(DefectMatch(defect_id=defect.defect_id, finding_code=code))
                matched_codes.add(code)
        else:
            unmatched_playtest.append(defect.defect_id)

    unmatched_pipeline = tuple(
        code for code in finding_codes if code not in matched_codes
    )

    return PlaytestComparison(
        playtest_defects=tuple(playtest_defects),
        pipeline_findings=finding_codes,
        matches=tuple(matches),
        unmatched_playtest=tuple(unmatched_playtest),
        unmatched_pipeline=unmatched_pipeline,
    )


def run_pipeline(
    blueprint_path: str | Path,
    run_id: str,
    *,
    output_root: str | Path | None = None,
    created_at: str | None = None,
    solver: BlindSolver | None = None,
    judge_provider: LLMProvider | None = None,
) -> PipelineRunResult:
    """Run the full offline multiagent pipeline over a blueprint."""

    blueprint_path = Path(blueprint_path).resolve()
    timestamp = created_at or FIXED_PIPELINE_CREATED_AT
    owns_output = output_root is None
    root = Path(output_root) if output_root is not None else Path(tempfile.mkdtemp(prefix="indiciario-pipeline-"))
    root.mkdir(parents=True, exist_ok=True)

    blueprint_before = blueprint_path.read_bytes()
    blueprint = load_blueprint(blueprint_path)
    blueprint_ref = str(blueprint_path)

    bundle_result, harness_result, harness_request, run_record = _blind_solve(
        blueprint,
        blueprint_ref,
        run_id,
        root,
        timestamp,
        solver=solver,
    )
    gate_evaluation, gate_mode, judge_verdict = _run_gate(
        run_record,
        blueprint,
        blueprint_ref,
        run_id,
        timestamp,
        judge_provider=judge_provider,
    )
    narrative_report, evidence_report = _run_reviews(
        blueprint,
        blueprint_ref,
        run_id,
        timestamp,
    )

    workspace_run = _assemble_workspace(
        run_id=run_id,
        case_ref=blueprint_ref,
        timestamp=timestamp,
        bundle_result=bundle_result,
        harness_result=harness_result,
        run_record=run_record,
        gate_evaluation=gate_evaluation,
        narrative_report=narrative_report,
        evidence_report=evidence_report,
        gate_mode=gate_mode,
        judge_verdict=judge_verdict,
    )

    ingested_artifact_ids = {
        artifact.get("artifact_id") for artifact in workspace_run.get("artifacts") or []
    }
    findings_by_artifact: dict[str, list[dict[str, Any]]] = {}
    if f"NR-{run_id}" in ingested_artifact_ids:
        findings_by_artifact[f"NR-{run_id}"] = list(narrative_report.get("findings") or [])
    if f"ER-{run_id}" in ingested_artifact_ids:
        findings_by_artifact[f"ER-{run_id}"] = list(evidence_report.get("findings") or [])
    consolidated_findings = tuple(
        finding
        for artifact_findings in findings_by_artifact.values()
        for finding in artifact_findings
    )

    manifest = _consolidate_manifest(
        workspace_run=workspace_run,
        run_id=run_id,
        findings_by_artifact=findings_by_artifact,
        timestamp=timestamp,
        gate_mode=gate_mode,
    )

    playtest_defects = (
        AURORA_PLAYTEST_DEFECTS
        if "caso_canonico_intermediario" in blueprint_path.name
        else ()
    )
    defect_map = (
        AURORA_DEFECT_TO_CODES
        if playtest_defects
        else {defect.defect_id: () for defect in playtest_defects}
    )
    comparison = compare_to_playtest(
        consolidated_findings,
        playtest_defects,
        defect_map,
    )

    if blueprint_path.read_bytes() != blueprint_before:
        raise RuntimeError("pipeline mutated the blueprint file")

    if owns_output:
        # Caller did not pin output_root; temp dir lifecycle is caller/OS concern.
        pass

    return PipelineRunResult(
        manifest=manifest,
        workspace_run=workspace_run,
        blind_solver_report=harness_result.report,
        gate_evaluation=gate_evaluation,
        narrative_report=narrative_report,
        evidence_report=evidence_report,
        findings=consolidated_findings,
        comparison=comparison,
    )


def _build_bundle(
    blueprint: Any,
    blueprint_ref: str,
    run_id: str,
    output_root: Path,
    timestamp: str,
) -> Any:
    source_root = output_root / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    artifact_specs = _materialize_e1_sources(blueprint, source_root)

    bundle_id = f"BUNDLE-{run_id}"
    request = BlindBundleBuildRequest(
        manifest_id=f"MANIFEST-{run_id}",
        run_id=run_id,
        bundle_id=bundle_id,
        case_id=_neutral_case_id(blueprint, run_id),
        case_version=str(getattr(blueprint, "versao", "0.1")).replace(".", "-"),
        role="blind_solver",
        stage="blind_solve",
        source_root=source_root,
        output_root=output_root / "bundles",
        created_by="ORCHESTRATOR",
        artifact_specs=artifact_specs,
        created_at=timestamp,
        overwrite=True,
    )
    return build_blind_bundle(request)


def _blind_solve(
    blueprint: Any,
    blueprint_ref: str,
    run_id: str,
    output_root: Path,
    timestamp: str,
    solver: BlindSolver | None = None,
) -> tuple[Any, Any, BlindSolverHarnessRequest, dict[str, Any]]:
    bundle_result = _build_bundle(blueprint, blueprint_ref, run_id, output_root, timestamp)
    harness_request = BlindSolverHarnessRequest(
        bundle_path=bundle_result.output_path,
        solver_id=f"SOLVER-{run_id}",
        run_id=run_id,
        created_by="ORCHESTRATOR",
        created_at=timestamp,
    )
    effective_solver = solver if solver is not None else DeterministicPipelineSolver(created_at=timestamp)
    harness_result = run_blind_solver_harness(
        harness_request,
        effective_solver,
    )
    validator_result = validate_report(harness_result.report)
    run_record = build_run_record(
        harness_result,
        harness_request,
        validator_result,
        created_by="ORCHESTRATOR",
    )
    return bundle_result, harness_result, harness_request, run_record


def _run_gate(
    run_record: Mapping[str, Any],
    blueprint: Any,
    blueprint_ref: str,
    run_id: str,
    timestamp: str,
    judge_provider: LLMProvider | None = None,
) -> tuple[dict[str, Any], str, dict[str, Any] | None]:
    """Build the gate evaluation for a run.

    Without ``judge_provider`` (stub mode, PJ_003), preserves the previous
    fabricated-approval plumbing byte-for-byte. With ``judge_provider``
    (judged mode, PJ_001/PJ_002), the decision is derived in Python from the
    real ``judge_conclusions`` verdict: a judge failure is never swallowed
    into a silent approval (PJ_005's case 7) — it propagates as a traceable
    ``RuntimeError``.
    """
    expected = _derive_expected_conclusions(blueprint)
    request = GateEvaluationRequest(
        run_record=run_record,
        private_solution_ref=blueprint_ref,
        evaluator_id="ORCHESTRATOR",
        evaluation_id=f"GE-{run_id}",
        created_by="ORCHESTRATOR",
        created_at=timestamp,
    )

    if judge_provider is None:
        gate_evaluation = build_gate_evaluation(
            request,
            expected_conclusions=expected,
            unexpected_valid_hypotheses=[],
            gaps=[
                GapItem(
                    id="GAP-STUB-01",
                    description="Stub solver does not evaluate private solution semantics.",
                    required_conclusion_id=None,
                    severity="minor",
                    impact="Expected for ISSUE-28 offline plumbing run.",
                )
            ],
            confidence_assessment=ConfidenceAssessment(
                solver_confidence="low",
                evaluator_agreement="partial",
                notes="Deterministic stub run; gate decision is explicit plumbing, not LLM quality.",
            ),
            decision="approved",
            justification=(
                "ISSUE-28 plumbing run: run record schema-valid; explicit approved "
                "decision to exercise reviewers and manifest consolidation."
            ),
            leak_detected=False,
            rollback_target=None,
        )
        return gate_evaluation, "stub", None

    try:
        verdict = judge_conclusions(
            run_record["report"],
            [
                ExpectedConclusionInput(id=item.id, statement=item.description, required=item.required)
                for item in expected
            ],
            judge_provider,
        )
    except ConclusionJudgeError as exc:
        raise RuntimeError(
            f"gate judge failed for run {run_id!r}: {exc}"
        ) from exc

    gate_evaluation, judge_verdict_dict = _build_judged_gate_evaluation(
        request, expected, verdict, run_record
    )
    return gate_evaluation, "judged", judge_verdict_dict


def _build_judged_gate_evaluation(
    request: GateEvaluationRequest,
    expected: list[ExpectedConclusion],
    verdict: JudgeVerdict,
    run_record: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive expected conclusions, gaps and decision from a JudgeVerdict (PJ_002).

    The decision is never taken from the model: only ``resolvido``/``met``
    values feed Python conditionals that mirror GE_003-GE_006.
    """
    met_by_id = {conclusion.id: conclusion.met for conclusion in verdict.conclusions}
    rationale_by_id = {conclusion.id: conclusion.rationale for conclusion in verdict.conclusions}
    judged_expected = [
        replace(item, met=met_by_id.get(item.id, False)) for item in expected
    ]

    leak_detected = verdict.classification == "vazamento"
    ambiguous = verdict.classification == "ambiguo"

    gaps: list[GapItem] = []
    for item in judged_expected:
        if item.required and not item.met:
            gaps.append(
                GapItem(
                    id=f"GAP-{item.id}",
                    description=f"Required conclusion {item.id!r} not met by judge verdict.",
                    required_conclusion_id=item.id,
                    severity="critical",
                    impact=rationale_by_id.get(item.id, "Judge did not confirm this conclusion."),
                )
            )
    if ambiguous:
        gaps.append(
            GapItem(
                id="GAP-AMBIGUOUS",
                description="Judge detected a plausible alternative solution.",
                required_conclusion_id=None,
                severity="major",
                impact=verdict.alternative_solution_summary or "classification=ambiguo",
            )
        )
    if leak_detected and not any(gap.id == "GAP-LEAK" for gap in gaps):
        gaps.append(
            GapItem(
                id="GAP-LEAK",
                description="Judge classified the run as a solution leak.",
                required_conclusion_id=None,
                severity="critical",
                impact="classification=vazamento",
            )
        )

    has_unmet_required = any(item.required and not item.met for item in judged_expected)
    decision = "approved" if not has_unmet_required and not leak_detected and not ambiguous else "rejected"

    report_confidence = str((run_record.get("report") or {}).get("confidence", "low"))
    gate_evaluation = build_gate_evaluation(
        request,
        expected_conclusions=judged_expected,
        unexpected_valid_hypotheses=[],
        gaps=gaps,
        confidence_assessment=ConfidenceAssessment(
            solver_confidence=report_confidence,
            evaluator_agreement="agree" if decision == "approved" else "disagree",
            notes=f"Judged run; classification={verdict.classification}.",
        ),
        decision=decision,
        justification=(
            f"Judged run: classification={verdict.classification}; "
            f"{len(gaps)} gap(s) derived from judge verdict."
        ),
        leak_detected=leak_detected,
        rollback_target=None,
    )
    return gate_evaluation, asdict(verdict)


def _run_reviews(
    blueprint: Any,
    blueprint_ref: str,
    run_id: str,
    created_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    narrative = narrative_report_to_dict(
        review_narrative(
            blueprint,
            blueprint_ref,
            report_id=f"NR-{run_id}",
            created_by="ORCHESTRATOR",
            created_at=created_at,
        )
    )
    evidence = evidence_report_to_dict(
        review_evidence(
            blueprint,
            blueprint_ref,
            report_id=f"ER-{run_id}",
            created_by="ORCHESTRATOR",
            created_at=created_at,
        )
    )
    return narrative, evidence


def _assemble_workspace(
    *,
    run_id: str,
    case_ref: str,
    timestamp: str,
    bundle_result: Any,
    harness_result: Any,
    run_record: Mapping[str, Any],
    gate_evaluation: Mapping[str, Any],
    narrative_report: Mapping[str, Any],
    evidence_report: Mapping[str, Any],
    gate_mode: str = "stub",
    judge_verdict: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    run = build_workspace_run(
        run_id=run_id,
        case_ref=case_ref,
        created_at=timestamp,
    )
    run = _apply_transition(run, "initialized", "blind_solve")

    bundle_path = str(bundle_result.output_path)
    bundle_hash_ref = json.dumps(bundle_result.manifest, sort_keys=True, ensure_ascii=False)
    run = _ingest(
        run,
        artifact_id=f"BUNDLE-{run_id}",
        artifact_type="blind_bundle",
        path=bundle_path,
        content_ref=bundle_hash_ref,
        stage="blind_solve",
        visible_to=("blind_solver",),
        timestamp=timestamp,
    )
    run = _ingest(
        run,
        artifact_id=f"BSR-{run_id}",
        artifact_type="blind_solver_report",
        path=f"{bundle_path}/blind_solver_report.json",
        content_ref=json.dumps(harness_result.report, sort_keys=True),
        stage="blind_solve",
        visible_to=("gate_evaluator",),
        timestamp=timestamp,
    )
    run = _ingest(
        run,
        artifact_id=f"RR-{run_id}",
        artifact_type="run_record",
        path=f"{bundle_path}/run_record.json",
        content_ref=json.dumps(dict(run_record), sort_keys=True),
        stage="blind_solve",
        visible_to=("gate_evaluator",),
        timestamp=timestamp,
    )

    run = _apply_transition(run, "blind_solve", "gate_evaluation")
    run = _ingest(
        run,
        artifact_id=f"GE-{run_id}",
        artifact_type="gate_evaluation",
        path=f"workspace/{run_id}/gate_evaluation.json",
        content_ref=json.dumps(dict(gate_evaluation), sort_keys=True),
        stage="gate_evaluation",
        visible_to=("human_operator",),
        timestamp=timestamp,
    )
    if gate_mode == "judged" and judge_verdict is not None:
        run = _ingest(
            run,
            artifact_id=f"JV-{run_id}",
            artifact_type="judge_verdict",
            path=f"workspace/{run_id}/judge_verdict.json",
            content_ref=json.dumps(dict(judge_verdict), sort_keys=True),
            stage="gate_evaluation",
            visible_to=("human_operator",),
            timestamp=timestamp,
        )
    if gate_mode == "judged":
        decision_outcome = str(gate_evaluation["decision"])
        decision_justification = str(gate_evaluation["justification"])
    else:
        # PJ_003: byte-for-byte preservation of the pre-33.3 stub decision record.
        decision_outcome = "approved"
        decision_justification = "ISSUE-28 plumbing run: explicit approved gate decision."
    run = _record_gate_decision(
        run,
        run_id,
        timestamp,
        outcome=decision_outcome,
        justification=decision_justification,
    )

    if gate_mode == "judged" and decision_outcome != "approved":
        # A judged rejection blocks the run at gate_evaluation: the
        # orchestrator's own state machine (OR_003/OR_008) forbids advancing
        # to narrative_review without an approved gate decision, and this
        # module must not weaken that invariant to force the linear stub
        # flow through a real rejection.
        return run

    run = _apply_transition(run, "gate_evaluation", "narrative_review")
    run = _ingest(
        run,
        artifact_id=f"NR-{run_id}",
        artifact_type="narrative_review",
        path=f"workspace/{run_id}/narrative_review.json",
        content_ref=json.dumps(dict(narrative_report), sort_keys=True),
        stage="narrative_review",
        visible_to=("human_operator",),
        timestamp=timestamp,
    )

    run = _apply_transition(run, "narrative_review", "evidence_review")
    run = _ingest(
        run,
        artifact_id=f"ER-{run_id}",
        artifact_type="evidence_review",
        path=f"workspace/{run_id}/evidence_review.json",
        content_ref=json.dumps(dict(evidence_report), sort_keys=True),
        stage="evidence_review",
        visible_to=("human_operator",),
        timestamp=timestamp,
    )

    run = _apply_transition(run, "evidence_review", "complete")
    run = dict(run)
    run["status"] = "done"
    return run


def _consolidate_manifest(
    *,
    workspace_run: Mapping[str, Any],
    run_id: str,
    findings_by_artifact: Mapping[str, list[Mapping[str, Any]]],
    timestamp: str,
    gate_mode: str = "stub",
) -> dict[str, Any]:
    return build_run_manifest(
        workspace_run,
        manifest_id=f"MANIFEST-{run_id}",
        findings_by_artifact=findings_by_artifact,
        generated_by="ORCHESTRATOR",
        generated_at=timestamp,
        notes="ISSUE-28 deterministic pipeline run.",
        gate_mode=gate_mode,
    )


def _apply_transition(
    run: Mapping[str, Any],
    from_stage: str,
    to_stage: str,
) -> dict[str, Any]:
    result = transition_stage(
        TransitionRequest(run=run, from_stage=from_stage, to_stage=to_stage)
    )
    if not result.valid:
        raise RuntimeError(
            f"invalid transition {from_stage!r} -> {to_stage!r}: {result.errors}"
        )
    return dict(result.run)


def _ingest(
    run: Mapping[str, Any],
    *,
    artifact_id: str,
    artifact_type: str,
    path: str,
    content_ref: str,
    stage: str,
    visible_to: tuple[str, ...],
    timestamp: str,
) -> dict[str, Any]:
    result = ingest_artifact(
        IngestRequest(
            run=run,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            path=path,
            sha256=_sha256_text(content_ref),
            stage=stage,
            visible_to=visible_to,
            ingested_at=timestamp,
        )
    )
    if not result.valid:
        raise RuntimeError(f"artifact ingest failed for {artifact_id}: {result.errors}")
    return dict(result.run)


def _record_gate_decision(
    run: Mapping[str, Any],
    run_id: str,
    timestamp: str,
    outcome: str,
    justification: str,
) -> dict[str, Any]:
    result = record_decision(
        DecisionRequest(
            run=run,
            decision_id=f"DEC-{run_id}",
            stage="gate_evaluation",
            outcome=outcome,
            justification=justification,
            decided_at=timestamp,
            decided_by="ORCHESTRATOR",
            rollback_to_stage=None,
        )
    )
    if not result.valid:
        raise RuntimeError(f"gate decision failed: {result.errors}")
    return dict(result.run)


def _derive_expected_conclusions(blueprint: Any) -> list[ExpectedConclusion]:
    conclusions: list[ExpectedConclusion] = []
    objetivos = getattr(blueprint, "objetivos_por_envelope", None) or []
    for index, objetivo in enumerate(objetivos, 1):
        envelope = str(getattr(objetivo, "envelope", f"E{index}"))
        resposta = str(getattr(objetivo, "resposta_esperada", ""))
        pergunta = str(getattr(objetivo, "pergunta_diegetica", ""))
        description = resposta or pergunta or f"Objetivo do envelope {envelope}"
        conclusions.append(
            ExpectedConclusion(
                id=f"EC-{envelope}",
                description=description,
                required=True,
                met=True,
                evidence=f"Derived from objetivos_por_envelope[{envelope}].",
            )
        )

    if not conclusions:
        guia = getattr(blueprint, "guia_operacional", None)
        solucao = getattr(guia, "solucao_em_5_frases", None) or []
        for index, frase in enumerate(solucao[:3], 1):
            conclusions.append(
                ExpectedConclusion(
                    id=f"EC-GUIA-{index}",
                    description=str(frase),
                    required=index == 1,
                    met=True,
                    evidence="Derived from guia_operacional.solucao_em_5_frases.",
                )
            )
    return conclusions


def _materialize_e1_sources(blueprint: Any, source_root: Path) -> list[ArtifactSpec]:
    specs: list[ArtifactSpec] = []
    documentos = getattr(blueprint, "documentos", None) or []
    e1_docs = [
        documento
        for documento in documentos
        if str(getattr(documento, "envelope", "")).upper().startswith("E1")
    ]
    if not e1_docs:
        e1_docs = list(documentos[:1])
    for index, documento in enumerate(e1_docs, 1):
        codigo = str(getattr(documento, "codigo", f"DOC-{index}"))
        relative_source = f"public/envelope_1/{codigo}.md"
        target = source_root / relative_source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_document_text(documento), encoding="utf-8")
        specs.append(
            ArtifactSpec(
                artifact_id=f"ART-{codigo}",
                source_path=relative_source,
                bundle_path=f"player/{codigo}.md",
                artifact_type="player_document",
                visibility="public_player",
                envelope_scope="current_envelope",
                source_role="author",
                included_reason=(
                    f"Documento {codigo} do envelope E1 listado para bundle cego."
                ),
                contains_solution=False,
                contains_future_envelopes=False,
                contains_private_author_notes=False,
                contains_other_agents_outputs=False,
            )
        )
    return specs


def _document_text(documento: Any) -> str:
    titulo = str(getattr(documento, "titulo", "Documento"))
    conteudo = getattr(documento, "conteudo", None) or {}
    if not conteudo:
        return titulo
    lines = [titulo, ""]
    for key, value in conteudo.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _neutral_case_id(blueprint: Any, run_id: str) -> str:
    titulo = str(getattr(blueprint, "titulo", "CASE"))
    ascii_title = titulo.encode("ascii", "ignore").decode("ascii")
    slug = "".join(ch if ch.isalnum() else "-" for ch in ascii_title.upper()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    if slug and slug[0].isalnum():
        return slug[:64]
    return f"CASE-{run_id}"[:64]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

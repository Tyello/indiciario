"""Solvability Meter: dificuldade calibrada por múltiplas execuções cegas.

This module implements ISSUE-33.2. It orchestrates N solver->judge rounds
(LLMBlindSolver + Conclusion Judge) over the same bundle and aggregates the
verdicts into a solve-rate based difficulty estimate.

Out of scope (SM contract): it does not alter solver, judge, harness or gate
behavior, and it does not decide approval — the report is an input, the
decision stays with the gate/human.

Honesty note: this measures difficulty *for an LLM solver*, a proxy. Human
playtest remains the real difficulty verdict. SM_003 thresholds are initial
and calibrable against future playtests.

Contracts:
- SM_001: runs < 1 or temperature outside [0, 2] -> ValueError before any run.
- SM_002: each run uses the same bundle and solver prompt; a run that fails
  in the harness/provider is recorded as incomplete, not fatal to the meter
  -- unless every run fails, which raises SolvabilityMeterError.
- SM_003: solve_rate == 1.0 -> "facil"; >= 0.5 -> "medio"; > 0.0 -> "dificil";
  == 0.0 -> "injusto". Pure Python derivation.
- SM_004: flags derived from run classifications and completeness.
- SM_005: difficulty_framework_ref cross-links docs/DIFFICULTY_FRAMEWORK.md.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from generator.blind_bundle_decoder import decode_blind_bundle
from generator.blind_solver_harness import (
    BlindSolverHarnessError,
    BlindSolverHarnessRequest,
    run_blind_solver_harness,
)
from generator.conclusion_judge import (
    ConclusionJudgeError,
    ExpectedConclusionInput,
    judge_conclusions,
)
from generator.llm_blind_solver import LLMBlindSolver
from generator.llm_provider import LLMProvider, ProviderError

DIFFICULTY_FRAMEWORK_REF = "docs/DIFFICULTY_FRAMEWORK.md#solvability-meter-proxy-llm"

_CLASSIFICATIONS: tuple[str, ...] = ("resolvido", "nao_resolvido", "vazamento", "ambiguo")


class SolvabilityMeterError(RuntimeError):
    """Raised when every run fails and no verdict can be aggregated."""


@dataclass(frozen=True)
class RunResult:
    """One completed run's judged outcome."""

    run_id: str
    classification: str
    required_met_count: int
    required_total: int


@dataclass(frozen=True)
class SolvabilityReport:
    """Aggregated result of measure_solvability (frozen, serializable)."""

    meter_id: str
    bundle_id: str
    runs_requested: int
    runs_completed: int
    run_results: list[RunResult]
    solve_rate: float
    classification_counts: dict[str, int]
    difficulty_estimate: str
    flags: list[str]
    difficulty_framework_ref: str = DIFFICULTY_FRAMEWORK_REF


def estimate_difficulty(solve_rate: float) -> str:
    """Derive a difficulty estimate from a solve_rate (SM_003, pure Python)."""
    if solve_rate == 1.0:
        return "facil"
    if solve_rate >= 0.5:
        return "medio"
    if solve_rate > 0.0:
        return "dificil"
    return "injusto"


def measure_solvability(
    bundle_path: Path,
    expected: Sequence[ExpectedConclusionInput],
    provider: LLMProvider,
    runs: int = 3,
    temperature: float = 0.7,
    key_evidence_ids: Sequence[str] | None = None,
) -> SolvabilityReport:
    """Run N solver->judge rounds over the same bundle and aggregate a report.

    Args:
        bundle_path: Path to the blind bundle (same bundle for every run).
        expected: Expected conclusions to judge each run's report against.
        provider: LLMProvider shared by every solver and judge call.
        runs: Number of rounds to attempt (must be >= 1).
        temperature: Recorded for reproducibility (must be in [0.0, 2.0]);
            not threaded into the solver/judge provider calls, since both
            hardcode their own request temperature and altering that is out
            of scope for this issue.
        key_evidence_ids: Optional artifact ids forwarded to the judge's
            leak check on each run.

    Returns:
        SolvabilityReport with per-run results, solve_rate, classification
        counts, difficulty_estimate and flags.

    Raises:
        ValueError: SM_001, if runs/temperature are out of range.
        SolvabilityMeterError: SM_002, if every run fails.
    """
    if runs < 1 or not (0.0 <= temperature <= 2.0):
        raise ValueError(
            "SM_001: runs must be >= 1 and temperature must be in [0.0, 2.0]; "
            f"got runs={runs}, temperature={temperature}"
        )

    bundle_meta = decode_blind_bundle(bundle_path)
    meter_id = f"METER_{int(time.time() * 1000)}"
    required_total = sum(1 for e in expected if e.required)

    run_results: list[RunResult] = []

    for i in range(runs):
        run_id = f"{meter_id}_RUN_{i}"
        solver_id = f"{meter_id}_SOLVER_{i}"

        try:
            harness_request = BlindSolverHarnessRequest(
                bundle_path=bundle_path,
                solver_id=solver_id,
                run_id=run_id,
                created_by="SOLVABILITY_METER",
            )
            solver = LLMBlindSolver(provider=provider)
            harness_result = run_blind_solver_harness(harness_request, solver)

            verdict = judge_conclusions(
                harness_result.report,
                expected,
                provider,
                key_evidence_ids=key_evidence_ids,
            )
        except (ProviderError, BlindSolverHarnessError, ConclusionJudgeError):
            continue

        required_met_count = sum(
            1
            for c in verdict.conclusions
            if c.met and any(e.id == c.id and e.required for e in expected)
        )

        run_results.append(
            RunResult(
                run_id=run_id,
                classification=verdict.classification,
                required_met_count=required_met_count,
                required_total=required_total,
            )
        )

    runs_completed = len(run_results)
    if runs_completed == 0:
        raise SolvabilityMeterError(f"all {runs} runs failed; no verdict could be produced")

    resolved_count = sum(1 for r in run_results if r.classification == "resolvido")
    solve_rate = resolved_count / runs_completed

    classification_counts = {c: 0 for c in _CLASSIFICATIONS}
    for r in run_results:
        classification_counts[r.classification] += 1

    flags: list[str] = []
    if classification_counts["ambiguo"] > 0:
        flags.append("AMBIGUIDADE_DETECTADA")
    if classification_counts["vazamento"] > 0:
        flags.append("VAZAMENTO_DETECTADO")
    if runs_completed < runs:
        flags.append("RUNS_INCOMPLETAS")

    return SolvabilityReport(
        meter_id=meter_id,
        bundle_id=bundle_meta.bundle_id,
        runs_requested=runs,
        runs_completed=runs_completed,
        run_results=run_results,
        solve_rate=solve_rate,
        classification_counts=classification_counts,
        difficulty_estimate=estimate_difficulty(solve_rate),
        flags=flags,
    )

"""Conclusion Judge: Evaluates expected conclusions against blind solver report.

This module implements ISSUE-33.1 STEP-03. It judges whether each expected
conclusion was adequately supported by the blind solver's report using an LLM
provider, with JSON repair loop and schema validation.

Contracts:
- CJ_001: Prompt contains report data + expected statements, nothing else.
- CJ_002: JSON repair with max_repair_attempts.
- CJ_003: All expected conclusions must appear in model response.
- CJ_004: Classification derived in Python (resolvido/nao_resolvido/vazamento/ambiguo).
- CJ_005: met=true with empty evidence_cited → rebase to met=false + warning.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.llm_provider import LLMProvider, ProviderRequest, ProviderResponseError


# --------------------------------------------------------------------------- #
# Constants and schemas                                                       #
# --------------------------------------------------------------------------- #

_JUDGE_VERDICT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "judge_verdict.schema.yaml"
)

_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parents[0] / "prompts"


# --------------------------------------------------------------------------- #
# Exceptions                                                                  #
# --------------------------------------------------------------------------- #

class ConclusionJudgeError(RuntimeError):
    """Error during conclusion judgment."""


# --------------------------------------------------------------------------- #
# Public dataclasses                                                          #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ExpectedConclusionInput:
    """An expected conclusion to be judged."""

    id: str
    statement: str
    required: bool


@dataclass(frozen=True)
class Conclusion:
    """A single judged conclusion in the verdict."""

    id: str
    met: bool
    evidence_cited: list[str]
    rationale: str


@dataclass(frozen=True)
class JudgeVerdict:
    """The verdict of the Conclusion Judge."""

    verdict_id: str
    report_run_id: str
    prompt_hash: str
    conclusions: list[Conclusion]
    alternative_solution_detected: bool
    alternative_solution_summary: str | None
    classification: str  # "resolvido" | "nao_resolvido" | "vazamento" | "ambiguo"
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Public functions                                                            #
# --------------------------------------------------------------------------- #

def judge_conclusions(
    report: Mapping[str, Any],
    expected: Sequence[ExpectedConclusionInput],
    provider: LLMProvider,
    prompt_version: str = "v1",
    max_repair_attempts: int = 1,
    key_evidence_ids: Sequence[str] | None = None,
) -> JudgeVerdict:
    """Judge expected conclusions against a blind solver report.

    Args:
        report: Mapping of blind solver report (must contain conclusion,
                reasoning_summary, evidence_used, open_questions, and run_id).
        expected: Sequence of expected conclusions to judge.
        provider: LLMProvider to call for judgment.
        prompt_version: Prompt template version (default "v1").
        max_repair_attempts: Max JSON repair attempts (default 1).
        key_evidence_ids: Optional sequence of artifact IDs that must be cited
                         for a "met" conclusion to avoid "vazamento" classification.

    Returns:
        JudgeVerdict with conclusions, classification, and warnings.

    Raises:
        ConclusionJudgeError: If report is invalid, model response is unparseable,
                             expected conclusions mismatch model response, or other
                             validation fails.
    """
    # Validate inputs
    if not expected:
        raise ConclusionJudgeError("expected conclusions list is empty")

    if not report or not isinstance(report, Mapping):
        raise ConclusionJudgeError("report must be a non-empty mapping")

    # Load prompt template and compute hash
    prompt_template = _load_prompt_template(prompt_version)
    prompt_hash = hashlib.sha256(prompt_template.encode()).hexdigest()

    # Render prompt with report and expected conclusions
    prompt = _render_prompt(prompt_template, report, expected)

    # Call provider with repair loop
    raw_verdict_dict = _call_provider_with_repair(
        provider,
        prompt,
        max_repair_attempts,
    )

    # Validate JSON structure against schema
    _validate_verdict_schema(raw_verdict_dict)

    # Extract report_run_id from report (try common keys), with a schema-conformant
    # fallback (HD_005): the schema requires minLength: 2, so "" is not an option.
    report_run_id = _resolve_report_run_id(report)

    # Build verdicts list in the order of expected (CJ_003)
    verdict_conclusions_dict = {
        c["id"]: c for c in raw_verdict_dict.get("conclusions", [])
    }

    verdict_conclusions: list[Conclusion] = []
    for exp in expected:
        if exp.id not in verdict_conclusions_dict:
            raise ConclusionJudgeError(
                f"Expected conclusion '{exp.id}' not found in model verdict"
            )

        raw_conclusion = verdict_conclusions_dict[exp.id]
        conclusion = Conclusion(
            id=raw_conclusion["id"],
            met=raw_conclusion["met"],
            evidence_cited=list(raw_conclusion.get("evidence_cited", [])),
            rationale=raw_conclusion.get("rationale", ""),
        )

        verdict_conclusions.append(conclusion)

    # CJ_005: Rebase met=false if evidence_cited is empty
    warnings: list[str] = []
    rebased_conclusions: list[Conclusion] = []

    for conclusion in verdict_conclusions:
        if conclusion.met is True and len(conclusion.evidence_cited) == 0:
            # Rebase to met=false
            rebased = replace(conclusion, met=False)
            rebased_conclusions.append(rebased)
            warnings.append(
                f"Conclusion '{conclusion.id}' claimed met=true "
                "but provided no evidence_cited; rebased to met=false."
            )
        else:
            rebased_conclusions.append(conclusion)

    # CJ_004: Derive classification
    classification = _derive_classification(
        rebased_conclusions,
        expected,
        raw_verdict_dict.get("alternative_solution_detected", False),
        key_evidence_ids,
    )

    # Build final verdict
    verdict = JudgeVerdict(
        verdict_id=raw_verdict_dict.get("verdict_id", f"VERDICT_{int(datetime.now(timezone.utc).timestamp())}"),
        report_run_id=report_run_id,
        prompt_hash=prompt_hash,
        conclusions=rebased_conclusions,
        alternative_solution_detected=raw_verdict_dict.get("alternative_solution_detected", False),
        alternative_solution_summary=raw_verdict_dict.get("alternative_solution_summary"),
        classification=classification,
        warnings=warnings,
    )

    # HD_005: the final verdict (including generated defaults) must itself be
    # schema-valid; never return it unchecked just because raw_verdict_dict was.
    _validate_verdict_schema(asdict(verdict))

    return verdict


# --------------------------------------------------------------------------- #
# Private helpers                                                             #
# --------------------------------------------------------------------------- #

def _resolve_report_run_id(report: Mapping[str, Any]) -> str:
    """Resolve report_run_id with a schema-conformant fallback (HD_005)."""
    candidate = report.get("solver_run_id") or report.get("run_id")
    if candidate:
        return str(candidate)
    return "UNKNOWN_RUN"


def _load_prompt_template(version: str) -> str:
    """Load the prompt template for the given version."""
    template_path = _PROMPT_TEMPLATE_PATH / f"conclusion_judge_{version}.md"

    try:
        return template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConclusionJudgeError(
            f"Failed to load prompt template {template_path}: {exc}"
        ) from exc


def _render_prompt(
    template: str,
    report: Mapping[str, Any],
    expected: Sequence[ExpectedConclusionInput],
) -> str:
    """Render prompt template with report data and expected conclusions."""
    # Extract report fields for substitution
    conclusion = report.get("conclusion", "")
    confidence = report.get("confidence", "")
    reasoning_summary = report.get("reasoning_summary", "")
    open_questions = report.get("open_questions", [])

    # Format evidence_used
    evidence_used = report.get("evidence_used", [])
    if isinstance(evidence_used, list):
        evidence_str = "\n".join(
            f"- Artifact {e.get('artifact_id', 'UNKNOWN')}: "
            f"{e.get('quote_or_summary', 'No summary')}"
            for e in evidence_used
        )
    else:
        evidence_str = str(evidence_used)

    # Format open_questions
    if isinstance(open_questions, list):
        open_qs_str = "\n".join(f"- {q}" for q in open_questions)
    else:
        open_qs_str = str(open_questions)

    # Format expected conclusions
    expected_conclusions_str = "\n".join(
        f"- **{e.id}** (required={e.required}): {e.statement}"
        for e in expected
    )

    # Render template
    rendered = template.format(
        conclusion=conclusion,
        confidence=confidence,
        reasoning_summary=reasoning_summary,
        evidence_used=evidence_str,
        open_questions=open_qs_str,
        expected_conclusions=expected_conclusions_str,
        report_run_id=report.get("solver_run_id", report.get("run_id", "UNKNOWN")),
    )

    return rendered


def _call_provider_with_repair(
    provider: LLMProvider,
    prompt: str,
    max_repair_attempts: int,
) -> dict[str, Any]:
    """Call provider and attempt repair if JSON is invalid (CJ_002)."""
    current_prompt = prompt
    last_error: str | None = None

    for attempt in range(max_repair_attempts + 1):
        try:
            request = ProviderRequest(prompt=current_prompt, temperature=0.0)
            response = provider.complete(request)
            result_dict = json.loads(response.text)
            return result_dict
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            if attempt < max_repair_attempts:
                # Construct repair prompt
                current_prompt = (
                    f"{prompt}\n\n"
                    "[REPAIR ATTEMPT]\n"
                    f"Previous response was invalid JSON. Error: {last_error}\n"
                    "Please respond with valid JSON only."
                )
            else:
                raise ConclusionJudgeError(
                    f"Failed to parse JSON after {max_repair_attempts + 1} attempts. "
                    f"Last error: {last_error}"
                ) from exc
        except ProviderResponseError as exc:
            raise ConclusionJudgeError(f"Provider error: {exc}") from exc

    raise ConclusionJudgeError("Unexpected: repair loop failed")


def _validate_verdict_schema(verdict: Mapping[str, Any]) -> None:
    """Validate verdict structure against judge_verdict.schema.yaml."""
    schema = yaml.safe_load(_JUDGE_VERDICT_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    errors = list(validator.iter_errors(verdict))
    if errors:
        error_messages = "; ".join(e.message for e in errors)
        raise ConclusionJudgeError(f"Verdict schema validation failed: {error_messages}")


def _derive_classification(
    conclusions: Sequence[Conclusion],
    expected: Sequence[ExpectedConclusionInput],
    alternative_solution_detected: bool,
    key_evidence_ids: Sequence[str] | None = None,
) -> str:
    """Derive classification based on conclusions and rules (CJ_004).

    Precedence (when multiple apply):
    1. ambiguo (if alternative_solution_detected)
    2. vazamento (if any met=true conclusion doesn't cite key_evidence_ids)
    3. nao_resolvido (if any required=true conclusion has met=false)
    4. resolvido (all required=true conclusions have met=true)
    """
    # Create a dict mapping conclusion id -> expected
    expected_by_id = {e.id: e for e in expected}

    # Check for ambiguous solutions
    if alternative_solution_detected:
        return "ambiguo"

    # Check for vazamento (evidence leak)
    if key_evidence_ids:
        key_evidence_set = set(key_evidence_ids)
        for conclusion in conclusions:
            if conclusion.met is True:
                cited_set = set(conclusion.evidence_cited)
                if not cited_set & key_evidence_set:  # No overlap
                    return "vazamento"

    # Check for unresolved required conclusions
    for conclusion in conclusions:
        exp = expected_by_id.get(conclusion.id)
        if exp and exp.required is True and conclusion.met is False:
            return "nao_resolvido"

    # All required are met
    return "resolvido"

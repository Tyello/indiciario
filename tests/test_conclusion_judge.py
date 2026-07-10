"""Tests for Conclusion Judge (ISSUE-33.1 STEP-02).

Cases cover:
- CJ_001: Sentinel test (architecture): report content in prompt, external content not.
- CJ_002: JSON repair on invalid first response.
- CJ_003: Missing expected conclusion item raises error.
- CJ_004: Classification derivation (nao_resolvido, ambiguo, vazamento, precedence).
- CJ_005: Empty evidence_cited with met=true is rebased to met=false + warning.
- CJ_006: Happy path with valid verdict.
- CJ_007: Schema validation of JudgeVerdict serialization.
- CJ_008: Bridge to gate evaluator (GE_004 rule).

Note: These tests are sentinels for generator.conclusion_judge, which will be
implemented in STEP-03. Until then, tests fail on import of that module.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from generator.fake_provider import FakeProvider, ScriptedResponse
from generator.gate_evaluator import (
    ConfidenceAssessment,
    ExpectedConclusion,
    GateEvaluationRequest,
    build_gate_evaluation,
)

# These imports will fail until STEP-03 (expected RED behavior)
from generator.conclusion_judge import (
    ConclusionJudgeError,
    ExpectedConclusionInput,
    JudgeVerdict,
    judge_conclusions,
)


# ============================================================================ #
# Fixtures and helpers                                                        #
# ============================================================================ #


def minimal_report(**overrides: object) -> dict[str, Any]:
    """Return a minimal BlindSolverReport-like mapping."""
    data = dict(
        schema_version="1.0",
        solver_run_id="SOLVER_RUN_001",
        solver_id="SOLVER_001",
        bundle_id="BUNDLE_001",
        manifest_id="MANIFEST_001",
        created_at="2026-07-09T10:00:00Z",
        conclusion="O culpado é Alice porque ela executou a troca física.",
        confidence="high",
        reasoning_summary="Análise das evidências: documentos comerciais, recibos e OS.",
        evidence_used=[
            {
                "artifact_id": "ART_001",
                "path": "documents/recibo.md",
                "quote_or_summary": "Recibo de pagamento",
                "relevance": "Prova de transação",
                "confidence": "high",
            }
        ],
        open_questions=[],
        assumptions=["Alice had motive and opportunity"],
        warnings=[],
    )
    data.update(overrides)
    return data


def minimal_expected_conclusion(**overrides: object) -> ExpectedConclusionInput:
    """Return a minimal ExpectedConclusionInput."""
    data = dict(
        id="culpado",
        statement="O culpado é quem executou a troca física.",
        required=True,
    )
    data.update(overrides)
    return ExpectedConclusionInput(**data)


def build_valid_verdict_json(**overrides: object) -> dict[str, Any]:
    """Build a minimal valid verdict JSON that matches the expected schema."""
    data = dict(
        verdict_id="VERDICT_001",
        report_run_id="SOLVER_RUN_001",
        prompt_hash="abc123def456",
        conclusions=[
            {
                "id": "culpado",
                "met": True,
                "evidence_cited": ["ART_001"],
                "rationale": "Documentos comprovam a execução.",
            }
        ],
        alternative_solution_detected=False,
        alternative_solution_summary=None,
    )
    data.update(overrides)
    return data


# ============================================================================ #
# CJ_006: Happy path                                                          #
# ============================================================================ #


def test_cj006_happy_path_valid_verdict() -> None:
    """Valid verdict from FakeProvider → JudgeVerdict with conclusions in order."""
    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)

    assert isinstance(result, JudgeVerdict)
    assert len(result.conclusions) == 1
    assert result.conclusions[0].id == "culpado"
    assert result.conclusions[0].met is True
    assert result.classification == "resolvido"


# ============================================================================ #
# CJ_003: Missing expected item                                               #
# ============================================================================ #


def test_cj003_missing_expected_conclusion_item() -> None:
    """FakeProvider returns verdict without expected item → ConclusionJudgeError."""
    report = minimal_report()
    # Expect two conclusions: culpado, metodo
    expected = [
        minimal_expected_conclusion(id="culpado"),
        minimal_expected_conclusion(id="metodo"),
    ]

    # But fake only returns one
    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    with pytest.raises(ConclusionJudgeError):
        judge_conclusions(report, expected, provider)


# ============================================================================ #
# CJ_004: Classification derivation (unit tests, no provider)                 #
# ============================================================================ #


def test_cj004_classification_all_required_met() -> None:
    """All required conclusions met → classification='resolvido'."""
    report = minimal_report()
    expected = [
        minimal_expected_conclusion(id="culpado", required=True),
        minimal_expected_conclusion(id="metodo", required=True),
    ]

    verdict_json = build_valid_verdict_json(
        conclusions=[
            {
                "id": "culpado",
                "met": True,
                "evidence_cited": ["ART_001"],
                "rationale": "Evidence found.",
            },
            {
                "id": "metodo",
                "met": True,
                "evidence_cited": ["ART_001"],
                "rationale": "Evidence found.",
            },
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)
    assert result.classification == "resolvido"


def test_cj004_classification_required_not_met() -> None:
    """Some required not met, no alternative → classification='nao_resolvido'."""
    report = minimal_report()
    expected = [
        minimal_expected_conclusion(id="culpado", required=True),
        minimal_expected_conclusion(id="motivo", required=False),
    ]

    verdict_json = build_valid_verdict_json(
        alternative_solution_detected=False,
        conclusions=[
            {
                "id": "culpado",
                "met": False,  # Required but not met
                "evidence_cited": [],
                "rationale": "Insufficient evidence.",
            },
            {
                "id": "motivo",
                "met": True,
                "evidence_cited": ["ART_001"],
                "rationale": "Evidence found.",
            },
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)
    assert result.classification == "nao_resolvido"


def test_cj004_classification_alternative_detected() -> None:
    """Alternative solution detected → classification='ambiguo' even if all met."""
    report = minimal_report()
    expected = [
        minimal_expected_conclusion(id="culpado", required=True),
    ]

    verdict_json = build_valid_verdict_json(
        alternative_solution_detected=True,
        alternative_solution_summary="Could also be Bob based on evidence.",
        conclusions=[
            {
                "id": "culpado",
                "met": True,
                "evidence_cited": ["ART_001"],
                "rationale": "Evidence supports Alice.",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)
    assert result.classification == "ambiguo"


def test_cj004_classification_evidence_leak() -> None:
    """key_evidence_ids provided but none cited in met conclusions → 'vazamento'."""
    report = minimal_report()
    expected = [
        minimal_expected_conclusion(id="culpado", required=True),
    ]

    verdict_json = build_valid_verdict_json(
        conclusions=[
            {
                "id": "culpado",
                "met": True,
                "evidence_cited": ["ART_002"],  # Different artifact, not key
                "rationale": "Some evidence.",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    # Call with key_evidence_ids to trigger leak detection
    result = judge_conclusions(
        report,
        expected,
        provider,
        key_evidence_ids=["ART_001"],  # Expected to be cited
    )
    assert result.classification == "vazamento"


def test_cj004_classification_precedence_ambiguo_over_vazamento() -> None:
    """When both ambiguo and vazamento apply, ambiguo takes precedence."""
    report = minimal_report()
    expected = [
        minimal_expected_conclusion(id="culpado", required=True),
    ]

    verdict_json = build_valid_verdict_json(
        alternative_solution_detected=True,
        alternative_solution_summary="Alternative found.",
        conclusions=[
            {
                "id": "culpado",
                "met": True,
                "evidence_cited": ["ART_002"],  # Not in key_evidence_ids
                "rationale": "Some evidence.",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(
        report,
        expected,
        provider,
        key_evidence_ids=["ART_001"],
    )
    # ambiguo wins over vazamento
    assert result.classification == "ambiguo"


# ============================================================================ #
# CJ_005: Empty evidence_cited rebased to met=False + warning                 #
# ============================================================================ #


def test_cj005_empty_evidence_cited_rebased() -> None:
    """met=true with evidence_cited=[] → met=false + warning in result."""
    report = minimal_report()
    expected = [minimal_expected_conclusion(id="culpado")]

    verdict_json = build_valid_verdict_json(
        conclusions=[
            {
                "id": "culpado",
                "met": True,  # Model says true
                "evidence_cited": [],  # But no evidence cited
                "rationale": "Seems right but no proof.",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)

    # Should be rebased to met=false
    assert result.conclusions[0].met is False
    # Should have a warning
    assert len(result.warnings) > 0
    assert any("evidence" in w.lower() for w in result.warnings)


# ============================================================================ #
# CJ_002: JSON repair loop                                                    #
# ============================================================================ #


def test_cj002_repair_first_invalid_second_valid() -> None:
    """First response invalid + second valid with max_repair_attempts=1 → success."""
    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    invalid_json = "{ invalid json"
    valid_json = json.dumps(build_valid_verdict_json())

    provider = FakeProvider([
        ScriptedResponse(text=invalid_json),
        ScriptedResponse(text=valid_json),
    ])

    result = judge_conclusions(report, expected, provider, max_repair_attempts=1)
    assert result.conclusions[0].id == "culpado"


def test_cj002_repair_exhausted_raises_error() -> None:
    """Two invalid responses with max_repair_attempts=1 → ConclusionJudgeError."""
    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    invalid_json1 = "{ invalid json 1"
    invalid_json2 = "{ invalid json 2"

    provider = FakeProvider([
        ScriptedResponse(text=invalid_json1),
        ScriptedResponse(text=invalid_json2),
    ])

    with pytest.raises(ConclusionJudgeError):
        judge_conclusions(report, expected, provider, max_repair_attempts=1)


# ============================================================================ #
# CJ_001: Sentinel test (architecture)                                        #
# ============================================================================ #


def test_cj001_prompt_contains_report_statements_not_blueprint() -> None:
    """Prompt includes report content + expected statements; excludes blueprint content."""
    report = minimal_report(
        reasoning_summary="SENTINELA_REPORT_REASONING"
    )
    expected = [
        minimal_expected_conclusion(
            statement="SENTINELA_STATEMENT_EXPECTED"
        )
    ]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    judge_conclusions(report, expected, provider)

    # Inspect the prompt that was sent to the provider
    assert len(provider.calls) > 0
    prompt = provider.calls[0].prompt

    # Should contain report reasoning
    assert "SENTINELA_REPORT_REASONING" in prompt
    # Should contain expected statement
    assert "SENTINELA_STATEMENT_EXPECTED" in prompt
    # Should NOT contain blueprint-only content
    assert "SENTINELA_BLUEPRINT_FORA" not in prompt


# ============================================================================ #
# CJ_007: Schema validation                                                   #
# ============================================================================ #


def _load_judge_verdict_schema() -> dict[str, Any]:
    import yaml

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "judge_verdict.schema.yaml"
    )
    return yaml.safe_load(schema_path.read_text(encoding="utf-8"))


def test_cj007_judge_verdict_serialization_validates_schema() -> None:
    """JudgeVerdict serialized validates against schemas/judge_verdict.schema.yaml."""
    from jsonschema import Draft202012Validator

    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)

    verdict_dict = asdict(result)
    schema = _load_judge_verdict_schema()

    Draft202012Validator(schema).validate(verdict_dict)


def test_cj007_schema_rejects_additional_properties() -> None:
    """JudgeVerdict schema forbids additionalProperties."""
    from jsonschema import Draft202012Validator, ValidationError

    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)
    verdict_dict = asdict(result)

    # Add an extra field not declared in the schema
    verdict_dict["extra_field"] = "should_be_rejected"

    schema = _load_judge_verdict_schema()

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(verdict_dict)


# ============================================================================ #
# HD_005: final verdict always schema-valid (ISSUE-33.4)                      #
# ============================================================================ #


def test_hd005_missing_run_id_falls_back_to_schema_valid_default() -> None:
    """HD_005: report without solver_run_id/run_id -> verdict still schema-valid."""
    report = minimal_report()
    del report["solver_run_id"]
    expected = [minimal_expected_conclusion()]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    result = judge_conclusions(report, expected, provider)

    assert len(result.report_run_id) >= 2

    schema = _load_judge_verdict_schema()
    from jsonschema import Draft202012Validator

    Draft202012Validator(schema).validate(asdict(result))


def test_hd005_broken_default_fails_revalidation_not_silent_return(monkeypatch: pytest.MonkeyPatch) -> None:
    """HD_005: a broken default (report_run_id shorter than minLength) must raise, not return silently."""
    import generator.conclusion_judge as conclusion_judge_module

    monkeypatch.setattr(conclusion_judge_module, "_resolve_report_run_id", lambda report: "")

    report = minimal_report()
    expected = [minimal_expected_conclusion()]

    verdict_json = build_valid_verdict_json()
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    with pytest.raises(ConclusionJudgeError):
        judge_conclusions(report, expected, provider)


# ============================================================================ #
# CJ_008: Bridge to gate evaluator                                            #
# ============================================================================ #


def test_cj008_verdict_feeds_gate_evaluator_ge004() -> None:
    """JudgeVerdict.conclusions → ExpectedConclusion → build_gate_evaluation.

    Scenario: required conclusion with met=false + decision=approved → GE_004 error.
    """
    report = minimal_report()
    expected = [minimal_expected_conclusion(id="culpado", required=True)]

    # Judge says the required conclusion is not met
    verdict_json = build_valid_verdict_json(
        conclusions=[
            {
                "id": "culpado",
                "met": False,  # Not met!
                "evidence_cited": [],
                "rationale": "Insufficient evidence.",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=json.dumps(verdict_json))])

    judge_verdict = judge_conclusions(report, expected, provider)

    # Convert JudgeVerdict conclusions to ExpectedConclusion for the gate
    expected_conclusions_for_gate = [
        ExpectedConclusion(
            id=c.id,
            description=next(
                e.statement for e in expected if e.id == c.id
            ),
            required=next(
                e.required for e in expected if e.id == c.id
            ),
            met=c.met,
            evidence=c.rationale,
        )
        for c in judge_verdict.conclusions
    ]

    # Build a gate evaluation with this verdict
    run_record = {
        "run_id": "RUN_001",
        "bundle_id": "BUNDLE_001",
    }

    request = GateEvaluationRequest(
        run_record=run_record,
        private_solution_ref="Author's solution",
        evaluator_id="HUMAN_EVAL_001",
        evaluation_id="EVAL_001",
    )

    gate_eval = build_gate_evaluation(
        request=request,
        expected_conclusions=expected_conclusions_for_gate,
        unexpected_valid_hypotheses=[],
        gaps=[],
        confidence_assessment=ConfidenceAssessment(
            solver_confidence="high",
            evaluator_agreement="partial",
            notes="Test assertion: required conclusion not met",
        ),
        decision="approved",
        justification="Judge verdict shows unmet required conclusion.",
    )

    # Import validation to check GE_004
    from generator.gate_evaluator import validate_gate_evaluation_semantics

    result = validate_gate_evaluation_semantics(gate_eval)

    # Should have GE_004 error because decision=approved but required not met
    assert any("GE_004" in error for error in result.semantic_errors)

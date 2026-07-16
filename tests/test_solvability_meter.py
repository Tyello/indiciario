"""Tests for the Solvability Meter (ISSUE-33.2).

Cases cover:
- SM_001: invalid runs/temperature raise ValueError before any provider call.
- Happy path 3/3, 2/3, 1/3, 0/3 resolved -> solve_rate and difficulty_estimate.
- SM_004: ambiguo/vazamento flags.
- SM_002: partial run failure (RUNS_INCOMPLETAS) and total failure (error).
- SM_003: threshold table at the edges, no provider involved.
- Schema: report serialization validates against solvability_report.schema.yaml.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError

from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    build_blind_bundle,
)
from generator.conclusion_judge import ExpectedConclusionInput
from generator.fake_provider import FakeProvider, ScriptedResponse
from generator.llm_provider import ProviderTransportError
from generator.solvability_meter import (
    SolvabilityMeterError,
    SolvabilityReport,
    estimate_difficulty_from_solve_rate,
    measure_solvability,
)

FIXED_CREATED_AT = "2026-06-14T00:00:00Z"


# ============================================================================ #
# Bundle fixtures (mirrors tests/test_llm_blind_solver.py)                    #
# ============================================================================ #


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento publico bruto\n")
    write(source / "private/solution.md", "Solucao privada\n")
    return source


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    root = tmp_path / "bundles"
    root.mkdir()
    return root


def public_spec(**overrides: object) -> ArtifactSpec:
    data = dict(
        artifact_id="ART_PUBLIC_001",
        source_path="public/envelope_1/depoimento.md",
        bundle_path="player/depoimento.md",
        artifact_type="player_document",
        visibility="public_player",
        envelope_scope="current_envelope",
        source_role="author",
        included_reason="Documento publico de jogador listado explicitamente para o bundle cego.",
        contains_solution=False,
        contains_future_envelopes=False,
        contains_private_author_notes=False,
        contains_other_agents_outputs=False,
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def build_request(source_tree: Path, output_root: Path, **overrides: object) -> BlindBundleBuildRequest:
    data = dict(
        manifest_id="MANIFEST_METER_001",
        run_id="RUN_METER_001",
        bundle_id="BUNDLE_METER_001",
        case_id="CASE_METER_001",
        case_version="V1",
        role="blind_solver",
        stage="blind_solve",
        source_root=source_tree,
        output_root=output_root,
        created_by="HUMAN_OPERATOR_001",
        artifact_specs=[public_spec()],
        generation_mode="manual",
        offline_safe=True,
        neutralize_paths=False,
        overwrite=False,
        created_at="2026-06-13T00:00:00Z",
    )
    data.update(overrides)
    return BlindBundleBuildRequest(**data)


def make_bundle(source_tree: Path, output_root: Path, **overrides: object) -> Path:
    return build_blind_bundle(build_request(source_tree, output_root, **overrides)).output_path


# ============================================================================ #
# Provider script helpers                                                    #
# ============================================================================ #


def solver_response_json(**extra_fields: object) -> str:
    """Build a minimal valid BlindSolverReport response as JSON."""
    response = {
        "schema_version": "1.0",
        "solver_run_id": "ANY",
        "solver_id": "ANY",
        "bundle_id": "ANY",
        "manifest_id": "ANY",
        "created_at": FIXED_CREATED_AT,
        "conclusion": "O culpado e Alice.",
        "confidence": "high",
        "reasoning_summary": "Analise das evidencias disponiveis.",
        "evidence_used": [
            {
                "artifact_id": "ART_PUBLIC_001",
                "path": "player/depoimento.md",
                "quote_or_summary": "Depoimento aponta Alice.",
                "relevance": "Suporta a hipotese principal.",
                "confidence": "high",
            }
        ],
        "open_questions": [],
        "assumptions": [],
        "warnings": [],
    }
    response.update(extra_fields)
    return json.dumps(response)


def judge_response_json(met: bool = True, evidence_cited: list[str] | None = None, **extra_fields: object) -> str:
    """Build a minimal valid JudgeVerdict response as JSON."""
    if evidence_cited is None:
        evidence_cited = ["ART_PUBLIC_001"] if met else []
    response = {
        "verdict_id": "VERDICT_ANY",
        "report_run_id": "ANY",
        "prompt_hash": "abc123def456",
        "conclusions": [
            {
                "id": "culpado",
                "met": met,
                "evidence_cited": evidence_cited,
                "rationale": "Racional do julgamento.",
            }
        ],
        "alternative_solution_detected": False,
        "alternative_solution_summary": None,
    }
    response.update(extra_fields)
    return json.dumps(response)


def expected_conclusions() -> list[ExpectedConclusionInput]:
    return [
        ExpectedConclusionInput(
            id="culpado",
            statement="O culpado e quem aparece no depoimento.",
            required=True,
        )
    ]


def run_pair(met: bool = True, judge_overrides: dict[str, Any] | None = None) -> list[ScriptedResponse]:
    """One run = one solver call + one judge call."""
    judge_overrides = judge_overrides or {}
    return [
        ScriptedResponse(text=solver_response_json()),
        ScriptedResponse(text=judge_response_json(met=met, **judge_overrides)),
    ]


# ============================================================================ #
# SM_001: input validation                                                   #
# ============================================================================ #


def test_sm001_runs_zero_raises_before_provider_call(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    provider = FakeProvider([])

    with pytest.raises(ValueError):
        measure_solvability(bundle, expected_conclusions(), provider, runs=0)

    assert provider.calls == ()


def test_sm001_temperature_out_of_range_raises_before_provider_call(
    source_tree: Path, output_root: Path
) -> None:
    bundle = make_bundle(source_tree, output_root)
    provider = FakeProvider([])

    with pytest.raises(ValueError):
        measure_solvability(bundle, expected_conclusions(), provider, runs=3, temperature=3.0)

    assert provider.calls == ()


# ============================================================================ #
# Happy path / solve_rate / difficulty_estimate table                        #
# ============================================================================ #


def test_sm_three_of_three_resolved_is_facil(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    for _ in range(3):
        script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert isinstance(report, SolvabilityReport)
    assert report.runs_completed == 3
    assert report.solve_rate == 1.0
    assert report.difficulty_estimate == "facil"
    assert report.flags == []
    assert report.classification_counts["resolvido"] == 3


def test_sm_two_of_three_resolved_is_medio(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    script.extend(run_pair(met=False))
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert report.runs_completed == 3
    assert report.solve_rate == pytest.approx(2 / 3)
    assert report.difficulty_estimate == "medio"


def test_sm_one_of_three_resolved_is_dificil(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    script.extend(run_pair(met=False))
    script.extend(run_pair(met=False))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert report.solve_rate == pytest.approx(1 / 3)
    assert report.difficulty_estimate == "dificil"


def test_sm_zero_of_three_resolved_is_injusto(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    for _ in range(3):
        script.extend(run_pair(met=False))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert report.solve_rate == 0.0
    assert report.difficulty_estimate == "injusto"


# ============================================================================ #
# SM_004: flags                                                              #
# ============================================================================ #


def test_sm004_ambiguo_run_sets_flag(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    script.extend(run_pair(met=True, judge_overrides={"alternative_solution_detected": True, "alternative_solution_summary": "Poderia ser Bob."}))
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert "AMBIGUIDADE_DETECTADA" in report.flags
    assert report.classification_counts["ambiguo"] == 1


def test_sm004_vazamento_run_sets_flag(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    # met=True but cites an artifact outside key_evidence_ids -> vazamento.
    script = run_pair(met=True, judge_overrides={"conclusions": [
        {
            "id": "culpado",
            "met": True,
            "evidence_cited": ["ART_OUTRO"],
            "rationale": "Evidencia fora do conjunto chave.",
        }
    ]})
    provider = FakeProvider(script)

    report = measure_solvability(
        bundle, expected_conclusions(), provider, runs=1, key_evidence_ids=["ART_PUBLIC_001"]
    )

    assert "VAZAMENTO_DETECTADO" in report.flags
    assert report.classification_counts["vazamento"] == 1


# ============================================================================ #
# SM_002: partial and total run failure                                      #
# ============================================================================ #


def test_sm002_one_failed_run_is_incomplete_not_fatal(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[Any] = []
    script.extend(run_pair(met=True))  # run 0 ok
    script.append(ProviderTransportError("network down"))  # run 1: solver call fails
    script.extend(run_pair(met=True))  # run 2 ok
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert report.runs_completed == 2
    assert report.runs_requested == 3
    assert "RUNS_INCOMPLETAS" in report.flags


def test_hd_non_object_json_counts_as_incomplete_run_not_fatal(
    source_tree: Path, output_root: Path
) -> None:
    """HD_001 integration: a run whose solver returns non-object JSON is incomplete, not fatal."""
    bundle = make_bundle(source_tree, output_root)
    non_dict_json = json.dumps([1, 2, 3])
    script: list[Any] = []
    script.extend(run_pair(met=True))  # run 0 ok
    script.append(ScriptedResponse(text=non_dict_json))  # run 1: solver attempt 1, non-object
    script.append(ScriptedResponse(text=non_dict_json))  # run 1: solver repair attempt, still non-object
    script.extend(run_pair(met=True))  # run 2 ok
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)

    assert report.runs_completed == 2
    assert report.runs_requested == 3
    assert "RUNS_INCOMPLETAS" in report.flags


def test_sm002_all_runs_failed_raises_error(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[Any] = [
        ProviderTransportError("network down"),
        ProviderTransportError("network down"),
    ]
    provider = FakeProvider(script)

    with pytest.raises(SolvabilityMeterError):
        measure_solvability(bundle, expected_conclusions(), provider, runs=2)


# ============================================================================ #
# SM_003: threshold table (unit, no provider)                                #
# ============================================================================ #


@pytest.mark.parametrize(
    "solve_rate,expected_difficulty",
    [
        (1.0, "facil"),
        (0.5, "medio"),
        (0.34, "dificil"),
        (0.0, "injusto"),
    ],
)
def test_sm003_difficulty_threshold_table(solve_rate: float, expected_difficulty: str) -> None:
    assert estimate_difficulty_from_solve_rate(solve_rate) == expected_difficulty


# ============================================================================ #
# RM_001, RM_002, RM_004: Reproducibility block and provider calls           #
# ============================================================================ #


def test_rm001_temperature_reaches_solver_provider_requests_not_judge(
    source_tree: Path, output_root: Path
) -> None:
    """RM_001: solver receives configured temperature; judge uses fixed 0.0."""
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    measure_solvability(bundle, expected_conclusions(), provider, runs=1, temperature=0.7)

    # Check provider.calls order and temperature values
    assert len(provider.calls) == 2, f"Expected 2 calls (solver + judge), got {len(provider.calls)}"
    assert provider.calls[0].temperature == 0.7, f"Solver call should have temperature=0.7, got {provider.calls[0].temperature}"
    assert provider.calls[-1].temperature == 0.0, f"Judge call should have temperature=0.0, got {provider.calls[-1].temperature}"


def test_rm002_reproducibility_block_populated(source_tree: Path, output_root: Path) -> None:
    """RM_002: reproducibility block is fully populated with all expected fields."""
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=2, temperature=0.5)

    assert report.reproducibility["temperature"] == 0.5
    assert report.reproducibility["provider_id"] == provider.provider_id
    assert report.reproducibility["runs_requested"] == 2

    solver_sha = report.reproducibility["solver_prompt_sha256"]
    judge_sha = report.reproducibility["judge_prompt_sha256"]
    assert isinstance(solver_sha, str) and len(solver_sha) == 64, \
        f"solver_prompt_sha256 should be 64-char hex string, got {solver_sha}"
    assert isinstance(judge_sha, str) and len(judge_sha) == 64, \
        f"judge_prompt_sha256 should be 64-char hex string, got {judge_sha}"


def test_rm004_solver_prompt_sha256_matches_template_file(source_tree: Path, output_root: Path) -> None:
    """RM_004: solver_prompt_sha256 matches the actual blind_solver_v1.md file hash."""
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=1)

    # Compute the hash independently from the template file
    template_path = Path(__file__).resolve().parents[1] / "generator" / "prompts" / "blind_solver_v1.md"
    expected_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()

    assert report.reproducibility["solver_prompt_sha256"] == expected_hash, \
        f"solver_prompt_sha256 mismatch: got {report.reproducibility['solver_prompt_sha256']}, expected {expected_hash}"


# ============================================================================ #
# Schema validation                                                          #
# ============================================================================ #


def _load_solvability_report_schema() -> dict[str, Any]:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "solvability_report.schema.yaml"
    )
    return yaml.safe_load(schema_path.read_text(encoding="utf-8"))


def test_schema_report_serialization_validates(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    for _ in range(3):
        script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)
    report_dict = asdict(report)

    schema = _load_solvability_report_schema()
    Draft202012Validator(schema).validate(report_dict)


def test_schema_rejects_additional_properties(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    for _ in range(3):
        script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    report = measure_solvability(bundle, expected_conclusions(), provider, runs=3)
    report_dict = asdict(report)
    report_dict["extra_field"] = "should_be_rejected"

    schema = _load_solvability_report_schema()
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(report_dict)


# ============================================================================ #
# RM_003: provider with supports_temperature=False                           #
# ============================================================================ #


def test_rm003_provider_temperature_support_false_sets_none_and_note(
    source_tree: Path, output_root: Path
) -> None:
    """RM_003: when provider.supports_temperature is False, reproducibility.temperature should be None.

    This tests the expected behavior after STEP-04 implementation: if a provider
    declares it does not support temperature control, the meter should not record
    a temperature value in the report, even if one was requested.
    """
    bundle = make_bundle(source_tree, output_root)
    script: list[ScriptedResponse] = []
    script.extend(run_pair(met=True))
    provider = FakeProvider(script)

    # Force provider to declare it does not support temperature
    # (Python allows setting attributes on instances without __slots__)
    provider.supports_temperature = False

    report = measure_solvability(
        bundle, expected_conclusions(), provider, runs=1, temperature=0.7
    )

    # When provider does not support temperature control, the meter should
    # not record a temperature value in reproducibility
    assert report.reproducibility.get("temperature") is None
    assert report.reproducibility.get("temperature_note") == "provider-controlled"

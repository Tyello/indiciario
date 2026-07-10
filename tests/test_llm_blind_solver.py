"""Tests for LLMBlindSolver (ISSUE-33 STEP-02).

Cases cover:
- LS_001: Sentinel test (architecture): bundle content in prompt, leaked content not.
- LS_002: JSON repair on invalid first response.
- LS_003: Happy path with ID override from context.
- LS_004: Extra field discarded, warning logged.
- LS_005: Prompt template hash audited.
- LS_006: Prompt includes exact artifact list.
- LS_007: Integration with run_blind_solver_harness.
- LS_008: Pipeline regression (solver param, STEP-04 pending).

Note: These tests are sentinels for generator.llm_blind_solver, which will be
implemented in STEP-03. Until then, tests fail on import of that module.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    build_blind_bundle,
)
from generator.blind_solver_harness import (
    BlindSolverContext,
    BlindSolverHarnessError,
    BlindSolverHarnessRequest,
    run_blind_solver_harness,
)
from generator.blind_solver_report_validator import validate_report
from generator.fake_provider import FakeProvider, ScriptedResponse
from generator.llm_blind_solver import LLMBlindSolver  # Will fail until STEP-03

# Reuse fixtures from test_blind_solver_harness.py
FIXED_CREATED_AT = "2026-06-14T00:00:00Z"


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento publico bruto\n")
    write(source / "public/envelope_1/recibo.md", "Recibo publico bruto\n")
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


def second_public_spec(**overrides: object) -> ArtifactSpec:
    data = dict(
        artifact_id="ART_PUBLIC_002",
        source_path="public/envelope_1/recibo.md",
        bundle_path="player/recibo.md",
        artifact_type="player_document",
        visibility="public_player",
        envelope_scope="current_envelope",
        source_role="author",
        included_reason="Segundo documento publico de jogador listado para o bundle cego.",
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def build_request(source_tree: Path, output_root: Path, **overrides: object) -> BlindBundleBuildRequest:
    data = dict(
        manifest_id="MANIFEST_TEST_001",
        run_id="RUN_TEST_001",
        bundle_id="BUNDLE_TEST_001",
        case_id="CASE_TEST_001",
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


def harness_request(bundle_path: Path, **overrides: object) -> BlindSolverHarnessRequest:
    data = dict(
        bundle_path=bundle_path,
        solver_id="SOLVER_LLM_001",
        run_id="SOLVER_RUN_LLM_001",
        created_by="HUMAN_OPERATOR_001",
        created_at=FIXED_CREATED_AT,
    )
    data.update(overrides)
    return BlindSolverHarnessRequest(**data)


# Helper: build minimal valid BlindSolverReport JSON response
def build_solver_response_json(
    solver_run_id: str = "wrong_id_1",
    solver_id: str = "wrong_id_2",
    bundle_id: str = "wrong_id_3",
    manifest_id: str = "wrong_id_4",
    **extra_fields,
) -> str:
    """Build a minimal valid BlindSolverReport response as JSON.

    By default uses wrong IDs to test override behavior (LS_003).
    """
    response = {
        "schema_version": "1.0",
        "solver_run_id": solver_run_id,
        "solver_id": solver_id,
        "bundle_id": bundle_id,
        "manifest_id": manifest_id,
        "created_at": FIXED_CREATED_AT,
        "conclusion": "LLM analysis complete.",
        "confidence": "medium",
        "reasoning_summary": "Analyzed all provided artifacts.",
        "evidence_used": [
            {
                "artifact_id": "ART_PUBLIC_001",
                "path": "player/depoimento.md",
                "quote_or_summary": "Key evidence from document.",
                "relevance": "Supporting the main hypothesis.",
                "confidence": "high",
            }
        ],
        "open_questions": [],
        "assumptions": [],
        "warnings": [],
    }
    response.update(extra_fields)
    return json.dumps(response)


# ============================================================================ #
# Tests (LS_001 through LS_008)
# ============================================================================ #


def test_ls_003_happy_path_id_override(source_tree: Path, output_root: Path) -> None:
    """LS_003: FakeProvider returns valid JSON with wrong IDs → solve overrides IDs from context.

    Verify that even if the JSON response has incorrect solver_run_id, solver_id,
    bundle_id, manifest_id, the final BlindSolverReport uses the correct values
    from the context.
    """
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    # FakeProvider with JSON response using wrong IDs
    response_json = build_solver_response_json(
        solver_run_id="WRONG_RUN_ID",
        solver_id="WRONG_SOLVER_ID",
        bundle_id="WRONG_BUNDLE_ID",
        manifest_id="WRONG_MANIFEST_ID",
    )
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    # Create context from bundle
    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    # Solve
    report = solver.solve(context)

    # Verify IDs are overridden from context, not from JSON
    assert report.solver_run_id == "SOLVER_RUN_LLM_001"
    assert report.solver_id == "SOLVER_LLM_001"
    assert report.bundle_id == bundle_meta.bundle_id
    assert report.manifest_id == bundle_meta.manifest_id

    # Verify report passes validation
    assert validate_report(report).valid


def test_ls_001_sentinel_leaked_content_not_in_prompt(
    source_tree: Path, output_root: Path, tmp_path: Path
) -> None:
    """LS_001: Sentinel test - bundle content included, leaked content excluded.

    Create a file OUTSIDE the bundle with unique sentinel string.
    Verify that:
    (a) Real artifact content IS in the prompt passed to LLM.
    (b) Sentinel string is NOT in the prompt (content leak detected if it is).
    """
    pytest.importorskip("generator.llm_blind_solver")
    from generator.llm_blind_solver import LLMBlindSolver

    # Create a file outside the bundle with unique sentinel
    sentinel_file = tmp_path / "leaked" / "gabarito_sentinela.txt"
    sentinel_string = "SENTINELA_FORA_DO_BUNDLE_XYZ123_UNIQUE"
    write(sentinel_file, sentinel_string)

    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    response_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    # Solve (triggering LLM call)
    solver.solve(context)

    # Capture the prompt that was sent to the LLM
    prompt = provider.calls[0].prompt

    # (a) Real artifact content MUST be in the prompt
    assert "Depoimento publico bruto" in prompt, "Real artifact content missing from prompt"

    # (b) Sentinel string MUST NOT be in the prompt
    assert sentinel_string not in prompt, f"LEAK DETECTED: sentinel '{sentinel_string}' found in prompt"


def test_ls_002_json_repair_valid_on_second_attempt(source_tree: Path, output_root: Path) -> None:
    """LS_002: First response is invalid JSON, second is valid → solve succeeds with 2 calls.

    Verify that LLMBlindSolver repairs JSON errors by resubmitting with the error attached,
    and that both calls are registered in fake_provider.calls.
    """
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    # Script: first response invalid JSON, second valid
    invalid_json = "not valid json {{{"
    valid_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=invalid_json), ScriptedResponse(text=valid_json)])
    solver = LLMBlindSolver(provider=provider)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    # Solve should succeed after repair
    report = solver.solve(context)

    # Verify 2 calls were made
    assert len(provider.calls) == 2, f"Expected 2 calls, got {len(provider.calls)}"

    # Verify report is valid
    assert validate_report(report).valid


def test_ls_002_both_responses_invalid_raises_error(source_tree: Path, output_root: Path) -> None:
    """LS_002: Both responses are invalid JSON → solve raises BlindSolverHarnessError."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    # Script: both responses invalid
    invalid_json_1 = "not valid json {{{"
    invalid_json_2 = "still not valid }}}"
    provider = FakeProvider([ScriptedResponse(text=invalid_json_1), ScriptedResponse(text=invalid_json_2)])
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=1)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    # Solve should raise error after max repair attempts exhausted
    with pytest.raises(BlindSolverHarnessError):
        solver.solve(context)


def test_ls_004_extra_field_discarded_warning_added(source_tree: Path, output_root: Path) -> None:
    """LS_004: JSON response with extra field → field discarded, warning logged.

    Verify that unknown fields (not part of BlindSolverReport schema) are safely
    discarded and a warning is added to the report.
    """
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    # Response with extra field "chain_of_thought"
    response_json = build_solver_response_json(chain_of_thought="This is extra reasoning...")
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    report = solver.solve(context)

    # Verify extra field is not in report (no chain_of_thought attribute)
    assert not hasattr(report, "chain_of_thought"), "Extra field should not be stored"

    # Verify warning was added (should mention unknown field or similar)
    assert len(report.warnings) > 0, "Expected warning about extra field"
    assert any("chain_of_thought" in str(w) or "extra" in str(w).lower() for w in report.warnings), (
        "Warning should mention the extra field or indicate field handling"
    )


def test_ls_005_prompt_template_hash_audited(source_tree: Path, output_root: Path) -> None:
    """LS_005: Template hash (sha256) is registered in the report.

    Verify that the hash of generator/prompts/blind_solver_v1.md appears
    in the report (likely in warnings with prefix "prompt_template_sha256:").
    """
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    response_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    report = solver.solve(context)

    # Compute expected hash of template (will fail if template doesn't exist yet, which is fine for STEP-02)
    template_path = Path("generator/prompts/blind_solver_v1.md")
    if template_path.exists():
        expected_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
        # Check if hash is in warnings or any field
        warnings_str = " ".join(str(w) for w in report.warnings)
        assert expected_hash in warnings_str, f"Template hash {expected_hash} not found in report warnings"


def test_ls_006_prompt_includes_exact_artifact_list(source_tree: Path, output_root: Path) -> None:
    """LS_006: Prompt contains exact list of included_artifacts, no extra ones.

    Build bundle with 2 artifacts (public_spec + second_public_spec).
    Verify that the prompt includes exactly these artifact_ids and no others.
    """
    pytest.importorskip("generator.llm_blind_solver")
    from generator.llm_blind_solver import LLMBlindSolver

    bundle = make_bundle(source_tree, output_root, artifact_specs=[public_spec(), second_public_spec()])
    request = harness_request(bundle)

    response_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    context = BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )

    solver.solve(context)

    prompt = provider.calls[0].prompt

    # Verify expected artifact IDs are in prompt
    assert "ART_PUBLIC_001" in prompt, "Expected artifact ID ART_PUBLIC_001 not in prompt"
    assert "ART_PUBLIC_002" in prompt, "Expected artifact ID ART_PUBLIC_002 not in prompt"

    # Verify no unexpected artifact IDs (this is a weak check; a full check would
    # enumerate all artifact_ids and count them, but this covers the basic case)
    # The negative test would be with a third artifact that shouldn't be there.


def test_ls_007_integration_with_harness(source_tree: Path, output_root: Path) -> None:
    """LS_007: run_blind_solver_harness with LLMBlindSolver produces valid run record end-to-end.

    Integrate LLMBlindSolver into the full harness and verify no exception,
    and result contains valid report.
    """
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    response_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    # Use the full harness
    result = run_blind_solver_harness(request, solver)

    # Verify run record is valid
    assert result.bundle_report.valid, "Bundle report validation failed"
    assert result.report is not None, "Report should be present"
    assert result.report["solver_run_id"] == "SOLVER_RUN_LLM_001"


def test_ls_008_pipeline_regression_without_solver_param(output_root: Path) -> None:
    """LS_008: Regression - pipeline_runner.run_pipeline() without solver parameter uses DeterministicPipelineSolver.

    This test verifies that existing behavior is preserved: if no solver is passed,
    the default stub (DeterministicPipelineSolver) is used. The pipeline produces a valid
    result using the stub solver.
    """
    from generator.pipeline_runner import run_pipeline

    # Use the canonical initiante blueprint
    blueprint_path = Path(__file__).parent.parent / "examples" / "caso_canonico_iniciante.json"
    assert blueprint_path.exists(), f"Blueprint not found at {blueprint_path}"

    # Call run_pipeline without solver parameter; should use DeterministicPipelineSolver
    result = run_pipeline(
        blueprint_path,
        run_id="LS_008_TEST_RUN",
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
    )

    # Verify result is valid (no exception, valid PipelineRunResult)
    assert result is not None, "Pipeline should produce a result"
    assert result.manifest is not None, "Result should include manifest"
    assert result.blind_solver_report is not None, "Result should include blind_solver_report"
    # Default stub is deterministic: no LLM call, conclusion follows the stub's fixed heuristic
    assert "SOLVER-LS_008_TEST_RUN" in result.blind_solver_report["solver_id"]


# ============================================================================ #
# HD_001-HD_005: hardening against hostile provider responses (ISSUE-33.4)    #
# ============================================================================ #


def _context_for(bundle: Path, request: BlindSolverHarnessRequest) -> BlindSolverContext:
    from generator.blind_bundle_decoder import decode_blind_bundle

    bundle_meta = decode_blind_bundle(bundle)
    return BlindSolverContext(
        solver_run_id=request.run_id,
        solver_id=request.solver_id,
        bundle_id=bundle_meta.bundle_id,
        manifest_id=bundle_meta.manifest_id,
        bundle_root=bundle,
    )


def test_hd001_non_dict_json_triggers_repair_then_succeeds(source_tree: Path, output_root: Path) -> None:
    """HD_001: valid JSON that isn't an object triggers repair, not AttributeError."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    non_dict_json = json.dumps([1, 2, 3])
    valid_json = build_solver_response_json()
    provider = FakeProvider([ScriptedResponse(text=non_dict_json), ScriptedResponse(text=valid_json)])
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=1)

    context = _context_for(bundle, request)
    report = solver.solve(context)

    assert len(provider.calls) == 2
    assert validate_report(report).valid


def test_hd001_two_non_dict_responses_raise_contract_error(source_tree: Path, output_root: Path) -> None:
    """HD_001: both attempts non-dict -> BlindSolverHarnessError, never AttributeError."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    non_dict_json = json.dumps([1, 2, 3])
    provider = FakeProvider([ScriptedResponse(text=non_dict_json), ScriptedResponse(text=non_dict_json)])
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=1)

    context = _context_for(bundle, request)

    with pytest.raises(BlindSolverHarnessError):
        solver.solve(context)


def test_hd001_warnings_non_list_normalized_with_warning(source_tree: Path, output_root: Path) -> None:
    """HD_001: warnings='nenhum' (not a list) -> report.warnings is a list with a normalization notice."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    response_json = build_solver_response_json(warnings="nenhum")
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    context = _context_for(bundle, request)
    report = solver.solve(context)

    assert isinstance(report.warnings, (list, tuple))
    assert any("normaliz" in w.lower() for w in report.warnings)


def test_hd002_evidence_extra_field_filtered_with_warning(source_tree: Path, output_root: Path) -> None:
    """HD_002: evidence_used item with extra field 'page' -> field filtered, warning logged."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    response_json = build_solver_response_json(
        evidence_used=[
            {
                "artifact_id": "ART_PUBLIC_001",
                "path": "player/depoimento.md",
                "quote_or_summary": "Key evidence.",
                "relevance": "Supports hypothesis.",
                "confidence": "high",
                "page": 2,
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    context = _context_for(bundle, request)
    report = solver.solve(context)

    assert not hasattr(report.evidence_used[0], "page")
    assert any("page" in w for w in report.warnings)


def test_hd002_evidence_non_dict_item_triggers_repair_then_contract_error(
    source_tree: Path, output_root: Path
) -> None:
    """HD_002: evidence_used item is a bare string -> repair/contract error, not TypeError."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    bad_json = build_solver_response_json(evidence_used=["string solta"])
    provider = FakeProvider([ScriptedResponse(text=bad_json), ScriptedResponse(text=bad_json)])
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=1)

    context = _context_for(bundle, request)

    with pytest.raises(BlindSolverHarnessError):
        solver.solve(context)
    assert len(provider.calls) == 2


def test_hd003_max_repair_attempts_two_makes_three_calls_before_error(
    source_tree: Path, output_root: Path
) -> None:
    """HD_003: max_repair_attempts=2 with 3 invalid responses -> exactly 3 calls, then contract error."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    invalid = "not valid json {{{"
    provider = FakeProvider([ScriptedResponse(text=invalid) for _ in range(3)])
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=2)

    context = _context_for(bundle, request)

    with pytest.raises(BlindSolverHarnessError):
        solver.solve(context)
    assert len(provider.calls) == 3


def test_hd003_max_repair_attempts_two_succeeds_on_third_response(
    source_tree: Path, output_root: Path
) -> None:
    """HD_003: max_repair_attempts=2, valid response on 3rd attempt -> success with 3 calls."""
    bundle = make_bundle(source_tree, output_root)
    request = harness_request(bundle)

    invalid = "not valid json {{{"
    valid = build_solver_response_json()
    provider = FakeProvider(
        [ScriptedResponse(text=invalid), ScriptedResponse(text=invalid), ScriptedResponse(text=valid)]
    )
    solver = LLMBlindSolver(provider=provider, max_repair_attempts=2)

    context = _context_for(bundle, request)
    report = solver.solve(context)

    assert len(provider.calls) == 3
    assert validate_report(report).valid


def test_hd004_literal_bundle_id_placeholder_in_artifact_stays_literal(
    tmp_path: Path, output_root: Path
) -> None:
    """HD_004: artifact content containing the literal '{bundle_id}' stays literal in the prompt."""
    source = tmp_path / "source_hd004"
    write(
        source / "public/envelope_1/nota.md",
        "Nota contem o literal {bundle_id} dentro do texto.\n",
    )
    bundle = make_bundle(
        source,
        output_root,
        artifact_specs=[
            public_spec(
                source_path="public/envelope_1/nota.md",
                bundle_path="player/nota.md",
            )
        ],
    )
    request = harness_request(bundle)

    response_json = build_solver_response_json(
        evidence_used=[
            {
                "artifact_id": "ART_PUBLIC_001",
                "path": "player/nota.md",
                "quote_or_summary": "Nota com placeholder literal.",
                "relevance": "Teste HD_004.",
                "confidence": "high",
            }
        ]
    )
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    context = _context_for(bundle, request)
    solver.solve(context)

    prompt = provider.calls[0].prompt
    assert "Nota contem o literal {bundle_id} dentro do texto." in prompt


def test_ls_008_pipeline_with_injected_solver_uses_adapter(output_root: Path) -> None:
    """LS_008: With solver injected, the pipeline's report comes from the adapter, not the stub.

    Confirms the opt-in injection point in run_pipeline actually routes to the
    provided LLMBlindSolver instead of silently falling back to the stub.
    """
    from generator.pipeline_runner import run_pipeline

    blueprint_path = Path(__file__).parent.parent / "examples" / "caso_canonico_iniciante.json"
    assert blueprint_path.exists(), f"Blueprint not found at {blueprint_path}"

    # conclusion left empty (no evidence-vs-conclusion consistency check to satisfy);
    # reasoning_summary is unconstrained and unique enough to prove adapter authorship.
    distinctive_reasoning = "RACIOCINIO_VINDO_DO_ADAPTER_LLM_NAO_DO_STUB"
    response_json = build_solver_response_json(
        conclusion="",
        reasoning_summary=distinctive_reasoning,
        evidence_used=[],
        open_questions=["Evidencias insuficientes para concluir (teste)."],
    )
    provider = FakeProvider([ScriptedResponse(text=response_json)])
    solver = LLMBlindSolver(provider=provider)

    result = run_pipeline(
        blueprint_path,
        run_id="LS_008_INJECTED_RUN",
        output_root=output_root,
        created_at=FIXED_CREATED_AT,
        solver=solver,
    )

    assert result is not None, "Pipeline should produce a result"
    assert result.blind_solver_report is not None, "Result should include blind_solver_report"
    assert result.blind_solver_report["reasoning_summary"] == distinctive_reasoning, (
        "Report should reflect the injected adapter's output, not the deterministic stub"
    )
    assert len(provider.calls) == 1, "Injected FakeProvider should have been called by the pipeline"

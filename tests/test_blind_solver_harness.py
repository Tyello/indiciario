from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    build_blind_bundle,
)
from generator.blind_solver_harness import (
    BlindSolverContext,
    BlindSolverEvidence,
    BlindSolverHarnessError,
    BlindSolverHarnessRequest,
    BlindSolverReport,
    report_to_dict,
    run_blind_solver_harness,
)

FIXED_CREATED_AT = "2026-06-14T00:00:00Z"


# --------------------------------------------------------------------------- #
# Bundle building helpers (reuse the real generator to produce valid bundles)  #
# --------------------------------------------------------------------------- #
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
        solver_id="SOLVER_STUB_001",
        run_id="SOLVER_RUN_001",
        created_by="HUMAN_OPERATOR_001",
        created_at=FIXED_CREATED_AT,
    )
    data.update(overrides)
    return BlindSolverHarnessRequest(**data)


# --------------------------------------------------------------------------- #
# Deterministic stub blind solver (test-only fake; no LLM, no network)         #
# --------------------------------------------------------------------------- #
class DeterministicStubBlindSolver:
    """A fake blind solver that reads the first declared artifact only."""

    def __init__(self, created_at: str = FIXED_CREATED_AT) -> None:
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


class PathReadingStubSolver(DeterministicStubBlindSolver):
    """Reads the first artifact by path instead of artifact_id."""

    def solve(self, context: BlindSolverContext) -> BlindSolverReport:
        first = context.list_artifacts()[0]
        text = context.read_artifact_path(first.path)
        report = super().solve(context)
        return replace(report, conclusion=f"Read by path with {len(text)} chars.")


class AccessAttemptSolver:
    """Attempts an access described by callable; used for negative tests."""

    def __init__(self, attempt) -> None:
        self.attempt = attempt

    def solve(self, context: BlindSolverContext) -> BlindSolverReport:
        self.attempt(context)
        base = DeterministicStubBlindSolver().solve(context)
        return base


class ReportMutatingSolver(DeterministicStubBlindSolver):
    """Produces a base report then applies a mutation for negative tests."""

    def __init__(self, mutate, created_at: str = FIXED_CREATED_AT) -> None:
        super().__init__(created_at)
        self.mutate = mutate

    def solve(self, context: BlindSolverContext):
        report = super().solve(context)
        return self.mutate(report)


# --------------------------------------------------------------------------- #
# Tests                                                                         #
# --------------------------------------------------------------------------- #
def test_harness_runs_with_valid_bundle_and_stub_solver(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    result = run_blind_solver_harness(harness_request(bundle), DeterministicStubBlindSolver())

    assert result.bundle_report.valid
    assert result.report["solver_run_id"] == "SOLVER_RUN_001"
    assert result.report["bundle_id"] == "BUNDLE_TEST_001"
    assert result.report["manifest_id"] == "MANIFEST_TEST_001"
    assert result.report["confidence"] == "low"
    assert result.report["evidence_used"][0]["artifact_id"] == "ART_PUBLIC_001"


def test_invalid_leak_check_blocks_execution(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    # Corrupt a declared artifact so the structural leak checker fails on hash mismatch.
    (bundle / "player/depoimento.md").write_text("conteudo adulterado\n", encoding="utf-8")

    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), DeterministicStubBlindSolver())


def test_context_lists_only_included_artifacts(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root, artifact_specs=[public_spec(), second_public_spec()])

    captured: dict[str, object] = {}

    class CapturingSolver(DeterministicStubBlindSolver):
        def solve(self, context: BlindSolverContext) -> BlindSolverReport:
            captured["paths"] = [art.path for art in context.list_artifacts()]
            return super().solve(context)

    run_blind_solver_harness(harness_request(bundle), CapturingSolver())
    assert captured["paths"] == ["player/depoimento.md", "player/recibo.md"]


def test_solver_can_read_artifact_by_id(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    result = run_blind_solver_harness(harness_request(bundle), DeterministicStubBlindSolver())
    assert "ART_PUBLIC_001" in result.accessed_artifacts


def test_solver_can_read_artifact_by_path(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    result = run_blind_solver_harness(harness_request(bundle), PathReadingStubSolver())
    assert "ART_PUBLIC_001" in result.accessed_artifacts
    assert result.report["conclusion"].startswith("Read by path")


def test_solver_cannot_read_undeclared_file_by_path(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = AccessAttemptSolver(lambda ctx: ctx.read_artifact_path("player/recibo.md"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_solver_cannot_read_excluded_artifact(source_tree: Path, output_root: Path) -> None:
    # Include a solution spec; the generator excludes it for blind_solver.
    solution = public_spec(
        artifact_id="ART_SOLUTION_001",
        source_path="private/solution.md",
        bundle_path="private/solution.md",
        artifact_type="solution",
        visibility="private_author",
        contains_solution=True,
        contains_private_author_notes=True,
    )
    bundle = make_bundle(source_tree, output_root, artifact_specs=[public_spec(), solution])

    solver = AccessAttemptSolver(lambda ctx: ctx.read_artifact_path("private/solution.md"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


@pytest.mark.parametrize("bad_path", ["../../etc/passwd", "/etc/passwd", "../escape.md"])
def test_solver_cannot_path_traverse(source_tree: Path, output_root: Path, bad_path: str) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = AccessAttemptSolver(lambda ctx, p=bad_path: ctx.read_artifact_path(p))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_context_does_not_expose_raw_bundle_path(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)

    leaked: dict[str, object] = {}

    class IntrospectingSolver(DeterministicStubBlindSolver):
        def solve(self, context: BlindSolverContext) -> BlindSolverReport:
            descriptor = context.list_artifacts()[0]
            leaked["descriptor_has_path_obj"] = any(
                isinstance(value, Path) for value in vars(descriptor).values()
            )
            leaked["context_public_paths"] = [
                name for name in dir(context) if not name.startswith("_") and isinstance(getattr(context, name, None), Path)
            ]
            return super().solve(context)

    run_blind_solver_harness(harness_request(bundle), IntrospectingSolver())
    assert leaked["descriptor_has_path_obj"] is False
    assert leaked["context_public_paths"] == []


def test_denied_access_raises_clear_error(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = AccessAttemptSolver(lambda ctx: ctx.read_artifact_text("ART_DOES_NOT_EXIST"))
    with pytest.raises(BlindSolverHarnessError, match="not declared|denied|allowed"):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_report_without_evidence_fails_when_conclusion_present(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, evidence_used=()))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_evidence_with_unknown_artifact_id_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)

    def mutate(report: BlindSolverReport) -> BlindSolverReport:
        bad = replace(report.evidence_used[0], artifact_id="ART_UNKNOWN_999")
        return replace(report, evidence_used=(bad,))

    solver = ReportMutatingSolver(mutate)
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_evidence_with_divergent_path_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)

    def mutate(report: BlindSolverReport) -> BlindSolverReport:
        bad = replace(report.evidence_used[0], path="player/recibo.md")
        return replace(report, evidence_used=(bad,))

    solver = ReportMutatingSolver(mutate)
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_report_bundle_id_mismatch_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, bundle_id="BUNDLE_OTHER_999"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_report_manifest_id_mismatch_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, manifest_id="MANIFEST_OTHER_999"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_report_solver_run_id_mismatch_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, solver_run_id="SOLVER_RUN_OTHER"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_invalid_confidence_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, confidence="certain"))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_empty_reasoning_summary_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    solver = ReportMutatingSolver(lambda report: replace(report, reasoning_summary=""))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)


def test_prohibited_extra_field_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)

    class RawDictSolver(DeterministicStubBlindSolver):
        def solve(self, context: BlindSolverContext):
            report = report_to_dict(super().solve(context))
            report["chain_of_thought"] = "raw private reasoning that must not exist"
            return report

    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), RawDictSolver())


def test_raw_prompt_extra_field_fails(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)

    class RawDictSolver(DeterministicStubBlindSolver):
        def solve(self, context: BlindSolverContext):
            report = report_to_dict(super().solve(context))
            report["raw_prompt"] = "system prompt leak"
            return report

    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), RawDictSolver())


def test_max_artifacts_blocks_large_bundle(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root, artifact_specs=[public_spec(), second_public_spec()])
    with pytest.raises(BlindSolverHarnessError, match="max_artifacts"):
        run_blind_solver_harness(harness_request(bundle, max_artifacts=1), DeterministicStubBlindSolver())


def test_max_bytes_per_artifact_blocks_large_artifact(source_tree: Path, output_root: Path) -> None:
    big = "x" * 5000 + "\n"
    write(source_tree / "public/envelope_1/depoimento.md", big)
    bundle = make_bundle(source_tree, output_root)
    with pytest.raises(BlindSolverHarnessError, match="max_bytes_per_artifact"):
        run_blind_solver_harness(harness_request(bundle, max_bytes_per_artifact=100), DeterministicStubBlindSolver())


def test_invalid_utf8_artifact_raises_clear_error(source_tree: Path, output_root: Path) -> None:
    write_bytes(source_tree / "public/envelope_1/depoimento.md", b"\xff\xfe\x00binary not utf8")
    bundle = make_bundle(source_tree, output_root)
    with pytest.raises(BlindSolverHarnessError, match="UTF-8|decode|utf-8"):
        run_blind_solver_harness(harness_request(bundle), DeterministicStubBlindSolver())


def test_deterministic_stub_is_reproducible(source_tree: Path, output_root: Path, tmp_path: Path) -> None:
    second_root = tmp_path / "bundles2"
    second_root.mkdir()
    bundle_a = make_bundle(source_tree, output_root)
    bundle_b = make_bundle(source_tree, second_root)

    result_a = run_blind_solver_harness(harness_request(bundle_a), DeterministicStubBlindSolver())
    result_b = run_blind_solver_harness(harness_request(bundle_b), DeterministicStubBlindSolver())
    assert result_a.report == result_b.report


def test_harness_does_not_modify_bundle(source_tree: Path, output_root: Path) -> None:
    bundle = make_bundle(source_tree, output_root)
    before = {p.relative_to(bundle).as_posix(): p.read_bytes() for p in bundle.rglob("*") if p.is_file()}
    run_blind_solver_harness(harness_request(bundle), DeterministicStubBlindSolver())
    after = {p.relative_to(bundle).as_posix(): p.read_bytes() for p in bundle.rglob("*") if p.is_file()}
    assert before == after


def test_harness_only_reads_inside_the_bundle(source_tree: Path, output_root: Path, tmp_path: Path) -> None:
    # A file outside the bundle must remain unreadable through the context.
    outside = write(tmp_path / "outside_secret.md", "segredo fora do bundle\n")
    bundle = make_bundle(source_tree, output_root)

    solver = AccessAttemptSolver(lambda ctx: ctx.read_artifact_path(str(outside)))
    with pytest.raises(BlindSolverHarnessError):
        run_blind_solver_harness(harness_request(bundle), solver)

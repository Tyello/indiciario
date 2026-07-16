"""Tests for the solvability_cli (ISSUE-33.8, STEP-02 RED).

Cases cover:
- CC_006: end-to-end CLI run with fakes injected via build_provider monkeypatch
  -> exit 0, report written to --out valid against schema, summary printed to stdout.
- CC_007: --out inside the bundle -> error + exit code != 0; bundle stays byte-identical.
- CC_008: --expected pointing at a full blueprint fixture -> aborts with error code != 0.
- Invariant: no test imports subprocess.

This module will fail at import (generator.solvability_cli does not exist yet).
That is expected RED behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

import generator.solvability_cli as solvability_cli
from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    build_blind_bundle,
)
from generator.fake_provider import FakeProvider, ScriptedResponse

FIXED_CREATED_AT = "2026-06-14T00:00:00Z"


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
        manifest_id="MANIFEST_CLI_001",
        run_id="RUN_CLI_001",
        bundle_id="BUNDLE_CLI_001",
        case_id="CASE_CLI_001",
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
        created_at=FIXED_CREATED_AT,
    )
    data.update(overrides)
    return BlindBundleBuildRequest(**data)


def make_bundle(source_tree: Path, output_root: Path, **overrides: object) -> Path:
    return build_blind_bundle(build_request(source_tree, output_root, **overrides)).output_path


def solver_response_json(**extra_fields: object) -> str:
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


def judge_response_json(met: bool = True, **extra_fields: object) -> str:
    response = {
        "verdict_id": "VERDICT_ANY",
        "report_run_id": "ANY",
        "prompt_hash": "abc123def456",
        "conclusions": [
            {
                "id": "culpado",
                "met": met,
                "evidence_cited": ["ART_PUBLIC_001"] if met else [],
                "rationale": "Racional do julgamento.",
            }
        ],
        "alternative_solution_detected": False,
        "alternative_solution_summary": None,
    }
    response.update(extra_fields)
    return json.dumps(response)


def run_pair(met: bool = True) -> list[ScriptedResponse]:
    return [
        ScriptedResponse(text=solver_response_json()),
        ScriptedResponse(text=judge_response_json(met=met)),
    ]


def write_expected_file(path: Path) -> Path:
    data = [{"id": "culpado", "statement": "O culpado e quem aparece no depoimento.", "required": True}]
    write(path, json.dumps(data))
    return path


def bundle_hash(bundle_path: Path) -> str:
    """Compute SHA256 hash of all files in bundle."""
    digest = hashlib.sha256()
    for file_path in sorted(bundle_path.rglob("*")):
        if file_path.is_file():
            digest.update(str(file_path.relative_to(bundle_path)).encode("utf-8"))
            digest.update(file_path.read_bytes())
    return digest.hexdigest()


def _load_schema() -> dict[str, Any]:
    schema_path = Path("schemas/solvability_report.schema.yaml")
    return yaml.safe_load(schema_path.read_text(encoding="utf-8"))


# ============================================================================ #
# CC_006: end-to-end with fakes                                              #
# ============================================================================ #


def test_cc006_end_to_end_with_fakes(
    source_tree: Path, output_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """CC_006: CLI end-to-end, all args accepted, report written, summary printed."""
    bundle = make_bundle(source_tree, output_root)
    expected_path = write_expected_file(tmp_path / "expected.json")
    out_path = tmp_path / "reports" / "report.json"

    script: list[ScriptedResponse] = []
    for _ in range(3):
        script.extend(run_pair(met=True))
    shared_provider = FakeProvider(script)

    monkeypatch.setattr(solvability_cli, "build_provider", lambda model_id: shared_provider)

    exit_code = solvability_cli.run(
        [
            "--bundle", str(bundle),
            "--expected", str(expected_path),
            "--runs", "3",
            "--temperature", "0.7",
            "--solver-model", "claude-sonnet-5",
            "--judge-model", "claude-sonnet-5",
            "--out", str(out_path),
        ]
    )

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    assert out_path.exists(), f"Report not written to {out_path}"

    report_dict = json.loads(out_path.read_text(encoding="utf-8"))
    Draft202012Validator(_load_schema()).validate(report_dict)
    assert report_dict["solve_rate"] == 1.0
    assert report_dict["difficulty_estimate"] == "facil"

    captured = capsys.readouterr()
    assert "solve_rate" in captured.out or "difficulty_estimate" in captured.out


def test_cc006_temperature_arg_accepted_no_crash(
    source_tree: Path, output_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI accepts --temperature but does not crash (may warn but continues)."""
    bundle = make_bundle(source_tree, output_root)
    expected_path = write_expected_file(tmp_path / "expected.json")
    out_path = tmp_path / "report.json"

    shared_provider = FakeProvider(run_pair(met=True))
    monkeypatch.setattr(solvability_cli, "build_provider", lambda model_id: shared_provider)

    exit_code = solvability_cli.run(
        [
            "--bundle", str(bundle),
            "--expected", str(expected_path),
            "--runs", "1",
            "--temperature", "0.5",
            "--solver-model", "claude-sonnet-5",
            "--judge-model", "claude-sonnet-5",
            "--out", str(out_path),
        ]
    )

    assert exit_code == 0


# ============================================================================ #
# CC_007: --out inside bundle -> error, bundle immutable                     #
# ============================================================================ #


def test_cc007_out_inside_bundle_rejected(
    source_tree: Path, output_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CC_007: --out pointing inside bundle -> exit != 0, bundle hash unchanged."""
    bundle = make_bundle(source_tree, output_root)
    expected_path = write_expected_file(tmp_path / "expected.json")
    out_path_inside_bundle = bundle / "report.json"

    hash_before = bundle_hash(bundle)

    shared_provider = FakeProvider([])
    monkeypatch.setattr(solvability_cli, "build_provider", lambda model_id: shared_provider)

    exit_code = solvability_cli.run(
        [
            "--bundle", str(bundle),
            "--expected", str(expected_path),
            "--solver-model", "claude-sonnet-5",
            "--judge-model", "claude-sonnet-5",
            "--out", str(out_path_inside_bundle),
        ]
    )

    assert exit_code != 0, f"Expected exit code != 0 when --out inside bundle, got {exit_code}"
    assert not out_path_inside_bundle.exists()
    assert bundle_hash(bundle) == hash_before, "Bundle was modified despite error"


# ============================================================================ #
# CC_008: --expected pointing to full blueprint aborts                        #
# ============================================================================ #


def test_cc008_expected_pointing_to_blueprint_aborts(
    source_tree: Path, output_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """CC_008: --expected with blueprint-like keys -> exit != 0, error message references CC_008."""
    bundle = make_bundle(source_tree, output_root)
    blueprint_like = tmp_path / "blueprint.json"
    write(
        blueprint_like,
        json.dumps(
            {
                "titulo": "Caso Fixture",
                "documentos": [],
                "personagens": [],
                "verdade_real": "O culpado e Alice.",
            }
        ),
    )
    out_path = tmp_path / "report.json"

    shared_provider = FakeProvider([])
    monkeypatch.setattr(solvability_cli, "build_provider", lambda model_id: shared_provider)

    exit_code = solvability_cli.run(
        [
            "--bundle", str(bundle),
            "--expected", str(blueprint_like),
            "--solver-model", "claude-sonnet-5",
            "--judge-model", "claude-sonnet-5",
            "--out", str(out_path),
        ]
    )

    assert exit_code != 0, f"Expected exit code != 0 when --expected is blueprint, got {exit_code}"
    assert not out_path.exists()
    captured = capsys.readouterr()
    error_output = captured.err + captured.out
    assert "CC_008" in error_output, f"Error message should reference CC_008, got: {error_output}"


def test_cc008_expected_with_blueprint_indicators(
    tmp_path: Path,
) -> None:
    """CC_008: detect blueprint by presence of key blueprint fields."""
    blueprint_like = tmp_path / "blueprint.json"
    write(
        blueprint_like,
        json.dumps(
            {
                "titulo": "Caso",
                "documentos": [],
                "personagens": [],
            }
        ),
    )

    # This test just verifies the structure exists for the CLI to detect
    data = json.loads(blueprint_like.read_text(encoding="utf-8"))
    assert "titulo" in data
    assert "documentos" in data
    assert "personagens" in data

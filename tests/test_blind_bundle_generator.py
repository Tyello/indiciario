from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.artifact_visibility_policy import evaluate_manifest_visibility
from generator.blind_bundle_generator import (
    ArtifactSpec,
    BlindBundleBuildRequest,
    BlindBundleBuildError,
    build_blind_bundle,
)


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento público\n")
    write(source / "private/solution.md", "Solução privada\n")
    write(source / "facilitator/guide.md", "Guia do facilitador\n")
    write(source / "review/report.md", "Relatório privado\n")
    write(source / "public/extra.md", "Arquivo extra não listado\n")
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
        included_reason="Documento público de jogador listado explicitamente para o bundle cego.",
        contains_solution=False,
        contains_future_envelopes=False,
        contains_private_author_notes=False,
        contains_other_agents_outputs=False,
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def solution_spec(**overrides: object) -> ArtifactSpec:
    data = dict(
        artifact_id="ART_SOLUTION_001",
        source_path="private/solution.md",
        bundle_path="private/solution.md",
        artifact_type="solution",
        visibility="private_author",
        envelope_scope="none",
        source_role="author",
        included_reason="Solução privada solicitada para testar negação de política.",
        contains_solution=True,
        contains_future_envelopes=False,
        contains_private_author_notes=True,
        contains_other_agents_outputs=False,
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def request(source_tree: Path, output_root: Path, **overrides: object) -> BlindBundleBuildRequest:
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


def load_manifest(bundle: Path) -> dict:
    return yaml.safe_load((bundle / "blind_bundle_manifest.yaml").read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> None:
    schema = yaml.safe_load(Path("schemas/blind_bundle_manifest.schema.yaml").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)


def test_builds_minimal_blind_solver_bundle_with_valid_manifest_hash_and_copy(
    source_tree: Path, output_root: Path
) -> None:
    result = build_blind_bundle(request(source_tree, output_root))

    bundle = output_root / "BUNDLE_TEST_001"
    copied = bundle / "player/depoimento.md"
    manifest_path = bundle / "blind_bundle_manifest.yaml"
    assert copied.read_text(encoding="utf-8") == "Depoimento público\n"
    assert manifest_path.exists()
    expected_hash = hashlib.sha256(copied.read_bytes()).hexdigest()

    manifest = load_manifest(bundle)
    validate_manifest(manifest)
    assert result.output_path == bundle
    assert result.included_count == 1
    assert result.excluded_count == 0
    assert result.copied_files == [Path("player/depoimento.md")]
    assert manifest["included_artifacts"] == [
        {
            "artifact_id": "ART_PUBLIC_001",
            "path": "player/depoimento.md",
            "artifact_type": "player_document",
            "visibility": "public_player",
            "envelope_scope": "current_envelope",
            "hash": expected_hash,
            "hash_algorithm": "sha256",
            "source_role": "author",
            "included_reason": "Documento público de jogador listado explicitamente para o bundle cego.",
        }
    ]
    assert manifest["transformations"][0]["type"] == "copy"
    assert manifest["transformations"][0]["hash_before"] == expected_hash
    assert manifest["transformations"][0]["hash_after"] == expected_hash
    assert manifest["integrity"] == {
        "hash_algorithm": "sha256",
        "artifact_count": 1,
        "included_count": 1,
        "excluded_count": 0,
        "transformation_count": 1,
    }
    assert manifest["isolation_check"]["status"] == "passed"
    assert evaluate_manifest_visibility(manifest).allowed


def test_denied_solution_is_excluded_not_copied_and_marks_isolation_failed(
    source_tree: Path, output_root: Path
) -> None:
    result = build_blind_bundle(
        request(source_tree, output_root, artifact_specs=[public_spec(), solution_spec()])
    )

    bundle = output_root / "BUNDLE_TEST_001"
    manifest = load_manifest(bundle)
    validate_manifest(manifest)
    assert result.included_count == 1
    assert result.excluded_count == 1
    assert not (bundle / "private/solution.md").exists()
    assert manifest["excluded_artifacts"] == [
        {
            "path": "private/solution.md",
            "artifact_type": "solution",
            "visibility": "private_author",
            "exclusion_reason": "Blind solver artifacts cannot include solution, future envelope, private note, or other-agent-output flags.",
            "exclusion_category": "solution_leak",
        }
    ]
    assert manifest["isolation_check"]["status"] == "failed"
    assert manifest["isolation_check"]["issues"][0]["affected_artifact_ids"] == ["ART_SOLUTION_001"]


def test_policy_warning_is_copied_and_marks_passed_with_warnings(
    source_tree: Path, output_root: Path
) -> None:
    spec = public_spec(
        artifact_id="ART_PRIVATE_WARN",
        source_path="private/solution.md",
        bundle_path="operator/solution.md",
        artifact_type="solution",
        visibility="private_author",
        contains_solution=True,
        contains_private_author_notes=True,
    )
    result = build_blind_bundle(
        request(
            source_tree,
            output_root,
            role="human_operator",
            stage="preflight_review",
            artifact_specs=[spec],
        )
    )
    manifest = result.manifest
    validate_manifest(manifest)
    assert (result.output_path / "operator/solution.md").exists()
    assert manifest["isolation_check"]["status"] == "passed_with_warnings"
    assert manifest["isolation_check"]["warnings"][0]["affected_artifact_ids"] == ["ART_PRIVATE_WARN"]


def test_neutralize_paths_uses_deterministic_safe_names_and_preserves_extension(
    source_tree: Path, output_root: Path
) -> None:
    spec = public_spec(bundle_path="revealing/suspect-name.md")
    result = build_blind_bundle(request(source_tree, output_root, artifact_specs=[spec], neutralize_paths=True))

    assert result.copied_files == [Path("artifacts/ARTIFACT-001.md")]
    assert (result.output_path / "artifacts/ARTIFACT-001.md").exists()
    assert not (result.output_path / "revealing/suspect-name.md").exists()
    transformation = result.manifest["transformations"][0]
    assert transformation["type"] == "normalize_filename"
    assert transformation["target_path"] == "bundle/artifacts/ARTIFACT-001.md"


@pytest.mark.parametrize(
    "bad_spec",
    [
        public_spec(source_path="/absolute.md"),
        public_spec(source_path="../outside.md"),
        public_spec(bundle_path="../escape.md"),
        public_spec(bundle_path=""),
        public_spec(source_path="public\\envelope_1\\depoimento.md"),
    ],
)
def test_unsafe_paths_fail_without_publishing_partial_bundle(
    source_tree: Path, output_root: Path, bad_spec: ArtifactSpec
) -> None:
    with pytest.raises(BlindBundleBuildError):
        build_blind_bundle(request(source_tree, output_root, artifact_specs=[bad_spec]))
    assert not (output_root / "BUNDLE_TEST_001").exists()
    assert not list(output_root.glob(".BUNDLE_TEST_001.tmp-*"))


def test_symlink_source_is_rejected_and_not_followed(source_tree: Path, output_root: Path) -> None:
    target = source_tree / "public/envelope_1/depoimento.md"
    link = source_tree / "public/link.md"
    link.symlink_to(target)

    with pytest.raises(BlindBundleBuildError):
        build_blind_bundle(request(source_tree, output_root, artifact_specs=[public_spec(source_path="public/link.md")]))
    assert not (output_root / "BUNDLE_TEST_001").exists()


def test_existing_output_requires_overwrite_and_overwrite_only_replaces_bundle_dir(
    source_tree: Path, output_root: Path
) -> None:
    existing = output_root / "BUNDLE_TEST_001"
    write(existing / "old.txt", "old")
    sibling = write(output_root / "KEEP_ME/sibling.txt", "keep")

    with pytest.raises(BlindBundleBuildError):
        build_blind_bundle(request(source_tree, output_root))
    assert (existing / "old.txt").exists()

    result = build_blind_bundle(request(source_tree, output_root, overwrite=True))
    assert not (result.output_path / "old.txt").exists()
    assert sibling.read_text(encoding="utf-8") == "keep"
    assert (result.output_path / "blind_bundle_manifest.yaml").exists()


def test_schema_validation_failure_cleans_tmp_and_does_not_publish(
    monkeypatch: pytest.MonkeyPatch, source_tree: Path, output_root: Path
) -> None:
    import generator.blind_bundle_generator as module

    def fail_schema(_manifest: dict) -> None:
        raise BlindBundleBuildError("schema failure")

    monkeypatch.setattr(module, "_validate_manifest_schema", fail_schema)
    with pytest.raises(BlindBundleBuildError, match="schema failure"):
        build_blind_bundle(request(source_tree, output_root))
    assert not (output_root / "BUNDLE_TEST_001").exists()
    assert not list(output_root.glob(".BUNDLE_TEST_001.tmp-*"))


def test_empty_request_and_unknown_role_fail_without_bundle(source_tree: Path, output_root: Path) -> None:
    with pytest.raises(BlindBundleBuildError):
        build_blind_bundle(request(source_tree, output_root, artifact_specs=[]))
    with pytest.raises(BlindBundleBuildError):
        build_blind_bundle(request(source_tree, output_root, role="unknown_role"))
    assert not (output_root / "BUNDLE_TEST_001").exists()


def test_build_is_deterministic_does_not_change_sources_and_reads_only_listed_files(
    source_tree: Path, tmp_path: Path
) -> None:
    first_output = tmp_path / "out1"
    second_output = tmp_path / "out2"
    first_output.mkdir()
    second_output.mkdir()
    before = (source_tree / "public/envelope_1/depoimento.md").read_bytes()

    req1 = request(source_tree, first_output)
    req2 = replace(req1, output_root=second_output)
    result1 = build_blind_bundle(req1)
    result2 = build_blind_bundle(req2)

    assert (source_tree / "public/envelope_1/depoimento.md").read_bytes() == before
    assert not (result1.output_path / "public/extra.md").exists()
    assert result1.manifest == result2.manifest
    assert result1.copied_files == result2.copied_files


def test_manifest_policy_denial_cleans_tmp_and_does_not_publish(
    monkeypatch: pytest.MonkeyPatch, source_tree: Path, output_root: Path
) -> None:
    import generator.blind_bundle_generator as module
    from generator.artifact_visibility_policy import PolicyDecision, PolicyReport

    def deny_manifest(_manifest: dict) -> PolicyReport:
        return PolicyReport(
            decisions=(
                PolicyDecision(
                    allowed=False,
                    severity="deny",
                    rule_id="VIS_DENY_TEST_MANIFEST",
                    reason="Manifest policy denial injected by regression test.",
                    recommended_action="Do not publish the bundle.",
                    matched_conditions=["test=true"],
                ),
            )
        )

    monkeypatch.setattr(module, "evaluate_manifest_visibility", deny_manifest)
    with pytest.raises(BlindBundleBuildError, match="generated manifest is denied"):
        build_blind_bundle(request(source_tree, output_root))
    assert not (output_root / "BUNDLE_TEST_001").exists()
    assert not list(output_root.glob(".BUNDLE_TEST_001.tmp-*"))

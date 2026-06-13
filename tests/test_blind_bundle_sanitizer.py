from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.blind_bundle_generator import ArtifactSpec, BlindBundleBuildRequest, build_blind_bundle
from generator.blind_bundle_leak_checker import check_blind_bundle
from generator.blind_bundle_sanitizer import (
    BlindBundleSanitizeError,
    BlindBundleSanitizeRequest,
    sanitize_blind_bundle,
)


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento público com palavra solução apenas como conteúdo bruto\n")
    write(source / "private/solution.md", "Solução privada que não pode ir ao blind_solver\n")
    write(source / "future/envelope_3.md", "Envelope futuro privado\n")
    write(source / "review/report.md", "Relatório de revisão\n")
    return source


@pytest.fixture
def source_output(tmp_path: Path) -> Path:
    root = tmp_path / "source_bundles"
    root.mkdir()
    return root


@pytest.fixture
def sanitized_output(tmp_path: Path) -> Path:
    root = tmp_path / "sanitized_bundles"
    root.mkdir()
    return root


def public_spec(**overrides: object) -> ArtifactSpec:
    data = dict(
        artifact_id="ART_PUBLIC_001",
        source_path="public/envelope_1/depoimento.md",
        bundle_path="revealing/depoimento-mirante.md",
        artifact_type="player_document",
        visibility="public_player",
        envelope_scope="current_envelope",
        source_role="author",
        included_reason="Documento público de jogador listado explicitamente para o bundle.",
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
        bundle_path="private/answer-key.md",
        artifact_type="solution",
        visibility="private_author",
        envelope_scope="none",
        source_role="author",
        included_reason="Solução privada incluída em bundle operacional para testar sanitização estrutural.",
        contains_solution=True,
        contains_future_envelopes=False,
        contains_private_author_notes=True,
        contains_other_agents_outputs=False,
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def review_warn_spec(**overrides: object) -> ArtifactSpec:
    data = dict(
        artifact_id="ART_REVIEW_001",
        source_path="review/report.md",
        bundle_path="review/report.md",
        artifact_type="review_report",
        visibility="review_private",
        envelope_scope="none",
        source_role="narrative_reviewer",
        included_reason="Relatório privado permitido com warning para operador humano.",
        contains_solution=False,
        contains_future_envelopes=False,
        contains_private_author_notes=False,
        contains_other_agents_outputs=True,
    )
    data.update(overrides)
    return ArtifactSpec(**data)


def build_request(source_tree: Path, source_output: Path, **overrides: object) -> BlindBundleBuildRequest:
    data = dict(
        manifest_id="MANIFEST_SOURCE_001",
        run_id="RUN_SOURCE_001",
        bundle_id="BUNDLE_SOURCE_001",
        case_id="CASE_TEST_001",
        case_version="V1",
        role="human_operator",
        stage="preflight_review",
        source_root=source_tree,
        output_root=source_output,
        created_by="HUMAN_OPERATOR_001",
        artifact_specs=[public_spec(), solution_spec(), review_warn_spec()],
        generation_mode="manual",
        offline_safe=True,
        neutralize_paths=False,
        overwrite=False,
        created_at="2026-06-13T00:00:00Z",
    )
    data.update(overrides)
    return BlindBundleBuildRequest(**data)


def sanitize_request(source_bundle: Path, sanitized_output: Path, **overrides: object) -> BlindBundleSanitizeRequest:
    data = dict(
        source_bundle_path=source_bundle,
        output_root=sanitized_output,
        sanitized_bundle_id="BUNDLE_SANITIZED_001",
        created_by="HUMAN_OPERATOR_001",
        role="blind_solver",
        stage="blind_solve",
        neutralize_paths=False,
        overwrite=False,
        allowed_transformations=("copy", "normalize_filename", "exclude_artifact"),
        created_at="2026-06-13T00:00:00Z",
    )
    data.update(overrides)
    return BlindBundleSanitizeRequest(**data)


def load_manifest(bundle: Path) -> dict:
    return yaml.safe_load((bundle / "blind_bundle_manifest.yaml").read_text(encoding="utf-8"))


def save_manifest(bundle: Path, manifest: dict) -> None:
    (bundle / "blind_bundle_manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")


def validate_manifest(manifest: dict) -> None:
    schema = yaml.safe_load(Path("schemas/blind_bundle_manifest.schema.yaml").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest), key=str)
    assert errors == []


def snapshot_tree(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_sanitizes_valid_bundle_non_destructively_with_schema_and_final_leak_check(
    source_tree: Path, source_output: Path, sanitized_output: Path
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path
    before = snapshot_tree(source_bundle)

    result = sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output))

    assert result.output_path == sanitized_output / "BUNDLE_SANITIZED_001"
    assert snapshot_tree(source_bundle) == before
    assert result.copied_count == 1
    assert result.excluded_count == 0
    manifest = load_manifest(result.output_path)
    validate_manifest(manifest)
    assert check_blind_bundle(result.output_path).valid
    assert result.leak_check_report.valid
    copied_path = result.output_path / manifest["included_artifacts"][0]["path"]
    assert copied_path.read_bytes() == (source_bundle / "revealing/depoimento-mirante.md").read_bytes()
    assert manifest["transformations"][0]["type"] == "copy"


def test_neutralize_paths_is_deterministic_preserves_extension_and_hashes(source_tree: Path, source_output: Path, sanitized_output: Path) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path

    result = sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output, neutralize_paths=True))

    manifest = result.manifest
    included = manifest["included_artifacts"][0]
    transformation = manifest["transformations"][0]
    assert included["path"] == "artifacts/ARTIFACT-001.md"
    assert transformation["type"] == "normalize_filename"
    assert transformation["target_path"] == "bundle/artifacts/ARTIFACT-001.md"
    source_hash = hashlib.sha256((source_bundle / "revealing/depoimento-mirante.md").read_bytes()).hexdigest()
    target_hash = hashlib.sha256((result.output_path / included["path"]).read_bytes()).hexdigest()
    assert included["hash"] == target_hash
    assert transformation["hash_before"] == source_hash
    assert transformation["hash_after"] == target_hash == source_hash


def test_policy_denied_artifacts_are_excluded_for_blind_solver(source_tree: Path, source_output: Path, sanitized_output: Path) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output)).output_path

    result = sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output, neutralize_paths=True))

    manifest = result.manifest
    assert result.copied_count == 1
    assert result.excluded_count == 2
    assert [artifact["artifact_id"] for artifact in manifest["included_artifacts"]] == ["ART_PUBLIC_001"]
    assert not (result.output_path / "private/answer-key.md").exists()
    assert {artifact["exclusion_category"] for artifact in manifest["excluded_artifacts"]} >= {"solution_leak", "other_agent_output"}
    policy = manifest["visibility_policy"]
    assert policy["allow_solution"] is False
    assert policy["allow_future_envelopes"] is False
    assert policy["allow_private_notes"] is False
    assert policy["allow_other_agents_outputs"] is False
    assert policy["contains_solution"] is False
    assert policy["contains_private_author_notes"] is False
    assert check_blind_bundle(result.output_path).valid


def test_policy_warnings_are_preserved_without_invalidating_for_human_operator(
    source_tree: Path, source_output: Path, sanitized_output: Path
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[review_warn_spec()])).output_path

    result = sanitize_blind_bundle(
        sanitize_request(source_bundle, sanitized_output, role="human_operator", stage="preflight_review")
    )

    assert result.leak_check_report.valid
    assert result.warnings
    assert result.manifest["isolation_check"]["status"] == "passed_with_warnings"
    assert result.manifest["isolation_check"]["warnings"]


def test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail(
    source_tree: Path, source_output: Path, sanitized_output: Path, tmp_path: Path
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path
    link = tmp_path / "source_link"
    link.symlink_to(source_bundle, target_is_directory=True)
    with pytest.raises(BlindBundleSanitizeError, match="symlink"):
        sanitize_blind_bundle(sanitize_request(link, sanitized_output))

    invalid_manifest_bundle = build_blind_bundle(
        replace(build_request(source_tree, source_output, artifact_specs=[public_spec()]), bundle_id="BUNDLE_INVALID", manifest_id="MANIFEST_INVALID")
    ).output_path
    manifest = load_manifest(invalid_manifest_bundle)
    del manifest["bundle_id"]
    save_manifest(invalid_manifest_bundle, manifest)
    with pytest.raises(BlindBundleSanitizeError, match="manifest"):
        sanitize_blind_bundle(sanitize_request(invalid_manifest_bundle, sanitized_output, sanitized_bundle_id="OUT_INVALID"))

    mismatch_bundle = build_blind_bundle(
        replace(build_request(source_tree, source_output, artifact_specs=[public_spec()]), bundle_id="BUNDLE_MISMATCH", manifest_id="MANIFEST_MISMATCH")
    ).output_path
    (mismatch_bundle / "revealing/depoimento-mirante.md").write_text("alterado\n", encoding="utf-8")
    with pytest.raises(BlindBundleSanitizeError, match="hash mismatch"):
        sanitize_blind_bundle(sanitize_request(mismatch_bundle, sanitized_output, sanitized_bundle_id="OUT_MISMATCH"))

    undeclared_bundle = build_blind_bundle(
        replace(build_request(source_tree, source_output, artifact_specs=[public_spec()]), bundle_id="BUNDLE_UNDECLARED", manifest_id="MANIFEST_UNDECLARED")
    ).output_path
    write(undeclared_bundle / "extra.md", "extra\n")
    with pytest.raises(BlindBundleSanitizeError, match="undeclared"):
        sanitize_blind_bundle(sanitize_request(undeclared_bundle, sanitized_output, sanitized_bundle_id="OUT_UNDECLARED"))


def test_output_existing_overwrite_atomic_cleanup_and_only_specific_bundle_replaced(
    source_tree: Path, source_output: Path, sanitized_output: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path
    existing = sanitized_output / "BUNDLE_SANITIZED_001"
    write(existing / "old.txt", "old")
    sibling = write(sanitized_output / "KEEP_ME/sibling.txt", "keep")

    with pytest.raises(BlindBundleSanitizeError, match="already exists"):
        sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output))
    assert (existing / "old.txt").exists()

    result = sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output, overwrite=True))
    assert not (result.output_path / "old.txt").exists()
    assert sibling.read_text(encoding="utf-8") == "keep"

    import generator.blind_bundle_sanitizer as module

    def fail_final_check(_bundle: Path):
        raise BlindBundleSanitizeError("injected final checker failure")

    monkeypatch.setattr(module, "_run_final_leak_check", fail_final_check)
    with pytest.raises(BlindBundleSanitizeError, match="injected final checker failure"):
        sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output, sanitized_bundle_id="BUNDLE_FAIL"))
    assert not (sanitized_output / "BUNDLE_FAIL").exists()
    assert not list(sanitized_output.glob(".BUNDLE_FAIL.tmp-*"))


def test_checker_final_is_executed_and_invalid_final_bundle_is_not_published(
    source_tree: Path, source_output: Path, sanitized_output: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path

    import generator.blind_bundle_sanitizer as module

    calls = {"count": 0}
    original = module.check_blind_bundle

    def spy(path: Path):
        calls["count"] += 1
        return original(path)

    monkeypatch.setattr(module, "check_blind_bundle", spy)
    sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output))
    assert calls["count"] >= 2

    second_output = sanitized_output / "second"
    second_output.mkdir()

    def corrupt_manifest(path: Path):
        report = original(path)
        if path.name.startswith(".BUNDLE_BAD.tmp"):
            write(path / "undeclared.md", "late leak\n")
            return original(path)
        return report

    monkeypatch.setattr(module, "check_blind_bundle", corrupt_manifest)
    with pytest.raises(BlindBundleSanitizeError, match="LEAK_UNDECLARED_FILE"):
        sanitize_blind_bundle(sanitize_request(source_bundle, second_output, sanitized_bundle_id="BUNDLE_BAD"))
    assert not (second_output / "BUNDLE_BAD").exists()
    assert not list(second_output.glob(".BUNDLE_BAD.tmp-*"))


def test_sanitizer_does_not_read_outside_source_bundle_or_change_text_and_is_deterministic(
    source_tree: Path, source_output: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[public_spec()])).output_path
    before_text = (source_bundle / "revealing/depoimento-mirante.md").read_text(encoding="utf-8")
    manifest = load_manifest(source_bundle)
    manifest["included_artifacts"][0]["path"] = "../outside.md"
    save_manifest(source_bundle, manifest)

    import generator.blind_bundle_sanitizer as module

    original_sha = module._sha256_file

    def guard(path: Path) -> str:
        assert path.resolve(strict=False).is_relative_to(source_bundle.resolve(strict=False))
        return original_sha(path)

    monkeypatch.setattr(module, "_sha256_file", guard)
    with pytest.raises(BlindBundleSanitizeError, match="invalid|unsafe"):
        sanitize_blind_bundle(sanitize_request(source_bundle, tmp_path / "out_bad"))

    monkeypatch.setattr(module, "_sha256_file", original_sha)
    clean_bundle = build_blind_bundle(
        replace(build_request(source_tree, source_output, artifact_specs=[public_spec()]), bundle_id="BUNDLE_CLEAN", manifest_id="MANIFEST_CLEAN")
    ).output_path
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    out1.mkdir()
    out2.mkdir()
    result1 = sanitize_blind_bundle(sanitize_request(clean_bundle, out1, neutralize_paths=True))
    result2 = sanitize_blind_bundle(sanitize_request(clean_bundle, out2, neutralize_paths=True))
    assert result1.manifest == result2.manifest
    assert (result1.output_path / "artifacts/ARTIFACT-001.md").read_text(encoding="utf-8") == before_text


def test_no_allowed_artifacts_and_unsafe_request_paths_fail(source_tree: Path, source_output: Path, sanitized_output: Path) -> None:
    source_bundle = build_blind_bundle(build_request(source_tree, source_output, artifact_specs=[solution_spec()])).output_path
    with pytest.raises(BlindBundleSanitizeError, match="at least one policy-allowed"):
        sanitize_blind_bundle(sanitize_request(source_bundle, sanitized_output))

    good_bundle = build_blind_bundle(
        replace(build_request(source_tree, source_output, artifact_specs=[public_spec()]), bundle_id="BUNDLE_GOOD", manifest_id="MANIFEST_GOOD")
    ).output_path
    for bad_id in ["../escape", "/absolute", "bad\\path", ""]:
        with pytest.raises(BlindBundleSanitizeError):
            sanitize_blind_bundle(sanitize_request(good_bundle, sanitized_output, sanitized_bundle_id=bad_id))


def test_no_cli_file_is_created() -> None:
    assert not Path("generator/blind_bundle_sanitizer_cli.py").exists()

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from generator.blind_bundle_generator import ArtifactSpec, BlindBundleBuildRequest, build_blind_bundle
from generator.blind_bundle_leak_checker import LeakSeverity, check_blind_bundle


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento público\n")
    write(source / "private/solution.md", "Solução privada\n")
    write(source / "review/report.md", "Relatório privado\n")
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


@pytest.fixture
def valid_bundle(source_tree: Path, output_root: Path) -> Path:
    return build_blind_bundle(request(source_tree, output_root)).output_path


def load_manifest(bundle: Path) -> dict:
    return yaml.safe_load((bundle / "blind_bundle_manifest.yaml").read_text(encoding="utf-8"))


def save_manifest(bundle: Path, manifest: dict) -> None:
    (bundle / "blind_bundle_manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def issues_by_code(report, code: str):
    return [issue for issue in report.issues if issue.code == code]


def test_valid_bundle_generated_by_generator_passes(valid_bundle: Path) -> None:
    report = check_blind_bundle(valid_bundle)

    assert report.valid
    assert report.manifest_loaded
    assert report.manifest_schema_valid
    assert report.policy_allowed
    assert report.checked_file_count == 1
    assert report.declared_file_count == 1
    assert report.error_count == 0
    assert report.critical_count == 0
    assert report.warning_count == 0


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (lambda bundle: (bundle / "blind_bundle_manifest.yaml").unlink(), "LEAK_MANIFEST_MISSING"),
        (lambda bundle: (bundle / "blind_bundle_manifest.yaml").write_text(": bad: yaml", encoding="utf-8"), "LEAK_MANIFEST_INVALID_YAML"),
    ],
)
def test_manifest_missing_or_invalid_yaml_fails(valid_bundle: Path, mutate, expected_code: str) -> None:
    mutate(valid_bundle)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert expected_code in issue_codes(report)


def test_manifest_schema_invalid_fails(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    del manifest["role"]
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_MANIFEST_SCHEMA_INVALID" in issue_codes(report)


def test_extra_physical_file_not_declared_fails(valid_bundle: Path) -> None:
    write(valid_bundle / "player/extra.md", "extra\n")

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_UNDECLARED_FILE" in issue_codes(report)


def test_declared_file_missing_fails(valid_bundle: Path) -> None:
    (valid_bundle / "player/depoimento.md").unlink()

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_DECLARED_FILE_MISSING" in issue_codes(report)


def test_hash_mismatch_fails(valid_bundle: Path) -> None:
    (valid_bundle / "player/depoimento.md").write_text("alterado\n", encoding="utf-8")

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    issue = issues_by_code(report, "LEAK_HASH_MISMATCH")[0]
    assert issue.severity == LeakSeverity.CRITICAL


def test_symlink_inside_bundle_fails(valid_bundle: Path) -> None:
    try:
        (valid_bundle / "player/link.md").symlink_to(valid_bundle / "player/depoimento.md")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_FILE_SYMLINK" in issue_codes(report)


def test_symlink_manifest_fails(valid_bundle: Path, tmp_path: Path) -> None:
    manifest_path = valid_bundle / "blind_bundle_manifest.yaml"
    outside_manifest = tmp_path / "outside_manifest.yaml"
    outside_manifest.write_text(manifest_path.read_text(encoding="utf-8"), encoding="utf-8")
    manifest_path.unlink()
    try:
        manifest_path.symlink_to(outside_manifest)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_MANIFEST_NOT_FILE" in issue_codes(report)
    assert "LEAK_FILE_SYMLINK" in issue_codes(report)


def test_excluded_artifact_present_physically_fails(source_tree: Path, output_root: Path) -> None:
    bundle = build_blind_bundle(request(source_tree, output_root, artifact_specs=[public_spec(), solution_spec()])).output_path
    write(bundle / "private/solution.md", "Solução privada vazada\n")

    report = check_blind_bundle(bundle)

    assert not report.valid
    assert "LEAK_EXCLUDED_ARTIFACT_PRESENT" in issue_codes(report)


def test_included_artifact_denied_by_policy_fails(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["included_artifacts"][0]["artifact_type"] = "solution"
    manifest["included_artifacts"][0]["visibility"] = "private_author"
    manifest["visibility_policy"]["allowed_categories"] = ["private_author"]
    manifest["visibility_policy"]["prohibited_categories"] = ["public_player"]
    manifest["visibility_policy"]["contains_solution"] = True
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_POLICY_DENIED_INCLUDED_ARTIFACT" in issue_codes(report)


def test_policy_warning_generates_warning_without_invalidating(source_tree: Path, output_root: Path) -> None:
    spec = solution_spec(artifact_id="ART_PRIVATE_WARN")
    bundle = build_blind_bundle(
        request(
            source_tree,
            output_root,
            role="human_operator",
            stage="preflight_review",
            artifact_specs=[spec],
        )
    ).output_path

    report = check_blind_bundle(bundle)

    assert report.valid
    assert "LEAK_POLICY_WARNING" in issue_codes(report)
    assert report.warning_count >= 1
    assert report.error_count == 0
    assert report.critical_count == 0


@pytest.mark.parametrize(
    ("status", "expected_code", "valid"),
    [
        ("failed", "LEAK_MANIFEST_ISOLATION_FAILED", False),
        ("passed_with_warnings", "LEAK_MANIFEST_ISOLATION_WARNING", True),
        ("not_run", "LEAK_MANIFEST_ISOLATION_FAILED", False),
    ],
)
def test_isolation_check_statuses_are_reported(valid_bundle: Path, status: str, expected_code: str, valid: bool) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["isolation_check"]["status"] = status
    if status == "failed":
        manifest["isolation_check"]["issues"] = [
            {
                "issue_id": "ISSUE_TEST",
                "severity": "high",
                "category": "injected",
                "description": "Injected structural issue.",
                "affected_artifact_ids": ["ART_PUBLIC_001"],
                "recommended_action": "Fix the injected issue.",
            }
        ]
    elif status == "passed_with_warnings":
        manifest["isolation_check"]["warnings"] = [
            {
                "warning_id": "WARNING_TEST",
                "category": "injected",
                "description": "Injected structural warning.",
                "affected_artifact_ids": ["ART_PUBLIC_001"],
                "recommended_action": "Review the injected warning.",
            }
        ]
    else:
        manifest["isolation_check"]["not_run_reason"] = "Injected not-run status for leak checker regression."
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert report.valid is valid
    assert expected_code in issue_codes(report)


@pytest.mark.parametrize("bad_path", ["/absolute.md", "../outside.md", "bad\\path.md", "./same.md"])
def test_unsafe_included_manifest_paths_fail(valid_bundle: Path, bad_path: str) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["included_artifacts"][0]["path"] = bad_path
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_UNSAFE_MANIFEST_PATH" in issue_codes(report)


def test_duplicate_declared_path_and_artifact_id_fail(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    duplicate = dict(manifest["included_artifacts"][0])
    manifest["included_artifacts"].append(duplicate)
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_DUPLICATE_DECLARED_PATH" in issue_codes(report)
    assert "LEAK_DUPLICATE_ARTIFACT_ID" in issue_codes(report)


def test_visibility_policy_prohibited_category_containing_included_visibility_fails(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["visibility_policy"]["prohibited_categories"] = ["public_player"]
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_MANIFEST_POLICY_CONTRADICTION" in issue_codes(report)


def test_visibility_outside_allowed_categories_fails(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["visibility_policy"]["allowed_categories"] = ["derived_report"]
    save_manifest(valid_bundle, manifest)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_MANIFEST_POLICY_CONTRADICTION" in issue_codes(report)


def test_bundle_path_missing_file_and_symlink_fail(tmp_path: Path) -> None:
    missing = check_blind_bundle(tmp_path / "missing")
    assert not missing.valid
    assert "LEAK_BUNDLE_PATH_MISSING" in issue_codes(missing)

    file_path = write(tmp_path / "file.txt", "not a bundle")
    file_report = check_blind_bundle(file_path)
    assert not file_report.valid
    assert "LEAK_BUNDLE_PATH_NOT_DIRECTORY" in issue_codes(file_report)

    real_dir = tmp_path / "real"
    real_dir.mkdir()
    link_dir = tmp_path / "link"
    try:
        link_dir.symlink_to(real_dir, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")
    link_report = check_blind_bundle(link_dir)
    assert not link_report.valid
    assert "LEAK_BUNDLE_PATH_SYMLINK" in issue_codes(link_report)


def test_report_is_deterministic(valid_bundle: Path) -> None:
    write(valid_bundle / "z-extra.md", "extra z\n")
    write(valid_bundle / "a-extra.md", "extra a\n")

    first = check_blind_bundle(valid_bundle)
    second = check_blind_bundle(valid_bundle)

    assert first == second


def test_checker_does_not_modify_bundle(valid_bundle: Path) -> None:
    before = {path.relative_to(valid_bundle).as_posix(): path.stat().st_mtime_ns for path in valid_bundle.rglob("*")}

    check_blind_bundle(valid_bundle)

    after = {path.relative_to(valid_bundle).as_posix(): path.stat().st_mtime_ns for path in valid_bundle.rglob("*")}
    assert after == before


def test_checker_does_not_read_outside_bundle(valid_bundle: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    outside = write(tmp_path / "outside.md", "outside content\n")
    manifest = load_manifest(valid_bundle)
    manifest["included_artifacts"][0]["path"] = "../outside.md"
    manifest["included_artifacts"][0]["hash"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    save_manifest(valid_bundle, manifest)

    import generator.blind_bundle_leak_checker as module

    original_sha256 = module._sha256_file

    def guard(path: Path) -> str:
        assert path.resolve(strict=False).is_relative_to(valid_bundle.resolve(strict=False))
        return original_sha256(path)

    monkeypatch.setattr(module, "_sha256_file", guard)

    report = check_blind_bundle(valid_bundle)

    assert not report.valid
    assert "LEAK_UNSAFE_MANIFEST_PATH" in issue_codes(report)


def test_all_issues_have_stable_required_fields(valid_bundle: Path) -> None:
    write(valid_bundle / "extra.md", "extra\n")

    report = check_blind_bundle(valid_bundle)

    assert report.issues
    for issue in report.issues:
        assert issue.issue_id
        assert issue.code
        assert issue.severity in set(LeakSeverity)
        assert issue.message
        assert issue.recommended_action


def test_warnings_do_not_invalidate_but_errors_and_critical_do(valid_bundle: Path) -> None:
    manifest = load_manifest(valid_bundle)
    manifest["isolation_check"]["status"] = "passed_with_warnings"
    manifest["isolation_check"]["warnings"] = [
        {
            "warning_id": "WARNING_TEST",
            "category": "injected",
            "description": "Injected warning.",
            "affected_artifact_ids": ["ART_PUBLIC_001"],
            "recommended_action": "Review.",
        }
    ]
    save_manifest(valid_bundle, manifest)
    warning_report = check_blind_bundle(valid_bundle)
    assert warning_report.valid
    assert warning_report.warning_count >= 1

    (valid_bundle / "extra.md").write_text("extra\n", encoding="utf-8")
    critical_report = check_blind_bundle(valid_bundle)
    assert not critical_report.valid
    assert critical_report.critical_count >= 1

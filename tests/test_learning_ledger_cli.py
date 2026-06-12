from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml

from generator.learning_ledger_cli import main
from generator.learning_ledger_validator import validate_learning_ledger


def run_cli(args: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = main(args)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def base_session_args(ledger: Path, session_id: str = "SESSION-001") -> list[str]:
    return [
        "create-session",
        "--ledger",
        str(ledger),
        "--session-id",
        session_id,
        "--case-id",
        "CASE-001",
        "--case-version",
        "COMMIT-ABC123",
        "--started-at",
        "2026-06-11T19:00:00-03:00",
        "--finished-at",
        "2026-06-11T20:00:00-03:00",
        "--duration-minutes",
        "60",
        "--created-by",
        "ACTOR-01",
    ]


def base_finding_args(ledger: Path, finding_id: str = "FINDING-001") -> list[str]:
    return [
        "create-finding",
        "--ledger",
        str(ledger),
        "--finding-id",
        finding_id,
        "--case-id",
        "CASE-001",
        "--case-version",
        "COMMIT-ABC123",
        "--source-session-id",
        "SESSION-001",
        "--category",
        "difficulty",
        "--severity",
        "medium",
        "--observation",
        "O grupo permaneceu parado por 12 minutos.",
        "--evidence",
        "Evento STALLED observado na sessão.",
        "--causal-hypothesis",
        "A relação entre os documentos não estava clara.",
        "--created-by",
        "ACTOR-01",
    ]


def base_decision_args(ledger: Path, decision_id: str = "DECISION-001") -> list[str]:
    return [
        "create-decision",
        "--ledger",
        str(ledger),
        "--decision-id",
        decision_id,
        "--case-id",
        "CASE-001",
        "--case-version",
        "COMMIT-ABC123",
        "--finding-id",
        "FINDING-001",
        "--result",
        "no_generalization",
        "--scope",
        "case_only",
        "--rationale",
        "Há evidência de apenas uma sessão.",
        "--decided-by",
        "ACTOR-01",
    ]


def create_session(ledger: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = run_cli(base_session_args(ledger), capsys)
    assert code == 0, err


def create_finding(ledger: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = run_cli(base_finding_args(ledger), capsys)
    assert code == 0, err


def init_ledger(ledger: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = run_cli(["init", "--ledger", str(ledger)], capsys)
    assert code == 0, err


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_no_tmp_files(ledger: Path) -> None:
    assert list(ledger.rglob("*.tmp")) == []


def test_init_creates_missing_empty_and_is_idempotent_without_deleting_content(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    code, out, err = run_cli(["init", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert "Learning Ledger inicializado em:" in out
    assert err == ""
    for child in ["sessions", "findings", "decisions"]:
        assert (ledger / child).is_dir()
    keep = ledger / "sessions" / "keep.txt"
    keep.write_text("preserve", encoding="utf-8")
    code, _, err = run_cli(["init", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert err == ""
    assert keep.read_text(encoding="utf-8") == "preserve"


def test_init_rejects_file_where_subdirectory_should_exist(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / "sessions").write_text("conflict", encoding="utf-8")
    code, out, err = run_cli(["init", "--ledger", str(ledger)], capsys)
    assert code == 1
    assert out == ""
    assert "sessions" in err


def test_schema_loading_works_outside_repo_cwd_and_runs_check_schema(tmp_path: Path, capsys, monkeypatch):
    import generator.learning_ledger_cli as cli

    cli._schema.cache_clear()
    cli._validator.cache_clear()
    calls: list[str] = []
    original = cli.Draft202012Validator.check_schema

    def spy(schema):
        calls.append(schema.get("$id", "schema"))
        return original(schema)

    monkeypatch.setattr(cli.Draft202012Validator, "check_schema", spy)
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    code, _, err = run_cli(base_session_args(ledger), capsys)
    assert code == 0, err
    code, out, err = run_cli(["validate", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert "Ledger válido" in out
    assert err == ""
    assert calls
    cli._schema.cache_clear()
    cli._validator.cache_clear()


def test_entrypoint_help_works_outside_repo_root(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.learning_ledger", "--help"],
        check=False,
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 0
    assert "create-decision" in result.stdout
    assert result.stderr == ""


def test_init_rejects_root_and_subdirectory_symlinks(tmp_path: Path, capsys):
    target = tmp_path / "target"
    target.mkdir()
    root_link = tmp_path / "ledger-link"
    try:
        root_link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")
    code, _, err = run_cli(["init", "--ledger", str(root_link)], capsys)
    assert code == 1
    assert "symlink" in err.lower()

    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / "sessions").symlink_to(target, target_is_directory=True)
    code, _, err = run_cli(["init", "--ledger", str(ledger)], capsys)
    assert code == 1
    assert "symlink" in err.lower()


def test_create_session_writes_valid_deterministic_yaml_and_validate_accepts(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    code, out, err = run_cli(base_session_args(ledger), capsys)
    assert code == 0
    assert "Sessão criada:" in out
    assert err == ""
    path = ledger / "sessions" / "SESSION-001.yaml"
    data = load_yaml(path)
    assert data["session_id"] == "SESSION-001"
    assert data["source_type"] == "live_observation"
    assert data["session_context"]["mode"] == "in_person"
    assert data["ratings"] == {"scale_min": 1, "scale_max": 5, "collected_from": "not_collected"}
    assert data["created_at"].endswith("+00:00")
    assert "!!python" not in path.read_text(encoding="utf-8")
    assert validate_learning_ledger(ledger).valid is True


def test_create_session_rejects_duplicate_invalid_id_timestamp_and_preexisting_invalid_ledger(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    code, _, err = run_cli(base_session_args(ledger), capsys)
    assert code == 1
    assert "já existe" in err
    code, _, err = run_cli(base_session_args(ledger, "bad/id"), capsys)
    assert code == 1
    assert "ID inválido" in err
    bad_ts = base_session_args(ledger, "SESSION-002")
    bad_ts[bad_ts.index("2026-06-11T19:00:00-03:00")] = "2026-06-11T19:00:00"
    code, _, err = run_cli(bad_ts, capsys)
    assert code == 1
    assert "timezone" in err
    (ledger / "findings" / "BROKEN.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")
    code, _, err = run_cli(base_session_args(ledger, "SESSION-003"), capsys)
    assert code == 1
    assert "Ledger inválido" in err
    assert not (ledger / "sessions" / "SESSION-003.yaml").exists()


def test_create_session_dry_run_and_post_write_rollback(tmp_path: Path, capsys, monkeypatch):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    code, out, err = run_cli([*base_session_args(ledger), "--dry-run"], capsys)
    assert code == 0
    assert "session_id: SESSION-001" in out
    assert err == ""
    assert not (ledger / "sessions" / "SESSION-001.yaml").exists()

    calls = {"n": 0}
    import generator.learning_ledger_cli as cli

    real_validate = cli.validate_learning_ledger

    def fail_after_write(path: Path):
        calls["n"] += 1
        if calls["n"] == 2:
            raise cli.LedgerCliError("forced post-write failure")
        return real_validate(path)

    monkeypatch.setattr(cli, "validate_learning_ledger", fail_after_write)
    code, _, err = run_cli(base_session_args(ledger), capsys)
    assert code == 1
    assert "forced post-write failure" in err
    assert not (ledger / "sessions" / "SESSION-001.yaml").exists()


def test_create_finding_checks_session_case_version_and_does_not_mutate_session(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    before = (ledger / "sessions" / "SESSION-001.yaml").read_text(encoding="utf-8")
    code, out, err = run_cli(base_finding_args(ledger), capsys)
    assert code == 0
    assert "Finding criado:" in out
    assert err == ""
    data = load_yaml(ledger / "findings" / "FINDING-001.yaml")
    assert data["status"] == "ACCEPTED"
    assert data["generalization_status"] == "pending"
    assert "learning_decision_id" not in data
    assert (ledger / "sessions" / "SESSION-001.yaml").read_text(encoding="utf-8") == before
    assert validate_learning_ledger(ledger).valid is True
    missing = base_finding_args(ledger, "FINDING-003")
    missing[missing.index("SESSION-001")] = "SESSION-404"
    code, _, err = run_cli(missing, capsys)
    assert code == 1
    assert "Sessão não encontrada" in err
    mismatch = base_finding_args(ledger, "FINDING-004")
    mismatch[mismatch.index("COMMIT-ABC123")] = "OTHER"
    code, _, err = run_cli(mismatch, capsys)
    assert code == 1
    assert "case_version" in err


def test_create_finding_rejects_duplicate(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    code, _, err = run_cli(base_finding_args(ledger), capsys)
    assert code == 1
    assert "já existe" in err


def test_end_to_end_create_decision_updates_finding_and_validate_json(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    code, out, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 0
    assert "Decisão criada:" in out
    assert err == ""
    finding = load_yaml(ledger / "findings" / "FINDING-001.yaml")
    decision = load_yaml(ledger / "decisions" / "DECISION-001.yaml")
    assert finding["generalization_status"] == "decided"
    assert finding["learning_decision_id"] == "DECISION-001"
    assert decision["related_finding_ids"] == ["FINDING-001"]
    assert decision["related_session_ids"] == ["SESSION-001"]
    assert decision["evidence_summary"]["session_count"] == 1
    assert decision["evidence_summary"]["finding_count"] == 1
    report = validate_learning_ledger(ledger)
    assert report.valid is True
    assert report.entity_counts == {"sessions": 1, "findings": 1, "decisions": 1}
    code, human, err = run_cli(["validate", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert "Ledger válido" in human
    assert "Sessions: 1" in human
    assert err == ""
    code, js, err = run_cli(["validate", "--ledger", str(ledger), "--format", "json"], capsys)
    assert code == 0
    parsed = json.loads(js)
    assert parsed["valid"] is True
    assert err == ""


def test_validate_invalid_ledger_returns_one_and_keeps_stdout_stderr_separate(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    (ledger / "findings" / "FINDING-001.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")
    code, out, err = run_cli(["validate", "--ledger", str(ledger)], capsys)
    assert code == 1
    assert "Ledger inválido" in out
    assert "LEDGER_SCHEMA_INVALID" in out
    assert err == ""


def test_create_decision_rejects_missing_non_pending_case_mismatch_duplicate_and_dry_run(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "Finding não encontrado" in err
    create_finding(ledger, capsys)
    dry_code, dry_out, dry_err = run_cli([*base_decision_args(ledger), "--dry-run"], capsys)
    assert dry_code == 0
    assert "# decision" in dry_out
    assert "# updated_finding" in dry_out
    assert dry_err == ""
    assert not (ledger / "decisions" / "DECISION-001.yaml").exists()
    mismatch = base_decision_args(ledger, "DECISION-002")
    mismatch[mismatch.index("CASE-001")] = "CASE-OTHER"
    code, _, err = run_cli(mismatch, capsys)
    assert code == 1
    assert "case_id" in err
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 0
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "já existe" in err
    code, _, err = run_cli(base_decision_args(ledger, "DECISION-002"), capsys)
    assert code == 1
    assert "pending" in err


def test_create_decision_atomic_rollback_when_second_replace_fails(tmp_path: Path, capsys, monkeypatch):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    finding_path = ledger / "findings" / "FINDING-001.yaml"
    before = finding_path.read_text(encoding="utf-8")
    import generator.learning_ledger_cli as cli

    real_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src, dst):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("forced replace failure")
        return real_replace(src, dst)

    monkeypatch.setattr(cli.os, "replace", flaky_replace)
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "forced replace failure" in err
    assert not (ledger / "decisions" / "DECISION-001.yaml").exists()
    assert finding_path.read_text(encoding="utf-8") == before
    assert list(ledger.rglob("*.tmp")) == []


def test_create_decision_staging_failure_does_not_touch_real_ledger(tmp_path: Path, capsys, monkeypatch):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    finding_path = ledger / "findings" / "FINDING-001.yaml"
    before = sha256(finding_path)
    import generator.learning_ledger_cli as cli

    def fail_stage(*args, **kwargs):
        raise cli.LedgerCliError("forced staging failure")

    monkeypatch.setattr(cli, "stage_future_ledger", fail_stage)
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "forced staging failure" in err
    assert not (ledger / "decisions" / "DECISION-001.yaml").exists()
    assert sha256(finding_path) == before
    assert validate_learning_ledger(ledger).valid is True
    assert_no_tmp_files(ledger)


def test_create_decision_first_replace_failure_leaves_original_state(tmp_path: Path, capsys, monkeypatch):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    finding_path = ledger / "findings" / "FINDING-001.yaml"
    before = sha256(finding_path)
    import generator.learning_ledger_cli as cli

    def fail_first(src, dst):
        raise OSError("forced first replace failure")

    monkeypatch.setattr(cli.os, "replace", fail_first)
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "forced first replace failure" in err
    assert not (ledger / "decisions" / "DECISION-001.yaml").exists()
    assert sha256(finding_path) == before
    assert validate_learning_ledger(ledger).valid is True
    assert_no_tmp_files(ledger)


def test_create_decision_post_commit_validation_failure_restores_with_replace(tmp_path: Path, capsys, monkeypatch):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    finding_path = ledger / "findings" / "FINDING-001.yaml"
    before = sha256(finding_path)
    import generator.learning_ledger_cli as cli

    real_validate = cli.validate_learning_ledger
    real_replace = cli.os.replace
    replace_targets: list[Path] = []
    real_ledger_calls = {"n": 0}

    def fake_validate(path):
        if Path(path).resolve() == ledger.resolve():
            real_ledger_calls["n"] += 1
            if real_ledger_calls["n"] == 2:
                issue = SimpleNamespace(code="FORCED_POST_COMMIT", file_path="ledger", message="forced")
                return SimpleNamespace(valid=False, errors=[issue])
        return real_validate(path)

    def tracking_replace(src, dst):
        replace_targets.append(Path(dst))
        return real_replace(src, dst)

    monkeypatch.setattr(cli, "validate_learning_ledger", fake_validate)
    monkeypatch.setattr(cli.os, "replace", tracking_replace)
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 1
    assert "FORCED_POST_COMMIT" in err
    assert not (ledger / "decisions" / "DECISION-001.yaml").exists()
    assert sha256(finding_path) == before
    assert finding_path in replace_targets
    assert validate_learning_ledger(ledger).valid is True
    assert_no_tmp_files(ledger)


def test_decision_preserves_unrelated_finding_fields(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    before = load_yaml(ledger / "findings" / "FINDING-001.yaml")
    code, _, err = run_cli(base_decision_args(ledger), capsys)
    assert code == 0, err
    after = load_yaml(ledger / "findings" / "FINDING-001.yaml")
    for key in ["observation", "evidence", "causal_hypothesis", "status", "severity", "rollback", "gate_effect"]:
        assert after[key] == before[key]


def test_symlink_destination_path_traversal_and_required_args_are_rejected(tmp_path: Path, capsys):
    ledger = tmp_path / "ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    link = ledger / "findings" / "FINDING-LINK.yaml"
    try:
        link.symlink_to(tmp_path / "outside.yaml")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported")
    code, _, err = run_cli(base_finding_args(ledger, "FINDING-LINK"), capsys)
    assert code == 1
    assert "symlink" in err.lower()
    code, _, err = run_cli(base_finding_args(ledger, ".."), capsys)
    assert code == 1
    assert "ID inválido" in err
    code = main(["create-session", "--ledger", str(ledger)])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert "required" in captured.err


def test_validate_warnings_do_not_fail_and_output_is_deterministic(tmp_path: Path, capsys):
    ledger = tmp_path / "warning_ledger"
    init_ledger(ledger, capsys)
    create_session(ledger, capsys)
    create_finding(ledger, capsys)
    finding_path = ledger / "findings" / "FINDING-001.yaml"
    finding = load_yaml(finding_path)
    finding["severity"] = "critical"
    finding_path.write_text(yaml.safe_dump(finding, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, out1, err = run_cli(["validate", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert "Warnings: 1" in out1
    assert err == ""
    code, out2, _ = run_cli(["validate", "--ledger", str(ledger)], capsys)
    assert code == 0
    assert out1 == out2


def test_entrypoint_smoke_help():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.learning_ledger", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "create-session" in result.stdout
    assert result.stderr == ""

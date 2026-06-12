from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

from generator.learning_ledger_validator import validate_learning_ledger

ROOT = Path(__file__).resolve().parents[1]
RETROSPECTIVE_ROOT = ROOT / "examples" / "learning" / "retrospective"
MANIFEST_PATH = RETROSPECTIVE_ROOT / "manifest.yaml"
ALLOWED_ROOT_DOCUMENTS = {"README.md", "manifest.yaml"}
RECONSTRUCTED_SOURCE_TYPES = {"reconstructed_notes", "facilitator_report", "mixed"}
FORBIDDEN_PARTICIPANT_NAMES = {"MARCELO", "GABI", "MARINA"}
DISALLOWED_SOURCE_PARTS = {"output", "tmp", "temp", ".pytest_cache", "__pycache__"}
REMOVED_TECHNICAL_LEDGER = "canonical-visual-build-blocked"
CONSOLIDATED_LEDGER_NAMES = {"aurora-envelope-goals", "aurora-document-diegesis", "aurora-hints-guidance"}
AURORA_LEDGER_PREFIX = "aurora-"
PARTICIPANT_NAME_TOKENS = {"MARCELO", "GABI", "MARINA"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def ledger_dirs(root: Path = RETROSPECTIVE_ROOT) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and child.name not in {"__pycache__"}
    )


def report_details(report: Any) -> str:
    return yaml.safe_dump(report.to_dict(), sort_keys=True, allow_unicode=True)


def manifest(root: Path = RETROSPECTIVE_ROOT) -> dict[str, Any]:
    path = root / "manifest.yaml"
    assert path.exists(), "examples/learning/retrospective/manifest.yaml is required"
    return load_yaml(path)


def manifest_entry_by_path(root: Path = RETROSPECTIVE_ROOT) -> dict[str, dict[str, Any]]:
    entries = manifest(root).get("ledgers", [])
    assert isinstance(entries, list), "manifest.ledgers must be a list"
    by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        assert isinstance(entry, dict), "each manifest ledger entry must be a mapping"
        path = entry.get("path")
        assert isinstance(path, str) and path, "each ledger entry must include path"
        by_path[path] = entry
    return by_path


def entity_files(ledger: Path, kind: str) -> list[Path]:
    directory = ledger / kind
    assert directory.is_dir(), f"{ledger} must include {kind}/"
    return sorted(directory.glob("*.y*ml"))


def load_entities(ledger: Path, kind: str) -> list[dict[str, Any]]:
    return [load_yaml(path) for path in entity_files(ledger, kind)]


def assert_retrospective_examples(root: Path = RETROSPECTIVE_ROOT) -> None:
    ledgers = ledger_dirs(root)
    assert len(ledgers) == 3, "ISSUE-10 should keep exactly three playtest-derived retrospective ledgers"
    assert not (root / REMOVED_TECHNICAL_LEDGER).exists(), "technical build ledger must not be represented as playtest"

    entries = manifest_entry_by_path(root)
    readme = root / "README.md"
    assert readme.exists(), "retrospective README.md is required"
    readme_text = readme.read_text(encoding="utf-8")
    assert "source_documents:" in readme_text, "README must expose testable source_documents lists"
    assert REMOVED_TECHNICAL_LEDGER not in readme_text, "README must not reference removed technical ledger"

    for child in root.iterdir():
        if child.is_file():
            assert child.name in ALLOWED_ROOT_DOCUMENTS, f"unexpected documentary file at retrospective root: {child.name}"

    for ledger in ledgers:
        relative_ledger = ledger.relative_to(root).as_posix()
        assert relative_ledger in entries, f"{relative_ledger} missing from manifest.yaml"
        assert relative_ledger != REMOVED_TECHNICAL_LEDGER
        assert "caso_canonico" not in ledger.as_posix(), "examples must not live inside canonical case folders"

        report = validate_learning_ledger(ledger)
        assert report.valid, report_details(report)
        assert report.entity_counts["sessions"] >= 1
        assert report.entity_counts["findings"] >= 1
        assert report.entity_counts["decisions"] >= 1
        assert report.to_dict() == validate_learning_ledger(ledger).to_dict(), "ledger report must be deterministic"

        sessions = load_entities(ledger, "sessions")
        findings = load_entities(ledger, "findings")
        decisions = load_entities(ledger, "decisions")
        decisions_by_id = {decision["learning_decision_id"]: decision for decision in decisions}
        findings_by_id = {finding["finding_id"]: finding for finding in findings}

        for session in sessions:
            quality = session["record_quality"]
            assert quality["reconstructed_after_session"] is True, "reconstructed_after_session must be true"
            assert quality["recorded_live"] is False, "recorded_live must be false"
            assert session["source_type"] in RECONSTRUCTED_SOURCE_TYPES
            assert session["ratings"]["collected_from"] == "not_collected"
            participant_ids = [participant["participant_id"] for participant in session.get("participants", [])]
            participant_blob = yaml.safe_dump(session.get("participants", []), allow_unicode=True).upper()
            assert not (PARTICIPANT_NAME_TOKENS & set(participant_blob.replace("-", " ").split()))
            assert participant_ids, "retrospective playtest sessions must preserve human participant records"
            assert "technical" not in session["session_context"].get("notes", "").lower()
            if relative_ledger.startswith(AURORA_LEDGER_PREFIX):
                assert len(session["participants"]) == 3, "Hotel Aurora playtest ledgers must preserve three anonymized participants"
                assert set(participant_ids) == {"PARTICIPANT-RETRO-01", "PARTICIPANT-RETRO-02", "PARTICIPANT-RETRO-03"}

        for finding in findings:
            decision_id = finding.get("learning_decision_id")
            assert finding["generalization_status"] == "decided"
            assert decision_id in decisions_by_id
            assert finding["finding_id"] in decisions_by_id[decision_id]["related_finding_ids"]
            assert finding["impact"]["affected_participant_count"] != 0, "affected participants must not use zero as unknown when playtest players existed"
            if relative_ledger in CONSOLIDATED_LEDGER_NAMES:
                assert finding["status"] == "RESOLVED", f"{relative_ledger} is historically consolidated"
                assert "action_expected" not in finding
                assert "assigned_to" not in finding
                resolution = finding.get("resolution")
                assert isinstance(resolution, dict), "resolved findings need resolution payload"
                assert resolution.get("corrected_artifact_version_ids"), "resolved findings need corrected artifact version ids"
                assert resolution.get("validation_evidence"), "resolved findings need validation evidence"
                assert resolution.get("validation_result") in {"confirmed", "partially_confirmed"}
                assert finding["gate_effect"]["blocks_gate"] is False
                assert finding["gate_effect"]["suggested_gate_state"] in {"PASS", "none"}

        for decision in decisions:
            assert decision["scope"]["level"] != "global_editorial" or decision.get("global_evidence_basis")
            assert decision["result"] != "guardrail", "retrospective examples must not promote automatically to guardrail"
            if relative_ledger in CONSOLIDATED_LEDGER_NAMES:
                assert decision["implementation_status"] != "proposed", "consolidated historical fixes must not remain proposed"
            for finding_id in decision["related_finding_ids"]:
                assert finding_id in findings_by_id
                finding = findings_by_id[finding_id]
                assert finding["learning_decision_id"] == decision["learning_decision_id"]

        source_documents = entries[relative_ledger].get("source_documents")
        assert isinstance(source_documents, list) and source_documents, f"{relative_ledger} must list source_documents"
        for source in source_documents:
            assert isinstance(source, str) and source, "source path must be a non-empty string"
            source_path = Path(source)
            assert not source_path.is_absolute(), f"source path must be relative: {source}"
            assert ".." not in source_path.parts, f"source path must not contain '..': {source}"
            assert not any(part in DISALLOWED_SOURCE_PARTS for part in source_path.parts), f"source path must not be generated/temp: {source}"
            assert source_path.parts[:2] == ("docs", "playtests"), f"retrospective ledgers must be sourced from playtest docs: {source}"
            assert (ROOT / source_path).is_file(), f"source document does not exist: {source}"
            assert source in readme_text, f"README must reference source document: {source}"

    manifest_text = (root / "manifest.yaml").read_text(encoding="utf-8")
    assert REMOVED_TECHNICAL_LEDGER not in manifest_text, "manifest must not reference removed technical ledger"


def test_retrospective_learning_examples_are_valid_and_provenanced() -> None:
    assert_retrospective_examples()


def copy_retrospective_tree(tmp_path: Path) -> Path:
    destination = tmp_path / "retrospective"
    shutil.copytree(RETROSPECTIVE_ROOT, destination)
    return destination


def test_guard_fails_when_no_ledger_is_found(tmp_path: Path) -> None:
    root = tmp_path / "retrospective"
    root.mkdir()
    (root / "README.md").write_text("source_documents:\n", encoding="utf-8")
    (root / "manifest.yaml").write_text("ledgers: []\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="exactly three"):
        assert_retrospective_examples(root)


def test_guard_fails_when_a_ledger_is_invalid(tmp_path: Path) -> None:
    root = copy_retrospective_tree(tmp_path)
    first_session = next((root / "aurora-envelope-goals" / "sessions").glob("*.yaml"))
    data = load_yaml(first_session)
    data.pop("session_id")
    first_session.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AssertionError, match="LEDGER_SCHEMA_INVALID"):
        assert_retrospective_examples(root)


def test_guard_fails_without_retrospective_marking(tmp_path: Path) -> None:
    root = copy_retrospective_tree(tmp_path)
    first_session = next((root / "aurora-envelope-goals" / "sessions").glob("*.yaml"))
    data = load_yaml(first_session)
    data["record_quality"]["recorded_live"] = True
    first_session.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AssertionError, match="recorded_live"):
        assert_retrospective_examples(root)


def test_guard_fails_when_source_document_is_missing(tmp_path: Path) -> None:
    root = copy_retrospective_tree(tmp_path)
    manifest_path = root / "manifest.yaml"
    data = load_yaml(manifest_path)
    data["ledgers"][0]["source_documents"] = ["docs/playtests/does-not-exist.md"]
    manifest_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AssertionError, match="source document does not exist"):
        assert_retrospective_examples(root)


def test_guard_fails_for_global_editorial_decision_without_basis(tmp_path: Path) -> None:
    root = copy_retrospective_tree(tmp_path)
    first_decision = next((root / "aurora-envelope-goals" / "decisions").glob("*.yaml"))
    data = load_yaml(first_decision)
    data["scope"] = {
        "level": "global_editorial",
        "description": "Deliberately invalid broad scope for guard test.",
        "applicability_conditions": ["Any case."],
        "evidence_threshold": "Multiple sessions and cases would be required.",
    }
    data.pop("global_evidence_basis", None)
    first_decision.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AssertionError, match="global_evidence_basis"):
        assert_retrospective_examples(root)


def test_validator_fails_when_finding_and_decision_links_are_not_reciprocal(tmp_path: Path) -> None:
    root = copy_retrospective_tree(tmp_path)
    first_finding = next((root / "aurora-envelope-goals" / "findings").glob("*.yaml"))
    data = load_yaml(first_finding)
    data["learning_decision_id"] = "DECISION-RETRO-MISSING"
    first_finding.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    report = validate_learning_ledger(root / "aurora-envelope-goals")
    assert not report.valid
    assert any(issue.code == "LEDGER_GENERALIZATION_STATUS_MISMATCH" for issue in report.errors)

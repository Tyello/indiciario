"""RED tests for run manifest semantics (ISSUE-27, STEP-06).

These tests describe cases 21-28 of the ISSUE-27 spec: semantic rules
RM_001-RM_008 applied by ``validate_run_manifest_semantics``.

They are expected to FAIL (RED) until ``generator/run_manifest.py`` provides
``validate_run_manifest_semantics``. The import of that symbol at module top
makes the whole module fail to collect with ImportError while the function is
absent; that missing symbol is the RED target of this step. No GREEN here.
"""

from __future__ import annotations

from typing import Any

from generator.run_manifest import (
    ManifestArtifactSummary,
    ManifestDecisionSummary,
    ManifestFinding,
    ManifestGateOutcome,
    ManifestSemanticResult,
    RunManifest,
    build_run_manifest,
    manifest_to_dict,
    validate_run_manifest,
    validate_run_manifest_semantics,
)
from generator.workspace import VALID_STAGES, build_workspace_run


def _artifact(**overrides: Any) -> dict[str, Any]:
    artifact = {
        "artifact_id": "BUNDLE-001",
        "artifact_type": "blind_bundle",
        "stage": "blind_solve",
        "sha256": "a" * 64,
    }
    artifact.update(overrides)
    return artifact


def _decision(**overrides: Any) -> dict[str, Any]:
    decision = {
        "decision_id": "DEC-001",
        "stage": "gate_evaluation",
        "outcome": "approved",
        "decided_by": "human",
        "decided_at": "2026-06-20T11:00:00Z",
    }
    decision.update(overrides)
    return decision


def _finding(**overrides: Any) -> dict[str, Any]:
    finding = {
        "source_artifact_id": "NR-AURORA-001",
        "source_type": "narrative_review",
        "code": "NR_003",
        "severity": "major",
        "field": "personagens",
        "message": "Nenhum personagem tem papel suspeito alem do executor.",
    }
    finding.update(overrides)
    return finding


def _gate_outcome(**overrides: Any) -> dict[str, Any]:
    gate_outcome = {
        "decision_id": "DEC-001",
        "outcome": "approved",
        "justification": "Conclusao esperada atingida.",
    }
    gate_outcome.update(overrides)
    return gate_outcome


def _manifest(
    *,
    manifest_id: str = "MANIFEST-AURORA-20260620-001",
    run_id: str = "RUN-AURORA-20260620-001",
    pipeline_status: str = "complete",
    stages_completed: list[str] | None = None,
    artifacts_summary: list[dict[str, Any]] | None = None,
    decisions_summary: list[dict[str, Any]] | None = None,
    findings: list[dict[str, Any]] | None = None,
    gate_outcome: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "manifest_id": manifest_id,
        "run_id": run_id,
        "case_ref": "examples/caso_canonico_intermediario.json",
        "generated_at": "2026-06-20T12:00:00Z",
        "generated_by": "orchestrator",
        "pipeline_status": pipeline_status,
        "stages_completed": (
            stages_completed
            if stages_completed is not None
            else [
                "blind_solve",
                "gate_evaluation",
                "narrative_review",
                "evidence_review",
            ]
        ),
        "artifacts_summary": (
            artifacts_summary if artifacts_summary is not None else []
        ),
        "decisions_summary": (
            decisions_summary if decisions_summary is not None else []
        ),
        "findings": findings if findings is not None else [],
        "gate_outcome": gate_outcome,
        "next_steps": (
            next_steps
            if next_steps is not None
            else ["Pipeline completo. Revisar findings e prosseguir para ISSUE-28."]
        ),
        "notes": notes,
    }


def _codes(result: ManifestSemanticResult) -> list[str]:
    return [
        message.split(":", 1)[0].strip()
        for message in (*result.errors, *result.warnings)
    ]


def _all_stage_artifacts() -> list[dict[str, Any]]:
    return [
        _artifact(
            artifact_id="BUNDLE-001",
            artifact_type="blind_bundle",
            stage="blind_solve",
        ),
        _artifact(
            artifact_id="GATE-001",
            artifact_type="gate_evaluation",
            stage="gate_evaluation",
        ),
        _artifact(
            artifact_id="NR-001",
            artifact_type="narrative_review",
            stage="narrative_review",
        ),
        _artifact(
            artifact_id="ER-001",
            artifact_type="evidence_review",
            stage="evidence_review",
        ),
    ]


# === Cases 21-28: rules RM_001-RM_008 ========================================


# --- Case 21: manifest_id == run_id -> RM_001 error --------------------------


def test_rm_001_manifest_id_equals_run_id_is_error() -> None:
    manifest = _manifest(
        manifest_id="SAME-ID-001",
        run_id="SAME-ID-001",
        artifacts_summary=_all_stage_artifacts(),
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_001" in " ".join(result.errors)
    assert result.valid is False


# --- Case 22: stage in stages_completed without artifact -> RM_002 error -----


def test_rm_002_stage_without_artifact_is_error() -> None:
    manifest = _manifest(
        stages_completed=["blind_solve", "gate_evaluation"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
        ],
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_002" in " ".join(result.errors)
    assert result.valid is False


# --- Case 23: gate_outcome.decision_id absent from decisions -> RM_003 error -


def test_rm_003_gate_outcome_decision_id_absent_is_error() -> None:
    manifest = _manifest(
        artifacts_summary=_all_stage_artifacts(),
        decisions_summary=[_decision(decision_id="DEC-001")],
        gate_outcome=_gate_outcome(decision_id="DEC-MISSING"),
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_003" in " ".join(result.errors)
    assert result.valid is False


# --- Case 24: pipeline_status complete without all 4 stages -> RM_004 error --


def test_rm_004_complete_without_all_stages_is_error() -> None:
    manifest = _manifest(
        pipeline_status="complete",
        stages_completed=["blind_solve", "gate_evaluation"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_004" in " ".join(result.errors)
    assert result.valid is False


# --- Case 25: finding source_artifact_id absent from artifacts -> RM_005 -----


def test_rm_005_finding_source_artifact_absent_is_error() -> None:
    manifest = _manifest(
        artifacts_summary=_all_stage_artifacts(),
        findings=[_finding(source_artifact_id="MISSING-ARTIFACT")],
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_005" in " ".join(result.errors)
    assert result.valid is False


# --- Case 26: multiple gate_evaluation decisions -> RM_006 warning -----------


def test_rm_006_multiple_gate_decisions_is_warning() -> None:
    manifest = _manifest(
        artifacts_summary=_all_stage_artifacts(),
        decisions_summary=[
            _decision(decision_id="DEC-001", stage="gate_evaluation"),
            _decision(
                decision_id="DEC-002",
                stage="gate_evaluation",
                outcome="rejected",
            ),
        ],
        gate_outcome=_gate_outcome(decision_id="DEC-001"),
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_006" in " ".join(result.warnings)
    assert result.valid is True


# --- Case 27: pipeline_status blocked without rejected decision -> RM_007 ----


def test_rm_007_blocked_without_rejected_is_warning() -> None:
    manifest = _manifest(
        pipeline_status="blocked",
        stages_completed=["blind_solve", "gate_evaluation"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
        decisions_summary=[_decision(decision_id="DEC-001", outcome="approved")],
        gate_outcome=_gate_outcome(decision_id="DEC-001"),
        next_steps=["Gate bloqueado. Revisar gate_outcome."],
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_007" in " ".join(result.warnings)
    assert result.valid is True


# --- Case 28: pipeline_status incomplete + next_steps empty -> RM_008 --------


def test_rm_008_incomplete_with_empty_next_steps_is_warning() -> None:
    manifest = _manifest(
        pipeline_status="incomplete",
        stages_completed=["blind_solve"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
        ],
        next_steps=[],
    )
    result = validate_run_manifest_semantics(manifest)
    assert "RM_008" in " ".join(result.warnings)
    assert result.valid is True


# === Cases 29-35: validate_run_manifest_semantics result + mutation ==========


# --- Case 29: clean manifest -> valid True, errors empty ---------------------


def test_clean_manifest_is_valid_with_no_errors() -> None:
    manifest = _manifest(artifacts_summary=_all_stage_artifacts())
    result = validate_run_manifest_semantics(manifest)
    assert isinstance(result, ManifestSemanticResult)
    assert result.valid is True
    assert result.errors == ()


# --- Case 30: RM_001 -> valid False -----------------------------------------


def test_rm_001_makes_result_invalid() -> None:
    manifest = _manifest(
        manifest_id="SAME-ID-001",
        run_id="SAME-ID-001",
        artifacts_summary=_all_stage_artifacts(),
    )
    result = validate_run_manifest_semantics(manifest)
    assert result.valid is False


# --- Case 31: only RM_006 warning -> valid True, warnings non-empty ----------


def test_only_warning_keeps_result_valid() -> None:
    manifest = _manifest(
        artifacts_summary=_all_stage_artifacts(),
        decisions_summary=[
            _decision(decision_id="DEC-001", stage="gate_evaluation"),
            _decision(
                decision_id="DEC-002",
                stage="gate_evaluation",
                outcome="rejected",
            ),
        ],
        gate_outcome=_gate_outcome(decision_id="DEC-001"),
    )
    result = validate_run_manifest_semantics(manifest)
    assert result.valid is True
    assert result.errors == ()
    assert result.warnings != ()
    assert _codes(result) == ["RM_006"]


# --- Case 32: multiple errors accumulated (RM_002 + RM_005) ------------------


def test_multiple_errors_accumulate() -> None:
    manifest = _manifest(
        stages_completed=["blind_solve", "gate_evaluation"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
        ],
        findings=[_finding(source_artifact_id="MISSING-ARTIFACT")],
    )
    result = validate_run_manifest_semantics(manifest)
    joined = " ".join(result.errors)
    assert "RM_002" in joined
    assert "RM_005" in joined
    assert len(result.errors) >= 2
    assert result.valid is False


# --- Case 33: no findings and no decisions -> semantically valid ------------


def test_manifest_without_findings_or_decisions_is_valid() -> None:
    manifest = _manifest(
        artifacts_summary=_all_stage_artifacts(),
        decisions_summary=[],
        findings=[],
        gate_outcome=None,
    )
    result = validate_run_manifest_semantics(manifest)
    assert result.valid is True
    assert result.errors == ()


# --- Case 34: warnings and valid True together (RM_007 + RM_008) -------------


def test_multiple_warnings_keep_result_valid() -> None:
    manifest = _manifest(
        pipeline_status="blocked",
        stages_completed=["blind_solve", "gate_evaluation"],
        artifacts_summary=[
            _artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
        decisions_summary=[_decision(decision_id="DEC-001", outcome="approved")],
        gate_outcome=_gate_outcome(decision_id="DEC-001"),
        next_steps=[],
    )
    result = validate_run_manifest_semantics(manifest)
    joined = " ".join(result.warnings)
    assert "RM_007" in joined
    assert "RM_008" in joined
    assert result.errors == ()
    assert result.valid is True


# --- Case 35: validate_run_manifest_semantics does not mutate input ----------


def test_semantics_does_not_mutate_input() -> None:
    import copy

    manifest = _manifest(
        manifest_id="SAME-ID-001",
        run_id="SAME-ID-001",
        artifacts_summary=_all_stage_artifacts(),
        findings=[_finding(source_artifact_id="MISSING-ARTIFACT")],
    )
    snapshot = copy.deepcopy(manifest)
    validate_run_manifest_semantics(manifest)
    assert manifest == snapshot


# === Cases 36-45: build_run_manifest =========================================


def _ws_artifact(**overrides: Any) -> dict[str, Any]:
    artifact = {
        "artifact_id": "BUNDLE-001",
        "artifact_type": "blind_bundle",
        "path": "workspace/run-001/artifacts/bundle-001/",
        "sha256": "a" * 64,
        "ingested_at": "2026-06-20T10:05:00Z",
        "stage": "blind_solve",
        "visible_to": ["blind_solver"],
    }
    artifact.update(overrides)
    return artifact


def _ws_decision(**overrides: Any) -> dict[str, Any]:
    decision = {
        "decision_id": "DEC-001",
        "stage": "gate_evaluation",
        "outcome": "approved",
        "justification": "Conclusao esperada atingida com evidencia suficiente.",
        "decided_at": "2026-06-20T11:00:00Z",
        "decided_by": "human",
        "rollback_to_stage": None,
    }
    decision.update(overrides)
    return decision


def _ws_run(
    *,
    status: str = "in_progress",
    current_stage: str = "blind_solve",
    artifacts: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    run = build_workspace_run(
        run_id="RUN-AURORA-20260620-001",
        case_ref="examples/caso_canonico_intermediario.json",
        created_at="2026-06-20T10:00:00Z",
    )
    run["status"] = status
    run["current_stage"] = current_stage
    run["artifacts"] = artifacts if artifacts is not None else []
    run["decisions"] = decisions if decisions is not None else []
    return run


def _ws_all_stage_artifacts() -> list[dict[str, Any]]:
    return [
        _ws_artifact(
            artifact_id="BUNDLE-001",
            artifact_type="blind_bundle",
            stage="blind_solve",
        ),
        _ws_artifact(
            artifact_id="GATE-001",
            artifact_type="gate_evaluation",
            stage="gate_evaluation",
        ),
        _ws_artifact(
            artifact_id="NR-001",
            artifact_type="narrative_review",
            stage="narrative_review",
        ),
        _ws_artifact(
            artifact_id="ER-001",
            artifact_type="evidence_review",
            stage="evidence_review",
        ),
    ]


# --- Case 36: status done -> pipeline_status complete ------------------------


def test_build_status_done_maps_to_complete() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["pipeline_status"] == "complete"


# --- Case 37: status in_progress -> pipeline_status incomplete ---------------


def test_build_status_in_progress_maps_to_incomplete() -> None:
    run = _ws_run(
        status="in_progress",
        current_stage="blind_solve",
        artifacts=[_ws_artifact()],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["pipeline_status"] == "incomplete"


# --- Case 38: status gate_blocked -> pipeline_status blocked -----------------


def test_build_status_gate_blocked_maps_to_blocked() -> None:
    run = _ws_run(
        status="gate_blocked",
        current_stage="gate_evaluation",
        artifacts=[
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _ws_artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
        decisions=[
            _ws_decision(decision_id="DEC-001", outcome="rejected"),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["pipeline_status"] == "blocked"


# --- Case 39: status rolled_back -> pipeline_status rolled_back --------------


def test_build_status_rolled_back_maps_to_rolled_back() -> None:
    run = _ws_run(
        status="rolled_back",
        current_stage="initialized",
        artifacts=[_ws_artifact()],
        decisions=[
            _ws_decision(
                decision_id="DEC-001",
                outcome="rollback",
                rollback_to_stage="blind_solve",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["pipeline_status"] == "rolled_back"


# --- Case 40: stages_completed only stages with ingested artifacts -----------


def test_build_stages_completed_only_with_artifacts() -> None:
    run = _ws_run(
        status="in_progress",
        current_stage="narrative_review",
        artifacts=[
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _ws_artifact(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["stages_completed"] == ["blind_solve", "narrative_review"]


# --- Case 41: stages_completed respects VALID_STAGES order -------------------


def test_build_stages_completed_respects_valid_stages_order() -> None:
    # Artifacts ingested out of stage order; output must follow VALID_STAGES.
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=[
            _ws_artifact(
                artifact_id="ER-001",
                artifact_type="evidence_review",
                stage="evidence_review",
            ),
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _ws_artifact(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
            ),
            _ws_artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    stages = manifest["stages_completed"]
    expected = [
        stage
        for stage in VALID_STAGES
        if stage in {"blind_solve", "gate_evaluation", "narrative_review", "evidence_review"}
    ]
    assert stages == expected


# --- Case 42: artifacts_summary mirrors workspace artifacts ------------------


def test_build_artifacts_summary_mirrors_workspace() -> None:
    artifacts = _ws_all_stage_artifacts()
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=artifacts,
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    summary = manifest["artifacts_summary"]
    assert len(summary) == len(artifacts)
    by_id = {entry["artifact_id"]: entry for entry in summary}
    for artifact in artifacts:
        entry = by_id[artifact["artifact_id"]]
        assert entry["artifact_type"] == artifact["artifact_type"]
        assert entry["stage"] == artifact["stage"]
        assert entry["sha256"] == artifact["sha256"]


# --- Case 43: decisions_summary mirrors workspace decisions ------------------


def test_build_decisions_summary_mirrors_workspace() -> None:
    decisions = [
        _ws_decision(decision_id="DEC-001", outcome="approved"),
        _ws_decision(
            decision_id="DEC-002",
            stage="narrative_review",
            outcome="rejected",
        ),
    ]
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=decisions,
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    summary = manifest["decisions_summary"]
    assert len(summary) == len(decisions)
    by_id = {entry["decision_id"]: entry for entry in summary}
    for decision in decisions:
        entry = by_id[decision["decision_id"]]
        assert entry["stage"] == decision["stage"]
        assert entry["outcome"] == decision["outcome"]
        assert entry["decided_by"] == decision["decided_by"]
        assert entry["decided_at"] == decision["decided_at"]


# --- Case 44: gate_outcome filled when gate_evaluation decision exists -------


def test_build_gate_outcome_filled_when_gate_decision_exists() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[
            _ws_decision(
                decision_id="DEC-001",
                stage="gate_evaluation",
                outcome="approved",
                justification="Conclusao esperada atingida.",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    gate_outcome = manifest["gate_outcome"]
    assert gate_outcome is not None
    assert gate_outcome["decision_id"] == "DEC-001"
    assert gate_outcome["outcome"] == "approved"
    assert gate_outcome["justification"] == "Conclusao esperada atingida."


# --- Case 45: gate_outcome null when no gate_evaluation decision -------------


def test_build_gate_outcome_null_without_gate_decision() -> None:
    run = _ws_run(
        status="in_progress",
        current_stage="narrative_review",
        artifacts=[
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _ws_artifact(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
            ),
        ],
        decisions=[
            _ws_decision(
                decision_id="DEC-001",
                stage="narrative_review",
                outcome="approved",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    assert manifest["gate_outcome"] is None


# === Cases 46-55: build_run_manifest findings and next_steps =================


def _ws_finding(**overrides: Any) -> dict[str, Any]:
    finding = {
        "code": "NR_003",
        "severity": "major",
        "field": "personagens",
        "message": "Nenhum personagem tem papel suspeito alem do executor.",
    }
    finding.update(overrides)
    return finding


# --- Case 46: empty findings_by_artifact -> findings [] ----------------------


def test_build_empty_findings_by_artifact_yields_no_findings() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(
        run,
        manifest_id="MANIFEST-AURORA-001",
        findings_by_artifact={},
    )
    assert manifest["findings"] == []


# --- Case 47: findings from narrative_review -> source_type narrative_review -


def test_build_findings_from_narrative_review_source_type() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(
        run,
        manifest_id="MANIFEST-AURORA-001",
        findings_by_artifact={"NR-001": [_ws_finding(code="NR_003")]},
    )
    findings = manifest["findings"]
    assert len(findings) == 1
    assert findings[0]["source_artifact_id"] == "NR-001"
    assert findings[0]["source_type"] == "narrative_review"
    assert findings[0]["code"] == "NR_003"


# --- Case 48: findings from evidence_review -> source_type evidence_review ---


def test_build_findings_from_evidence_review_source_type() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(
        run,
        manifest_id="MANIFEST-AURORA-001",
        findings_by_artifact={"ER-001": [_ws_finding(code="ER_002")]},
    )
    findings = manifest["findings"]
    assert len(findings) == 1
    assert findings[0]["source_artifact_id"] == "ER-001"
    assert findings[0]["source_type"] == "evidence_review"
    assert findings[0]["code"] == "ER_002"


# --- Case 49: build_run_manifest does not mutate run nor findings_by_artifact -


def test_build_does_not_mutate_run_or_findings_by_artifact() -> None:
    import copy

    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    findings_by_artifact = {
        "NR-001": [_ws_finding(code="NR_003")],
        "ER-001": [_ws_finding(code="ER_002")],
    }
    run_snapshot = copy.deepcopy(run)
    findings_snapshot = copy.deepcopy(findings_by_artifact)
    build_run_manifest(
        run,
        manifest_id="MANIFEST-AURORA-001",
        findings_by_artifact=findings_by_artifact,
    )
    assert run == run_snapshot
    assert findings_by_artifact == findings_snapshot


# --- Case 50: complete run without findings -> next_steps pipeline complete --


def test_build_complete_run_next_steps_pipeline_complete() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    next_steps = manifest["next_steps"]
    assert next_steps == [
        "Pipeline completo. Revisar findings e prosseguir para ISSUE-28.",
    ]


# --- Case 51: incomplete run without blind_solve -> next_steps blind_solve ---


def test_build_incomplete_without_blind_solve_next_steps_blind_solve() -> None:
    run = _ws_run(
        status="in_progress",
        current_stage="initialized",
        artifacts=[],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    next_steps = manifest["next_steps"]
    assert next_steps == [
        "Ingerir blind_solver_report para avançar para gate_evaluation.",
    ]


# --- Case 52: incomplete run without gate_evaluation -> next_steps gate -------


def test_build_incomplete_without_gate_evaluation_next_steps_gate() -> None:
    run = _ws_run(
        status="in_progress",
        current_stage="blind_solve",
        artifacts=[
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
        ],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    next_steps = manifest["next_steps"]
    assert next_steps == [
        "Ingerir gate_evaluation para avançar para narrative_review.",
    ]


# --- Case 53: blocked run -> next_steps gate blocked ------------------------


def test_build_blocked_run_next_steps_gate_blocked() -> None:
    run = _ws_run(
        status="gate_blocked",
        current_stage="gate_evaluation",
        artifacts=[
            _ws_artifact(
                artifact_id="BUNDLE-001",
                artifact_type="blind_bundle",
                stage="blind_solve",
            ),
            _ws_artifact(
                artifact_id="GATE-001",
                artifact_type="gate_evaluation",
                stage="gate_evaluation",
            ),
        ],
        decisions=[_ws_decision(decision_id="DEC-001", outcome="rejected")],
    )
    manifest = build_run_manifest(run, manifest_id="MANIFEST-AURORA-001")
    next_steps = manifest["next_steps"]
    assert next_steps == [
        "Gate bloqueado. Revisar gate_outcome e registrar decisão de rollback ou desbloqueio.",
    ]


# --- Case 54: manifest from build_run_manifest passes validate_run_manifest --


def test_build_manifest_passes_structural_validation() -> None:
    run = _ws_run(
        status="done",
        current_stage="complete",
        artifacts=_ws_all_stage_artifacts(),
        decisions=[_ws_decision()],
    )
    manifest = build_run_manifest(
        run,
        manifest_id="MANIFEST-AURORA-001",
        findings_by_artifact={"NR-001": [_ws_finding(code="NR_003")]},
    )
    errors = validate_run_manifest(manifest)
    assert errors == []


# --- Case 55: manifest_to_dict + validate_run_manifest round-trip no loss -----


def test_manifest_to_dict_round_trip_no_loss() -> None:
    manifest = RunManifest(
        manifest_id="MANIFEST-AURORA-001",
        run_id="RUN-AURORA-20260620-001",
        case_ref="examples/caso_canonico_intermediario.json",
        generated_at="2026-06-20T12:00:00Z",
        generated_by="orchestrator",
        pipeline_status="complete",
        stages_completed=(
            "blind_solve",
            "gate_evaluation",
            "narrative_review",
            "evidence_review",
        ),
        artifacts_summary=(
            ManifestArtifactSummary(
                artifact_id="NR-001",
                artifact_type="narrative_review",
                stage="narrative_review",
                sha256="a" * 64,
            ),
        ),
        decisions_summary=(
            ManifestDecisionSummary(
                decision_id="DEC-001",
                stage="gate_evaluation",
                outcome="approved",
                decided_by="human",
                decided_at="2026-06-20T11:00:00Z",
            ),
        ),
        findings=(
            ManifestFinding(
                source_artifact_id="NR-001",
                source_type="narrative_review",
                code="NR_003",
                severity="major",
                field="personagens",
                message="Nenhum personagem tem papel suspeito.",
            ),
        ),
        gate_outcome=ManifestGateOutcome(
            decision_id="DEC-001",
            outcome="approved",
            justification="Conclusao esperada atingida.",
        ),
        next_steps=(
            "Pipeline completo. Revisar findings e prosseguir para ISSUE-28.",
        ),
        notes="",
    )
    as_dict = manifest_to_dict(manifest)
    assert validate_run_manifest(as_dict) == []
    assert as_dict["manifest_id"] == "MANIFEST-AURORA-001"
    assert as_dict["gate_outcome"]["decision_id"] == "DEC-001"
    assert as_dict["findings"][0]["source_artifact_id"] == "NR-001"
    assert as_dict["stages_completed"] == [
        "blind_solve",
        "gate_evaluation",
        "narrative_review",
        "evidence_review",
    ]

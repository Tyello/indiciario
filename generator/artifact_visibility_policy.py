"""Pure artifact visibility policy for multi-agent blind bundle metadata.

The policy complements the blind bundle manifest schema with deterministic,
offline semantic decisions. It evaluates only structured metadata supplied by
callers; it never reads artifact files, checks hashes, or validates the manifest
schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["allow", "warn", "deny"]

ROLES = frozenset(
    {
        "blind_solver",
        "logic_reviewer",
        "narrative_reviewer",
        "evidence_reviewer",
        "visual_reviewer",
        "accessibility_reviewer",
        "adversarial_reviewer",
        "gate_evaluator",
        "facilitator",
        "human_operator",
        "technical_reviewer",
    }
)

STAGES = frozenset(
    {
        "case_generation",
        "preflight_review",
        "blind_solve",
        "evidence_review",
        "narrative_review",
        "visual_review",
        "accessibility_review",
        "adversarial_review",
        "gate_evaluation",
        "playtest_analysis",
        "learning_review",
        "technical_validation",
    }
)

VISIBILITY_CATEGORIES = frozenset(
    {
        "public_player",
        "private_author",
        "review_private",
        "facilitator",
        "derived_report",
        "playtest_anonymized",
        "technical_metadata",
    }
)

ARTIFACT_TYPES = frozenset(
    {
        "case_blueprint",
        "player_document",
        "facilitator_guide",
        "envelope_cover",
        "map",
        "clue",
        "answer_key",
        "solution",
        "review_report",
        "playtest_report",
        "learning_record",
        "schema",
        "template",
        "render_output",
        "manifest",
        "other",
    }
)

ENVELOPE_SCOPES = frozenset(
    {
        "none",
        "envelope_1",
        "envelope_2",
        "envelope_3",
        "current_envelope",
        "previous_envelopes",
        "future_envelopes",
        "all_envelopes",
        "unknown",
    }
)

BLIND_ROLES = frozenset({"blind_solver"})
SOLUTION_TYPES = frozenset({"solution", "answer_key"})
BLIND_DENIED_TYPES = frozenset(
    {"solution", "answer_key", "facilitator_guide", "review_report", "playtest_report", "learning_record"}
)
PLAYTEST_STAGES = frozenset({"playtest_analysis", "learning_review"})
TECHNICAL_TYPES = frozenset({"schema", "template", "render_output", "manifest"})
REVIEWER_ROLES = frozenset(
    {
        "logic_reviewer",
        "narrative_reviewer",
        "evidence_reviewer",
        "visual_reviewer",
        "accessibility_reviewer",
        "adversarial_reviewer",
        "technical_reviewer",
    }
)


@dataclass(frozen=True)
class ArtifactVisibilityInput:
    """Metadata required to decide whether a role may receive one artifact."""

    role: str
    stage: str
    artifact_id: str
    artifact_type: str
    visibility: str
    envelope_scope: str
    contains_solution: bool = False
    contains_future_envelopes: bool = False
    contains_private_author_notes: bool = False
    contains_other_agents_outputs: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    """One explicit policy result with stable reason and rule identifier."""

    allowed: bool
    severity: Severity
    rule_id: str
    reason: str
    recommended_action: str
    matched_conditions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyReport:
    """Aggregate policy result for an artifact or manifest."""

    decisions: tuple[PolicyDecision, ...]

    @property
    def allowed(self) -> bool:
        return self.denied_count == 0

    @property
    def denied_count(self) -> int:
        return sum(1 for decision in self.decisions if decision.severity == "deny")

    @property
    def warning_count(self) -> int:
        return sum(1 for decision in self.decisions if decision.severity == "warn")


def _decision(
    severity: Severity,
    rule_id: str,
    reason: str,
    recommended_action: str,
    matched_conditions: list[str] | None = None,
) -> PolicyDecision:
    return PolicyDecision(
        allowed=severity != "deny",
        severity=severity,
        rule_id=rule_id,
        reason=reason,
        recommended_action=recommended_action,
        matched_conditions=matched_conditions or [],
    )


def _report(decision: PolicyDecision) -> PolicyReport:
    return PolicyReport(decisions=(decision,))


def evaluate_artifact_visibility(artifact: ArtifactVisibilityInput) -> PolicyReport:
    """Evaluate one artifact visibility decision from structured metadata only."""

    unknown = _unknown_value_decision(artifact)
    if unknown is not None:
        return _report(unknown)

    if artifact.stage == "blind_solve" and artifact.role != "blind_solver":
        return _report(
            _decision(
                "deny",
                "VIS_DENY_STAGE_ROLE_MISMATCH",
                "Only the blind solver role is explicitly compatible with blind_solve stage artifacts.",
                "Move this review to the role-specific stage or prepare a separate non-blind bundle.",
                ["stage=blind_solve", f"role={artifact.role}"],
            )
        )

    if artifact.role in BLIND_ROLES:
        return _report(_evaluate_blind_solver(artifact))
    if artifact.role == "logic_reviewer":
        return _report(_evaluate_logic_reviewer(artifact))
    if artifact.role == "narrative_reviewer":
        return _report(_evaluate_narrative_reviewer(artifact))
    if artifact.role == "evidence_reviewer":
        return _report(_evaluate_evidence_reviewer(artifact))
    if artifact.role == "visual_reviewer":
        return _report(_evaluate_visual_reviewer(artifact))
    if artifact.role == "accessibility_reviewer":
        return _report(_evaluate_accessibility_reviewer(artifact))
    if artifact.role == "adversarial_reviewer":
        return _report(_evaluate_adversarial_reviewer(artifact))
    if artifact.role == "gate_evaluator":
        return _report(_evaluate_gate_evaluator(artifact))
    if artifact.role == "facilitator":
        return _report(_evaluate_facilitator(artifact))
    if artifact.role == "human_operator":
        return _report(_evaluate_human_operator(artifact))
    if artifact.role == "technical_reviewer":
        return _report(_evaluate_technical_reviewer(artifact))

    return _report(
        _decision(
            "deny",
            "VIS_DENY_UNKNOWN_ROLE",
            "The role is not recognized by the artifact visibility policy.",
            "Use a role declared by the blind bundle manifest schema.",
            [f"role={artifact.role}"],
        )
    )


def evaluate_manifest_visibility(manifest: dict[str, Any]) -> PolicyReport:
    """Evaluate included_artifacts from an already-loaded manifest dictionary.

    The caller is responsible for schema validation and YAML loading. This function
    consumes only the provided dictionary and does not read files, compute hashes,
    or inspect artifact contents.
    """

    role = str(manifest.get("role", ""))
    stage = str(manifest.get("stage", ""))
    visibility_policy = manifest.get("visibility_policy") or {}
    included_artifacts = manifest.get("included_artifacts") or []

    decisions: list[PolicyDecision] = []
    for artifact in included_artifacts:
        input_data = ArtifactVisibilityInput(
            role=role,
            stage=stage,
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_type=str(artifact.get("artifact_type", "")),
            visibility=str(artifact.get("visibility", "")),
            envelope_scope=str(artifact.get("envelope_scope", "")),
            contains_solution=bool(
                visibility_policy.get("contains_solution", False) or artifact.get("contains_solution", False)
            ),
            contains_future_envelopes=bool(
                visibility_policy.get("contains_future_envelopes", False)
                or artifact.get("contains_future_envelopes", False)
            ),
            contains_private_author_notes=bool(
                visibility_policy.get("contains_private_author_notes", False)
                or artifact.get("contains_private_author_notes", False)
            ),
            contains_other_agents_outputs=bool(
                visibility_policy.get("contains_other_agents_outputs", False)
                or artifact.get("contains_other_agents_outputs", False)
            ),
        )
        decisions.extend(evaluate_artifact_visibility(input_data).decisions)

    if not decisions:
        decisions.append(
            _decision(
                "deny",
                "VIS_DENY_EMPTY_MANIFEST_ARTIFACTS",
                "The manifest has no included artifacts to evaluate.",
                "Provide at least one included_artifacts entry before evaluating visibility.",
                ["included_artifacts=empty"],
            )
        )

    return PolicyReport(decisions=tuple(decisions))


def _unknown_value_decision(artifact: ArtifactVisibilityInput) -> PolicyDecision | None:
    if artifact.role not in ROLES:
        return _decision(
            "deny",
            "VIS_DENY_UNKNOWN_ROLE",
            "The role is not recognized by the artifact visibility policy.",
            "Use a role declared by the blind bundle manifest schema.",
            [f"role={artifact.role}"],
        )
    if artifact.stage not in STAGES:
        return _decision(
            "deny",
            "VIS_DENY_UNKNOWN_STAGE",
            "The stage is not recognized by the artifact visibility policy.",
            "Use a stage declared by the blind bundle manifest schema.",
            [f"stage={artifact.stage}"],
        )
    if artifact.visibility not in VISIBILITY_CATEGORIES:
        return _decision(
            "deny",
            "VIS_DENY_UNKNOWN_VISIBILITY",
            "The visibility category is not recognized by the artifact visibility policy.",
            "Use a visibility category declared by the blind bundle manifest schema.",
            [f"visibility={artifact.visibility}"],
        )
    if artifact.artifact_type not in ARTIFACT_TYPES:
        return _decision(
            "deny",
            "VIS_DENY_UNKNOWN_ARTIFACT_TYPE",
            "The artifact type is not recognized by the artifact visibility policy.",
            "Use an artifact_type declared by the blind bundle manifest schema.",
            [f"artifact_type={artifact.artifact_type}"],
        )
    if artifact.envelope_scope not in ENVELOPE_SCOPES:
        return _decision(
            "deny",
            "VIS_DENY_UNKNOWN_ENVELOPE_SCOPE",
            "The envelope scope is not recognized by the artifact visibility policy.",
            "Use an envelope_scope declared by the blind bundle manifest schema.",
            [f"envelope_scope={artifact.envelope_scope}"],
        )
    return None


def _has_sensitive_flag(artifact: ArtifactVisibilityInput) -> bool:
    return any(
        (
            artifact.contains_solution,
            artifact.contains_future_envelopes,
            artifact.contains_private_author_notes,
            artifact.contains_other_agents_outputs,
        )
    )


def _sensitive_conditions(artifact: ArtifactVisibilityInput) -> list[str]:
    conditions: list[str] = []
    if artifact.contains_solution:
        conditions.append("contains_solution=true")
    if artifact.contains_future_envelopes:
        conditions.append("contains_future_envelopes=true")
    if artifact.contains_private_author_notes:
        conditions.append("contains_private_author_notes=true")
    if artifact.contains_other_agents_outputs:
        conditions.append("contains_other_agents_outputs=true")
    return conditions


def _deny_default(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    return _decision(
        "deny",
        "VIS_DENY_CONSERVATIVE_DEFAULT",
        "No explicit allow rule matched this role, stage, artifact type, visibility, and envelope scope.",
        "Create a more specific sanitized artifact or route it to an authorized role.",
        [
            f"role={artifact.role}",
            f"stage={artifact.stage}",
            f"artifact_type={artifact.artifact_type}",
            f"visibility={artifact.visibility}",
            f"envelope_scope={artifact.envelope_scope}",
        ],
    )


def _allow(rule_id: str, reason: str, artifact: ArtifactVisibilityInput) -> PolicyDecision:
    return _decision(
        "allow",
        rule_id,
        reason,
        "Include the artifact with the declared metadata.",
        [
            f"role={artifact.role}",
            f"stage={artifact.stage}",
            f"artifact_type={artifact.artifact_type}",
            f"visibility={artifact.visibility}",
        ],
    )


def _warn(rule_id: str, reason: str, action: str, artifact: ArtifactVisibilityInput) -> PolicyDecision:
    return _decision(
        "warn",
        rule_id,
        reason,
        action,
        [
            f"role={artifact.role}",
            f"stage={artifact.stage}",
            f"artifact_type={artifact.artifact_type}",
            f"visibility={artifact.visibility}",
        ]
        + _sensitive_conditions(artifact),
    )


def _evaluate_blind_solver(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    if _has_sensitive_flag(artifact):
        return _decision(
            "deny",
            "VIS_DENY_BLIND_SENSITIVE_FLAG",
            "Blind solver artifacts cannot include solution, future envelope, private note, or other-agent-output flags.",
            "Remove the sensitive material or prepare a sanitized public/derived artifact.",
            _sensitive_conditions(artifact),
        )
    if artifact.artifact_type in {"solution", "answer_key"}:
        return _decision(
            "deny",
            "VIS_DENY_BLIND_SOLUTION",
            "Blind solver cannot receive solution or answer key artifacts.",
            "Exclude this artifact from blind bundles.",
            [f"artifact_type={artifact.artifact_type}"],
        )
    if artifact.envelope_scope == "future_envelopes":
        return _decision(
            "deny",
            "VIS_DENY_BLIND_FUTURE_ENVELOPE",
            "Blind solver cannot receive future envelope material.",
            "Restrict the bundle to current, previous, or scope-free artifacts.",
            ["envelope_scope=future_envelopes"],
        )
    if artifact.visibility == "private_author":
        return _decision(
            "deny",
            "VIS_DENY_BLIND_PRIVATE_AUTHOR",
            "Blind solver cannot receive private author material.",
            "Exclude private author artifacts or create a sanitized public player version.",
            ["visibility=private_author"],
        )
    if artifact.visibility == "facilitator" or artifact.artifact_type == "facilitator_guide":
        return _decision(
            "deny",
            "VIS_DENY_BLIND_FACILITATOR",
            "Blind solver cannot receive facilitator-only material.",
            "Exclude facilitator-only artifacts from blind bundles.",
            [f"visibility={artifact.visibility}", f"artifact_type={artifact.artifact_type}"],
        )
    if artifact.visibility == "review_private" or artifact.artifact_type == "review_report":
        return _decision(
            "deny",
            "VIS_DENY_BLIND_REVIEW_PRIVATE",
            "Blind solver cannot receive private review outputs before or during blind solving.",
            "Route review outputs only after blind solving is complete and never into the blind bundle.",
            [f"visibility={artifact.visibility}", f"artifact_type={artifact.artifact_type}"],
        )
    if artifact.visibility in {"playtest_anonymized", "technical_metadata"}:
        return _decision(
            "deny",
            "VIS_DENY_BLIND_NON_PLAYER_VISIBILITY",
            "Blind solver receives player-safe or sanitized derived material only.",
            "Remove technical/playtest material or convert it into a sanitized derived report if appropriate.",
            [f"visibility={artifact.visibility}"],
        )
    if artifact.artifact_type in {"playtest_report", "learning_record"}:
        return _decision(
            "deny",
            "VIS_DENY_BLIND_REVIEW_PRIVATE",
            "Blind solver cannot receive playtest, learning, or review reports.",
            "Exclude analytical reports from blind bundles.",
            [f"artifact_type={artifact.artifact_type}"],
        )
    if artifact.visibility == "derived_report":
        if artifact.artifact_type in {"review_report", "learning_record", "solution", "answer_key"}:
            return _decision(
                "deny",
                "VIS_DENY_BLIND_REVIEW_PRIVATE",
                "Derived reports for blind solver cannot be solution, answer key, review, or learning artifacts.",
                "Create a sanitized derived report without private reasoning or solution content.",
                [f"artifact_type={artifact.artifact_type}", "visibility=derived_report"],
            )
        return _allow("VIS_ALLOW_DERIVED_REPORT", "Blind solver may receive sanitized derived reports without sensitive flags.", artifact)
    if artifact.visibility == "public_player" and artifact.envelope_scope in {"none", "current_envelope", "previous_envelopes"}:
        if artifact.artifact_type in {"player_document", "clue", "map", "envelope_cover", "case_blueprint", "manifest", "other"}:
            return _allow("VIS_ALLOW_PUBLIC_PLAYER", "Blind solver may receive safe public-player artifacts.", artifact)
    return _deny_default(artifact)


def _deny_playtest_outside_stage(artifact: ArtifactVisibilityInput) -> PolicyDecision | None:
    if artifact.visibility == "playtest_anonymized" and artifact.stage not in PLAYTEST_STAGES:
        return _decision(
            "deny",
            "VIS_DENY_PLAYTEST_DATA_OUTSIDE_ANALYSIS",
            "Playtest anonymized material is limited to playtest analysis or learning review stages.",
            "Move the artifact to playtest_analysis/learning_review or exclude it.",
            [f"stage={artifact.stage}", "visibility=playtest_anonymized"],
        )
    return None


def _reviewer_sensitive_warning(artifact: ArtifactVisibilityInput) -> PolicyDecision | None:
    if _has_sensitive_flag(artifact):
        return _warn(
            "VIS_WARN_REVIEWER_SENSITIVE_FLAG",
            "Reviewer artifact contains sensitive flags and should be handled as private review material.",
            "Confirm the reviewer role needs this sensitive metadata and keep it out of blind bundles.",
            artifact,
        )
    return None


def _evaluate_logic_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _warn(
            "VIS_WARN_REVIEWER_SOLUTION",
            "Logic reviewer may need solution material to validate puzzle consistency, but it remains private.",
            "Confirm this review is non-blind and keep the artifact out of blind bundles.",
            artifact,
        )
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.visibility in {"public_player", "review_private", "derived_report", "technical_metadata"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Logic reviewer may receive public, review-private, derived, or technical material.", artifact)
    if artifact.visibility == "private_author" and artifact.stage in {"preflight_review", "gate_evaluation"}:
        return _allow("VIS_ALLOW_PRIVATE_AUTHOR_REVIEW", "Logic reviewer may receive private author material in preflight or gate evaluation.", artifact)
    if artifact.visibility == "facilitator" and artifact.stage == "gate_evaluation":
        return _allow("VIS_ALLOW_FACILITATOR_REVIEW", "Logic reviewer may receive facilitator material during gate evaluation.", artifact)
    if artifact.visibility == "facilitator" and artifact.artifact_type not in SOLUTION_TYPES:
        return _allow("VIS_ALLOW_FACILITATOR_REVIEW", "Logic reviewer may receive non-solution facilitator context for review.", artifact)
    return _deny_default(artifact)


def _evaluate_narrative_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _warn(
            "VIS_WARN_REVIEWER_SOLUTION",
            "Narrative reviewer may inspect solution material only as private review context.",
            "Confirm this review is non-blind and keep the artifact out of blind bundles.",
            artifact,
        )
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.visibility in {"public_player", "review_private", "derived_report"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Narrative reviewer may receive public, review-private, or derived material.", artifact)
    if artifact.visibility == "private_author" and artifact.stage in {"narrative_review", "preflight_review"}:
        return _allow("VIS_ALLOW_PRIVATE_AUTHOR_REVIEW", "Narrative reviewer may receive private author notes in narrative or preflight review.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage in PLAYTEST_STAGES:
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Narrative reviewer may receive anonymized playtest material during analysis/learning.", artifact)
    return _deny_default(artifact)


def _evaluate_evidence_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _warn("VIS_WARN_REVIEWER_SOLUTION", "Evidence reviewer may need solution context to verify evidentiary sufficiency.", "Confirm the review is non-blind.", artifact)
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.visibility == "facilitator":
        return _warn("VIS_WARN_REVIEWER_FACILITATOR", "Facilitator material can be relevant to evidence review but should remain private.", "Confirm necessity before including facilitator material.", artifact)
    if artifact.visibility in {"public_player", "review_private", "derived_report", "private_author"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Evidence reviewer may receive player, review, derived, or private author material.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage in PLAYTEST_STAGES:
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Evidence reviewer may receive anonymized playtest material during analysis/learning.", artifact)
    return _deny_default(artifact)


def _evaluate_visual_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _decision("deny", "VIS_DENY_REVIEWER_SOLUTION", "Visual reviewer does not receive solution or answer key artifacts by default.", "Route solution validation to gate evaluator or authorized private reviewer.", [f"artifact_type={artifact.artifact_type}"])
    if artifact.visibility == "private_author" and artifact.stage not in {"visual_review", "preflight_review"}:
        return _decision("deny", "VIS_DENY_PRIVATE_AUTHOR_OUTSIDE_STAGE", "Visual reviewer receives private author material only in visual or preflight review.", "Move the artifact to visual_review/preflight_review or exclude it.", [f"stage={artifact.stage}"])
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.artifact_type in {"render_output", "template"} or artifact.visibility == "technical_metadata":
        return _allow("VIS_ALLOW_TECHNICAL_METADATA", "Visual reviewer may receive render outputs, templates, and technical metadata.", artifact)
    if artifact.visibility in {"public_player", "derived_report", "review_private"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Visual reviewer may receive player-facing, derived, or layout review material.", artifact)
    if artifact.visibility == "private_author" and artifact.stage in {"visual_review", "preflight_review"}:
        return _allow("VIS_ALLOW_PRIVATE_AUTHOR_REVIEW", "Visual reviewer may receive private author context in visual/preflight review.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage == "playtest_analysis":
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Visual reviewer may receive anonymized playtest material during playtest analysis.", artifact)
    return _deny_default(artifact)


def _evaluate_accessibility_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _decision("deny", "VIS_DENY_REVIEWER_SOLUTION", "Accessibility reviewer does not receive solution or answer key artifacts.", "Route solution validation to gate evaluator.", [f"artifact_type={artifact.artifact_type}"])
    if artifact.visibility == "private_author":
        return _decision("deny", "VIS_DENY_PRIVATE_AUTHOR_OUTSIDE_STAGE", "Accessibility reviewer has no current private-author access rule.", "Use public/rendered/technical artifacts unless a future policy expands access.", ["visibility=private_author"])
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.artifact_type in {"render_output", "template"} or artifact.visibility == "technical_metadata":
        return _allow("VIS_ALLOW_TECHNICAL_METADATA", "Accessibility reviewer may receive render outputs, templates, and technical metadata.", artifact)
    if artifact.visibility in {"public_player", "derived_report"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Accessibility reviewer may receive player-facing and derived material.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage == "playtest_analysis":
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Accessibility reviewer may receive anonymized playtest material during playtest analysis.", artifact)
    return _deny_default(artifact)


def _evaluate_adversarial_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES:
        return _warn("VIS_WARN_REVIEWER_SOLUTION", "Adversarial reviewer may inspect solution artifacts as private non-blind review material.", "Confirm the role is not operating as blind_solver.", artifact)
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.visibility in {"public_player", "review_private", "private_author", "derived_report"}:
        return _allow("VIS_ALLOW_REVIEWER_PRIVATE", "Adversarial reviewer may receive public, private review, author, or derived material.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage in PLAYTEST_STAGES:
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Adversarial reviewer may receive anonymized playtest material during analysis/learning.", artifact)
    return _deny_default(artifact)


def _evaluate_gate_evaluator(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    if artifact.visibility == "playtest_anonymized" and artifact.stage not in {"playtest_analysis", "learning_review", "gate_evaluation"}:
        return _decision("deny", "VIS_DENY_PLAYTEST_DATA_OUTSIDE_ANALYSIS", "Gate evaluator receives anonymized playtest data only in playtest, learning, or gate evaluation stages.", "Move the artifact to a compatible stage or exclude it.", [f"stage={artifact.stage}"])
    if artifact.artifact_type in SOLUTION_TYPES:
        return _allow("VIS_ALLOW_GATE_EVALUATOR_SOLUTION", "Gate evaluator is authorized to inspect solution and answer key artifacts.", artifact)
    if artifact.artifact_type == "learning_record":
        return _allow("VIS_ALLOW_GATE_EVALUATOR_LEARNING", "Gate evaluator may receive learning records for final evaluation.", artifact)
    if _has_sensitive_flag(artifact):
        return _allow("VIS_ALLOW_GATE_EVALUATOR_SENSITIVE", "Gate evaluator may receive sensitive private metadata required for final checks.", artifact)
    if artifact.visibility in {"public_player", "review_private", "facilitator", "derived_report", "private_author"}:
        return _allow("VIS_ALLOW_GATE_EVALUATOR_PRIVATE", "Gate evaluator may receive public, private, facilitator, and derived artifacts.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage in {"playtest_analysis", "learning_review", "gate_evaluation"}:
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Gate evaluator may receive anonymized playtest data in compatible stages.", artifact)
    return _deny_default(artifact)


def _evaluate_facilitator(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    if artifact.contains_other_agents_outputs and artifact.visibility != "derived_report":
        return _decision("deny", "VIS_DENY_OTHER_AGENTS_OUTPUTS", "Facilitator artifacts cannot include other agents' outputs unless packaged as a derived report.", "Use derived_report visibility or exclude other-agent outputs.", ["contains_other_agents_outputs=true"])
    if artifact.visibility == "private_author" and artifact.stage not in {"gate_evaluation", "preflight_review"}:
        return _decision("deny", "VIS_DENY_PRIVATE_AUTHOR_OUTSIDE_STAGE", "Facilitator receives private author material only during preflight or gate evaluation.", "Move the artifact to a compatible stage or exclude it.", [f"stage={artifact.stage}"])
    if artifact.artifact_type in SOLUTION_TYPES:
        return _allow("VIS_ALLOW_FACILITATOR_SOLUTION", "Facilitator may receive solution and answer key material.", artifact)
    if artifact.visibility in {"public_player", "facilitator", "derived_report"}:
        return _allow("VIS_ALLOW_FACILITATOR", "Facilitator may receive public, facilitator, and derived artifacts.", artifact)
    if artifact.visibility == "private_author" and artifact.stage in {"gate_evaluation", "preflight_review"}:
        return _allow("VIS_ALLOW_PRIVATE_AUTHOR_REVIEW", "Facilitator may receive private author context in preflight/gate evaluation.", artifact)
    return _deny_default(artifact)


def _evaluate_human_operator(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    if artifact.visibility in {"private_author", "playtest_anonymized"} or artifact.artifact_type in SOLUTION_TYPES or _has_sensitive_flag(artifact):
        return _warn(
            "VIS_WARN_HUMAN_OPERATOR_PRIVATE",
            "Human operator can structurally orchestrate this artifact, but it contains private or sensitive material.",
            "Handle manually, avoid blind reasoning, and keep this out of blind solver bundles.",
            artifact,
        )
    return _allow("VIS_ALLOW_HUMAN_OPERATOR", "Human operator may structurally handle artifacts for orchestration.", artifact)


def _evaluate_technical_reviewer(artifact: ArtifactVisibilityInput) -> PolicyDecision:
    playtest_denial = _deny_playtest_outside_stage(artifact)
    if playtest_denial is not None:
        return playtest_denial
    if artifact.artifact_type in SOLUTION_TYPES and artifact.stage != "technical_validation":
        return _decision("deny", "VIS_DENY_REVIEWER_SOLUTION", "Technical reviewer receives solution artifacts only when technical validation requires it.", "Move to technical_validation or route to gate evaluator.", [f"stage={artifact.stage}"])
    if artifact.artifact_type in SOLUTION_TYPES and artifact.stage == "technical_validation":
        return _warn("VIS_WARN_REVIEWER_SOLUTION", "Technical reviewer may inspect solution artifacts during technical validation only.", "Confirm technical necessity and keep it private.", artifact)
    sensitive_warning = _reviewer_sensitive_warning(artifact)
    if sensitive_warning is not None:
        return sensitive_warning
    if artifact.visibility == "technical_metadata" or artifact.artifact_type in TECHNICAL_TYPES:
        return _allow("VIS_ALLOW_TECHNICAL_METADATA", "Technical reviewer may receive technical metadata, schemas, templates, render outputs, and manifests.", artifact)
    if artifact.visibility == "derived_report":
        return _allow("VIS_ALLOW_DERIVED_REPORT", "Technical reviewer may receive derived reports.", artifact)
    if artifact.visibility == "playtest_anonymized" and artifact.stage in PLAYTEST_STAGES:
        return _allow("VIS_ALLOW_PLAYTEST_ANALYSIS", "Technical reviewer may receive anonymized playtest data during analysis/learning.", artifact)
    return _deny_default(artifact)

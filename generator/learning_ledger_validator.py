"""Deterministic semantic validator for Learning Ledger directories."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATHS = {
    "session": ROOT / "schemas" / "playtest_session.schema.yaml",
    "finding": ROOT / "schemas" / "playtest_finding.schema.yaml",
    "decision": ROOT / "schemas" / "learning_decision.schema.yaml",
}
TYPE_DIRS = {"sessions": "session", "findings": "finding", "decisions": "decision"}
ID_FIELDS = {
    "session": "session_id",
    "finding": "finding_id",
    "decision": "learning_decision_id",
}
COUNT_KEYS = {"session": "sessions", "finding": "findings", "decision": "decisions"}
ALLOWED_NON_YAML = {"README.md", ".gitkeep"}


@dataclass(frozen=True)
class LedgerIssue:
    code: str
    message: str
    file_path: str
    entity_type: str
    entity_id: str | None = None
    field_path: str | None = None
    related_id: str | None = None

    def sort_key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.file_path,
            self.entity_type,
            self.entity_id or "",
            self.code,
            self.field_path or "",
            self.message,
        )


@dataclass(frozen=True)
class LedgerValidationReport:
    valid: bool
    errors: list[LedgerIssue]
    warnings: list[LedgerIssue]
    entity_counts: dict[str, int]
    processed_files: list[str]
    schema_invalid_files: list[str]
    semantic_invalid_entities: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [asdict(error) for error in self.errors],
            "warnings": [asdict(warning) for warning in self.warnings],
            "entity_counts": dict(self.entity_counts),
            "processed_files": list(self.processed_files),
            "schema_invalid_files": list(self.schema_invalid_files),
            "semantic_invalid_entities": list(self.semantic_invalid_entities),
        }


@dataclass(frozen=True)
class LoadedEntity:
    entity_type: str
    entity_id: str
    file_path: str
    absolute_path: Path
    data: dict[str, Any]


class LearningLedgerValidator:
    """Validate a Learning Ledger root without mutating input files."""

    def __init__(self, ledger_path: Path | str):
        self.ledger_path = Path(ledger_path)
        self.errors: list[LedgerIssue] = []
        self.warnings: list[LedgerIssue] = []
        self.processed_files: list[str] = []
        self.schema_invalid_files: list[str] = []
        self.entities: dict[str, list[LoadedEntity]] = {"session": [], "finding": [], "decision": []}
        self.indexes: dict[str, dict[str, LoadedEntity]] = {"session": {}, "finding": {}, "decision": {}}
        self.duplicate_ids: dict[str, set[str]] = {"session": set(), "finding": set(), "decision": set()}
        self._validators = self._load_schema_validators()

    def validate(self) -> LedgerValidationReport:
        if not self.ledger_path.exists():
            raise FileNotFoundError(f"Learning ledger directory does not exist: {self.ledger_path}")
        if not self.ledger_path.is_dir():
            raise NotADirectoryError(f"Learning ledger path is not a directory: {self.ledger_path}")

        self._load_entities()
        self._index_entities()
        self._validate_sessions()
        self._validate_findings()
        self._validate_decisions()
        self._validate_finding_decision_links()
        self._validate_supersession()
        return self._report()

    def _load_schema_validators(self) -> dict[str, Draft202012Validator]:
        validators = {}
        for entity_type, path in SCHEMA_PATHS.items():
            if not path.exists():
                raise FileNotFoundError(f"Required schema not found: {path}")
            with path.open(encoding="utf-8") as fh:
                schema = yaml.safe_load(fh)
            Draft202012Validator.check_schema(schema)
            validators[entity_type] = Draft202012Validator(schema, format_checker=FormatChecker())
        return validators

    def _load_entities(self) -> None:
        for dirname, entity_type in TYPE_DIRS.items():
            directory = self.ledger_path / dirname
            if not directory.exists():
                continue
            if directory.is_symlink():
                self._add_error("LEDGER_FILE_UNSUPPORTED", "Pasta controlada não pode ser symlink", dirname, entity_type)
                continue
            if not directory.is_dir():
                self._add_error("LEDGER_FILE_UNSUPPORTED", "Caminho controlado não é diretório", dirname, entity_type)
                continue
            for path in sorted(directory.iterdir(), key=lambda p: p.name):
                rel = self._relative(path)
                if path.name.startswith(".") and path.name != ".gitkeep":
                    continue
                if path.name in ALLOWED_NON_YAML:
                    continue
                if path.is_symlink():
                    self._add_error("LEDGER_FILE_UNSUPPORTED", "Symlink não é permitido no ledger", rel, entity_type)
                    continue
                if not path.is_file():
                    self._add_error("LEDGER_FILE_UNSUPPORTED", "Somente arquivos YAML são aceitos", rel, entity_type)
                    continue
                if path.suffix.lower() not in {".yaml", ".yml"}:
                    self._add_error("LEDGER_FILE_UNSUPPORTED", "Extensão não suportada em pasta controlada", rel, entity_type)
                    continue
                self.processed_files.append(rel)
                self._load_file(path, rel, entity_type)

    def _load_file(self, path: Path, rel: str, entity_type: str) -> None:
        try:
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            self.schema_invalid_files.append(rel)
            self._add_error("LEDGER_FILE_INVALID", f"YAML inválido: {exc.__class__.__name__}", rel, entity_type)
            return
        if not isinstance(data, dict):
            self.schema_invalid_files.append(rel)
            self._add_error("LEDGER_FILE_INVALID", "Documento YAML deve ser objeto", rel, entity_type)
            return
        errors = sorted(self._validators[entity_type].iter_errors(data), key=lambda e: list(e.path))
        if errors:
            self.schema_invalid_files.append(rel)
            for error in errors:
                self._add_error(
                    "LEDGER_SCHEMA_INVALID",
                    error.message,
                    rel,
                    entity_type,
                    entity_id=data.get(ID_FIELDS[entity_type]),
                    field_path=self._format_path(list(error.path)),
                )
            return
        entity_id = str(data[ID_FIELDS[entity_type]])
        self.entities[entity_type].append(LoadedEntity(entity_type, entity_id, rel, path, data))

    def _index_entities(self) -> None:
        for entity_type, entities in self.entities.items():
            seen: dict[str, LoadedEntity] = {}
            for entity in entities:
                if entity.entity_id in seen:
                    self.duplicate_ids[entity_type].add(entity.entity_id)
                    first = seen[entity.entity_id]
                    msg = f"ID duplicado também encontrado em {first.file_path}"
                    self._add_error("LEDGER_DUPLICATE_ID", msg, entity.file_path, entity_type, entity.entity_id, ID_FIELDS[entity_type], entity.entity_id)
                    self._add_error("LEDGER_DUPLICATE_ID", f"ID duplicado também encontrado em {entity.file_path}", first.file_path, entity_type, first.entity_id, ID_FIELDS[entity_type], entity.entity_id)
                else:
                    seen[entity.entity_id] = entity
            self.indexes[entity_type] = {eid: ent for eid, ent in seen.items() if eid not in self.duplicate_ids[entity_type]}

    def _validate_sessions(self) -> None:
        for entity in self.entities["session"]:
            if self._is_duplicate(entity):
                continue
            data = entity.data
            self._check_time(entity, data.get("finished_at"), data.get("started_at"), "finished_at", "started_at")
            self._check_time(entity, data.get("updated_at"), data.get("created_at"), "updated_at", "created_at")
            for idx, stage in enumerate(data.get("stages", [])):
                opened = stage.get("opened_at") or stage.get("started_at")
                self._check_time(entity, stage.get("completed_at"), opened, f"stages[{idx}].completed_at", f"stages[{idx}].opened_at")
            participants = self._field_set(entity, data.get("participants", []), "participant_id", "participants", "LEDGER_DUPLICATE_ID")
            stages = self._field_set(entity, data.get("stages", []), "stage_id", "stages", "LEDGER_DUPLICATE_ID")
            events = self._field_set(entity, data.get("events", []), "event_id", "events", "LEDGER_DUPLICATE_ID")
            hypotheses = self._field_set(entity, data.get("hypotheses", []), "hypothesis_id", "hypotheses", "LEDGER_DUPLICATE_ID")
            self._field_set(entity, data.get("stalls", []), "stall_id", "stalls", "LEDGER_DUPLICATE_ID")
            hints = self._field_set(entity, data.get("hints", []), "hint_id", "hints", "LEDGER_DUPLICATE_ID")
            self._unique_values(entity, [s.get("sequence") for s in data.get("stages", [])], "stages[].sequence", "LEDGER_DUPLICATE_ID")
            self._unique_values(entity, [e.get("sequence") for e in data.get("events", [])], "events[].sequence", "LEDGER_DUPLICATE_ID")
            for idx, event in enumerate(data.get("events", [])):
                self._must_exist(entity, event.get("stage_id"), stages, "LEDGER_STAGE_NOT_FOUND", f"events[{idx}].stage_id")
                for pidx, pid in enumerate(event.get("participants", [])):
                    self._must_exist(entity, pid, participants, "LEDGER_PARTICIPANT_NOT_FOUND", f"events[{idx}].participants[{pidx}]")
            for idx, hyp in enumerate(data.get("hypotheses", [])):
                self._must_exist(entity, hyp.get("proposed_at_event"), events, "LEDGER_EVENT_NOT_FOUND", f"hypotheses[{idx}].proposed_at_event")
                self._must_exist(entity, hyp.get("stage_id"), stages, "LEDGER_STAGE_NOT_FOUND", f"hypotheses[{idx}].stage_id")
                for pidx, pid in enumerate(hyp.get("proposed_by", [])):
                    self._must_exist(entity, pid, participants, "LEDGER_PARTICIPANT_NOT_FOUND", f"hypotheses[{idx}].proposed_by[{pidx}]")
                self._must_exist(entity, hyp.get("changed_from"), hypotheses, "LEDGER_HYPOTHESIS_NOT_FOUND", f"hypotheses[{idx}].changed_from")
            for idx, stall in enumerate(data.get("stalls", [])):
                self._must_exist(entity, stall.get("detected_at_event"), events, "LEDGER_EVENT_NOT_FOUND", f"stalls[{idx}].detected_at_event")
                self._must_exist(entity, stall.get("stage_id"), stages, "LEDGER_STAGE_NOT_FOUND", f"stalls[{idx}].stage_id")
                self._must_exist(entity, stall.get("resolved_by_hint_id"), hints, "LEDGER_HINT_NOT_FOUND", f"stalls[{idx}].resolved_by_hint_id")
            for idx, hint in enumerate(data.get("hints", [])):
                self._must_exist(entity, hint.get("requested_at_event"), events, "LEDGER_EVENT_NOT_FOUND", f"hints[{idx}].requested_at_event")
                self._must_exist(entity, hint.get("delivered_at_event"), events, "LEDGER_EVENT_NOT_FOUND", f"hints[{idx}].delivered_at_event")
                self._must_exist(entity, hint.get("stage_id"), stages, "LEDGER_STAGE_NOT_FOUND", f"hints[{idx}].stage_id")
                for pidx, pid in enumerate(hint.get("requested_by", [])):
                    self._must_exist(entity, pid, participants, "LEDGER_PARTICIPANT_NOT_FOUND", f"hints[{idx}].requested_by[{pidx}]")
            for group in ["positive_moments", "confusion_points", "memorable_quotes", "facilitator_observations", "technical_issues"]:
                self._field_set(entity, data.get(group, []), "observation_id", group, "LEDGER_DUPLICATE_ID")
                for idx, obs in enumerate(data.get(group, [])):
                    self._must_exist(entity, obs.get("occurred_at_event"), events, "LEDGER_EVENT_NOT_FOUND", f"{group}[{idx}].occurred_at_event")
            for idx, rating in enumerate(data.get("ratings", {}).get("participant_ratings", [])):
                self._must_exist(entity, rating.get("participant_id"), participants, "LEDGER_PARTICIPANT_NOT_FOUND", f"ratings.participant_ratings[{idx}].participant_id")

    def _validate_findings(self) -> None:
        for entity in self.entities["finding"]:
            if self._is_duplicate(entity):
                continue
            data = entity.data
            self._check_time(entity, data.get("updated_at"), data.get("created_at"), "updated_at", "created_at")
            self._check_time(entity, data.get("resolution", {}).get("resolved_at"), data.get("created_at"), "resolution.resolved_at", "created_at")
            self._check_time(entity, data.get("deferral", {}).get("review_after"), data.get("created_at"), "deferral.review_after", "created_at")
            self._field_set(entity, data.get("evidence", []), "evidence_id", "evidence", "LEDGER_DUPLICATE_ID")
            related_sessions = []
            for idx, sid in enumerate(data.get("source_session_ids", [])):
                session = self.indexes["session"].get(sid)
                if not session:
                    self._add_error("LEDGER_SESSION_NOT_FOUND", "Finding referencia sessão inexistente", entity.file_path, "finding", entity.entity_id, f"source_session_ids[{idx}]", sid)
                    continue
                related_sessions.append(session)
                self._case_match(entity, session, "finding", f"source_session_ids[{idx}]")
            versions = {s.data.get("case_version") for s in related_sessions}
            if len(versions) > 1:
                self._add_error("LEDGER_CASE_VERSION_MISMATCH", "Finding relaciona sessões de versões diferentes", entity.file_path, "finding", entity.entity_id, "source_session_ids")
            declared = set(data.get("source_session_ids", []))
            for idx, ev in enumerate(data.get("evidence", [])):
                sid = ev.get("source_session_id")
                session = self.indexes["session"].get(sid)
                if not session:
                    self._add_error("LEDGER_SESSION_NOT_FOUND", "Evidência referencia sessão inexistente", entity.file_path, "finding", entity.entity_id, f"evidence[{idx}].source_session_id", sid)
                    continue
                if sid not in declared:
                    self._add_error("LEDGER_SESSION_NOT_FOUND", "Evidência usa sessão fora de source_session_ids", entity.file_path, "finding", entity.entity_id, f"evidence[{idx}].source_session_id", sid)
                self._validate_evidence_refs(entity, ev, idx, session)
            reval = data.get("revalidation", {})
            for idx, sid in enumerate(reval.get("completed_session_ids", [])):
                if sid not in self.indexes["session"]:
                    self._add_error("LEDGER_REVALIDATION_SESSION_NOT_FOUND", "Revalidação referencia sessão inexistente", entity.file_path, "finding", entity.entity_id, f"revalidation.completed_session_ids[{idx}]", sid)
            if reval.get("required") is True:
                completed = reval.get("completed_session_ids", [])
                target = reval.get("target_session_count")
                if target is not None and target < len(completed):
                    self._add_error("LEDGER_REVALIDATION_INCONSISTENT", "target_session_count menor que sessões concluídas", entity.file_path, "finding", entity.entity_id, "revalidation.target_session_count")
                if reval.get("result") == "passed" and reval.get("method") == "new_playtest" and not completed:
                    self._add_error("LEDGER_REVALIDATION_INCONSISTENT", "Revalidação aprovada sem sessão concluída", entity.file_path, "finding", entity.entity_id, "revalidation.completed_session_ids")
                if reval.get("result") == "not_required":
                    self._add_error("LEDGER_REVALIDATION_INCONSISTENT", "required true é incompatível com result not_required", entity.file_path, "finding", entity.entity_id, "revalidation.result")
            gate = data.get("gate_effect", {})
            self._validate_gate(entity, gate)

    def _validate_evidence_refs(self, finding: LoadedEntity, evidence: dict[str, Any], idx: int, session: LoadedEntity) -> None:
        data = session.data
        stages = {s.get("stage_id") for s in data.get("stages", [])}
        events = {e.get("event_id") for e in data.get("events", [])}
        participants = {p.get("participant_id") for p in data.get("participants", [])}
        self._must_exist(finding, evidence.get("event_id"), events, "LEDGER_EVENT_NOT_FOUND", f"evidence[{idx}].event_id")
        self._must_exist(finding, evidence.get("stage_id"), stages, "LEDGER_STAGE_NOT_FOUND", f"evidence[{idx}].stage_id")
        for pidx, pid in enumerate(evidence.get("participant_ids", [])):
            self._must_exist(finding, pid, participants, "LEDGER_PARTICIPANT_NOT_FOUND", f"evidence[{idx}].participant_ids[{pidx}]")

    def _validate_decisions(self) -> None:
        for entity in self.entities["decision"]:
            if self._is_duplicate(entity):
                continue
            data = entity.data
            self._check_time(entity, data.get("updated_at"), data.get("created_at"), "updated_at", "created_at")
            self._check_time(entity, data.get("implemented_at"), data.get("decided_at"), "implemented_at", "decided_at")
            self._check_time(entity, data.get("verified_at"), data.get("implemented_at"), "verified_at", "implemented_at")
            self._check_time(entity, data.get("reviewed_at"), data.get("decided_at"), "reviewed_at", "decided_at")
            related_finding_ids = data.get("related_finding_ids", [])
            primary = data.get("primary_finding_id")
            if primary and primary not in related_finding_ids:
                self._add_error("LEDGER_PRIMARY_FINDING_NOT_RELATED", "primary_finding_id não está em related_finding_ids", entity.file_path, "decision", entity.entity_id, "primary_finding_id", primary)
            findings = []
            for idx, fid in enumerate(related_finding_ids):
                finding = self.indexes["finding"].get(fid)
                if not finding:
                    self._add_error("LEDGER_FINDING_NOT_FOUND", "Decisão referencia finding inexistente", entity.file_path, "decision", entity.entity_id, f"related_finding_ids[{idx}]", fid)
                    continue
                findings.append(finding)
                self._case_match(entity, finding, "decision", f"related_finding_ids[{idx}]")
            for idx, sid in enumerate(data.get("related_session_ids", [])):
                if sid not in self.indexes["session"]:
                    self._add_error("LEDGER_SESSION_NOT_FOUND", "Decisão referencia sessão inexistente", entity.file_path, "decision", entity.entity_id, f"related_session_ids[{idx}]", sid)
            summary = data.get("evidence_summary", {})
            if summary.get("finding_count") != len(set(related_finding_ids)):
                self._add_error("LEDGER_FINDING_COUNT_MISMATCH", "finding_count diverge de related_finding_ids únicos", entity.file_path, "decision", entity.entity_id, "evidence_summary.finding_count")
            explicit_sessions = data.get("related_session_ids")
            if explicit_sessions is not None:
                session_count = len(set(explicit_sessions))
            else:
                session_count = len({sid for finding in findings for sid in finding.data.get("source_session_ids", [])})
            if summary.get("session_count") != session_count:
                self._add_error("LEDGER_SESSION_COUNT_MISMATCH", "session_count diverge das sessões relacionadas", entity.file_path, "decision", entity.entity_id, "evidence_summary.session_count")
            if summary.get("independent_groups") is True and summary.get("session_count", 0) < 2:
                self._add_error("LEDGER_SESSION_COUNT_MISMATCH", "independent_groups true exige pelo menos duas sessões", entity.file_path, "decision", entity.entity_id, "evidence_summary.independent_groups")
            basis = data.get("global_evidence_basis")
            if basis:
                if basis.get("multiple_sessions") != (summary.get("session_count", 0) > 1):
                    self._add_error("LEDGER_REVALIDATION_INCONSISTENT", "multiple_sessions diverge de session_count", entity.file_path, "decision", entity.entity_id, "global_evidence_basis.multiple_sessions")
                if basis.get("multiple_cases") is True:
                    self._add_warning("LEDGER_REVALIDATION_INCONSISTENT", "multiple_cases não é comprovável sem catálogo de casos nesta versão", entity.file_path, "decision", entity.entity_id, "global_evidence_basis.multiple_cases")
            reval = data.get("revalidation", {})
            if reval.get("required") is True and reval.get("minimum_sessions") is not None and reval.get("minimum_sessions") < 1:
                self._add_error("LEDGER_REVALIDATION_INCONSISTENT", "minimum_sessions deve ser positivo quando informado", entity.file_path, "decision", entity.entity_id, "revalidation.minimum_sessions")

    def _validate_finding_decision_links(self) -> None:
        decisions_by_finding: dict[str, list[LoadedEntity]] = {}
        for decision in self.entities["decision"]:
            if self._is_duplicate(decision):
                continue
            for fid in decision.data.get("related_finding_ids", []):
                decisions_by_finding.setdefault(fid, []).append(decision)
        for finding in self.entities["finding"]:
            if self._is_duplicate(finding):
                continue
            status = finding.data.get("generalization_status")
            decision_id = finding.data.get("learning_decision_id")
            inbound = decisions_by_finding.get(finding.entity_id, [])
            if status == "pending":
                if decision_id or inbound:
                    self._add_error("LEDGER_GENERALIZATION_STATUS_MISMATCH", "Finding pending não pode estar ligado a decisão", finding.file_path, "finding", finding.entity_id, "generalization_status", decision_id or inbound[0].entity_id)
            elif status == "not_applicable":
                if decision_id or inbound:
                    self._add_error("LEDGER_GENERALIZATION_STATUS_MISMATCH", "Finding not_applicable não pode estar ligado a decisão", finding.file_path, "finding", finding.entity_id, "generalization_status", decision_id or inbound[0].entity_id)
            elif status == "decided":
                decision = self.indexes["decision"].get(decision_id or "")
                if not decision:
                    self._add_error("LEDGER_DECISION_NOT_FOUND", "Finding decided referencia decisão inexistente", finding.file_path, "finding", finding.entity_id, "learning_decision_id", decision_id)
                elif finding.entity_id not in decision.data.get("related_finding_ids", []):
                    self._add_error("LEDGER_GENERALIZATION_STATUS_MISMATCH", "Decisão indicada não referencia o finding", finding.file_path, "finding", finding.entity_id, "learning_decision_id", decision_id)
        for decision in self.entities["decision"]:
            if self._is_duplicate(decision):
                continue
            for idx, fid in enumerate(decision.data.get("related_finding_ids", [])):
                finding = self.indexes["finding"].get(fid)
                if not finding:
                    continue
                if finding.data.get("generalization_status") != "decided" or finding.data.get("learning_decision_id") != decision.entity_id:
                    self._add_error("LEDGER_GENERALIZATION_STATUS_MISMATCH", "Ligação decisão↔finding não é recíproca", decision.file_path, "decision", decision.entity_id, f"related_finding_ids[{idx}]", fid)

    def _validate_supersession(self) -> None:
        graph: dict[str, str] = {}
        for decision in self.entities["decision"]:
            if self._is_duplicate(decision):
                continue
            did = decision.entity_id
            supersedes = decision.data.get("supersedes_decision_id")
            superseded_by = decision.data.get("superseded_by_decision_id")
            if supersedes:
                if supersedes == did:
                    self._add_error("LEDGER_SUPERSEDES_SELF", "Decisão não pode superseder a si mesma", decision.file_path, "decision", did, "supersedes_decision_id", supersedes)
                elif supersedes not in self.indexes["decision"]:
                    self._add_error("LEDGER_SUPERSEDES_NOT_FOUND", "supersedes_decision_id inexistente", decision.file_path, "decision", did, "supersedes_decision_id", supersedes)
                else:
                    graph[did] = supersedes
                    other = self.indexes["decision"][supersedes]
                    if other.data.get("superseded_by_decision_id") and other.data.get("superseded_by_decision_id") != did:
                        self._add_error("LEDGER_STATUS_TRANSITION_INVALID", "Supersessão não recíproca", decision.file_path, "decision", did, "supersedes_decision_id", supersedes)
            if superseded_by:
                if superseded_by == did:
                    self._add_error("LEDGER_SUPERSEDES_SELF", "Decisão não pode apontar superseded_by para si", decision.file_path, "decision", did, "superseded_by_decision_id", superseded_by)
                elif superseded_by not in self.indexes["decision"]:
                    self._add_error("LEDGER_SUPERSEDED_BY_NOT_FOUND", "superseded_by_decision_id inexistente", decision.file_path, "decision", did, "superseded_by_decision_id", superseded_by)
                else:
                    other = self.indexes["decision"][superseded_by]
                    if other.data.get("supersedes_decision_id") != did:
                        self._add_error("LEDGER_STATUS_TRANSITION_INVALID", "Supersessão não recíproca", decision.file_path, "decision", did, "superseded_by_decision_id", superseded_by)
        self._detect_cycles(graph)

    def _detect_cycles(self, graph: dict[str, str]) -> None:
        for start in sorted(graph):
            seen: dict[str, int] = {}
            chain: list[str] = []
            node = start
            while node in graph:
                if node in seen:
                    cycle = chain[seen[node]:] + [node]
                    entity = self.indexes["decision"].get(start)
                    if entity:
                        self._add_error("LEDGER_SUPERSESSION_CYCLE", "Ciclo de supersessão: " + " -> ".join(cycle), entity.file_path, "decision", start, "supersedes_decision_id", graph[start])
                    break
                seen[node] = len(chain)
                chain.append(node)
                node = graph[node]

    def _validate_gate(self, entity: LoadedEntity, gate: dict[str, Any]) -> None:
        blocks = gate.get("blocks_gate")
        state = gate.get("suggested_gate_state")
        if blocks is True and state == "PASS":
            self._add_error("LEDGER_GATE_EFFECT_INCONSISTENT", "blocks_gate true contradiz PASS", entity.file_path, entity.entity_type, entity.entity_id, "gate_effect")
        if blocks is False and state == "BLOCK":
            self._add_error("LEDGER_GATE_EFFECT_INCONSISTENT", "BLOCK exige blocks_gate true", entity.file_path, entity.entity_type, entity.entity_id, "gate_effect")
        if blocks is True and state == "none":
            self._add_error("LEDGER_GATE_EFFECT_INCONSISTENT", "none não deve bloquear gate", entity.file_path, entity.entity_type, entity.entity_id, "gate_effect")
        if entity.data.get("severity") == "critical" and blocks is False:
            self._add_warning("LEDGER_GATE_EFFECT_INCONSISTENT", "Finding crítico sem bloqueio de gate requer revisão editorial", entity.file_path, entity.entity_type, entity.entity_id, "gate_effect")

    def _case_match(self, entity: LoadedEntity, related: LoadedEntity, entity_type: str, field_path: str) -> None:
        if entity.data.get("case_id") != related.data.get("case_id"):
            self._add_error("LEDGER_CASE_MISMATCH", "case_id divergente entre entidades relacionadas", entity.file_path, entity_type, entity.entity_id, field_path, related.entity_id)
        if entity.data.get("case_version") != related.data.get("case_version"):
            self._add_error("LEDGER_CASE_VERSION_MISMATCH", "case_version divergente entre entidades relacionadas", entity.file_path, entity_type, entity.entity_id, field_path, related.entity_id)

    def _check_time(self, entity: LoadedEntity, later: str | None, earlier: str | None, later_path: str, earlier_path: str) -> None:
        if not later or not earlier:
            return
        if self._parse_dt(later) < self._parse_dt(earlier):
            self._add_error("LEDGER_TIME_ORDER_INVALID", f"{later_path} não pode preceder {earlier_path}", entity.file_path, entity.entity_type, entity.entity_id, later_path)

    def _parse_dt(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _field_set(self, entity: LoadedEntity, items: list[dict[str, Any]], key: str, base: str, code: str) -> set[str]:
        seen: set[str] = set()
        duplicate_reported: set[str] = set()
        for idx, item in enumerate(items):
            value = item.get(key)
            if value in seen and value not in duplicate_reported:
                duplicate_reported.add(value)
                self._add_error(code, f"Valor duplicado para {key}", entity.file_path, entity.entity_type, entity.entity_id, f"{base}[{idx}].{key}", value)
            seen.add(value)
        return seen

    def _unique_values(self, entity: LoadedEntity, values: list[Any], field_path: str, code: str) -> None:
        seen: set[Any] = set()
        for value in values:
            if value in seen:
                self._add_error(code, f"Valor duplicado em {field_path}", entity.file_path, entity.entity_type, entity.entity_id, field_path, str(value))
                return
            seen.add(value)

    def _must_exist(self, entity: LoadedEntity, value: str | None, allowed: set[str], code: str, field_path: str) -> None:
        if value and value not in allowed:
            self._add_error(code, "Referência inexistente", entity.file_path, entity.entity_type, entity.entity_id, field_path, value)

    def _is_duplicate(self, entity: LoadedEntity) -> bool:
        return entity.entity_id in self.duplicate_ids[entity.entity_type]

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.ledger_path).as_posix()

    def _format_path(self, path: list[Any]) -> str:
        if not path:
            return "$"
        out = ""
        for part in path:
            if isinstance(part, int):
                out += f"[{part}]"
            else:
                out += ("." if out else "") + str(part)
        return out

    def _add_error(self, code: str, message: str, file_path: str, entity_type: str, entity_id: str | None = None, field_path: str | None = None, related_id: str | None = None) -> None:
        self.errors.append(LedgerIssue(code, message, file_path, entity_type, entity_id, field_path, related_id))

    def _add_warning(self, code: str, message: str, file_path: str, entity_type: str, entity_id: str | None = None, field_path: str | None = None, related_id: str | None = None) -> None:
        self.warnings.append(LedgerIssue(code, message, file_path, entity_type, entity_id, field_path, related_id))

    def _report(self) -> LedgerValidationReport:
        errors = sorted(self.errors, key=LedgerIssue.sort_key)
        warnings = sorted(self.warnings, key=LedgerIssue.sort_key)
        semantic_invalid = sorted({e.entity_id for e in errors if e.entity_id})
        return LedgerValidationReport(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            entity_counts={COUNT_KEYS[k]: len(self.indexes[k]) for k in ["session", "finding", "decision"]},
            processed_files=sorted(self.processed_files),
            schema_invalid_files=sorted(set(self.schema_invalid_files)),
            semantic_invalid_entities=semantic_invalid,
        )


def validate_learning_ledger(ledger_path: Path | str) -> LedgerValidationReport:
    """Validate a Learning Ledger directory and return a deterministic report."""

    return LearningLedgerValidator(ledger_path).validate()

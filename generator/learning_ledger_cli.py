"""Manual offline-first CLI for the Learning Ledger."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from generator.learning_ledger_validator import validate_learning_ledger

EXIT_OK = 0
EXIT_OPERATIONAL = 1
EXIT_USAGE = 2

ENTITY_DIRS = {
    "session": "sessions",
    "finding": "findings",
    "decision": "decisions",
}
SCHEMA_PATHS = {
    "session": Path("schemas/playtest_session.schema.yaml"),
    "finding": Path("schemas/playtest_finding.schema.yaml"),
    "decision": Path("schemas/learning_decision.schema.yaml"),
}
NEUTRAL_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,63}$")


class LedgerCliError(Exception):
    """Expected CLI failure with a user-facing message."""


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:  # noqa: ANN401 - PyYAML hook accepts any object.
        return True


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dump_yaml(payload: Any) -> str:  # noqa: ANN401 - payloads are schema-shaped dict/list data.
    return yaml.dump(
        payload,
        Dumper=NoAliasDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(dump_yaml(payload), encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise LedgerCliError(f"Arquivo YAML inválido: {path}")
    return data


@lru_cache(maxsize=None)
def _schema(entity_type: str) -> dict[str, Any]:
    path = SCHEMA_PATHS[entity_type]
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=None)
def _validator(entity_type: str) -> Draft202012Validator:
    return Draft202012Validator(_schema(entity_type), format_checker=FormatChecker())


def _format_error_path(path: Sequence[Any]) -> str:
    if not path:
        return "$"
    out = ""
    for part in path:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += ("." if out else "") + str(part)
    return out


def validate_payload(entity_type: str, payload: dict[str, Any]) -> None:
    errors = sorted(_validator(entity_type).iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        raise LedgerCliError(
            f"Payload {entity_type} inválido em {_format_error_path(first.path)}: {first.message}"
        )


def assert_id(value: str, label: str = "ID") -> None:
    if not NEUTRAL_ID_RE.fullmatch(value):
        raise LedgerCliError(
            f"ID inválido ({label}): use ^[A-Z0-9][A-Z0-9_-]{{1,63}}$ sem barras, pontos, espaços ou minúsculas."
        )


def assert_timestamp(value: str, label: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerCliError(f"{label} deve ser RFC 3339 válido com timezone.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LedgerCliError(f"{label} deve incluir timezone explícito.")


def ensure_structure(ledger: Path, *, create_root: bool) -> Path:
    root = ledger.resolve()
    if not ledger.exists():
        if create_root:
            ledger.mkdir(parents=True)
        else:
            raise LedgerCliError(f"Ledger não existe: {ledger}")
    if not ledger.is_dir():
        raise LedgerCliError(f"--ledger deve apontar para diretório: {ledger}")
    for child in ENTITY_DIRS.values():
        path = ledger / child
        if path.exists() and not path.is_dir():
            raise LedgerCliError(f"Conflito: {path} deveria ser diretório, mas é arquivo.")
        if create_root:
            path.mkdir(exist_ok=True)
    return root


def entity_path(ledger: Path, entity_type: str, entity_id: str) -> Path:
    assert_id(entity_id, f"{entity_type}_id")
    root = ledger.resolve()
    parent = (ledger / ENTITY_DIRS[entity_type]).resolve()
    if root not in (parent, *parent.parents):
        raise LedgerCliError("Caminho de entidade sai do ledger.")
    path = ledger / ENTITY_DIRS[entity_type] / f"{entity_id}.yaml"
    resolved_parent = path.parent.resolve()
    if resolved_parent != parent:
        raise LedgerCliError("Caminho de entidade inválido.")
    return path


def assert_new_file(path: Path) -> None:
    if path.is_symlink():
        raise LedgerCliError(f"Destino é symlink e não será sobrescrito: {path}")
    if path.exists():
        raise LedgerCliError(f"Arquivo de destino já existe: {path}")


def require_valid_ledger(ledger: Path) -> None:
    report = validate_learning_ledger(ledger)
    if not report.valid:
        first = report.errors[0]
        raise LedgerCliError(f"Ledger inválido; corrija antes de escrever. [{first.code}] {first.file_path} {first.message}")


def atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
    assert_new_file(path)
    tmp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as fh:
            tmp_name = fh.name
            fh.write(dump_yaml(payload))
            fh.flush()
            os.fsync(fh.fileno())
        if path.is_symlink() or path.exists():
            raise LedgerCliError(f"Arquivo de destino já existe: {path}")
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name:
            Path(tmp_name).unlink(missing_ok=True)


def rollback_new_file(path: Path) -> None:
    if path.exists() and not path.is_symlink():
        path.unlink()


def replace_two_files_atomically(new_file: Path, new_payload: dict[str, Any], existing_file: Path, existing_payload: dict[str, Any]) -> None:
    assert_new_file(new_file)
    if existing_file.is_symlink():
        raise LedgerCliError(f"Finding é symlink e não será alterado: {existing_file}")
    original = existing_file.read_bytes()
    tmp_paths: list[Path] = []
    replaced_new = False
    replaced_existing = False
    try:
        for path, payload in [(new_file, new_payload), (existing_file, existing_payload)]:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as fh:
                tmp_paths.append(Path(fh.name))
                fh.write(dump_yaml(payload))
                fh.flush()
                os.fsync(fh.fileno())
        if new_file.exists() or new_file.is_symlink():
            raise LedgerCliError(f"Arquivo de destino já existe: {new_file}")
        os.replace(tmp_paths[0], new_file)
        replaced_new = True
        os.replace(tmp_paths[1], existing_file)
        replaced_existing = True
    except Exception:
        if replaced_new and new_file.exists() and not new_file.is_symlink():
            new_file.unlink()
        if replaced_existing or existing_file.exists():
            existing_file.write_bytes(original)
        raise
    finally:
        for tmp in tmp_paths:
            tmp.unlink(missing_ok=True)


def build_session(args: argparse.Namespace) -> dict[str, Any]:
    for value, label in [
        (args.session_id, "session_id"),
        (args.case_id, "case_id"),
        (args.case_version, "case_version"),
        (args.participant_id, "participant_id"),
        (args.stage_id, "stage_id"),
        (args.event_id, "event_id"),
        (args.created_by, "created_by"),
    ]:
        assert_id(value, label)
    assert_timestamp(args.started_at, "started_at")
    assert_timestamp(args.finished_at, "finished_at")
    created_at = args.created_at or now_utc()
    assert_timestamp(created_at, "created_at")
    payload = {
        "schema_version": "1.0",
        "session_id": args.session_id,
        "case_id": args.case_id,
        "case_version": args.case_version,
        "started_at": args.started_at,
        "finished_at": args.finished_at,
        "duration_minutes": args.duration_minutes,
        "session_context": {
            "mode": args.mode,
            "material_format": [args.material_format],
            "location_type": args.location_type,
            "facilitator_present": False,
        },
        "participants": [
            {
                "participant_id": args.participant_id,
                "age_group": "not_informed",
                "mystery_experience": "not_informed",
                "relationship_to_project": "not_informed",
            }
        ],
        "stages": [
            {
                "stage_id": args.stage_id,
                "label": "Registro mínimo criado pela CLI",
                "sequence": 1,
                "opened_at": args.started_at,
                "completion_status": "not_reached",
            }
        ],
        "events": [
            {
                "event_id": args.event_id,
                "sequence": 1,
                "occurred_at": args.started_at,
                "type": "session_started",
                "stage_id": args.stage_id,
                "participants": [args.participant_id],
                "description": "Sessão registrada manualmente pela CLI.",
            }
        ],
        "outcome": {
            "session_status": "partial",
            "final_answer_submitted": False,
            "solution_correctness": "not_submitted",
            "completion_without_facilitator_override": False,
            "ending_reached": False,
        },
        "ratings": {"scale_min": 1, "scale_max": 5, "collected_from": "not_collected"},
        "record_quality": {
            "recorded_live": False,
            "reconstructed_after_session": True,
            "confidence": "medium",
            "missing_information": [],
            "observer_bias_risks": [],
        },
        "privacy": {
            "anonymized": True,
            "consent_to_record_observations": False,
            "consent_to_use_anonymized_quotes": False,
            "contains_personal_data": False,
        },
        "created_at": created_at,
        "created_by": args.created_by,
        "source_type": "live_observation",
    }
    validate_payload("session", payload)
    return payload


def build_finding(args: argparse.Namespace, session: dict[str, Any]) -> dict[str, Any]:
    for value, label in [
        (args.finding_id, "finding_id"),
        (args.case_id, "case_id"),
        (args.case_version, "case_version"),
        (args.source_session_id, "source_session_id"),
        (args.created_by, "created_by"),
    ]:
        assert_id(value, label)
    if session.get("case_id") != args.case_id:
        raise LedgerCliError("case_id do finding diverge da sessão.")
    if session.get("case_version") != args.case_version:
        raise LedgerCliError("case_version do finding diverge da sessão.")
    created_at = args.created_at or now_utc()
    assert_timestamp(created_at, "created_at")
    payload = {
        "schema_version": "1.0",
        "finding_id": args.finding_id,
        "case_id": args.case_id,
        "case_version": args.case_version,
        "source_session_ids": [args.source_session_id],
        "observation": {
            "summary": args.observation,
            "observed_by": [args.created_by],
            "frequency": {"occurrences": 1, "sessions_observed": 1},
        },
        "evidence": [
            {
                "evidence_id": "EVIDENCE-001",
                "type": "facilitator_observation",
                "description": args.evidence,
                "source_session_id": args.source_session_id,
                "strength": "moderate",
            }
        ],
        "causal_hypothesis": {
            "statement": args.causal_hypothesis,
            "confidence": "low",
            "needs_more_evidence": True,
        },
        "category": args.category,
        "severity": args.severity,
        "finding_scope": {"level": "case"},
        "impact": {
            "player_effects": [args.observation],
            "case_effects": [],
            "affected_participant_count": 1,
            "affected_session_count": 1,
            "blocks_progression": False,
            "compromises_fairness": False,
            "compromises_solvability": False,
            "compromises_immersion": False,
            "technical_only": False,
        },
        "rollback": {"required": False, "target": "none"},
        "status": "ACCEPTED",
        "gate_effect": {"blocks_gate": False, "suggested_gate_state": "none"},
        "generalization_status": "pending",
        "created_at": created_at,
        "created_by": args.created_by,
        "action_expected": {"type": "investigation", "description": "Investigar o finding antes de aplicar mudanças."},
        "assigned_to": args.created_by,
    }
    validate_payload("finding", payload)
    return payload


def result_payload(result: str, rationale: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "no_generalization": {
            "no_generalization": {
                "reason": rationale,
                "disposition": "insufficient_evidence",
                "residual_risk": "O problema pode se repetir em outro grupo.",
                "reconsideration_condition": "Reavaliar após nova sessão.",
            }
        },
        "example_only": {
            "example": {
                "summary": rationale,
                "example_reference": "Registro manual criado pela CLI.",
                "caution": "Usar apenas como exemplo qualitativo até haver evidência adicional.",
            }
        },
        "heuristic": {
            "heuristic": {
                "statement": rationale,
                "rationale": rationale,
                "applicability_conditions": ["Quando evidência adicional confirmar o padrão."],
                "strength": "tentative",
                "validation_plan": "Revalidar em novo playtest.",
            }
        },
        "guardrail": {
            "guardrail": {
                "normative_rule": rationale,
                "prohibited_failure": "Aplicação sem evidência suficiente.",
                "applicability_conditions": ["Quando houver evidência suficiente para regra normativa."],
                "severity_if_violated": "medium",
                "enforcement_target": "documentation",
                "validation_plan": "Revisar manualmente antes de aplicar.",
            }
        },
        "validator_candidate": {
            "validator_candidate": {
                "rule_summary": rationale,
                "validation_target": "learning_ledger",
                "detectable_deterministically": False,
                "required_inputs": ["learning ledger"],
                "false_positive_risks": ["Pode capturar falso positivo sem mais evidência."],
                "test_strategy": "Adicionar fixture em PR futura se aprovado.",
            }
        },
        "case_review_candidate": {
            "case_review_candidate": {
                "review_area": "learning-ledger",
                "question_or_check": rationale,
                "target_section": "case_review",
                "applicability_conditions": ["Quando o padrão se repetir."],
                "reviewer_role": "reviewer",
                "examples_needed": True,
                "validation_plan": "Revisar após novos exemplos.",
            }
        },
        "regression_test": {
            "regression_test": {
                "scenario": rationale,
                "failure_prevented": "Regressão do comportamento observado.",
                "test_level": "manual",
                "fixture_strategy": "Criar fixture específica em PR futura.",
                "expected_behavior": "Comportamento aprovado permanece estável.",
                "validation_command": "pytest tests/ -q",
            }
        },
    }
    return copy.deepcopy(defaults[result])


def merge_data_file(base: dict[str, Any], data_file: Path | None) -> dict[str, Any]:
    if data_file is None:
        return base
    extra = load_yaml(data_file)
    protected = {
        "schema_version",
        "learning_decision_id",
        "case_id",
        "case_version",
        "related_finding_ids",
        "primary_finding_id",
        "related_session_ids",
        "evidence_summary",
        "decided_at",
        "decided_by",
        "created_at",
        "created_by",
    }
    forbidden = protected & set(extra)
    if forbidden:
        raise LedgerCliError(f"--data-file não pode sobrescrever campos protegidos: {', '.join(sorted(forbidden))}")
    merged = copy.deepcopy(base)
    merged.update(extra)
    return merged


def build_decision(args: argparse.Namespace, finding: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    for value, label in [
        (args.decision_id, "decision_id"),
        (args.case_id, "case_id"),
        (args.case_version, "case_version"),
        (args.finding_id, "finding_id"),
        (args.decided_by, "decided_by"),
    ]:
        assert_id(value, label)
    if finding.get("generalization_status") != "pending":
        raise LedgerCliError("Finding deve estar com generalization_status pending.")
    if finding.get("case_id") != args.case_id:
        raise LedgerCliError("case_id da decisão diverge do finding.")
    if finding.get("case_version") != args.case_version:
        raise LedgerCliError("case_version da decisão diverge do finding.")
    decided_at = args.decided_at or now_utc()
    assert_timestamp(decided_at, "decided_at")
    related_sessions = sorted(set(finding.get("source_session_ids", [])))
    scope = {
        "level": args.scope,
        "target_ids": [args.case_id],
        "description": "Decisão mínima criada manualmente pela CLI.",
        "applicability_conditions": [],
    }
    base = {
        "schema_version": "1.0",
        "learning_decision_id": args.decision_id,
        "case_id": args.case_id,
        "case_version": args.case_version,
        "related_finding_ids": [args.finding_id],
        "primary_finding_id": args.finding_id,
        "related_session_ids": related_sessions,
        "scope": scope,
        "result": args.result,
        "rationale": {
            "summary": args.rationale,
            "evidence_reviewed": [args.finding_id, *related_sessions],
            "why_this_scope": "A evidência disponível está limitada ao escopo informado.",
            "why_this_result": args.rationale,
            "confidence": "low",
            "alternatives_considered": [],
            "counter_evidence": [],
            "limitations": ["Registro mínimo criado pela CLI."],
        },
        "evidence_summary": {
            "session_count": len(related_sessions),
            "finding_count": 1,
            "repeated_pattern": False,
            "independent_groups": False,
            "evidence_strength": "weak",
            "notes": "Contagens derivadas automaticamente dos vínculos do finding.",
        },
        "implementation_status": "not_planned",
        "decision_risk": {
            "overgeneralization_risk": "high",
            "undergeneralization_risk": "low",
            "notes": "Evita transformar ocorrência isolada em regra ampla sem evidência adicional.",
        },
        "revalidation": {
            "required": True,
            "method": "new_playtest",
            "success_criteria": ["Observar se o padrão se repete em nova sessão."],
            "minimum_sessions": 1,
            "status": "pending",
        },
        "decided_at": decided_at,
        "decided_by": args.decided_by,
        "created_at": decided_at,
        "created_by": args.decided_by,
        "decision_authority": {
            "role": "human_operator",
            "approved_by": [],
            "dissenting_views": [],
            "decision_notes": "Decisão registrada manualmente pela CLI.",
        },
    }
    base.update(result_payload(args.result, args.rationale))
    decision = merge_data_file(base, args.data_file)
    updated_finding = copy.deepcopy(finding)
    updated_finding["generalization_status"] = "decided"
    updated_finding["learning_decision_id"] = args.decision_id
    updated_finding["updated_at"] = decided_at
    updated_finding["updated_by"] = args.decided_by
    validate_payload("decision", decision)
    validate_payload("finding", updated_finding)
    return decision, updated_finding


def cmd_init(args: argparse.Namespace) -> int:
    ensure_structure(args.ledger, create_root=True)
    print(f"Learning Ledger inicializado em: {args.ledger.resolve()}")
    return EXIT_OK


def cmd_create_session(args: argparse.Namespace) -> int:
    # Build first so ID/timestamp errors are reported even if the existing ledger is invalid.
    payload = build_session(args)
    ensure_structure(args.ledger, create_root=False)
    require_valid_ledger(args.ledger)
    path = entity_path(args.ledger, "session", args.session_id)
    assert_new_file(path)
    if args.dry_run:
        print(dump_yaml(payload), end="")
        return EXIT_OK
    atomic_write_yaml(path, payload)
    try:
        require_valid_ledger(args.ledger)
    except Exception:
        rollback_new_file(path)
        raise
    print(f"Sessão criada: {path}")
    return EXIT_OK


def load_entity_by_id(ledger: Path, entity_type: str, entity_id: str) -> dict[str, Any]:
    path = entity_path(ledger, entity_type, entity_id)
    if not path.exists():
        label = {"session": "Sessão", "finding": "Finding", "decision": "Decisão"}[entity_type]
        suffix = "encontrada" if entity_type in {"session", "decision"} else "encontrado"
        raise LedgerCliError(f"{label} não {suffix}: {entity_id}")
    if path.is_symlink():
        raise LedgerCliError(f"Arquivo de entidade é symlink e foi recusado: {path}")
    data = load_yaml(path)
    validate_payload(entity_type, data)
    return data


def cmd_create_finding(args: argparse.Namespace) -> int:
    for value, label in [(args.finding_id, "finding_id"), (args.case_id, "case_id"), (args.case_version, "case_version"), (args.source_session_id, "source_session_id"), (args.created_by, "created_by")]:
        assert_id(value, label)
    ensure_structure(args.ledger, create_root=False)
    require_valid_ledger(args.ledger)
    session = load_entity_by_id(args.ledger, "session", args.source_session_id)
    payload = build_finding(args, session)
    path = entity_path(args.ledger, "finding", args.finding_id)
    assert_new_file(path)
    if args.dry_run:
        print(dump_yaml(payload), end="")
        return EXIT_OK
    atomic_write_yaml(path, payload)
    try:
        require_valid_ledger(args.ledger)
    except Exception:
        rollback_new_file(path)
        raise
    print(f"Finding criado: {path}")
    return EXIT_OK


def cmd_create_decision(args: argparse.Namespace) -> int:
    for value, label in [(args.decision_id, "decision_id"), (args.case_id, "case_id"), (args.case_version, "case_version"), (args.finding_id, "finding_id"), (args.decided_by, "decided_by")]:
        assert_id(value, label)
    ensure_structure(args.ledger, create_root=False)
    require_valid_ledger(args.ledger)
    finding = load_entity_by_id(args.ledger, "finding", args.finding_id)
    finding_path = entity_path(args.ledger, "finding", args.finding_id)
    decision_path = entity_path(args.ledger, "decision", args.decision_id)
    assert_new_file(decision_path)
    # Confirma que todas as sessões derivadas existem e estão válidas antes de construir a decisão.
    for session_id in finding.get("source_session_ids", []):
        load_entity_by_id(args.ledger, "session", session_id)
    decision, updated_finding = build_decision(args, finding)
    if args.dry_run:
        print("# decision")
        print(dump_yaml(decision), end="")
        print("# updated_finding")
        print(dump_yaml(updated_finding), end="")
        return EXIT_OK
    replace_two_files_atomically(decision_path, decision, finding_path, updated_finding)
    try:
        require_valid_ledger(args.ledger)
    except Exception:
        if decision_path.exists() and not decision_path.is_symlink():
            decision_path.unlink()
        write_yaml(finding_path, finding)
        raise
    print(f"Decisão criada: {decision_path}")
    print(f"Finding atualizado: {finding_path}")
    return EXIT_OK


def cmd_validate(args: argparse.Namespace) -> int:
    report = validate_learning_ledger(args.ledger)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("Ledger válido" if report.valid else "Ledger inválido")
        print(f"Sessions: {report.entity_counts['sessions']}")
        print(f"Findings: {report.entity_counts['findings']}")
        print(f"Decisions: {report.entity_counts['decisions']}")
        print(f"Warnings: {len(report.warnings)}")
        for issue in report.errors:
            print(f"[{issue.code}]")
            print(issue.file_path)
            if issue.field_path:
                print(issue.field_path)
            print(issue.message)
    return EXIT_OK if report.valid else EXIT_OPERATIONAL


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI manual e offline para operar o Learning Ledger.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Inicializa a estrutura sessions/findings/decisions.")
    p_init.add_argument("--ledger", type=Path, required=True)
    p_init.set_defaults(func=cmd_init)

    p_session = sub.add_parser("create-session", help="Cria uma sessão mínima válida.")
    p_session.add_argument("--ledger", type=Path, required=True)
    p_session.add_argument("--session-id", required=True)
    p_session.add_argument("--case-id", required=True)
    p_session.add_argument("--case-version", required=True)
    p_session.add_argument("--started-at", required=True)
    p_session.add_argument("--finished-at", required=True)
    p_session.add_argument("--duration-minutes", type=int, required=True)
    p_session.add_argument("--created-by", required=True)
    p_session.add_argument("--participant-id", default="PARTICIPANT-01")
    p_session.add_argument("--stage-id", default="STAGE-01")
    p_session.add_argument("--event-id", default="EVENT-01")
    p_session.add_argument("--mode", default="in_person", choices=["in_person", "remote", "hybrid"])
    p_session.add_argument("--material-format", default="printed", choices=["printed", "mobile", "tablet", "desktop"])
    p_session.add_argument("--location-type", default="home", choices=["home", "office", "event", "school", "other"])
    p_session.add_argument("--created-at")
    p_session.add_argument("--dry-run", action="store_true")
    p_session.set_defaults(func=cmd_create_session)

    p_finding = sub.add_parser("create-finding", help="Cria um finding mínimo válido.")
    p_finding.add_argument("--ledger", type=Path, required=True)
    p_finding.add_argument("--finding-id", required=True)
    p_finding.add_argument("--case-id", required=True)
    p_finding.add_argument("--case-version", required=True)
    p_finding.add_argument("--source-session-id", required=True)
    p_finding.add_argument("--category", required=True)
    p_finding.add_argument("--severity", required=True)
    p_finding.add_argument("--observation", required=True)
    p_finding.add_argument("--evidence", required=True)
    p_finding.add_argument("--causal-hypothesis", required=True)
    p_finding.add_argument("--created-by", required=True)
    p_finding.add_argument("--created-at")
    p_finding.add_argument("--dry-run", action="store_true")
    p_finding.set_defaults(func=cmd_create_finding)

    p_decision = sub.add_parser("create-decision", help="Cria uma decisão e atualiza o finding reciprocamente.")
    p_decision.add_argument("--ledger", type=Path, required=True)
    p_decision.add_argument("--decision-id", required=True)
    p_decision.add_argument("--case-id", required=True)
    p_decision.add_argument("--case-version", required=True)
    p_decision.add_argument("--finding-id", required=True)
    p_decision.add_argument(
        "--result",
        required=True,
        choices=[
            "no_generalization",
            "example_only",
            "heuristic",
            "guardrail",
            "validator_candidate",
            "case_review_candidate",
            "regression_test",
        ],
    )
    p_decision.add_argument("--scope", required=True, choices=["case_only", "mechanic_family", "global_editorial"])
    p_decision.add_argument("--rationale", required=True)
    p_decision.add_argument("--decided-by", required=True)
    p_decision.add_argument("--decided-at")
    p_decision.add_argument("--data-file", type=Path)
    p_decision.add_argument("--dry-run", action="store_true")
    p_decision.set_defaults(func=cmd_create_decision)

    p_validate = sub.add_parser("validate", help="Valida o ledger usando validate_learning_ledger().")
    p_validate.add_argument("--ledger", type=Path, required=True)
    p_validate.add_argument("--format", choices=["human", "json"], default="human")
    p_validate.set_defaults(func=cmd_validate)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return args.func(args)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
    except LedgerCliError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_OPERATIONAL
    except (OSError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_OPERATIONAL


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

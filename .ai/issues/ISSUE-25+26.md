# ISSUE-25+26 — Multiagent Workspace + Manual Orchestrator

## Estado

```
STATUS: draft
CURRENT_STEP: STEP-00
NEXT_ACTION: orchestrate
REVIEW_STATUS: none
LAST_COMPLETED_STEP: none
LAST_EXECUTION_REPORT: none
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

As ISSUE-16–22 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `generator/gate_evaluator.py` — Gate Evaluator com regras GE_001–GE_008
- `generator/narrative_reviewer.py` — Narrative Reviewer com regras NR_001–NR_008
- `generator/evidence_reviewer.py` — Evidence Reviewer com regras ER_001–ER_008
- 1104 testes passando

O que ainda não existe:
- Estrutura de workspace por run que organiza artefatos, logs e estado
- Manual Orchestrator que conduz a run sem LLM, registra ingestões e gates

## Spec completa

Ver `.ai/issues/ISSUE-25+26_SPEC.md`

## Steps

Os steps serão planejados pelo orquestrador no STEP-00. Estrutura esperada:

- STEP-01: reading — leitura de APIs existentes e mapeamento de campos
- STEP-02: baseline — suíte atual antes de qualquer alteração
- STEP-03: red — fixtures + testes de schema (casos 1–10)
- STEP-04: red — testes de schema (casos 11–20)
- STEP-05: green — schema + validate_workspace_run + dataclasses + build + run_to_dict
- STEP-06: red — testes de workspace semântico (casos 21–50)
- STEP-07: green — validate_workspace_semantics (WS_001–WS_008)
- STEP-08: red — testes do manual orchestrator (casos 51–85)
- STEP-09: green — ingest_artifact + record_decision + transition_stage + validate_orchestrator_transition (OR_001–OR_008)
- STEP-10: refactor — helpers compartilhados, dedup de lookups
- STEP-11: validation — suíte completa e checagens finais
- STEP-12: wrap-up — documentação opcional

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Aguardando orquestração inicial.

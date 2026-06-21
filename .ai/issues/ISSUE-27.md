# ISSUE-27 — Run Manifest / Run Summary

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

As ISSUE-16–26 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `generator/gate_evaluator.py` — Gate Evaluator com regras GE_001–GE_008
- `generator/narrative_reviewer.py` — Narrative Reviewer com regras NR_001–NR_008
- `generator/evidence_reviewer.py` — Evidence Reviewer com regras ER_001–ER_008
- `generator/workspace.py` — Workspace com regras WS_001–WS_008
- `generator/manual_orchestrator.py` — Manual Orchestrator com regras OR_001–OR_008
- 1192 testes passando

O que ainda não existe:
- Documento consolidado que captura o resultado completo de uma run
- Schema para esse documento (run_manifest.schema.yaml)
- Builder que deriva pipeline_status, stages_completed, findings e next_steps
  deterministicamente a partir do WorkspaceRun

## Spec completa

Ver `.ai/issues/ISSUE-27_SPEC.md`

## Steps

Os steps serão planejados pelo orquestrador no STEP-00. Estrutura esperada:

- STEP-01: reading — leitura das APIs de workspace.py, manual_orchestrator.py e schemas existentes
- STEP-02: baseline — suíte atual antes de qualquer alteração
- STEP-03: red — fixtures valid/ + testes de schema (casos 1–10)
- STEP-04: red — fixtures invalid/ + testes de schema (casos 11–20)
- STEP-05: green — schema + validate_run_manifest + dataclasses + manifest_to_dict
- STEP-06: red — testes de run_manifest semântico e build (casos 21–55)
- STEP-07: green — validate_run_manifest_semantics (RM_001–RM_008) + build_run_manifest
- STEP-08: refactor — helpers privados de pipeline_status e next_steps; import de VALID_STAGES/VALID_ARTIFACT_TYPES/VALID_OUTCOMES de workspace.py
- STEP-09: validation — suíte completa e checagens finais
- STEP-10: wrap-up — documentação opcional

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Aguardando orquestração inicial.

# ISSUE-28 — Rodar o pipeline completo no caso Hotel Aurora

## Estado

```
STATUS: done
CURRENT_STEP: STEP-12
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-12
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-28/STEP-12_EXECUTION.md
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

As Fases A–G estão completas. Todos os componentes da pipeline multiagente
existem e são testados isoladamente (1248 testes):

- bundle: `generator/blind_bundle_generator.py`
- blind solve: `generator/blind_solver_harness.py` (+ stub determinístico em testes)
- run record: `generator/blind_solve_run_record.py`
- gate: `generator/gate_evaluator.py` (GE_*)
- reviewers: `generator/narrative_reviewer.py` (NR_*) + `generator/evidence_reviewer.py` (ER_*)
- workspace + orchestrator: `generator/workspace.py` (WS_*) + `generator/manual_orchestrator.py` (OR_*)
- manifest: `generator/run_manifest.py` (RM_*)

O que ainda não aconteceu: **nenhuma run ponta-a-ponta sobre um caso real.**
ISSUE-28 é a primeira — aplica a pipeline ao canônico Intermediário
**O Último Brinde do Hotel Aurora** (`examples/caso_canonico_intermediario.json`)
e compara os findings da pipeline com os defeitos documentados no playtest real.

Restrição: ainda não há LLM (Fase I começa na ISSUE-31). O blind solver desta
run é um stub determinístico, offline. O valor real está em (1) provar que a
tubulação encaixa sobre um caso real produzindo artefatos schema-válidos e
(2) rodar os reviewers determinísticos sobre o blueprint do Aurora e cruzar com
o playtest.

Esta issue **desbloqueia ISSUE-23 e ISSUE-24** (Visual + Accessibility Reviewer).

## Spec completa

Ver `.ai/issues/ISSUE-28_SPEC.md`

## Steps

- STEP-01: reading — concluído (auto-approved)
- STEP-02: baseline — concluído (auto-approved)
- STEP-03: red — compare_to_playtest tests — concluído
- STEP-04: green — compare_to_playtest + dataclasses — concluído
- STEP-05: red — run_pipeline synthetic tests — concluído
- STEP-06: green — DeterministicPipelineSolver + run_pipeline — concluído
- STEP-07: red — Aurora tests — concluído
- STEP-08: green — Aurora run fechada — concluído
- STEP-09: refactor — helpers privados por etapa — concluído
- STEP-10: validation — 1280 testes (5 symlink Windows pré-existentes) — concluído
- STEP-11: documentation — docs/AURORA_PIPELINE_RUN.md + ROADMAP — concluído (auto-approved)
- STEP-12: wrap-up — concluído (auto-approved)

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
- Concluída junho/2026: `generator/pipeline_runner.py`, 32 testes novos, primeira run Aurora documentada.

# ISSUE-28 — Rodar o pipeline completo no caso Hotel Aurora

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

Os steps serão planejados pelo orquestrador no STEP-00. Estrutura esperada:

- STEP-01: reading — leitura de todas as APIs públicas da pipeline e do caso Aurora
- STEP-02: baseline — suíte atual antes de qualquer alteração
- STEP-03: red — testes de `compare_to_playtest` (função pura, casos 1–8)
- STEP-04: green — `compare_to_playtest` + dataclasses + AURORA_PLAYTEST_DEFECTS
- STEP-05: red — testes de `run_pipeline` sobre blueprint sintético (casos 9–22)
- STEP-06: green — `DeterministicPipelineSolver` + `run_pipeline` (encadeamento via APIs públicas)
- STEP-07: red — testes da run real do Aurora (casos 23–32)
- STEP-08: green — fechar a run do Aurora (derivação de conclusões esperadas, consolidação)
- STEP-09: refactor — helpers privados por etapa de pipeline
- STEP-10: validation — suíte completa, git diff vazio em examples/, checagens finais
- STEP-11: documentation — `docs/AURORA_PIPELINE_RUN.md` + status em ROADMAP.md
- STEP-12: wrap-up — relatório final

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Maior valor do roadmap; aguardando orquestração inicial.

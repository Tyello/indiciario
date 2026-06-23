# ISSUE-29+30 — Fintech no pipeline + Relatório comparativo de qualidade

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

ISSUE-28 provou a pipeline ponta-a-ponta sobre o Aurora (intermediário). Agora
validamos sobre um **novo blueprint corporativo de dificuldade médio-alta** —
Fintech — e consolidamos métricas de qualidade entre os dois casos.

Pré-requisito: **blueprint Fintech** precisa estar em `examples/caso_fintech.json`
(novo ou adaptado de um existente).

A PR entrega:
- ISSUE-29: run completa do Fintech no `pipeline_runner.py` (reutilizado)
- ISSUE-30: relatório comparativo Aurora vs Fintech com ≥6 métricas de qualidade

Próximo passo (após merge): criar um novo caso canônico via chat LLM (fora do
repo) e validar com a pipeline.

## Spec completa

Ver `.ai/issues/ISSUE-29+30_SPEC.md`

## Decisão de blueprint Fintech

Três opções:

**Opção A (recomendada para velocidade):**
Adaptar um dos casos existentes (`showcase_tecnico.json` ou outro) como
referência corporativa. Editar manualmente campos de conflito, documentos,
personagens.
Tempo: ~1 dia

**Opção B (novo, customizado):**
Criar `caso_fintech.json` do zero estruturando uma fraude financeira real.
Documentos: extratos bancários, e-mails corporativos, registros, contratos.
Tempo: ~3–5 dias

**Opção C (com LLM, prototípico):**
Usar chat GPT/Claude manualmente para estruturar os documentos Fintech,
depois validar no validator e rodar no pipeline.
Tempo: ~2 dias

Qual opção você prefere?

## Steps

Os steps serão planejados pelo orquestrador no STEP-00. Estrutura esperada:

- STEP-01: reading — pipeline_runner.py, Aurora run, estrutura de blueprint
- STEP-02: baseline — suíte atual antes de qualquer alteração
- STEP-03: preparacao-fintech — validar/preparar blueprint Fintech
- STEP-04: run-fintech — executar run_pipeline sobre Fintech
- STEP-05: red — testes de geração de relatório comparativo
- STEP-06: green — CaseMetrics + MetricComparison + QualityComparativeReport + generate_quality_report
- STEP-07: red — testes de comparação Aurora vs Fintech
- STEP-08: green — integração das duas runs, consolidação de relatório
- STEP-09: documentation — FINTECH_PIPELINE_RUN.md + QUALITY_COMPARATIVE_REPORT.md
- STEP-10: refactor — helpers de cálculo de densidade/vazamento/pacing
- STEP-11: validation — suíte completa, checagens finais
- STEP-12: wrap-up — relatório final

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da decisão de atuar em Fintech + relatório
  (após ISSUE-23+24).
  Próximo passo após merge: criar novo caso canônico via LLM + validar.

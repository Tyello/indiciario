# ISSUE-30.5 — Quality Gate para Canonical

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

ISSUE-29+30 consolidou métricas Aurora vs Fintech. Agora você quer criar novo
Intermediário II validado como canônico.

Para isso, precisa de uma **função de curadoria** que diga: "Este novo caso
qualifica como Intermediário?" com feedback explícito sobre quais critérios
foram atingidos/falharam.

Aurora é o baseline intermediário validado por playtest humano. Esta issue
codifica os critérios que Aurora satisfaz (density, documents, findings, pacing,
pipeline status) como threshold para novos intermediários.

## Spec completa

Ver `.ai/issues/ISSUE-30.5_SPEC.md`

## Métricas baseline (Aurora intermediário I)

- Densidade: 26.464 chars total
- Documentos: 17
- Findings ER_*: 3 (todos ER_007)
- Findings VR_*: 0
- Findings AR_*: 0
- Stages completed: 4/4
- Pipeline status: complete (não bloqueado)
- Playtest: validado por Marcelo

Isso define o intervalo para **intermediário** (±15% densidade, ±3 documentos,
≤5 findings ER_*, etc.).

## Steps esperados (orquestrador definirá)

- STEP-01: reading — QUALITY_COMPARATIVE_REPORT, Aurora metrics, models.py
- STEP-02: baseline — suíte atual
- STEP-03: red — testes de curadoria
- STEP-04: green — CANONICAL_CRITERIA constant + dataclasses + evaluate_for_canonical
- STEP-05: refactor — helpers de cálculo
- STEP-06: validation — suíte, Aurora/Fintech qualificações confirmadas
- STEP-07: documentation — CANONICAL_CRITERIA.md
- STEP-08: wrap-up — relatório final

## Histórico

- Issue criada por Claude Sonnet 4.6 após ISSUE-29+30 mergeada.
  Próximo: usar evaluate_for_canonical para validar novo Intermediário II.

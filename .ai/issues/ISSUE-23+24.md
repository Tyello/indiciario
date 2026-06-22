# ISSUE-23+24 — Visual Reviewer + Accessibility Reviewer

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

ISSUE-28 provou a pipeline ponta-a-ponta sobre o Aurora e **desbloqueou**
ISSUE-23 (Visual Reviewer) e ISSUE-24 (Accessibility Reviewer).

Os reviewers narrative e evidence já existem (`generator/narrative_reviewer.py`,
`generator/evidence_reviewer.py`) e compartilham o contrato
`schemas/review_report.schema.yaml` com `reviewer_type: [narrative, evidence]`.

Restrição arquitetural descoberta na leitura do repo: o schema do review_report
é fechado em narrative/evidence, e há **testes existentes que dependem de
`visual_review` ser um valor inválido** nos enums de workspace/manifest
(`tests/test_run_manifest_schema.py` casos 15 e 17). Portanto esta issue cria um
**schema novo e independente** (`visual_accessibility_review_report.schema.yaml`)
com `reviewer_type: [visual, accessibility]` e **não** toca os schemas/enums/
módulos/testes existentes. A integração desses artefatos no workspace/manifest
fica para uma issue futura de integração.

## Spec completa

Ver `.ai/issues/ISSUE-23+24_SPEC.md`

## Backlog herdado (registrar, fora de escopo desta issue)

- **Lacuna no `manual_orchestrator` (descoberta na PR #95):** a transição para o
  stage `complete` não avança `status` para `done` automaticamente; o
  `pipeline_runner` compensa com mutação direta `run["status"] = "done"`.
  Considerar avançar o status terminal dentro do orchestrator numa issue futura.
- **NR_002/005/007:** regras de clareza/escopo de documentos/objetivos ainda não
  implementadas; o playtest do Aurora (PD_01–PD_03) caiu em `unmatched_playtest`.
- **Integração visual/accessibility:** estender enums de `artifact_type`/
  `source_type` em workspace/manifest para incluir visual_review/accessibility_review
  (com migração dos testes 15/17 do manifest schema) numa issue dedicada.

## Steps

Os steps serão planejados pelo orquestrador no STEP-00. Estrutura esperada:

- STEP-01: reading — narrative/evidence reviewers, review_report schema, campos visuais do Blueprint
- STEP-02: baseline — suíte atual antes de qualquer alteração
- STEP-03: red — fixtures + testes de schema (casos 1–16)
- STEP-04: green — schema + visual_reviewer dataclasses/helpers + validate + report_to_dict
- STEP-05: red — testes do visual reviewer (casos 17–32)
- STEP-06: green — review_visual (VR_001–VR_006)
- STEP-07: red — testes do accessibility reviewer (casos 33–48)
- STEP-08: green — review_accessibility (AR_001–AR_006), importando de visual_reviewer
- STEP-09: refactor — helpers de varredura por envelope compartilhados; constantes de limiar
- STEP-10: validation — suíte completa; confirmar review_report.schema e testes 15/17 do manifest intactos
- STEP-11: documentation — status em ROADMAP.md
- STEP-12: wrap-up — relatório final

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Desbloqueada por ISSUE-28; aguardando orquestração inicial.

# ISSUE-17 — Blind Solver Report Validator

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

A ISSUE-16 entregou:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `schemas/blind_solver_report.schema.yaml` — contrato estrutural do report
- Validação estrutural via `validate_blind_solver_report()` já integrada ao harness

O que ainda não existe:
- Validador standalone que pode ser chamado independentemente do harness
- Separação semântica entre fatos, hipóteses e conclusão no report
- Validação de que `reasoning_summary` não é vago (ex: apenas "inconclusivo")
- Validação de que `confidence` é coerente com presença/ausência de evidências
- CLI ou função pública para validar um report YAML/JSON sem rodar o harness completo
- Fixtures demonstrando report com hipótese com evidência e informação ausente declarada

## Spec completa

Ver `.ai/issues/ISSUE-17_SPEC.md`

## Steps

(a ser preenchido pelo orquestrador em STEP-00)

## Histórico

- Issue criada; aguardando orquestração inicial.

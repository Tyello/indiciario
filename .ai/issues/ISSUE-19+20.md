# ISSUE-19+20 — Gate Evaluator (schema + harness)

## Estado

```
STATUS: done
CURRENT_STEP: STEP-12
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-12
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-19/STEP-12_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-19/STEP-11_REVIEW.md
BLOCKER: none
```

## Contexto

As ISSUE-16, ISSUE-17 e ISSUE-18 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado e resultado estruturado
- `schemas/blind_solver_report.schema.yaml` — contrato do output do solver
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `schemas/blind_solve_run_record.schema.yaml` — run record rastreável
- `generator/blind_solve_run_record.py` — builder e validador do run record

O que ainda não existe:
- Schema para registrar uma **avaliação privada** de um run congelado
- Harness que valida a estrutura dessa avaliação e aplica regras semânticas (GE_001–GE_008)
- Ligação formal entre: run record, solução privada do autor e decisão de aprovação/rejeição/rollback
- Fixtures demonstrando avaliação aprovada, rejeitada e com rollback

## Spec completa

Ver `.ai/issues/ISSUE-19_SPEC.md`

## Steps

### STEP-01 — Leitura e mapeamento das APIs existentes

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler run record, harness, validador, schemas e testes relevantes.
- Mapear no execution report as estruturas públicas que o Gate Evaluator vai consumir:
  `BlindSolveRunRecord` (via `build_run_record`/`validate_run_record`),
  `BlindSolverReport` embutido no record, campos `run_id`, `bundle_id`,
  `report.confidence`, `report.conclusion`.
- Identificar o `gate_decision: null` do run record como ponto de extensão.
- Registrar os nomes exatos de atributos/campos que o builder vai produzir.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/skills/README.md`
- `.ai/skills/tdd.md`
- `generator/blind_solver_harness.py`
- `generator/blind_solve_run_record.py`
- `generator/blind_solver_report_validator.py`
- `schemas/blind_solve_run_record.schema.yaml`
- `schemas/blind_solver_report.schema.yaml`
- `tests/test_blind_solve_run_record.py`
- `tests/test_blind_solver_harness.py`
- `docs/BLIND_SOLVER_HARNESS.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar qualquer arquivo de implementação, teste, schema ou fixture.
- Criar schema ou código.
- Rodar pytest.

Done quando:
- Execution report lista os nomes exatos das estruturas e campos que o Gate
  Evaluator consumirá e produzirá.

Revisão:
- Confirmar que só houve leitura e que o report mapeia as APIs corretamente.
- Nenhum arquivo de implementação/teste alterado.

### STEP-02 — Baseline da suíte

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Registrar o estado atual da suíte antes de qualquer alteração.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-19/STEP-02_EXECUTION.md`

Comandos permitidos:
- `pytest tests/test_blind_solve_run_record.py -q`
- `pytest tests/test_blind_solve_run_record_schema.py -q`
- `pytest tests/ -q`

Proibido:
- Alterar qualquer código, teste, schema ou fixture.
- Corrigir falhas.

Done quando:
- Execution report contém a contagem de testes (passed) e confirma suíte verde.

Revisão:
- Confirmar que apenas comandos de baseline foram executados.
- Resultados registrados.

### STEP-03 — RED: fixtures + testes de schema (parte 1, casos 1–10)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as fixtures válidas da gate evaluation.
- Criar `tests/test_gate_evaluation_schema.py` com os casos 1–10 da spec:
  1. `valid_approved.yaml` passa
  2. `valid_rejected.yaml` passa
  3. `valid_rollback.yaml` passa
  4. `valid_no_gaps.yaml` passa
  5. `valid_unexpected_hypotheses.yaml` passa
  6. `expected_conclusions` vazio é válido
  7. `leak_detected: true` é válido no schema
  8. `confidence_assessment.evaluator_agreement: "partial"` é válido
  9. `notes` vazio é válido
  10. `unexpected_valid_hypotheses` com strings é válido
- Os testes devem falhar (RED) porque `schemas/gate_evaluation.schema.yaml`
  e `validate_gate_evaluation` ainda não existem.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `schemas/blind_solve_run_record.schema.yaml`
- `tests/test_blind_solve_run_record_schema.py`

Arquivos editáveis:
- `tests/test_gate_evaluation_schema.py`
- `tests/fixtures/gate_evaluation/valid/valid_approved.yaml`
- `tests/fixtures/gate_evaluation/valid/valid_rejected.yaml`
- `tests/fixtures/gate_evaluation/valid/valid_rollback.yaml`
- `tests/fixtures/gate_evaluation/valid/valid_no_gaps.yaml`
- `tests/fixtures/gate_evaluation/valid/valid_unexpected_hypotheses.yaml`

Comandos permitidos:
- `pytest tests/test_gate_evaluation_schema.py -q`

Proibido:
- Criar `schemas/gate_evaluation.schema.yaml`.
- Criar `generator/gate_evaluator.py`.
- Implementar qualquer GREEN.

Done quando:
- Fixtures criadas conforme a spec.
- Testes 1–10 existem e FALHAM pelo motivo certo, registrado no execution report.

Revisão:
- Confirmar que só testes/fixtures foram criados, sem implementação GREEN.
- Confirmar falha RED registrada.

### STEP-04 — RED: testes de schema (parte 2, casos 11–20)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as fixtures inválidas da gate evaluation.
- Adicionar a `tests/test_gate_evaluation_schema.py` os casos 11–20 da spec:
  11. `schema_version: "2.0"` falha
  12. `decision: "pending"` falha
  13. `evaluation_id` ausente falha
  14. `run_id` ausente falha
  15. `justification` ausente falha
  16. `rollback_target: "unknown_stage"` falha
  17. `expected_conclusions` item sem `id` falha
  18. `gaps` item sem `severity` falha
  19. `gaps` item com `severity: "trivial"` falha
  20. campo extra no topo falha
- Os novos testes devem falhar (RED) por ausência do schema.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `tests/test_gate_evaluation_schema.py`
- `tests/fixtures/gate_evaluation/valid/valid_approved.yaml`

Arquivos editáveis:
- `tests/test_gate_evaluation_schema.py`
- `tests/fixtures/gate_evaluation/invalid/invalid_decision.yaml`
- `tests/fixtures/gate_evaluation/invalid/missing_evaluation_id.yaml`
- `tests/fixtures/gate_evaluation/invalid/missing_justification.yaml`
- `tests/fixtures/gate_evaluation/invalid/invalid_rollback_target.yaml`
- `tests/fixtures/gate_evaluation/invalid/extra_top_field.yaml`
- `tests/fixtures/gate_evaluation/invalid/invalid_gap_severity.yaml`

Comandos permitidos:
- `pytest tests/test_gate_evaluation_schema.py -q`

Proibido:
- Criar schema ou implementação.
- Implementar GREEN.

Done quando:
- Testes 11–20 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar apenas testes/fixtures alterados, sem GREEN.

### STEP-05 — GREEN: schema + validate_gate_evaluation

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `schemas/gate_evaluation.schema.yaml` conforme o modelo da spec
  (campos obrigatórios, `additionalProperties: false` no topo, enums de
  `decision`, `rollback_target`, `severity`, `evaluator_agreement`,
  `expected_conclusions[]` e `gaps[]` com campos obrigatórios).
- Criar `generator/gate_evaluator.py` com a função pública
  `validate_gate_evaluation(evaluation) -> list[str]`.
- Fazer os testes de schema (STEP-03/04) passarem (GREEN).

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `tests/test_gate_evaluation_schema.py`
- `generator/blind_solver_report_validator.py`
- `schemas/blind_solve_run_record.schema.yaml`

Arquivos editáveis:
- `schemas/gate_evaluation.schema.yaml`
- `generator/gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluation_schema.py -q`
- `ruff check generator/gate_evaluator.py`

Proibido:
- Implementar `validate_gate_evaluation_semantics` ou `build_gate_evaluation` ainda.
- Alterar schemas/arquivos existentes além dos criados.
- Criar novos testes de escopo relevante.

Done quando:
- Todos os 20 testes de schema passam.
- `ruff` limpo no novo arquivo.

Revisão:
- Confirmar implementação mínima (schema + validate_gate_evaluation).
- Sem novos testes; sem alteração de arquivos existentes proibidos.

### STEP-06 — RED: testes semânticos GE_001–GE_006 (casos 21–30)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_gate_evaluator.py` com os casos 21–30 da spec:
  21. `decision: rollback` sem `rollback_target` → GE_001 error
  22. `decision: rollback` com `rollback_target` preenchido → sem GE_001
  23. `decision: approved` com `rollback_target` preenchido → GE_002 error
  24. `decision: approved` com `rollback_target: null` → sem GE_002
  25. `leak_detected: true` + `decision: approved` → GE_003 error
  26. `leak_detected: true` + `decision: rejected` → sem GE_003
  27. `decision: approved` com `required=true` e `met=false` → GE_004/GE_005 error
  28. `decision: approved` com todos `required=true` e `met=true` → sem GE_004
  29. `decision: approved` com gap `severity: critical` → GE_006 error
  30. `decision: rejected` com gap `severity: critical` → sem GE_006
- Testes devem falhar (RED) por ausência de `validate_gate_evaluation_semantics`.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `tests/fixtures/gate_evaluation/valid/valid_approved.yaml`
- `generator/gate_evaluator.py`

Arquivos editáveis:
- `tests/test_gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py -q`

Proibido:
- Implementar `validate_gate_evaluation_semantics`.
- Implementar GREEN.

Done quando:
- Testes 21–30 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar só teste criado, sem GREEN.

### STEP-07 — RED: testes GE_007/GE_008 + builder (casos 31–50)

Status: pending
Owner: executor
Type: red

Objetivo:
- Adicionar a `tests/test_gate_evaluator.py` os casos 31–50 da spec:
  31–36: GE_007/GE_008 (aviso, referência ao run record, valid flag)
  37–50: `build_gate_evaluation`, integração, não mutação, preservação de campos
- Testes devem falhar (RED) por ausência de `validate_gate_evaluation_semantics`
  e `build_gate_evaluation`.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `generator/blind_solve_run_record.py`
- `generator/gate_evaluator.py`
- `tests/test_gate_evaluator.py`
- `tests/fixtures/gate_evaluation/valid/`

Arquivos editáveis:
- `tests/test_gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py -q`

Proibido:
- Implementar GREEN.

Done quando:
- Testes 31–50 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar só teste alterado, sem GREEN.

### STEP-08 — GREEN: validate_gate_evaluation_semantics

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `validate_gate_evaluation_semantics(evaluation, run_record=None)`
  em `generator/gate_evaluator.py` com as regras GE_001–GE_008.
- Implementar dataclasses `GateEvaluationRequest` e `GateEvaluationResult`.
- Fazer os testes semânticos (STEP-06/07 parcial, casos 21–36) passarem.
- NÃO implementar `build_gate_evaluation` ainda.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `tests/test_gate_evaluator.py`
- `generator/gate_evaluator.py`
- `generator/blind_solver_report_validator.py`

Arquivos editáveis:
- `generator/gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py::test_ge001_rollback_without_target -q` (ou padrão similar)
- `pytest tests/test_gate_evaluator.py -k "semantics or GE_" -q`
- `ruff check generator/gate_evaluator.py`

Proibido:
- Implementar `build_gate_evaluation`.
- Criar novos testes de escopo relevante.
- Alterar arquivos existentes fora de `generator/gate_evaluator.py`.

Done quando:
- Testes 21–36 passam.
- `ruff` limpo.

Revisão:
- Confirmar GREEN mínimo; sem `build_gate_evaluation`; sem alteração de proibidos.

### STEP-09 — GREEN: build_gate_evaluation

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `build_gate_evaluation(request, expected_conclusions, ...) -> dict`
  em `generator/gate_evaluator.py` conforme a API da spec.
- Construir a evaluation ligando `evaluation_id`, `run_id`, `bundle_id` do
  `request.run_record`, serializando `expected_conclusions`, `gaps`,
  `confidence_assessment` e `decision`/`justification`/`rollback_target`.
- Não mutar inputs.
- Fazer todos os testes do builder (casos 37–50) passarem.
- Suíte de schema (STEP-03/04) e suíte semântica (STEP-06/07) devem continuar verdes.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`
- `.ai/runs/ISSUE-19/STEP-01_EXECUTION.md`
- `tests/test_gate_evaluator.py`
- `generator/gate_evaluator.py`
- `generator/blind_solve_run_record.py`

Arquivos editáveis:
- `generator/gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py -q`
- `pytest tests/test_gate_evaluation_schema.py -q`
- `ruff check generator/gate_evaluator.py`

Proibido:
- Criar novos testes de escopo relevante.
- Alterar arquivos existentes fora de `generator/gate_evaluator.py`.

Done quando:
- Todos os 50 testes dos dois arquivos passam.
- `ruff` limpo.

Revisão:
- Confirmar GREEN mínimo; sem escopo extra; sem alteração de proibidos.

### STEP-10 — REFACTOR

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Reorganizar helpers de `generator/gate_evaluator.py` (clareza, dedup das
  regras GE_001–GE_008), sem alterar comportamento nem API pública.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `generator/gate_evaluator.py`
- `tests/test_gate_evaluator.py`
- `tests/test_gate_evaluation_schema.py`

Arquivos editáveis:
- `generator/gate_evaluator.py`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py -q`
- `pytest tests/test_gate_evaluation_schema.py -q`
- `ruff check generator/gate_evaluator.py`

Proibido:
- Adicionar comportamento novo.
- Alterar API pública.
- Adicionar testes de escopo relevante.

Done quando:
- Testes continuam verdes; `ruff` limpo; comportamento inalterado.

Revisão:
- Confirmar ausência de comportamento/API novos.

### STEP-11 — VALIDATION: suíte completa e checagens

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar a validação final completa e registrar resultados (inclui teste 50 — suíte
  completa sem regressão).

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/issues/ISSUE-19_SPEC.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-19/STEP-11_EXECUTION.md`

Comandos permitidos:
- `ruff check generator/gate_evaluator.py`
- `pytest tests/test_gate_evaluation_schema.py -q`
- `pytest tests/test_gate_evaluator.py -q`
- `pytest tests/test_blind_solve_run_record.py -q`
- `pytest tests/test_blind_solve_run_record_schema.py -q`
- `pytest tests/test_blind_solver_harness.py -q`
- `pytest tests/test_blind_solver_report_validator.py -q`
- `pytest tests/ -q`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- Corrigir falhas.
- Alterar código/testes.

Done quando:
- Suíte completa passa sem regressão (990+ testes) e resultados registrados.
- `git diff --stat` confirma que só arquivos novos da issue foram criados.

Revisão:
- Confirmar só comandos de validação; resultados registrados; nenhuma correção feita.

### STEP-12 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Atualizar `docs/BLIND_SOLVER_HARNESS.md` com seção curta sobre o Gate Evaluator
  (API, decisões, regras GE_001–GE_008).
- Registrar resumo final no execution report do step.

Contexto permitido:
- `.ai/issues/ISSUE-19+20.md`
- `.ai/runs/ISSUE-19/STEP-11_EXECUTION.md`
- `docs/BLIND_SOLVER_HARNESS.md`

Arquivos editáveis:
- `docs/BLIND_SOLVER_HARNESS.md`
- `.ai/runs/ISSUE-19/STEP-12_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar implementação ou testes.
- Rodar pytest.

Done quando:
- Doc atualizado (ou justificado como desnecessário) e resumo final registrado.

Revisão:
- Confirmar só documentação/relatório alterados.

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Aguardando orquestração inicial.
- STEP-01 executado; aguardando revisão.
- STEP-01 auto-approved (low-risk reading); orquestrador avançou para STEP-02.
- STEP-02 executado; baseline 982 passed / 3 skipped / 5 failed (5 falhas = limitação Windows symlink WinError 1314, sem regressão).
- STEP-02 auto-approved (low-risk baseline); orquestrador avançou para STEP-03.
- STEP-02 executado; aguardando revisão.
- STEP-03 executado; aguardando revisão.
- STEP-03 aprovado; aguardando orquestrador.
- STEP-04 executado; aguardando revisão.
- STEP-04 aprovado; aguardando orquestrador.
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado; aguardando orquestrador.
- STEP-06 executado; aguardando revisão.
- STEP-06 aprovado; aguardando orquestrador.
- STEP-07 executado; aguardando revisão.
- STEP-07 aprovado; aguardando orquestrador.
- STEP-08 executado; aguardando revisão.
- STEP-08 aprovado; aguardando orquestrador.
- STEP-09 executado; aguardando revisão.
- STEP-09 aprovado; aguardando orquestrador.
- STEP-10 executado; aguardando revisão.
- STEP-10 aprovado; aguardando orquestrador.
- STEP-11 executado; suíte completa 1033 passed / 3 skipped / 5 failed (+51 vs baseline, sem regressão); aguardando revisão.
- STEP-11 aprovado; aguardando orquestrador.
- STEP-12 executado; aguardando revisão.
- STEP-12 auto-approved (low-risk wrap-up); sem próximo step → STATUS: done.

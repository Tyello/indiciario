# ISSUE-21+22 — Narrative Reviewer + Evidence Reviewer

## Estado

```
STATUS: ready
CURRENT_STEP: STEP-01
NEXT_ACTION: executor
REVIEW_STATUS: pending
LAST_COMPLETED_STEP: none
LAST_EXECUTION_REPORT: none
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

As ISSUE-16–20 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `generator/gate_evaluator.py` — Gate Evaluator com regras GE_001–GE_008
- 1033 testes passando

O que ainda não existe:
- Revisores especializados que operam sobre o Blueprint (não sobre o bundle cego)
- Schema comum para o report de qualquer reviewer (`review_report.schema.yaml`)
- Narrative Reviewer: avalia diegese, imersão, motivação, tom, personagens
- Evidence Reviewer: avalia cadeia de evidências, pistas órfãs, cobertura de envelopes

## Spec completa

Ver `.ai/issues/ISSUE-21_SPEC.md`

## Steps

### STEP-01 — Leitura e mapeamento das APIs existentes

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler `generator/models.py` e mapear campos do Blueprint usados pelos revisores:
  `documentos`, `personagens`, `executor_id`, `matriz_pistas`, `red_herrings`,
  `pilares_validacao`, `objetivos_por_envelope`, `cadeia_causal`, `dicas`, `tom`.
- Ler `generator/case_review.py` e `generator/gate_evaluator.py` para capturar
  padrões de finding/dataclass/builder já estabelecidos no repo.
- Registrar no execution report: nomes exatos dos campos do Blueprint que cada
  regra NR_* e ER_* vai acessar.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/skills/README.md`
- `.ai/skills/tdd.md`
- `generator/models.py`
- `generator/case_review.py`
- `generator/case_kernel.py`
- `generator/gate_evaluator.py`
- `generator/blind_solver_report_validator.py`
- `schemas/gate_evaluation.schema.yaml`
- `tests/test_gate_evaluator.py`

Arquivos editáveis:
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar qualquer arquivo de implementação, teste, schema ou fixture.
- Criar schema ou código.
- Rodar pytest.

Done quando:
- Execution report lista os campos exatos do Blueprint que cada regra acessará.

Revisão:
- Confirmar que só houve leitura.
- Nenhum arquivo de implementação/teste alterado.

### STEP-02 — Baseline da suíte

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Registrar o estado atual da suíte antes de qualquer alteração.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-21/STEP-02_EXECUTION.md`

Comandos permitidos:
- `pytest tests/test_gate_evaluator.py -q`
- `pytest tests/test_gate_evaluation_schema.py -q`
- `pytest tests/ -q`

Proibido:
- Alterar qualquer código, teste, schema ou fixture.
- Corrigir falhas.

Done quando:
- Execution report contém contagem de testes passando e confirma suíte verde.

Revisão:
- Confirmar que apenas baseline foi rodado; resultados registrados.

### STEP-03 — RED: fixtures + testes de schema (casos 1–10)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as fixtures válidas do review report.
- Criar `tests/test_review_report_schema.py` com os casos 1–10 da spec:
  1. `valid_narrative_approved.yaml` passa
  2. `valid_narrative_needs_revision.yaml` passa
  3. `valid_evidence_blocked.yaml` passa
  4. `valid_no_findings.yaml` passa
  5. `reviewer_type: "evidence"` é válido
  6. `overall_confidence: "low"` é válido
  7. `findings` com `severity: "info"` é válido
  8. `findings[].recommendation` vazia é válida
  9. `findings[].field` vazia é válida
  10. `notes` vazia é válida
- Os testes devem falhar (RED) porque `schemas/review_report.schema.yaml`
  e `validate_review_report` ainda não existem.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `schemas/gate_evaluation.schema.yaml`
- `tests/test_gate_evaluation_schema.py`

Arquivos editáveis:
- `tests/test_review_report_schema.py`
- `tests/fixtures/review_report/valid/valid_narrative_approved.yaml`
- `tests/fixtures/review_report/valid/valid_narrative_needs_revision.yaml`
- `tests/fixtures/review_report/valid/valid_evidence_blocked.yaml`
- `tests/fixtures/review_report/valid/valid_no_findings.yaml`

Comandos permitidos:
- `pytest tests/test_review_report_schema.py -q`

Proibido:
- Criar `schemas/review_report.schema.yaml`.
- Criar qualquer módulo em `generator/`.
- Implementar qualquer GREEN.

Done quando:
- Fixtures criadas conforme spec.
- Testes 1–10 existem e FALHAM pelo motivo certo, registrado no report.

Revisão:
- Confirmar que só testes/fixtures foram criados, sem GREEN.
- Falha RED registrada.

### STEP-04 — RED: testes de schema (casos 11–20)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as fixtures inválidas do review report.
- Adicionar a `tests/test_review_report_schema.py` os casos 11–20 da spec:
  11. `schema_version: "2.0"` falha
  12. `reviewer_type: "visual"` falha
  13. `status: "pending"` falha
  14. `report_id` ausente falha
  15. `summary` ausente falha
  16. `overall_confidence: "very_high"` falha
  17. `findings[].severity: "warning"` falha
  18. `findings[].code` ausente falha
  19. campo extra no topo falha
  20. `findings[].id` ausente falha
- Os novos testes devem falhar (RED) por ausência do schema.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `tests/test_review_report_schema.py`
- `tests/fixtures/review_report/valid/valid_narrative_approved.yaml`

Arquivos editáveis:
- `tests/test_review_report_schema.py`
- `tests/fixtures/review_report/invalid/invalid_reviewer_type.yaml`
- `tests/fixtures/review_report/invalid/invalid_status.yaml`
- `tests/fixtures/review_report/invalid/missing_report_id.yaml`
- `tests/fixtures/review_report/invalid/missing_summary.yaml`
- `tests/fixtures/review_report/invalid/invalid_severity.yaml`
- `tests/fixtures/review_report/invalid/extra_top_field.yaml`

Comandos permitidos:
- `pytest tests/test_review_report_schema.py -q`

Proibido:
- Criar schema ou implementação.
- Implementar GREEN.

Done quando:
- Testes 11–20 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar apenas testes/fixtures alterados, sem GREEN.

### STEP-05 — GREEN: schema + validate_review_report

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `schemas/review_report.schema.yaml` conforme o modelo da spec.
- Criar `generator/narrative_reviewer.py` com dataclasses `ReviewFinding`,
  `ReviewReport` e função pública `validate_review_report(report) -> list[str]`
  e `report_to_dict(report) -> dict`.
- NÃO implementar `review_narrative` ainda.
- Fazer os testes de schema (STEP-03/04) passarem (GREEN).

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `tests/test_review_report_schema.py`
- `generator/gate_evaluator.py`
- `schemas/gate_evaluation.schema.yaml`

Arquivos editáveis:
- `schemas/review_report.schema.yaml`
- `generator/narrative_reviewer.py`

Comandos permitidos:
- `pytest tests/test_review_report_schema.py -q`
- `ruff check generator/narrative_reviewer.py`

Proibido:
- Implementar `review_narrative` ou `review_evidence`.
- Criar `generator/evidence_reviewer.py`.
- Alterar schemas/arquivos existentes além dos criados.

Done quando:
- Todos os 20 testes de schema passam.
- `ruff` limpo.

Revisão:
- Confirmar implementação mínima (schema + dataclasses + validate_review_report + report_to_dict).
- Sem review_narrative; sem evidence_reviewer.

### STEP-06 — RED: testes do Narrative Reviewer (casos 21–45)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_narrative_reviewer.py` com os casos 21–45 da spec:
  21–28: regras NR_001–NR_008
  29–38: `review_narrative` e status
  39–45: `validate_review_report` e integração
- Testes devem falhar (RED) por ausência de `review_narrative`.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `generator/narrative_reviewer.py`
- `generator/models.py`
- `tests/test_gate_evaluator.py`
- `examples/caso_canonico_intermediario.json`

Arquivos editáveis:
- `tests/test_narrative_reviewer.py`

Comandos permitidos:
- `pytest tests/test_narrative_reviewer.py -q`

Proibido:
- Implementar `review_narrative`.
- Implementar GREEN.

Done quando:
- Testes 21–45 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar só teste criado, sem GREEN.

### STEP-07 — GREEN: review_narrative (NR_001–NR_008)

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `review_narrative(blueprint, blueprint_ref, report_id, ...) -> ReviewReport`
  em `generator/narrative_reviewer.py` com as regras NR_001–NR_008.
- Implementar lógica de status: blocked (critical), needs_revision (major),
  approved (minor/info/sem findings).
- Fazer os testes 21–45 passarem.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `tests/test_narrative_reviewer.py`
- `generator/narrative_reviewer.py`
- `generator/models.py`
- `generator/case_review.py`

Arquivos editáveis:
- `generator/narrative_reviewer.py`

Comandos permitidos:
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_review_report_schema.py -q`
- `ruff check generator/narrative_reviewer.py`

Proibido:
- Criar `generator/evidence_reviewer.py`.
- Criar novos testes de escopo relevante.
- Alterar arquivos existentes fora de `generator/narrative_reviewer.py`.

Done quando:
- Todos os 25 testes do narrative reviewer passam.
- Testes de schema continuam verdes.
- `ruff` limpo.

Revisão:
- Confirmar GREEN mínimo; sem evidence_reviewer; sem alteração de proibidos.

### STEP-08 — RED: testes do Evidence Reviewer (casos 46–70)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_evidence_reviewer.py` com os casos 46–70 da spec:
  46–53: regras ER_001–ER_008
  54–63: `review_evidence` e status
  64–70: integração e edge cases
- Testes devem falhar (RED) por ausência de `generator/evidence_reviewer.py`.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `generator/narrative_reviewer.py`
- `generator/models.py`
- `tests/test_narrative_reviewer.py`
- `examples/caso_canonico_intermediario.json`

Arquivos editáveis:
- `tests/test_evidence_reviewer.py`

Comandos permitidos:
- `pytest tests/test_evidence_reviewer.py -q`

Proibido:
- Criar `generator/evidence_reviewer.py`.
- Implementar GREEN.

Done quando:
- Testes 46–70 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar só teste criado, sem GREEN.

### STEP-09 — GREEN: review_evidence (ER_001–ER_008)

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `generator/evidence_reviewer.py` com `review_evidence(blueprint, ...) -> ReviewReport`.
- Importar `ReviewFinding`, `ReviewReport`, `validate_review_report`, `report_to_dict`
  de `generator/narrative_reviewer` (sem duplicar).
- Implementar regras ER_001–ER_008 com a mesma lógica de status.
- Fazer os testes 46–70 passarem.
- Testes de narrative e schema devem continuar verdes.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`
- `.ai/runs/ISSUE-21/STEP-01_EXECUTION.md`
- `tests/test_evidence_reviewer.py`
- `generator/narrative_reviewer.py`
- `generator/models.py`

Arquivos editáveis:
- `generator/evidence_reviewer.py`

Comandos permitidos:
- `pytest tests/test_evidence_reviewer.py -q`
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_review_report_schema.py -q`
- `ruff check generator/evidence_reviewer.py`

Proibido:
- Duplicar dataclasses de `narrative_reviewer.py`.
- Criar novos testes de escopo relevante.
- Alterar `generator/narrative_reviewer.py` além do necessário para export.

Done quando:
- Todos os 25 testes do evidence reviewer passam.
- Todos os 25 testes do narrative reviewer continuam verdes.
- `ruff` limpo.

Revisão:
- Confirmar sem duplicação de dataclasses; sem alteração de proibidos.

### STEP-10 — REFACTOR

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Extrair helpers de leitura de campos do Blueprint compartilhados entre
  `narrative_reviewer.py` e `evidence_reviewer.py` (se existirem).
- Garantir que a lógica de derivação de status seja idêntica nos dois revisores
  (dedup via função privada compartilhada ou helper interno).
- Sem alterar comportamento nem API pública.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `generator/narrative_reviewer.py`
- `generator/evidence_reviewer.py`
- `tests/test_narrative_reviewer.py`
- `tests/test_evidence_reviewer.py`
- `tests/test_review_report_schema.py`

Arquivos editáveis:
- `generator/narrative_reviewer.py`
- `generator/evidence_reviewer.py`

Comandos permitidos:
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_evidence_reviewer.py -q`
- `pytest tests/test_review_report_schema.py -q`
- `ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py`

Proibido:
- Adicionar comportamento novo.
- Alterar API pública.
- Adicionar testes de escopo relevante.

Done quando:
- Todos os testes continuam verdes; `ruff` limpo; comportamento inalterado.

Revisão:
- Confirmar ausência de comportamento/API novos.

### STEP-11 — VALIDATION: suíte completa e checagens

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar validação final completa e registrar resultados
  (inclui caso 70 — suíte sem regressão).

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/issues/ISSUE-21_SPEC.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-21/STEP-11_EXECUTION.md`

Comandos permitidos:
- `ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py`
- `pytest tests/test_review_report_schema.py -q`
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_evidence_reviewer.py -q`
- `pytest tests/test_gate_evaluator.py -q`
- `pytest tests/test_blind_solve_run_record.py -q`
- `pytest tests/ -q`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- Corrigir falhas.
- Alterar código/testes.

Done quando:
- Suíte completa passa sem regressão (1033+ testes) e resultados registrados.
- `git diff --stat` confirma que só arquivos novos da issue foram criados.

Revisão:
- Confirmar só comandos de validação; resultados registrados; nenhuma correção feita.

### STEP-12 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Atualizar `docs/BLIND_SOLVER_HARNESS.md` com seção curta sobre os revisores
  (API, regras NR_*/ER_*, relação com Gate Evaluator).
- Registrar resumo final no execution report do step.

Contexto permitido:
- `.ai/issues/ISSUE-21+22.md`
- `.ai/runs/ISSUE-21/STEP-11_EXECUTION.md`
- `docs/BLIND_SOLVER_HARNESS.md`

Arquivos editáveis:
- `docs/BLIND_SOLVER_HARNESS.md`
- `.ai/runs/ISSUE-21/STEP-12_EXECUTION.md`

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

# ISSUE-33.6 — Evidência citada ⊆ evidência lida — passos

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-01
NEXT_ACTION: aguardar merge da ISSUE-41.1
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: ISSUE-41.1 (CI verde); independente das 33.3–33.5
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.6_SPEC.md`. Alvos: `generator/blind_solver_harness.py` (validação semântica), possivelmente `generator/blind_solve_run_record.py`, testes.

Fecha RISCO-02. Warning auditável, nunca erro fatal nesta fase.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `blind_solver_harness.py` (`_validate_report_semantics`, estrutura de `accessed_artifacts` e canal de warnings), `blind_solver_report_validator.py` (numeração RV real — confirmar RV_009 livre), schema do run record.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.6*.md; .ai/skills/tdd.md; docs/AUDITORIA_FABLE_2026-07.md; generator/blind_solver_harness.py; generator/blind_solver_report_validator.py; generator/blind_solve_run_record.py; schemas/; tests/test_blind_solver_harness.py; tests/test_llm_blind_solver.py
Editáveis: .ai/runs/ISSUE-33.6/STEP-01_EXECUTION.md
Comandos: `grep -n "RV_0" generator/blind_solver_report_validator.py generator/blind_solver_harness.py`
Proibido: editar código.
Done quando: numeração confirmada; canal de warnings do run record mapeado.
Revisão: auto-approve (reading).
Dependências: ISSUE-41.1 done.

### STEP-02 — RED
Editáveis: tests/test_blind_solver_harness.py; .ai/runs/ISSUE-33.6/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_blind_solver_harness.py -q`
Done quando: casos 1–4 falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Editáveis: generator/blind_solver_harness.py; generator/blind_solve_run_record.py (se necessário); .ai/runs/ISSUE-33.6/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_blind_solver_harness.py tests/test_llm_blind_solver.py -q`
Done quando: casos verdes, incluindo regressão RV_011.
Revisão: revisor obrigatório — warning, não erro; zero falso positivo.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Editáveis: módulos e testes tocados; .ai/runs/ISSUE-33.6/STEP-04_EXECUTION.md
Comandos: `pytest tests/ -q -k "harness or run_record"`; `ruff check generator/ tests/`
Done quando: verde + ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Editáveis: docs/BLIND_SOLVER_HARNESS.md; docs/GUIA_CODIGOS_ERROS.md (✅/⏭️); docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-33.6/STEP-05_EXECUTION.md
Done quando: ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`
Editáveis: .ai/runs/ISSUE-33.6/STEP-06_EXECUTION.md
Done quando: sem regressão; CI verde.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.6/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.6.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (RISCO-02).

# ISSUE-33.5 — Reprodutibilidade e temperatura real no Solvability Meter — passos

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-01
NEXT_ACTION: aguardar merge da ISSUE-33.4 (mesmos módulos; evitar conflito)
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: ISSUE-33.4
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.5_SPEC.md`. Alvos: `generator/solvability_meter.py`, `generator/llm_blind_solver.py` (plumbing de temperatura), `schemas/solvability_report.schema.yaml`, testes.

Fecha BUG-06 e Melhorias 2/3 da auditoria.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, meter/solver/judge atuais (pós-33.4), schema do report, e mapear chamadores de `estimate_difficulty` nos dois módulos (grep) para RM_003.
- Registrar decisão de plumbing da temperatura (construtor vs parâmetro de solve).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.5*.md; .ai/skills/tdd.md; docs/AUDITORIA_FABLE_2026-07.md; generator/solvability_meter.py; generator/llm_blind_solver.py; generator/conclusion_judge.py; generator/playtest_metrics.py; schemas/solvability_report.schema.yaml; tests/test_solvability_meter.py
Editáveis: .ai/runs/ISSUE-33.5/STEP-01_EXECUTION.md
Comandos: `grep -rn "estimate_difficulty" generator/ tests/ docs/ framework/`
Proibido: editar código.
Done quando: chamadores mapeados e decisão de plumbing registrada.
Revisão: auto-approve (reading).
Dependências: ISSUE-33.4 done.

### STEP-02 — RED
Editáveis: tests/test_solvability_meter.py; tests/test_llm_blind_solver.py; .ai/runs/ISSUE-33.5/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_solvability_meter.py tests/test_llm_blind_solver.py -q`
Done quando: casos 1–4 falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Editáveis: generator/solvability_meter.py; generator/llm_blind_solver.py; schemas/solvability_report.schema.yaml; .ai/runs/ISSUE-33.5/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_solvability_meter.py tests/test_llm_blind_solver.py -q`
Done quando: casos 1–5 verdes.
Revisão: revisor obrigatório — temperatura no solver e não no judge; schema estrito preservado.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Editáveis: módulos e testes tocados; .ai/runs/ISSUE-33.5/STEP-04_EXECUTION.md
Comandos: `pytest tests/ -q -k "solvability or llm_blind_solver"`; `ruff check generator/ tests/`
Done quando: verde + ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Editáveis: docs/BLIND_SOLVER_HARNESS.md; framework/19_PLAYTEST_E_METRICAS.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-33.5/STEP-05_EXECUTION.md
Done quando: ✅/⏭️ justificados (incluindo decisão "judge sempre 0.0").
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`
Editáveis: .ai/runs/ISSUE-33.5/STEP-06_EXECUTION.md
Done quando: sem regressão; CI verde.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.5/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.5.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (BUG-06, Melhorias 2/3).

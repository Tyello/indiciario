# ISSUE-33.4 — Hardening do adapter LLM e do judge — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: STEP-07
BLOCKER: none
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.4_SPEC.md`. Alvos: `generator/llm_blind_solver.py`, `generator/conclusion_judge.py`, testes correspondentes.

Fecha BUG-03/04/05/07 e RISCO-04. Regra de ouro para o revisor: resposta hostil do modelo → reparo ou erro **contratual**; exceção crua é falha da issue.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/llm_blind_solver.py` (pontos :58, :87-94, :109-112, :127-129, :190-216), `generator/conclusion_judge.py` (loop de reparo correto como referência; :194-203 para RISCO-04), `generator/solvability_meter.py` (famílias capturadas em SM_002).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.4*.md; .ai/skills/tdd.md; docs/AUDITORIA_FABLE_2026-07.md; generator/llm_blind_solver.py; generator/conclusion_judge.py; generator/solvability_meter.py; schemas/judge_verdict.schema.yaml; tests/test_llm_blind_solver.py; tests/test_conclusion_judge.py; tests/test_solvability_meter.py
Editáveis: .ai/runs/ISSUE-33.4/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar código.
Done quando: cada BUG mapeado a linha real atual (números podem ter mudado).
Revisão: auto-approve (reading).
Dependências: ISSUE-41.1 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever os 7 casos da SPEC nos arquivos de teste existentes.
Editáveis: tests/test_llm_blind_solver.py; tests/test_conclusion_judge.py; tests/test_solvability_meter.py; .ai/runs/ISSUE-33.4/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py tests/test_conclusion_judge.py tests/test_solvability_meter.py -q`
Done quando: novos testes falham reproduzindo os bugs (AttributeError/TypeError/1-retry visíveis no report).
Revisão: revisor obrigatório — cada teste RED deve reproduzir o bug da auditoria, não um cenário adjacente.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar HD_001–HD_005.
Editáveis: generator/llm_blind_solver.py; generator/conclusion_judge.py; .ai/runs/ISSUE-33.4/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py tests/test_conclusion_judge.py tests/test_solvability_meter.py -q`
Proibido: alterar schemas (salvo necessidade provada do HD_005, registrada).
Done quando: 7 casos verdes.
Revisão: revisor obrigatório.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Editáveis: generator/llm_blind_solver.py; generator/conclusion_judge.py; testes tocados; .ai/runs/ISSUE-33.4/STEP-04_EXECUTION.md
Comandos: `pytest tests/ -q -k "llm_blind_solver or conclusion_judge or solvability"`; `ruff check generator/ tests/`
Done quando: verde + ruff limpo; duplicação de parsing entre solver e judge extraída se surgiu.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Editáveis: docs/BLIND_SOLVER_HARNESS.md; docs/GUIA_CODIGOS_ERROS.md (⏭️ provável, justificar); docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-33.4/STEP-05_EXECUTION.md
Done quando: ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`
Editáveis: .ai/runs/ISSUE-33.4/STEP-06_EXECUTION.md
Done quando: sem regressão; CI verde.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.4/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.4.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (BUG-03/04/05/07, RISCO-04).

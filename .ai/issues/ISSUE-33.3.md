# ISSUE-33.3 — Ligar o Conclusion Judge ao pipeline_runner — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-07
BLOCKER: none (ISSUE-41.1 concluída em 2026-07-09)
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.3_SPEC.md`. Alvos: `generator/pipeline_runner.py`, schema de manifest afetado, `tests/test_pipeline_runner.py`.

Fecha RISCO-01 (gate fabricado), DIV-12 e BUG-08 da auditoria. Ponto de atenção do revisor: decisão do gate é derivação em Python puro (PJ_002); regressão do caminho stub é o critério central (PJ_003).

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/pipeline_runner.py` (_run_gate completo, pontos :409/:635/:646/:649), `generator/conclusion_judge.py` (assinatura real), `generator/gate_evaluator.py` (GE_004/gaps), schema do manifest do pipeline, `tests/test_pipeline_runner.py`.
- Registrar: onde `gate_mode` entra no schema; grep de `EC-GUia` no repo inteiro (PJ_004).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.3*.md; .ai/skills/tdd.md; docs/AUDITORIA_FABLE_2026-07.md; generator/pipeline_runner.py; generator/conclusion_judge.py; generator/gate_evaluator.py; generator/llm_blind_solver.py; schemas/; tests/test_pipeline_runner.py
Editáveis: .ai/runs/ISSUE-33.3/STEP-01_EXECUTION.md
Comandos: `grep -rn "EC-GUia" .`
Proibido: editar código.
Done quando: mapa dos pontos de mudança + resultado do grep registrados.
Revisão: auto-approve (reading).
Dependências: ISSUE-41.1 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever os 7 casos da SPEC (regressão do stub primeiro).
Editáveis: tests/test_pipeline_runner.py; .ai/runs/ISSUE-33.3/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_pipeline_runner.py -q`
Proibido: tocar produção.
Done quando: novos testes falham pelo motivo certo; antigos verdes.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar PJ_001–PJ_005 (runner + schema do manifest + typo).
Editáveis: generator/pipeline_runner.py; schema do manifest afetado; .ai/runs/ISSUE-33.3/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_pipeline_runner.py -q`
Proibido: alterar conclusion_judge/gate_evaluator.
Done quando: 7 casos verdes.
Revisão: revisor obrigatório — PJ_002 em Python puro; falha do judge nunca aprova (caso 7).
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
Editáveis: generator/pipeline_runner.py; tests/test_pipeline_runner.py; .ai/runs/ISSUE-33.3/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_pipeline_runner.py -q`; `ruff check generator/pipeline_runner.py tests/test_pipeline_runner.py`
Done quando: verde + ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- Impacto da SPEC: ESTADO_ATUAL ✅, ROADMAP ✅ (DIV-12), BLIND_SOLVER_HARNESS ✅, CLAUDE.md ✅/⏭️, INDICE ✅/⏭️.
Editáveis: docs/ESTADO_ATUAL.md; docs/ROADMAP.md; docs/BLIND_SOLVER_HARNESS.md; CLAUDE.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-33.3/STEP-05_EXECUTION.md
Done quando: ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`; `grep -rn "EC-GUia" .`
Editáveis: .ai/runs/ISSUE-33.3/STEP-06_EXECUTION.md
Done quando: sem regressão; grep vazio; CI verde.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.3/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.3.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (RISCO-01, DIV-12, BUG-08).

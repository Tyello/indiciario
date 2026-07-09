# ISSUE-33.2 — Solvability Meter — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: STEP-07 concluído — todos os steps aprovados
LAST_COMPLETED_STEP: STEP-07
BLOCKER: none
```

## Contexto

Skill: `tdd` — código novo + schema novo; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-33.2_SPEC.md`. Alvos: `generator/solvability_meter.py` (novo), `schemas/solvability_report.schema.yaml` (novo), `tests/test_solvability_meter.py` (novo).

Ponto de atenção para o revisor: derivações de dificuldade e flags são **Python puro** (SM_003/SM_004) — nada disso é confiado ao modelo; e a doc deve carregar a nota de proxy (dificuldade para LLM ≠ dificuldade humana).

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/llm_blind_solver.py`, `generator/conclusion_judge.py`, `docs/DIFFICULTY_FRAMEWORK.md`, `framework/19_PLAYTEST_E_METRICAS.md`, fixtures de bundle usadas nas issues 33/33.1.
- Registrar no report: níveis exatos do DIFFICULTY_FRAMEWORK para o mapeamento SM_005 e a interface real do juiz.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.2*.md; .ai/skills/tdd.md; generator/llm_blind_solver.py; generator/conclusion_judge.py; generator/llm_provider.py; generator/fake_provider.py; docs/DIFFICULTY_FRAMEWORK.md; framework/19_PLAYTEST_E_METRICAS.md; tests/test_llm_blind_solver.py; tests/test_conclusion_judge.py
Editáveis: .ai/runs/ISSUE-33.2/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar código.
Done quando: report mapeia níveis do framework de dificuldade e interfaces consumidas.
Revisão: auto-approve (reading).
Dependências: ISSUE-33.1 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever `tests/test_solvability_meter.py` cobrindo os 8 casos da SPEC (caso 7 sem provider).
- Confirmar falha por módulo/schema inexistente.
Editáveis: tests/test_solvability_meter.py; .ai/runs/ISSUE-33.2/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_solvability_meter.py -q`
Proibido: criar módulos de produção.
Done quando: testes falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Criar `schemas/solvability_report.schema.yaml` e `generator/solvability_meter.py` (SM_001–SM_005).
Editáveis: generator/solvability_meter.py; schemas/solvability_report.schema.yaml; .ai/runs/ISSUE-33.2/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_solvability_meter.py -q`
Proibido: alterar solver, juiz, harness, gate.
Done quando: suite do arquivo passa 100%.
Revisão: revisor obrigatório — foco em SM_002 (falha parcial vs. total) e limiares de borda.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
- Limpar sem mudar comportamento.
Editáveis: generator/solvability_meter.py; tests/test_solvability_meter.py; .ai/runs/ISSUE-33.2/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_solvability_meter.py -q`; `ruff check generator/solvability_meter.py tests/test_solvability_meter.py`
Done quando: suite verde, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- Aplicar impacto documental da SPEC: `framework/19_PLAYTEST_E_METRICAS.md` ✅ (com nota de proxy), `docs/DIFFICULTY_FRAMEWORK.md` ✅ (cross-link), `docs/BLIND_SOLVER_HARNESS.md` ✅, `docs/ROADMAP.md` ✅, `docs/ESTADO_ATUAL.md` ✅, `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️.
Editáveis: framework/19_PLAYTEST_E_METRICAS.md; docs/DIFFICULTY_FRAMEWORK.md; docs/BLIND_SOLVER_HARNESS.md; docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-33.2/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados; nota de proxy presente.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo; schema novo carregável pelo `schema_loader`.
Editáveis: .ai/runs/ISSUE-33.2/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: sem regressão; falhas pré-existentes listadas.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-33.2/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.2.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat; bloqueada até merge da ISSUE-33.1.
- Desbloqueada e executada STEP-01–STEP-07 em sessão única (ISSUE-33 e ISSUE-33.1 já com STATUS: done na árvore de trabalho local). STATUS: done.

# ISSUE-30.9 — GP_004 isenta contratos de descarte

## Estado

```
STATUS: done
CURRENT_STEP: STEP-06
NEXT_ACTION: human
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-06
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-30.9/STEP-06_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-30.9/STEP-05_REVIEW.md
BLOCKER: none
```

## Contexto

Skill: `tdd` — defeito de métrica com contrato verificável; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-30.9_SPEC.md`. Alvo: `generator/clue_graph.py` (cálculo de `orphan_contracts`/`dead_ends` → `GP_004`). Testes: `tests/test_clue_graph.py`.

GP_004 é falso positivo em contratos `tipo: descarte` (confirmado na calibração 30.8). Isentar `tipo == descarte`. Sem schema novo.

## Steps

### STEP-01 — Leitura e ratificação
Status: pending | Owner: executor | Type: reading
- Ler SPEC, a função de detecção de órfãos em `clue_graph.py`, e o valor exato que o schema usa para `tipo` descarte (enum/string).
- Localizar o arquivo de teste do clue_graph e confirmar como instanciar o grafo a partir de um blueprint nos testes.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-30.9*.md; .ai/skills/tdd.md; generator/clue_graph.py; generator/models.py; tests/test_clue_graph.py; examples/caso_referencia_uma_noite_sem_flores.json
Editáveis: .ai/runs/ISSUE-30.9/STEP-01_EXECUTION.md
Comandos: nenhum
Done quando: report fixa o valor de `tipo` descarte e o ponto exato da edição.
Revisão: auto-approve (reading).

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever os 3 testes do SPEC. Rodar e confirmar que (1) falha hoje (GP_004 dispara para C-E1-DESCARTE), (2) e (3) conforme esperado.
Contexto permitido: .ai/issues/ISSUE-30.9*.md; .ai/runs/ISSUE-30.9/STEP-01_EXECUTION.md; generator/clue_graph.py (leitura); tests/test_clue_graph.py
Editáveis: tests/test_clue_graph.py; .ai/runs/ISSUE-30.9/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_clue_graph.py -q`
Proibido: alterar implementação.
Done quando: teste 1 falha por AssertionError; testes 2/3 conforme SPEC.
Revisão: revisor obrigatório.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar GP4-01..04 em `clue_graph.py`: excluir `tipo == descarte` do cálculo de órfãos/becos.
- Rodar `pytest tests/test_clue_graph.py -q` → 0 falhas.
Contexto permitido: .ai/issues/ISSUE-30.9*.md; .ai/runs/ISSUE-30.9/STEP-02*.md; generator/clue_graph.py; tests/test_clue_graph.py
Editáveis: generator/clue_graph.py; .ai/runs/ISSUE-30.9/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_clue_graph.py -q`
Proibido: tocar GP_003/GP_007; reescrever travessia; mudar schema.
Done quando: 3 testes passam; sem alteração fora da função alvo.
Revisão: revisor obrigatório.

### STEP-04 — DOCS
Status: pending | Owner: executor | Type: documentation
- `docs/GUIA_CODIGOS_ERROS.md` ✅ (GP_004 isenta descarte).
- `docs/ESTADO_ATUAL.md` ✅ (uma linha).
- `framework/08` / `docs/INDICE_DOCUMENTACAO.md` ⏭️ com motivo.
Editáveis: docs/GUIA_CODIGOS_ERROS.md; docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-30.9/STEP-04_EXECUTION.md
Comandos: nenhum
Revisão: auto-approve.

### STEP-05 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff check generator/ tests/` limpo.
- `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict` → exit 0, um aviso a menos (sem GP_004 para C-E1-DESCARTE).
Editáveis: .ai/runs/ISSUE-30.9/STEP-05_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`; `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`
Revisão: revisor obrigatório.

### STEP-06 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Arquivos alterados; impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-30.9/STEP-06_EXECUTION.md; .ai/issues/ISSUE-30.9.md (STATUS)
Comandos: `git diff --name-only`

## Auto-approve
reading (STEP-01), documentation (STEP-04), wrap-up (STEP-06).

## Revisor obrigatório
red (STEP-02), green (STEP-03), validation (STEP-05).

## Histórico
- STEP-00 gerado em chat; STEP-01 pronto.
- STEP-01 executado; auto-approved (low-risk, reading).
- STEP-02 executado; aguardando revisão.
- STEP-02 aprovado; aguardando orquestrador.
- Orquestrador avança para STEP-03 (GREEN).
- STEP-03 executado; 3 testes alvo + suíte completa de clue_graph passam (14/14); aguardando revisão.
- STEP-03 aprovado; aguardando orquestrador.
- Orquestrador avança para STEP-04 (DOCS).
- STEP-04 executado; auto-approved (low-risk, documentation).
- Orquestrador avança para STEP-05 (VALIDATION).
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado (DVG-EXEC-001 aceita, minor, não-bloqueante: ruff limpo interpretado como escopo dos arquivos tocados pela issue; 51 erros pré-existentes em main confirmados via git stash pelo revisor); aguardando orquestrador.
- Orquestrador avança para STEP-06 (WRAP-UP).
- STEP-06 executado; arquivos alterados listados, impacto documental resolvido; STATUS: done.

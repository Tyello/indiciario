# ISSUE-41.2 — Aposentar o espelho docs/prompts/ — passos

## Estado

```
STATUS: ready
CURRENT_STEP: STEP-01
NEXT_ACTION: executor roda STEP-01 (independente; pode paralelizar com 41.1)
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: none
```

## Contexto

Skill: `diagnose` + documentação — a fase crítica é o diff de preservação (SS_001), não a deleção.

Spec: `.ai/issues/ISSUE-41.2_SPEC.md`. Alvos: `docs/prompts/` (aposentadoria), `docs/INDICE_DOCUMENTACAO.md`, referências espalhadas.

## Steps

### STEP-01 — Diff de preservação (SS_001) + inventário de referências
Status: pending | Owner: executor | Type: reading
- Diff par a par dos 9 pares; classificar cada diferença: (a) skill mais nova → descartar lado prompts, (b) prompts com conteúdo único de valor → candidato a porte, (c) divergência trivial.
- Grep exaustivo de referências a `docs/prompts` e registrar decisão SS_002 (README de redirecionamento vs remoção total).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-41.2*.md; .ai/skills/ (todos); docs/prompts/ (todos); docs/INDICE_DOCUMENTACAO.md; CLAUDE.md; README.md
Editáveis: .ai/runs/ISSUE-41.2/STEP-01_EXECUTION.md
Comandos: `diff` par a par; `grep -rn "docs/prompts" .`
Proibido: remover ou editar qualquer arquivo.
Done quando: tabela de veredito por par + inventário de referências no report.
Revisão: revisor obrigatório — é aqui que se garante que nada de valor se perde.
Dependências: nenhuma.

### STEP-02 — Porte de conteúdo único (se houver)
Status: pending | Owner: executor | Type: green
- Aplicar em `.ai/skills/` somente os portes aprovados no STEP-01. Se nenhum: registrar e pular.
Editáveis: .ai/skills/*; .ai/runs/ISSUE-41.2/STEP-02_EXECUTION.md
Comandos: nenhum
Done quando: portes aplicados = exatamente os aprovados.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — Aposentadoria + atualização de referências (SS_002/003/004)
Status: pending | Owner: executor | Type: documentation
- Executar a decisão SS_002; atualizar todas as referências; atualizar o índice.
Editáveis: docs/prompts/ (remoção/README); docs/INDICE_DOCUMENTACAO.md; CLAUDE.md; AGENTS.md; README.md; docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-41.2/STEP-03_EXECUTION.md
Comandos: `grep -rn "docs/prompts" .`
Done quando: grep limpo (exceto README de redirecionamento, se mantido); índice atualizado.
Revisão: revisor obrigatório.
Dependências: STEP-02 aprovado.

### STEP-04 — VALIDATION
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`
Editáveis: .ai/runs/ISSUE-41.2/STEP-04_EXECUTION.md
Done quando: sem regressão.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — WRAP-UP
Editáveis: .ai/runs/ISSUE-41.2/STEP-05_EXECUTION.md; .ai/issues/ISSUE-41.2.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-04 aprovado.

## Auto-approve
wrap-up (STEP-05).

## Revisor obrigatório
STEP-01 (preservação), STEP-02, STEP-03, STEP-04.

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (DIV-09; decisão: aposentar, não sincronizar).

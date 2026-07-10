# ISSUE-41.3 — Reconciliação de estado documental — passos

## Estado

```
STATUS: ready
CURRENT_STEP: STEP-01
NEXT_ACTION: executor roda STEP-01 (recomendado após merge da 41.1 para registrar CI verde junto; não é bloqueio formal)
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: none
```

## Contexto

Skill: `grill-with-docs` — reconciliação guiada por evidência da auditoria, cada correção verificável por grep.

Spec: `.ai/issues/ISSUE-41.3_SPEC.md`. Sem código (exceto possível linha do ci.yml, RD_009).

Nota de sequenciamento: se executada após 33.3/41.2, incorporar os estados dessas issues na mesma passada (ROADMAP/ESTADO já saem completos).

## Steps

### STEP-01 — Leitura e coleta de valores reais
Status: pending | Owner: executor | Type: reading
- Ler SPEC e cada doc alvo; coletar valores do dia: `pytest --collect-only -q` (contagem), lista real de entregáveis 40.x (código + runs), fila real de issues.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-41.3*.md; .ai/skills/grill-with-docs.md; docs/AUDITORIA_FABLE_2026-07.md; docs/ROADMAP.md; docs/ESTADO_ATUAL.md; CLAUDE.md; README.md; framework/00_README.md; docs/INDICE_DOCUMENTACAO.md; docs/GUIA_CODIGOS_ERROS.md; docs/EXPERIMENTO_GERACAO_DO_ZERO.md; .ai/issues/ISSUE-40.*.md; .ai/ISSUE_TEMPLATE.md; .github/workflows/ci.yml; examples/ (listagem)
Editáveis: .ai/runs/ISSUE-41.3/STEP-01_EXECUTION.md
Comandos: `pytest --collect-only -q | tail -3`; greps da SPEC (baseline "antes")
Proibido: editar docs.
Done quando: valores reais coletados e baseline dos greps registrado.
Revisão: auto-approve (reading).
Dependências: nenhuma (ver nota de sequenciamento).

### STEP-02 — RD_001..RD_006 (estado e rosters)
Status: pending | Owner: executor | Type: documentation
Editáveis: docs/ROADMAP.md; docs/ESTADO_ATUAL.md; CLAUDE.md; AGENTS.md; framework/00_README.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-41.3/STEP-02_EXECUTION.md
Comandos: greps de verificação 1–5 da SPEC
Done quando: greps 1–5 passam.
Revisão: revisor obrigatório — fidelidade aos valores coletados no STEP-01, sem inflar entregáveis.
Dependências: STEP-01 aprovado.

### STEP-03 — RD_007..RD_009 (guia de códigos, headers 40.x, entrypoint)
Status: pending | Owner: executor | Type: documentation
Editáveis: docs/GUIA_CODIGOS_ERROS.md; .ai/issues/ISSUE-40.1.md a ISSUE-40.6.md (só headers de status); .ai/ISSUE_TEMPLATE.md; .github/workflows/ci.yml (só forma do comando, se RD_009 exigir); .ai/runs/ISSUE-41.3/STEP-03_EXECUTION.md
Comandos: greps 6–7 da SPEC
Done quando: greps passam; headers coerentes.
Revisão: revisor obrigatório.
Dependências: STEP-02 aprovado.

### STEP-04 — VALIDATION
Comandos: `pytest tests/ -q`; todos os greps da SPEC em sequência (registrar saída)
Editáveis: .ai/runs/ISSUE-41.3/STEP-04_EXECUTION.md
Done quando: suite sem regressão; greps 1–7 todos passando.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — WRAP-UP
Editáveis: .ai/runs/ISSUE-41.3/STEP-05_EXECUTION.md; .ai/issues/ISSUE-41.3.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-04 aprovado.

## Auto-approve
reading (STEP-01), wrap-up (STEP-05).

## Revisor obrigatório
documentation (STEP-02, STEP-03), validation (STEP-04).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (DIV-01..07, DIV-11, Melhoria-6).

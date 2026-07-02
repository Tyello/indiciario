# ISSUE-30.10 — Codificar padrões importados do corpus de calibração

## Estado

```
STATUS: done
CURRENT_STEP: STEP-06
NEXT_ACTION: none
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-06
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-30.10/STEP-06_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-30.10/STEP-05_REVIEW.md
BLOCKER: none
```

## Contexto

Skill: `grill-with-docs` — autoria de framework guiada por evidência (calibração + canônicos).

Spec: `.ai/issues/ISSUE-30.10_SPEC.md`. Alvos: `framework/08_MODELO_REFERENCIA.md` (primário), `framework/07_PROMPT_GERADOR_DE_CASO.md` (cross-link). Sem código.

Destila os padrões PAT-01..04 da calibração (30.8) para o modelo de referência, integrando à Parte 1 existente sem duplicar.

## Steps

### STEP-01 — Leitura e mapa de integração
Status: done (auto-approved) | Owner: executor | Type: reading
- Ler SPEC, `framework/08` inteiro, `framework/07`, `docs/CALIBRACAO_REFERENCIA_EXTERNA.md`, e o blueprint de calibração.
- Para cada PAT-01..04, identificar a subseção da Parte 1 com que se sobrepõe (1.2/1.3/1.5) e decidir integrar vs. nova subseção, registrando o mapa no report.
- Confirmar que os campos que cada padrão cita existem no schema.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-30.10*.md; .ai/skills/grill-with-docs.md; framework/08_MODELO_REFERENCIA.md; framework/07_PROMPT_GERADOR_DE_CASO.md; docs/CALIBRACAO_REFERENCIA_EXTERNA.md; examples/caso_referencia_uma_noite_sem_flores.json
Editáveis: .ai/runs/ISSUE-30.10/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar framework ou código.
Done quando: report traz o mapa de integração e a verificação de campos.
Revisão: auto-approve (reading).
Dependências: nenhuma.

### STEP-02 — Autoria dos padrões no framework/08
Status: pending | Owner: executor | Type: documentation
- Adicionar PAT-01..04 ao `framework/08`, cada um com os cinco elementos (definição, quando usar, campos, exemplo, modo de falha) e cross-ref à Parte 2 onde indicado.
- Não duplicar a Parte 1; integrar conforme o mapa do STEP-01.
Contexto permitido: .ai/issues/ISSUE-30.10*.md; .ai/runs/ISSUE-30.10/STEP-01_EXECUTION.md; framework/08_MODELO_REFERENCIA.md; examples/caso_referencia_uma_noite_sem_flores.json (leitura)
Editáveis: framework/08_MODELO_REFERENCIA.md; .ai/runs/ISSUE-30.10/STEP-02_EXECUTION.md
Comandos: nenhum
Proibido: alterar 07 (próximo step), código ou schema.
Done quando: PAT-01..04 presentes e completos.
Revisão: revisor obrigatório — fidelidade aos exemplos reais; ausência de duplicação.
Dependências: STEP-01 aprovado.

### STEP-03 — Cross-link no framework/07
Status: pending | Owner: executor | Type: documentation
- Adicionar PAT-05: ponteiro no `framework/07` instruindo o gerador a considerar PAT-01..04 pelo nome.
Contexto permitido: .ai/issues/ISSUE-30.10*.md; framework/07_PROMPT_GERADOR_DE_CASO.md; framework/08_MODELO_REFERENCIA.md (leitura)
Editáveis: framework/07_PROMPT_GERADOR_DE_CASO.md; .ai/runs/ISSUE-30.10/STEP-03_EXECUTION.md
Comandos: nenhum
Done quando: 07 referencia os quatro padrões pelo nome.
Revisão: auto-approve (documentation leve) ou revisor — à escolha do orquestrador.
Dependências: STEP-02 aprovado.

### STEP-04 — DOCS de impacto
Status: pending | Owner: executor | Type: documentation
- `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` ✅ (ponteiro de fechamento).
- `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️ (atualizar descrição do 08 se mudou materialmente).
- `docs/ESTADO_ATUAL.md` ✅ (uma linha).
Editáveis: docs/CALIBRACAO_REFERENCIA_EXTERNA.md; docs/INDICE_DOCUMENTACAO.md; docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-30.10/STEP-04_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-03 aprovado.

### STEP-05 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão (confirma que nenhum código foi tocado).
- Conferência manual: cada PAT cita campos/casos que existem.
Editáveis: .ai/runs/ISSUE-30.10/STEP-05_EXECUTION.md
Comandos: `pytest tests/ -q`
Done quando: suíte sem regressão; conferência registrada.
Revisão: revisor obrigatório.
Dependências: STEP-04 aprovado.

### STEP-06 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-30.10/STEP-06_EXECUTION.md; .ai/issues/ISSUE-30.10.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-05 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-04), wrap-up (STEP-06).

## Revisor obrigatório
documentation de conteúdo (STEP-02), validation (STEP-05).

## Histórico
- STEP-00 gerado em chat; STEP-01 pronto.
- STEP-01 executado; aguardando revisão.
- STEP-01 auto-aprovado (reading). STEP-02 pronto.
- STEP-02 executado; aguardando revisão.
- STEP-02 aprovado; aguardando orquestrador.
- STEP-03 executado; aguardando revisão.
- STEP-04 executado; aguardando revisão.
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado; aguardando orquestrador.
- STEP-06 executado (wrap-up); impacto documental resolvido; STATUS: done.

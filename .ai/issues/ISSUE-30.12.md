# ISSUE-30.12 — Gate estrutural entre blueprint e documentos finais

## Estado

```
STATUS: pending
CURRENT_STEP: STEP-01
NEXT_ACTION: executor
REVIEW_STATUS: none
LAST_COMPLETED_STEP: none
LAST_EXECUTION_REPORT: none
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

Skill: `grill-with-docs` — autoria de framework guiada por evidência (achado real da ISSUE-30.11, não hipótese).

Spec: `.ai/issues/ISSUE-30.12_SPEC.md`. Alvo primário: `framework/07_PROMPT_GERADOR_DE_CASO.md`. Alvos secundários: `docs/CASE_GENERATION_WORKFLOW.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`. Sem código.

Origem: STEP-02/STEP-03 da ISSUE-30.11 geraram o blueprint completo (esqueleto + 17 documentos) numa única passada; só depois de tudo escrito o STEP-03 descobriu 327 erros de construção Pydantic, exigindo reescrita estrutural total. Esta issue codifica, como regra de processo no `framework/07`, a verificação de forma do esqueleto **antes** da Fase 2 (documentos finais) — independente do resultado do playtest humano pendente na 30.11.

## Steps

### STEP-01 — Leitura e mapa de integração
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `framework/07_PROMPT_GERADOR_DE_CASO.md` inteiro, `docs/CASE_GENERATION_WORKFLOW.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`, `docs/CONTEUDO_SCHEMA.md`.
- Ler `.ai/runs/ISSUE-30.11/STEP-02_EXECUTION.md`, `STEP-02_REVIEW.md` e `STEP-03_EXECUTION.md` para confirmar a evidência citada na SPEC (327 erros Pydantic, quais campos).
- Confirmar o ponto exato de inserção no 07 (entre o fim do `## GATE DE QUALIDADE` e o início de `## ENTREGÁVEIS — NESTA ORDEM`) e registrar no report.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-30.12*.md; .ai/skills/grill-with-docs.md; framework/07_PROMPT_GERADOR_DE_CASO.md; docs/CASE_GENERATION_WORKFLOW.md; docs/BLUEPRINT_AUTHORING_GUIDE.md; docs/CONTEUDO_SCHEMA.md; .ai/runs/ISSUE-30.11/STEP-02_EXECUTION.md; .ai/runs/ISSUE-30.11/STEP-02_REVIEW.md; .ai/runs/ISSUE-30.11/STEP-03_EXECUTION.md
Editáveis: .ai/runs/ISSUE-30.12/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar framework, docs de destino ou código.
Done quando: report confirma o ponto de inserção e cita a evidência da 30.11 com precisão (arquivo + números reais, não parafraseados).
Revisão: auto-approve (reading).
Dependências: nenhuma.

### STEP-02 — Autoria do GATE ESTRUTURAL no framework/07
Status: pending | Owner: executor | Type: documentation
- Inserir a subseção `## GATE ESTRUTURAL — OBRIGATÓRIO ENTRE A FASE 1 E A FASE 2` no local mapeado no STEP-01, com o texto do contrato da SPEC.
- Adicionar a frase de enquadramento em `## ENTREGÁVEIS — NESTA ORDEM`.
- Não tocar no `## GATE DE QUALIDADE` narrativo existente.
Contexto permitido: .ai/issues/ISSUE-30.12*.md; .ai/runs/ISSUE-30.12/STEP-01_EXECUTION.md; framework/07_PROMPT_GERADOR_DE_CASO.md
Editáveis: framework/07_PROMPT_GERADOR_DE_CASO.md; .ai/runs/ISSUE-30.12/STEP-02_EXECUTION.md
Comandos: nenhum
Proibido: alterar o gate narrativo existente; alterar docs secundários (próximo step).
Done quando: subseção presente no local certo; frase de enquadramento presente; gate narrativo intacto.
Revisão: revisor obrigatório — fidelidade ao contrato da SPEC; confirmar que o gate narrativo não foi tocado.
Dependências: STEP-01 aprovado.

### STEP-03 — Cross-link em CASE_GENERATION_WORKFLOW.md e BLUEPRINT_AUTHORING_GUIDE.md
Status: pending | Owner: executor | Type: documentation
- Adicionar a nota de cross-referência na seção 2 (Geração) do `CASE_GENERATION_WORKFLOW.md`.
- Adicionar a nota de cross-referência no `BLUEPRINT_AUTHORING_GUIDE.md`, distinguindo o gate de forma do checklist narrativo existente.
Contexto permitido: .ai/issues/ISSUE-30.12*.md; framework/07_PROMPT_GERADOR_DE_CASO.md (leitura, já com o gate); docs/CASE_GENERATION_WORKFLOW.md; docs/BLUEPRINT_AUTHORING_GUIDE.md
Editáveis: docs/CASE_GENERATION_WORKFLOW.md; docs/BLUEPRINT_AUTHORING_GUIDE.md; .ai/runs/ISSUE-30.12/STEP-03_EXECUTION.md
Comandos: nenhum
Done quando: ambos os docs referenciam o gate pelo nome/local exato no 07, sem duplicar o texto do gate.
Revisão: auto-approve (documentation leve) ou revisor — à escolha do orquestrador.
Dependências: STEP-02 aprovado.

### STEP-04 — DOCS de impacto
Status: pending | Owner: executor | Type: documentation
- `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` ✅ (linha fechando o ciclo: achado STEP-02/03 da 30.11 → regra de processo via 30.12).
- `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️ (confirmar se a coluna "Atualizar quando" do 07 já cobre; registrar motivo se ⏭️).
- `docs/ESTADO_ATUAL.md` ✅ (uma linha).
- `CLAUDE.md` ✅/⏭️ (ponteiro de próxima issue, se aplicável no momento do merge).
Editáveis: docs/EXPERIMENTO_GERACAO_DO_ZERO.md; docs/INDICE_DOCUMENTACAO.md; docs/ESTADO_ATUAL.md; CLAUDE.md; .ai/runs/ISSUE-30.12/STEP-04_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-03 aprovado.

### STEP-05 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão (confirma que nenhum código foi tocado).
- Rodar `python -m generator.validator examples/caso_canonico_iniciante.json --strict` para confirmar que o comando citado no gate funciona contra um blueprint válido.
- Rodar o mesmo comando contra uma cópia temporária (fora do repo/não commitada) com um campo deliberadamente malformado, confirmando que o erro de construção aparece como esperado. Descartar a cópia depois.
Editáveis: .ai/runs/ISSUE-30.12/STEP-05_EXECUTION.md
Comandos: `pytest tests/ -q`; `python -m generator.validator examples/caso_canonico_iniciante.json --strict`
Done quando: suíte sem regressão; comando do gate confirmado funcional nos dois sentidos (positivo e negativo).
Revisão: revisor obrigatório.
Dependências: STEP-04 aprovado.

### STEP-06 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-30.12/STEP-06_EXECUTION.md; .ai/issues/ISSUE-30.12.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-05 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-04), wrap-up (STEP-06).

## Revisor obrigatório
documentation de conteúdo (STEP-02), validation (STEP-05).

## Histórico
- STEP-00 gerado em chat; STEP-01 pronto.

# STEP-03 — Retirada do espelho e atualização de referências (ISSUE-41.2)

## SS_002 — decisão binária

Sem evidência de links externos apontando pros arquivos de `docs/prompts/` (repo privado, sem
publicação externa desses caminhos). Decisão: **manter `docs/prompts/README.md` único de
redirecionamento**, apagar os 8 arquivos de skill.

## Arquivos removidos

`docs/prompts/{diagnose,grill_with_docs,handoff,improve_codebase_architecture,tdd,to_issues,to_prd,zoom_out}.md`

## Arquivo reescrito

`docs/prompts/README.md` — nota de aposentadoria + link pra `.ai/skills/`.

## Referências atualizadas (SS_003)

- `docs/INDICE_DOCUMENTACAO.md` — linha 40 (removida menção ao espelho no gatilho "skill nova/alterada");
  linha 163 removida (entrada do espelho na tabela de `docs/`).
- `docs/AGENT_SKILLS.md` — 8 links da tabela de skills + 3 exemplos de "forma curta" + 1 frase de
  resolução de nome de skill, todos apontando agora para `.ai/skills/*.md`.
- `docs/ESTADO_ATUAL.md` — 1 linha registrando a aposentadoria (ISSUE-41.2).

## Exceção deliberada — não atualizado

`docs/AUDITORIA_FABLE_2026-07.md` (DIV-09, linha 143) mantido como está: é um snapshot histórico
datado de auditoria, não uma instrução ativa. Reescrever o achado para refletir o estado pós-fix
falsificaria o registro do que foi encontrado na auditoria. Precedente: `CLAUDE.md` já resolve isso
declarando que `docs/ESTADO_ATUAL.md` prevalece em conflito sobre estado — a auditoria não precisa
ser mantida sincronizada com o presente.

`CLAUDE.md` e `AGENTS.md` — grep confirmou zero referências a `docs/prompts`; nenhuma mudança
necessária (o impacto documental da issue previa isso como condicional: "se referenciarem o espelho").

Referências remanescentes fora do escopo de atualização: os próprios `.ai/issues/ISSUE-41.2*.md` e
`.ai/runs/ISSUE-41.2/*` (documentam esta própria retirada, não são referências órfãs).

Revisão: mecânica, seguindo decisão aprovada no STEP-01.

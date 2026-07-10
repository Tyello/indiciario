# ISSUE-41.2 — Aposentar o espelho docs/prompts/ (single-sourcing das skills)

## Contexto

Os 9 pares `docs/prompts/*` ↔ `.ai/skills/*` divergem todos (69–120 linhas cada — AUDITORIA, DIV-09), apesar da instrução "manter em sincronia" no índice. O princípio do projeto já decidiu a questão: espelhos redundantes divergem e criam dívida de manutenção; `.ai/skills/` é a fonte autoritativa. Entre criar um guard de sincronia no CI e aposentar o espelho, esta issue **aposenta** — um guard perpetuaria a duplicação que o princípio condena.

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — DIV-09, EVO ISSUE-41.2 (opção "aposentar").

## Objetivo

`docs/prompts/` deixa de existir como conteúdo duplicado; toda referência aponta para `.ai/skills/` e nenhuma instrução de sincronia sobrevive.

## Fora de escopo

- Alterar o conteúdo de qualquer skill em `.ai/skills/`.
- Criar tooling de sincronia (rejeitado por princípio).

## Contrato / regras

| Código | Regra |
|---|---|
| `SS_001` | Antes de remover, diff par a par registrado no run report; se algum arquivo de `docs/prompts/` contiver conteúdo **mais novo/único** ausente da skill correspondente, a diferença é portada para `.ai/skills/` primeiro (com aprovação do revisor) — nada de valor se perde na aposentadoria. |
| `SS_002` | `docs/prompts/` é removido e substituído por um único `docs/prompts/README.md` de redirecionamento ("conteúdo vive em `.ai/skills/`; este diretório foi aposentado na ISSUE-41.2"), ou removido por completo com redirecionamento no índice — decisão binária registrada no STEP-01 conforme houver links externos apontando para os arquivos. |
| `SS_003` | Toda referência a `docs/prompts/` no repo (grep exaustivo: docs/, framework/, .ai/, CLAUDE.md, AGENTS.md, README.md) é atualizada para `.ai/skills/`. |
| `SS_004` | `docs/INDICE_DOCUMENTACAO.md`: entrada do espelho aposentada; regra "manter em sincronia" removida; `.ai/skills/` registrado como fonte única. |

## Impacto documental

- [ ] `docs/INDICE_DOCUMENTACAO.md` — motivo: SS_004 (aposentadoria formal).
- [ ] `CLAUDE.md` / `AGENTS.md` — motivo: SS_003, se referenciarem o espelho.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.

## Casos de teste (TDD)

Issue majoritariamente documental; verificação por comandos:

1. SS_001: report do diff par a par com veredito por arquivo (portado / descartado com motivo).
2. SS_003: `grep -rn "docs/prompts" . --include="*.md" --include="*.py" --include="*.yaml"` → zero ocorrências fora do README de redirecionamento (se mantido).
3. `pytest tests/ -q` sem regressão (nenhum teste pode depender do espelho; se depender, é achado a registrar e corrigir aqui).

## Restrições arquiteturais

Herdar as padrão. Nenhuma skill alterada exceto porte aprovado via SS_001. Sem tooling novo.

## Critério de aceite

- [ ] Diff par a par registrado; conteúdo único portado ou descartado com motivo
- [ ] Zero referência órfã a `docs/prompts/`
- [ ] Índice reflete a fonte única
- [ ] pytest tests/ -q sem regressão

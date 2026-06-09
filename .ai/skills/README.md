# .ai/skills

Skills operacionais carregáveis por agentes no Indiciário.

Antes de executar qualquer tarefa, o agente deve:

1. ler `AGENTS.md`;
2. ler `docs/LLM_CONTEXT.md`;
3. identificar a skill adequada nesta pasta;
4. carregar o arquivo correspondente;
5. executar seguindo a skill.

## Mapa de seleção

| Situação | Skill | Arquivo |
|---|---|---|
| Bug, regressão, falha de PDF/build/validator ou causa desconhecida | `diagnose` | `.ai/skills/diagnose.md` |
| Mudança em código, validator, schema, renderer, package builder ou regra automatizável | `tdd` | `.ai/skills/tdd.md` |
| Mudança editorial, progressão, envelopes, dicas, mapas ou guia | `grill-with-docs` | `.ai/skills/grill-with-docs.md` |
| Iniciativa grande demais para uma PR | `to-prd` | `.ai/skills/to-prd.md` |
| Quebrar PRD, roadmap ou playtest em tarefas pequenas | `to-issues` | `.ai/skills/to-issues.md` |
| Encerrar rodada e passar contexto | `handoff` | `.ai/skills/handoff.md` |
| Entender fluxo antes de mexer | `zoom-out` | `.ai/skills/zoom-out.md` |
| Revisão arquitetural explícita e incremental | `improve-codebase-architecture` | `.ai/skills/improve-codebase-architecture.md` |

## Regra de desempate

- Causa desconhecida: `diagnose`.
- Regra nova automatizável: `tdd`.
- Decisão editorial/produto: `grill-with-docs`.
- Escopo grande: `to-prd` antes de implementar.
- Contexto confuso: `zoom-out` antes de qualquer mudança.

## Obrigatório na resposta final do agente

- skill escolhida;
- motivo da escolha;
- arquivos alterados;
- comandos executados;
- resultados ou limitações;
- pendências reais.

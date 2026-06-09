# Prompts reutilizáveis

Esta pasta implementa o nível 3 de uso das skills no Indiciário: prompts especializados versionados no próprio repositório.

Use estes arquivos diretamente em Codex, Claude Code, ChatGPT ou outro agente compatível.

## Skills disponíveis

| Skill | Arquivo | Uso típico |
|---|---|---|
| `diagnose` | [`diagnose.md`](diagnose.md) | Investigar bug, regressão, PDF quebrado, erro de build ou causa desconhecida. |
| `tdd` | [`tdd.md`](tdd.md) | Implementar regra técnica/editorial protegida por teste. |
| `grill-with-docs` | [`grill_with_docs.md`](grill_with_docs.md) | Confrontar mudança com docs antes de mexer em produto/editorial. |
| `to-prd` | [`to_prd.md`](to_prd.md) | Transformar iniciativa grande em PRD curto. |
| `to-issues` | [`to_issues.md`](to_issues.md) | Quebrar PRD/roadmap/playtest em issues pequenas. |
| `handoff` | [`handoff.md`](handoff.md) | Registrar estado para próximo agente/rodada. |
| `zoom-out` | [`zoom_out.md`](zoom_out.md) | Entender fluxo e ponto mínimo de mudança antes de implementar. |
| `improve-codebase-architecture` | [`improve_codebase_architecture.md`](improve_codebase_architecture.md) | Revisar arquitetura de forma incremental e sem feature nova. |

## Como chamar

Forma explícita:

```text
Use docs/prompts/diagnose.md para investigar o problema abaixo.
```

Forma curta:

```text
Use a skill diagnose.
```

Quando usar a forma curta, o agente deve resolver o nome da skill para o arquivo correspondente nesta pasta.

## Regras globais

1. Leia `AGENTS.md` antes de executar qualquer prompt.
2. Use `docs/AGENT_SKILLS.md` como índice e matriz de escolha.
3. Não use prompts para abrir escopo além da prioridade atual.
4. Baseline visual real exige Playwright/Chromium.
5. Documento de jogador contém evidência bruta, não interpretação do autor.

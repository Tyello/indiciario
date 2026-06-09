# Skills operacionais para agentes

Este guia adapta, para o Indiciário, o uso das skills de engenharia do repositório `mattpocock/skills`.

A regra central é simples: use skills para melhorar diagnóstico, decisão e entrega incremental. Não use skills para abrir novas frentes antes de baseline visual real e playtest.

## Skills adotadas

| Skill | Quando usar no Indiciário | Saída esperada |
|---|---|---|
| `diagnose` | Bugs difíceis de PDF, Playwright, merge, layout, placeholders, manifests, validação ou regressão visual. | Reprodução mínima, hipótese, instrumentação, correção pequena e teste de regressão. |
| `tdd` | Mudanças em `validator`, schemas YAML, `case_kernel`, `case_review`, renderer, package builder, manifests e casos canônicos. | Red → green → refactor, com teste protegendo a regra editorial/técnica. |
| `grill-with-docs` | Antes de alterar regra editorial, progressão de envelopes, mapas, dicas, guia do facilitador ou contrato de blueprint. | Decisão confrontada com docs atuais e, se necessário, atualização de documentação. |
| `to-prd` | Features médias/grandes: novo sistema de playtest, biblioteca visual, novo caso canônico, mudança no pipeline de geração. | PRD curto, com objetivo, não-objetivos, escopo, critérios de aceitação e riscos. |
| `to-issues` | Quebrar PRD, roadmap ou revisão de playtest em tarefas executáveis para Codex. | Issues pequenas, independentes e verticais. |
| `handoff` | Encerrar uma rodada de Codex/Claude/ChatGPT deixando contexto seguro para a próxima. | Resumo do estado, arquivos alterados, validações, pendências e próximos passos. |
| `zoom-out` | Quando o agente estiver preso em detalhe de implementação ou risco de refatorar sem entender o fluxo. | Explicação de alto nível do fluxo afetado e do menor ponto correto de mudança. |
| `improve-codebase-architecture` | Apenas em ciclos específicos de arquitetura, não durante hardening pré-playtest. | Diagnóstico arquitetural com mudanças incrementais e reversíveis. |

## Skills não priorizadas agora

Não usar como fluxo padrão nesta fase:

- `prototype`, salvo para variação descartável de layout/mapa sem entrar no pipeline principal;
- `triage`, salvo quando houver muitas issues abertas;
- `setup-matt-pocock-skills`, porque este guia já define a adaptação local;
- skills pessoais, depreciadas ou de ensino que não movem baseline/playtest.

## Escolha rápida

Use esta matriz antes de iniciar uma tarefa:

| Situação | Skill principal |
|---|---|
| Algo quebrou e a causa não é óbvia | `diagnose` |
| Vou alterar código de validação/renderização/pacote | `tdd` |
| Vou mexer em regra editorial ou experiência do jogador | `grill-with-docs` |
| A mudança parece grande demais para uma PR | `to-prd` → `to-issues` |
| O contexto está confuso ou espalhado | `zoom-out` |
| Vou passar a tarefa para outro agente | `handoff` |
| Quero revisar arquitetura sem feature nova | `improve-codebase-architecture` |

## Como usar em prompts para Codex

### Diagnóstico

```text
Use a abordagem diagnose.
Reproduza o problema no menor escopo possível, formule hipóteses, instrumente só o necessário, corrija a menor causa comprovada e adicione teste de regressão.
Não refatore áreas não relacionadas.
No final, reporte comandos executados e limitações de ambiente.
```

### TDD

```text
Use a abordagem tdd.
Antes de implementar, escreva ou ajuste um teste que falhe pela regra desejada.
Implemente o menor código/conteúdo para passar.
Depois refatore sem mudar comportamento.
Valide com pytest, ruff quando houver Python e validator strict quando tocar blueprint/casos.
```

### Grill with docs

```text
Use a abordagem grill-with-docs.
Leia README.md, AGENTS.md e os docs relacionados antes de propor alteração.
Questione se a mudança preserva offline-first, solvabilidade, imersão, separação entre evidência bruta e interpretação, e prioridade de baseline/playtest.
Se a decisão mudar regra do produto, atualize a documentação junto.
```

### PRD e issues

```text
Use to-prd e depois to-issues.
Crie um PRD curto com objetivo, não-objetivos, escopo, critérios de aceitação, riscos e validação.
Depois quebre em issues pequenas, cada uma com entrega testável e sem misturar editorial, renderização e arquitetura quando possível.
```

### Handoff

```text
Use handoff.
Registre: objetivo, estado atual, arquivos alterados, decisões tomadas, comandos executados, limitações de ambiente, riscos e próximo passo recomendado.
Não esconda falhas de build, Playwright, PDF ou validator.
```

## Guardrails do Indiciário

Mesmo usando skills, estas regras prevalecem:

1. Documento de jogador contém evidência bruta, não interpretação do autor.
2. Guia do facilitador, dicas e relatórios podem explicar; documentos diegéticos não.
3. Mapas são plantas operacionais neutras, não solução visual.
4. Baseline visual real exige Playwright/Chromium; PDF fake não prova visual.
5. Playtest e evidência concreta valem mais que refatoração teórica.
6. Não abrir marketplace, banco, Telegram comercial, dashboard ou IA de imagem sem instrução explícita.
7. PR pequena e vertical é melhor que pacote amplo.

## Critério mínimo de conclusão

Toda tarefa conduzida com estas skills deve terminar com:

- resumo objetivo do que mudou;
- arquivos alterados;
- comandos executados;
- resultado de testes/validators/build;
- falhas ou limitações de ambiente explicitadas;
- próximos passos se houver pendência real.

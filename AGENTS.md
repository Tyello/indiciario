# AGENTS.md — Guia operacional para agentes de IA

Este arquivo é obrigatório para qualquer agente que trabalhe no repositório Indiciário.

## Protocolo automático obrigatório

Antes de executar qualquer tarefa, o agente deve seguir esta ordem:

1. Ler `AGENTS.md`.
2. Ler `docs/LLM_CONTEXT.md`.
3. Identificar a skill adequada para a tarefa.
4. Carregar a skill correspondente em `.ai/skills/`.
5. Executar seguindo o procedimento da skill carregada.
6. Informar na resposta final qual skill foi usada e por quê.

Nenhuma tarefa deve ser executada sem seleção explícita de skill.

## Mapa de skills

| Situação | Skill | Arquivo |
|---|---|---|
| Bug, regressão, erro de build, PDF quebrado, validator falhando ou causa desconhecida | `diagnose` | `.ai/skills/diagnose.md` |
| Mudança em código, validator, schema, renderer, package builder ou regra automatizável | `tdd` | `.ai/skills/tdd.md` |
| Mudança editorial, progressão, envelopes, dificuldade, dicas, mapas ou guia do facilitador | `grill-with-docs` | `.ai/skills/grill-with-docs.md` |
| Tarefa grande demais para uma PR pequena | `to-prd` | `.ai/skills/to-prd.md` |
| Quebrar PRD, roadmap, auditoria ou playtest em tarefas pequenas | `to-issues` | `.ai/skills/to-issues.md` |
| Encerrar rodada e registrar contexto para outro agente | `handoff` | `.ai/skills/handoff.md` |
| Contexto confuso ou risco de alterar o lugar errado | `zoom-out` | `.ai/skills/zoom-out.md` |
| Revisão arquitetural explícita e incremental | `improve-codebase-architecture` | `.ai/skills/improve-codebase-architecture.md` |


## Skills multiagente futuras

As skills listadas no mapa acima são as únicas disponíveis para seleção operacional hoje. O roadmap multiagente registra três skills futuras — `context-firewall`, `blind-solve` e `playtest-to-learning` — mas elas estão **PLANNED — NOT IMPLEMENTED** e não existem como arquivos em `.ai/skills/`. Consulte `docs/AGENT_SKILLS.md` para o mapa detalhado e a distinção entre skill, papel, protocolo e capacidade técnica.

Referências normativas para esse roadmap:

- `docs/MULTIAGENT_OPERATING_PROTOCOL.md`;
- `docs/BLIND_CONTEXT_PROTOCOL.md`;
- `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`;
- `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md`.

Regra operacional:

- se a skill existe em `.ai/skills/`, ela pode ser usada conforme sua documentação;
- se uma skill está marcada como futura ou planejada, o agente **não deve invocá-la, simulá-la ou tratá-la como capacidade existente**;
- até a implementação formal, use a skill existente mais adequada: `grill-with-docs` para revisão documental/segurança de contexto, `to-prd` para arquitetura ou escopo amplo, `to-issues` para decomposição aprovada, `diagnose` para depuração e `tdd` para implementação com testes;
- tarefas arquiteturais ou documentais continuam seguindo `to-prd`, `to-issues` ou `grill-with-docs`, conforme o caso;
- tarefas de implementação devem seguir a decomposição aprovada e não prometer bundling, isolamento, hashing, validação, orquestração, Gate Evaluator ou Learning Loop antes das issues correspondentes.

A existência de um protocolo ou de uma entrada no roadmap não significa que a skill ou a capacidade técnica já exista.

## Regra de desempate

- Causa desconhecida: use `diagnose`.
- Regra nova testável: use `tdd`.
- Decisão editorial ou experiência do jogador: use `grill-with-docs`.
- Escopo grande ou nebuloso: use `zoom-out` antes de implementar.
- Iniciativa de produto ou roadmap: use `to-prd` antes de implementar.

## Contexto obrigatório

Depois deste arquivo, carregue sempre:

- `docs/LLM_CONTEXT.md`;
- `.ai/skills/README.md`;
- a skill selecionada em `.ai/skills/`.

Consulte também, conforme a tarefa:

- `README.md`;
- `docs/ESTADO_ATUAL.md`;
- `docs/ROADMAP.md`;
- `docs/DIRETRIZES_EDITORIAIS.md`;
- `docs/LLM_OPERATING_MANUAL.md`;
- `docs/CASE_DESIGN_PIPELINE.md`;
- `docs/BLUEPRINT_AUTHORING_GUIDE.md`;
- `docs/DIFFICULTY_FRAMEWORK.md`;
- `docs/CASE_GENERATION_WORKFLOW.md`;
- `docs/VISUAL_SYSTEM.md`;
- `docs/FLOORPLANS.md`;
- `docs/PRINTABLES.md`;
- `docs/SIGNATURES_AND_HANDWRITING.md`.

## Princípios do Indiciário

Indiciário é um framework para mistérios investigativos jogáveis em grupo, em formato de dossiê com envelopes, documentos, pistas, dicas, guia do facilitador e PDFs finais.

Princípios:

- offline-first;
- sem QR code obrigatório;
- sem internet obrigatória;
- sem aplicativo externo obrigatório;
- sem links externos como parte da solução;
- foco em dedução, investigação, impressão e experiência de grupo.

Slogan:

> Todo caso deixa sinais.

## Fluxo oficial

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library / templates
→ Build Package
→ Baseline visual real
→ Playtest
→ Ajustes finos
```

## Regras editoriais centrais

1. Documento de jogador contém evidência bruta, não interpretação do autor.
2. Guia do facilitador, dicas e relatórios podem explicar; documentos diegéticos não.
3. Mapas são plantas operacionais neutras, não solução visual.
4. Documento comercial deve parecer documento real, não síntese do puzzle.
5. Dicas destravam grupos; não substituem investigação.
6. Baseline visual real exige Playwright/Chromium. PDF fake não prova qualidade visual.

## Casos canônicos

1. **O Desvio da Reserva Mirante**
   - `examples/caso_canonico_iniciante.json`;
   - régua Iniciante.

2. **O Último Brinde do Hotel Aurora**
   - `examples/caso_canonico_intermediario.json`;
   - régua Intermediária;
   - deve permanecer sem mapa, salvo evidência nova ou instrução explícita.

## Prioridade atual

1. Operar pelo fluxo oficial.
2. Gerar baseline visual real dos canônicos com Playwright/Chromium.
3. Revisar PDFs, manifests e print manifests.
4. Realizar novo playtest do Intermediário.
5. Registrar travamentos, hipóteses erradas, tempo real, uso de dicas/cartões e diversão percebida.
6. Só depois decidir ajustes finos ou planejar canônico Avançado.

## Fora de prioridade sem instrução explícita

Não implementar por iniciativa própria:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- geração em massa;
- pagamento;
- IA gerando imagens;
- canônico Avançado antes de baseline visual e novo playtest.

## Comandos obrigatórios

Testes:

```bash
pytest tests/ -q
```

Lint quando tocar Python:

```bash
ruff check generator/
```

Validator strict dos canônicos quando tocar blueprint, schema, validator, documentação de estado ou pacote:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
python generator/validator.py examples/caso_canonico_intermediario.json --strict
```

Build real quando tocar renderização ou pacote:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Se Playwright/Chromium não estiver instalado:

```bash
python -m playwright install chromium
```

Se o build real não for possível por limitação de ambiente, registre isso explicitamente. Não use PDF fake como prova de baseline visual real.

## Critério de tarefa concluída

Uma tarefa só está concluída quando:

- a skill usada foi informada;
- o motivo da escolha foi informado;
- os arquivos alterados foram listados;
- os comandos executados foram listados;
- os resultados ou limitações foram explicitados;
- mudanças editoriais não vazam gabarito para documentos de jogador;
- a PR ou resposta explica claramente o que mudou, por que mudou e como foi validado.

# Skills operacionais para agentes

Este guia adapta, para o Indiciário, o uso das skills de engenharia do repositório `mattpocock/skills` e registra o mapa de evolução das futuras skills multiagente.

A regra central é simples: use skills para melhorar diagnóstico, decisão e entrega incremental. Não use skills para abrir novas frentes antes de baseline visual real e playtest.

## Conceitos fundamentais

Os termos abaixo devem permanecer separados em qualquer tarefa, PR ou run multiagente:

- **Skill**: procedimento reutilizável que orienta como executar uma tarefa.
- **Papel**: responsabilidade assumida por um agente em uma run, como Blind Solver, Gate Evaluator ou moderador.
- **Protocolo**: documento normativo que define regras, limites, segurança e governança.
- **Capacidade técnica**: código ou infraestrutura que executa funções como bundling, isolamento, hashing, validação ou orquestração.

A existência de um protocolo ou de uma entrada no roadmap não significa que a skill ou a capacidade técnica já exista. Um papel como Blind Solver pode estar descrito nos protocolos sem que a skill `blind-solve` esteja disponível; uma capacidade conceitual como Context Firewall pode estar especificada sem que exista implementação, sandbox, manifest executável ou skill operacional.

## Skills adotadas

| Skill | Quando usar no Indiciário | Prompt reutilizável | Saída esperada |
|---|---|---|---|
| `diagnose` | Bugs difíceis de PDF, Playwright, merge, layout, placeholders, manifests, validação ou regressão visual. | [`docs/prompts/diagnose.md`](prompts/diagnose.md) | Reprodução mínima, hipótese, instrumentação, correção pequena e teste de regressão. |
| `tdd` | Mudanças em `validator`, schemas YAML, `case_kernel`, `case_review`, renderer, package builder, manifests e casos canônicos. | [`docs/prompts/tdd.md`](prompts/tdd.md) | Red → green → refactor, com teste protegendo a regra editorial/técnica. |
| `grill-with-docs` | Antes de alterar regra editorial, progressão de envelopes, mapas, dicas, guia do facilitador, contrato de blueprint ou documentação que oriente seleção de skills. | [`docs/prompts/grill_with_docs.md`](prompts/grill_with_docs.md) | Decisão confrontada com docs atuais e, se necessário, atualização de documentação. |
| `to-prd` | Features médias/grandes: novo sistema de playtest, biblioteca visual, novo caso canônico, mudança no pipeline de geração. | [`docs/prompts/to_prd.md`](prompts/to_prd.md) | PRD curto, com objetivo, não-objetivos, escopo, critérios de aceitação e riscos. |
| `to-issues` | Quebrar PRD, roadmap ou revisão de playtest em tarefas executáveis para Codex. | [`docs/prompts/to_issues.md`](prompts/to_issues.md) | Issues pequenas, independentes e verticais. |
| `handoff` | Encerrar uma rodada de Codex/Claude/ChatGPT deixando contexto seguro para a próxima. | [`docs/prompts/handoff.md`](prompts/handoff.md) | Resumo do estado, arquivos alterados, validações, pendências e próximos passos. |
| `zoom-out` | Quando o agente estiver preso em detalhe de implementação ou risco de refatorar sem entender o fluxo. | [`docs/prompts/zoom_out.md`](prompts/zoom_out.md) | Explicação de alto nível do fluxo afetado e do menor ponto correto de mudança. |
| `improve-codebase-architecture` | Apenas em ciclos específicos de arquitetura, não durante hardening pré-playtest. | [`docs/prompts/improve_codebase_architecture.md`](prompts/improve_codebase_architecture.md) | Diagnóstico arquitetural com mudanças incrementais e reversíveis. |

## Skills multiagente planejadas

As skills multiagente serão criadas para transformar os protocolos aprovados em procedimentos operacionais repetíveis, auditáveis e seguros. Elas devem ajudar agentes humanos ou LLMs a preparar contexto, executar resolução cega e converter playtests em aprendizado sem confundir revisão documental com capacidade técnica.

Elas ainda não estão disponíveis porque os protocolos atuais são normativos e conceituais, mas nem todos os contratos, schemas, manifests, políticas de visibilidade, bundles, Gate Evaluators, ferramentas de validação e pilotos existem. Nenhuma skill planejada deve ser invocada, simulada ou tratada como disponível antes de cumprir as regras de ativação futura.

### Estado e disponibilidade

| Skill | Estado | Pode ser usada? | Pré-requisito principal |
|---|---|---|---|
| `context-firewall` | PLANNED | Não | Manifest e política de visibilidade |
| `blind-solve` | PLANNED | Não | Context Firewall e Gate Evaluator |
| `playtest-to-learning` | PLANNED | Não | Schemas do Learning Loop |

Essas entradas não apontam para arquivos em `.ai/skills/` porque os arquivos ainda não existem. Criar um prompt informal ou declarar um papel em uma conversa não torna a skill operacional.

### Ordem de implementação futura

1. **Primeiro: `playtest-to-learning`**.
   - Somente depois dos schemas de sessão, finding e decisão de aprendizado.
   - Motivo: registra o próximo playtest, gera valor imediato e não depende do Blind Solver.
2. **Em paralelo após contratos necessários: `context-firewall`**.
   - Somente depois dos contratos de manifest, política de visibilidade e capacidade de bundle.
3. **Depois: `blind-solve`**.
   - Somente quando Context Firewall e Gate Evaluator estiverem operacionais.

> Blind-solve não deve ser criado antes do mecanismo de isolamento que o torna confiável.

### Contratos, capacidades e validação necessários

Antes de qualquer futura skill sair de PLANNED, os contratos e capacidades correspondentes devem existir em nível mínimo:

- contratos de artifact, version, run, actor, role, gate, finding, incident, transformation e lineage, conforme `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`;
- política de visibilidade e bundle cego compatíveis com `docs/BLIND_CONTEXT_PROTOCOL.md`;
- governança de papéis, gates, rollback e incidentes compatível com `docs/MULTIAGENT_OPERATING_PROTOCOL.md`;
- ordem e decomposição alinhadas a `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md`;
- schemas ou contratos executáveis específicos quando a skill depender de output versionado;
- piloto ou teste que prove o fluxo mínimo sem contaminar contexto, apagar histórico ou declarar PASS sem gate separado.

A validação futura deve demonstrar que a skill produz output rastreável, respeita o papel declarado, preserva lineage, registra incidentes e falha de forma explícita quando pré-requisitos não existirem. O risco principal evitado é a falsa confiança: acreditar que documentação, prompt ou nomenclatura neutra fornecem isolamento, aprendizado ou aprovação automática.

## Skill futura: `context-firewall`

### Status

PLANNED — NOT IMPLEMENTED.

### Objetivo

Orientar a preparação e auditoria de contexto isolado para um papel específico.

### Usar quando

- preparar futura execução cega;
- selecionar artefatos permitidos;
- excluir materiais privados;
- normalizar nomes;
- registrar transformações;
- verificar composição conceitual do bundle.

### Não usar quando

- a tarefa for apenas revisão documental geral;
- não houver política de visibilidade;
- o protocolo de cegueira não se aplicar;
- o usuário estiver pedindo implementação de bundler ou leak checker sem issue específica.

### Pré-requisitos

- protocolo operacional aprovado;
- protocolo de cegueira aprovado;
- contratos conceituais aprovados;
- schema futuro de manifest;
- política de visibilidade futura;
- implementação técnica de bundle.

### Documentos normativos

- `docs/BLIND_CONTEXT_PROTOCOL.md`;
- `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`;
- `docs/MULTIAGENT_OPERATING_PROTOCOL.md`.

### Saída futura esperada

- contexto preparado;
- referências de artefatos;
- registro de exclusões;
- auditoria;
- decisão de validade.

Esses outputs ainda não possuem schema implementado.

### Limites

- não garante detecção semântica perfeita;
- não substitui operador humano;
- não pode alterar conteúdo visível silenciosamente;
- não deve prometer sandbox inexistente.

## Skill futura: `blind-solve`

### Status

PLANNED — NOT IMPLEMENTED.

### Objetivo

Orientar um agente cego a tentar resolver uma etapa usando somente o material autorizado.

### Usar quando

- bundle cego tiver sido preparado e auditado;
- papel e estágio estiverem definidos;
- contexto estiver isolado;
- output puder ser congelado;
- Gate Evaluator separado estiver disponível.

### Não usar quando

- solução já apareceu na conversa;
- contexto não puder ser comprovadamente isolado;
- agente tiver acesso a repositório, envelopes futuros ou guia;
- tarefa for revisão não cega;
- bundle ainda não existir;
- não houver Gate Evaluator independente.

### Pré-requisitos

- Context Firewall funcional;
- manifest ou contrato de bundle implementado;
- schema futuro de output;
- política de ferramentas;
- protocolo de incidentes;
- Gate Evaluator.

### Documentos normativos

- `docs/BLIND_CONTEXT_PROTOCOL.md`;
- `docs/MULTIAGENT_OPERATING_PROTOCOL.md`;
- `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`.

### Saída futura esperada

- pergunta compreendida;
- fatos observados;
- hipóteses;
- evidências;
- contradições;
- lacunas;
- materiais analisados;
- decisão sugerida;
- confiança.

O Blind Solver:

- não aprova seu próprio gate;
- não recebe solução;
- não corrige seu próprio output após conhecer a resposta;
- não substitui playtest humano.

## Skill futura: `playtest-to-learning`

### Status

PLANNED — NOT IMPLEMENTED.

### Objetivo

Transformar dados e observações de playtest em findings rastreáveis e decisões de aprendizado.

### Usar quando

- existir sessão de playtest registrada;
- houver observações concretas;
- for necessário separar fato, hipótese causal e decisão;
- correções precisarem gerar aprendizado persistente.

### Não usar quando

- não houve playtest real;
- a informação veio apenas de mesa simulada;
- existe somente preferência individual sem evidência;
- o objetivo for generalizar automaticamente uma ocorrência;
- os schemas de sessão e finding ainda não estiverem implementados.

### Pré-requisitos

- schema de sessão;
- schema de finding;
- schema de decisão de aprendizado;
- Learning Loop;
- política de generalização;
- validação de referências.

### Documentos normativos

- `docs/MULTIAGENT_OPERATING_PROTOCOL.md`;
- `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`;
- `docs/PRD_MULTIAGENT_CASE_CREATION.md`;
- `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md`.

### Saída futura esperada

- observação;
- evidência;
- hipótese causal;
- finding;
- escopo;
- rollback;
- decisão de generalização;
- revalidação.

Regras futuras obrigatórias:

- uma ocorrência isolada não vira regra global;
- finding nunca é apagado;
- correção não significa automaticamente resolução;
- playtest humano continua sendo a fonte da evidência.

## Seleção temporária de skills existentes

Enquanto as futuras skills não existirem, use alternativas explícitas e não alegue equivalência técnica:

| Necessidade temporária | Skill existente |
|---|---|
| Revisar decisões de segurança de contexto | `grill-with-docs` |
| Definir arquitetura ou escopo amplo | `to-prd` |
| Decompor uma iniciativa aprovada | `to-issues` |
| Depurar implementação futura | `diagnose` |
| Implementar com testes | `tdd` |

Não substitua `context-firewall` ou `blind-solve` por um prompt informal e alegue equivalência. Revisão documental pode apontar risco, mas não isola contexto; decomposição pode planejar capacidade, mas não implementa bundling; TDD pode implementar uma issue aprovada, mas não cria autorização para pular pré-requisitos.

## Regras de ativação futura

Uma futura skill só pode sair de PLANNED para AVAILABLE quando:

- existir arquivo em `.ai/skills/`;
- protocolos necessários estiverem aprovados;
- contratos e schemas necessários existirem;
- implementação mínima estiver disponível;
- testes ou piloto comprovarem o fluxo;
- documentação dos três mapas (`AGENTS.md`, `.ai/skills/README.md` e `docs/AGENT_SKILLS.md`) for atualizada;
- a skill declarar quando usar e quando não usar;
- riscos e limitações estiverem explícitos.

Não basta criar o arquivo Markdown para considerar a skill operacional.

## Anti-regras para skills planejadas

As atualizações de mapa e tarefas futuras não devem:

- criar arquivos de skills fora de issue específica;
- apresentar skill planejada como disponível;
- instruir uso de `context-firewall` hoje;
- instruir uso de `blind-solve` hoje;
- instruir uso de `playtest-to-learning` hoje;
- criar links quebrados para arquivos inexistentes;
- misturar papel de Blind Solver com skill `blind-solve`;
- misturar Context Firewall técnico com skill `context-firewall`;
- afirmar que documentação fornece isolamento;
- mudar prioridades do plano;
- implementar providers;
- alterar casos;
- alterar schemas;
- ampliar escopo para outras skills futuras.

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
| Vou mexer em regra editorial, experiência do jogador ou documentação de seleção de skills | `grill-with-docs` |
| A mudança parece grande demais para uma PR | `to-prd` → `to-issues` |
| O contexto está confuso ou espalhado | `zoom-out` |
| Vou passar a tarefa para outro agente | `handoff` |
| Quero revisar arquitetura sem feature nova | `improve-codebase-architecture` |

## Como usar em prompts para Codex

### Forma curta

```text
Use docs/prompts/diagnose.md para investigar o problema abaixo.

Problema:
...
```

```text
Use docs/prompts/tdd.md para implementar a regra abaixo.

Regra:
...
```

```text
Use docs/prompts/grill_with_docs.md antes de propor mudança editorial.

Mudança desejada:
...
```

### Forma por nome de skill

Quando o agente já conhece este repositório, também pode ser chamado assim:

```text
Use a skill diagnose.
```

O agente deve resolver o nome da skill para o prompt correspondente em `docs/prompts/` ou para o arquivo existente correspondente em `.ai/skills/`. Se o nome se referir a uma skill planejada, o agente deve declarar que ela não está disponível e selecionar a skill existente adequada.

## Guardrails do Indiciário

Mesmo usando skills, estas regras prevalecem:

1. Documento de jogador contém evidência bruta, não interpretação do autor.
2. Guia do facilitador, dicas e relatórios podem explicar; documentos diegéticos não.
3. Mapas são plantas operacionais neutras, não solução visual.
4. Baseline visual real exige Playwright/Chromium; PDF fake não prova visual.
5. Playtest e evidência concreta valem mais que refatoração teórica.
6. Não abrir marketplace, banco, Telegram comercial, dashboard ou IA de imagem sem instrução explícita.
7. PR pequena e vertical é melhor que pacote amplo.
8. Skills planejadas não são disponíveis; protocolos documentais não executam capacidades técnicas.

## Critério mínimo de conclusão

Toda tarefa conduzida com estas skills deve terminar com:

- resumo objetivo do que mudou;
- arquivos alterados;
- comandos executados;
- resultado de testes/validators/build;
- falhas ou limitações de ambiente explicitadas;
- próximos passos se houver pendência real.

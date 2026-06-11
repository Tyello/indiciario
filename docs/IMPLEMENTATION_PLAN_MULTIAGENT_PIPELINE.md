# Plano de implementação — Indiciário Story Pipeline multiagente

## 1. Objetivo do plano

Este documento converte `docs/PRD_MULTIAGENT_CASE_CREATION.md` em uma sequência de implementações pequenas, independentes, ordenadas e verificáveis para o Indiciário Story Pipeline.

O PRD continua sendo a fonte da visão: ele descreve a capacidade futura, os princípios e os cenários desejados. Este plano define a ordem operacional para transformar essa visão em issues e PRs menores, sem iniciar a implementação nesta etapa.

Diretrizes de execução:

- cada issue deve preferencialmente resultar em uma única PR;
- a implementação deve parar ao final de cada etapa para validação;
- nenhuma fase posterior deve ser iniciada apenas porque a anterior foi mergeada: seus critérios de saída devem estar comprovados;
- o pipeline atual permanece preservado e prioritário;
- baseline visual real e novo playtest do Intermediário continuam prioridade antes de expandir para automação ampla;
- esta PR cria apenas o plano documental e não altera schemas, código, testes, casos canônicos, bundles ou roadmap.

## 2. Princípios de decomposição

### Verticalidade

Cada tarefa deve entregar uma capacidade utilizável ou verificável, não apenas uma camada técnica sem resultado observável.

### Independência

Evitar misturar na mesma issue:

- documentação;
- novo schema;
- lógica de domínio;
- CLI;
- integração com LLM;
- alteração de caso;
- renderer;
- provider.

Quando esses elementos forem inseparáveis, a issue deve justificar explicitamente a exceção.

### Manual-first

O fluxo inicial deve funcionar sem chamada automática a LLM. Outputs de LLM, quando existirem, entram como arquivos fornecidos manualmente e versionáveis.

### Testabilidade

Issues P0 e P1 precisam possuir validação objetiva: revisão documental com checklist, fixture mínima, validação de schema, teste automatizado, comando CLI determinístico ou evidência versionada.

### Reversibilidade

Toda nova capacidade deve poder ser removida ou desativada sem quebrar o pipeline atual. O caminho oficial existente não deve depender de artefatos multiagente para continuar funcionando.

### Compatibilidade

O pipeline atual continua oficial até que uma futura decisão documentada diga o contrário:

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library/templates
→ Build Package
→ Baseline
→ Playtest
→ Ajustes
```

### Segurança de contexto

Nenhum agente cego pode depender apenas de uma instrução verbal para não acessar conteúdo privado. A cegueira precisa ser sustentada por bundles, manifests, política de visibilidade, hashes e verificação de isolamento.

## 3. Mapa geral das fases

### Fase A — Governança e contratos

- **Objetivo:** fixar linguagem operacional, responsabilidades, limites de autoridade humana, contratos conceituais e mapa futuro de skills antes de criar schemas ou código.
- **Pré-requisitos:** PRD aprovado e prioridade atual preservada.
- **Entregáveis:** protocolo operacional, protocolo de cegueira, contratos conceituais de artefato/run e plano de atualização do mapa de skills.
- **Critério de entrada:** PRD disponível e lido; nenhuma implementação multiagente iniciada.
- **Critério de saída:** documentos-base aprovados com revisão humana e sem ambiguidade entre skill, papel e orquestrador.
- **Riscos:** criar documentação abstrata demais, duplicar manuais existentes ou autorizar automação antes de controles mínimos.
- **Fora de escopo:** schemas executáveis, scripts, providers, alteração dos canônicos e skills novas nesta fase inicial.

### Fase B — Learning Loop de playtest

- **Objetivo:** registrar sessões, findings e decisões de aprendizado de forma versionável antes de generalizar regras.
- **Pré-requisitos:** contratos conceituais de artefato/run aprovados.
- **Entregáveis:** schemas de sessão, finding e decisão; validador do ledger; CLI manual; exemplos retroativos sem alterar casos.
- **Critério de entrada:** governança mínima definida e próximo playtest ainda tratado como prioridade atual.
- **Critério de saída:** uma sessão/finding/decisão pode ser registrada e validada sem banco de dados.
- **Riscos:** transformar observação isolada em regra global, misturar ajuste de caso com registro de aprendizado ou perder rastreabilidade.
- **Fora de escopo:** alterar casos canônicos, automatizar coleta, criar dashboard ou generalizar heurísticas sem evidência.

### Fase C — Context Firewall e blind bundles

- **Objetivo:** preparar bundles cegos por papel com manifest, hashes, política de visibilidade e verificação de vazamento.
- **Pré-requisitos:** protocolos de cegueira e contratos de artifact/run; schemas do Learning Loop não precisam bloquear o início dos contratos de bundle, mas ajudam na rastreabilidade.
- **Entregáveis:** schema de manifest, política de visibilidade, criação manual de bundle, leak check, testes de sanitização e CLI de preparação/inspeção.
- **Critério de entrada:** definição documental do que é permitido/proibido por papel.
- **Critério de saída:** bundle manual reproduzível pode ser preparado e inspecionado sem acesso a solução privada.
- **Riscos:** falsa sensação de cegueira, sanitização destrutiva, nomes de arquivos reveladores e promessa de detecção semântica perfeita.
- **Fora de escopo:** descoberta automática do caso inteiro, providers, análise semântica perfeita e execução automática de agentes.

### Fase D — Blind Solver e Gate Evaluator

- **Objetivo:** padronizar output de resolução cega e avaliação privada posterior sem autocertificação.
- **Pré-requisitos:** Context Firewall, manifest, política de visibilidade e schema de output do solver.
- **Entregáveis:** schemas, skill/protocolo de Blind Solver, decisão sobre Gate Evaluator, piloto manual em um envelope e Blind Review renderizado separado.
- **Critério de entrada:** bundles cegos podem ser preparados e verificados.
- **Critério de saída:** um piloto manual gera output congelado, avaliação, findings e limites documentados sem alterar o caso.
- **Riscos:** vazar gabarito, tratar piloto como certificação, confundir revisão lógica com baseline visual humano.
- **Fora de escopo:** playtest substituído, certificação completa dos canônicos, automação de providers e alteração de envelopes.

### Fase E — Revisões editoriais estruturadas

- **Objetivo:** padronizar reviews por papel e consolidar outputs sem apagar evidência original.
- **Pré-requisitos:** contrato comum de review e contratos de artifact/run.
- **Entregáveis:** contrato comum, skills editoriais futuras e mecanismo manual de consolidação.
- **Critério de entrada:** outputs de revisão possuem formato mínimo e rastreabilidade.
- **Critério de saída:** revisões podem ser comparadas e consolidadas com preservação dos originais.
- **Riscos:** transformar revisor em autor silencioso, criar skills antes de contrato comum ou misturar consolidação com orquestrador completo.
- **Fora de escopo:** alteração automática de conteúdo, novo caso, provider e dashboard.

### Fase F — Mesa investigativa simulada

- **Objetivo:** modelar análise individual, debate coletivo, crítico adversarial e relatório de limitações sem substituir playtest humano.
- **Pré-requisitos:** blind bundles, contrato comum de review e registros de runs.
- **Entregáveis:** schemas de estado individual/coletivo/rodadas/crítico, skill simulated-table, piloto manual e relatório de correlação.
- **Critério de entrada:** Blind Solver manual já exercitado e limitações de cegueira conhecidas.
- **Critério de saída:** piloto manual documenta hipóteses, mudanças, consenso, dissenso, orçamento e limitações.
- **Riscos:** tratar personas como independência cognitiva, superestimar correlação com humanos ou automatizar providers cedo.
- **Fora de escopo:** providers automáticos, certificação de diversão e substituição do playtest humano.

### Fase G — Workspace/orquestrador manual

- **Objetivo:** organizar arquivos por caso, workflow declarativo, status, lineage, ingestão, gates e rollback manual.
- **Pré-requisitos:** contratos de run/artifact, Learning Loop, bundles e reviews manuais exercitados.
- **Entregáveis:** estrutura de workspace, workflow declarativo, inicialização manual, status/lineage, ingestão, gates e CLI unificada posterior.
- **Critério de entrada:** padrões manuais existem e foram usados em pilotos.
- **Critério de saída:** um workspace pode reproduzir o estado de uma execução sem banco de dados.
- **Riscos:** criar orquestrador horizontal grande, acoplar ao pipeline atual ou bloquear baseline/playtest.
- **Fora de escopo:** dashboard, banco, multiusuário, providers e execução autônoma completa.

### Fase H — Diversidade e dificuldade

- **Objetivo:** criar instrumentos não bloqueantes para comparar arquitetura de casos e calibrar dificuldade por grafo de inferência.
- **Pré-requisitos:** dados de canônicos e playtests suficientes; Learning Loop validado.
- **Entregáveis:** schema de fingerprint, extração dos canônicos sem alterá-los, comparação não bloqueante, skills de diversidade/dificuldade e correlação com playtests.
- **Critério de entrada:** baseline e playtests fornecem evidência mínima para comparação.
- **Critério de saída:** estimativas são registradas como apoio editorial, não como gate absoluto.
- **Riscos:** usar quantidade de documentos como proxy principal, punir similaridades legítimas ou antecipar o canônico Avançado.
- **Fora de escopo:** ML, embeddings, RAG, bloqueio automático de casos e criação do canônico Avançado.

### Fase I — Providers e inteligência editorial futura

- **Objetivo:** registrar condições de entrada para automação futura sem transformá-la em tarefa pronta agora.
- **Pré-requisitos:** fases A–H comprovadas manualmente, baseline/playtest priorizados e custos/limites conhecidos.
- **Entregáveis:** issues P3 condicionais para providers, benchmark, RAG/embeddings/ML e geração massiva.
- **Critério de entrada:** evidência de que o fluxo manual gera valor e possui segurança de contexto.
- **Critério de saída:** decisão humana futura aprova investigação técnica específica.
- **Riscos:** abrir frente ampla, vazar contexto privado, criar dependência externa obrigatória ou desviar da experiência offline-first.
- **Fora de escopo:** implementação imediata de OpenAI, Anthropic, Ollama, RAG, embeddings, ML, fine-tuning, custo automatizado e geração massiva.

## 4. Backlog detalhado

### ISSUE-01 — Documentar protocolo operacional multiagente manual-first
**Prioridade:** P0
**Tipo:** docs
**Fase:** A
**Dependências:** nenhuma
#### Objetivo
Criar `docs/MULTIAGENT_OPERATING_PROTOCOL.md` com etapas, papéis, responsabilidades, visibilidades, gates, rollback, autoridade humana e distinção entre skill, papel e orquestrador.
#### Problema resolvido
Evita que schemas e scripts futuros sejam construídos sobre conceitos ambíguos ou automação prematura.
#### Escopo
Documento operacional; glossário; sequência de etapas; autoridade humana; manual-first; relação com pipeline oficial.
#### Fora de escopo
Schemas, código, skills novas, providers, orquestrador e alterações em casos.
#### Critérios de aceitação
O documento explica papéis, entradas, saídas, gates, rollback e limites; preserva o pipeline atual; declara que playtest humano segue soberano.
#### Validação sugerida
Revisão documental com checklist do PRD; `git diff --check`; confirmação de que nenhum arquivo executável mudou.
#### Arquivos prováveis
`docs/MULTIAGENT_OPERATING_PROTOCOL.md`.
#### Riscos
Virar manual genérico ou autorizar execução automática sem controles.
#### Evidência necessária para encerrar
Documento aprovado em PR própria e checklist mostrando cobertura dos tópicos obrigatórios.

### ISSUE-02 — Documentar protocolo de cegueira e segurança de contexto
**Prioridade:** P0
**Tipo:** security
**Fase:** A
**Dependências:** ISSUE-01
#### Objetivo
Criar `docs/BLIND_CONTEXT_PROTOCOL.md` definindo Context Firewall, dados permitidos/proibidos, prompt injection documental, sanitização não destrutiva, artefatos derivados, manifest, hashes e auditoria.
#### Problema resolvido
Impede que agentes cegos dependam apenas de instrução verbal para não acessar conteúdo privado.
#### Escopo
Política conceitual de cegueira; ameaças; categorias privadas; controles mínimos; limites da detecção semântica.
#### Fora de escopo
Implementar bundler, leak checker, schemas, prompts ou execução de Blind Solver.
#### Critérios de aceitação
Documento lista dados proibidos, dados permitidos, controles de isolamento e procedimentos de auditoria; diferencia vazamento técnico de interpretação do conteúdo.
#### Validação sugerida
Revisão humana orientada por exemplos de `verdade_real`, guia do facilitador e envelopes futuros; `git diff --check`.
#### Arquivos prováveis
`docs/BLIND_CONTEXT_PROTOCOL.md`.
#### Riscos
Prometer segurança perfeita ou remover contexto necessário para a investigação cega.
#### Evidência necessária para encerrar
Checklist de ameaças coberto e decisão explícita sobre limitações.

### ISSUE-03 — Definir contratos conceituais de artefato e run
**Prioridade:** P0
**Tipo:** docs
**Fase:** A
**Dependências:** ISSUE-01, ISSUE-02
#### Objetivo
Definir conceitualmente `artifact_id`, versionamento, visibilidade, lineage, `run_id`, provider/model opcionais, hashes, parâmetros, timestamps e origem dos arquivos.
#### Problema resolvido
Cria vocabulário estável antes de schemas e CLIs, evitando incompatibilidades precoces.
#### Escopo
Documento ou seção em protocolo aprovado; exemplos não executáveis de registros; regras de versionamento.
#### Fora de escopo
Criar schema YAML/JSON nesta issue, para não misturar contrato conceitual com validação executável.
#### Critérios de aceitação
Todos os campos essenciais possuem definição, obrigatoriedade conceitual e relação com lineage.
#### Validação sugerida
Revisão documental cruzada com PRD e protocolos; nenhuma alteração em `schemas/`, `generator/` ou `scripts/`.
#### Arquivos prováveis
`docs/MULTIAGENT_OPERATING_PROTOCOL.md` ou documento dedicado de contratos.
#### Riscos
Campos excessivos para o fluxo manual ou falta de compatibilidade com versões futuras.
#### Evidência necessária para encerrar
Tabela de campos conceituais e exemplos mínimos revisados.

### ISSUE-04 — Atualizar mapa de skills para futuras skills multiagente
**Prioridade:** P1
**Tipo:** docs
**Fase:** A
**Dependências:** ISSUE-01, ISSUE-02, ISSUE-03
#### Objetivo
Atualizar o mapa de skills para prever `context-firewall`, `blind-solve` e `playtest-to-learning` após aprovação dos protocolos.
#### Problema resolvido
Garante que agentes escolham procedimentos corretos quando as skills forem criadas futuramente.
#### Escopo
Atualização coordenada de mapas e documentação de seleção; descrição de quando usar cada skill futura.
#### Fora de escopo
Criar arquivos `.ai/skills/*.md`, prompts, scripts ou providers.
#### Critérios de aceitação
`AGENTS.md`, `.ai/skills/README.md` e `docs/AGENT_SKILLS.md` ficam consistentes entre si.
#### Validação sugerida
Revisão documental; `git diff --check`; confirmação de que nenhum arquivo de skill novo foi criado.
#### Arquivos prováveis
`AGENTS.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Referenciar skills antes de contratos aprovados ou confundir skill com papel de agente.
#### Evidência necessária para encerrar
Diferença revisada mostrando consistência dos três mapas.

### ISSUE-05 — Definir schema de sessão de playtest versionável
**Prioridade:** P0
**Tipo:** schema
**Fase:** B
**Dependências:** ISSUE-03
#### Objetivo
Criar schema para sessão de playtest com versão do caso, perfil dos jogadores, duração, eventos cronológicos, dicas, hipóteses, travamentos, resultado, diversão, surpresa e justiça percebida.
#### Problema resolvido
Permite registrar o próximo playtest de forma objetiva e reaproveitável.
#### Escopo
Schema e fixtures mínimas válidas/inválidas.
#### Fora de escopo
CLI, banco de dados, dashboard, alteração de casos e migração de aprendizados.
#### Critérios de aceitação
Schema valida uma sessão completa e rejeita campos obrigatórios ausentes ou eventos sem ordem temporal.
#### Validação sugerida
Teste de schema com fixtures; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/` se criado no futuro, `tests/`, eventual pasta de fixtures.
#### Riscos
Capturar dados pessoais desnecessários ou tornar registro manual pesado demais.
#### Evidência necessária para encerrar
Schema, fixtures e testes passando.

### ISSUE-06 — Definir schema de finding de playtest
**Prioridade:** P0
**Tipo:** schema
**Fase:** B
**Dependências:** ISSUE-03
#### Objetivo
Criar schema para finding contendo observação, evidência, hipótese causal, severidade, escopo, etapa de rollback, status, sessões relacionadas e decisão de generalização.
#### Problema resolvido
Separa observação de causa provável e impede correções sem rastreabilidade.
#### Escopo
Schema e fixtures de findings por severidade/status.
#### Fora de escopo
Validador de ledger, CLI, alteração de casos e regra global automática.
#### Critérios de aceitação
Finding exige evidência e sessão relacionada; status permitidos são explícitos.
#### Validação sugerida
Teste de fixtures válidas/inválidas; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Confundir hipótese causal com fato comprovado.
#### Evidência necessária para encerrar
Schema com exemplos cobrindo severidade, rollback e generalização pendente.

### ISSUE-07 — Definir schema de decisão de aprendizado
**Prioridade:** P0
**Tipo:** schema
**Fase:** B
**Dependências:** ISSUE-03, ISSUE-06
#### Objetivo
Criar schema que distinga escopos `case_only`, `mechanic_family`, `difficulty_level`, `global_editorial`, `technical` e `visual`, e resultados `no_generalization`, `example_only`, `heuristic`, `guardrail`, `validator_candidate`, `case_review_candidate` e `regression_test`.
#### Problema resolvido
Evita que aprendizados isolados virem regras globais sem decisão explícita.
#### Escopo
Schema de decisão, relacionamento com finding e justificativa obrigatória.
#### Fora de escopo
Aplicar decisões no validator, Case Review, docs editoriais ou casos.
#### Critérios de aceitação
Toda decisão referencia finding existente e exige justificativa para qualquer generalização.
#### Validação sugerida
Fixtures e testes de enum/referência; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Criar taxonomia rígida demais para playtests iniciais.
#### Evidência necessária para encerrar
Exemplos cobrindo pelo menos uma não generalização e uma candidata futura.

### ISSUE-08 — Criar validador do learning ledger
**Prioridade:** P0
**Tipo:** test
**Fase:** B
**Dependências:** ISSUE-05, ISSUE-06, ISSUE-07
#### Objetivo
Validar IDs, referências, transições de estado, sessão existente, finding relacionado, revalidação e decisão explícita sobre generalização.
#### Problema resolvido
Torna o Learning Loop confiável antes de registrar dados reais do próximo playtest.
#### Escopo
Validador determinístico e testes com fixtures.
#### Fora de escopo
CLI de registro, banco, dashboard e alteração de regras editoriais.
#### Critérios de aceitação
Validador rejeita referências quebradas, transições inválidas e findings sem decisão.
#### Validação sugerida
`pytest tests/ -q` com casos positivos e negativos.
#### Arquivos prováveis
`generator/` ou `scripts/` conforme padrão futuro, `tests/`, fixtures.
#### Riscos
Duplicar lógica de schema ou impor workflow cedo demais.
#### Evidência necessária para encerrar
Relatório de testes demonstrando falhas esperadas e sucesso em ledger válido.

### ISSUE-09 — Criar CLI manual para registrar sessão e finding
**Prioridade:** P0
**Tipo:** cli
**Fase:** B
**Dependências:** ISSUE-08
#### Objetivo
Criar CLI sem banco de dados para registrar sessão e finding em YAML/JSON versionável.
#### Problema resolvido
Permite operar o próximo playtest sem depender de planilhas soltas ou dashboard.
#### Escopo
Comandos manuais para criar arquivos, validar e preservar IDs.
#### Fora de escopo
Interface web, banco, importação automática, LLM e alteração de casos.
#### Critérios de aceitação
CLI cria sessão/finding mínimos, não sobrescreve arquivos sem confirmação técnica e roda o validador.
#### Validação sugerida
Testes de CLI com diretório temporário; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/`, `tests/`, pasta futura de fixtures/exemplos.
#### Riscos
UX pesada ou nomenclatura desalinhada dos scripts existentes.
#### Evidência necessária para encerrar
Comandos documentados e teste automatizado de criação/validação.

### ISSUE-10 — Migrar aprendizados anteriores como exemplos de ledger
**Prioridade:** P2
**Tipo:** editorial
**Fase:** B
**Dependências:** ISSUE-09
#### Objetivo
Registrar retroativamente alguns aprendizados comprovados de playtests existentes como exemplos para provar os schemas.
#### Problema resolvido
Exercita o formato com dados reais sem alterar casos canônicos.
#### Escopo
Exemplos versionáveis derivados de playtests documentados; marcação clara de retrospectivo.
#### Fora de escopo
Alterar casos, atualizar roadmap, criar regra global ou reabrir decisões editoriais.
#### Critérios de aceitação
Exemplos passam no validador e indicam fonte documental.
#### Validação sugerida
Validador do ledger; `pytest tests/ -q`.
#### Arquivos prováveis
Pasta futura de exemplos em `docs/playtests/` ou `examples/learning/`.
#### Riscos
Reinterpretar playtests antigos além da evidência registrada.
#### Evidência necessária para encerrar
Ledger de exemplo validado e links para documentos de playtest usados.

### ISSUE-11 — Definir schema do manifest de blind bundle
**Prioridade:** P0
**Tipo:** schema
**Fase:** C
**Dependências:** ISSUE-02, ISSUE-03
#### Objetivo
Criar schema de manifest cobrindo papel, etapa, artefatos permitidos, categorias proibidas, hashes, política de visibilidade, transformações, artefatos derivados e resultado do isolation check.
#### Problema resolvido
Estabelece contrato verificável para bundles cegos.
#### Escopo
Schema e fixtures de manifest válido/inválido.
#### Fora de escopo
Criar bundle, CLI, leak checker e execução de Blind Solver.
#### Critérios de aceitação
Manifest exige hashes, visibilidade e lista explícita de incluídos/excluídos.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Manifest insuficiente para auditoria ou complexo demais para uso manual.
#### Evidência necessária para encerrar
Fixtures cobrindo pelo menos um papel cego e uma exclusão registrada.

### ISSUE-12 — Implementar política de visibilidade de artefatos
**Prioridade:** P0
**Tipo:** domain
**Fase:** C
**Dependências:** ISSUE-02, ISSUE-03
#### Objetivo
Representar `public_player`, `private_author`, `review_private`, `facilitator`, `derived_report` e `playtest_anonymized`.
#### Problema resolvido
Permite classificar artefatos antes da criação de bundles e impedir entradas indevidas.
#### Escopo
Modelo simples de visibilidade, testes e documentação mínima.
#### Fora de escopo
Bundle completo, renderer, providers e alteração de casos.
#### Critérios de aceitação
Cada visibilidade tem semântica documentada e testes de permissão por papel.
#### Validação sugerida
Testes unitários de matriz papel × visibilidade; `pytest tests/ -q`.
#### Arquivos prováveis
`generator/` ou módulo futuro de domínio, `tests/`, docs de protocolo.
#### Riscos
Acoplar visibilidade ao layout atual de arquivos ou revelar categorias privadas por nome.
#### Evidência necessária para encerrar
Matriz de permissões testada e documentada.

### ISSUE-13 — Implementar criação manual de blind bundle por entrada explícita
**Prioridade:** P1
**Tipo:** security
**Fase:** C
**Dependências:** ISSUE-11, ISSUE-12
#### Objetivo
Criar bundle manual com entrada explícita, cópia de arquivos permitidos, normalização de nomes, manifest, hashes, `ROLE.md`, `OUTPUT_SCHEMA.yaml` e artefatos excluídos.
#### Problema resolvido
Entrega o primeiro Context Firewall operacional sem descobrir automaticamente o caso inteiro.
#### Escopo
Função ou script interno determinístico; fixtures com arquivos permitidos/proibidos.
#### Fora de escopo
Auto-discovery, providers, execução de agente e alteração dos canônicos.
#### Critérios de aceitação
Bundle gerado contém apenas arquivos declarados, hashes corretos e registro de excluídos.
#### Validação sugerida
Testes com diretório temporário; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/` ou `generator/`, `tests/`.
#### Riscos
Normalização revelar informação ou excluir evidência necessária sem registrar.
#### Evidência necessária para encerrar
Bundle fixture reproduzível e manifest validado.

### ISSUE-14 — Implementar verificação de vazamento em blind bundle
**Prioridade:** P1
**Tipo:** security
**Fase:** C
**Dependências:** ISSUE-13
#### Objetivo
Detectar categorias proibidas, arquivos futuros, nomes internos reveladores, caminhos privados, metadados privados e arquivos não declarados.
#### Problema resolvido
Reduz risco de vazamento técnico antes de uma execução cega.
#### Escopo
Leak checker conservador baseado em manifest, caminhos, metadados e declarações.
#### Fora de escopo
Prometer detecção perfeita de conteúdo semântico ou julgamento editorial automático.
#### Critérios de aceitação
Checker rejeita fixtures com vazamentos técnicos conhecidos e aprova bundle mínimo válido.
#### Validação sugerida
Testes negativos por tipo de vazamento; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/` ou `generator/`, `tests/`.
#### Riscos
Falso negativo por vazamento semântico ou falso positivo excessivo.
#### Evidência necessária para encerrar
Tabela de limites e testes cobrindo cada classe mínima.

### ISSUE-15 — Testar sanitização não destrutiva de artefatos derivados
**Prioridade:** P1
**Tipo:** test
**Fase:** C
**Dependências:** ISSUE-13, ISSUE-14
#### Objetivo
Garantir que conteúdo visível não seja alterado silenciosamente, transformações gerem novo artefato, o original seja preservado e diff/hash sejam registrados.
#### Problema resolvido
Impede que o processo de cegueira corrompa evidências do jogador.
#### Escopo
Testes de transformação e registro de lineage.
#### Fora de escopo
Criar novas transformações complexas, OCR, semântica de conteúdo ou renderer.
#### Critérios de aceitação
Toda transformação tem artefato derivado, hash novo, hash original e diff/descrição.
#### Validação sugerida
`pytest tests/ -q` com fixture de sanitização.
#### Arquivos prováveis
`tests/`, fixtures, módulo de bundle se existir.
#### Riscos
Registrar diff insuficiente para auditoria humana.
#### Evidência necessária para encerrar
Teste falharia se o original fosse sobrescrito.

### ISSUE-16 — Criar CLI de preparação e inspeção de blind bundle
**Prioridade:** P1
**Tipo:** cli
**Fase:** C
**Dependências:** ISSUE-13, ISSUE-14, ISSUE-15
#### Objetivo
Expor comandos manuais para preparar e inspecionar bundles, seguindo padrões já usados no repositório.
#### Problema resolvido
Torna o Context Firewall operável sem orquestrador completo.
#### Escopo
CLI para preparar, validar e inspecionar manifest/arquivos.
#### Fora de escopo
Executar LLM, descobrir caso automaticamente, dashboard e workspace completo.
#### Critérios de aceitação
Comandos produzem saída determinística, códigos de erro e documentação mínima.
#### Validação sugerida
Testes de CLI; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/`, `tests/`, docs de uso.
#### Riscos
Nome de comando desalinhado dos padrões do repo ou escopo crescer para orquestrador.
#### Evidência necessária para encerrar
Execução em diretório temporário demonstrando preparar e inspecionar.

### ISSUE-17 — Definir schema do output do Blind Solver
**Prioridade:** P1
**Tipo:** schema
**Fase:** D
**Dependências:** ISSUE-11, ISSUE-12
#### Objetivo
Criar schema para pergunta compreendida, fatos, hipóteses, evidências, contradições, alternativas, informações ausentes, documentos ignorados, documentos superinterpretados, decisão sugerida, confiança e artefatos analisados.
#### Problema resolvido
Padroniza outputs cegos para avaliação posterior.
#### Escopo
Schema e fixtures de output completo/incompleto.
#### Fora de escopo
Skill `blind-solve`, Gate Evaluator, execução de LLM e avaliação privada.
#### Critérios de aceitação
Output separa fato de interpretação e referencia artefatos analisados.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Campo de confiança gerar falsa precisão.
#### Evidência necessária para encerrar
Fixtures demonstrando hipótese com evidência e informação ausente.

### ISSUE-18 — Criar skill blind-solve baseada em protocolo e schema
**Prioridade:** P1
**Tipo:** editorial
**Fase:** D
**Dependências:** ISSUE-01, ISSUE-02, ISSUE-11, ISSUE-17
#### Objetivo
Criar skill `blind-solve` declarando informações permitidas/proibidas, tratamento de documentos, separação entre fato e interpretação, prevenção de premissas inventadas e formato final.
#### Problema resolvido
Dá procedimento operacional seguro ao papel Blind Solver.
#### Escopo
Arquivo de skill e documentação de uso.
#### Fora de escopo
Executar solver, criar providers, alterar casos ou avaliar solução.
#### Critérios de aceitação
Skill aponta para protocolos, exige output no schema e proíbe acesso a artefatos privados.
#### Validação sugerida
Revisão documental; confirmação de consistência com mapa de skills.
#### Arquivos prováveis
`.ai/skills/blind-solve.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Skill virar prompt que tenta garantir cegueira sem bundle técnico.
#### Evidência necessária para encerrar
Skill revisada com checklist de segurança de contexto.

### ISSUE-19 — Definir schema do Gate Evaluator
**Prioridade:** P1
**Tipo:** schema
**Fase:** D
**Dependências:** ISSUE-17
#### Objetivo
Criar schema para run do solver, conclusões esperadas, conclusões observadas, hipóteses válidas inesperadas, vazamento, decisão, justificativa e rollback.
#### Problema resolvido
Permite avaliar output cego congelado sem autocertificação.
#### Escopo
Schema e fixtures para aprovar, reprovar e pedir rollback.
#### Fora de escopo
Skill/protocolo do Gate Evaluator, execução de piloto e alterações de caso.
#### Critérios de aceitação
Avaliação referencia run do solver e registra decisão com justificativa.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Evaluator vazar solução para bundles futuros se outputs forem misturados.
#### Evidência necessária para encerrar
Fixtures cobrindo vazamento e hipótese inesperada válida.

### ISSUE-20 — Decidir e criar protocolo ou skill do Gate Evaluator
**Prioridade:** P1
**Tipo:** architecture
**Fase:** D
**Dependências:** ISSUE-19, ISSUE-23
#### Objetivo
Decidir explicitamente se Gate Evaluator será skill própria ou parte de revisão estruturada, com justificativa.
#### Problema resolvido
Evita proliferar skills sem necessidade ou misturar avaliação privada com resolução cega.
#### Escopo
Documento de decisão e, se aprovado, skill/protocolo mínimo.
#### Fora de escopo
Executar avaliação real, alterar casos e criar orquestrador.
#### Critérios de aceitação
Decisão registra trade-offs, visibilidade privada e relação com contrato comum de review.
#### Validação sugerida
Revisão arquitetural documental; `git diff --check`.
#### Arquivos prováveis
`docs/`, `.ai/skills/` se a decisão for criar skill.
#### Riscos
Decisão prematura antes do contrato comum de review.
#### Evidência necessária para encerrar
ADR ou seção equivalente com decisão e impacto.

### ISSUE-21 — Executar piloto manual de Blind Solver em um envelope canônico
**Prioridade:** P1
**Tipo:** editorial
**Fase:** D
**Dependências:** ISSUE-16, ISSUE-18, ISSUE-19, ISSUE-20
#### Objetivo
Usar somente um envelope de um canônico existente para preparar bundle, executar Blind Solver manual, congelar output, executar Gate Evaluator e registrar findings.
#### Problema resolvido
Prova o fluxo manual sem alterar o caso nem substituir playtest.
#### Escopo
Piloto documentado com artefatos gerados e limitações.
#### Fora de escopo
Certificar caso, alterar canônico, rodar todos os envelopes, provider automático e baseline visual.
#### Critérios de aceitação
Output cego e avaliação privada ficam separados; findings registrados; nenhuma alteração em exemplos canônicos.
#### Validação sugerida
Validador de bundle, schemas de output/evaluator e revisão humana.
#### Arquivos prováveis
Pasta futura de pilotos/artefatos em `docs/` ou `output/` versionável conforme decisão.
#### Riscos
Vazamento acidental de solução ou interpretação de piloto como aprovação final.
#### Evidência necessária para encerrar
Manifest, output congelado, avaliação e findings com hashes.

### ISSUE-22 — Criar Blind Review renderizado separado da revisão lógica
**Prioridade:** P1
**Tipo:** editorial
**Fase:** D
**Dependências:** ISSUE-16, ISSUE-23
#### Objetivo
Criar procedimento para revisar material final de jogador quanto a destaque visual, ordem, paginação, metadados, pistas perdidas, pistas reveladas pelo layout e problemas P&B.
#### Problema resolvido
Separa risco visual cego de solvabilidade lógica e de baseline visual humano.
#### Escopo
Contrato/procedimento de review renderizado e output verificável.
#### Fora de escopo
Alterar renderer, substituir baseline real, criar PDF fake ou modificar templates.
#### Critérios de aceitação
Procedimento exige material final real e declara limites frente ao baseline humano.
#### Validação sugerida
Revisão documental e, quando tocar PDF futuramente, build real com Playwright/Chromium.
#### Arquivos prováveis
`docs/`, possível schema futuro de review.
#### Riscos
Misturar com baseline visual ou prometer detecção de todos os problemas de impressão.
#### Evidência necessária para encerrar
Checklist visual renderizado aprovado sem alterar pacote.

### ISSUE-23 — Criar contrato comum de review estruturado
**Prioridade:** P1
**Tipo:** schema
**Fase:** E
**Dependências:** ISSUE-03
#### Objetivo
Definir formato-base com papel, etapa, status, confiança, findings, evidência, impacto, rollback, desconhecidos e premissas assumidas.
#### Problema resolvido
Unifica outputs de revisores sem apagar diferenças de papel.
#### Escopo
Schema/contrato comum e fixtures.
#### Fora de escopo
Skills específicas, consolidação e alteração de conteúdo revisado.
#### Critérios de aceitação
Review referencia artefatos, separa evidência de premissa e registra rollback.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Contrato genérico demais ou incompatível com Gate Evaluator.
#### Evidência necessária para encerrar
Fixtures para pelo menos dois papéis de review.

### ISSUE-24 — Criar skill mystery-grill para revisão de mistério
**Prioridade:** P2
**Tipo:** editorial
**Fase:** E
**Dependências:** ISSUE-23
#### Objetivo
Criar skill para pressionar premissa, solvabilidade, red herrings e curva investigativa usando contrato comum de review.
#### Problema resolvido
Padroniza uma revisão editorial específica sem alterar o artefato revisado.
#### Escopo
Skill e documentação de uso.
#### Fora de escopo
Alterar casos, validator, Case Review ou executar providers automaticamente.
#### Critérios de aceitação
Skill exige evidências, unknowns, impacto e rollback.
#### Validação sugerida
Revisão documental com mapa de skills.
#### Arquivos prováveis
`.ai/skills/mystery-grill.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Sobrepor-se ao `grill-with-docs` sem distinção clara.
#### Evidência necessária para encerrar
Descrição de quando usar a skill e exemplo mínimo de output.

### ISSUE-25 — Criar skill diegesis-audit para documentos diegéticos
**Prioridade:** P2
**Tipo:** editorial
**Fase:** E
**Dependências:** ISSUE-23
#### Objetivo
Criar skill focada em evidência bruta, verossimilhança documental e ausência de interpretação autoral em documentos de jogador.
#### Problema resolvido
Reduz vazamento de gabarito em documentos diegéticos.
#### Escopo
Skill e critérios de revisão diegética.
#### Fora de escopo
Reescrever documentos, criar templates ou alterar renderer.
#### Critérios de aceitação
Skill diferencia evidência, interpretação e metadado revelador.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`.ai/skills/diegesis-audit.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Duplicar diretrizes editoriais sem operacionalização.
#### Evidência necessária para encerrar
Checklist de auditoria alinhado às diretrizes existentes.

### ISSUE-26 — Criar skill evidence-audit para cadeia de evidências
**Prioridade:** P2
**Tipo:** editorial
**Fase:** E
**Dependências:** ISSUE-23
#### Objetivo
Criar skill para verificar fatos, evidências, inferências, contradições e redundâncias sem conhecer ajustes não permitidos.
#### Problema resolvido
Fortalece rastreabilidade de pistas e evita inferência inventada.
#### Escopo
Skill e formato de output baseado no contrato comum.
#### Fora de escopo
Alterar clue graph, validator ou casos.
#### Critérios de aceitação
Skill exige referência a artefatos e separa fato de hipótese.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`.ai/skills/evidence-audit.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Conflitar com Case Review automatizado.
#### Evidência necessária para encerrar
Comparação documentada com Case Review atual.

### ISSUE-27 — Criar skill learning-governance para decisões de aprendizado
**Prioridade:** P2
**Tipo:** editorial
**Fase:** E
**Dependências:** ISSUE-07, ISSUE-23
#### Objetivo
Criar skill para revisar findings e decisões de aprendizado antes de generalizar heurísticas ou guardrails.
#### Problema resolvido
Evita inflação de regras globais a partir de playtests isolados.
#### Escopo
Skill de governança e critérios para generalização.
#### Fora de escopo
Modificar validator, Case Review, diretrizes ou casos.
#### Critérios de aceitação
Skill exige escopo de generalização e evidência de recorrência ou justificativa forte.
#### Validação sugerida
Revisão documental com exemplos retrospectivos.
#### Arquivos prováveis
`.ai/skills/learning-governance.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Burocratizar aprendizados simples.
#### Evidência necessária para encerrar
Checklist de decisão aplicado a um exemplo.

### ISSUE-28 — Criar mecanismo manual de consolidação de reviews
**Prioridade:** P1
**Tipo:** cli
**Fase:** E
**Dependências:** ISSUE-23
#### Objetivo
Criar mecanismo manual para consolidar reviews preservando outputs originais e impedindo alteração silenciosa.
#### Problema resolvido
Permite comparar revisões sem criar orquestrador completo.
#### Escopo
Formato ou CLI simples de consolidação, hashes e referências aos originais.
#### Fora de escopo
Orquestrador completo, resolução automática de conflitos e alteração dos artefatos revisados.
#### Critérios de aceitação
Consolidação referencia originais por hash e registra decisões humanas.
#### Validação sugerida
Testes com dois reviews de fixture; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/` ou `generator/`, `tests/`.
#### Riscos
Consolidação virar editor de conteúdo.
#### Evidência necessária para encerrar
Arquivo consolidado reproduzível e originais intactos.

### ISSUE-29 — Definir schema do estado individual da mesa simulada
**Prioridade:** P2
**Tipo:** schema
**Fase:** F
**Dependências:** ISSUE-17, ISSUE-23
#### Objetivo
Definir schema para hipóteses, fatos, dúvidas, confiança e artefatos vistos por participante simulado antes do debate.
#### Problema resolvido
Congela análise individual para medir mudança posterior.
#### Escopo
Schema e fixtures.
#### Fora de escopo
Providers, skill, mesa coletiva e alteração de casos.
#### Critérios de aceitação
Estado individual referencia bundle/run e proíbe edição após congelamento.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Confundir persona com independência cognitiva real.
#### Evidência necessária para encerrar
Fixture congelada válida e mutação rejeitada.

### ISSUE-30 — Definir schema das rodadas coletivas
**Prioridade:** P2
**Tipo:** schema
**Fase:** F
**Dependências:** ISSUE-29
#### Objetivo
Modelar compartilhamento, confronto, síntese e mudanças por rodada.
#### Problema resolvido
Torna auditável como hipóteses coletivas surgem.
#### Escopo
Schema de rodada e referências aos estados individuais.
#### Fora de escopo
Estado coletivo final, crítico adversarial e automação de conversa.
#### Critérios de aceitação
Rodadas registram contribuições, conflitos e mudanças de hipótese.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Registro verboso demais para uso manual.
#### Evidência necessária para encerrar
Fixture com pelo menos duas rodadas e mudança de hipótese.

### ISSUE-31 — Definir schema do estado coletivo
**Prioridade:** P2
**Tipo:** schema
**Fase:** F
**Dependências:** ISSUE-30
#### Objetivo
Definir consenso, dissenso, hipótese dominante, evidências aceitas, dúvidas abertas e decisão do grupo.
#### Problema resolvido
Captura o resultado da mesa simulada sem substituir playtest.
#### Escopo
Schema e fixtures.
#### Fora de escopo
Crítico adversarial, relatório de correlação e providers.
#### Critérios de aceitação
Estado coletivo distingue consenso e dissenso e referencia rodadas.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Forçar consenso onde há ambiguidade útil.
#### Evidência necessária para encerrar
Fixture com dissenso válido.

### ISSUE-32 — Definir schema do crítico adversarial
**Prioridade:** P2
**Tipo:** schema
**Fase:** F
**Dependências:** ISSUE-31
#### Objetivo
Modelar ataques à hipótese coletiva, evidências contrárias, fragilidades e resposta do grupo.
#### Problema resolvido
Registra resistência das conclusões sem revelar solução privada ao moderador cego.
#### Escopo
Schema e fixtures.
#### Fora de escopo
Execução automática de crítico e Gate Evaluator privado.
#### Critérios de aceitação
Crítico referencia estado coletivo e separa objeção válida de especulação.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Crítico virar revisor com acesso indevido a solução.
#### Evidência necessária para encerrar
Fixture com objeção baseada em artefato público.

### ISSUE-33 — Criar skill simulated-table
**Prioridade:** P2
**Tipo:** editorial
**Fase:** F
**Dependências:** ISSUE-29, ISSUE-30, ISSUE-31, ISSUE-32
#### Objetivo
Criar skill com análise individual, congelamento, compartilhamento, confronto, síntese, crítico adversarial e orçamento.
#### Problema resolvido
Padroniza piloto manual de mesa sem providers automáticos.
#### Escopo
Skill e instruções de execução manual.
#### Fora de escopo
Automatizar chamadas, criar personas permanentes ou substituir playtest humano.
#### Critérios de aceitação
Skill exige congelamento antes da conversa e registra orçamento/limitações.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`.ai/skills/simulated-table.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Sugerir independência cognitiva inexistente.
#### Evidência necessária para encerrar
Skill declara explicitamente limitações de personas simuladas.

### ISSUE-34 — Executar piloto manual de mesa simulada
**Prioridade:** P2
**Tipo:** editorial
**Fase:** F
**Dependências:** ISSUE-33
#### Objetivo
Registrar perfil, modelo quando conhecido, orçamento, ordem dos documentos, hipóteses individuais, mudanças, consenso, dissenso e limitações.
#### Problema resolvido
Testa a mesa simulada como ferramenta auxiliar, não certificadora.
#### Escopo
Piloto manual documentado com artefatos congelados.
#### Fora de escopo
Providers automáticos, alteração de casos, certificação e substituição de playtest.
#### Critérios de aceitação
Piloto mantém estados individuais e coletivo separados e registra limitações.
#### Validação sugerida
Validação dos schemas da fase F e revisão humana.
#### Arquivos prováveis
Pasta futura de pilotos/relatórios.
#### Riscos
Gastar esforço antes de blind solver e playtest humano comprovarem valor.
#### Evidência necessária para encerrar
Relatório do piloto com artefatos e orçamento.

### ISSUE-35 — Criar relatório de correlação e limitações da mesa simulada
**Prioridade:** P2
**Tipo:** docs
**Fase:** F
**Dependências:** ISSUE-34, ISSUE-10
#### Objetivo
Comparar achados da mesa simulada com playtests humanos e declarar limitações.
#### Problema resolvido
Impede tratar personas como independência cognitiva ou prova de diversão.
#### Escopo
Relatório interpretativo baseado em dados disponíveis.
#### Fora de escopo
Métrica automática, ML, certificação e ajuste de casos.
#### Critérios de aceitação
Relatório distingue correlação, divergência e ausência de evidência.
#### Validação sugerida
Revisão documental por evidência citada.
#### Arquivos prováveis
`docs/` ou pasta futura de relatórios.
#### Riscos
Conclusões fortes demais com poucos dados.
#### Evidência necessária para encerrar
Tabela comparativa com limitações explícitas.

### ISSUE-36 — Definir estrutura de workspace por caso
**Prioridade:** P2
**Tipo:** architecture
**Fase:** G
**Dependências:** ISSUE-03, ISSUE-09, ISSUE-16, ISSUE-28
#### Objetivo
Definir layout de workspace por caso para artefatos, runs, bundles, reviews, findings e decisões.
#### Problema resolvido
Organiza rastreabilidade sem banco de dados.
#### Escopo
Documento/estrutura de diretórios e regras de nomeação.
#### Fora de escopo
CLI de inicialização, orquestrador, providers e migração de dados reais.
#### Critérios de aceitação
Layout acomoda lineage e não interfere no pipeline atual.
#### Validação sugerida
Revisão arquitetural e fixture de árvore vazia.
#### Arquivos prováveis
`docs/`, possível fixture futura.
#### Riscos
Estrutura pesada ou incompatível com output atual.
#### Evidência necessária para encerrar
Exemplo de árvore e regras de ownership.

### ISSUE-37 — Definir workflow declarativo manual
**Prioridade:** P2
**Tipo:** architecture
**Fase:** G
**Dependências:** ISSUE-36
#### Objetivo
Modelar etapas, entradas, saídas, gates e rollback em arquivo declarativo.
#### Problema resolvido
Permite reproduzir fluxo sem orquestrador automático.
#### Escopo
Formato conceitual/schema inicial e exemplo mínimo.
#### Fora de escopo
Executar workflow, providers e CLI unificada.
#### Critérios de aceitação
Workflow referencia etapas e critérios sem acoplar ao build atual.
#### Validação sugerida
Validação de schema ou revisão documental, conforme implementação.
#### Arquivos prováveis
`schemas/`, `docs/`, `tests/` se schema for criado.
#### Riscos
Criar linguagem de workflow grande demais.
#### Evidência necessária para encerrar
Exemplo mínimo validável.

### ISSUE-38 — Implementar inicialização manual do workspace
**Prioridade:** P2
**Tipo:** cli
**Fase:** G
**Dependências:** ISSUE-36, ISSUE-37
#### Objetivo
Criar comando manual para inicializar workspace vazio conforme estrutura aprovada.
#### Problema resolvido
Reduz erro humano ao criar diretórios e manifests iniciais.
#### Escopo
CLI determinística e testes em diretório temporário.
#### Fora de escopo
Ingestão de outputs, execução de etapas e providers.
#### Critérios de aceitação
Comando cria árvore esperada sem sobrescrever conteúdo existente.
#### Validação sugerida
Testes de CLI; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/`, `tests/`.
#### Riscos
Escopo crescer para orquestração completa.
#### Evidência necessária para encerrar
Teste cobrindo inicialização e erro em workspace existente.

### ISSUE-39 — Implementar status e lineage do workspace
**Prioridade:** P2
**Tipo:** domain
**Fase:** G
**Dependências:** ISSUE-38
#### Objetivo
Registrar status de etapas, hashes, run IDs e relações entre artefatos.
#### Problema resolvido
Torna auditável o estado do workspace.
#### Escopo
Leitura/validação de status e lineage.
#### Fora de escopo
Gates, rollback, ingestão automática e UI.
#### Critérios de aceitação
Status referencia artefatos existentes e detecta hash divergente.
#### Validação sugerida
Testes de domínio; `pytest tests/ -q`.
#### Arquivos prováveis
`generator/` ou `scripts/`, `tests/`.
#### Riscos
Duplicar manifest de bundle ou ledger.
#### Evidência necessária para encerrar
Fixture com lineage válido e inválido.

### ISSUE-40 — Implementar ingestão manual de outputs
**Prioridade:** P2
**Tipo:** cli
**Fase:** G
**Dependências:** ISSUE-39
#### Objetivo
Permitir importar outputs de reviews, solvers e playtests para o workspace preservando originais.
#### Problema resolvido
Centraliza artefatos sem alteração silenciosa.
#### Escopo
CLI de ingestão com cópia, hash e validação de schema quando aplicável.
#### Fora de escopo
Executar agentes, editar outputs e consolidar automaticamente decisões.
#### Critérios de aceitação
Ingestão rejeita schema inválido e não sobrescreve original.
#### Validação sugerida
Testes de CLI; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/`, `tests/`.
#### Riscos
Misturar conteúdo privado em área pública.
#### Evidência necessária para encerrar
Teste de ingestão válida e rejeição por visibilidade/schema.

### ISSUE-41 — Implementar gates e rollback manual no workspace
**Prioridade:** P2
**Tipo:** domain
**Fase:** G
**Dependências:** ISSUE-39, ISSUE-40
#### Objetivo
Registrar decisões humanas de gate e rollback para etapa correta.
#### Problema resolvido
Evita remendos tardios e mantém causa ligada à etapa de origem.
#### Escopo
Comandos ou funções para registrar gate, bloqueio e rollback.
#### Fora de escopo
Aplicar rollback automaticamente em conteúdo, providers e UI.
#### Critérios de aceitação
Rollback exige justificativa, etapa alvo e artefatos afetados.
#### Validação sugerida
Testes de transição de status; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/` ou `generator/`, `tests/`.
#### Riscos
Tratar rollback como operação destrutiva.
#### Evidência necessária para encerrar
Fixture com gate aprovado, bloqueado e rollback.

### ISSUE-42 — Criar CLI unificada case_flow
**Prioridade:** P2
**Tipo:** cli
**Fase:** G
**Dependências:** ISSUE-38, ISSUE-39, ISSUE-40, ISSUE-41
#### Objetivo
Unificar comandos manuais comprovados em uma interface `case_flow` ou nome equivalente conforme padrões do repositório.
#### Problema resolvido
Melhora operação depois que capacidades individuais estiverem estáveis.
#### Escopo
CLI agregadora para status, inicialização, ingestão, gates e inspeção.
#### Fora de escopo
Providers, dashboard, execução autônoma e substituição dos comandos menores antes de estabilização.
#### Critérios de aceitação
CLI delega capacidades existentes e mantém compatibilidade com scripts anteriores.
#### Validação sugerida
Testes de CLI; `pytest tests/ -q`.
#### Arquivos prováveis
`scripts/`, `tests/`, docs de operação.
#### Riscos
PR horizontal grande ou abstração prematura.
#### Evidência necessária para encerrar
Comandos anteriores continuam funcionando e CLI unificada passa testes.

### ISSUE-43 — Definir schema de case fingerprint
**Prioridade:** P2
**Tipo:** schema
**Fase:** H
**Dependências:** ISSUE-03, ISSUE-10
#### Objetivo
Modelar fingerprint de caso com mecânica, curva de envelopes, tipos de evidência, fontes de ambiguidade e estrutura de inferência.
#### Problema resolvido
Cria base para diversidade sem alterar casos.
#### Escopo
Schema e fixtures sintéticas.
#### Fora de escopo
Embeddings, ML, bloqueio automático e canônico Avançado.
#### Critérios de aceitação
Fingerprint não usa quantidade de documentos como proxy principal de dificuldade.
#### Validação sugerida
Testes de schema; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `tests/`.
#### Riscos
Reduzir criatividade a checklist mecânico.
#### Evidência necessária para encerrar
Fixture demonstrando inferências e mecânica.

### ISSUE-44 — Extrair fingerprints dos canônicos sem alterá-los
**Prioridade:** P2
**Tipo:** editorial
**Fase:** H
**Dependências:** ISSUE-43
#### Objetivo
Registrar fingerprints dos canônicos existentes como artefatos derivados.
#### Problema resolvido
Permite comparação futura sem mexer nos JSONs canônicos.
#### Escopo
Artefatos derivados e validação contra schema.
#### Fora de escopo
Alterar canônicos, ajustar dificuldade ou iniciar Avançado.
#### Critérios de aceitação
Fingerprints referenciam versões dos casos e não modificam `examples/`.
#### Validação sugerida
Validador de schema; `git diff --check`.
#### Arquivos prováveis
Pasta futura de fingerprints em `docs/` ou `examples/derived/`.
#### Riscos
Vazar spoilers em local público inadequado.
#### Evidência necessária para encerrar
Hashes/versões dos casos fonte e fingerprints validados.

### ISSUE-45 — Criar comparação de similaridade não bloqueante
**Prioridade:** P2
**Tipo:** domain
**Fase:** H
**Dependências:** ISSUE-44
#### Objetivo
Comparar fingerprints com heurísticas transparentes e resultado não bloqueante.
#### Problema resolvido
Ajuda a evitar repetição mecânica sem impedir decisões editoriais.
#### Escopo
Função/CLI de comparação simples e relatório.
#### Fora de escopo
Embeddings, ML, gate obrigatório e geração de caso.
#### Critérios de aceitação
Relatório declara similaridades, diferenças e limitações.
#### Validação sugerida
Testes com fingerprints fixture; `pytest tests/ -q`.
#### Arquivos prováveis
`generator/` ou `scripts/`, `tests/`.
#### Riscos
Pontuação virar ranking absoluto de qualidade.
#### Evidência necessária para encerrar
Relatório fixture com aviso de não bloqueante.

### ISSUE-46 — Criar skill case-diversity-review
**Prioridade:** P2
**Tipo:** editorial
**Fase:** H
**Dependências:** ISSUE-45, ISSUE-23
#### Objetivo
Criar skill para revisar diversidade criativa usando fingerprints e evidência editorial.
#### Problema resolvido
Fornece revisão humana/LLM estruturada sem bloquear automaticamente.
#### Escopo
Skill e critérios de análise.
#### Fora de escopo
Criar caso novo, alterar canônicos, embeddings e ML.
#### Critérios de aceitação
Skill declara que similaridade não é falha automática.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`.ai/skills/case-diversity-review.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Homogeneizar casos por medo de semelhança.
#### Evidência necessária para encerrar
Skill com perguntas de diversidade e limites.

### ISSUE-47 — Modelar grafo de inferências para dificuldade
**Prioridade:** P2
**Tipo:** schema
**Fase:** H
**Dependências:** ISSUE-43
#### Objetivo
Representar relações entre evidências, inferências, pré-requisitos, saltos lógicos e redundância.
#### Problema resolvido
Cria base de dificuldade além da quantidade de documentos.
#### Escopo
Schema/modelo de grafo e fixtures.
#### Fora de escopo
Pontuação final, alteração de casos, ML e Case Review automático.
#### Critérios de aceitação
Modelo representa pelo menos inferência direta, inferência composta e pista redundante.
#### Validação sugerida
Testes de schema/modelo; `pytest tests/ -q`.
#### Arquivos prováveis
`schemas/`, `generator/`, `tests/`.
#### Riscos
Complexidade excessiva para autoria manual.
#### Evidência necessária para encerrar
Fixture de grafo pequeno validado.

### ISSUE-48 — Criar skill difficulty-calibration
**Prioridade:** P2
**Tipo:** editorial
**Fase:** H
**Dependências:** ISSUE-47, ISSUE-23
#### Objetivo
Criar skill para calibrar dificuldade a partir de grafo de inferências, playtests e régua editorial.
#### Problema resolvido
Ajuda a discutir dificuldade com evidência, não apenas volume de material.
#### Escopo
Skill e checklist de calibração.
#### Fora de escopo
Alterar réguas canônicas, bloquear casos ou substituir playtest.
#### Critérios de aceitação
Skill exige comparação com evidência de playtest quando disponível.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`.ai/skills/difficulty-calibration.md`, `.ai/skills/README.md`, `docs/AGENT_SKILLS.md`.
#### Riscos
Transformar estimativa em verdade objetiva.
#### Evidência necessária para encerrar
Skill declara limites e relação com playtest.

### ISSUE-49 — Comparar estimativa automática de dificuldade com playtests
**Prioridade:** P2
**Tipo:** test
**Fase:** H
**Dependências:** ISSUE-47, ISSUE-48, ISSUE-10
#### Objetivo
Comparar estimativas com dados suficientes de playtests humanos.
#### Problema resolvido
Valida se a calibração tem correlação útil antes de virar guardrail.
#### Escopo
Relatório/teste exploratório com dados existentes suficientes.
#### Fora de escopo
Criar regra global, ajustar canônicos, ML e certificação automática.
#### Critérios de aceitação
Relatório declara amostra, divergências, limites e decisão de não generalizar se evidência for fraca.
#### Validação sugerida
Revisão documental e testes se houver função determinística.
#### Arquivos prováveis
`docs/`, `tests/` se aplicável.
#### Riscos
Poucos dados gerarem conclusão exagerada.
#### Evidência necessária para encerrar
Comparação com dados de playtest e decisão explícita.

### ISSUE-50 — Registrar condições de entrada para providers automáticos
**Prioridade:** P3
**Tipo:** architecture
**Fase:** I
**Dependências:** ISSUE-21, ISSUE-34, ISSUE-42
#### Objetivo
Documentar condições mínimas para investigar OpenAI, Anthropic, Ollama ou outros providers no futuro.
#### Problema resolvido
Evita iniciar integração antes de segurança, rastreabilidade e valor manual comprovados.
#### Escopo
Condições de entrada, riscos, requisitos de opt-in e critérios de decisão futura.
#### Fora de escopo
Implementar provider, chamar APIs, armazenar chaves ou escolher fornecedor.
#### Critérios de aceitação
Documento deixa providers como P3 e opcionais, sem dependência para o fluxo oficial.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`docs/`.
#### Riscos
Abrir frente técnica ampla sem evidência.
#### Evidência necessária para encerrar
Lista de pré-condições e decisão humana necessária.

### ISSUE-51 — Registrar condições para benchmark de providers
**Prioridade:** P3
**Tipo:** test
**Fase:** I
**Dependências:** ISSUE-50
#### Objetivo
Definir somente critérios futuros para benchmark de providers, incluindo qualidade, custo, vazamento, reprodutibilidade e limites.
#### Problema resolvido
Impede benchmark prematuro sem protocolo de segurança.
#### Escopo
Plano conceitual de benchmark futuro.
#### Fora de escopo
Rodar benchmark, integrar APIs ou comparar modelos reais agora.
#### Critérios de aceitação
Critérios exigem bundles seguros e outputs versionados antes de qualquer teste.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`docs/`.
#### Riscos
Virar ranking de modelos sem contexto.
#### Evidência necessária para encerrar
Checklist de pré-requisitos não implementado.

### ISSUE-52 — Registrar condições para RAG e embeddings
**Prioridade:** P3
**Tipo:** architecture
**Fase:** I
**Dependências:** ISSUE-50
#### Objetivo
Documentar quando RAG ou embeddings poderiam ser investigados sem virar dependência do jogo.
#### Problema resolvido
Mantém offline-first e evita indexar conteúdo privado sem necessidade.
#### Escopo
Condições futuras, riscos de privacidade e critérios de opt-in.
#### Fora de escopo
Implementar embeddings, vector DB, busca semântica ou RAG.
#### Critérios de aceitação
Documento declara que RAG/embeddings não são necessários para solução dos casos.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`docs/`.
#### Riscos
Criar dependência externa ou vazar spoilers.
#### Evidência necessária para encerrar
Registro de condições e riscos.

### ISSUE-53 — Registrar condições para ML, fine-tuning e custo automatizado
**Prioridade:** P3
**Tipo:** architecture
**Fase:** I
**Dependências:** ISSUE-50
#### Objetivo
Definir condições futuras para ML, fine-tuning e estimativas automáticas de custo.
#### Problema resolvido
Impede iniciar aprendizado automatizado antes de dados suficientes e governança.
#### Escopo
Critérios de dados, privacidade, custo e reversibilidade.
#### Fora de escopo
Treinar modelos, coletar dataset, automatizar custos ou criar telemetria.
#### Critérios de aceitação
Condições exigem dados consentidos, minimização e aprovação humana.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`docs/`.
#### Riscos
Transformar playtests em dataset sem consentimento.
#### Evidência necessária para encerrar
Registro de pré-condições e bloqueios explícitos.

### ISSUE-54 — Registrar condições para geração massiva e inteligência editorial futura
**Prioridade:** P3
**Tipo:** editorial
**Fase:** I
**Dependências:** ISSUE-50, ISSUE-51, ISSUE-52, ISSUE-53
#### Objetivo
Documentar condições para geração massiva e inteligência editorial futura sem abrir implementação.
#### Problema resolvido
Mantém foco em baseline, playtest e qualidade manual antes de escala.
#### Escopo
Condições de entrada, riscos editoriais e critérios de qualidade.
#### Fora de escopo
Gerar casos em massa, canônico Avançado, marketplace, dashboard e providers.
#### Critérios de aceitação
Issue permanece P3 e exige evidência de qualidade antes de escala.
#### Validação sugerida
Revisão documental.
#### Arquivos prováveis
`docs/`.
#### Riscos
Diluir identidade do Indiciário e repetir mecânicas.
#### Evidência necessária para encerrar
Registro explícito de que não é tarefa pronta para implementação imediata.

## 5. Priorização

Distribuição proposta:

- **P0 — 10 issues:** ISSUE-01, ISSUE-02, ISSUE-03, ISSUE-05, ISSUE-06, ISSUE-07, ISSUE-08, ISSUE-09, ISSUE-11, ISSUE-12.
  - Bloqueiam segurança de contexto, registro do próximo playtest, confiabilidade do Learning Loop e contratos essenciais.
- **P1 — 13 issues:** ISSUE-04, ISSUE-13, ISSUE-14, ISSUE-15, ISSUE-16, ISSUE-17, ISSUE-18, ISSUE-19, ISSUE-20, ISSUE-21, ISSUE-22, ISSUE-23, ISSUE-28.
  - Viabilizam Blind Solver manual, Gate Evaluator, piloto controlado, rastreabilidade e consolidação inicial.
- **P2 — 26 issues:** ISSUE-10, ISSUE-24, ISSUE-25, ISSUE-26, ISSUE-27, ISSUE-29, ISSUE-30, ISSUE-31, ISSUE-32, ISSUE-33, ISSUE-34, ISSUE-35, ISSUE-36, ISSUE-37, ISSUE-38, ISSUE-39, ISSUE-40, ISSUE-41, ISSUE-42, ISSUE-43, ISSUE-44, ISSUE-45, ISSUE-46, ISSUE-47, ISSUE-48, ISSUE-49.
  - Cobrem mesa simulada, workspace, diversidade, dificuldade e exemplos após a fundação estar comprovada.
- **P3 — 5 issues:** ISSUE-50, ISSUE-51, ISSUE-52, ISSUE-53, ISSUE-54.
  - Mantêm providers, ML, RAG, automação ampla e inteligência editorial futura fora da implementação imediata.

## 6. Dependências e caminho crítico

Diagrama textual do caminho crítico proposto:

```text
ISSUE-01/ISSUE-02
  ↓
ISSUE-03
  ↓
ISSUE-05/ISSUE-06/ISSUE-07
  ↓
ISSUE-08/ISSUE-09
  ↓
ISSUE-11/ISSUE-12
  ↓
ISSUE-13/ISSUE-14/ISSUE-15/ISSUE-16
  ↓
ISSUE-17/ISSUE-18/ISSUE-19/ISSUE-20
  ↓
ISSUE-21
  ↓
ISSUE-23/ISSUE-28
  ↓
ISSUE-29–ISSUE-49
  ↓
ISSUE-50–ISSUE-54 somente após decisão futura
```

### Caminho crítico

O caminho crítico para uma primeira validação multiagente manual é:

1. governança e cegueira documental: ISSUE-01, ISSUE-02, ISSUE-03;
2. Learning Loop mínimo para registrar playtests e findings: ISSUE-05, ISSUE-06, ISSUE-07, ISSUE-08, ISSUE-09;
3. Context Firewall mínimo: ISSUE-11, ISSUE-12, ISSUE-13, ISSUE-14, ISSUE-15, ISSUE-16;
4. Blind Solver/Gate Evaluator mínimo: ISSUE-17, ISSUE-18, ISSUE-19, ISSUE-20, ISSUE-21.

### Tarefas paralelizáveis

- ISSUE-01 e ISSUE-02 podem ser rascunhadas em paralelo, mas devem convergir antes de ISSUE-03.
- ISSUE-05, ISSUE-06 e ISSUE-07 podem ser trabalhadas em paralelo após ISSUE-03.
- ISSUE-11 e ISSUE-12 podem avançar em paralelo após ISSUE-02/ISSUE-03.
- ISSUE-24, ISSUE-25 e ISSUE-26 podem avançar em paralelo após ISSUE-23.
- ISSUE-29, ISSUE-30, ISSUE-31 e ISSUE-32 devem manter ordem de dependência, mas podem ser revisadas como um pacote conceitual antes de implementação.
- ISSUE-43 e ISSUE-47 podem evoluir em paralelo após contratos essenciais e exemplos suficientes.

### Tarefas que não devem começar cedo

- ISSUE-18 não deve começar antes de manifest, protocolo de cegueira e schema de output do solver.
- ISSUE-21 não deve começar antes de bundle, leak check e Gate Evaluator.
- ISSUE-33/ISSUE-34 não devem começar antes do piloto de Blind Solver trazer evidência útil.
- ISSUE-42 não deve começar antes de comandos menores comprovados.
- ISSUE-50–ISSUE-54 não devem começar como implementação enquanto providers, RAG, embeddings, ML e geração massiva continuarem P3.

### Pontos de validação humana

- Após ISSUE-01/ISSUE-02/ISSUE-03: validar conceitos e autoridade humana.
- Após ISSUE-09: confirmar que o próximo playtest pode ser registrado sem fricção excessiva.
- Após ISSUE-16: revisar segurança de contexto e limites de vazamento.
- Após ISSUE-21: decidir se o piloto justifica continuar para revisões estruturadas.
- Após ISSUE-35: comparar mesa simulada com playtest humano antes de confiar em correlação.
- Antes de ISSUE-50–ISSUE-54: decisão explícita de produto/arquitetura.

## 7. Próxima PR recomendada

A próxima PR de implementação deve ser documental e não deve criar código.

Recomendação: separar em duas PRs para reduzir risco conceitual:

1. **PR 1 — Protocolo operacional multiagente manual-first**
   - Implementa ISSUE-01.
   - Opcionalmente inclui a parte conceitual mínima de ISSUE-03 se a definição de `artifact_id`/`run_id` for necessária para explicar o protocolo, mas sem schema.
2. **PR 2 — Protocolo de contexto cego e segurança**
   - Implementa ISSUE-02.
   - Refina contratos de visibilidade usados por ISSUE-03, ainda sem schema ou código.

Se houver pouco tempo de revisão, prefira começar apenas pela PR 1. A razão é que o protocolo operacional define papéis, autoridade humana e manual-first; sem isso, o protocolo de cegueira pode ficar tecnicamente correto, mas operacionalmente ambíguo.

## 8. Não objetivos desta PR

Esta PR não cria:

- arquivos `.ai/skills/*.md`;
- schemas;
- scripts;
- código;
- testes novos;
- bundles;
- exemplos de playtest;
- alterações em casos;
- alterações no roadmap;
- issues reais no GitHub;
- providers;
- banco;
- dashboard;
- builds de PDF.

Esta PR cria apenas `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md`.

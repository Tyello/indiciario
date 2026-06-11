# PRD — Indiciário Story Pipeline: Criação e revisão multiagente de casos

## 1. Título

**Indiciário Story Pipeline — Criação e revisão multiagente de casos**.

Este PRD descreve uma capacidade futura, manual-first e incremental, para estruturar a criação de novos casos em etapas versionadas, com autores, revisores independentes, Blind Solvers, mesa investigativa simulada, gates explícitos, rollback para a etapa correta e Learning Loop de playtest.

## 2. Objetivo

Criar um processo implementável para evoluir a autoria de casos do Indiciário sem substituir o fluxo oficial atual, garantindo que:

- cada etapa produza um artefato versionado;
- agente autor, agente revisor, papel cego e orquestrador tenham responsabilidades separadas;
- revisores independentes avaliem cada etapa antes do avanço;
- agentes cegos recebam apenas o que um jogador teria naquele momento;
- Blind Solvers tentem resolver cada envelope sem solução, gabarito ou metadados reveladores;
- múltiplos agentes possam formar uma mesa investigativa simulada;
- problemas retornem à etapa correta, sem remendos tardios;
- aprendizados de playtest sejam registrados sem virar regra global automaticamente;
- novos casos evitem repetir mecanicamente a arquitetura dos canônicos anteriores;
- playtest humano continue sendo a validação final de diversão, ritmo, emoção e justiça percebida.

## 3. Problema

O fluxo atual já funciona do Blueprint ao pacote final, mas a criação anterior ao Blueprint ainda pode depender de decisões autorais pouco rastreáveis. Isso dificulta responder:

- qual hipótese foi considerada em cada etapa;
- quem revisou sem conhecer a solução;
- se um envelope é resolvível por evidência ou por inferência inventada;
- se uma falha pertence à premissa, narrativa, arquitetura do mistério, envelope, documento, visual ou pacote;
- quais aprendizados de playtest são recorrentes e quais são apenas ocorrências isoladas;
- se um novo caso está repetindo a mesma mecânica, curva de envelopes ou twist dos casos anteriores.

A proposta cria uma camada de governança editorial antes e depois do Blueprint, sem alterar agora schemas, validator, Case Kernel, Case Review, renderer, templates, PDFs ou casos canônicos.

## 4. Não-objetivos

Fora do escopo inicial deste PRD:

- automação de chamadas para provedores;
- múltiplos modelos em produção;
- machine learning próprio;
- embeddings e RAG;
- fine-tuning;
- banco de dados;
- dashboard;
- editor visual;
- geração massiva de casos;
- novo caso Avançado;
- alteração dos casos canônicos;
- mudança no Blueprint atual;
- mudança no validator;
- mudança no Case Kernel;
- mudança no Case Review;
- alteração de templates ou PDFs;
- criação de arquivos `.ai/skills/*.md` nesta tarefa;
- implementação de orquestrador, agentes executáveis, scripts, providers de LLM ou pipelines automáticos nesta tarefa.

O PRD também não autoriza iniciar o canônico Avançado antes da prioridade atual: baseline visual real, revisão de pacotes e novo playtest do Intermediário.

## 5. Cenários de uso

### 5.1 Criação de caso novo sem pular direto para Blueprint

Um autor prepara Brief, Laboratório de premissas, Bíblia narrativa, Arquitetura do mistério, Planejamento de envelopes e Planejamento documental. Cada etapa gera artefato próprio e passa por revisão independente antes de avançar.

### 5.2 Revisão cega de envelope

Um Blind Solver recebe apenas pergunta pública, instruções públicas, documentos já liberados, ferramentas públicas de apoio e envelopes disponíveis até aquele momento. Ele registra fatos, hipóteses, evidências, contradições, informações ausentes e decisão de avanço.

### 5.3 Mesa investigativa simulada

Vários agentes recebem o mesmo bundle público, analisam isoladamente, congelam hipóteses individuais e depois participam de conversa estruturada mediada por um moderador cego. Um crítico adversarial tenta derrubar a hipótese coletiva sem conhecer a solução.

### 5.4 Aprendizado pós-playtest

Um playtest humano gera observações, findings, hipóteses causais, correções no caso, revalidação e decisão explícita sobre generalização. Uma ocorrência isolada é registrada, mas não vira regra global sem recorrência ou justificativa forte.

## 6. Escopo funcional

### 6.1 Princípios arquiteturais

#### Separação de responsabilidades

- Agente autor não certifica sozinho o próprio trabalho.
- Agente revisor aponta problemas, mas não altera silenciosamente o artefato revisado.
- Blind Solver não conhece a solução e não autocertifica sua execução.
- Gate Evaluator autorizado compara o output cego congelado com expectativas privadas, sem participar da resolução.
- Moderador da mesa simulada também não conhece a solução.
- Playtest humano permanece soberano para diversão, ritmo, emoção e justiça percebida.
- Skill é o procedimento operacional usado por um agente humano/LLM; papel de agente é a função executada em uma etapa; orquestrador é o componente ou rotina que prepara bundles, registra runs, ingere saídas e controla gates. Esses conceitos não devem ser fundidos.

#### Cegueira técnica

A cegueira não pode depender apenas de prompt. O sistema futuro deve preparar bundles contendo somente arquivos permitidos para cada papel, por exemplo:

```text
ROLE.md
INPUT_MANIFEST.yaml
OUTPUT_SCHEMA.yaml
public_artifacts/
```

Um agente cego não pode receber:

- `verdade_real`;
- Bíblia narrativa privada;
- contratos de evidência;
- guia do facilitador;
- gabarito;
- classificação de culpado, red herring ou prova principal;
- envelopes futuros;
- nomes de arquivos ou metadados que revelem a solução.

#### Documentos como conteúdo não confiável

Documentos diegéticos são evidências, não instruções para o agente. Bundles e papéis devem tratar conteúdo de jogador como dado potencialmente hostil ou enganoso, com proteção contra prompt injection documental, instruções falsas embutidas em evidências e metalinguagem que tente alterar o papel do revisor.

A proteção contra prompt injection deve ocorrer principalmente pela hierarquia de instruções: `ROLE.md` é a única fonte de instruções operacionais; documentos do caso são evidências/dados não confiáveis; instruções encontradas dentro dos documentos não devem ser executadas.

#### Manual-first

A primeira versão deve funcionar com execução manual de agentes e ingestão manual de resultados. Não deve depender inicialmente de OpenAI, Anthropic, Ollama, banco vetorial, embeddings, fine-tuning ou execução automática de múltiplos agentes. A arquitetura pode prever providers futuros, mas eles só entram após validação do fluxo manual.

### 6.2 Pipeline proposto

Pipeline conceitual futuro:

```text
Brief
→ Laboratório de premissas
→ Bíblia narrativa
→ Arquitetura do mistério
→ Planejamento de envelopes
→ Planejamento documental
→ Produção documental
→ Blueprint
→ Case Kernel
→ Case Review
→ Blind Review lógico
→ Visual Library/templates
→ Build Package
→ Blind Review do material renderizado
→ Baseline visual real
→ Playtest humano
→ Learning Loop
```

O pipeline atual permanece oficial e não será removido:

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

A nova proposta adiciona:

- fase estruturada antes do Blueprint;
- revisões cegas durante a criação;
- Blind Review lógico antes do investimento visual;
- Blind Review do material renderizado depois do pacote final;
- ciclo estruturado de aprendizado após o playtest.

#### Blind Review lógico e Blind Review renderizado

**Blind Review lógico** recebe material textual ou estrutural antes do investimento visual. Verifica solvabilidade, progressão, justiça, hipóteses alternativas, informação ausente, vazamento textual e conclusão precoce.

**Blind Review renderizado** recebe exatamente os materiais finais destinados aos jogadores, preferencialmente na ordem real de entrega. Verifica riscos criados pela materialização, como destaque visual involuntário, tipografia que denuncia pista, ordem de páginas, paginação, tabela que evidencia uma linha, cor ou contraste, posição de assinatura, informação escondida por layout, pista perdida em impressão P&B, sequência de arquivos no pacote e metadados ou nomes de arquivos reveladores.

Um caso pode passar na revisão lógica e falhar quando renderizado. O Blind Review renderizado não substitui baseline visual humano nem playtest.

### 6.3 Revisão independente por etapa

#### Laboratório de premissas

Revisores sugeridos:

- Cold Reader;
- auditor de diversidade;
- crítico de clichês.

O Cold Reader recebe somente:

- título;
- logline;
- incidente;
- pergunta pública;
- sinopse sem solução.

#### Bíblia narrativa

Revisores sugeridos:

- revisor de plausibilidade humana;
- leitor emocional;
- crítico de motivação;
- crítico de relações causais.

#### Arquitetura do mistério

Revisores sugeridos:

- Mystery Grill;
- Adversarial Solver;
- auditor de justiça;
- auditor de evidências.

#### Planejamento de envelope

Revisores sugeridos:

- Blind Solver individual;
- calibrador de dificuldade;
- auditor de progressão.

#### Produção documental

Revisores sugeridos:

- auditor de diegese;
- auditor de vazamento;
- auditor anti-obviedade;
- revisor visual/documental quando aplicável.

#### Blueprint final

Executar conceitualmente:

- validator;
- Case Kernel;
- Case Review;
- Blind Review lógico;
- Visual Library/templates;
- Build Package;
- Blind Review do material renderizado;
- mesa investigativa simulada;
- crítico adversarial da hipótese coletiva.

### 6.4 Blind Solver por envelope

O Blind Solver deve trabalhar em sessão isolada e receber apenas:

- pergunta pública;
- instruções públicas;
- documentos já liberados;
- ferramentas públicas de apoio;
- envelopes disponíveis até aquele momento.

Saída estruturada conceitual:

```yaml
pergunta_publica_compreendida: ""
fatos_observados: []
hipoteses:
  - descricao: ""
    confianca: 0.0
    evidencias: []
    contradicoes: []
suspeitos_ordenados: []
conclusoes_sustentadas: []
conclusoes_nao_sustentadas: []
informacoes_ausentes: []
documentos_ignorados: []
documentos_superinterpretados: []
decisao:
  status: advance | stay | request_hint
confianca_geral: 0.0
```

O Blind Solver declara quais artefatos analisou, mas essa declaração não prova isolamento. A certificação de quais artefatos foram disponibilizados pertence ao Context Firewall e ao manifest do bundle.

#### Gate Evaluator

Fluxo de decisão:

```text
Blind Solver
→ output congelado/selado
→ Gate Evaluator autorizado
→ decisão do gate
```

O Gate Evaluator:

- não participa da resolução;
- não conversa com o Blind Solver antes do output ser congelado;
- recebe o relatório final do Blind Solver;
- pode acessar as expectativas privadas necessárias;
- compara conclusões observadas com conclusões esperadas;
- não altera a resposta original do solver;
- registra divergências, vazamentos e hipóteses inesperadas;
- decide PASS, REVISE, BLOCK ou INCONCLUSIVE;
- indica a etapa correta de rollback.

Exemplo conceitual:

```yaml
gate_evaluation:
  stage: E1
  solver_run_id: RUN-0041
  expected_conclusions:
    - C-E1-JANELA
    - C-E1-INCONSISTENCIA
  observed_conclusions:
    - C-E1-JANELA
  unexpected_valid_hypotheses: []
  final_solution_leaked: false
  status: REVISE
  reason: >
    O solver percebeu a janela temporal, mas não encontrou a
    inconsistência necessária para justificar a abertura do E2.
  rollback_target: envelope_design
```

Estados de gate:

- **PASS**: o envelope sustenta a decisão esperada para aquele momento, sem vazamento de solução e sem exigir inferência inexistente.
- **REVISE**: há problema corrigível na etapa atual ou anterior, mas o fluxo ainda é compreensível e não invalida a justiça do caso.
- **BLOCK**: há falha que impede avanço justo ou compromete a integridade do mistério.
- **INCONCLUSIVE**: a execução não permite decisão confiável; requer novo solver, bundle corrigido, instrução mais clara ou evidência adicional de teste.

Exemplos de bloqueio:

- solução correta totalmente visível no E1;
- pergunta pública não compreendida;
- alternativa igualmente válida permanece aberta;
- conclusão obrigatória depende de informação inexistente;
- o agente só consegue resolver inventando premissas;
- o agente encontra vazamento de solução.

### 6.5 Mesa investigativa simulada

A simulação coletiva ocorre em duas fases.

#### Fase individual

Cada agente analisa o mesmo bundle de forma isolada. Hipóteses individuais são registradas e congeladas antes da conversa.

#### Fase coletiva

Rodadas sugeridas:

1. compartilhamento sem confronto;
2. confronto de evidências;
3. síntese coletiva.

Perfis possíveis:

- generalista;
- cronológico;
- documental;
- humano/relacional;
- cético probatório.

Perfis alteram foco de atenção, mas não fornecem pistas secretas.

O moderador:

- não conhece a solução;
- exige referência documental;
- registra divergências;
- impede que confiança seja tratada como prova;
- não indica quais documentos devem ser cruzados.

Após a conversa, um crítico adversarial recebe documentos públicos, estado coletivo e hipótese final da mesa, e tenta derrubar a teoria sem acesso à solução real.

A simulação deve medir:

- hipótese individual versus hipótese adotada pelo grupo;
- acertos abandonados;
- erros amplificados;
- consenso por evidência versus consenso por autoridade;
- documentos ignorados;
- documentos superinterpretados;
- recontextualização após novo envelope;
- necessidade de dica;
- teorias alternativas ainda defensáveis.

A mesa simulada deve operar sob orçamento explícito. Valores concretos serão definidos em implementação futura, mas o run deve registrar limites conceituais como:

```yaml
simulation_budget:
  individual_analysis_limit: ""
  discussion_rounds: 3
  messages_per_agent_per_round: 1
  maximum_challenges_per_agent: 2
  hints_allowed: 0
  document_reopen_limit: ""
  maximum_total_tokens: ""
```

A conversa não é ilimitada: número de rodadas, quantidade de intervenções, uso de dicas e releituras podem ser controlados. O orçamento faz parte dos metadados do run, e runs com orçamentos diferentes não devem ser comparados como equivalentes. O objetivo é testar solvabilidade sob restrições, não descobrir se a LLM resolve o caso com tempo e tokens infinitos.

Mesa simulada não substitui playtest humano.

### 6.6 Context Firewall

Capacidade futura responsável por preparar bundles tecnicamente cegos. Deve:

- aplicar políticas de visibilidade;
- copiar apenas artefatos autorizados;
- sanitizar metadados;
- normalizar nomes de arquivos;
- impedir acesso a etapas futuras;
- remover classificações internas;
- calcular hash dos arquivos;
- gerar manifest;
- registrar versão dos artefatos;
- proteger contra prompt injection documental;
- permitir auditoria posterior do que cada agente recebeu.

A prova de isolamento deve vir do manifest do bundle, da política de visibilidade, dos hashes, do relatório de violações e da comparação entre artefatos autorizados e disponibilizados. O Blind Solver informa quais artefatos analisou; o Context Firewall certifica quais artefatos foram disponibilizados.

Exemplo conceitual:

```yaml
bundle:
  bundle_id: BND-E1-004
  role: blind_solver
  stage: E1
  allowed_artifacts:
    - E1-01
    - E1-02
    - E1-03
  forbidden_categories:
    - private_author
    - facilitator
    - future_envelope
  isolation_check:
    passed: true
    violations: []
  manifest_hash: ""
```

Visibilidades sugeridas:

- `public_player`;
- `private_author`;
- `review_private`;
- `facilitator`;
- `derived_report`;
- `playtest_anonymized`.

#### Sanitização não destrutiva

O Context Firewall pode remover metadados técnicos, normalizar nomes de arquivos, excluir comentários ocultos, impedir exposição de caminhos internos, impedir acesso a artefatos proibidos e tratar documentos como conteúdo não confiável. Ele não pode reescrever silenciosamente o conteúdo visível das evidências entregues aos jogadores.

A sanitização padrão deve ser não destrutiva. Ela pode remover metadados que não fazem parte da experiência, renomear arquivos, remover campos internos invisíveis ao jogador e isolar instruções operacionais em `ROLE.md`. Ela não pode modificar frases, corrigir conteúdo, remover evidência, resumir documento, substituir terminologia, esconder informação visível ou tornar uma pista mais ou menos clara.

Qualquer transformação do conteúdo visível deve criar um artefato derivado, preservar o original, registrar o motivo, registrar o diff, alterar o hash, invalidar comparações diretas com runs anteriores e passar por nova revisão.

Metadados conceituais para artefatos futuros:

```yaml
artifact_id: ""
stage: ""
visibility: ""
contains_solution: false
generated_by: ""
derived_from: []
version: ""
```

### 6.7 Gates e rollback

Cada etapa possui gate explícito com estados `PASS`, `REVISE`, `BLOCK` ou `INCONCLUSIVE`.

Todo finding deve indicar a etapa correta de correção:

- `premise`;
- `narrative`;
- `mystery_architecture`;
- `envelope_design`;
- `document_spec`;
- `document_content`;
- `blueprint`;
- `visual`;
- `package`.

Exemplos de rollback:

- motivo não inferível → voltar para narrativa ou arquitetura do mistério;
- E1 resolve tudo → voltar para planejamento de envelope;
- documento artificial → voltar para spec documental;
- mapa entrega rota → voltar para visual/mapa;
- solução alternativa aberta → voltar para arquitetura do mistério.

O processo não deve corrigir falhas profundas adicionando um documento explicativo no último envelope.

### 6.8 Learning Loop do playtest

Ciclo futuro:

```text
Playtest
→ sessão registrada
→ observações
→ findings
→ hipóteses causais
→ correção no caso
→ revalidação
→ decisão de generalização
→ documentação/heurística/teste quando aplicável
```

Estados sugeridos para findings:

- `observed`;
- `hypothesis`;
- `corrected_in_case`;
- `revalidated`;
- `recurring_pattern`;
- `candidate_rule`;
- `canonical_rule`;
- `rejected_generalization`.

Toda ocorrência deve ser registrada, mas nem toda ocorrência deve virar regra. Cada finding precisa registrar decisão sobre:

- correção do caso;
- documentação;
- teste de regressão;
- validator;
- Case Review;
- escopo;
- revalidação;
- generalização.

Escopos possíveis:

- `case_only`;
- `mechanic_family`;
- `difficulty_level`;
- `global_editorial`;
- `technical`;
- `visual`.

Separação conceitual:

- **Invariantes**: regras de justiça, solvabilidade e integridade.
- **Heurísticas**: boas práticas dependentes de gênero, dificuldade ou mecânica.
- **Decisões criativas**: escolhas específicas do caso que não devem virar padrão global.

### 6.9 Diversidade criativa

Case fingerprint conceitual:

```yaml
public_question_type: ""
incident_type: ""
truth_structure: ""
responsibility_model: ""
primary_mechanic: ""
secondary_mechanic: ""
progression_shape: ""
evidence_family: ""
reveal_type: ""
human_conflict: ""
ending_type: ""
```

Comparação com casos anteriores deve inicialmente gerar apenas warning, sem bloqueio automático. O objetivo é detectar repetição de:

- mesma mecânica;
- mesma curva de envelopes;
- mesmo tipo de twist;
- mesmo tipo de responsável;
- mesma evidência dominante;
- mesma consequência emocional.

Cada caso futuro pode declarar experimento criativo:

```yaml
hypothesis: ""
risk: ""
measurement: []
success_criteria: []
```

### 6.10 Dificuldade

A classificação futura deve separar:

- qualidade narrativa;
- dificuldade dedutiva;
- carga de leitura;
- complexidade de navegação;
- complexidade narrativa;
- necessidade de suporte.

Não tratar quantidade de documentos como dificuldade. A dificuldade deve considerar:

- profundidade do grafo de inferências;
- hipóteses concorrentes;
- ambiguidade;
- quantidade de recontextualizações;
- pistas por ausência;
- operações mentais;
- necessidade de combinar conclusões;
- uso de dicas;
- resultados de Blind Solvers;
- resultados da mesa simulada;
- dados de playtest humano.

A qualidade narrativa deve permanecer alta em todos os níveis, do Iniciante ao Mestre.

### 6.11 Reprodutibilidade e rastreabilidade

Toda execução futura deve registrar conceitualmente:

```yaml
run_id: ""
case_version: ""
workflow_version: ""
skill_version: ""
role_version: ""
provider: ""
model: ""
parameters: {}
input_manifest_hash: ""
output_hash: ""
started_at: ""
finished_at: ""
```

O sistema deve permitir responder:

- o que o agente recebeu;
- qual versão recebeu;
- qual papel executou;
- qual output produziu;
- qual finding surgiu;
- qual PR corrigiu;
- como foi revalidado.

### 6.12 Métricas futuras

Métricas desejadas, sem coleta automática nesta tarefa:

- horas humanas por caso;
- horas humanas por etapa;
- quantidade de revisões;
- taxa de bloqueio por etapa;
- tempo para corrigir findings;
- tokens e custo por agente;
- documentos ignorados;
- documentos dominantes;
- hipóteses alternativas abertas;
- dicas necessárias;
- tempo real de playtest;
- satisfação;
- surpresa;
- justiça percebida;
- diversão;
- confiança da classificação de dificuldade.

## 7. Escopo técnico

### 7.1 Artefatos conceituais futuros

A primeira implementação deve priorizar documentação e arquivos de governança, antes de qualquer automação. Artefatos conceituais esperados:

- definição de etapas e gates;
- políticas de visibilidade;
- modelo conceitual de `artifact_id`, versão, hash e lineage;
- formato de manifest de bundle;
- formato de saída do Blind Solver;
- formato de avaliação do Gate Evaluator;
- formato de findings e Learning Loop;
- formato de fingerprint e experimento criativo.

### 7.2 Novas skills futuras propostas

Não criar estes arquivos nesta tarefa. As descrições abaixo servem como backlog conceitual.

#### Fundação

| Skill | Quando usar | Entradas permitidas | Entradas proibidas | Saída | Gate/decisão |
|---|---|---|---|---|---|
| `context-firewall` | Preparar bundle cego para papel específico. | Políticas de visibilidade, artefatos autorizados, schemas de saída. | Solução privada para papéis cegos, envelopes futuros, metadados reveladores. | Bundle, manifest, hashes, relatório de isolamento. | Bundle aprovado ou bloqueado. |
| `blind-solve` | Testar envelope ou caso sem solução. | Bundle `public_player`, instruções públicas, documentos liberados. | Gabarito, guia do facilitador, contratos, `verdade_real`, classificações internas. | Relatório estruturado de fatos, hipóteses, artefatos analisados e decisão sugerida. | Output congelado para avaliação posterior por Gate Evaluator. |
| `playtest-to-learning` | Converter playtest em ledger de aprendizado. | Registro de sessão, observações, métricas humanas, artefatos usados. | Reescrita automática de caso, generalização automática. | Findings, hipóteses causais, decisões de escopo. | Corrigir caso, observar mais ou propor regra candidata. |

#### Editorial

| Skill | Quando usar | Entradas permitidas | Entradas proibidas | Saída | Gate/decisão |
|---|---|---|---|---|---|
| `mystery-grill` | Pressionar arquitetura do mistério antes de documentos. | Pergunta pública, verdade privada para revisor autorizado, contratos, envelopes planejados. | Alteração silenciosa do artefato. | Lista de falhas, alternativas abertas e rollback sugerido. | Aprovar arquitetura ou revisar. |
| `simulated-table` | Simular mesa multiagente manual. | Bundle público, perfis, protocolo de rodadas. | Solução real, guia do facilitador, pistas secretas. | Hipóteses individuais, síntese coletiva, divergências. | Sinalizar avanço, dica, revisão ou bloqueio. |
| `learning-governance` | Decidir se finding vira heurística ou regra. | Findings revalidados, recorrência, impacto, escopo. | Ocorrência isolada tratada como regra global sem justificativa. | Decisão de generalização e documentação. | Rejeitar, manter local, promover a heurística ou regra. |

#### Evolução

| Skill | Quando usar | Entradas permitidas | Entradas proibidas | Saída | Gate/decisão |
|---|---|---|---|---|---|
| `case-diversity-review` | Comparar fingerprint com casos anteriores. | Fingerprints, resumo público e metadados editoriais. | Bloqueio automático por semelhança isolada. | Warnings de repetição e oportunidades criativas. | Warning, revisão criativa ou aceite justificado. |
| `difficulty-calibration` | Calibrar dificuldade dedutiva e suporte. | Grafo de inferência, blind solves, mesa simulada, playtests. | Contagem simples de documentos como proxy principal. | Classificação argumentada por dimensões. | Ajustar dificuldade, suporte ou progressão. |
| `diegesis-audit` | Revisar se documentos parecem documentos reais. | Specs e conteúdos documentais públicos. | Gabarito como instrução para jogador. | Findings de artificialidade, voz do autor e metajogo. | Revisar spec/conteúdo ou aprovar. |
| `evidence-audit` | Verificar justiça e suficiência das evidências. | Arquitetura, contratos e documentos autorizados ao revisor. | Reescrever solução sem autorização. | Lacunas, redundâncias e dependências frágeis. | Corrigir arquitetura, envelope ou documento. |

#### Futuro

| Skill | Quando usar | Entradas permitidas | Entradas proibidas | Saída | Gate/decisão |
|---|---|---|---|---|---|
| `retrieval-curation` | Curar contexto para agentes quando houver base documental maior. | Artefatos autorizados e políticas de visibilidade. | RAG irrestrito com solução para papel cego. | Pacote de contexto auditável. | Contexto aprovado ou bloqueado. |
| `prompt-regression` | Testar prompts/papéis contra casos conhecidos. | Casos de teste, bundles, saídas esperadas. | Uso de dados privados em testes cegos. | Relatório de regressão de prompt. | Prompt aprovado, revisar ou bloquear. |
| `provider-benchmark` | Comparar provedores após fluxo manual validado. | Tarefas padronizadas, bundles, métricas. | Decisão por benchmark sem playtest humano. | Comparativo de qualidade, custo e risco. | Provider recomendado ou rejeitado. |
| `cost-audit` | Controlar custo operacional futuro. | Runs, tokens, duração, retries, saídas. | Conteúdo privado desnecessário. | Relatório de custo por etapa/agente. | Otimizar, limitar ou manter. |

## 8. Critérios de aceitação

O PRD e futuras implementações derivadas devem cumprir:

1. preservar o pipeline atual;
2. preservar a prioridade atual do roadmap;
3. diferenciar claramente skill, papel de agente e orquestrador;
4. definir cegueira técnica;
5. definir revisão independente ao final de cada etapa;
6. definir Blind Solver por envelope;
7. definir Gate Evaluator como responsável por comparar output cego congelado com expectativas privadas;
8. definir mesa multiagente com análise individual anterior e orçamento conceitual;
9. definir Context Firewall como responsável pela prova de isolamento via manifest;
10. definir sanitização não destrutiva;
11. definir gates e rollback;
12. definir Learning Loop;
13. impedir generalização automática de um playtest isolado;
14. definir diversidade criativa;
15. separar dificuldade de carga documental;
16. manter playtest humano como validação final;
17. diferenciar Blind Review lógico e Blind Review do material renderizado;
18. propor rollout incremental;
19. propor decomposição em PRs pequenas;
20. não implementar nenhuma feature nesta tarefa.

Critérios verificáveis para a primeira PR de implementação futura:

- nenhum caso canônico é alterado;
- nenhum schema ou validator é alterado sem PR própria;
- qualquer bundle cego possui manifest com hashes, política de visibilidade e relatório de isolamento;
- qualquer finding possui etapa de correção indicada;
- qualquer relatório de Blind Solver lista os artefatos analisados;
- nenhum relatório de Blind Solver é aceito como prova de isolamento sem o manifest correspondente do Context Firewall.

## 9. Riscos e trade-offs

- **Risco de burocracia**: etapas demais podem travar autoria. Mitigação: começar manual-first e aplicar somente em iniciativas grandes ou novos canônicos.
- **Falsa confiança em agentes**: Blind Solver e mesa simulada podem parecer validação suficiente. Mitigação: playtest humano permanece soberano.
- **Cegueira incompleta**: prompts não bastam para isolar contexto. Mitigação: Context Firewall com cópia seletiva, sanitização não destrutiva, hashes, manifest e relatório de violações.
- **Correlação entre agentes**: vários agentes usando o mesmo modelo, provider, prompt-base, ordem de documentos e parâmetros semelhantes podem compartilhar vieses e criar falsa impressão de independência. Concordância de quatro entre cinco agentes não deve ser interpretada como amostra estatística equivalente a cinco humanos. Mitigações futuras: preservar análises individuais antes da conversa, variar perfis de atenção, variar ordem de leitura, variar seed e temperatura quando disponíveis, executar mesas compostas apenas por generalistas, executar mesas mistas, comparar providers futuramente, medir diversidade de hipóteses em vez de apenas quantidade de votos e continuar usando playtest humano como evidência final. Diversidade de personas não deve ser apresentada como independência cognitiva real.
- **Generalização indevida**: um playtest isolado pode gerar regra ruim. Mitigação: estados de finding e decisão explícita de escopo/generalização.
- **Homogeneização criativa**: métricas podem empurrar todos os casos para o mesmo molde. Mitigação: fingerprint gera warning, não bloqueio automático, e cada caso pode declarar experimento criativo.
- **Custo operacional futuro**: múltiplos agentes podem encarecer a produção. Mitigação: medir horas, tokens, revisões e taxa de bloqueio antes de automatizar providers.

## 10. Validação

Validação documental desta PRD:

- `git diff --check` deve passar;
- links e caminhos mencionados devem ser revisados manualmente;
- nenhum código, schema, blueprint ou caso deve ser modificado;
- `pytest tests/ -q` deve ser executado se o ambiente estiver preparado;
- build de PDF não deve ser usado como validação desta tarefa.

Validação futura da capacidade:

- executar pilotos manuais em caso experimental ou etapa de planejamento aprovada;
- comparar Blind Solver, mesa simulada e playtest humano;
- medir se findings retornam à etapa correta;
- verificar se uma correção foi revalidada antes de virar regra;
- auditar pelo manifest se cada agente recebeu somente o bundle permitido;
- comparar revisões lógicas e renderizadas para detectar falhas introduzidas pelo pacote final.

## 11. Sugestão de decomposição

Próxima skill recomendada: `to-issues`.

PRs pequenas e independentes sugeridas:

1. **Documentação de governança**: etapas, papéis, gates, visibilidades e separação entre skill, papel e orquestrador.
2. **Schemas de playtest e learning ledger**: estruturas conceituais para sessão, observação, finding, decisão e revalidação.
3. **Context Firewall e blind bundle**: política de visibilidade, manifest, hashes, normalização de nomes e teste de isolamento manual.
4. **Blind Solver manual**: protocolo por envelope, saída estruturada e output congelado para avaliação posterior.
5. **Revisões estruturadas e gates**: Gate Evaluator, templates manuais de revisão por etapa, decisão PASS/REVISE/BLOCK/INCONCLUSIVE e rollback obrigatório.
6. **Mesa Simulada manual**: fase individual, conversa estruturada, moderador cego, crítico adversarial e relatório.
7. **Workspace/orquestrador manual**: preparação de etapas, ingestão de saídas, status, rollback e lineage, sem providers automáticos.
8. **Fingerprint**: modelo de diversidade criativa e warnings de repetição não bloqueantes.
9. **Dificuldade**: calibração por grafo de inferências, blind solves, mesa simulada, suporte e playtest humano.
10. **Providers automáticos**: somente após validação do fluxo manual, com benchmark, custo, privacidade e auditoria.

### Rollout incremental proposto

#### Fase 0 — Prioridade atual

- baseline real;
- revisão visual;
- novo playtest do Hotel Aurora.

#### Fase 1 — Governança

- documentos;
- políticas de visibilidade;
- schemas conceituais;
- critérios dos gates.

#### Fase 2 — Learning Loop

- sessão;
- finding;
- decisão;
- rastreabilidade.

#### Fase 3 — Blind Bundle manual

- Context Firewall;
- manifest;
- Blind Solver manual;
- testes de isolamento.

#### Fase 4 — Mesa simulada manual

- análises individuais;
- conversa estruturada;
- crítico adversarial;
- relatório.

#### Fase 5 — Workspace e orquestrador manual

- preparação de etapas;
- ingestão;
- status;
- rollback;
- lineage.

#### Fase 6 — Diversidade e dificuldade

- fingerprint;
- warnings;
- calibração por dados.

#### Fase 7 — Providers automáticos

Somente após validação do fluxo manual.

#### Fase 8 — Inteligência editorial

Somente após vários casos e playtests.

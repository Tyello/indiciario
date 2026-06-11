# Contratos conceituais de artefato e run multiagente

## 1. Propósito

Este documento define contratos conceituais para permitir que futuras implementações do pipeline multiagente do Indiciário respondam, de forma rastreável e preservando o pipeline atual:

- o que foi produzido;
- por quem;
- em qual etapa;
- com quais entradas;
- com qual contexto;
- a partir de quais versões;
- que transformação ocorreu;
- que finding motivou a mudança;
- qual gate foi decidido;
- qual output foi usado;
- qual execução continua válida;
- qual artefato deriva de outro.

O objetivo é estabelecer vocabulário estável antes da criação futura de schemas YAML ou JSON, manifests, CLIs, blind bundles, Context Firewall, Learning Loop, Blind Solver, Gate Evaluator e orquestrador manual.

Este documento **não é schema**. Os exemplos são ilustrativos. Nenhuma estrutura descrita aqui é validada automaticamente. Contratos formais serão implementados em issues posteriores. O pipeline atual do Indiciário permanece preservado e compatível sem implementar estes contratos agora.

## 2. Convenções normativas

Este documento usa os termos:

- **DEVE**: requisito conceitual obrigatório para futuras implementações compatíveis.
- **NÃO DEVE**: comportamento proibido em futuras implementações compatíveis.
- **PODE**: possibilidade opcional, aplicável quando útil ao contexto.
- **RECOMENDA-SE**: orientação adaptável, que pode ser ajustada por justificativa explícita.

Nenhuma regra desta PR cria validação automática, enum executável, schema, CLI ou obrigação de armazenamento.

## 3. Princípios dos contratos

### Rastreabilidade

Toda saída relevante DEVE poder ser relacionada à execução que a produziu, aos inputs usados e à etapa do pipeline em que surgiu.

### Imutabilidade histórica

Artefatos e outputs usados em revisão NÃO DEVEM ser alterados retroativamente. Se o conteúdo precisa mudar, uma nova versão deve ser criada.

### Versionamento explícito

Correção gera nova versão, não substituição silenciosa. A versão anterior continua existindo para auditoria, rollback e comparação.

### Lineage

Derivações DEVEM indicar sua origem. O histórico precisa explicar de qual artefato, versão, run ou finding um output deriva.

### Contexto mínimo

Uma run registra apenas o necessário para explicar sua execução, validar seu escopo e auditar seus outputs. Ela NÃO DEVE capturar contexto privado desnecessário.

### Separação entre identidade e localização

Um identificador conceitual NÃO DEVE depender obrigatoriamente do caminho do arquivo. Caminhos podem mudar sem mudar a identidade do artefato.

### Independência de provider

Contratos NÃO DEVEM depender de OpenAI, Anthropic, Ollama ou qualquer outro fornecedor. Provider e modelo podem ser metadados, nunca pré-condição conceitual.

### Independência de armazenamento

Contratos NÃO DEVEM exigir banco de dados. Uma implementação futura pode usar arquivos, manifests, banco, sistema híbrido ou outro armazenamento.

### Integridade não é confidencialidade

Hash pode demonstrar igualdade ou alteração de conteúdo, mas não impede vazamento, não protege segredo e não comprova que a interpretação semântica foi preservada.

### Compatibilidade incremental

O pipeline atual continua válido sem implementar estes contratos. A adoção futura DEVE ser incremental e preservar o fluxo Blueprint → Case Kernel → Case Review → Visual Library / templates → Build Package → Baseline visual real → Playtest → Ajustes finos.

## 4. Entidades conceituais

- **Artifact**: unidade de conteúdo ou evidência versionável. Pode ser um blueprint, documento de jogador, guia, relatório, bundle, output de solver ou evidência de validação.
- **Artifact Version**: estado específico e imutável de um Artifact. Identidade e versão são separadas: o mesmo Artifact pode ter muitas versões.
- **Run**: execução concreta de uma etapa por um Actor assumindo uma Role, com entradas, contexto permitido, outputs e estado operacional.
- **Stage**: etapa do pipeline, como Brief, Case Kernel, Case Review, Blind Solver, Gate Evaluation, Build Package ou Playtest.
- **Role**: responsabilidade assumida pelo Actor naquela run, como author, reviewer, blind_solver ou gate_evaluator.
- **Actor**: pessoa, LLM, script, ferramenta ou sistema que executou uma ação.
- **Input Reference**: referência a uma versão exata, bundle, instrução ou evidência usada como entrada.
- **Output Reference**: referência a uma versão exata ou output congelado produzido por uma run.
- **Bundle**: conjunto de entradas disponibilizado para uma run, especialmente relevante para blind runs.
- **Finding**: observação de problema, risco, lacuna, contradição ou melhoria identificada em revisão, solver, gate, playtest ou validação.
- **Gate Decision**: resultado de avaliação formal de avanço, com estados PASS, REVISE, BLOCK ou INCONCLUSIVE.
- **Incident**: evento de segurança, contaminação, vazamento, sanitização excessiva/insuficiente ou invalidade operacional.
- **Transformation**: mudança aplicada entre versões, como sanitização, renderização, correção editorial, merge ou split.
- **Lineage Edge**: relação de derivação entre artefatos, versões, runs, findings ou outputs.
- **Human Decision**: decisão tomada por operador, autor, avaliador ou responsável humano quando o processo exige julgamento não automatizado.
- **Validation Evidence**: evidência usada para sustentar que uma correção, gate, finding resolvido ou output é aceitável para seu propósito.

As diferenças centrais são: Artifact é a identidade versionável; Artifact Version é o conteúdo imutável; Run é a execução; Actor é quem executa; Role é a responsabilidade; Gate Decision é a decisão de avanço; Finding é a observação; Incident é o evento de invalidação ou segurança; Transformation descreve mudança; Lineage Edge conecta origens e derivações.

## 5. Identificadores conceituais

Identificadores conceituais representam entidades sem definir formato final. Futuras implementações podem usar identificadores humanos, sequenciais, gerados ou híbridos.

Identificadores previstos:

- `artifact_id`: identidade estável de um Artifact.
- `artifact_version_id`: identidade de uma versão específica e imutável.
- `run_id`: identidade de uma execução concreta.
- `bundle_id`: identidade de um conjunto de entradas preparado.
- `finding_id`: identidade de uma observação rastreável.
- `gate_decision_id`: identidade de uma decisão de gate.
- `incident_id`: identidade de um incidente.
- `transformation_id`: identidade de uma transformação registrada.
- `actor_id`: identidade opcional de um executor real.
- `case_id`: identidade conceitual do caso.
- `stage_id`: identidade conceitual da etapa.

Regras:

- Identificadores DEVEM ser estáveis.
- Identificadores NÃO DEVEM carregar solução, culpado, classificação privada ou metadado revelador.
- Identificadores NÃO DEVEM depender somente de nome de arquivo.
- Identificadores NÃO DEVEM ser reutilizados para entidades diferentes.
- Uma nova versão mantém `artifact_id` e recebe novo `artifact_version_id`.
- Uma nova run recebe novo `run_id`.
- Repetir a mesma tarefa não reutiliza `run_id`.
- Identificadores podem ser humanos ou gerados futuramente.
- O formato final pertence a schemas e implementação futura.

Exemplos neutros, ilustrativos e não obrigatórios:

```text
ART-0001
ARTV-0001-02
RUN-0042
BND-0018
FND-0031
GATE-0024
INC-0007
```

## 6. Contrato conceitual de Artifact

Campos conceituais mínimos:

- `artifact_id`: identidade estável da unidade versionável.
- `artifact_version_id`: versão específica referenciada quando o registro aponta para conteúdo concreto.
- `case_id`: caso ao qual o artefato pertence.
- `artifact_type`: tipo conceitual, como blueprint, player_document, facilitator_guide, review_report, solver_output ou rendered_pdf.
- `title` ou `label` neutro: nome legível sem solução ou classificação privada.
- `stage`: etapa em que o artefato foi criado, usado ou congelado.
- `visibility`: categoria de acesso pretendida.
- `contains_solution`: indicação conceitual de presença de solução, gabarito ou expectativa privada.
- `created_by`: Actor ou run responsável pela criação.
- `created_at`: momento de criação, com timezone claro em implementação futura.
- `source_path` opcional: localização conhecida, sem virar identidade.
- `content_hash` opcional: hash de conteúdo, quando definido futuramente.
- `derived_from`: versões ou artefatos de origem.
- `supersedes`: versões substituídas por esta versão, sem apagar histórico.
- `status`: estado do artefato.
- `notes` opcionais: observações neutras e não executáveis.

Visibilidades alinhadas ao protocolo de cegueira:

- `PUBLIC_PLAYER`: visível ao jogador ou Blind Solver no momento correto.
- `PRIVATE_AUTHOR`: reservado a autoria, verdade real, solução ou decisões privadas.
- `REVIEW_PRIVATE`: disponível a revisão autorizada, mas não a agente cego.
- `FACILITATOR`: destinado ao facilitador, dicas ou condução.
- `FUTURE_STAGE`: material de etapa futura, não liberado para uma run atual.
- `DERIVED_REPORT`: relatório derivado, síntese, QA ou análise.
- `PLAYTEST_ANONYMIZED`: dado de playtest minimizado ou anonimizado.

Status conceituais de artefato:

- `DRAFT`: em elaboração.
- `FROZEN`: preservado para revisão, comparação, gate ou auditoria.
- `SUPERSEDED`: substituído por versão posterior, sem apagar histórico.
- `WITHDRAWN`: removido do fluxo por decisão humana.
- `INVALIDATED`: não confiável para o uso pretendido.
- `PUBLISHED` opcional: publicado ou liberado para uso final.
- `ARCHIVED` opcional: preservado fora do fluxo ativo.

`FROZEN` significa preservado para revisão. `SUPERSEDED` significa substituído por versão posterior, sem apagar histórico. `INVALIDATED` significa não confiável para o uso pretendido. `WITHDRAWN` significa removido do fluxo por decisão humana. Status de artefato NÃO DEVE ser confundido com gate.

## 7. Contrato conceitual de Artifact Version

Uma versão representa conteúdo específico. Conteúdo alterado gera nova versão. Alteração apenas de localização não deve obrigatoriamente gerar nova versão. Alteração de conteúdo visível sempre gera nova versão. Sanitização técnica pode gerar versão derivada. Transformação editorial sempre deve ser registrada. O original deve ser preservado. Versões usadas por runs anteriores não podem ser substituídas retroativamente.

Exemplo conceitual não executável; isto não é schema:

```text
artifact_version:
  artifact_id: ART-0001
  artifact_version_id: ARTV-0001-02
  version: 2
  status: FROZEN
  visibility: PUBLIC_PLAYER
  contains_solution: false
  derived_from:
    - ARTV-0001-01
  transformation:
    type: technical_sanitization
    description: "Remoção de metadado técnico não diegético"
  content_hash: "conceitual"
```

## 8. Contrato conceitual de Run

Campos conceituais mínimos:

- `run_id`: identidade da execução concreta.
- `case_id`: caso ao qual a run pertence.
- `stage`: etapa executada.
- `role`: responsabilidade assumida na run.
- `actor`: executor real.
- `blindness_mode`: modo de cegueira operacional.
- `started_at`: início.
- `finished_at`: fim, quando houver.
- `status`: estado operacional da run.
- `input_bundle`: bundle usado, quando aplicável.
- `input_artifact_versions`: versões de artefato usadas como entrada.
- `output_artifact_versions`: versões produzidas ou congeladas.
- `instructions_version` opcional: versão das instruções ou prompt.
- `workflow_version` opcional: versão do processo.
- `provider` opcional: fornecedor técnico, quando houver.
- `model` opcional: modelo técnico, quando houver.
- `parameters` opcionais: parâmetros conhecidos e relevantes.
- `tools_allowed`: ferramentas autorizadas.
- `tools_used`: ferramentas efetivamente usadas.
- `incidents`: incidentes relacionados.
- `gate_decision`: gate associado ou posterior.
- `human_operator`: operador humano responsável, quando houver.
- `notes`: observações.

Modos de cegueira:

- `BLIND`: acesso restrito ao que o papel pode ver.
- `NON_BLIND`: acesso não cego, incluindo informações privadas quando autorizado.
- `HYBRID`: run com partes cegas e não cegas explicitamente separadas.
- `CONTAMINATED`: run com cegueira comprometida.

Status da run, separado do gate:

- `PREPARED`: preparada, ainda não iniciada.
- `RUNNING`: em execução.
- `COMPLETED`: finalizou e produziu output ou conclusão operacional.
- `FAILED`: falhou operacionalmente.
- `CANCELLED`: interrompida antes de conclusão.
- `INVALIDATED`: output não pode ser usado para a finalidade declarada.

`COMPLETED` não significa `PASS`. `FAILED` não significa necessariamente `BLOCK` editorial. `INVALIDATED` significa que o output não pode ser usado para a finalidade declarada. Gate é decisão posterior ou associada. Uma run pode completar e receber `INCONCLUSIVE`. Uma run contaminada deve ser `INVALIDATED` para evidência cega.

## 9. Contrato conceitual de Bundle

Campos conceituais:

- `bundle_id`: identidade do conjunto de entradas.
- `case_id`: caso relacionado.
- `stage`: etapa alvo.
- `target_role`: papel que receberá o bundle.
- `blindness_mode`: cegueira esperada.
- `allowed_artifact_versions`: versões autorizadas.
- `excluded_categories`: categorias excluídas, como solução, guia ou envelopes futuros.
- `instructions_reference`: referência a instruções permitidas.
- `expected_output_reference`: referência ao tipo de output esperado, sem gabarito privado em bundle cego.
- `tools_allowed`: ferramentas autorizadas.
- `transformations_applied`: sanitizações, conversões ou renderizações realizadas antes da run.
- `created_by`: Actor ou run que preparou o bundle.
- `created_at`: momento de criação.
- `bundle_hash` opcional: hash de composição, quando definido futuramente.
- `audit_status`: estado de revisão do bundle.

Um bundle referencia versões, não apenas nomes. Um bundle NÃO DEVE esconder transformação aplicada. Bundle para agente cego NÃO DEVE conter expectativa privada. Bundle deve ser congelado antes da run. Qualquer mudança gera novo `bundle_id` ou nova versão conceitual. A estrutura formal pertence a issues posteriores.

## 10. Contrato conceitual de Transformation

Categorias conceituais:

- `TECHNICAL_SANITIZATION`;
- `FILE_RENAMING`;
- `METADATA_REMOVAL`;
- `FORMAT_CONVERSION`;
- `RENDERING`;
- `EDITORIAL_CHANGE`;
- `CONTENT_CORRECTION`;
- `EXTRACTION`;
- `MERGE`;
- `SPLIT`;
- `ANONYMIZATION`.

Toda transformação deve registrar conceitualmente:

- `transformation_id`;
- input versions;
- output versions;
- `type`;
- `reason`;
- `performed_by`;
- `timestamp`;
- `visible_content_changed`;
- `diff_reference` opcional;
- `review_required`;
- `invalidates_previous_comparison`.

Regras:

- Transformação de conteúdo visível deve marcar `visible_content_changed` como verdadeiro.
- Sanitização técnica NÃO DEVE ser usada para esconder alteração editorial.
- `RENDERING` pode alterar percepção e exige Blind Review renderizado quando aplicável.
- Anonimização NÃO DEVE destruir evidência necessária.

## 11. Contrato conceitual de Lineage

Relações possíveis:

- `DERIVED_FROM`;
- `SUPERSEDES`;
- `GENERATED_FROM`;
- `SANITIZED_FROM`;
- `RENDERED_FROM`;
- `MERGED_FROM`;
- `SPLIT_FROM`;
- `CORRECTS`;
- `RESPONDS_TO_FINDING`;
- `USED_AS_INPUT`;
- `PRODUCED_BY_RUN`.

Lineage é grafo, não necessariamente cadeia linear. Um artefato pode derivar de vários. Um output pode responder a vários findings. Lineage não substitui versionamento. Lineage NÃO DEVE ser reconstruído apenas pelo nome do arquivo. Histórico nunca deve ser apagado por conveniência.

Exemplo conceitual, sem formato executável:

```text
ARTV-E1-04-V2
  SANITIZED_FROM → ARTV-E1-04-V1
  PRODUCED_BY_RUN → RUN-0042
  RESPONDS_TO_FINDING → FND-0018
```

## 12. Contrato conceitual de Finding

Campos conceituais alinhados ao protocolo operacional:

- `finding_id`: identidade do finding.
- `case_id`: caso relacionado.
- `source_run`: run que originou a observação.
- `source_artifact_version`: versão observada.
- `stage`: etapa onde surgiu.
- `category`: categoria do problema, risco ou melhoria.
- `severity`: severidade independente do gate.
- `description`: descrição clara.
- `evidence`: evidências usadas.
- `status`: estado do finding.
- `assigned_to`: responsável por tratar ou decidir.
- `rollback_target`: ponto recomendado de retorno.
- `blocks_gate`: impacto no gate.
- `created_at`: criação.
- `resolved_by_artifact_version`: versão que resolve, quando aplicável.
- `validation_evidence`: evidência de revalidação.
- `related_findings`: findings relacionados.
- `decision_notes`: justificativas de decisão.

Estados conceituais obrigatórios:

- `ACCEPTED`;
- `REJECTED`;
- `DEFERRED`;
- `NOT_APPLICABLE`;
- `RESOLVED`.

O contrato separa status, severidade, impacto no gate e condição operacional. Finding nunca é apagado. `REJECTED` exige justificativa. `DEFERRED` exige risco residual. `RESOLVED` exige evidência. Alteração sem revalidação não resolve finding.

## 13. Contrato conceitual de Gate Decision

Campos conceituais:

- `gate_decision_id`: identidade da decisão.
- `case_id`: caso relacionado.
- `stage`: etapa avaliada.
- `related_run`: run avaliada ou principal.
- `evaluator`: Actor ou Role que avaliou.
- `decided_at`: momento da decisão.
- `state`: estado do gate.
- `reason`: razão resumida.
- `findings_considered`: findings considerados.
- `expected_conclusions` opcionais: expectativas privadas quando autorizadas.
- `observed_conclusions` opcionais: conclusões observadas no output.
- `rollback_target`: ponto de retorno.
- `residual_risk`: risco aceito ou pendente.
- `requires_new_run`: se exige nova execução.
- `evidence_references`: versões, outputs ou relatórios usados.

Estados:

- `PASS`;
- `REVISE`;
- `BLOCK`;
- `INCONCLUSIVE`.

Regras:

- `PASS` pode ter risco residual.
- `REVISE` exige correção e nova avaliação.
- `BLOCK` exige nova evidência ou execução antes de `PASS`.
- `INCONCLUSIVE` NÃO DEVE ser convertido administrativamente em `PASS`.
- Blind Solver NÃO DEVE decidir seu próprio gate.
- Gate aponta para versões exatas utilizadas.

## 14. Contrato conceitual de Incident

Campos alinhados ao protocolo de cegueira:

- `incident_id`: identidade do incidente.
- `case_id`: caso relacionado.
- `related_run`: run afetada.
- `related_bundle`: bundle afetado.
- `type`: tipo conceitual.
- `detected_at`: momento de detecção.
- `detected_by`: Actor, Role ou evidência que detectou.
- `description`: descrição.
- `exposed_information`: informação exposta ou potencialmente exposta.
- `impact`: impacto sobre cegueira, validade ou segurança.
- `run_validity`: validade da run.
- `gate_effect`: efeito sobre gate.
- `remediation`: ação de correção.
- `requires_rerun`: se exige nova run.
- `status`: estado do incidente.
- `evidence`: evidência do incidente.

Tipos conceituais:

- `LEAK_CONFIRMED`;
- `LEAK_SUSPECTED`;
- `OVER_SANITIZATION`;
- `UNDER_SANITIZATION`;
- `TOOL_ESCAPE`;
- `HISTORY_CONTAMINATION`.

Status conceitual do incidente:

- `OPEN`;
- `UNDER_REVIEW`;
- `CONFIRMED`;
- `DISMISSED`;
- `REMEDIATED`.

Esses nomes não criam enums executáveis.

## 15. Contrato conceitual de Actor e Role

Actor é o executor real. Pode ser:

- pessoa;
- LLM;
- script;
- ferramenta;
- sistema futuro.

Campos conceituais de Actor:

- `actor_id`: identidade opcional e minimizada.
- `actor_type`: humano, llm, script, tool, system ou similar futuro.
- `display_name` neutro: nome de exibição sem dado pessoal desnecessário.
- `provider` opcional: fornecedor técnico.
- `model` opcional: modelo, quando houver.
- `version` opcional: versão do executor.
- `human_supervisor` opcional: supervisor responsável.

Role é responsabilidade assumida em uma run. Roles conceituais:

- `author`;
- `reviewer`;
- `blind_solver`;
- `gate_evaluator`;
- `moderator`;
- `adversarial_critic`;
- `human_operator`;
- `renderer`;
- `validator`;
- `other`.

Regras:

- Actor não é Role.
- O mesmo Actor pode assumir Roles diferentes em runs diferentes.
- Acumulação de Roles conflitantes DEVE ser registrada.
- `actor_id` NÃO DEVE expor dado pessoal desnecessário.
- Playtests devem preferir anonimização.

## 16. Provider, model e parâmetros

Provider e model são opcionais. Runs manuais ou humanas podem não ter provider. Nomes de provider NÃO DEVEM determinar comportamento contratual. Parâmetros devem ser registrados quando conhecidos e relevantes. Ausência de parâmetro não invalida automaticamente a run. Runs com parâmetros diferentes NÃO DEVEM ser tratadas como equivalentes sem análise. Custo e tokenização pertencem a issues futuras.

Exemplos de parâmetros conceituais, sem formato obrigatório:

- `temperature`;
- `seed`;
- `max_tokens`;
- `reasoning_mode`;
- `tool_access`;
- `context_window`;
- `prompt_version`.

## 17. Hashes e integridade

- `content_hash` representa conteúdo.
- `bundle_hash` representa composição do bundle.
- `output_hash` representa output congelado.
- Hash não garante confidencialidade.
- Hash não detecta interpretação semântica.
- Hash muda quando conteúdo relevante muda, conforme normalização futura.
- O algoritmo final será definido futuramente.
- Não se deve registrar hash sem informar o que foi normalizado.
- Dois arquivos visualmente iguais podem ter hashes diferentes.
- Dois arquivos com mesmo texto podem gerar experiência diferente após renderização.

Tipos conceituais a diferenciar:

- hash de bytes;
- hash de conteúdo normalizado;
- hash de manifest;
- hash de bundle.

Nenhum algoritmo é escolhido nesta PR.

## 18. Timestamps e ordem temporal

Timestamps conceituais:

- `created_at`: criação de artefato, bundle, finding ou registro.
- `started_at`: início de run.
- `finished_at`: conclusão de run.
- `decided_at`: decisão de gate ou decisão humana.
- `invalidated_at`: momento em que a invalidade foi registrada.
- `superseded_at`: momento em que uma versão foi substituída.

Regras:

- Timestamps devem ser claros quanto a timezone.
- Ordem temporal NÃO DEVE ser inferida apenas por nome de arquivo.
- Uma run não pode terminar antes de começar.
- Gate não pode preceder output congelado.
- Versão derivada não pode preceder sua origem.
- Precisão final será definida nos schemas.

## 19. Versionamento

Diferentes versões não devem ser condensadas em um único campo porque respondem a perguntas distintas:

- versão do artefato: qual conteúdo específico foi usado ou produzido;
- versão da skill: qual procedimento operacional orientou um papel;
- versão das instruções: qual prompt, briefing ou orientação foi entregue;
- versão do workflow: qual processo estava vigente;
- versão do contrato: qual formato futuro foi usado;
- versão do caso: qual estado editorial do caso estava em jogo;
- commit do repositório: qual estado técnico do repo existia;
- versão do modelo: qual executor técnico foi utilizado quando conhecido.

Declarações:

- `case_version` pode apontar para commit ou versão editorial.
- `workflow_version` identifica processo.
- `instruction_version` identifica papel ou prompt.
- Artifact Version identifica conteúdo.
- Contract Version identifica formato futuro.
- Model Version identifica executor técnico quando conhecido.

## 20. Status e validade

| Entidade | Exemplos de estado |
|---|---|
| Artifact | `DRAFT`, `FROZEN`, `SUPERSEDED`, `INVALIDATED` |
| Run | `PREPARED`, `RUNNING`, `COMPLETED`, `FAILED`, `INVALIDATED` |
| Finding | `ACCEPTED`, `REJECTED`, `DEFERRED`, `NOT_APPLICABLE`, `RESOLVED` |
| Gate | `PASS`, `REVISE`, `BLOCK`, `INCONCLUSIVE` |
| Incident | `OPEN`, `UNDER_REVIEW`, `CONFIRMED`, `DISMISSED`, `REMEDIATED` |

Estado de uma entidade não substitui estado de outra. Run `COMPLETED` pode resultar em `BLOCK`. Artifact `FROZEN` pode estar ligado a run `INVALIDATED`. Finding `RESOLVED` não implica `PASS` automático. `PASS` não torna todos os artefatos publicados.

## 21. Imutabilidade e correções

- Output congelado não é editado.
- Correção gera nova versão.
- Registro errado pode ser corrigido por nova entrada ou retificação rastreável.
- Histórico não deve ser apagado.
- Hash não deve ser substituído retroativamente.
- Bundle não deve ser alterado após início da run.
- Run contaminada permanece registrada como contaminada.
- Findings rejeitados permanecem visíveis.
- Rollback não remove lineage.

## 22. Dados pessoais e minimização

Contratos NÃO DEVEM exigir nome real de jogador. Playtests devem usar identificadores neutros. E-mail, telefone, documento e outros dados pessoais não são necessários. Actor humano pode ser identificado por pseudônimo ou ID interno. Dados pessoais só entram quando houver justificativa. Anonimização não deve destruir rastreabilidade operacional. Detalhes legais e retenção ficam fora do escopo desta PR.

## 23. Exemplos conceituais integrados

Os exemplos abaixo são não executáveis e não são schemas.

### Exemplo 1 — Autor cria documento

```text
Run de autoria:
  run_id: RUN-0101
  case_id: CASE-MIRANTE-NOVO
  stage: document_authoring
  role: author
  actor: ACT-AUTOR-01
  status: COMPLETED
  input_artifact_versions:
    - ARTV-KERNEL-01
  output_artifact_versions:
    - ARTV-DOC-E1-01

Artefato inicial:
  artifact_id: ART-DOC-E1
  artifact_version_id: ARTV-DOC-E1-01
  artifact_type: player_document
  visibility: PUBLIC_PLAYER
  contains_solution: false
  status: FROZEN
  produced_by_run: RUN-0101
```

### Exemplo 2 — Blind Solver usa bundle

```text
Bundle cego:
  bundle_id: BND-0201
  target_role: blind_solver
  blindness_mode: BLIND
  allowed_artifact_versions:
    - ARTV-PERGUNTA-PUBLICA-01
    - ARTV-DOC-E1-01
    - ARTV-DOC-E1-02
  excluded_categories:
    - PRIVATE_AUTHOR
    - FACILITATOR
    - FUTURE_STAGE

Run blind:
  run_id: RUN-0202
  role: blind_solver
  actor: ACT-SOLVER-ANON-01
  blindness_mode: BLIND
  input_bundle: BND-0201
  status: COMPLETED
  output_artifact_versions:
    - ARTV-SOLVER-OUTPUT-01

Output congelado:
  artifact_version_id: ARTV-SOLVER-OUTPUT-01
  status: FROZEN
  output_hash: "conceitual"

Gate Evaluator separado:
  gate_decision_id: GATE-0203
  evaluator: ACT-EVAL-01
  related_run: RUN-0202
  state: INCONCLUSIVE
  evidence_references:
    - ARTV-SOLVER-OUTPUT-01
```

### Exemplo 3 — Finding gera correção

```text
Finding aceito:
  finding_id: FND-0301
  source_run: RUN-0202
  source_artifact_version: ARTV-DOC-E1-02
  status: ACCEPTED
  rollback_target: document_authoring
  blocks_gate: true

Nova versão:
  artifact_id: ART-DOC-E1
  artifact_version_id: ARTV-DOC-E1-03
  supersedes:
    - ARTV-DOC-E1-02
  transformation:
    type: CONTENT_CORRECTION
    reason: "Finding aceito indicou ambiguidade indevida"
    visible_content_changed: true

Lineage:
  ARTV-DOC-E1-03
    CORRECTS → ARTV-DOC-E1-02
    RESPONDS_TO_FINDING → FND-0301
    PRODUCED_BY_RUN → RUN-0302

Revalidação:
  finding_id: FND-0301
  status: RESOLVED
  resolved_by_artifact_version: ARTV-DOC-E1-03
  validation_evidence:
    - GATE-0304
```

## 24. Anti-regras

Este documento NÃO DEVE:

- exigir banco de dados;
- escolher UUID, ULID ou sequência definitiva;
- escolher algoritmo de hash;
- criar schema YAML ou JSON;
- definir classes Python;
- criar diretórios obrigatórios;
- confundir caminho com identidade;
- apagar versões antigas;
- permitir edição de output congelado;
- tratar hash como proteção de segredo;
- colocar solução dentro de IDs;
- tornar provider obrigatório;
- tornar modelo específico obrigatório;
- transformar contrato conceitual em implementação.

## 25. Relação com documentos anteriores

`MULTIAGENT_OPERATING_PROTOCOL` define operação, papéis, gates e rollback. `BLIND_CONTEXT_PROTOCOL` define acesso, cegueira, ameaças e incidentes. Este documento define identidade, versão, execução e lineage. O PRD define visão. O Implementation Plan define ordem. Futuros schemas devem respeitar os três protocolos: operação, cegueira e contratos de identidade/execução. Em conflito, segurança, cegueira e preservação histórica devem prevalecer.

## 26. Checklist de revisão

- [ ] Entidades separadas.
- [ ] Identificadores neutros.
- [ ] Versão separada de identidade.
- [ ] Run separada de gate.
- [ ] Actor separado de role.
- [ ] Status separados por entidade.
- [ ] Lineage preservado.
- [ ] Output congelado.
- [ ] Transformação registrada.
- [ ] Findings rastreáveis.
- [ ] Incidentes relacionados.
- [ ] Hashes sem promessa de confidencialidade.
- [ ] Dados pessoais minimizados.
- [ ] Exemplos não executáveis.
- [ ] Nenhum schema criado.

## 27. Limitações

Nesta PR:

- não há schema;
- não há validador;
- não há geração automática de IDs;
- não há hashing;
- não há manifest;
- não há storage;
- não há banco;
- não há CLI;
- não há orquestrador;
- não há migração de casos;
- não há integração com providers;
- nomes e campos podem evoluir antes da implementação;
- compatibilidade definitiva será decidida nas issues de schema.

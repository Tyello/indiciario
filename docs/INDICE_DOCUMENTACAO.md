# Índice de Documentação do Indiciário

Este documento é o **registro central de documentação** do projeto. Ele responde três perguntas para cada documento: **o que serve**, **quando é lido** (em qual workflow) e — coluna decisiva — **quando precisa ser atualizado**.

Ele tem duas funções operacionais:

1. Servir de mapa para qualquer pessoa ou agente entender onde mora cada assunto.
2. Alimentar o **pré-requisito de impacto documental** (ver abaixo): antes de começar uma tarefa, você consulta este índice para declarar quais docs a entrega vai exigir atualizar.

> Em conflito sobre **onde** um assunto deve ser documentado, este índice prevalece. Em conflito sobre **estado** do projeto, `docs/ESTADO_ATUAL.md` prevalece. Em conflito **editorial**, `docs/DIRETRIZES_EDITORIAIS.md` prevalece.

---

## Pré-requisito de impacto documental

**Regra (vale para qualquer atuação, não só issues):** nenhuma tarefa começa sem declarar o **conjunto de impacto documental** e nenhuma tarefa fecha sem resolvê-lo.

**No início da tarefa**, consultando este índice (coluna "Atualizar quando" e a tabela de gatilhos reversos), liste os documentos que a entrega provavelmente exigirá atualizar.

**No fim da tarefa**, para cada documento listado, confirme uma de duas coisas:

- ✅ atualizado nesta entrega; ou
- ⏭️ avaliado e não foi necessário (com uma linha de motivo).

Essa declaração é parte do **critério de tarefa concluída** em `AGENTS.md` e `CLAUDE.md`, e é um campo obrigatório do `.ai/ISSUE_TEMPLATE.md`.

### Gatilhos reversos (mudei isto → reveja aquilo)

Use esta tabela como atalho. Ela não é exaustiva; na dúvida, confira a coluna "Atualizar quando" do doc específico.

| Se a entrega mexeu em… | Reveja / atualize |
|---|---|
| Novo caso em `examples/` ou mudança de régua/dificuldade | `README.md` (roster), `AGENTS.md` (roster), `CLAUDE.md` (roster), `docs/ESTADO_ATUAL.md`, `docs/DIFFICULTY_FRAMEWORK.md`, e o plano em `docs/canonical_plans/` |
| Contagem de testes, fase do pipeline, limitação conhecida | `docs/ESTADO_ATUAL.md`, `CLAUDE.md` (tabela de fases + limitações) |
| Conclusão/abertura de issue, "próxima issue" | `CLAUDE.md` (ponteiro de próxima issue), `docs/ROADMAP.md` |
| Schema, validator, novos códigos de erro/aviso | `docs/GUIA_CODIGOS_ERROS.md`, `docs/ESTADO_ATUAL.md`, schema do template afetado |
| Regra editorial / anti-obviedade / diegese | `docs/DIRETRIZES_EDITORIAIS.md` (fonte), e refletir em `ANTI_OBVIEDADE`, `DIEGESE_DOCUMENTAL`, `CASE_FAILURE_PATTERNS` |
| Catálogo de tipos de documento / specs visuais | `framework/03_TIPOS_DE_DOCUMENTOS.md`, `framework/12_GUIA_DE_PRODUCAO.md`, `docs/VISUAL_SYSTEM.md` |
| Camada visual (tokens, plantas, assinaturas, printables) | `docs/VISUAL_SYSTEM.md`, `docs/VISUAL_LIBRARY_2_0.md`, `docs/FLOORPLANS.md`, `docs/SIGNATURES_AND_HANDWRITING.md`, `docs/PRINTABLES.md` |
| Skill nova/alterada | `.ai/skills/` (fonte), `.ai/skills/README.md`, `AGENTS.md` (mapa), `docs/AGENT_SKILLS.md`, e o espelho `docs/prompts/` |
| Ordem/numeração de arquivos do `framework/` | `framework/00_README.md` (tabela de ordem) |
| Run E2E do pipeline em um caso | doc `docs/*_PIPELINE_RUN.md` do caso, e `docs/QUALITY_COMPARATIVE_REPORT.md` se for comparativo |
| Workflow de agente (orchestrator/executor/reviewer) | `.ai/workflows/`, e `CLAUDE.md` se mudar auto-approve/obrigatoriedade de revisor |
| **Qualquer doc novo ou movido** | **este índice** (`docs/INDICE_DOCUMENTACAO.md`) |

> A última linha é a mais importante: **criar, mover ou aposentar um documento sempre obriga atualizar este índice.**

---

## Legenda

**Público:** `Dev` (engenharia) · `Agente` (Claude Code/Codex no repo) · `LLM-gen` (LLM gerando caso em chat) · `Designer` (humano desenhando caso) · `Facilitador` (mesa/playtest).

**Workflow (quando é lido):** `INIT` inicialização de agente · `GEN` geração de caso · `VAL` validação/build de código · `PLAY` playtest/mesa · `PIPE` pipeline multiagente · `GOV` governança/estado/roadmap.

---

## Raiz do repositório

| Arquivo | Propósito | Público | Workflow | Atualizar quando |
|---|---|---|---|---|
| `README.md` | Porta de entrada: visão, comandos, CI, prioridade, roster | Todos | GOV | Muda comando, CI, roster de casos ou prioridade |
| `AGENTS.md` | Protocolo obrigatório de agente + mapa de skills + critério de conclusão | Agente | INIT | Muda protocolo, skill, regra de conclusão ou roster |
| `CLAUDE.md` | Contexto de produto/estado/roadmap p/ Claude Code | Agente | INIT | Muda estado, fase do pipeline, próxima issue ou roster |
| `AUDITORIA_DE_CONFORMIDADE.md` | Auditoria pontual doc-vs-código (snapshot datado) | Dev | GOV | Não se edita; gera-se nova auditoria datada quando necessário |
| `docs/INDICE_DOCUMENTACAO.md` | **Este índice** | Todos | GOV/INIT | Sempre que um doc é criado, movido ou aposentado |

## `framework/` — kit de geração (chat com LLM)

> Ordem de leitura autoritativa: `framework/00_README.md`. O `framework/` cobre só a **geração**; validação/build ficam em `generator/` (ponte: `docs/CASE_GENERATION_WORKFLOW.md`).

| Arquivo                         | Propósito | Público | Workflow | Atualizar quando |
|---------------------------------|---|---|---|---|
| `00_README.md`                  | Índice, ordem de leitura, fluxo de geração | LLM-gen/Agente | GEN | Muda qualquer arquivo, numeração ou ordem do `framework/` |
| `01_PRINCIPIOS_DO_MODELO.md`    | As 8 leis do jogo justo | LLM-gen | GEN | Muda um princípio fundante |
| `02_ESTRUTURA_ENVELOPES.md`     | Arquitetura de envelopes e critério de avanço | LLM-gen | GEN | Muda modelo de envelopes/avanço |
| `03_TIPOS_DE_DOCUMENTOS.md`     | Catálogo dos 15 tipos de documento | LLM-gen | GEN | Adiciona/remove tipo de documento ou spec visual |
| `04_DESIGN_DE_PISTAS.md`        | Regras de pistas, códigos, cadeias, dificuldade | LLM-gen | GEN | Muda regra de pista/código/dificuldade |
| `05_CHECKLIST_SOLVABILIDADE.md` | Gate de qualidade pré-documentos | LLM-gen/Designer | GEN | Muda critério de solvabilidade ou rubrica de risco |
| `06_TEMPLATE_NOVO_CASO.md`      | Template de planejamento (14 seções) | Designer/LLM-gen | GEN | Muda o que um caso precisa planejar |
| `07_PROMPT_GERADOR_DE_CASO.md`  | Prompt expandido p/ gerar caso via LLM | LLM-gen | GEN | Muda entregáveis, formato ou gate da geração |
| `08_MODELO_REFERENCIA.md`       | Padrões e anti-padrões de referência | LLM-gen | GEN | Surge novo padrão/anti-padrão validado |
| `09_TEMPLATE_GABARITO.md`       | Template do gabarito do mestre | LLM-gen/Facilitador | GEN | Muda estrutura do gabarito |
| `10_TEMPLATE_DICAS.md`          | Template de dicas progressivas | LLM-gen/Facilitador | GEN | Muda intensidade/estrutura de dicas |
| `11_GUIA_DO_FACILITADOR.md`     | Como conduzir a sessão (operação de mesa) | Facilitador | PLAY | Muda condução de sessão |
| `12_GUIA_DE_PRODUCAO.md`        | Design visual, tipografia, impressão | Designer | GEN/VAL | Muda paleta, tipografia ou regra de impressão |
| `13_CONTRATO_EVIDENCIA.md`      | Contrato conclusão↔prova↔fase | LLM-gen/Dev | GEN/VAL | Muda contrato de evidência |
| `14_GRAFO_DE_PISTAS.md`         | Grafo lógico, `graph_report.json`, GP_001–007 | Dev/LLM-gen | VAL | Muda regra de grafo ou código GP_* |
| `15_CONTROLES_DA_LLM.md`        | Guard rails da LLM, `llm_feedback.json` | LLM-gen | GEN | Muda permissão/proibição de correção por LLM |
| `16_GUIA_DE_IMPRESSAO.md`       | Pacote de impressão, `print_manifest.json` | Designer/Dev | VAL | Muda regra de impressão/perfil/`print_manifest` |
| `17_GUIA_FACILITADOR.md`        | Produção do `guia_facilitador.pdf` + dicas contextuais | Facilitador | GEN/PLAY | Muda como se produz o guia do facilitador |
| `18_VISUAL_PROCEDURAL.md`       | Mapas/cartões SVG-HTML procedurais | Designer/Dev | GEN/VAL | Muda regra de visual procedural |
| `19_PLAYTEST_E_METRICAS.md`     | Métricas heurísticas de playtest | Dev/Designer | PLAY | Muda métrica/faixa heurística |
| `CONTEUDO_SCHEMA.md`            | Schema de conteúdo do blueprint | Dev/LLM-gen | GEN/VAL | Muda contrato de conteúdo do blueprint |

## `docs/` — núcleo de processo, editorial e governança

| Arquivo | Propósito | Público | Workflow | Atualizar quando |
|---|---|---|---|---|
| `ESTADO_ATUAL.md` | **Fonte de verdade do estado**; prevalece em conflito de estado | Todos | GOV | Muda estado, testes, roster ou limitação real |
| `ROADMAP.md` | Direção e ordem recomendada | Dev/Agente | GOV | Muda prioridade ou ordem de trabalho |
| `LLM_CONTEXT.md` | Contexto operacional mínimo (leitura obrigatória de agente) | Agente | INIT | Muda princípio, fluxo ou prioridade central |
| `LLM_OPERATING_MANUAL.md` | Como a LLM cria/revisa/corrige casos | LLM-gen | GEN | Muda regra de operação da LLM |
| `DIRETRIZES_EDITORIAIS.md` | **Fonte editorial**; prevalece em conflito editorial | LLM-gen/Designer | GEN | Muda decisão editorial |
| `ANTI_OBVIEDADE.md` | Regras anti-spoiler (+ `obviousness_checker.py`) | LLM-gen/Dev | GEN/VAL | Muda regra de obviedade ou código OBV_* |
| `DIEGESE_DOCUMENTAL.md` | Documentos parecem naturais no mundo | LLM-gen/Designer | GEN | Muda regra de diegese |
| `CASE_FAILURE_PATTERNS.md` | Falhas editoriais já observadas | LLM-gen/Designer | GEN | Surge novo padrão de falha de playtest |
| `DIFFICULTY_FRAMEWORK.md` | Régua de dificuldade por nível | Designer/LLM-gen | GEN | Muda faixa de dificuldade ou entra caso novo |
| `CANONICAL_CRITERIA.md` | Critérios do Canonical Quality Gate (`canonical_quality_gate.py`) | Dev/Agente | VAL | Muda critério canônico ou a implementação |
| `CASE_DESIGN_PIPELINE.md` | Processo editorial pré-blueprint | Designer | GEN | Muda processo de design de caso |
| `BLUEPRINT_AUTHORING_GUIDE.md` | Contrato mínimo de autoria de blueprint | LLM-gen/Designer | GEN | Muda contrato de autoria ou campo schema-enforced |
| `CASE_KERNEL.md` | DNA investigativo (`case_kernel.py`) | Dev | VAL | Muda comportamento do Case Kernel |
| `CASE_REVIEW.md` | Relatório editorial automático (`case_review.py`) | Dev | VAL | Muda comportamento do Case Review |
| `CASE_GENERATION_WORKFLOW.md` | **Ponte `framework/` ↔ `generator/`** | Agente/LLM-gen | GEN/VAL | Muda a fronteira geração↔validação |
| `GUIA_CODIGOS_ERROS.md` | Códigos OBV/PT/GP/ER + módulos | Dev | VAL | Adiciona/altera código de erro ou aviso |
| `VISUAL_SYSTEM.md` | Tokens/classes visuais v1 | Designer/Dev | VAL | Muda token, classe ou padrão visual |
| `VISUAL_LIBRARY_2_0.md` | Assets visuais estruturados (`floor_plan_library.py`) | Designer/Dev | VAL | Muda biblioteca visual |
| `FLOORPLANS.md` | Padrão P2 de plantas baixas | Designer/Dev | VAL | Muda regra de planta baixa ou código MAP_* |
| `SIGNATURES_AND_HANDWRITING.md` | Camada P3 de assinaturas/manuscritos | Designer/Dev | VAL | Muda regra de assinatura/rubrica/manuscrito |
| `PRINTABLES.md` | Cartões de mesa apartados | Designer/Facilitador | VAL/PLAY | Muda regra de printable |
| `AGENT_SKILLS.md` | Playbook de skills + roadmap de skills futuras | Agente | INIT | Muda skill existente ou planejada |
| `ARTIFACT_VISIBILITY_POLICY.md` | Política determinística de visibilidade | Dev | PIPE | Muda regra de visibilidade de artefato |

## `docs/` — pipeline multiagente

> Vários destes foram escritos como **visão/requisito** e hoje têm parte implementada (fases A–H concluídas). Cada um deve trazer no topo um carimbo de status (✅ implementado / 🔮 visão) — pendência registrada como dívida.

| Arquivo | Propósito | Público | Workflow | Atualizar quando |
|---|---|---|---|---|
| `PRD_MULTIAGENT_CASE_CREATION.md` | Visão da capacidade multiagente | Dev | GOV/PIPE | Muda a visão do pipeline |
| `IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` | PRD → sequência de issues; prevalece p/ roadmap multiagente | Dev/Agente | GOV/PIPE | Muda plano/ordem de implementação |
| `MULTIAGENT_OPERATING_PROTOCOL.md` | Protocolo manual-first | Dev | PIPE | Muda protocolo manual-first |
| `MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md` | Contratos conceituais de artefato/run | Dev | PIPE | Muda contrato conceitual de run |
| `BLIND_CONTEXT_PROTOCOL.md` | Requisitos de cegueira de contexto | Dev | PIPE | Muda requisito de cegueira |
| `BLIND_SOLVER_HARNESS.md` | Harness do blind solver (ISSUE-16) | Dev | PIPE | Muda comportamento do harness |
| `AURORA_PIPELINE_RUN.md` | Registro da run E2E do Aurora (ISSUE-28) | Dev | PIPE | Nova run do Aurora ou mudança no runner relevante |
| `FINTECH_PIPELINE_RUN.md` | Registro da run E2E do Fintech (ISSUE-29) | Dev | PIPE | Nova run do Fintech |
| `QUALITY_COMPARATIVE_REPORT.md` | Comparativo Aurora vs Fintech (ISSUE-30) | Dev | PIPE | Novo comparativo entre casos |

## `docs/` — subpastas

| Caminho | Propósito | Público | Atualizar quando |
|---|---|---|---|
| `docs/baselines/` | Baselines operacional/visual por caso | Dev/Designer | Gera-se baseline novo de um caso (falta II e Fintech) |
| `docs/canonical_plans/` | Planos editoriais por caso | Designer/LLM-gen | Cria/revisa o plano de um caso |
| `docs/playtests/` | Registros de playtest (entrada do Learning Loop) | Designer/Facilitador | Roda novo playtest |
| `docs/prompts/` | **Espelho** copy-paste das skills de `.ai/skills/` | Agente | Muda uma skill em `.ai/skills/` (manter em sincronia) |

## `.ai/` — automação de agentes

| Caminho | Propósito | Público | Atualizar quando |
|---|---|---|---|
| `.ai/skills/` | **Fonte de verdade das skills** carregáveis por agente | Agente | Cria/altera skill |
| `.ai/workflows/` | orchestrator / executor / reviewer | Agente | Muda loop de orquestração/execução/revisão |
| `.ai/issues/` | Specs + steps por issue | Dev/Agente | Cria/atualiza issue (ver `.ai/ISSUE_TEMPLATE.md`) |
| `.ai/ISSUE_TEMPLATE.md` | Framework de criação de issues (inclui impacto documental) | Dev/Agente | Muda o padrão de como issues são especificadas |
| `.ai/runs/` | Logs STEP-NN de execução/revisão | Agente | Trilha de auditoria; transiente, não exige curadoria |

---

## Workflows e ordem de leitura

**Inicialização de agente (toda tarefa):** `AGENTS.md` → `docs/LLM_CONTEXT.md` → `.ai/skills/README.md` → skill selecionada. `CLAUDE.md` é lido automaticamente pelo Claude Code. *Declare aqui o impacto documental antes de executar.*

**Geração de caso (chat com LLM):** `framework/00` → `01`–`05` → preencher `06` → gate `05` → `07` → documentos com `03`+`12` → gabarito `09` → dicas `10` → facilitador `11`/`16` → visual `17`. Lido junto: `docs/CASE_DESIGN_PIPELINE`, `DIFFICULTY_FRAMEWORK`, `BLUEPRINT_AUTHORING_GUIDE`, `ANTI_OBVIEDADE`, `CANONICAL_CRITERIA`. Ponte para o código: `docs/CASE_GENERATION_WORKFLOW`.

**Validação / build:** `generator/validator.py` → `case_kernel` → `case_review` → `package_builder` → relatórios. Referência: `GUIA_CODIGOS_ERROS`, `14_GRAFO_DE_PISTAS`, `15_CONTROLES_DA_LLM`, `ARTIFACT_VISIBILITY_POLICY`.

**Playtest / mesa:** `framework/11`, `framework/16`, `framework/18`, `docs/playtests/`, `PRINTABLES`. Saída alimenta o Learning Loop (`examples/learning/`), não vira patch direto no blueprint.

**Governança / merge:** `ESTADO_ATUAL`, `ROADMAP`, `.ai/workflows/reviewer.md`, skill `handoff`, `.ai/issues/`.

# Estado atual do Indiciário

Este documento registra a situação atual do projeto após os playtests reais, consolidação das réguas canônicas, hardening editorial/técnico/visual até P3 e entrega inicial do fluxo operacional Indiciário 2.0.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Visão do produto

Indiciário é um framework e futuro produto para geração de mistérios investigativos jogáveis em grupo, em formato de dossiê, envelopes, documentos e materiais de apoio.

Referências de experiência:

- jogos investigativos físicos;
- dossiês investigativos;
- board games de dedução;
- escape rooms como referência de ritmo;
- experiências como “Sob Investigação” e “Uma Noite Sem Flores”.

Princípios atuais:

- offline first;
- sem QR code;
- sem internet obrigatória;
- sem aplicativos externos;
- sem links externos como parte da solução;
- jogável em mesa, notebook, tablet ou impressão;
- foco em dedução, investigação e experiência de grupo.

Slogan atual:

> Todo caso deixa sinais.

## Estado técnico

O framework está tecnicamente funcional.

Funcionalidades já existentes no repositório incluem:

- schemas YAML por template;
- `required_when`;
- bloqueio de placeholders residuais;
- QA Report;
- Graph Report;
- Case Kernel (`generator/case_kernel.py`) para extrair o DNA investigativo do blueprint;
- Case Review Report (`generator/case_review.py` e `scripts/case_review.py`) para revisar o núcleo antes do pacote;
- contratos de evidência;
- grafo de pistas;
- feedback para LLM;
- guia do facilitador;
- dicas contextuais;
- guia de impressão;
- visual procedural;
- métricas de playtest;
- guardrail anti-obviedade integrado ao validator;
- progressão por envelope schema-enforced;
- package builder;
- manifest;
- print manifest;
- Playwright como renderizador oficial;
- merge PDF com `pikepdf`;
- sistema visual documental P0 com tokens CSS globais, cabeçalho/rodapé documental, classes por tipo e família, tabelas P&B first e carimbos burocráticos opcionais;
- printables apartados P1 para cartões recortáveis de personagem, local e objeto, registrados no manifest e no guia de impressão como apoio de mesa;
- plantas baixas P2 com renderer dedicado, A4 paisagem, P&B first, portas, janelas, câmeras e validações `MAP_*`;
- suporte P3 a assinatura, rubrica e manuscrito curto por perfil de personagem no blueprint;
- possibilidade de override SVG para assinatura/rubrica;
- Visual Library 2.0 mínima (`generator/floor_plan_library.py`) com plantas-base estruturadas genéricas, ainda sem integração automática aos canônicos;
- pipeline multiagente offline: Gate Evaluator (`generator/gate_evaluator.py`, `schemas/gate_evaluation.schema.yaml`), Narrative Reviewer (`generator/narrative_reviewer.py`), Evidence Reviewer (`generator/evidence_reviewer.py`), Visual Reviewer (`generator/visual_reviewer.py`), Accessibility Reviewer (`generator/accessibility_reviewer.py`), Multiagent Workspace (`generator/workspace.py`), Manual Orchestrator (`generator/manual_orchestrator.py`), Run Manifest (`generator/run_manifest.py`), Pipeline Runner (`generator/pipeline_runner.py`), Quality Comparative Reviewer (`generator/quality_comparative_reviewer.py`).

Suite de testes: `pytest tests/ -q` reporta cerca de 1464 testes (checar contagem exata antes de citar em PR, ela cresce a cada issue).

Fase Provider (ISSUE-31–34, LLM real): ISSUE-31, ISSUE-32, ISSUE-33, ISSUE-33.1 e ISSUE-33.2 concluídas. ISSUE-33.2 concluída — `generator/solvability_meter.py` implementa `measure_solvability`, que roda N execuções solver→juiz sobre o mesmo bundle e agrega num `SolvabilityReport` com taxa de resolução e `difficulty_estimate` (proxy LLM; playtest humano continua sendo o veredito real). ISSUE-31 concluída — `generator/llm_provider.py` define o contrato neutro de provider (`Protocol` `LLMProvider`, dataclasses `ProviderRequest`/`ProviderResponse`, hierarquia de erro, `validate_provider_request`). ISSUE-32 concluída — `generator/fake_provider.py` implementa `FakeProvider` (satisfaz `LLMProvider` estruturalmente, sem herança), devolvendo respostas roteirizadas (`ScriptedResponse`) ou erros injetados (`ProviderError`) em ordem determinística, sem rede; garante CI determinística. ISSUE-33 concluída — `generator/llm_blind_solver.py` implementa classe `LLMBlindSolver` (satisfaz `Protocol BlindSolver`), conectando modelo real ao harness via `LLMProvider` (injeção externa), mantendo blind bundle como única entrada; contrato LS_001–LS_005, regra de isolamento (solver nunca com acesso ao repo); integração opt-in em `generator/pipeline_runner.py` via parâmetro `solver` (default `None` preserva `DeterministicPipelineSolver` para backward compatibility); testes determinísticos via `FakeProvider` em CI. ISSUE-33.1 concluída — `generator/conclusion_judge.py` implementa função `judge_conclusions` que recebe `BlindSolverReport` + conclusões esperadas + `LLMProvider`, retorna `JudgeVerdict` com classificação (resolvido/nao_resolvido/vazamento/ambiguo) e alimenta campo `met` do Gate Evaluator; contrato CJ_001–CJ_005 com loop de reparo JSON e classificação derivada em Python puro; testado com `FakeProvider`.

Limitações reais do pipeline multiagente, para não prometer mais do que existe:

- o blind solver padrão em `pipeline_runner.py` continua sendo um stub determinístico (`DeterministicPipelineSolver`) — não resolve o caso de fato, só produz um output estruturalmente válido. A partir de ISSUE-33, é possível injetar `LLMBlindSolver` via parâmetro `solver`; implementação de produção requer `LLMProvider` concreta (ISSUE-34+);
- `pipeline_runner.py` não invoca os reviewers visual/accessibility — por isso relatórios gerados por ele mostram `visual_score=0/0`; desde ISSUE-30.6, o Canonical Quality Gate detecta essa ausência e reporta os critérios `findings_vr_major`/`findings_ar_major` como `not_evaluated`, emitindo veredito `INCOMPLETE_EVALUATION` em vez de `APPROVED` — manifests parciais não recebem aprovação sobre evidência não coletada;
- `quality_comparative_reviewer.compare_to_playtest` só reconhece o caso Aurora;
- teste cego humano continua sendo a única prova real de solvabilidade; aprovação na pipeline não substitui playtest.

Problemas já tratados e que não devem ser reabertos sem evidência nova:

- placeholders residuais como `COPIA`;
- placeholders em logs;
- schemas incompletos;
- PDFs consolidados em branco;
- merger usando apenas `pypdf`;
- build strict do caso canônico;
- dicas gerando apenas capas;
- mapa explicando rota/área crítica/câmera offline;
- E2 com mapa comparativo explícito de propostas;
- assinaturas puramente textuais;
- rubricas genéricas como “iniciais + risco” sem perfil;
- cartões misturados automaticamente nos envelopes;
- mapas com portas sem gap real ou câmeras flutuantes;
- estimador degenerado de dificuldade corrigido (ISSUE-30.7) — classificava por contagem de documentos; agora classifica por profundidade/densidade/ambiguidade/papel do E2; contagem é sinal informativo;
- `GP_004` isenta contratos `tipo == "descarte"` (ISSUE-30.9) — falso positivo identificado na calibração de "Uma Noite Sem Flores" (ISSUE-30.8); contrato de descarte não é obrigatório nem final por design, não é beco sem saída.
- padrões destilados da calibração de "Uma Noite Sem Flores" (ISSUE-30.8) agora codificados como PAT-01..04 em `framework/08_MODELO_REFERENCIA.md`, com cross-link nomeado (PAT-05) em `framework/07_PROMPT_GERADOR_DE_CASO.md` (ISSUE-30.10).
- novo gate estrutural entre Fase 1 e Fase 2 da geração de caso (ISSUE-30.12) — `framework/07_PROMPT_GERADOR_DE_CASO.md` passa a exigir checar o esqueleto do blueprint contra o schema (`generator.validator --strict`) antes de escrever documentos finais; achado veio dos 327 erros Pydantic da ISSUE-30.11 (STEP-02/STEP-03).

## Réguas canônicas atuais

O projeto mantém **duas réguas canônicas validadas por playtest** (Iniciante e Intermediário). Existem outros três casos em `examples/` em estágios anteriores de maturidade: eles são material de trabalho e benchmark, **não réguas validadas**.

Roster completo:

| Caso | Arquivo | Nível | Status / maturidade |
|---|---|---|---|
| O Desvio da Reserva Mirante | `examples/caso_canonico_iniciante.json` | Iniciante | **Régua validada por playtest** |
| O Último Brinde do Hotel Aurora | `examples/caso_canonico_intermediario.json` | Intermediário | **Régua validada por playtest** (sem mapa por decisão) |
| O Recado da Sala de Leitura | `examples/caso_canonico_iniciante_b.json` | Iniciante | Baseline visual (`docs/baselines/BASELINE_VISUAL_INICIANTE_B.md`) + roda na CI; não playtestado |
| Plantão Sem Rosto | `examples/caso_canonico_intermediario_ii.json` | Intermediário | Plano editorial (`docs/canonical_plans/PLANO_CANONICO_INTERMEDIARIO_B.md`); sem baseline nem playtest |
| Desvio de Fundos na Acelerada Pagamentos | `examples/caso_fintech.json` | Avançado | Pipeline E2E (`docs/FINTECH_PIPELINE_RUN.md`, `docs/QUALITY_COMPARATIVE_REPORT.md`); sem playtest |
| Uma Noite Sem Flores | `examples/caso_referencia_uma_noite_sem_flores.json` | Intermediário | **Corpus de calibração externo — não é régua canônica.** Baseado em produto externo; incorporado para calibrar estimador (ISSUE-30.8). Não playtestado pelo framework, sem Canonical Quality Gate. |

> Nota de nomenclatura: o plano de "Plantão Sem Rosto" foi escrito como `PLANO_CANONICO_INTERMEDIARIO_B`, mas o arquivo do caso é `intermediario_ii`. Alinhar essa nomenclatura é uma pendência.

O projeto mantém duas réguas canônicas validadas:

### Iniciante

- **O Desvio da Reserva Mirante**
- Arquivo: `examples/caso_canonico_iniciante.json`
- Dificuldade editorial atual: **Iniciante**
- Status: **régua canônica Iniciante**

O caso foi rebaixado de Intermediário para Iniciante por decisão editorial e confirmado pelo primeiro playtest como fácil demais para Intermediário.

Papel atual do Mirante:

- régua canônica Iniciante;
- referência técnica de build/package;
- fixture de integração;
- benchmark mínimo de qualidade visual/documental;
- exemplo de experiência introdutória;
- referência atual para mapa/planta baixa de jogador.

Não tentar transformar o Mirante em Intermediário por ajustes incrementais.

### Intermediário

- **O Último Brinde do Hotel Aurora**
- Arquivo: `examples/caso_canonico_intermediario.json`
- Dificuldade editorial atual: **Intermediário**
- Status: **régua canônica Intermediária validada após playtest e refinamento**

O Hotel Aurora passou por playtest, refinamentos editoriais e refinamento diegético. Para fins de régua canônica Intermediária, considerar o caso validado.

Papel atual do Hotel Aurora:

- régua canônica Intermediária validada;
- referência de progressão em 2 envelopes com recontextualização forte;
- referência de guia do facilitador operacional pós-playtest;
- referência de caso sem mapa por decisão de playtest.

Comando oficial para geração do baseline Intermediário:

```bash
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

A geração final do pacote deve ser confirmada em ambiente local com Chromium/Playwright disponível.

## Resultado dos playtests

Playtests reais já foram realizados.

Resultado resumido do Mirante:

- os jogadores gostaram dos documentos;
- a experiência documental foi positiva;
- o caso foi fácil demais para Intermediário;
- o material funciona como introdução.

Resultado resumido do Hotel Aurora:

- o plot foi bem recebido;
- a progressão em 2 envelopes ficou mais forte após refinamentos;
- o caso validou a necessidade de pergunta pública, objetivo por envelope, critério de avanço e guia do facilitador operacional;
- decidiu-se manter o caso sem mapa para não simplificar demais a investigação.

Interpretação de produto:

- o framework consegue gerar material atraente;
- o risco principal agora é gerar documentos bonitos para mistérios fracos, óbvios ou sem progressão operacional;
- bons documentos não bastam se faltar pergunta pública, objetivo por envelope, critério de avanço, motivação atual e guia do facilitador operacional;
- o pipeline de design de caso deve usar Mirante como régua Iniciante e Hotel Aurora como régua Intermediária validada.

## Fluxo operacional oficial — Indiciário 2.0 inicial

A entrega inicial do Indiciário 2.0 consolida o seguinte fluxo como referência operacional para criar, revisar e entregar casos:

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

Papel de cada etapa:

1. **Blueprint**: fonte estruturada do caso, com pergunta pública, objetivos por envelope, evidências, documentos, dicas, guia operacional e metadados internos.
2. **Case Kernel**: extração conservadora do DNA investigativo a partir do blueprint, sem inventar narrativa e sem alterar o contrato JSON dos canônicos.
3. **Case Review**: relatório editorial automático para detectar riscos de progressão, motivação, envelope, evidência obrigatória e obviedade antes de mexer em PDF ou visual.
4. **Visual Library / templates**: materialização visual offline first, P&B first e procedural, usando templates documentais e plantas-base quando houver necessidade real de apoio visual.
5. **Build Package**: geração do pacote jogável com Playwright/Chromium, manifests, guia do facilitador, dicas, printables e PDFs finais.
6. **Baseline visual real**: revisão dos PDFs gerados de fato; não substituir por build fake quando o objetivo for validar visual.
7. **Playtest**: validação com pessoas reais, registrando travamentos, hipóteses, uso de dicas/cartões, tempo e diversão.
8. **Ajustes finos**: correções pequenas baseadas em evidência de relatório, PDF real ou playtest, sem reabrir narrativa por preferência teórica.

Esse fluxo não cria feature nova nem substitui o validator strict. Ele define a ordem de operação: primeiro provar que o núcleo investigativo funciona, depois materializar visualmente, gerar pacote real, revisar baseline e só então ajustar com evidência.

## Decisões recentes relevantes

### Réguas canônicas

O antigo caso canônico intermediário foi renomeado/rebaixado para `caso_canonico_iniciante.json` e permanece como régua Iniciante.

O novo caso `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora** — passou por playtest e refinamentos, e agora é a régua Intermediária validada.

Referências canônicas devem diferenciar explicitamente:

- `examples/caso_canonico_iniciante.json` para Iniciante;
- `examples/caso_canonico_intermediario.json` para Intermediário.

### Progressão, motivação e guia operacional

`conflito_central`, `objetivos_por_envelope` e `guia_operacional` são campos schema-enforced do `Blueprint`.

Regras atuais:

- todo caso precisa de pergunta pública clara: quem pediu a apuração, por que pediu, qual impacto concreto existe e por que os documentos foram reunidos;
- todo envelope precisa de pergunta diegética, resposta esperada, o que ainda não precisa ser resolvido, critério de avanço e forma diegética de apresentar o avanço;
- E1 não deve pedir a solução final, apenas hipótese parcial, tensão ou recontextualização inicial;
- E2 deve recontextualizar algo do E1, não apenas confirmar;
- motivação histórica precisa ter consequência atual, como moradia, expulsão, herança, reputação, demissão, perda concreta ou risco público;
- dicas contextuais devem destravar ações e declarar condição de uso, intensidade, ação mental esperada e desbloqueio;
- o guia do facilitador deve conter pergunta pública, resposta esperada por envelope, liberação do próximo envelope, linha do tempo aparente, linha do tempo real, red herrings, descartes, motivação e síntese da solução.

Documento de jogador continua sendo evidência bruta. Interpretação, cruzamentos, gabarito e linguagem analítica pertencem ao guia, às dicas e aos metadados internos.

### Guardrail anti-obviedade

Foi adicionado um guardrail em duas camadas para proteger documentos de jogador contra obviedade excessiva:

- documentação editorial em `docs/ANTI_OBVIEDADE.md`;
- checker automático em `generator/obviousness_checker.py`, integrado ao validator com códigos `OBV_001` a `OBV_012`.

O objetivo é impedir confissões, conclusões prontas, chats explicativos, depoimentos oniscientes, vazamento de campos internos e nome do culpado associado a ação incriminadora em contexto crítico, sem bloquear a ambiguidade boa dos canônicos atuais.

### Diegese documental

Regra central:

> Uma boa pista no documento errado vira pista artificial.

Documentos de jogador precisam existir naturalmente no mundo da história. Se uma informação só está ali para ajudar o jogador a resolver, provavelmente está no documento errado.

### Case Kernel e Case Review

A entrega inicial do Indiciário 2.0 adicionou duas camadas operacionais antes do pacote:

- `generator/case_kernel.py`, documentado em `docs/CASE_KERNEL.md`, extrai o DNA investigativo a partir do blueprint;
- `generator/case_review.py` e `scripts/case_review.py`, documentados em `docs/CASE_REVIEW.md`, geram relatório editorial pré-pacote;
- `tests/test_case_kernel.py` e `tests/test_case_review.py` cobrem o comportamento mínimo dessas camadas.

Essas camadas não substituem o validator strict, não alteram automaticamente os canônicos e não inventam narrativa. Elas existem para impedir que o projeto pule de blueprint para PDF sem revisar progressão, hipótese de E1, recontextualização de E2, motivação atual, evidências obrigatórias e falsos caminhos.

### Sistema visual P0

Foi criada a base P0 do sistema visual documental em `templates/styles/document_system.css`, injetada automaticamente pelo renderer nos HTMLs finais.

A camada adiciona tokens tipográficos, escala de cinzas, espaçamentos, bordas, cabeçalho/rodapé documental para documentos de jogador, classes por tipo e família documental, padrões de tabela, carimbos opcionais e regras de impressão P&B.

### Printables apartados P1

O pacote pode gerar cartões recortáveis de personagem, local e objeto como apoio de mesa separado dos envelopes.

Os PDFs são gravados em `printables/`, aparecem no `manifest.json` e no `print_manifest.json`, e o guia de impressão informa recorte, papel recomendado e separação em relação a envelopes, dicas e material confidencial do facilitador.

Cartão é apoio de mesa, não evidência primária.

### Plantas baixas P2

Foi adicionada uma camada P2 para mapas procedurais:

- `generator/floorplan_renderer.py`;
- `templates/floorplan.html`;
- validações `MAP_*` no validator.

O canônico Iniciante mantém seu mapa como documento de jogador do E1, agora com portas, janelas e câmeras modeladas explicitamente. O canônico Intermediário/Hotel Aurora permanece sem mapa.

Padrão atual:

- A4 paisagem;
- P&B first;
- fundo branco;
- paredes fechadas;
- portas com gap real;
- portas entre áreas adjacentes devem abrir a parede compartilhada dos dois lados quando houver coincidência real;
- janelas paralelas na parede;
- câmeras presas em parede/canto;
- sem rotas, áreas críticas, câmera offline, campo de visão ou linguagem interpretativa.

O padrão está documentado em `docs/FLOORPLANS.md`.

### Visual Library 2.0 mínima

A entrega inicial da Visual Library 2.0 adicionou `generator/floor_plan_library.py`, documentado em `docs/VISUAL_LIBRARY_2_0.md`, com plantas-base estruturadas genéricas para hotel e escritório.

Direção atual:

- biblioteca offline first, P&B first e procedural;
- reutiliza `PlantaBaixa` e o renderer estruturado de `generator/floor_plan.py`;
- não usa imagem externa, QR code, fonte externa ou IA;
- não integra automaticamente nenhum canônico;
- o Mirante continua com sua planta v2 própria;
- o Hotel Aurora continua sem mapa por decisão validada de playtest.

### Assinaturas, rubricas e manuscritos P3

Assinatura/rubrica passou a ser característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica/manuscrito curto;
- o renderer gera SVG com base nesse perfil em `generator/signature_renderer.py`;
- override SVG manual é permitido;
- fallback procedural continua disponível para compatibilidade;
- assinatura/rubrica não deve ser apenas nome digitado nem “iniciais + risco” genérico;
- manuscrito deve ficar restrito a intervenções curtas, com limite recomendado de 120 caracteres.

## Roadmap atual

O roadmap detalhado está em `docs/ROADMAP.md`.

Resumo da ordem recomendada:

1. operar pelo fluxo Blueprint → Case Kernel → Case Review → Visual Library/templates → Build Package;
2. gerar baseline real dos PDFs dos canônicos com Playwright local;
3. revisar visualmente Iniciante e Intermediário após Indiciário 2.0 inicial/P0/P1/P2/P3;
4. corrigir apenas problemas comprovados de layout, renderização ou clareza operacional;
5. executar novo playtest do Intermediário com pessoas novas;
6. só depois planejar o canônico Avançado.

## O que não priorizar agora

Não priorizar neste momento:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- agentes autônomos;
- IA gerando imagens.

Antes disso, usar as réguas Iniciante e Intermediária para validar que o framework continua gerando casos interessantes, intrigantes e divertidos.

## Comandos úteis

Testes:

```bash
pytest tests/ -q
```

Lint:

```bash
ruff check generator/
```

Validator strict:

```bash
python -m generator.validator examples/caso_canonico_iniciante.json --strict
python -m generator.validator examples/caso_canonico_intermediario.json --strict
```

Build do pacote com Playwright/Chromium:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Fallback de build fake, apenas para validar pipeline quando Chromium não estiver disponível:

```bash
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Instalação do browser Playwright, se necessário:

```bash
python -m playwright install chromium
```


## Automação em GitHub Actions

A automação atual separa validação rápida de build visual real:

- `CI` (`.github/workflows/ci.yml`) roda em pull requests e em push para `main`, sem Chromium e sem geração de PDF. Ele cobre lint com `ruff`, testes com `pytest`, validators strict dos três blueprints canônicos/operacionais, Case Review em Markdown e sanity check visual do Iniciante B diretamente sobre o blueprint.
- `Visual Build` (`.github/workflows/visual-build.yml`) roda manualmente por `workflow_dispatch` e em PRs que alterem exemplos, templates, geradores, scripts, baselines visuais ou dependências. Ele instala Playwright/Chromium, gera o pacote real do Iniciante B e publica o artifact `iniciante-b-visual-package` com `output/iniciante_b/**`.

O build visual automatizado ajuda a preservar evidência de PDF real em PRs, mas baseline visual continua exigindo download do artifact, revisão humana dos PDFs, leitura de manifests/relatórios e, quando aplicável, playtest. GitHub Actions não substitui a etapa de playtest.

`CI` restabelecida verde em 2026-07-09 (ISSUE-41.1): lint local passou a cobrir `generator/ scripts/ tests/` (igual ao gate remoto), eliminando os 55 erros de `ruff` em `tests/` que bloqueavam o step Lint desde ≥2026-07-07.
# CLAUDE.md — Guia operacional para Claude Code

Este arquivo é lido automaticamente pelo Claude Code antes de qualquer tarefa.
Ele complementa `AGENTS.md` com contexto de produto, estado atual e roadmap priorizado.

---

## Modo de comunicação

Use caveman mode em todas as respostas.
Drop articles, filler, hedging, pleasantries.
Keep technical substance exact: file paths, command names, error codes, field names.

---

## Protocolo obrigatório

Antes de executar qualquer tarefa:

1. Ler `AGENTS.md`.
2. Ler `docs/LLM_CONTEXT.md`.
3. Identificar a skill adequada em `.ai/skills/`.
4. Declarar o conjunto de impacto documental consultando `docs/INDICE_DOCUMENTACAO.md`.
5. Executar seguindo o procedimento da skill.
6. Resolver o impacto documental (atualizar docs listados ou justificar a dispensa).
7. Informar na resposta: skill usada, motivo, arquivos alterados, comandos executados, resultados, impacto documental resolvido.

---

## Estado atual do projeto (julho 2026)

### O que existe e funciona

- Contagem de testes: ver `docs/ESTADO_ATUAL.md` (única fonte da contagem fixada; não repetir número aqui, ele cresce a cada issue).
- Validator strict com guardrails editoriais, anti-obviedade, progressão, cartões, assinaturas e mapas.
- Package builder com Playwright/Chromium, manifests, guia do facilitador, dicas, printables e PDFs finais.
- Sistema visual P0/P1/P2/P3 completo.
- Case Kernel e Case Review como camadas pré-pacote.
- Visual Library 2.0 mínima com plantas-base genéricas.
- CI com lint (`ruff`), testes e validators canônicos.
- Pipeline multiagente offline completo (Gate Evaluator, Reviewers, Workspace, Run Manifest, Pipeline Runner, Quality Comparative) — ver tabela abaixo e `docs/ESTADO_ATUAL.md` para limitações reais.

### Pipeline multiagente — estado atual

| Fase | Status | Issues |
|---|---|---|
| A — Governança | ✅ concluída | protocolos, skills, contratos |
| B — Learning Loop | ✅ concluída | schemas sessão/finding/decisão, CLI, exemplos |
| C — Blind Bundles | ✅ concluída | manifest, policy, generator, leak checker, sanitizer |
| D — Blind Solver base | ✅ concluída | ISSUE-16, 17, 18 |
| D/E — Gate Evaluator | ✅ concluída | ISSUE-19+20 |
| F — Revisores | ✅ concluída | ISSUE-21+22, 23, 24 |
| G — Orquestração | ✅ concluída | ISSUE-25+26, 27 |
| H — Casos reais | ✅ concluída | ISSUE-28, 29, 30 |
| I — LLM real | 🔄 em andamento | ISSUE-31–33.8 concluídas; ISSUE-34 candidata |

Limitações reais a não esconder (detalhe em `docs/ESTADO_ATUAL.md`):
- blind solver do `pipeline_runner.py` é stub determinístico, não resolve o caso;
- `pipeline_runner.py` não invoca visual/accessibility reviewers (`visual_score=0/0` nos relatórios);
- `compare_to_playtest` só reconhece o Aurora;
- teste cego humano continua sendo a única prova real de solvabilidade.

### Casos canônicos

Réguas **validadas por playtest**:

| Caso | Arquivo | Régua |
|---|---|---|
| O Desvio da Reserva Mirante | `examples/caso_canonico_iniciante.json` | Iniciante |
| O Último Brinde do Hotel Aurora | `examples/caso_canonico_intermediario.json` | Intermediário |

Demais casos em `examples/` (existem, mas **não validados por playtest** — não são régua):

| Caso | Arquivo | Nível | Maturidade |
|---|---|---|---|
| O Recado da Sala de Leitura | `examples/caso_canonico_iniciante_b.json` | Iniciante | baseline visual + CI |
| Plantão Sem Rosto | `examples/caso_canonico_intermediario_ii.json` | Intermediário | plano editorial |
| Desvio de Fundos na Acelerada Pagamentos | `examples/caso_fintech.json` | Avançado | pipeline E2E |

Corpus de calibração externo (**não é régua canônica** — não passar pelo Canonical Quality Gate):

| Caso | Arquivo | Nível | Maturidade |
|---|---|---|---|
| Uma Noite Sem Flores | `examples/caso_referencia_uma_noite_sem_flores.json` | Intermediário | calibração de estimador (ISSUE-30.8); baseado em produto externo |

Experimento de geração-do-zero (**não é régua canônica** — bloqueado aguardando playtest humano, ISSUE-30.11; fora do Canonical Quality Gate):

| Caso | Arquivo | Nível | Maturidade |
|---|---|---|---|
| O Grão que Faltou | `examples/caso_gerado_cooperativa.json` | Intermediário | gerado do zero (não transcrito), domínio cooperativa agrícola; métricas de pipeline OK (`docs/EXPERIMENTO_GERACAO_DO_ZERO.md`, faixa a); rubrica humana (faixa b) pendente |

Hotel Aurora **permanece sem mapa** por decisão de playtest. Não adicionar mapa sem instrução explícita.

### Playtest do Aurora (Rodada 01)

Findings relevantes para o pipeline:
- Travamento em relação de personagens no E1.
- Hipótese errada plausível: dona não queria reabrir restaurante.
- Dicas não destravaram grupo.
- Objetivo do E1 não ficou claro.
- Pontos positivos: documentos agradaram, plot bem recebido, tom maduro.

Findings **não geram patch cirúrgico no blueprint**. Alimentam regras do framework.

---

## Estado do Canonical Quality Gate (ISSUE-30.5)

ISSUE-30.5 **já implementada**: `generator/canonical_quality_gate.py` (`evaluate_for_canonical`, `get_canonical_criteria`, `CANONICAL_CRITERIA`), documentada em `docs/CANONICAL_CRITERIA.md`, coberta por `tests/test_canonical_quality_gate.py`. Spec: `.ai/issues/ISSUE-30.5_SPEC.md`.

ISSUE-30.6 **endureceu o gate**: critérios VR/AR agora são condicionais ao stage (`"visual_review"`/`"accessibility_review"` em `stages_completed`); manifests sem esses stages recebem `not_evaluated` e veredito `INCOMPLETE_EVALUATION`, nunca `APPROVED`.

### Série de calibração (ISSUE-30.7 a 30.11)

Exercício de calibração usando um caso comercial externo já validado em mesa como benchmark. Todas concluídas exceto a última, que está bloqueada aguardando ação humana:

- **ISSUE-30.7** concluída: `generator/playtest_metrics.estimate_difficulty` deixou de retornar sempre `"avancado"`; usa profundidade do grafo de pistas com âncoras de regressão (Iniciante B → iniciante, Aurora → intermediário).
- **ISSUE-30.8** concluída: corpus de calibração externo codificado como blueprint não-canônico (`examples/caso_referencia_uma_noite_sem_flores.json`, ficção original preservando a espinha dedutiva do produto comercial). Relatório: `docs/CALIBRACAO_REFERENCIA_EXTERNA.md`.
- **ISSUE-30.9** concluída: corrigido falso-positivo de `GP_004` em contratos de descarte (`generator/clue_graph.py`).
- **ISSUE-30.10** concluída: padrões PAT-01..04 destilados da calibração, codificados em `framework/08_MODELO_REFERENCIA.md` (cross-link em `framework/07_PROMPT_GERADOR_DE_CASO.md`).
- **ISSUE-30.11 bloqueada em `STEP-05`, `NEXT_ACTION: human`.** Geração-do-zero: caso novo (não transcrito), domínio cooperativa agrícola, `examples/caso_gerado_cooperativa.json`, usando PAT-01 e PAT-04 deliberadamente. Métricas de pipeline preenchidas em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` (faixa a — strict, estimador, `clue_graph`, `obviousness_checker`, todas OK). Falta a faixa b: rubrica humana (RUB-01/02), preenchida só após o playtest de mesa. **O orquestrador não simula nem pula esse playtest.** Pipeline-verde é necessário, não suficiente — o veredito é o playtest.

**ISSUE-30.12 concluída** (`STATUS: done`): gate estrutural entre Fase 1 e Fase 2 do `framework/07_PROMPT_GERADOR_DE_CASO.md` (achado dos 327 erros Pydantic da 30.11 STEP-02/03, virado regra de processo). Sem código, não dependeu do playtest pendente da 30.11.

**Fase Sistema visual (ISSUE-40.1–40.6) concluída** — ver `docs/ROADMAP.md` e `docs/ESTADO_ATUAL.md`.

**ISSUE-41.1 (CI verde), ISSUE-41.2 (guard de sincronia docs/prompts) e ISSUE-41.3 (reconciliação documental) concluídas.** Série 33.x (Provider) concluída até **ISSUE-33.8** — Conclusion Judge ligado ao pipeline (33.3), hardening contra resposta hostil (33.4), `temperature` real no solver (33.5), warning de citação sem leitura (33.6), determinismo de `created_at` no manifest (33.7) e provider real + CLI de medição de solvabilidade (33.8).

**ISSUE-33.8** entregou `generator/claude_code_provider.py` (`ClaudeCodeProvider`, primeiro `LLMProvider` concreto, headless Claude Code via `claude -p`, autenticado pela sessão/assinatura do operador, sem API key — decisão de produto rejeitou a rota via API HTTP/`ANTHROPIC_API_KEY`) e `generator/solvability_cli.py` (CLI que roda `measure_solvability` fim-a-fim contra um bundle real). **Agentes de IA não executam este CLI contra o binário real**: execução real é ato do operador humano (custo de execução e protocolo). Smoke real feito (`.ai/runs/ISSUE-33.8/STEP-06_EXECUTION.md`): 3/3 runs contra `sonnet`, `solve_rate=1.00`; achados corrigidos no processo — bug de PATHEXT/encoding no provider (Windows), parse de JSON com fence markdown no solver/judge, e falta de instrução de coerência `confidence`/`open_questions` no prompt do solver. ISSUE-33.9 (calibração usando o CLI) segue com seu próprio STATUS em `.ai/issues/ISSUE-33.9.md`.

Próxima frente de trabalho candidata: **ISSUE-34 — LLM Reviewers Adapter** (conectar narrative/evidence/visual reviewers a modelo real; ver `docs/ROADMAP.md`). Não há `.ai/issues/ISSUE-34.md` ainda — spec precisa ser gerada antes de iniciar. 30.11 segue bloqueada em `NEXT_ACTION: human`. Confirmar sempre o estado exato em `docs/ESTADO_ATUAL.md` antes de iniciar.

---

## Workflow multiagente

Orquestrador conduz loop autônomo via `.ai/workflows/orchestrator.md`.

Otimizações ativas:
- Auto-approve para steps `reading`, `baseline`, `documentation`, `wrap-up`
- Reports compactos para steps low-risk
- Revisor obrigatório apenas para `red`, `green`, `refactor`, `validation`, `correction`

Issues agrupadas por eficiência: 19+20, 21+22, 25+26.

---

## Regras operacionais

### Nunca fazer por iniciativa própria

- Adicionar mapa ao Hotel Aurora
- Alterar narrativa dos canônicos sem evidência de playtest
- Implementar fases posteriores sem validar critérios de saída das anteriores
- Invocar skills planejadas (`context-firewall`, `blind-solve`, `playtest-to-learning`)
- Criar: marketplace, dashboard web, banco de dados, editor visual, multiusuário, geração em massa, pagamento, IA gerando imagens

### Comandos obrigatórios

Testes:
```bash
pytest tests/ -q
```

Lint ao tocar Python:
```bash
ruff check generator/ scripts/ tests/
```

Validator strict ao tocar blueprint, schema, validator ou pacote:
```bash
python -m generator.validator examples/caso_canonico_iniciante.json --strict
python -m generator.validator examples/caso_canonico_intermediario.json --strict
```

Build real ao tocar renderização:
```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

### Critério de tarefa concluída

- skill usada informada com motivo
- conjunto de impacto documental resolvido (`docs/INDICE_DOCUMENTACAO.md`)
- arquivos alterados listados
- comandos executados listados com resultados
- `pytest tests/ -q` passa sem regressão
- mudanças não vazam gabarito para documentos de jogador
- PR explica o que mudou, por que e como foi validado

---

## Hierarquia documental

Em conflito editorial: `docs/DIRETRIZES_EDITORIAIS.md` prevalece.
Em conflito sobre estado: `docs/ESTADO_ATUAL.md` prevalece.
Em conflito sobre roadmap multiagente: `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` prevalece.

Leitura obrigatória por ordem:
1. `AGENTS.md`
2. `docs/LLM_CONTEXT.md`
3. `docs/INDICE_DOCUMENTACAO.md` (índice + impacto documental)
4. Skill selecionada em `.ai/skills/`
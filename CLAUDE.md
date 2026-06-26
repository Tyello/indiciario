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

## Estado atual do projeto (junho 2026)

### O que existe e funciona

- **~1354 testes** coletados por `pytest tests/ -q` (checar contagem exata antes de citar em PR; ver `docs/ESTADO_ATUAL.md`).
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
| I — LLM real | 🔮 futuro | ISSUE-31–34 |

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

Próxima frente de trabalho: ver `docs/ROADMAP.md`. Não há issue em andamento fixada aqui — confirmar o estado em `docs/ESTADO_ATUAL.md` antes de iniciar.

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
ruff check generator/
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
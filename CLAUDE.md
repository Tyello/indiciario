# CLAUDE.md — Guia operacional para Claude Code

Este arquivo é lido automaticamente pelo Claude Code antes de qualquer tarefa.
Ele complementa `AGENTS.md` com contexto de produto, estado atual e roadmap priorizado.

---

## Modo de comunicação

Use caveman mode em todas as respostas desta sessão.
Drop articles, filler, pleasantries. Keep technical substance exact.

---

## Protocolo obrigatório

Antes de executar qualquer tarefa:

1. Ler `AGENTS.md`.
2. Ler `docs/LLM_CONTEXT.md`.
3. Identificar a skill adequada em `.ai/skills/`.
4. Executar seguindo o procedimento da skill.
5. Informar na resposta: skill usada, motivo, arquivos alterados, comandos executados, resultados.

---

## Estado atual do projeto (junho 2026)

### O que existe e funciona

- 865 testes passando (`pytest tests/ -q`).
- Validator strict com guardrails editoriais, anti-obviedade, progressão, cartões, assinaturas e mapas.
- Package builder com Playwright/Chromium, manifests, guia do facilitador, dicas, printables e PDFs finais.
- Sistema visual P0/P1/P2/P3 completo: CSS documental, printables, plantas baixas, assinaturas/manuscritos.
- Case Kernel (`generator/case_kernel.py`) e Case Review (`generator/case_review.py`) como camadas pré-pacote.
- Visual Library 2.0 mínima (`generator/floor_plan_library.py`) com plantas-base genéricas.
- Infraestrutura multiagente documental (Fases A–C): protocolos, schemas de sessão/finding/decisão, blind bundle, leak checker.
- CI com lint (`ruff`), testes e validators canônicos. Visual Build separado com Playwright real.

### Casos canônicos

| Caso | Arquivo | Régua | Status |
|---|---|---|---|
| O Desvio da Reserva Mirante | `examples/caso_canonico_iniciante.json` | Iniciante | Régua validada |
| O Último Brinde do Hotel Aurora | `examples/caso_canonico_intermediario.json` | Intermediário | Régua validada pós-playtest |

O Hotel Aurora **permanece sem mapa** por decisão de playtest. Não adicionar mapa sem instrução explícita.

### Playtest do Aurora (Rodada 01 — 2026-06-05)

Participantes: Marcelo (36), Gabi (35), Marina (11). Tempo total: ~90–100 min (60–70 min E1, 30 min E2).

Findings principais:
- **Travamento em relação de personagens**: quem conhece quem, motivações cruzadas não ficaram claras no E1.
- **Hipótese errada plausível**: grupo suspeitou que a dona não queria reabrir o restaurante.
- **Dicas fracas**: não destravaram o grupo de forma efetiva.
- **Objetivo do E1 não ficou claro**: grupo não sabia qual conclusão era suficiente para abrir E2.
- Pontos positivos: documentos agradaram, plot bem recebido, tom maduro, distração das chaves funcionou.

Esses findings estão no Learning Ledger em `examples/learning/retrospective/`.

---

## Roadmap priorizado

### Prioridade imediata (próximas tasks)

**O projeto está na transição entre baseline visual e início do pipeline multiagente.**

O baseline visual foi gerado sem problemas. O playtest do Aurora foi realizado e registrado.
A próxima fase lógica é iniciar a **Fase D do roadmap multiagente: Blind Solver**.

Antes de começar a Fase D, verificar se o playtest da Rodada 01 está formalmente registrado
nos schemas do Learning Loop (sessão YAML, findings, decisões). Se não estiver completo,
esse é o primeiro passo — os findings do Aurora alimentam o blind solver.

### Fase D — Blind Solver (próxima a implementar)

Issues a executar em ordem:

**ISSUE-16 — Blind Solver: contrato de saída e harness offline**
- Definir schema de resposta do solver (fatos, hipóteses, conclusão, confiança, evidência usada).
- Criar harness offline que recebe um blind bundle e produz um relatório estruturado.
- Implementar com solver stub/fake — sem LLM real obrigatória ainda.
- Validar que o solver não acessa material fora do bundle.
- Skill recomendada: `tdd`.

**ISSUE-17 — Blind Solver Report Validator**
- Validar se a resposta do solver tem estrutura útil.
- Separar fatos, hipóteses, conclusão, confiança e evidência usada.
- Impedir resposta vaga ou sem rastreabilidade.
- Skill recomendada: `tdd`.

**ISSUE-18 — Blind Solve Run Record**
- Registrar execução cega como run rastreável.
- Ligar: bundle usado, solver, output, artifacts, decisões posteriores.
- Skill recomendada: `tdd`.

### Fase E — Gate Evaluator

**ISSUE-19 — Gate Evaluator: contrato de avaliação**
- Avaliar se o caso é justo dado o bundle cego.
- Classificar problemas: pista insuficiente, pista ambígua, solução óbvia demais, excesso de ruído, quebra de progressão, vazamento de solução.
- Skill recomendada: `to-prd` antes de implementar (escopo amplo).

**ISSUE-20 — Gate Evaluator Harness**
- Receber solver report + manifest + documentos privados autorizados.
- Gerar gate decision.
- Bloquear caso se necessário.
- Skill recomendada: `tdd`.

### Fase F — Revisores especializados

**ISSUE-21 — Narrative Reviewer**: imersão, diegese, motivação, tom, personagens.
**ISSUE-22 — Evidence Reviewer**: cadeia de evidências, pistas órfãs, buracos lógicos.
**ISSUE-23 — Visual Reviewer**: renderização, legibilidade, densidade, mapas, aparência documental.
**ISSUE-24 — Accessibility Reviewer**: leitura mobile/tablet, contraste, fonte, sobrecarga cognitiva, impressão.

Skill recomendada para todas: `to-prd` antes de implementar. São escopo amplo.

### Fase G — Orquestração de runs

**ISSUE-25** — Multiagent Workspace: diretório padrão por run, artefatos de entrada/saída, logs, findings, gate decisions.
**ISSUE-26** — Manual Orchestrator: orquestrar etapas sem LLM automática, comandos manuais, offline, rastreável.
**ISSUE-27** — Run Manifest / Run Summary: consolidar tudo que aconteceu em uma run.

### Fase H — Aplicação em casos reais

**ISSUE-28** — Rodar pipeline no caso Hotel Aurora: aplicar blind bundle → blind solver → gate evaluator → findings → comparar com playtest real.
**ISSUE-29** — Rodar pipeline no caso Fintech (caso corporativo médio-alto).
**ISSUE-30** — Relatório comparativo de qualidade: antes/depois, clareza, dificuldade, vazamentos, visual, pacing.

### Fase I — Automação com LLM (só depois da base testável)

**ISSUE-31** — Provider Interface: interface para chamar LLM sem acoplar a OpenAI/Claude/Ollama.
**ISSUE-32** — Fake Provider para testes: simular respostas previsíveis, CI determinística.
**ISSUE-33** — LLM Blind Solver Adapter: conectar modelo real ao harness, mantendo blind bundle como única entrada.
**ISSUE-34** — LLM Reviewers Adapter: conectar narrative/evidence/visual reviewers.

### Pendente antes do Avançado

Não iniciar `caso_canonico_avancado.json` sem:
- ISSUE-28 completa (pipeline rodado no Aurora).
- Segundo playtest do Aurora com pessoas novas registrado formalmente.
- Plano Markdown do Avançado aprovado por Marcelo.

---

## Regras operacionais

### O que nunca fazer por iniciativa própria

- Adicionar mapa ao Hotel Aurora.
- Alterar narrativa dos canônicos sem evidência de playtest.
- Implementar fases posteriores sem validar critérios de saída das anteriores.
- Invocar skills planejadas (`context-firewall`, `blind-solve`, `playtest-to-learning`) — elas ainda não existem como arquivos.
- Criar: marketplace, dashboard web, banco de dados, editor visual, multiusuário, Telegram comercial, geração em massa, pagamento, IA gerando imagens.

### Comandos obrigatórios

Testes (sempre rodar antes de fechar tarefa):
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

Uma tarefa só está concluída quando:
- skill usada foi informada com motivo;
- arquivos alterados foram listados;
- comandos executados foram listados com resultados;
- `pytest tests/ -q` passa sem regressão;
- mudanças não vazam gabarito para documentos de jogador;
- PR explica o que mudou, por que mudou e como foi validado.

---

## Contexto do playtest para o pipeline multiagente

Os findings do Aurora (Rodada 01) são o primeiro conjunto de dados reais para o pipeline.
Ao implementar o Blind Solver e o Gate Evaluator, usar o Aurora como caso de referência.

Findings relevantes para o pipeline:
- Travamento em relação de personagens → evidência de que a cadeia de personagens no E1 não estava clara o suficiente.
- Hipótese errada (dona não quer reabrir) → red herring funcionou, mas pode ter sido forte demais.
- Dicas não destravaram → possível input para o Evidence Reviewer (ISSUE-22).
- Objetivo do E1 não ficou claro → gap na apresentação da pergunta pública para o jogador.

Esses findings **não devem gerar patch cirúrgico no blueprint do Aurora**.
Devem alimentar regras no framework para que futuros casos não repitam os mesmos problemas.

---

## Hierarquia documental

Em conflito editorial: `docs/DIRETRIZES_EDITORIAIS.md` prevalece.
Em conflito sobre estado do projeto: `docs/ESTADO_ATUAL.md` prevalece.
Em conflito sobre roadmap multiagente: `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` prevalece.

Leitura obrigatória por ordem:
1. `AGENTS.md`
2. `docs/LLM_CONTEXT.md`
3. Skill selecionada em `.ai/skills/`

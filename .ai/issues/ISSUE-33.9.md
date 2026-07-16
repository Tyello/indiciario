# ISSUE-33.9 — Calibração do Solvability Meter contra o benchmark — passos

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-04
NEXT_ACTION: human
REVIEW_STATUS: STEP-01 aprovado; STEP-02 PARCIAL (registrado); STEP-03 decidido (prosseguir sem anonimização)
LAST_COMPLETED_STEP: STEP-03
BLOCKER: STEP-04 exige execução headless (`claude -p`) consumindo cota da assinatura — ato do Marcelo, agente não executa (adendo aplicado, ver ISSUE-33.9_ADENDO.md)
```

## Contexto

Skill: `diagnose` — experimento com preparação/análise por agente e execução de API por humano. Não é issue de TDD: os "testes" são as hipóteses H1–H4 da SPEC.

Spec: `.ai/issues/ISSUE-33.9_SPEC.md`. Divisão de trabalho explícita: **STEP-02 e STEP-04 são do Marcelo** (custo de API e protocolo — agente não executa provider real).

## Steps

### STEP-01 — Preparação (Fase 1)
Status: pending | Owner: executor | Type: green
- Entregáveis E1 (expected + key_evidence_ids extraídos do blueprint transcrito, em `calibration/`) e E2 (bundle + leak_checker + hashes); smoke test do circuito com FakeProvider sobre o bundle real.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.9*.md; .ai/skills/diagnose.md; blueprint do benchmark em examples/; generator/; schemas/; docs/BLIND_SOLVER_HARNESS.md
Editáveis: calibration/expected_uma_noite_sem_flores.json; calibration/ (bundle e hashes); .ai/runs/ISSUE-33.9/STEP-01_EXECUTION.md
Comandos: geração de bundle; leak_checker; `python -m generator.solvability_cli` com fakes (smoke)
Proibido: qualquer chamada de API real; alterar o blueprint.
Done quando: E1/E2 commitáveis; smoke verde; hashes registrados.
Revisão: revisor obrigatório — statements de E1 fiéis ao gabarito e mínimos.
Dependências: ISSUE-33.9 done.

### STEP-02 — Sonda de contaminação (Fase 2) — HUMANO
Status: pending | Owner: **Marcelo** | Type: validation
- Executar as 3 perguntas da SPEC via `claude -p` headless (sem bundle, cwd tmp vazio — ver adendo); colar respostas brutas no report do step; classificar CONTAMINADO/PARCIAL/LIMPO.
Editáveis: .ai/runs/ISSUE-33.9/STEP-02_EXECUTION.md
Done quando: classificação registrada com evidência bruta.
Revisão: auto-approve (registro humano).
Dependências: STEP-01 aprovado.

### STEP-03 — Decisão de prosseguimento
Status: pending | Owner: executor | Type: reading
- Se CONTAMINADO: propor no report se prossegue como limite-superior ou se anonimiza o bundle primeiro (com estimativa de esforço); decisão final é do Marcelo, registrada aqui.
- Se LIMPO/PARCIAL: registrar e liberar STEP-04.
Editáveis: .ai/runs/ISSUE-33.9/STEP-03_EXECUTION.md
Done quando: decisão registrada.
Revisão: revisor obrigatório (é decisão de validade experimental).
Dependências: STEP-02 concluído.

### STEP-04 — Medições (Fase 3) — HUMANO
Status: pending | Owner: **Marcelo** | Type: validation
- Rodar as 2 configurações da SPEC via CLI (`--runs 5`/`--runs 3`, `--solver-model opus --judge-model sonnet`); commitar reports em `calibration/reports/`; anotar consumo de cota da assinatura (não custo em dinheiro) por run.
Editáveis: calibration/reports/; .ai/runs/ISSUE-33.9/STEP-04_EXECUTION.md
Done quando: reports JSON válidos commitados + custos anotados.
Revisão: auto-approve (registro humano).
Dependências: STEP-03 aprovado.

### STEP-05 — Análise e relatório (Fase 4)
Status: pending | Owner: executor | Type: documentation
- Julgar H1–H4 com os reports; auditar 1 run em detalhe (pistas usadas vs decisivas; RV_009); escrever `docs/CALIBRACAO_SOLVABILIDADE_2026-07.md` na estrutura da SPEC, incluindo a decisão sobre SM_003/prompts e a liberação (ou não) do passo seguinte.
Editáveis: docs/CALIBRACAO_SOLVABILIDADE_2026-07.md; .ai/runs/ISSUE-33.9/STEP-05_EXECUTION.md
Done quando: relatório completo com as 6 seções e decisão explícita.
Revisão: revisor obrigatório — conclusões sustentadas pelos números, sem inflar.
Dependências: STEP-04 concluído.

### STEP-06 — DOCS complementares
Status: pending | Owner: executor | Type: documentation
- INDICE ✅ (doc + calibration/), framework/05 ✅, ESTADO_ATUAL ✅, ROADMAP ✅.
Editáveis: docs/INDICE_DOCUMENTACAO.md; framework/05_CHECKLIST_SOLVABILIDADE.md; docs/ESTADO_ATUAL.md; docs/ROADMAP.md; .ai/runs/ISSUE-33.9/STEP-06_EXECUTION.md
Done quando: ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-05 aprovado.

### STEP-07 — VALIDATION + WRAP-UP
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`; `git diff --name-only`
Editáveis: .ai/runs/ISSUE-33.9/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.9.md (STATUS)
Done quando: sem regressão (nada de código mudou); STATUS: done.
Revisão: revisor obrigatório.
Dependências: STEP-06 aprovado.

## Auto-approve
STEP-02 e STEP-04 (registros humanos), documentation (STEP-06).

## Revisor obrigatório
STEP-01, STEP-03, STEP-05, STEP-07.

## Histórico
- STEP-00 gerado em chat; experimento humano+agente; desbloqueia medição dos casos existentes e a ISSUE-30.11 (blueprint novo com detetive real no circuito).

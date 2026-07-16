# ISSUE-33.8 — ClaudeCodeProvider (headless) + CLI de medição — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-09
NEXT_ACTION: none
REVIEW_STATUS: STEP-01–05 aprovados (spec-reviewer, com 3 overrides de orquestrador por
  falso-positivo de baseline); STEP-06 smoke real executado (operador humano), 5
  achados/bugs reais encontrados e corrigidos/registrados; STEP-07 docs auto-aprovado;
  STEP-08 validação auto-aprovada (suíte + lint + invariantes verdes)
LAST_COMPLETED_STEP: STEP-09
BLOCKER: none
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.8_SPEC.md`. Alvos: `generator/claude_code_provider.py` (novo), `generator/solvability_cli.py` (novo), ajuste do bloco reproducibility no meter/schema (CC_005), testes novos.

Pontos inegociáveis para o revisor: confinamento CC_001 (cwd tmp vazio + tools off) provado por teste; nenhum teste invoca o binário `claude`; CLI nunca escreve no bundle nem aceita gabarito como entrada. Agentes não executam o CLI contra provider real.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/llm_provider.py`, `generator/fake_provider.py`, `generator/solvability_meter.py` (bloco reproducibility da 33.5), `schemas/solvability_report.schema.yaml`, fixtures de bundle.
- Rodar `claude --help` e registrar: flag exata para desabilitar tools na versão instalada (CC_001), forma de passar prompt via stdin com `-p`, e se há canal system (CC_004).
- Registrar campos característicos de blueprint para o guard CC_008.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.8*.md; .ai/skills/tdd.md; generator/llm_provider.py; generator/fake_provider.py; generator/llm_blind_solver.py; generator/conclusion_judge.py; generator/solvability_meter.py; schemas/; tests/test_solvability_meter.py
Editáveis: .ai/runs/ISSUE-33.8/STEP-01_EXECUTION.md
Comandos: `claude --help` (somente help; nenhuma execução de prompt)
Proibido: editar código; executar `claude -p`.
Done quando: flags reais registradas; decisões CC_001/004 fixadas com a sintaxe da versão instalada.
Revisão: auto-approve (reading).
Dependências: nenhuma.

### STEP-02 — RED
Editáveis: tests/test_claude_code_provider.py; tests/test_solvability_cli.py; tests/test_solvability_meter.py (caso CC_005); .ai/runs/ISSUE-33.8/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_claude_code_provider.py tests/test_solvability_cli.py -q`
Done quando: os 6 grupos de casos da SPEC falham pelo motivo certo.
Revisão: revisor obrigatório — caso 1 (confinamento) deve verificar argv E cwd, não só um deles.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN (provider)
Editáveis: generator/claude_code_provider.py; .ai/runs/ISSUE-33.8/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_claude_code_provider.py -q`
Proibido: tocar CLI/meter (próximos steps).
Done quando: casos 1–4 (parte provider) verdes.
Revisão: revisor obrigatório — CC_003 completo, nunca exceção crua.
Dependências: STEP-02 aprovado.

### STEP-04 — GREEN (CC_005 no meter + CLI)
Editáveis: generator/solvability_meter.py; schemas/solvability_report.schema.yaml; generator/solvability_cli.py; .ai/runs/ISSUE-33.8/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_solvability_cli.py tests/test_solvability_meter.py -q`
Done quando: casos 4–5 verdes; schema estrito preservado.
Revisão: revisor obrigatório — CC_007 (hash do bundle) e CC_008 (guard de gabarito).
Dependências: STEP-03 aprovado.

### STEP-05 — REFACTOR
Editáveis: módulos e testes tocados; .ai/runs/ISSUE-33.8/STEP-05_EXECUTION.md
Comandos: `pytest tests/ -q -k "claude_code or solvability"`; `ruff check generator/ tests/`
Done quando: verde + ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-04 aprovado.

### STEP-06 — Smoke real (opcional, HUMANO)
Status: pending | Owner: **Marcelo** | Type: validation
- Uma única execução real de baixo custo para provar o plumbing: `claude -p "responda apenas OK" --model <solver-model>` manualmente e, se ok, o CLI com `--runs 1` contra um bundle de fixture (não o benchmark). Colar saídas no report.
- Se pular (direto para a 33.8), registrar a decisão.
Editáveis: .ai/runs/ISSUE-33.8/STEP-06_EXECUTION.md
Done quando: smoke registrado ou pulo justificado.
Revisão: auto-approve (registro humano).
Dependências: STEP-05 aprovado.

### STEP-07 — DOCS
Editáveis: docs/BLIND_SOLVER_HARNESS.md; docs/BLIND_CONTEXT_PROTOCOL.md; docs/ROADMAP.md; docs/ESTADO_ATUAL.md; CLAUDE.md; AGENTS.md; docs/GUIA_CODIGOS_ERROS.md; .ai/runs/ISSUE-33.8/STEP-07_EXECUTION.md
Done quando: ✅/⏭️ justificados, incluindo "agente não executa provider real" e a limitação de temperatura.
Revisão: auto-approve.
Dependências: STEP-06 concluído.

### STEP-08 — VALIDATION
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`; grep do caso 6 (nenhum teste invoca o binário)
Editáveis: .ai/runs/ISSUE-33.8/STEP-08_EXECUTION.md
Done quando: sem regressão; CI verde.
Revisão: revisor obrigatório.
Dependências: STEP-07 aprovado.

### STEP-09 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.8/STEP-09_EXECUTION.md; .ai/issues/ISSUE-33.8.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-08 aprovado.

## Auto-approve
reading (STEP-01), STEP-06 (registro humano), documentation (STEP-07), wrap-up (STEP-09).

## Revisor obrigatório
red (STEP-02), green (STEP-03, STEP-04), refactor (STEP-05), validation (STEP-08).

## Histórico
- STEP-00 gerado em chat; substitui a versão AnthropicProvider por decisão de produto (sem API key; headless via assinatura).

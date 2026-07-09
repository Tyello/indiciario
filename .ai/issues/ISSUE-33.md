# ISSUE-33 — LLM Blind Solver Adapter — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-08
NEXT_ACTION: none
REVIEW_STATUS: STEP-08 concluído — todos os steps aprovados
LAST_COMPLETED_STEP: STEP-08
BLOCKER: none
```

## Contexto

Skill: `tdd` — código novo com contrato de segurança (protocolo cego); RED antes de GREEN.

Spec: `.ai/issues/ISSUE-33_SPEC.md`. Alvos: `generator/llm_blind_solver.py` (novo), `generator/prompts/blind_solver_v1.md` (novo), `tests/test_llm_blind_solver.py` (novo), `generator/pipeline_runner.py` (parâmetro opt-in).

Regra inegociável desta issue: **o prompt do solver só pode conter conteúdo do bundle** (LS_001). O revisor deve tratar qualquer vazamento como bloqueante crítico.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/blind_solver_harness.py` (Protocol `BlindSolver`, `BlindSolverContext`, `BlindSolverReport`), `schemas/blind_solver_report.schema.yaml`, `generator/blind_solver_report_validator.py`, `generator/pipeline_runner.py` (ponto de injeção do solver), fixtures de bundle em `tests/test_blind_solver_harness.py`.
- Registrar no report: assinatura exata do Protocol, campos do report, ponto de injeção no pipeline, fixtures reutilizáveis.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33*.md; .ai/skills/tdd.md; docs/BLIND_SOLVER_HARNESS.md; docs/BLIND_CONTEXT_PROTOCOL.md; generator/blind_solver_harness.py; generator/blind_solver_report_validator.py; generator/pipeline_runner.py; generator/llm_provider.py; generator/fake_provider.py; schemas/blind_solver_report.schema.yaml; tests/test_blind_solver_harness.py
Editáveis: .ai/runs/ISSUE-33/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar código.
Done quando: report mapeia Protocol, schema e fixtures com nomes reais.
Revisão: auto-approve (reading).
Dependências: ISSUE-31 done; ISSUE-32 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever `tests/test_llm_blind_solver.py` cobrindo os 8 casos da SPEC, incluindo o teste-sentinela do protocolo cego (caso 2) e o teste de regressão do pipeline (caso 8).
- Confirmar falha por módulo inexistente.
Editáveis: tests/test_llm_blind_solver.py; .ai/runs/ISSUE-33/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py -q`
Proibido: criar módulos de produção.
Done quando: testes falham pelo motivo certo.
Revisão: revisor obrigatório — confirmar que o teste-sentinela de fato planta conteúdo fora do bundle e o procura no prompt.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN (adapter + prompt)
Status: pending | Owner: executor | Type: green
- Criar `generator/prompts/blind_solver_v1.md` conforme conteúdo mínimo da SPEC.
- Implementar `generator/llm_blind_solver.py` (LS_001–LS_005).
Editáveis: generator/llm_blind_solver.py; generator/prompts/blind_solver_v1.md; .ai/runs/ISSUE-33/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py -q -k "not pipeline"`
Proibido: tocar `pipeline_runner.py` (próximo step).
Done quando: casos 1–7 verdes.
Revisão: revisor obrigatório — foco em LS_001 e LS_003 (ids nunca confiados ao modelo).
Dependências: STEP-02 aprovado.

### STEP-04 — GREEN (integração opt-in no pipeline)
Status: pending | Owner: executor | Type: green
- Adicionar parâmetro `solver: BlindSolver | None = None` ao `pipeline_runner.py`; `None` mantém o stub.
Editáveis: generator/pipeline_runner.py; .ai/runs/ISSUE-33/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py tests/test_aurora_pipeline.py -q`
Done quando: caso 8 verde e testes existentes do pipeline sem regressão.
Revisão: revisor obrigatório — default preservado é o critério central.
Dependências: STEP-03 aprovado.

### STEP-05 — REFACTOR
Status: pending | Owner: executor | Type: refactor
- Limpar sem mudar comportamento; docstrings com a regra de isolamento.
Editáveis: generator/llm_blind_solver.py; tests/test_llm_blind_solver.py; .ai/runs/ISSUE-33/STEP-05_EXECUTION.md
Comandos: `pytest tests/test_llm_blind_solver.py -q`; `ruff check generator/llm_blind_solver.py tests/test_llm_blind_solver.py`
Done quando: suite verde, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-04 aprovado.

### STEP-06 — DOCS
Status: pending | Owner: executor | Type: documentation
- Aplicar impacto documental da SPEC: `docs/BLIND_SOLVER_HARNESS.md` ✅, `docs/ROADMAP.md` ✅, `docs/ESTADO_ATUAL.md` ✅, `docs/BLIND_CONTEXT_PROTOCOL.md` ✅, `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️.
Editáveis: docs/BLIND_SOLVER_HARNESS.md; docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/BLIND_CONTEXT_PROTOCOL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-33/STEP-06_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-05 aprovado.

### STEP-07 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo; confirmar que nenhum teste abre rede (buscar por uso de provider real: `grep -rn "anthropic\|api_key\|https://" generator/llm_blind_solver.py tests/test_llm_blind_solver.py`).
Editáveis: .ai/runs/ISSUE-33/STEP-07_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`; grep acima
Done quando: sem regressão; grep sem ocorrências de provider real.
Revisão: revisor obrigatório.
Dependências: STEP-06 aprovado.

### STEP-08 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-33/STEP-08_EXECUTION.md; .ai/issues/ISSUE-33.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-07 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-06), wrap-up (STEP-08).

## Revisor obrigatório
red (STEP-02), green (STEP-03, STEP-04), refactor (STEP-05), validation (STEP-07).

## Histórico
- STEP-00 gerado em chat; bloqueada até merge das ISSUE-31 e ISSUE-32.

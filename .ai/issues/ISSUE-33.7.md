# ISSUE-33.7 — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: STEP-07
BLOCKER: none
```

## Contexto

Skill: `tdd`. Spec: `.ai/issues/ISSUE-33.7_SPEC.md`. Alvos: `generator/narrative_reviewer.py`,
`generator/evidence_reviewer.py`, `generator/pipeline_runner.py` (`_run_reviews`),
`tests/test_pipeline_runner.py`, `tests/test_narrative_reviewer.py`,
`tests/test_evidence_reviewer.py`.

Fecha a dívida registrada em `.ai/runs/ISSUE-33.3/STEP-06_EXECUTION.md`: `_now_iso()`
hardcoded em `review_narrative`/`review_evidence` quebra o determinismo do pipeline quando
as duas chamadas do teste cruzam a fronteira de segundo. Ponto de atenção do revisor:
parâmetro novo tem que ser opcional com default `None` → `_now_iso()`, para não quebrar
chamadores existentes fora do `pipeline_runner` (NC_001).

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/narrative_reviewer.py` (assinatura de `review_narrative`, uso de
  `_now_iso`), `generator/evidence_reviewer.py` (idem `review_evidence`),
  `generator/pipeline_runner.py::_run_reviews` (como created_at do run está disponível
  nesse ponto), `tests/test_pipeline_runner.py` (teste de determinismo existente).
- Grep por outros chamadores de `review_narrative`/`review_evidence` no repo (confirmar
  fora de escopo declarado: nenhum outro consumidor).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.7*.md;
.ai/skills/tdd.md; .ai/runs/ISSUE-33.3/STEP-06_EXECUTION.md; generator/narrative_reviewer.py;
generator/evidence_reviewer.py; generator/pipeline_runner.py; tests/test_pipeline_runner.py;
tests/test_narrative_reviewer.py; tests/test_evidence_reviewer.py
Editáveis: .ai/runs/ISSUE-33.7/STEP-01_EXECUTION.md
Comandos: `grep -rn "review_narrative(\|review_evidence(" .`
Proibido: editar código.
Done quando: pontos de mudança mapeados + confirmação de chamadores únicos registrados.
Revisão: auto-approve (reading).

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever os 5 casos da SPEC (determinismo primeiro).
Editáveis: tests/test_pipeline_runner.py; tests/test_narrative_reviewer.py;
tests/test_evidence_reviewer.py; .ai/runs/ISSUE-33.7/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_pipeline_runner.py tests/test_narrative_reviewer.py tests/test_evidence_reviewer.py -q`
Proibido: tocar produção.
Done quando: novos testes falham pelo motivo certo; antigos verdes.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar NC_001–NC_003.
Editáveis: generator/narrative_reviewer.py; generator/evidence_reviewer.py;
generator/pipeline_runner.py; .ai/runs/ISSUE-33.7/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_pipeline_runner.py tests/test_narrative_reviewer.py tests/test_evidence_reviewer.py -q`
Done quando: 5 casos verdes.
Revisão: revisor obrigatório — parâmetro novo é opt-in (default preserva comportamento atual).
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
Editáveis: generator/narrative_reviewer.py; generator/evidence_reviewer.py;
generator/pipeline_runner.py; tests/; .ai/runs/ISSUE-33.7/STEP-04_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: verde + ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- Impacto da SPEC: BLIND_SOLVER_HARNESS ✅, ESTADO_ATUAL ✅, INDICE ✅/⏭️.
Editáveis: docs/BLIND_SOLVER_HARNESS.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md;
.ai/runs/ISSUE-33.7/STEP-05_EXECUTION.md
Done quando: ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
Comandos: `pytest tests/ -q` (rodar ao menos 3x seguidas para checar flake residual);
`ruff check generator/ scripts/ tests/`
Editáveis: .ai/runs/ISSUE-33.7/STEP-06_EXECUTION.md
Done quando: sem regressão; sem flake de determinismo em 3 rodadas.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Editáveis: .ai/runs/ISSUE-33.7/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.7.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir da dívida registrada em
  `.ai/runs/ISSUE-33.3/STEP-06_EXECUTION.md` (flake de determinismo por `_now_iso()`).

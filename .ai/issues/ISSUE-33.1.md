# ISSUE-33.1 — Conclusion Judge — passos

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-01
NEXT_ACTION: aguardar merge da ISSUE-33
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: ISSUE-33 (consome BlindSolverReport real e prompts versionados)
```

## Contexto

Skill: `tdd` — código novo + schema novo; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-33.1_SPEC.md`. Alvos: `generator/conclusion_judge.py` (novo), `generator/prompts/conclusion_judge_v1.md` (novo), `schemas/judge_verdict.schema.yaml` (novo), `tests/test_conclusion_judge.py` (novo).

Ponto de atenção para o revisor: a **classificação nunca é confiada ao modelo** (CJ_004 é derivação em Python puro); o modelo só julga `met` por afirmação.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/gate_evaluator.py` (ExpectedConclusion, build_gate_evaluation, GE_004), `schemas/gate_evaluation.schema.yaml`, `generator/llm_blind_solver.py` (padrão de prompt versionado + repair), `schemas/blind_solver_report.schema.yaml`, exemplos de gabarito em `examples/caso_canonico_iniciante.json` (`solucao_em_5_frases`, `solucao_final`).
- Registrar no report: forma exata de `ExpectedConclusion` do gate e o padrão de schema YAML do repo.
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.1*.md; .ai/skills/tdd.md; docs/BLIND_SOLVER_HARNESS.md; generator/gate_evaluator.py; generator/llm_blind_solver.py; generator/llm_provider.py; generator/fake_provider.py; schemas/gate_evaluation.schema.yaml; schemas/blind_solver_report.schema.yaml; examples/caso_canonico_iniciante.json
Editáveis: .ai/runs/ISSUE-33.1/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar código.
Done quando: report mapeia os contratos consumidos com nomes reais.
Revisão: auto-approve (reading).
Dependências: ISSUE-33 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever `tests/test_conclusion_judge.py` cobrindo os 8 casos da SPEC (caso 3 sem provider; caso 6 com sentinela).
- Confirmar falha por módulo/schema inexistente.
Editáveis: tests/test_conclusion_judge.py; .ai/runs/ISSUE-33.1/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_conclusion_judge.py -q`
Proibido: criar módulos de produção.
Done quando: testes falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Criar `schemas/judge_verdict.schema.yaml` (`additionalProperties: false`), `generator/prompts/conclusion_judge_v1.md` e `generator/conclusion_judge.py` (CJ_001–CJ_005, derivação com precedência).
Editáveis: generator/conclusion_judge.py; generator/prompts/conclusion_judge_v1.md; schemas/judge_verdict.schema.yaml; .ai/runs/ISSUE-33.1/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_conclusion_judge.py -q`
Proibido: alterar gate_evaluator, harness ou solver.
Done quando: suite do arquivo passa 100%.
Revisão: revisor obrigatório — foco em CJ_004 (derivação pura, precedência) e CJ_005.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
- Limpar sem mudar comportamento; extrair helpers comuns com o solver adapter se houver duplicação de parsing/repair (sem mover contratos).
Editáveis: generator/conclusion_judge.py; generator/llm_blind_solver.py (somente extração de helper compartilhado, se aplicável); tests/test_conclusion_judge.py; .ai/runs/ISSUE-33.1/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_conclusion_judge.py tests/test_llm_blind_solver.py -q`; `ruff check generator/ tests/test_conclusion_judge.py`
Done quando: suites verdes, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- Aplicar impacto documental da SPEC: `docs/BLIND_SOLVER_HARNESS.md` ✅, `framework/05_CHECKLIST_SOLVABILIDADE.md` ✅, `docs/ROADMAP.md` ✅, `docs/ESTADO_ATUAL.md` ✅, `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️.
Editáveis: docs/BLIND_SOLVER_HARNESS.md; framework/05_CHECKLIST_SOLVABILIDADE.md; docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-33.1/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados. O texto no framework/05 deve deixar explícito: juiz automatizado é complementar, playtest humano continua sendo o veredito.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo; validar schema novo carregável pelo `schema_loader`.
Editáveis: .ai/runs/ISSUE-33.1/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: sem regressão; falhas pré-existentes listadas.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-33.1/STEP-07_EXECUTION.md; .ai/issues/ISSUE-33.1.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat; bloqueada até merge da ISSUE-33.

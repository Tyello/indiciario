# ISSUE-31 — Provider Interface para LLM — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: STEP-07 aprovado
LAST_COMPLETED_STEP: STEP-07
BLOCKER: none
```

## Contexto

Skill: `tdd` — módulo novo de código com contrato testável; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-31_SPEC.md`. Alvo: `generator/llm_provider.py` (novo) + `tests/test_llm_provider.py` (novo). Nenhum consumidor existente é alterado nesta issue.

Origem: `docs/ROADMAP.md` — fase Provider (ISSUE-31–34). Esta é a fundação: ISSUE-32 (fake provider) e ISSUE-33 (solver adapter) dependem dela.

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `docs/ROADMAP.md` (seção 31–34), `generator/blind_solver_harness.py` (padrão de Protocol + dataclasses frozen já usado no repo) e `generator/blind_solve_run_record.py` (padrão de `validate_* -> list[str]`).
- Confirmar no report que nenhum módulo existente declara `LLMProvider`/`ProviderRequest` (evitar duplicação).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-31*.md; .ai/skills/tdd.md; docs/ROADMAP.md; generator/blind_solver_harness.py; generator/blind_solve_run_record.py
Editáveis: .ai/runs/ISSUE-31/STEP-01_EXECUTION.md
Comandos: `grep -rn "LLMProvider\|ProviderRequest" generator/ tests/`
Proibido: editar código.
Done quando: report confirma ausência de duplicação e cita os padrões de referência.
Revisão: auto-approve (reading).
Dependências: nenhuma.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever `tests/test_llm_provider.py` cobrindo os 8 casos da SPEC.
- Rodar e confirmar falha por `ModuleNotFoundError`/`ImportError` (módulo ainda não existe).
Editáveis: tests/test_llm_provider.py; .ai/runs/ISSUE-31/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_llm_provider.py -q`
Proibido: criar `generator/llm_provider.py`.
Done quando: todos os testes novos falham pelo motivo certo, registrado no report.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar `generator/llm_provider.py` conforme contrato da SPEC (dataclasses frozen, Protocol runtime_checkable, erros, `validate_provider_request` com PV_001–PV_004).
Editáveis: generator/llm_provider.py; .ai/runs/ISSUE-31/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_llm_provider.py -q`
Proibido: tocar em qualquer outro módulo do generator.
Done quando: suite do arquivo passa 100%.
Revisão: revisor obrigatório — fidelidade ao contrato (nomes, códigos PV, imutabilidade).
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
- Limpar sem mudar comportamento; docstrings honestas ("não chama LLM, não acessa rede").
Editáveis: generator/llm_provider.py; tests/test_llm_provider.py; .ai/runs/ISSUE-31/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_llm_provider.py -q`; `ruff check generator/llm_provider.py tests/test_llm_provider.py`
Done quando: suite verde, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- Aplicar impacto documental da SPEC: `docs/ROADMAP.md` ✅, `docs/ESTADO_ATUAL.md` ✅, `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️ com justificativa.
Editáveis: docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-31/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo nos arquivos tocados.
Editáveis: .ai/runs/ISSUE-31/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: sem regressão; falhas pré-existentes (se houver) listadas explicitamente.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-31/STEP-07_EXECUTION.md; .ai/issues/ISSUE-31.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat; STEP-01 pronto.

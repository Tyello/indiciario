# ISSUE-32 — Fake Provider para testes determinísticos — passos

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-01
NEXT_ACTION: aguardar merge da ISSUE-31
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: ISSUE-31 (importa LLMProvider/ProviderRequest/erros)
```

## Contexto

Skill: `tdd` — módulo novo de código; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-32_SPEC.md`. Alvo: `generator/fake_provider.py` (novo) + `tests/test_fake_provider.py` (novo). Depende da ISSUE-31 mergeada (importa contrato de lá; proibido redeclarar dataclasses).

## Steps

### STEP-01 — Leitura
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `generator/llm_provider.py` (contrato real mergeado) e `tests/test_llm_provider.py`.
- Confirmar no report os nomes exatos importáveis (dataclasses, erros, validador).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-32*.md; .ai/skills/tdd.md; generator/llm_provider.py; tests/test_llm_provider.py
Editáveis: .ai/runs/ISSUE-32/STEP-01_EXECUTION.md
Comandos: nenhum
Proibido: editar código.
Done quando: report lista os símbolos importados da ISSUE-31.
Revisão: auto-approve (reading).
Dependências: ISSUE-31 done.

### STEP-02 — RED
Status: pending | Owner: executor | Type: red
- Escrever `tests/test_fake_provider.py` cobrindo os 7 casos da SPEC.
- Confirmar falha por módulo inexistente.
Editáveis: tests/test_fake_provider.py; .ai/runs/ISSUE-32/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`
Proibido: criar `generator/fake_provider.py`.
Done quando: testes falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: pending | Owner: executor | Type: green
- Implementar `generator/fake_provider.py` conforme contrato (FP_001–FP_004, consumo em ordem, `calls` imutável).
Editáveis: generator/fake_provider.py; .ai/runs/ISSUE-32/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`
Proibido: alterar `generator/llm_provider.py`.
Done quando: suite do arquivo passa 100%.
Revisão: revisor obrigatório — verificar que nada foi redeclarado (import da 31) e que FP_001 não consome roteiro.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: pending | Owner: executor | Type: refactor
- Limpar sem mudar comportamento.
Editáveis: generator/fake_provider.py; tests/test_fake_provider.py; .ai/runs/ISSUE-32/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`; `ruff check generator/fake_provider.py tests/test_fake_provider.py`
Done quando: suite verde, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: pending | Owner: executor | Type: documentation
- `docs/ROADMAP.md` ✅; `docs/ESTADO_ATUAL.md` ✅; `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️ com justificativa.
Editáveis: docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-32/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo.
Editáveis: .ai/runs/ISSUE-32/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: sem regressão; falhas pré-existentes listadas.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos alterados; resolver impacto documental; STATUS: done.
Editáveis: .ai/runs/ISSUE-32/STEP-07_EXECUTION.md; .ai/issues/ISSUE-32.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat; bloqueada até merge da ISSUE-31.

# ISSUE-32 — Fake Provider para testes determinísticos — passos

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

Skill: `tdd` — módulo novo de código; RED antes de GREEN.

Spec: `.ai/issues/ISSUE-32_SPEC.md`. Alvo: `generator/fake_provider.py` (novo) + `tests/test_fake_provider.py` (novo). Depende da ISSUE-31 mergeada (importa contrato de lá; proibido redeclarar dataclasses).

## Steps

### STEP-01 — Leitura
Status: done | Owner: executor | Type: reading
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
Status: done | Owner: executor | Type: red
- Escrever `tests/test_fake_provider.py` cobrindo os 7 casos da SPEC.
- Confirmar falha por módulo inexistente.
Editáveis: tests/test_fake_provider.py; .ai/runs/ISSUE-32/STEP-02_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`
Proibido: criar `generator/fake_provider.py`.
Done quando: testes falham pelo motivo certo.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — GREEN
Status: done | Owner: executor | Type: green
- Implementar `generator/fake_provider.py` conforme contrato (FP_001–FP_004, consumo em ordem, `calls` imutável).
Editáveis: generator/fake_provider.py; .ai/runs/ISSUE-32/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`
Proibido: alterar `generator/llm_provider.py`.
Done quando: suite do arquivo passa 100%.
Revisão: revisor obrigatório — verificar que nada foi redeclarado (import da 31) e que FP_001 não consome roteiro.
Dependências: STEP-02 aprovado.

### STEP-04 — REFACTOR
Status: done | Owner: executor | Type: refactor
- Limpar sem mudar comportamento.
Editáveis: generator/fake_provider.py; tests/test_fake_provider.py; .ai/runs/ISSUE-32/STEP-04_EXECUTION.md
Comandos: `pytest tests/test_fake_provider.py -q`; `ruff check generator/fake_provider.py tests/test_fake_provider.py`
Done quando: suite verde, ruff limpo.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS
Status: done | Owner: executor | Type: documentation
- `docs/ROADMAP.md` ✅; `docs/ESTADO_ATUAL.md` ✅; `docs/INDICE_DOCUMENTACAO.md` ✅/⏭️ com justificativa.
Editáveis: docs/ROADMAP.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-32/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅ atualizados; ⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: done | Owner: executor | Type: validation
- `pytest tests/ -q` sem regressão; `ruff` limpo.
Editáveis: .ai/runs/ISSUE-32/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ tests/`
Done quando: sem regressão; falhas pré-existentes listadas.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: done | Owner: executor | Type: wrap-up
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
- ISSUE-31 concluída (`STATUS: done`) — bloqueio removido, símbolos confirmados em `generator/llm_provider.py`: `LLMProvider`, `ProviderRequest`, `ProviderResponse`, `ProviderError`, `ProviderResponseError`, `ProviderTransportError`, `validate_provider_request`.
- STEP-02/03: `tests/test_fake_provider.py` (7 casos) e `generator/fake_provider.py` já existiam no working tree ao retomar a issue; verificado que cobrem FP_001–FP_004 e que `FakeProvider` não redeclara dataclasses da ISSUE-31 (importa diretamente).
- STEP-04: `ruff check` acusou `LLMProvider` importado sem uso em `generator/fake_provider.py` (Protocol satisfeito estruturalmente, sem necessidade de import nominal); removido. `ruff check generator/fake_provider.py tests/test_fake_provider.py` limpo após o ajuste.
- STEP-05: `docs/ROADMAP.md` e `docs/ESTADO_ATUAL.md` atualizados marcando ISSUE-32 concluída. `docs/INDICE_DOCUMENTACAO.md` sem entrada nova — dispensado: módulo é suporte de teste interno (paralelo à ISSUE-31, que também não gerou entrada no índice), não documentação de produto/usuário.
- STEP-06: `pytest tests/test_fake_provider.py -q` → 7 passed. `pytest tests/ -q` → 1463 passed, 3 skipped, 5 failed; as 5 falhas são pré-existentes e não relacionadas (erro de symlink no Windows por falta de privilégio — `tests/test_blind_bundle_generator.py`, `tests/test_blind_bundle_leak_checker.py`, `tests/test_blind_bundle_sanitizer.py`), confirmado como ambiente, não regressão desta issue.
- STEP-07: arquivos alterados — `generator/fake_provider.py` (novo, ajustado), `tests/test_fake_provider.py` (novo), `docs/ROADMAP.md`, `docs/ESTADO_ATUAL.md`, `.ai/issues/ISSUE-32.md`. Impacto documental resolvido. `STATUS: done`.

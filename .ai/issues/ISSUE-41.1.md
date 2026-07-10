# ISSUE-41.1 — CI verde de novo — passos

## Estado

```
STATUS: ready
CURRENT_STEP: STEP-01
NEXT_ACTION: executor roda STEP-01
REVIEW_STATUS: n/a
LAST_COMPLETED_STEP: none
BLOCKER: none
```

## Contexto

Skill: `tdd` — correção guiada por evidência de lint/CI; o "RED" é o estado quebrado atual, registrado antes de corrigir.

Spec: `.ai/issues/ISSUE-41.1_SPEC.md`. Alvos: `tests/conftest.py`, `tests/test_blind_solve_run_record.py`, 4 arquivos com F401, 3 arquivos de teste de symlink, entrypoint do validator, `CLAUDE.md`, `AGENTS.md`, `.gitignore`.

Prioridade máxima do lote (TOP-1 da auditoria): destrava a prova automatizada de todo o resto.

## Steps

### STEP-01 — Leitura + baseline do vermelho
Status: pending | Owner: executor | Type: reading
- Ler SPEC, `.github/workflows/ci.yml`, `tests/test_blind_solve_run_record.py` (mapa das fixtures importadas), os 4 arquivos com F401, os 3 arquivos de symlink e `tests/test_learning_ledger_cli.py:200-215` (padrão de skip).
- Registrar baseline: saída completa de `ruff check generator/ scripts/ tests/` e lista dos 5 testes de symlink falhando (se em Windows).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-41.1*.md; .ai/skills/tdd.md; docs/AUDITORIA_FABLE_2026-07.md; .github/workflows/ci.yml; tests/
Editáveis: .ai/runs/ISSUE-41.1/STEP-01_EXECUTION.md
Comandos: `ruff check generator/ scripts/ tests/`; `pytest tests/test_blind_bundle_generator.py tests/test_blind_bundle_leak_checker.py tests/test_blind_bundle_sanitizer.py -q`
Proibido: editar código.
Done quando: baseline registrado com números exatos.
Revisão: auto-approve (reading).
Dependências: nenhuma.

### STEP-02 — Fixtures para conftest (CI_001) + F401 (CI_002)
Status: pending | Owner: executor | Type: green
- Migrar fixtures compartilhadas para conftest; remover imports com noqa; remover os 4 F401.
Editáveis: tests/conftest.py; tests/test_blind_solve_run_record.py; tests/test_accessibility_reviewer.py; tests/test_gate_font_fidelity.py; tests/test_pipeline_runner.py; tests/test_quality_comparative_reviewer.py; .ai/runs/ISSUE-41.1/STEP-02_EXECUTION.md
Comandos: `ruff check tests/`; `pytest tests/test_blind_solve_run_record.py tests/test_accessibility_reviewer.py tests/test_gate_font_fidelity.py tests/test_pipeline_runner.py tests/test_quality_comparative_reviewer.py -q`
Done quando: zero F811/F401; arquivos tocados 100% verdes.
Revisão: revisor obrigatório — confirmar que nenhuma fixture mudou de comportamento, só de local.
Dependências: STEP-01 aprovado.

### STEP-03 — Skip-guard de symlink (CI_003)
Status: pending | Owner: executor | Type: green
- Aplicar o padrão do learning_ledger_cli nos 5 testes: try/except OSError na criação do symlink → pytest.skip.
Editáveis: tests/test_blind_bundle_generator.py; tests/test_blind_bundle_leak_checker.py; tests/test_blind_bundle_sanitizer.py; .ai/runs/ISSUE-41.1/STEP-03_EXECUTION.md
Comandos: `pytest tests/test_blind_bundle_generator.py tests/test_blind_bundle_leak_checker.py tests/test_blind_bundle_sanitizer.py -q -rs`
Done quando: em Windows os 5 aparecem como SKIPPED com motivo; nenhuma asserção do comportamento sob teste foi enfraquecida.
Revisão: revisor obrigatório — o skip cobre SÓ a criação do symlink.
Dependências: STEP-02 aprovado.

### STEP-04 — Encoding do CLI (CI_005) + worktree (CI_006)
Status: pending | Owner: executor | Type: green
- Adicionar reconfigure UTF-8 guardado no entrypoint do validator; remover worktree órfão; garantir `.gitignore`.
Editáveis: generator/validator.py (ou módulo de entrypoint real, confirmar no STEP-01); .gitignore; .ai/runs/ISSUE-41.1/STEP-04_EXECUTION.md
Comandos: `python -m generator.validator examples/caso_canonico_iniciante.json --strict`; `git worktree prune`; `git worktree list`
Done quando: saída do CLI sem mojibake; `git worktree list` só com o principal; diretório órfão ausente.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — DOCS (CI_004 + impacto)
Status: pending | Owner: executor | Type: documentation
- CLAUDE.md ✅ e AGENTS.md ✅ (comando de lint completo); docs/ESTADO_ATUAL.md ✅ (uma linha, CI restabelecida); docs/INDICE_DOCUMENTACAO.md ✅/⏭️.
Editáveis: CLAUDE.md; AGENTS.md; docs/ESTADO_ATUAL.md; docs/INDICE_DOCUMENTACAO.md; .ai/runs/ISSUE-41.1/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: itens ✅/⏭️ justificados.
Revisão: auto-approve.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION
Status: pending | Owner: executor | Type: validation
- Suite completa + lint completo + push do branch e verificação do run de CI real.
Editáveis: .ai/runs/ISSUE-41.1/STEP-06_EXECUTION.md
Comandos: `pytest tests/ -q`; `ruff check generator/ scripts/ tests/`; `gh run watch` (ou link do run)
Done quando: suite verde local (com SKIPs de symlink justificados), lint zero, CI do branch verde com steps Tests/validators executados.
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

### STEP-07 — WRAP-UP
Status: pending | Owner: executor | Type: wrap-up
- Listar arquivos; impacto documental; link do run de CI verde; STATUS: done.
Editáveis: .ai/runs/ISSUE-41.1/STEP-07_EXECUTION.md; .ai/issues/ISSUE-41.1.md (STATUS)
Comandos: `git diff --name-only`
Dependências: STEP-06 aprovado.

## Auto-approve
reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório
green (STEP-02, 03, 04), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat a partir de docs/AUDITORIA_FABLE_2026-07.md (BUG-01/02, RISCO-03, DIV-08, Melhorias 1/4/5).

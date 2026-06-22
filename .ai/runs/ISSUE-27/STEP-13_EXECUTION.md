# Execution Report — ISSUE-27 STEP-13

STEP: STEP-13
STEP_TYPE: validation
EXECUTION_STATUS: completed

## Objetivo
Rodar suite completa e checagens finais; confirmar ausencia de regressao.

## Arquivos lidos
- .ai/issues/ISSUE-27.md
- .ai/issues/ISSUE-27_SPEC.md (referenciado; nao lido — fora de necessidade)

## Arquivos alterados
- .ai/runs/ISSUE-27/STEP-13_EXECUTION.md (este report)
- .ai/issues/ISSUE-27.md (somente campos de estado/historico permitidos)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/ -q` — 1248 passed, 3 skipped, 5 failed in 179.15s
- `.venv/Scripts/python.exe -m ruff check generator/run_manifest.py` — All checks passed!
- `git diff --check` — exit 0 (apenas warning CRLF em .ai/issues/ISSUE-27.md; sem erro de whitespace)
- `git status --short` — ver abaixo
- `git diff --stat` — apenas .ai/issues/ISSUE-27.md (547 insertions, 18 deletions)

## Contagem exata
- passed: 1248
- skipped: 3
- failed: 5

Baseline STEP-02: 1192 passed, 3 skipped, 5 failed.
Esperado: 1192 + 55 = 1247+. Obtido 1248 passed (56 novos testes ISSUE-27). Sem regressao.

## Lista de failed (5)
- tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed
- tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails
- tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails
- tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail
- tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail

Causa: OSError [WinError 1314] "O cliente nao tem o privilegio necessario" em `symlink_to`. Pre-existentes Windows (symlink privilege). Mesmos 5 da baseline STEP-02. Nenhuma nova regressao.

## git status --short
```
 M .ai/issues/ISSUE-27.md
?? .ai/runs/ISSUE-27/
?? generator/run_manifest.py
?? schemas/run_manifest.schema.yaml
?? tests/fixtures/run_manifest/
?? tests/test_run_manifest.py
?? tests/test_run_manifest_schema.py
```

Confirmacao: unico arquivo EXISTENTE modificado e `.ai/issues/ISSUE-27.md` (state file da issue, permitido). Demais sao net-new de ISSUE-27 (generator/run_manifest.py, schemas/run_manifest.schema.yaml, tests/fixtures/run_manifest/, tests/test_run_manifest.py, tests/test_run_manifest_schema.py) + .ai/runs/ISSUE-27/. Nenhum arquivo de produto/codigo/teste existente alterado fora do escopo.

## Evidencia de aderencia ao tipo (validation)
- Apenas comandos permitidos do STEP-13 executados.
- Nenhuma falha corrigida; nenhum codigo ou teste alterado.
- Resultados exatos registrados.

## Divergencias
- nenhuma

## Observacoes para revisao
- 5 failed sao os mesmos symlink WinError 1314 da baseline; ambiente Windows sem privilegio de symlink. Sem regressao.
- 56 testes novos (1248 - 1192) cobrindo schema + semantica + build de run_manifest.

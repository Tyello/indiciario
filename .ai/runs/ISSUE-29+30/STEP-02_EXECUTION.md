# STEP-02 — Baseline — Execution Report

ISSUE: ISSUE-29+30
STEP: STEP-02 (Baseline)
Data: 2026-06-23

## Comando executado

```
python -m pytest tests/ -q
```
(via `python3` no Git Bash, Windows)

## Resultado

```
6 failed, 1327 passed, 3 skipped in 197.34s (0:03:17)
```

## Falhas detalhadas

1. `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
   - `OSError: [WinError 1314] O cliente não tem o privilégio necessário` ao chamar `Path.symlink_to`.
   - Causa: ambiente Windows sem privilégio de criação de symlink (precisa "Create symbolic links" / modo Administrador / Developer Mode). Não relacionado ao código da issue.

2. `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
   - Mesmo `WinError 1314` ao criar symlink de teste.

3. `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
   - Mesmo `WinError 1314`.

4. `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
   - Mesmo `WinError 1314`.

5. `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
   - Mesmo `WinError 1314`.

6. `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
   - `AssertionError`: `result_a.manifest != result_b.manifest` — divergência no `sha256` do artifact `stage: evidence_review` entre duas execuções do pipeline com o mesmo `created_at`.
   - Indica não-determinismo real no pipeline (não é problema de ambiente). Pré-existente, não introduzido por esta sessão.

## Classificação

- 5 falhas: ambiente (privilégio de symlink no Windows) — não bloqueante, não relacionado à issue.
- 1 falha: não-determinismo pré-existente no `run_pipeline` (`test_run_pipeline_is_deterministic_with_same_created_at`) — falha real, pré-existente, registrada como baseline conhecido.

## Estatísticas

- Total: 1336 testes coletados
- Passed: 1327
- Failed: 6
- Skipped: 3
- Tempo: 197.34s (0:03:17)

## Decisão

Baseline registrado. Falhas são pré-existentes (ambiente Windows + não-determinismo conhecido), não bloqueiam avanço do fluxo. Avançar para STEP-03 conforme protocolo de baseline (low-risk, auto-approve).

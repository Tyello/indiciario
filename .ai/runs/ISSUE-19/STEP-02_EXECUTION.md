# Execution Report — ISSUE-19 STEP-02

STEP: STEP-02
STEP_TYPE: baseline
EXECUTION_STATUS: completed

## Arquivos lidos
- `.ai/issues/ISSUE-19+20.md`

## Arquivos alterados
- nenhum

## Comandos executados
- `pytest tests/test_blind_solve_run_record.py -q` — 22 passed in 5.82s
- `pytest tests/test_blind_solve_run_record_schema.py -q` — 16 passed in 0.70s
- `pytest tests/ -q` — 5 failed, 982 passed, 3 skipped in 179.98s

Nota: comandos rodados via interpretador do projeto `.venv/Scripts/python.exe -m pytest ...` (ambiente Windows).

## Resultado
- `test_blind_solve_run_record.py`: 22 passed. Verde.
- `test_blind_solve_run_record_schema.py`: 16 passed. Verde.
- Suíte completa `tests/`: 982 passed, 3 skipped. 5 failed conhecidos.
- 5 falhas são limitação Windows (symlink exige privilégio admin), documentadas em memory `test-environment.md`, não são regressão:
  - `test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
  - `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
  - `test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
  - `test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
  - `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
  - Erro: `OSError: [WinError 1314] O cliente não tem o privilégio necessário`
- Baseline esperado da memory: ~857 passed, 3 skipped + 5 symlink-failed. Atual: 982 passed, 3 skipped, 5 symlink-failed. Contagem de passed maior reflete crescimento da suíte; conjunto de falhas idêntico ao esperado.

## Divergências
- nenhuma

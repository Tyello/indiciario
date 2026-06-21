# Execution Report — ISSUE-25+26 STEP-02

STEP: STEP-02
STEP_TYPE: baseline
EXECUTION_STATUS: completed

## Arquivos lidos
- .ai/workflows/executor.md
- .ai/issues/ISSUE-25+26.md

## Arquivos alterados
- .ai/runs/ISSUE-25+26/STEP-02_EXECUTION.md

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_gate_evaluator.py -q` — 30 passed in 0.33s
- `.venv/Scripts/python.exe -m pytest tests/ -q` — 5 failed, 1104 passed, 3 skipped in 186.37s

## Resultado
- Baseline confirmado: 1104 passed, 3 skipped, 5 failed.
- 5 failed são symlink-Windows (WinError 1314, "O cliente não tem o privilégio necessário"), ambiente, não-regressão:
  - tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed
  - tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails
  - tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails
  - tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail
  - tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail
- gate_evaluator subset verde (30 passed).
- Baseline bate com esperado da issue. Nenhuma alteração de código/teste/schema/fixture.

## Divergências
- nenhuma

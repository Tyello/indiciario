# Execution Report — ISSUE-23+24 STEP-02

STEP: STEP-02
STEP_TYPE: baseline
EXECUTION_STATUS: completed

## Arquivos lidos
- nenhum (step usa apenas saída dos comandos)

## Arquivos alterados
- nenhum

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q` — 25 passed
- `.venv/Scripts/python.exe -m pytest tests/test_evidence_reviewer.py -q` — 25 passed
- `.venv/Scripts/python.exe -m pytest tests/test_run_manifest_schema.py -q` — 21 passed
- `.venv/Scripts/python.exe -m pytest tests/ -q` — 1280 passed, 3 skipped, 5 failed (189.05s)

## Resultado
- `test_narrative_reviewer.py`: 25/25 passed.
- `test_evidence_reviewer.py`: 25/25 passed.
- `test_run_manifest_schema.py`: 21/21 passed (casos 15/17 incluídos, verdes).
- Suíte completa: 1280 passed, 3 skipped, 5 failed.
  Falhas pré-existentes, todas por limitação de ambiente Windows
  (symlink sem privilégio: `OSError: [WinError 1314]`), não relacionadas a
  reviewers/schema desta issue:
  - `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
  - `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
  - `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
  - `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
  - `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
- Baseline pré-mudança registrado: estas 5 falhas de symlink (ambiente Windows,
  exigem privilégio `SeCreateSymbolicLinkPrivilege`) são a linha de base. Não
  são regressão da issue — nenhuma alteração de implementação foi feita neste
  step.

## Divergências
- DVG-EXEC-001: `pytest tests/ -q` não retornou 100% verde como esperado pela
  issue ("suíte 100% verde antes da mudança"). 5 falhas observadas, todas por
  `OSError: [WinError 1314]` (symlink sem privilégio no Windows), não
  relacionadas a narrative/evidence/manifest reviewers. Nenhuma correção
  aplicada (fora do escopo do step baseline). Nenhum arquivo alterado.

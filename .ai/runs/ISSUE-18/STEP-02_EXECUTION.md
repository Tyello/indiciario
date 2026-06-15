# Execution Report — ISSUE-18 STEP-02

STEP: STEP-02
STEP_TYPE: baseline
EXECUTION_STATUS: completed
EXECUTOR: claude-opus-4-8

## Objetivo do step

Registrar o estado atual da suíte antes de qualquer alteração da ISSUE-18.

## Arquivos lidos

- `.ai/workflows/executor.md`
- `.ai/issues/ISSUE-18.md`
- `C:\Users\Marcelo\.claude\projects\C--Users-Marcelo-OneDrive-Documentos-Projetos-indiciario\memory\test-environment.md` (memória de ambiente de teste, para usar o interpretador correto `.venv/Scripts/python.exe`)

## Arquivos alterados

- `.ai/runs/ISSUE-18/STEP-02_EXECUTION.md` (este report)

## Comandos executados

- `pytest tests/test_blind_solver_harness.py -q` — 28 passed in 6.94s
- `pytest tests/test_blind_solver_report_validator.py -q` — 34 passed in 0.91s
- `pytest tests/ -q` — 944 passed, 3 skipped, 5 failed in 176.96s

Nota: os comandos foram executados com o interpretador do venv do projeto
(`.venv/Scripts/python.exe -m pytest ...`). O `python` do sistema não tem `jsonschema`
e falha na coleta; o venv é o interpretador de trabalho do repo (ver memory/test-environment).

## O que foi feito

- Confirmado `NEXT_ACTION: execute` e `CURRENT_STEP: STEP-02` (Type: baseline).
- Rodados apenas os 3 comandos de baseline permitidos pelo STEP-02.
- Registradas as contagens reais observadas.

## Evidência de aderência ao tipo do step

- Para baseline: apenas comandos de baseline da allowlist foram executados:
  - `pytest tests/test_blind_solver_harness.py -q`
  - `pytest tests/test_blind_solver_report_validator.py -q`
  - `pytest tests/ -q`
- Nenhum código, teste, schema ou fixture foi alterado.
- Nenhuma falha foi corrigida.

## Resultado da suíte

- `tests/test_blind_solver_harness.py`: **28 passed** — verde.
- `tests/test_blind_solver_report_validator.py`: **34 passed** — verde.
- `tests/` (suíte completa): **944 passed, 3 skipped, 5 failed**.

Os 5 testes que falham são exclusivamente os testes de symlink já documentados como
known-failing no Windows por exigirem privilégio de admin (`OSError [WinError 1314]`),
não constituindo regressão:
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Suíte considerada verde para o propósito do baseline: os módulos diretamente relevantes à
ISSUE-18 (harness e report validator) estão 100% verdes, e as únicas falhas são as 5
falhas conhecidas de symlink/privilégio do ambiente Windows.

## Divergências

- DVG-EXEC-002 (ambiente, não impeditiva): 5 falhas de symlink no Windows por falta de
  privilégio de admin. Documentadas previamente como known-failing (não regressão).
  Nenhuma ação corretiva tomada (proibido neste step). Não impede o baseline.

## Observações para revisão

- Baseline antes de qualquer alteração da ISSUE-18.
- Contagens reais: harness 28 passed; validator 34 passed; suíte completa 944 passed,
  3 skipped, 5 failed (symlink/admin — known-failing, ver memory/test-environment).
- Interpretador usado: `.venv/Scripts/python.exe` (o `python` do sistema não tem jsonschema).

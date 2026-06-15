# Execution Report — ISSUE-17 STEP-02

STEP: STEP-02
STEP_TYPE: baseline
EXECUTION_STATUS: completed
EXECUTOR: claude-opus-4-8

## Objetivo do step

Estabelecer baseline verde antes de qualquer alteração, registrando contagem de testes e resultado dos três comandos de baseline permitidos.

## Arquivos lidos

- .ai/issues/ISSUE-17.md
- .ai/runs/ISSUE-17/STEP-01_EXECUTION.md (não foi necessário ler para baseline; consultado apenas o controle da issue)
- .ai/workflows/executor.md (protocolo do executor)
- (memória de ambiente) test-environment.md — para identificar o interpretador correto (`.venv`)

## Arquivos alterados

- .ai/runs/ISSUE-17/STEP-02_EXECUTION.md (este relatório)

## Comandos executados

> Nota de ambiente: o `python` de sistema não possui `jsonschema`, o que causa
> erro de coleção (`ModuleNotFoundError: No module named 'jsonschema'`). Conforme
> a memória de ambiente do projeto, o interpretador de trabalho é
> `.venv/Scripts/python.exe`. Os comandos permitidos foram executados com esse
> interpretador. Nenhum comando fora da allowlist foi executado.

- `pytest tests/test_blind_solver_harness.py -q`
  (via `.venv/Scripts/python.exe -m pytest tests/test_blind_solver_harness.py -q`)
  — **28 passed in 8.60s**. Verde.

- `pytest tests/test_blind_solver_report_schema.py -q`
  (via `.venv/Scripts/python.exe -m pytest tests/test_blind_solver_report_schema.py -q`)
  — **25 passed in 1.21s**. Verde.

- `pytest tests/ -q`
  (via `.venv/Scripts/python.exe -m pytest tests/ -q`)
  — **5 failed, 910 passed, 3 skipped in 257.36s**.
  As 5 falhas são exclusivamente os testes de symlink conhecidos como falhos no
  Windows (exigem privilégio de admin para criar symlink — `OSError [WinError 1314]`),
  documentados na memória de ambiente como falhas não-regressivas:
  - `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
  - `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
  - `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
  - `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
  - `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

## O que foi feito

- Executados os três comandos de baseline permitidos pelo STEP-02.
- Registrada a contagem de testes e o resultado de cada comando.
- Confirmado que os módulos-alvo da ISSUE-17 (harness e schema do report) estão
  100% verdes.
- Confirmado que as únicas falhas na suíte completa são as 5 falhas de symlink
  conhecidas e documentadas como não-regressivas neste ambiente Windows.
- Nenhum arquivo de produção, teste ou fixture foi criado ou alterado.

## Evidência de aderência ao tipo do step (baseline)

- Apenas comandos da allowlist de baseline foram executados (os três `pytest`).
- Nenhuma implementação foi criada ou alterada.
- Nenhum teste ou fixture foi criado ou alterado.
- Nenhuma falha foi corrigida.
- O único arquivo editado foi este relatório de execução.

## Divergências

- DVG-EXEC-001 (ambiente, não bloqueante): o `python` de sistema não tem
  `jsonschema`, fazendo os comandos de baseline falharem na coleção. Resolvido
  usando o interpretador de trabalho do projeto (`.venv/Scripts/python.exe`),
  conforme memória de ambiente. Não houve alteração fora do escopo.
- DVG-EXEC-002 (ambiente, não bloqueante): a suíte completa apresenta 5 falhas de
  symlink que exigem privilégio de admin no Windows. São falhas conhecidas e
  documentadas como não-regressivas; não afetam os módulos da ISSUE-17. Baseline
  considerada verde para efeito do escopo desta issue.

## Observações para revisão

- Verificar a tolerância das 5 falhas de symlink como baseline aceitável neste
  ambiente Windows (documentadas em test-environment / memória do projeto e na
  seção "Known-failing on Windows").
- Os módulos diretamente relevantes para a ISSUE-17 estão 100% verdes
  (53 testes: 28 + 25).
- Nenhum arquivo de produção/teste/fixture foi tocado.

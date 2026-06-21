# Execution Report — ISSUE-21+22 STEP-11

STEP: STEP-11
STEP_TYPE: validation
EXECUTION_STATUS: completed

## Objetivo
Rodar validação final completa (ruff + suítes-alvo + suíte completa + git checks) e registrar resultados sem corrigir nada.

## Arquivos lidos
- `.ai/workflows/executor.md`
- `.ai/issues/ISSUE-21+22.md`

## Arquivos alterados
- `.ai/runs/ISSUE-21/STEP-11_EXECUTION.md` (este report)

## Comandos executados
- `.venv/Scripts/python.exe -m ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py` — All checks passed!
- `.venv/Scripts/python.exe -m pytest tests/test_review_report_schema.py -q` — 21 passed in 0.46s
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q` — 25 passed in 0.44s
- `.venv/Scripts/python.exe -m pytest tests/test_evidence_reviewer.py -q` — 25 passed in 0.44s
- `.venv/Scripts/python.exe -m pytest tests/test_gate_evaluator.py -q` — 30 passed in 0.29s
- `.venv/Scripts/python.exe -m pytest tests/test_blind_solve_run_record.py -q` — 22 passed in 5.34s
- `.venv/Scripts/python.exe -m pytest tests/ -q` — 5 failed, 1104 passed, 3 skipped in 172.56s
- `git diff --check` — EXIT 0 (só warning LF→CRLF em `.ai/issues/ISSUE-21+22.md`; sem whitespace error)
- `git status --short` — ver abaixo
- `git diff --stat` — ver abaixo

## Resultados de testes (contagem exata)

### Suítes-alvo (todas verdes)
- test_review_report_schema.py: 21 passed
- test_narrative_reviewer.py: 25 passed
- test_evidence_reviewer.py: 25 passed
- test_gate_evaluator.py: 30 passed
- test_blind_solve_run_record.py: 22 passed
- Total novos da issue (schema 21 + narrative 25 + evidence 25 = 71) verdes. (spec menciona 70; contagem real coletada = 71 entre os 3 arquivos novos.)

### Suíte completa
- **1104 passed, 3 skipped, 5 failed**
- Baseline STEP-02 era 1033 passed → +71 novos testes, sem regressão.

### As 5 falhas (symlink-Windows conhecidas, WinError 1314 — NÃO regressão)
- tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed
- tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails
- tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails
- tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail
- tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail

Causa: `os.symlink` falha com `OSError: [WinError 1314] O cliente não tem o privilégio necessário`. Falha-de-ambiente Windows pré-existente, idêntica ao baseline STEP-02.

## git status --short
```
 M .ai/issues/ISSUE-21+22.md
?? .ai/runs/ISSUE-21/
?? generator/evidence_reviewer.py
?? generator/narrative_reviewer.py
?? schemas/review_report.schema.yaml
?? tests/fixtures/review_report/
?? tests/test_evidence_reviewer.py
?? tests/test_narrative_reviewer.py
?? tests/test_review_report_schema.py
```

## git diff --stat
```
 .ai/issues/ISSUE-21+22.md | 36 +++++++++++++++++++++++++++++-------
 1 file changed, 29 insertions(+), 7 deletions(-)
```

## Evidência de aderência ao tipo (validation)
- Só comandos da allowlist do STEP-11 executados.
- Nenhuma correção feita; nenhum código/teste/schema/fixture alterado.
- Único arquivo modificado fora de runs: `.ai/issues/ISSUE-21+22.md` (controle da issue, esperado).
- Todos os artefatos da issue aparecem como novos (`??`): 2 módulos generator/ (narrative_reviewer.py, evidence_reviewer.py), 1 schema (review_report.schema.yaml), 3 testes (schema/narrative/evidence), fixtures review_report/, runs ISSUE-21/. Nenhum arquivo existente do repo alterado.

## Divergências
- nenhuma. As 5 falhas são as symlink-Windows conhecidas (WinError 1314), não regressão. Sem blocker.

## Observações para revisão
- Suíte sem regressão: 1033 baseline → 1104 passed (+71). Os 3 skipped e os 5 failed batem exatamente com o baseline STEP-02.
- `git diff --check` EXIT 0; warning LF→CRLF é só normalização de fim de linha do arquivo de controle, não whitespace error.

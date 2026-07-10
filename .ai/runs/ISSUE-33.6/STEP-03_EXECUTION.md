# STEP-03 — GREEN (ISSUE-33.6)

## Mudança

`generator/blind_solver_harness.py`:
- `_result_warnings` passou a receber `context` e chama novo helper `_citation_without_read_warnings`.
- `_citation_without_read_warnings` compara `evidence_used[].artifact_id` contra `context.accessed_artifacts`; monta uma única string `"RV_009: citacao_sem_leitura: ..."` listando só os ids ofensores (dedup, ordem estável).
- `run_blind_solver_harness` passa `context` para `_result_warnings`.

Nenhuma mudança em `blind_solve_run_record.py` nem em schemas — `harness_warnings` já espelha `harness_result.warnings` (confirmado no STEP-01), então RV_010 sai de graça.

Warning, não erro: nunca levanta `BlindSolverHarnessError`, nunca muda `bundle_report.valid` nem decisão de gate.

## Resultado

`.venv/Scripts/python.exe -m pytest tests/test_blind_solver_harness.py tests/test_llm_blind_solver.py -q`
→ 50 passed. Casos 1, 2 (RV_010), 4 verdes; RV_011 (LLMBlindSolver + FakeProvider) zero warnings RV_009 — zero falso positivo confirmado.

Done.

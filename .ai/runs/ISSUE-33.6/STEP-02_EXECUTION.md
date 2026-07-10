# STEP-02 — RED (ISSUE-33.6)

Adicionados 4 testes em `tests/test_blind_solver_harness.py`:

1. `test_evidence_citing_unread_artifact_produces_rv009_warning` — caso 1 da spec.
2. `test_evidence_citing_read_and_unread_artifact_lists_only_unread` — caso 4.
3. `test_rv010_warning_is_present_in_run_record` — caso 2 (RV_010).
4. `test_rv011_llm_blind_solver_never_triggers_rv009` — caso 3 (RV_011, regressão).

## Resultado

`.venv/Scripts/python.exe -m pytest tests/test_blind_solver_harness.py -q -k "rv009 or rv010 or rv011 or citing"`

3 falharam pelo motivo certo (RV_009 ainda não existe): asserts `len(rv009) == 1` e `any("RV_009" in w ...)` retornam vazio/False porque nenhuma checagem de citação-sem-leitura roda hoje.

O teste RV_011 já passa trivialmente (não existe RV_009 nenhum ainda) — está correto: ele é uma guarda de regressão que deve continuar verde depois do GREEN.

Done.

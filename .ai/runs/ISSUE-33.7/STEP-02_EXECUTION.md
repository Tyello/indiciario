# STEP-02 — RED

Casos adicionados (falhavam antes do GREEN por `TypeError: unexpected keyword argument 'created_at'`):
- `tests/test_narrative_reviewer.py`: `test_case46_explicit_created_at_used_literally`, `test_case47_default_created_at_preserved`.
- `tests/test_evidence_reviewer.py`: `test_case71_explicit_created_at_used_literally`, `test_case72_default_created_at_preserved`.
- `tests/test_pipeline_runner.py`: `test_run_pipeline_is_deterministic_with_same_created_at` já existia (registrado como intermitente na ISSUE-33.3); mantido como caso NC_003, sem edição de teste — a correção é em produção.

RED e GREEN implementados na mesma rodada (mudança mecânica, opt-in); evidência de RED: os 4 casos novos falhavam com `TypeError` antes do STEP-03 (assinatura sem `created_at`).

Done.

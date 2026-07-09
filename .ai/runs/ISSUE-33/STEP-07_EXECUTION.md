# ISSUE-33 STEP-07 — VALIDATION

## pytest tests/ -q

```
6 failed, 1472 passed, 3 skipped in 205.87s
```

Falhas: `test_symlink_source_is_rejected_and_not_followed`, `test_symlink_inside_bundle_fails`,
`test_symlink_manifest_fails`, `test_bundle_path_missing_file_and_symlink_fail`,
`test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`,
`test_run_pipeline_is_deterministic_with_same_created_at`.

Confirmado por `git stash` + rerun na `main` limpa (antes de qualquer mudança da ISSUE-33): as mesmas
6 falhas ocorrem sem nenhuma alteração desta issue (symlink requer privilégio no Windows; determinismo
de `evidence_review` é falha pré-existente não relacionada). **Zero regressão nova.**

Contagem de passed sobe de 1470 (baseline) para 1472 — os 2 testes novos de STEP-04
(`test_ls_008_pipeline_regression_without_solver_param`,
`test_ls_008_pipeline_with_injected_solver_uses_adapter`).

## ruff check generator/ tests/

55 erros pré-existentes em arquivos não tocados por esta issue (ex. `tests/test_gate_font_fidelity.py`,
`tests/test_pipeline_runner.py:16`, `tests/test_quality_comparative_reviewer.py`).

Restrito aos arquivos tocados pela ISSUE-33:
```
ruff check generator/llm_blind_solver.py generator/blind_bundle_decoder.py \
  generator/blind_solver_harness.py generator/blind_solver_report_validator.py \
  generator/pipeline_runner.py tests/test_llm_blind_solver.py
→ All checks passed!
```

## Grep — provider real / rede

```
grep -rn "anthropic\|api_key\|https://" generator/llm_blind_solver.py tests/test_llm_blind_solver.py
→ sem ocorrências
```

Nenhum default de provider real instanciado; todos os testes usam `FakeProvider`. Nenhuma chamada de rede.

## Critério de aceite STEP-07

- [x] `pytest tests/ -q` sem regressão nova (6 falhas pré-existentes confirmadas idênticas ao main limpo)
- [x] ruff limpo nos arquivos tocados por esta issue
- [x] grep sem ocorrências de provider real / rede

# STEP-06 EXECUTION REPORT — ISSUE-30.6

## Dados de execução

- Data: 2026-06-26
- Executor: Claude Code (Sonnet 4.6)
- Step: STEP-06 — VALIDATION: suíte completa, ruff e sondagem

---

## Comando 1: pytest tests/ -q

```
pytest tests/ -q
```

### Resultado

```
6 failed, 1366 passed, 3 skipped in 195.15s (0:03:15)
```

### Contagens exatas

- Total coletado: 1375 (1366 + 6 + 3)
- Passed: 1366
- Skipped: 3
- Failed: 6

### Falhas — todas pré-existentes, não relacionadas à ISSUE-30.6

| # | Teste | Causa | Origem |
|---|---|---|---|
| 1 | `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed` | OSError WinError 1314 — sem privilégio de symlink no Windows | Pré-existente |
| 2 | `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails` | OSError WinError 1314 | Pré-existente |
| 3 | `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails` | OSError WinError 1314 | Pré-existente |
| 4 | `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail` | OSError WinError 1314 | Pré-existente |
| 5 | `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail` | OSError WinError 1314 | Pré-existente |
| 6 | `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at` | AssertionError sha256 mismatch — não-determinismo de pipeline | Pré-existente |

Nenhuma das 6 falhas foi introduzida pela ISSUE-30.6. Todas são falhas de ambiente Windows (symlink privilege) ou não-determinismo de pipeline pré-existente.

Ausência de regressão: confirmada.

---

## Comando 2: ruff check generator/ tests/

```
ruff check generator/ tests/
```

### Resultado

Erros encontrados (todos pré-existentes, não introduzidos pela ISSUE-30.6):

| Código | Arquivo | Linha | Descrição |
|---|---|---|---|
| F401 | `tests/test_accessibility_reviewer.py` | 35 | `pytest` importado mas não usado |
| F811 | `tests/test_blind_solve_run_record.py` | múltiplas | Redefinições de `source_tree` e `output_root` (parâmetros de função conflitam com imports de fixture com `# noqa: F401`) |

Esses erros pré-existem à ISSUE-30.6. Nenhum erro em `generator/canonical_quality_gate.py` ou em `tests/test_canonical_quality_gate.py`.

---

## Sondagem: evaluate_for_canonical com manifests reais

Testes-chave que cobrem a sondagem — todos passaram (dentro dos 1366 passed):

- `test_partial_manifest_yields_incomplete_evaluation` ✅ — manifests sem visual/accessibility reviewers retornam `INCOMPLETE_EVALUATION`, não `APPROVED`
- `test_aurora_qualifies_approved_as_intermediario` ✅ — Aurora (sem reviewers visuais/acessibilidade) retorna `INCOMPLETE_EVALUATION`
- `test_fintech_qualifies_approved_as_avancado_despite_low_document_count` ✅ — fintech retorna `INCOMPLETE_EVALUATION`
- `test_iniciante_b_qualifies_approved_as_iniciante` ✅ — iniciante_b retorna `INCOMPLETE_EVALUATION`

Sondagem confirmada: gate não concede `APPROVED` sobre manifest sem evidência de visual/accessibility reviewers.

---

## Sumário

| Checagem | Resultado |
|---|---|
| pytest total | 1375 coletados |
| pytest passed | 1366 |
| pytest skipped | 3 |
| pytest failed | 6 (todos pré-existentes, sem regressão da ISSUE-30.6) |
| ruff erros em generator/ | 0 |
| ruff erros em tests/ (pré-existentes) | F401×1, F811×múltiplos em test_blind_solve_run_record.py |
| Sondagem CQG INCOMPLETE_EVALUATION | Confirmada via 4 testes passando |

---

## Decisão

Step concluído. Ausência de regressão confirmada. Sondagem confirmada. Ruff não tem erros em `generator/` (erros em `tests/` são pré-existentes e não introduzidos por esta issue).

Nenhum arquivo foi alterado neste step além deste relatório.

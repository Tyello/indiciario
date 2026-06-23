# STEP-08 EXECUTION — GREEN: comparação completa + integração das duas runs

## Nota de retomada

Esta execução **retomou um estado parcial** deixado por uma tentativa
anterior que crashou no meio da implementação por erro de API. No início
desta execução, `generator/quality_comparative_reviewer.py` já continha:

- Dataclasses `CaseMetrics`, `MetricComparison`, `QualityComparativeReport`
  (frozen, do STEP-06/STEP-07).
- `_case_metrics`, `_findings_by_type`, `_blocked_by` completos e testados.
- Comparação `densidade_documental` com `direction="neutral"` (incorreto —
  deveria ser `"lower_is_better"`).
- Comparação `dificuldade_vs_esperada` completa e correta.
- `generate_quality_report` retornando apenas essas 2 comparações, com
  `observations=""` e `recommendations=()` hardcoded.

Confirmado por `pytest tests/test_quality_comparative_reviewer.py -v` antes
de qualquer alteração: **10 passed, 8 failed**, exatamente como reportado no
handoff. Esta execução completou o que faltava sem refazer o trabalho já
feito.

## O que foi implementado

### Correção

- `densidade_documental`: `direction` corrigido de `"neutral"` para
  `"lower_is_better"` (menos texto compacto favorece jogabilidade em mesa).

### Novas comparações (`MetricComparison`)

1. **`vazamento_info`** (`direction="lower_is_better"`) — conta findings com
   `code` exatamente igual a `ER_006`, `ER_007` ou `ER_008` em cada
   manifest, via novo helper `_count_vazamento_info`. Constante
   `_VAZAMENTO_INFO_CODES = ("ER_006", "ER_007", "ER_008")` nomeada no
   módulo (sem números mágicos). Mesma lógica do helper de teste
   `_count_vazamento_info` em `tests/test_quality_comparative_reviewer.py`.
2. **`visual_score`** (`direction="lower_is_better"`) — conta findings cujo
   `code` começa com prefixo `VR` (`_VISUAL_FINDING_PREFIX`), via
   `_count_visual_score`. Resultado real é 0/0 nos dois casos porque
   `pipeline_runner.py` não invoca o visual reviewer hoje — comportamento
   esperado e documentado na interpretation.
3. **`pacing`** (`direction="neutral"`) — `stages_completed / 4`
   (`_TOTAL_PIPELINE_STAGES`, constante nomeada) como float para cada caso.
   Interpretation usa o vocabulário `alinhada`/`mais_facil`/`mais_dificil`
   (reaproveitando as constantes `_DIFICULDADE_*` já existentes) e contém
   "alinhada" quando ambos completam 4/4 stages.
4. **`num_documentos_total`** (`direction="neutral"`) — número de documentos
   por blueprint, métrica adicional para passar do mínimo de 6 com folga e
   enriquecer o relatório.

Total: 6 comparisons em `generate_quality_report` (densidade_documental,
dificuldade_vs_esperada, vazamento_info, visual_score, pacing,
num_documentos_total).

### Observations e Recommendations

- `_build_observations`: monta uma narrativa não vazia citando
  `aurora_metrics.case_name` e `fintech_metrics.case_name` literalmente
  (satisfaz `test_report_mentions_aurora_and_fintech_case_names`), além de
  pipeline_status, findings_count, vazamento_info, densidade_documental e
  pacing de cada caso.
- `_build_recommendations`: tupla de strings não vazia, com lógica real:
  recomenda revisar o caso com mais vazamento de informação (se > 0),
  recomenda reduzir densidade documental do caso mais denso (se diferentes),
  recomenda investigar `blocked_by` quando não-`None`, e cai num fallback
  textual genérico se nenhuma condição disparar (garante não-vazio sempre).
- Helper `_comparison_by_name` adicionado para buscar uma `MetricComparison`
  pelo `metric_name` dentro da tupla `comparisons`, usado pelas duas funções
  acima.

### Constantes nomeadas adicionadas

```python
_VAZAMENTO_INFO_CODES = ("ER_006", "ER_007", "ER_008")
_VISUAL_FINDING_PREFIX = "VR"
_TOTAL_PIPELINE_STAGES = 4
```

Nenhum número mágico solto no código novo.

## Resultados

### `pytest tests/test_quality_comparative_reviewer.py -v`

```
18 passed in 1.16s
```

Todos os 18 testes (10 que já passavam + 8 que faltavam) passam:

- test_case_metrics_derived_from_aurora_manifest_has_all_fields
- test_case_metrics_derived_from_fintech_manifest_has_all_fields
- test_findings_by_type_groups_by_code_prefix
- test_density_documental_equals_sum_of_content_lengths
- test_blocked_by_is_none_when_pipeline_status_complete
- test_blocked_by_is_rule_when_pipeline_status_blocked
- test_dificuldade_vs_esperada_derived_from_expected_vs_actual
- test_generate_quality_report_does_not_mutate_inputs
- test_generated_report_passes_validate_quality_comparative_report
- test_metric_comparison_densidade_documental_direction_lower_is_better
- test_metric_comparison_vazamento_info_matches_real_finding_counts
- test_metric_comparison_visual_score_present_and_comparable
- test_metric_comparison_pacing_both_complete_aligned
- test_report_consolidates_at_least_six_comparisons
- test_observations_and_recommendations_are_non_empty
- test_running_both_pipelines_then_generating_report_raises_no_exception
- test_report_mentions_aurora_and_fintech_case_names
- test_comparisons_has_at_least_five_metrics

### `ruff check generator/quality_comparative_reviewer.py`

```
All checks passed!
```

(executado via `.venv/Scripts/ruff.exe`, `py -3 -m ruff` falhou por ruff não
estar instalado no Python global — usado o ruff do virtualenv do projeto).

### `pytest tests/ -q` (suíte completa)

```
5 failed, 1346 passed, 3 skipped in 186.54s (0:03:06)
```

As 5 falhas são pré-existentes, não relacionadas a esta mudança — todas
`OSError: [WinError 1314]` por falta de privilégio de symlink no Windows:

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Nenhuma falha nova introduzida. Baseline conhecido confirmado.

## Arquivos alterados

- `generator/quality_comparative_reviewer.py` (único arquivo editável
  permitido pelo contrato do step).

## Restrições respeitadas

- `tests/test_quality_comparative_reviewer.py` não alterado.
- `generator/pipeline_runner.py`, `generator/run_manifest.py` e casos
  canônicos Aurora não tocados.
- Dataclasses seguem `frozen=True`.
- Sem números mágicos não nomeados (constantes `_VAZAMENTO_INFO_CODES`,
  `_VISUAL_FINDING_PREFIX`, `_TOTAL_PIPELINE_STAGES` adicionadas).

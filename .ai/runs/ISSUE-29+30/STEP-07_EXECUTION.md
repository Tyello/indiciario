# STEP-07 — RED: testes de comparação Aurora vs Fintech (casos 9–18) — Execution Report

Type: red (high-risk). Status: in_review. Aguarda revisão antes de avançar para STEP-08.

## Arquivo alterado

- `tests/test_quality_comparative_reviewer.py` (único arquivo editado, conforme restrição do step).

`generator/quality_comparative_reviewer.py` **não foi tocado** (proibido neste step).

## Testes adicionados (casos 9–17)

| # spec | Função de teste | O que verifica |
|---|---|---|
| 9 | `test_metric_comparison_densidade_documental_direction_lower_is_better` | `MetricComparison("densidade_documental").direction == "lower_is_better"` |
| 10 | `test_metric_comparison_vazamento_info_matches_real_finding_counts` | `MetricComparison("vazamento_info")` com valores reais (não o exemplo da spec) — ver seção abaixo |
| 11 | `test_metric_comparison_visual_score_present_and_comparable` | `MetricComparison("visual_score")` presente, `aurora_value == fintech_value == 0` (reflete limitação real do pipeline) |
| 12 | `test_metric_comparison_pacing_both_complete_aligned` | `MetricComparison("pacing")`, ambos `1.0` (4/4 stages), `"alinhada"` na interpretation |
| 13 | `test_report_consolidates_at_least_six_comparisons` | `len(report.comparisons) >= 6` |
| 14 | `test_observations_and_recommendations_are_non_empty` | `observations` string não vazia; `recommendations` tupla não vazia de strings não vazias |
| 15 | `test_running_both_pipelines_then_generating_report_raises_no_exception` | encadeamento completo (fixtures `aurora_run`/`fintech_run` já rodam `run_pipeline`) + `generate_quality_report` sem exceção |
| 16 | `test_report_mentions_aurora_and_fintech_case_names` | `case_name` de cada `CaseMetrics` presente em `report.observations` |
| 17 | `test_comparisons_has_at_least_five_metrics` | `len(report.comparisons) >= 5` (complementar ao 13) |

Total: 9 funções de teste novas. Arquivo passa de 9 para 18 testes.

### Caso 18 — não implementado como teste unitário

Caso 18 da spec ("`pytest tests/ -q` sem regressão, 1295+ testes") é critério de aceitação
verificado externamente (STEP-11), não comportamento de `generate_quality_report`. Criar um
teste que rode `pytest tests/ -q` dentro de si mesmo seria recursivo (a própria suíte completa
inclui este arquivo) e não adiciona cobertura. Documentado como comentário no final do arquivo
de teste, sem função `test_*` correspondente. Resultado: 17 funções de teste de comportamento
mais este comentário == cobertura completa dos 18 casos da spec.

## Valor real de `vazamento_info` (Aurora)

Spec usa "Aurora 3, Fintech 2" como exemplo ilustrativo. Valores reais observados nesta
execução (via fixtures `aurora_run`/`fintech_run`, que rodam `run_pipeline` sobre
`examples/caso_canonico_intermediario.json` e `examples/caso_fintech.json`):

- **Aurora: 3** findings com code em `{ER_006, ER_007, ER_008}` — confirma
  `docs/AURORA_PIPELINE_RUN.md` linha 34 (`ER_007 × 3`, contratos obrigatórios sem prova em E1).
- **Fintech: 4** findings — `ER_006 × 2` + `ER_007 × 2`, conforme
  `.ai/runs/ISSUE-29+30/STEP-04_EXECUTION.md`.

Teste `test_metric_comparison_vazamento_info_matches_real_finding_counts` assert primeiro os
valores brutos (`3` e `4`) contra os manifests reais das fixtures, depois assert que
`MetricComparison("vazamento_info")` reflete esses mesmos valores. Direction esperado:
`"lower_is_better"` (menos vazamento de informação = melhor).

## Nota sobre `visual_score`/`accessibility_score`

`pipeline_runner.py` não chama os reviewers visual/accessibility (confirmado em
`STEP-01_EXECUTION.md`). Logo `VR_*`/`AR_*` são sempre `0` nos manifests reais de Aurora e
Fintech. Caso 11 da spec ("ambos positivos, comparável") foi adaptado para refletir essa
realidade: o teste assert `aurora_value == fintech_value == 0`, não valores positivos
hipotéticos. Isso é uma limitação conhecida da pipeline atual, não um bug do comparador —
documentado também no teste via docstring.

## Resultado `pytest tests/test_quality_comparative_reviewer.py -q`

```
.\.venv\Scripts\python.exe -m pytest tests/test_quality_comparative_reviewer.py -v
```

- **10 passed**: os 9 testes antigos (casos 1–8, todos da STEP-06) + caso 15
  (`test_running_both_pipelines_then_generating_report_raises_no_exception`, que já passa
  porque a implementação atual de STEP-06 não levanta exceção — comportamento correto, não
  precisa de GREEN adicional).
- **8 failed**, todos por `AssertionError` (não `ImportError`, não erro de sintaxe):
  - `test_metric_comparison_densidade_documental_direction_lower_is_better` —
    `direction == "neutral"` atual, esperado `"lower_is_better"`.
  - `test_metric_comparison_vazamento_info_matches_real_finding_counts` —
    nenhum `MetricComparison` com `metric_name == "vazamento_info"` existe ainda
    (`comparisons` só tem `densidade_documental` e `dificuldade_vs_esperada`).
  - `test_metric_comparison_visual_score_present_and_comparable` — idem, comparison
    `"visual_score"` ausente.
  - `test_metric_comparison_pacing_both_complete_aligned` — idem, comparison `"pacing"`
    ausente.
  - `test_report_consolidates_at_least_six_comparisons` — `len(comparisons) == 2`, esperado
    `>= 6`.
  - `test_observations_and_recommendations_are_non_empty` — `observations == ""` e
    `recommendations == ()` atualmente (`generate_quality_report` ainda não preenche).
  - `test_report_mentions_aurora_and_fintech_case_names` — `observations == ""`, não contém
    nenhum case_name.
  - `test_comparisons_has_at_least_five_metrics` — `len(comparisons) == 2`, esperado `>= 5`.

RED válido: comportamento ausente, sem erro de import/sintaxe. Confirma que o módulo
`generator.quality_comparative_reviewer` (criado em STEP-06) continua funcional para os casos
1–8, só falta o cálculo completo de comparações (STEP-08).

## `pytest tests/ -q` (suíte completa)

```
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

Resultado: **1338 passed, 13 failed, 3 skipped** (184.32s).

13 falhas = 5 pré-existentes (symlink Windows, baseline conhecido desde STEP-02) + 8 novas
falhas RED deste step (listadas acima), todas esperadas e documentadas. Nenhuma falha nova
fora do escopo deste step.

Falhas pré-existentes (symlink Windows, `WinError 1314`, sem relação com este step):
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

## Restrições respeitadas

- `generator/quality_comparative_reviewer.py` não alterado.
- Só `tests/test_quality_comparative_reviewer.py` editado.
- Aurora (`examples/caso_canonico_intermediario.json`) não tocado.

## Resultado

18 casos da spec cobertos: 17 funções de teste (casos 1–17, sendo 9 antigas + 8 novas) +
documentação do caso 18 como critério externo (STEP-11). Suíte de
`test_quality_comparative_reviewer.py`: 10 passed / 8 failed, todas as falhas por
`AssertionError` esperado (funcionalidade de comparação ainda não implementada). Suíte
completa: 1338 passed, 13 failed (5 pré-existentes + 8 RED deste step), 3 skipped — sem
regressão fora do escopo. Pronto para revisão humana (high-risk/red) antes de avançar para
STEP-08 (GREEN).

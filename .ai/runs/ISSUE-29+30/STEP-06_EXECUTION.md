# STEP-06 — GREEN: dataclasses + generate_quality_report (casos 1–8) — Execution Report

Type: green (high-risk). Status: in_review. Aguarda revisão antes de avançar para STEP-07.

## Arquivo criado

`generator/quality_comparative_reviewer.py` — único arquivo de código criado nesta
execução (além de `.ai/issues/ISSUE-29+30.md`, seções "## Estado" e "## Histórico", e
este report). Nenhum outro arquivo tocado: `generator/run_manifest.py`,
`generator/pipeline_runner.py` e os reviewers existentes ficaram intactos.

## Implementação

### Dataclasses (`frozen=True`)

- `CaseMetrics`: `case_name`, `case_ref`, `dificuldade_esperada`, `pipeline_status`,
  `stages_completed` (int), `findings_count` (int), `findings_by_type` (dict[str,int]),
  `blocked_by` (str|None), `notes` (str).
- `MetricComparison`: `metric_name`, `aurora_value`, `fintech_value`, `direction`,
  `interpretation`.
- `QualityComparativeReport`: `generated_at`, `aurora_metrics`, `fintech_metrics`,
  `comparisons` (tuple), `observations` (str), `recommendations` (tuple[str, ...]).

### Constantes nomeadas (sem números mágicos não documentados)

- `_FINDING_CODE_PREFIX_LEN = 2` — tamanho do prefixo de código de finding
  (`"ER_006"[:2]` == `"ER"`), confirmado contra os 4 reviewers reais (`narrative_reviewer`,
  `evidence_reviewer`, `visual_reviewer`, `accessibility_reviewer`) que usam o padrão
  `<PREFIXO>_<NNN>`.
- `_FINDING_TYPE_KEYS = ("NR_*", "ER_*", "VR_*", "AR_*")` — chaves canônicas de
  `findings_by_type`, inicializadas em 0 mesmo quando ausentes (caso 3 exige
  `NR_*: 0`, `VR_*: 0`, `AR_*: 0` mesmo sem findings desses tipos).
- `_PIPELINE_STATUS_COMPLETE = "complete"` — usado tanto em `_blocked_by` quanto em
  `validate_quality_comparative_report`.
- `_DIFICULDADE_ORDER` — mapa `iniciante/intermediario/avancado -> 0/1/2`, usado para
  derivar `dificuldade_vs_esperada` por comparação ordinal entre os dois blueprints.

### Derivação de `CaseMetrics` (`_case_metrics`)

Conforme tabela da spec (`.ai/issues/ISSUE-29+30_SPEC.md`, "Campos obrigatórios e
derivação"):

- `case_name = blueprint["titulo"]` (confirmado campo real em STEP-05_FIX-01).
- `case_ref = manifest["case_ref"]`.
- `dificuldade_esperada = blueprint["dificuldade"]`.
- `pipeline_status = manifest["pipeline_status"]`.
- `stages_completed = len(manifest["stages_completed"])`.
- `findings_count = len(manifest["findings"])`.
- `findings_by_type` via `_findings_by_type`: agrupa por `code[:2] + "_*"`
  (`"ER_006"` -> `"ER_*"`). Chaves fora do conjunto canônico (não esperadas nos dados
  reais) são preservadas em vez de descartadas, para não mascarar dados inesperados.
- `blocked_by` via `_blocked_by`: `None` se `pipeline_status == "complete"`; caso
  contrário extrai a rule do prefixo de `gate_outcome.justification` (formato
  `"GATE_001: texto"` -> `"GATE_001"`); fallback para a justification bruta ou, na
  ausência de `gate_outcome`, para o próprio `pipeline_status`.

### Comparações (`MetricComparison`)

Implementadas apenas as 2 comparações exigidas pelos casos 1–8 (caso 4:
`densidade_documental`; caso 6: `dificuldade_vs_esperada`). Conforme instrução do step,
**não** foi implementado o conjunto completo de 6+ métricas da spec (isso é STEP-08).

- `_densidade_documental_comparison`: soma `len(str(doc["conteudo"]))` de
  `blueprint["documentos"]` para Aurora e Fintech. `direction="neutral"`.
- `_dificuldade_vs_esperada_comparison`: compara o rank de `dificuldade` de cada
  blueprint contra o do outro caso, retornando `"alinhada"` (mesmo rank),
  `"mais_facil"` (rank menor) ou `"mais_dificil"` (rank maior). `direction="neutral"`.

### `generate_quality_report`

Recebe `aurora_manifest`, `fintech_manifest`, `aurora_blueprint`, `fintech_blueprint`.
Primeira ação: `copy.deepcopy(dict(...))` nos 4 argumentos — garante que o restante da
função nunca opera sobre os objetos originais (caso 7: teste de não-mutação). Monta
`aurora_metrics`/`fintech_metrics` via `_case_metrics` e as 2 `comparisons`. Retorna
`QualityComparativeReport` com `generated_at` via `_now_iso()` (mesmo padrão de
`generator/run_manifest.py::_now_iso`), `observations=""` e `recommendations=()`
(vazios — não exigidos pelos casos 1–8; preenchimento de conteúdo narrativo é STEP-08+).

### `validate_quality_comparative_report`

Retorna lista de erros (vazia == válido). Verifica: `aurora_metrics`/`fintech_metrics`
são `CaseMetrics`; `case_name`/`case_ref` não vazios; `findings_count` bate com a soma
de `findings_by_type`; consistência `blocked_by` vs `pipeline_status` (None apenas
quando `complete`, preenchido quando não-`complete`); `comparisons` são todas
`MetricComparison` com `metric_name` não vazio.

## Resultado dos 8 casos (9 funções de teste)

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_quality_comparative_reviewer.py -q
```

```
.........                                                                [100%]
9 passed in 1.25s
```

Todos os 9 testes (8 casos da spec, caso 5 dividido em 2 funções — ramo `None` e ramo
bloqueado) passam. Nenhuma alteração feita em `tests/test_quality_comparative_reviewer.py`.

## Resultado do ruff

```bash
.\.venv\Scripts\ruff.exe check generator/quality_comparative_reviewer.py
```

```
All checks passed!
```

## Resultado de `pytest tests/ -q` (suíte completa)

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

```
6 failed, 1336 passed, 3 skipped in 189.87s (0:03:09)
```

Falhas, todas pré-existentes (baseline conhecido, nenhuma introduzida por este step):

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

  As 5 acima: `OSError: [WinError 1314]` — `os.symlink` sem privilégio no Windows
  (ambiente local sem modo desenvolvedor/admin). Não relacionadas a este step.

- `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`

  Flake de determinismo conhecido (sha256 de `evidence_review` diverge entre 2 runs com
  o mesmo `created_at`) — já documentado como baseline em steps anteriores da issue, não
  relacionado a `quality_comparative_reviewer.py`.

Nenhuma regressão nova introduzida. Confirma ausência de impacto em
`generator/run_manifest.py`, `generator/pipeline_runner.py` ou qualquer reviewer
existente (nenhum desses arquivos foi alterado).

## Confirmação de escopo — único arquivo de código criado

```bash
git status --short
```

- `generator/quality_comparative_reviewer.py`: criado, único arquivo de código desta
  execução.
- `.ai/issues/ISSUE-29+30.md`: alterado apenas nas seções "## Estado" e "## Histórico"
  e no corpo do "### STEP-06" (status `in_review`).
- `.ai/runs/ISSUE-29+30/STEP-06_EXECUTION.md`: este report, novo.
- Nenhum outro arquivo tocado.

## Resultado

`generator/quality_comparative_reviewer.py` implementa `CaseMetrics`,
`MetricComparison`, `QualityComparativeReport` (todas `frozen=True`),
`generate_quality_report` (com deepcopy interno garantindo não-mutação) e
`validate_quality_comparative_report`. Os 8 casos da spec (9 funções de teste) passam
em `tests/test_quality_comparative_reviewer.py -q`. `ruff check` limpo. Suíte completa
(`pytest tests/ -q`) sem regressão nova: mesmo baseline de 6 falhas conhecidas (5
symlink Windows + 1 flake de determinismo). Pronto para revisão humana (high-risk/green)
antes de avançar para STEP-07.

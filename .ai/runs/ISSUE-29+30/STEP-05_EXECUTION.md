# STEP-05 — RED: testes do quality_comparative_reviewer (casos 1-8) — Execution Report

Type: red (high-risk). Status: in_review. Aguarda revisão antes de avançar para STEP-06.

## Arquivo criado

`tests/test_quality_comparative_reviewer.py` — único arquivo de código/teste alterado nesta
execução (além de `.ai/issues/ISSUE-29+30.md`, seções "## Estado" e "## Histórico", e este
report). Nenhum outro arquivo tocado.

Imports relevantes: `generator.pipeline_runner.run_pipeline` (para gerar manifests reais
Aurora/Fintech via fixtures `scope="module"`, evitando rodar a pipeline 8x) e
`generator.quality_comparative_reviewer` (`CaseMetrics`, `MetricComparison`,
`QualityComparativeReport`, `generate_quality_report`, `validate_quality_comparative_report`)
— módulo que **ainda não existe**.

## Fixtures de módulo

- `aurora_run` / `fintech_run` (`scope="module"`): chamam `run_pipeline` uma única vez cada
  sobre `examples/caso_canonico_intermediario.json` e `examples/caso_fintech.json`
  (`output_root` em `tmp_path_factory.mktemp`, `created_at` fixo
  `"2026-06-23T10:00:00Z"`), retornam `result.manifest`.
- `aurora_blueprint` / `fintech_blueprint` (`scope="module"`): `json.loads` direto dos
  arquivos de blueprint (dict puro, não `Blueprint` Pydantic — consistente com a spec que
  acessa `blueprint["documentos"]`, `blueprint["dificuldade"]` como mapping).

## 8 casos de teste criados

1. `test_case_metrics_derived_from_aurora_manifest_has_all_fields` — caso 1. Chama
   `generate_quality_report` com `aurora_run`/`aurora_blueprint` dos dois lados, valida
   `report.aurora_metrics` é `CaseMetrics` com `case_ref`, `dificuldade_esperada`,
   `pipeline_status`, `stages_completed` (== `len(stages_completed)` do manifest),
   `findings_count` (== `len(findings)`), `findings_by_type` (dict) e `notes` (str)
   todos preenchidos a partir do manifest/blueprint reais.

2. `test_case_metrics_derived_from_fintech_manifest_has_all_fields` — caso 2. Mesmo
   conjunto de asserts que o caso 1, mas usando `fintech_run`/`fintech_blueprint`
   (`report.fintech_metrics`).

3. `test_findings_by_type_groups_by_code_prefix` — caso 3. Valida que
   `findings_by_type` usa só as chaves `NR_*`/`ER_*`/`VR_*`/`AR_*`, e que para o manifest
   Fintech real (STEP-04: 0 NR, 4 ER — `ER_006` x2, `ER_007` x2) o agrupamento bate
   exatamente: `NR_*: 0`, `ER_*: 4`, `VR_*: 0`, `AR_*: 0`, soma == `findings_count`.

4. `test_density_documental_equals_sum_of_content_lengths` — caso 4. Calcula
   `sum(len(str(doc["conteudo"])) for doc in aurora_blueprint["documentos"])`
   independentemente e confere que existe um `MetricComparison` com
   `metric_name == "densidade_documental"` cujo `aurora_value` bate com esse valor.

5. `test_blocked_by_is_none_when_pipeline_status_complete` (caso 5, ramo `None`) +
   `test_blocked_by_is_rule_when_pipeline_status_blocked` (caso 5, ramo bloqueado).
   Primeiro confirma `aurora_run["pipeline_status"] == "complete"` e que
   `aurora_metrics.blocked_by is None`. Segundo monta um manifest sintético via
   `copy.deepcopy(aurora_run)` com `pipeline_status` forçado para `"blocked"` e
   `gate_outcome.outcome` `"rejected"`, confirma `blocked_by` não-`None` (`str`).

6. `test_dificuldade_vs_esperada_derived_from_expected_vs_actual` — caso 6. Roda
   `generate_quality_report` cruzando Aurora x Fintech, valida existência de
   `MetricComparison` com `metric_name == "dificuldade_vs_esperada"` e que
   `aurora_value`/`fintech_value` estão no enum esperado
   (`"alinhada"`/`"mais_facil"`/`"mais_dificil"`).

7. `test_generate_quality_report_does_not_mutate_inputs` — caso 7. Faz
   `copy.deepcopy` dos 4 argumentos antes da chamada, invoca
   `generate_quality_report`, confere igualdade estrutural (`==`) dos 4 argumentos
   contra as cópias depois da chamada (deepcopy check de não-mutação).

8. `test_generated_report_passes_validate_quality_comparative_report` — caso 8.
   Confirma `isinstance(report, QualityComparativeReport)` e
   `validate_quality_comparative_report(report) == []`.

## Resultado do pytest

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_quality_comparative_reviewer.py -q
```

Saída (RED válido — falha por ausência do módulo, não por erro de teste):

```
=================================== ERRORS ====================================
_________ ERROR collecting tests/test_quality_comparative_reviewer.py _________
ImportError while importing test module 'tests/test_quality_comparative_reviewer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
  ...\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\test_quality_comparative_reviewer.py:20: in <module>
    from generator.quality_comparative_reviewer import (
E   ModuleNotFoundError: No module named 'generator.quality_comparative_reviewer'
=========================== short test summary info ===========================
ERROR tests/test_quality_comparative_reviewer.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.70s
```

`ModuleNotFoundError` é subclasse de `ImportError` — confirma RED esperado pela issue
("Testes devem falhar por `ImportError` (módulo ainda não existe)"). Falha ocorre na
linha do import do módulo inexistente (`generator.quality_comparative_reviewer`), não em
nenhum assert ou erro de sintaxe do arquivo de teste — coleta falha antes de qualquer
teste rodar, conforme esperado para RED em nível de módulo (8 testes presentes no
arquivo, todos bloqueados pelo mesmo `ImportError` de coleta).

## Confirmação de escopo — nenhum outro arquivo alterado

```bash
git status --short
```

```
 M .ai/issues/ISSUE-29+30.md
?? .ai/runs/ISSUE-29+30/
?? examples/caso_fintech.json
?? tests/test_quality_comparative_reviewer.py
```

- `tests/test_quality_comparative_reviewer.py`: único arquivo de teste/código criado
  nesta execução (permitido — único arquivo editável do step).
- `.ai/issues/ISSUE-29+30.md`: alterado apenas nas seções "## Estado" e "## Histórico"
  (permitido pelo protocolo do step).
- `.ai/runs/ISSUE-29+30/`: diretório de reports, inclui este arquivo novo
  (`STEP-05_EXECUTION.md`); demais reports (`STEP-01` a `STEP-04`) já existiam de steps
  anteriores.
- `examples/caso_fintech.json`: já existia de STEP-03/STEP-04, intocado nesta execução
  (confirmado — nenhum diff de conteúdo, apenas reaparece como `??` por não ter sido
  commitado ainda).
- `generator/quality_comparative_reviewer.py` **não foi criado** (proibido neste step,
  confirmado — comando `ls generator/quality_comparative_reviewer.py` resultaria em
  arquivo inexistente; módulo é importado apenas pelo teste, que falha por isso).

## Resultado

8 casos de teste criados em `tests/test_quality_comparative_reviewer.py`, cobrindo
exatamente os casos 1-8 da spec (`.ai/issues/ISSUE-29+30_SPEC.md`, seção "Testes
obrigatórios"): derivação de `CaseMetrics` para Aurora e Fintech, agrupamento
`findings_by_type` por prefixo de código, `densidade_documental` como soma de
`len(conteudo)`, `blocked_by` nos dois ramos (`None` e preenchido), `dificuldade_vs_esperada`
como comparação enum, imutabilidade de `generate_quality_report` via deepcopy check, e
validação do relatório via `validate_quality_comparative_report`. `pytest
tests/test_quality_comparative_reviewer.py -q` falha por `ModuleNotFoundError` (subclasse
de `ImportError`) na importação de `generator.quality_comparative_reviewer` — RED válido,
módulo real não foi criado neste step. Nenhum outro arquivo de código/teste alterado.
Pronto para revisão humana (high-risk/red) antes de avançar para STEP-06.

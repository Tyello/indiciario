# STEP-10 — Refactor: generator/quality_comparative_reviewer.py — Execution Report

Type: refactor (high-risk). Status: in_review.

## Estado encontrado antes do refactor

`generator/quality_comparative_reviewer.py` já estava em bom estado,
consequência dos STEP-06/STEP-08 (TDD + review aprovado):

- Densidade documental, vazamento de informação, pacing, dificuldade vs
  esperada, visual_score e num_documentos_total já estavam extraídos em
  funções nomeadas e testáveis (`_densidade_documental_comparison`,
  `_vazamento_info_comparison`, `_pacing_comparison`,
  `_dificuldade_vs_esperada_comparison`, `_visual_score_comparison`,
  `_num_documentos_total_comparison`). Nenhuma dessas lógicas estava
  inline em `generate_quality_report`.
- Números mágicos já nomeados em constantes no topo do arquivo:
  `_TOTAL_PIPELINE_STAGES`, `_VAZAMENTO_INFO_CODES`,
  `_VISUAL_FINDING_PREFIX`, `_FINDING_CODE_PREFIX_LEN`,
  `_FINDING_TYPE_KEYS`, `_PIPELINE_STATUS_COMPLETE`,
  `_DIFICULDADE_ORDER`, `_DIFICULDADE_ALINHADA`,
  `_DIFICULDADE_MAIS_FACIL`, `_DIFICULDADE_MAIS_DIFICIL`. Não havia
  literais como `"ER_006"` repetidos soltos no corpo das funções — o
  conjunto de códigos vive em `_VAZAMENTO_INFO_CODES` e é referenciado
  por nome.
- `generate_quality_report` já delega 100% das 6 métricas + `CaseMetrics`
  + `observations`/`recommendations` para helpers; não há lógica de
  cálculo inline a extrair.

Conclusão: a maior parte do objetivo do STEP-10 já estava cumprida em
STEP-06/STEP-08. Refactor real e legítimo identificado: duplicação entre
`_count_vazamento_info` e `_count_visual_score`.

## Refactor aplicado

Antes, as duas funções repetiam o mesmo padrão (extrair lista de
findings do manifest, somar 1 para cada finding cujo `code` satisfaz um
predicado):

```python
def _count_vazamento_info(manifest):
    findings = list(manifest.get("findings") or [])
    return sum(1 for finding in findings if finding.get("code") in _VAZAMENTO_INFO_CODES)

def _count_visual_score(manifest):
    findings = list(manifest.get("findings") or [])
    return sum(1 for finding in findings if str(finding.get("code") or "").startswith(_VISUAL_FINDING_PREFIX))
```

Extraído helper comum `_count_findings_matching(manifest, predicate)`
que centraliza a iteração/normalização de `code` para `str`, e as duas
funções agora delegam para ele com um predicado lambda:

```python
def _count_findings_matching(manifest, predicate):
    """Count findings in `manifest` whose `code` satisfies `predicate`."""
    findings = list(manifest.get("findings") or [])
    return sum(1 for finding in findings if predicate(str(finding.get("code") or "")))

def _count_vazamento_info(manifest):
    return _count_findings_matching(manifest, lambda code: code in _VAZAMENTO_INFO_CODES)

def _count_visual_score(manifest):
    return _count_findings_matching(manifest, lambda code: code.startswith(_VISUAL_FINDING_PREFIX))
```

Comportamento idêntico: `_count_vazamento_info` antes comparava
`finding.get("code")` (valor bruto, possivelmente `None`) contra o set;
agora compara `str(finding.get("code") or "")` contra o mesmo set. Como
`_VAZAMENTO_INFO_CODES` contém apenas strings não vazias (`ER_006`,
`ER_007`, `ER_008`), nem `None` nem `""` pertencem ao set em nenhum dos
dois casos — resultado idêntico para todas as entradas possíveis.

Import adicionado: `from collections.abc import Callable` (tipagem do
parâmetro `predicate`).

Nenhuma outra mudança de código. `_findings_by_type` e `_blocked_by` já
estavam corretamente nomeados/documentados e não duplicam lógica com
nenhuma outra função — não foram tocados.

## Resultado dos testes

### `tests/test_quality_comparative_reviewer.py`

```
18 passed in 1.17s
```

Idêntico ao baseline pré-refactor (mesmos 18 testes, mesmo resultado).

### `ruff check generator/quality_comparative_reviewer.py`

```
All checks passed!
```

### `pytest tests/ -q` (suite completa)

```
5 failed, 1346 passed, 3 skipped in 183.85s
```

As 5 falhas são as mesmas pré-existentes de symlink em ambiente Windows
(privilégio `SeCreateSymbolicLinkPrivilege` ausente), nada relacionado a
este arquivo:

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Baseline documentado na issue como "~5 falhas symlink Windows
pré-existentes" — confirma sem regressão nova.

## Restrições respeitadas

- Único arquivo editado: `generator/quality_comparative_reviewer.py`.
- `tests/test_quality_comparative_reviewer.py` não foi alterado.
- Nenhuma mudança de comportamento observável: os mesmos 18 testes
  passam, com os mesmos asserts, sem qualquer alteração de resultado.

## Arquivos alterados nesta execução

- `generator/quality_comparative_reviewer.py`: extraído
  `_count_findings_matching`, import de `Callable` adicionado.
- Criado: `.ai/runs/ISSUE-29+30/STEP-10_EXECUTION.md` (este relatório).
- Atualizado: `.ai/issues/ISSUE-29+30.md` (seção "## Estado",
  "### STEP-10" e "## Histórico").

## Resultado

Refactor pequeno e legítimo aplicado (deduplicação de
`_count_vazamento_info`/`_count_visual_score` via
`_count_findings_matching`). A maior parte do objetivo do STEP-10 (helpers
nomeados, sem números mágicos) já estava satisfeita em STEP-06/STEP-08 —
não havia trabalho cosmético a inventar. 18/18 testes do arquivo idênticos
antes/depois, `ruff check` limpo, suite completa sem regressão nova além
do baseline conhecido de symlinks Windows. Requer review humano (type:
refactor, high-risk).

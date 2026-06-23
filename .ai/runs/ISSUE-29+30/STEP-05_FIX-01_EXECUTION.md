# STEP-05_FIX-01 — Correção: cobertura de CaseMetrics.case_name — Execution Report

## Motivo da correção

STEP-05_REVIEW.md rejeitou (REJECTED minor): spec
(`.ai/issues/ISSUE-29+30_SPEC.md`, seção "Campos obrigatórios e derivação") define
`CaseMetrics.case_name` como campo do dataclass, distinto de `case_ref`. Testes 1 e 2
("todos os campos preenchidos corretamente") não verificavam `case_name`.

## Confirmação do campo correto do blueprint

Spec (`.ai/issues/ISSUE-29+30_SPEC.md`, tabela "Campos obrigatórios e derivação"):
`case_name` deriva de `manifest["case_ref"]` ou extraído do blueprint.

Schema `Blueprint` (`generator/models.py`, linha 569): campo `titulo: str` é o nome do
caso no nível raiz do blueprint (confirmado via `grep -n "^class\|titulo"` —
classe raiz do JSON do blueprint usa `titulo` para o nome do caso, ex.:
`examples/caso_canonico_intermediario.json["titulo"]` == "O Último Brinde do Hotel
Aurora"). Campo usado nos asserts: `aurora_blueprint["titulo"]` /
`fintech_blueprint["titulo"]`.

## Alteração — `tests/test_quality_comparative_reviewer.py`

Único arquivo editado. Dois asserts adicionados:

Teste 1 (`test_case_metrics_derived_from_aurora_manifest_has_all_fields`), após
`assert isinstance(metrics, CaseMetrics)`:
```python
assert metrics.case_name == aurora_blueprint["titulo"]
```

Teste 2 (`test_case_metrics_derived_from_fintech_manifest_has_all_fields`), após
`assert isinstance(metrics, CaseMetrics)`:
```python
assert metrics.case_name == fintech_blueprint["titulo"]
```

Nenhum outro trecho do arquivo alterado. `generator/quality_comparative_reviewer.py`
não criado/alterado (restrição respeitada).

## Resultado pytest

```
py -3 -m pytest tests/test_quality_comparative_reviewer.py -q
```

```
ImportError while importing test module '...tests\test_quality_comparative_reviewer.py'.
tests\test_quality_comparative_reviewer.py:20: in <module>
    from generator.quality_comparative_reviewer import (
E   ModuleNotFoundError: No module named 'generator.quality_comparative_reviewer'
1 error in 0.95s
```

RED esperado e correto — módulo sob teste ainda não existe. Nenhuma regressão de
sintaxe/lógica introduzida pela correção.

## Restrições respeitadas

- Apenas `tests/test_quality_comparative_reviewer.py` editado.
- `generator/quality_comparative_reviewer.py` não criado.

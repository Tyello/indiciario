# STEP-11-FIX — CORRECTION: remover guard RED obsoleto

## O que foi feito

Removidas as 2 linhas do guard RED obsoleto em
`tests/test_accessibility_reviewer.py` (linhas 51-52 originais):

```python
with pytest.raises(ModuleNotFoundError):
    import generator.accessibility_reviewer  # noqa: F401
```

Nenhuma outra linha alterada. `import pytest` (linha 35) mantido intacto
mesmo sem outro uso no arquivo — fora da allowlist do step tocar esse import.
Nenhum caso de teste (33-48) alterado. `generator/accessibility_reviewer.py`
e `generator/visual_reviewer.py` não tocados.

## Diff

Arquivo é untracked no git (criado em STEP-09, nunca commitado), então
`git diff` não mostra histórico — confirmação feita por grep: guard ausente,
docstring/imports/casos de teste intactos.

## Comandos executados

```
.venv/Scripts/python.exe -m pytest tests/test_accessibility_reviewer.py -q
.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py -q
.venv/Scripts/python.exe -m pytest tests/test_visual_accessibility_review_report_schema.py -q
```

Resultados:

- `tests/test_accessibility_reviewer.py` → **16 passed** (antes: erro de
  coleta, 0 executados).
- `tests/test_visual_reviewer.py` → **16 passed** (intacto).
- `tests/test_visual_accessibility_review_report_schema.py` → **16 passed**
  (intacto).

Total: **48/48 passed**.

## Arquivos alterados

- `tests/test_accessibility_reviewer.py` (removidas as 2 linhas do guard
  `pytest.raises(ModuleNotFoundError)`; nenhuma outra alteração).

## Arquivos NÃO alterados

- `generator/accessibility_reviewer.py`
- `generator/visual_reviewer.py`
- casos de teste 33-48 em `tests/test_accessibility_reviewer.py`

## Done

Critério do step atingido: 48/48 testes verdes nos três arquivos. `STATUS`
da issue volta de `blocked` para `running`.

# STEP-12 — REFACTOR: helpers compartilhados — Review Report

## Veredito

APROVADO.

## Checks

- Refactor puro confirmado: novo helper privado `_exceeds_conteudo_limit(document) -> bool`
  em `generator/visual_reviewer.py`, logo após `_document_text`. Prefixo `_`,
  sem API pública nova.
- VR_001 (`visual_reviewer.py`) e AR_002 (`accessibility_reviewer.py`) ambos
  usam o helper em vez do predicado duplicado `len(_document_text(document)) >
  MAX_CONTEUDO_CHARS`. `accessibility_reviewer.py` importa
  `_exceeds_conteudo_limit` de `visual_reviewer.py`, mantém `MAX_CONTEUDO_CHARS`
  (ainda usado na mensagem do finding).
- Nenhum comportamento novo: predicado é logicamente idêntico ao código
  anterior, só extraído.
- Nenhum teste novo: `tests/test_visual_reviewer.py` e
  `tests/test_accessibility_reviewer.py` permanecem com os mesmos 16 casos
  cada (verificado contra histórico STEP-06/07/09/10, sem casos adicionados).
- Nenhuma mudança de assinatura pública: `review_visual`,
  `review_accessibility`, dataclasses e demais helpers exportados intactos.
- Allowlist do step (`generator/visual_reviewer.py`,
  `generator/accessibility_reviewer.py`) respeitada — `git status --short`
  mostra só esses dois arquivos como modificados entre os rastreados pelo
  step; demais entradas untracked pertencem a steps anteriores (não
  commitados, fora do escopo desta revisão).

## Reexecução

```
.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py tests/test_accessibility_reviewer.py tests/test_visual_accessibility_review_report_schema.py -q
→ 48 passed
```

Confirma 48/48: 16 (`test_visual_reviewer.py`) + 16
(`test_accessibility_reviewer.py`) + 16
(`test_visual_accessibility_review_report_schema.py`).

## Decisão

STEP-12 aprovado. Avançar para STEP-13 (VALIDATION: suíte completa) fica a
critério do orquestrador.

# STEP-12 — REFACTOR: helpers compartilhados — Execution Report

## Objetivo
Extrair helper de varredura compartilhado entre VR_001 (`visual_reviewer.py`) e
AR_002 (`accessibility_reviewer.py`), sem alterar comportamento observável;
confirmar ausência de números mágicos soltos.

## Diagnóstico
Duplicação encontrada: VR_001 e AR_002 tinham o mesmo loop
`for index, document in enumerate(documentos): texto = _document_text(document);
if len(texto) > MAX_CONTEUDO_CHARS: ...`. `_document_text`/`_enum_value` já
eram compartilhados desde o STEP-11 (importados em `accessibility_reviewer.py`).
Faltava extrair o predicado de limite em si.

## Alterações

### `generator/visual_reviewer.py`
- Adicionado helper `_exceeds_conteudo_limit(document) -> bool`, logo após
  `_document_text`, na seção "Blueprint field helpers (read-only)":
  ```python
  def _exceeds_conteudo_limit(document: Any) -> bool:
      """Whether ``document``'s concatenated ``conteudo`` is above
      :data:`MAX_CONTEUDO_CHARS`. Shared by VR_001 and AR_002."""

      return len(_document_text(document)) > MAX_CONTEUDO_CHARS
  ```
- VR_001 atualizado para usar o helper:
  `for index, document in enumerate(documentos): if _exceeds_conteudo_limit(document): ...`
  (removida a linha intermediária `texto = _document_text(document)`).

### `generator/accessibility_reviewer.py`
- Import troca `_document_text` por `_exceeds_conteudo_limit` (vindo de
  `generator.visual_reviewer`).
- AR_002 atualizado para usar o helper, mesma forma do VR_001.
- `MAX_CONTEUDO_CHARS` mantido no import: ainda usado na mensagem do finding
  (`f"acima de {MAX_CONTEUDO_CHARS} caracteres..."`).

Nenhum outro arquivo alterado. Nenhuma regra nova, nenhum teste novo, nenhuma
API pública nova (helper é privado, prefixo `_`).

## Números mágicos
Revisão das constantes existentes — todas nomeadas, nenhuma solta no corpo das
regras:
- `MAX_CONTEUDO_CHARS` (VR_001/AR_002)
- `VISUAL_DOC_TYPES` (VR_006)
- `MAX_DOCS_PER_ENVELOPE` (AR_001)
- `MAX_CROSS_REFS` (AR_004)

## Comandos executados

```
.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py -q
→ 16 passed

.venv/Scripts/python.exe -m pytest tests/test_accessibility_reviewer.py -q
→ 16 passed

.venv/Scripts/python.exe -m pytest tests/test_visual_accessibility_review_report_schema.py -q
→ 16 passed

.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py tests/test_accessibility_reviewer.py tests/test_visual_accessibility_review_report_schema.py -q
→ 48 passed
```

## Resultado
48/48 testes verdes após o refactor (16 visual + 16 accessibility + 16 schema).
Nenhum comportamento observável alterado — apenas extração de helper privado
reduzindo duplicação de 2 linhas para 1 chamada em cada um dos dois call sites
(VR_001 e AR_002). `git status --short` confirma que somente
`generator/visual_reviewer.py` e `generator/accessibility_reviewer.py` foram
tocados entre os arquivos da allowlist (demais entradas untracked são de steps
anteriores, ainda não commitados).

Pronto para revisão.

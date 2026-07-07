# ISSUE-40.1 — STEP-03_FIX-01 — Execution Report

Owner: executor
Type: correction (high-risk)
Status: done — aguardando revisão

## Objetivo do step

Corrigir escopo de `05_carta.html` (tirar Libre Baskerville, que nunca é
aplicada de fato — `.doc-family-letter .page` sobrepõe com Georgia) e remover
`_injetar_fontface_warmup` se a suíte confirmar que não é mais necessário.

## O que foi feito

### 1. `tests/test_font_vendoring.py`

Removida a entrada `"05_carta.html": ["Libre Baskerville"]` de `CUSTOM_FONTS`.
Nenhum outro ajuste no teste (assert e mecânica de medição via
`canvas.font` permanecem intactos).

### 2. `generator/renderer.py`

- Removida a chamada `_injetar_fontface_warmup(html)` em
  `_injetar_css_documental` — agora a função só injeta o
  `<style data-indiciario-visual-system>` e retorna `html` sem marcação
  extra.
- Rodado `pytest tests/test_font_vendoring.py -q` **sem** o warm-up: **8/8
  GREEN** (8 templates restantes no inventário, já que 05 saiu do escopo).
  Nenhum outro par template×fonte quebrou.
- Como a suíte confirmou que o warm-up não é necessário para nenhum par
  restante, removido código morto associado em `generator/renderer.py`:
  `FONTFACE_WARMUP_FAMILIES`, `_fontface_warmup_html()`,
  `_injetar_fontface_warmup()`. Confirmado via grep (`warmup|Warmup|WARMUP`
  em `*.py`) que não sobra nenhuma referência no repositório.

Por que os 8 pares restantes passam sem o warm-up: o teste renderiza cada
template completo via Playwright e mede a fonte resolvida com
`canvas.font` dentro da própria página renderizada — para os templates que
permanecem no escopo, a fonte custom é de fato aplicada em texto visível na
cascata CSS real do template (não há outro caso de `.doc-family-*` com
especificidade maior sobrepondo o `body` como acontecia em `05_carta.html`),
então `document.fonts.ready` é disparado naturalmente pelo próprio uso da
fonte no layout, sem precisar de nenhuma marcação de warm-up.

### 3. `.ai/issues/ISSUE-40.1.md`

- Nota de decisão pós-STEP-01 (bloco de histórico acima do STEP-01):
  `Libre Baskerville (05, 11)` → `Libre Baskerville (11)`.
- Adicionada nova linha de nota registrando a decisão pós-STEP-03_FIX-01
  (05 fora do escopo, Georgia é a fonte real do template).

## Comandos executados

```
.venv/Scripts/python.exe -m pytest tests/test_font_vendoring.py -q
→ 8 passed in 2.08s

.venv/Scripts/python.exe -m pytest tests/ -q
→ 5 failed, 1385 passed, 3 skipped in 193.71s
  (os 5 failed são os mesmos pré-existentes documentados no STEP-03:
  test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed,
  test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails,
  test_blind_bundle_leak_checker.py::test_symlink_manifest_fails,
  test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail,
  test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail
  — todos WinError 1314, symlink sem privilégio no Windows, ambiente, não
  relacionados a este step. 1385 vs 1386 do STEP-03: diferença de 1 é o caso
  parametrizado 05_carta.html×Libre Baskerville removido do escopo.)

.venv/Scripts/python.exe -m ruff check generator/
→ All checks passed!

.venv/Scripts/python.exe -m ruff check tests/
→ pré-existentes em test_accessibility_reviewer.py e
  test_blind_solve_run_record.py, arquivos não tocados neste step.
  tests/test_font_vendoring.py isolado: All checks passed!
```

## Verificação do "proibido"

- Nenhum mecanismo de warm-up foi reintroduzido.
- `assets/fonts/*.woff2` e `templates/styles/document_system.css` não
  tocados.
- `templates/05_carta.html` não alterado (conteúdo/narrativa intactos) —
  só a expectativa no teste mudou.

## Done quando (checklist da issue)

- [x] `CUSTOM_FONTS` não lista mais Libre Baskerville para `05_carta.html`.
- [x] `_injetar_fontface_warmup` removido — suíte confirmou não ser
  necessário para os pares restantes.
- [x] `pytest tests/test_font_vendoring.py -q` GREEN para os pares
  restantes (8/8).
- [x] `pytest tests/ -q` sem regressão nova (mesmos 5 failed pré-existentes).
- [x] Inventário na issue corrigido (`Libre Baskerville (11)`).

## Transição

`Type: correction` é high-risk. `STATUS`, `NEXT_ACTION` e `REVIEW_STATUS`
atualizados na issue para review obrigatória.

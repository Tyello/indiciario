# Execution Report — ISSUE-40.2 STEP-02

STEP: STEP-02
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo

Criar `tests/test_gate_font_fidelity.py` com dois testes que evidenciam a
lacuna do gate atual quanto a fallback silencioso de fonte: um que passa
hoje (gate atual não pega o fallback) e um que falha hoje (critério real,
GREEN só no STEP-03).

## Arquivos lidos

- .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md
- .ai/issues/ISSUE-40.2_SPEC.md
- generator/canonical_quality_gate.py (evaluate_for_canonical, QualificationCriterion, CanonicalQualification)
- generator/renderer.py (DOCUMENT_SYSTEM_CSS_PATH, _document_system_css, _inline_fontface_urls)
- generator/pipeline_runner.py (run_pipeline)
- tests/test_font_vendoring.py (_montar_html, _MEDIR_FONTE_JS, CUSTOM_FONTS, fixture browser)
- tests/test_canonical_quality_gate.py (padrão de uso de run_pipeline + evaluate_for_canonical)
- templates/styles/document_system.css (blocos @font-face)

## Arquivos alterados

- tests/test_gate_font_fidelity.py (novo)

## Comandos executados

- `.venv/Scripts/python.exe -m pytest tests/test_gate_font_fidelity.py -q`
  → `1 failed, 1 passed in 1.88s`.
  - `test_gate_currently_misses_font_fallback` PASSOU.
  - `test_gate_catches_font_fallback` FALHOU: `ImportError: cannot import
    name 'evaluate_font_fidelity' from 'generator.canonical_quality_gate'`.

## O que foi feito

- Fixture `css_com_fonte_removida` (tmp_path + monkeypatch): copia
  `document_system.css` real, remove via regex o bloco `@font-face`
  inteiro de `'DM Sans'` (fonte de `01_email.html`), grava em `tmp_path` e
  faz `monkeypatch.setattr(generator.renderer, "DOCUMENT_SYSTEM_CSS_PATH",
  <caminho-tmp>)`. Fixture compartilhada pelos dois testes — mesma
  montagem, mesmo template (`01_email.html`), mesma fonte (`DM Sans`).
- `test_gate_currently_misses_font_fallback`:
  1. Confirma via medição real do Chromium (reusa `_montar_html` e
     `_MEDIR_FONTE_JS` de `tests/test_font_vendoring.py`, técnica de
     `canvas.measureText` da 40.1, fixture `browser` importada do mesmo
     módulo) que a fonte de fato cai em fallback nesta montagem.
  2. Roda `run_pipeline` sobre `examples/caso_canonico_iniciante.json` e
     chama `evaluate_for_canonical(blueprint, manifest, "iniciante")` — o
     gate real usado hoje.
  3. Assert: `"font_fidelity"` não está entre os nomes de
     `qualification.criteria_results` — evidencia que o gate atual é cego
     ao problema mesmo com a fonte comprovadamente quebrada.
- `test_gate_catches_font_fallback`: chama
  `generator.canonical_quality_gate.evaluate_font_fidelity(templates=
  ["01_email.html"], browser=browser)` esperando `QualificationCriterion`
  com `status="blocker"` e `recommendation` citando template ("01_email.html")
  e fonte ("DM Sans"). Import deferido para dentro da função (não no topo
  do módulo) para não quebrar a coleta do teste 1 quando a função não
  existe.

## Evidência de aderência ao tipo

- RED real, não simulado: rodei a suíte e capturei a saída (`1 failed, 1
  passed`) antes de escrever este relatório.
- `test_gate_currently_misses_font_fallback` passa hoje pela razão certa
  (ausência do check), não por acidente — o teste primeiro comprova via
  medição real que a fonte quebrou, só então verifica que o gate ignora
  isso.
- `test_gate_catches_font_fallback` falha hoje pela razão certa
  (`ImportError` de função que só existe a partir do STEP-03), não por bug
  de teste.
- Nenhum arquivo em `generator/` tocado. `tests/test_font_vendoring.py`
  não alterado (só importado).

## Divergências

- Nenhuma em relação ao STEP-01: nome de critério `font_fidelity` seguido
  à risca; nenhum prefixo `GP_0XX` reusado; nenhum stage novo introduzido.
- `test_gate_catches_font_fallback` falha hoje por `ImportError` (não por
  `AssertionError` sobre o critério retornado) — esperado, já que a
  função nem existe ainda; STEP-03 introduz `evaluate_font_fidelity` e o
  teste passa a exercer a lógica real do critério.

## Observações para revisão

- Confirmar que a comparabilidade exigida pelo STEP-02 ("os dois testes
  usam a mesma montagem") está satisfeita: ambos dependem da fixture
  `css_com_fonte_removida` (mesmo template/fonte), embora só o primeiro
  faça a medição Playwright direta — o segundo delega essa medição para
  dentro de `evaluate_font_fidelity` (ainda não implementada).
- `test_gate_currently_misses_font_fallback` ficará sem sentido depois do
  STEP-03 (quando `font_fidelity` passar a existir de fato no gate) — o
  STEP-04 da issue já prevê essa revisão/remoção.

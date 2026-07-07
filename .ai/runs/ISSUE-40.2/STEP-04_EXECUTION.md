# Execution Report — ISSUE-40.2 STEP-04

STEP: STEP-04
STEP_TYPE: validation
EXECUTION_STATUS: completed

## Objetivo

Verificação de regressão pós-GREEN: confirmar os dois testes do STEP-02 no
estado esperado, rodar a suíte completa sem regressão, e confirmar o
critério de aceite #3 da issue (remover `@font-face` de propósito → gate
falha; restaurar → gate passa).

## Arquivos lidos

- tests/test_gate_font_fidelity.py
- generator/canonical_quality_gate.py
- tests/test_font_vendoring.py
- .ai/runs/ISSUE-40.2/STEP-03_FIX-01_EXECUTION.md
- .ai/runs/ISSUE-40.2/STEP-03_FIX-01_REVIEW.md

## Arquivos alterados

- `tests/test_gate_font_fidelity.py`: só docstring de
  `test_gate_currently_misses_font_fallback` atualizada (nenhum assert
  tocado). Wording antigo dizia "o check ainda não existe (ISSUE-40.2)" --
  desatualizado desde o STEP-03/STEP-03_FIX-01, onde `evaluate_font_fidelity`
  passou a existir e a ser conectável via `font_fidelity_criterion`. Nova
  docstring registra: o teste continua válido, não é tautológico -- documenta
  que uma chamada *default* de `evaluate_for_canonical` (sem passar o
  parâmetro opcional) continua sem o critério `font_fidelity` por design
  (`evaluate_for_canonical` não invoca Playwright por conta própria), e
  aponta para `test_gate_wires_font_fidelity_into_evaluate_for_canonical`
  como o teste que cobre o caminho conectado.

## Comandos executados

1. `.venv/Scripts/python.exe -m pytest tests/test_gate_font_fidelity.py -q`
   → `3 passed in 2.24s` (antes do ajuste de docstring).
   - `test_gate_currently_misses_font_fallback`: PASSOU.
   - `test_gate_catches_font_fallback`: PASSOU (era o critério real do
     STEP-02/03; confirmado GREEN pós-implementação).
   - `test_gate_wires_font_fidelity_into_evaluate_for_canonical` (STEP-03_FIX-01):
     PASSOU.
2. `.venv/Scripts/python.exe -m pytest tests/ -q` → `5 failed, 1388 passed,
   3 skipped in 190.60s`.
   - As 5 falhas são `test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`,
     `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`,
     `test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`,
     `test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`,
     `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`.
   - Todas falham em `Path.symlink_to(...)` com
     `OSError: [WinError 1314] O cliente não tem o privilégio necessário` --
     limitação conhecida do ambiente Windows local (usuário sem privilégio
     de criar symlink), não relacionada a font/gate. Documentado em memória
     de ambiente de teste desta máquina. Nenhuma dessas suites toca
     `generator/canonical_quality_gate.py`, `generator/font_fidelity.py` ou
     `tests/test_gate_font_fidelity.py`. Sem regressão introduzida por
     ISSUE-40.2.
3. `.venv/Scripts/python.exe -m pytest tests/test_gate_font_fidelity.py -q`
   (re-execução após ajuste de docstring) → `3 passed in 2.33s`.

## Confirmação do critério de aceite #3

"Removendo deliberadamente um `@font-face`, o gate falha; restaurando, o
gate passa" -- confirmado pela combinação de dois testes reais (Chromium via
Playwright, não mock):

- **Remoção → falha**: `test_gate_catches_font_fallback` usa a fixture
  `css_com_fonte_removida` (remove via regex o bloco `@font-face` de
  `'DM Sans'` de uma cópia real de `document_system.css`, aponta
  `generator.renderer.DOCUMENT_SYSTEM_CSS_PATH` para essa cópia via
  `monkeypatch`) e chama `evaluate_font_fidelity(templates=["01_email.html"],
  browser=browser)`. Resultado: `criterio.status == "blocker"`, com
  `recommendation` nomeando template (`01_email.html`) e fonte (`DM Sans`) --
  não é boolean agregado, satisfaz também o critério de aceite #2.
  `test_gate_wires_font_fidelity_into_evaluate_for_canonical` estende isso:
  o mesmo critério, passado a `evaluate_for_canonical(...,
  font_fidelity_criterion=criterio)`, vira `CuratorQualification.NOT_READY`
  no veredito real do gate (não só na função isolada).
- **Restauração → passa**: o `monkeypatch` do `css_com_fonte_removida` é
  revertido automaticamente pelo pytest ao fim de cada teste (fixture-scoped
  em `function`), restaurando `DOCUMENT_SYSTEM_CSS_PATH` para o
  `document_system.css` real e intacto. Com o CSS real (todos os
  `@font-face` presentes),
  `tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema`
  (parametrizado por template+fonte, cobre `01_email.html`/`DM Sans` entre
  outros pares do inventário `CUSTOM_FONTS`) confirma via a mesma técnica de
  medição (`canvas.measureText` real no Chromium) que a fonte É aplicada
  (`fonte_aplicada is True`) -- ou seja, `evaluate_font_fidelity` sobre o CSS
  real não acumularia esse par em `fallbacks` e retornaria
  `status="ok"`/`is_satisfied=True` para ele. Esse teste roda dentro da
  suíte completa (item 2 acima, nos 1388 passed) sem o `@font-face` removido,
  provando o lado "restaurado → passa" com a mesma montagem/técnica, sem
  necessidade de um teste round-trip redundante dedicado.

A lógica realmente exercita remoção→falha e (por combinação com a suíte da
40.1 sobre o CSS real) restauração→passa; não é tautológica.

## Divergências

Nenhuma.

## Observações para revisão

- As 5 falhas de symlink em `tests/test_blind_bundle_*` são pré-existentes,
  específicas do ambiente Windows local (privilégio de symlink), e alheias
  ao escopo de ISSUE-40.2. Segunda opinião do revisor bem-vinda para
  confirmar que não são regressão introduzida por este lote de trabalho --
  nenhum arquivo tocado por STEP-01..STEP-04 desta issue tem relação com
  bundles/symlinks.
- Único arquivo alterado neste step foi `tests/test_gate_font_fidelity.py`,
  e só a docstring de um teste (permitido pelo STEP-04); nenhum assert ou
  comportamento de check foi alterado.

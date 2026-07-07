# Execution Report — ISSUE-40.2 STEP-03_FIX-01

STEP: STEP-03_FIX-01
STEP_TYPE: correction
EXECUTION_STATUS: completed

## Objetivo

Corrigir DVG-001 do STEP-03_REVIEW.md: `evaluate_font_fidelity` existia mas
não era chamada por `evaluate_for_canonical` nem por qualquer consumidor real
do gate -- função morta frente ao critério de aceite #1 da issue. Conectar
via parâmetro opcional em `evaluate_for_canonical`, sem reintroduzir
Playwright dentro do gate.

## Arquivos lidos

- .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md
- .ai/runs/ISSUE-40.2/STEP-03_EXECUTION.md
- .ai/runs/ISSUE-40.2/STEP-03_REVIEW.md
- generator/canonical_quality_gate.py
- generator/font_fidelity.py
- tests/test_gate_font_fidelity.py
- tests/test_canonical_quality_gate.py

## Arquivos alterados

- `generator/canonical_quality_gate.py`:
  - `evaluate_for_canonical` passa a aceitar parâmetro keyword-only
    `font_fidelity_criterion: QualificationCriterion | None = None`.
  - Quando fornecido, o critério é anexado a `criteria_results` (mesmo ponto
    onde `pipeline_status` é anexado, antes do cálculo de `observations` e
    de `has_blocker`/`has_out_of_range`/`has_unevaluated`) -- participa do
    veredito `qualification` pela mesma lógica dos demais critérios (status
    `"blocker"` força `CuratorQualification.NOT_READY`).
  - Nenhuma chamada a Playwright dentro de `evaluate_for_canonical` --
    o critério chega pronto (construído por quem invoca o gate via
    `evaluate_font_fidelity`, que continua exigindo um `browser` vivo).
  - Docstring atualizada explicando o novo parâmetro e a decisão de não
    invocar Playwright aqui.
- `tests/test_gate_font_fidelity.py`: adicionado
  `test_gate_wires_font_fidelity_into_evaluate_for_canonical` -- constrói o
  critério via `evaluate_font_fidelity` (mesma montagem com `@font-face`
  removido) e confirma que, passado a `evaluate_for_canonical`, o critério
  aparece em `criteria_results` e o veredito vira
  `CuratorQualification.NOT_READY`. Os dois testes existentes
  (`test_gate_currently_misses_font_fallback`, `test_gate_catches_font_fallback`)
  não foram alterados: o primeiro continua válido porque chamadas de
  `evaluate_for_canonical` **sem** o novo parâmetro continuam sem
  `"font_fidelity"` em `criteria_results` (comportamento antigo preservado
  por design, conforme pedido no STEP-03_FIX-01 e no STEP-01).

## Comandos executados

- `.venv/Scripts/python.exe -m pytest tests/test_gate_font_fidelity.py -q`
  → `3 passed in 2.35s`.
- `.venv/Scripts/python.exe -m pytest tests/test_canonical_quality_gate.py -q`
  → `21 passed in 1.85s` (chamadas existentes de `evaluate_for_canonical`
  sem o novo parâmetro continuam funcionando, sem regressão).
- `.venv/Scripts/python.exe -m ruff check generator/` → `All checks passed!`

## O que foi feito

Wiring mínimo pedido pela revisão: `evaluate_for_canonical` ganhou o
parâmetro opcional `font_fidelity_criterion`, anexa o critério a
`criteria_results` quando presente, e deixa o cálculo de `qualification`
(via `has_blocker`) tratá-lo igual aos demais critérios -- sem duplicar
lógica de blocker, sem tocar `pipeline_runner.py` (fora de escopo desta
correção, conforme instrução), sem reintroduzir Playwright no módulo do
gate.

## Divergências

Nenhuma. Segui exatamente o mecanismo decidido no STEP-01 e exigido pela
revisão (DVG-001): parâmetro opcional, append a `criteria_results`,
preservação de chamadas antigas.

## Observações para revisão

- `pipeline_runner.py` não foi tocado -- continua sem invocar
  `evaluate_font_fidelity`/passar `font_fidelity_criterion`. Isso fica
  fora do escopo desta correção por instrução explícita ("Não toque
  pipeline_runner.py"). Se o critério de aceite #1 da issue for lido como
  exigindo que o pipeline real (não só a função `evaluate_for_canonical`)
  produza esse critério automaticamente end-to-end, ainda falta essa
  invocação em algum orquestrador -- sinalizo para a próxima revisão/step
  decidir se isso é escopo do STEP-04 (verificação) ou de uma issue futura
  (40.3+ já citam reuso do gate visual).

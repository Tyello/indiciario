# Review Report — ISSUE-40.2 STEP-03_FIX-01

STEP: STEP-03_FIX-01
STEP_TYPE: correction
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados

- generator/canonical_quality_gate.py
- tests/test_gate_font_fidelity.py (só se precisar ajustar teste para cobrir o wiring)

## Arquivos alterados encontrados (`git status --short` + `git diff --name-only`)

- generator/canonical_quality_gate.py (M)
- tests/test_gate_font_fidelity.py (novo, ajustado — herdado do STEP-02/STEP-03)
- .ai/issues/ISSUE-40.2.md (M, controle)
- tests/test_font_vendoring.py (M) — herdado do STEP-03 (extração de helper), já aprovado como dentro de escopo no STEP-03_REVIEW.md; nenhuma mudança nova nesta correção.
- generator/font_fidelity.py (novo) — herdado do STEP-03, não tocado nesta correção.

Dentro do escopo de arquivos editáveis do STEP-03_FIX-01. `generator/pipeline_runner.py` confirmado intocado (`git status --short generator/pipeline_runner.py` sem saída) — respeita a proibição explícita do contrato.

## Comandos re-executados nesta revisão

- `pytest tests/test_gate_font_fidelity.py -q` → `3 passed in 2.36s`. Confirma o relatado.
- `pytest tests/test_canonical_quality_gate.py -q` → `21 passed in 1.75s`. Confirma ausência de regressão nas chamadas antigas de `evaluate_for_canonical`.
- `ruff check generator/` → `All checks passed!`. Confirma o relatado.

## Verificações

- [x] Execution report existe
- [x] Type válido (correction)
- [x] Arquivos alterados dentro da allowlist do STEP-03_FIX-01
- [x] Comandos executados dentro do permitido
- [x] `evaluate_for_canonical` aceita `font_fidelity_criterion: QualificationCriterion | None = None` (keyword-only), sem quebrar chamadas antigas (21 testes de `test_canonical_quality_gate.py` chamam sem o parâmetro e continuam passando)
- [x] Quando fornecido, o critério é anexado a `criteria_results` e participa de `has_blocker`/`qualification` como os demais critérios (visto no diff: append antes do cálculo de `observations`)
- [x] Nenhum import/chamada de Playwright dentro de `evaluate_for_canonical` — `evaluate_font_fidelity` (import de `generator.font_fidelity`) permanece função separada, chamada por quem invoca o gate
- [x] `pipeline_runner.py` não tocado (confirmado via `git status --short`)
- [x] Novo teste `test_gate_wires_font_fidelity_into_evaluate_for_canonical` prova fim-a-fim: `font_fidelity` aparece em `criteria_results` e `qualification.qualification == CuratorQualification.NOT_READY` quando o critério é passado — endereça exatamente a lacuna do DVG-001 (função antes morta do ponto de vista do critério de aceite #1)
- [x] Sem escopo novo (nenhum outro check visual, nenhuma alteração em `pipeline_runner.py`)

## Divergências

Nenhuma. DVG-001 do STEP-03_REVIEW.md resolvido: `evaluate_font_fidelity` deixou de ser função morta — `evaluate_for_canonical` agora a consome via parâmetro opcional, exatamente o mecanismo que o STEP-01 já havia recomendado e que a rejeição exigiu.

Nota não-bloqueante (mesma observação já registrada no execution report): `pipeline_runner.py` ainda não invoca `evaluate_font_fidelity`/passa `font_fidelity_criterion` automaticamente — isso foi proibido nesta correção por escopo, não é divergência desta issue. Fica para orquestrador decidir se cabe no STEP-04 (verificação) ou issue futura.

## Decisão

APPROVED

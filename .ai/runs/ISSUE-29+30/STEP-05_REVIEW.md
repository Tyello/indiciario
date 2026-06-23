# STEP-05 — RED: testes do quality_comparative_reviewer (casos 1-8) — Review Report

Veredito: **REJECTED minor**.

## Verificações executadas

1. `tests/test_quality_comparative_reviewer.py` existe, 8 funções de teste (mais a
   complementar do caso 5), cobrindo os 8 casos da spec (`.ai/issues/ISSUE-29+30_SPEC.md`,
   seção "Testes obrigatórios", casos 1-8): CaseMetrics Aurora, CaseMetrics Fintech,
   findings_by_type, densidade_documental, blocked_by (dois ramos), dificuldade_vs_esperada,
   imutabilidade, validate_quality_comparative_report.

2. Import: `from generator.quality_comparative_reviewer import (CaseMetrics,
   MetricComparison, QualityComparativeReport, generate_quality_report,
   validate_quality_comparative_report)` — assinaturas conforme spec
   (`generate_quality_report(aurora_manifest, fintech_manifest, aurora_blueprint,
   fintech_blueprint) -> QualityComparativeReport`).

3. `pytest tests/test_quality_comparative_reviewer.py -q` rodado:
   ```
   ModuleNotFoundError: No module named 'generator.quality_comparative_reviewer'
   1 error in 0.60s
   ```
   RED válido — falha de coleta por import ausente, não erro de sintaxe/lógica de teste.

4. `git status --short`:
   ```
    M .ai/issues/ISSUE-29+30.md
   ?? .ai/runs/ISSUE-29+30/
   ?? examples/caso_fintech.json
   ?? tests/test_quality_comparative_reviewer.py
   ```
   `examples/caso_fintech.json` já existia de STEP-03/04 (não criado/alterado nesta
   execução — confirmado via report do executor e ausência de diff). Nenhum arquivo em
   `generator/` criado ou alterado. `generator/quality_comparative_reviewer.py` não existe
   (`ls generator/ | grep quality` vazio). TDD RED respeitado.

5. Fixtures `aurora_run`/`fintech_run` com `scope="module"` chamam `run_pipeline` uma
   única vez cada (evita rodar a pipeline 8x redundantemente). Números usados no caso 3
   (`findings_by_type`: `NR_*: 0`, `ER_*: 4`) batem com os achados documentados em STEP-04
   (ER_006 x2, ER_007 x2 no manifest Fintech real). Fixture é razoável e reflete dados reais.

6. Asserts não tautológicos: caso 4 recalcula `densidade_documental` independentemente
   somando `len(conteudo)` de cada documento do blueprint e compara contra o valor do
   relatório; caso 3 usa contagens reais documentadas (não valores triviais/sempre-True);
   caso 7 faz `copy.deepcopy` dos 4 argumentos antes e depois da chamada, comparando
   estruturalmente; caso 6 restringe contra enum fechado
   (`"alinhada"/"mais_facil"/"mais_dificil"`). Lógica de cada assert valida comportamento
   real esperado pela spec.

## Achado — REJECTED minor

A spec (`.ai/issues/ISSUE-29+30_SPEC.md`, seção "Campos obrigatórios e derivação") define
`CaseMetrics.case_name` como campo do dataclass `CaseMetrics` (distinto de `case_ref`).
Nenhum dos 8 casos de teste verifica `case_name`. Os testes 1 e 2 (`CaseMetrics` derivado
de Aurora/Fintech, "todos os campos preenchidos corretamente") cobrem `case_ref`,
`dificuldade_esperada`, `pipeline_status`, `stages_completed`, `findings_count`,
`findings_by_type`, `notes` — mas omitem `case_name`. Caso 1/2 da spec exige
explicitamente "todos os campos preenchidos corretamente"; faltar a verificação de
`case_name` é lacuna de cobertura em campo obrigatório do dataclass, não cobertura
incidental — corrigível sem reescrever o arquivo.

## Demais pontos — sem objeção

Fixtures, lógica de asserts, isolamento de escopo, e RED por ImportError estão corretos
e bem executados.

## Decisão

REJECTED minor. Corrigir adicionando assert de `metrics.case_name` (Aurora e Fintech) nos
testes 1 e 2 (ou caso novo dedicado), com valor esperado coerente com o blueprint (ex.:
`aurora_blueprint["nome"]`/campo equivalente, a confirmar contra o schema Blueprint real).

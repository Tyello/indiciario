# Review Report — ISSUE-27 STEP-04

STEP: STEP-04
STEP_TYPE: red
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- tests/fixtures/run_manifest/invalid/invalid_pipeline_status.yaml
- tests/fixtures/run_manifest/invalid/missing_manifest_id.yaml
- tests/fixtures/run_manifest/invalid/missing_run_id.yaml
- tests/fixtures/run_manifest/invalid/invalid_source_type.yaml
- tests/fixtures/run_manifest/invalid/invalid_severity.yaml
- tests/fixtures/run_manifest/invalid/invalid_outcome.yaml
- tests/fixtures/run_manifest/invalid/extra_top_field.yaml
- tests/fixtures/run_manifest/invalid/gate_outcome_missing_decision_id.yaml
- tests/test_run_manifest_schema.py (casos 11-20 anexados)

## Arquivos alterados encontrados
- .ai/issues/ISSUE-27.md (estado — único tracked no diff)
- tests/fixtures/run_manifest/invalid/ (8 fixtures, untracked)
- tests/test_run_manifest_schema.py (untracked; casos 11-20 adicionados)

## Verificações
- [x] Execution report existe
- [x] Type válido (red, não Red-Green)
- [x] Arquivos dentro do escopo (allowlist STEP-04)
- [x] Comandos dentro do permitido (pytest tests/test_run_manifest_schema.py -q)
- [x] Critérios de done atendidos (casos 11-20 escritos; suíte falha por módulo ausente)
- [x] Critérios do tipo atendidos (só testes/fixtures; sem GREEN)
- [x] Sem escopo extra

## Verificações específicas
- generator/run_manifest.py NÃO existe.
- schemas/run_manifest.schema.yaml NÃO existe.
- tests/test_run_manifest.py NÃO existe.
- RED confirmado: `ModuleNotFoundError: No module named 'generator.run_manifest'`; 1 error during collection.
- 8 fixtures invalid/ batem exatamente com a allowlist e com a seção "Fixtures necessárias" da spec.
- Casos 11-20 coerentes com spec (tabela "Casos 11–20: rejeições estruturais").
- Casos 11 (schema_version "2.0") e 17 (artifact_type "visual_review") via override de `_valid_manifest()` — aceitável: spec lista apenas 8 fixtures invalid/, e esses dois casos não têm fixture dedicada. Espelha padrão dos casos 5-10 já aprovados no STEP-03.

## Divergências
- nenhuma

## Decisão
APPROVED

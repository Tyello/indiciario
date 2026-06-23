# STEP-05_FIX-01 — Correção: cobertura de CaseMetrics.case_name — Review Report

Veredito: **APPROVED**.

## Verificações executadas

1. Campo correto do blueprint confirmado em `generator/models.py` linha 569:
   `titulo: str` é campo raiz do dataclass `Blueprint`. Asserts adicionados nos
   testes 1 e 2 usam `aurora_blueprint["titulo"]` / `fintech_blueprint["titulo"]`
   — campo certo, não `case_ref` nem outro alias.

2. Valor esperado extraído da fixture `aurora_blueprint`/`fintech_blueprint`
   (carrega JSON real via `_load_blueprint_dict`), não literal hardcoded.
   Assert não tautológico: compara `metrics.case_name` (campo derivado pelo
   módulo sob teste, ainda inexistente) contra dado real do blueprint.

3. `pytest tests/test_quality_comparative_reviewer.py -q`:
   ```
   ModuleNotFoundError: No module named 'generator.quality_comparative_reviewer'
   1 error in 0.58s
   ```
   RED ainda válido — falha de import, módulo não criado.

4. `git status --short`:
   ```
    M .ai/issues/ISSUE-29+30.md
   ?? .ai/runs/ISSUE-29+30/
   ?? examples/caso_fintech.json
   ?? tests/test_quality_comparative_reviewer.py
   ```
   Único arquivo de código alterado: `tests/test_quality_comparative_reviewer.py`.
   `examples/caso_fintech.json` já existia de STEP-03/04 (não tocado nesta fix).
   Nenhum arquivo em `generator/` criado/alterado.

5. Releitura dos casos 3-8: idênticos ao estado revisado em STEP-05_REVIEW.md.
   Única mudança no arquivo: linha 89 (`assert metrics.case_name ==
   aurora_blueprint["titulo"]`) e linha 109 (`assert metrics.case_name ==
   fintech_blueprint["titulo"]`). Correção cirúrgica, escopo respeitado.

## Decisão

APPROVED. Lacuna de STEP-05_REVIEW.md (case_name não coberto) corrigida
corretamente, sem efeitos colaterais.

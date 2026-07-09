# ISSUE-33 STEP-04 — GREEN (integração opt-in no pipeline) — EXECUTION

## Mudanças implementadas

### 1. generator/pipeline_runner.py

- Adicionado `BlindSolver` ao import de `generator.blind_solver_harness` (linha 23)
- Adicionado parâmetro opcional `solver: BlindSolver | None = None` a `run_pipeline()` (linha 214)
- Repassado `solver=solver` para chamada de `_blind_solve()` (linha 233)
- Adicionado parâmetro `solver: BlindSolver | None = None` a `_blind_solve()` (linha 347)
- Implementado logic `effective_solver = solver if solver is not None else DeterministicPipelineSolver(created_at=timestamp)` (linha 360)
- Passado `effective_solver` para `run_blind_solver_harness()` em vez de instância direta (linha 363)

### 2. tests/test_llm_blind_solver.py

- Removido `@pytest.mark.skip` do teste `test_ls_008_pipeline_regression_without_solver_param`
- Reescrito corpo do teste para:
  - Chamar `run_pipeline()` com blueprint canônico (`caso_canonico_iniciante.json`)
  - Não passar parâmetro `solver` (exercita o default)
  - Verificar que resultado é válido: `PipelineRunResult` com `manifest` e `blind_solver_report`

## Validação

```bash
pytest tests/test_llm_blind_solver.py tests/test_aurora_pipeline.py tests/test_pipeline_runner.py -q
```

Resultado: **41 passed in 11.31s** ✓

- Todos os testes existentes (test_aurora_pipeline.py, test_pipeline_runner.py) continuam passando (zero regressão)
- Teste LS_008 agora executa sem skip e valida o default (DeterministicPipelineSolver)

## Critério de sucesso

✅ Caso 8 (LS_008) verde e sem skip
✅ Nenhum teste do pipeline regrediu
✅ Default (solver=None) usa DeterministicPipelineSolver e preserva comportamento anterior
✅ Parâmetro solver é opcional (@kwonly, default None)

## Status

Implementação concluída. Pronto para revisor.

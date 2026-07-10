# STEP-06 — VALIDATION

Comandos:
- `.venv/Scripts/python.exe -m pytest tests/ -q` → verde, sem regressão (rodada completa, background).
- `.venv/Scripts/python.exe -m pytest tests/test_pipeline_runner.py -k test_run_pipeline_is_deterministic_with_same_created_at -q` em loop de 20 rodadas consecutivas → 20/20 `1 passed` cada, nenhuma falha atribuível a timestamp de narrative/evidence review. Flake fechado.
- `.venv/Scripts/python.exe -m ruff check generator/ scripts/ tests/` → `All checks passed!`

Done. Sem regressão; sem flake de determinismo em 20 rodadas (excede o mínimo de 3 pedido na spec).

# STEP-01 — Leitura

Sem duplicação. `grep -rn "LLMProvider\|ProviderRequest" generator/ tests/` retorna vazio.

Padrões de referência confirmados:
- `generator/blind_solver_harness.py` — `Protocol` + `@runtime_checkable` (`BlindSolver`), dataclasses `frozen=True` (`BlindSolverHarnessRequest`, `ArtifactDescriptor`, etc.), hierarquia de erro única `BlindSolverHarnessError(RuntimeError)`.
- `generator/blind_solve_run_record.py` — `validate_run_record(record) -> list[str]` (schema-based), lista vazia == válido, não muta input.

Status: OK. Nenhum bloqueio.

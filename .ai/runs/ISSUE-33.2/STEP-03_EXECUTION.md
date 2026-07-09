# STEP-03 — GREEN (ISSUE-33.2)

Criados:

- `schemas/solvability_report.schema.yaml` — `additionalProperties: false`, `$defs.run_result`,
  `classification_counts` com as 4 chaves fixas obrigatórias, `difficulty_estimate` enum.
- `generator/solvability_meter.py` — `measure_solvability`, `estimate_difficulty` (SM_003 pura),
  `RunResult`, `SolvabilityReport` (frozen), `SolvabilityMeterError`. SM_001–SM_005 implementadas
  conforme SPEC.

`pytest tests/test_solvability_meter.py -q` → `16 passed` na primeira execução.

Foco de revisão (SM_003/SM_004): derivação de dificuldade e flags é 100% Python puro,
sem envolver o modelo — `estimate_difficulty` testável isoladamente sem provider (caso 7).
Falha de run (SM_002) capturada por `except (ProviderError, BlindSolverHarnessError, ConclusionJudgeError)`
por run individual, sem interromper o laço; `SolvabilityMeterError` só é levantado após o laço,
quando `runs_completed == 0`.

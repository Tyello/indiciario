# STEP-01 — Leitura (ISSUE-33.2)

Contratos consumidos, nomes reais:

- `ExpectedConclusionInput(id, statement, required)` — `generator/conclusion_judge.py`.
- `judge_conclusions(report, expected, provider, prompt_version="v1", max_repair_attempts=1, key_evidence_ids=None) -> JudgeVerdict` — `generator/conclusion_judge.py`.
  `JudgeVerdict(verdict_id, report_run_id, prompt_hash, conclusions: list[Conclusion], alternative_solution_detected, alternative_solution_summary, classification, warnings)`.
  `Conclusion(id, met, evidence_cited, rationale)`.
- `LLMBlindSolver(provider, prompt_version="v1", max_repair_attempts=1).solve(context) -> BlindSolverReport` — `generator/llm_blind_solver.py`.
- `run_blind_solver_harness(request: BlindSolverHarnessRequest, solver: BlindSolver) -> BlindSolverHarnessResult` — `generator/blind_solver_harness.py`. `BlindSolverHarnessRequest(bundle_path, solver_id, run_id, created_by, created_at=None, ...)`. `BlindSolverHarnessResult(report: dict, bundle_report, accessed_artifacts, denied_access_attempts, warnings)`.
- `decode_blind_bundle(bundle_path) -> BundleMetadata(bundle_id, manifest_id)` — `generator/blind_bundle_decoder.py`.
- `LLMProvider` Protocol + `ProviderError`/`ProviderTransportError`/`ProviderResponseError` — `generator/llm_provider.py`.
- `FakeProvider(responses)` / `ScriptedResponse(text, model_id)` — `generator/fake_provider.py`; `.calls` tuple; script items may be `ProviderError` instances (injects failure, still recorded in `.calls`).
- Fixtures de bundle reutilizáveis (padrão) de `tests/test_llm_blind_solver.py`: `source_tree`, `output_root`, `public_spec`, `build_request`, `make_bundle`.
- Padrão de schema YAML do repo: `$schema` Draft 2020-12, `additionalProperties: false`, `$defs` para sub-objetos, `enum` para classificações — ver `schemas/judge_verdict.schema.yaml`.

Ponto de composição: `measure_solvability` chama `run_blind_solver_harness(harness_request, LLMBlindSolver(provider=provider))` (mesmo padrão do teste LS_007 de ISSUE-33) e então `judge_conclusions(harness_result.report, expected, provider, key_evidence_ids=...)` (mesmo provider, chamadas sequenciais no roteiro do `FakeProvider`).

Nota de honestidade confirmada: `temperature` é validada (SM_001) mas não é encaminhada às chamadas do provider — `LLMBlindSolver.solve` e `judge_conclusions._call_provider_with_repair` fixam `temperature=0.0` na própria `ProviderRequest`; alterar isso seria mexer em solver/juiz, fora de escopo da 33.2. Registrado no docstring do módulo.

Revisão: auto-approve (reading).

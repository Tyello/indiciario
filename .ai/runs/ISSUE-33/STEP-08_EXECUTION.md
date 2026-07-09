# ISSUE-33 STEP-08 — WRAP-UP

## Arquivos alterados/criados

Modificados:
- `generator/blind_solver_harness.py` — construtor alternativo de `BlindSolverContext` via `bundle_root` (backward-compatible)
- `generator/blind_solver_report_validator.py` — `validate_report` aceita `BlindSolverReport` dataclass além de Mapping
- `generator/pipeline_runner.py` — `run_pipeline(..., solver: BlindSolver | None = None)`, opt-in, default preserva `DeterministicPipelineSolver`
- `docs/BLIND_SOLVER_HARNESS.md` — seção "LLM Blind Solver Adapter (ISSUE-33)"
- `docs/ROADMAP.md` — ISSUE-33 concluída
- `docs/ESTADO_ATUAL.md` — adapter registrado, caráter opt-in
- `docs/BLIND_CONTEXT_PROTOCOL.md` — seção de isolamento do LLM Blind Solver

Criados:
- `generator/llm_blind_solver.py` — `LLMBlindSolver` (LS_001–LS_005)
- `generator/prompts/blind_solver_v1.md` — template versionado PT-BR
- `generator/blind_bundle_decoder.py` — `decode_blind_bundle` (helper reusado pelos testes e adapter)
- `tests/test_llm_blind_solver.py` — 10 testes (8 casos da SPEC + 2 do caso 8 completo)
- `.ai/runs/ISSUE-33/STEP-01..08_EXECUTION.md` — relatórios de execução por step

## Impacto documental — resolvido

- [x] `docs/BLIND_SOLVER_HARNESS.md`
- [x] `docs/ROADMAP.md`
- [x] `docs/ESTADO_ATUAL.md`
- [x] `docs/BLIND_CONTEXT_PROTOCOL.md`
- [x] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ justificado: prompt versionado é código, não doc

## Critério de aceite ISSUE-33 — final

- [x] LS_001–LS_005 implementadas e cobertas por teste
- [x] Teste-sentinela do protocolo cego (caso 2 / LS_001) presente e verde
- [x] Harness fim-a-fim com adapter + FakeProvider produz run record válido (LS_007)
- [x] `pipeline_runner` sem provider preserva comportamento atual (zero regressão) — reforçado com 2º teste de integração (solver injetado usa o adapter)
- [x] `pytest tests/ -q` passa sem regressão (1472 passed vs baseline 1470; 6 falhas pré-existentes idênticas ao main limpo, confirmadas via git stash)
- [x] ruff limpo nos arquivos tocados
- [x] impacto documental resolvido

## Correções feitas em revisão (não pelo executor Haiku)

1. STEP-03: `evidence_used`/`open_questions`/`assumptions` chegavam como listas de dicts crus em vez de
   `BlindSolverEvidence`/tipos corretos — corrigido para instanciar `BlindSolverEvidence` (mantendo `list`,
   não `tuple`, porque `validate_report` usa jsonschema que exige `type: array` == Python `list`).
2. STEP-04: caso 8 da SPEC ("com solver injetado, o report do run vem do adapter") não estava coberto —
   adicionado `test_ls_008_pipeline_with_injected_solver_uses_adapter`.

ISSUE-33 concluída.
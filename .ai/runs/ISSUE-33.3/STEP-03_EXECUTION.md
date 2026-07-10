# STEP-03 — GREEN (ISSUE-33.3)

Implementado em `generator/pipeline_runner.py`:

- `run_pipeline`/`_run_gate` ganham `judge_provider: LLMProvider | None = None`.
- `_run_gate`: com `judge_provider`, monta `ExpectedConclusionInput` via `_derive_expected_conclusions`,
  chama `judge_conclusions(report, expected_inputs, judge_provider)`, deriva `met` real por conclusão.
  `decision`/`gaps`/`leak_detected` derivados em Python puro do veredito + regras GE existentes
  (nunca do modelo). Sem `judge_provider`, ramo stub preservado byte a byte.
- `_derive_expected_conclusions`: typo `EC-GUia-{index}` → `EC-GUIA-{index}` (PJ_004).
- `_record_gate_decision`: passa a receber decisão/justificativa reais do gate evaluation
  (não mais `outcome="approved"` fixo) — necessário para não reintroduzir o mesmo bug um nível abaixo.
- `_assemble_workspace`: ingestão condicional do artefato `judge_verdict` quando `gate_mode == "judged"`.
- `_consolidate_manifest`: repassa `gate_mode` para `build_run_manifest`.
- Erro do provider (`ConclusionJudgeError`/`ProviderResponseError`) mapeado para `RuntimeError`
  com contexto do run_id, propagado como falha do stage (caso 7 — nunca aprovação silenciosa).

Suporte:
- `generator/run_manifest.py`: `RunManifest.gate_mode: str = "stub"`, `build_run_manifest(gate_mode=...)`,
  `manifest_to_dict` inclui o campo (default preserva chamadas existentes).
- `generator/workspace.py`: `judge_verdict` em `VALID_ARTIFACT_TYPES`.
- `schemas/run_manifest.schema.yaml`: `gate_mode` (enum `stub`/`judged`) em `properties`, **não** em
  `required` (compat com manifests antigos); `judge_verdict` no enum `artifact_type`.
- `schemas/workspace_run.schema.yaml`: `judge_verdict` no enum `artifact_type`.

Resultado: `pytest tests/test_pipeline_runner.py -q` — 34 testes (27 existentes + 7 novos), todos verdes.
`conclusion_judge.py`/`gate_evaluator.py` não alterados (fora de escopo, PJ_00x consome as assinaturas existentes).

Revisão: obrigatória — decisão em Python puro confirmada (grep por qualquer branch que confie a
`decision` a texto do modelo: nenhum); caso 7 confirmado (falha propaga, não aprova).

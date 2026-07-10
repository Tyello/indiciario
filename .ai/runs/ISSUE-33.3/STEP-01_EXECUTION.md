# STEP-01 — Leitura (ISSUE-33.3)

## Grep EC-GUia
Único hit de código: `generator/pipeline_runner.py:646` (`id=f"EC-GUia-{index}"`).
Outro hit é `docs/AUDITORIA_FABLE_2026-07.md:70`, citação histórica do bug — não altera (é evidência do achado, não artefato ativo).
Nenhum manifest/fixture versionado referencia o id antigo.

## Pontos de mudança em generator/pipeline_runner.py
- `run_pipeline` (linha ~209): novo parâmetro `judge_provider: LLMProvider | None = None`, repassado a `_run_gate`.
- `_run_gate` (linha ~375-416): hoje fabrica `decision="approved"` fixo (`:409`) e gaps stub. Ganha ramo judge: monta `ExpectedConclusionInput` a partir de `_derive_expected_conclusions`, chama `judge_conclusions(run_record["report"], expected_inputs, judge_provider)`, deriva `met` real por conclusão, deriva `decision`/`gaps`/`leak_detected` em Python puro a partir do veredito + regras GE existentes. Retorna `(gate_evaluation, gate_mode, judge_verdict_dict_or_None)`.
- `_derive_expected_conclusions` (linha ~622-653): typo `EC-GUia-{index}` → `EC-GUIA-{index}` (PJ_004).
- `_record_gate_decision` (linha ~598-619): hoje grava `outcome="approved"` fixo, sempre — mesmo bug de fabricação, um nível abaixo do gate. Passa a receber a decisão/justificativa reais do gate evaluation (necessário para não reintroduzir o mesmo problema que a issue fecha).
- `_assemble_workspace` (linha ~443-535): ganha ingestão condicional do artefato `judge_verdict` (novo `artifact_type`) quando `gate_mode == "judged"`.
- `_consolidate_manifest` (linha ~538-552): repassa `gate_mode` para `build_run_manifest`.

## generator/conclusion_judge.py (assinatura real, não muda)
`judge_conclusions(report: Mapping, expected: Sequence[ExpectedConclusionInput], provider: LLMProvider, prompt_version="v1", max_repair_attempts=1, key_evidence_ids=None) -> JudgeVerdict`.
`JudgeVerdict.conclusions: list[Conclusion(id, met, evidence_cited, rationale)]`, `.classification: resolvido|nao_resolvido|vazamento|ambiguo`.
Erro de provider (`ProviderResponseError`) não tem retry — vira `ConclusionJudgeError` na primeira tentativa (não há repair loop para erro de transporte, só para JSON inválido). `_run_gate` deve deixar essa exceção propagar como falha rastreável do stage (nunca aprovação silenciosa) — mapeada para `RuntimeError` com contexto do run_id.

## generator/gate_evaluator.py (GE_004/gaps, não muda)
`build_gate_evaluation` monta o dict; `validate_gate_evaluation_semantics` aplica GE_001-GE_008 (GE_004/GE_005 bloqueiam `approved` com required não-met; GE_003 bloqueia `approved` com `leak_detected=true`; GE_006 bloqueia `approved` com gap `severity="critical"`). Decisão Python de `_run_gate` precisa ser consistente com essas regras por construção (nunca aprovar com required não-met/leak/gap crítico).

## Schema do manifest (gate_mode)
`schemas/run_manifest.schema.yaml`: `additionalProperties: false`, sem `gate_mode` hoje. Adicionar `gate_mode` em `properties` (enum `stub`/`judged`) **sem** adicioná-lo a `required` — assim manifests antigos (sem o campo) continuam válidos contra o schema novo (nota de compatibilidade da SPEC). `generator/run_manifest.py`: `build_run_manifest` ganha `gate_mode: str = "stub"`; dataclass `RunManifest` ganha `gate_mode: str = "stub"` (default preserva chamadas existentes em `tests/test_run_manifest.py`); `manifest_to_dict` inclui o campo.

Artefato novo `judge_verdict`: precisa entrar em `VALID_ARTIFACT_TYPES` (`generator/workspace.py`), no enum `artifact_type` de `schemas/workspace_run.schema.yaml` e de `schemas/run_manifest.schema.yaml` (ambos additionalProperties:false). Nenhum teste faz assert de igualdade exata sobre `VALID_ARTIFACT_TYPES` (`tests/test_workspace.py` só usa como conjunto de referência) — extensão seguraestrutural.

## tests/test_pipeline_runner.py
27 testes hoje, todos offline, sem `judge_provider`. `generator/fake_provider.py` já expõe `FakeProvider`/`ScriptedResponse` (usado em `tests/test_conclusion_judge.py`) — reaproveitado para os 7 casos novos da SPEC.

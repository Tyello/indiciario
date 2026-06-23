# STEP-01 — Reading — Execution Report

Type: reading. Status: done. Auto-approved (low-risk).

## generator/pipeline_runner.py

API pública (`__all__`): `AURORA_DEFECT_TO_CODES`, `AURORA_PLAYTEST_DEFECTS`, `DefectMatch`, `DeterministicPipelineSolver`, `PipelineRunResult`, `PlaytestComparison`, `PlaytestDefect`, `VALID_ARTIFACT_TYPES`, `VALID_OUTCOMES`, `VALID_STAGES`, `compare_to_playtest`, `run_pipeline`.

### `run_pipeline`

```python
def run_pipeline(
    blueprint_path: str | Path,
    run_id: str,
    *,
    output_root: str | Path | None = None,
    created_at: str | None = None,
) -> PipelineRunResult
```

- Lê blueprint via `load_blueprint` (case_review.py), guarda bytes antes/depois — levanta `RuntimeError("pipeline mutated the blueprint file")` se houver mutação.
- `created_at` default = `FIXED_PIPELINE_CREATED_AT = "2026-06-22T12:00:00Z"`.
- `output_root` default: tempdir `indiciario-pipeline-*` (caller/OS gerencia lifecycle).
- Encadeamento de estágios (todos via APIs públicas existentes, sem LLM/rede):
  1. `_blind_solve` → `_build_bundle` (materializa docs E1 em `source_root`, chama `build_blind_bundle`) → `run_blind_solver_harness` com `DeterministicPipelineSolver` (stub: lê só o 1º artefato) → `validate_report` → `build_run_record`.
  2. `_run_gate` → `_derive_expected_conclusions` (de `objetivos_por_envelope`, fallback `guia_operacional.solucao_em_5_frases`) → `build_gate_evaluation` com decisão fixa `"approved"`, 1 gap stub (`GAP-STUB-01`, severity `minor`), `leak_detected=False`.
  3. `_run_reviews` → `review_narrative` + `review_evidence` (revisão estática determinística do blueprint).
  4. `_assemble_workspace` → `build_workspace_run` + sequência `transition_stage`/`ingest_artifact`/`record_decision` (manual_orchestrator) percorrendo stages `initialized→blind_solve→gate_evaluation→narrative_review→evidence_review→complete`; ingere `BUNDLE`, `BSR` (blind_solver_report), `RR` (run_record), `GE` (gate_evaluation), `NR`, `ER`. Seta `run["status"] = "done"` ao final.
  5. Consolida `findings_by_artifact = {f"NR-{run_id}": ..., f"ER-{run_id}": ...}` → `_consolidate_manifest` → `build_run_manifest` (run_manifest.py).
  6. `compare_to_playtest` contra `AURORA_PLAYTEST_DEFECTS` **apenas se** `"caso_canonico_intermediario" in blueprint_path.name` (hardcoded — para Fintech isso será tupla vazia, sem comparação real de playtest a menos que o pipeline_runner seja estendido, o que é proibido no escopo desta issue).

Retorna `PipelineRunResult` (frozen dataclass):
```python
@dataclass(frozen=True)
class PipelineRunResult:
    manifest: dict[str, Any]
    workspace_run: dict[str, Any]
    blind_solver_report: dict[str, Any]
    gate_evaluation: dict[str, Any]
    narrative_report: dict[str, Any]
    evidence_report: dict[str, Any]
    findings: tuple[dict[str, Any], ...]
    comparison: PlaytestComparison
```

`findings` consolida apenas NR_* e ER_* (ordem: todos NR primeiro, depois todos ER — vem de `findings_by_artifact.values()`). **Não inclui VR_*/AR_* (visual/accessibility)** — `_run_reviews` só chama `review_narrative`/`review_evidence`; reviewers visual/accessibility (ISSUE-23+24) não estão encadeados em `run_pipeline`. Isso é relevante para ISSUE-30: `findings_by_type` esperando `VR_*`/`AR_*` da spec só terá esses códigos se vierem de fora do `run_pipeline` atual, ou ficará com contagem 0 para VR/AR.

`PlaytestComparison` (frozen): `playtest_defects`, `pipeline_findings` (códigos), `matches` (`DefectMatch(defect_id, finding_code)`), `unmatched_playtest`, `unmatched_pipeline`.

Proibido alterar este módulo (confirmado pela issue, STEP-03 a STEP-08).

## generator/run_manifest.py

API pública: `SCHEMA_VERSION = "1.0"`, `STATUS_MAP`, `VALID_ARTIFACT_TYPES/OUTCOMES/STAGES` (de `generator.workspace`), dataclasses `ManifestArtifactSummary`, `ManifestDecisionSummary`, `ManifestFinding`, `ManifestGateOutcome`, `ManifestSemanticResult`, `RunManifest`, funções `build_run_manifest`, `manifest_to_dict`, `validate_run_manifest`, `validate_run_manifest_semantics`.

### `RunManifest` (frozen dataclass)

Campos: `manifest_id`, `run_id`, `case_ref`, `generated_at`, `generated_by`, `pipeline_status`, `stages_completed: tuple[str,...]`, `artifacts_summary: tuple[ManifestArtifactSummary,...]`, `decisions_summary: tuple[ManifestDecisionSummary,...]`, `findings: tuple[ManifestFinding,...]`, `gate_outcome: ManifestGateOutcome | None`, `next_steps: tuple[str,...]`, `notes`.

`ManifestFinding`: `source_artifact_id`, `source_type` (`"narrative_review"` | `"evidence_review"` — comentário no código não menciona visual/accessibility), `code`, `severity` (`critical|major|minor|info`), `field`, `message`.

`STATUS_MAP`: `done→complete`, `gate_blocked→blocked`, `rolled_back→rolled_back`, `initialized→incomplete`, `in_progress→incomplete`.

`_MANIFEST_STAGES` = `VALID_STAGES` menos `initialized`/`complete` (4 stages reais: `blind_solve`, `gate_evaluation`, `narrative_review`, `evidence_review`).

### `build_run_manifest(run, manifest_id, findings_by_artifact=None, generated_by="orchestrator", notes="", generated_at=None) -> dict`

- Deepcopy de `run` e `findings_by_artifact` (nunca muta entradas).
- Deriva `pipeline_status` via `STATUS_MAP`, `stages_completed` (ordenado por `VALID_STAGES`, só stages com artefato presente).
- `artifacts_summary`/`decisions_summary` projetam campos do `run["artifacts"]`/`run["decisions"]`.
- `gate_outcome`: primeira decision com `stage == "gate_evaluation"` (decision_id, outcome, justification) ou `None`.
- `findings`: para cada `artifact_id` em `findings_by_artifact`, resolve `source_type = artifact_type_by_id[artifact_id]`, monta dict com `code/severity/field/message` (campo `field` default `""`).
- `next_steps`: deterministico por `pipeline_status` (complete/blocked/rolled_back) ou pelo primeiro stage ausente (incomplete).

### Validação

- `validate_run_manifest(manifest) -> list[str]`: carrega `schemas/run_manifest.schema.yaml` (Draft202012Validator + FormatChecker), retorna lista ordenada de mensagens de erro (vazia == válido). **Schema-estrutural via JSON Schema**, arquivo em `schemas/run_manifest.schema.yaml` (raiz do projeto, não `generator/schemas/`).
- `validate_run_manifest_semantics(manifest) -> ManifestSemanticResult` (frozen: `manifest`, `errors`, `warnings`, `valid`): aplica regras `RM_001`–`RM_008`:
  - RM_001: `manifest_id == run_id` → erro.
  - RM_002: stage em `stages_completed` sem artefato correspondente → erro.
  - RM_003: `gate_outcome.decision_id` ausente em `decisions_summary` → erro.
  - RM_004: `pipeline_status == "complete"` sem os 4 stages → erro.
  - RM_005: finding `source_artifact_id` ausente em `artifacts_summary` → erro.
  - RM_006: múltiplas decisions de `gate_evaluation` → warning.
  - RM_007: `pipeline_status == "blocked"` sem decision `outcome == "rejected"` → warning.
  - RM_008: `next_steps` vazio com `pipeline_status != "complete"` → warning.
  - `valid = not errors` (warnings nunca invalidam).

Formato de `findings` (lista de dicts dentro do manifest serializado): `{"source_artifact_id": str, "source_type": str|None, "code": str|None, "severity": str|None, "field": str, "message": str|None}`.

## docs/AURORA_PIPELINE_RUN.md

Documenta a run ISSUE-28 sobre `examples/caso_canonico_intermediario.json`. Estrutura: título, "Escopo desta run" (sem LLM/rede/mutação; solver stub determinístico; gate approved; revisores narrative+evidence; orquestração manual_orchestrator+manifest), "Ordem de encadeamento" (lista numerada 1-9 das chamadas de API públicas), "Resultado da run" (tabela: `run_id`, `pipeline_status: complete`, `stages_completed` (4), `gate_decision: approved`, findings NR=0, findings ER=3 — todos `ER_007` ×3), "Comparação com playtest real" (tabela `PD_01/02/03` vs resultado pipeline — todos `unmatched_playtest`; `unmatched_pipeline: ER_007 ×3`), "Interpretação honesta" (pipeline funciona, mas não captura defeitos de clareza de envelope do playtest; blind solver stub não resolve o caso de fato), "Como reproduzir" (comandos pytest + snippet Python chamando `run_pipeline`), "Próxima PR recomendada".

Esse é o formato-referência exigido para `docs/FINTECH_PIPELINE_RUN.md` (STEP-09).

## examples/caso_canonico_intermediario.json (Aurora)

Campos de topo == campos do modelo Pydantic `Blueprint` (`generator/models.py:566-625`), que É o schema real usado por `load_blueprint`/`Blueprint(**data)`. Lista completa (ordem do model, todos presentes no JSON Aurora):

`titulo, subtitulo, genero, tom, modo_validacao, dificuldade, tempo_estimado_min, numero_jogadores, formato_envelopes, premissa, conflito_central, objetivos_por_envelope, guia_operacional, verdade_real, executor_id, planejador_id, beneficiario_id, motivacao, metodo_ocultacao, erro_que_permite_descobrir, cadeia_causal, personagens, linha_tempo_real, linha_tempo_percebida, linha_tempo_documental, pilares_validacao, intervalo_critico_inicio, intervalo_critico_fim, documentos, matriz_pistas, red_herrings, cadeia_financeira, codigos, dicas, dicas_contextuais, contratos_evidencia, visual_procedural, printable_cards, playtest, versao, observacoes_producao`.

Dificuldade Aurora: `intermediario`. `documentos` tem >=8 entradas (min_length=8), cada `Documento` tem `codigo, titulo, envelope, tipo, emocao_esperada, objetivo_narrativo, pistas_contidas, confirma, confirmado_por, red_herring_potencial, risco_ambiguidade, ids_citados, codigos_citados, conteudo` (dict livre por tipo de documento).

## examples/showcase_tecnico.json (referência corporativa)

Mesmos campos de topo do Blueprint Pydantic (mesma classe, validação idêntica). `dificuldade: intermediario`, `genero: "fraude corporativa"`, `tom: corporativo`, `numero_jogadores: "4"`, `formato_envelopes: 2`. 16 documentos (tipos: email_narrador, email_institucional, chat, boletim, depoimento, log_acesso, protocolo, contrato, manual, glossario, folha_cruzamento, recibo, orcamento, extrato, outro). `matriz_pistas` com 3 pistas, `red_herrings` com 2 entradas (`personagem_id, motivo_aparente, como_descartar, documento_descarte, categoria`), `contratos_evidencia` com 3 (`id, conclusao, fase, tipo, prova_principal, confirmacao_independente, descarta_alternativas, personagens_afetados, acao_esperada_jogador, risco_ambiguidade, obrigatoria_para_avanco`), `pilares_validacao` com exatamente 4 (`nome, documento_principal, confirmacao, personagem_id` — `max_length=4` no model). `personagens`: 6 (papéis `executor, narrador, beneficiario, planejador, red_herring×2`). `dicas`: 6 (`numero, intensidade, envelope, condicao_uso, texto, o_que_desbloqueia`). Serve de referência estrutural corporativa para o Fintech (mesmo schema Pydantic, gênero/tom corporativos já presentes), mas **não será usado diretamente** (a issue já decidiu Opção B: criar `caso_fintech.json` do zero).

## Schema de blueprint usado pelo validator

Não é YAML/JSON-Schema solto — é o **modelo Pydantic `Blueprint`** em `generator/models.py:566-625` (`class Blueprint(BaseModel)`). `load_blueprint` (generator/case_review.py:409-412) faz `Blueprint(**data)` direto — toda validação estrutural/tipo ocorre na construção do modelo Pydantic (erros de campo ausente, tipo errado, `min_length`/`max_length` etc. levantam `pydantic.ValidationError`).

Campos obrigatórios (sem default, todos exigidos): `titulo, subtitulo, genero, tom, modo_validacao, dificuldade, tempo_estimado_min, numero_jogadores, formato_envelopes (>=1), premissa, conflito_central, objetivos_por_envelope (min 1), guia_operacional, verdade_real, executor_id, planejador_id, beneficiario_id, motivacao, metodo_ocultacao, erro_que_permite_descobrir, cadeia_causal (min 3), personagens (min 4), linha_tempo_real (min 3), pilares_validacao (exatamente 4), intervalo_critico_inicio, intervalo_critico_fim, documentos (min 8), matriz_pistas (min 3), red_herrings (min 2), dicas (min 6)`.

Campos com default (opcionais): `linha_tempo_percebida, linha_tempo_documental` (`[]`), `cadeia_financeira, codigos, dicas_contextuais, contratos_evidencia, printable_cards` (`[]`), `visual_procedural` (`None`), `playtest` (`None`), `versao` (`"0.1"`), `observacoes_producao` (`None`).

`generator/validator.py:340` define `class BlueprintValidator` — camada adicional de regras editoriais/anti-obviedade/progressão **acima** da validação estrutural Pydantic (guardrails citados no CLAUDE.md). Roda depois que `Blueprint(**data)` já passou.

Não confundir com `schemas/run_manifest.schema.yaml` (JSON Schema YAML, usado só por `run_manifest.py` para o manifest de run, módulo totalmente diferente) nem com `generator/schemas/*.yaml` (schemas de **tipo de documento** — extrato, contrato, chat, etc. — usados na renderização/validação de `conteudo` por tipo, não do blueprint inteiro).

## Comando exato de validação de blueprint

Confirmado em `generator/validator.py` linha 6 (docstring) e linha 1755+ (`argparse`):

```bash
python -m generator.validator <arquivo.json> [--strict] [--json]
```

`--strict`: falha também em risco Médio (não só Alto). `--json`: saída em JSON. Exemplos reais usados no CLAUDE.md/AGENTS.md:

```bash
python -m generator.validator examples/caso_canonico_iniciante.json --strict
python -m generator.validator examples/caso_canonico_intermediario.json --strict
```

Para STEP-03, o comando equivalente para o Fintech será:
```bash
python -m generator.validator examples/caso_fintech.json --strict
```

## Observações relevantes para steps seguintes

1. `run_pipeline` decide `AURORA_PLAYTEST_DEFECTS` por nome de arquivo hardcoded (`"caso_canonico_intermediario" in blueprint_path.name`) — para Fintech, `compare_to_playtest` roda com `playtest_defects=()`, ou seja, comparação com playtest será trivialmente vazia a menos que `caso_fintech.json` tenha seu próprio bloco `playtest` consumido fora do `run_pipeline` (módulo não pode ser alterado).
2. `run_pipeline` **não invoca reviewers visuais/accessibility** (VR_*/AR_*) apesar da spec ISSUE-29+30 mencionar esses códigos em `findings_by_type`. Para STEP-06/08, `generate_quality_report` provavelmente terá `VR_*`/`AR_*` zerados ao usar só o `manifest` de `run_pipeline`, a menos que esses reviewers sejam chamados separadamente em `quality_comparative_reviewer.py` (fora de `pipeline_runner.py`, permitido pelo escopo).
3. Schema de blueprint é Pydantic (`generator/models.py`), não YAML solto — `--strict` no CLI roda além disso o `BlueprintValidator` (regras editoriais).
4. `docs/AURORA_PIPELINE_RUN.md` é o template de formato a replicar em `docs/FINTECH_PIPELINE_RUN.md`.

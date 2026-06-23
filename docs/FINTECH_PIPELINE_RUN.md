# Fintech Pipeline Run — ISSUE-29

Execução ponta-a-ponta da pipeline multiagente offline sobre o caso avançado **Desvio de Fundos na Acelerada Pagamentos** (`examples/caso_fintech.json`).

## Escopo desta run

- **Sem LLM**, sem internet, sem mutação do blueprint.
- Blind solver: stub determinístico (`DeterministicPipelineSolver`).
- Gate: decisão explícita `approved` com conclusões derivadas de `objetivos_por_envelope`.
- Revisores: `review_narrative` + `review_evidence` (determinísticos).
- Orquestração: `manual_orchestrator` + `build_run_manifest`.

## Ordem de encadeamento (APIs públicas)

1. `load_blueprint` — leitura do JSON do Fintech.
2. `build_blind_bundle` — bundle cego com documentos E1 materializados em `output_root`.
3. `run_blind_solver_harness` — stub lê primeiro artefato do bundle.
4. `validate_report` + `build_run_record` — congela run record.
5. `build_gate_evaluation` — conclusões de `objetivos_por_envelope`, decisão `approved`.
6. `review_narrative` / `review_evidence` — revisão estática do blueprint.
7. `build_workspace_run` → `transition_stage` / `ingest_artifact` / `record_decision` — workspace completo.
8. `build_run_manifest` — manifest consolidado com findings NR + ER.
9. `compare_to_playtest` — sem efeito (Fintech não tem playtest real associado).

## Resultado da run (2026-06-23, determinístico)

| Campo | Valor |
|---|---|
| `run_id` | `RUN-FINTECH-20260623-001` (STEP-04) / reproduzível via `run_pipeline` |
| `pipeline_status` | `complete` |
| `stages_completed` | `blind_solve`, `gate_evaluation`, `narrative_review`, `evidence_review` (4/4) |
| `gate_decision` | `approved` (`gate_outcome.decision_id = "DEC-RUN-FINTECH-20260623-001"`) |
| Findings narrative (NR_*) | **0** |
| Findings evidence (ER_*) | **4** (`ER_006` × 2, `ER_007` × 2) |

### Findings completos (`result.findings` == `manifest["findings"]`)

Todos `severity: major`, `source_artifact_id: "ER-RUN-FINTECH-20260623-001"`:

1. **`ER_006`** — `field: "red_herrings[0]"` — *"Red herring '06' não pode ser descartado: nenhuma pista contradiz ou contextualiza o documento de descarte."*
2. **`ER_006`** — `field: "red_herrings[1]"` — *"Red herring '07' não pode ser descartado: nenhuma pista contradiz ou contextualiza o documento de descarte."*
3. **`ER_007`** — `field: "contratos_evidencia[2]"` — *"Contrato obrigatório 'C-E2-RETROCOMISSAO' depende de prova 'E2-01' ausente do E1."*
4. **`ER_007`** — `field: "contratos_evidencia[3]"` — *"Contrato obrigatório 'C-E2-BENEFICIARIO' depende de prova 'E2-04' ausente do E1."*

Nenhum erro/exceção. Os 4 findings são avaliações do `evidence_reviewer` estático sobre o blueprint — não bloqueiam o pipeline (gate já fixo `approved` por `run_pipeline`, independente desses findings).

## Comparação com playtest real

`compare_to_playtest` é hardcoded para reconhecer apenas `caso_canonico_intermediario` (Aurora) em `pipeline_runner.py`. `caso_fintech.json` não corresponde a esse filtro, logo a comparação é trivialmente vazia do lado playtest:

- `playtest_defects`: `()` (vazio, esperado — Fintech não tem playtest real disponível)
- `pipeline_findings`: `('ER_006', 'ER_006', 'ER_007', 'ER_007')`
- `matches`: `()`
- `unmatched_playtest`: `()`
- `unmatched_pipeline`: `('ER_006', 'ER_006', 'ER_007', 'ER_007')`

### Interpretação honesta

A tubulação encaixa para um segundo blueprint, não só para o Aurora: manifest schema + semântica válidos, artefatos intermediários schema-válidos, blueprint byte-idêntico (nenhum ajuste foi necessário em `examples/caso_fintech.json` durante a run).

Os 4 findings ER refletem limitações reais do blueprint Fintech: dois red herrings (`'06'`, `'07'`) sem pista de contradição/contextualização associada, e dois contratos de evidência do E2 (`C-E2-RETROCOMISSAO`, `C-E2-BENEFICIARIO`) dependendo de provas (`E2-01`, `E2-04`) ausentes do E1. Não bloqueiam o gate nem a validação do manifest.

O blind solve stub **não** resolve o caso; isso fica para Fase I (ISSUE-31+).

## Validação do manifest

`validate_run_manifest(manifest)` (estrutural, JSON Schema `schemas/run_manifest.schema.yaml`):

```
errors: []
valid: True
```

`validate_run_manifest_semantics(manifest)` (regras RM_001–RM_008):

```
errors: ()
warnings: ()
valid: True
```

Ambos válidos, sem erros nem warnings. `manifest_id != run_id` (RM_001 ok), todos os 4 stages completados têm artefato correspondente (RM_002 ok), `gate_outcome.decision_id` presente em `decisions_summary` (RM_003 ok), `pipeline_status == complete` com os 4 stages presentes (RM_004 ok), os 4 findings referenciam `source_artifact_id` presente em `artifacts_summary` (RM_005 ok), apenas 1 decision de `gate_evaluation` (RM_006 ok, sem warning), `pipeline_status != blocked` (RM_007 n/a), `next_steps` não vazio dado `pipeline_status == complete` (RM_008 ok).

Resultado confirmado de forma independente em STEP-04 (executor) e na revisão correspondente (`.ai/runs/ISSUE-29+30/STEP-04_REVIEW.md`, veredito **APPROVED**), e reproduzido de novo em STEP-09 para esta documentação.

## Como reproduzir

```bash
pytest tests/test_pipeline_runner.py -q
```

Ou programaticamente:

```python
from generator.pipeline_runner import run_pipeline

result = run_pipeline(
    "examples/caso_fintech.json",
    "RUN-FINTECH-20260623-001",
    created_at="2026-06-23T10:00:00Z",
)
print(result.manifest["pipeline_status"], result.findings)
```

## Próxima PR recomendada

**ISSUE-30** (relatório comparativo de qualidade Aurora vs Fintech) — ver `docs/QUALITY_COMPARATIVE_REPORT.md`.

# Aurora Pipeline Run — ISSUE-28

Primeira execução ponta-a-ponta da pipeline multiagente offline sobre o caso canônico **O Último Brinde do Hotel Aurora** (`examples/caso_canonico_intermediario.json`).

## Escopo desta run

- **Sem LLM**, sem internet, sem mutação do blueprint.
- Blind solver: stub determinístico (`DeterministicPipelineSolver`).
- Gate: decisão explícita `approved` com conclusões derivadas de `objetivos_por_envelope`.
- Revisores: `review_narrative` + `review_evidence` (determinísticos).
- Orquestração: `manual_orchestrator` + `build_run_manifest`.

## Ordem de encadeamento (APIs públicas)

1. `load_blueprint` — leitura do JSON do Aurora.
2. `build_blind_bundle` — bundle cego com documentos E1 materializados em `output_root`.
3. `run_blind_solver_harness` — stub lê primeiro artefato do bundle.
4. `validate_report` + `build_run_record` — congela run record.
5. `build_gate_evaluation` — conclusões de `objetivos_por_envelope`, decisão `approved`.
6. `review_narrative` / `review_evidence` — revisão estática do blueprint.
7. `build_workspace_run` → `transition_stage` / `ingest_artifact` / `record_decision` — workspace completo.
8. `build_run_manifest` — manifest consolidado com findings NR + ER.
9. `compare_to_playtest` — cruza findings com `AURORA_PLAYTEST_DEFECTS`.

## Resultado da run (2026-06-22, determinístico)

| Campo | Valor |
|---|---|
| `run_id` | `RUN-AURORA-PIPELINE-001` (testes) / reproduzível via `run_pipeline` |
| `pipeline_status` | `complete` |
| `stages_completed` | `blind_solve`, `gate_evaluation`, `narrative_review`, `evidence_review` |
| `gate_decision` | `approved` |
| Findings narrative (NR_*) | **0** |
| Findings evidence (ER_*) | **3** (`ER_007` × 3 — contratos obrigatórios sem prova em E1) |

## Comparação com playtest real

Defeitos declarados em `AURORA_PLAYTEST_DEFECTS` (extraídos de `playtest.observacoes`, não inferidos):

| ID | Defeito do playtest | Resultado pipeline |
|---|---|---|
| PD_01 | Não ficou claro o que resolver no E1 | `unmatched_playtest` — sem regra NR de clareza de objetivo |
| PD_02 | Não ficou claro quando receber o E2 | `unmatched_playtest` — sem regra de progressão entre envelopes |
| PD_03 | Não ficou claro quais perguntas responder no E2 | `unmatched_playtest` — sem regra NR de clareza de objetivo |

- **matches:** nenhum (esperado — mapeamento `AURORA_DEFECT_TO_CODES` vazio para clareza de envelope).
- **unmatched_pipeline:** `ER_007` (× 3) — findings reais do Evidence Reviewer, sem defeito de playtest correspondente.

### Interpretação honesta

A tubulação encaixa: manifest schema + semântica válidos, artefatos intermediários schema-válidos, blueprint byte-idêntico.

A pipeline **não** captura hoje os defeitos de clareza de envelope do playtest Rodada 01 — confirma backlog de regras NR_002/005/007 (clareza/escopo de documentos e objetivos).

O blind solve stub **não** resolve o caso; isso fica para Fase I (ISSUE-31+).

## Como reproduzir

```bash
pytest tests/test_aurora_pipeline.py -q
pytest tests/test_pipeline_runner.py -q
```

Ou programaticamente:

```python
from generator.pipeline_runner import run_pipeline

result = run_pipeline(
    "examples/caso_canonico_intermediario.json",
    "RUN-AURORA-20260622-001",
    created_at="2026-06-22T12:00:00Z",
)
print(result.manifest["pipeline_status"], result.comparison)
```

## Próxima PR recomendada

**ISSUE-23+24** — Visual + Accessibility Reviewer (desbloqueadas por esta issue).

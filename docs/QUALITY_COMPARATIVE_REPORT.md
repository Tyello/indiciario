# Quality Comparative Report — Aurora vs Fintech (ISSUE-30)

Relatório consolidado comparando os dois casos canônicos rodados ponta-a-ponta pela pipeline multiagente offline (`generator.pipeline_runner.run_pipeline`): **O Último Brinde do Hotel Aurora** (intermediário, `examples/caso_canonico_intermediario.json`) e **Desvio de Fundos na Acelerada Pagamentos** (avançado, `examples/caso_fintech.json`). Gerado via `generator.quality_comparative_reviewer.generate_quality_report`.

## Como foi gerado

```python
from generator.pipeline_runner import run_pipeline
from generator.quality_comparative_reviewer import generate_quality_report

aurora_result = run_pipeline("examples/caso_canonico_intermediario.json", "RUN-AURORA-...", created_at="...")
fintech_result = run_pipeline("examples/caso_fintech.json", "RUN-FINTECH-...", created_at="...")

report = generate_quality_report(
    aurora_result.manifest,
    fintech_result.manifest,
    aurora_blueprint,
    fintech_blueprint,
)
```

Executado de forma independente nesta sessão (STEP-09) sobre as duas runs reais, reproduzindo byte a byte os valores já verificados em `.ai/runs/ISSUE-29+30/STEP-08_EXECUTION.md` e `STEP-08_REVIEW.md`. `validate_quality_comparative_report(report)` retornou `errors: []`.

## CaseMetrics (resumo por caso)

| Campo | Aurora | Fintech |
|---|---|---|
| `case_name` | O Último Brinde do Hotel Aurora | Desvio de Fundos na Acelerada Pagamentos |
| `dificuldade_esperada` | intermediario | avancado |
| `pipeline_status` | complete | complete |
| `stages_completed` | 4 | 4 |
| `findings_count` | 3 | 4 |
| `findings_by_type` | `NR_*=0, ER_*=3, VR_*=0, AR_*=0` | `NR_*=0, ER_*=4, VR_*=0, AR_*=0` |
| `blocked_by` | None | None |

Findings Aurora (ER_007 × 3 — contratos obrigatórios sem prova em E1, conforme `docs/AURORA_PIPELINE_RUN.md`): `contratos_evidencia[3]` (C-E2-OMISSAO/E2-01), `contratos_evidencia[4]` (C-E2-OBJETO/E2-05), `contratos_evidencia[7]` (C-FINAL-AURORA/E2-07).

Findings Fintech (ER_006 × 2 + ER_007 × 2, conforme `docs/FINTECH_PIPELINE_RUN.md`): red herrings `'06'`/`'07'` sem contradição associada; contratos `C-E2-RETROCOMISSAO`/`C-E2-BENEFICIARIO` dependendo de provas `E2-01`/`E2-04` ausentes do E1.

## Tabela de métricas (6 `MetricComparison`)

| metric_name | aurora_value | fintech_value | direction | interpretation |
|---|---|---|---|---|
| `densidade_documental` | 26464 | 29647 | lower_is_better | Soma dos comprimentos de conteúdo dos documentos de cada caso. Menos texto compacto favorece a jogabilidade. |
| `dificuldade_vs_esperada` | mais_facil | mais_dificil | neutral | Dificuldade declarada de cada caso comparada com a do outro caso. |
| `vazamento_info` | 3 | 4 | lower_is_better | Quantidade de findings ER_006/ER_007/ER_008 (vazamento de informação do gabarito) detectados em cada caso. |
| `visual_score` | 0 | 0 | lower_is_better | Quantidade de findings VR_* (visual reviewer) detectados em cada caso. `pipeline_runner.py` não invoca o visual reviewer hoje, logo 0/0 é o resultado real e esperado. |
| `pacing` | 1.0 | 1.0 | neutral | Fração de stages completados (`stages_completed / 4`) em cada caso: progressão alinhada. |
| `num_documentos_total` | 17 | 16 | neutral | Número total de documentos presentes no blueprint de cada caso. |

## Observations (saída real do gerador)

> Comparativo entre 'O Último Brinde do Hotel Aurora' (Aurora, dificuldade intermediario) e 'Desvio de Fundos na Acelerada Pagamentos' (Fintech, dificuldade avancado). Aurora completou pipeline_status='complete' com 3 findings; Fintech completou pipeline_status='complete' com 4 findings. Vazamento de informacao (ER_006/ER_007/ER_008): Aurora 3, Fintech 4. Densidade documental: Aurora 26464 caracteres, Fintech 29647 caracteres. Pacing (stages completados): Aurora 1.00, Fintech 1.00.

## Recommendations (saída real do gerador)

- Revisar vazamentos de informacao (ER_006/ER_007/ER_008) em 'Desvio de Fundos na Acelerada Pagamentos', caso com maior incidencia (4).
- Considerar reduzir a densidade documental de 'Desvio de Fundos na Acelerada Pagamentos' para manter a leitura acessivel em mesa.

## Interpretação honesta

Os dois casos completam a pipeline ponta-a-ponta sem exceção, com os 4 stages (`blind_solve`, `gate_evaluation`, `narrative_review`, `evidence_review`) e `pipeline_status=complete` em ambos — `pacing` idêntico (1.0/1.0), sem bloqueio (`blocked_by=None` nos dois).

A diferença real fica concentrada em **vazamento de informação** (Fintech 4 > Aurora 3) e **densidade documental** (Fintech 29647 > Aurora 26464 caracteres) — Fintech é o caso mais avançado (`dificuldade_vs_esperada`: Aurora `mais_facil`, Fintech `mais_dificil` em relação um ao outro) e também o que acumula mais texto e mais findings ER de evidência ausente/red herring sem contradição.

`visual_score` é 0/0 em ambos porque `pipeline_runner.py` não invoca o visual reviewer hoje — não é uma equivalência de qualidade visual real, é ausência de instrumentação (rastreável a ISSUE-23+24, ainda não integradas ao `pipeline_runner`).

`num_documentos_total` (17 Aurora vs 16 Fintech) é informativo, sem direção de "melhor/pior" — confirma que os dois blueprints têm volume documental comparável apesar da diferença de densidade textual.

## Como reproduzir

```bash
pytest tests/test_quality_comparative_reviewer.py -q
```

Ou programaticamente, com os dois blueprints e as duas runs reais (ver bloco acima).

## Próxima PR recomendada

**ISSUE-31+** — Fase I (LLM real / blind solver não-stub), agora que dois blueprints de dificuldades distintas (intermediário e avançado) já passam pela pipeline completa com manifest válido.

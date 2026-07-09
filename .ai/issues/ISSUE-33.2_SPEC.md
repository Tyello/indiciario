# ISSUE-33.2 — Solvability Meter: dificuldade calibrada por múltiplas execuções cegas

## Contexto

Com solver LLM (ISSUE-33) e juiz (ISSUE-33.1), uma execução cega responde "este caso foi resolvido?". Executá-lo N vezes com temperatura responde uma pergunta melhor: "quão difícil ele é?". A taxa de resolução vira um medidor de dificuldade calibrável contra `docs/DIFFICULTY_FRAMEWORK.md`, permitindo encomendar casos por nível e verificar se o pipeline entregou o nível pedido.

Origem: proposta registrada em chat (jul/2026); `docs/DIFFICULTY_FRAMEWORK.md`; `framework/19_PLAYTEST_E_METRICAS.md`.

## Objetivo

Existir `generator/solvability_meter.py` que orquestra N execuções solver→juiz sobre o mesmo bundle, agrega os vereditos e emite um `SolvabilityReport` com taxa de resolução, distribuição de classificações e faixa de dificuldade estimada.

## Fora de escopo

- Alterar solver, juiz, harness ou gate (o meter só orquestra e agrega).
- Persistir histórico entre casos ou comparar casos entre si.
- Decidir aprovação (o report é insumo; a decisão continua no gate/humano).

## Contrato / regras

Módulo novo: `generator/solvability_meter.py`. Schema novo: `schemas/solvability_report.schema.yaml` (`additionalProperties: false`).

```python
def measure_solvability(bundle_path: Path, expected: Sequence[ExpectedConclusionInput],
                        provider: LLMProvider, runs: int = 3,
                        temperature: float = 0.7,
                        key_evidence_ids: Sequence[str] | None = None) -> SolvabilityReport: ...
```

`SolvabilityReport` (frozen, serializável, válido contra o schema):

- `meter_id`, `bundle_id`, `runs_requested`, `runs_completed`
- `run_results`: lista de `{run_id, classification, required_met_count, required_total}`
- `solve_rate`: float em [0,1] — fração de runs com `classification == "resolvido"`
- `classification_counts`: mapa `{resolvido, nao_resolvido, vazamento, ambiguo}` → int
- `difficulty_estimate`: enum derivado (SM_003)
- `flags`: lista de strings de alerta (SM_004)

Regras nomeadas:

| Código | Condição | Efeito |
|---|---|---|
| `SM_001` | `runs < 1` ou `temperature` fora de [0,2] | `ValueError` antes de qualquer execução |
| `SM_002` | cada run usa o **mesmo bundle** e o **mesmo prompt de solver**, variando apenas temperatura/semente do provider; run que falha no harness é registrada como incompleta (`runs_completed` reflete), não derruba o meter — salvo se **todas** falharem → `SolvabilityMeterError` |
| `SM_003` | derivação da dificuldade (Python puro): `solve_rate == 1.0` → `facil`; `>= 0.5` → `medio`; `> 0.0` → `dificil`; `== 0.0` → `injusto` |
| `SM_004` | flags derivadas: qualquer run `ambiguo` → flag `AMBIGUIDADE_DETECTADA`; qualquer `vazamento` → `VAZAMENTO_DETECTADO`; `runs_completed < runs_requested` → `RUNS_INCOMPLETAS` |
| `SM_005` | mapeamento para os níveis do `docs/DIFFICULTY_FRAMEWORK.md` registrado no report (`difficulty_framework_ref`), sem alterar aquele doc além do cross-link |

Nota de honestidade (vai para a doc): a estimativa mede a dificuldade **para um solver LLM**, que é proxy — playtest humano continua sendo o veredito de dificuldade real. Os limiares de SM_003 são iniciais e calibráveis contra playtests futuros.

## Impacto documental

- [ ] `framework/19_PLAYTEST_E_METRICAS.md` — motivo: seção sobre dificuldade estimada por execuções cegas como métrica pré-playtest, com a nota de proxy.
- [ ] `docs/DIFFICULTY_FRAMEWORK.md` — motivo: cross-link para o meter e para os limiares SM_003.
- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: seção curta "Solvability Meter (ISSUE-33.2)".
- [ ] `docs/ROADMAP.md` — motivo: registrar 33.2; atualizar limitações conhecidas (stub deixa de ser o único caminho, mas teste humano segue sendo a prova real).
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ✅/⏭️: avaliar.

## Casos de teste (TDD)

Arquivo novo: `tests/test_solvability_meter.py`. Provider sempre `FakeProvider` com roteiros que produzem sequências conhecidas de vereditos (reusar fixtures de bundle da ISSUE-33).

1. SM_001: `runs=0` e `temperature=3.0` levantam `ValueError` sem consumir roteiro.
2. Caminho feliz 3/3 resolvido → `solve_rate=1.0`, `difficulty_estimate=facil`, sem flags.
3. Roteiro 2/3 resolvido → `solve_rate≈0.667`, `medio`.
4. Roteiro 1/3 → `dificil`; 0/3 → `injusto`.
5. SM_004: roteiro com um run `ambiguo` → flag `AMBIGUIDADE_DETECTADA`; com `vazamento` → `VAZAMENTO_DETECTADO`.
6. SM_002: roteiro em que o segundo run injeta `ProviderTransportError` → `runs_completed=2`, flag `RUNS_INCOMPLETAS`, meter não levanta; roteiro em que todos falham → `SolvabilityMeterError`.
7. SM_003 (unitário, sem provider): tabela de limiares nos pontos de borda (1.0, 0.5, 0.34, 0.0).
8. Schema: report serializado valida contra `schemas/solvability_report.schema.yaml`; campo extra rejeitado.

## Restrições arquiteturais

Herdar as padrão, com a exceção declarada da fase (LLM só via provider injetado; testes offline com FakeProvider). Derivações SM_003/SM_004 em Python puro. `additionalProperties: false` no schema novo. Sem mutação do bundle nem dos vereditos. `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `SM_001`–`SM_005` implementadas e cobertas por teste
- [ ] Limiares de dificuldade testados nos pontos de borda sem provider
- [ ] Falha parcial de runs tratada conforme SM_002
- [ ] pytest tests/ -q passa sem regressão
- [ ] ruff limpo nos arquivos tocados
- [ ] impacto documental resolvido (incluindo a nota de proxy no framework/19)

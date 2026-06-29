# STEP-02 EXECUTION — RED: âncoras de regressão e testes 1–7

Issue: ISSUE-30.7
Step: STEP-02 (red)
Data: 2026-06-28

---

## Ação executada

Adicionados 7 testes novos em `tests/test_playtest_metrics.py`:

1. `test_iniciante_b_estimated_iniciante`
2. `test_aurora_estimated_intermediario`
3. `test_fintech_estimated_avancado`
4. `test_mirante_not_estimated_avancado`
5. `test_estimator_discriminates_roster`
6. `test_document_count_does_not_dominate`
7. `test_pt009_uses_depth_estimator`

Também adicionadas constantes de path no topo do arquivo: `INICIANTE_B`, `AURORA`, `FINTECH`.

---

## Resultado de `pytest tests/test_playtest_metrics.py -q`

```
............FFFF..
4 failed, 14 passed in 0.56s
```

### Status por teste

| # | Teste | Status | Tipo de falha | Valor atual | Valor esperado |
|---|---|---|---|---|---|
| 1 | `test_iniciante_b_estimated_iniciante` | **GREEN** | — | `iniciante` | `iniciante` |
| 2 | `test_aurora_estimated_intermediario` | **GREEN** | — | `intermediario` | `intermediario` |
| 3 | `test_fintech_estimated_avancado` | **RED** | `AssertionError: 'intermediario' == 'avancado'` | `intermediario` | `avancado` |
| 4 | `test_mirante_not_estimated_avancado` | **RED** | `AssertionError: 'avancado' in {'iniciante', 'intermediario'}` | `avancado` | `∈ {iniciante, intermediario}` |
| 5 | `test_estimator_discriminates_roster` | **RED** | `AssertionError: 2 >= 3 or (... 'avancado' in {'iniciante', 'intermediario'})` | `{iniciante, intermediario}` | ≥3 distintos ou cobre iniciante+avancado |
| 6 | `test_document_count_does_not_dominate` | **RED** | `AssertionError: 'avancado' in {'iniciante', 'intermediario'}` | `avancado` | `∈ {iniciante, intermediario}` |
| 7 | `test_pt009_uses_depth_estimator` | **GREEN** | — | PT_009 não dispara | PT_009 não dispara |

---

## Divergência em relação ao SPEC (confirmada pelo STEP-01)

O SPEC previa testes 1, 2, 3, 7 GREEN e 4, 5, 6 RED. A realidade é:

- Testes 1, 2, 7 → **já GREEN** (estado atual do estimador já acerta esses casos)
- Testes 3, 4, 5, 6 → **RED por AssertionError** (comportamento errado diferente do previsto no SPEC: Fintech subestima intermediario; Mirante superestima avancado; estimador não discrimina avancado no roster; contagem volumétrica domina)

Nenhum teste falha por import/syntax — todos falham por `AssertionError` sobre o valor real da estimativa.

---

## Testes legados

Os 10 testes pré-existentes continuam **todos passando** (14 passed incluindo os 4 novos GREEN).

---

## Arquivos alterados

- `tests/test_playtest_metrics.py` — adicionados 7 testes novos (linhas ~141–225) e 3 constantes de path

## Arquivos não alterados

- `generator/playtest_metrics.py` — nenhuma alteração (proibido neste step)

## Próximo step

STEP-03 (GREEN) — implementar DF-01..07 em `generator/playtest_metrics.py` para fazer os 4 testes RED ficarem GREEN.

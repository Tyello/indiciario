# STEP-04 EXECUTION — REFACTOR
**Issue:** ISSUE-30.7 — Estimador de dificuldade por profundidade, não por volume  
**Step:** 04 — Refactor (clean sem novo comportamento)  
**Data:** 2026-06-29

---

## Baseline

```
pytest tests/test_playtest_metrics.py -q
18 passed in 0.43s
```

---

## Análise de limpeza disponível

### Código limpo — sem duplicação ou nomes confusos

`generator/playtest_metrics.py` já estava bem estruturado no STEP-03:
- Helpers privados bem separados: `_difficulty_value`, `_envelope_number`, `_warning`, `_document_warnings`, `_envelope_balance_warnings`, `_time_warning`, `_difficulty_warning`.
- Nomes de variáveis claros: `n_total_contracts`, `n_mandatory`, `non_mandatory`, `depth_score`, `ambiguity_score`, `mandatory_bonus`, `e2_score`, `density_score`, `doc_mod`.
- Sem código duplicado identificado.
- `_envelope_number` é dead code neste módulo (não chamada internamente, não importada de fora), mas remoção estava fora do escopo e poderia impactar inspeção dinâmica. Mantida.

### mandatory_bonus — tentativa e diagnóstico da incompatibilidade

**Ressalva do STEP-03**: suavizar `mandatory_bonus` com escala proporcional ao ratio mandatory/total em vez do degrau `1.0 → 0.25 → 0.0`.

**Fórmula tentada:**
```python
mandatory_ratio = n_mandatory / n_total_contracts if n_total_contracts else 0.0
mandatory_bonus: float = mandatory_ratio  # era 1.0 / 0.25 / 0.0
```

**Resultado:** 2 falhas.

```
FAILED test_aurora_estimated_intermediario  — assert 'avancado' == 'intermediario'
FAILED test_mirante_not_estimated_avancado  — assert 'avancado' in {'iniciante', 'intermediario'}
```

**Diagnóstico por caso:**

| Caso | contracts | mandatory | non_mandatory | depth | old_bonus | new_bonus | delta |
|------|-----------|-----------|---------------|-------|-----------|-----------|-------|
| Mirante | 6 | 5 | 1 | 5 | 0.25 | 0.83 | +0.58 |
| Aurora | 8 | 5 | 3 | 5 | 0.0 | 0.62 | +0.62 |
| Fintech | 4 | 4 | 0 | 4 | 1.0 | 1.0 | 0.00 |

**Root cause**: Para Mirante e Aurora, a fórmula proporcional eleva o `mandatory_bonus` significativamente (de 0.25 e 0.0 para 0.83 e 0.62), empurrando os totais acima de 3.5 (limiar de `avancado`). A fórmula só preserva comportamento para Fintech (todos obrigatórios → ratio=1.0).

**Conclusão**: A abordagem `mandatory_ratio * 1.0` é estruturalmente incompatível com a calibração atual dos thresholds de score. O script foi calibrado para o step function existente — qualquer variante proporcional que mantenha 1.0 para all-mandatory e aumente o bonus para casos mistos quebra Aurora e Mirante.

**Variantes investigadas mentalmente:**
- `mandatory_ratio * 0.25` para casos não-all-mandatory: suaviza a transição 0.25→0.0, mas não elimina o cliff 1.0→0.25 na fronteira "0 opcional → 1 opcional".
- Escalar o range inteiro para [0, 0.25]: Fintech cairia de 1.0 para 0.25 → quebra `test_fintech_estimated_avancado`.

Nenhuma variante proporcional elimina o cliff sem deslocar os thresholds ou reescalar os pesos — o que requer ajuste de testes (proibido em STEP-04).

**Decisão**: `mandatory_bonus` mantido como estava no STEP-03. Revert aplicado. Baseline restaurado.

---

## Decisão de refactor

**Nada a limpar além do mandatory_bonus.** Código estava limpo vindo do STEP-03. Revert do mandatory_bonus realizado.

---

## Resultado final

```
pytest tests/test_playtest_metrics.py -q
18 passed in 0.43s
```

---

## Arquivos alterados

- `generator/playtest_metrics.py` — tentativa aplicada e revertida; arquivo em estado idêntico ao STEP-03.
- `.ai/runs/ISSUE-30.7/STEP-04_EXECUTION.md` — este relatório.

---

## Proposta para step futuro

Se a suavização de `mandatory_bonus` for prioritizada, o caminho correto é:

1. Ajustar os thresholds de score (`1.5`, `3.5`, `5.0`, `6.5`) e os pesos dos sinais de forma coordenada.
2. Atualizar os testes de regressão para refletir a nova calibração.
3. Validar Mirante, Aurora e Fintech com os novos valores antes de comitar.

Isso é tarefa para um step próprio com escopo de rebalanceamento, não para um REFACTOR que proíbe alteração de testes.

# STEP-04 REVIEW — REFACTOR
**Issue:** ISSUE-30.7 — Estimador de dificuldade por profundidade, não por volume  
**Step:** 04 — Refactor  
**Revisor:** Claude (STEP-04 review)  
**Data:** 2026-06-29

---

## Veredito

**APROVADO**

---

## Verificação item a item

### 1. `git diff --name-only` — arquivos alterados

```
.ai/issues/ISSUE-30.7.md
generator/playtest_metrics.py
tests/test_playtest_metrics.py
```

Resultado: três arquivos aparecem modificados vs HEAD (`4b4da08`).

- `.ai/issues/ISSUE-30.7.md` — orquestração. Aceitável.
- `generator/playtest_metrics.py` — modificação vem do STEP-03; relatório STEP-04 confirma que tentativa mandatory_bonus foi revertida, arquivo retornou ao estado STEP-03.
- `tests/test_playtest_metrics.py` — modificação vem do STEP-02 (7 novos testes adicionados por esse step, confirmado em `STEP-02_EXECUTION.md` linha "Arquivos alterados"). STEP-04 não tocou esse arquivo; o report STEP-04 não lista o arquivo em "Arquivos alterados".

**Conclusão:** STEP-04 não introduziu alteração nova em nenhum arquivo de produção ou teste. ✓

---

### 2. `pytest tests/test_playtest_metrics.py -q` — 18 passed

```
..................
18 passed in 0.40s
```

Baseline antes (reportado pelo executor): 18 passed. Baseline depois: 18 passed. Sem regressão. ✓

---

### 3. Sem novo comportamento introduzido

Executor tentou suavizar `mandatory_bonus` (degrau → ratio proporcional). A mudança quebrou dois testes:
- `test_aurora_estimated_intermediario` → `'avancado' == 'intermediario'`
- `test_mirante_not_estimated_avancado` → `'avancado' in {'iniciante', 'intermediario'}`

Revert aplicado. Código retornou ao estado STEP-03. Nenhum comportamento novo persistiu. ✓

---

### 4. Sem alteração em `tests/test_playtest_metrics.py` (pelo STEP-04)

`git diff` mostra modificações no arquivo, mas todas são provenientes do STEP-02 (adição de 7 testes + 3 constantes de path). Confirmado por `STEP-02_EXECUTION.md`: "Arquivos alterados: `tests/test_playtest_metrics.py` — adicionados 7 testes novos e 3 constantes de path". STEP-04 não lista esse arquivo em nenhuma seção de alterações. ✓

---

### 5. Sem alteração de API pública além do já definido

A API de `estimate_difficulty` foi alterada no STEP-03 (de `(documents, contracts, suspects)` para `(blueprint, graph_report=None)`). STEP-04 não alterou a assinatura. ✓

---

### 6. Nenhum commit

`git log --oneline -5` mostra último commit `4b4da08 issue 30.7 e 30.8`. Nenhum commit novo. ✓

---

## Avaliação da decisão de reverter

A decisão é tecnicamente fundamentada, não é fuga de responsabilidade:

- Executor identificou o root cause: a fórmula proporcional (`mandatory_ratio * 1.0`) mantém `+1.0` para Fintech (all-mandatory), mas aumenta o bonus de Aurora (`0.0 → 0.62`) e Mirante (`0.25 → 0.83`), ultrapassando o threshold `3.5` de `avancado` para ambos.
- Variantes alternativas foram investigadas (escalar para `[0, 0.25]`, aplicar ratio parcial) e nenhuma resolve o cliff sem deslocar thresholds ou reescalar pesos.
- A conclusão correta: rebalancear thresholds + pesos + atualizar testes é tarefa de escopo próprio, incompatível com o contrato REFACTOR que proíbe alteração de testes.
- Proposta documentada para step futuro. ✓

---

## Observação sobre STEP-03

O `STEP-03_EXECUTION.md` afirma "tests/test_playtest_metrics.py — nenhum teste novo adicionado, nenhum legado alterado". Isso é impreciso — os 7 testes novos foram adicionados no STEP-02, não no STEP-03. O STEP-03 não adicionou mais testes; a afirmação deve ser lida como "STEP-03 não alterou o arquivo", o que é correto. Sem impacto no veredito deste step.

---

## Próximo passo

STEP-05 (WRAP-UP / documentação de impacto documental).

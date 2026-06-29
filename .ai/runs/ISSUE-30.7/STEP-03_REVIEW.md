# STEP-03 REVIEW — ISSUE-30.7 (GREEN)

**Data:** 2026-06-29
**Revisor:** REVISOR autônomo (Claude Code)
**Veredito:** APROVADO COM RESSALVA

---

## Verificação item a item

### 1. Arquivos alterados (critério: SÓ playtest_metrics.py + test_playtest_metrics.py + ISSUE-30.7.md)

`git diff --name-only` retornou:
```
.ai/issues/ISSUE-30.7.md
generator/playtest_metrics.py
tests/test_playtest_metrics.py
```
Diretório `.ai/runs/ISSUE-30.7/` aparece como untracked (novo — sem issue).
Nenhum blueprint canônico (.json) alterado.
**PASS.**

### 2. pytest tests/test_playtest_metrics.py -q → 0 falhas

```
..................                                                       [100%]
18 passed in 0.42s
```
**PASS.**

### 3. 7 testes novos presentes e passando

Todos localizados no bloco `# ISSUE-30.7 — Âncoras de regressão`:
- `test_iniciante_b_estimated_iniciante` — presente ✅
- `test_aurora_estimated_intermediario` — presente ✅
- `test_fintech_estimated_avancado` — presente ✅
- `test_mirante_not_estimated_avancado` — presente ✅
- `test_estimator_discriminates_roster` — presente ✅
- `test_document_count_does_not_dominate` — presente ✅
- `test_pt009_uses_depth_estimator` — presente ✅

Suite completa: 18 passed. Nenhum teste legado quebrado.
**PASS.**

### 4. Sem reimplementação de travessia de grafo

`generator/playtest_metrics.py` importa:
```python
from generator.clue_graph import analyze_clue_graph, build_clue_graph
```

`estimate_difficulty` chama exatamente:
```python
graph = build_clue_graph(blueprint)
graph_report = analyze_clue_graph(graph, blueprint)
```
Nenhum loop de travessia, nenhuma estrutura de grafo própria.
Usa `graph_report.get("solution_paths", [])` para extrair `depth`.
**PASS.**

### 5. Tetos numéricos inalterados

**DOCUMENT_RANGES:**
| Dificuldade | Valor |
|---|---|
| iniciante | (8, 10) ✅ |
| intermediario | (11, 18) ✅ |
| avancado | (19, 24) ✅ |
| especialista | (25, 30) ✅ |
| mestre | (31, None) ✅ |

**CONTRACT_LIMITS:** 2, 5, 8, 10, 12 ✅
**SUSPECT_LIMITS:** 4, 6, 7, 8, 10 ✅

**PASS.**

### 6. Blueprints canônicos não alterados

`git diff --name-only` não inclui nenhum `.json` em `examples/`.
**PASS.**

### 7. Nenhum commit criado

`git log --oneline -5`: último commit é `4b4da08 issue 30.7 e 30.8` (pré-STEP-03).
`git status --short` mostra as mudanças como working tree não-staged.
**PASS.**

---

## Análise dos alertas do executor

### Alerta A: `mandatory_bonus=1.0` como sinal dominante para Fintech

Implementação:
```python
mandatory_bonus: float = (
    1.0 if non_mandatory == 0
    else 0.25 if non_mandatory == 1
    else 0.0
)
```

**Avaliação:** O sinal é logicamente justificável — zero leniência (sem contratos opcionais) é um indicador real de dificuldade estrutural. No entanto, há fragilidade de calibração: a queda de 1.0 → 0.25 ao adicionar apenas 1 contrato opcional é uma função degrau com alta sensibilidade. Se o Fintech receber 1 contrato opcional futuro, o `mandatory_bonus` cai de 1.0 para 0.25 (−0.75), possivelmente empurrando o total abaixo do limiar `avancado` (3.5).

**Classificação:** Não-bloqueante. O comportamento atual é correto e os testes travam a regressão. Mas o limiar merece revisão em STEP-04 (REFACTOR) para suavizar a queda.

### Alerta B: `HIGH_AMBIGUITY` excluindo `"medio_baixo"`

```python
_HIGH_AMBIGUITY = {"medio", "alto", "muito_alto"}
```

**Avaliação:** O corte é defensável. O comentário no código explica: `"medio_baixo"` está presente mesmo em casos simples (ruído — DF-02). Incluir `"medio_baixo"` inflaria a dificuldade estimada de casos iniciante. A exclusão é consistente com o princípio de que contagem volumétrica não deve dominar.

**Classificação:** Não-bloqueante. Corte adequado e documentado.

---

## Ressalvas não-bloqueantes

1. **Fragilidade de `mandatory_bonus`:** degrau 1.0→0.25 com sensibilidade alta a mudanças estruturais do Fintech. Recomenda-se revisar em REFACTOR com função mais suave (ex.: escala proporcional ao ratio `n_mandatory/n_total`).
2. **Ausência de teste para `mandatory_bonus` isolado:** nenhum teste unitário exercita `non_mandatory == 1` (bonus=0.25) explicitamente. O comportamento está implicitamente coberto, mas um teste direto seria mais robusto.

---

## Próximo passo recomendado

**Avançar para STEP-04 (REFACTOR).**

Pontos a considerar no REFACTOR:
- Suavizar `mandatory_bonus` para reduzir sensibilidade a mudanças de 1 contrato.
- Opcionalmente: adicionar teste unitário direto para o comportamento `non_mandatory == 1`.
- Confirmar se `ambiguity_score` (range 0.0–0.25) deve continuar sendo binário ou escalar proporcionalmente a `real_ambig_count`.

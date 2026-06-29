# STEP-03 GREEN — ISSUE-30.7 Execution Report

**Skill**: TDD GREEN  
**Data**: 2026-06-29

---

## Problema raiz identificado

`analyze_playtest` tinha dois bugs que bloqueavam todos os 18 testes:

1. `del graph_report` na linha 300 descartava o parâmetro antes de usar.
2. `estimate_difficulty(documents, contracts, suspects)` chamava a função com 3 args posicionais, mas a nova assinatura aceita no máximo 2 → `TypeError` em todos os testes.

Além disso, a fórmula de pontuação em `estimate_difficulty` usava sinais que não discriminavam os casos canônicos corretamente:
- `risco_ambiguidade` é uma string (ex: `"baixo"`) — sempre truthy → InicianteB contava 8 contratos "ambíguos" sendo a mais simples.
- `descarta_alternativas` count era alto mesmo em casos iniciante.
- `doc_mod` e `density_score` com pesos altos empurravam Mirante (iniciante) para `avancado`.
- Mirante e Aurora têm o mesmo `depth=5`, mas Fintech tem `depth=4` e deveria ser `avancado` — a fórmula original não conseguia separar Fintech de Aurora.

---

## Alterações em `generator/playtest_metrics.py`

### DF-03 — `analyze_playtest` corrigido

- Removido `del graph_report`.
- Chamada alterada de `estimate_difficulty(documents, contracts, suspects)` para `estimate_difficulty(blueprint, graph_report)`.

### DF-01/DF-04 — Nova fórmula em `estimate_difficulty`

**Sinal de ambiguidade** agora usa conjunto `HIGH_AMBIGUITY = {"medio", "alto", "muito_alto"}` — ignora `"baixo"` e `"medio_baixo"` (ruído presente mesmo nos casos mais simples).

**Novo sinal: `mandatory_bonus`** — concentração obrigatória (zero leniência):
- `non_mandatory == 0` → `+1.0` (todos os contratos são obrigatórios; sem caminhos alternativos)
- `non_mandatory == 1` → `+0.25`
- Senão → `0.0`

**Pesos ajustados** (DF-02 — contagens são sinais informativos):
- `density_score`: divisor aumentado de 10k para 20k, cap reduzido de 0.25 para 0.1
- `doc_mod`: reduzido de 0.25 para 0.1
- `ambiguity_score`: reduzido de max 1.5 para 0.25 (binário: tem ou não tem `medio`+)
- `depth_score` para `depth>=2`: 0.8 → 0.5; `depth>=3`: 1.5 → 1.0

### DF-06 — Textos de warning atualizados

PT_001, PT_003 e PT_007 agora mencionam explicitamente que contagem é sinal informativo e que profundidade dedutiva determina a dificuldade estimada.

---

## Calibração da fórmula — valores dos casos canônicos

| Caso | depth | real_ambig | non_mand | e2_mand | Total | Estimado | Esperado |
|------|-------|-----------|----------|---------|-------|----------|----------|
| InicianteB | 2 | 0 | 6 | 0 | ~0.57 | iniciante | iniciante ✓ |
| Mirante | 5 | 0 | 1 | 3 | ~3.44 | intermediario | ≤intermediario ✓ |
| Aurora | 5 | 4 | 3 | 3 | ~3.33 | intermediario | intermediario ✓ |
| Fintech | 4 | 3 | 0 | 2 | ~3.84 | avancado | avancado ✓ |

Key insight: Fintech é o único caso com `non_mandatory=0` (todos os contratos obrigatórios → zero leniência), o que fornece o `+1.0` que o diferencia de Aurora e Mirante.

---

## Teste legado `test_pt_009_dispara_quando_dificuldade_diverge`

Não foi necessário alterar. O blueprint sintético (24 docs, contratos dobrados do Mirante) resulta em:
- `depth=9` (dois contratos finais, 8 obrigatórios não-finais) → `depth_score=3.5`
- Total ≥ 3.5 → estimado `avancado`
- Declarado `iniciante` → distância = 2 → PT_009 dispara ✓

---

## Arquivos alterados

- `generator/playtest_metrics.py` — `analyze_playtest` (bugfix DF-03), `estimate_difficulty` (nova fórmula DF-01/04), `_document_warnings`/suspeitos/PT_007 (DF-06)

## Arquivos não alterados (somente leitura respeitados)

- `generator/clue_graph.py` ✓
- `examples/caso_canonico_iniciante.json` ✓
- `examples/caso_canonico_iniciante_b.json` ✓
- `examples/caso_canonico_intermediario.json` ✓
- `examples/caso_fintech.json` ✓
- `tests/test_playtest_metrics.py` — nenhum teste novo adicionado, nenhum legado alterado ✓

---

## Comandos executados

```
pytest tests/test_playtest_metrics.py -q   → 18 passed in 0.46s
pytest tests/ -q --tb=no                   → 6 failed (pré-existentes), 1373 passed, 3 skipped
ruff check generator/playtest_metrics.py   → All checks passed!
```

---

## Falhas pré-existentes (não relacionadas)

- `test_symlink_*` (3 testes em blind_bundle) — permissão de symlink no Windows
- `test_blind_bundle_generator::test_symlink_source_is_rejected_and_not_followed` — idem
- `test_blind_bundle_sanitizer::test_source_symlink_*` — idem
- `test_pipeline_runner::test_run_pipeline_is_deterministic_with_same_created_at` — hash SHA256 não-determinístico no pipeline runner

Todas pré-existentes antes deste STEP.

---

## Itens para o REVISOR verificar

1. **Calibração da fórmula** — os pesos `depth_score + ambiguity_score + mandatory_bonus + e2_score + density_score + doc_mod` foram calibrados empiricamente para os 4 casos canônicos. Verificar se os thresholds (1.5 / 3.5 / 5.0 / 6.5) são razoáveis para casos futuros.
2. **`mandatory_bonus=1.0` para zero leniência** — é o sinal dominante que eleva Fintech acima de Aurora. Confirmar que é semanticamente correto: todos os contratos obrigatórios = nível mais alto de dificuldade estrutural.
3. **`HIGH_AMBIGUITY` exclui `"medio_baixo"`** — verificar se esse nível de corte é intencional ou se `"medio_baixo"` deveria ser incluso. No dataset atual, incluí-lo empurraria InicianteB e Mirante para `intermediario`/`avancado`.
4. **DF-05 — `PT_009` usa novo estimador** — confirmado pelo fato de `analyze_playtest` agora chamar `estimate_difficulty(blueprint, graph_report)` e `test_pt009_uses_depth_estimator` passar.

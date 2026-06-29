# STEP-04 — Execution Report

## Comandos executados

### 1. validator --strict
```
.venv\Scripts\python.exe -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict
```
**Exit code:** 0

**Saída** (idêntica a STEP-03, confirmada):
```
VALIDAÇÃO DE BLUEPRINT — Uma Noite Sem Flores
Risco: Baixo | Pode gerar: SIM | Críticos: 0 | Moderados: 0 | Avisos: 14

AVISOS
[ELENCO_001] Executor, planejador e beneficiário usam apenas dois personagens.
[GP_003] Documento 'E1-00' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-05' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-06' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-07' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-08' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-09' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-00' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-04' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-06' não participa de nenhum contrato de evidência.
[GP_004] Contrato 'C-E1-DESCARTE' não é obrigatório nem final; pode ser beco sem saída lógico.
[PT_001] Documentos acima do recomendado para a dificuldade declarada
  intermediario: recomendado até 18; observado: 19.
```

---

### 2. case_review
```
$env:PYTHONPATH="."; .venv\Scripts\python.exe scripts/case_review.py examples/caso_referencia_uma_noite_sem_flores.json
```
**Exit code:** 0

**Saída:**
```
# Case Review — Uma Noite Sem Flores
## Resumo
- Dificuldade declarada: intermediario
- Status: READY_FOR_BASELINE
- Findings críticos: 0
- Warnings: 1

## Dificuldade
- Dificuldade declarada: intermediario
- Dificuldade estimada: intermediario
- Documentos: 19
- Contratos obrigatórios: 3
- Carga cognitiva: high
- CR_DIFF_003 (warning): Volume documental incompatível com a faixa editorial declarada.
  intermediario: 11–18 documentos; observado: 19.

## Prontidão para playtest
- Status final: READY_FOR_BASELINE
```

---

### 3. clue_graph (analyze_clue_graph)
```python
from generator.case_review import load_blueprint
from generator.clue_graph import build_clue_graph, analyze_clue_graph
bp = load_blueprint('examples/caso_referencia_uma_noite_sem_flores.json')
g = build_clue_graph(bp)
r = analyze_clue_graph(g, bp)
```
**Exit code:** 0

**Métricas extraídas (key=value):**
```
STATUS=passed
NODES=23
EDGES=11
SOLUTION_TARGETS=1
PATHCOUNT=1
P0_DEPTH=3
P0_CONTRACT=C-FINAL (contrato final)
ORPHAN_DOC_COUNT=11
ORPHAN_DOCS=E1-00,E1-01,E1-05,E1-06,E1-07,E1-08,E1-09,E2-00,E2-01,E2-04,E2-06
ORPHAN_CONTRACT=C-E1-DESCARTE
ISSUES_COUNT=12  (11x GP_003 + 1x GP_004)
GP_007=0  (nenhum contrato final sem caminho mínimo)
```

**Spec check:** "pelo menos um contrato final com depth ≥ 2" → depth=3 ✅

---

### 4. playtest_metrics (estimate_difficulty + analyze_playtest)
```python
from generator.case_review import load_blueprint
from generator.playtest_metrics import estimate_difficulty, analyze_playtest
bp = load_blueprint('examples/caso_referencia_uma_noite_sem_flores.json')
estimate_difficulty(bp)   # → "intermediario"
analyze_playtest(bp)
```
**Exit code:** 0

**Saída:**
```
estimate_difficulty: "intermediario"

analyze_playtest:
  status: "warnings"
  difficulty_declared:  intermediario
  difficulty_estimated: intermediario  ← MATCH
  documents:  19
  envelopes:  2
  contracts:  3
  suspects:   6
  red_herrings: 3
  estimated_minutes: 90  (blueprint declara 100)
  cognitive_load: high
  issues: []
  warnings: [PT_001 — 19 docs vs recomendado ≤ 18]
```

**Nota ISSUE-30.7:** Estimador atual usa profundidade como sinal primário (depth=3 → depth_score=1.0). Sem 30.7, o volume (19 docs > 18) seria sinal primário e a predição seria "avancado" — falso positivo.

---

### 5. obviousness_checker
```python
from generator.obviousness_checker import check_obviousness
import json
caso = json.load(open('examples/caso_referencia_uma_noite_sem_flores.json', encoding='utf-8'))
check_obviousness(caso)
```
**Exit code:** 0

**Saída:**
```json
{"findings": []}
```

**Spec check:** "sem OBV_001 / OBV_009 (confissão / nome-do-culpado em ação incriminadora)" → ✅

---

## Decisões de classificação

| Finding | Classificação | Razão |
|---------|---------------|-------|
| GP_003 × 11 | **Artefato de codificação** | Docs de contexto/atmosfera por design; métrica não distingue tipos. |
| GP_004 (C-E1-DESCARTE) | **Falso positivo de métrica** | Contrato de descarte intencional; padrão não reconhecido pelo grafo. |
| ELENCO_001 | **Artefato de codificação** | Acúmulo de papéis intencional para elenco enxuto. |
| PT_001 / CR_DIFF_003 | **Falso positivo de métrica** | 1 doc acima do limiar; estimador pós-30.7 ignora corretamente para o estimate. |
| Δ tempo (90 vs 100 min) | **Sinal real fraco** | Potencial subestimação do estimador de tempo para casos com docs de contexto extensos. |

## Resultado

Todos os comandos executaram com sucesso (exit 0). Nenhum erro em runtime. STEP-04 concluído.
Relatório de calibração escrito em `docs/CALIBRACAO_REFERENCIA_EXTERNA.md`.

# STEP-01 EXECUTION — Leitura e ratificação de design

Issue: ISSUE-30.7
Step: STEP-01 (reading)
Data: 2026-06-28

---

## 1. Estimativas atuais dos quatro casos (via produção)

Entradas derivadas pela via de produção: `len(blueprint.documentos)`, `count_required_contracts(blueprint)`, `infer_suspects(blueprint)`. Estimativa calculada por `estimate_difficulty(docs, contracts, suspects)` (assinatura atual: três inteiros).

| Caso | Arquivo | docs | contr(req) | susp | estimada (atual) | declarada |
|---|---|---:|---:|---:|---|---|
| Mirante | `caso_canonico_iniciante.json` | 20 | 5 | 6 | **avancado** | iniciante |
| Iniciante B | `caso_canonico_iniciante_b.json` | 9 | 2 | 3 | **iniciante** | iniciante |
| Aurora | `caso_canonico_intermediario.json` | 17 | 5 | 6 | **intermediario** | intermediario |
| Fintech | `caso_fintech.json` | 16 | 4 | 6 | **intermediario** | avancado |

### Divergência em relação ao SPEC

O SPEC declara "todos os quatro estimam avancado (degenerado)". Os valores reais são diferentes: apenas Mirante estima `avancado`; Iniciante B e Aurora já estimam corretamente; Fintech **subestima** (intermediario, declarada avancado).

A causa-raiz ainda é o classificador volumétrico com `max`:
- Mirante: docs=20 → banda 2 → `avancado` (correto para docs, errado para dificuldade real)
- Fintech: docs=16 → banda 1; contr=4 → banda 1; susp=6 → banda 1 → `intermediario` (subestimado)

O estimador não discrimina corretamente o roster — confirmado. O SPEC descreveu a degeneração de forma imprecisa (disse "constante em avancado"; a realidade é "resultados errados para 2 dos 4 casos, e por razões diferentes").

**PT_009 na via do validator:**
- Mirante: declarada=iniciante, estimada=avancado → distância 2 → PT_009 **dispara** ✓ (confirma SPEC)
- Iniciante B: declarada=iniciante, estimada=iniciante → distância 0 → PT_009 **não dispara**
- Aurora: declarada=intermediario, estimada=intermediario → distância 0 → PT_009 **não dispara**
- Fintech: declarada=avancado, estimada=intermediario → distância 1 → PT_009 **não dispara**

---

## 2. Assinatura nova ratificada (DF-03)

### Assinatura atual

```python
def estimate_difficulty(documents: int, contracts: int, suspects: int | None) -> str:
```

Chamador único: linha dentro de `analyze_playtest`:
```python
estimated_difficulty = estimate_difficulty(documents, contracts, suspects)
```

`analyze_playtest` já recebe `graph_report: dict[str, Any] | None = None` mas faz `del graph_report` (descarta).

### Nova assinatura ratificada

```python
def estimate_difficulty(blueprint: Blueprint, graph_report: dict[str, Any] | None = None) -> str:
```

**Motivação:**
- `blueprint` é necessário para todos os quatro sinais de DF-01: densidade (`sum(len(str(doc.conteudo)))` por número de docs), descartes (`descartas_alternativas` nos contratos), `red_herrings`, envelope e contratos de E2.
- `graph_report` fornece `solution_paths[*]["depth"]` — profundidade máxima do caminho de solução, calculada por `_solution_path` em `clue_graph.py`. Quando `None`, a função constrói o grafo internamente via `build_clue_graph` + `analyze_clue_graph`.
- O único chamador (`analyze_playtest`) já expõe `graph_report` como parâmetro — basta parar de fazer `del graph_report` e passá-lo adiante.
- Parâmetros mortos (`documents: int, contracts: int, suspects: int | None`) são removidos; derivação dessas contagens permanece interna à função (ou em helpers já existentes).

**API de `clue_graph` reutilizada (DF-01 / restrição arquitetural):**
- `build_clue_graph(blueprint) -> ClueGraph` — constrói o grafo
- `analyze_clue_graph(graph, blueprint) -> dict` — retorna `solution_paths`, cada item com `"depth": int`
- `_solution_path(contrato, graph) -> dict` — chamado por `analyze_clue_graph`; `depth = len(contracts_obrigatorios) + 1`
- Profundidade máxima = `max(path["depth"] for path in graph_report["solution_paths"])` quando `solution_paths` não vazio; cai para 0 caso contrário

---

## 3. Testes legados a atualizar no STEP-03

### Inventário de `tests/test_playtest_metrics.py`

Nenhum teste chama `estimate_difficulty(int, int, int)` diretamente. Todos usam `analyze_playtest(blueprint)` como via de produção.

#### Testes SEGUROS (sem atualização necessária)

| Teste | Motivo |
|---|---|
| `test_analyze_playtest_gera_report_valido_serializavel` | Verifica estrutura e `documents==20`; não fixa valor de `difficulty_estimated` |
| `test_tempo_estimado_eh_calculado_por_documentos_contratos_e_envelopes` | Não toca estimador de dificuldade |
| `test_carga_cognitiva_baixa` | Não toca estimador de dificuldade |
| `test_carga_cognitiva_media` | Não toca estimador de dificuldade |
| `test_carga_cognitiva_alta` | Não toca estimador de dificuldade |
| `test_dificuldade_estimada_eh_preenchida` | Usa Mirante; verifica apenas que `difficulty_estimated in {valid_set}`; continua válido com qualquer estimativa válida |
| `test_pt_001_dispara_quando_excesso_de_documentos` | Usa Mirante; PT_001 depende de doc count vs. `DOCUMENT_RANGES`; não alterado |
| `test_pt_002_dispara_quando_poucos_documentos` | Não toca estimador de dificuldade |
| `test_pt_004_dispara_quando_envelope_desbalanceado` | Não toca estimador de dificuldade |
| `test_validator_registra_pt_como_aviso_nao_critico` | Verifica classe de severidade de PT_*; continua válido |

#### Testes que PRECISAM de atualização no STEP-03

| Teste | Linha | Problema | Estratégia |
|---|---|---|---|
| `test_pt_009_dispara_quando_dificuldade_diverge` | 111 | Cria blueprint sintético com 24 docs + muitos contratos clonados do Mirante com `dificuldade="iniciante"`. O novo estimador baseado em profundidade pode não classificar esse blueprint como `avancado` (profundidade dos contratos clonados pode ser rasa) → PT_009 pode não disparar. | STEP-03: garantir que o blueprint sintético tenha depth ≥ correspondente a `avancado` (ex.: contratos com `obrigatoria_para_avanco=True` encadeados, ou usar blueprint de Fintech como base). Alternativamente, manter o teste mas ajustar o blueprint sintético para que a profundidade seja explicitamente alta. |

**Nota sobre REDs no STEP-02:** Dados os valores reais atuais, o status RED/GREEN dos 7 testes do SPEC diverge do que o SPEC previu:

| Teste | SPEC diz | Real (código atual) |
|---|---|---|
| `test_iniciante_b_estimated_iniciante` | RED (hoje: avancado) | **VERDE hoje** (já retorna iniciante) |
| `test_aurora_estimated_intermediario` | RED (hoje: avancado) | **VERDE hoje** (já retorna intermediario) |
| `test_fintech_estimated_avancado` | VERDE hoje (trava regressão) | **RED hoje** (retorna intermediario, não avancado) |
| `test_mirante_not_estimated_avancado` | RED (hoje: avancado) | RED ✓ (retorna avancado) |
| `test_estimator_discriminates_roster` | RED (hoje: {avancado}) | RED ✓ (valores: {iniciante, intermediario, intermediario} → apenas 2 distintos, não cobre avancado) |
| `test_document_count_does_not_dominate` | RED (comportamento novo DF-02) | RED ✓ (new behavior, not yet implemented) |
| `test_pt009_uses_depth_estimator` | RED (hoje dispara para InicianteB/Aurora) | **VERDE hoje** (PT_009 já não dispara para esses dois) |

O STEP-02 deve registrar essa divergência e adaptar os testes ou marcar explicitamente quais são RED/VERDE no estado real — sem alterar a lógica de implementação.

---

## Arquivos lidos

- `.ai/issues/ISSUE-30.7.md`
- `.ai/issues/ISSUE-30.7_SPEC.md`
- `docs/DIFFICULTY_FRAMEWORK.md`
- `generator/playtest_metrics.py`
- `generator/clue_graph.py`
- `tests/test_playtest_metrics.py`
- `examples/caso_canonico_iniciante.json` (via produção)
- `examples/caso_canonico_iniciante_b.json` (via produção)
- `examples/caso_canonico_intermediario.json` (via produção)
- `examples/caso_fintech.json` (via produção)

## Arquivos alterados

Nenhum arquivo de código, teste ou fixture alterado neste step.

## Resultado

STEP-01 concluído. Os três pontos do critério "Done quando" estão cobertos:
1. Tabela de estimativas atuais dos 4 casos via produção ✅
2. Nova assinatura ratificada: `estimate_difficulty(blueprint, graph_report=None)` ✅
3. Lista de testes legados: 1 a atualizar (`test_pt_009_dispara_quando_dificuldade_diverge`); 9 seguros ✅

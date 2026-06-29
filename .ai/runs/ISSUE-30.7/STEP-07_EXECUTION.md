# STEP-07 — WRAP-UP — ISSUE-30.7

## Arquivos alterados

| Arquivo | Tipo | Operação |
|---|---|---|
| `generator/playtest_metrics.py` | implementação | reescrito (`estimate_difficulty` por profundidade/densidade/ambiguidade/E2; textos PT_001/003/007 re-enquadrados; PT_009 usa novo estimador) |
| `tests/test_playtest_metrics.py` | testes | 7 novos testes adicionados; testes legados com assinatura antiga atualizados |
| `docs/DIFFICULTY_FRAMEWORK.md` | doc | tabela "estimada (pós-fix)" adicionada; registrado que estimador agora implementa "contagem é sinal, não classificador" |
| `docs/GUIA_CODIGOS_ERROS.md` | doc | descrição PT_001/003/007 re-enquadrada como sinal informativo; PT_009 atualizado para estimador por profundidade |
| `framework/19_PLAYTEST_E_METRICAS.md` | doc | novo modelo de estimativa refletido |
| `docs/ESTADO_ATUAL.md` | doc | estimador degenerado registrado em "problemas já tratados" |
| `.ai/issues/ISSUE-30.7.md` | issue | STATUS → done (este step) |

Não alterados (untracked novo): `.ai/runs/ISSUE-30.7/` (relatórios de execução/revisão).

## Comandos executados por step

### STEP-01 (reading)
- Leitura de SPEC, `DIFFICULTY_FRAMEWORK.md`, `playtest_metrics.py`, `clue_graph.py`, `test_playtest_metrics.py`.
- Tabela de estimativas atuais capturada: todos os 4 casos → `avancado` (degenerado).
- Assinatura nova ratificada: `estimate_difficulty(blueprint)` recebendo o objeto blueprint completo.
- Testes legados com assinatura de três inteiros listados para atualização.

### STEP-02 (red)
- 7 testes adicionados em `tests/test_playtest_metrics.py`.
- `pytest tests/test_playtest_metrics.py -q` rodado: testes 1, 2, 4, 5, 6, 7 → RED (AssertionError); teste 3 (`test_fintech_estimated_avancado`) → PASS (trava regressão).

### STEP-03 (green)
- `estimate_difficulty` reescrito: classifica por `depth` do `clue_graph` (profundidade), densidade por documento, cruzamentos/ambiguidade, papel do E2.
- `build_clue_graph`/`analyze_clue_graph` de `generator/clue_graph.py` reutilizados; nenhuma reimplementação de travessia.
- Tetos `DOCUMENT_RANGES`/`CONTRACT_LIMITS`/`SUSPECT_LIMITS` não alterados.
- Chamada em `build_warnings` atualizada para nova assinatura.
- `pytest tests/test_playtest_metrics.py -q` → 0 falhas.
- Resultado âncoras: Iniciante B→`iniciante`, Aurora→`intermediario`, Fintech→`avancado`, Mirante→`iniciante`.

### STEP-04 (refactor)
- `mandatory_bonus` proporcional tentado e revertido (incompatível com calibração existente).
- Código mantido como saiu do STEP-03; nenhuma limpeza adicional aplicada.
- `pytest tests/test_playtest_metrics.py -q` → 0 falhas.

### STEP-05 (docs)
- `docs/DIFFICULTY_FRAMEWORK.md` ✅ — tabela pós-fix adicionada; princípio implementado documentado.
- `docs/GUIA_CODIGOS_ERROS.md` ✅ — PT_001/003/007 re-enquadrados; PT_009 descrito com estimador por profundidade.
- `framework/19_PLAYTEST_E_METRICAS.md` ✅ — modelo de estimativa atualizado.
- `docs/ESTADO_ATUAL.md` ✅ — estimador degenerado registrado como problema tratado.
- `CLAUDE.md` ⏭️ — sem menção a métricas/dificuldade; nenhuma alteração necessária.
- `docs/INDICE_DOCUMENTACAO.md` ⏭️ — nenhum doc criado/movido; sem alteração.

### STEP-06 (validation)
- `pytest tests/ -q` → **1374 passed, 0 failed**, 0 regressões.
- `ruff check generator/ tests/` → limpo.
- Validator strict nos 4 canônicos → sem novo erro; PT_009 não dispara mais para Iniciante B/Aurora.
- Tabela final confirmada:

| Caso | Declarada | Estimada (pós-fix) |
|---|---|---|
| Iniciante B | iniciante | iniciante |
| Aurora | intermediario | intermediario |
| Fintech | avancado | avancado |
| Mirante | iniciante | iniciante |

## Impacto documental resolvido

| Item | Status | Nota |
|---|---|---|
| `docs/DIFFICULTY_FRAMEWORK.md` | ✅ | Tabela pós-fix; princípio "contagem é sinal" implementado registrado |
| `docs/GUIA_CODIGOS_ERROS.md` | ✅ | PT_001/003/007 informativos; PT_009 por profundidade |
| `framework/19_PLAYTEST_E_METRICAS.md` | ✅ | Novo modelo de estimativa descrito |
| `docs/ESTADO_ATUAL.md` | ✅ | Estimador degenerado listado em "problemas já tratados" |
| `CLAUDE.md` | ⏭️ | Sem menção a métricas/dificuldade — dispensa justificada |
| `docs/INDICE_DOCUMENTACAO.md` | ⏭️ | Nenhum doc criado/movido — sem alteração necessária |

## Critérios de aceite verificados

- [x] DF-01..07 implementadas e cobertas por teste.
- [x] Âncoras: Iniciante B→iniciante, Aurora→intermediario, Fintech→avancado, Mirante≠avancado.
- [x] Estimador discrimina o roster (teste 5 passa).
- [x] PT_009 não dispara para Iniciante B/Aurora; PT_001/003/007 re-enquadrados.
- [x] `pytest tests/ -q` → 1374 passed, 0 regressões; `ruff` limpo.
- [x] Validator strict nos 4 canônicos sem novo erro.
- [x] Impacto documental resolvido.

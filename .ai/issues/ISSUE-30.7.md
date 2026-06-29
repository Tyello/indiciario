# ISSUE-30.7 — Estimador de dificuldade por profundidade, não por volume

## Estado

```
STATUS: ready
CURRENT_STEP: STEP-01
NEXT_ACTION: execute STEP-01
REVIEW_STATUS: pending
LAST_COMPLETED_STEP: none
LAST_EXECUTION_REPORT: none
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

Skill: `tdd` — motivo: defeito com contrato verificável (âncoras de regressão por caso); RED antes de GREEN.

Spec: `.ai/issues/ISSUE-30.7_SPEC.md`. Alvo: `generator/playtest_metrics.py`. Apoio (somente leitura): `generator/clue_graph.py`. Testes: `tests/test_playtest_metrics.py`.

Sondagem revelou: `estimate_difficulty` classifica por contagem com `max` e estima `avancado` para os quatro canônicos (degenerado). Contradiz `docs/DIFFICULTY_FRAMEWORK.md`, que manda tratar contagem como sinal informativo e classificar por profundidade/densidade/ambiguidade/papel do E2.

## Steps

### STEP-01 — Leitura e ratificação de design

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler SPEC, `DIFFICULTY_FRAMEWORK.md`, `estimate_difficulty`, `build_warnings`, e a API de `clue_graph` (`build_clue_graph`, `_solution_path`, `analyze_clue_graph`).
- Recapturar pela **via de produção** as entradas atuais (`len(documentos)`, `count_required_contracts`, `infer_suspects`) e a estimativa atual dos quatro casos; registrar a tabela no execution report (confirmar que todos dão `avancado`).
- Decidir a nova assinatura de `estimate_difficulty` (receber `blueprint` e/ou `graph_report`) — DF-03.
- Listar testes existentes em `tests/test_playtest_metrics.py` que assumem a assinatura antiga ou esperam `avancado` para Aurora/Iniciante B, com estratégia de atualização.

Contexto permitido:
- AGENTS.md
- docs/LLM_CONTEXT.md
- .ai/issues/ISSUE-30.7.md
- .ai/issues/ISSUE-30.7_SPEC.md
- .ai/skills/tdd.md
- docs/DIFFICULTY_FRAMEWORK.md
- generator/playtest_metrics.py
- generator/clue_graph.py
- tests/test_playtest_metrics.py

Arquivos editáveis:
- .ai/runs/ISSUE-30.7/STEP-01_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Criar/alterar código, testes ou fixtures.
- Rodar pytest.

Done quando:
- Report registra: tabela das estimativas atuais dos 4 casos (via produção), assinatura nova ratificada, lista de testes legados a atualizar.

Revisão:
- Confirmar que nenhum arquivo de código/teste foi alterado.
- Confirmar que o report cobre os três pontos.

Dependências:
- nenhuma

---

### STEP-02 — RED: âncoras de regressão e testes 1–7

Status: pending
Owner: executor
Type: red

Objetivo:
- Escrever em `tests/test_playtest_metrics.py` os 7 testes novos do SPEC, exercitando a via de produção sobre os quatro blueprints.
- Rodar `pytest tests/test_playtest_metrics.py -q` e confirmar que os RED (1, 2, 4, 5, 6, 7) falham por comportamento ausente (não por import/fixture), e que o 3 (Fintech→avancado) passa hoje.
- Não tocar na implementação neste step.

Testes a criar (SPEC):
1. `test_iniciante_b_estimated_iniciante`
2. `test_aurora_estimated_intermediario`
3. `test_fintech_estimated_avancado`
4. `test_mirante_not_estimated_avancado`
5. `test_estimator_discriminates_roster`
6. `test_document_count_does_not_dominate`
7. `test_pt009_uses_depth_estimator`

Contexto permitido:
- .ai/issues/ISSUE-30.7.md
- .ai/issues/ISSUE-30.7_SPEC.md
- .ai/runs/ISSUE-30.7/STEP-01_EXECUTION.md
- generator/playtest_metrics.py (somente leitura)
- generator/clue_graph.py (somente leitura)
- tests/test_playtest_metrics.py

Arquivos editáveis:
- tests/test_playtest_metrics.py (somente adicionar testes novos)
- .ai/runs/ISSUE-30.7/STEP-02_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_playtest_metrics.py -q`

Proibido:
- Alterar `generator/playtest_metrics.py` ou qualquer implementação.
- Fazer GREEN no mesmo step.

Done quando:
- 7 testes adicionados; os RED falham por `AssertionError` (não import/syntax); teste 3 passa.
- Demais testes do arquivo continuam passando.

Revisão:
- `git diff` mostra só `tests/test_playtest_metrics.py` alterado.
- Report lista cada teste e o tipo de falha.

Dependências:
- STEP-01 aprovado

---

### STEP-03 — GREEN: novo classificador DF-01..07

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar DF-01..07 em `generator/playtest_metrics.py`:
  - Novo `estimate_difficulty` por profundidade (`clue_graph` depth) + densidade/doc + ambiguidade/cruzamentos + papel do E2; contagens só como sinal informativo (DF-01/DF-02).
  - Nova assinatura ratificada no STEP-01; atualizar `build_warnings` (único chamador) — DF-03.
  - Substituir o atalho `>30 / >12 → MESTRE` por critério de profundidade/densidade — DF-04.
  - `PT_009` usa o novo estimador — DF-05.
  - Re-enquadrar texto de `PT_001/PT_003/PT_007` como sinal informativo — DF-06.
  - Manter chaves de `summary` (DF-07).
- Atualizar os testes legados listados no STEP-01.
- Rodar `pytest tests/test_playtest_metrics.py -q` e confirmar 0 falhas.

Contexto permitido:
- .ai/issues/ISSUE-30.7.md
- .ai/issues/ISSUE-30.7_SPEC.md
- .ai/runs/ISSUE-30.7/STEP-01_EXECUTION.md
- .ai/runs/ISSUE-30.7/STEP-02_EXECUTION.md
- .ai/runs/ISSUE-30.7/STEP-02_REVIEW.md
- generator/playtest_metrics.py
- generator/clue_graph.py (somente leitura — reusar, não reimplementar travessia)
- tests/test_playtest_metrics.py

Arquivos editáveis:
- generator/playtest_metrics.py
- tests/test_playtest_metrics.py (somente os legados identificados; sem testes novos de escopo além do GREEN)
- .ai/runs/ISSUE-30.7/STEP-03_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_playtest_metrics.py -q`

Proibido:
- Reimplementar travessia de grafo (reusar `clue_graph`).
- Recalibrar `DOCUMENT_RANGES`/`CONTRACT_LIMITS`/`SUSPECT_LIMITS`.
- Alterar blueprints canônicos.
- Fazer commit.

Done quando:
- 7 testes novos passam; legados atualizados passam.
- `pytest tests/test_playtest_metrics.py -q` com 0 falhas.
- Nenhuma duplicação de lógica de grafo.

Revisão:
- `git diff` mostra só `generator/playtest_metrics.py` e `tests/test_playtest_metrics.py`.
- Confirmar reuso de `clue_graph` (sem reimplementação).
- Confirmar tetos numéricos inalterados.

Dependências:
- STEP-02 aprovado

---

### STEP-04 — REFACTOR

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Limpar `playtest_metrics.py` sem mudar comportamento (extrair helpers de sinal, nomes claros).
- Confirmar `pytest tests/test_playtest_metrics.py -q` ainda passa.
- Se nada a limpar, registrar e concluir.

Arquivos editáveis:
- generator/playtest_metrics.py
- .ai/runs/ISSUE-30.7/STEP-04_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_playtest_metrics.py -q`

Proibido:
- Novo comportamento; alterar testes; alterar API pública além do já definido.

Done quando:
- Sem regressão; report descreve a limpeza (ou declara que não havia).

Revisão:
- `git diff` só em `generator/playtest_metrics.py`.

Dependências:
- STEP-03 aprovado

---

### STEP-05 — DOCS: impacto documental

Status: pending
Owner: executor
Type: documentation

Objetivo:
- Aplicar o conjunto declarado no SPEC:
  - `docs/DIFFICULTY_FRAMEWORK.md` ✅ — registrar que o estimador implementa "contagem é sinal, não classificador"; atualizar tabela de métricas com coluna "estimada (pós-fix)".
  - `docs/GUIA_CODIGOS_ERROS.md` ✅ — atualizar `PT_001/003/007` (informativo) e `PT_009` (profundidade).
  - `framework/19_PLAYTEST_E_METRICAS.md` ✅ — refletir o novo modelo de estimativa.
  - `docs/ESTADO_ATUAL.md` ✅ — registrar em "problemas já tratados" o estimador degenerado corrigido.
  - `CLAUDE.md` ✅/⏭️ — uma linha se houver menção a métricas; senão ⏭️ com motivo.
  - `docs/INDICE_DOCUMENTACAO.md` ⏭️ — nenhum doc criado/movido.

Arquivos editáveis:
- docs/DIFFICULTY_FRAMEWORK.md
- docs/GUIA_CODIGOS_ERROS.md
- framework/19_PLAYTEST_E_METRICAS.md
- docs/ESTADO_ATUAL.md
- CLAUDE.md
- .ai/runs/ISSUE-30.7/STEP-05_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Alterar código ou testes.

Done quando:
- Docs ✅ atualizados; docs ⏭️ avaliados com motivo no report.

Revisão:
- Nenhum arquivo de código/teste alterado; itens do SPEC cobertos.

Dependências:
- STEP-04 aprovado

---

### STEP-06 — VALIDATION

Status: pending
Owner: executor
Type: validation

Objetivo:
- `pytest tests/ -q` (suíte completa) sem regressão.
- `ruff check generator/ tests/` limpo.
- Sondagem: rodar validator strict nos quatro canônicos e registrar que `PT_009` não dispara mais para Iniciante B/Aurora; anexar a tabela final "declarada vs estimada" dos quatro casos no report.

Arquivos editáveis:
- .ai/runs/ISSUE-30.7/STEP-06_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/ -q`
- `ruff check generator/ tests/`
- `python -m generator.validator examples/caso_canonico_iniciante.json --strict`
- `python -m generator.validator examples/caso_canonico_iniciante_b.json --strict`
- `python -m generator.validator examples/caso_canonico_intermediario.json --strict`
- `python -m generator.validator examples/caso_fintech.json --strict`

Proibido:
- Corrigir falhas; alterar código/docs.

Done quando:
- pytest 0 falhas; ruff limpo; tabela final registrada com os 4 casos discriminados.

Revisão:
- Report tem saída literal do pytest e a tabela final.

Dependências:
- STEP-05 aprovado

---

### STEP-07 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Listar arquivos alterados e comandos executados com resultados.
- Resolver impacto documental (✅/⏭️ por item).
- Atualizar ISSUE-30.7.md para STATUS: done.

Arquivos editáveis:
- .ai/runs/ISSUE-30.7/STEP-07_EXECUTION.md (somente relatório)
- .ai/issues/ISSUE-30.7.md (somente STATUS)

Comandos permitidos:
- `git diff --name-only`
- `git status --short`

Proibido:
- Alterar implementação/testes/docs; commit ou PR.

Done quando:
- Report completo; STATUS: done.

Revisão:
- N/A (wrap-up é auto-approve).

Dependências:
- STEP-06 aprovado

---

## Auto-approve

reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório

red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

---

## Histórico

- STEP-00 gerado em chat; STEP-01 pronto para execução.

# ISSUE-30.8 — "Uma Noite Sem Flores" como terceiro ponto de calibração

## Estado

```
STATUS: done
CURRENT_STEP: done
NEXT_ACTION: none
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-07
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-30.8/STEP-07_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-30.8/STEP-06_REVIEW.md
BLOCKER: none
```

## Contexto

Skill: `grill-with-docs` — motivo: autoria fiel guiada pelo framework + análise ancorada em docs; não é TDD de código.

Spec: `.ai/issues/ISSUE-30.8_SPEC.md`. Saídas: `examples/caso_referencia_uma_noite_sem_flores.json` (não-canônico) e `docs/CALIBRACAO_REFERENCIA_EXTERNA.md`. Apoio (leitura): `framework/07_PROMPT_GERADOR_DE_CASO.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`, `framework/03_TIPOS_DE_DOCUMENTOS.md`, `docs/DIFFICULTY_FRAMEWORK.md`, `docs/ANTI_OBVIEDADE.md`.

Dependência recomendada: **após ISSUE-30.7** (para o relatório comparar estimador antigo vs. novo neste terceiro caso). A autoria pode começar em paralelo.

Predição a confirmar: nossas checagens de volume superdimensionam a dificuldade de um caso rico e validado.

## Steps

### STEP-01 — Leitura, decisões de tradução e de escopo

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler SPEC, `framework/07`, `BLUEPRINT_AUTHORING_GUIDE.md`, `framework/03`, `DIFFICULTY_FRAMEWORK.md`, `ANTI_OBVIEDADE.md`, `docs/FLOORPLANS.md`.
- Fixar as decisões TR-01..05 (importar/adaptar/descartar cada gancho digital) — registrar a tabela TR no execution report.
- Decidir TR-04 (mapa como planta P2 vs. referência textual) por custo.
- Decidir dificuldade declarada (AF-01) como hipótese a calibrar.
- Decidir decomposição: caso único vs. 30.8a (E1) + 30.8b (E2) — registrar a decisão e, se decompor, parar e sinalizar para reemissão dos arquivos.
- Decidir via de autoria do STEP-02 (chat vs. executor).

Contexto permitido:
- AGENTS.md
- docs/LLM_CONTEXT.md
- .ai/issues/ISSUE-30.8.md
- .ai/issues/ISSUE-30.8_SPEC.md
- .ai/skills/grill-with-docs.md
- framework/07_PROMPT_GERADOR_DE_CASO.md
- docs/BLUEPRINT_AUTHORING_GUIDE.md
- framework/03_TIPOS_DE_DOCUMENTOS.md
- docs/DIFFICULTY_FRAMEWORK.md
- docs/ANTI_OBVIEDADE.md
- docs/FLOORPLANS.md

Arquivos editáveis:
- .ai/runs/ISSUE-30.8/STEP-01_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Criar o blueprint ou docs neste step.

Done quando:
- Report fixa: tabela TR, decisão TR-04, dificuldade declarada hipotética, decisão de decomposição, via de autoria.

Revisão:
- Confirmar que nenhum artefato de saída foi criado ainda.
- Confirmar que a tabela TR cobre os ganchos do SPEC.

Dependências:
- Recomendada: ISSUE-30.7 mergeada (não bloqueante para STEP-01/02).

---

### STEP-02 — Autoria do blueprint (E1 + E2)

Status: pending
Owner: executor (ou autoria em chat, conforme STEP-01)
Type: generation

Objetivo:
- Produzir `examples/caso_referencia_uma_noite_sem_flores.json` seguindo `framework/07` e o contrato de `BLUEPRINT_AUTHORING_GUIDE.md`.
- Garantir FF-01..06: dois envelopes; pilar de presença (log × manual de crachá); descarte `motivo_sem_oportunidade`; salto logístico com `documento_prova`; ambiguidade sem confissão; código offline (FF-06/TR-03).
- Reescrever todos os documentos (sem transcrever o original); recriar nomes/empresas/CNPJs como ficção própria.
- Marcar o caso como corpus de calibração não-canônico (AF-03).
- Registrar no report como o JSON foi produzido (chat ou executor) e onde foi commitado.

Contexto permitido:
- .ai/issues/ISSUE-30.8.md
- .ai/issues/ISSUE-30.8_SPEC.md
- .ai/runs/ISSUE-30.8/STEP-01_EXECUTION.md
- framework/07_PROMPT_GERADOR_DE_CASO.md
- framework/03_TIPOS_DE_DOCUMENTOS.md
- docs/BLUEPRINT_AUTHORING_GUIDE.md
- examples/caso_canonico_intermediario.json (somente leitura — referência de forma, não de conteúdo)

Arquivos editáveis:
- examples/caso_referencia_uma_noite_sem_flores.json
- .ai/runs/ISSUE-30.8/STEP-02_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum (validação fica no STEP-03)

Proibido:
- Copiar texto literal do material de referência além do mínimo.
- Alterar canônicos ou qualquer outro exemplo.

Done quando:
- Blueprint existe, cobre FF-01..06, marcado como não-canônico.

Revisão:
- Conferir presença das entidades FF-02/03/04 no JSON.
- Conferir ausência de confissão/nome-em-ação (FF-05) por leitura.
- Conferir marcação não-canônica.

Dependências:
- STEP-01 aprovado

---

### STEP-03 — GREEN estrutural: validator strict

Status: pending
Owner: executor
Type: green

Objetivo:
- Rodar `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`.
- Corrigir o blueprint até **0 erros** (avisos permitidos e anotados).
- Registrar a lista de avisos remanescentes (entram no relatório do STEP-04).

Contexto permitido:
- .ai/issues/ISSUE-30.8_SPEC.md
- .ai/runs/ISSUE-30.8/STEP-02_EXECUTION.md
- .ai/runs/ISSUE-30.8/STEP-02_REVIEW.md
- examples/caso_referencia_uma_noite_sem_flores.json
- generator/validator.py (somente leitura)

Arquivos editáveis:
- examples/caso_referencia_uma_noite_sem_flores.json
- .ai/runs/ISSUE-30.8/STEP-03_EXECUTION.md (somente relatório)

Comandos permitidos:
- `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`

Proibido:
- Relaxar o validator ou o schema para acomodar o caso.
- Alterar outros artefatos.

Done quando:
- Validator strict retorna 0 erros; avisos listados no report.

Revisão:
- Confirmar 0 erros e que nenhum schema/validator foi afrouxado.

Dependências:
- STEP-02 aprovado

---

### STEP-04 — Análise e relatório de calibração

Status: pending
Owner: executor
Type: analysis

Objetivo:
- Rodar e capturar: `validator --strict`, `case_review`, `clue_graph` (depth, GP_*), estimador de dificuldade (antigo e — se ISSUE-30.7 mergeada — novo), `obviousness_checker`.
- Escrever `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` (CR-01..03): tabela TR; saídas da pipeline; classificação de cada finding em **sinal real / artefato de codificação / falso positivo de métrica**; conclusão sobre a predição (métricas superdimensionam casos ricos?) e recomendações ao framework.

Contexto permitido:
- .ai/issues/ISSUE-30.8_SPEC.md
- .ai/runs/ISSUE-30.8/STEP-03_EXECUTION.md
- examples/caso_referencia_uma_noite_sem_flores.json (somente leitura)
- generator/case_review.py, generator/clue_graph.py, generator/playtest_metrics.py, generator/obviousness_checker.py (somente leitura)

Arquivos editáveis:
- docs/CALIBRACAO_REFERENCIA_EXTERNA.md
- .ai/runs/ISSUE-30.8/STEP-04_EXECUTION.md (somente relatório)

Comandos permitidos:
- `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`
- `PYTHONPATH=. python scripts/case_review.py examples/caso_referencia_uma_noite_sem_flores.json`
- `python - <<...>>` para chamar `clue_graph`/`playtest_metrics` sobre o blueprint

Proibido:
- Alterar o blueprint ou o código para "melhorar" números (a análise é honesta, não cosmética).

Done quando:
- Relatório completo com a classificação CR-02 e a conclusão CR-03.

Revisão:
- Conferir que cada finding tem uma das três classificações com justificativa.

Dependências:
- STEP-03 aprovado

---

### STEP-05 — DOCS: impacto documental

Status: pending
Owner: executor
Type: documentation

Objetivo:
- `docs/INDICE_DOCUMENTACAO.md` ✅ — registrar o novo doc de calibração e o novo exemplo.
- `docs/DIFFICULTY_FRAMEWORK.md` ✅ — adicionar linha do caso externo na tabela de métricas (docs, densidade, depth), marcado como corpus de calibração.
- `docs/ESTADO_ATUAL.md` ✅ — roster: caso de referência como não-régua/corpus de calibração externo.
- `README.md` / `AGENTS.md` / `CLAUDE.md` ✅/⏭️ — distinguir réguas canônicas de corpus de calibração (uma linha cada ou ⏭️ justificado).
- CI: incluir o novo blueprint na cobertura de `validator --strict` (`.github/workflows/ci.yml`), fora da promoção canônica.

Arquivos editáveis:
- docs/INDICE_DOCUMENTACAO.md
- docs/DIFFICULTY_FRAMEWORK.md
- docs/ESTADO_ATUAL.md
- README.md, AGENTS.md, CLAUDE.md
- .github/workflows/ci.yml
- .ai/runs/ISSUE-30.8/STEP-05_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Adicionar o caso à promoção canônica ou ao Canonical Quality Gate como certificação.

Done quando:
- Índice, DIFFICULTY e ESTADO atualizados; rosters avaliados; CI cobre o novo strict.

Revisão:
- Confirmar índice atualizado (regra "doc novo → índice").
- Confirmar marcação não-canônica em todos os pontos.

Dependências:
- STEP-04 aprovado

---

### STEP-06 — VALIDATION

Status: pending
Owner: executor
Type: validation

Objetivo:
- `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict` → 0 erros.
- `pytest tests/ -q` sem regressão.
- `ruff check` limpo em qualquer arquivo novo (esperado: nenhum script).
- Confirmar que o YAML do CI é válido após a edição.

Arquivos editáveis:
- .ai/runs/ISSUE-30.8/STEP-06_EXECUTION.md (somente relatório)

Comandos permitidos:
- `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`
- `pytest tests/ -q`
- `ruff check generator/ scripts/ tests/`

Proibido:
- Corrigir falhas aqui; alterar artefatos.

Done quando:
- Strict 0 erros; pytest sem regressão; ruff limpo; CI YAML válido.

Revisão:
- Report com saídas literais.

Dependências:
- STEP-05 aprovado

---

### STEP-07 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Listar arquivos criados/alterados e comandos executados.
- Resolver impacto documental (✅/⏭️).
- Atualizar ISSUE-30.8.md para STATUS: done.

Arquivos editáveis:
- .ai/runs/ISSUE-30.8/STEP-07_EXECUTION.md (somente relatório)
- .ai/issues/ISSUE-30.8.md (somente STATUS)

Comandos permitidos:
- `git diff --name-only`
- `git status --short`

Proibido:
- Alterar artefatos; commit ou PR.

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

generation (STEP-02), green (STEP-03), analysis (STEP-04), validation (STEP-06).

---

## Histórico

- STEP-00 gerado em chat; STEP-01 pronto para execução.

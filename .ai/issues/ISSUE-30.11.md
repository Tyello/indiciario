# ISSUE-30.11 — Geração-do-zero: gerar um caso novo e playtestar

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-01
NEXT_ACTION: human
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-00
LAST_EXECUTION_REPORT: none
LAST_REVIEW_REPORT: none
BLOCKER: depende de ISSUE-30.10 mergeada (padrões PAT codificados)
```

> **Pré-requisito:** mergear ISSUE-30.10 antes de iniciar. Quando os padrões PAT estiverem no `framework/08`, mude BLOCKER para `none`, STATUS para `running` e NEXT_ACTION para `execute`.

## Contexto

Skill: `grill-with-docs` — geração guiada pelo framework + análise comparativa ancorada em docs. A autoria do blueprint (STEP-02) segue o fluxo "LLM gera em chat", como na 30.8.

Spec: `.ai/issues/ISSUE-30.11_SPEC.md`. Saídas: `examples/caso_gerado_<dominio>.json` (experimental) e `docs/EXPERIMENTO_GERACAO_DO_ZERO.md`. Depende de 30.10; beneficia-se de 30.9.

Responde "geramos do zero no nível da referência?". Pipeline-verde é necessário, não suficiente — o veredito é o playtest humano (portão HUMAN-01).

## Steps

### STEP-01 — Definir parâmetros e rubrica
Status: pending | Owner: executor | Type: reading
- Escolher o domínio novo (≠ museu/arte) e fixar parâmetros (Intermediário, 2 envelopes, ≥2 padrões PAT a empregar).
- Redigir a rubrica RUB-01/02 em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` (esqueleto).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-30.11*.md; framework/07_PROMPT_GERADOR_DE_CASO.md; framework/08_MODELO_REFERENCIA.md; docs/BLUEPRINT_AUTHORING_GUIDE.md; docs/CALIBRACAO_REFERENCIA_EXTERNA.md
Editáveis: docs/EXPERIMENTO_GERACAO_DO_ZERO.md (esqueleto/rubrica); .ai/runs/ISSUE-30.11/STEP-01_EXECUTION.md
Comandos: nenhum
Done quando: domínio + parâmetros + rubrica definidos.
Revisão: auto-approve (reading), mas confirmar domínio ≠ calibração.

### STEP-02 — Gerar o blueprint do zero
Status: pending | Owner: executor (ou autoria em chat) | Type: generation
- Gerar `examples/caso_gerado_<dominio>.json` a partir do framework, **sem** transcrever, empregando ≥2 padrões PAT.
- Marcar experimental/não-canônico em `observacoes_producao`. Registrar quais PAT foram usados.
Contexto permitido: .ai/issues/ISSUE-30.11*.md; .ai/runs/ISSUE-30.11/STEP-01_EXECUTION.md; framework/07_PROMPT_GERADOR_DE_CASO.md; framework/08_MODELO_REFERENCIA.md; framework/03_TIPOS_DE_DOCUMENTOS.md; docs/BLUEPRINT_AUTHORING_GUIDE.md
Editáveis: examples/caso_gerado_<dominio>.json; .ai/runs/ISSUE-30.11/STEP-02_EXECUTION.md
Comandos: nenhum (validação no STEP-03)
Proibido: copiar caso externo; reusar domínio de museu/arte.
Done quando: blueprint gerado, PAT declarados, marcado experimental.
Revisão: revisor obrigatório — originalidade, uso real dos PAT, marcação.

### STEP-03 — GREEN estrutural + pipeline
Status: pending | Owner: executor | Type: green
- `validator --strict` até 0 erros; rodar estimador (deve dar Intermediário por profundidade), `clue_graph` (depth ≥ 2, sem GP_007), `obviousness_checker` (sem OBV_001/009).
- Registrar todas as saídas.
Editáveis: examples/caso_gerado_<dominio>.json; .ai/runs/ISSUE-30.11/STEP-03_EXECUTION.md
Comandos: `python -m generator.validator examples/caso_gerado_<dominio>.json --strict`; chamadas a clue_graph/playtest_metrics/obviousness via `python -`
Proibido: afrouxar validator/schema.
Done quando: strict 0 erros; métricas registradas.
Revisão: revisor obrigatório.

### STEP-04 — Relatório pré-playtest e PAUSA
Status: pending | Owner: executor | Type: analysis
- Preencher em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` a faixa (a) métricas de pipeline e a comparação inicial com o caso de calibração.
- Setar o controle: `NEXT_ACTION: human`, BLOCKER: "aguardando playtest humano". **O orquestrador para aqui.**
Editáveis: docs/EXPERIMENTO_GERACAO_DO_ZERO.md; .ai/runs/ISSUE-30.11/STEP-04_EXECUTION.md; .ai/issues/ISSUE-30.11.md (estado)
Comandos: nenhum
Done quando: relatório pré-playtest pronto; estado em `human`.
Revisão: auto-approve; em seguida PARAR.

### STEP-05 — Ingerir playtest e veredito (pós-mesa, humano)
Status: pending | Owner: humano → executor | Type: analysis
- Após o playtest, registrar a rubrica RUB-01/02 preenchida pelos jogadores.
- Completar `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` (REP-01/02): comparação pipeline + rubrica e **veredito honesto** — geramos no nível da referência? gaps por dimensão? cada gap → recomendação (incl. necessidade de revisor qualitativo, gap 1).
Editáveis: docs/EXPERIMENTO_GERACAO_DO_ZERO.md; .ai/runs/ISSUE-30.11/STEP-05_EXECUTION.md
Comandos: nenhum
Done quando: rubrica preenchida + veredito + recomendações.
Revisão: revisor obrigatório.
Dependências: playtest humano concluído.

### STEP-06 — DOCS + VALIDATION + WRAP-UP
Status: pending | Owner: executor | Type: documentation/validation
- INDICE (novo doc + exemplo), ESTADO, rosters (experimental/não-canônico), CI (strict do novo caso, fora do canônico).
- `pytest tests/ -q` sem regressão. STATUS: done.
Editáveis: docs/INDICE_DOCUMENTACAO.md; docs/ESTADO_ATUAL.md; README.md; AGENTS.md; CLAUDE.md; .github/workflows/ci.yml; .ai/runs/ISSUE-30.11/STEP-06_EXECUTION.md; .ai/issues/ISSUE-30.11.md (STATUS)
Comandos: `pytest tests/ -q`; `python -m generator.validator examples/caso_gerado_<dominio>.json --strict`
Revisão: revisor obrigatório (validation).
Dependências: STEP-05 aprovado.

## Auto-approve
reading (STEP-01), relatório pré-playtest (STEP-04, depois PARA).

## Revisor obrigatório
generation (STEP-02), green (STEP-03), analysis pós-playtest (STEP-05), validation (STEP-06).

## Histórico
- STEP-00 gerado em chat. Bloqueada por ISSUE-30.10. Portão humano em STEP-04→05.

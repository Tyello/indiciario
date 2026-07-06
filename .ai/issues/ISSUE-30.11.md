# ISSUE-30.11 — Geração-do-zero: gerar um caso novo e playtestar

## Estado

```
STATUS: blocked
CURRENT_STEP: STEP-05
NEXT_ACTION: human
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-04
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-30.11/STEP-04_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-30.11/STEP-03_FIX-1_REVIEW.md
BLOCKER: "aguardando playtest humano"
```

> **Pré-requisito:** ISSUE-30.10 mergeada (PR #104, padrões PAT-01..04 em `framework/08_MODELO_REFERENCIA.md`). Desbloqueada em 2026-07-02.

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
- STEP-01 executado (reading, auto-approve): domínio cooperativa agrícola + parâmetros + rubrica RUB-01/02 em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md`.
- STEP-02 executado (generation): `examples/caso_gerado_cooperativa.json` gerado do zero, marcado experimental/não-canônico, PAT-01+PAT-04 (núcleo) e PAT-02+PAT-03 (reforço) declarados e rastreados a IDs de documento. 3 divergências de escopo de leitura disclosed em `.ai/runs/ISSUE-30.11/STEP-02_EXECUTION.md` (inclui leitura inadvertida de fragmento estrutural do caso de calibração externo, sem narrativa reaproveitada). Aguardando revisor obrigatório (REVIEW_STATUS: pending).
- STEP-02 aprovado (APPROVED, severity minor). Checagem de contaminação obrigatória: comparado `codigos` e nomes/domínio do gerado contra `examples/caso_referencia_uma_noite_sem_flores.json` — sem vazamento concreto (hex/nomes/estrutura narrativa não coincidem; único ponto de contato é o padrão genérico PAT-03 de framework). 4 PAT verificados contra definições em `framework/08_MODELO_REFERENCIA.md` e batem com uso real e rastreável. Divergências de escopo de leitura (DVG-EXEC-001/002/003) mantidas como minor, disclosed, sem impacto no artefato. Ver `.ai/runs/ISSUE-30.11/STEP-02_REVIEW.md`. Próximo: STEP-03 (GREEN estrutural + pipeline).
- STEP-03 executado (green, high-risk): `examples/caso_gerado_cooperativa.json` reescrito estruturalmente para conformidade com `generator/models.py` (draft de STEP-02 não instanciava o `Blueprint` Pydantic — 327 erros). Narrativa/PAT/personagens preservados. `validator --strict`: 0 críticos, 1 moderado (`DC_000`), Pode gerar: SIM. Estimador de dificuldade: `intermediario` (85 min). `clue_graph`: `C-FINAL` depth=4, sem `GP_007` (só `GP_003` warning em documentos de contexto). `obviousness_checker`: zero findings, sem `OBV_001`/`OBV_009`. Divergências disclosed (DVG-EXEC-004/005/006) em `.ai/runs/ISSUE-30.11/STEP-03_EXECUTION.md`. Aguardando revisor obrigatório (REVIEW_STATUS: pending).
- STEP-03 **REJECTED** (severity major). Os 4 critérios formais (validator --strict, estimador, clue_graph, obviousness_checker) reconfirmados de forma independente e todos corretos; `generator/` intocado. Rejeição por quebra de rastreabilidade de PAT-01 (padrão-núcleo aprovado no STEP-02): a reescrita estrutural removeu a regra de exclusividade de credencial ("crachás são pessoais e intransferíveis", `E1-02`) do conteúdo do documento e da cadeia formal (`pilares_validacao`/`contratos_evidencia.C-E1-01` passaram a confirmar `E1-04` com `E1-03` — escala — em vez de `E1-02` — regra), sem disclosure. Isso reproduz o "modo de falha" documentado no próprio `framework/08_MODELO_REFERENCIA.md` para esse padrão (log sem regra de exclusividade → presença vira coincidência, não prova). PAT-02/03/04 verificados e preservados. Correção pedida ao executor: restaurar a regra em `E1-02` e trocar `confirmacao_independente` de `C-E1-01` (e/ou pilar correspondente) para `E1-02`; re-rodar os 4 comandos. Detalhe completo em `.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md`. Próximo: executor corrige o mesmo STEP-03.
- STEP-03 FIX-1 executado (correction): restaurada regra de exclusividade de credencial em `E1-02` (pistas_contidas + CORPO_CARTA), `contratos_evidencia.C-E1-01.confirmacao_independente` trocado de `E1-03` para `E1-02`, `pilares_validacao[0]` ("presença física") com `confirmacao: E1-02`, `pilares_validacao[1]` renomeado "escala de turno (reforço)" mantendo `E1-03` como camada opcional. `documentos[E1-02/E1-04].confirma`/`confirmado_por` atualizados para refletir o par log×regra. Os 4 comandos (validator --strict, estimador, clue_graph, obviousness_checker) re-rodados: 0 críticos, `intermediario`/85min, `C-FINAL` depth=4 sem `GP_007`, zero findings obviousness — sem regressão. `E1-02` não aparece mais como órfão em `GP_003`. Relatório completo em `.ai/runs/ISSUE-30.11/STEP-03_FIX-1_EXECUTION.md`. Aguardando revisor obrigatório.
- STEP-03 FIX-1 **APPROVED**. Leitura direta do JSON confirmou (não só o relatório do executor): regra de exclusividade de crachá em texto legível em `E1-02` (pistas_contidas + CORPO_CARTA), `pilares_validacao[0]` e `contratos_evidencia.C-E1-01` referenciando `E1-02` como confirmação do log `E1-04`, `E1-02` deixou de ser órfão. Os 4 comandos formais (validator --strict, estimador, clue_graph, obviousness_checker) re-rodados de forma independente: idênticos ao execution report, sem regressão. `generator/` confirmado intocado (`git status`/`git diff --stat`). PAT-02 (red_herrings/E1-09) e PAT-03 (codigos) confirmados inalterados; PAT-04 (objetivos_por_envelope) intacto com nota cosmética não bloqueante (prosa de `resposta_esperada` ainda cita "escala" sem mencionar a regra — fora do escopo do pedido de correção). Motivo original da rejeição (PAT-01 quebrado) resolvido. Detalhe completo em `.ai/runs/ISSUE-30.11/STEP-03_FIX-1_REVIEW.md`. Próximo: STEP-04 (relatório pré-playtest e pausa para portão humano).
- STEP-04 executado (analysis, auto-approve): `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` seção 3 (métricas de pipeline) preenchida com os números finais aprovados de STEP-03/FIX-1 (validator strict 0 críticos/1 moderado DC_000, estimador intermediario/85min vs 100min declarado, clue_graph C-FINAL depth=4 sem GP_007, obviousness zero findings, 4/4 PAT rastreáveis). Seção 4 (comparação inicial, faixa a) preenchida contra `docs/CALIBRACAO_REFERENCIA_EXTERNA.md`: nas métricas objetivas o gerado iguala ou supera a calibração (depth maior, obviousness limpo, PAT confirmado), mas isso não responde à pergunta do experimento — falta a faixa (b), rubrica humana. Rubrica RUB-01/02 conferida íntegra, não reescrita. Faixa (b) e REP-02 seguem placeholder, dependem do playtest. Relatório completo em `.ai/runs/ISSUE-30.11/STEP-04_EXECUTION.md`. **Orquestrador para aqui**: `NEXT_ACTION: human`, `BLOCKER: "aguardando playtest humano"`. Retoma no STEP-05 só com os resultados do playtest (Marcelo + mesa) em mãos — não simular, não pular.

# Review Report — ISSUE-30.11 STEP-03 FIX-1

STEP: STEP-03 — GREEN estrutural + pipeline (correção pós-rejeição)
STEP_TYPE: green/correction (revisor obrigatório)
REVIEW_STATUS: approved
SEVERITY: none

## Objeto da revisão

Correção pontual pedida em `.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md` (rejeição original, major: PAT-01 quebrado — `E1-02` perdeu a regra de exclusividade de crachá e ficou órfão da cadeia formal). Execução reportada em `.ai/runs/ISSUE-30.11/STEP-03_FIX-1_EXECUTION.md`.

## 1. Leitura direta do JSON (não confiei no relatório do executor)

Li `examples/caso_gerado_cooperativa.json` diretamente via script Python (não peguei os campos do relatório).

- **Regra de exclusividade em `E1-02`**: confirmada em `pistas_contidas` — "Crachás de acesso ao terminal da báscula são pessoais e intransferíveis; nenhum lançamento manual pode ser feito com o crachá de outro operador." — e reforçada em `conteudo.CORPO_CARTA` com detalhe operacional adicional ("o sistema não permite lançamento manual sem autenticação do crachá do operador responsável pelo turno"). Texto legível, presente, não é só metadado.
- **`pilares_validacao[0]`** ("presença física", `personagem_id: 02`): `documento_principal: E1-04`, `confirmacao: E1-02`. Confere.
- **`pilares_validacao[1]`** (renomeado "escala de turno (reforço)"): `documento_principal: E1-04`, `confirmacao: E1-03` — mantido como camada opcional, não interfere na cadeia principal.
- **`contratos_evidencia.C-E1-01`**: `prova_principal: E1-04`, `confirmacao_independente: E1-02`. Confere — é exatamente o par log × regra que o padrão PAT-01 exige.
- **`E1-02` não é órfão**: aparece em `pilares_validacao[0].confirmacao`, em `contratos_evidencia.C-E1-01.confirmacao_independente` e em `documentos[E1-04].confirma`/`documentos[E1-02].confirmado_por` (par cruzado `E1-02` ↔ `E1-04`).

Todos os três pontos pedidos na tarefa (item 1) confirmados por leitura direta do JSON, não pelo relatório.

## 2. Re-execução independente dos 4 comandos (ambiente `.venv\Scripts\python.exe`, raiz do repo)

### `validator --strict`
```
.venv\Scripts\python.exe -m generator.validator examples\caso_gerado_cooperativa.json --strict
```
Críticos: 0. Moderados: 1 (`DC_000`, pré-existente, não relacionado a PAT-01). Avisos: 11 (`ELENCO_001` x1, `GP_003` x9 — lista agora tem `E1-03` no lugar de `E1-02`, `CONT_002` x1). Idêntico ao execution report. **ATENDIDO.**

### Estimador de dificuldade
`estimate_difficulty(bp)` = `intermediario`, `estimate_minutes(bp)` = `85`. Idêntico. **ATENDIDO.**

### `clue_graph`
`analyze_clue_graph` → `status: passed`. `solution_paths`: `C-FINAL` depth=4 (`E1-09`, `E2-04`, `E2-05` / contratos `C-E1-01`, `C-E2-01`, `C-E2-02`, `C-FINAL`). `issues`: só `GP_003` x9, **zero `GP_007`**. Idêntico. **ATENDIDO.**

### `obviousness_checker`
`check_obviousness(d)` → `ObviousnessReport(findings=[])`. Zero findings, sem `OBV_001`/`OBV_009`. Idêntico. **ATENDIDO.**

Nenhuma regressão nos 4 critérios formais do STEP-03.

## 3. `generator/` intocado

```
git status --short
 M .ai/issues/ISSUE-30.11.md
?? .ai/runs/ISSUE-30.11/
?? docs/EXPERIMENTO_GERACAO_DO_ZERO.md
?? examples/caso_gerado_cooperativa.json

git diff --stat
 .ai/issues/ISSUE-30.11.md | 24 +++++++++++++++---------
```
Nenhum arquivo em `generator/` alterado, staged ou sujo. **ATENDIDO.**

## 4. PAT-02/03/04 não afetados

Comparei os campos contra o que STEP-03_REVIEW.md já havia verificado como preservados:

- **PAT-03 (código offline)** — `codigos[0]` = `{"documento":"E2-02","criterio":"codigo_lote","elementos":["LT-04-02-C"],"chave_em":"E2-03"}`. Idêntico byte a byte ao verificado no review anterior. **Preservado.**
- **PAT-02 (descarte motivo-sem-oportunidade)** — `red_herrings` para personagens `05` e `07` mantêm `categoria: "motivo_sem_oportunidade"` e `documento_descarte: "E1-09"`, exatamente como no STEP-03 original (a correção não tocou `red_herrings`). **Preservado.**
- **PAT-04 (virada de envelope)** — `objetivos_por_envelope[0]` continua resolvendo "quem" no E1 e reabrindo para "para onde foi" no E2; estrutura intacta. Nota cosmética, não bloqueante: `resposta_esperada` do envelope 1 ainda descreve o cruzamento como "log de acesso × escala de trabalho" em prosa, sem citar a regra de exclusividade — mas isso é texto narrativo de apoio (`objetivos_por_envelope`), não faz parte da cadeia formal (`pilares_validacao`/`contratos_evidencia`) que sustentava a rejeição, e o pedido de correção (itens 1–5 do STEP-03_REVIEW.md) não mencionava esse campo. Não bloqueia.

Confirmado: o executor tocou apenas os campos listados no pedido de correção (`E1-02`, `contratos_evidencia.C-E1-01`, `pilares_validacao`, `documentos[E1-02/E1-04].confirma`/`confirmado_por`), como declarado na seção "Evidência de aderência ao tipo (correction)" do execution report — e essa declaração bate com a leitura direta do JSON.

## Decisão

**APPROVED.**

A correção resolve exatamente o motivo da rejeição original: PAT-01 (log de acesso × regra de exclusividade de credencial) volta a ter cadeia formal completa e rastreável (`pilares_validacao[0]` + `contratos_evidencia.C-E1-01` apontando para `E1-02`, cujo texto contém a regra em linguagem legível). `E1-02` deixou de ser órfão. Os 4 critérios formais do STEP-03 continuam corretos, sem regressão. `generator/` intocado. PAT-02/03/04 confirmados preservados, sem efeitos colaterais da correção pontual.

## Arquivos verificados
- `examples/caso_gerado_cooperativa.json` (leitura direta via script Python: `documentos[E1-02/E1-04]`, `pilares_validacao`, `contratos_evidencia`, `red_herrings`, `codigos`, `objetivos_por_envelope`)
- `.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md` (rejeição original)
- `.ai/runs/ISSUE-30.11/STEP-03_FIX-1_EXECUTION.md`
- Re-execução independente: `generator.validator` (CLI), `generator.playtest_metrics.estimate_difficulty/estimate_minutes`, `generator.clue_graph.build_clue_graph/analyze_clue_graph`, `generator.obviousness_checker.check_obviousness`
- `git status --short`, `git diff --stat`

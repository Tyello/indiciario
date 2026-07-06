# Review Report — ISSUE-30.11 STEP-03

STEP: STEP-03 — GREEN estrutural + pipeline
STEP_TYPE: green (high-risk, revisor obrigatório)
REVIEW_STATUS: rejected
SEVERITY: major (regressão de PAT-01, não vazamento de gabarito, não afrouxamento de validator)

## Comandos re-rodados independentemente (não confiei no execution report)

Ambiente: `.venv\Scripts\python.exe`, raiz do repo.

### 1. `validator --strict`
```
.venv\Scripts\python.exe -m generator.validator examples\caso_gerado_cooperativa.json --strict
```
Saída confirmada: Críticos: 0. Moderados: 1 (`DC_000`). Avisos: 11 (`ELENCO_001` x1, `GP_003` x9, `CONT_002` x1). Idêntico ao execution report. **ATENDIDO.**

### 2. Estimador de dificuldade
`estimate_difficulty` = `intermediario`, `estimate_minutes` = `85`. Idêntico ao execution report. **ATENDIDO.**

### 3. `clue_graph`
`status: passed`. `solution_paths`: `C-FINAL` depth=4 (`E1-09`, `E2-04`, `E2-05` / contratos `C-E1-01`, `C-E2-01`, `C-E2-02`, `C-FINAL`). `issues`: só `GP_003` (warning) x9, nenhum `GP_007`. Idêntico ao execution report. **ATENDIDO.**

### 4. `obviousness_checker`
`ObviousnessReport(findings=[])`. Zero findings, sem `OBV_001`/`OBV_009`. Idêntico ao execution report. **ATENDIDO.**

Os 4 critérios formais do STEP-03 (spec) estão corretos e verificados de forma independente. Isso não é o motivo da rejeição.

## `generator/` intocado

```
git status --short
 M .ai/issues/ISSUE-30.11.md
?? .ai/runs/ISSUE-30.11/
?? docs/EXPERIMENTO_GERACAO_DO_ZERO.md
?? examples/caso_gerado_cooperativa.json
```
Nenhum arquivo em `generator/` alterado ou staged. Proibição "afrouxar validator/schema" respeitada. **ATENDIDO.**

## Rastreabilidade PAT-01..04 pós-reescrita (item 3 da tarefa) — FALHA em PAT-01

Comparei os campos do blueprint reescrito contra o que `STEP-02_REVIEW.md` verificou e aprovou.

- **PAT-03 (código offline)** — `codigos[0]` = `{"documento":"E2-02","criterio":"codigo_lote","elementos":["LT-04-02-C"],"chave_em":"E2-03"}`. Idêntico byte a byte ao aprovado no STEP-02. **Preservado.**
- **PAT-04 (virada de envelope)** — `objetivos_por_envelope[0]` resolve "quem" (E1), `objetivos_por_envelope[1]` reabre para "para onde foi o dinheiro/carga" (E2). Estrutura da virada intacta. **Preservado.**
- **PAT-02 (descarte motivo-sem-oportunidade)** — `red_herrings` (personagens `05` e `07`) mantêm `categoria: "motivo_sem_oportunidade"`, agora descartados por `E1-09` (folha de cruzamento nova, criada para satisfazer `ELENCO_004`) em vez de `E2-07` (atestado médico, mecanismo do STEP-02). Mudança de mecanismo concreto, mas categoria e rastreabilidade a documento de descarte concreto seguem válidas. **Preservado** (mecanismo diferente, padrão intacto — aceitável).
- **PAT-01 (pilar de presença credencial × regra)** — **QUEBRADO.**
  - STEP-02 declarou e o STEP-02_REVIEW.md verificou explicitamente: `PIL-01` = log `E1-04` confirmado por `E1-02` (manual, item 3.5: "crachás são pessoais e intransferíveis") **e** `E1-03` (escala). O revisor anterior escreveu: "Bate com a definição do padrão (documento_principal = log de acesso, confirmação = manual/regra)."
  - No blueprint reescrito, `pilares_validacao` tem dois pilares para o personagem `02`: `{"nome":"presença física","documento_principal":"E1-04","confirmacao":"E1-03",...}` e `{"nome":"credencial de acesso","documento_principal":"E1-03","confirmacao":"E1-04",...}`. **Nenhum dos dois usa `E1-02`.** Mesmo padrão se repete em `contratos_evidencia.C-E1-01`: `prova_principal: E1-04`, `confirmacao_independente: E1-03` — de novo, sem `E1-02`.
  - Pior: o conteúdo de `E1-02` foi **reescrito** no STEP-03. O texto "crachás são pessoais e intransferíveis" não existe mais em lugar nenhum do JSON (busquei `intransfer`, `pessoal e`, `crach` no arquivo inteiro — zero ocorrência da regra de exclusividade). `E1-02` hoje só fala de procedimento de pesagem (dupla conferência, lançamento manual em falha de sensor) — conteúdo totalmente diferente do que o STEP-02 declarou e o revisor aprovou.
  - Isso é exatamente o "modo de falha" que o próprio `framework/08_MODELO_REFERENCIA.md` documenta para este padrão: log de acesso sem documento de regra que confirme exclusividade da credencial → a presença vira coincidência, não prova. O caso hoje resolve E1 cruzando log × escala (quem estava escalado para trabalhar), o que é uma dedução mais fraca e genérica — não estabelece que o crachá não podia ter sido usado por outra pessoa, que era o ponto central do padrão aprovado.
  - `E1-02` agora é um documento órfão: não aparece em nenhum pilar, nem em nenhum contrato de evidência (consistente com o aviso `GP_003` que o valida como "não participa de nenhum contrato" — mas o problema não é o aviso, é que o documento perdeu a função que justificava sua existência e a aprovação do STEP-02).

## Por que isso bloqueia (e não é só nota)

A tarefa deste STEP-03 não é só "passa strict + estimador + clue_graph + obviousness" — a issue inteira (GEN-03) exige uso **deliberado e rastreável** de ≥2 padrões PAT, e PAT-01 foi um dos dois padrões-núcleo aprovados no STEP-02 (junto com PAT-04). A reescrita estrutural do STEP-03 silenciosamente removeu a lógica dedutiva que sustentava PAT-01, sem disclosure — nenhuma das divergências DVG-EXEC-004/005/006 menciona essa mudança. O relatório de execução afirma "narrativa/PAT/personagens preservados" (linha 10) e no histórico da issue "PAT-01..04 (herdados de STEP-02: ... presença antes de nomes/ações — PAT-01...)" — essa afirmação está incorreta para PAT-01 como hoje implementado.

Isso importa de verdade para o objetivo da ISSUE-30.11: o playtest humano em STEP-05 vai avaliar exatamente esse tipo de dedução (RUB-01 dimensão 1: "pista não óbvia mas justa"). Um caso cujo pilar de presença não fecha logicamente (falta a regra que impede "outra pessoa usou o crachá") é mais fraco do que o que foi aprovado, e o pipeline automático (validator/clue_graph/obviousness) não pega esse tipo de furo — é exatamente o gap 1 que a própria issue existe para tornar concreto. Deixar passar sem correção contaminaria o experimento.

## Divergências disclosed (DVG-EXEC-004/005/006) — avaliação

- **DVG-EXEC-004** (releitura de `generator/validator.py`/`clue_graph.py`/`models.py` para extrair códigos de erro exatos): não bloqueante. Uso estrutural, dentro do espírito do escopo já permitido ("generator/ para entender validator/clue_graph/estimador/obviousness_checker"), nenhum arquivo de `generator/` alterado. Aceito.
- **DVG-EXEC-005** (`DC_000` moderado deixado sem correção por falta de tempo para extrair enum de `dicas_contextuais`): não bloqueante. Critério de STEP-03 é 0 críticos, não 0 moderados; 1 moderado isolado não derruba o `--strict`. Aceito.
- **DVG-EXEC-006** (9 avisos `GP_003` + `ELENCO_001` deixados como estão): não bloqueante em si — avisos não bloqueiam geração e culpado único é decisão intencional herdada do STEP-02. Porém, um dos `GP_003` (`E1-02`) é sintoma direto do problema real descrito acima; não é o aviso que importa, é a causa (perda da regra de exclusividade).

## Decisão

**REJECTED.**

Critérios formais do STEP-03 (validator/estimador/clue_graph/obviousness/generator intocado) todos atendidos e reconfirmados de forma independente — isso não muda. A rejeição é por quebra de rastreabilidade de PAT-01, que é requisito de GEN-03 (contrato da issue) e foi explicitamente aprovado com uma implementação concreta no STEP-02_REVIEW.md que a reescrita do STEP-03 descartou sem disclosure.

## O que corrigir (para o executor, mesmo STEP-03)

1. Restaurar em `E1-02` (manual da báscula) a regra de exclusividade de credencial equivalente à declarada no STEP-02 (ex.: reintroduzir um item de procedimento tipo "crachás são pessoais e intransferíveis; lançamento manual deve ser feito pelo operador titular do crachá" — pode conviver com o conteúdo atual sobre lançamento manual/dupla conferência, não precisa descartar o que já existe).
2. Rewire a confirmação formal: em `contratos_evidencia.C-E1-01`, trocar `confirmacao_independente` de `E1-03` para `E1-02` (log × regra de exclusividade, conforme definição do padrão), ou — se quiser manter a escala como reforço — usar dois pilares distintos em `pilares_validacao` (um `documento_principal: E1-04` / `confirmacao: E1-02` para a exclusividade de credencial, outro opcional `E1-04`/`E1-03` para reforçar o horário), mas o pilar/contrato que sustenta a conclusão de `C-E1-01` (presença exclusiva) precisa ter `E1-02` na cadeia formal, não só a escala.
3. Re-rodar os 4 comandos (`validator --strict`, estimador, `clue_graph`, `obviousness_checker`) depois do ajuste e confirmar que nada regride (em especial que `E1-02` deixa de aparecer como `GP_003` órfão, ou que ao menos a lógica de exclusividade fica registrada em algum artefato formal do blueprint, não só em prosa).
4. Registrar no novo execution report a correção como resposta direta a este review (não é uma divergência nova, é correção do apontado aqui).
5. Não é necessário re-tocar PAT-02/03/04 — verificados e preservados.

## Arquivos verificados
- `examples/caso_gerado_cooperativa.json` (leitura completa dos campos `pilares_validacao`, `contratos_evidencia`, `red_herrings`, `objetivos_por_envelope`, `codigos`, `documentos[E1-02/E1-09/E2-07]`)
- `.ai/runs/ISSUE-30.11/STEP-03_EXECUTION.md`
- `.ai/runs/ISSUE-30.11/STEP-02_EXECUTION.md`, `.ai/runs/ISSUE-30.11/STEP-02_REVIEW.md`
- `generator/models.py` (confirmação do shape de `Pilar`: `documento_principal` + `confirmacao` únicos, sem lista — explica por que a triangulação de 3 docs do STEP-02 não cabia 1:1, mas não justifica descartar `E1-02` da cadeia)
- `framework/08_MODELO_REFERENCIA.md` (definição de PAT-01 e seu "modo de falha" documentado)
- `git status --short` (escopo de arquivos tocados)

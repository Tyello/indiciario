# ISSUE-40.6 — STEP-06 EXECUTION (documentation)

Type: documentation
Owner: executor

## Objetivo

Resolver o impacto documental da ISSUE-40.6 (microidentidades
institucionais): documentar em `templates/README.md` e no documento de
doutrina do sistema visual o que foi implementado no STEP-03 (GREEN) e a
correção de fallback do STEP-05.

## Achado — path correto do documento de doutrina

A tarefa referenciava `framework/09_SISTEMA_VISUAL.md`. Esse arquivo não
existe; o documento de doutrina real é `framework/20_SISTEMA_VISUAL.md`
(confirmado por `Glob framework/*SISTEMA_VISUAL*` e por
`docs/INDICE_DOCUMENTACAO.md`, que já lista `20_SISTEMA_VISUAL.md` como "Doutrina
de repaginação documental; gate de fidelidade de fonte (ISSUE-40.2), camada
e microidentidade (40.3/40.6)"). O próprio `20_SISTEMA_VISUAL.md` já trazia
um placeholder (`<!-- Seção de Microidentidade (40.6) será adicionada
quando essa issue for concluída. -->`) esperando este step. Editado
`framework/20_SISTEMA_VISUAL.md`, não um arquivo `09_*` novo.

Também corrigida, em `templates/README.md`, uma referência cruzada
pré-existente e stale ao mesmo arquivo errado
(`framework/09_SISTEMA_VISUAL.md` na seção "Isolamento de Marca") para
`framework/20_SISTEMA_VISUAL.md`.

## Arquivos alterados

### `templates/README.md`

Nova seção **"Microidentidades Institucionais (ISSUE-40.6)"**, inserida
antes de "Próximos templates recomendados". Documenta:

- O que é o sistema (cor/fonte/forma de header compartilhados por
  documentos da mesma instituição fictícia).
- Path do arquivo de tokens: `templates/styles/institution_identity.css`
  (tokens `--inst-color`, `--inst-font-display`, `--inst-header-shape`,
  injetado via `_institution_identity_css` em `generator/renderer.py`).
- As 3 classes de forma de header: `reto` (default do reset), `diagonal`
  (clip-path), `faixa-dupla` (borda dupla).
- Path da biblioteca de glifos: `assets/logos/glifo-01.svg`..`glifo-15.svg`
  (flat, geométricos abstratos, `fill="currentColor"`).
- Templates institucionais hoje: `templates/06_log_acesso.html`,
  `templates/manual.html`, `templates/cadastro.html`.
- Variáveis de contexto que o gerador de caso precisa fornecer:
  `INST_COLOR`, `INST_FONT_DISPLAY`, `INST_HEADER_SHAPE`.
- Nota de fallback (STEP-05): sem essas variáveis, o documento renderiza
  com valores neutros padrão (`#333`, `Georgia, serif`, `reto`) via
  `_aplicar_fallback_institucional`, em vez de deixar placeholder residual
  — cobre tanto `renderizar_documento` quanto o motor de baixo nível
  `renderizar_html`.
- Cross-link para `framework/20_SISTEMA_VISUAL.md`.

Também corrigida a referência stale `framework/09_SISTEMA_VISUAL.md` →
`framework/20_SISTEMA_VISUAL.md` na seção "Isolamento de Marca" (linha
pré-existente, erro de digitação de issue anterior, não introduzido por
mim).

### `framework/20_SISTEMA_VISUAL.md`

Substituído o placeholder de comentário HTML pela seção
**"Microidentidades Institucionais (ISSUE-40.6)"**, seguindo o mesmo tom e
estrutura das seções anteriores (Gate de fidelidade de fonte, Sistema de
Camadas): motivação (reconhecimento "isto veio da mesma instituição" em
meio segundo, papel análogo ao da paleta papel-cor da 40.4 mas por
instituição emissora em vez de tipo de documento), mecanismo (3 tokens CSS
+ variáveis de contexto + biblioteca de glifos), nota de fallback neutro
quando o blueprint não usa a feature, lista de templates institucionais e
cross-link de volta para `templates/README.md`.

### `docs/INDICE_DOCUMENTACAO.md`

`framework/20_SISTEMA_VISUAL.md` já estava indexado e sua descrição já
citava "camada e microidentidade (40.3/40.6)" — nenhuma mudança necessária
ali.

`templates/README.md` **não estava indexado** (não existia nenhuma seção
`templates/` no índice, gap pré-existente anterior a esta issue — as
issues 40.1–40.5 também tocaram esse arquivo sem indexá-lo). Adicionada
nova seção **"`templates/` — biblioteca de templates de renderização"**
com uma linha para `templates/README.md` (Propósito, Público, Workflow,
"Atualizar quando"), fechando a lacuna.

## Comandos executados

Nenhum comando de teste/lint (step de documentation, sem mudança de
código). Comandos usados foram só de leitura/busca:

```
Glob framework/*SISTEMA_VISUAL*
grep -n "templates/README" docs/INDICE_DOCUMENTACAO.md
grep -n "09_SISTEMA_VISUAL|20_SISTEMA_VISUAL|## " templates/README.md
```

## Impacto documental

- ✅ `templates/README.md` — atualizado (nova seção + correção de link stale).
- ✅ `framework/20_SISTEMA_VISUAL.md` — atualizado (seção de microidentidade
  substituindo o placeholder).
- ✅ `docs/INDICE_DOCUMENTACAO.md` — atualizado (nova entrada para
  `templates/README.md`; `20_SISTEMA_VISUAL.md` já cobria 40.6).

## Não fiz

- Não toquei `generator/renderer.py`, `templates/06_log_acesso.html`,
  `templates/manual.html`, `templates/cadastro.html`,
  `templates/styles/institution_identity.css` nem qualquer código —
  fora do escopo deste step (documentation).
- Não criei `framework/09_SISTEMA_VISUAL.md` (arquivo não existe e não
  deveria existir; a doutrina vive em `framework/20_SISTEMA_VISUAL.md`).

## Próximo passo

Conferir com o orquestrador se STEP-06 fecha a ISSUE-40.6 ou se falta
step de wrap-up/handoff.

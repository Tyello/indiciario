# STEP-05_FIX-01 — Execution Report

Issue: ISSUE-40.2
Step: STEP-05_FIX-01 — Renumerar doc de framework (colisão com 09_TEMPLATE_GABARITO.md)
Type: correction

## Ação executada

1. Confirmado que `framework/09_TEMPLATE_GABARITO.md` já ocupava o prefixo `09`, colidindo
   com `framework/09_SISTEMA_VISUAL.md` criado no STEP-05.
2. Renomeado `framework/09_SISTEMA_VISUAL.md` → `framework/20_SISTEMA_VISUAL.md` (rename
   simples via `mv`; conteúdo idêntico, byte a byte — nenhuma linha doutrinária tocada).
   Repo local não tinha o arquivo sob controle de versão ainda (`git mv` falhou com
   "not under version control"), então usado `mv` direto; conteúdo preservado integralmente.
3. Cross-link em `framework/07_PROMPT_GERADOR_DE_CASO.md` (linha na lista de regras
   técnicas obrigatórias, mesmo bullet que referencia a doutrina de fonte) atualizado de
   `framework/09_SISTEMA_VISUAL.md` para `framework/20_SISTEMA_VISUAL.md`.
4. Entrada na tabela de `docs/INDICE_DOCUMENTACAO.md` (linha do documento de sistema
   visual) atualizada de `09_SISTEMA_VISUAL.md` para `20_SISTEMA_VISUAL.md`.
5. Critério de aceite #4 em `.ai/issues/ISSUE-40.2.md` corrigido de
   "`framework/09_SISTEMA_VISUAL.md` existe e documenta a regra." para
   "`framework/20_SISTEMA_VISUAL.md` existe e documenta a regra."
6. Campos de controle da issue atualizados: `STATUS: waiting_review`,
   `NEXT_ACTION: review`, `REVIEW_STATUS: pending`, `LAST_EXECUTION_REPORT` apontando
   para este relatório. `LAST_COMPLETED_STEP` mantido em `STEP-04` (FIX-01 ainda não
   aprovado).
7. Adicionada entrada de Histórico registrando a reprovação do STEP-05 (colisão de
   numeração) e a execução deste FIX.

## Grep de confirmação — `09_SISTEMA_VISUAL`

Rodado após as edições acima. Resultado: **sem ocorrências** nos 4 arquivos do contrato
(`framework/09_SISTEMA_VISUAL.md` renomeado, `framework/07_PROMPT_GERADOR_DE_CASO.md`,
`docs/INDICE_DOCUMENTACAO.md`, `.ai/issues/ISSUE-40.2.md` critério #4).

Restam ocorrências fora do escopo editável deste step, todas legítimas ou stale:

- `.ai/issues/ISSUE-40.2.md` (outras linhas, ex. 233, 244, 255, 269, 270, 276, 279, 292):
  texto histórico das seções STEP-05 e STEP-05_FIX-01 descrevendo a própria ação de
  criação/renomeação — cita o nome antigo como parte do relato do que foi feito, não é
  stale (é registro de ato passado).
- `.ai/runs/ISSUE-40.2/STEP-05_EXECUTION.md`: relatório de execução histórico e imutável
  do STEP-05; fora de `Arquivos editáveis` deste step. Não alterado.
- `.ai/issues/ISSUE-40.2_SPEC.md`, `.ai/issues/ISSUE-40.3.md`, `.ai/issues/ISSUE-40.3_SPEC.md`,
  `.ai/issues/ISSUE-40.5_SPEC.md`, `.ai/issues/ISSUE-40.6.md`, `.ai/issues/ISSUE-40.6_SPEC.md`:
  citam `framework/09_SISTEMA_VISUAL.md` como o doc que 40.3/40.5/40.6 vão estender/fechar.
  Nome ficou stale por causa desta renumeração, mas nenhum desses arquivos está em
  `Arquivos editáveis` do STEP-05_FIX-01 — não tocados. **Sinalizado para o
  orquestrador**: issues 40.3/40.5/40.6 (ainda não iniciadas) vão precisar de ajuste de
  nome quando forem abertas para execução, ou podem ser corrigidas agora em follow-up
  separado se o orquestrador preferir.

## Comandos executados

Nenhum comando de teste/lint necessário (rename + edição de texto, conforme contrato do
step). Comandos de verificação usados: `mv`, `ls`, grep de confirmação.

## Doutrina

Nenhum conteúdo doutrinário do documento alterado — apenas nome de arquivo e referências
cruzadas. Conteúdo de `framework/20_SISTEMA_VISUAL.md` idêntico ao criado no STEP-05.

## Revisão — caminho seguido

Tipo do step é `correction`, que por padrão do executor.md pediria
`NEXT_ACTION: review` / `REVIEW_STATUS: pending` (executor nunca se auto-aprova). A
seção "Revisão" do próprio step, porém, diz "(auto-approve, low-risk — correção de
numeração, sem decisão de conteúdo)". Segui o protocolo padrão do executor.md mesmo
assim — setei `waiting_review`/`review`/`pending` como em qualquer correction — e deixei
registrada aqui e no Histórico da issue a nota de elegibilidade a auto-approve/low-risk,
para o orquestrador decidir fast-track na revisão, mesmo padrão já usado no fechamento do
STEP-05 (Type: documentation, também marcado auto-approve, também resolvido via
`waiting_review` + nota, não via self-approval do executor).

## Critério de aceite #4 (issue) — status

Cumprido: `framework/20_SISTEMA_VISUAL.md` existe, `framework/09_SISTEMA_VISUAL.md` não
existe mais, cross-link e índice atualizados, texto do critério corrigido.

## Arquivos alterados

- `framework/09_SISTEMA_VISUAL.md` → renomeado para `framework/20_SISTEMA_VISUAL.md`
- `framework/07_PROMPT_GERADOR_DE_CASO.md`
- `docs/INDICE_DOCUMENTACAO.md`
- `.ai/issues/ISSUE-40.2.md` (critério de aceite #4, campos de controle, Histórico)
- `.ai/runs/ISSUE-40.2/STEP-05_FIX-01_EXECUTION.md` (este relatório, novo)

Parando aqui. Não avancei para outro step, não me auto-aprovei.

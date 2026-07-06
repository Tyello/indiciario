# Execution Report — ISSUE-30.11 STEP-03 FIX-1

STEP: STEP-03 (correção pós-rejeição)
STEP_TYPE: correction
EXECUTION_STATUS: completed

## Objetivo
Restaurar PAT-01 (pilar de presença credencial×regra) no blueprint, rejeitado em `.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md`, sem tocar `generator/`.

## Review source
`.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md`

## Arquivos lidos
- `.ai/runs/ISSUE-30.11/STEP-03_REVIEW.md`
- `.ai/issues/ISSUE-30.11.md`
- `.ai/runs/ISSUE-30.11/STEP-02_REVIEW.md`
- `framework/08_MODELO_REFERENCIA.md`
- `examples/caso_gerado_cooperativa.json`
- `generator/clue_graph.py` (leitura, confirmar mecanismo de `_used_documents`/GP_003 a partir de `prova_principal`/`confirmacao_independente`)

## Arquivos alterados
- `examples/caso_gerado_cooperativa.json`

## Comandos executados
- `.venv\Scripts\python.exe -m generator.validator examples\caso_gerado_cooperativa.json --strict` — Críticos: 0, Moderados: 1 (`DC_000`, pré-existente, não relacionado), Avisos: 11 (`ELENCO_001` x1, `GP_003` x9, `CONT_002` x1). **PASS.**
- Script curto via `.venv\Scripts\python.exe -c "..."` chamando `generator.playtest_metrics.estimate_difficulty`/`estimate_minutes` — `intermediario`, `85`. Idêntico ao STEP-03 original. **PASS.**
- Script curto chamando `generator.clue_graph.build_clue_graph`/`analyze_clue_graph` — `status: passed`, `solution_paths`: `C-FINAL` depth=4 (`E1-09`, `E2-04`, `E2-05` / contratos `C-E1-01`, `C-E2-01`, `C-E2-02`, `C-FINAL`), `issues`: só `GP_003` x9, nenhum `GP_007`. **PASS.**
- Script curto chamando `generator.obviousness_checker.check_obviousness` — `ObviousnessReport(findings=[])`. Zero findings, sem `OBV_001`/`OBV_009`. **PASS.**

## O que foi feito

1. **Restaurada regra de exclusividade de credencial em `E1-02`** ("Manual de operação da báscula de recebimento"):
   - `pistas_contidas` ganhou item: `"Crachás de acesso ao terminal da báscula são pessoais e intransferíveis; nenhum lançamento manual pode ser feito com o crachá de outro operador."`
   - `conteudo.CORPO_CARTA` ganhou parágrafo: `"Os crachás de acesso ao terminal são pessoais e intransferíveis: cada operador só pode autenticar lançamentos com o próprio crachá, e o sistema não permite lançamento manual sem autenticação do crachá do operador responsável pelo turno."`
   - Conteúdo original sobre dupla conferência/lançamento manual em falha de sensor foi preservado (não removido).

2. **Rewire formal `E1-02` na cadeia de evidência**:
   - `contratos_evidencia.C-E1-01.confirmacao_independente`: `E1-03` → `E1-02`.
   - `contratos_evidencia.C-E1-01.acao_esperada_jogador` reescrito para descrever o cruzamento real: log (`E1-04`) × regra do manual (`E1-02`), em vez de log × escala.
   - `pilares_validacao[0]` ("presença física"): `confirmacao` `E1-03` → `E1-02` (agora `documento_principal: E1-04`, `confirmacao: E1-02`, `personagem_id: 02`).
   - `pilares_validacao[1]` renomeado de "credencial de acesso" (que invertia `documento_principal`/`confirmacao` de forma redundante com o pilar 0) para `"escala de turno (reforço)"`, mantendo `documento_principal: E1-04`, `confirmacao: E1-03` — E1-03 preservado como terceira camada de reforço narrativo, conforme item 4 do pedido de correção (não precisa ser removido se ainda fizer sentido).
   - `documentos[E1-02].confirma`/`confirmado_por`: `[]` → `["E1-04"]` (espelha o par log×regra).
   - `documentos[E1-04].confirma`/`confirmado_por`: `["E1-03"]` → `["E1-02", "E1-03"]` (E1-04 agora confirmado tanto pela regra de exclusividade quanto pela escala).

## Evidência de aderência ao tipo (correction)
- Só corrigi as divergências listadas no review (PAT-01/E1-02/pilares/contrato). Não implementei melhorias adicionais, não toquei `red_herrings`/PAT-02, `codigos`/PAT-03, `objetivos_por_envelope`/PAT-04 (confirmados preservados pelo revisor, item 5 do pedido).
- Não editei `generator/`.
- Não avancei `CURRENT_STEP`, não alterei `REVIEW_STATUS` para approved.

## Confirmação de que PAT-01 foi restaurado

Definição de PAT-01 (`framework/08_MODELO_REFERENCIA.md`, seção 1.8): "um registro de presença (log de acesso: ator + ponto + horário) só vira prova quando confirmado por um documento de regra independente que declara a credencial pessoal/intransferível e o ponto de acesso exclusivo por autenticação." Campos: `pilares_validacao` (`documento_principal` = log, `confirmacao` = manual/política).

Estado atual do blueprint:
- Regra de exclusividade em texto, em `E1-02` (documento tipo `manual`): *"Crachás de acesso ao terminal da báscula são pessoais e intransferíveis; nenhum lançamento manual pode ser feito com o crachá de outro operador."* (também no `CORPO_CARTA`, com detalhe operacional adicional).
- `pilares_validacao[0]`: `documento_principal: E1-04` (log de acesso), `confirmacao: E1-02` (manual/regra), `personagem_id: 02` — par log × regra-de-exclusividade, igual ao aprovado no `STEP-02_REVIEW.md`.
- `contratos_evidencia.C-E1-01`: `prova_principal: E1-04`, `confirmacao_independente: E1-02` — mesma dupla formalizada no contrato de evidência que sustenta a conclusão de presença exclusiva de Joaquim (personagem `02`).
- `E1-02` deixou de ser órfão: aparece em `pilares_validacao[0].confirmacao`, em `contratos_evidencia.C-E1-01.confirmacao_independente` e em `documentos[E1-04].confirma`/`confirmado_por`. Consequência confirmada nos avisos `GP_003` re-rodados: `E1-02` não aparece mais na lista (lista atual: `E1-01`, `E1-03`, `E1-06`, `E1-07`, `E1-08`, `E2-01`, `E2-06`, `E2-07`, `E2-08` — 9 itens, mesma contagem do STEP-03 original, mas com `E1-02` trocado por `E1-03`, que agora é reforço opcional intencionalmente não-contratual).
- `E1-03` (escala) preservado como terceira camada de reforço (`pilares_validacao[1]`, renomeado "escala de turno (reforço)"), não removido — decisão permitida pelo item 4 do pedido de correção.

## Divergências
- nenhuma

## Observações para revisão
- `GP_003` continua com 9 ocorrências (mesma contagem do STEP-03 original), mas o conjunto de documentos mudou: `E1-02` saiu da lista de órfãos (agora participa do contrato `C-E1-01`), `E1-03` entrou (reforço narrativo intencional, sem contrato formal — consistente com "não precisa remover E1-03 se ainda fizer sentido narrativo").
- `DC_000` (moderado) e demais avisos (`ELENCO_001`, `CONT_002`) inalterados — fora do escopo desta correção (já avaliados como não-bloqueantes pelo revisor em DVG-EXEC-005/006 do STEP-03 original).
- Nenhuma regressão nos 4 critérios formais: strict 0 críticos, estimador `intermediario`, `clue_graph` depth=4 sem `GP_007`, `obviousness_checker` zero findings.

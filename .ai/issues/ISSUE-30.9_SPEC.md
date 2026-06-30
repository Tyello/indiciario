# ISSUE-30.9 — GP_004 isenta contratos de descarte

## Contexto

A calibração da ISSUE-30.8 disparou `GP_004` no contrato `C-E1-DESCARTE` de "Uma Noite Sem Flores": *"Contrato não é obrigatório nem final; pode ser beco sem saída lógico."* O relatório de calibração (`docs/CALIBRACAO_REFERENCIA_EXTERNA.md`, CR-02) classificou isso como **falso positivo de métrica**: um contrato de descarte é, por design, nem obrigatório nem final — seu papel é guiar o jogador a descartar um red herring, não ser gate de avanço.

A lógica atual em `generator/clue_graph.py` marca como órfão (`dead_ends` → `GP_004`) todo contrato que `not obrigatoria_para_avanco and not _is_final_contract`. Isso captura contratos de descarte legítimos junto com becos sem saída reais. O campo `tipo` (com valor `descarte`) já existe no schema — a correção é barata e não exige mudança de schema.

**Origem:** balanço de calibração 2026-06-29; o próprio relatório recomenda a isenção (prioridade baixa, mas acionável). Defeito de métrica informa a regra; não é patch de caso.

## Objetivo

`GP_004` deixa de disparar para contratos com `tipo == "descarte"`, continuando a disparar para contratos genuinamente órfãos (não-obrigatórios, não-finais e não-descarte).

## Fora de escopo

Os outros dois pontos cegos que a calibração levantou ficam **deliberadamente fora**, em coerência com o que o relatório de calibração já decidiu:

- **`GP_003` (documentos de contexto fora de contrato)** — o relatório recomenda *aguardar mais casos* antes de introduzir uma distinção "documento de contexto" (exigiria mudança de schema). Não tratar aqui.
- **Estimador de tempo (delta 90 vs 100 min)** — o relatório registra para **ISSUE-31+**. Não tratar aqui.

Tratar esses agora contradiria a conclusão recém-mergeada da 30.8. Ficam como dívida consciente.

## Contrato / regras

- **GP4-01** — Na função de `generator/clue_graph.py` que computa `orphan_contracts`/`dead_ends`, excluir contratos com `tipo == "descarte"` (usar o valor de enum/string que o schema define para descarte; confirmar no STEP-01).
- **GP4-02** — `GP_004` permanece para contratos órfãos reais: não-obrigatório, não-final **e** não-descarte.
- **GP4-03** — Nenhuma mudança em `GP_003`, `GP_007`, nem na noção de contrato final; só a exclusão de `descarte` do cálculo de beco sem saída.
- **GP4-04** — Sem mudança de schema; `tipo` já existe e já aceita `descarte`.

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilho: "novos/alterados códigos de erro").

- [ ] `docs/GUIA_CODIGOS_ERROS.md` — atualizar a descrição de `GP_004`: não dispara para contratos de descarte (que são, por natureza, não-obrigatórios e não-finais).
- [ ] `docs/ESTADO_ATUAL.md` — uma linha em "problemas já tratados": GP_004 isenta descarte (falso positivo identificado na calibração).
- [ ] `framework/08_MODELO_REFERENCIA.md` — ⏭️/✅: se a ISSUE-30.10 já adicionou PAT-02 (descarte), conferir coerência; senão ⏭️.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ nenhum doc criado/movido.

## Casos de teste (TDD — RED antes de GREEN)

Em `tests/test_clue_graph.py` (ou o arquivo de teste do clue_graph existente):

1. `test_gp004_nao_dispara_para_descarte_calibracao` — sobre `examples/caso_referencia_uma_noite_sem_flores.json`, `GP_004` **não** aparece para `C-E1-DESCARTE`. (Hoje dispara → RED.)
2. `test_gp004_ainda_dispara_para_orfao_real` — caso sintético com um contrato não-obrigatório, não-final e `tipo != descarte` → `GP_004` dispara. (Trava regressão / evita over-fix.)
3. `test_gp004_descarte_sintetico_isento` — caso sintético com contrato `tipo == descarte` não-obrigatório/não-final → `GP_004` não dispara.

## Restrições arquiteturais

Sem schema novo; sem LLM; sem rede. Mudança mínima e localizada na função de detecção de órfãos; não reescrever a travessia do grafo. `ruff` limpo; suíte sem regressão.

## Critério de aceite

- [ ] GP4-01..04 implementadas; 3 testes passam.
- [ ] `GP_004` não dispara para `C-E1-DESCARTE` na calibração; continua disparando para órfão real.
- [ ] `pytest tests/ -q` sem regressão; `ruff` limpo.
- [ ] `python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict` segue exit 0 (com um aviso a menos).
- [ ] Impacto documental resolvido (✅/⏭️).

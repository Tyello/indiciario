# Execution Report — ISSUE-30.9 STEP-02

STEP: STEP-02
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Escrever os 3 testes do SPEC para GP_004/descarte e confirmar comportamento RED atual.

## Arquivos lidos
- .ai/issues/ISSUE-30.9.md
- .ai/issues/ISSUE-30.9_SPEC.md
- .ai/runs/ISSUE-30.9/STEP-01_EXECUTION.md
- generator/clue_graph.py (leitura)
- tests/test_clue_graph.py

## Arquivos alterados
- tests/test_clue_graph.py

## Comandos executados
- `.venv\Scripts\python.exe -m pytest tests/test_clue_graph.py -q` — 2 failed, 12 passed.

## O que foi feito
- Import de `load_blueprint` (`generator/case_review.py`) e path constante para `examples/caso_referencia_uma_noite_sem_flores.json`.
- `test_gp004_nao_dispara_para_descarte_calibracao`: carrega o caso de calibração real e assere que `C-E1-DESCARTE` não aparece em `orphan_contracts`/`dead_ends`/issues `GP_004`.
- `test_gp004_ainda_dispara_para_orfao_real`: caso sintético com `tipo="oportunidade"`, `obrigatorio=False`, não final → assere que `GP_004` ainda dispara (trava de regressão).
- `test_gp004_descarte_sintetico_isento`: caso sintético com `tipo="descarte"`, `obrigatorio=False`, não final → assere que `GP_004` não dispara.
- Nenhuma alteração em `generator/clue_graph.py`.

## Evidência de aderência ao tipo
- Só `tests/test_clue_graph.py` foi editado; `generator/clue_graph.py` permanece intocado (conferido via leitura, nenhuma chamada Edit/Write nele).
- Resultado pytest confirma RED real: 2 falhas por `AssertionError` no comportamento ainda não corrigido.

## Resultado por teste
- `test_gp004_nao_dispara_para_descarte_calibracao` — **FALHA** (`AssertionError: 'C-E1-DESCARTE' not in ['C-E1-DESCARTE']`). Esperado pelo SPEC: RED hoje, GP_004 dispara incorretamente para o contrato de descarte do caso de calibração.
- `test_gp004_ainda_dispara_para_orfao_real` — **PASSA**. Comportamento atual de GP_004 para órfão real (não-obrigatório, não-final, tipo != descarte) já é o esperado; este teste é trava de regressão, não depende da correção pendente.
- `test_gp004_descarte_sintetico_isento` — **FALHA** (`AssertionError: 'C-E1-DESCARTE-SINTETICO' not in ['C-E1-DESCARTE-SINTETICO']`). Mesma lógica de exceção ainda não implementada testada via caso sintético; RED esperado pelo mesmo motivo do teste 1 — o SPEC não afirma que este teste passa antes da correção, e logicamente ele testa exatamente a regra ausente (isenção de `tipo == "descarte"`).

## Divergências
- nenhuma

## Observações para revisão
- Resultado de 2 falhas (não 1) é consistente: testes 1 e 3 cobrem o mesmo comportamento ausente (isenção de `tipo == "descarte"`) em dois contextos (caso real de calibração vs. caso sintético); teste 2 é a trava de não-regressão e já passa com o código atual.
- STEP-03 (GREEN) deve fazer os 3 testes passarem sem alterar GP_003/GP_007 nem a noção de contrato final.

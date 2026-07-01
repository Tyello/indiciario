# Execution Report — ISSUE-30.9 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos
- AGENTS.md
- docs/LLM_CONTEXT.md
- .ai/issues/ISSUE-30.9.md
- .ai/issues/ISSUE-30.9_SPEC.md
- .ai/skills/tdd.md
- generator/clue_graph.py
- generator/models.py (campo `tipo` de `ContratoEvidencia`)
- tests/test_clue_graph.py
- examples/caso_referencia_uma_noite_sem_flores.json (contrato `C-E1-DESCARTE`)

## Arquivos alterados
- nenhum

## Comandos executados
- nenhum

## Resultado

- **Campo `tipo` de `ContratoEvidencia`**: tipado como `str` simples em `generator/models.py` (sem `Literal`/enum). Não há validação fechada de valores — qualquer string é aceita, então isentar `tipo == "descarte"` não exige schema novo.
- **Valor exato usado para descarte**: `"descarte"` (string literal, minúscula, sem acento). Confirmado em `examples/caso_referencia_uma_noite_sem_flores.json`, contrato `C-E1-DESCARTE` (linha 1786): `"tipo": "descarte"`, `"obrigatoria_para_avanco": false`, `"fase": "E1"`.
- **Ponto exato da edição em `generator/clue_graph.py`**: função `analyze_clue_graph`, bloco de cálculo de órfãos/becos sem saída, linhas 217-230:
  - `final_contracts` (linha 217) já filtra por `_is_final_contract` (fase `"final"` ou tipo `"solucao_final"`).
  - `orphan_contracts` (linhas 218-222) é a lista que precisa da nova exclusão: hoje inclui qualquer contrato com `not contrato.obrigatoria_para_avanco and not _is_final_contract(contrato)`. Falta excluir também `contrato.tipo == "descarte"`.
  - `dead_ends` (linha 223) é derivado diretamente de `orphan_contracts` (`dead_ends = list(orphan_contracts)`), então a correção em `orphan_contracts` propaga automaticamente para `dead_ends`.
  - O loop GP_004 (linhas 224-230) itera sobre `orphan_contracts`; ao corrigir a lista-fonte, o issue GP_004 deixa de ser emitido para contratos de descarte sem necessidade de tocar o loop em si.
  - Com `C-E1-DESCARTE` (`tipo="descarte"`, `obrigatoria_para_avanco=False`, não final) no blueprint de calibração, hoje o contrato cai em `orphan_contracts`/`dead_ends` e dispara GP_004 — esse é o falso positivo a corrigir (confirmado pelo SPEC, vinculado à calibração ISSUE-30.8).

- **Instanciação do grafo em testes**: `tests/test_clue_graph.py` usa o helper `_contrato(id_, *, fase, tipo, prova, confirmacao, descartes, obrigatorio)` (linhas 10-32) para construir `ContratoEvidencia`, e `_blueprint_com_contratos(*contratos)` (linhas 35-38) para injetar contratos em um `blueprint_valido()` importado de `tests.test_generator_validator`. Padrão usado pelos testes existentes de GP_004 (`test_contrato_nao_obrigatorio_e_nao_final_aparece_em_orphan_contracts_e_dead_ends`, linha 113): construir `ContratoEvidencia` via `_contrato(...)`, montar blueprint via `_blueprint_com_contratos(...)`, gerar grafo via `build_clue_graph(blueprint)` e relatório via `analyze_clue_graph(graph, blueprint)`. Os 3 testes do STEP-02 devem seguir esse mesmo padrão, variando `tipo="descarte"`.

## Divergências
- nenhuma

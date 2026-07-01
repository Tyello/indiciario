# Execution Report — ISSUE-30.9 STEP-03

STEP: STEP-03
STEP_TYPE: green
EXECUTION_STATUS: completed

## Objetivo
Implementar GP4-01..04 em `generator/clue_graph.py`: excluir contratos `tipo == "descarte"` do cálculo de `orphan_contracts`/`dead_ends`/`GP_004`.

## Arquivos lidos
- .ai/issues/ISSUE-30.9.md
- .ai/issues/ISSUE-30.9_SPEC.md
- .ai/runs/ISSUE-30.9/STEP-01_EXECUTION.md
- .ai/runs/ISSUE-30.9/STEP-02_EXECUTION.md
- generator/clue_graph.py
- generator/models.py
- tests/test_clue_graph.py

## Arquivos alterados
- generator/clue_graph.py

## Mudança feita
Em `analyze_clue_graph`, condição de `orphan_contracts` (linhas ~218-222) passou de:
```python
orphan_contracts = sorted(
    contrato.id
    for contrato in graph.contracts.values()
    if not contrato.obrigatoria_para_avanco and not _is_final_contract(contrato)
)
```
para:
```python
orphan_contracts = sorted(
    contrato.id
    for contrato in graph.contracts.values()
    if not contrato.obrigatoria_para_avanco
    and not _is_final_contract(contrato)
    and contrato.tipo != "descarte"
)
```
`dead_ends` (= `list(orphan_contracts)`) e o loop que emite `GP_004` não foram tocados — herdam a correção automaticamente, como previsto no SPEC. Nenhuma mudança em `GP_003`, `GP_007`, `_is_final_contract`, schema, ou travessia do grafo.

## Comandos executados
1. `.venv/Scripts/python.exe -m pytest tests/test_clue_graph.py -q` → **14 passed** (3 novos do STEP-02 + 11 pré-existentes). 0 falhas.
2. `.venv/Scripts/python.exe -m pytest tests/ -q` → **5 failed, 1377 passed, 3 skipped**. As 5 falhas são pré-existentes e não relacionadas: `test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`, `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`, `test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`, `test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`, `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail` — todas `OSError: [WinError 1314]` por falta de privilégio de symlink no Windows local (limitação de ambiente conhecida, registrada em memória de sessão; nada a ver com `clue_graph.py`). Sem regressão atribuível a esta mudança.
3. `.venv/Scripts/python.exe -m ruff check generator/` → **All checks passed!**
4. `.venv/Scripts/python.exe -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict` → exit 0. 13 avisos (antes 14 — `GP_004` para `C-E1-DESCARTE` não aparece mais). Avisos restantes: 1 `ELENCO_001`, 11 `GP_003`, 1 `PT_001`. Nenhum `GP_004`.

## Resultado por teste (tests/test_clue_graph.py)
- `test_gp004_nao_dispara_para_descarte_calibracao` — PASSA.
- `test_gp004_ainda_dispara_para_orfao_real` — PASSA (regressão preservada).
- `test_gp004_descarte_sintetico_isento` — PASSA.

## Evidência de aderência ao tipo
- Único arquivo de produção editado: `generator/clue_graph.py`, único trecho tocado (condição de `orphan_contracts`).
- `tests/test_clue_graph.py` não foi editado neste step (só leitura).
- `GP_003`, `GP_007`, `_is_final_contract` e travessia do grafo intactos.

## Divergências
- nenhuma

## Observações para revisão
- As 5 falhas de symlink em `tests/` são ambiente Windows pré-existente (sem privilégio para `os.symlink`), não regressão desta mudança. Confirmar se necessário rodando `git stash` + suíte antes da edição, mas já documentado como limitação conhecida do ambiente local.

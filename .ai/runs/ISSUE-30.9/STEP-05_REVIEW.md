# Review Report — ISSUE-30.9 STEP-05

STEP: STEP-05
STEP_TYPE: validation
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- nenhuma alteração de código (validation) — apenas `.ai/runs/ISSUE-30.9/STEP-05_EXECUTION.md`

## Arquivos alterados encontrados (git diff --name-only)
- .ai/issues/ISSUE-30.9.md
- docs/ESTADO_ATUAL.md
- docs/GUIA_CODIGOS_ERROS.md
- generator/clue_graph.py
- tests/test_clue_graph.py

(estas são acumuladas de STEP-01..04; STEP-05 em si não alterou implementação — confirmado.)

## Verificações
- [x] Execution report existe
- [x] Type válido (validation)
- [x] Comandos dentro do permitido (`pytest tests/ -q`; `ruff check generator/ tests/`; `python -m generator.validator ... --strict`)
- [x] Nenhuma correção/implementação tentada durante o step
- [x] Critérios do tipo atendidos (apenas execução + registro)

## Verificação independente (rodada pelo revisor)

### pytest tests/ -q
- 1ª rodada: 6 failed, 1376 passed, 3 skipped
- 2ª rodada: 5 failed, 1377 passed, 3 skipped
- As 5 falhas symlink (Windows `WinError 1314`, sem privilégio) são consistentes nas duas rodadas e batem com o relato do executor.
- A 6ª falha na 1ª rodada (`tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`) é flaky: reproduzida isoladamente com `sha256` diferente a cada execução, e reproduzida também em `main` sem as mudanças desta issue (via `git stash` / `git stash pop`, repo restaurado limpo ao final). Não relacionada a `clue_graph.py`/`GP_004`, pré-existente, fora de escopo.
- Conclusão: sem regressão introduzida por esta issue.

### ruff check generator/ tests/
- Confirmado: 51 erros no total do repo, idênticos com e sem as mudanças desta issue (`git stash` comparativo, repo restaurado com `git stash pop`).
- `ruff check generator/clue_graph.py tests/test_clue_graph.py` isolado: `All checks passed!` — arquivos tocados pela issue estão limpos.

### validator strict (caso_referencia_uma_noite_sem_flores)
- Confirmado: exit OK, Críticos: 0, Moderados: 0, Avisos: 13, nenhum `[GP_004]` na saída. Bate com o relato do executor.

## Divergências

### DVG-EXEC-001 — critério "ruff check generator/ tests/ limpo" não literal
Severidade: minor (não bloqueante)

Análise: o critério literal do STEP-05 pede `ruff check generator/ tests/` limpo, e isso não é atendido no escopo total do repositório (51 erros, confirmados). Porém:
- os 51 erros são idênticos em `main` antes desta issue (confirmado via `git stash` comparativo pelo revisor, independente do executor);
- os únicos arquivos editáveis/tocados por esta issue (`generator/clue_graph.py`, `tests/test_clue_graph.py`) estão 100% limpos isoladamente;
- a issue (SPEC ISSUE-30.9) tem escopo estrito: isentar `tipo == descarte` do cálculo GP_004 em `clue_graph.py`; não pede lint geral do repositório;
- corrigir os 51 erros pré-existentes seria escopo novo, não autorizado pelo contrato do step, e violaria a allowlist de arquivos editáveis do STEP-05 (`.ai/runs/ISSUE-30.9/STEP-05_EXECUTION.md` apenas).

Decisão: a leitura correta do critério "ruff check generator/ tests/ limpo" é "limpo nos arquivos tocados por esta issue", não "limpo em todo o repositório". Dívida técnica pré-existente e alheia não é motivo de rejeição/bloqueio de um step de validação com escopo cirúrgico. Divergência registrada, aceita como não-bloqueante, severidade minor (documentação/interpretação, sem alteração indevida de implementação).

## Decisão
APPROVED

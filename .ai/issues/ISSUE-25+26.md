# ISSUE-25+26 — Multiagent Workspace + Manual Orchestrator

## Estado

```
STATUS: done
CURRENT_STEP: STEP-12
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-12
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-25+26/STEP-12_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-25+26/STEP-11_REVIEW.md
BLOCKER: none
```

## Contexto

As ISSUE-16–22 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `generator/gate_evaluator.py` — Gate Evaluator com regras GE_001–GE_008
- `generator/narrative_reviewer.py` — Narrative Reviewer com regras NR_001–NR_008
- `generator/evidence_reviewer.py` — Evidence Reviewer com regras ER_001–ER_008
- 1104 testes passando

O que ainda não existe:
- Estrutura de workspace por run que organiza artefatos, logs e estado
- Manual Orchestrator que conduz a run sem LLM, registra ingestões e gates

## Spec completa

Ver `.ai/issues/ISSUE-25+26_SPEC.md`

## Ambiente

Interpretador correto: `.venv/Scripts/python.exe`.
`python` do sistema não tem jsonschema. Comandos pytest/ruff sempre via
`.venv/Scripts/python.exe -m pytest ...` e `.venv/Scripts/python.exe -m ruff ...`.
Baseline conhecido: 1104 passed, 3 skipped, 5 failed (5 falhas symlink-Windows
WinError 1314, ambiente, não-regressão).

## Steps

### STEP-01 — Leitura e mapeamento das APIs existentes

Status: pending
Owner: executor
Type: reading

Objetivo:
- Mapear padrões a reaproveitar: dataclasses + builder + validate de
  `generator/gate_evaluator.py`, `generator/blind_solve_run_record.py`,
  `generator/narrative_reviewer.py`.
- Mapear padrão de schema YAML com `additionalProperties: false` e `neutral_id`
  em `schemas/gate_evaluation.schema.yaml`, `schemas/review_report.schema.yaml`,
  `schemas/blind_solve_run_record.schema.yaml`.
- Mapear padrão de teste de schema em `tests/test_gate_evaluation_schema.py` e
  padrão de teste semântico em `tests/test_gate_evaluator.py`.
- Registrar no execution report: como `validate_*` carrega schema YAML, formato
  das mensagens de erro, helper `neutral_id`, e como dataclasses são serializadas.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/skills/README.md`
- `.ai/skills/tdd.md`
- `generator/gate_evaluator.py`
- `generator/blind_solve_run_record.py`
- `generator/narrative_reviewer.py`
- `schemas/gate_evaluation.schema.yaml`
- `schemas/review_report.schema.yaml`
- `schemas/blind_solve_run_record.schema.yaml`
- `tests/test_gate_evaluator.py`
- `tests/test_gate_evaluation_schema.py`

Arquivos editáveis:
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar qualquer arquivo de implementação, teste, schema ou fixture.
- Criar schema ou código.
- Rodar pytest.

Done quando:
- Execution report descreve padrões exatos de schema-loading, mensagens de erro,
  neutral_id e serialização de dataclasses a reusar.

Revisão:
- Confirmar que só houve leitura; nenhum arquivo de implementação/teste alterado.

### STEP-02 — Baseline da suíte

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Registrar estado atual da suíte antes de qualquer alteração.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-25+26/STEP-02_EXECUTION.md`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_gate_evaluator.py -q`
- `.venv/Scripts/python.exe -m pytest tests/ -q`

Proibido:
- Alterar qualquer código, teste, schema ou fixture.
- Corrigir falhas.

Done quando:
- Execution report contém contagem de testes (esperado 1104 passed, 3 skipped,
  5 failed symlink-Windows conhecidas) e confirma baseline.

Revisão:
- Confirmar que apenas baseline foi rodado; resultados registrados.

### STEP-03 — RED: fixtures + testes de schema (casos 1–10)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as 4 fixtures válidas em `tests/fixtures/workspace_run/valid/`:
  `valid_initialized.yaml`, `valid_in_progress_with_artifact.yaml`,
  `valid_gate_blocked.yaml`, `valid_done.yaml`.
- Criar `tests/test_workspace_run_schema.py` com os casos 1–10 da spec.
- Testes devem FALHAR (RED) por ausência de `schemas/workspace_run.schema.yaml`
  e de `generator.workspace.validate_workspace_run`.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `schemas/gate_evaluation.schema.yaml`
- `tests/test_gate_evaluation_schema.py`

Arquivos editáveis:
- `tests/test_workspace_run_schema.py`
- `tests/fixtures/workspace_run/valid/valid_initialized.yaml`
- `tests/fixtures/workspace_run/valid/valid_in_progress_with_artifact.yaml`
- `tests/fixtures/workspace_run/valid/valid_gate_blocked.yaml`
- `tests/fixtures/workspace_run/valid/valid_done.yaml`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`

Proibido:
- Criar `schemas/workspace_run.schema.yaml`.
- Criar qualquer módulo em `generator/`.
- Implementar qualquer GREEN.

Done quando:
- 4 fixtures válidas criadas conforme spec.
- Casos 1–10 existem e FALHAM pelo motivo certo, registrado no report.

Revisão:
- Confirmar que só testes/fixtures criados, sem GREEN; RED registrado.

### STEP-04 — RED: testes de schema (casos 11–20)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar as 8 fixtures inválidas em `tests/fixtures/workspace_run/invalid/`:
  `invalid_status.yaml`, `invalid_stage.yaml`, `missing_run_id.yaml`,
  `missing_case_ref.yaml`, `invalid_artifact_type.yaml`, `invalid_outcome.yaml`,
  `extra_top_field.yaml`, `missing_justification.yaml`.
- Adicionar a `tests/test_workspace_run_schema.py` os casos 11–20 da spec.
- Novos testes devem FALHAR (RED) por ausência do schema.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `tests/test_workspace_run_schema.py`
- `tests/fixtures/workspace_run/valid/valid_initialized.yaml`

Arquivos editáveis:
- `tests/test_workspace_run_schema.py`
- `tests/fixtures/workspace_run/invalid/invalid_status.yaml`
- `tests/fixtures/workspace_run/invalid/invalid_stage.yaml`
- `tests/fixtures/workspace_run/invalid/missing_run_id.yaml`
- `tests/fixtures/workspace_run/invalid/missing_case_ref.yaml`
- `tests/fixtures/workspace_run/invalid/invalid_artifact_type.yaml`
- `tests/fixtures/workspace_run/invalid/invalid_outcome.yaml`
- `tests/fixtures/workspace_run/invalid/extra_top_field.yaml`
- `tests/fixtures/workspace_run/invalid/missing_justification.yaml`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`

Proibido:
- Criar schema ou implementação.
- Implementar GREEN.

Done quando:
- 8 fixtures inválidas criadas; casos 11–20 existem e falham pelo motivo certo.

Revisão:
- Confirmar apenas testes/fixtures alterados, sem GREEN; valid/ intactas.

### STEP-05 — GREEN: schema + dataclasses + validate/build/serialize

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `schemas/workspace_run.schema.yaml` conforme modelo da spec
  (`additionalProperties: false` no topo, em `artifacts[]` e `decisions[]`;
  enums de `status`, `current_stage`/`stage`, `artifact_type`, `outcome`).
- Criar `generator/workspace.py` com dataclasses `WorkspaceArtifact`,
  `WorkspaceDecision`, `WorkspaceRun`, `WorkspaceSemanticResult`, constantes
  `SCHEMA_VERSION`/`VALID_*`, e funções `validate_workspace_run`,
  `build_workspace_run`, `run_to_dict`.
- NÃO implementar `validate_workspace_semantics` ainda (stub não exigido).
- Fazer os 20 testes de schema (STEP-03/04) passarem (GREEN).

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `tests/test_workspace_run_schema.py`
- `generator/gate_evaluator.py`
- `generator/blind_solve_run_record.py`
- `schemas/gate_evaluation.schema.yaml`
- `schemas/blind_solve_run_record.schema.yaml`

Arquivos editáveis:
- `schemas/workspace_run.schema.yaml`
- `generator/workspace.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`
- `.venv/Scripts/python.exe -m ruff check generator/workspace.py`

Proibido:
- Implementar `validate_workspace_semantics`.
- Criar `generator/manual_orchestrator.py`.
- Alterar arquivos existentes além dos criados.

Done quando:
- Todos os 20 testes de schema passam; `ruff` limpo.

Revisão:
- Confirmar implementação mínima (schema + dataclasses + validate_workspace_run
  + build_workspace_run + run_to_dict); sem semantics; sem orchestrator.

### STEP-06 — RED: testes de workspace semântico (casos 21–50)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_workspace.py` com os casos 21–50 da spec:
  21–28: regras WS_001–WS_008
  29–36: `validate_workspace_semantics`
  37–44: `build_workspace_run` e `validate_workspace_run`
  45–50: integração e edge cases
- Testes devem FALHAR (RED) por ausência de `validate_workspace_semantics`.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `generator/workspace.py`
- `tests/test_gate_evaluator.py`

Arquivos editáveis:
- `tests/test_workspace.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace.py -q`

Proibido:
- Implementar `validate_workspace_semantics`.
- Implementar GREEN.

Done quando:
- Casos 21–50 existem e falham pelo motivo certo, registrado no report.

Revisão:
- Confirmar só teste criado, sem GREEN.

### STEP-07 — GREEN: validate_workspace_semantics (WS_001–WS_008)

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `validate_workspace_semantics(run) -> WorkspaceSemanticResult`
  em `generator/workspace.py` com as regras WS_001–WS_008.
- Lógica de resultado: `valid: False` se qualquer erro; warnings sempre
  registrados mesmo com `valid: True`.
- Fazer os testes 21–50 passarem; testes de schema continuam verdes.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `tests/test_workspace.py`
- `generator/workspace.py`

Arquivos editáveis:
- `generator/workspace.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`
- `.venv/Scripts/python.exe -m ruff check generator/workspace.py`

Proibido:
- Criar `generator/manual_orchestrator.py`.
- Criar novos testes de escopo relevante.
- Alterar arquivos existentes fora de `generator/workspace.py`.

Done quando:
- Todos os 30 testes de `test_workspace.py` passam; schema verde; `ruff` limpo.

Revisão:
- Confirmar GREEN mínimo; WS_001–WS_008 com teste nomeado; sem orchestrator.

### STEP-08 — RED: testes do manual orchestrator (casos 51–85)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_manual_orchestrator.py` com os casos 51–85 da spec:
  51–58: regras OR_001–OR_008
  59–68: `ingest_artifact`
  69–76: `record_decision`
  77–85: `transition_stage`
- Testes devem FALHAR (RED) por ausência de `generator/manual_orchestrator.py`.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `generator/workspace.py`
- `tests/test_workspace.py`

Arquivos editáveis:
- `tests/test_manual_orchestrator.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_manual_orchestrator.py -q`

Proibido:
- Criar `generator/manual_orchestrator.py`.
- Implementar GREEN.

Done quando:
- Casos 51–85 existem e falham pelo motivo certo (ModuleNotFoundError).

Revisão:
- Confirmar só teste criado, sem GREEN.

### STEP-09 — GREEN: manual orchestrator (OR_001–OR_008)

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `generator/manual_orchestrator.py` com dataclasses `IngestRequest`,
  `TransitionRequest`, `DecisionRequest`, `OrchestratorResult`,
  `TransitionResult`, importando `WorkspaceArtifact`, `WorkspaceDecision`,
  `WorkspaceRun`, `WorkspaceSemanticResult` de `generator.workspace` (sem
  duplicar).
- Implementar `ingest_artifact`, `record_decision`, `transition_stage`,
  `validate_orchestrator_transition` com regras OR_001–OR_008.
- Nenhuma função muta o dict de entrada (`request.run`).
- Fazer os testes 51–85 passarem; workspace e schema continuam verdes.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md`
- `tests/test_manual_orchestrator.py`
- `generator/workspace.py`

Arquivos editáveis:
- `generator/manual_orchestrator.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_manual_orchestrator.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`
- `.venv/Scripts/python.exe -m ruff check generator/manual_orchestrator.py`

Proibido:
- Duplicar dataclasses de `workspace.py`.
- Criar novos testes de escopo relevante.
- Alterar `generator/workspace.py` além do necessário para export.

Done quando:
- Todos os 35 testes do orchestrator passam; workspace + schema verdes;
  `ruff` limpo.

Revisão:
- Confirmar sem duplicação de dataclasses; imutabilidade de entrada; OR_*
  com teste nomeado; sem alteração de proibidos.

### STEP-10 — REFACTOR

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Extrair helpers de lookup de artefatos/decisões por tipo/stage usados em
  múltiplas funções.
- Garantir que regras OR_* não dupliquem lógica de WS_*.
- Sem alterar comportamento nem API pública.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `generator/workspace.py`
- `generator/manual_orchestrator.py`
- `tests/test_workspace.py`
- `tests/test_manual_orchestrator.py`
- `tests/test_workspace_run_schema.py`

Arquivos editáveis:
- `generator/workspace.py`
- `generator/manual_orchestrator.py`

Comandos permitidos:
- `.venv/Scripts/python.exe -m pytest tests/test_workspace.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_manual_orchestrator.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`
- `.venv/Scripts/python.exe -m ruff check generator/workspace.py generator/manual_orchestrator.py`

Proibido:
- Adicionar comportamento novo.
- Alterar API pública.
- Adicionar testes de escopo relevante.

Done quando:
- Todos os testes continuam verdes; `ruff` limpo; comportamento inalterado.

Revisão:
- Confirmar ausência de comportamento/API novos.

### STEP-11 — VALIDATION: suíte completa e checagens

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar validação final completa e registrar resultados.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-25+26/STEP-11_EXECUTION.md`

Comandos permitidos:
- `.venv/Scripts/python.exe -m ruff check generator/workspace.py generator/manual_orchestrator.py`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace_run_schema.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_workspace.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_manual_orchestrator.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_evidence_reviewer.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_gate_evaluator.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_gate_evaluation_schema.py -q`
- `.venv/Scripts/python.exe -m pytest tests/test_blind_solve_run_record.py -q`
- `.venv/Scripts/python.exe -m pytest tests/ -q`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- Corrigir falhas.
- Alterar código/testes.

Done quando:
- Suíte completa passa sem regressão (1104 baseline + 85 novos = ~1189 passed,
  5 failed symlink-Windows conhecidas) e resultados registrados.
- `git diff --stat` confirma que só arquivos novos da issue foram criados.

Revisão:
- Confirmar só comandos de validação; resultados registrados; nenhuma correção.

### STEP-12 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Atualizar `docs/BLIND_SOLVER_HARNESS.md` com seção curta sobre Workspace e
  Manual Orchestrator (API, regras WS_*/OR_*, relação com Gate Evaluator).
- Registrar resumo final no execution report do step.

Contexto permitido:
- `.ai/issues/ISSUE-25+26.md`
- `.ai/runs/ISSUE-25+26/STEP-11_EXECUTION.md`
- `docs/BLIND_SOLVER_HARNESS.md`

Arquivos editáveis:
- `docs/BLIND_SOLVER_HARNESS.md`
- `.ai/runs/ISSUE-25+26/STEP-12_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar implementação ou testes.
- Rodar pytest.

Done quando:
- Doc atualizado (ou justificado como desnecessário) e resumo final registrado.

Revisão:
- Confirmar só documentação/relatório alterados.

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Aguardando orquestração inicial.
- STEP-00 orquestrado: 12 steps planejados (reading/baseline/red×3/green×3/refactor/validation/wrap-up). CURRENT_STEP→STEP-01, NEXT_ACTION→execute.
- STEP-01 executado; aguardando revisão.
- STEP-01 auto-approved (low-risk reading); só leitura/mapeamento, sem divergências. Avançando STEP-02.
- STEP-02 executado; aguardando revisão.
- STEP-02 auto-approved (low-risk baseline); 1104 passed, 3 skipped, 5 failed symlink-Windows conhecidas. Baseline verde. Avançando STEP-03.
- STEP-01 executado; aguardando revisão.
- STEP-02 executado; aguardando revisão.
- STEP-03 executado; aguardando revisão.
- STEP-03 aprovado; aguardando orquestrador.
- STEP-03 aprovado (red, SEVERITY none); só testes/fixtures valid/, sem GREEN, RED por ModuleNotFoundError. Avançando STEP-04.
- STEP-04 executado; aguardando revisão.
- STEP-04 aprovado; aguardando orquestrador.
- STEP-04 aprovado (red, SEVERITY none); 8 fixtures invalid/ + casos 11–20, valid/ intactas, sem GREEN. Avançando STEP-05.
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado; aguardando orquestrador.
- STEP-05 aprovado (green, SEVERITY none); só schema + workspace.py, sem semantics, sem orchestrator, 21 passed schema. Avançando STEP-06.
- STEP-06 executado; aguardando revisão.
- STEP-06 aprovado; aguardando orquestrador.
- STEP-06 aprovado (red, SEVERITY none); só tests/test_workspace.py casos 21–50, sem GREEN, RED por ImportError validate_workspace_semantics. Avançando STEP-07.
- STEP-07 executado; aguardando revisão.
- STEP-07 aprovado; aguardando orquestrador.
- STEP-07 aprovado (green, SEVERITY none); só workspace.py, WS_001–WS_008 com teste nomeado, sem mutação, 31 passed. Avançando STEP-08.
- STEP-08 executado; aguardando revisão.
- STEP-08 aprovado; aguardando orquestrador.
- STEP-08 aprovado (red, SEVERITY none); só tests/test_manual_orchestrator.py casos 51–85, sem GREEN, RED por ModuleNotFoundError. Avançando STEP-09.
- STEP-09 executado; aguardando revisão.
- STEP-09 aprovado; aguardando orquestrador.
- STEP-09 aprovado (green, SEVERITY none); só manual_orchestrator.py, zero dataclass duplicada (importadas de workspace), sem mutação de entrada, OR_001–OR_008 com teste nomeado, 36 passed. Avançando STEP-10.
- STEP-10 executado; aguardando revisão.
- STEP-10 aprovado; aguardando orquestrador.
- STEP-10 aprovado (refactor, SEVERITY none); só manual_orchestrator.py (_has_artifact_type generalizado), API/comportamento inalterados, 88 verde. Avançando STEP-11.
- STEP-11 executado; aguardando revisão.
- STEP-11 aprovado; aguardando orquestrador.
- STEP-11 aprovado (validation, SEVERITY none); suíte completa 1192 passed, 5 failed symlink-Windows, nenhum arquivo existente alterado. Avançando STEP-12.
- STEP-12 executado; aguardando revisão.
- STEP-12 auto-approved (low-risk wrap-up); só doc BLIND_SOLVER_HARNESS.md + relatório. STATUS→done. ISSUE-25+26 concluída. Próxima: ISSUE-27.
- STEP-12 executado; aguardando revisão.

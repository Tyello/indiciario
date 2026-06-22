# ISSUE-27 — Run Manifest / Run Summary

## Estado

```
STATUS: done
CURRENT_STEP: STEP-14
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-14
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-27/STEP-14_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-27/STEP-13_REVIEW.md
BLOCKER: none
```

## Contexto

As ISSUE-16–26 entregaram:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `generator/blind_solver_report_validator.py` — validador semântico (RV_001–RV_008)
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `generator/gate_evaluator.py` — Gate Evaluator com regras GE_001–GE_008
- `generator/narrative_reviewer.py` — Narrative Reviewer com regras NR_001–NR_008
- `generator/evidence_reviewer.py` — Evidence Reviewer com regras ER_001–ER_008
- `generator/workspace.py` — Workspace com regras WS_001–WS_008
- `generator/manual_orchestrator.py` — Manual Orchestrator com regras OR_001–OR_008
- 1192 testes passando

O que ainda não existe:
- Documento consolidado que captura o resultado completo de uma run
- Schema para esse documento (run_manifest.schema.yaml)
- Builder que deriva pipeline_status, stages_completed, findings e next_steps
  deterministicamente a partir do WorkspaceRun

## Spec completa

Ver `.ai/issues/ISSUE-27_SPEC.md`

## Steps

### STEP-01 — Reading das APIs e schemas

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler API pública e enums de workspace.py, padrões de schema e padrões de teste.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/workspace.py`
- `generator/manual_orchestrator.py`
- `schemas/workspace_run.schema.yaml`
- `schemas/gate_evaluation.schema.yaml`
- `schemas/review_report.schema.yaml`
- `tests/test_workspace.py`
- `tests/test_workspace_run_schema.py`

Arquivos editáveis:
- `.ai/runs/ISSUE-27/STEP-01_EXECUTION.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar implementação, testes ou schema.

Done quando:
- Execution report lista APIs, enums (VALID_STAGES, VALID_ARTIFACT_TYPES, VALID_OUTCOMES), padrão de fixtures e padrão de teste de schema.

Revisão:
- Auto-approve (low-risk).

---

### STEP-02 — Baseline da suíte

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Registrar baseline da suíte antes de qualquer alteração.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-27/STEP-02_EXECUTION.md`

Comandos permitidos:
- `pytest tests/ -q`

Proibido:
- Alterar implementação, testes ou schema.

Done quando:
- Execution report registra contagem (esperado 1192+ passed) e estado limpo.

Revisão:
- Auto-approve (low-risk).

---

### STEP-03 — RED schema: fixtures válidas + casos 1–10

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures válidas e testes de schema casos 1–10. Falham por FileNotFoundError no schema.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `tests/test_workspace_run_schema.py`

Arquivos editáveis:
- `tests/fixtures/run_manifest/valid/valid_complete.yaml`
- `tests/fixtures/run_manifest/valid/valid_incomplete.yaml`
- `tests/fixtures/run_manifest/valid/valid_blocked.yaml`
- `tests/fixtures/run_manifest/valid/valid_no_findings.yaml`
- `tests/test_run_manifest_schema.py`

Comandos permitidos:
- `pytest tests/test_run_manifest_schema.py -q`

Proibido:
- Criar `generator/run_manifest.py` ou `schemas/run_manifest.schema.yaml`. Sem GREEN.

Done quando:
- Casos 1–10 escritos; suíte do arquivo falha por schema/módulo ausente; execution report mostra a falha.

Revisão:
- Apenas testes/fixtures criados; falham pelo comportamento ausente; sem implementação.

---

### STEP-04 — RED schema: rejeições estruturais casos 11–20

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures inválidas e testes de schema casos 11–20.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `tests/test_run_manifest_schema.py`
- `tests/fixtures/run_manifest/valid/valid_complete.yaml`

Arquivos editáveis:
- `tests/fixtures/run_manifest/invalid/invalid_pipeline_status.yaml`
- `tests/fixtures/run_manifest/invalid/missing_manifest_id.yaml`
- `tests/fixtures/run_manifest/invalid/missing_run_id.yaml`
- `tests/fixtures/run_manifest/invalid/invalid_source_type.yaml`
- `tests/fixtures/run_manifest/invalid/invalid_severity.yaml`
- `tests/fixtures/run_manifest/invalid/invalid_outcome.yaml`
- `tests/fixtures/run_manifest/invalid/extra_top_field.yaml`
- `tests/fixtures/run_manifest/invalid/gate_outcome_missing_decision_id.yaml`
- `tests/test_run_manifest_schema.py`

Comandos permitidos:
- `pytest tests/test_run_manifest_schema.py -q`

Proibido:
- Criar `generator/run_manifest.py` ou schema. Sem GREEN.

Done quando:
- Casos 11–20 escritos; suíte falha por schema/módulo ausente.

Revisão:
- Apenas testes/fixtures; sem implementação.

---

### STEP-05 — GREEN schema + dataclasses + validate_run_manifest + manifest_to_dict

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar schema, dataclasses, `validate_run_manifest`, `manifest_to_dict`. Fazer casos 1–20 passarem.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `schemas/workspace_run.schema.yaml`
- `schemas/gate_evaluation.schema.yaml`
- `generator/workspace.py`
- `tests/test_run_manifest_schema.py`

Arquivos editáveis:
- `schemas/run_manifest.schema.yaml`
- `generator/run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest_schema.py -q`
- `ruff check generator/run_manifest.py`

Proibido:
- Adicionar testes novos. Implementar `validate_run_manifest_semantics` ou `build_run_manifest` além de stubs mínimos não exigidos por casos 1–20.

Done quando:
- Casos 1–20 passam; `ruff` limpo; schema tem `additionalProperties: false` no topo e em arrays/gate_outcome; `gate_outcome` nullable.

Revisão:
- Implementação mínima; sem escopo extra; enums conforme spec.

---

### STEP-06 — RED semântico: RM_001–RM_008 casos 21–28

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar testes casos 21–28 (RM_001–RM_008) em test_run_manifest.py.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/run_manifest.py`
- `tests/test_workspace.py`

Arquivos editáveis:
- `tests/test_run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`

Proibido:
- Implementar `validate_run_manifest_semantics`. Sem GREEN.

Done quando:
- Casos 21–28 escritos; falham por função ausente.

Revisão:
- Apenas testes; falham pelo comportamento ausente.

---

### STEP-07 — RED semântico: validate_run_manifest_semantics casos 29–35

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar testes casos 29–35 (resultado, mutação, acúmulo) em test_run_manifest.py.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/run_manifest.py`
- `tests/test_workspace.py`

Arquivos editáveis:
- `tests/test_run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`

Proibido:
- Implementar semântica. Sem GREEN.

Done quando:
- Casos 29–35 escritos; falham por função ausente.

Revisão:
- Apenas testes; falham pelo comportamento ausente.

---

### STEP-08 — GREEN validate_run_manifest_semantics (RM_001–RM_008)

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `validate_run_manifest_semantics` + `ManifestSemanticResult`. Fazer casos 21–35 passarem.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/workspace.py`
- `tests/test_run_manifest.py`

Arquivos editáveis:
- `generator/run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`
- `ruff check generator/run_manifest.py`

Proibido:
- Adicionar testes. Implementar `build_run_manifest` além do necessário.

Done quando:
- Casos 21–35 passam; `ruff` limpo; nunca muta input.

Revisão:
- RM_001–RM_008 conforme tabela; valid=False só em error.

---

### STEP-09 — RED build: build_run_manifest casos 36–45

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar testes casos 36–45 (pipeline_status, stages, espelhamento, gate_outcome).

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/run_manifest.py`
- `generator/workspace.py`
- `tests/test_workspace.py`

Arquivos editáveis:
- `tests/test_run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`

Proibido:
- Implementar `build_run_manifest`. Sem GREEN.

Done quando:
- Casos 36–45 escritos; falham por função ausente.

Revisão:
- Apenas testes; falham pelo comportamento ausente.

---

### STEP-10 — RED build: findings e next_steps casos 46–55

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar testes casos 46–55 (findings_by_artifact, next_steps, round-trip).

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/run_manifest.py`
- `generator/workspace.py`
- `tests/test_workspace.py`

Arquivos editáveis:
- `tests/test_run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`

Proibido:
- Implementar `build_run_manifest`. Sem GREEN.

Done quando:
- Casos 46–55 escritos; falham por função ausente.

Revisão:
- Apenas testes; falham pelo comportamento ausente.

---

### STEP-10_FIX-01 — Correção: next_steps casos 51–53

Status: pending
Owner: executor
Type: correction
Review source: .ai/runs/ISSUE-27/STEP-10_REVIEW.md

Objetivo:
- Endereçar DVG-001 do STEP-10_REVIEW: casos 51–53 em tests/test_run_manifest.py usam igualdade exata com strings ASCII-folded ("avancar", "decisao") que divergem da tabela acentuada de next_steps da spec (ISSUE-27_SPEC.md linhas ~261–264).

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `.ai/runs/ISSUE-27/STEP-10_REVIEW.md`
- `tests/test_run_manifest.py`

Arquivos editáveis:
- `tests/test_run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`

Proibido:
- Implementar `build_run_manifest` ou alterar `generator/run_manifest.py`. Sem GREEN.
- Corrigir divergências não listadas. Adicionar casos novos.

Done quando:
- Casos 51–53 alinham next_steps ao texto exato (acentuado) da tabela da spec OU usam assert de substring/keyword, permitindo que GREEN emita o texto da spec.
- Suíte do arquivo continua RED por `build_run_manifest` ausente (ImportError).

Revisão:
- Apenas DVG-001 endereçada; sem GREEN; sem escopo novo; mantém RED.

---

### STEP-11 — GREEN build_run_manifest + derivações

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `build_run_manifest`, derivação de `pipeline_status` e `next_steps`. Fazer casos 36–55 passarem.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/workspace.py`
- `tests/test_run_manifest.py`

Arquivos editáveis:
- `generator/run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`
- `ruff check generator/run_manifest.py`

Proibido:
- Adicionar testes. Mutar inputs.

Done quando:
- Casos 36–55 passam; `ruff` limpo; nunca muta `run` nem `findings_by_artifact`.

Revisão:
- STATUS_MAP e tabela next_steps conforme spec; espelhamento correto.

---

### STEP-12 — REFACTOR helpers privados e imports

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Extrair helpers privados de `pipeline_status` e `next_steps`; garantir import de `VALID_STAGES`, `VALID_ARTIFACT_TYPES`, `VALID_OUTCOMES` de `generator/workspace.py` sem duplicação.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`
- `generator/workspace.py`
- `generator/run_manifest.py`

Arquivos editáveis:
- `generator/run_manifest.py`

Comandos permitidos:
- `pytest tests/test_run_manifest.py -q`
- `pytest tests/test_run_manifest_schema.py -q`
- `ruff check generator/run_manifest.py`

Proibido:
- Comportamento novo. API pública nova. Testes novos.

Done quando:
- Sem duplicação de constantes; helpers nomeados; testes continuam passando.

Revisão:
- Sem mudança de comportamento; imports de workspace presentes.

---

### STEP-13 — VALIDATION suíte completa

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar suíte completa e checagens finais.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/issues/ISSUE-27_SPEC.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-27/STEP-13_EXECUTION.md`

Comandos permitidos:
- `pytest tests/ -q`
- `ruff check generator/run_manifest.py`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- Corrigir falhas, alterar código ou testes.

Done quando:
- Suíte passa sem regressão (1247+ esperado: 1192 + 55); nenhum arquivo existente alterado fora do escopo.

Revisão:
- Resultados registrados; sem correção.

---

### STEP-14 — WRAP-UP

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Atualizar estado da issue e resumo final. Doc opcional.

Contexto permitido:
- `.ai/issues/ISSUE-27.md`
- `.ai/runs/ISSUE-27/STEP-13_EXECUTION.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-27/STEP-14_EXECUTION.md`
- `docs/BLIND_SOLVER_HARNESS.md`

Comandos permitidos:
- nenhum

Proibido:
- Alterar implementação ou testes.

Done quando:
- Resumo final registrado.

Revisão:
- Auto-approve (low-risk).

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
- STEP-00 orquestrado: 14 steps planejados (reading, baseline, 4 RED schema/semântico/build, 3 GREEN, refactor, validation, wrap-up). RED dividido para respeitar máx 10 casos/step.
- STEP-01 executado e auto-approved (low-risk, reading).
- STEP-02 executado e auto-approved (low-risk, baseline). Baseline 1192 passed, 3 skipped, 5 failed (symlink WinError 1314, pré-existentes).
- STEP-03 executado e aprovado pelo revisor (RED schema casos 1–10, ModuleNotFoundError confirmado).
- STEP-04 executado e aprovado pelo revisor (RED schema casos 11–20, 8 fixtures invalid/).
- STEP-05 executado e aprovado pelo revisor (GREEN schema + dataclasses + validate_run_manifest + manifest_to_dict, 21 passed).
- STEP-06 executado e aprovado pelo revisor (RED semântico casos 21–28 RM_001–RM_008, ImportError).
- STEP-07 executado e aprovado pelo revisor (RED semântico casos 29–35, ImportError).
- STEP-08 executado e aprovado pelo revisor (GREEN validate_run_manifest_semantics RM_001–RM_008, 15 passed).
- STEP-09 executado e aprovado pelo revisor (RED build casos 36–45, ImportError build_run_manifest).
- STEP-10 executado (RED build casos 46–55), reprovado pelo revisor (DVG-001 minor: next_steps casos 51–53 com igualdade exata folded). Criado STEP-10_FIX-01.
- STEP-10_FIX-01 executado e aprovado pelo revisor (casos 51–53 alinhados ao texto acentuado da spec, RED mantido). STEP-10 concluído.
- STEP-11 executado e aprovado pelo revisor (GREEN build_run_manifest + derivações, 35 passed, VALID_STAGES importado de workspace).
- STEP-12 executado e aprovado pelo revisor (refactor: constantes importadas de workspace sem duplicar, helpers privados, 35+21 passed).
- STEP-13 executado e aprovado pelo revisor (validation: 1248 passed, 5 symlink failed pré-existentes, sem regressão, nenhum arquivo existente alterado).
- STEP-14 executado e auto-approved (low-risk, wrap-up). ISSUE-27 concluída.
- STEP-01 executado; aguardando revisão.
- STEP-02 executado; aguardando revisão.
- STEP-03 executado; aguardando revisão.
- STEP-03 aprovado; aguardando orquestrador.
- STEP-04 executado; aguardando revisão.
- STEP-04 aprovado; aguardando orquestrador.
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado; aguardando orquestrador.
- STEP-06 executado; aguardando revisão.
- STEP-06 aprovado; aguardando orquestrador.
- STEP-07 executado; aguardando revisão.
- STEP-07 aprovado; aguardando orquestrador.
- STEP-08 executado; aguardando revisão.
- STEP-08 aprovado; aguardando orquestrador.
- STEP-09 executado; aguardando revisão.
- STEP-09 aprovado; aguardando orquestrador.
- STEP-10 executado; aguardando revisão.
- STEP-10 reprovado; aguardando orquestrador.
- STEP-10_FIX-01 executado; aguardando revisão.
- STEP-10_FIX-01 aprovado; aguardando orquestrador.
- STEP-11 executado; aguardando revisão.
- STEP-11 aprovado; aguardando orquestrador.
- STEP-12 executado; aguardando revisão.
- STEP-12 aprovado; aguardando orquestrador.
- STEP-13 executado; aguardando revisão.
- STEP-13 aprovado; aguardando orquestrador.
- STEP-14 executado; aguardando revisão.

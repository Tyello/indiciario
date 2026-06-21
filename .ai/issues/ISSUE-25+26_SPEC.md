# ISSUE-25+26_SPEC — Multiagent Workspace + Manual Orchestrator

## Identificação

- **Issues:** ISSUE-25 + ISSUE-26 (agrupadas em uma PR)
- **Título:** Multiagent Workspace + Manual Orchestrator
- **Fase:** G (Orquestração de runs)
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-workspace-manual-orchestrator`
- **Título sugerido da PR:** `feat: add multiagent workspace and manual orchestrator`
- **Commit sugerido:** `feat: add multiagent workspace and manual orchestrator`

---

## Decisão de agrupamento

ISSUE-25 (Workspace) e ISSUE-26 (Manual Orchestrator) são entregues juntas porque:

1. O Manual Orchestrator é definido como "orquestrar o workspace" — sem workspace
   não há superfície para o orchestrator operar.
2. O workspace expõe uma API Python (`WorkspaceLayout`, `WorkspaceState`,
   `ingest_artifact`) que o orchestrator consome diretamente; implementar um
   sem o outro deixaria a interface sem contrato verificável.
3. A superfície da PR é equivalente à ISSUE-19+20 e ISSUE-21+22: um schema +
   dois módulos + testes.
4. O agrupamento mantém a mesma PR pequena com escopo único e reversível.

---

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py` (RV_001–RV_008)
- ✅ ISSUE-18: `generator/blind_solve_run_record.py` + `schemas/blind_solve_run_record.schema.yaml`
- ✅ ISSUE-19+20: `generator/gate_evaluator.py` + `schemas/gate_evaluation.schema.yaml`
- ✅ ISSUE-21+22: `generator/narrative_reviewer.py` + `generator/evidence_reviewer.py` + `schemas/review_report.schema.yaml`

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia `.ai/skills/diagnose.md`.
7. Leia integralmente:
   - `generator/gate_evaluator.py` — padrão de dataclasses + builder
   - `generator/blind_solve_run_record.py` — padrão de validate + build
   - `generator/narrative_reviewer.py` — padrão de dataclasses compartilhadas
   - `schemas/gate_evaluation.schema.yaml` — padrão de schema YAML
   - `schemas/review_report.schema.yaml` — padrão de schema com `additionalProperties: false`
   - `schemas/blind_solve_run_record.schema.yaml` — padrão de `neutral_id`
   - `tests/test_gate_evaluator.py` — padrão de teste semântico
   - `tests/test_gate_evaluation_schema.py` — padrão de teste de schema
   - `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` (seções Fase G)
   - `.ai/issues/ISSUE-25+26.md` — issue de controle desta PR
8. Execute antes de alterar:
   ```bash
   pytest tests/ -q
   ```

---

## Objetivo

Criar a infraestrutura de **workspace por run** e o **Manual Orchestrator** que
organiza e rastreia uma execução multiagente completa sem banco de dados e sem
chamada automática a LLM.

### ISSUE-25 — Multiagent Workspace

O Workspace é um diretório padronizado por run de caso, que armazena:

- artefatos de entrada (bundle, manifest)
- outputs dos agentes (blind solver report, gate evaluation, review reports)
- log de ingestão com hashes
- estado da run (status, etapa atual, lineage dos artefatos)

O Workspace **não executa** nenhum agente. Ele organiza, valida ao ingerir e
rastreia o que aconteceu.

### ISSUE-26 — Manual Orchestrator

O Manual Orchestrator é o módulo que usa o Workspace para conduzir uma run
passo a passo, de forma determinística e offline:

- inicializa o workspace para um caso
- registra ingestão de outputs fornecidos manualmente
- verifica gates (critérios mínimos por etapa) antes de avançar
- registra decisões humanas de gate (approve/reject/rollback)
- produz um `RunState` consultável sem banco de dados

O Orchestrator **não** chama LLM, **não** executa agentes automaticamente e
**não** modifica artefatos ingeridos.

---

## Modelo conceitual

### Schema: `workspace_run.schema.yaml`

```yaml
schema_version: "1.0"
run_id: "aurora-run-20260620-001"         # neutral_id
case_ref: "examples/caso_canonico_intermediario.json"
created_at: "2026-06-20T10:00:00Z"
created_by: "orchestrator"

status: "in_progress"
# enum: initialized | in_progress | gate_blocked | done | rolled_back

current_stage: "blind_solve"
# enum: initialized | blind_solve | gate_evaluation | narrative_review |
#       evidence_review | complete

artifacts:
  - artifact_id: "bundle-aurora-001"       # neutral_id
    artifact_type: "blind_bundle"
    # enum: blind_bundle | blind_solver_report | run_record |
    #       gate_evaluation | narrative_review | evidence_review
    path: "workspace/aurora-run-001/artifacts/bundle-aurora-001/"
    sha256: "abc123..."
    ingested_at: "2026-06-20T10:05:00Z"
    stage: "blind_solve"
    # enum: mesmas que current_stage (exceto initialized/complete)
    visible_to: ["blind_solver"]
    # lista aberta; papéis: blind_solver | gate_evaluator |
    #                        narrative_reviewer | evidence_reviewer |
    #                        orchestrator | all

decisions:
  - decision_id: "dec-001"                 # neutral_id
    stage: "gate_evaluation"
    outcome: "approved"
    # enum: approved | rejected | rollback
    justification: "Conclusão esperada atingida com evidência suficiente."
    decided_at: "2026-06-20T11:00:00Z"
    decided_by: "human"
    rollback_to_stage: null                # string | null

notes: ""
```

---

## Campos obrigatórios do schema

### Nível raiz

| Campo | Tipo | Regra |
|---|---|---|
| `schema_version` | const `"1.0"` | Imutável |
| `run_id` | neutral_id | Único para esta run |
| `case_ref` | string ≥ 1 | Caminho do blueprint avaliado |
| `created_at` | date-time | ISO 8601 com timezone |
| `created_by` | string ≥ 1 | Quem inicializou |
| `status` | enum | `initialized` / `in_progress` / `gate_blocked` / `done` / `rolled_back` |
| `current_stage` | enum | ver enum de stages |
| `artifacts` | array | ≥ 0 itens |
| `decisions` | array | ≥ 0 itens |
| `notes` | string | pode ser vazio |

### `artifacts[]`

| Campo | Tipo | Regra |
|---|---|---|
| `artifact_id` | neutral_id | Único dentro da run |
| `artifact_type` | enum | ver enum de types |
| `path` | string ≥ 1 | Caminho relativo ao workspace raiz |
| `sha256` | string ≥ 1 | Hash do artefato no momento da ingestão |
| `ingested_at` | date-time | ISO 8601 com timezone |
| `stage` | enum | Etapa em que foi ingerido |
| `visible_to` | array de string | ≥ 1 item |

### `decisions[]`

| Campo | Tipo | Regra |
|---|---|---|
| `decision_id` | neutral_id | Único dentro da run |
| `stage` | enum | Etapa da decisão |
| `outcome` | enum | `approved` / `rejected` / `rollback` |
| `justification` | string ≥ 1 | Obrigatória |
| `decided_at` | date-time | ISO 8601 com timezone |
| `decided_by` | string ≥ 1 | Quem decidiu |
| `rollback_to_stage` | string ou null | Obrigatório quando `outcome: rollback` |

---

## Enums centrais

### `status`
`initialized` | `in_progress` | `gate_blocked` | `done` | `rolled_back`

### `current_stage` / `stage` (em artifacts e decisions)
`initialized` | `blind_solve` | `gate_evaluation` | `narrative_review` |
`evidence_review` | `complete`

> **Nota:** `initialized` e `complete` são válidos em `current_stage` mas
> **não** são válidos em `artifacts[].stage` (um artefato é sempre ingerido
> em uma etapa ativa). `complete` também não é válido em `decisions[].stage`.

### `artifact_type`
`blind_bundle` | `blind_solver_report` | `run_record` |
`gate_evaluation` | `narrative_review` | `evidence_review`

### `outcome` (em decisions)
`approved` | `rejected` | `rollback`

---

## Regras semânticas do Workspace (WS_*)

As regras WS_* são validadas por `validate_workspace_semantics`. Nunca acessam
o filesystem nem abrem artefatos; operam apenas sobre o dict da run.

| Código | Campo avaliado | Regra | Severidade |
|---|---|---|---|
| WS_001 | `decisions[].rollback_to_stage` | Decisão com `outcome: rollback` e `rollback_to_stage: null` | error |
| WS_002 | `decisions[].rollback_to_stage` | Decisão com `outcome != rollback` e `rollback_to_stage != null` | error |
| WS_003 | `artifacts[].artifact_id` | Dois artefatos com o mesmo `artifact_id` | error |
| WS_004 | `decisions[].decision_id` | Duas decisões com o mesmo `decision_id` | error |
| WS_005 | `artifacts[].stage` | Artefato com `stage: initialized` ou `stage: complete` | error |
| WS_006 | `status` + `decisions` | `status: done` sem nenhuma decisão `outcome: approved` | warning |
| WS_007 | `current_stage` + `status` | `status: rolled_back` e `current_stage` não é `initialized` | warning |
| WS_008 | `artifacts[].visible_to` | `visible_to` lista vazia | error |

**Lógica de resultado:**

- `valid: False` se qualquer erro WS_* disparar.
- `valid: True` se apenas warnings.
- Warnings são sempre registrados mesmo quando `valid: True`.

---

## Regras semânticas do Orchestrator (OR_*)

As regras OR_* são validadas por `validate_orchestrator_transition`. Verificam
se uma transição de etapa é permitida dado o estado atual.

| Código | Regra | Severidade |
|---|---|---|
| OR_001 | Transição pedida de etapa que não é a `current_stage` | error |
| OR_002 | Avançar para `gate_evaluation` sem artefato `run_record` ingerido | error |
| OR_003 | Avançar para `narrative_review` sem decisão `approved` em `gate_evaluation` | error |
| OR_004 | Avançar para `evidence_review` sem artefato `narrative_review` ingerido | error |
| OR_005 | Avançar para `complete` sem artefato `evidence_review` ingerido | error |
| OR_006 | Registrar decisão em `stage` que não está no histórico de stages transitados | warning |
| OR_007 | Ingerir artefato com `artifact_type` já presente para o mesmo `stage` | warning |
| OR_008 | Avançar de `gate_blocked` sem decisão explícita de rollback ou desbloqueio | error |

---

## API pública esperada

```python
# generator/workspace.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "1.0"

VALID_STAGES: tuple[str, ...] = (
    "initialized",
    "blind_solve",
    "gate_evaluation",
    "narrative_review",
    "evidence_review",
    "complete",
)

VALID_STATUSES: tuple[str, ...] = (
    "initialized",
    "in_progress",
    "gate_blocked",
    "done",
    "rolled_back",
)

VALID_ARTIFACT_TYPES: tuple[str, ...] = (
    "blind_bundle",
    "blind_solver_report",
    "run_record",
    "gate_evaluation",
    "narrative_review",
    "evidence_review",
)


@dataclass(frozen=True)
class WorkspaceArtifact:
    artifact_id: str
    artifact_type: str
    path: str
    sha256: str
    ingested_at: str
    stage: str
    visible_to: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceDecision:
    decision_id: str
    stage: str
    outcome: str            # "approved" | "rejected" | "rollback"
    justification: str
    decided_at: str
    decided_by: str
    rollback_to_stage: str | None


@dataclass(frozen=True)
class WorkspaceRun:
    run_id: str
    case_ref: str
    created_at: str
    created_by: str
    status: str
    current_stage: str
    artifacts: tuple[WorkspaceArtifact, ...]
    decisions: tuple[WorkspaceDecision, ...]
    notes: str


@dataclass(frozen=True)
class WorkspaceSemanticResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


def validate_workspace_run(run: Mapping[str, Any]) -> list[str]:
    """Validate structurally against workspace_run.schema.yaml.
    Returns list of error messages (empty = valid)."""
    ...


def validate_workspace_semantics(run: Mapping[str, Any]) -> WorkspaceSemanticResult:
    """Apply semantic rules WS_001–WS_008. Never touches the filesystem."""
    ...


def build_workspace_run(
    run_id: str,
    case_ref: str,
    created_by: str = "orchestrator",
    notes: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a minimal initialized workspace run dict (no artifacts, no decisions).
    Status = 'initialized', current_stage = 'initialized'."""
    ...


def run_to_dict(run: WorkspaceRun) -> dict[str, Any]:
    """Serialize WorkspaceRun to dict ready for validate_workspace_run."""
    ...
```

```python
# generator/manual_orchestrator.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping

from generator.workspace import (
    WorkspaceArtifact,
    WorkspaceDecision,
    WorkspaceRun,
    WorkspaceSemanticResult,
)


@dataclass(frozen=True)
class IngestRequest:
    run: Mapping[str, Any]
    artifact_id: str
    artifact_type: str
    path: str
    sha256: str
    stage: str
    visible_to: tuple[str, ...]
    ingested_at: str | None = None


@dataclass(frozen=True)
class TransitionRequest:
    run: Mapping[str, Any]
    from_stage: str
    to_stage: str


@dataclass(frozen=True)
class DecisionRequest:
    run: Mapping[str, Any]
    decision_id: str
    stage: str
    outcome: str            # "approved" | "rejected" | "rollback"
    justification: str
    decided_by: str
    rollback_to_stage: str | None = None
    decided_at: str | None = None


@dataclass(frozen=True)
class OrchestratorResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


@dataclass(frozen=True)
class TransitionResult:
    run: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


def ingest_artifact(request: IngestRequest) -> OrchestratorResult:
    """Add an artifact to the run state.
    Applies OR_007. Never mutates request.run. Returns new run dict."""
    ...


def record_decision(request: DecisionRequest) -> OrchestratorResult:
    """Record a gate decision in the run state.
    Applies OR_006. Transitions status to gate_blocked if outcome=rejected.
    Never mutates request.run. Returns new run dict."""
    ...


def transition_stage(request: TransitionRequest) -> TransitionResult:
    """Validate and apply a stage transition.
    Applies OR_001–OR_008. Never mutates request.run. Returns new run dict."""
    ...


def validate_orchestrator_transition(
    run: Mapping[str, Any],
    from_stage: str,
    to_stage: str,
) -> TransitionResult:
    """Apply OR_001–OR_008 rules for a proposed transition.
    Does not modify the run. Used for dry-run checks."""
    ...
```

`WorkspaceArtifact`, `WorkspaceDecision`, `WorkspaceRun`, `WorkspaceSemanticResult`
são definidos em `generator/workspace.py` e importados em
`generator/manual_orchestrator.py`. Não duplicar.

---

## Escopo permitido

Criar:
- `schemas/workspace_run.schema.yaml`
- `generator/workspace.py` — dataclasses compartilhadas, `validate_workspace_run`, `validate_workspace_semantics`, `build_workspace_run`, `run_to_dict`
- `generator/manual_orchestrator.py` — `ingest_artifact`, `record_decision`, `transition_stage`, `validate_orchestrator_transition`; importa dataclasses de `workspace.py`
- `tests/test_workspace_run_schema.py`
- `tests/test_workspace.py`
- `tests/test_manual_orchestrator.py`
- `tests/fixtures/workspace_run/valid/`
- `tests/fixtures/workspace_run/invalid/`

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — seção sobre Workspace e Orchestrator (opcional)

---

## Fora de escopo

**Não implementar:**
- Visual Reviewer (ISSUE-23 — só após ISSUE-28)
- Accessibility Reviewer (ISSUE-24 — só após ISSUE-28)
- Run Manifest consolidado (ISSUE-27)
- Execução automática de agentes
- CLI complexa ou interativa
- Leitura/hash real de arquivos do filesystem (usar sha256 fornecido pelo chamador)
- Banco de dados, serialização para disco, persistência automática
- Alteração de casos canônicos
- Alteração de `blind_solver_harness.py`, `gate_evaluator.py`,
  `blind_solve_run_record.py`, `narrative_reviewer.py`, `evidence_reviewer.py`
- LLM, internet, OCR
- Skills em `.ai/skills/`

---

## Testes obrigatórios

### `tests/test_workspace_run_schema.py` (20 casos)

Casos 1–10: fixtures válidas e variações

1. fixture `valid_initialized.yaml` passa (status: initialized, artifacts: [], decisions: [])
2. fixture `valid_in_progress_with_artifact.yaml` passa (1 artefato ingerido)
3. fixture `valid_gate_blocked.yaml` passa (status: gate_blocked, 1 decisão rejected)
4. fixture `valid_done.yaml` passa (status: done, 1 decisão approved)
5. `artifact_type: "run_record"` é válido
6. `artifact_type: "gate_evaluation"` é válido
7. `decisions[].outcome: "rollback"` com `rollback_to_stage` não nulo é válido
8. `visible_to: ["all"]` é válido
9. `current_stage: "complete"` é válido
10. `notes` vazio é válido

Casos 11–20: rejeições estruturais

11. `schema_version: "2.0"` falha
12. `status: "running"` falha (não é enum válido)
13. `current_stage: "review"` falha (não é enum válido)
14. `run_id` ausente falha
15. `case_ref` ausente falha
16. `artifact_type: "visual_review"` falha (não existe ainda)
17. `artifacts[].visible_to: []` falha (minItems: 1)
18. `decisions[].outcome: "pending"` falha
19. campo extra no topo falha (`additionalProperties: false`)
20. `decisions[].justification` ausente falha

### `tests/test_workspace.py` (30 casos)

Casos 21–28: regras WS_001–WS_008

21. decisão `outcome: rollback` com `rollback_to_stage: null` → WS_001 error
22. decisão `outcome: approved` com `rollback_to_stage: "blind_solve"` → WS_002 error
23. dois artefatos com mesmo `artifact_id` → WS_003 error
24. duas decisões com mesmo `decision_id` → WS_004 error
25. artefato com `stage: "initialized"` → WS_005 error
26. artefato com `stage: "complete"` → WS_005 error
27. `status: done` sem decisão `approved` → WS_006 warning (valid=True)
28. `status: rolled_back` com `current_stage: "blind_solve"` → WS_007 warning (valid=True)

Casos 29–36: `validate_workspace_semantics`

29. `visible_to: []` em artefato → WS_008 error (valid=False)
30. run sem erros semânticos → `valid: True`, `errors: ()`
31. run com WS_001 error → `valid: False`
32. run com apenas WS_006 warning → `valid: True`, `warnings` não vazio
33. múltiplos erros acumulados na mesma validação
34. warnings acumulados junto com valid=True
35. run vazia (artifacts: [], decisions: []) → válida semanticamente
36. dois erros diferentes em sequência (WS_003 + WS_004)

Casos 37–44: `build_workspace_run` e `validate_workspace_run`

37. `build_workspace_run` retorna dict com `status: initialized`
38. `build_workspace_run` retorna dict com `current_stage: initialized`
39. `build_workspace_run` retorna dict com `artifacts: []` e `decisions: []`
40. run construída por `build_workspace_run` passa `validate_workspace_run`
41. `validate_workspace_run` retorna lista vazia para run válida
42. `validate_workspace_run` retorna erros para run sem `run_id`
43. `run_to_dict` serializa `WorkspaceRun` com artifacts e decisions
44. `run_to_dict` + `validate_workspace_run` → round-trip sem perda

Casos 45–50: integração e edge cases

45. artefato com `stage: "blind_solve"` em run `current_stage: "gate_evaluation"` é estruturalmente válido (ingestão retroativa)
46. `visible_to: ["blind_solver", "orchestrator"]` é válido (múltiplos papéis)
47. `validate_workspace_run` + fixtures válidas passam todas
48. `validate_workspace_run` + fixtures inválidas rejeitam com erro
49. WS_005 dispara para `stage: initialized` E para `stage: complete` (dois casos separados)
50. `pytest tests/ -q` sem regressão (parcial — confirmado em STEP de validation)

### `tests/test_manual_orchestrator.py` (35 casos)

Casos 51–58: regras OR_001–OR_008

51. `validate_orchestrator_transition` de `blind_solve` para `gate_evaluation` sem `run_record` → OR_002 error
52. `validate_orchestrator_transition` de `gate_evaluation` para `narrative_review` sem decisão `approved` → OR_003 error
53. `validate_orchestrator_transition` de `narrative_review` para `evidence_review` sem artefato `narrative_review` → OR_004 error
54. `validate_orchestrator_transition` de `evidence_review` para `complete` sem artefato `evidence_review` → OR_005 error
55. `validate_orchestrator_transition` de `gate_blocked` para `narrative_review` sem decisão rollback ou desbloqueio → OR_008 error
56. `ingest_artifact` com `artifact_type` já presente no mesmo stage → OR_007 warning (result.valid=True)
57. `record_decision` com `stage` não no histórico transitado → OR_006 warning (result.valid=True)
58. OR_001: `transition_stage` com `from_stage` diferente do `current_stage` → error

Casos 59–68: `ingest_artifact`

59. `ingest_artifact` com run válida → artefato adicionado ao dict retornado
60. `ingest_artifact` atualiza `status` para `in_progress` se estava `initialized`
61. `ingest_artifact` não muta `request.run`
62. `ingest_artifact` gera `ingested_at` automaticamente se não fornecido
63. `ingest_artifact` com OR_007 → retorna valid=True (warning, não bloqueia)
64. run retornada por `ingest_artifact` passa `validate_workspace_run`
65. dois `ingest_artifact` sequenciais acumulam artefatos corretamente
66. `ingest_artifact` preserva `decisions` existentes no retorno
67. `ingest_artifact` preserva `current_stage` e `run_id` no retorno
68. `artifact_id` duplicado: OR_007 → warning, artefato NÃO adicionado de novo

Casos 69–76: `record_decision`

69. `record_decision` com `outcome: approved` → decisão adicionada ao dict
70. `record_decision` não muta `request.run`
71. `record_decision` com `outcome: rejected` → `status` muda para `gate_blocked`
72. `record_decision` com `outcome: approved` → `status` não muda para `gate_blocked`
73. `record_decision` com `outcome: rollback` → `status` muda para `rolled_back`
74. `record_decision` gera `decided_at` automaticamente se não fornecido
75. run retornada por `record_decision` passa `validate_workspace_run`
76. `record_decision` OR_006 warning não bloqueia (valid=True)

Casos 77–85: `transition_stage`

77. `transition_stage` de `initialized` para `blind_solve` → válida (sem pré-requisito de artefato)
78. `transition_stage` de `blind_solve` para `gate_evaluation` com `run_record` presente → válida
79. `transition_stage` de `gate_evaluation` para `narrative_review` com `approved` → válida
80. `transition_stage` de `narrative_review` para `evidence_review` com `narrative_review` artefato → válida
81. `transition_stage` de `evidence_review` para `complete` com `evidence_review` artefato → válida
82. `transition_stage` não muta `request.run`
83. `transition_stage` com `from_stage` errado → OR_001 error, valid=False
84. `transition_stage` atualiza `current_stage` no dict retornado quando válida
85. `pytest tests/ -q` sem regressão (1104+ testes)

---

## Fixtures necessárias

### `tests/fixtures/workspace_run/valid/`

- `valid_initialized.yaml` — status: initialized, artifacts: [], decisions: [], current_stage: initialized
- `valid_in_progress_with_artifact.yaml` — status: in_progress, 1 artefato blind_bundle em blind_solve
- `valid_gate_blocked.yaml` — status: gate_blocked, 1 artefato run_record, 1 decisão rejected
- `valid_done.yaml` — status: done, artefatos das 4 etapas, 1 decisão approved

### `tests/fixtures/workspace_run/invalid/`

- `invalid_status.yaml` — status: "running"
- `invalid_stage.yaml` — current_stage: "review"
- `missing_run_id.yaml` — run_id ausente
- `missing_case_ref.yaml` — case_ref ausente
- `invalid_artifact_type.yaml` — artifact_type: "visual_review"
- `invalid_outcome.yaml` — decisions[0].outcome: "pending"
- `extra_top_field.yaml` — campo extra no topo
- `missing_justification.yaml` — decisions[0].justification ausente

---

## Anti-regras

A implementação NÃO DEVE:

- Chamar LLM ou internet
- Ler, gravar ou hashear arquivos reais do filesystem (sha256 é fornecido pelo chamador)
- Modificar o blueprint ou qualquer artefato existente
- Persistir estado em disco automaticamente
- Duplicar dataclasses entre `workspace.py` e `manual_orchestrator.py`
- Criar skills em `.ai/skills/`
- Alterar casos canônicos
- Alterar `blind_solver_harness.py`, `gate_evaluator.py`, `blind_solve_run_record.py`, `narrative_reviewer.py`, `evidence_reviewer.py`
- Lançar exceção para run com `artifacts: []` ou `decisions: []` (tratar como listas vazias normais)
- Criar CLI interativa ou com argparse
- Usar banco de dados, SQLite, arquivos de configuração externos

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/workspace_run.schema.yaml`
2. existir `generator/workspace.py`
3. existir `generator/manual_orchestrator.py`
4. `WorkspaceArtifact`, `WorkspaceDecision`, `WorkspaceRun`, `WorkspaceSemanticResult` definidos em `workspace.py`
5. `manual_orchestrator.py` importa dataclasses de `workspace.py` (sem duplicação)
6. existir função pública `validate_workspace_run(run) -> list[str]`
7. existir função pública `validate_workspace_semantics(run) -> WorkspaceSemanticResult`
8. existir função pública `build_workspace_run(run_id, case_ref, ...) -> dict`
9. existir função pública `run_to_dict(run: WorkspaceRun) -> dict`
10. existir função pública `ingest_artifact(request: IngestRequest) -> OrchestratorResult`
11. existir função pública `record_decision(request: DecisionRequest) -> OrchestratorResult`
12. existir função pública `transition_stage(request: TransitionRequest) -> TransitionResult`
13. existir função pública `validate_orchestrator_transition(run, from_stage, to_stage) -> TransitionResult`
14. schema ter `additionalProperties: false` no topo e em `artifacts[]` e em `decisions[]`
15. `status` ter enum `initialized | in_progress | gate_blocked | done | rolled_back`
16. `current_stage` e `artifacts[].stage` ter enum `initialized | blind_solve | gate_evaluation | narrative_review | evidence_review | complete`
17. `artifact_type` ter enum `blind_bundle | blind_solver_report | run_record | gate_evaluation | narrative_review | evidence_review`
18. `decisions[].outcome` ter enum `approved | rejected | rollback`
19. regras WS_001–WS_008 implementadas
20. regras OR_001–OR_008 implementadas
21. `ingest_artifact` e `record_decision` nunca mutam o dict de entrada
22. `transition_stage` nunca muta o dict de entrada
23. fixtures válidas passam no schema
24. fixtures inválidas falham com mensagem correta
25. todos os 20 testes de `test_workspace_run_schema.py` passam
26. todos os 30 testes de `test_workspace.py` passam
27. todos os 35 testes de `test_manual_orchestrator.py` passam
28. nenhum arquivo existente alterado (exceto doc opcional)
29. `pytest tests/ -q` passa sem regressão (1104+ testes)
30. `ruff check generator/workspace.py generator/manual_orchestrator.py` passa
31. nenhum LLM/internet usado
32. nenhum caso canônico alterado
33. nenhuma skill criada em `.ai/skills/`

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Confirmar que falham por
`ImportError` ou `ModuleNotFoundError` em `generator.workspace` /
`generator.manual_orchestrator`, ou `FileNotFoundError` no schema.

**GREEN:** schema → `validate_workspace_run` + dataclasses → `validate_workspace_semantics`
→ `build_workspace_run` + `run_to_dict` → `ingest_artifact` → `record_decision`
→ `transition_stage` + `validate_orchestrator_transition`.

**REFACTOR:** extrair helpers de lookup de artefatos e decisões por tipo/stage
usados em múltiplas funções; garantir que nenhuma regra OR_* duplique lógica
de WS_*.

---

## Validação final

```bash
ruff check generator/workspace.py generator/manual_orchestrator.py

pytest tests/test_workspace_run_schema.py -q
pytest tests/test_workspace.py -q
pytest tests/test_manual_orchestrator.py -q

pytest tests/test_narrative_reviewer.py -q
pytest tests/test_evidence_reviewer.py -q
pytest tests/test_gate_evaluator.py -q
pytest tests/test_gate_evaluation_schema.py -q
pytest tests/test_blind_solve_run_record.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- fixture `valid_initialized.yaml` passa no schema
- `build_workspace_run` + `validate_workspace_run` → round-trip limpo
- `ingest_artifact` não muta o dict de entrada (testar com `copy.deepcopy`)
- `validate_workspace_semantics` detecta WS_001–WS_008 corretamente
- `validate_orchestrator_transition` detecta OR_001–OR_008 corretamente
- nenhum arquivo existente alterado (exceto doc opcional)
- nenhum caso canônico alterado
- `pytest tests/ -q` passa sem regressão (1104+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, enums)
- regras WS_001–WS_008 implementadas (breve descrição)
- regras OR_001–OR_008 implementadas (breve descrição)
- fixtures criadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum LLM/internet foi usado
- confirmação de que nenhuma skill foi criada
- próxima PR recomendada: ISSUE-27 — Run Manifest / Run Summary

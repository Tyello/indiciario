# ISSUE-27_SPEC — Run Manifest / Run Summary

## Identificação

- **Issue:** ISSUE-27
- **Título:** Run Manifest / Run Summary
- **Fase:** G (Orquestração de runs)
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-run-manifest`
- **Título sugerido da PR:** `feat: add run manifest`
- **Commit sugerido:** `feat: add run manifest`

---

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py` (RV_001–RV_008)
- ✅ ISSUE-18: `generator/blind_solve_run_record.py` + `schemas/blind_solve_run_record.schema.yaml`
- ✅ ISSUE-19+20: `generator/gate_evaluator.py` + `schemas/gate_evaluation.schema.yaml`
- ✅ ISSUE-21+22: `generator/narrative_reviewer.py` + `generator/evidence_reviewer.py` + `schemas/review_report.schema.yaml`
- ✅ ISSUE-25+26: `generator/workspace.py` + `generator/manual_orchestrator.py` + `schemas/workspace_run.schema.yaml`

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia integralmente:
   - `generator/workspace.py` — API, dataclasses, enums (VALID_STAGES, VALID_STATUSES, VALID_ARTIFACT_TYPES)
   - `generator/manual_orchestrator.py` — funções públicas e dataclasses de request/result
   - `schemas/workspace_run.schema.yaml` — estrutura do WorkspaceRun que o manifest consolida
   - `schemas/gate_evaluation.schema.yaml` — padrão de schema com `$defs`
   - `schemas/review_report.schema.yaml` — padrão de schema sem `$defs`
   - `tests/test_workspace.py` — padrão de teste semântico com `_run()` helper
   - `tests/test_workspace_run_schema.py` — padrão de teste de schema com fixtures
   - `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` (seção ISSUE-27)
   - `.ai/issues/ISSUE-27.md`
7. Execute antes de alterar:
   ```bash
   pytest tests/ -q
   ```

---

## Objetivo

Criar o **Run Manifest** — documento consolidado que captura tudo que aconteceu em uma run multiagente completa: quais bundles foram usados, quais agentes agiram, quais outputs foram produzidos, quais findings foram registrados, quais decisões de gate foram tomadas e quais próximos passos são recomendados.

O Run Manifest é um **artefato de saída imutável**: gerado a partir de um `WorkspaceRun` consolidado, nunca modificado depois de criado. Ele serve como registro rastreável de uma run para auditoria, comparação entre runs e insumo para ISSUE-28 (Aurora no pipeline real).

O Run Manifest **não executa** nenhum agente, **não modifica** o workspace e **não acessa** o filesystem além de ler os schemas necessários para validação.

---

## Modelo conceitual

### `run_manifest.schema.yaml`

```yaml
schema_version: "1.0"
manifest_id: "MANIFEST-AURORA-20260620-001"    # neutral_id
run_id: "RUN-AURORA-20260620-001"              # referência ao WorkspaceRun
case_ref: "examples/caso_canonico_intermediario.json"
generated_at: "2026-06-20T12:00:00Z"
generated_by: "orchestrator"

pipeline_status: "complete"
# enum: complete | incomplete | blocked | rolled_back
# derivado de WorkspaceRun.status:
#   done        → complete
#   gate_blocked → blocked
#   rolled_back  → rolled_back
#   initialized/in_progress → incomplete

stages_completed:
  - "blind_solve"
  - "gate_evaluation"
  - "narrative_review"
  - "evidence_review"
# lista de stages que têm ao menos um artefato ingerido
# ordem: a ordem de VALID_STAGES (exceto initialized/complete)

artifacts_summary:
  - artifact_id: "BUNDLE-AURORA-001"
    artifact_type: "blind_bundle"
    stage: "blind_solve"
    sha256: "abc123..."

decisions_summary:
  - decision_id: "DEC-001"
    stage: "gate_evaluation"
    outcome: "approved"
    decided_by: "human"
    decided_at: "2026-06-20T11:00:00Z"

findings:
  # findings consolidados de TODOS os review reports ingeridos como artefatos
  # narrative_review e evidence_review
  - source_artifact_id: "NR-AURORA-001"
    source_type: "narrative_review"
    code: "NR_003"
    severity: "major"
    field: "personagens"
    message: "Nenhum personagem tem papel suspeito além do executor."

gate_outcome:
  # resultado do gate_evaluation (se existir decisão de gate)
  decision_id: "DEC-001"
  outcome: "approved"
  justification: "Conclusão esperada atingida."

next_steps:
  # lista de recomendações textuais derivadas do estado da run
  # geradas deterministicamente; não requerem LLM
  - "Pipeline completo. Pronto para ISSUE-28 (Aurora no pipeline real)."

notes: ""
```

---

## Campos obrigatórios do schema

### Nível raiz

| Campo | Tipo | Regra |
|---|---|---|
| `schema_version` | const `"1.0"` | Imutável |
| `manifest_id` | neutral_id | Único para este manifest |
| `run_id` | neutral_id | ID do WorkspaceRun de origem |
| `case_ref` | string ≥ 1 | Caminho do blueprint |
| `generated_at` | date-time | ISO 8601 com timezone |
| `generated_by` | string ≥ 1 | Quem gerou |
| `pipeline_status` | enum | `complete` / `incomplete` / `blocked` / `rolled_back` |
| `stages_completed` | array de string | ≥ 0 itens; cada item é stage válido |
| `artifacts_summary` | array | ≥ 0 itens |
| `decisions_summary` | array | ≥ 0 itens |
| `findings` | array | ≥ 0 itens |
| `gate_outcome` | object ou null | null se sem decisão de gate |
| `next_steps` | array de string | ≥ 0 itens |
| `notes` | string | pode ser vazio |

### `artifacts_summary[]`

| Campo | Tipo | Regra |
|---|---|---|
| `artifact_id` | neutral_id | Ref ao artefato no workspace |
| `artifact_type` | enum | mesmo enum de `workspace_run` |
| `stage` | enum | mesmo enum de `artifacts[].stage` em workspace_run |
| `sha256` | string ≥ 1 | Hash do artefato |

### `decisions_summary[]`

| Campo | Tipo | Regra |
|---|---|---|
| `decision_id` | neutral_id | Ref à decisão no workspace |
| `stage` | enum | mesmo enum de `decisions[].stage` em workspace_run |
| `outcome` | enum | `approved` / `rejected` / `rollback` |
| `decided_by` | string ≥ 1 | Quem decidiu |
| `decided_at` | date-time | ISO 8601 com timezone |

### `findings[]`

| Campo | Tipo | Regra |
|---|---|---|
| `source_artifact_id` | string ≥ 1 | ID do artefato de origem (review report) |
| `source_type` | enum | `narrative_review` / `evidence_review` |
| `code` | string ≥ 1 | Código da regra: `NR_*` ou `ER_*` |
| `severity` | enum | `critical` / `major` / `minor` / `info` |
| `field` | string | Pode ser vazio |
| `message` | string ≥ 1 | Descrição do problema |

### `gate_outcome` (quando não null)

| Campo | Tipo | Regra |
|---|---|---|
| `decision_id` | neutral_id | Ref à decisão de gate |
| `outcome` | enum | `approved` / `rejected` / `rollback` |
| `justification` | string ≥ 1 | Texto da justificativa |

---

## Enums centrais

### `pipeline_status`
`complete` | `incomplete` | `blocked` | `rolled_back`

### `stages_completed[]` (valores válidos)
`blind_solve` | `gate_evaluation` | `narrative_review` | `evidence_review`

### `artifacts_summary[].artifact_type`
`blind_bundle` | `blind_solver_report` | `run_record` |
`gate_evaluation` | `narrative_review` | `evidence_review`

### `artifacts_summary[].stage` e `decisions_summary[].stage`
`blind_solve` | `gate_evaluation` | `narrative_review` | `evidence_review`

### `decisions_summary[].outcome` e `gate_outcome.outcome`
`approved` | `rejected` | `rollback`

### `findings[].source_type`
`narrative_review` | `evidence_review`

### `findings[].severity`
`critical` | `major` | `minor` | `info`

---

## Regras semânticas do Run Manifest (RM_*)

Aplicadas por `validate_run_manifest_semantics`. Nunca tocam o filesystem.

| Código | Campo avaliado | Regra | Severidade |
|---|---|---|---|
| RM_001 | `run_id` + `artifacts_summary[].artifact_id` | `manifest_id` duplica `run_id` (mesmo valor) | error |
| RM_002 | `stages_completed` + `artifacts_summary` | Stage em `stages_completed` sem artefato correspondente em `artifacts_summary` | error |
| RM_003 | `gate_outcome` + `decisions_summary` | `gate_outcome.decision_id` não encontrado em `decisions_summary` | error |
| RM_004 | `pipeline_status` + `stages_completed` | `pipeline_status: complete` sem todos os 4 stages em `stages_completed` | error |
| RM_005 | `findings[].source_artifact_id` + `artifacts_summary` | Finding referencia `source_artifact_id` ausente de `artifacts_summary` | error |
| RM_006 | `decisions_summary` + `gate_outcome` | Múltiplas decisões de `gate_evaluation` mas `gate_outcome` referencia apenas uma — warning se houver mais de uma decisão em `gate_evaluation` | warning |
| RM_007 | `pipeline_status` + `decisions_summary` | `pipeline_status: blocked` sem nenhuma decisão `rejected` em `decisions_summary` | warning |
| RM_008 | `next_steps` | `next_steps` vazio quando `pipeline_status` não é `complete` | warning |

**Lógica de resultado:**
- `valid: False` se qualquer error disparar.
- `valid: True` se apenas warnings.
- Warnings sempre registrados.

---

## Lógica de derivação do `pipeline_status`

Derivado deterministicamente de `WorkspaceRun.status`:

```python
STATUS_MAP = {
    "done": "complete",
    "gate_blocked": "blocked",
    "rolled_back": "rolled_back",
    "initialized": "incomplete",
    "in_progress": "incomplete",
}
```

---

## Lógica de derivação de `next_steps`

Gerado deterministicamente a partir de `pipeline_status` e `stages_completed`:

| Condição | next_steps gerado |
|---|---|
| `pipeline_status: complete` | `["Pipeline completo. Revisar findings e prosseguir para ISSUE-28."]` |
| `pipeline_status: blocked` | `["Gate bloqueado. Revisar gate_outcome e registrar decisão de rollback ou desbloqueio."]` |
| `pipeline_status: rolled_back` | `["Run revertida. Reiniciar a partir do stage de rollback."]` |
| `pipeline_status: incomplete` + sem `blind_solve` | `["Ingerir blind_solver_report para avançar para gate_evaluation."]` |
| `pipeline_status: incomplete` + sem `gate_evaluation` | `["Ingerir gate_evaluation para avançar para narrative_review."]` |
| `pipeline_status: incomplete` + sem `narrative_review` | `["Ingerir narrative_review para avançar para evidence_review."]` |
| `pipeline_status: incomplete` + sem `evidence_review` | `["Ingerir evidence_review para completar a run."]` |

---

## API pública esperada

```python
# generator/run_manifest.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ManifestFinding:
    source_artifact_id: str
    source_type: str       # "narrative_review" | "evidence_review"
    code: str
    severity: str          # "critical" | "major" | "minor" | "info"
    field: str
    message: str


@dataclass(frozen=True)
class ManifestGateOutcome:
    decision_id: str
    outcome: str           # "approved" | "rejected" | "rollback"
    justification: str


@dataclass(frozen=True)
class ManifestArtifactSummary:
    artifact_id: str
    artifact_type: str
    stage: str
    sha256: str


@dataclass(frozen=True)
class ManifestDecisionSummary:
    decision_id: str
    stage: str
    outcome: str
    decided_by: str
    decided_at: str


@dataclass(frozen=True)
class RunManifest:
    manifest_id: str
    run_id: str
    case_ref: str
    generated_at: str
    generated_by: str
    pipeline_status: str
    stages_completed: tuple[str, ...]
    artifacts_summary: tuple[ManifestArtifactSummary, ...]
    decisions_summary: tuple[ManifestDecisionSummary, ...]
    findings: tuple[ManifestFinding, ...]
    gate_outcome: ManifestGateOutcome | None
    next_steps: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class ManifestSemanticResult:
    manifest: dict[str, Any]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    valid: bool


def validate_run_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Validate structurally against run_manifest.schema.yaml.
    Returns list of error messages (empty = valid)."""
    ...


def validate_run_manifest_semantics(
    manifest: Mapping[str, Any],
) -> ManifestSemanticResult:
    """Apply semantic rules RM_001–RM_008. Never touches filesystem."""
    ...


def build_run_manifest(
    run: Mapping[str, Any],
    manifest_id: str,
    findings_by_artifact: Mapping[str, list[Mapping[str, Any]]] | None = None,
    generated_by: str = "orchestrator",
    notes: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a run manifest dict from a WorkspaceRun dict.

    ``findings_by_artifact`` maps artifact_id → list of finding dicts
    (each with keys: code, severity, field, message). The source_type is
    derived from the artifact's artifact_type in the run.
    Never mutates inputs.
    """
    ...


def manifest_to_dict(manifest: RunManifest) -> dict[str, Any]:
    """Serialize RunManifest to dict ready for validate_run_manifest."""
    ...
```

Todos os dataclasses e funções públicas são definidos em `generator/run_manifest.py`. Não há módulo auxiliar separado nesta issue.

---

## Escopo permitido

Criar:
- `schemas/run_manifest.schema.yaml`
- `generator/run_manifest.py` — dataclasses, `validate_run_manifest`, `validate_run_manifest_semantics`, `build_run_manifest`, `manifest_to_dict`
- `tests/test_run_manifest_schema.py`
- `tests/test_run_manifest.py`
- `tests/fixtures/run_manifest/valid/`
- `tests/fixtures/run_manifest/invalid/`

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — seção sobre Run Manifest (opcional)

---

## Fora de escopo

**Não implementar:**
- Leitura de arquivos de review report do disco (findings vêm via `findings_by_artifact`)
- CLI interativa ou com argparse
- Alteração de `workspace.py`, `manual_orchestrator.py` ou qualquer módulo existente
- Alteração de casos canônicos
- Visual Reviewer (ISSUE-23), Accessibility Reviewer (ISSUE-24)
- LLM, internet, banco de dados
- Skills em `.ai/skills/`
- ISSUE-28 (Aurora no pipeline real) — só após esta PR mergeada

---

## Testes obrigatórios

### `tests/test_run_manifest_schema.py` (20 casos)

Casos 1–10: fixtures válidas e variações

1. fixture `valid_complete.yaml` passa (pipeline_status: complete, 4 stages)
2. fixture `valid_incomplete.yaml` passa (pipeline_status: incomplete, 1 stage)
3. fixture `valid_blocked.yaml` passa (pipeline_status: blocked, gate_outcome com rejected)
4. fixture `valid_no_findings.yaml` passa (findings: [], gate_outcome: null)
5. `pipeline_status: rolled_back` é válido
6. `findings[].severity: "info"` é válido
7. `findings[].field: ""` é válido (campo pode ser vazio)
8. `gate_outcome: null` é válido
9. `next_steps: []` é válido
10. `notes: ""` é válido

Casos 11–20: rejeições estruturais

11. `schema_version: "2.0"` falha
12. `pipeline_status: "running"` falha (não é enum válido)
13. `manifest_id` ausente falha
14. `run_id` ausente falha
15. `findings[].source_type: "visual_review"` falha
16. `findings[].severity: "warning"` falha
17. `artifacts_summary[].artifact_type: "visual_review"` falha
18. `decisions_summary[].outcome: "pending"` falha
19. campo extra no topo falha (`additionalProperties: false`)
20. `gate_outcome` com `decision_id` ausente falha

### `tests/test_run_manifest.py` (35 casos)

Casos 21–28: regras RM_001–RM_008

21. `manifest_id == run_id` → RM_001 error
22. stage em `stages_completed` sem artefato correspondente → RM_002 error
23. `gate_outcome.decision_id` ausente de `decisions_summary` → RM_003 error
24. `pipeline_status: complete` sem todos os 4 stages → RM_004 error
25. finding com `source_artifact_id` ausente de `artifacts_summary` → RM_005 error
26. múltiplas decisões em `gate_evaluation` → RM_006 warning (valid=True)
27. `pipeline_status: blocked` sem decisão `rejected` → RM_007 warning (valid=True)
28. `pipeline_status: incomplete` + `next_steps: []` → RM_008 warning (valid=True)

Casos 29–36: `validate_run_manifest_semantics`

29. manifest sem erros → `valid: True`, `errors: ()`
30. manifest com RM_001 → `valid: False`
31. manifest com apenas RM_006 warning → `valid: True`, `warnings` não vazio
32. múltiplos errors acumulados (RM_002 + RM_005)
33. manifest vazio de findings e decisions → semanticamente válido
34. warnings e valid=True juntos (RM_007 + RM_008)
35. `validate_run_manifest_semantics` não muta o dict de entrada

Casos 36–45: `build_run_manifest`

36. `build_run_manifest` de run `status: done` → `pipeline_status: complete`
37. `build_run_manifest` de run `status: in_progress` → `pipeline_status: incomplete`
38. `build_run_manifest` de run `status: gate_blocked` → `pipeline_status: blocked`
39. `build_run_manifest` de run `status: rolled_back` → `pipeline_status: rolled_back`
40. `stages_completed` contém só stages com artefatos ingeridos
41. `stages_completed` respeita a ordem de `VALID_STAGES`
42. `artifacts_summary` espelha artefatos do workspace
43. `decisions_summary` espelha decisões do workspace
44. `gate_outcome` preenchido quando existe decisão em `gate_evaluation`
45. `gate_outcome: null` quando sem decisão em `gate_evaluation`

Casos 46–55: `build_run_manifest` — findings e next_steps

46. `findings_by_artifact` vazio → `findings: []`
47. findings de artefato `narrative_review` → `source_type: narrative_review`
48. findings de artefato `evidence_review` → `source_type: evidence_review`
49. `build_run_manifest` não muta `run` nem `findings_by_artifact`
50. run completa sem findings → `next_steps` contém mensagem de pipeline completo
51. run incompleta sem `blind_solve` → `next_steps` contém mensagem de blind_solve
52. run incompleta sem `gate_evaluation` → `next_steps` contém mensagem de gate_evaluation
53. run bloqueada → `next_steps` contém mensagem de gate bloqueado
54. manifest gerado por `build_run_manifest` passa `validate_run_manifest`
55. `manifest_to_dict` + `validate_run_manifest` → round-trip sem perda

---

## Fixtures necessárias

### `tests/fixtures/run_manifest/valid/`

- `valid_complete.yaml` — pipeline_status: complete, 4 stages, findings com NR_*/ER_*, gate_outcome approved, next_steps
- `valid_incomplete.yaml` — pipeline_status: incomplete, 1 stage (blind_solve), findings: [], gate_outcome: null
- `valid_blocked.yaml` — pipeline_status: blocked, gate_outcome rejected, next_steps
- `valid_no_findings.yaml` — pipeline_status: complete, findings: [], gate_outcome: null, next_steps: []

### `tests/fixtures/run_manifest/invalid/`

- `invalid_pipeline_status.yaml` — pipeline_status: "running"
- `missing_manifest_id.yaml` — manifest_id ausente
- `missing_run_id.yaml` — run_id ausente
- `invalid_source_type.yaml` — findings[0].source_type: "visual_review"
- `invalid_severity.yaml` — findings[0].severity: "warning"
- `invalid_outcome.yaml` — decisions_summary[0].outcome: "pending"
- `extra_top_field.yaml` — campo extra no topo
- `gate_outcome_missing_decision_id.yaml` — gate_outcome sem decision_id

---

## Anti-regras

A implementação NÃO DEVE:

- Chamar LLM ou internet
- Ler arquivos de review report do disco (findings chegam via parâmetro)
- Modificar `workspace.py`, `manual_orchestrator.py` ou qualquer arquivo existente
- Criar uma CLI ou script interativo
- Duplicar enums ou constantes de `workspace.py` — importar `VALID_STAGES`, `VALID_ARTIFACT_TYPES` e `VALID_OUTCOMES` diretamente
- Criar skills em `.ai/skills/`
- Alterar casos canônicos
- Lançar exceção para run com `artifacts: []` ou `decisions: []`

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/run_manifest.schema.yaml`
2. existir `generator/run_manifest.py`
3. `ManifestFinding`, `ManifestGateOutcome`, `ManifestArtifactSummary`, `ManifestDecisionSummary`, `RunManifest`, `ManifestSemanticResult` definidos em `run_manifest.py`
4. existir função pública `validate_run_manifest(manifest) -> list[str]`
5. existir função pública `validate_run_manifest_semantics(manifest) -> ManifestSemanticResult`
6. existir função pública `build_run_manifest(run, manifest_id, ...) -> dict`
7. existir função pública `manifest_to_dict(manifest: RunManifest) -> dict`
8. schema ter `additionalProperties: false` no topo e em `artifacts_summary[]`, `decisions_summary[]`, `findings[]` e `gate_outcome`
9. `pipeline_status` ter enum `complete | incomplete | blocked | rolled_back`
10. `findings[].source_type` ter enum `narrative_review | evidence_review`
11. `findings[].severity` ter enum `critical | major | minor | info`
12. `gate_outcome` ser nullable (`type: [object, 'null']`)
13. regras RM_001–RM_008 implementadas
14. lógica de `pipeline_status` derivada deterministicamente de `WorkspaceRun.status`
15. lógica de `next_steps` derivada deterministicamente de `pipeline_status` + `stages_completed`
16. `build_run_manifest` nunca muta inputs
17. `validate_run_manifest_semantics` nunca muta input
18. `VALID_STAGES`, `VALID_ARTIFACT_TYPES`, `VALID_OUTCOMES` importados de `workspace.py` (sem duplicar)
19. fixtures válidas passam no schema
20. fixtures inválidas falham com mensagem correta
21. todos os 20 testes de `test_run_manifest_schema.py` passam
22. todos os 35 testes de `test_run_manifest.py` passam
23. nenhum arquivo existente alterado (exceto doc opcional)
24. `pytest tests/ -q` passa sem regressão (1192+ testes)
25. `ruff check generator/run_manifest.py` passa
26. nenhum LLM/internet usado
27. nenhum caso canônico alterado
28. nenhuma skill criada em `.ai/skills/`

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Confirmar que falham por
`ImportError` em `generator.run_manifest` ou `FileNotFoundError` no schema.

**GREEN:** schema → dataclasses + `validate_run_manifest` → `validate_run_manifest_semantics`
(RM_001–RM_008) → `build_run_manifest` + `manifest_to_dict`.

**REFACTOR:** extrair helpers de derivação de `pipeline_status` e `next_steps`
como funções privadas nomeadas; garantir que importações de `workspace.py`
substituam qualquer duplicação de constantes.

---

## Validação final

```bash
ruff check generator/run_manifest.py

pytest tests/test_run_manifest_schema.py -q
pytest tests/test_run_manifest.py -q

pytest tests/test_workspace.py -q
pytest tests/test_manual_orchestrator.py -q
pytest tests/test_narrative_reviewer.py -q
pytest tests/test_evidence_reviewer.py -q
pytest tests/test_gate_evaluator.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- fixture `valid_complete.yaml` passa no schema
- `build_run_manifest` de run `status: done` → `pipeline_status: complete` + 4 stages
- `validate_run_manifest_semantics` detecta RM_001–RM_008 corretamente
- `build_run_manifest` + `validate_run_manifest` → round-trip limpo
- nenhum arquivo existente alterado
- `pytest tests/ -q` passa sem regressão (1192+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, enums)
- regras RM_001–RM_008 implementadas (breve descrição)
- lógica de `pipeline_status` e `next_steps`
- fixtures criadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum LLM/internet foi usado
- confirmação de que nenhuma skill foi criada
- próxima PR recomendada: ISSUE-28 — Rodar pipeline no caso Hotel Aurora

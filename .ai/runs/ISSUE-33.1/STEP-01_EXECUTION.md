# ISSUE-33.1 — Conclusion Judge — STEP-01 Report

**Execution Date**: 2026-07-09  
**Executor**: Haiku (spec-executor)  
**Status**: COMPLETED

---

## 1. ExpectedConclusion Dataclass (gate_evaluator.py)

### Location
`generator/gate_evaluator.py`, lines 42–50

### Exact Signature
```python
@dataclass(frozen=True)
class ExpectedConclusion:
    """A single expected conclusion the author wanted the solver to reach."""

    id: str
    description: str
    required: bool
    met: bool
    evidence: str
```

### Evidence
- **id**: string identifier (e.g., "culpado", "metodo", "motivo")
- **description**: narrative description of the expected conclusion
- **required**: boolean flag; when True, failing this conclusion blocks gate approval (GE_004)
- **met**: boolean flag; `true` when the solver's report satisfies this conclusion
- **evidence**: string containing the evidentiary basis for the conclusion

---

## 2. build_gate_evaluation Function & GE_004 Rule

### Location
`generator/gate_evaluator.py`, lines 238–286

### Exact Signature
```python
def build_gate_evaluation(request: GateEvaluationRequest, ...) -> dict[str, Any]: ...
```

### Parameters
- `request: GateEvaluationRequest` — input dataclass containing:
  - `run_record: Mapping[str, Any]` — frozen blind solve run record
  - `private_solution_ref: str` — reference to author's solution
  - `evaluator_id: str` — who evaluated
  - `evaluation_id: str` — unique evaluation ID
  - `created_by: str` — default "orchestrator"
  - `created_at: str | None` — ISO timestamp; generated if None

### Return Type
`dict[str, Any]` — serialized gate evaluation matching `schemas/gate_evaluation.schema.yaml`

### GE_004 Rule (lines 139–148)

**Condition**: `decision == "approved"` AND any `ExpectedConclusion` with `required=true` has `met=false`

**Effect**: Blocante error — prevents approved decision when a required conclusion is not met

**Code**:
```python
# GE_004/GE_005: approved decision requires every required conclusion met.
has_unmet_required = any(
    item.get("required") is True and item.get("met") is False
    for item in expected_conclusions
)
if decision == "approved" and has_unmet_required:
    errors.append(
        "GE_004: decision='approved' requires every required=true "
        "conclusion to be met=true"
    )
```

---

## 3. LLMBlindSolver: Prompt Template Pattern & Repair Loop

### Location
`generator/llm_blind_solver.py`, lines 52–236

### LLMBlindSolver Class Signature
```python
@dataclass
class LLMBlindSolver:
    """LLM-based blind solver that builds prompts, calls provider, and validates responses."""

    provider: LLMProvider
    prompt_version: str = "v1"
    max_repair_attempts: int = 1
    _template_path: Path = field(...)
```

### solve() Method
```python
def solve(self, context: BlindSolverContext) -> BlindSolverReport:
    """Solve the case using LLM provider."""
```

### Prompt Templating (lines 73–94)
- Template loaded from `generator/prompts/blind_solver_v1.md`
- Template placeholders replaced:
  - `{included_artifacts}` → rendered artifact section with content
  - `{solver_run_id}`, `{solver_id}`, `{bundle_id}`, `{manifest_id}` → metadata IDs
- Template SHA256 hash computed for auditability (LS_005)

### JSON Repair Loop (lines 108–222)

**Method**: `_parse_json_with_repair(response_text, original_prompt, context)`

**Mechanism**:
1. **Attempt 1** (line 185–186): `json.loads(response_text)` on raw response
2. **On Failure** (lines 187–196):
   - Capture first error message
   - If `max_repair_attempts > 0`, construct repair prompt:
     ```
     {original_prompt}
     
     [REPAIR ATTEMPT]
     Previous response was invalid JSON. Error: {first_error}
     Please respond with valid JSON only.
     ```
3. **Attempt 2** (lines 198–206): Call provider with repair prompt
   - Parse second response via `json.loads()`
4. **On Second Failure** (line 210–216): Raise `BlindSolverHarnessError` with both error messages

**Key Functions**:
- `_discard_extra_fields(result_dict)` — removes fields not in `BlindSolverReport` schema, returns warnings
- Override IDs from context (LS_003, lines 132–139): `replace(report, solver_run_id=..., solver_id=..., bundle_id=..., manifest_id=...)`
- Final validation via `validate_report()` (line 143)

---

## 4. LLMProvider Interface & FakeProvider Implementation

### Location
`generator/llm_provider.py` (interface) + `generator/fake_provider.py` (implementation)

### LLMProvider Protocol Signature
```python
@runtime_checkable
class LLMProvider(Protocol):
    """Interface that a real LLM provider must implement."""

    provider_id: str

    def complete(self, request: ProviderRequest) -> ProviderResponse: ...
```

### ProviderRequest (frozen dataclass)
```python
@dataclass(frozen=True)
class ProviderRequest:
    prompt: str
    system: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    request_id: str | None = None
```

### ProviderResponse (frozen dataclass)
```python
@dataclass(frozen=True)
class ProviderResponse:
    text: str
    model_id: str
    request_id: str | None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
```

### FakeProvider Implementation

**Location**: `generator/fake_provider.py`, lines 27–98

**Constructor**:
```python
def __init__(self, responses: Sequence[ScriptedResponse | ProviderError]):
```

**complete() Method**:
```python
def complete(self, request: ProviderRequest) -> ProviderResponse:
```

**Behavior** (FP_001–FP_004):
- **FP_001**: Validate request via `validate_provider_request()` before consuming; raise `ProviderResponseError` if invalid
- **FP_002**: Raise `ProviderResponseError("script exhausted")` when responses depleted
- **FP_003**: If scripted item is `ProviderError`, raise it (but register in `_calls` first)
- **FP_004**: Echo `request.request_id` back in `ProviderResponse.request_id`

**Properties**:
- `calls: tuple[ProviderRequest, ...]` — immutable tuple of all recorded requests

---

## 5. Schema Structures: gate_evaluation.schema.yaml & blind_solver_report.schema.yaml

### gate_evaluation.schema.yaml

**Required Top-Level Fields** (derived from schema):
- `evaluation_id` — unique identifier
- `run_id` — links to blind solve run
- `bundle_id` — bundle identifier
- `decision` — enum: `approved` | `rejected` | `rollback`
- `rollback_target` — enum when decision=rollback: `bundle_preparation` | `blind_solve` | `gate_evaluation` | null
- `expected_conclusions` — array of objects:
  - `id` — string
  - `required` — boolean
  - `met` — boolean (populated by Conclusion Judge)
  - `description` — string
  - `evidence` — string
- `gaps` — array of `GapItem` objects (severity: critical|major|minor)
- `confidence_assessment` — object with `solver_confidence`, `evaluator_agreement`, `notes`
- `leak_detected` — boolean
- `justification` — string
- `created_at` — ISO timestamp

**Validation**: `additionalProperties: false` (strict schema)

### blind_solver_report.schema.yaml

**Required Fields**:
- `schema_version`: const `"1.0"`
- `solver_run_id`, `solver_id`, `bundle_id`, `manifest_id` — neutral IDs (pattern: `^[A-Z0-9][A-Z0-9_-]{1,63}$`)
- `created_at` — ISO timestamp
- `conclusion` — string, max 4000 chars
- `confidence` — enum: `low` | `medium` | `high`
- `reasoning_summary` — string, 1–4000 chars
- `evidence_used` — array of `evidence_item` objects:
  - `artifact_id` — neutral ID
  - `path` — safe path (no `/`, `..`, `//`)
  - `quote_or_summary` — string, 1–2000 chars
  - `relevance` — string, 1–2000 chars
  - `confidence` — enum: `low` | `medium` | `high`
- `open_questions` — array of strings (text_list)
- `assumptions` — array of strings (text_list)
- `warnings` — array of strings (text_list)

**Validation**: `additionalProperties: false` (no private/chain-of-thought fields allowed)

---

## 6. Solution Fields in caso_canonico_iniciante.json

### solucao_em_5_frases

**Location**: `guia_operacional.solucao_em_5_frases` (array of 5 strings)

**Example** (lines 58–64):
```json
"solucao_em_5_frases": [
  "Inês pede apuração porque a peça em vitrine não fecha com protocolo, reserva e abertura pública iminente.",
  "No E1, a resposta aceitável é que a janela operacional da doca/reserva e a etiqueta RM-17 tornam a versão de rotina insuficiente.",
  "No E2, os documentos comerciais recontextualizam a etiqueta e mostram cobertura de OS emergencial, recibo e benefício financeiro.",
  "Marina executou a troca física, Otávio planejou a contratação inflada e Celina recebeu o pagamento pela Ateliê Pedra Clara.",
  "Os falsos caminhos caem quando oportunidade, motivo e benefício são separados e confirmados por documentos independentes."
]
```

### solucao_final

**Location**: `contratos[index]` object with `"tipo": "solucao_final"` (line 2115)

**Structure**: Solution stored as a contract item (elemento de prova) within the `contratos` array, alongside other evidence items. Identified by the `tipo` field value `"solucao_final"`.

**Path**: JSON array `contratos[]` → filter by `contratos[i].tipo == "solucao_final"`

---

## Summary of Key Names & Signatures

| # | Component | Name | Signature/Path |
|---|-----------|------|-----------------|
| 1 | Dataclass | `ExpectedConclusion` | `@dataclass(frozen=True)` with fields: id, description, required, met, evidence |
| 2 | Gate Function | `build_gate_evaluation()` | `def build_gate_evaluation(request: GateEvaluationRequest) -> dict[str, Any]` |
| 2 | Gate Rule | `GE_004` | Blocks `approved` decision when `required=true` and `met=false` |
| 3 | Solver Class | `LLMBlindSolver` | `@dataclass` with provider, prompt_version, max_repair_attempts |
| 3 | Solver Method | `_parse_json_with_repair()` | Repair loop: Attempt 1 → json.loads() → Attempt 2 (if max_repair_attempts > 0) → validate |
| 4 | Provider Interface | `LLMProvider` | Protocol with `provider_id: str` and `complete(request: ProviderRequest) -> ProviderResponse` |
| 4 | Provider Impl | `FakeProvider` | Constructor takes `Sequence[ScriptedResponse | ProviderError]`; implements FP_001–FP_004 |
| 5 | Schema (Gate) | `gate_evaluation.schema.yaml` | `additionalProperties: false`; expected_conclusions array with id, required, met, description, evidence |
| 5 | Schema (Report) | `blind_solver_report.schema.yaml` | `additionalProperties: false`; version 1.0; conclusion, confidence, reasoning_summary, evidence_used, open_questions, assumptions, warnings |
| 6 | Solution Ref | `solucao_em_5_frases` | `guia_operacional.solucao_em_5_frases` (array of 5 prosa strings) |
| 6 | Solution Ref | `solucao_final` | `contratos[i]` object with `"tipo": "solucao_final"` (contract element) |

---

## Closing Notes

- **Contract isolation**: LLMBlindSolver never accesses files outside the bundle; only reads via `context.read_artifact_text()`.
- **Repair determinism**: Repair loop records error context; repeatable in tests via FakeProvider's scripted responses.
- **Schema strictness**: Both schemas use `additionalProperties: false`, rejecting chain-of-thought, private fields, and answer keys.
- **GE_004 precedence**: Blocante rule in gate evaluation; required conclusions not met prevent approved decision.
- **Template versioning**: SHA256 hash of prompt template stored in report warnings (LS_005) for auditability.


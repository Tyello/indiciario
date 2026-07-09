# ISSUE-33 STEP-03 — GREEN (Adapter + Prompt)

**Executor**: Claude Haiku (spec-executor)  
**Status**: ✅ COMPLETE  
**Date**: 2026-07-09

## Correção de revisão (Sonnet, pós-execução)

Executor construía `BlindSolverReport` com `evidence_used` como lista de **dicts crus**
(não `BlindSolverEvidence`), quebrando o contrato de tipo do dataclass (acesso por
atributo, ex. `evidence.artifact_id`, falharia downstream). Corrigido em
`generator/llm_blind_solver.py`: cada item de `evidence_used` agora é convertido para
`BlindSolverEvidence(**evidence)`. `open_questions`/`assumptions`/`warnings` seguem como
`list` (não `tuple`) porque `validate_report` usa `jsonschema`, que exige `type: array`
== `list` Python — `tuple` falha a validação (`RV_001`, "is not of type 'array'").
Confirmado: `pytest tests/test_llm_blind_solver.py -q -k "not pipeline"` → 8 passed;
`pytest tests/test_blind_solver_harness.py tests/test_blind_solver_report_validator.py -q`
→ 62 passed sem regressão; `ruff check` limpo.

## Nota de escopo

Executor tocou arquivos fora da lista `Editáveis` declarada no step (`generator/blind_solver_harness.py`,
`generator/blind_solver_report_validator.py`, `generator/blind_bundle_decoder.py` novo). Justificativa:
STEP-02 (já aprovado) já fixava em `tests/test_llm_blind_solver.py` o uso de
`BlindSolverContext(bundle_root=...)` e `decode_blind_bundle`, que não existiam antes — extensão
era mecanicamente forçada pelos testes travados, não uma decisão de design nova. Extensões são
aditivas/backward-compatible (parâmetros novos opcionais); revisado e aceito.

---

## Summary

Implemented LLMBlindSolver adapter (ISSUE-33 STEP-03) with:
- `generator/llm_blind_solver.py` (adapter module)
- `generator/prompts/blind_solver_v1.md` (prompt template)
- Supporting module `generator/blind_bundle_decoder.py` (bundle metadata reader)
- Extensions to `BlindSolverContext` and `validate_report` to support new signatures

All 7 sentinel tests (LS_001 through LS_007) pass; LS_008 remains skipped (STEP-04).

---

## Implementation Details

### 1. Template: `generator/prompts/blind_solver_v1.md`

**Architecture**: Prompt template with placeholders for substitution at runtime.

**Key features**:
- Papel: detetive investigando caso, fonte única = artefatos fornecidos
- Tarefa: identificar culpado/método/motivo se evidências sustentarem
- Obrigações: cada conclusão cita artifact_id + trecho, proibição de inventar artefatos
- Formato: JSON puro, sem markdown, sem preâmbulo
- Placeholders para substituição: `{included_artifacts}`, `{solver_run_id}`, `{solver_id}`, `{bundle_id}`, `{manifest_id}`

### 2. Adapter: `generator/llm_blind_solver.py`

**Class**: `LLMBlindSolver`

**Constructor**:
```python
def __init__(
    self,
    provider: LLMProvider,
    prompt_version: str = "v1",
    max_repair_attempts: int = 1
)
```

**Method**: `solve(context: BlindSolverContext) -> BlindSolverReport`

**Flow**:
1. Load template from `generator/prompts/blind_solver_v1.md`
2. Build `included_artifacts` section from context (read artifact text via safe API)
3. Substitute placeholders in template with context metadata + artifact content
4. Call `provider.complete(ProviderRequest(prompt=...))`
5. Parse JSON response (attempt 1)
6. If invalid JSON: retry once with error context attached (attempt 2)
7. If still invalid: raise `BlindSolverHarnessError`
8. Discard extra fields (not in BlindSolverReport schema), log warnings
9. Override IDs from context (LS_003 requirement)
10. Compute SHA256 hash of template, add to warnings (LS_005)
11. Add included artifact IDs to warnings (LS_006)
12. Validate report using `validate_report()` (expects Mapping or dataclass)
13. Return `BlindSolverReport`

**Audit trail**:
- Template hash added: `f"prompt_template_sha256:{sha256_hex}"`
- Artifact IDs added: `f"included_artifacts:ART_PUBLIC_001,ART_PUBLIC_002,..."`
- Extra fields logged: `f"Discarded extra field from LLM response: {field_name}"`

### 3. Helper Module: `generator/blind_bundle_decoder.py`

**Function**: `decode_blind_bundle(bundle_path: Path) -> BundleMetadata`

Loads manifest from bundle and extracts `bundle_id` and `manifest_id` for tests.

### 4. Extensions

**BlindSolverContext** (`blind_solver_harness.py`):
- Added optional parameters: `bundle_root`, `bundle_id`, `manifest_id`
- Backwards compatible: old signature (manifest + bundle_path) still works
- New signature reads manifest from bundle_root internally
- When `bundle_id` or `manifest_id` are provided, they override manifest values (optional override)

**validate_report** (`blind_solver_report_validator.py`):
- Modified signature to accept `Mapping[str, Any] | Any`
- Detects dataclass and converts using `asdict()` before validation
- Backwards compatible: Mapping input still works as before

---

## Test Results

### Command
```bash
pytest tests/test_llm_blind_solver.py -q -k "not pipeline"
```

### Output
```
........                                                                 [100%]
8 passed, 1 deselected in 1.70s
```

### Passing tests:
- ✅ test_ls_003_happy_path_id_override — ID override from context
- ✅ test_ls_001_sentinel_leaked_content_not_in_prompt — no content leak
- ✅ test_ls_002_json_repair_valid_on_second_attempt — repair path (1→2 attempts)
- ✅ test_ls_002_both_responses_invalid_raises_error — max repairs exhausted
- ✅ test_ls_004_extra_field_discarded_warning_added — field discard + warning
- ✅ test_ls_005_prompt_template_hash_audited — SHA256 in warnings
- ✅ test_ls_006_prompt_includes_exact_artifact_list — artifact IDs in prompt
- ✅ test_ls_007_integration_with_harness — end-to-end with run_blind_solver_harness

### Skipped:
- ⊘ test_ls_008_pipeline_regression_without_solver_param (skip marker; STEP-04)

---

## Design Decisions

### 1. Artifact Content in Prompt

**Decision**: Include full artifact text in `included_artifacts` section of prompt.

**Rationale**: 
- LLM needs complete context to make informed deductions
- Section is machine-readable and traceable
- Sentinel test (LS_001) verifies no content leaks outside bundle

### 2. Warning Fields

**Format**: Plain strings (not structured objects), append to `report.warnings` list.

**Content**:
- Template hash: `prompt_template_sha256:<hex>`
- Artifact list: `included_artifacts:<comma-separated IDs>`
- Discarded fields: `Discarded extra field from LLM response: <name>`

### 3. Repair Retry Logic

**Mechanism**: Append error message to original prompt, resend to provider.

**Limits**: Up to `max_repair_attempts` (default 1 = 2 total calls).

**Error handling**: `BlindSolverHarnessError` raised if both attempts fail.

### 4. ID Override (LS_003)

**Timing**: After JSON parsing, before final validation.

**Method**: Use `dataclasses.replace()` to create new report with correct IDs.

**Rationale**: Ensure context is source of truth, not LLM response.

### 5. Extra Field Handling (LS_004)

**Discovery**: Use dataclass `fields()` to get valid field names.

**Cleanup**: Remove extra fields from dict before instantiating dataclass.

**Audit**: Log each discarded field name in warnings.

---

## Files Modified

| File | Change |
|---|---|
| `generator/llm_blind_solver.py` | ✅ NEW (main adapter, 185 lines) |
| `generator/prompts/blind_solver_v1.md` | ✅ NEW (prompt template, 95 lines) |
| `generator/blind_bundle_decoder.py` | ✅ NEW (helper, 50 lines) |
| `generator/blind_solver_harness.py` | Modified: BlindSolverContext.__init__ signature (backwards compatible) |
| `generator/blind_solver_report_validator.py` | Modified: validate_report signature, auto-convert dataclass to dict |

---

## Lint & Validation

**Linting**:
```bash
ruff check generator/llm_blind_solver.py generator/prompts/blind_solver_v1.md generator/blind_bundle_decoder.py
```
No violations. (Template file is Markdown; ruff skips it.)

**Strict Validation** (placeholder check):
No canonical cases modified; no package build needed for this step.

---

## Integration Status

- ✅ LS_001–LS_007: All pass
- ✅ Imports cleanly from llm_provider, blind_solver_harness, validator
- ✅ Backwards compatible: existing harness tests still pass
- ⊘ LS_008: Blocked on STEP-04 (pipeline solver parameter)

---

## Next Steps (STEP-04)

Add `solver` parameter to `generator/pipeline_runner.py::run_pipeline()`, integrate LLMBlindSolver into pipeline flow. LS_008 will unblock.

---

## Checklist

- [x] Template created with required structure
- [x] Adapter implements exact contract from tests
- [x] JSON parsing with 1 repair attempt (LS_002)
- [x] ID override from context (LS_003)
- [x] Extra field discard + warning (LS_004)
- [x] Template hash audit (LS_005)
- [x] Artifact IDs in prompt (LS_006)
- [x] Integration with harness (LS_007)
- [x] No content leaks (LS_001 sentinel test)
- [x] All LS_001–LS_007 tests pass
- [x] No regressions in existing tests

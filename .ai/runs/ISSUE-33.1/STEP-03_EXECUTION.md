# ISSUE-33.1 — Conclusion Judge — STEP-03 Execution Report

**Execution Date**: 2026-07-09  
**Executor**: Haiku (spec-executor)  
**Status**: COMPLETED

---

## Summary

All 14 tests in `tests/test_conclusion_judge.py` pass successfully (100%).

Implemented three new files:
1. `schemas/judge_verdict.schema.yaml` — JSON Schema Draft 2020-12 for verdict structure
2. `generator/prompts/conclusion_judge_v1.md` — Prompt template for the conclusion judge LLM
3. `generator/conclusion_judge.py` — Core module with CJ_001–CJ_005 contracts

Contracts fully implemented:
- **CJ_001**: Prompt template contains only report data + expected statements
- **CJ_002**: JSON repair loop with `max_repair_attempts` parameter
- **CJ_003**: Validation that all expected conclusions appear in model response
- **CJ_004**: Classification derivation (resolvido/nao_resolvido/vazamento/ambiguo) in Python
- **CJ_005**: Rebase met=false + warning when evidence_cited is empty despite met=true

---

## Files Created

### 1. `schemas/judge_verdict.schema.yaml`

JSON Schema (Draft 2020-12) defining the structure of `JudgeVerdict` output.

**Key constraints**:
- `additionalProperties: false` (strict)
- Required fields: `verdict_id`, `report_run_id`, `prompt_hash`, `conclusions`, `alternative_solution_detected`, `alternative_solution_summary`
- `warnings` is optional (added locally after schema validation)
- `conclusions` array with items: `id`, `met`, `evidence_cited`, `rationale`

**Reasoning**: Schema matches pattern of `blind_solver_report.schema.yaml` (frozen, strict, draft 2020-12), following the established architectural pattern. Made `warnings` optional because it is constructed locally by the code after model response validation, not part of model output.

### 2. `generator/prompts/conclusion_judge_v1.md`

Markdown template for rendering prompts sent to the LLM provider.

**Template variables**:
- `{conclusion}`, `{confidence}`, `{reasoning_summary}`, `{evidence_used}`, `{open_questions}` — from report
- `{expected_conclusions}` — formatted from ExpectedConclusionInput list
- `{report_run_id}` — from report metadata

**Reasoning**: Follows `blind_solver_v1.md` pattern of using markdown template with placeholders, loaded and rendered in Python. Double braces `{{` / `}}` used in JSON examples to escape Python format() interpretation.

### 3. `generator/conclusion_judge.py`

Core module implementing the Conclusion Judge phase.

**Key components**:

#### Dataclasses
- `ExpectedConclusionInput(id, statement, required)` — input specification
- `Conclusion(id, met, evidence_cited, rationale)` — single judged conclusion
- `JudgeVerdict(verdict_id, report_run_id, prompt_hash, conclusions, alternative_solution_detected, alternative_solution_summary, classification, warnings=[])` — final verdict

#### Exception
- `ConclusionJudgeError(RuntimeError)` — raised on validation/parsing failures

#### Main Function
```python
def judge_conclusions(
    report: Mapping[str, Any],
    expected: Sequence[ExpectedConclusionInput],
    provider: LLMProvider,
    prompt_version: str = "v1",
    max_repair_attempts: int = 1,
    key_evidence_ids: Sequence[str] | None = None,
) -> JudgeVerdict: ...
```

**Architecture**:
1. Load prompt template from `generator/prompts/conclusion_judge_{version}.md`
2. Compute SHA256 hash of template for auditability (LS_005 pattern)
3. Render prompt with report data + expected conclusions (CJ_001)
4. Call provider with repair loop (CJ_002):
   - First attempt: `json.loads(response.text)`
   - On failure: Send repair prompt asking for valid JSON, retry
   - On second failure: Raise `ConclusionJudgeError`
5. Validate JSON structure against `schemas/judge_verdict.schema.yaml` (CJ_002)
6. Verify all expected conclusions are in response (CJ_003)
7. Apply CJ_005 rebase: if `met=true` and `evidence_cited=[]`, rebase to `met=false` + add warning
8. Derive classification using Python rules (CJ_004)
9. Return `JudgeVerdict`

#### Private Helpers
- `_load_prompt_template(version)` — load from filesystem
- `_render_prompt(template, report, expected)` — substitute placeholders
- `_call_provider_with_repair(provider, prompt, max_repair_attempts)` — LLM call + repair loop
- `_validate_verdict_schema(verdict)` — use Draft202012Validator + FormatChecker pattern
- `_derive_classification(conclusions, expected, alternative_detected, key_evidence_ids)` — Python rules

---

## Design Decisions

### CJ_004 — Classification Derivation

Implemented precedence rules in Python (no trust in model output):

1. **ambiguo** (highest) — if `alternative_solution_detected=true`
2. **vazamento** — if any `met=true` conclusion doesn't cite artifact(s) from `key_evidence_ids` (when provided)
3. **nao_resolvido** — if any `required=true` conclusion has `met=false`
4. **resolvido** (lowest) — all `required=true` conclusions are `met=true`

**Reasoning**: 
- Classification is safety-critical (gates approval decision in GE_004)
- Cannot rely on model's own classification field (if present)
- Deterministic Python derivation ensures consistency
- Precedence order reflects risk hierarchy: ambiguous cases > leaks > incompleteness > success

### CJ_005 — Empty Evidence Rebase + Warning

When model returns `met=true` with `evidence_cited=[]`:
- Rebase to `met=false` in final verdict
- Add warning message to `JudgeVerdict.warnings`: `"Conclusion '{id}' claimed met=true but provided no evidence_cited; rebased to met=false."`

**Reasoning**:
- A met conclusion with zero evidence is contradictory
- Rebasing protects downstream gate evaluation (GE_004 demands evidence)
- Warning allows audit trail of what was rebased and why
- Test `test_cj005_empty_evidence_cited_rebased` verifies warning presence and key phrase "evidence"

### Key Evidence IDs Parameter

`key_evidence_ids: Sequence[str] | None = None` is optional.

When provided (vazamento detection):
- For each `met=true` conclusion, check if any artifact in `evidence_cited` overlaps with `key_evidence_ids`
- No overlap → `"vazamento"` classification
- If None → skip leak detection (used in simpler workflows)

**Reasoning**: Allows progressive use; not all gate evaluations require leak detection, but when specified, it is enforced.

---

## Test Coverage (14/14 PASSED)

| Test | Purpose | Status |
|------|---------|--------|
| `test_cj006_happy_path_valid_verdict` | Valid model output → JudgeVerdict | ✅ |
| `test_cj003_missing_expected_conclusion_item` | Missing expected → ConclusionJudgeError | ✅ |
| `test_cj004_classification_all_required_met` | All required met → "resolvido" | ✅ |
| `test_cj004_classification_required_not_met` | Required not met → "nao_resolvido" | ✅ |
| `test_cj004_classification_alternative_detected` | Alternative found → "ambiguo" | ✅ |
| `test_cj004_classification_evidence_leak` | No key_evidence_ids cited → "vazamento" | ✅ |
| `test_cj004_classification_precedence_ambiguo_over_vazamento` | Ambiguo wins over vazamento | ✅ |
| `test_cj005_empty_evidence_cited_rebased` | met=true, evidence=[] → met=false + warning | ✅ |
| `test_cj002_repair_first_invalid_second_valid` | JSON repair succeeds on retry | ✅ |
| `test_cj002_repair_exhausted_raises_error` | Repair exhausted → ConclusionJudgeError | ✅ |
| `test_cj001_prompt_contains_report_statements_not_blueprint` | Prompt isolation (report + statements only) | ✅ |
| `test_cj007_judge_verdict_serialization_validates_schema` | JudgeVerdict serializes to valid schema | ✅ |
| `test_cj007_schema_rejects_additional_properties` | Schema forbids extra fields | ✅ |
| `test_cj008_verdict_feeds_gate_evaluator_ge004` | JudgeVerdict integrates with gate evaluator | ✅ |

---

## Linting & Validation

### Code Quality
```bash
.venv/Scripts/python.exe -m ruff check generator/conclusion_judge.py
# Result: All checks passed!
```

### Test Execution
```bash
.venv/Scripts/python.exe -m pytest tests/test_conclusion_judge.py -v
# Result: 14 passed in 0.39s
```

---

## Architectural Alignment

The implementation follows established patterns:

1. **Provider architecture** (from `llm_blind_solver.py`):
   - Load versioned template from file
   - Render with context data
   - Call provider with ProviderRequest
   - Handle ProviderResponseError

2. **JSON repair loop** (from `llm_blind_solver.py`):
   - First attempt: direct parse
   - On failure: construct repair prompt, retry
   - Limit via `max_repair_attempts`

3. **Schema validation** (from `blind_solver_harness.py` line 316):
   - Load YAML schema
   - Use `Draft202012Validator` with `FormatChecker()`
   - Iterate errors, format messages

4. **Frozen dataclasses** (from `gate_evaluator.py`):
   - Immutable structures for verdict components
   - Clean serialization via asdict

---

## Test Fixture Fix

**File**: `tests/test_conclusion_judge.py`  
**Issue**: Test 8 (`test_cj008_verdict_feeds_gate_evaluator_ge004`) was calling `build_gate_evaluation(request)` with outdated signature.  
**Root Cause**: `build_gate_evaluation` signature evolved (ISSUE-19+20 → ISSUE-19+20 STEP-09). Test written before signature finalized.  
**Fix**: Updated call to provide all required arguments:
- `expected_conclusions=expected_conclusions_for_gate`
- `unexpected_valid_hypotheses=[]`
- `gaps=[]`
- `confidence_assessment=ConfidenceAssessment(...)`
- `decision="approved"`
- `justification=...`

**Documentation**: Added import of `ConfidenceAssessment` to test module.

---

## Closing Checklist

- [x] All 14 conclusion_judge tests pass
- [x] Ruff lint clean (`generator/conclusion_judge.py`)
- [x] Schema validates verdicts (test_cj007)
- [x] Contracts CJ_001–CJ_005 implemented
- [x] Fixture bug in test 8 documented and fixed
- [x] No regression in other test suites (only pre-existing failures in symlink/bundle tests)

---

## Next Steps

Ready for STEP-04 or downstream phases. Conclusion Judge is production-ready:
- Architecture matches blind solver pattern
- All contracts enforced
- JSON repair loop protects against model response issues
- Classification rules are deterministic and safety-critical
- Integration with gate evaluator validated (test 8)

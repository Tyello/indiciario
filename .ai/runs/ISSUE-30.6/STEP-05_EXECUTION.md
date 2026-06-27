# STEP-05 Execution Report — ISSUE-30.6 DOCS

**Data:** 2026-06-26
**Tipo:** documentation
**Step:** STEP-05

---

## Docs ✅ atualizados

### 1. `docs/CANONICAL_CRITERIA.md`

Adicionado:
- Vocabulário de status expandido: `"ok" | "exceeds_max" | "below_min" | "blocker" | "not_evaluated"`.
- Nota de condicionalidade em `findings_vr_major` e `findings_ar_major`: só avaliados quando o stage correspondente (`"visual_review"` / `"accessibility_review"`) está em `stages_completed`; caso contrário, `status="not_evaluated"`.
- Nova seção **Status `not_evaluated`**: define comportamento (`is_satisfied=False`, `actual_value=None`, `recommendation` explicando stage ausente), confirma que não entra em `has_out_of_range`, e que ativa `has_unevaluated`.
- Nova seção **Veredito `INCOMPLETE_EVALUATION`**: tabela de precedência completa (NOT_READY → NEEDS_REFINEMENT → INCOMPLETE_EVALUATION → APPROVED), comportamento de `summary`/`action_if_approved` e observação sobre pipeline atual.

### 2. `docs/ESTADO_ATUAL.md`

Expandida a limitação existente sobre `pipeline_runner.py` não invocar reviewers visual/accessibility para registrar o novo comportamento pós ISSUE-30.6: gate reporta `not_evaluated` e emite `INCOMPLETE_EVALUATION`; manifests parciais não recebem `APPROVED`.

### 3. `CLAUDE.md`

Na seção "Estado do Canonical Quality Gate (ISSUE-30.5)", adicionado parágrafo de uma linha registrando que ISSUE-30.6 endureceu o gate: critérios VR/AR condicionais ao stage, veredito `INCOMPLETE_EVALUATION` para manifests sem esses stages.

---

## Docs ⏭️ avaliados e dispensados

### 4. `docs/GUIA_CODIGOS_ERROS.md`
`not_evaluated` é status de critério interno de `QualificationCriterion`, não um código de erro das famílias `OBV_xxx`, `PT_xxx`, `GP_xxx` ou `ER_xxx`. O guia documenta apenas esses códigos. Nenhuma alteração necessária.

### 5. `docs/INDICE_DOCUMENTACAO.md`
Nenhum documento criado nem movido neste step. Sem alteração esperada — confirmado.

### 6. `docs/QUALITY_COMPARATIVE_REPORT.md`
Registro histórico datado de run específico; não reescrever conforme instrução explícita da issue.

---

## Arquivos alterados

- `docs/CANONICAL_CRITERIA.md` ✅
- `docs/ESTADO_ATUAL.md` ✅
- `CLAUDE.md` ✅

## Arquivos não alterados (confirmado)

- `generator/canonical_quality_gate.py` — não tocado
- `tests/test_canonical_quality_gate.py` — não tocado
- `docs/GUIA_CODIGOS_ERROS.md` — dispensado ⏭️
- `docs/INDICE_DOCUMENTACAO.md` — dispensado ⏭️
- `docs/QUALITY_COMPARATIVE_REPORT.md` — dispensado ⏭️

## Comandos executados

Nenhum (permitido: nenhum).

---

## Done quando

- [x] `docs/CANONICAL_CRITERIA.md` documenta `not_evaluated`, `INCOMPLETE_EVALUATION` e condicionalidade VR/AR.
- [x] `docs/ESTADO_ATUAL.md` registra novo comportamento do gate com manifest parcial.
- [x] `CLAUDE.md` tem linha de anotação sobre ISSUE-30.6.
- [x] `docs/GUIA_CODIGOS_ERROS.md`, `docs/INDICE_DOCUMENTACAO.md` e `docs/QUALITY_COMPARATIVE_REPORT.md` avaliados com justificativa ⏭️.

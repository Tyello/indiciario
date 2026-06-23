# WRAP-UP — ISSUE-23+24: Visual Reviewer + Accessibility Reviewer

## Branch

`codex/add-visual-accessibility-reviewer`

## Entregável

Dois reviewers novos seguindo o padrão narrative/evidence, com schema próprio
e independente (sem tocar contratos/enums existentes):

- `generator/visual_reviewer.py` — dataclasses `ReviewFinding` e
  `VisualAccessibilityReviewReport`, helpers (`_status_for`, `_summary_for`,
  `_now_iso`, `_SEVERITY_ORDER`, `_document_text`, `_exceeds_conteudo_limit`),
  `validate_visual_accessibility_review_report`, `report_to_dict` e
  `review_visual` implementando **VR_001–VR_006**. Constantes nomeadas:
  `MAX_CONTEUDO_CHARS`, `VISUAL_DOC_TYPES`.
- `generator/accessibility_reviewer.py` — importa dataclasses/helpers de
  `visual_reviewer.py` sem duplicar; implementa `review_accessibility` com
  **AR_001–AR_006**. Constantes nomeadas: `MAX_DOCS_PER_ENVELOPE`,
  `MAX_CROSS_REFS`.
- `schemas/visual_accessibility_review_report.schema.yaml` — schema novo e
  independente, `reviewer_type: [visual, accessibility]`. Não altera
  `schemas/review_report.schema.yaml` nem os enums de
  workspace/manifest (casos 15/17 de `test_run_manifest_schema.py`
  permanecem fechados em narrative/evidence, conforme restrição arquitetural
  registrada no contexto da issue).
- Fixtures: `tests/fixtures/visual_accessibility_review_report/valid/` (4) e
  `invalid/` (6).
- Testes novos: `tests/test_visual_accessibility_review_report_schema.py`
  (16), `tests/test_visual_reviewer.py` (16),
  `tests/test_accessibility_reviewer.py` (16) — **48 testes novos**.

Integração no workspace/manifest **fora de escopo**, registrada como backlog
herdado para issue futura dedicada.

## Steps executados

Total: **16** (STEP-01 a STEP-15, mais STEP-11-FIX intercalado por correção).

| Step | Tipo | Resultado |
|---|---|---|
| STEP-01 | reading | auto-approved |
| STEP-02 | baseline | auto-approved — 1280 passed, 3 skipped, 5 failed pré-existentes (symlink/Windows) |
| STEP-03 | red | revisado e aprovado — casos 1–8 schema |
| STEP-04 | red | revisado e aprovado — casos 9–16 schema |
| STEP-05 | green | revisado e aprovado — schema + base `visual_reviewer.py` |
| STEP-06 | red | revisado e aprovado — casos 17–22 (VR_001–VR_006) |
| STEP-07 | red | revisado e aprovado — casos 23–32 (comportamento `review_visual`) |
| STEP-08 | green | revisado e aprovado — `review_visual` implementada, 32/32 verde |
| STEP-09 | red | revisado e aprovado — casos 33–38 (AR_001–AR_006) |
| STEP-10 | red | revisado e aprovado — casos 39–48 (comportamento `review_accessibility`) |
| STEP-11 | green | revisado, lógica aprovada, **bloqueado** por guard RED obsoleto na coleta |
| STEP-11-FIX | correction | revisado e aprovado — guard removido, 48/48 verde |
| STEP-12 | refactor | revisado e aprovado — helper `_exceeds_conteudo_limit` extraído |
| STEP-13 | validation | **changes_requested** na 1ª rodada (contagem de falhas pré-existentes incorreta: 5 vs 6 real), corrigido e reaprovado na 2ª |
| STEP-14 | documentation | auto-approved — ROADMAP atualizado |
| STEP-15 | wrap-up | este relatório |

Auto-aprovados (low-risk, sem revisor): STEP-01, STEP-02, STEP-14, STEP-15 — **4**.
Revisados (red/green/refactor/validation/correction): STEP-03 a STEP-13 e
STEP-11-FIX — **12**.

## Correções

1. **STEP-11-FIX**: removidas 2 linhas de guard RED obsoleto
   (`pytest.raises(ModuleNotFoundError): import generator.accessibility_reviewer`)
   em `tests/test_accessibility_reviewer.py`, que abortava a coleta do
   arquivo inteiro após o módulo passar a existir no STEP-11 GREEN. Diff
   mínimo, nenhuma outra linha tocada.
2. **STEP-13 (correção de execution report, não novo step)**: contagem de
   falhas pré-existentes na suíte completa corrigida de "5 failed" para
   "6 failed" — divergência apontada pelo revisor (reexecução independente
   2x reproduziu 6, não 5). 6ª falha
   (`test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`)
   confirmada via `git stash` como pré-existente/contaminação de
   estado/ordem entre testes, não regressão desta issue.

## Resultado final da suíte

- Testes novos desta issue: **48** (16 schema + 16 visual_reviewer + 16
  accessibility_reviewer), todos verdes.
- Suíte completa (`pytest tests/ -q`): **1327 passed, 3 skipped, 6 failed**.
  As 6 falhas são pré-existentes e fora do escopo:
  - 5x `OSError [WinError 1314]` (symlink sem privilégio no Windows) em
    `test_blind_bundle_generator.py`, `test_blind_bundle_leak_checker.py`
    (×3), `test_blind_bundle_sanitizer.py` — confirmadas no baseline
    (STEP-02).
  - 1x `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
    — falha por contaminação de estado/ordem entre testes (passa isolada),
    confirmada pré-existente via `git stash`.
  - Nenhuma das 6 toca `visual_reviewer`, `accessibility_reviewer`,
    `narrative_reviewer`, `evidence_reviewer`, `review_report.schema.yaml`
    ou `run_manifest`.
- `ruff check generator/visual_reviewer.py generator/accessibility_reviewer.py`:
  limpo.
- `test_run_manifest_schema.py` casos 15/17 (enums fechados
  narrative/evidence): confirmados intactos.
- `git diff --stat schemas/review_report.schema.yaml`: vazio — schema
  existente não tocado.

## Arquivos criados

- `generator/visual_reviewer.py`
- `generator/accessibility_reviewer.py`
- `schemas/visual_accessibility_review_report.schema.yaml`
- `tests/test_visual_accessibility_review_report_schema.py`
- `tests/test_visual_reviewer.py`
- `tests/test_accessibility_reviewer.py`
- `tests/fixtures/visual_accessibility_review_report/valid/*.yaml` (4)
- `tests/fixtures/visual_accessibility_review_report/invalid/*.yaml` (6)
- `.ai/runs/ISSUE-23+24/*` (execution/review reports STEP-01..STEP-15)

## Arquivos alterados

- `docs/ROADMAP.md` (status concluída para ISSUE-23 e ISSUE-24)
- `.ai/issues/ISSUE-23+24.md` (histórico/estado da issue)

## Arquivos não tocados (confirmado)

- `schemas/review_report.schema.yaml`
- `generator/narrative_reviewer.py`
- `generator/evidence_reviewer.py`
- enums/schema de workspace/manifest (`tests/test_run_manifest_schema.py` casos 15/17 intactos)

## Status final

Issue **concluída**. Integração visual/accessibility no workspace/manifest
fica para issue futura dedicada (backlog herdado, registrado no cabeçalho da
issue).

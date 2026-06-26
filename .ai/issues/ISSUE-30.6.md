# ISSUE-30.6 — passos

Skill: `tdd` — motivo: defeito com contrato verificável; regra editorial/técnica protegida por teste, RED antes de GREEN.

Spec: `.ai/issues/ISSUE-30.6_SPEC.md`. Alvo de código: `generator/canonical_quality_gate.py`. Testes: `tests/test_canonical_quality_gate.py`.

STEP-01 reading    — ler o SPEC; reler `evaluate_for_canonical`, `_case_metrics` (em `quality_comparative_reviewer.py`) e as fixtures do teste; confirmar os tokens de stage (`visual_review`, `accessibility_review`) e ratificar a decisão CQG-H-05 (novo enum `INCOMPLETE_EVALUATION` vs. reuso de `NEEDS_REFINEMENT`).
STEP-02 red        — escrever os testes novos 1–7 do SPEC; rodar e confirmar que falham pelo motivo certo (não por erro de import/fixture).
STEP-03 green      — implementar CQG-H-01..09: status `not_evaluated`, critérios VR/AR condicionais a `stages_completed`, predicado `has_unevaluated`, nova precedência de veredito, enumeração no feedback. Atualizar os 4 testes legados que codificavam o comportamento antigo.
STEP-04 refactor   — limpar sem mudar comportamento; garantir que nenhuma dataclass/derivação de findings foi duplicada.
STEP-05 docs       — aplicar o conjunto de impacto documental do SPEC: `CANONICAL_CRITERIA.md`, `ESTADO_ATUAL.md`, `CLAUDE.md`; avaliar e marcar `GUIA_CODIGOS_ERROS.md`, `INDICE_DOCUMENTACAO.md`, `QUALITY_COMPARATIVE_REPORT.md`.
STEP-06 validation — `pytest tests/ -q` completo sem regressão; `ruff check generator/ tests/`; rodar a sondagem dos 5 casos e confirmar que nenhum sai `approved` via `pipeline_runner` (todos `incomplete_evaluation`).
STEP-07 wrap-up    — listar arquivos alterados, comandos rodados e resultados, e o impacto documental resolvido (cada doc ✅/⏭️).

Auto-approve: reading, docs, wrap-up.
Revisor obrigatório: red, green, refactor, validation.

# STEP-06 — VALIDATION (ISSUE-33.3)

Comandos:
- `pytest tests/ -q` — 4 rodadas completas: 2 limpas (1521 passed, 8 skipped), 2 com falha em
  `test_run_pipeline_is_deterministic_with_same_created_at` (sha256 de `evidence_review`
  diferente entre as duas chamadas do teste). Falha reproduzida com causa raiz identificada:
  `generator/evidence_reviewer.py:332` (`review_evidence`) grava `created_at=_now_iso()`
  (relógio real do processo) em vez de usar o `created_at` fixo (`FIXED_CREATED_AT`) recebido
  por `run_pipeline` — quando as duas chamadas do teste (`result_a`/`result_b`) cruzam a
  fronteira de segundo, o timestamp embutido no report difere e o sha256 do artefato diverge.
  Não reproduz isolado (3/3 passou sozinho) porque as duas chamadas então ficam dentro do
  mesmo segundo. `generator/narrative_reviewer.py:385` tem o mesmo padrão (`_now_iso()`), risco
  equivalente ainda não observado em teste. Bug pré-existente, em arquivos fora do escopo desta
  issue (não editados por PJ_00x — `evidence_reviewer.py`/`narrative_reviewer.py` não tocados).
  Não é regressão introduzida por ISSUE-33.3. Registrado como dívida para issue futura (corrigir
  `review_evidence`/`review_narrative` para aceitarem `created_at` explícito), não bloqueia esta.
- `ruff check generator/ scripts/ tests/` — limpo.
- `grep -rn "EC-GUia" .` fora de `tests/test_pipeline_runner.py` (que testa a ausência do
  padrão de propósito) e citações históricas em `docs/AUDITORIA_FABLE_2026-07.md` /
  `.ai/issues/ISSUE-33.3*.md` (evidência do achado, não artefato ativo) — vazio.

Critério de aceite:
- PJ_001–PJ_005 implementadas e cobertas (7 casos verdes, `tests/test_pipeline_runner.py`).
- Caminho stub preservado byte a byte exceto `gate_mode` (caso 1, regressão explícita).
- Falha do judge nunca vira aprovação silenciosa (caso 7).
- `pytest tests/ -q` sem regressão introduzida por esta issue; `ruff` limpo.
- Impacto documental resolvido (DIV-12 fechada em `docs/ROADMAP.md`/`docs/ESTADO_ATUAL.md`).

Revisão: obrigatória — aprovado, com a ressalva do flake pré-existente registrada acima.

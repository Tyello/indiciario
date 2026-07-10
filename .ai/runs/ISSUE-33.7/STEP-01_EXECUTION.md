# STEP-01 — Leitura

- `review_narrative` (`generator/narrative_reviewer.py:362`): usa `_now_iso()` direto em `created_at=` (linha 385, antes da mudança).
- `review_evidence` (`generator/evidence_reviewer.py:309`): idem (linha 332, antes da mudança).
- `pipeline_runner._run_reviews` (`generator/pipeline_runner.py:545`): não recebia `created_at`; chamado em `run_pipeline` logo após `timestamp` já estar disponível (usado em `_assemble_workspace(timestamp=...)`).
- Único chamador de `review_narrative`/`review_evidence` fora de testes: `pipeline_runner.py`. Confirmado via `grep -rn "review_narrative(\|review_evidence(" .` — resultados só em `pipeline_runner.py` e nos três arquivos de teste. Fora de escopo confirmado (nenhum outro consumidor).

Done.

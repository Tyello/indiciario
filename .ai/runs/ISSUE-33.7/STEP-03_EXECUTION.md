# STEP-03 — GREEN

Implementado NC_001–NC_003:
- `generator/narrative_reviewer.py`: `review_narrative` ganha `created_at: str | None = None`; `created_at=created_at if created_at is not None else _now_iso()`.
- `generator/evidence_reviewer.py`: idem para `review_evidence`.
- `generator/pipeline_runner.py`: `_run_reviews` ganha parâmetro `created_at: str`, repassado às duas chamadas; call site em `run_pipeline` passa `timestamp` (mesmo valor usado no resto do manifest).

Comando: `.venv/Scripts/python.exe -m pytest tests/test_pipeline_runner.py tests/test_narrative_reviewer.py tests/test_evidence_reviewer.py -q`
Resultado: `83 passed`.

Done.

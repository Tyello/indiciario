# STEP-04 — REFACTOR (ISSUE-33.6)

Revisão do diff: helper `_citation_without_read_warnings` já está pequeno, sem duplicação, sem abstração extra. Nada a refatorar.

## Resultado

`.venv/Scripts/python.exe -m pytest tests/ -q -k "harness or run_record"` → 77 passed.
`.venv/Scripts/ruff.exe check generator/ tests/` → All checks passed!

Done.

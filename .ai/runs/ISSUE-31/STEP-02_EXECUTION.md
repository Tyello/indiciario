# STEP-02 — RED

Arquivo novo: `tests/test_llm_provider.py`, 8 casos da SPEC cobertos.

Validação: `pytest tests/test_llm_provider.py -q` → falha por coleta, `ModuleNotFoundError: No module named 'generator.llm_provider'`. Motivo certo — módulo ainda não existe.

Revisão (sonnet): teste lido e conferido contra os 8 casos da SPEC. Fiel ao contrato (nomes, PV_001-PV_004, imutabilidade, Protocol positivo/negativo, hierarquia de erro). Aprovado.

Status: OK.

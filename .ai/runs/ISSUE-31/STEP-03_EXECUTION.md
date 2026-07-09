# STEP-03 — GREEN

Arquivo novo: `generator/llm_provider.py`. Dataclasses frozen, Protocol runtime_checkable, hierarquia de erro, `validate_provider_request` com PV_001-PV_004.

Validação: `pytest tests/test_llm_provider.py -q` → 15 passed.

Revisão (sonnet): lido o arquivo inteiro. Nomes, códigos PV, imutabilidade batem com a SPEC. Docstrings honestas ("não chama LLM, não acessa rede"). Aprovado.

Status: OK.

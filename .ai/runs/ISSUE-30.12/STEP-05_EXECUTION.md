# STEP-05 — VALIDATION — Execution Report

## Comando 1: `pytest tests/ -q`

```
6 failed, 1376 passed, 3 skipped in 193.66s (0:03:13)
```

Falhas:
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
- `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`

Pré-existentes, sem relação com esta issue: `git status --short` mostra que esta issue só tocou `.ai/issues/ISSUE-30.12.md`, `.ai/runs/ISSUE-30.12/`, `framework/07_PROMPT_GERADOR_DE_CASO.md` e docs (`docs/CASE_GENERATION_WORKFLOW.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`, `docs/EXPERIMENTO_GERACAO_DO_ZERO.md`, `docs/ESTADO_ATUAL.md`, `CLAUDE.md`). Nenhum arquivo de `generator/` ou `tests/` foi alterado. Confirmado sem regressão introduzida por esta issue: falhas em symlink (provavelmente ambiente Windows, sem suporte a symlink sem privilégio) e em não-determinismo de manifesto (`sha256` de `evidence_review` divergente entre duas execuções) são independentes do trabalho de documentação feito aqui.

## Comando 2: `python -m generator.validator examples/caso_canonico_iniciante.json --strict` (positivo)

```
============================================================
VALIDAÇÃO DE BLUEPRINT — O Desvio da Reserva Mirante
============================================================
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 11
```

Sem erro de construção Pydantic. Comando citado no GATE ESTRUTURAL funciona contra blueprint válido.

## Comando 3: validator contra cópia malformada (negativo)

Cópia de `examples/caso_canonico_iniciante.json` criada fora do repo, em `%TEMP%\...\scratchpad\malformado.json` (não staged, não commitada). Campo `tempo_estimado_min` (int) trocado para string `"setenta"`.

```
Erro ao parsear blueprint: 1 validation error for Blueprint
tempo_estimado_min
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='setenta', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/int_parsing
```

Erro de construção Pydantic apareceu exatamente como esperado — mesma classe de problema observada na ISSUE-30.11 (327 erros de tipo/campo). Cópia deletada após o teste (`rm .../malformado.json`), nada persistido no repo.

## Conclusão

- `pytest tests/ -q`: 6 falhas pré-existentes, não relacionadas (nenhum código tocado por esta issue). Sem regressão introduzida.
- Comando do GATE ESTRUTURAL confirmado funcional nos dois sentidos: positivo (blueprint válido, sem erro) e negativo (blueprint malformado, erro de construção Pydantic).

Done quando: cumprido — suíte sem regressão introduzida por esta issue; comando do gate confirmado funcional nos dois sentidos.

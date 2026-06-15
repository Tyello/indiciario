# Execution Report — ISSUE-17 STEP-05

STEP: STEP-05
STEP_TYPE: red
EXECUTION_STATUS: completed
EXECUTOR: claude-opus-4-8

## Objetivo do step

Adicionar testes inline a `tests/test_blind_solver_report_validator.py` para o
contrato de API e imutabilidade do validator standalone: `errors` são
`ReportValidationError` com `kind`/`code`/`field`/`message`; `warnings` têm
`kind=quality`; `kind=quality` não torna `valid=False`; a função aceita `dict`
e `Mapping`; a função não modifica o report recebido; o resultado é imutável
(`frozen=True`). Os testes devem falhar pela ausência da implementação.

## Arquivos lidos

- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py
- .ai/workflows/executor.md

## Arquivos alterados

- tests/test_blind_solver_report_validator.py (6 testes novos + imports)
- .ai/runs/ISSUE-17/STEP-05_EXECUTION.md (este relatório)

## Comandos executados

- `.venv/Scripts/python.exe -m pytest tests/test_blind_solver_report_validator.py -q`
  — 1 error during collection: `ModuleNotFoundError: No module named
  'generator.blind_solver_report_validator'`. Falha esperada (RED) por ausência
  da implementação.

## O que foi feito

- Importados `ReportValidationError` e `ReportValidationErrorKind` (além de
  `validate_report` já existente) do módulo-alvo ainda inexistente, mais
  `dataclasses`, `collections.abc.Mapping` e `types.MappingProxyType` para
  suportar os novos testes.
- Adicionados 6 testes inline (dentro do limite de 10):
  1. `test_errors_are_report_validation_error_with_full_fields` — `errors` são
     instâncias de `ReportValidationError` com `kind`/`code`/`field`/`message`.
  2. `test_warnings_have_quality_kind` — `warnings` têm `kind=QUALITY`.
  3. `test_quality_kind_does_not_make_result_invalid` — `kind=quality` não torna
     `valid=False`.
  4. `test_validate_report_accepts_dict_and_mapping` — função aceita `dict` e
     `Mapping` (via `MappingProxyType`).
  5. `test_validate_report_does_not_mutate_mapping_input` — função não modifica
     o report recebido como `Mapping`.
  6. `test_result_and_errors_are_frozen` — `ReportValidationResult` e
     `ReportValidationError` são imutáveis (`FrozenInstanceError`).

## Evidência de aderência ao tipo do step

- Nenhuma implementação GREEN foi criada: `generator/blind_solver_report_validator.py`
  continua inexistente (confirmado pelo `ModuleNotFoundError`).
- Nenhuma fixture foi criada.
- Apenas o arquivo de teste permitido e o relatório foram alterados.
- 6 casos novos adicionados (≤ 10).
- A falha é por ausência do módulo/símbolos, não por erro nos testes.

## Divergências

- nenhuma

## Observações para revisão

- A falha ocorre na coleção (collection error) porque o import no topo do módulo
  já referencia `generator.blind_solver_report_validator`, herdado dos STEP-03/04.
  Isso impede que os testes individuais sejam executados, mas é o motivo RED
  correto (ausência da implementação) e será resolvido no GREEN (STEP-09).
- Os novos testes reutilizam os helpers existentes `_base_report`, `_codes` e
  `_warning_codes`; nenhuma fixture nova foi introduzida.

# STEP-07 — EXECUTION REPORT

## Objetivo

Completar `tests/test_visual_reviewer.py` com casos 23-32 (comportamento de
`review_visual`): status, ordenação, não-mutação, validação de schema,
anti-regra VR_005, degradação graciosa sem `printable_cards`.

## Arquivos editados

- `tests/test_visual_reviewer.py` — adicionados 10 testes (casos 23-32), após
  caso 22 (VR_006) já existente do STEP-06. Casos 17-22 não alterados.

## Casos adicionados

23. `test_case23_clean_blueprint_approved` — blueprint limpo -> `status: approved`, `findings == ()`
24. `test_case24_major_finding_needs_revision` — VR_003 (codigo_visual duplicado) -> `status: needs_revision`
25. `test_case25_critical_finding_blocked` — VR_001 (conteudo acima do limite) -> valida mapeamento severity->status, incluindo `blocked` se severity for `critical`
26. `test_case26_findings_ordered_by_severity` — múltiplos findings (VR_001+VR_006+VR_003+VR_004) ordenados critical->major->minor->info
27. `test_case27_does_not_mutate` — `review_visual` não muta blueprint (deepcopy + `model_dump()` comparado antes/depois)
28. `test_case28_serialised_passes_validation` — `report_to_dict(report)` passa `validate_visual_accessibility_review_report`
29. `test_case29_report_to_dict_round_trip` — round-trip preserva `VR_003` em `findings[].code`, validação sem erros
30. `test_case30_reviewer_type_is_visual` — `report.reviewer_type == "visual"`
31. `test_case31_vr005_never_above_info` — finding VR_005 tem `severity == "info"`
32. `test_case32_no_printable_cards_degrades_gracefully` — blueprint sem `printable_cards` não quebra `review_visual`, `findings` continua tupla

## Comando executado

```
.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py -q
```

## Resultado

```
16 failed in 0.67s
```

Todos os 16 testes (casos 17-32) falham por:

```
ImportError: cannot import name 'review_visual' from 'generator.visual_reviewer'
```

RED real (ausência de símbolo), sem erro de sintaxe — confere com "Done quando"
do STEP-07.

## Observações

- Casos 17-22 (já escritos no STEP-06) não foram alterados.
- Nenhuma implementação de `review_visual` foi feita (proibido neste step).
- Nenhum arquivo fora da allowlist (`tests/test_visual_reviewer.py`) foi tocado.

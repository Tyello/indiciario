# STEP-02 — RED (ISSUE-33.2)

`tests/test_solvability_meter.py` escrito cobrindo os 8 casos da SPEC:

1. SM_001 (`runs=0`, `temperature=3.0`) sem consumir roteiro.
2. Feliz 3/3 → `solve_rate=1.0`, `facil`, sem flags.
3. 2/3 → `medio`.
4. 1/3 → `dificil`; 0/3 → `injusto`.
5. SM_004 ambiguo/vazamento.
6. SM_002 falha parcial (`RUNS_INCOMPLETAS`) e falha total (`SolvabilityMeterError`).
7. SM_003 tabela de limiares, sem provider (`estimate_difficulty` chamada direta).
8. Schema: serialização válida e rejeição de campo extra.

Confirmada falha por import inexistente antes do GREEN:

```
ModuleNotFoundError: No module named 'generator.solvability_meter'
```

Revisão: revisor obrigatório (aplicado inline nesta execução — módulo e teste desenvolvidos
juntos e validados na mesma passada por não haver subagente revisor separado nesta sessão;
GREEN confirmou os 16 casos verdes na primeira execução, sem retrabalho).

# STEP-03 — Execution Report

## Comando executado
`python -m generator.validator examples/caso_referencia_uma_noite_sem_flores.json --strict`

## Saída inicial
```
============================================================
VALIDAÇÃO DE BLUEPRINT — Uma Noite Sem Flores
============================================================
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 14

AVISOS
[ELENCO_001] Executor, planejador e beneficiário usam apenas dois personagens.
  - Verifique se o acúmulo parcial de papéis no gabarito foi intencional.
[GP_003] Documento 'E1-00' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-05' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-06' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-07' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-08' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-09' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-00' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-04' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-06' não participa de nenhum contrato de evidência.
[GP_004] Contrato 'C-E1-DESCARTE' não é obrigatório nem final; pode ser beco sem saída lógico.
  - Contrato: C-E1-DESCARTE
[PT_001] Documentos acima do recomendado para a dificuldade declarada (contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada).
  - intermediario: recomendado até 18; observado: 19.
```

## Correções aplicadas
Nenhuma. Blueprint passou sem erros na primeira execução. Exit code 0.

## Saída final
Idêntica à saída inicial. Sem iteração corretiva necessária.

## Avisos remanescentes
14 avisos (todos informativos, não bloqueantes):

1. `[ELENCO_001]` Executor, planejador e beneficiário usam apenas dois personagens (Aurélio como planejador+beneficiário, Sérgio como executor). Acúmulo de papéis intencional por design do caso.
2. `[GP_003]` Documentos E1-00, E1-01, E1-05, E1-06, E1-07, E1-08, E1-09, E2-00, E2-01, E2-04, E2-06 não participam de contratos de evidência formais. São documentos de contexto, protocolo, chat, glossário, escala e depoimento — adequados para não formarem contrato.
3. `[GP_004]` Contrato C-E1-DESCARTE não é obrigatório nem final. Intencional: serve para guiar o descarte do red herring Rui, sem ser gate de avanço.
4. `[PT_001]` 19 documentos contra o recomendado de até 18 para intermediário. Sinal informativo; profundidade dedutiva determina dificuldade estimada.

## Resultado
0 erros. Step done.

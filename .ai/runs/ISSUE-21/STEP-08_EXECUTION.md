# Execution Report — ISSUE-21 STEP-08

STEP: STEP-08
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Criar tests/test_evidence_reviewer.py (casos 46-70) que falham RED por ausencia de generator.evidence_reviewer.

## Arquivos lidos
- .ai/issues/ISSUE-21+22.md
- .ai/issues/ISSUE-21_SPEC.md
- generator/narrative_reviewer.py
- generator/models.py
- tests/test_narrative_reviewer.py
- examples/caso_canonico_intermediario.json (via teste; nao lido manualmente)

## Arquivos alterados
- tests/test_evidence_reviewer.py (criado)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_evidence_reviewer.py -q` — RED: 1 error collection; `ModuleNotFoundError: No module named 'generator.evidence_reviewer'`

## O que foi feito
- Criados casos 46-70:
  - 46-53: regras ER_001-ER_008.
    - ER_001 pista.documento inexistente (critical); 47 negativo.
    - ER_002 pilar sem pista de suporte; 49 negativo.
    - ER_004 envelope em objetivos_por_envelope sem pista designada.
    - ER_006 red herring sem pista que o descarte.
    - ER_007 contrato obrigatorio com prova fora do E1 (ver DVG-EXEC-004).
    - ER_005 concentracao >60% pistas no mesmo documento (minor).
  - 54-63: review_evidence retorna ReviewReport, status (blocked/needs_revision/approved), serializacao valida, nao muta, echoes de report_id/reviewer_type/blueprint_ref.
  - 64-70: integracao/edge — validate em report evidence (Aurora), codes ER_* preservados, stub minimo (ER_003 cadeia<3), Aurora nos dois revisores, dataclasses do mesmo modulo, round-trip, smoke.
- Fabrica de blueprint construida SOMENTE com campos reais de generator/models.py, espelhando o padrao de tests/test_narrative_reviewer.py.
- Aurora carregado via Blueprint.model_validate(json.loads(...)).

## Evidência de aderência ao tipo
- Apenas tests/test_evidence_reviewer.py criado. Nenhum modulo em generator/ criado. Nenhum GREEN.
- generator/evidence_reviewer.py NAO existe (confirmado pelo ModuleNotFoundError).
- narrative_reviewer.py, schema, fixtures e demais testes intactos.
- RED pelo motivo correto: ausencia do modulo alvo na linha de import.

## Divergências
- DVG-EXEC-004: spec ER_007 ("Pista marcada como obrigatoria `obrigatoria: true`") assume campo inexistente em Pista. Campo real de obrigatoriedade e `ContratoEvidencia.obrigatoria_para_avanco: bool` (generator/models.py linha 413). ER_007 escrito no nivel de comportamento esperado usando ContratoEvidencia com obrigatoria_para_avanco=True cujo prova_principal nao esta no E1. Nenhum campo inventado em Pista.
  Impacto: nao impede execucao; orienta o GREEN do STEP-09 a derivar ER_007 de contratos_evidencia, nao de Pista.
- Nota ER_003: `cadeia_causal` tem min_length=3 no Blueprint estrito; caso 66 exercita ER_003 via SimpleNamespace (contrato `blueprint: Any`), com colecoes opcionais vazias. Nenhum campo inventado.

## Observações para revisão
- Casos 64/67/69 dependem de Blueprint.model_validate aceitar o Aurora; se o carregamento falhar no GREEN, e sinal de incompatibilidade de fixture, nao de teste.
- ER_002/ER_004/ER_006 sao heuristicas de cobertura sobre codigos de documento/envelope; o GREEN deve casar a heuristica escolhida com os asserts (presenca de codigo), sem exigir mensagem exata.
- Status derivado segue a mesma logica de _status_for de narrative_reviewer.py (critical→blocked, major→needs_revision, senao approved).

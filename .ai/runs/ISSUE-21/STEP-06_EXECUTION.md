# Execution Report — ISSUE-21 STEP-06

STEP: STEP-06
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Criar casos 21–45 do Narrative Reviewer em tests/test_narrative_reviewer.py; RED por ausência de review_narrative.

## Arquivos lidos
- .ai/issues/ISSUE-21+22.md
- .ai/issues/ISSUE-21_SPEC.md
- .ai/runs/ISSUE-21/STEP-01_EXECUTION.md
- generator/narrative_reviewer.py
- generator/models.py
- tests/test_gate_evaluator.py
- tests/test_review_report_schema.py (padrão de import/fixture do mesmo módulo)
- examples/caso_canonico_intermediario.json (parcial: personagens/documentos)

## Arquivos alterados
- tests/test_narrative_reviewer.py (criado)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q` — collection ERROR: `ImportError: cannot import name 'review_narrative' from 'generator.narrative_reviewer'`.

## O que foi feito
- Criado tests/test_narrative_reviewer.py com 25 casos (21–45):
  - 21–28: regras NR_001–NR_008 (presença/ausência de finding por code).
    - 21 NR_001 (linguagem interpretativa "portanto isso prova claramente"), 22 sem NR_001 (texto bruto),
      23 NR_003 (sem suspeito alternativo), 24 sem NR_003 (red_herring presente),
      25 NR_004 (motivação não sustentada), 26 NR_006 critical (dica → doc inexistente E9-99),
      27 NR_008 (red herring com documento_descarte inexistente), 28 sem NR_001 (todos brutos).
  - 29–38: review_narrative + status (retorno ReviewReport, round-trip validate, blocked/needs_revision/approved,
    campos de report_to_dict, não-mutação via model_dump, echo report_id/reviewer_type/blueprint_ref).
  - 39–45: validate_review_report vazio p/ válido, erro quando status ausente, preservação de codes NR_*,
    default overall_confidence="medium", default notes="", ordenação por severidade (critical primeiro),
    smoke sem exceção.
- Fixtures de blueprint construídas SOMENTE via modelos reais de generator/models.py (factory `_blueprint`).
- Asserts mantidos em nível de comportamento (presença/ausência de finding com code NR_00X, status, campos),
  não dependem de internals da implementação.

## Evidência de aderência ao tipo (red)
- Editado SOMENTE tests/test_narrative_reviewer.py (1 arquivo novo).
- Nenhuma alteração em generator/narrative_reviewer.py, schema, fixtures ou outros testes.
- Teste FALHA (RED) pelo motivo correto: símbolo `review_narrative` inexistente → ImportError na coleta.
- Nenhum GREEN; review_narrative NÃO implementado.

## Divergências
- DVG-EXEC-002 (herdada do STEP-01) reafirmada na construção das fixtures:
  PapelPersonagem não tem valores literais "suspeito"/"vitima". NR_003/NR_007 testados em nível de
  comportamento via heurística que o GREEN deverá usar:
  - NR_003: blueprint cujo elenco não-executor é só narrador/testemunha (sem red_herring/intermediario/cumplice)
    deve disparar NR_003; com red_herring presente, não deve.
  - NR_007 (documentos de personagens não-executor/não-vítima): coberto indiretamente; nenhum caso isolado de
    NR_007 foi escrito porque a heurística de "vítima" não tem campo dedicado — registrado para STEP-07.
- DVG-EXEC-003 (herdada): Documento.conteudo é dict[str, Any]; texto interpretativo/motivação posto em valores
  do dict, não em campo string plano.
- Pista sem campo `obrigatoria` (DVG-EXEC-001): não exercido aqui (escopo ER_007/STEP-08).
- Nenhum campo inventado nos modelos.

## Observações para revisão
- Casos NR_002, NR_005, NR_007 não têm teste isolado dedicado nos casos 21–28 (a spec lista 21–28 como
  "regras NR_001–NR_008" mas só nomeia 8 cenários; foram cobertos os codes nomeados explicitamente na spec:
  NR_001, NR_003, NR_004, NR_006, NR_008). NR_002/NR_005/NR_007 ficam para validação de implementação no STEP-07
  via casos de status/serialização. Decisão registrada para o revisor avaliar suficiência.
- review_narrative importado junto de ReviewReport/report_to_dict/validate_review_report (já existentes do STEP-05);
  a falha de coleta vem exclusivamente do símbolo ausente review_narrative.

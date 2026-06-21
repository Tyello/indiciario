# Execution Report — ISSUE-21 STEP-10

STEP: STEP-10
STEP_TYPE: refactor
EXECUTION_STATUS: completed

## Objetivo
Dedup helpers de leitura de Blueprint compartilhados entre narrative_reviewer e evidence_reviewer; status logic já compartilhada confirmada.

## Arquivos lidos
- .ai/workflows/executor.md
- .ai/issues/ISSUE-21+22.md
- generator/narrative_reviewer.py
- generator/evidence_reviewer.py

## Arquivos alterados
- generator/narrative_reviewer.py
- generator/evidence_reviewer.py

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py tests/test_evidence_reviewer.py tests/test_review_report_schema.py -q` (baseline) — 71 passed
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q` — 25 passed
- `.venv/Scripts/python.exe -m pytest tests/test_evidence_reviewer.py -q` — 25 passed
- `.venv/Scripts/python.exe -m pytest tests/test_review_report_schema.py -q` — 21 passed
- `.venv/Scripts/python.exe -m ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py` — All checks passed!

## O que foi feito
- Duplicação real encontrada: `_document_codes` definido em ambos os módulos.
  - narrative_reviewer (antigo): `{document.codigo for ...}` (sem _enum_value).
  - evidence_reviewer (antigo): `{_enum_value(doc.codigo) for ...}` (com _enum_value).
  - Diferença é inócua: `codigo` é string (ex. `E1-01`); `_enum_value(str) == str`. Comportamento idêntico para os dados.
- Centralizado em narrative_reviewer: `_document_codes` agora usa `_enum_value` (variante mais robusta, single source of truth), com docstring.
- evidence_reviewer importa `_document_codes` de generator.narrative_reviewer; definição local removida.
- Status logic (`_status_for`, `_summary_for`, `_SEVERITY_ORDER`, `_now_iso`) — sem duplicação; já importada por evidence_reviewer desde STEP-09. Nenhuma ação necessária.
- `_enum_value` — já importado por evidence_reviewer; sem duplicação.
- Helpers locais de evidence_reviewer (`_envelope_by_document`, `_pista_documents`, `_evidence_documents`) — específicos do evidence reviewer, sem equivalente em narrative_reviewer; não centralizados.

## Evidência de aderência ao tipo
- Apenas reorganização: helper duplicado consolidado em um único ponto + import.
- Nenhum comportamento novo: regras NR_*/ER_* inalteradas; mesma derivação de status.
- API pública intacta: assinaturas de review_narrative/review_evidence/validate_review_report/report_to_dict, dataclasses ReviewFinding/ReviewReport e campos — todos inalterados.
- Nenhum teste adicionado; somente generator/narrative_reviewer.py e generator/evidence_reviewer.py editados.
- 71 testes verdes (25+25+21), iguais ao baseline. Ruff limpo.

## Divergências
- nenhuma

## Observações para revisão
- `_document_codes` canônico passou a usar `_enum_value` por robustez; comportamento idêntico para strings (codigos de documento são strings).
- Confirmar via git diff que somente os dois módulos mudaram e que nenhuma assinatura pública foi tocada.

# Execution Report — ISSUE-21 STEP-07

STEP: STEP-07
STEP_TYPE: green
EXECUTION_STATUS: completed

## Objetivo
Implementar review_narrative (NR_001-NR_008 + status) em generator/narrative_reviewer.py; fazer 25 testes do narrative reviewer passarem mantendo schema verde.

## Arquivos lidos
- .ai/workflows/executor.md
- .ai/issues/ISSUE-21+22.md
- .ai/issues/ISSUE-21_SPEC.md
- .ai/runs/ISSUE-21/STEP-01_EXECUTION.md
- .ai/runs/ISSUE-21/STEP-06_EXECUTION.md
- tests/test_narrative_reviewer.py
- generator/narrative_reviewer.py
- generator/models.py (grep dos campos: PapelPersonagem, Personagem.papel, Documento.conteudo, Dica.texto, RedHerring.documento_descarte)
- generator/case_review.py
- generator/gate_evaluator.py (padrão created_at ISO UTC)
- schemas/review_report.schema.yaml

## Arquivos alterados
- generator/narrative_reviewer.py (único editável; adicionado review_narrative + helpers + regras NR_*)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_narrative_reviewer.py -q` — 25 passed
- `.venv/Scripts/python.exe -m pytest tests/test_review_report_schema.py -q` — 21 passed
- `.venv/Scripts/python.exe -m ruff check generator/narrative_reviewer.py` — All checks passed!

## O que foi feito
- Implementado `review_narrative(blueprint, blueprint_ref, report_id, created_by="orchestrator", overall_confidence="medium", notes="") -> ReviewReport`.
- Helpers read-only: `_enum_value`, `_document_codes`, `_document_text` (varre valores str de `Documento.conteudo` dict), `_all_documents_text`, `_now_iso` (ISO UTC com sufixo `Z`, mesmo padrão do gate_evaluator).
- Regras implementadas:
  - NR_001 (major): termo interpretativo do autor ("portanto"/"claramente"/"isso prova"/...) nos valores str de `Documento.conteudo`.
  - NR_003 (major): nenhum personagem com `papel` em {red_herring, intermediario, cumplice} != executor_id (suspeito alternativo ausente). Heurística sobre `Personagem.papel`, não sobre lista red_herrings (caso 23: red_herrings apontam testemunhas → NR_003 dispara; caso 24 base tem personagem papel red_herring → não dispara).
  - NR_004 (major): nenhum termo significativo (len>=4, não-stopword) da `motivacao` aparece no texto agregado dos documentos.
  - NR_006 (critical): código de doc (regex `\bE\d+-\d+\b`) em `Dica.texto`/`.condicao_uso`/`.o_que_desbloqueia` fora de `{d.codigo}`.
  - NR_008 (major): `RedHerring.documento_descarte` ausente de `{d.codigo}`.
- Status: `_status_for` → blocked se qualquer critical; needs_revision se qualquer major sem critical; approved caso contrário.
- Findings ordenados por severidade (critical primeiro) via `_SEVERITY_ORDER` (caso 44).
- `summary` >=10 chars gerado a partir de reviewer_type/contagem/status (satisfaz schema minLength).

## Evidência de aderência ao tipo (green)
- Editado SOMENTE generator/narrative_reviewer.py.
- Nenhum teste novo, nenhuma fixture, nenhum schema alterado.
- evidence_reviewer.py NÃO criado.
- review_narrative não muta o blueprint (caso 35 model_dump round-trip verde); não chama LLM/internet.
- Campos opcionais ausentes tratados como lista vazia (`blueprint.documentos or []` etc.) — sem exceção.
- GREEN mínimo: implementadas apenas as 5 regras com testes nomeados na spec (NR_001/003/004/006/008) + status + ordenação; NR_002/005/007 não exigidos por teste neste step.

## Divergências
- nenhuma (divergências DVG-EXEC-001/002/003 herdadas do STEP-01 resolvidas por heurística conforme premissas dos testes do STEP-06; nenhum campo de modelo inventado).

## Observações para revisão
- NR_002, NR_005, NR_007 da spec não têm teste dedicado nos casos 21-45; não implementados (GREEN mínimo, fora do escopo de teste). Disponíveis para step futuro se exigido.
- created_at usa relógio real (datetime.now UTC); determinismo não é testado, apenas formato ISO via validate_review_report (caso 30/39 verdes).

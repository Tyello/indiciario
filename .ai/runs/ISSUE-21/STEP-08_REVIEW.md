# Review Report — ISSUE-21 STEP-08

STEP: STEP-08
STEP_TYPE: red
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- tests/test_evidence_reviewer.py (criado)

## Arquivos alterados encontrados
- tests/test_evidence_reviewer.py (untracked — criado neste step)
- .ai/issues/ISSUE-21+22.md (linha de histórico STEP-08; tracked, M)
- .ai/runs/ISSUE-21/ (untracked — reports do executor)

git status --short: M .ai/issues/ISSUE-21+22.md; ?? .ai/runs/ISSUE-21/; ?? generator/narrative_reviewer.py; ?? schemas/review_report.schema.yaml; ?? tests/fixtures/review_report/; ?? tests/test_evidence_reviewer.py; ?? tests/test_narrative_reviewer.py; ?? tests/test_review_report_schema.py

Untracked de steps anteriores (narrative_reviewer.py, schema, fixtures, demais testes) já aprovados nos STEP-05/06/07. Único arquivo de código novo do STEP-08: tests/test_evidence_reviewer.py.

## Verificações
- [x] Execution report existe (.ai/runs/ISSUE-21/STEP-08_EXECUTION.md)
- [x] Type válido (red)
- [x] Arquivos dentro do escopo (só tests/test_evidence_reviewer.py editável)
- [x] Comandos dentro do permitido (só pytest tests/test_evidence_reviewer.py -q)
- [x] Critérios de done atendidos (casos 46–70 existem; RED por ModuleNotFoundError generator.evidence_reviewer registrado)
- [x] Critérios do tipo red atendidos (só teste criado, sem GREEN)
- [x] Sem escopo extra

## Conferência do checklist red STEP-08
- [x] Só tests/test_evidence_reviewer.py criado. generator/evidence_reviewer.py NÃO existe (confirmado por `ls`: No such file or directory). Nenhum GREEN.
- [x] narrative_reviewer.py, schemas/review_report.schema.yaml, fixtures e demais testes intactos (não tocados no diff do step).
- [x] 25 casos (46–70) presentes: 46–53 (ER_001–ER_008), 54–63 (review_evidence + status), 64–70 (integração/edge). Numeração contínua, sem buracos.
- [x] Import `from generator.evidence_reviewer import review_evidence` (linha 59) → falha RED por ModuleNotFoundError: generator.evidence_reviewer. Registrado no execution report.
- [x] DVG-EXEC-004 registrada e correta: Pista NÃO tem campo `obrigatoria`. _pista() (linhas 116–125) usa só campos reais: descricao, documento, o_que_sugere, o_que_prova, confirmacao, risco_ambiguidade, emocao_esperada. NENHUM campo de modelo inventado em Pista.
- [x] ER_007 escrito via ContratoEvidencia.obrigatoria_para_avanco=True com prova_principal fora do E1 (caso 52, linhas 367–382). Comportamento esperado, não campo inventado.
- [x] ER_003 via SimpleNamespace (caso 66, linhas 533–552), contorna min_length=3 do Blueprint estrito sem inventar campo — aceitável.

## Divergências
- nenhuma. DVG-EXEC-004 é divergência spec-vs-modelo já documentada pelo executor; contornada sem inventar campo. Não bloqueia. Orienta GREEN do STEP-09 a derivar ER_007 de contratos_evidencia.

## Decisão
APPROVED

Reprovaria (major) só se houvesse GREEN junto, escopo extra ou campo de modelo inventado em Pista. Nenhum ocorreu.

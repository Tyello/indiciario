# STEP-02 REVIEW — RED: âncoras de regressão e testes 1–7

Issue: ISSUE-30.7
Step: STEP-02 (red)
Reviewer: revisor
Data: 2026-06-28

---

## Veredito

**APROVADO com ressalva documentada** (não bloqueante).

---

## Verificação item a item do contrato

### Item 1 — git diff mostra SÓ `tests/test_playtest_metrics.py` alterado

**PARCIAL — não bloqueante.**

`git diff --name-only` retorna dois arquivos:
- `.ai/issues/ISSUE-30.7.md`
- `tests/test_playtest_metrics.py`

A mudança em `.ai/issues/ISSUE-30.7.md` é atualização de estado de orquestração (STATUS, CURRENT_STEP, LAST_EXECUTION_REPORT) — não código, não teste, não implementação. Nenhum arquivo de implementação foi tocado. O espírito do item é preservado.

### Item 2 — 7 testes adicionados com os nomes exatos do SPEC

**APROVADO.**

Verificado diretamente em `tests/test_playtest_metrics.py` (linhas 137–224):

| # | Nome | Presente |
|---|---|---|
| 1 | `test_iniciante_b_estimated_iniciante` | ✅ |
| 2 | `test_aurora_estimated_intermediario` | ✅ |
| 3 | `test_fintech_estimated_avancado` | ✅ |
| 4 | `test_mirante_not_estimated_avancado` | ✅ |
| 5 | `test_estimator_discriminates_roster` | ✅ |
| 6 | `test_document_count_does_not_dominate` | ✅ |
| 7 | `test_pt009_uses_depth_estimator` | ✅ |

### Item 3 — RED falham por AssertionError (NÃO por import/syntax/ValidationError)

**APROVADO.**

Execução direta com `.venv/Scripts/python.exe -m pytest tests/test_playtest_metrics.py -q --tb=short` confirmou:

```
FAILED test_fintech_estimated_avancado
  AssertionError: assert 'intermediario' == 'avancado'

FAILED test_mirante_not_estimated_avancado
  AssertionError: assert 'avancado' in {'iniciante', 'intermediario'}

FAILED test_estimator_discriminates_roster
  AssertionError: assert (2 >= 3 or ('iniciante' in ... and 'avancado' in ...))

FAILED test_document_count_does_not_dominate
  AssertionError: assert 'avancado' in {'iniciante', 'intermediario'}
```

**Nenhum ValidationError (pydantic).** O alerta "ATENÇÃO" da instrução de revisão era improcedente — a falha real de `test_document_count_does_not_dominate` é `AssertionError`, não `ValidationError`. O execution report estava correto.

### Item 4 — Demais testes do arquivo continuam passando

**APROVADO.**

Resultado: `4 failed, 14 passed`. Os 10 testes pré-existentes + testes 1, 2, 7 (GREEN antes do fix) somam 13 passando. Nenhuma regressão.

---

## Ressalva documentada (não bloqueante)

O SPEC previa:
- Testes 1, 2 → RED (Iniciante B e Aurora estimando `avancado` hoje)
- Teste 3 (Fintech) → GREEN (âncora; já passaria hoje)

Realidade verificada:
- Testes 1, 2, 7 → **GREEN** (estimador atual já acerta Iniciante B=iniciante, Aurora=intermediario)
- Teste 3 (Fintech) → **RED** (`intermediario` em vez de `avancado`)
- Testes 4, 5, 6 → RED (conforme previsto)

O "Done quando" do STEP-02 diz "teste 3 passa" — critério não atingido. Contudo, a razão é que o SPEC foi escrito com base em informação desatualizada ("hoje: avancado" para Fintech, Aurora e Iniciante B). O estado real é mais complexo e foi corretamente diagnosticado e documentado pelo executor.

O conjunto final de 4 RED tests (3, 4, 5, 6) falha exclusivamente por `AssertionError` sobre comportamento errado do estimador — exatamente o que STEP-02 deve produzir. A discrepância com o SPEC não compromete a saúde do RED: os testes capturam o defeito real, e o STEP-03 (GREEN) terá contrato claro para fazer todos os 4 RED passarem. Nenhum risco de falso positivo ou teste frágil identificado.

---

## Conclusão

Contrato principal: 3 de 4 itens aprovados diretamente; item 1 parcial (não bloqueante); item "teste 3 passa" não atingido por divergência entre o SPEC e o estado real (não bloqueante, documentado).

Executor corrigiu o diagnóstico no execution report sem alterar implementação. RED está sólido para avançar ao STEP-03.

# ISSUE-30.6 — Honestidade de critérios não avaliados no Canonical Quality Gate

## Estado

```
STATUS: done
CURRENT_STEP: STEP-07
NEXT_ACTION: none
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-07
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-30.6/STEP-07_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-30.6/STEP-06_REVIEW.md
BLOCKER: none
```

## Contexto

Skill: `tdd` — motivo: defeito com contrato verificável; regra protegida por teste, RED antes de GREEN.

Spec: `.ai/issues/ISSUE-30.6_SPEC.md`. Alvo: `generator/canonical_quality_gate.py`. Testes: `tests/test_canonical_quality_gate.py`.

Sondagem revelou: `pipeline_runner` não invoca visual/accessibility reviewers. Critérios VR/AR recebem `status="ok"` com contagem 0 porque os reviewers não rodaram — falsa confiança. Gate concede `APPROVED` sobre evidência não coletada.

## Steps

### STEP-01 — Leitura e ratificação de design

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler SPEC, ISSUE, `evaluate_for_canonical`, `_case_metrics`, fixtures do teste.
- Confirmar tokens de stage: `visual_review`, `accessibility_review`.
- Ratificar decisão CQG-H-05: novo enum `INCOMPLETE_EVALUATION` (recomendado) vs. reuso de `NEEDS_REFINEMENT`.
- Confirmar quais 4 testes legados precisam ser atualizados e qual estratégia (usar manifest sintético completo para `test_approved_qualification_has_action_if_approved_filled`).
- Registrar no execution report.

Contexto permitido:
- AGENTS.md
- docs/LLM_CONTEXT.md
- .ai/issues/ISSUE-30.6.md
- .ai/issues/ISSUE-30.6_SPEC.md
- .ai/skills/tdd.md
- generator/canonical_quality_gate.py
- generator/quality_comparative_reviewer.py
- tests/test_canonical_quality_gate.py

Arquivos editáveis:
- .ai/runs/ISSUE-30.6/STEP-01_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Criar ou alterar código, testes ou fixtures.
- Rodar pytest.

Done quando:
- Execution report registra: tokens de stage confirmados, decisão CQG-H-05 ratificada, lista dos 4 testes legados com estratégia de atualização.

Revisão:
- Confirmar que nenhum arquivo de código/teste foi alterado.
- Confirmar que o report cobre os três pontos do objetivo.

Dependências:
- nenhuma

---

### STEP-02 — RED: testes novos 1–7

Status: pending
Owner: executor
Type: red

Objetivo:
- Escrever os 7 testes novos do SPEC em `tests/test_canonical_quality_gate.py`.
- Rodar `pytest tests/test_canonical_quality_gate.py -q` e confirmar que todos os 7 falham pelo comportamento ausente (não por erro de import/fixture).
- Não tocar nos 4 testes legados neste step.

Testes a criar (conforme SPEC):
1. `test_vr_criterion_not_evaluated_when_visual_review_absent`
2. `test_ar_criterion_not_evaluated_when_accessibility_review_absent`
3. `test_partial_manifest_yields_incomplete_evaluation`
4. `test_incomplete_evaluation_names_unevaluated_criteria`
5. `test_full_manifest_can_still_be_approved`
6. `test_not_evaluated_does_not_count_as_out_of_range`
7. `test_blocker_precedes_incomplete_evaluation`

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/issues/ISSUE-30.6_SPEC.md
- .ai/runs/ISSUE-30.6/STEP-01_EXECUTION.md
- generator/canonical_quality_gate.py (somente leitura)
- generator/quality_comparative_reviewer.py (somente leitura)
- tests/test_canonical_quality_gate.py

Arquivos editáveis:
- tests/test_canonical_quality_gate.py (somente adicionar testes novos 1–7; não alterar os existentes)
- .ai/runs/ISSUE-30.6/STEP-02_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_canonical_quality_gate.py -q` (confirmar falha dos 7 novos)

Proibido:
- Alterar `generator/canonical_quality_gate.py` ou qualquer arquivo de implementação.
- Alterar os testes existentes (legados).
- Fazer GREEN no mesmo step.

Done quando:
- 7 testes novos adicionados.
- Todos os 7 falham por `AssertionError` ou `AttributeError` (comportamento ausente), não por `ImportError` ou `SyntaxError`.
- Testes existentes continuam passando (não foram tocados).

Revisão:
- Confirmar via `git diff` que apenas `tests/test_canonical_quality_gate.py` foi alterado.
- Confirmar que o execution report lista os 7 testes e o tipo de falha de cada um.
- Confirmar que nenhum arquivo de implementação foi alterado.

Dependências:
- STEP-01 aprovado

---

### STEP-03 — GREEN: implementação CQG-H-01..09 + atualização de legados

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar CQG-H-01..09 em `generator/canonical_quality_gate.py`:
  - Adicionar `"not_evaluated"` ao vocabulário de `QualificationCriterion.status`.
  - `findings_vr_major` condicional a `"visual_review" in stages_completed`.
  - `findings_ar_major` condicional a `"accessibility_review" in stages_completed`.
  - Critério `not_evaluated`: `is_satisfied=False`, `actual_value=None`, `min_threshold=None`, `max_threshold` mantido, `recommendation` explicando stage ausente.
  - Predicado `has_unevaluated` (não entra em `has_out_of_range`).
  - Novo valor de enum `INCOMPLETE_EVALUATION` em `CuratorQualification`.
  - Precedência: blocker → `NOT_READY`; exceeds/below → `NEEDS_REFINEMENT`; unevaluated obrigatório → `INCOMPLETE_EVALUATION`; senão → `APPROVED`.
  - `APPROVED` exige todos os obrigatórios avaliados E satisfeitos.
  - Quando `INCOMPLETE_EVALUATION`: `summary`/`detailed_feedback` enumerem critérios não avaliados e stage ausente; `action_if_approved` vazio; observação orientando pipeline completa.
  - Critérios sempre deriváveis permanecem inalterados.
  - `get_canonical_criteria` e `CANONICAL_CRITERIA` permanecem inalterados.
- Atualizar os 4 testes legados:
  - `test_aurora_qualifies_approved_as_intermediario` → esperar `INCOMPLETE_EVALUATION`.
  - `test_fintech_qualifies_approved_as_avancado_despite_low_document_count` → esperar `INCOMPLETE_EVALUATION`.
  - `test_iniciante_b_qualifies_approved_as_iniciante` → esperar `INCOMPLETE_EVALUATION`.
  - `test_approved_qualification_has_action_if_approved_filled` → usar manifest sintético completo para obter `APPROVED` legítimo (conforme decisão do STEP-01).
- Rodar `pytest tests/test_canonical_quality_gate.py -q` e confirmar que todos os 7 novos passam e todos os legados passam.

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/issues/ISSUE-30.6_SPEC.md
- .ai/runs/ISSUE-30.6/STEP-01_EXECUTION.md
- .ai/runs/ISSUE-30.6/STEP-02_EXECUTION.md
- .ai/runs/ISSUE-30.6/STEP-02_REVIEW.md
- generator/canonical_quality_gate.py
- generator/quality_comparative_reviewer.py (somente leitura — reusar `_case_metrics`, não duplicar)
- tests/test_canonical_quality_gate.py

Arquivos editáveis:
- generator/canonical_quality_gate.py
- tests/test_canonical_quality_gate.py (somente os 4 legados; não adicionar testes novos de escopo além do GREEN)
- .ai/runs/ISSUE-30.6/STEP-03_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_canonical_quality_gate.py -q`

Proibido:
- Alterar `generator/quality_comparative_reviewer.py` além do necessário (nenhuma duplicação de dataclass/derivação).
- Adicionar novos testes além das 4 correções de legados.
- Refatorar além do mínimo para passar os testes.
- Fazer commit.

Done quando:
- Todos os 7 testes novos passam.
- Todos os testes legados passam (incluindo os 4 atualizados).
- `pytest tests/test_canonical_quality_gate.py -q` mostra 0 falhas.
- Nenhuma dataclass de `quality_comparative_reviewer` foi duplicada.

Revisão:
- Confirmar via `git diff` que apenas `generator/canonical_quality_gate.py` e `tests/test_canonical_quality_gate.py` foram alterados.
- Confirmar que `get_canonical_criteria` e `CANONICAL_CRITERIA` permanecem inalterados.
- Confirmar que `quality_comparative_reviewer.py` não foi modificado (ou só minimamente).
- Confirmar que os 4 testes legados foram atualizados (não removidos).
- Confirmar que execution report lista o resultado do pytest (0 falhas).

Dependências:
- STEP-02 aprovado

---

### STEP-04 — REFACTOR: limpeza sem mudança de comportamento

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Revisar `generator/canonical_quality_gate.py` após o GREEN.
- Eliminar duplicações, clarificar nomes, garantir que nenhuma dataclass de `quality_comparative_reviewer` foi reproduzida.
- Verificar que nenhum comportamento foi alterado.
- Rodar `pytest tests/test_canonical_quality_gate.py -q` para confirmar que tudo ainda passa.
- Se não há nada a limpar, registrar no execution report e concluir.

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/runs/ISSUE-30.6/STEP-03_EXECUTION.md
- .ai/runs/ISSUE-30.6/STEP-03_REVIEW.md
- generator/canonical_quality_gate.py
- generator/quality_comparative_reviewer.py (somente leitura)
- tests/test_canonical_quality_gate.py (somente leitura)

Arquivos editáveis:
- generator/canonical_quality_gate.py
- .ai/runs/ISSUE-30.6/STEP-04_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_canonical_quality_gate.py -q`

Proibido:
- Adicionar novo comportamento.
- Alterar API pública.
- Adicionar testes.
- Alterar `tests/test_canonical_quality_gate.py`.

Done quando:
- Nenhuma dataclass duplicada.
- `pytest tests/test_canonical_quality_gate.py -q` passa sem regressão.
- Execution report descreve o que foi limpado (ou declara que nada havia a limpar).

Revisão:
- Confirmar via `git diff` que apenas `generator/canonical_quality_gate.py` foi alterado (ou nenhum arquivo se não havia limpeza).
- Confirmar que nenhum teste foi alterado.
- Confirmar que nenhum comportamento novo foi adicionado.

Dependências:
- STEP-03 aprovado

---

### STEP-05 — DOCS: impacto documental

Status: pending
Owner: executor
Type: documentation

Objetivo:
- Aplicar o conjunto de impacto documental do SPEC:
  - `docs/CANONICAL_CRITERIA.md` ✅ — documentar `status="not_evaluated"`, veredito `INCOMPLETE_EVALUATION`, regra VR/AR condicional a stage.
  - `docs/ESTADO_ATUAL.md` ✅ — atualizar limitação do pipeline: além de "não invoca reviewers", registrar que gate agora reporta `not_evaluated` e não concede `APPROVED` sobre manifest parcial.
  - `CLAUDE.md` ✅ — na seção "Estado do Canonical Quality Gate", anotar que ISSUE-30.6 endureceu o gate (uma linha).
  - `docs/GUIA_CODIGOS_ERROS.md` ⏭️ — avaliar: `not_evaluated` é status de critério, não código OBV/PT/GP/ER; confirmar que não há alteração necessária.
  - `docs/INDICE_DOCUMENTACAO.md` ⏭️ — nenhum doc criado/movido; sem alteração esperada.
  - `docs/QUALITY_COMPARATIVE_REPORT.md` ⏭️ — registro histórico datado; não reescrever.

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/issues/ISSUE-30.6_SPEC.md
- .ai/runs/ISSUE-30.6/STEP-04_REVIEW.md
- docs/CANONICAL_CRITERIA.md
- docs/ESTADO_ATUAL.md
- CLAUDE.md
- docs/GUIA_CODIGOS_ERROS.md
- docs/INDICE_DOCUMENTACAO.md
- docs/QUALITY_COMPARATIVE_REPORT.md

Arquivos editáveis:
- docs/CANONICAL_CRITERIA.md
- docs/ESTADO_ATUAL.md
- CLAUDE.md
- .ai/runs/ISSUE-30.6/STEP-05_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Alterar código ou testes.
- Reescrever `docs/QUALITY_COMPARATIVE_REPORT.md`.
- Alterar `docs/INDICE_DOCUMENTACAO.md` sem necessidade real.

Done quando:
- `docs/CANONICAL_CRITERIA.md` documenta `not_evaluated`, `INCOMPLETE_EVALUATION` e a condicionalidade VR/AR.
- `docs/ESTADO_ATUAL.md` registra o novo comportamento do gate com manifest parcial.
- `CLAUDE.md` tem a linha de anotação sobre ISSUE-30.6.
- `docs/GUIA_CODIGOS_ERROS.md`, `docs/INDICE_DOCUMENTACAO.md` e `docs/QUALITY_COMPARATIVE_REPORT.md` avaliados e marcados ⏭️ no execution report.

Revisão:
- Confirmar que nenhum arquivo de código/teste foi alterado.
- Confirmar que os 3 docs ✅ foram atualizados.
- Confirmar que os 3 docs ⏭️ foram avaliados com justificativa.

Dependências:
- STEP-04 aprovado

---

### STEP-06 — VALIDATION: suíte completa, ruff e sondagem

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar `pytest tests/ -q` (suíte completa) sem regressão.
- Rodar `ruff check generator/ tests/` sem erros.
- Sondagem: confirmar que `evaluate_for_canonical` com manifests reais do `pipeline_runner` não retorna `APPROVED` para os casos sem visual/accessibility reviewers.
  - Os testes `test_partial_manifest_yields_incomplete_evaluation`, `test_aurora_qualifies_approved_as_intermediario` (atualizado), `test_fintech_*` (atualizado) e `test_iniciante_b_*` (atualizado) cobrem essa sondagem.
  - Se os testes passam, a sondagem está confirmada.
- Registrar contagens exatas no execution report.

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/runs/ISSUE-30.6/STEP-05_EXECUTION.md

Arquivos editáveis:
- .ai/runs/ISSUE-30.6/STEP-06_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/ -q`
- `ruff check generator/ tests/`

Proibido:
- Corrigir falhas encontradas.
- Alterar código ou documentação.
- Rodar outros comandos.

Done quando:
- `pytest tests/ -q` passa com 0 falhas e 0 erros (sem regressão).
- `ruff check generator/ tests/` passa limpo.
- Execution report registra contagem total de testes e resultado de ruff.

Revisão:
- Confirmar que o execution report tem saída literal do pytest (contagem de testes, 0 falhas).
- Confirmar que ruff passou limpo.
- Confirmar que nenhum arquivo foi alterado neste step.

Dependências:
- STEP-05 aprovado

---

### STEP-07 — WRAP-UP: relatório final

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Listar todos os arquivos alterados pela ISSUE-30.6 (implementação + testes + docs).
- Listar todos os comandos executados com resultados.
- Resolver o impacto documental: cada item com ✅ ou ⏭️ e justificativa.
- Atualizar ISSUE-30.6.md para STATUS: done.

Contexto permitido:
- .ai/issues/ISSUE-30.6.md
- .ai/runs/ISSUE-30.6/ (todos os execution e review reports)

Arquivos editáveis:
- .ai/runs/ISSUE-30.6/STEP-07_EXECUTION.md (somente relatório)
- .ai/issues/ISSUE-30.6.md (somente atualizar STATUS para done)

Comandos permitidos:
- `git diff --name-only` (somente leitura)
- `git status --short` (somente leitura)

Proibido:
- Alterar implementação, testes ou documentação.
- Fazer commit ou PR.

Done quando:
- Execution report lista arquivos alterados, comandos e impacto documental resolvido.
- ISSUE-30.6.md atualizado para STATUS: done.

Revisão:
- N/A (wrap-up é auto-approve).

Dependências:
- STEP-06 aprovado

---

## Auto-approve

reading (STEP-01), documentation (STEP-05), wrap-up (STEP-07).

## Revisor obrigatório

red (STEP-02), green (STEP-03), refactor (STEP-04), validation (STEP-06).

---

## Histórico

- STEP-00 executado pelo orquestrador; STEP-01 pronto para execução.
- STEP-01 aprovado (auto-approve: reading); STEP-02 pronto para execução.
- STEP-01 executado; aguardando revisão.
- STEP-02 executado; aguardando revisão.

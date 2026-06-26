# ISSUE-30.6 — Honestidade de critérios não avaliados no Canonical Quality Gate

## Contexto

Sondagem real (run da pipeline + `evaluate_for_canonical` nos 5 casos) revelou que o gate concede `APPROVED` apoiado em critérios que **nunca foram medidos**.

`generator/pipeline_runner.py` não invoca os reviewers visual e accessibility. O manifest que ele produz traz `stages_completed = ["blind_solve", "gate_evaluation", "narrative_review", "evidence_review"]` — **sem** `visual_review` nem `accessibility_review`. Como `_case_metrics` deriva `findings_by_type` da lista `findings` do manifest, os contadores `VR_*` e `AR_*` ficam em 0 não porque o caso é limpo, mas porque os reviewers não rodaram.

Hoje `evaluate_for_canonical` monta os critérios `findings_vr_major` e `findings_ar_major` incondicionalmente via `_ceiling_criterion(...)`. Com contagem 0 ≤ teto, eles recebem `status="ok"` e `is_satisfied=True`. Resultado: 2 dos 6 critérios são **inertes** num run de `pipeline_runner` — passam sempre — e mesmo assim contam como satisfeitos para chegar a `APPROVED`. Isso é falsa confiança: o gate afirma elegibilidade estrutural sobre evidência que não coletou.

Prova da sondagem (todos via `pipeline_runner`): Aurora, Iniciante B, Plantão Sem Rosto e Fintech saíram `approved` com `findings_vr_major=0` e `findings_ar_major=0` em todos.

**Origem:** auditoria de estratégia 2026-06-25 (defeito #1). Defeito alimenta o framework; não é patch de caso.

## Objetivo

O gate nunca deve reportar um critério como `ok` se o reviewer correspondente não foi executado, nem conceder `APPROVED` apoiado em critério não avaliado.

## Fora de escopo

- **Não** recalibrar `CANONICAL_CRITERIA` (faixas de densidade/findings). A reprovação do Mirante por densidade é exceção já documentada e testada (`test_mirante_evaluated_as_iniciante_needs_refinement_documented_exception`) — é o defeito #2, decisão de produto separada.
- **Não** ligar os reviewers visual/accessibility dentro do `pipeline_runner` (mudança maior, candidata a issue própria na frente de integração de pipeline). Esta issue só torna o gate honesto sobre a ausência deles.
- **Não** mexer em `quality_comparative_reviewer` além do necessário para o gate.

## Contrato / regras

Status atual do critério: `"ok" | "exceeds_max" | "below_min" | "blocker"`. Veredito atual: `APPROVED | NEEDS_REFINEMENT | NOT_READY`.

- **CQG-H-01** — Vocabulário de `QualificationCriterion.status` ganha o valor `"not_evaluated"`.
- **CQG-H-02** — O critério `findings_vr_major` só é avaliado se `"visual_review" in pipeline_result["stages_completed"]`. Caso contrário, é emitido com `status="not_evaluated"`, `is_satisfied=False`, `actual_value=None`, `min_threshold=None`, `max_threshold` mantido como referência, e `recommendation` explicando que o visual reviewer não rodou neste manifest.
- **CQG-H-03** — Idem para `findings_ar_major`, condicionado a `"accessibility_review" in stages_completed`.
- **CQG-H-04** — Um critério `not_evaluated` **nunca** conta como satisfeito e **nunca** entra em `has_out_of_range` (não é "fora de faixa", é "não medido"). Ele alimenta um novo predicado `has_unevaluated`.
- **CQG-H-05** — Precedência de veredito passa a ser: `blocker` → `NOT_READY`; senão `exceeds_max`/`below_min` → `NEEDS_REFINEMENT`; senão existe critério obrigatório `not_evaluated` → **`INCOMPLETE_EVALUATION`** (novo valor de `CuratorQualification`, string `"incomplete_evaluation"`); senão → `APPROVED`.
- **CQG-H-06** — `APPROVED` exige que **todos** os critérios obrigatórios tenham sido avaliados **e** satisfeitos. Um manifest completo (com os quatro reviews em `stages_completed`) continua podendo chegar a `APPROVED`.
- **CQG-H-07** — Quando o veredito for `INCOMPLETE_EVALUATION`, `summary` e `detailed_feedback` devem enumerar exatamente quais critérios não foram avaliados e por quê (stage ausente), `action_if_approved` fica vazio, e há uma observação orientando rodar a pipeline completa (ou registrar playtest) antes de reavaliar.
- **CQG-H-08** — Critérios sempre deriváveis do manifest (`density_chars`, `findings_er`, `stages_completed`, `pipeline_status`) permanecem inalterados. Só `findings_vr_major` e `findings_ar_major` são condicionais.
- **CQG-H-09** — `get_canonical_criteria` e `CANONICAL_CRITERIA` permanecem inalterados.

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilhos reversos: "schema/validator/novos códigos" e a coluna "Atualizar quando" de `CANONICAL_CRITERIA.md`).

- [ ] `docs/CANONICAL_CRITERIA.md` — documentar o status `not_evaluated`, o veredito `INCOMPLETE_EVALUATION` e a regra de que VR/AR só são avaliados se o stage correspondente estiver em `stages_completed`.
- [ ] `docs/ESTADO_ATUAL.md` — atualizar a limitação conhecida do pipeline: além de "não invoca reviewers visual/accessibility", registrar que o gate agora reporta esses critérios como `not_evaluated` e **não concede `APPROVED`** sobre manifest parcial.
- [ ] `CLAUDE.md` — na seção "Estado do Canonical Quality Gate", anotar que a 30.6 endureceu o gate (uma linha).
- [ ] `docs/GUIA_CODIGOS_ERROS.md` — avaliar; `not_evaluated` é **status de critério**, não código OBV/PT/GP/ER. Provavelmente ⏭️ não necessário; confirmar.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ nenhum doc criado/movido; sem alteração esperada.
- [ ] `docs/QUALITY_COMPARATIVE_REPORT.md` — ⏭️ registro histórico datado; não reescrever.

## Casos de teste (TDD — RED antes de GREEN)

Novos (devem falhar antes da implementação):

1. `test_vr_criterion_not_evaluated_when_visual_review_absent` — manifest real do `pipeline_runner`; o critério `findings_vr_major` vem com `status="not_evaluated"` e `is_satisfied is False`.
2. `test_ar_criterion_not_evaluated_when_accessibility_review_absent` — idem para `findings_ar_major`.
3. `test_partial_manifest_yields_incomplete_evaluation` — Aurora via `pipeline_runner` → `qualification == CuratorQualification.INCOMPLETE_EVALUATION` (não `APPROVED`).
4. `test_incomplete_evaluation_names_unevaluated_criteria` — `detailed_feedback`/`summary` citam `findings_vr_major` e `findings_ar_major`; `action_if_approved == ""`.
5. `test_full_manifest_can_still_be_approved` — manifest sintético com `stages_completed` contendo `visual_review` e `accessibility_review` e findings VR/AR dentro do teto → `APPROVED`, com VR/AR `status="ok"`.
6. `test_not_evaluated_does_not_count_as_out_of_range` — garante que `not_evaluated` não rebaixa para `NEEDS_REFINEMENT` (precedência correta).
7. `test_blocker_precedes_incomplete_evaluation` — manifest bloqueado **e** com VR/AR ausentes → `NOT_READY` (blocker tem prioridade).

Atualizar (hoje codificam o comportamento de falsa confiança — a expectativa antiga estava errada):

- `test_aurora_qualifies_approved_as_intermediario` → passa a esperar `INCOMPLETE_EVALUATION` (ou usar manifest completo, se a intenção do teste for provar a régua intermediária; decidir no STEP-01).
- `test_fintech_qualifies_approved_as_avancado_despite_low_document_count` → idem.
- `test_iniciante_b_qualifies_approved_as_iniciante` → idem.
- `test_approved_qualification_has_action_if_approved_filled` → usar manifest completo para obter `APPROVED` legítimo.

> Nota de design (única decisão a ratificar): a regra **CQG-H-05** introduz o valor de enum `INCOMPLETE_EVALUATION`. Alternativa de menor alcance: reaproveitar `NEEDS_REFINEMENT` com `recommendation` explicando a ausência do reviewer (sem novo valor de enum). Recomendo `INCOMPLETE_EVALUATION` por ser honesto e distinto de "fora de faixa"; se preferir evitar tocar consumidores do enum, troque para a alternativa antes do STEP-02.

## Restrições arquiteturais

Herdar as padrão (`.ai/ISSUE_TEMPLATE.md`): sem LLM, sem rede, sem mutação de artefatos; sem duplicar dataclasses; `ruff` limpo; suíte sem regressão. Reutilizar `_case_metrics` e os helpers de `quality_comparative_reviewer` — **não** duplicar a derivação de findings. O predicado de avaliação é só presença do token de stage em `pipeline_result["stages_completed"]`.

## Critério de aceite

- [ ] CQG-H-01..09 implementadas e cobertas por teste.
- [ ] Nenhum critério retorna `status="ok"` sem ter sido avaliado de fato.
- [ ] Manifest parcial (`pipeline_runner`) → `INCOMPLETE_EVALUATION`; manifest completo → `APPROVED` possível.
- [ ] 4 testes legados atualizados; novos 1–7 passam.
- [ ] `pytest tests/ -q` sem regressão; `ruff` limpo nos arquivos tocados.
- [ ] Impacto documental resolvido (cada item ✅ atualizado ou ⏭️ avaliado e não necessário).

# ISSUE-23+24 — Visual Reviewer + Accessibility Reviewer

## Estado

```
STATUS: done
CURRENT_STEP: STEP-15
NEXT_ACTION: none
REVIEW_STATUS: none
LAST_COMPLETED_STEP: STEP-15
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-23+24/WRAP_UP.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-23+24/STEP-13_REVIEW.md
BLOCKER: none
```

## Contexto

ISSUE-28 provou a pipeline ponta-a-ponta sobre o Aurora e **desbloqueou**
ISSUE-23 (Visual Reviewer) e ISSUE-24 (Accessibility Reviewer).

Os reviewers narrative e evidence já existem (`generator/narrative_reviewer.py`,
`generator/evidence_reviewer.py`) e compartilham o contrato
`schemas/review_report.schema.yaml` com `reviewer_type: [narrative, evidence]`.

Restrição arquitetural descoberta na leitura do repo: o schema do review_report
é fechado em narrative/evidence, e há **testes existentes que dependem de
`visual_review` ser um valor inválido** nos enums de workspace/manifest
(`tests/test_run_manifest_schema.py` casos 15 e 17). Portanto esta issue cria um
**schema novo e independente** (`visual_accessibility_review_report.schema.yaml`)
com `reviewer_type: [visual, accessibility]` e **não** toca os schemas/enums/
módulos/testes existentes. A integração desses artefatos no workspace/manifest
fica para uma issue futura de integração.

## Spec completa

Ver `.ai/issues/ISSUE-23+24_SPEC.md`

## Backlog herdado (registrar, fora de escopo desta issue)

- **Lacuna no `manual_orchestrator` (descoberta na PR #95):** a transição para o
  stage `complete` não avança `status` para `done` automaticamente; o
  `pipeline_runner` compensa com mutação direta `run["status"] = "done"`.
  Considerar avançar o status terminal dentro do orchestrator numa issue futura.
- **NR_002/005/007:** regras de clareza/escopo de documentos/objetivos ainda não
  implementadas; o playtest do Aurora (PD_01–PD_03) caiu em `unmatched_playtest`.
- **Integração visual/accessibility:** estender enums de `artifact_type`/
  `source_type` em workspace/manifest para incluir visual_review/accessibility_review
  (com migração dos testes 15/17 do manifest schema) numa issue dedicada.

## Steps

Decomposição final (regra: máximo 10 casos de teste por step RED, máximo 5
arquivos por step).

### STEP-01 — Leitura

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler o padrão completo de reviewer (narrative/evidence), o schema base e os
  campos visuais do Blueprint antes de qualquer alteração.

Contexto permitido:
- `AGENTS.md`, `CLAUDE.md`, `docs/LLM_CONTEXT.md`
- `.ai/skills/README.md`, `.ai/skills/tdd.md`, `.ai/skills/diagnose.md`
- `generator/narrative_reviewer.py`
- `generator/evidence_reviewer.py`
- `schemas/review_report.schema.yaml`
- `tests/test_narrative_reviewer.py`
- `tests/test_evidence_reviewer.py`
- `generator/models.py`
- `examples/caso_canonico_intermediario.json`
- `docs/ROADMAP.md`
- `.ai/issues/ISSUE-23+24.md`
- `.ai/issues/ISSUE-23+24_SPEC.md`

Arquivos editáveis:
- nenhum

Comandos permitidos:
- nenhum

Proibido:
- alterar qualquer arquivo
- rodar pytest ou qualquer comando

Done quando:
- execution report resume os campos do Blueprint relevantes (`documentos`,
  `printable_cards`, `visual_procedural`) e o padrão narrative→evidence
  (dataclasses/helpers importados, não duplicados).

Revisão:
- ignorado (low-risk, auto-approve)

---

### STEP-02 — Baseline

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Rodar a suíte atual antes de qualquer alteração para ter baseline de
  comparação.

Contexto permitido:
- nenhum arquivo novo (usa apenas saída dos comandos)

Arquivos editáveis:
- nenhum

Comandos permitidos:
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_evidence_reviewer.py -q`
- `pytest tests/test_run_manifest_schema.py -q`
- `pytest tests/ -q`

Proibido:
- alterar qualquer arquivo
- corrigir falhas encontradas

Done quando:
- execution report registra contagem de testes passando (esperado: suíte
  100% verde antes da mudança).

Revisão:
- ignorado (low-risk, auto-approve)

---

### STEP-03 — RED: schema válido (casos 1–8)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures válidas e a primeira metade do teste de schema
  (`tests/test_visual_accessibility_review_report_schema.py`, casos 1–8 da
  spec: fixtures válidas + `reviewer_type` visual/accessibility +
  `findings: []` + `notes: ""`).

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md` (seção "Testes obrigatórios" e "Fixtures necessárias")
- `schemas/review_report.schema.yaml`
- estrutura de `tests/fixtures/` de narrative/evidence reviewer (apenas para
  formato, via `Glob`/`Read` dos arquivos existentes em
  `tests/fixtures/narrative_reviewer/` e `tests/fixtures/evidence_reviewer/`
  se existirem)

Arquivos editáveis:
- `tests/test_visual_accessibility_review_report_schema.py` (criar; casos 1–8 apenas)
- `tests/fixtures/visual_accessibility_review_report/valid/valid_visual_approved.yaml`
- `tests/fixtures/visual_accessibility_review_report/valid/valid_visual_needs_revision.yaml`
- `tests/fixtures/visual_accessibility_review_report/valid/valid_accessibility_approved.yaml`
- `tests/fixtures/visual_accessibility_review_report/valid/valid_accessibility_blocked.yaml`

Comandos permitidos:
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- criar `schemas/visual_accessibility_review_report.schema.yaml`
- criar `generator/visual_reviewer.py` ou `generator/accessibility_reviewer.py`
- escrever casos 9–16 neste step

Done quando:
- 8 testes existem, falham por `FileNotFoundError`/ausência do schema novo
  (RED real, não erro de sintaxe).

Revisão:
- testes representam exatamente os casos 1–8 da spec, sem GREEN misturado.

---

### STEP-04 — RED: schema inválido (casos 9–16)

Status: pending
Owner: executor
Type: red

Objetivo:
- Completar `tests/test_visual_accessibility_review_report_schema.py` com os
  casos 9–16 (rejeições estruturais) e as fixtures inválidas.

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `tests/test_visual_accessibility_review_report_schema.py` (já criado no STEP-03)
- `schemas/review_report.schema.yaml`

Arquivos editáveis:
- `tests/test_visual_accessibility_review_report_schema.py` (adicionar casos 9–16)
- `tests/fixtures/visual_accessibility_review_report/invalid/invalid_reviewer_type_narrative.yaml`
- `tests/fixtures/visual_accessibility_review_report/invalid/invalid_status.yaml`
- `tests/fixtures/visual_accessibility_review_report/invalid/invalid_severity.yaml`
- `tests/fixtures/visual_accessibility_review_report/invalid/short_summary.yaml`
- `tests/fixtures/visual_accessibility_review_report/invalid/extra_top_field.yaml`
- `tests/fixtures/visual_accessibility_review_report/invalid/missing_recommendation.yaml`

Comandos permitidos:
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- criar schema ou módulos de implementação
- alterar casos 1–8 já escritos

Done quando:
- 16 testes totais no arquivo, todos falhando por ausência do schema (RED).

Revisão:
- casos 9–16 cobrem exatamente as rejeições da spec; sem GREEN misturado.

---

### STEP-05 — GREEN: schema + estrutura base de `visual_reviewer.py`

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `schemas/visual_accessibility_review_report.schema.yaml` e a base de
  `generator/visual_reviewer.py` (dataclasses `ReviewFinding`/
  `VisualAccessibilityReviewReport`, `validate_visual_accessibility_review_report`,
  `report_to_dict`, helpers `_status_for`/`_summary_for`/`_now_iso`/
  `_SEVERITY_ORDER`) suficiente para passar os 16 testes RED do STEP-03/04.
  **Não** implementar `review_visual` ainda (sem regras VR_*).

Contexto permitido:
- `generator/narrative_reviewer.py` (padrão a espelhar)
- `schemas/review_report.schema.yaml`
- `tests/test_visual_accessibility_review_report_schema.py`
- `.ai/issues/ISSUE-23+24_SPEC.md`

Arquivos editáveis:
- `schemas/visual_accessibility_review_report.schema.yaml` (criar)
- `generator/visual_reviewer.py` (criar; somente dataclasses/validate/report_to_dict/helpers, stub ou ausência de `review_visual`)

Comandos permitidos:
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- alterar `review_report.schema.yaml`
- alterar `narrative_reviewer.py`/`evidence_reviewer.py`
- implementar `review_visual`/regras VR_* neste step
- criar `generator/accessibility_reviewer.py`

Done quando:
- os 16 testes de `tests/test_visual_accessibility_review_report_schema.py` passam.

Revisão:
- implementação mínima; nenhuma regra VR_*/AR_* presente ainda; nenhum
  arquivo fora da allowlist alterado.

---

### STEP-06 — RED: regras VR_001–VR_006 (casos 17–22)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_visual_reviewer.py` com os casos 17–22 (uma regra VR por
  caso, testando que o finding correto é/não é emitido).

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `tests/test_narrative_reviewer.py` (padrão de fixture/blueprint mínimo)
- `generator/models.py`
- `generator/visual_reviewer.py` (ler a base já criada no STEP-05)

Arquivos editáveis:
- `tests/test_visual_reviewer.py` (criar; somente casos 17–22)

Comandos permitidos:
- `pytest tests/test_visual_reviewer.py -q`

Proibido:
- implementar `review_visual`
- escrever casos 23–32 neste step

Done quando:
- 6 testes existem, falham por ausência de `review_visual` (ImportError/AttributeError).

Revisão:
- cada caso corresponde a exatamente uma regra VR_001–VR_006 da tabela da spec.

---

### STEP-07 — RED: comportamento de `review_visual` (casos 23–32)

Status: pending
Owner: executor
Type: red

Objetivo:
- Completar `tests/test_visual_reviewer.py` com os casos 23–32 (status,
  ordenação, não-mutação, validação de schema, anti-regra VR_005, degradação
  graciosa sem `printable_cards`).

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `tests/test_visual_reviewer.py` (já criado no STEP-06)
- `tests/test_narrative_reviewer.py` (padrão de testes de comportamento de review_*)

Arquivos editáveis:
- `tests/test_visual_reviewer.py` (adicionar casos 23–32)

Comandos permitidos:
- `pytest tests/test_visual_reviewer.py -q`

Proibido:
- implementar `review_visual`
- alterar casos 17–22 já escritos

Done quando:
- 16 testes totais no arquivo, todos falhando por ausência de `review_visual`.

Revisão:
- casos 23–32 cobrem exatamente o comportamento listado na spec; sem GREEN misturado.

---

### STEP-08 — GREEN: `review_visual` (VR_001–VR_006)

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar `review_visual` em `generator/visual_reviewer.py` aplicando
  VR_001–VR_006, suficiente para passar os 16 testes do STEP-06/07.

Contexto permitido:
- `generator/visual_reviewer.py`
- `generator/narrative_reviewer.py` (padrão de `review_narrative`)
- `tests/test_visual_reviewer.py`
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `generator/models.py`

Arquivos editáveis:
- `generator/visual_reviewer.py`

Comandos permitidos:
- `pytest tests/test_visual_reviewer.py -q`
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- alterar `narrative_reviewer.py`/`evidence_reviewer.py`/`review_report.schema.yaml`
- criar `generator/accessibility_reviewer.py`
- usar números mágicos (limiares devem ser constantes nomeadas, ex.: `MAX_CONTEUDO_CHARS`)
- elevar severidade de VR_005 acima de `info`

Done quando:
- os 32 testes de `tests/test_visual_reviewer.py` e
  `tests/test_visual_accessibility_review_report_schema.py` passam juntos.

Revisão:
- VR_001–VR_006 implementadas conforme tabela da spec; limiares são
  constantes nomeadas; VR_005 nunca eleva status; `review_visual` não muta o blueprint.

---

### STEP-09 — RED: regras AR_001–AR_006 (casos 33–38)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_accessibility_reviewer.py` com os casos 33–38 (uma regra
  AR por caso).

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `generator/visual_reviewer.py`
- `tests/test_evidence_reviewer.py` (padrão de teste de reviewer importado)
- `generator/models.py`

Arquivos editáveis:
- `tests/test_accessibility_reviewer.py` (criar; somente casos 33–38)

Comandos permitidos:
- `pytest tests/test_accessibility_reviewer.py -q`

Proibido:
- implementar `review_accessibility` ou `generator/accessibility_reviewer.py`
- escrever casos 39–48 neste step

Done quando:
- 6 testes existem, falham por ausência de `generator.accessibility_reviewer`.

Revisão:
- cada caso corresponde a exatamente uma regra AR_001–AR_006 da tabela da spec.

---

### STEP-10 — RED: comportamento de `review_accessibility` (casos 39–48)

Status: pending
Owner: executor
Type: red

Objetivo:
- Completar `tests/test_accessibility_reviewer.py` com os casos 39–48
  (importação sem duplicação, não-mutação, validação de schema, constantes
  nomeadas, caso real do Aurora).

Contexto permitido:
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `tests/test_accessibility_reviewer.py` (já criado no STEP-09)
- `examples/caso_canonico_intermediario.json`

Arquivos editáveis:
- `tests/test_accessibility_reviewer.py` (adicionar casos 39–48)

Comandos permitidos:
- `pytest tests/test_accessibility_reviewer.py -q`

Proibido:
- implementar `review_accessibility`
- alterar casos 33–38 já escritos

Done quando:
- 16 testes totais no arquivo, todos falhando por ausência de
  `generator.accessibility_reviewer`.

Revisão:
- casos 39–48 cobrem exatamente o comportamento listado na spec; sem GREEN misturado.

---

### STEP-11 — GREEN: `accessibility_reviewer.py` (AR_001–AR_006)

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `generator/accessibility_reviewer.py` importando dataclasses/helpers
  de `generator/visual_reviewer.py` e implementando `review_accessibility`
  com AR_001–AR_006, suficiente para passar os 16 testes do STEP-09/10.

Contexto permitido:
- `generator/visual_reviewer.py`
- `generator/evidence_reviewer.py` (padrão de import de narrative_reviewer)
- `tests/test_accessibility_reviewer.py`
- `.ai/issues/ISSUE-23+24_SPEC.md`
- `generator/models.py`

Arquivos editáveis:
- `generator/accessibility_reviewer.py` (criar)

Comandos permitidos:
- `pytest tests/test_accessibility_reviewer.py -q`
- `pytest tests/test_visual_reviewer.py -q`
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- duplicar `ReviewFinding`/`VisualAccessibilityReviewReport`/helpers em vez de importar
- alterar `generator/visual_reviewer.py`, `narrative_reviewer.py`, `evidence_reviewer.py`
- usar números mágicos (limiares: `MAX_DOCS_PER_ENVELOPE`, `MAX_CROSS_REFS`)

Done quando:
- os 48 testes dos três arquivos novos passam juntos.

Revisão:
- AR_001–AR_006 implementadas conforme tabela da spec; importa de
  `visual_reviewer.py` sem duplicar; limiares nomeados; não muta blueprint.

---

### STEP-11-FIX — CORRECTION: remover guard RED obsoleto

Status: pending
Owner: executor
Type: correction

Objetivo:
- `tests/test_accessibility_reviewer.py` linhas 51-52 têm
  `with pytest.raises(ModuleNotFoundError): import generator.accessibility_reviewer`,
  criado no STEP-09 para comprovar RED. Após o STEP-11 (GREEN), o módulo
  existe, o import não levanta mais, `pytest.raises` falha com "DID NOT RAISE"
  e aborta a coleta do arquivo inteiro (0/16 testes executam). Remover o
  guard; ele não faz parte do contrato de teste (não é um dos casos 33-48 da
  spec), era só andaime de RED. Padrão STEP-06/07 (`test_visual_reviewer.py`)
  não usa esse guard — usa lazy import dentro do helper `_review()`.

Contexto permitido:
- `.ai/runs/ISSUE-23+24/STEP-11_EXECUTION.md`
- `tests/test_accessibility_reviewer.py`
- `tests/test_visual_reviewer.py` (referência do padrão sem guard)

Arquivos editáveis:
- `tests/test_accessibility_reviewer.py` (remover apenas linhas do guard
  `with pytest.raises(ModuleNotFoundError): ...`; nenhuma outra alteração)

Comandos permitidos:
- `pytest tests/test_accessibility_reviewer.py -q`
- `pytest tests/test_visual_reviewer.py -q`
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- alterar qualquer caso de teste (33-48)
- alterar `generator/accessibility_reviewer.py` ou `generator/visual_reviewer.py`
- remover o `import pytest` se ainda usado em outro lugar do arquivo

Done quando:
- os 48 testes dos três arquivos (visual_reviewer + schema + accessibility_reviewer)
  passam juntos; `STATUS` da issue volta de `blocked` para `running`.

Revisão:
- diff mínimo: só as 2 linhas do guard removidas, nada mais; 48/48 verde.

---

### STEP-12 — REFACTOR: helpers compartilhados

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Extrair helpers de varredura de documentos/cards por envelope reutilizados
  entre VR_*/AR_* (ex.: contagem de docs por envelope, concatenação de
  conteúdo) sem alterar comportamento observável; confirmar ausência de
  números mágicos.

Contexto permitido:
- `generator/visual_reviewer.py`
- `generator/accessibility_reviewer.py`
- `tests/test_visual_reviewer.py`
- `tests/test_accessibility_reviewer.py`

Arquivos editáveis:
- `generator/visual_reviewer.py`
- `generator/accessibility_reviewer.py`

Comandos permitidos:
- `pytest tests/test_visual_reviewer.py -q`
- `pytest tests/test_accessibility_reviewer.py -q`
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`

Proibido:
- adicionar comportamento novo
- adicionar testes
- alterar API pública sem necessidade

Done quando:
- os 48 testes continuam passando após o refactor; nenhum número mágico solto.

Revisão:
- nenhum comportamento novo; testes inalterados continuam verdes; sem API pública nova não autorizada.

---

### STEP-13 — VALIDATION: suíte completa

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar suíte completa, lint e confirmar que nada fora do escopo foi tocado.

Contexto permitido:
- nenhum arquivo novo (apenas saída dos comandos)

Arquivos editáveis:
- nenhum

Comandos permitidos:
- `ruff check generator/visual_reviewer.py generator/accessibility_reviewer.py`
- `pytest tests/test_visual_accessibility_review_report_schema.py -q`
- `pytest tests/test_visual_reviewer.py -q`
- `pytest tests/test_accessibility_reviewer.py -q`
- `pytest tests/test_narrative_reviewer.py -q`
- `pytest tests/test_evidence_reviewer.py -q`
- `pytest tests/test_run_manifest_schema.py -q`
- `pytest tests/ -q`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- corrigir falhas encontradas
- alterar qualquer arquivo

Done quando:
- `pytest tests/ -q` passa sem regressão (1279+ testes);
- `test_run_manifest_schema.py` casos 15/17 continuam verdes;
- `git diff --stat schemas/review_report.schema.yaml` vazio (schema intacto);
- `ruff check` sem erros.

Revisão:
- resultados registrados batem com os exigidos; nenhuma correção feita neste step.

---

### STEP-14 — DOCUMENTATION: status no ROADMAP

Status: pending
Owner: executor
Type: documentation

Objetivo:
- Marcar ISSUE-23 e ISSUE-24 como concluídas em `docs/ROADMAP.md` (só status,
  sem reescrever a seção).

Contexto permitido:
- `docs/ROADMAP.md`

Arquivos editáveis:
- `docs/ROADMAP.md`

Comandos permitidos:
- nenhum

Proibido:
- alterar código ou testes
- reescrever descrição das issues, só o status

Done quando:
- ISSUE-23 e ISSUE-24 marcadas concluídas no ROADMAP.

Revisão:
- ignorado (low-risk, auto-approve)

---

### STEP-15 — WRAP-UP: relatório final

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Consolidar relatório final da issue (resumo do que foi entregue, comandos
  executados, resultado da suíte).

Contexto permitido:
- `.ai/runs/ISSUE-23+24/` (todos os execution/review reports já criados)
- `.ai/issues/ISSUE-23+24.md`

Arquivos editáveis:
- `.ai/runs/ISSUE-23+24/WRAP_UP.md` (criar)

Comandos permitidos:
- nenhum

Proibido:
- alterar implementação
- rodar novos testes

Done quando:
- `.ai/runs/ISSUE-23+24/WRAP_UP.md` resume entregáveis, comandos e resultado da suíte.

Revisão:
- ignorado (low-risk, auto-approve)

## Histórico

- Issue criada por Claude Sonnet 4.6 a partir da handoff de junho/2026.
  Desbloqueada por ISSUE-28; aguardando orquestração inicial.
- STEP-00 concluído: 15 steps planejados (STEP-01..STEP-15), decompostos
  para respeitar limite de 10 casos de teste por step RED. Avançando para
  STEP-01 (reading).
- STEP-01 executado (reading); auto-approved (low-risk). Avançando para STEP-02.
- STEP-02 executado (baseline). 1280 passed, 3 skipped, 5 failed pré-existentes
  em blind_bundle_* (OSError WinError 1314, symlink sem privilégio no Windows),
  fora do escopo (não tocam narrative/evidence/manifest). auto-approved
  (low-risk). Avançando para STEP-03.
- STEP-01 executado; aguardando revisão.
- STEP-02 executado; aguardando revisão.
- STEP-03 executado; aguardando revisão.
- STEP-03 aprovado; aguardando orquestrador.
- STEP-04 executado; aguardando revisão.
- STEP-04 aprovado; aguardando orquestrador.
- STEP-05 executado; aguardando revisão.
- STEP-05 aprovado; aguardando orquestrador.
- STEP-06 executado (RED casos 17-22, VR_001-VR_006); aguardando revisão.
- STEP-06 aprovado; aguardando orquestrador.
- STEP-07 executado (RED casos 23-32, comportamento de `review_visual`: status,
  ordenação, não-mutação, validação de schema, anti-regra VR_005, degradação
  graciosa sem printable_cards). 16 testes totais em
  `tests/test_visual_reviewer.py`, todos falhando por
  `ImportError: cannot import name 'review_visual'`. aguardando revisão.
- STEP-07 aprovado; aguardando orquestrador.
- STEP-08 executado (GREEN: `review_visual` com VR_001-VR_006 implementadas em
  `generator/visual_reviewer.py`; constantes nomeadas `MAX_CONTEUDO_CHARS` e
  `VISUAL_DOC_TYPES`; VR_002 resolve personagem citado via `ids_citados` e
  casa por `nome`==`titulo` do card, já que `PrintableCard` não tem campo de
  ligação direto a `personagem_id`). 32/32 testes verdes
  (`test_visual_reviewer.py` 16 + `test_visual_accessibility_review_report_schema.py`
  16). `narrative_reviewer.py`/`evidence_reviewer.py`/`review_report.schema.yaml`
  intactos; `accessibility_reviewer.py` não criado. aguardando revisão.
- STEP-08 aprovado; aguardando orquestrador.
- STEP-09 executado; aguardando revisão.
- STEP-09 aprovado; aguardando orquestrador.
- STEP-10 executado (RED casos 39-48, comportamento de `review_accessibility`:
  import de `ReviewFinding`/helpers de `visual_reviewer.py` sem duplicar,
  não-mutação, validação de schema, `reviewer_type`, ordenação por
  severidade, round-trip `report_to_dict`, constantes nomeadas
  `MAX_DOCS_PER_ENVELOPE`/`MAX_CROSS_REFS`, caso real do Aurora). 16 testes
  totais em `tests/test_accessibility_reviewer.py`, todos falhando por
  `ModuleNotFoundError: generator.accessibility_reviewer`. aguardando revisão.
- STEP-10 aprovado; aguardando orquestrador.
- STEP-11 executado: `generator/accessibility_reviewer.py` criado, AR_001-AR_006
  implementadas, importa de `visual_reviewer.py` sem duplicar (`ReviewFinding`,
  `VisualAccessibilityReviewReport`, helpers, `MAX_CONTEUDO_CHARS`). AR_005
  implementada como "conteudo vazio" (decisão registrada no execution report,
  necessária para não contradizer caso 39). BLOQUEADO: guard RED em
  `tests/test_accessibility_reviewer.py:51-52` (`pytest.raises(ModuleNotFoundError)`
  no import do módulo) agora falha porque o módulo existe, abortando a coleta
  do arquivo — 0/16 testes do arquivo executam, apesar da implementação estar
  completa. `test_visual_reviewer.py` (16) e
  `test_visual_accessibility_review_report_schema.py` (16) continuam 100%
  verdes, intactos. Arquivo de teste fora da allowlist editável deste step.
  Aguardando revisão/decisão do orquestrador.
- STEP-11 revisado: logica de `generator/accessibility_reviewer.py`
  (AR_001-AR_006) **aprovada**. Validacao manual fora do pytest (script
  standalone em /tmp, guard patcheado so em memoria, nenhum arquivo do repo
  tocado) confirma 16/16 casos 33-48 passam quando o guard obsoleto e
  ignorado. Blocker de coleta (`tests/test_accessibility_reviewer.py:51-52`,
  `pytest.raises(ModuleNotFoundError)` que nao levanta mais) confirmado
  reproduzindo o erro real via pytest. Allowlist respeitada (so
  `generator/accessibility_reviewer.py` alterado). `test_visual_reviewer.py`
  e `test_visual_accessibility_review_report_schema.py` confirmados intactos
  (16+16 passed). Ver .ai/runs/ISSUE-23+24/STEP-11_REVIEW.md. Decisao de
  transicao para STEP-11-FIX e do orquestrador.
- STEP-11-FIX executado: removidas as 2 linhas do guard RED obsoleto
  (`pytest.raises(ModuleNotFoundError)` no import de
  `generator.accessibility_reviewer`) em `tests/test_accessibility_reviewer.py`.
  Nenhuma outra alteração no arquivo (casos 33-48 intactos, `import pytest`
  mantido). `generator/accessibility_reviewer.py` e `generator/visual_reviewer.py`
  não tocados. 48/48 testes verdes (`test_accessibility_reviewer.py` 16 +
  `test_visual_reviewer.py` 16 + `test_visual_accessibility_review_report_schema.py`
  16). Ver .ai/runs/ISSUE-23+24/STEP-11-FIX_EXECUTION.md. Aguardando revisão.
- STEP-11-FIX revisado: diff mínimo confirmado (só guard removido, casos
  33-48 intactos, `import pytest` mantido). `generator/accessibility_reviewer.py`
  e `generator/visual_reviewer.py` confirmados não tocados (timestamps
  anteriores ao STEP-11-FIX). Reexecução: 48/48 passed
  (`test_accessibility_reviewer.py` + `test_visual_reviewer.py` +
  `test_visual_accessibility_review_report_schema.py`). **Aprovado**. Ver
  .ai/runs/ISSUE-23+24/STEP-11-FIX_REVIEW.md. STATUS volta para `running`,
  NEXT_ACTION para orquestrador decidir próximo step (STEP-12). Aguardando
  orquestrador.
- STEP-12 executado (REFACTOR): extraido helper privado
  `_exceeds_conteudo_limit(document)` em `generator/visual_reviewer.py`
  (logo apos `_document_text`), substituindo a duplicacao do predicado
  `len(_document_text(document)) > MAX_CONTEUDO_CHARS` que existia em VR_001
  e AR_002. `generator/accessibility_reviewer.py` agora importa
  `_exceeds_conteudo_limit` em vez de `_document_text` diretamente; mantem
  import de `MAX_CONTEUDO_CHARS` (ainda usado na mensagem do finding).
  Nenhum comportamento novo, nenhum teste novo, nenhuma API publica nova.
  Constantes nomeadas confirmadas sem numeros magicos soltos
  (`MAX_CONTEUDO_CHARS`, `VISUAL_DOC_TYPES`, `MAX_DOCS_PER_ENVELOPE`,
  `MAX_CROSS_REFS`). 48/48 testes verdes (`test_visual_reviewer.py` 16 +
  `test_accessibility_reviewer.py` 16 +
  `test_visual_accessibility_review_report_schema.py` 16). Ver
  .ai/runs/ISSUE-23+24/STEP-12_EXECUTION.md. Aguardando revisao.
- STEP-12 revisado: refactor puro confirmado (helper privado
  `_exceeds_conteudo_limit`, sem comportamento novo, sem teste novo, sem
  mudanca de assinatura publica). Allowlist respeitada (so
  `generator/visual_reviewer.py` e `generator/accessibility_reviewer.py`
  tocados). Reexecucao confirma 48/48 (`test_visual_reviewer.py` 16 +
  `test_accessibility_reviewer.py` 16 +
  `test_visual_accessibility_review_report_schema.py` 16). **Aprovado**. Ver
  .ai/runs/ISSUE-23+24/STEP-12_REVIEW.md. STATUS continua `running`,
  NEXT_ACTION para orquestrador decidir proximo step (STEP-13). Aguardando
  orquestrador.
- STEP-13 executado (VALIDATION): `ruff check generator/visual_reviewer.py
  generator/accessibility_reviewer.py` limpo. Suite focada (schema+visual+
  accessibility+narrative+evidence+manifest) 119/119 verde, casos 15/17 de
  `test_run_manifest_schema.py` confirmados intactos. `pytest tests/ -q`
  completo: 1328 passed, 3 skipped, 5 failed — as 5 falhas sao as mesmas
  pre-existentes de symlink/Windows (`OSError WinError 1314`) confirmadas
  como baseline no STEP-02, fora do escopo desta issue, nao corrigidas
  (proibido neste step). `git diff --stat schemas/review_report.schema.yaml`
  vazio (schema existente intacto). `git status --short` mostra apenas
  arquivos novos esperados desta issue + modificacao no proprio arquivo da
  issue. Nenhum arquivo alterado fora da allowlist (step e read-only).
  Ver .ai/runs/ISSUE-23+24/STEP-13_EXECUTION.md. Aguardando revisao.
- STEP-13 revisado: ruff limpo e suite focada (119/119, incluindo casos 15/17
  de test_run_manifest_schema.py) confirmados batendo com execution report.
  schemas/review_report.schema.yaml intacto (git diff vazio). Validacao
  funcional standalone (sem tocar arquivos) confirma review_visual e
  review_accessibility produzem reports validos contra o schema novo no
  caso canonico intermediario (0 erros cada, visual=approved/0 findings,
  accessibility=needs_revision/2 findings). DIVERGENCIA: pytest tests/ -q
  reexecutado 2x de forma independente reproduz 6 failed, nao 5 como o
  execution report registra — falha adicional
  test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at
  (passa isolada, falha so na suite completa por contaminacao de
  estado/ordem). Confirmado via git stash que essa falha e pre-existente,
  independente das mudancas desta issue (persiste com mudancas
  stashed). REVIEW_STATUS: changes_requested — nao por erro de
  implementacao (logica dos reviewers aprovada), mas porque o execution
  report do STEP-13 precisa corrigir a contagem de falhas pre-existentes
  (6, nao 5) antes de fechar o step de validation. Ver
  .ai/runs/ISSUE-23+24/STEP-13_REVIEW.md. STATUS volta para blocked,
  aguardando orquestrador decidir correcao do execution report.
- STEP-13 reexecutado (correcao do execution report, nao novo step):
  `pytest tests/ -q` rodado de forma independente (1x) pelo executor,
  confirma `6 failed, 1327 passed, 3 skipped` — mesma contagem reportada
  pelo revisor em 2 rodadas independentes. `.ai/runs/ISSUE-23+24/STEP-13_EXECUTION.md`
  reescrito: lista as 6 falhas reais (5 symlink/Windows + 1
  `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`),
  explica a 6a como contaminacao de estado/ordem entre testes (passa isolada,
  falha so na suite completa), confirma via `git stash` (ja documentado na
  revisao) que e pre-existente e independente das mudancas desta issue — nao
  e regressao. Nenhuma falha corrigida, nenhum arquivo de codigo/teste
  alterado, apenas o execution report. STATUS volta para `running`,
  NEXT_ACTION para `review`, REVIEW_STATUS para `pending`. Aguardando
  revisao do execution report corrigido.
- STEP-13 revisado (reexecucao da revisao): execution report corrigido
  confirmado — lista as 6 falhas reais (5 symlink/Windows pre-existentes + 1
  `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`)
  com explicacao da 6a (contaminacao de estado/ordem, diff isolado no sha256
  do artefato `evidence_review`, pre-existente confirmada via `git stash`).
  `pytest tests/ -q` reexecutado pelo revisor: `6 failed, 1327 passed,
  3 skipped`, bate exatamente com o execution report. Nenhuma das 6 falhas
  toca os modulos/schema desta issue. **Aprovado**. Ver
  .ai/runs/ISSUE-23+24/STEP-13_REVIEW.md. STATUS continua `running`,
  NEXT_ACTION para orquestrador decidir proximo step (STEP-14). Aguardando
  orquestrador.
- STEP-14 executado (DOCUMENTATION): `docs/ROADMAP.md` atualizado, adicionado
  `Status: **concluída** (junho 2026).` sob os titulos `### ISSUE-23 — Visual
  Reviewer` e `### ISSUE-24 — Accessibility Reviewer`. Nenhuma outra linha
  tocada, descricao das issues mantida; status da fase F (linha "pendente,
  apos Gate Evaluator") nao alterado, fora do escopo (ISSUE-21+22 da mesma
  fase ainda pendente). Nenhum codigo/teste tocado, nenhum comando rodado
  (step nao permite). Ver .ai/runs/ISSUE-23+24/STEP-14_EXECUTION.md.
  Auto-approved (low-risk). Aguardando orquestrador decidir proximo step
  (STEP-15).
- STEP-15 executado (WRAP-UP): relatorio final criado em
  .ai/runs/ISSUE-23+24/WRAP_UP.md, sintetizando os 16 steps (STEP-01..STEP-15
  + STEP-11-FIX): 4 auto-aprovados (STEP-01, STEP-02, STEP-14, STEP-15), 12
  revisados (STEP-03..STEP-13 + STEP-11-FIX), 2 correcoes (guard RED obsoleto
  no STEP-11-FIX; contagem de falhas pre-existentes no execution report do
  STEP-13, de 5 para 6). Entregavel: generator/visual_reviewer.py
  (review_visual, VR_001-VR_006), generator/accessibility_reviewer.py
  (review_accessibility, AR_001-AR_006), schemas/visual_accessibility_review_report.schema.yaml
  novo e independente (reviewer_type [visual, accessibility], schemas/enums
  existentes intactos), 48 testes novos. Suite completa final: 1327 passed,
  3 skipped, 6 failed (todas pre-existentes, fora do escopo, confirmadas via
  baseline STEP-02 e git stash no STEP-13). Nenhum comando pesado reexecutado
  neste step (proibido). Issue concluida. STATUS: done, NEXT_ACTION: none.

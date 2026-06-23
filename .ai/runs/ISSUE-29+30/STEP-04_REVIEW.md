# STEP-04 — Run do Fintech no pipeline — Review Report

Revisor: independente. Veredito: **APPROVED**.

## Reprodução independente

Script ad-hoc próprio (não persistido no repo), salvo em
`C:\Users\Marcelo\AppData\Local\Temp\claude\...\scratchpad\review_step04_fintech.py`,
executado via:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe "<scratchpad>\review_step04_fintech.py"
```

Chamada: `run_pipeline("examples/caso_fintech.json", "RUN-FINTECH-20260623-001", created_at="2026-06-23T10:00:00Z")`.

Output:
```
=== pipeline_status ===
complete
=== stages_completed ===
['blind_solve', 'gate_evaluation', 'narrative_review', 'evidence_review']
=== validate_run_manifest (structural) ===
errors: []
valid: True
=== validate_run_manifest_semantics ===
errors: ()
warnings: ()
valid: True
=== OK ===
```

Sem exceção. `pipeline_status: complete`. 4 stages completados (`blind_solve`,
`gate_evaluation`, `narrative_review`, `evidence_review`) — confere com o
report.

## Findings — confirmação exata

Dump JSON dos 4 findings via script auxiliar confirma, byte a byte com o
execution report:

- `ER_006` — `field: "red_herrings[0]"` — red herring `'06'` sem contradição/contextualização.
- `ER_006` — `field: "red_herrings[1]"` — red herring `'07'` sem contradição/contextualização.
- `ER_007` — `field: "contratos_evidencia[2]"` — `C-E2-RETROCOMISSAO` depende de `E2-01` ausente do E1.
- `ER_007` — `field: "contratos_evidencia[3]"` — `C-E2-BENEFICIARIO` depende de `E2-04` ausente do E1.

Todos `severity: major`, `source_artifact_id: "ER-RUN-FINTECH-20260623-001"`.
0 findings NR. Total 4 ER. **Idêntico ao reportado.**

## Validação de manifest

`validate_run_manifest` (estrutural, JSON Schema): `errors: []`, `valid: True`.
`validate_run_manifest_semantics` (RM_001–RM_008): `errors: ()`, `warnings: ()`,
`valid: True`. Confirmado na reprodução independente.

## Integridade do repositório

```
$ git status --short
 M .ai/issues/ISSUE-29+30.md
?? .ai/runs/ISSUE-29+30/
?? examples/caso_fintech.json
```

Idêntico antes e depois da execução do script ad-hoc e do `pytest`.

```
$ git diff --stat -- generator/
(vazio)
```

`generator/` intocado. `examples/caso_canonico_intermediario.json` e
`examples/caso_canonico_iniciante.json` não aparecem no `git status` — intocados
(Aurora e iniciante preservados). `examples/caso_fintech.json` aparece como `??`
porque foi criado no STEP-03 (já revisado/aprovado) e ainda não commitado —
não é alteração desta execução do STEP-04. Nenhum script ad-hoc commitado;
script de reprodução desta revisão ficou inteiramente no scratchpad da sessão,
fora do repositório git.

## `pytest tests/ -q`

Resultado desta execução: **1327 passed, 6 failed, 3 skipped** (182.78s).

Falhas:
- 5 falhas de symlink Windows (`WinError 1314`, ambiente sem privilégio de
  symlink) — pré-existentes, mapeadas desde STEP-02.
- `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
  — falhou nesta execução. **Não é regressão nova.** Baseline real desde
  STEP-02 (`.ai/runs/ISSUE-29+30/STEP-02_EXECUTION.md`, linha 38-45) é
  **6 failed** (5 symlink + este teste), documentado como "não-determinismo
  real no pipeline... pré-existente, não introduzido por esta sessão" e
  confirmado de novo em STEP-03_REVIEW.md (linha 105-106). O teste usa
  `minimal_blueprint_path` próprio — não referencia `caso_fintech.json`, logo
  não tem relação com a run desta revisão. O executor relatou 5 failed porque
  o flake passou casualmente nessa rodada específica dele; nesta reprodução o
  flake voltou a falhar — comportamento intermitente já documentado, dentro da
  variação esperada mencionada no contrato da tarefa de revisão.

Nenhuma falha fora do conjunto baseline conhecido (5 symlink + 1 flake de
determinismo). Sem regressão nova.

## Avaliação dos findings ER_006/ER_007

Releitura de "Objetivo"/"Done quando" do STEP-04 na issue: o contrato exige
apenas que a run complete sem exceção e que `pipeline_status`/`findings`
sejam registrados no execution report para uso nos steps seguintes. Não exige
findings zero. Os 4 findings ER (`ER_006` x2, `ER_007` x2) são avaliações
estáticas do `evidence_reviewer` sobre limitações reais do blueprint Fintech
(red herrings sem pista de contradição, contratos E2 dependendo de prova E1
ausente) — não bloqueiam o gate (fixo `approved` por construção de
`run_pipeline`) nem a validação do manifest. Esses findings alimentam o
relatório comparativo dos steps seguintes (STEP-06/08), conforme já indicado
no execution report. Leitura do executor confirmada como correta.

## Veredito

**APPROVED.**

- Run reproduzida de forma independente: sem exceção, `pipeline_status: complete`,
  4 stages completados, findings idênticos (0 NR, 4 ER: ER_006 x2, ER_007 x2).
- `validate_run_manifest` e `validate_run_manifest_semantics`: `valid=True` em
  ambos, confirmado de forma independente.
- `generator/` intocado. Aurora (`caso_canonico_intermediario.json`) e
  `caso_canonico_iniciante.json` intocados. Nenhum script ad-hoc commitado.
- `pytest tests/ -q`: 6 failed nesta reprodução — mesmo conjunto de falhas
  pré-existentes do baseline desde STEP-02 (5 symlink + 1 flake de
  determinismo intermitente). Sem regressão nova.
- Findings ER_006/ER_007 são esperados e aceitáveis para este step — não são
  bloqueio, conforme o próprio "Done quando" do STEP-04.

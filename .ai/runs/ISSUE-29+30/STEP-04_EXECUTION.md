# STEP-04 — Run do Fintech no pipeline — Execution Report

Type: green (high-risk). Status: in_review. Aguarda revisão antes de avançar para STEP-05.

## Script ad-hoc usado (não persistido no repo)

Executado via `.\.venv\Scripts\python.exe <script>` com `PYTHONPATH` apontando para a raiz
do repo (necessário pois o script roda fora do diretório do projeto, na pasta scratchpad da
sessão; sem isso `ModuleNotFoundError: No module named 'generator'`). Conteúdo completo do
script (salvo em
`C:\Users\Marcelo\AppData\Local\Temp\claude\C--Users-Marcelo\86fb765f-1399-43cd-82cf-90e0830bce96\scratchpad\run_fintech_pipeline.py`,
fora do repositório):

```python
import json
import sys

from generator.pipeline_runner import run_pipeline
from generator.run_manifest import validate_run_manifest, validate_run_manifest_semantics

result = run_pipeline(
    "examples/caso_fintech.json",
    "RUN-FINTECH-20260623-001",
    created_at="2026-06-23T10:00:00Z",
)

manifest = result.manifest

print("=== pipeline_status ===")
print(manifest.get("pipeline_status"))

print("=== stages_completed ===")
print(manifest.get("stages_completed"))

print("=== findings (from result.findings) ===")
print(json.dumps(result.findings, indent=2, ensure_ascii=False))

print("=== findings (from manifest) ===")
print(json.dumps(manifest.get("findings"), indent=2, ensure_ascii=False))

print("=== gate_outcome ===")
print(json.dumps(manifest.get("gate_outcome"), indent=2, ensure_ascii=False))

structural_errors = validate_run_manifest(manifest)
print("=== validate_run_manifest (structural) ===")
print("errors:", structural_errors)
print("valid:", not structural_errors)

semantic_result = validate_run_manifest_semantics(manifest)
print("=== validate_run_manifest_semantics ===")
print("errors:", semantic_result.errors)
print("warnings:", semantic_result.warnings)
print("valid:", semantic_result.valid)

print("=== comparison ===")
print("playtest_defects:", result.comparison.playtest_defects)
print("pipeline_findings:", result.comparison.pipeline_findings)
print("matches:", result.comparison.matches)
print("unmatched_playtest:", result.comparison.unmatched_playtest)
print("unmatched_pipeline:", result.comparison.unmatched_pipeline)

if structural_errors or not semantic_result.valid:
    sys.exit(1)
```

Comando de execução:
```bash
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe "<caminho-scratchpad>\run_fintech_pipeline.py"
```

Exit code: `0` (sem exceção, sem erros de validação).

## Resultado da run

`run_pipeline("examples/caso_fintech.json", "RUN-FINTECH-20260623-001", created_at="2026-06-23T10:00:00Z")`
retornou `PipelineRunResult` sem levantar exceção (sem `RuntimeError` de mutação de blueprint,
sem `ValidationError` Pydantic, sem erro de gate).

| Campo | Valor |
|---|---|
| `pipeline_status` | `complete` |
| `stages_completed` | `['blind_solve', 'gate_evaluation', 'narrative_review', 'evidence_review']` (todos os 4 stages reais) |
| `gate_outcome.outcome` | `approved` |
| `gate_outcome.decision_id` | `DEC-RUN-FINTECH-20260623-001` |
| `gate_outcome.justification` | `"ISSUE-28 plumbing run: explicit approved gate decision."` |

### `findings` (lista completa, NR primeiro depois ER — `result.findings` == `manifest["findings"]`)

NR (`narrative_review`): **0 findings**.

ER (`evidence_review`): **4 findings**, todos `severity: major`, `source_artifact_id: "ER-RUN-FINTECH-20260623-001"`:

1. `ER_006` — `field: "red_herrings[0]"` — *"Red herring '06' não pode ser descartado: nenhuma pista contradiz ou contextualiza o documento de descarte."*
2. `ER_006` — `field: "red_herrings[1]"` — *"Red herring '07' não pode ser descartado: nenhuma pista contradiz ou contextualiza o documento de descarte."*
3. `ER_007` — `field: "contratos_evidencia[2]"` — *"Contrato obrigatório 'C-E2-RETROCOMISSAO' depende de prova 'E2-01' ausente do E1."*
4. `ER_007` — `field: "contratos_evidencia[3]"` — *"Contrato obrigatório 'C-E2-BENEFICIARIO' depende de prova 'E2-04' ausente do E1."*

Nenhum erro/exceção. Os 4 findings são avaliações do `evidence_reviewer` estático sobre o
blueprint — não bloqueiam o pipeline (gate já fixo `approved` por `run_pipeline`, conforme
mapeado em STEP-01: decisão fixa "approved" + 1 gap stub, sem depender desses findings).

### Comparação com playtest (`compare_to_playtest`)

`caso_fintech.json` não corresponde ao filtro hardcoded
(`"caso_canonico_intermediario" in blueprint_path.name`) em `pipeline_runner.py` — confirmado
em STEP-01. Resultado:
- `playtest_defects`: `()` (vazio, esperado)
- `pipeline_findings`: `('ER_006', 'ER_006', 'ER_007', 'ER_007')`
- `matches`: `()`
- `unmatched_playtest`: `()`
- `unmatched_pipeline`: `('ER_006', 'ER_006', 'ER_007', 'ER_007')`

Comportamento esperado e documentado — sem playtest real disponível para Fintech, comparação
é trivialmente vazia do lado playtest.

## Validação do manifest

`validate_run_manifest(manifest)` (estrutural, JSON Schema `schemas/run_manifest.schema.yaml`):
```
errors: []
valid: True
```

`validate_run_manifest_semantics(manifest)` (regras RM_001–RM_008):
```
errors: ()
warnings: ()
valid: True
```

Ambos válidos, sem erros nem warnings. `manifest_id != run_id` (RM_001 ok), todos os 4 stages
completados têm artefato correspondente (RM_002 ok), `gate_outcome.decision_id` presente em
`decisions_summary` (RM_003 ok), `pipeline_status == complete` com os 4 stages presentes (RM_004
ok), os 4 findings referenciam `source_artifact_id` presente em `artifacts_summary` (RM_005 ok),
apenas 1 decision de `gate_evaluation` (RM_006 ok, sem warning), `pipeline_status != blocked`
(RM_007 n/a), `next_steps` não vazio dado `pipeline_status == complete` (RM_008 ok).

## Ajuste no blueprint

**Nenhum ajuste foi necessário.** O pipeline rodou ponta-a-ponta sem exceção e sem bloqueio de
gate na primeira execução (gate é fixo `approved` por construção de `run_pipeline`, independente
dos findings ER). `examples/caso_fintech.json` permanece idêntico ao estado aprovado em STEP-03
(confirmado via `git status --short` abaixo — nenhuma modificação no arquivo nesta execução).

## `pytest tests/ -q`

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

Resultado: **1328 passed, 5 failed, 3 skipped** (184.18s).

Falhas (idênticas ao baseline STEP-02/STEP-03, todas pré-existentes, ambiente Windows sem
privilégio de symlink — `WinError 1314`):
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

`test_run_pipeline_is_deterministic_with_same_created_at` (flake de determinismo conhecido,
mapeado em STEP-02/STEP-03) **passou** nesta execução — não é nova falha, mesma instabilidade
intermitente já documentada. Nenhuma falha nova introduzida pela execução de `run_pipeline`
sobre o blueprint Fintech.

## `git status --short` (confirmação de limpeza)

```
 M .ai/issues/ISSUE-29+30.md
?? .ai/runs/ISSUE-29+30/
?? examples/caso_fintech.json
```

Nenhum script ad-hoc commitado no repositório — script de execução ficou inteiramente na pasta
scratchpad da sessão (fora do repo git), nunca staged/tracked. `examples/caso_fintech.json`
permanece no estado aprovado em STEP-03 (sem diff desta execução — só listado como `??` por
ainda não ter sido commitado desde sua criação em STEP-03).

## Arquivos alterados nesta execução

- Criado: `.ai/runs/ISSUE-29+30/STEP-04_EXECUTION.md` (este relatório).
- Atualizado: `.ai/issues/ISSUE-29+30.md` (seção "## Estado" e "## Histórico").

Nenhum módulo em `generator/` foi alterado (`pipeline_runner.py`, `run_manifest.py` e
reviewers intocados). `examples/caso_fintech.json` não foi modificado.

## Resultado

`run_pipeline` executa ponta-a-ponta sobre o blueprint Fintech sem exceção, `pipeline_status:
complete`, todos os 4 stages completados, gate `approved`. Manifest resultante passa
`validate_run_manifest` (estrutural) e `validate_run_manifest_semantics` (RM_001–RM_008) com
`valid=True` em ambos, zero erros, zero warnings. 4 findings ER (`ER_006` ×2, `ER_007` ×2,
todos `major`) e 0 findings NR — refletem limitações reais do blueprint (red herrings sem
pista de contradição associada, contratos de evidência E2 dependendo de prova ausente do E1),
mas não bloqueiam o pipeline nem a validação do manifest. Nenhum ajuste foi necessário no
blueprint. `pytest tests/ -q` sem regressão nova (1328 passed, 5 failed pré-existentes de
symlink Windows, 3 skipped). Pronto para revisão humana deste step (high-risk/green) antes de
avançar para STEP-05.

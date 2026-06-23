# Review Report — ISSUE-23+24 STEP-13

STEP: STEP-13
STEP_TYPE: validation
REVIEW_STATUS: approved

## Contrato do step

Step `validation`: read-only, nenhum arquivo alterado, nenhuma falha
corrigida, apenas comandos da allowlist. Done quando `pytest tests/ -q` passa
sem regressão (≥1279), casos 15/17 de `test_run_manifest_schema.py` verdes,
`schemas/review_report.schema.yaml` intacto, `ruff check` limpo.

## Histórico desta revisão

Rodada anterior (DVG-REVIEW-001, ver histórico abaixo) encontrou divergência:
execution report registrava `5 failed, 1328 passed`, mas reexecução
independente (2x) do revisor reproduziu `6 failed, 1327 passed, 3 skipped` —
faltava `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
na lista de falhas pré-existentes. REVIEW_STATUS anterior: `changes_requested`,
não por falha de implementação dos reviewers (aprovada), mas por registro
incorreto no execution report.

Executor corrigiu `.ai/runs/ISSUE-23+24/STEP-13_EXECUTION.md`: agora lista as
6 falhas reais (5 symlink/Windows pré-existentes + a 6ª), explica a causa da
6ª (`AssertionError` em `tests/test_pipeline_runner.py:351`,
`result_a.manifest != result_b.manifest`, sha256 do artefato `evidence_review`
diverge entre duas execuções do mesmo pipeline; passa isolada; falha só na
suíte completa por contaminação de estado/ordem) e reafirma, com a mesma
evidência de `git stash` já levantada na revisão anterior, que é
pré-existente e independente das mudanças desta issue.

## Reverificação desta rodada

```
.venv/Scripts/python.exe -m pytest tests/ -q
```

Resultado: `6 failed, 1327 passed, 3 skipped in 344.52s`.

Falhas reproduzidas (idênticas à lista do execution report corrigido):
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
- `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`

6ª falha confirmada nesta rodada com o mesmo padrão: `AssertionError` em
`tests/test_pipeline_runner.py:351`, diff isolado no sha256 do artefato
`stage: evidence_review` entre as duas execuções (`result_a` vs `result_b`).
Bate exatamente com a causa descrita no execution report corrigido.

## Veredito

Contagem real (`6 failed, 1327 passed, 3 skipped`) bate com o execution
report corrigido. Explicação da 6ª falha (contaminação de estado/ordem entre
testes, pré-existente, confirmada via `git stash` na rodada anterior, não
regressão de ISSUE-23+24) está correta e reprodutível. Validações já feitas
na rodada anterior (lógica dos reviewers, schema intacto, lint limpo,
allowlist respeitada) permanecem válidas — nada no diff de código mudou desde
então, só o texto do execution report.

**STEP-13 aprovado.**

## Decisão

- STATUS: `running`
- NEXT_ACTION: aguardando orquestrador decidir próximo step (STEP-14)
- REVIEW_STATUS: `approved`

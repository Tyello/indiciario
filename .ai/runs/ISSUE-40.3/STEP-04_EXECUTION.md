# STEP-04 — Verificação de regressão — Execution Report

Owner: executor
Type: validation

## Comandos rodados

1. `py -m pytest tests/test_layer_rules.py -q`
   → **28 passed** em 9.78s. Cobre todo o inventário do STEP-01 (8 templates de papel testados contra box-shadow/border-radius/gradient; templates de tela+papel testados contra ausência de doc-code/título/"Envelope N" no DOM visível). Nada ficou de fora.

2. `py -m pytest tests/ -q`
   → **5 failed, 1416 passed, 3 skipped** em 200.60s.

   As 5 falhas são pré-existentes e não relacionadas a esta issue:
   - `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
   - `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
   - `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
   - `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
   - `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

   Todas falham com `OSError: [WinError 1314] O cliente não tem o privilégio necessário` em `Path.symlink_to(...)` — ambiente Windows local sem privilégio de criar symlink (falta "Create symbolic links" no usuário, comum fora de admin/Developer Mode). Nenhuma relação com `templates/`, `document_system.css`, `base.html` ou `tests/test_layer_rules.py`. Nenhuma dessas suítes está no conjunto de contexto/arquivos editáveis de ISSUE-40.3. Confirmado: nenhuma regressão nova introduzida pelas mudanças desta issue.

3. `py -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict`
   → Completou sem erro: `QA: passed`, `Graph: passed`, `Playtest: warnings`, `LLM Feedback: generated`.

4. `py -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict`
   → Completou sem erro: `QA: passed`, `Graph: passed`, `Playtest: ok`, `LLM Feedback: generated`.

## Conclusão

- `tests/test_layer_rules.py` roda 100% verde contra o inventário completo.
- `pytest tests/ -q` sem regressão nova (as 5 falhas são de ambiente Windows/symlink, pré-existentes, fora do escopo tocado por 40.3).
- Ambos os builds canônicos `--strict` completam sem erro — extração/reset de camada em `document_system.css` e injeção de `.layer-screen`/`.layer-paper` via `generator/renderer.py` não quebrou o pipeline de build.
- Nenhum arquivo de `templates/`, CSS ou `generator/` foi alterado neste step (fora do escopo de STEP-04 — só validação).

Done conforme contrato: `pytest tests/ -q` passa sem regressão nova; os dois builds `--strict` completam sem erro.

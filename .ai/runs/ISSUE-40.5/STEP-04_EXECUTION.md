# ISSUE-40.5 / STEP-04 — Execution Report (Verificação)

Type: validation
Owner: executor
Commit base: 5f7a7970d79ee744a4e86ca948eaf1b9845ed987

## Objetivo do step

Rodar `tests/test_brand_isolation.py` contra os 16 templates de Camada 1/2 confirmados, revisar
se algum template dependia de `--accent` (esperado: nenhum) e rodar suíte completa confirmando
ausência de regressão nova atribuível a esta issue.

## Comandos executados

Ambiente Windows: usado `.venv\Scripts\python.exe` (venv do projeto), conforme padrão local.

### `pytest tests/test_brand_isolation.py -q`

```
.................                                                        [100%]
17 passed in 3.39s
```

17/17 passed: `test_diegetic_template_does_not_inherit_brand_accent` (16 templates parametrizados,
`NON_LAYER0_TEMPLATES` = `PAPER_LAYER_TEMPLATES` + `SCREEN_LAYER_TEMPLATES` da 40.3) +
`test_accent_variable_scoped_to_camada_0` (1). Todos verdes — confirma que nenhum dos 16 templates
diegéticos herda `--accent`/`rgb(139, 26, 26)` no computed style real (Playwright), e que
`--accent` está declarado dentro de `.camada-0` em `templates/base.html`, não em `:root` global.

### `pytest tests/test_layer_rules.py -q`

```
............................                                              [100%]
28 passed in 5.40s
```

28/28 passed. Sem regressão nas regras de camada (P0/P1/P2/P3) introduzidas pela 40.3/40.4.

### `pytest tests/ -q`

```
5 failed, 1437 passed, 3 skipped in 230.61s (0:03:50)
```

Falhas:

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Todas falham em `Path.symlink_to(...)` com `OSError: [WinError 1314] O cliente não tem o
privilégio necessário` — falta de privilégio de symlink no Windows local, não relacionado a
`templates/base.html`, `.camada-0`, `--accent` ou a qualquer arquivo tocado por esta issue.
Mesmo padrão documentado como pré-existente e não relacionado nas 40.3/STEP-04 e 40.4/STEP-04.

Nenhuma dessas falhas toca `templates/`, `tests/test_brand_isolation.py` ou
`tests/test_layer_rules.py`. Confirmado: **sem regressão nova atribuível a esta issue**.

## Verificação visual / "sem cor nenhuma"

Não houve necessidade de screenshot manual: o próprio `test_diegetic_template_does_not_inherit_brand_accent`
inspeciona `getComputedStyle` de todos os elementos visíveis do body de cada um dos 16 templates via
Playwright e falha se `color`/`background-color`/`border-color` resolver para `rgb(139, 26, 26)` (ou se
`--accent` estiver setado no escopo). Passou 100% — confirma o achado do STEP-01/03: nenhum dos 16
templates diegéticos dependia de `--accent` para ter cor, então mover a declaração para `.camada-0` não
deixou nenhum template "sem cor nenhuma". `08_orcamento.html` (`.accent-bar` / `{{COR_PRIMARIA}}`)
confirmado fora de escopo (mecanismo per-instituição, Jinja, não a CSS var `--accent`) — não tocado,
sem necessidade de verificação adicional.

## Conclusão

Critério de aceite do STEP-04 satisfeito:
- `tests/test_brand_isolation.py` passa 100% (17/17) contra os 16 templates confirmados.
- Nenhum template ficou sem cor por regressão não prevista.
- `pytest tests/ -q`: 5 falhas pré-existentes de symlink Windows, documentadas como não relacionadas,
  seguindo o precedente da 40.3/40.4. Sem regressão nova atribuível à 40.5.

Avança para STEP-05 (Docs).

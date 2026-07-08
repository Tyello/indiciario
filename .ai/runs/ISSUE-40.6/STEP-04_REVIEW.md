# ISSUE-40.6 / STEP-04 — Review Report (Reviewer)

Owner: revisor
Type: validation review (independente)

## Objetivo

Revisar de forma independente o relatório de execução do STEP-04
(`.ai/runs/ISSUE-40.6/STEP-04_EXECUTION.md`), confirmando os números de
teste, a alegação de regressão nova (placeholders `INST_COLOR` /
`INST_FONT_DISPLAY` / `INST_HEADER_SHAPE` / `HORA_COM_SEGUNDOS`) e a
alegação de que as 5 falhas de symlink são pré-existentes e não
relacionadas.

## Comandos executados

Ambiente: `./.venv/Scripts/python.exe` (venv do projeto, Windows).

### 1. `git log --oneline -10` e `git diff HEAD -- templates/06_log_acesso.html generator/renderer.py`

Confirma que `templates/06_log_acesso.html` e `generator/renderer.py`
estão modificados (working tree, ainda não commitados) — consistente com
STEP-03 desta issue em andamento.

`git diff HEAD -- generator/renderer.py` mostra, entre outras mudanças de
ISSUE-40.6 (registro de `manual.html`/`cadastro.html` em
`DOCUMENT_PLAYER_TEMPLATES`, `TEMPLATE_DOCUMENT_CLASS`,
`TEMPLATE_LAYER_PAPER`, `DOCUMENT_TYPE_FAMILIES`, e injeção de
`_institution_identity_css()`), a função `_preparar_dados_documentais`
com vários `preparados.setdefault(...)` para outros tokens (`DOC_CONTROLE`,
`DOC_STAMP_LABEL`, `CODIGO_DOCUMENTO`, `NOME_CASO`, `ENVELOPE`) — **mas
nenhum `setdefault` foi adicionado para `INST_COLOR`, `INST_FONT_DISPLAY`,
`INST_HEADER_SHAPE` ou `HORA_COM_SEGUNDOS`**. Confirmado via
`grep -n "HORA_COM_SEGUNDOS|INST_COLOR|INST_FONT_DISPLAY|INST_HEADER_SHAPE" generator/renderer.py`
→ zero ocorrências no arquivo Python. Ou seja: esses 4 tokens só existem
como texto literal no template (`templates/06_log_acesso.html`, confirmado
por leitura direta — linhas do bloco de carimbo/rodapé e header contêm
`{{INST_COLOR}}`, `{{INST_FONT_DISPLAY}}`, `{{INST_HEADER_SHAPE}}`,
`{{HORA_COM_SEGUNDOS}}` literais) e nunca recebem valor default no código
de preparação de dados quando o contexto de instituição não é passado.
Isso bate exatamente com a causa raiz alegada pelo executor.

### 2. Rodei os 5 testes citados como "novas falhas" isoladamente

```
pytest tests/test_renderer.py::test_caso_canonico_dicas_contextuais_aparecem_no_html_debug \
       tests/test_renderer.py::test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador \
       tests/test_renderer.py::test_renderizar_documento_usa_familia_visual_e_emissor_de_email \
       tests/test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais \
       tests/test_package_manifests.py::test_build_package_strict_nao_gera_pdf_fake_sem_env -q
```

Resultado: **5 failed**, todas com a mesma assinatura de erro relatada:

```
generator.renderer.PlaceholderResidualError: E1-02.pdf — 3 resíduo(s)
técnico(s): {{INST_COLOR}}, {{INST_FONT_DISPLAY}}, {{INST_HEADER_SHAPE}}
```

```
AssertionError: assert {'E1-04': [...], 'E1-05': [...]} == {}
  Left contains 2 more items:
  {'E1-04': ['{{HORA_COM_SEGUNDOS}}', '{{INST_COLOR}}',
             '{{INST_FONT_DISPLAY}}', '{{INST_HEADER_SHAPE}}'], ...}
```

`test_build_package_strict_nao_gera_pdf_fake_sem_env` falha porque a
exceção esperada (`"Playwright não está instalado"`) nunca é levantada —
o pipeline falha antes, no `PlaceholderResidualError` do
`RenderCaseError`, mascarando o comportamento que o teste realmente quer
verificar. Confirma exatamente o que o executor descreveu.

Números batem 1:1 com o relatado no STEP-04_EXECUTION.md.

### 3. Rodei os 5 testes de symlink citados como "pré-existentes"

```
pytest tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed \
       tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails \
       tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails \
       tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail \
       tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail -q
```

Resultado: **5 failed**, todas com `OSError: [WinError 1314] O cliente
não tem o privilégio necessário` disparado dentro de `Path.symlink_to(...)`
— falha ao criar symlink no Windows local por falta do privilégio
"Create symbolic links" (ambiente sem admin/Developer Mode). Nenhuma
relação com `templates/`, `generator/renderer.py`, `institution_identity`
ou qualquer arquivo tocado por ISSUE-40.6: os testes pertencem a
`test_blind_bundle_generator.py`, `test_blind_bundle_leak_checker.py`,
`test_blind_bundle_sanitizer.py` — módulos de blind bundle (Fase C do
pipeline multiagente), sem nenhuma dependência de renderer/templates.

**Precedente confirmado via `git show`:** o relatório
`.ai/runs/ISSUE-40.3/STEP-04_EXECUTION.md` (commit `3cd3993`, já mesclado
em `main` antes de ISSUE-40.6) lista **exatamente os mesmos 5 testes**,
com a mesma causa (`OSError: [WinError 1314]`), como falhas pré-existentes
de ambiente, numa issue anterior sem nenhuma relação com institution
identity. Confirma que essas 5 falhas não são introduzidas por
ISSUE-40.6 — são uma limitação de ambiente local (Windows sem privilégio
de symlink) que já existia e já era documentada antes desta issue começar.

### 4. Leitura de `templates/06_log_acesso.html` e `generator/renderer.py`

Confirmado por leitura direta do template: os 4 placeholders
`{{INST_COLOR}}`, `{{INST_FONT_DISPLAY}}`, `{{INST_HEADER_SHAPE}}`,
`{{HORA_COM_SEGUNDOS}}` aparecem como literais no HTML (header/carimbo de
exportação), sem qualquer `{% if %}`/default embutido no próprio template.
Confirmado por leitura de `generator/renderer.py` (`_preparar_dados_documentais`,
`_institution_identity_css`, `_injetar_css_documental`): existe
infraestrutura de CSS (`institution_identity.css`, injetada
incondicionalmente via `_injetar_css_documental`) mas **nenhum código
popula `INST_COLOR`/`INST_FONT_DISPLAY`/`INST_HEADER_SHAPE`/
`HORA_COM_SEGUNDOS` com valor default quando o dicionário de dados do
documento não os contém** — ao contrário de outros tokens do mesmo bloco
(`DOC_CONTROLE`, `DOC_STAMP_LABEL`, `CODIGO_DOCUMENTO`, `NOME_CASO`,
`ENVELOPE`) que têm `setdefault(...)` explícito logo acima/abaixo no
mesmo trecho de código. `tests/test_institution_identity.py` não detecta
isso porque seu helper `_montar_html_institucional` sempre injeta os 4
tokens manualmente antes de renderizar — não exercita o caminho "sem
contexto de instituição", que é o caminho usado por todo blueprint
canônico hoje (`caso_canonico_iniciante.json`, `showcase_tecnico.json`
etc., nenhum dos quais tem esses 4 campos em `conteudo`).

## Veredito

**Alegação de regressão: CONFIRMADA.**

- As 5 falhas novas são reais, reproduzíveis, e a causa raiz apontada pelo
  executor (falta de fallback/default para os 4 tokens de identidade
  institucional em `_preparar_dados_documentais`, introduzida no STEP-03)
  está correta e verificada por leitura de código, não só por inferência
  do traceback.
- As 5 falhas de symlink são de fato pré-existentes, de ambiente
  (Windows sem privilégio de symlink), não relacionadas a
  `institution_identity`/renderer/templates, e têm precedente documentado
  em ISSUE-40.3 (mesmo conjunto de 5 testes, mesma causa, antes desta
  issue existir).
- O relatório do executor (`STEP-04_EXECUTION.md`) é preciso: números
  batem, causa raiz bate, distinção entre falhas relacionadas/não
  relacionadas está correta.

## Recomendação

**Não avançar para docs/wrap-up.** Abrir um STEP-05 tipo `correction`
antes de qualquer step de documentação, com escopo:

- Adicionar `setdefault` (ou equivalente) para `INST_COLOR`,
  `INST_FONT_DISPLAY`, `INST_HEADER_SHAPE` e `HORA_COM_SEGUNDOS` em
  `_preparar_dados_documentais` (ou função correspondente), com valores
  neutros que não quebrem a diferenciação institucional quando ela É
  fornecida (i.e., só aplicar o default quando o campo estiver ausente).
- Reexecutar os 5 testes que hoje falham
  (`test_package_manifests.py::test_build_package_strict_nao_gera_pdf_fake_sem_env`,
  `test_renderer.py::test_caso_canonico_dicas_contextuais_aparecem_no_html_debug`,
  `test_renderer.py::test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador`,
  `test_renderer.py::test_renderizar_documento_usa_familia_visual_e_emissor_de_email`,
  `test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`)
  e confirmar volta a 0 falhas novas.
- Reexecutar `pytest tests/test_institution_identity.py -q` e
  `pytest tests/test_layer_rules.py -q` para garantir que o fallback não
  quebra a diferenciação institucional já validada (4/4 e 28/28).
- Só então reexecutar `pytest tests/ -q` completo e confirmar `10 failed`
  → `5 failed` (só os symlinks pré-existentes), antes de fechar a issue.

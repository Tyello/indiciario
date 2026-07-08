# ISSUE-40.6 / STEP-04 — Execution Report (Validation)

Type: validation
Owner: executor

## Objetivo do step

1. Rodar `pytest tests/test_institution_identity.py -q` (museu_teste + empresa_teste).
2. Verificar visualmente (screenshot) que a diferenciação institucional é
   perceptível, não só tecnicamente presente no CSS.
3. Rodar `pytest tests/ -q` e confirmar ausência de regressão nova.

## Comandos executados

Ambiente Windows: `./.venv/Scripts/python.exe` (venv do projeto).

### `pytest tests/test_institution_identity.py -q`

```
....                                                                     [100%]
4 passed in 2.38s
```

4/4 passed: `test_documents_of_same_institution_share_identity`,
`test_documents_of_different_institutions_do_not_share_identity`,
`test_manual_has_revision_and_signature`,
`test_access_log_has_export_stamp_with_seconds`.

### `pytest tests/test_layer_rules.py -q`

```
............................                                              [100%]
28 passed in 4.73s
```

28/28 passed. Sem regressão de camada.

### Verificação visual (Playwright)

Reusei `_montar_html_institucional` de `tests/test_institution_identity.py`
(sem alterá-lo) num script auxiliar
`.ai/runs/ISSUE-40.6/_step04_screenshot.py` (fora de diretório de produção,
permitido pelo contrato deste step). O script renderiza `manual.html`,
`06_log_acesso.html` e `cadastro.html` para `museu_teste` e `empresa_teste`
(`INSTITUTION_TEST_DATA` do próprio teste) via Playwright/Chromium e salva
screenshot do `.institution .header` (com margem) para cada combinação.

Screenshots gerados em `.ai/runs/ISSUE-40.6/`:

- `museu_teste_manual.png` / `empresa_teste_manual.png`
- `museu_teste_06_log_acesso.png` / `empresa_teste_06_log_acesso.png`
- `museu_teste_cadastro.png` / `empresa_teste_cadastro.png`

**Diferenciação visual observada** (comparação lado a lado, mesmo template,
duas instituições):

- **Cor**: `museu_teste` — header em vermelho escuro/vinho (`#7a1f1f`, o
  bordô de `INST_COLOR`). `empresa_teste` — header em azul escuro
  (`#1f4a7a`). Diferença de cor nítida a olho nu nos 3 templates.
- **Fonte**: `museu_teste` usa fonte serifada (Libre Baskerville) no
  título do header (`{{NOME_INSTITUICAO}}`) — traços com serifa visíveis
  no manual.html. `empresa_teste` usa fonte sem serifa (DM Sans) no mesmo
  elemento — traços retos, geométricos. Diferença perceptível comparando
  `museu_teste_manual.png` e `empresa_teste_manual.png`.
- **Forma do header**: `museu_teste` (`shape-diagonal`) tem o header
  cortado por uma diagonal visível na borda inferior direita (clip-path) —
  claramente visível em `museu_teste_manual.png`, onde a faixa vermelha
  desce em diagonal antes do corpo do documento começar.
  `empresa_teste` (`shape-reto`) tem borda inferior reta, sem corte —
  visível em `empresa_teste_manual.png`. Diferença de silhueta do header
  perceptível mesmo ignorando cor/fonte.
- Confirmado também em `06_log_acesso.html` e `cadastro.html`: mesma cor e
  fonte por instituição em todos os 3 templates (coerência intra-
  instituição), e cor/fonte/forma distintas entre `museu_teste` e
  `empresa_teste` no mesmo template (diferenciação inter-instituição).

Conclusão: a diferenciação não é só um valor de CSS custom property sem
efeito visível — o resultado renderizado (cor de fundo, tipografia,
silhueta do header) é distinguível a olho nu entre as duas instituições de
teste.

### `pytest tests/ -q`

```
10 failed, 1436 passed, 3 skipped in 199.51s (0:03:19)
```

**5 falhas pré-existentes, não relacionadas** (mesmo padrão documentado em
40.3/40.4/40.5 STEP-04 — `Path.symlink_to(...)` falha com
`OSError: [WinError 1314]` por falta de privilégio de symlink no Windows
local, não relacionado a nenhum arquivo tocado por esta issue):

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

**5 falhas NOVAS, atribuíveis a esta issue (STEP-03/GREEN) — regressão
real, não documentável como "pré-existente":**

- `tests/test_package_manifests.py::test_build_package_strict_nao_gera_pdf_fake_sem_env`
- `tests/test_renderer.py::test_caso_canonico_dicas_contextuais_aparecem_no_html_debug`
- `tests/test_renderer.py::test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador`
- `tests/test_renderer.py::test_renderizar_documento_usa_familia_visual_e_emissor_de_email`
- `tests/test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`

Causa raiz (confirmada por leitura do traceback, não corrigida neste step
— fora do escopo/arquivos editáveis do STEP-04): `templates/06_log_acesso.html`
(e o template de email/log usado por `renderizar_documento`/`renderizar_caso`
no fluxo normal de blueprint) agora contém `{{INST_COLOR}}`,
`{{INST_FONT_DISPLAY}}`, `{{INST_HEADER_SHAPE}}` (e, no carimbo de
exportação, `{{HORA_COM_SEGUNDOS}}`) como placeholders literais no HTML de
saída. `tests/test_institution_identity.py` não pega essa regressão porque
seu helper `_montar_html_institucional` sempre injeta esses 3+1 tokens no
contexto de dados (`_dados_institucionais`) antes de renderizar. Mas o
fluxo real de blueprint/pacote (`renderizar_documento`, `renderizar_caso`,
`build_package`) não passa esses dados de instituição — hoje nenhum
blueprint canônico (`examples/caso_canonico_iniciante.json` etc.) tem
`INST_COLOR`/`INST_FONT_DISPLAY`/`INST_HEADER_SHAPE`/`HORA_COM_SEGUNDOS`
no seu `conteudo`. Resultado: os placeholders sobrevivem literalmente no
HTML final e disparam `detectar_residuos_tecnicos`/`PlaceholderResidualError`
em modo `strict`, ou aparecem como resíduo em
`detectar_placeholders`/`test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`.

Evidência (excerto do traceback):

```
generator.renderer.PlaceholderResidualError: E1-01.pdf — 3 resíduo(s)
técnico(s): {{INST_COLOR}}, {{INST_FONT_DISPLAY}}, {{INST_HEADER_SHAPE}}
```

```
AssertionError: assert {'E1-04': [...]} == {}
  Left contains 2 more items:
  {'E1-04': ['{{HORA_COM_SEGUNDOS}}', '{{INST_COLOR}}',
             '{{INST_FONT_DISPLAY}}', '{{INST_HEADER_SHAPE}}'],
   'E1-05': ['{{HORA_COM_SEGUNDOS}}', ...
```

Isso não é uma falha do critério de aceite do STEP-04 em si (os 4 testes de
`test_institution_identity.py` passam, e a diferenciação visual está
confirmada) — é uma regressão real introduzida pelo STEP-03 que faltou
cobertura: o STEP-03 não deu fallback/default para
`INST_COLOR`/`INST_FONT_DISPLAY`/`INST_HEADER_SHAPE`/`HORA_COM_SEGUNDOS`
quando um documento é renderizado sem contexto de instituição (o caso de
todo blueprint canônico hoje). Precisa de correção em
`generator/renderer.py` (ou nos templates) antes de fechar a issue —
registrado aqui como achado do STEP-04, não corrigido neste step porque
STEP-04 é `validation` e os arquivos editáveis deste step são só
`.ai/runs/ISSUE-40.6/`.

## Arquivos gerados neste step

- `.ai/runs/ISSUE-40.6/_step04_screenshot.py` (script auxiliar, reusa
  `_montar_html_institucional` de `tests/test_institution_identity.py`
  sem alterá-lo)
- `.ai/runs/ISSUE-40.6/museu_teste_manual.png`
- `.ai/runs/ISSUE-40.6/empresa_teste_manual.png`
- `.ai/runs/ISSUE-40.6/museu_teste_06_log_acesso.png`
- `.ai/runs/ISSUE-40.6/empresa_teste_06_log_acesso.png`
- `.ai/runs/ISSUE-40.6/museu_teste_cadastro.png`
- `.ai/runs/ISSUE-40.6/empresa_teste_cadastro.png`
- `.ai/runs/ISSUE-40.6/STEP-04_EXECUTION.md` (este relatório)

Nenhum arquivo de produção (`templates/`, `generator/`, `tests/`) foi
alterado neste step.

## Conclusão

- Critério "rodar os 2 conjuntos de teste": satisfeito, 4/4 passed.
- Critério "diferenciação visual perceptível": satisfeito e descrito acima
  (cor, fonte, forma de header, nos 3 templates × 2 instituições).
- Critério "suíte completa sem regressão nova": **NÃO satisfeito** — 5
  falhas novas atribuíveis a esta issue (lista acima), além das 5 falhas
  pré-existentes de symlink (não relacionadas, precedente 40.3/40.4/40.5).

Esta issue **não deve avançar para docs/wrap-up** sem antes corrigir a
regressão de placeholders residuais (`INST_COLOR`, `INST_FONT_DISPLAY`,
`INST_HEADER_SHAPE`, `HORA_COM_SEGUNDOS`) quando documentos são renderizados
sem contexto de instituição. Recomendo um STEP-05 tipo `correction` antes
de STEP-06 (docs), com defaults neutros para os 4 tokens em
`_preparar_dados_documentais` (ou equivalente), reexecutando este STEP-04
depois da correção.

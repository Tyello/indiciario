# ISSUE-40.6 — STEP-02 EXECUTION (RED)

Type: red
Owner: executor

## Objetivo

Criar `tests/test_institution_identity.py` com os 4 testes exigidos, seguindo
o padrão Playwright/CSS computado de `tests/test_layer_rules.py` (render real
via pipeline de `generator/renderer.py`, não grep de string em arquivo-fonte).

## Arquivo criado

`tests/test_institution_identity.py` — 4 testes:

1. `test_documents_of_same_institution_share_identity`
2. `test_documents_of_different_institutions_do_not_share_identity`
3. `test_manual_has_revision_and_signature`
4. `test_access_log_has_export_stamp_with_seconds`

`INSTITUTION_TEST_DATA` (`museu_teste` / `empresa_teste`) copiado literal de
`ISSUE-40.6_SPEC.md`.

## Mecanismo de renderização (achado STEP-01 aplicado)

O STEP-01 registrou que `generator.font_fidelity._montar_html` hardcoda
`_preparar_dados_documentais(template_nome, {})` (contexto vazio) e não serve
para este RED, porque precisa injetar dados de instituição (`INST_COLOR`,
`INST_FONT_DISPLAY`, `INST_HEADER_SHAPE`, etc.) no contexto de render.

Solução: helper próprio `_montar_html_institucional(template_nome, inst)`
que replica o mesmo pipeline usado por `_montar_html`, mas passa um
dicionário de dados de instituição em vez de `{}`:

```
_preparar_dados_documentais(template_nome, _dados_institucionais(inst))
  -> template_path.read_text()
  -> _injetar_css_documental(html_raw)
  -> _injetar_classes_body(html_raw, template_nome, dados)
  -> _injetar_cabecalho_rodape_documental(html_raw, template_nome, dados)
  -> renderizar_html(html_raw, dados)
```

Todas as 4 funções importadas de `generator/renderer.py` (mesmas usadas por
`font_fidelity._montar_html` e por `tests/test_layer_rules.py`).

`_dados_institucionais(inst)` injeta:
- `INST_COLOR`, `INST_FONT_DISPLAY`, `INST_HEADER_SHAPE` — tokens de
  microidentidade (valores de `INSTITUTION_TEST_DATA`).
- `INST_REVISAO` ("Revisão 2"), `INST_REVISAO_DATA` ("06/08/2024") — para o
  critério de aceite #4 (manual).
- `ASSINATURA_RESPONSAVEL_NOME` — para o bloco de assinatura do manual (a
  chave `ASSINATURA_RESPONSAVEL` faz parte de `ASSINATURA_KEYS` em
  `generator/renderer.py`, consumida por `preparar_assinaturas_visuais`
  dentro de `renderizar_html`).
- `DATA_EXPORTACAO` ("06/08/2024"), `HORA_EXPORTACAO` ("17:04" — **sem**
  segundos, formato realista de dado real, ver
  `examples/sinal_verde_demo_blueprint.json:621` = `"10:10"`) e
  `HORA_COM_SEGUNDOS` ("17:04:07") — para o critério de aceite #5 (log de
  acesso). `HORA_EXPORTACAO` foi deliberadamente mantido sem segundos para
  não fazer o teste passar "por acidente" hoje (se a variável de teste já
  tivesse segundos, a string interpolada em `{{HORA_EXPORTACAO}}` bateria com
  o regex mesmo sem o template ter sido alterado). `HORA_COM_SEGUNDOS` é o
  dado que o STEP-03 deve efetivamente usar no carimbo novo (nome citado na
  spec/issue: `{{HORA_COM_SEGUNDOS}}`).

## Detalhe de cada teste

### `test_documents_of_same_institution_share_identity`

Renderiza os 3 templates de `museu_teste` (`manual.html`, `06_log_acesso.html`,
`cadastro.html`) e lê `document.querySelector('.institution .header')` via
`getComputedStyle` (background-color, font-family, clip-path, border-top/
bottom-width — cobre `reto`/`diagonal`/`faixa-dupla`). Falha se o elemento não
existir, ou se a identidade computada divergir entre os 3 templates.

**Nasce RED real** para `06_log_acesso.html` — `.institution .header` não
existe no DOM hoje (o template usa `.page` / `.log-header`, sem classe
`.institution`).
**Nasce RED por `FileNotFoundError`** para `manual.html` e `cadastro.html`
— ainda não existem em `templates/*.html` (confirmado no STEP-01, criados no
STEP-03).

### `test_documents_of_different_institutions_do_not_share_identity`

Para cada um dos 3 templates, renderiza com `museu_teste` e `empresa_teste` e
compara a identidade computada — exige que ambas existam (`is not None`) e
sejam diferentes entre si.

Mesmo padrão de RED: `06_log_acesso.html` falha no `assert ... is not None`
(elemento ausente); `manual.html`/`cadastro.html` falham por
`FileNotFoundError` antes mesmo da asserção.

### `test_manual_has_revision_and_signature`

Regex `Revis[ãa]o\s+\d+\s*[—-]\s*\d{2}/\d{2}/\d{4}` sobre
`document.body.innerText`, mais busca de um elemento `svg` dentro de seletor
de assinatura (`svg.signature, .signature svg, .assinatura svg,
[class*='assinatura'] svg`). **Nasce RED por `FileNotFoundError`** —
`manual.html` não existe.

### `test_access_log_has_export_stamp_with_seconds`

Regex `EXPORTADOS?\s+EM\s+\d{2}/\d{2}/\d{4}\s+ÀS\s+\d{2}:\d{2}:\d{2}` sobre
`document.body.innerText`. **Nasce RED real** (não por ausência de arquivo):
`06_log_acesso.html` existe e renderiza, mas o texto produzido hoje é
`"EXPORTADO EM 06/08/2024 ÀS 17:04"` — falta o "S" de "EXPORTADOS" (a spec
pede plural) e faltam os segundos (`17:04` em vez de `17:04:07`). Confirmado
no output real do pytest (ver seção abaixo).

## Output real do pytest

Comando: `./.venv/Scripts/python.exe -m pytest tests/test_institution_identity.py -q`

Resultado: **4 failed** (100% dos testes novos, todos RED, nenhum GREEN-por-
desenho/vacuidade):

```
FAILED tests/test_institution_identity.py::test_documents_of_same_institution_share_identity
FAILED tests/test_institution_identity.py::test_documents_of_different_institutions_do_not_share_identity
FAILED tests/test_institution_identity.py::test_manual_has_revision_and_signature
FAILED tests/test_institution_identity.py::test_access_log_has_export_stamp_with_seconds
4 failed in 1.01s
```

Causas confirmadas na saída completa:
- `test_documents_of_same_institution_share_identity` — `AssertionError:
  06_log_acesso.html: elemento '.institution .header' ausente do DOM`.
- `test_documents_of_different_institutions_do_not_share_identity` —
  `FileNotFoundError` ao tentar ler `templates/manual.html` (primeiro
  template da lista, iterado antes de `06_log_acesso.html`).
- `test_manual_has_revision_and_signature` — `FileNotFoundError:
  templates/manual.html`.
- `test_access_log_has_export_stamp_with_seconds` — `AssertionError` com o
  texto renderizado completo do log de acesso, mostrando
  `"EXPORTADO EM 06/08/2024 ÀS 17:04"` (sem segundos, singular) contra o
  regex que exige `HH:MM:SS`.

Nenhum teste nasceu GREEN-por-desenho: os 4 são RED genuíno hoje — 2 por
ausência de arquivo (`manual.html`, `cadastro.html` — precedente aceito pela
issue/spec para o STEP-02) e 2 por comportamento real ausente
(`.institution .header` inexistente; carimbo sem segundos).

## Não fiz

- Não toquei template, CSS ou `generator/renderer.py` (proibido neste step).
- Não usei grep de string no HTML-fonte como teste — todas as asserções
  usam `getComputedStyle`/`querySelector`/`innerText` sobre o DOM renderizado
  via Playwright (`page.set_content` + `page.evaluate`), replicando o padrão
  de `tests/test_layer_rules.py`.

## Comandos executados

```
./.venv/Scripts/python.exe -m pytest tests/test_institution_identity.py -q
```
(resultado: 4 failed — RED confirmado, ver acima)

## Arquivos alterados

- `tests/test_institution_identity.py` (novo)
- `.ai/runs/ISSUE-40.6/STEP-02_EXECUTION.md` (este relatório)

## Recomendação para STEP-03

- Criar `templates/styles/institution_identity.css` (path confirmado no
  STEP-01) com `.institution`, `.institution .header`,
  `.institution .header.shape-diagonal`, `.institution .header.shape-
  faixa-dupla`, conforme esqueleto da spec.
- Criar `templates/manual.html` e `templates/cadastro.html` com elemento
  raiz `.institution` e header `.header` (selecionável por
  `.institution .header`, como o teste espera).
- Manual: header deve renderizar `{{INST_REVISAO}} — {{INST_REVISAO_DATA}}`
  batendo no regex `Revis[ãa]o\s+\d+\s*[—-]\s*\d{2}/\d{2}/\d{4}`; rodapé
  precisa de um `<svg>` de assinatura (reusar
  `generator/signature_renderer.py::build_signature_svg`) dentro de um
  elemento com classe contendo "assinatura" ou "signature".
- `06_log_acesso.html`: trocar `.log-header` para incluir/renomear para
  `.header` dentro de um wrapper `.institution`, e trocar o carimbo para
  `"EXPORTADOS EM {{DATA}} ÀS {{HORA_COM_SEGUNDOS}}"` (usar a variável nova
  `HORA_COM_SEGUNDOS`, não `HORA_EXPORTACAO`).
- `cadastro.html`: `.institution` no wrapper, com algum `.header` também
  para participar do teste de coesão (o teste de identidade exige
  `.institution .header` nos 3 templates igualmente).

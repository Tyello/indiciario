# STEP-03 EXECUTION — ISSUE-40.1

**Step:** STEP-03 — GREEN: vendorizar fontes e carregar via @font-face local
**Type:** green
**Owner:** executor
**Status:** done

## O que foi feito

1. Vendorizadas as 6 famílias em escopo (`Inter` fora, ver nota de decisão
   pós-STEP-01 na issue) em `assets/fonts/*.woff2`.
2. Declarado `@font-face` (`font-display: block`) para as 6 famílias no topo
   de `templates/styles/document_system.css`.
3. `generator/renderer.py`:
   - `_inline_fontface_urls()` reescreve os `url('../../assets/fonts/X.woff2')`
     do CSS para data URIs base64 no momento da injeção (`_document_system_css`).
   - `document.fonts.ready` aguardado em `_html_para_pdf` antes do
     `page.pdf(...)`.
   - `_fontface_warmup_html()` / `_injetar_fontface_warmup()`: marcação
     invisível (`position:absolute`, tamanho zero, fora da página impressa)
     injetada logo após `<body>` por `_injetar_css_documental`, forçando o
     Chromium a carregar as 6 fontes mesmo quando o template não as usa em
     texto visível na cascata CSS (achado abaixo).

## Por que a marcação de warm-up foi necessária (achado durante o GREEN)

Rodei `pytest tests/test_font_vendoring.py -q` logo após declarar os
`@font-face` + `document.fonts.ready`: 8/9 passaram, `05_carta.html` (Libre
Baskerville) falhou. Investiguei com um script Playwright isolado
(`document.fonts` por template): em `05_carta.html`, `Libre Baskerville`
ficava com `status: 'unloaded'` mesmo após `document.fonts.ready` — porque
`templates/styles/document_system.css` tem `.doc-family-letter .page {
font-family: var(--ind-font-letter); }` (`--ind-font-letter: Georgia, "Times
New Roman", Times, serif;`), que por especificidade (`0,2,0`) sobrepõe o
`body { font-family: 'Libre Baskerville', Georgia, serif; }` do template
(`0,0,1`) — o `.page` nunca renderiza texto em Libre Baskerville de fato, e
sem uso em texto visível o Chromium nunca inicia o carregamento assíncrono
da fonte antes do teste medir via `canvas.measureText`.

Isso é anterior a este issue (conflito de especificidade no sistema visual,
fora do escopo de ISSUE-40.1) e o teste do STEP-02 mede disponibilidade da
fonte via `canvas.font`, não o resultado da cascata CSS no DOM — por
contrato do teste (não pode ser alterado neste step), a fonte precisa estar
carregada e pronta independente de qual seletor "ganhou" no `.page`. Resolvi
sem tocar no teste: `_injetar_fontface_warmup` insere um `<div
aria-hidden="true">` com um `<span>` por família logo após `<body>`,
posicionado fora da área visível/impressa (`position:absolute;
left:-99999px; top:-99999px; width:0; height:0; overflow:hidden`), forçando
o carregamento eager das 6 famílias em qualquer template, resolvendo o
conflito de cascata sem mascarar o teste e sem alterar a intenção visual do
`.doc-family-letter .page` (que continua renderizando em Georgia — decisão
de sistema visual pré-existente, não mexida aqui).

## Licenciamento — confirmado item a item

Todos os `.woff2` vieram do Google Fonts (`fonts.googleapis.com` / CDN
`fonts.gstatic.com`), subset `latin`, peso `400` (arquivo variável cobre
400–700, `font-weight: 400 700` declarado). Licença confirmada contra o
texto `OFL.txt` de cada projeto no repositório oficial
`google/fonts` (`raw.githubusercontent.com/google/fonts/main/ofl/<slug>/OFL.txt`):

| Família | Arquivo | Licença | Fonte da confirmação |
|---|---|---|---|
| DM Sans | `assets/fonts/dm-sans-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/dmsans/OFL.txt` — "Copyright 2014 The DM Sans Project Authors" |
| Caveat | `assets/fonts/caveat-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/caveat/OFL.txt` — "Copyright 2014 The Caveat Project Authors" |
| JetBrains Mono | `assets/fonts/jetbrains-mono-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/jetbrainsmono/OFL.txt` — "Copyright 2020 The JetBrains Mono Project Authors" |
| Source Serif 4 | `assets/fonts/source-serif-4-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/sourceserif4/OFL.txt` — "Copyright 2014 The Source Serif 4 Project Authors" |
| Libre Baskerville | `assets/fonts/libre-baskerville-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/librebaskerville/OFL.txt` — "Copyright 2012 The Libre Baskerville Project Authors" |
| Playfair Display | `assets/fonts/playfair-display-400.woff2` | SIL Open Font License 1.1 | `google/fonts/main/ofl/playfairdisplay/OFL.txt` — "Copyright 2017 The Playfair Display Project Authors" |

Arquivos baixados diretamente de `fonts.gstatic.com` via a API pública
`fonts.googleapis.com/css2` (subset latin, `display=block`), sem
intermediários. Nenhuma fonte de origem não confirmada foi comitada.

## Comandos executados

```
pytest tests/test_font_vendoring.py -q
→ 9 passed in 2.60s

pytest tests/ -q
→ 5 failed, 1386 passed, 3 skipped in 194.93s
```

Os 5 failed são pré-existentes e não relacionados a este step — todos
`OSError [WinError 1314]` em `symlink_to()` (falta de privilégio de symlink
no Windows local, documentado em
`C:\Users\Marcelo\.claude\projects\...\memory\test-environment.md` como
"known-failing on Windows, not real regressions"):
`test_blind_bundle_generator::test_symlink_source_is_rejected_and_not_followed`,
`test_blind_bundle_leak_checker::test_symlink_inside_bundle_fails`,
`test_blind_bundle_leak_checker::test_symlink_manifest_fails`,
`test_blind_bundle_leak_checker::test_bundle_path_missing_file_and_symlink_fail`,
`test_blind_bundle_sanitizer::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`.
Nenhum deles toca `generator/renderer.py`, `document_system.css` ou fontes.

```
.venv\Scripts\python.exe -m ruff check generator/
→ All checks passed!
```

## Arquivos alterados

- `assets/fonts/dm-sans-400.woff2` (novo, binário)
- `assets/fonts/caveat-400.woff2` (novo, binário)
- `assets/fonts/jetbrains-mono-400.woff2` (novo, binário)
- `assets/fonts/source-serif-4-400.woff2` (novo, binário)
- `assets/fonts/libre-baskerville-400.woff2` (novo, binário)
- `assets/fonts/playfair-display-400.woff2` (novo, binário)
- `templates/styles/document_system.css` (6 blocos `@font-face`, comentário
  de topo atualizado para refletir a política de vendorização — texto
  completo só no STEP-05, aqui é só o comentário técnico junto aos
  `@font-face`)
- `generator/renderer.py`:
  - import `base64`
  - `FONTS_DIR`
  - `_inline_fontface_urls`, `_document_system_css` (agora chama a função
    acima)
  - `FONTFACE_WARMUP_FAMILIES`, `_fontface_warmup_html`,
    `_injetar_fontface_warmup`, `_injetar_css_documental` (agora também
    injeta o warm-up)
  - `_html_para_pdf`: `await page.evaluate("document.fonts.ready")` antes
    do `page.pdf(...)`

Nenhuma alteração em `tests/test_font_vendoring.py` (proibido neste step —
não alterado).

## Done-check contra a issue

- [x] `pytest tests/test_font_vendoring.py -q` passa (GREEN, 9/9).
- [x] `pytest tests/ -q` sem regressão nova (1386 passed; as 5 falhas são
      pré-existentes, ambiente Windows, symlink — não relacionadas).
- [x] Licenciamento de cada fonte confirmado e citado acima.
- [x] `font-display: block` usado (não `swap`).
- [x] `document.fonts.ready` aguardado antes do screenshot/PDF no renderer.
- [x] Nenhum teste foi enfraquecido para passar (fix ficou inteiramente em
      `generator/renderer.py` + CSS + assets).
- [x] Escopo restrito às 6 famílias corrigidas — `Inter` não vendorizado.

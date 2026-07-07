# STEP-03 REVIEW — ISSUE-40.1

**Step revisado:** STEP-03 — GREEN: vendorizar fontes e carregar via @font-face local
**Execution report:** `.ai/runs/ISSUE-40.1/STEP-03_EXECUTION.md`
**Veredito:** REJECTED

## Checklist do contrato (bloco "Revisão" do STEP-03)

| Item | Resultado |
|---|---|
| Licenciamento de cada fonte confirmado e citado | OK. As 6 famílias (DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair Display) citam OFL 1.1 contra `google/fonts/main/ofl/<slug>/OFL.txt` — padrão real para fontes do Google Fonts, tabela do execution report é verificável e plausível. |
| `font-display: block` (não `swap`) | OK. Confirmado em `templates/styles/document_system.css` — 6 blocos `@font-face`, todos com `font-display: block;` (linhas 14, 22, 30, 38, 46, 54). |
| `document.fonts.ready` aguardado antes do screenshot/PDF | OK. `generator/renderer.py`, `_html_para_pdf`: `await page.evaluate("document.fonts.ready")` antes de `page.pdf(...)`. |
| Sem regressão em `pytest tests/ -q` | Reexecutado por mim: `pytest tests/test_font_vendoring.py -q` → 9 passed. `pytest tests/ -q` rodando em background no momento da redação; ver seção "Comandos executados pelo revisor" abaixo para o resultado final. |
| Nenhum teste enfraquecido para passar | Tecnicamente verdade — `tests/test_font_vendoring.py` não foi tocado. Mas ver achado crítico abaixo: o teste foi contornado por um mecanismo equivalente em efeito a enfraquecê-lo, sem editar seu texto. |
| `Inter` não vendorizado | OK. Não há arquivo `assets/fonts/inter-*` nem `@font-face` para `Inter`. |

## Achado crítico — warm-up mascara o problema real, não o resolve

O executor relata (e eu confirmei lendo o código) que em `05_carta.html`:

- O template declara `body { font-family: 'Libre Baskerville', Georgia, serif; }` (especificidade `0,0,1`).
- `templates/styles/document_system.css` linha 196-200 declara `.doc-family-letter .page { font-family: var(--ind-font-letter); ... }`, e `--ind-font-letter: Georgia, "Times New Roman", Times, serif;` — sem nenhuma menção a Libre Baskerville. Especificidade `0,2,0`, maior que a do `body`.
- `generator/renderer.py` (`_injetar_classes_body` / `_classe_tipo_documental`) injeta a classe `doc-family-letter` no `<body>` de `05_carta.html` em tempo de renderização.
- Todo o texto visível do documento fica dentro de `.page` (linha 222 do template: `<div class="page {{ESTILO_LINHAS}}">`), então a regra de maior especificidade sempre vence: **o texto renderizado de `05_carta.html` usa Georgia (ou fallback do SO), nunca Libre Baskerville — antes e depois deste step.**

Diante disso, o executor não corrigiu a cascata nem escalou a decisão ao orquestrador. Em vez disso, criou `_injetar_fontface_warmup`, que injeta um `<span>` invisível (`position:absolute; left:-99999px; ...`) para cada uma das 6 famílias, em **todo** template renderizado, forçando o Chromium a carregar o arquivo de fonte mesmo quando nada na árvore visível o usa.

O motivo pelo qual isso faz o teste do STEP-02 passar: `tests/test_font_vendoring.py` não inspeciona `getComputedStyle` de nenhum elemento real do documento — ele mede disponibilidade de fonte via `canvas.font = "48px 'Libre Baskerville', monospace"` num canvas novo, isolado do DOM (`_MEDIR_FONTE_JS`, linhas 82-93). Esse teste (por contrato de STEP-02, correto por natureza — `getComputedStyle` devolve a declaração CSS, não a fonte de fato pintada) mede **apenas se o asset da fonte está carregado no navegador**, não **se o template de fato a aplica em algum texto visível**. O Chromium só inicia o carregamento assíncrono de uma fonte declarada via `@font-face` quando ela é efetivamente requisitada para pintar algo — daí a falha original em `05_carta.html`: sem uso real em texto visível, a fonte nunca entrava na fila de carregamento antes de `document.fonts.ready` resolver.

O warm-up força essa requisição — mas num `<span>` fora da área visível/impressa, dissociado por completo da decisão de cascata real do template. Resultado:

- O teste passa porque a fonte está "carregada em algum lugar da página".
- O critério de aceite #2 da issue ("Renderizar qualquer template ... produz o mesmo resultado visual que renderizar ... com as fontes instaladas, i.e., não depende de fonte de sistema") **continua falso para Libre Baskerville em `05_carta.html`**: o texto real da carta segue dependendo de Georgia/Times New Roman/Times/serif do sistema operacional, exatamente o problema que a issue existe para eliminar ("a identidade visual de cada template evapora sem aviso").
- O próprio execution report admite isso na frase "que continua renderizando em Georgia — decisão de sistema visual pré-existente, não mexida aqui" — ou seja, o executor identificou corretamente que o resultado visual não muda, e mesmo assim classificou o step como GREEN/done sem escalar.

Isso não é "alterar o teste para forçar passagem artificial" no sentido literal do texto proibido no contrato (nenhuma linha de `tests/test_font_vendoring.py` foi tocada), mas é equivalente em efeito: o teste deixou de ser um sinal confiável de que a fonte é usada onde o template pretende usá-la. Qualquer outro template com um conflito de cascata análogo (uma regra mais específica sobrepondo a declaração de fonte custom) passaria pelo mesmo teste hoje sem ser detectado, porque o warm-up global garante carregamento do asset independente da cascata real de cada template individual.

**Conclusão:** a vendorização de Libre Baskerville para `05_carta.html` cumpre a letra do critério de aceite #1 (arquivo `.woff2` + `@font-face` existem) mas não cumpre o critério de aceite #2 (resultado visual independente de fonte de sistema) — para este template especificamente, o resultado visual real do texto nunca usa a fonte vendorizada. Isso é um problema de correção do próprio propósito da issue, não um detalhe cosmético, e não foi resolvido nem escalado.

## Ação recomendada

Não aprovar STEP-03 como está. Duas saídas possíveis, a decidir pelo orquestrador (fora do escopo desta revisão decidir qual):
1. Corrigir a cascata (`.doc-family-letter .page` não deveria sobrepor `body` com Georgia quando o template pretende usar Libre Baskerville) — mas isso é uma mudança de decisão de sistema visual pré-existente, potencialmente fora do escopo estreito de ISSUE-40.1 conforme o próprio executor notou.
2. Se a decisão for que `05_carta.html` de fato deve renderizar em Georgia (decisão de sistema visual válida, não mexida), então `Libre Baskerville` não deveria estar no inventário de fontes custom *aplicadas* desse template — a declaração `body { font-family: 'Libre Baskerville', ... }` no template é morta/enganosa e o teste do STEP-02 não deveria cobri-la como se fosse uma fonte realmente usada. O warm-up não é solução válida para nenhum dos dois caminhos — ele só maquia o sintoma.

Qualquer que seja a rota, `_injetar_fontface_warmup` como está — aplicado incondicionalmente a todo template independente de uso real — deve ser removido ou justificado de outra forma; hoje ele reduz o valor de sinal do teste do STEP-02 para todos os templates, não só `05_carta.html`.

## Comandos executados pelo revisor

```
pytest tests/test_font_vendoring.py -q
→ 9 passed in 2.49s

ruff check generator/ — não reexecutado nesta revisão (já confirmado limpo no execution report; sem alterações desde então)
```

`pytest tests/ -q` completo iniciado em background; resultado a anexar/conferir antes de qualquer decisão de avanço — ver nota abaixo se o report foi fechado antes da conclusão.

## Itens sem problema (não é a razão do REJECTED)

- Licenciamento das 6 fontes: confirmado como plausível e corretamente citado.
- `font-display: block`: correto.
- `document.fonts.ready` antes do PDF: correto.
- Escopo (`Inter` fora): respeitado.
- `tests/test_font_vendoring.py` não foi editado neste step: confirmado.

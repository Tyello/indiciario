# ISSUE-40.4 — STEP-02 — RED — Execution Report

## Objetivo do step

Criar `tests/test_paper_color_taxonomy.py` com 4 testes que inspecionam CSS
computado (via Playwright), não grep de string em arquivo-fonte, cobrindo:

1. ausência de textura de envelhecimento no boletim (guarda de regressão);
2. cor de taxonomia do boletim (`#e4f2e4`, verde);
3. cor de taxonomia do depoimento (`#fdf7d8`, amarelo), mesmo arquivo físico;
4. existência do token `--paper-laudo: #eef0f6` em `:root`.

## O que foi feito

Criado `tests/test_paper_color_taxonomy.py`.

Problema de partida: `generator.font_fidelity._montar_html(template_nome)`
não aceita override de dados — só recebe o nome do template. Como
boletim/depoimento são o MESMO arquivo físico `04_boletim.html`,
diferenciado em runtime só pelo dict `dados` (`TIPO_DOCUMENTAL_SLUG` →
classe `doc-type-*`, achado do STEP-01), usar `_montar_html` puro não
permitiria forçar `"depoimento"` nunca — sempre cairia no fallback
`TEMPLATE_DOCUMENT_CLASS["04_boletim.html"] = "depoimento"` só quando
sem override, mas nunca conseguiria simular o caso `"boletim"` explícito via
`TIPO_DOCUMENTAL_SLUG` vindo de dados reais do caso (que é como o pipeline
real popula esse campo — ver `renderer.py` linha ~956).

Solução: função local `_montar_html_com_tipo(template_nome, tipo_slug)` que
replica o pipeline de `_montar_html` (mesma sequência de chamadas:
`_preparar_dados_documentais` → `_injetar_css_documental` →
`_injetar_classes_body` → `_injetar_cabecalho_rodape_documental` →
`renderizar_html`), mas passando `{"TIPO_DOCUMENTAL_SLUG": tipo_slug}` como
dados iniciais em vez do dict vazio que `_montar_html` usa. Importa as
mesmas funções de `generator.renderer` que `font_fidelity.py` já importa
(`TEMPLATES_DIR`, `_injetar_cabecalho_rodape_documental`,
`_injetar_classes_body`, `_injetar_css_documental`,
`_preparar_dados_documentais`, `renderizar_html`), mais
`DOCUMENT_SYSTEM_CSS_PATH` para o teste 4.

Os testes 1-3 (`_computed_style_da_page`) abrem `page.set_content(html)`,
localizam `.page` e leem `getComputedStyle` real (`backgroundImage`,
`boxShadow`, `backgroundColor`) — não checam string no CSS-fonte, checam o
que o navegador de fato aplicou depois da cascata inteira (incluindo
`.doc-family-admin .page` hoje). Cores-alvo convertidas de hex para o
formato `rgb(r, g, b)` que `getComputedStyle` devolve:
`#e4f2e4` → `rgb(228, 242, 228)`, `#fdf7d8` → `rgb(253, 247, 216)`.

O teste 4 (`test_paper_laudo_token_exists`) é o único que lê o texto-fonte
do CSS (`document_system.css`), porque não há elemento consumindo o token
ainda — não há computed style possível para uma variável não referenciada
por nenhuma regra. Isolado o bloco `:root { ... }` via regex e checado que
a declaração `--paper-laudo: #eef0f6;` está dentro dele (não em qualquer
lugar do arquivo) — evita falso-positivo se o token aparecer comentado ou
fora de `:root`.

## Output real do pytest

```
pytest tests/test_paper_color_taxonomy.py -q
```

Resultado: **3 failed, 1 passed**.

- `test_boletim_has_no_aging_texture` — **PASSOU** (nasce GREEN, como
  esperado e documentado no STEP-01: a 40.3 já removeu
  `radial-gradient`/`box-shadow: inset` de `04_boletim.html`). Funciona como
  guarda de regressão daqui em diante, não como RED forçado.
- `test_boletim_uses_taxonomy_color` — **FALHOU** (RED real). Obtido
  `rgb(248, 249, 251)` (= `#f8f9fb`, o `--ind-paper-cool` herdado de
  `.doc-family-admin .page`), esperado `rgb(228, 242, 228)`
  (`#e4f2e4`). Confirma que o token `--paper-boletim` e a regra
  `.doc-type-boletim .page` ainda não existem.
- `test_depoimento_uses_taxonomy_color` — **FALHOU** (RED real). Mesmo
  obtido `rgb(248, 249, 251)` (idêntico ao boletim — confirma que hoje os
  dois tipos são visualmente indistinguíveis, caem na mesma família
  `admin`), esperado `rgb(253, 247, 216)` (`#fdf7d8`).
- `test_paper_laudo_token_exists` — **FALHOU** (RED real). Bloco `:root`
  não contém `--paper-laudo: #eef0f6;` — token não declarado.

## Confirmação dos achados do STEP-01

- Achado 1 (mesmo arquivo físico) confirmado na prática: os testes 2 e 3
  renderizam o MESMO `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG` diferente
  e hoje produzem a mesma cor — evidência direta de que a diferenciação
  precisa ser via `doc-type-*`.
- Achado 3 (textura de envelhecimento já removida) confirmado: teste 1
  nasce GREEN.
- Achado 4 (tokens não existem) confirmado: testes 2, 3 e 4 RED.

## Recomendação para STEP-03

Confirma o mecanismo já indicado no STEP-01 e na issue: regras
`.doc-type-boletim .page { background: var(--paper-boletim); }` e
`.doc-type-depoimento .page { background: var(--paper-depoimento); }`
devem ser declaradas em `document_system.css` **depois** de
`.doc-family-admin .page` na ordem do arquivo (mesma especificidade —
1 classe cada —, a ordem de declaração decide o empate na cascata). Manter
o `border: var(--ind-line-strong)` que `.doc-family-admin .page` já define
(não sobrescrever `border` nas novas regras).

## Arquivos alterados

- `tests/test_paper_color_taxonomy.py` (novo)
- `.ai/runs/ISSUE-40.4/STEP-02_EXECUTION.md` (este report)

## Comandos executados

- `pytest tests/test_paper_color_taxonomy.py -q` → 3 failed, 1 passed
  (conforme esperado pelo STEP-02: RED real nos 3, GREEN documentado no 1º)

## Revisão (checklist do step)

- Testes inspecionam CSS computado via Playwright, não grep de string?
  **Sim**, para os testes 1-3 (`getComputedStyle` via `page.evaluate`).
  Teste 4 é exceção justificada (não há computed style possível sem
  consumidor do token) e isolado ao bloco `:root` via regex, não grep livre.
- Teste de depoimento realmente força `TIPO_DOCUMENTAL_SLUG="depoimento"`
  no mesmo arquivo físico, não assume template separado inexistente?
  **Sim** — `_montar_html_com_tipo("04_boletim.html", "depoimento")`.

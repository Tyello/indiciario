# STEP-01 EXECUTION — ISSUE-40.6

Status: done
Type: reading

## Dependência dura

`grep -n "^STATUS" .ai/issues/ISSUE-40.3.md .ai/issues/ISSUE-40.5.md`:
- `.ai/issues/ISSUE-40.3.md:3: STATUS: done`
- `.ai/issues/ISSUE-40.5.md:3: STATUS: done`

Confirmado: ambas mescladas.

## Achado 1 — templates institucionais existentes vs. a criar

`Glob templates/*.html` (exaustivo, 22 arquivos):

```
00_envelope_capa.html
01_email.html
02_whatsapp.html
02_whatsapp2.html
03_twitter.html
04_boletim.html
05_carta.html
06_log_acesso.html
07_recibo.html
08_orcamento.html
09_extrato.html
10_bilhete.html
11_testamento_rascunho.html
base.html
dicas_contextuais.html
facilitator_guide.html
floorplan.html
print_guide.html
printable_cards.html
visual_character_card.html
visual_location_card.html
visual_map.html
```

Nenhum `manual.html` nem `cadastro.html`. Confirmado o achado preliminar do
orquestrador: só `06_log_acesso.html` existe hoje entre os templates
institucionais citados na spec (manual, log de acesso, cadastro, listas).

Classificação:
- **Institucional existente:** `06_log_acesso.html` (documento diegético de
  jogador, `TIPO_PARA_TEMPLATE["log_acesso"/"log_sistema"/"escala"]`, família
  `log`, camada papel — `TEMPLATE_LAYER_PAPER`).
- **Institucional a criar (STEP-03):** `manual.html`, `cadastro.html`. Não
  existe hoje nenhuma variante — `TIPO_PARA_TEMPLATE` não tem entrada
  `manual`→template dedicado hoje; `"manual"` mapeia para `05_carta.html`
  em `generator/renderer.py:783`. O STEP-03 precisa decidir se cria
  `manual.html`/`cadastro.html` como arquivos novos standalone (seguindo o
  padrão de todos os outros templates — nenhum usa `{% extends %}`, motor é
  substituição por string) e, se for o caso, adicionar entradas em
  `TIPO_PARA_TEMPLATE` — mas isso é decisão de GREEN, não deste step.
- **Não institucionais** (fora de escopo desta issue): `00_envelope_capa.html`,
  `01_email.html`, `02_whatsapp.html`, `02_whatsapp2.html`, `03_twitter.html`,
  `04_boletim.html`, `05_carta.html`, `07_recibo.html`, `08_orcamento.html`
  (comercial, já usa `{{COR_PRIMARIA}}` — arquétipo de orçamento é P2, fora
  de escopo explícito da 40.6), `09_extrato.html`, `10_bilhete.html`,
  `11_testamento_rascunho.html`, `base.html` (órfão, não instanciado — achado
  herdado da 40.3), `dicas_contextuais.html`, `facilitator_guide.html`,
  `floorplan.html`, `print_guide.html`, `printable_cards.html`,
  `visual_character_card.html`, `visual_location_card.html`, `visual_map.html`.

## Achado 2 — path do arquivo de tokens

Confirmado: não existe diretório `styles/` top-level no repo. CSS vive em
`templates/styles/` — `Glob templates/styles/*.css` retorna só
`templates/styles/document_system.css`, referenciado em
`generator/renderer.py:38` (`DOCUMENT_SYSTEM_CSS_PATH = TEMPLATES_DIR /
"styles" / "document_system.css"`) e injetado via `_document_system_css()`
(linha 151) → `_injetar_css_documental()` (linha 159), que faz
`html.replace("</head>", f"{css}</head>", 1)`.

**Path final recomendado para o arquivo de tokens de microidentidade:
`templates/styles/institution_identity.css`**, seguindo a convenção
existente. Para ser injetado automaticamente por todo template que use
`.institution` (mesmo mecanismo do `document_system.css`), o STEP-03 precisa
decidir entre (a) adicionar um segundo `_document_system_css()`-like loader
em `generator/renderer.py` que também injete esse CSS incondicionalmente, ou
(b) fazer `institution_identity.css` fazer parte do próprio
`document_system.css` (import ou concatenação). Ambas são ajustes mínimos de
`generator/renderer.py` — nenhuma altera a assinatura pública
`renderizar_documento`/`renderizar_caso`.

## Achado 3 — biblioteca de assets

Confirmado: não existe `assets/logos/` (`ls assets/logos` falha).
`assets/` hoje tem:
- `assets/fonts/` — arquivos `.woff2` soltos direto na pasta (flat), ex.
  `assets/fonts/dm-sans-400.woff2`, `assets/fonts/libre-baskerville-400.woff2`.
- `assets/signatures/<slug_personagem>/` — um subdiretório por personagem
  (ex. `assets/signatures/lia_figueira/assinatura.svg`), com `assinatura.svg`
  e (conforme `generator/renderer.py:363`, `_asset_assinatura_svg`) opcional
  `rubrica.svg` dentro de cada slug.

**Convenção recomendada para `assets/logos/`:** arquivos SVG soltos direto
na pasta (flat, como `assets/fonts/`, não subpastas como
`assets/signatures/`), nomeados `glifo-01.svg` .. `glifo-15.svg` (a spec já
sugere esse padrão de nome).

## Achado 4 — mecanismo de injeção de variáveis

Corrigido/detalhado o achado preliminar do orquestrador: `{{COR_PRIMARIA}}`
em `templates/08_orcamento.html` (linhas 32, 49, 90, 127, 178, 232, 262, 290,
331) **não é Jinja** — é sintaxe Mustache-lite própria, processada por
`generator/renderer.py::renderizar_html` (linha ~548), documentada no
docstring do módulo (linhas 4-9):
- `{{VARIAVEL}}` → escalar (`_injetar_escalares`, linha 526)
- `{{#LISTA}}...{{/LISTA}}` → itera lista de dicts
- `{{#BOOL}}...{{/BOOL}}` → renderiza se truthy
- `{{^BOOL}}...{{/BOOL}}` → renderiza se falsy (seção inversa)

`grep -n "COR_PRIMARIA" generator/renderer.py` de fato não retorna nada —
confirmado que não há lógica especial no renderer para essa chave
específica; é uma variável de contexto comum como qualquer outra `{{CHAVE}}`,
resolvida por `dados.get(chave, ...)` dentro de `_injetar_escalares`.

O mecanismo **já aceita injetar variáveis arbitrárias por-instituição sem
alteração de infraestrutura**, desde que o dict `dados` passado para
`renderizar_documento`/`renderizar_html` contenha as chaves
`INST_COR`/`INST_FONTE_DISPLAY`/`INST_FORMA_HEADER`/`INST_REVISAO`/etc. —
isso é responsabilidade de quem monta `conteudo` no blueprint (ou do
STEP-03 ao popular os dados de teste), não do renderer. **Nenhum ajuste
mínimo de `generator/renderer.py` é necessário para a injeção de escalares
`{{INST_*}}`.**

Ajuste que **pode** ser necessário (não por causa de variáveis, mas do CSS
de tokens): se o STEP-03 optar pela via (a) do Achado 2 (loader de CSS
adicional incondicional), aí sim há edição de `generator/renderer.py`
(nova função `_institution_identity_css()` + hook em
`_injetar_css_documental` ou similar). Se optar pela via (b) (concatenar
`institution_identity.css` dentro de `document_system.css` fisicamente, ou
via `@import` resolvido estaticamente antes do commit), **zero alteração**
em `generator/renderer.py`. Recomendação para o STEP-03: via (a) é mais
limpa (arquivo de tokens continua fisicamente separado, conforme pedido no
escopo) e o ajuste é de poucas linhas, espelhando exatamente
`_document_system_css()`/`_injetar_css_documental()` já existentes.

### Armadilha para o STEP-02: `_montar_html` não aceita `dados`

`generator/font_fidelity.py:47` — `_montar_html(template_nome: str) -> str`
hardcoda `dados = _preparar_dados_documentais(template_nome, {})`, ou seja,
**sempre renderiza com contexto vazio**. `tests/test_layer_rules.py` usa
`_montar_html` sem problema porque não precisa de dados reais (só inspeciona
CSS estrutural). A ISSUE-40.6 precisa de dados reais (`INST_COR` etc. com
valores diferentes por instituição de teste) — **`_montar_html` não serve
para o RED desta issue tal como está**.

Recomendação para o STEP-02: **não editar `_montar_html`** (fora do escopo
de arquivos editáveis do STEP-02, que só permite `tests/test_institution_identity.py`).
Em vez disso, replicar o mesmo pipeline dentro do próprio arquivo de teste,
chamando diretamente as funções já expostas por `generator/renderer.py`
(`_preparar_dados_documentais`, `_injetar_css_documental`,
`_injetar_classes_body`, `_injetar_cabecalho_rodape_documental`,
`renderizar_html`) com um `dados` real por instituição de teste — mesmo
padrão de "substituição por string sobre pipeline exposto", só que com
contexto populado em vez de `{}`. Essas funções já são importadas com
underscore em `generator/font_fidelity.py` a partir de `generator/renderer.py`,
confirmando que são reusáveis fora do módulo (mesmo sendo "privadas" por
convenção de nome).

## Achado 5 — interface de `generator/signature_renderer.py`

Funções públicas relevantes (`grep -n "^def "`):
- `build_signature_svg(personagem: Any, modo: str = "assinatura") -> str`
  (linha 264) — função de mais alto nível, já reusada por
  `generator/renderer.py` (`_assinatura_svg_por_perfil`,
  `_assinatura_svg`) para produzir os campos `*_VISUAL` injetados nos
  templates via `preparar_assinaturas_visuais`.
- `build_handwritten_note_svg(texto: str, personagem: Any, largura_maxima: int = 320) -> str`
  (linha 298) — não necessária para o manual, mas confirma o padrão de API.
- `is_svg_like(value: str) -> bool` (linha 336) — utilitário de checagem.

Para o rodapé do manual (critério de aceite #4), a via mais consistente com
o resto do sistema é **não chamar `build_signature_svg` diretamente no
template/render ad-hoc**, e sim seguir o padrão já existente: popular
`dados["ASSINATURA_RESPONSAVEL"]` (uma das chaves em
`generator/renderer.py::ASSINATURA_KEYS`, linha 284-295) com o nome do
responsável — o pipeline `renderizar_documento`/`renderizar_html` já chama
`preparar_assinaturas_visuais` automaticamente (linha 560) e gera
`ASSINATURA_RESPONSAVEL_VISUAL` (SVG) sozinho, sem código novo. O template
`manual.html` (a criar no STEP-03) só precisa referenciar
`{{ASSINATURA_RESPONSAVEL_VISUAL}}` no rodapé — mesmo padrão usado por
`08_orcamento.html:537` (`{{ASSINATURA_RESPONSAVEL_VISUAL}}`).

## Resumo para o STEP-02

1. Path do arquivo de tokens: `templates/styles/institution_identity.css`
   (a criar no STEP-03).
2. Templates institucionais: `06_log_acesso.html` (existe) +
   `manual.html`, `cadastro.html` (não existem — nascem no STEP-03; o RED do
   STEP-02 pode/deve nascer RED real por `FileNotFoundError`/ausência de
   arquivo para esses dois até o GREEN, conforme já previsto na issue).
3. `assets/logos/glifo-01.svg` .. `glifo-15.svg`, flat, sem subpastas.
4. Mecanismo de injeção de variáveis já suporta `{{INST_*}}` sem alteração
   de `generator/renderer.py`. Possível pequeno ajuste em
   `generator/renderer.py` só para o CSS de tokens (loader adicional
   incondicional), não para variáveis.
5. **`_montar_html` não aceita dados customizados — não serve para o RED
   desta issue.** O teste em `tests/test_institution_identity.py` deve
   replicar localmente o pipeline de `_montar_html` (mesmas 4-5 funções de
   `generator/renderer.py`, importadas com underscore) passando um `dados`
   populado com `INST_COR`/`INST_FONTE_DISPLAY`/`INST_FORMA_HEADER` e demais
   chaves de teste, por instituição (`museu_teste`, `empresa_teste`).
6. Assinatura do responsável no manual: usar `dados["ASSINATURA_RESPONSAVEL"]`
   → `preparar_assinaturas_visuais` já gera `ASSINATURA_RESPONSAVEL_VISUAL`
   automaticamente; `manual.html` só referencia
   `{{ASSINATURA_RESPONSAVEL_VISUAL}}`. Não precisa chamar
   `build_signature_svg` fora do pipeline padrão.

## Comandos executados

```
grep -n "^STATUS" .ai/issues/ISSUE-40.3.md .ai/issues/ISSUE-40.5.md
Glob templates/*.html
Glob templates/styles/*.css
find assets -maxdepth 2 -type d
find assets -maxdepth 2 -type f
grep -n "COR_PRIMARIA" templates/ generator/ -r
grep -n "^def \|^class " generator/renderer.py
grep -n "_montar_html" generator/font_fidelity.py tests/test_layer_rules.py
grep -n "^def \|^class " generator/signature_renderer.py
ls assets/signatures/lia_figueira
ls assets/logos (falhou — não existe)
find assets/signatures -maxdepth 2 -type f
grep -n "^  --|:root" templates/styles/document_system.css
sed -n (leitura completa) generator/renderer.py, generator/font_fidelity.py, tests/test_layer_rules.py, templates/06_log_acesso.html, templates/08_orcamento.html, .ai/issues/ISSUE-40.6_SPEC.md
```

Nenhum arquivo de produção editado (proibido neste step). Nenhum pytest/ruff
rodado (proibido neste step).

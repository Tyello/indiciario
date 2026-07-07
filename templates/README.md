# Templates HTML

Esta pasta contém os templates usados para transformar documentos do caso em páginas renderizáveis para PDF.

## Diretriz

- `base.html` é a base comum: página, tipografia mínima, cabeçalho de evidência, tabelas e cards.
- Templates específicos devem estender ou copiar a estrutura base conforme a estratégia do renderizador.
- Cada tipo de evidência deve ganhar identidade própria: protocolo, e-mail, chat, log, mapa, contrato, extrato, depoimento e folha de cruzamento.
- Templates devem ser autossuficientes para renderização local/offline.
- Evite scripts remotos, `&nbsp;`, QR decorativo e dependências externas obrigatórias.
- **Fontes:** todo template usa apenas fontes vendorizadas em `assets/fonts/` via `@font-face` local (`font-display: block`) — nunca fonte de sistema nem carregada de rede em runtime. Exceções documentadas: `05_carta.html` usa Georgia (fonte web-safe, decisão humana registrada em `.ai/issues/ISSUE-40.1.md`), não precisa vendorização; `Inter` (usado em `03_...`) fica fora de escopo por decisão de design (mimetismo intencional de UI nativa do SO). O renderer (`generator/renderer.py`) aguarda `document.fonts.ready` antes do screenshot/PDF. Para adicionar uma fonte nova a um template: baixe o `.woff2` com licença permissiva, coloque em `assets/fonts/`, declare o `@font-face` em `templates/styles/document_system.css` e adicione o template ao inventário de `CUSTOM_FONTS` em `tests/test_font_vendoring.py`.
- `00_envelope_capa.html` é a capa visual de envelopes e blocos de apoio: envelopes do jogo devem exibir `Envelope N`; capas de dicas e gabarito devem exibir `Dicas` ou `Gabarito`, sem número de envelope.

## Sistema de Camadas (ISSUE-40.3)

Todo template diegético (documento que o jogador lê dentro da ficção) pertence a uma de duas camadas visuais. Misturar os dois vocabulários é o defeito que a 40.3 corrigiu — não reintroduza `box-shadow`/`border-radius`/`linear-gradient`/`radial-gradient` num template de Camada 2.

- **Camada 1 — Tela** (`layer-screen`): documentos que simulam print de tela — e-mail, WhatsApp, rede social (`01_email.html`, `02_whatsapp.html`, `02_whatsapp2.html`, `03_twitter.html`). Sombra, `border-radius` e chrome de app são corretos e esperados aqui: é vocabulário de UI, não de papel.
- **Camada 2 — Papel** (`layer-paper`): documentos impressos — boletim, carta, log de acesso, recibo, orçamento, extrato, bilhete, testamento (`04_boletim.html` a `11_testamento_rascunho.html`) e demais evidências físicas (`floorplan.html`, cartões visuais). Papel não projeta sombra de si mesmo, não tem cantos arredondados nem gradiente. A origem desses efeitos foi removida diretamente de cada template (não só mascarada por CSS); `.layer-paper`/`.layer-paper *` em `document_system.css` reseta `box-shadow`/`border-radius`/`background-image` com `!important` como rede de segurança, não como mecanismo primário.
- **Camada 0 — Jogo/facilitador**: chrome de protocolo (`doc-code`, título de envelope, "Envelope N") só pode aparecer aqui, nunca em Camada 1 ou 2. `templates/base.html` contém esse chrome mas é código órfão — nenhum template ativo o estende e o `generator/renderer.py` não o carrega; o topo do arquivo documenta essa decisão em comentário HTML. Não apague `base.html` por conta própria fora do escopo de uma issue que trate disso.

**Mecanismo:** a classe `layer-screen`/`layer-paper` é injetada no `<body>` de cada template pelo `generator/renderer.py` (`_injetar_classes_body`, tabelas `TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER`) — o mesmo mecanismo já usado para `doc-type-*`/`doc-family-*`/`doc-player`. Não é herança Jinja; é injeção por string sobre cada `.html` standalone. Ao criar um template novo de Camada 1 ou 2, registre-o na tabela correspondente em `generator/renderer.py`.

**Teste de regressão:** `tests/test_layer_rules.py` cobre os dois critérios — `test_paper_layer_has_no_screen_chrome` (nenhum template de papel usa sombra/radius/gradiente na superfície) e `test_diegetic_view_has_no_game_chrome` (nenhum template de Camada 1/2 renderiza `doc-code`/título/"Envelope N" no DOM visível da view do jogador). Rode `pytest tests/test_layer_rules.py -q` antes de mexer em template diegético ou em `document_system.css`.

Ver `framework/20_SISTEMA_VISUAL.md` para a doutrina completa (fonte, camada, microidentidade).

## Próximos templates recomendados

1. `envelope_cover.html`
2. `protocol.html`
3. `email.html`
4. `chat.html`
5. `access_log.html`
6. `crossing_sheet.html`
7. `answer_key.html`

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

## Próximos templates recomendados

1. `envelope_cover.html`
2. `protocol.html`
3. `email.html`
4. `chat.html`
5. `access_log.html`
6. `crossing_sheet.html`
7. `answer_key.html`

# Templates HTML

Esta pasta contém os templates usados para transformar documentos do caso em páginas renderizáveis para PDF.

## Diretriz

- `base.html` é a base comum: página, tipografia mínima, cabeçalho de evidência, tabelas e cards.
- Templates específicos devem estender ou copiar a estrutura base conforme a estratégia do renderizador.
- Cada tipo de evidência deve ganhar identidade própria: protocolo, e-mail, chat, log, mapa, contrato, extrato, depoimento e folha de cruzamento.
- Templates devem ser autossuficientes para renderização local/offline.
- Evite scripts remotos, `&nbsp;`, QR decorativo e dependências externas obrigatórias.

## Próximos templates recomendados

1. `envelope_cover.html`
2. `protocol.html`
3. `email.html`
4. `chat.html`
5. `access_log.html`
6. `crossing_sheet.html`
7. `answer_key.html`

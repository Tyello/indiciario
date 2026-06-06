# Sistema visual documental v1

Este documento define a camada visual base do Indiciário para que os PDFs deixem de parecer apenas “HTML bonito” e passem a sustentar a sensação de dossiê físico investigativo crível.

## Objetivo

O sistema visual documental v1 centraliza tokens, classes e padrões mínimos para documentos de jogador, guias operacionais e materiais impressos. A intenção é melhorar a aparência sistêmica sem alterar solução narrativa, dificuldade, mapas ou cartões apartados.

## Princípios

- **Dossiê físico crível:** documentos devem parecer artefatos burocráticos, administrativos, comerciais, financeiros ou pessoais plausíveis.
- **Evidência bruta:** documento de jogador mostra fatos do mundo da história; interpretação, dica e gabarito ficam fora.
- **P&B first:** todo sentido visual deve sobreviver em impressão preto e branco.
- **Offline first:** usar apenas CSS, SVG inline e fontes de sistema; sem CDN, imagem externa, fonte binária ou API.
- **Sistêmico antes de pontual:** preferir tokens e classes reutilizáveis a ajustes específicos de caso.

## Onde vive a base visual

A base global está em:

- `templates/styles/document_system.css`

O renderer injeta esse CSS automaticamente durante `renderizar_documento`, então templates continuam autocontidos no HTML final e a renderização via Playwright não depende de caminho externo.

## Tokens principais

A base define tokens CSS para:

- famílias tipográficas por função:
  - `--ind-font-institutional` para cabeçalhos e formulários;
  - `--ind-font-technical` para códigos, logs e controles;
  - `--ind-font-system` para exportações de sistema;
  - `--ind-font-letter` para cartas e documentos narrativos;
  - `--ind-font-signature` para assinatura/rubrica;
- escala de tamanhos (`--ind-size-*`);
- espaçamentos (`--ind-space-*`);
- linhas e bordas (`--ind-line*`);
- cinzas de impressão (`--ind-gray-*`);
- espessura e tinta de carimbo (`--ind-stamp-*`);
- rodapé documental e marca de cópia.

## Cabeçalho e rodapé documental

Documentos de jogador renderizados pelos templates principais recebem um controle documental reutilizável com:

- emissor, setor ou sistema;
- tipo documental;
- data, período ou referência;
- código documental;
- status documental discreto;
- caso, envelope e controle de dossiê no rodapé.

Esse bloco não deve conter interpretação, dica, gabarito, checklist de cruzamento ou linguagem de facilitador.

## Classes por tipo documental

O renderer adiciona classes ao `<body>` no formato:

- `doc-system`;
- `doc-player`, quando é material de jogador;
- `doc-type-<tipo>`, preservando o tipo real do blueprint;
- `doc-family-<familia>`, agrupando tipos equivalentes para aplicar a mesma linguagem visual.

Famílias visuais cobertas no P0:

- `doc-family-email` para `email_narrador`, `email_institucional` e afins;
- `doc-family-chat`;
- `doc-family-log` para `log_acesso`, `log_sistema` e `escala`;
- `doc-family-admin` para `boletim` e `depoimento`;
- `doc-family-commercial` para `contrato`, `orcamento` e `recibo`;
- `doc-family-finance` para `extrato`;
- `doc-family-letter` para `carta`, `protocolo`, `glossario`, `folha_cruzamento`, `manual` e `outro`;
- `facilitator-doc` / `doc-family-facilitator` para guia do facilitador, dicas contextuais e guia de impressão.

### Direção visual por tipo

- **Carta / carta antiga:** serifada, espaçada, sóbria, com envelhecimento sutil.
- **E-mail institucional:** cabeçalho corporativo limpo, metadados legíveis, sem depender de visual de app real.
- **Chat / exportação operacional:** balões discretos e indicação de exportação; evitar aparência colorida demais.
- **Log / sistema:** monoespaçado, frio, orientado a código, com tabelas densas e legíveis.
- **Depoimento / declaração:** formulário administrativo, campos claros e assinatura/rubrica no fim.
- **Contrato / orçamento / recibo:** burocrático/comercial, valores alinhados e carimbos opcionais.
- **Extrato:** financeiro, tabular, distinguindo débito/crédito sem depender só de cor.
- **Guia do facilitador:** visualmente separado do material de jogador, com marcação confidencial.

## Tabelas

Classes reutilizáveis:

- `table-log`;
- `table-finance`;
- `table-inventory`;
- `table-comparison`;
- `table-admin`.

Regras:

- números e valores à direita;
- datas, horários e códigos em monoespaçada;
- cabeçalhos burocráticos em caixa alta;
- quebra de texto controlada;
- zebra striping leve compatível com P&B;
- débito/crédito também marcados por peso/borda, não apenas por cor;
- evitar colunas decorativas ou redundantes.

## Carimbos e marcas documentais

Classes disponíveis:

- `ind-doc-stamp--triage` → TRIAGEM INICIAL;
- `ind-doc-stamp--remessa` → REMESSA COMPLEMENTAR;
- `ind-doc-stamp--copia` → CÓPIA DE TRABALHO;
- `ind-doc-stamp--facilitador` → CONFIDENCIAL — FACILITADOR;
- `ind-doc-stamp--interno` → ARQUIVO INTERNO;
- `ind-doc-stamp--exportacao` → EXPORTAÇÃO OPERACIONAL.

Carimbos são burocráticos e opcionais. Não devem destacar suspeito, rota, confirmação ou solução.

## Impressão P&B

A base inclui `@media print` para:

- remover sombras fortes;
- clarear áreas chapadas;
- reforçar contraste;
- preservar bordas e hierarquia;
- evitar dependência de cor;
- reduzir risco de quebra ruim em mensagens, assinaturas e tabelas.

Antes de playtest, revisar pelo menos um PDF consolidado em P&B ou escala de cinza.

## Assinaturas, rubricas e manuscritos P3

A infraestrutura atual usa perfis de personagem no blueprint, SVG inline procedural e override SVG manual. O P3 consolida essa camada em `generator/signature_renderer.py` para:

- preservar SVG inline offline;
- diferenciar assinatura completa, rubrica e manuscrito curto;
- evitar quebra de página no bloco de assinatura;
- manter leitura em P&B;
- gerar traços por caminhos SVG, sem fonte decorativa aplicada a blocos longos.

Não usar fonte externa, imagem gerada por IA ou assinatura textual simples como substituto do perfil editorial. Detalhes de campos, estilos, limites e checklist estão em `docs/SIGNATURES_AND_HANDWRITING.md`.

## Jogador vs. facilitador

- Material do jogador: evidência bruta, cabeçalho/rodapé documental, sem linguagem de solução.
- Guia do facilitador: pode conter interpretação, confirmação, contrato lógico, dicas e gabarito, mas deve ser visualmente confidencial.
- Dicas contextuais: sempre separadas fisicamente dos envelopes dos jogadores.


## P1 — Printables apartados

O P1 adiciona cartões recortáveis de apoio de mesa em `templates/printable_cards.html`, usando o mesmo princípio P&B first do sistema documental v1. Os cartões são gerados como printables separados em `printables/`, registrados no `manifest.json` e no `print_manifest.json`, e não entram automaticamente nos envelopes de investigação.

Classes principais:

- `printable-card-sheet`;
- `printable-card`;
- `printable-card--personagem`;
- `printable-card--local`;
- `printable-card--objeto`;
- `cut-line`;
- `card-code`;
- `card-meta`.

Regras editoriais:

- cartão é referência de mesa, não evidência primária;
- não pode conter culpa, motivação secreta, gabarito ou orientação de cruzamento;
- deve funcionar sem cor, imagem externa, fonte externa, QR code ou internet;
- deve ser impresso separado dos envelopes e recortado quando indicado pelo guia de impressão.

Ver também `docs/PRINTABLES.md`.

## Checklist visual antes de playtest

1. Os documentos parecem artefatos reais, não cards explicativos?
2. O cabeçalho/rodapé informa controle documental sem entregar interpretação?
3. Alguma tabela depende só de cor para sentido?
4. Débitos, créditos, datas, horários e códigos estão alinhados?
5. Carimbos são burocráticos e neutros?
6. Assinaturas/rubricas aparecem como SVG offline e não quebram página?
7. Guia do facilitador está claramente separado do material do jogador?
8. A impressão P&B continua legível?
9. Não há CDN, imagem externa ou fonte binária?
10. Não houve alteração narrativa acidental nos canônicos?

## P2 — plantas baixas profissionais procedurais

Mapas agora seguem o contrato em `docs/FLOORPLANS.md`: A4 landscape, P&B first, fundo branco, paredes fechadas, portas com gap real, janelas paralelas na parede e câmeras presas em parede/canto. O renderer dedicado `generator/floorplan_renderer.py` gera SVG inline sem imagem externa e o template `templates/floorplan.html` preserva uma página paisagem.

A planta baixa não pode virar pista visual interpretativa. Rotas, áreas críticas, câmera offline, campo de visão, suspeitos, solução e instruções de cruzamento pertencem ao facilitador/dicas/gabarito, nunca ao mapa de jogador.

# Sistema visual documental v1

Este documento define a camada visual do Indiciário para que os PDFs deixem de parecer apenas “HTML bonito” e sustentem a sensação de dossiê físico investigativo crível.

## Objetivo

O sistema visual centraliza tokens, classes e padrões mínimos para documentos de jogador, guias operacionais, printables, assinaturas/manuscritos e plantas baixas. A intenção é melhorar a aparência sistêmica sem alterar solução narrativa ou dificuldade dos casos canônicos.

## Princípios

- **Dossiê físico crível:** documentos devem parecer artefatos burocráticos, administrativos, comerciais, financeiros, operacionais ou pessoais plausíveis.
- **Evidência bruta:** documento de jogador mostra fatos do mundo da história; interpretação, dica e gabarito ficam fora.
- **P&B first:** todo sentido visual deve sobreviver em impressão preto e branco.
- **Offline first:** usar apenas CSS, SVG inline e fontes de sistema; sem CDN, imagem externa, fonte binária ou API.
- **Sistêmico antes de pontual:** preferir tokens, renderers e classes reutilizáveis a ajustes específicos de caso.
- **Separação física:** documentos de jogador, material do facilitador, dicas e printables devem continuar distinguíveis no pacote.

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

O sistema visual possui classes reutilizáveis para controle documental, mas documentos diegéticos de jogador não devem exibir metadados técnicos visíveis como envelope, código interno ou “controle de dossiê” quando isso quebrar imersão.

A rastreabilidade deve ficar em:

- `manifest.json`;
- `print_manifest.json`;
- guia do facilitador;
- relatórios internos/debug;
- nomes de arquivos.

Esse bloco nunca deve conter interpretação, dica, gabarito, checklist de cruzamento ou linguagem de facilitador.

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
- **Chat / exportação operacional:** balões discretos e indicação de exportação fora do fluxo das mensagens; evitar aparência colorida demais.
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

## P1 — Printables apartados

O P1 adiciona cartões recortáveis de apoio de mesa em `templates/printable_cards.html`, usando o mesmo princípio P&B first do sistema documental. Os cartões são gerados como printables separados em `printables/`, registrados no `manifest.json` e no `print_manifest.json`, e não entram automaticamente nos envelopes de investigação.

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

## P2 — Plantas baixas estruturadas

Mapas seguem o contrato em `docs/FLOORPLANS.md`: A4 landscape, P&B first, planta como espaço arquitetônico, paredes compartilhadas, portas com gap real, janelas em parede, câmeras em parede/canto e ausência total de rota/solução visual.

Arquitetura atual:

- `generator/floor_plan.py` é a direção atual para mapas canônicos novos e para o Mirante v2.
- `generator/floorplan_renderer.py` permanece como renderer legado/compatibilidade.
- `templates/floorplan.html` preserva uma página paisagem.
- `generator/visual_procedural.py` integra o mapa do Mirante chamando `render_floor_plan_svg(build_mirante_planta())`.

O mapa v2 do Mirante usa:

- ambientes com códigos `A-xx`;
- portas com códigos `P-xx`;
- portão externo `G-xx`;
- câmeras `CAM-xx`;
- posto de controle externo;
- pátio operacional;
- doca/serviço;
- indicador discreto de controle por cartão.

A planta baixa não pode virar pista visual interpretativa. Rotas, áreas críticas, câmera offline, campo de visão, suspeitos, solução e instruções de cruzamento pertencem ao facilitador/dicas/gabarito, nunca ao mapa de jogador.

Regra visual importante:

- o renderer deve comunicar passagem por gap/vão claro; arco realista de giro da porta é opcional e não deve poluir a leitura.
- se a geometria estiver ruim, corrigir o builder da planta; não “colar” salas com conectores artificiais.

## P3 — Assinaturas, rubricas e manuscritos

A infraestrutura atual usa perfis de personagem no blueprint, SVG inline procedural e override SVG manual. O P3 consolida essa camada em `generator/signature_renderer.py` para:

- preservar SVG inline offline;
- diferenciar assinatura completa, rubrica e manuscrito curto;
- evitar quebra de página no bloco de assinatura;
- manter leitura em P&B;
- gerar traços por caminhos SVG, sem fonte decorativa aplicada a blocos longos.

Não usar fonte externa, imagem gerada por IA ou assinatura textual simples como substituto do perfil editorial. Detalhes de campos, estilos, limites e checklist estão em `docs/SIGNATURES_AND_HANDWRITING.md`.

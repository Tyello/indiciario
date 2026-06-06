# Roadmap do Indiciário

Este roadmap registra a direção atual do projeto depois dos playtests reais e dos hardenings editorial, técnico e visual até P2.

## Estado atual

O Indiciário já possui:

- régua canônica Iniciante: `examples/caso_canonico_iniciante.json` — **O Desvio da Reserva Mirante**;
- régua canônica Intermediária: `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora**;
- validator strict com guardrails editoriais, anti-obviedade, progressão, cartões, assinaturas/manuscrito e mapas;
- package builder com manifest, print manifest, guia de impressão, guia do facilitador, dicas, QA e grafo de pistas;
- sistema visual P0;
- printables apartados P1;
- plantas baixas P2;
- assinaturas/rubricas/manuscritos P3.

O projeto está em fase de **validação de baseline real e playtest adicional**, não em fase de plataforma comercial.

## Fase concluída — Fundação técnica e editorial

Status: **concluída**.

Concluído:

- Blueprint JSON funcional.
- Renderização HTML/CSS para PDF.
- Playwright/Chromium como renderizador oficial.
- Merge PDF com `pikepdf`.
- Schemas YAML por template.
- `required_when`.
- Placeholder blocker.
- QA Report.
- Graph Report.
- Contratos de evidência.
- Grafo de pistas.
- LLM feedback.
- Guia do facilitador.
- Dicas contextuais.
- Guia de impressão.
- Package builder.
- Manifest e print manifest.
- Playtest metrics.

Não reabrir esta fase sem evidência concreta.

## Fase concluída — Qualidade editorial e progressão

Status: **concluída como base, com melhorias futuras incrementais**.

Concluído:

- `docs/ANTI_OBVIEDADE.md`.
- `generator/obviousness_checker.py`.
- Integração `OBV_*` ao validator.
- `conflito_central`, `objetivos_por_envelope` e `guia_operacional` como campos do blueprint.
- Validações de progressão `PROG_*`.
- Diretriz de diegese documental em `docs/DIEGESE_DOCUMENTAL.md`.

Objetivo alcançado:

> impedir que a LLM gere documentos bonitos antes de existir uma investigação jogável.

## Fase concluída — Sistema visual base P0

Status: **concluída**.

Entregou:

- `templates/styles/document_system.css`;
- tokens CSS globais;
- classes por tipo e família documental;
- cabeçalho/rodapé documental;
- tabelas P&B first;
- carimbos burocráticos;
- separação visual entre jogador e facilitador.

## Fase concluída — Printables apartados P1

Status: **concluída**.

Entregou:

- `PrintableCard` no modelo;
- `generator/printable_cards.py`;
- `templates/printable_cards.html`;
- PDFs em `printables/`;
- manifest/print manifest com `printable_support`;
- validações `CARD_*`;
- `docs/PRINTABLES.md`.

Regra consolidada:

> cartão é apoio de mesa, não evidência primária.

## Fase concluída — Plantas baixas P2

Status: **concluída**.

Entregou:

- `generator/floorplan_renderer.py`;
- `templates/floorplan.html`;
- campos estruturais de mapa: portas, janelas, câmeras, categoria e inclusão por envelope;
- validações `MAP_*`;
- documentação `docs/FLOORPLANS.md`.

Contrato visual:

- A4 paisagem;
- P&B first;
- paredes fechadas;
- portas com gap real;
- portas entre áreas adjacentes abrem gap na parede compartilhada quando há coincidência real;
- janelas em paredes;
- câmeras em parede/canto;
- sem rota, solução, área crítica, câmera offline, campo de visão ou linguagem interpretativa.

Hotel Aurora permanece sem mapa por decisão de playtest.

## Fase concluída — Assinaturas, rubricas e manuscritos P3

Status: **concluída**.

Entregou:

- `generator/signature_renderer.py`;
- perfis visuais por personagem;
- SVG procedural offline;
- assinatura e rubrica distintas;
- manuscrito curto procedural;
- overrides SVG compatíveis com aliases antigos e novos;
- validações `SIG_*` e `HAND_*`;
- `docs/SIGNATURES_AND_HANDWRITING.md`.

Regra consolidada:

> assinatura, rubrica e manuscrito são características editoriais do personagem, não decoração genérica.

## Próxima fase — Baseline real pós-P0/P1/P2/P3

Status: **próximo passo recomendado**.

Objetivo:

Gerar os pacotes reais dos dois canônicos com Playwright/Chromium e revisar visualmente página por página.

Comandos:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Revisar:

- capa geral;
- capas de envelope;
- documentos do jogador;
- guia do facilitador;
- dicas contextuais;
- guia de impressão;
- cartões apartados;
- assinaturas/rubricas;
- manuscritos curtos;
- mapa do Iniciante;
- P&B/escala de cinza.

Critério de conclusão:

- os dois pacotes geram sem erro real de Playwright;
- não há resíduos técnicos;
- não há quebra visual grave;
- o mapa do Iniciante parece planta operacional, não pista visual;
- Hotel Aurora continua sem mapa;
- material de jogador, facilitador, dicas e printables estão fisicamente separados.

## Próxima fase — Ajustes finos pós-baseline

Status: **pendente, dependente da revisão visual real**.

Só corrigir problemas comprovados, como:

- overflow de tabela;
- assinatura mal posicionada;
- manuscrito ilegível;
- cartão cortando texto;
- mapa com porta/janela/câmera mal posicionada;
- guia de impressão ambíguo;
- separação de arquivos incorreta.

Não usar esta fase para reabrir narrativa dos canônicos sem evidência de playtest.

## Próxima fase — Novo playtest do Intermediário

Status: **pendente**.

Objetivo:

Testar o Hotel Aurora com pessoas novas, usando o pacote pós-P0/P1/P2/P3.

Avaliar:

- clareza da pergunta pública;
- quando o grupo entende que pode abrir E2;
- se E2 recontextualiza sem explicar demais;
- uso real dos cartões apartados;
- necessidade real de dicas;
- clareza do guia do facilitador;
- tempo real de jogo;
- participação de jogadores mais jovens;
- sensação de diversão, intriga e justiça.

Critério de conclusão:

- grupo entende o objetivo de E1;
- E2 muda a leitura sem parecer gabarito;
- facilitador consegue conduzir sem improvisar solução;
- dicas destravam sem substituir investigação;
- documentos continuam interessantes.

## Próxima fase — Canônico Avançado

Status: **não iniciar antes do baseline real e novo playtest do Intermediário**.

Objetivo futuro:

Criar `examples/caso_canonico_avancado.json` como terceira régua editorial.

Direção esperada:

- mais ambiguidade;
- mais cruzamento temporal;
- mais falsos caminhos plausíveis;
- solução justa, mas menos direta;
- 2 ou 3 envelopes, conforme a história pedir;
- mecânica investigativa diferente de Mirante e Hotel Aurora;
- sem aumento artificial de dificuldade por excesso de documentos.

Critério para iniciar:

- baseline visual dos dois canônicos revisado;
- novo playtest do Intermediário registrado;
- principais problemas de layout/pacote resolvidos;
- plano Markdown do Avançado aprovado antes de gerar JSON.

## Fase futura — Biblioteca canônica completa

Status: **futuro**.

Depois do Avançado, avaliar:

- `caso_canonico_especialista.json`;
- `caso_canonico_mestre.json`.

Cada canônico deve testar uma mecânica investigativa diferente, não apenas uma dificuldade maior.

## Fase futura — Inteligência editorial

Status: **futuro, após vários casos e playtests**.

Ideias:

- benchmark report;
- comparador de casos;
- calibragem automática de dificuldade;
- análise de progressão;
- análise de red herrings;
- detecção de documento que resolve demais;
- sugestões de dicas baseadas em travamentos reais.

## Não priorizar agora

Não priorizar neste momento:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- agentes autônomos;
- IA gerando imagens;
- automação de venda.

Essas frentes só fazem sentido depois de provar que o framework gera mistérios consistentemente bons, jogáveis e desejáveis.
# Visual Library 2.0 — base mínima

A Visual Library 2.0 é a camada de assets visuais estruturados do Indiciário. Ela não existe para decorar casos: existe para fornecer bases visuais críveis, reutilizáveis e auditáveis que possam sustentar investigações futuras sem depender de imagem externa, internet ou geração por IA.

## Princípios

Todo asset visual da biblioteca deve ser:

- **offline first**;
- **P&B first**;
- imprimível;
- procedural por SVG/CSS;
- compatível com PDF via Playwright/Chromium;
- sem QR code;
- sem imagem externa;
- sem fonte externa;
- sem dependência de IA;
- neutro o bastante para não entregar rota, solução, culpa ou área crítica.

## Escopo inicial

A base mínima começa com plantas baixas estruturadas em `generator/floor_plan_library.py`.

O módulo reaproveita as dataclasses e o renderer de `generator/floor_plan.py`, em vez de criar um segundo modelo de planta. Isso mantém a mesma filosofia que estabilizou a planta v2 do Mirante:

- ambientes retangulares estruturados;
- paredes derivadas por adjacência;
- portas com vão/gap real;
- janelas em paredes;
- câmeras presas a parede ou canto;
- SVG inline procedural;
- leitura operacional neutra.

Builders disponíveis:

- `build_hotel_planta_base()` — térreo operacional genérico de hotel, com quartos simples conectados ao corredor e sem vínculo com o Hotel Aurora canônico;
- `build_escritorio_planta_base()` — escritório administrativo genérico para casos futuros.

## Não integração automática

A Visual Library 2.0 não altera canônicos por padrão.

Em especial:

- **O Desvio da Reserva Mirante** continua usando sua planta estruturada v2 própria;
- **O Último Brinde do Hotel Aurora** continua sem mapa, conforme decisão validada de playtest;
- nenhuma planta-base deve ser injetada automaticamente em caso existente.

Para usar um asset da biblioteca em um caso futuro, a necessidade investigativa precisa estar clara no desenho do caso. Mapa não é brinde visual nem decoração de pacote.

## Contrato editorial

Uma planta-base da biblioteca pode mostrar:

- ambientes;
- circulação;
- portas;
- janelas;
- controles de acesso discretos;
- câmeras neutras;
- áreas externas operacionais quando fizer sentido.

Uma planta-base da biblioteca não deve mostrar:

- rota usada;
- solução;
- área crítica destacada;
- câmera offline;
- campo de visão;
- suspeito;
- legenda investigativa;
- linguagem de gabarito.

## Critério para novos assets

Antes de adicionar novo builder visual, verifique se ele é realmente uma base reutilizável e se passa pelos mesmos critérios de planta baixa estruturada documentados em `docs/FLOORPLANS.md`.

A biblioteca deve crescer em PRs pequenas: um tipo de asset por vez, com teste próprio e sem reabrir canônicos sem evidência nova de PDF, teste ou playtest.

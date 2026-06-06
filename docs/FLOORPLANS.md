# P2 visual — plantas baixas procedurais

Este documento define o padrão P2 para mapas do Indiciário. Um mapa de jogador é uma planta baixa neutra ou operacional simplificada: ajuda o grupo a entender espaço, circulação e nomenclatura, mas não funciona como pista comentada nem como gabarito visual.

## Objetivo

- Produzir material arquitetônico/operacional crível para mesa, notebook, tablet ou impressão.
- Manter o produto **offline first**, sem imagem externa, QR code, link ou aplicativo.
- Evitar vazamento de solução, rota, suspeito, sequência de movimento ou interpretação visual.

## Planta baixa x pista visual

A planta baixa mostra evidência espacial bruta: ambientes, paredes, portas, janelas, câmeras neutras e códigos técnicos. A interpretação pertence ao guia do facilitador, dicas contextuais, gabarito ou discussão dos jogadores.

Nunca use a planta para dizer o que comparar, quem é suspeito, qual rota ocorreu, qual câmera falhou ou por que uma área importa.

## Contrato visual obrigatório

- A4 **landscape** sempre.
- P&B first: fundo branco, linhas pretas/cinzas e sem paleta narrativa.
- Paredes externas mais fortes; divisórias internas mais leves.
- Portas com gap real na parede e símbolo técnico discreto.
- Janelas com linhas paralelas na parede.
- Câmeras presas em parede/canto, sem campo de visão desenhado.
- Norte/escala apenas quando discretos e com aparência técnica.
- Se houver legenda, prefira códigos no mapa; se houver nomes diretamente nas áreas, não duplique tudo na legenda.

## Modelagem mínima

Mapas vivem em `visual_procedural.mapas` e continuam opcionais. O contrato P2 aceita os campos legados (`areas`, `conexoes`, `marcadores`, `legenda`) e acrescenta elementos estruturais explícitos:

- `orientacao`: deve ser `landscape`.
- `areas`: `id`, `nome`, `x`, `y`, `w`, `h`, `tipo`, `observacao` opcional.
- `portas`: `id`, `area_a`, `area_b` ou `exterior`, `parede`, `posicao`, `largura`, `controle_acesso` opcional.
- `janelas`: `id`, `area`, `parede`, `posicao`, `largura`.
- `cameras`: `id`, `area`, `parede`, `posicao`, `orientacao` opcional.
- `categoria`: `documento_jogador`, `apoio_visual` ou `facilitador`.
- `incluir_no_envelope`: controla se o mapa entra no envelope indicado por `fase` ou como apoio apartado.

## Proibido em mapas de jogador

Termos e recursos bloqueados pelo contrato P2:

- rota;
- provável;
- suspeito;
- culpado;
- área crítica;
- caminho;
- offline;
- bloqueio visual;
- ponto cego;
- usar para cruzar;
- compare com;
- solução;
- gabarito.

Também são proibidos setas de rota, destaque de área crítica, cores de solução, campo de visão de câmera e qualquer texto interpretativo.

## Validação MAP_*

O validator aplica guardrails estruturais simples:

- `MAP_001`: orientação diferente de landscape.
- `MAP_002`: porta referencia área inexistente.
- `MAP_003`: janela referencia área inexistente.
- `MAP_004`: câmera referencia área inexistente.
- `MAP_005`: porta fora dos limites da parede.
- `MAP_006`: janela fora dos limites da parede.
- `MAP_007`: câmera sem parede/posição ou fora da parede.
- `MAP_008`: linguagem interpretativa proibida.
- `MAP_009`: legenda redundante com nomes completos já duplicados nas áreas.
- `MAP_010`: destaque de rota/área crítica/solução.

A validação não substitui revisão visual, mas bloqueia erros grosseiros como portas flutuantes, janelas sem área e câmera solta.

## Quando incluir mapa

Inclua mapa quando a compreensão do espaço for parte da investigação ou da logística de mesa. Não inclua mapa apenas para decorar o pacote. Hotel Aurora permanece sem mapa enquanto a decisão de playtest for manter o caso sem planta.

## Checklist antes de playtest

1. O PDF está em A4 paisagem?
2. A planta é legível em P&B?
3. Todas as portas estão sobre paredes e com gap?
4. Janelas estão sobre paredes externas/coerentes?
5. Câmeras estão presas em parede/canto?
6. Não há rota, área crítica, campo de visão ou cor de solução?
7. A legenda não duplica nomes quando os nomes já estão nas salas?
8. O manifest/print manifest indica impressão em paisagem e separa envelope, apoio visual e facilitador?

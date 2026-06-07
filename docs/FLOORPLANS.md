# P2 visual — plantas baixas estruturadas

Este documento define o padrão P2 para mapas do Indiciário. Um mapa de jogador é uma planta baixa neutra ou operacional simplificada: ajuda o grupo a entender espaço, circulação e nomenclatura, mas não funciona como pista comentada nem como gabarito visual.

## Objetivo

- Produzir material arquitetônico/operacional crível para mesa, notebook, tablet ou impressão.
- Manter o produto **offline first**, sem imagem externa, QR code, link ou aplicativo.
- Evitar vazamento de solução, rota, suspeito, sequência de movimento ou interpretação visual.
- Priorizar plantas modeladas como espaço arquitetônico, não diagramas de caixas soltas.

## Arquitetura atual

O Indiciário possui duas camadas de mapa:

1. **Planta estruturada v2** em `generator/floor_plan.py`.
   - É a direção atual para mapas canônicos e novos mapas.
   - Modela a planta como dados: áreas, portas, janelas, câmeras e portões.
   - Renderiza SVG inline P&B a partir da geometria.
   - Detecta paredes compartilhadas e corta gaps de portas/janelas.
   - Hoje é usada pelo canônico Iniciante **O Desvio da Reserva Mirante**.

2. **Renderer legado** em `generator/floorplan_renderer.py`.
   - Mantido para compatibilidade com mapas antigos declarados em `visual_procedural.mapas`.
   - Não deve ser a primeira escolha para novos mapas canônicos.

Integração atual:

- `generator/visual_procedural.py` direciona o mapa `casa_acervo_mirante_andar_1` para `render_floor_plan_svg(build_mirante_planta())`.
- `templates/floorplan.html` continua sendo a embalagem HTML/PDF em A4 paisagem.
- Hotel Aurora permanece sem mapa por decisão de playtest.

## Planta baixa x pista visual

A planta baixa mostra evidência espacial bruta: ambientes, paredes, portas, janelas, câmeras neutras, portões e códigos técnicos. A interpretação pertence ao guia do facilitador, dicas contextuais, gabarito ou discussão dos jogadores.

Nunca use a planta para dizer o que comparar, quem é suspeito, qual rota ocorreu, qual câmera falhou ou por que uma área importa.

## Contrato visual obrigatório

- A4 **landscape** sempre.
- P&B first: fundo branco, linhas pretas/cinzas e sem paleta narrativa.
- Paredes externas mais fortes; divisórias internas mais leves.
- Planta deve parecer espaço arquitetônico coerente, com circulação plausível.
- Áreas adjacentes devem compartilhar parede quando forem fisicamente vizinhas.
- Portas devem abrir gap real na parede e usar símbolo técnico discreto.
- Portas controladas por cartão podem usar indicador visual mínimo de acesso.
- Portões podem aparecer como símbolo operacional de acesso externo/serviço.
- Janelas usam marcação técnica em parede.
- Câmeras ficam presas em parede/canto, sem campo de visão desenhado.
- Norte/escala apenas quando discretos e com aparência técnica.
- Se houver legenda, prefira códigos no mapa; se houver nomes diretamente nas áreas, não duplique tudo na legenda.

## Modelagem v2 recomendada

Para novos mapas canônicos, usar `generator/floor_plan.py`. Para bases reutilizáveis de casos futuros, consultar `generator/floor_plan_library.py` e `docs/VISUAL_LIBRARY_2_0.md` sem integração automática aos canônicos.

Modelo atual:

- `PlantaBaixa`: id, título, largura, altura, áreas, portas, janelas, câmeras e portões.
- `AreaPlanta`: ambiente ou área operacional com `id`, `nome`, coordenadas, dimensões, `tipo` e `codigo`.
- `PortaPlanta`: passagem entre duas áreas ou exterior, orientação, posição, largura e `controle_acesso` opcional.
- `JanelaPlanta`: abertura vinculada a uma área e orientação.
- `CameraPlanta`: câmera neutra vinculada a uma área e posicionada em parede/canto.
- `PortaoPlanta`: acesso externo/operacional, usado para portões de pátio, serviço ou doca.

Convenções atuais:

- Ambientes usam códigos `A-xx`.
- Portas usam códigos `P-xx`.
- Portões usam códigos `G-xx`.
- Câmeras usam códigos `CAM-xx`.
- Janelas usam códigos `J-xx`.

A geometria deve nascer coerente no builder da planta. O renderer não deve “consertar” salas desconexas com conectores artificiais.

## Campos legados

Mapas em `visual_procedural.mapas` continuam opcionais e podem usar os campos legados:

- `orientacao`: deve ser `landscape`.
- `areas`: `id`, `nome`, `x`, `y`, `w`, `h`, `tipo`, `observacao` opcional.
- `portas`: `id`, `area_a`, `area_b` ou `exterior`, `parede`, `posicao`, `largura`, `controle_acesso` opcional.
- `janelas`: `id`, `area`, `parede`, `posicao`, `largura`.
- `cameras`: `id`, `area`, `parede`, `posicao`, `orientacao` opcional.
- `categoria`: `documento_jogador`, `apoio_visual` ou `facilitador`.
- `incluir_no_envelope`: controla se o mapa entra no envelope indicado por `fase` ou como apoio apartado.

Para novos mapas, prefira criar builders estruturados em `floor_plan.py` ou módulo equivalente, em vez de expandir o modelo legado.

## Mirante v2

O mapa canônico do Iniciante usa `build_mirante_planta()`.

Características consolidadas:

- planta estruturada como espaço de acervo/galeria, não diagrama;
- corredor técnico contínuo;
- recepção/controle, galeria, reservas técnicas, administração, monitoramento, apoio, doca e pátio operacional;
- posto de controle externo reduzido, associado ao acesso operacional;
- portão externo `G-01` para acesso de serviço/doca;
- portas simplificadas com vão e ombreiras, sem arco de giro chamativo;
- indicador discreto de cartão em portas com `controle_acesso=True`;
- footprint/hachura derivado da geometria das áreas, sem retângulo hardcoded.

O Mirante deve continuar sendo referência de mapa de jogador: operacional, legível e neutro.

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

## Validação MAP_* e validação v2

O validator aplica guardrails estruturais simples para mapas declarados no blueprint:

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

A planta v2 também possui validação própria em `validar_planta()`, cobrindo referências de áreas, posição plausível de portas/janelas/câmeras, adjacência e ausência de elementos soltos.

A validação não substitui revisão visual, mas bloqueia erros grosseiros como portas flutuantes, janelas sem área, câmera solta e linguagem de solução no mapa.

## Regras de porta e acesso

Porta é elemento geométrico e operacional, não decoração.

Regras:

1. A porta precisa estar sobre uma parede existente.
2. A posição precisa caber dentro dos limites da parede.
3. Se conectar duas áreas internas, elas devem ser adjacentes.
4. Quando houver adjacência real, o renderer deve abrir gap visual na parede compartilhada.
5. Porta para exterior pode abrir apenas a parede da área interna.
6. Portas com cartão devem usar indicador discreto, não explicação textual longa.
7. O símbolo da porta deve priorizar clareza do vão; arco de abertura realista é opcional e não deve poluir a leitura.

Se uma porta aparece em uma área sem parede ou sem abertura visual, o mapa deve ser tratado como falho para playtest.

## Regras de área externa e portão

Quando houver doca, serviço, garagem, carga/descarga ou saída operacional, a planta deve representar a lógica externa mínima:

- pátio ou área externa operacional;
- portão ou acesso controlado quando fizer sentido;
- posto de controle/guarita como elemento pequeno e plausível, não sala grande equivalente aos ambientes internos;
- espaço visual suficiente para parada de veículo quando a história envolver doca, retirada ou entrega.

A área externa deve orientar o espaço, mas não revelar rota, método ou solução.

## Quando incluir mapa

Inclua mapa quando a compreensão do espaço for parte da investigação ou da logística de mesa. Não inclua mapa apenas para decorar o pacote.

Hotel Aurora permanece sem mapa enquanto a decisão de playtest for manter o caso sem planta.

## Checklist antes de playtest

1. O PDF está em A4 paisagem?
2. A planta é legível em P&B?
3. O mapa parece planta operacional, não diagrama de caixas?
4. Todas as portas estão sobre paredes e com gap?
5. Portas entre áreas adjacentes abrem a parede compartilhada?
6. Portas com cartão têm indicador discreto e compreensível?
7. Janelas estão sobre paredes externas/coerentes?
8. Câmeras estão presas em parede/canto?
9. Portões/áreas externas estão claros quando houver doca ou serviço?
10. Não há rota, área crítica, campo de visão ou cor de solução?
11. A legenda não duplica nomes quando os nomes já estão nas salas?
12. O manifest/print manifest indica impressão em paisagem e separa envelope, apoio visual e facilitador?
13. O mapa ajuda orientação espacial sem responder a investigação?

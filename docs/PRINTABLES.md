# Printables apartados — cartões de mesa

Printables apartados são materiais de apoio físico que acompanham o dossiê, mas **não entram automaticamente nos envelopes de investigação**. Eles existem para organizar a mesa, ajudar o grupo a lembrar nomes, locais e objetos, e facilitar a condução do playtest sem transformar referência visual em pista.

## Diferença editorial

| Tipo | Função | Entrega |
|---|---|---|
| Documento de investigação | Evidência primária diegética, com fatos do mundo da história. | Dentro dos envelopes dos jogadores. |
| Cartão apartado | Referência pública de mesa para pessoa, local ou objeto. | Separado dos envelopes, recortável. |
| Dica contextual | Destravamento controlado pelo facilitador. | Nunca misturada aos envelopes. |
| Guia/gabarito | Interpretação, solução e condução. | Confidencial do facilitador. |

Cartões **não substituem evidências** e **não devem ser usados como prova**. Se o grupo precisa confirmar algo, essa confirmação deve continuar nos documentos do caso.

## Tipos de cartão

O P1 visual suporta três tipos:

- `personagem`: nomes, funções públicas e referência social de mesa;
- `local`: ambientes relevantes para orientação sem mapa de solução;
- `objeto`: itens centrais ou recorrentes, sem revelar cadeia de prova.

Cada cartão pode trazer:

- código visual ou ID;
- título;
- subtítulo;
- descrição curta;
- marcador de categoria;
- tags visuais neutras;
- envelope sugerido para entrega;
- observação pública, quando necessária.

## O que não pode aparecer

Cartões ficam no lado dos jogadores. Portanto, não podem conter:

- solução, gabarito, confissão ou confirmação investigativa;
- culpa, motivação secreta, executor, planejador ou beneficiário;
- orientação explícita de cruzamento, como “compare com” ou “cruze com”;
- contratos de evidência, IDs internos ou códigos como `C-E1-*`, `C-E2-*`, `C-FINAL-*`;
- referência a documentos como se fossem checklist de solução.

## Quando entregar

Padrão recomendado:

1. Imprimir os cartões em A4, preferencialmente 180g.
2. Recortar nas linhas discretas de corte.
3. Entregar como bloco apartado no início da sessão ou junto do primeiro envelope.
4. Reforçar verbalmente que são referência de mesa, não prova.

Em casos com progressão mais sensível, o facilitador pode segurar cartões de local/objeto até o envelope recomendado, desde que isso não vire mecanismo secreto obrigatório.

## Impressão P&B e recorte

O template `templates/printable_cards.html` é P&B first:

- bordas, pesos e padrões substituem dependência de cor;
- ícones são SVG inline simples;
- não há fonte externa, imagem externa, QR code ou dependência online;
- cada folha A4 contém cartões em grade de duas colunas, com linhas de corte discretas.

## Checklist antes do playtest

- [ ] Os cartões estão em `printables/` no pacote final.
- [ ] O `manifest.json` e o `print_manifest.json` indicam recorte e apoio de mesa.
- [ ] O guia de impressão separa envelopes, facilitador, dicas e printables.
- [ ] Nenhum cartão entrega solução ou orienta cruzamento.
- [ ] Os canônicos passam no validator strict.
- [ ] Um build fake ou real foi executado para confirmar os PDFs de cartões.

## Limites deixados para P2

- Variações avançadas de layout por dificuldade.
- Seleção automática de cartões a partir de playtest/blueprint.
- Cartões com verso, dobra ou componentes modulares.
- Refinamento de ícones procedurais por família de caso.

## Folhas de apoio preenchíveis

Folha de apoio é ferramenta neutra de mesa, não gabarito. Ela pode organizar horários, nomes, salas ou hipóteses de trabalho, mas não deve instruir a solução nem conter campos que exponham metadados técnicos.

Regras práticas:

- Deve haver espaço real para anotação manual ou digital.
- Tabelas de apoio/preenchimento devem oferecer pelo menos 4 linhas em branco reais.
- Evitar 5+ colunas em A4; quando inevitável, justificar visualmente e validar em PDF real.
- Usar campos neutros e diegéticos, como “Horário”, “Fonte”, “Documento” e “Anotação do grupo”.
- Não usar campos artificiais como “persona”, “Registro interno/persona”, `TODO`, placeholder ou qualquer rótulo técnico de autoria.
- Não pode virar gabarito, checklist de cruzamento ou instrução como “compare este documento”.

Antes do playtest, rode o sanity check visual no blueprint e, se houver PDF renderizado, também no PDF da folha de apoio.

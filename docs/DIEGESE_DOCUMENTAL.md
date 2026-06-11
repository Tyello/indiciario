# Diegese documental no Indiciário

Este documento registra regras editoriais para garantir que documentos de jogador pareçam existir naturalmente no mundo da história.

Ele complementa:

- `docs/DIRETRIZES_EDITORIAIS.md`
- `docs/CASE_DESIGN_PIPELINE.md`
- `docs/BLUEPRINT_AUTHORING_GUIDE.md`
- `docs/LLM_OPERATING_MANUAL.md`

## Regra central

Uma boa pista no documento errado vira pista artificial.

Antes de adicionar uma informação a um documento, pergunte:

1. Quem teria criado esse documento dentro da história?
2. Essa pessoa teria motivo real para registrar essa informação?
3. Essa informação estaria nesse tipo documental?
4. O texto parece evidência bruta ou parece comentário do autor?
5. A pista ficaria mais natural se viesse de outra pessoa, registro ou remessa?

Se a resposta principal for “isso ajuda o jogador a resolver”, a informação provavelmente está no lugar errado.

## Alocação correta de pistas

Pistas devem aparecer no documento que naturalmente as carregaria.

Exemplos:

| Informação | Documento ruim | Documento melhor |
|---|---|---|
| Alguém pediu para evitar o terraço por causa do vento | menu assinado pela própria pessoa suspeita | declaração de terceiro, relatório de circulação ou consolidação posterior |
| Existência de moradores atuais em uma ala antiga | lista de convidados do jantar | ficha administrativa, controle de ocupação, relatório de governança |
| Promessa antiga de família | documento misturado com atualização moderna | carta original limpa, separada de ficha atual |
| Mensagem operacional de bastidores | WhatsApp da vítima sem justificativa | exportação de grupo operacional fornecida por gerência/recepção |
| Rascunho de discurso | e-mail explicativo demais | versão impressa, anotada ou recolhida no evento |
| Sinal visto de relance | anotação perfeitamente legível no programa | depoimento parcial, folha dobrada, palavras soltas percebidas rapidamente |

## Regra de separação temporal

Não misture camadas temporais em um único documento quando isso parecer artificial.

Exemplo ruim:

```text
Carta de 1968 com anexo administrativo de 2026 no mesmo corpo.
```

Melhor:

- documento antigo: carta original, limpa e emocional;
- documento atual: ficha administrativa, lista, controle de ocupação, relatório, e-mail ou registro contemporâneo.

A carta dá origem emocional.

O documento atual dá consequência concreta.

## Promessa antiga e consequência atual

Quando a motivação depende de algo antigo, use pelo menos dois níveis documentais:

1. **Origem histórica:** carta, ata antiga, fotografia, termo familiar, memorial, diário, promessa.
2. **Pressão atual:** moradia, ocupação, herança, demissão, expulsão, risco público, contrato, lista omitida, regularização pendente.

A origem histórica sozinha raramente sustenta ação presente.

A consequência atual transforma lore em urgência investigativa.


## Motivo inferível no documento certo

A pista de motivo deve existir em um documento que naturalmente conteria aquela informação. O objetivo é permitir inferência humana sem transformar documento de jogador em confissão, comentário de autor ou gabarito disfarçado.

Boas âncoras de motivo são contextos observáveis: vínculo, preferência, perda concreta, benefício, ameaça, consequência atual, pedido administrativo, participação regular ou responsabilidade institucional. Elas não precisam dizer “este é o motivo”; precisam permitir que o grupo entenda por que a ação faria sentido para aquela pessoa.

Evite criar um e-mail, depoimento ou bilhete cuja única função seja explicar intenção. Se a informação existe apenas porque o jogador precisa dela, realoque para um documento mais natural ou divida em origem histórica e pressão atual. A fonte normativa para completude da solução e motivo inferível é `docs/DIRETRIZES_EDITORIAIS.md`.

## Recados, bilhetes e materiais vistos de relance

Recado ou bilhete não deve virar letreiro da solução.

Evitar:

```text
Helena recebeu um bilhete misterioso escrito “vá à sala de memória ver a pasta Aurora”.
```

Preferir:

```text
A testemunha viu Helena mexendo em uma folha dobrada, menor que o cardápio. De relance, leu apenas “brinde” e “Aurora”. Não sabe se era discurso, lembrete, anexo ou página de apoio.
```

Diretrizes:

- leitura parcial é mais natural que frase perfeita;
- percepção indireta é melhor que certeza absoluta cedo demais;
- palavras soltas podem orientar sem entregar;
- o documento completo pode aparecer depois, em outro envelope, como recontextualização.

## Red herring bom não é autoincriminação

Um falso suspeito pode gerar distração forte, mas não deve parecer que escreveu a própria pista.

Exemplo ruim:

```text
Renato Viana solicitou formalmente que ninguém levasse bandejas ao terraço entre 21h15 e 21h32.
```

Isso é uma boa distração, mas no documento errado pode soar fabricado.

Melhor:

```text
Caio ouviu Renato pedir à copa que evitasse bandejas no terraço por causa do vento; na hora pareceu cuidado normal de serviço.
```

Ou:

```text
Copa registrou orientação verbal para concentrar serviço no salão durante a sobremesa, evitando circulação de bandejas no terraço por causa do vento.
```

A informação continua útil, mas surge de forma natural.

## Chats e mensagens operacionais

Todo chat precisa ter origem clara.

Antes de incluir uma conversa, defina:

- de qual aparelho, grupo ou sistema ela saiu;
- quem forneceu a exportação;
- por que esse material está no dossiê;
- quem tinha acesso à conversa;
- se a vítima participava ou não.

Evitar:

```text
Conversa do WhatsApp da vítima sem explicar como foi obtida.
```

Preferir:

```text
Exportação do grupo operacional do evento, fornecida pela gerência/recepção.
```

Também evitar duplicar horários:

- se o template já tem campo `HORARIO`, o texto da mensagem não precisa começar com `21h08 —`.

## Documento social não deve carregar ficha administrativa

Documento de mesa, lista de convidados ou programa social deve falar de evento, posições, protocolo e percepção social.

Não deve carregar informações administrativas densas que existem para explicar motivo.

Exemplo ruim:

```text
Lista de lugares marcada com nota de cadastro sobre ocupantes atuais da ala antiga.
```

Melhor:

- lista de lugares: quem sentou onde, quem viu o quê, cadeira mantida, objeto citado;
- ficha administrativa: ocupação atual, lista retida, pendência de gerência;
- carta antiga: promessa original;
- rascunho de brinde: versão pública planejada.

## Rascunhos, discursos e e-mails

Nem todo motivo deve vir por e-mail.

E-mail tende a explicar demais quando usado para carregar intenção, cópia, motivo e omissão ao mesmo tempo.

Use e-mail quando:

- a troca institucional é natural;
- destinatário, cópia e motivo fazem sentido;
- a mensagem traz informação nova para quem recebe;
- não parece escrita para explicar a solução.

Use rascunho de discurso quando:

- o que importa é a versão pública planejada;
- a pista está na linguagem escolhida;
- a omissão aparece por contraste com outro documento;
- o documento foi impresso, anotado ou recolhido no evento.

## Checklist de revisão diegética

Antes de aprovar um documento de jogador, revise:

1. Este documento existiria naturalmente?
2. Quem o criou teria motivo para registrar isso?
3. A informação está no tipo documental correto?
4. Existe separação entre documento antigo e documento atual?
5. O documento social está livre de notas administrativas explicativas?
6. Red herrings surgem de terceiros/registros naturais, não de autoincriminação artificial?
7. Chats indicam origem e justificativa de exportação?
8. Horários não estão duplicados em mensagens?
9. Recados são parciais o bastante para não virar seta gigante?
10. A pista de motivo aparece em documento que naturalmente conteria aquela informação?
11. A interpretação ficou fora do documento do jogador?

## Aplicação ao Hotel Aurora

No caso canônico Intermediário, a revisão pós-playtest consolidou estas decisões:

- tratar o caso como ausência crítica antes do brinde, não desaparecimento definitivo;
- preservar a distração do vento/terraço de Renato, mas fora da sequência formal assinada por ele;
- trocar anotação de margem por folha dobrada vista de relance;
- substituir e-mail explicativo por rascunho impresso do brinde;
- separar carta original de 1968 da ficha administrativa atual da ala Aurora;
- justificar conversa de bastidores como exportação de grupo operacional;
- remover nota administrativa da lista social de lugares.

Essas decisões devem guiar próximos casos sempre que houver risco de documento parecer pista fabricada.


## Nota visual P0

A aparência documental deve reforçar a diegese sem explicar a investigação. Cabeçalhos, rodapés, carimbos, tabelas e marcas de cópia podem indicar origem burocrática, controle interno ou exportação operacional, mas não podem orientar cruzamentos, confirmar suspeitos ou funcionar como dica visual de solução. Use `docs/VISUAL_SYSTEM.md` como checklist visual antes de gerar material de playtest.


## Manuscrito curto

Anotação manuscrita em documento de jogador é evidência bruta: uma intervenção breve do mundo da história. Use apenas para frases curtas, palavras soltas ou ressalvas marginais associadas a personagem. Não use manuscrito para orientar comparação, confirmar solução, expor gabarito ou transformar um documento em dica.

## Plantas baixas como documento diegético

Plantas baixas são documentos operacionais simplificados. Elas podem mostrar ambientes, códigos de portas, janelas e câmeras neutras, mas não devem explicar investigação, sequência de movimento, falha de vigilância ou importância de uma área. Quando uma interpretação espacial for necessária, registre no guia do facilitador, não no PDF de jogador.

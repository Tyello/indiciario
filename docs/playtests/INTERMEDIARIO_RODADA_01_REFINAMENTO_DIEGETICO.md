# Refinamento diegético — Canônico Intermediário — Rodada 01

Caso: **O Último Brinde do Hotel Aurora**

Arquivo do caso: `examples/caso_canonico_intermediario.json`

Referência de playtest: `docs/playtests/INTERMEDIARIO_RODADA_01.md`

## Status final consolidado

Status: **validado como régua canônica Intermediária**.

Após este refinamento, o Hotel Aurora passa a ser o baseline canônico Intermediário do Indiciário. O objetivo agora é preservar esta versão como régua de comparação, não abrir novo ciclo de alterações narrativas sem evidência nova de playtest, PDF ou validação.

Baseline de geração do pacote:

```bash
py -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

## Contexto

Após o playtest do Intermediário e uma nova geração visual do pacote, o caso mostrou boa aceitação de plot e documentos, mas ainda tinha documentos que pareciam escritos para orientar o jogador, não documentos que existiriam naturalmente no hotel.

O objetivo desta rodada de refinamento foi melhorar diegese sem mudar a solução central.

## Problema principal identificado

O caso já tinha estrutura correta:

- pergunta pública mais clara;
- eixo de ausência crítica antes do brinde;
- dois envelopes;
- sem mapa;
- motivação com consequência atual;
- guia do facilitador mais operacional.

O problema restante era outro:

> Algumas informações corretas estavam no documento errado.

Isso gerava sensação de pista artificial.

## Decisões editoriais consolidadas

### 1. Lista de convidados não deve carregar nota administrativa

`E1-02` deve funcionar como documento social/de mesa.

Deve conter:

- lugares marcados;
- quem estava perto de quem;
- cadeira de Helena mantida;
- percepção social de objetos ou presença.

Não deve conter:

- nota sobre operação reduzida do hotel;
- informação sobre moradores/ocupantes da ala antiga;
- explicação administrativa da motivação.

A informação da ala antiga pertence ao E2, em documento administrativo próprio.

### 2. Distração de Renato continua boa, mas mudou de lugar

A orientação de Renato para evitar bandejas no terraço por causa do vento é uma boa distração.

Ela não deve aparecer como autodeclaração direta na sequência oficial de serviço assinada por Renato, porque parece pista plantada.

Melhor distribuição:

- no menu, o vento pode aparecer como condição operacional do evento;
- na declaração de Caio, pode aparecer como algo ouvido de Renato;
- no relatório de circulação, pode aparecer como orientação verbal da copa;
- no E2, registros podem descartar Renato pela janela da sobremesa.

### 3. Folha dobrada é melhor que anotação na margem

A versão “anotação na margem do programa” ainda soava como recado central.

A versão mais natural:

- Isadora vê Helena mexendo em uma folha dobrada;
- percebe apenas palavras soltas como “brinde” e “Aurora”;
- não sabe se era discurso, lembrete, anexo ou material de apoio;
- isso gera dúvida sem virar seta de solução.

### 4. Rascunho do brinde substitui e-mail explicativo

O e-mail da Helena explicava demais a relação entre Helena, Caio, Marta, pasta Aurora e lista da ala.

A peça mais natural é o rascunho impresso do brinde.

Função do rascunho:

- mostrar a versão pública planejada por Helena;
- sugerir que a ala antiga seria tratada como memória institucional e expansão futura;
- deixar implícito que a promessa não seria cumprida em sentido concreto;
- não explicar a solução por e-mail com cópia para todos.

### 5. Carta original e ficha atual devem ser separadas

A carta de 1968 deve ser apenas carta original.

Ela dá origem emocional à promessa.

A consequência atual deve aparecer em outro documento:

- ficha administrativa;
- controle de ocupação;
- lista retida;
- relatório de governança;
- documento de gerência.

Não misturar carta antiga com anexo moderno no mesmo corpo documental.

### 6. WhatsApp precisa ter origem clara

A conversa de bastidores não deve parecer acesso ao WhatsApp de Helena.

A forma correta:

- exportação do grupo operacional do jantar;
- fornecida por gerência/recepção;
- com membros claros;
- sem duplicar hora no texto se o template já mostra `HORARIO`.

### 7. E1 deve continuar sem solução final

O E1 deve permitir resposta parcial:

> Helena saiu por algo ligado ao brinde/Aurora, e os avistamentos posteriores são indiretos.

O E1 não deve entregar:

- Marta como responsável;
- motivo completo;
- ficha da ala antiga;
- cadeia final da manipulação.

## Direção final do caso após refinamento

A versão mais forte do Hotel Aurora é:

1. Helena sai antes do brinde.
2. Otto quer saber por que isso compromete a reabertura.
3. O E1 mostra que a saída não parece retirada social espontânea.
4. O E2 mostra que a ala antiga tinha consequência atual concreta.
5. A carta original explica a promessa.
6. A ficha administrativa mostra que a lista atual foi retida.
7. O rascunho do brinde mostra que Helena trataria a ala como memória/expansão.
8. Marta age para impedir que a memória viva vire decoração.

## Checklist específico para baseline de pacote

Para manter o baseline Intermediário validado, revisar visualmente em novas gerações:

1. `E1-02` não contém nota administrativa da ala antiga.
2. `E1-03` não faz Renato assinar a própria pista.
3. A distração do vento/terraço aparece como percepção de terceiro ou registro operacional.
4. `E1-08` fala de folha dobrada vista de relance, não de anotação perfeita.
5. `E2-02` é rascunho de brinde, não e-mail explicativo.
6. `E2-04` é carta original limpa.
7. A ficha/lista atual da ala está em documento separado.
8. `E2-08` é exportação de grupo operacional, não conversa da vítima.
9. Chats não duplicam horário no texto.
10. Contratos, linha do tempo e dicas apontam para os documentos corretos depois da redistribuição.

## Impacto consolidado após refinamento

A experiência validada fica mais natural porque:

- o grupo não recebe explicação administrativa cedo demais;
- Renato continua distraindo, mas sem parecer artificial;
- a folha do brinde orienta sem entregar;
- o E2 recontextualiza a promessa com consequência atual;
- a motivação de Marta fica humana e concreta;
- o facilitador tem cadeia mais limpa para conduzir.

## Regra reutilizável

Sempre que uma informação parecer útil demais, revisar não só o texto, mas também o recipiente documental.

A pergunta não é apenas:

> Esta pista está explícita demais?

Também é:

> Esta pista estaria naturalmente neste documento?

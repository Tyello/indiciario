# Playtest — Canônico Intermediário — Rodada 01

Caso: **O Último Brinde do Hotel Aurora**

## Status final após refinamento

Status: **validado como régua canônica Intermediária após playtest, refinamentos editoriais e refinamento diegético**.

Esta rodada deixou de ser uma pendência aberta: os problemas P0 foram incorporados ao blueprint e ao guia operacional do Hotel Aurora. O registro histórico abaixo permanece como diagnóstico da rodada, mas a versão consolidada do caso é `examples/caso_canonico_intermediario.json`.

Comando oficial para geração do baseline:

```bash
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

A geração final do pacote deve ser confirmada em ambiente local com Chromium/Playwright disponível.

Arquivo do caso: `examples/caso_canonico_intermediario.json`

Data de registro: 2026-06-05

## Participantes

- Marcelo, 36
- Gabi, 35
- Marina, 11

## Tempo de jogo

Tempo total: **100 minutos**.

Observação: a maior parte do tempo foi consumida no Envelope 1.

## Resultado geral

O grupo gostou bastante dos documentos e do plot, mas a experiência mostrou falhas importantes de orientação e progressão.

Resumo:

- documentos agradaram;
- plot foi bem recebido;
- Gabi conseguiu enxergar a lógica e praticamente resolveu sozinha;
- Marcelo ficou perdido em parte da progressão, mas a solução fez sentido após a visão de Gabi;
- Marina teve pouca participação;
- Envelope 1 concentrou tempo demais;
- objetivos de cada envelope não estavam claros;
- dicas foram fracas e pouco úteis;
- guia do facilitador não explicou bem a solução.

## Pontos positivos

- Os documentos funcionaram e foram interessantes.
- O plot foi bem recebido.
- A distração das chaves de acesso funcionou.
- O grupo desconfiou de caminhos falsos plausíveis.
- A hipótese com Caio e Marta pareceu possível ao grupo.
- A estrutura teve material suficiente para uma jogadora resolver com boa leitura dos documentos.

## Problemas encontrados

### 1. Objetivo do Envelope 1 não ficou claro

Dúvidas do grupo:

- O que precisamos resolver no primeiro envelope?
- O motivo do sumiço da Helena?
- O culpado?
- Em que momento sabemos que podemos abrir o segundo envelope?

Interpretação:

O Envelope 1 não trouxe uma pergunta operacional clara. O grupo investigou, mas não sabia qual conclusão era suficiente para avançar.

Correção recomendada:

- Criar uma página de objetivo/abertura de envelope, ou incorporar na carta inicial, deixando claro que o E1 pede uma hipótese parcial.
- O E1 não deve pedir culpado nem motivo completo.
- O E1 deve pedir algo como: “determinar se a ausência parece voluntária ou se há sinais de encenação/contradição”.

### 2. Critério de abertura do Envelope 2 não ficou claro

O grupo não sabia quando podia abrir o segundo envelope.

Correção recomendada:

Criar um critério simples e diegético, por exemplo:

- abrir E2 quando o grupo tiver uma hipótese sobre o que não fecha na ausência de Helena;
- ou quando conseguir apontar dois sinais contraditórios no E1;
- ou quando responder uma pergunta parcial indicada pelo facilitador.

O critério deve estar no material do facilitador e, possivelmente, de forma imersiva na abertura do E1.

### 3. Envelope 2 também não deixou claras as perguntas finais

Dúvida do grupo:

- quais perguntas precisamos responder no Envelope 2?

Correção recomendada:

O E2 deve orientar, sem entregar solução, que o grupo precisa fechar:

- o que aconteceu com a presença/ausência de Helena;
- quem tinha meio de sustentar a versão errada;
- qual motivo torna a ação coerente;
- quais suspeitas iniciais são descartadas.

### 4. Inconsistência de motivação envolvendo a pasta Aurora

Problema percebido:

- No e-mail, Helena já sabe da pasta Aurora e fala com Caio, copiando Marta.
- Então não fica claro por que Marta precisaria mandar um bilhete para Helena.
- Também não fica claro por que Marta precisaria relembrar Helena do desejo familiar se Helena já estava ciente.
- A dúvida emergente: Helena não ia honrar o pedido do pai/mãe?

Interpretação:

O conflito central ficou conceitualmente interessante, mas a motivação operacional do bilhete ficou incoerente ou mal explicada.

Correção recomendada:

Escolher uma das direções:

1. Helena sabe da promessa, mas pretende reinterpretá-la publicamente de forma conveniente. O bilhete não “lembra” Helena; ele a atrai com a promessa de um documento novo/comprometedor.
2. Helena sabe da pasta, mas não sabe que existe uma carta específica mais forte.
3. Marta acredita que Helena vai trair a promessa, mas precisa tirá-la do salão para impedir que ela anuncie uma versão pública controlada.
4. Remover ou ajustar o e-mail para que ele não deixe Helena tão consciente do ponto central antes do bilhete.

A melhor direção provável: Helena sabe que a pasta existe, mas não conhece ou não pretende usar a carta decisiva. O bilhete deve sugerir que surgiu um documento que mudaria o brinde, não apenas repetir o que ela já sabe.

### 5. Geografia sem mapa gerou confusão

Problema percebido:

- Não ficou claro que o terraço era outro cômodo/ambiente.
- Talvez o mapa ajudasse, mas também poderia simplificar demais o desafio.

Interpretação:

A decisão de não usar mapa é boa para diferenciar o caso do Mirante, mas o caso precisa compensar com orientação espacial textual mais clara.

Correção recomendada:

Não voltar imediatamente com mapa completo.

Antes, tentar:

- diagrama textual simples de ambientes;
- cartão “orientação do andar social” sem planta baixa;
- descrição mais clara na carta inicial ou relatório de circulação;
- termos consistentes para salão, terraço, recepção, corredor de serviço, sala de memória e suíte.

### 6. Participação da criança foi baixa

Marina, 11 anos, não conseguiu interagir muito.

Interpretação:

O caso Intermediário pode ser adulto demais em densidade de texto e inferência, mas ainda pode incluir pontos de interação para criança sem reduzir dificuldade geral.

Correção recomendada:

Criar elementos de participação:

- cartões de suspeitos/personagens sem spoiler;
- checklist de evidências físicas;
- tabela simples “quem viu pessoa / quem viu objeto / quem viu movimento”; 
- marcador de hipóteses por envelope;
- pergunta de facilitador direcionada para a criança em momentos seguros.

### 7. Dicas foram fracas

Observação:

- As dicas quase não foram usadas.
- Quando usadas, quase não deram direção.

Correção recomendada:

Reescrever dicas em camadas mais úteis:

- leve: orientar foco;
- média: indicar tipo de cruzamento;
- forte: formular pergunta quase operacional;
- quase gabarito: pedir uma tabela ou síntese específica.

Dicas devem ajudar o grupo a sair do travamento, não apenas repetir clima.

### 8. Guia do facilitador não explicou bem a solução

Problema:

- O guia não explicou bem a solução.
- A solução pareceu indicar que Marta armou, mas não resolveu claramente a aparente consciência prévia de Helena sobre a pasta/promessa.

Correção recomendada:

Reescrever o guia com:

- solução em 5 frases;
- linha do tempo real;
- linha do tempo aparente;
- resposta esperada do Envelope 1;
- resposta esperada do Envelope 2;
- por que cada suspeito forte é descartado;
- por que a motivação de Marta é coerente;
- como explicar a pasta Aurora sem contradição;
- quando abrir E2;
- como usar dicas.

## Decisões de correção recomendadas

### P0 — Antes de novo playtest

1. Adicionar objetivo claro ao Envelope 1.
2. Adicionar critério claro para abertura do Envelope 2.
3. Adicionar objetivo claro ao Envelope 2.
4. Corrigir a lógica da pasta Aurora/e-mail/bilhete.
5. Reescrever guia do facilitador.
6. Reescrever dicas contextuais para serem mais úteis.

### P1 — Melhorias importantes

1. Melhorar orientação espacial sem mapa completo.
2. Criar material de apoio para participação da criança.
3. Reduzir densidade onde o texto atrapalha a leitura coletiva.
4. Reforçar que o Envelope 1 pede hipótese parcial, não solução final.

### P2 — Avaliar depois

1. Reconsiderar mapa mínimo apenas se orientação textual continuar falhando.
2. Ajustar quantidade de documentos se o E1 continuar longo demais.
3. Criar modo de playtest com papéis/leituras para envolver jogadores mais novos.

## Métricas registradas

```json
{
  "status": "validado_pos_playtest_refinamento",
  "rodadas": 1,
  "tempo_real_medio": 100,
  "jogadores_teste": 3,
  "perfil_jogadores": ["adulto 36", "adulto 35", "criança 11"],
  "travamentos": [
    "objetivo do Envelope 1 pouco claro",
    "critério de abertura do Envelope 2 pouco claro",
    "perguntas finais do Envelope 2 pouco claras",
    "motivação do bilhete/pasta Aurora confusa",
    "orientação espacial sem mapa parcialmente confusa"
  ],
  "hipoteses_erradas_ou_parciais": [
    "Renato como possível cúmplice",
    "Caio e Marta como envolvidos",
    "saída/ausência voluntária ainda confusa no E1"
  ],
  "pontos_positivos": [
    "documentos agradaram",
    "plot agradou",
    "distração das chaves de acesso funcionou",
    "solução fez sentido após articulação do grupo"
  ],
  "ajustes_pos_teste": [
    "objetivos por envelope",
    "critério de avanço",
    "dicas contextuais",
    "guia do facilitador",
    "lógica da pasta Aurora",
    "orientação espacial textual"
  ],
  "status_final": "régua canônica Intermediária validada",
  "comando_oficial_geracao_baseline": "python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict",
  "confirmacao_pacote_final": "A geração final do pacote deve ser confirmada em ambiente local com Chromium/Playwright disponível."
}
```

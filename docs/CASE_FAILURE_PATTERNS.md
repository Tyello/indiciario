# Padrões de falha editorial em casos do Indiciário

Este documento registra falhas já observadas ou codificadas na documentação editorial do Indiciário para calibrar próximos casos. Ele não substitui `docs/DIRETRIZES_EDITORIAIS.md`, `docs/ANTI_OBVIEDADE.md` nem `docs/BLUEPRINT_AUTHORING_GUIDE.md`; em conflito, siga esses documentos.

Fontes usadas: `docs/ESTADO_ATUAL.md`, `docs/DIRETRIZES_EDITORIAIS.md`, `docs/ANTI_OBVIEDADE.md`, `docs/CASE_DESIGN_PIPELINE.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md` e `docs/playtests/`.

Referências canônicas atuais:

- **Iniciante:** *O Desvio da Reserva Mirante* — régua de clareza estrutural para primeiro contato.
- **Intermediário:** *O Último Brinde do Hotel Aurora* — régua validada pós-playtest para densidade textual, recontextualização em E2 e condução sem mapa.

> Decisão consolidada: **Hotel Aurora deve continuar sem mapa**, salvo evidência nova de playtest ou instrução explícita.

## 1. Objetivo de envelope ausente ou ambíguo

### Sintoma

O grupo lê o envelope sem saber qual pergunta precisa responder, quando pode avançar ou que tipo de hipótese parcial é suficiente.

### Por que prejudica

Sem objetivo claro, o grupo tenta resolver o caso inteiro cedo demais. Isso aumenta tempo morto, gera frustração e faz o facilitador improvisar critérios de avanço.

### Exemplo abstrato

E1 reúne logs, depoimentos e carta inicial, mas não explica se o grupo deve identificar culpado, confirmar ausência, montar cronologia ou apontar contradições.

### Correção recomendada

- Declarar pergunta diegética, resposta esperada, critério de avanço e o que ainda não precisa ser resolvido.
- Fazer E1 produzir hipótese parcial, tensão ou contradição produtiva, não solução final.
- Espelhar o objetivo do envelope em `contratos_evidencia`, `dicas_contextuais` e guia do facilitador.

## 2. Documento que parece dica

### Sintoma

Um documento de jogador usa tom de orientação, checklist ou instrução de cruzamento em vez de parecer evidência do mundo ficcional.

### Por que prejudica

O jogador sente que o autor está explicando como resolver. Isso reduz agência investigativa e enfraquece a diegese.

### Exemplo abstrato

Um recibo inclui frases como “compare este valor com o extrato” ou “este documento não prova sozinho”.

### Correção recomendada

- Mover interpretação para guia do facilitador, dica contextual, gabarito ou metadado interno.
- Reescrever o documento como evidência bruta: recibo, contrato, e-mail, log ou registro operacional.
- Se a pista está correta mas artificial, revisar também o recipiente documental: a informação talvez pertença a outro tipo de documento.

## 3. Documento que resolve demais

### Sintoma

Um único documento permite responder quem fez, como fez, por que fez e qual benefício obteve.

### Por que prejudica

O mistério deixa de exigir cadeia de evidência. A descoberta vira leitura passiva de conclusão pronta.

### Exemplo abstrato

Um depoimento afirma que uma personagem planejou a sabotagem, explica o motivo financeiro e descreve o método.

### Correção recomendada

- Distribuir a solução em cadeia: hipótese, recontextualização, confirmação independente e descarte justo de alternativas.
- Garantir que todo documento seja necessário, mas não suficiente.
- Usar o E2 para recontextualizar algo do E1, não apenas repetir uma acusação já fechada.

## 4. Mapa que entrega solução

### Sintoma

O mapa do jogador destaca rota, área crítica, câmera offline, campo de visão, X vermelho, seta de solução ou legenda investigativa.

### Por que prejudica

Mapa deve orientar espaço, não funcionar como gabarito visual. Destaques analíticos substituem dedução por leitura de marcação.

### Exemplo abstrato

Uma planta baixa mostra a “rota provável da peça” com seta colorida e a câmera desligada destacada em vermelho.

### Correção recomendada

- Manter mapas de jogador como plantas neutras: ambientes, paredes, portas, janelas, câmeras neutras, nomes de ambientes, códigos de portas, norte e escala discretos.
- Colocar versões analíticas apenas no guia do facilitador ou em material interno.
- Para Hotel Aurora, preservar a solução já validada: orientação espacial textual, cartões ou descrição operacional, **sem mapa completo**.

## 5. Chat confessional

### Sintoma

Chat, WhatsApp, e-mail curto ou conversa operacional vira fala de vilão: “o plano deu certo”, “ninguém vai descobrir” ou “fui eu”.

### Por que prejudica

Conversa confessional entrega intenção e autoria cedo demais. Também soa inverossímil: pessoas envolvidas raramente registrariam uma confissão tão limpa em canal operacional.

### Exemplo abstrato

Exportação de grupo contém mensagem: “trocamos a taça e ninguém percebeu”.

### Correção recomendada

- Fazer chats parecerem exportações operacionais ambíguas, com ruído, lacunas, termos internos e mensagens que ganham sentido depois.
- Dar origem clara ao chat: grupo operacional, recepção, gerência ou canal de serviço.
- Evitar duplicar informações que o template já apresenta, como horário.

## 6. Red herring artificial

### Sintoma

Falso suspeito existe apenas para enganar, sem motivo aparente, comportamento plausível ou evidência de descarte justa.

### Por que prejudica

Ambiguidade vira arbitrariedade. O grupo sente que qualquer resposta poderia ser verdadeira até o autor revelar uma preferência.

### Exemplo abstrato

Um personagem aparece com “atitude suspeita” em vários documentos, mas não há pressão real, oportunidade plausível nem documento que explique por que essa suspeita cai.

### Correção recomendada

- Dar função dramática a cada suspeito: motivo aparente, oportunidade aparente, segredo ou pressão.
- Planejar documento ou contrato de descarte para alternativas fortes.
- Usar red herrings como mentira plausível sustentada por fatos parciais, não como ruído gratuito.

## 7. Material visual pouco crível

### Sintoma

Documento comercial, administrativo, mapa, assinatura, rubrica, cartão ou apoio de mesa parece peça de puzzle antes de parecer documento real.

### Por que prejudica

A estética pode ser bonita, mas a credibilidade documental cai. O grupo passa a ler design gráfico como indicação de solução.

### Exemplo abstrato

Um orçamento resume todos os fornecedores lado a lado com coluna “suspeita”, em vez de existir como proposta independente de empresa.

### Correção recomendada

- Separar documentos comerciais em peças plausíveis: orçamento, recibo, contrato, extrato, chat e e-mail, quando isso aumentar investigação.
- Evitar quadro comparativo de jogador quando ele funcionar como síntese do puzzle.
- Manter assinaturas/rubricas como característica editorial de personagem, não texto cursivo genérico.
- Tratar cartões como apoio de mesa, não evidência principal.

## 8. Guia do facilitador insuficiente

### Sintoma

O facilitador não consegue explicar a solução, usar dicas no momento certo, abrir envelopes com segurança ou resolver travamentos comuns.

### Por que prejudica

Mesmo com bons documentos, a sessão perde ritmo. O facilitador vira coautor improvisado da condução e pode entregar demais ou de menos.

### Exemplo abstrato

O guia diz apenas “a culpada é Marta”, mas não traz linha do tempo real, linha do tempo aparente, descarte dos suspeitos fortes nem resposta esperada por envelope.

### Correção recomendada

- Incluir solução em síntese curta, cadeia causal, linha do tempo real, linha do tempo aparente, objetivos por envelope, critérios de avanço, red herrings e descartes.
- Explicar como e quando usar dicas contextuais em camadas.
- Permitir linguagem analítica no guia, mas impedir que essa linguagem vaze para documentos de jogador.

## 9. Pilar de validação sem pista de suporte (ER_002)

### Sintoma

Um dos quatro pilares de validação do E1 aparece no gabarito, no critério de avanço ou no guia, mas não existe pista correspondente na `matriz_pistas` apontando o documento que o sustenta.

### Por que prejudica

O grupo precisa defender a hipótese para abrir o E2, mas a defesa depende de leitura do autor ou de inferência não documentada. O facilitador fica sem base justa para negar ou liberar avanço.

### Exemplo abstrato

O E1 exige provar “benefício operacional suspeito”, mas nenhum log, recibo, escala ou depoimento planejado contém pista explícita que sustente esse pilar.

### Correção recomendada

- Para cada pilar do E1, criar pelo menos uma pista na `matriz_pistas`.
- Apontar o documento exato onde a pista aparece e o que ela prova.
- Confirmar pilares críticos por documento independente quando o pilar sustentar avanço.

## 10. Red herring com descarte solto, não fiado como pista (ER_006)

### Sintoma

O falso suspeito tem documento de descarte, mas a `matriz_pistas` não contém pista que leve o grupo a esse documento ou mostre como ele contradiz/contextualiza a suspeita.

### Por que prejudica

O red herring parece arbitrariedade do autor: o descarte existe no gabarito ou na prosa, não na investigação. O grupo pode continuar acusando uma alternativa falsa sem ferramenta justa para eliminá-la.

### Exemplo abstrato

Um fornecedor suspeito tem contrato legítimo que o inocenta, mas nenhuma pista da matriz manda comparar o horário do contrato, a autorização ou a entrega com a suspeita levantada em E1.

### Correção recomendada

- Declarar uma pista de descarte na `matriz_pistas` para cada red herring forte.
- Ligar a pista ao documento de descarte e ao falso suspeito correspondente.
- Escrever o descarte como evidência bruta, não como frase explicativa de autor.

## 11. Revelação do E2 marcada como avanço obrigatório (ER_007)

### Sintoma

Um contrato com `obrigatoria_para_avanco: true` usa `prova_principal` em E2, ou a revelação/solução do E2 foi modelada como se fosse requisito para abrir o próximo envelope.

### Por que prejudica

O gate de avanço passa a exigir documento que o grupo ainda não possui, ou vaza que uma prova futura é necessária. Isso transforma destino investigativo em pré-requisito e contamina a progressão.

### Exemplo abstrato

O contrato `fase: "E1"` pede identificar o beneficiário final, mas a `prova_principal` é um extrato que só aparece no E2; ou o contrato final aparece com `obrigatoria_para_avanco: true`.

### Correção recomendada

- Usar `obrigatoria_para_avanco: true` somente para contratos com `prova_principal` no envelope atual.
- No gate E1→E2, manter prova principal em documento E1.
- Modelar revelação do E2 como contrato `fase: "E2"`/`tipo: "recontextualizacao"` e solução como `fase: "final"`/`tipo: "solucao_final"`, ambos com `obrigatoria_para_avanco: false`.

## 12. Suspeitos demais para o nível (PT_003 + deriva de dificuldade)

### Sintoma

O caso declara uma dificuldade, mas apresenta mais suspeitos do que a régua recomenda para aquele nível; por exemplo, Intermediário acima de 6 suspeitos relevantes.

### Por que prejudica

A mesa dispersa hipóteses, demora para descartar alternativas e sente dificuldade maior que a prometida. Mesmo com evidência correta, a experiência deriva para nível superior.

### Exemplo abstrato

Um caso intermediário apresenta sete pessoas com motivo, oportunidade ou comportamento suspeito, todas exigindo leitura e descarte ativo.

### Correção recomendada

- Contar apenas suspeitos com hipótese plausível de mesa, não figurantes.
- Fundir personagens, reduzir suspeita aparente ou transformar suspeito fraco em contexto.
- Conferir `docs/DIFFICULTY_FRAMEWORK.md` antes de fechar elenco: Intermediário recomenda até 6 suspeitos.

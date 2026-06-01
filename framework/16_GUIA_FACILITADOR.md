# 16 — Guia do Facilitador e Dicas Contextuais

Este arquivo define como produzir e usar o `guia_facilitador.pdf`, um material
confidencial de condução de sessão. Ele complementa o gabarito e as dicas
progressivas, mas não substitui os contratos de evidência nem autoriza atalhos de
solução sem prova documental.

---

## 1. Papel do facilitador

O facilitador é o guardião da experiência, não um narrador que resolve o caso pelo
grupo. Suas funções são:

- preparar os envelopes e manter materiais confidenciais separados;
- apresentar a premissa pública sem acrescentar fatos novos;
- observar se o grupo está formulando hipóteses com base em documentos;
- liberar envelopes apenas quando o critério da fase for cumprido;
- oferecer dicas contextuais graduais quando houver travamento real;
- conduzir o fechamento, pedindo que os jogadores reconstruam a solução com
evidências.

O facilitador nunca deve improvisar pistas externas, confirmar suspeitos por
intuição ou revelar a verdade real antes da etapa final.

---

## 2. Gabarito vs. guia do facilitador

| Material | Finalidade | Uso durante a sessão |
|----------|------------|----------------------|
| Gabarito do mestre | Explica a solução, culpados, linha do tempo e interpretação correta das pistas. | Consultar para checar respostas e conduzir o fechamento. |
| Guia do facilitador | Organiza condução, fluxo de sessão, critérios de avanço, contratos obrigatórios e dicas contextuais. | Consultar durante a partida para decidir quando intervir, liberar envelope ou oferecer dica. |

O gabarito responde **o que aconteceu**. O guia do facilitador responde **como
conduzir o grupo até que ele demonstre o que aconteceu**.

---

## 3. Quando liberar envelopes

A liberação de envelopes deve seguir os contratos de evidência obrigatórios da
fase. Um grupo pode avançar quando consegue declarar uma conclusão operacional e
apontar:

1. a prova principal;
2. a confirmação independente;
3. a ação esperada ou inferência correta;
4. a ausência de dependência de documento ainda não liberado.

Não exija que os jogadores usem as mesmas palavras do blueprint. Exija que a
conclusão seja equivalente e sustentada pelos documentos corretos.

Se o grupo chega a uma conclusão correta sem citar evidências, peça: “Qual
arquivo prova isso?” ou “Que outro documento confirma essa leitura?”. Essa
pergunta preserva o jogo justo e evita avanço por chute.

---

## 4. Quando oferecer dicas

Ofereça dicas apenas quando houver travamento observável, por exemplo:

- o grupo circula pelos mesmos documentos por vários minutos sem nova hipótese;
- uma pista essencial foi lida, mas não conectada ao documento de confirmação;
- jogadores estão presos em um red herring já descartável pelo material;
- a discussão virou adivinhação sem referência documental;
- o tempo de sessão exige uma intervenção para preservar o ritmo.

Use sempre a menor intervenção suficiente:

1. **leve** — aponta onde olhar ou qual comparação fazer;
2. **média** — identifica uma relação entre documentos;
3. **forte** — descreve a inferência necessária sem nomear a solução final;
4. **quase_gabarito** — destrava fechamento quando o grupo já viu as evidências,
mas não consegue formular a conclusão.

---

## 5. Como evitar spoiler

Para evitar spoiler:

- não leia a verdade real em voz alta;
- não mencione nomes de culpados em dicas leves ou médias;
- não entregue dicas de fase futura antes da liberação do envelope correspondente;
- transforme respostas diretas em perguntas documentais;
- ofereça uma dica por vez e aguarde nova tentativa;
- use a condição de uso da dica como trava: se a condição ainda não ocorreu, não
use a dica.

Uma boa intervenção muda o foco do grupo para evidências existentes; uma má
intervenção substitui a investigação por narração do facilitador.

---

## 6. Como conduzir grupos travados

Quando um grupo travar, siga este protocolo:

1. **Diagnosticar o travamento**: mapa, personagem, cronologia, finanças,
logística, documento, contrato, descarte ou solução.
2. **Pedir evidência**: solicite que o grupo separe os documentos que sustentam a
hipótese atual.
3. **Oferecer dica leve**: direcione a comparação sem resolver.
4. **Verificar avanço**: se o grupo conecta prova e confirmação, retome o fluxo.
5. **Escalar gradualmente**: só use dicas médias/fortes se a intervenção anterior
não gerou progresso.
6. **Quase-gabarito apenas no final**: use quando a experiência está em risco e o
grupo já manipulou as evidências necessárias.

Se o grupo estiver rápido demais, não atrase artificialmente. Apenas peça que
verbalize a cadeia de evidências antes de liberar o próximo material.

---

## 7. Contratos de evidência como critério de avanço

Contratos de evidência são a régua objetiva de condução. Cada contrato conecta:

- fase;
- conclusão esperada;
- prova principal;
- confirmação independente;
- ação esperada do jogador;
- obrigatoriedade para avanço.

Use contratos obrigatórios para decidir liberação de envelope. Use contratos não
obrigatórios para reconhecer entendimento lateral, descarte de suspeitos ou
aprofundamento de tema.

Critério prático:

- **Avança**: conclusão correta + prova principal + confirmação independente.
- **Pede mais evidência**: conclusão correta sem confirmação.
- **Oferece dica**: documentos certos foram vistos, mas não conectados.
- **Não avança**: conclusão depende de documento futuro ou informação externa.

---

## 8. Dicas contextuais no blueprint

O campo `dicas_contextuais` é opcional para compatibilidade com blueprints antigos,
mas recomendado em casos com `contratos_evidencia`. Cada dica deve declarar:

- `id` único;
- `categoria` de travamento;
- `fase` (`E1`, `E2`, `E3`... ou `final`);
- `titulo` curto;
- `condicao_uso` real e observável;
- `texto` pronto para o facilitador adaptar à mesa;
- `nivel` (`leve`, `media`, `forte`, `quase_gabarito`);
- contratos e/ou documentos relacionados existentes.

As dicas contextuais são material confidencial do facilitador. Elas nunca entram
nos envelopes dos jogadores.

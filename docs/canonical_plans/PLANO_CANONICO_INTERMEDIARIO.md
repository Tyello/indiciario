# Plano do caso canônico Intermediário

Este arquivo é o espaço de planejamento do próximo caso canônico Intermediário do Indiciário.

Não gerar `examples/caso_canonico_intermediario.json` antes deste plano estar editorialmente aprovado.

## Status

Premissa escolhida: **Hotel / desaparecimento em jantar fechado**.

Título provisório:

> **O Último Brinde do Hotel Aurora**

Este título ainda pode mudar. O objetivo agora é consolidar núcleo dramático, suspeitos, curva de suspeita e plano de envelopes antes de qualquer blueprint JSON.

## Premissa editorial

O caso Intermediário não deve ser uma versão mais difícil de “O Desvio da Reserva Mirante”.

Ele deve nascer com:

- história mais humana;
- pergunta dramática mais forte;
- suspeitos mais equilibrados;
- pelo menos dois falsos caminhos fortes;
- E1 com hipótese boa, mas incompleta;
- E2 que recontextualiza o E1;
- mecânica investigativa diferente de logs + mapa + credenciais + contrato/recibo.

## Resultado do playtest do canônico Iniciante

Caso: “O Desvio da Reserva Mirante”

Resultado:

- jogadores gostaram dos documentos;
- material visual/documental funcionou;
- caso ficou fácil demais;
- serviu melhor como Iniciante do que como Intermediário.

Lição para o Intermediário:

- não basta remover dicas óbvias;
- a ambiguidade precisa nascer na estrutura;
- suspeitos precisam ter motivo, oportunidade, comportamento estranho e descarte justo;
- a virada deve mudar o significado de algo visto antes;
- o caso precisa ter mais tensão humana, não só lógica documental.

## Critérios para o canônico Intermediário

O novo caso deve atender, no mínimo:

1. 4 a 5 suspeitos plausíveis.
2. Pelo menos 2 red herrings fortes.
3. Nenhum culpado deve concentrar todas as evidências fortes no E1.
4. E1 deve gerar uma hipótese sólida, mas incompleta.
5. E2 deve recontextualizar algo do E1, não apenas confirmar.
6. Deve haver pelo menos 2 momentos reais de descoberta.
7. Deve haver uma mentira aparente plausível.
8. Deve haver motivo humano, não apenas lógica operacional.
9. O mapa, se existir, deve ser ferramenta espacial neutra.
10. Nenhum documento do jogador pode funcionar como checklist de solução.

## Premissa escolhida — Hotel / desaparecimento em jantar fechado

### Cenário

Hotel Aurora, um hotel histórico em processo de reabertura após anos de decadência. A família proprietária realiza um jantar fechado para investidores, antigos funcionários e imprensa local.

O evento acontece em um andar social do hotel:

- salão de jantar;
- terraço envidraçado;
- corredor de serviço;
- copa/cozinha de apoio;
- biblioteca ou sala de memória;
- recepção do andar;
- elevador social;
- escada de serviço;
- suíte reservada.

### Incidente inicial

Helena Valença, herdeira e figura central da reabertura, desaparece antes do brinde final.

A leitura inicial parece simples: depois de uma discussão discreta, Helena teria deixado o jantar por vontade própria para evitar um anúncio público.

Mas alguns registros não fecham:

- o último brinde menciona Helena como se ela ainda estivesse no salão;
- um depoimento diz que ela passou pelo corredor de serviço;
- outro documento sugere presença dela no terraço;
- o cartão da suíte registra uso em horário incompatível;
- um objeto pessoal aparece onde não deveria.

### Pergunta dramática

Helena saiu por vontade própria, foi retirada do jantar ou alguém fabricou sua presença no horário errado?

### Motivo humano

Reputação familiar, herança, medo de exposição pública e disputa sobre o futuro do hotel.

O desaparecimento não deve ser apenas “sumiu porque alguém queria dinheiro”. Deve envolver vergonha, controle de narrativa e medo de uma verdade vir à tona durante o jantar.

### Mecânica investigativa principal

**Depoimentos contraditórios + cronologia + objeto com dupla interpretação.**

O grupo precisa perceber que a linha do tempo social do jantar não bate com os registros físicos do hotel.

A chave do caso não deve ser um único log. A solução deve nascer do cruzamento entre:

- depoimentos;
- mapa/planta do andar;
- horários de serviço;
- cartão de quarto/elevador;
- bilhete/convite;
- mensagem de bastidor;
- objeto pessoal de Helena;
- registro de recepção.

### Por que este caso é bom para Intermediário

- cenário fácil de imaginar;
- tensão social mais forte que auditoria documental;
- suspeitos podem ter motivos humanos diferentes;
- depoimentos permitem ambiguidade real;
- o E1 pode levar a uma hipótese errada, mas plausível;
- o E2 pode recontextualizar a presença/ausência de Helena;
- permite documentos interessantes: menu, lista de lugares, bilhetes, depoimentos, planta do hotel, cartão de acesso, mensagem e relatório de recepção.

### Risco principal

Virar apenas quebra-cabeça de horários.

Mitigação:

- criar motivo humano forte;
- evitar muitos registros frios;
- fazer cada suspeito ter comportamento emocionalmente plausível;
- incluir objeto/documento que muda de significado no E2.

## Núcleo dramático provisório

```json
{
  "pergunta_central": "Helena saiu por vontade própria, foi retirada do jantar ou alguém fabricou sua presença no horário errado?",
  "verdade_real": "Helena deixou o salão antes do brinde final após receber uma mensagem/bilhete que parecia vir de alguém de confiança. Sua ausência foi mascarada por um objeto pessoal e por relatos ambíguos, criando a impressão de que ela permaneceu no evento por mais tempo do que realmente permaneceu.",
  "mentira_aparente": "Helena discutiu com alguém e abandonou o jantar por vontade própria para evitar o anúncio público da reabertura.",
  "tema_humano": "Reputação familiar, controle da narrativa e medo de exposição pública.",
  "motivo_emocional": "Alguém precisava impedir que Helena revelasse, durante o brinde, uma informação que mudaria o futuro do hotel e exporia uma vergonha familiar ou profissional.",
  "virada_principal": "O grupo percebe que a presença de Helena no fim do jantar foi parcialmente fabricada; o objeto usado como sinal de presença não prova que ela estava ali.",
  "sensacao_final_desejada": "Os jogadores devem sentir que todos estavam olhando para a pessoa que saiu, quando a pergunta correta era: quem precisava que todos acreditassem que ela ainda estava lá?"
}
```

## Verdade real e mentira aparente

### Verdade real provisória

Helena sai do salão antes do horário que todos assumem como “última presença”. Ela é atraída para fora por uma comunicação que parece legítima. Enquanto isso, sinais sociais de presença — objeto pessoal, lugar à mesa, fala de outro convidado, movimentação no corredor — mantêm a impressão de que ela ainda circulava pelo jantar.

A intenção do culpado não precisa ser “machucar Helena”. A intenção pode ser:

- atrasar o anúncio;
- impedir a leitura de um documento;
- recuperar um objeto/carta/contrato em posse dela;
- criar uma saída voluntária falsa;
- fazer outra pessoa parecer responsável.

### Mentira aparente

Helena teria deixado o jantar por impulso após uma discussão.

Essa mentira é plausível porque:

- houve tensão antes do brinde;
- ao menos uma pessoa viu alguém parecido com Helena perto do terraço;
- o lugar dela permaneceu montado;
- um objeto pessoal dela apareceu em local público;
- um registro físico sugere deslocamento, mas não prova autoria.

### Como a mentira deve cair

O E2 deve mostrar que:

- a linha do tempo dos depoimentos não fecha;
- o objeto pessoal não prova presença;
- o registro físico pode ser de cartão/objeto, não da pessoa;
- alguém tinha motivo para fabricar presença e atraso;
- a ausência de Helena no momento do brinde era útil para alguém.

## Suspeitos provisórios

Os nomes abaixo são provisórios. Podem mudar antes do blueprint.

### 1. Lívia Valença — prima e sócia minoritária

```json
{
  "nome": "Lívia Valença",
  "papel_publico": "Prima de Helena e sócia minoritária no hotel",
  "segredo_ou_pressao": "Temia perder influência com a reabertura e com uma possível mudança no controle do hotel.",
  "motivo_aparente": "Queria impedir Helena de fazer o anúncio final.",
  "oportunidade_aparente": "Circulou entre salão, terraço e biblioteca durante o jantar.",
  "comportamento_estranho": "Insiste que Helena estava alterada e que saiu por vontade própria.",
  "evidencia_contra": ["mensagem ambígua", "conhecimento da rotina familiar", "acesso ao objeto pessoal"],
  "evidencia_que_descarta": [],
  "curva_de_suspeita": {
    "inicio": "medio",
    "E1": "medio-alto",
    "E2": "alto",
    "final": "culpada ou articuladora principal"
  }
}
```

### 2. Caio Fontes — gerente do hotel

```json
{
  "nome": "Caio Fontes",
  "papel_publico": "Gerente do Hotel Aurora",
  "segredo_ou_pressao": "A reabertura expõe falhas antigas de gestão e dívidas operacionais.",
  "motivo_aparente": "Poderia querer evitar um anúncio que o afastaria do controle do hotel.",
  "oportunidade_aparente": "Tem acesso a chaves, staff e corredores internos.",
  "comportamento_estranho": "Tenta controlar a narrativa com discrição excessiva e orienta funcionários a não alarmarem convidados.",
  "evidencia_contra": ["controle de acessos", "contato com recepção", "presença no corredor de serviço"],
  "evidencia_que_descarta": ["registro independente o coloca resolvendo ocorrência pública em parte da janela crítica"],
  "curva_de_suspeita": {
    "inicio": "alto",
    "E1": "alto",
    "E2": "medio-baixo",
    "final": "red herring forte"
  }
}
```

### 3. Isadora Nunes — jornalista convidada

```json
{
  "nome": "Isadora Nunes",
  "papel_publico": "Jornalista local convidada para cobrir a reabertura",
  "segredo_ou_pressao": "Tinha uma pauta sensível sobre a família Valença e queria uma declaração exclusiva.",
  "motivo_aparente": "Poderia pressionar Helena ou usar o desaparecimento como furo jornalístico.",
  "oportunidade_aparente": "Foi vista perto do terraço e trocou mensagens durante o jantar.",
  "comportamento_estranho": "Anota detalhes demais e muda uma frase no depoimento.",
  "evidencia_contra": ["anotações", "mensagens", "proximidade com Helena"],
  "evidencia_que_descarta": ["tem prova de que buscava entrevista, não retirada; seu horário não fecha com o deslocamento físico"],
  "curva_de_suspeita": {
    "inicio": "medio",
    "E1": "medio-alto",
    "E2": "baixo",
    "final": "red herring forte"
  }
}
```

### 4. Renato Viana — chef/eventos

```json
{
  "nome": "Renato Viana",
  "papel_publico": "Chef responsável pelo jantar de reabertura",
  "segredo_ou_pressao": "Teve conflito com Helena por cortes de orçamento e demissão de equipe antiga.",
  "motivo_aparente": "Tinha ressentimento e acesso ao corredor de serviço.",
  "oportunidade_aparente": "Circulou entre cozinha, copa e salão no horário crítico.",
  "comportamento_estranho": "Diz não ter visto Helena, apesar de estar na rota provável de circulação.",
  "evidencia_contra": ["acesso de serviço", "conflito prévio", "horário de prato final"],
  "evidencia_que_descarta": ["sua equipe confirma preparação simultânea e o item de cozinha vira descarte justo"],
  "curva_de_suspeita": {
    "inicio": "medio",
    "E1": "alto",
    "E2": "baixo",
    "final": "red herring forte"
  }
}
```

### 5. Marta Salgado — governanta antiga

```json
{
  "nome": "Marta Salgado",
  "papel_publico": "Governanta antiga do hotel",
  "segredo_ou_pressao": "Protege funcionários antigos e sabe segredos da família Valença.",
  "motivo_aparente": "Poderia querer impedir o anúncio por lealdade ao passado do hotel.",
  "oportunidade_aparente": "Conhece passagens, salas fechadas e rotinas de serviço.",
  "comportamento_estranho": "Reconhece um detalhe que não deveria ter visto se estivesse onde disse estar.",
  "evidencia_contra": ["conhecimento espacial", "acesso à rouparia/biblioteca", "depoimento cuidadoso demais"],
  "evidencia_que_descarta": ["pode revelar uma verdade antiga sem ser autora do desaparecimento"],
  "curva_de_suspeita": {
    "inicio": "baixo",
    "E1": "medio",
    "E2": "medio",
    "final": "testemunha-chave ou cúmplice involuntária"
  }
}
```

## Mecânica investigativa principal

```json
{
  "tipo": "depoimentos_contraditorios_cronologia_objeto_duplo",
  "descricao": "O grupo cruza depoimentos, horários, planta do andar e registros de acesso para perceber que a presença de Helena no fim do jantar foi inferida por sinais indiretos, não comprovada por visão direta.",
  "documentos_necessarios": [
    "lista de convidados/lugares",
    "menu ou programa do jantar",
    "depoimentos curtos",
    "planta do andar",
    "registro de cartão/elevador",
    "mensagens internas",
    "objeto pessoal ou anotação",
    "relatório de recepção"
  ],
  "risco": "Virar puzzle de horários se os documentos não tiverem emoção e comportamento humano."
}
```

## Momentos de descoberta esperados

```json
[
  {
    "momento": "O grupo percebe que a última presença de Helena no salão é inferida por objeto/lugar à mesa, não por testemunho direto confiável.",
    "documentos": ["lista de lugares", "depoimento", "foto/descrição de mesa", "mensagem"],
    "emocao": "dúvida inicial",
    "risco": "Se estiver explícito demais, entrega a virada cedo."
  },
  {
    "momento": "O grupo percebe que dois deslocamentos atribuídos a Helena não poderiam ter sido feitos pela mesma pessoa na janela indicada.",
    "documentos": ["planta", "registro de acesso", "depoimentos", "relatório de serviço"],
    "emocao": "virada lógica",
    "risco": "Virar planilha de horário se não houver motivo emocional claro."
  },
  {
    "momento": "O grupo reinterpreta o objeto pessoal de Helena: ele não prova que ela esteve no local; prova que alguém queria sugerir isso.",
    "documentos": ["objeto pessoal", "depoimento", "mensagem de bastidor"],
    "emocao": "recontextualização",
    "risco": "Se o objeto for óbvio demais, vira pista única."
  }
]
```

## Plano de envelopes provisório

```json
[
  {
    "envelope": "E1",
    "funcao": "gerar hipótese forte, mas incompleta",
    "conclusao_esperada": "Helena provavelmente não saiu simplesmente por vontade própria; a linha do tempo do jantar tem contradições e alguém manipulou sinais de presença.",
    "nao_precisa_descobrir_ainda": [
      "quem arquitetou a manipulação",
      "motivo completo",
      "significado final do objeto pessoal",
      "qual documento do E2 recontextualiza o anúncio"
    ],
    "pilares_obrigatorios": [
      "contradição de horário",
      "deslocamento espacial incompatível",
      "sinal de presença não confiável"
    ],
    "riscos": [
      "grupo acusar o gerente cedo demais",
      "grupo tratar o desaparecimento como saída voluntária sem investigar",
      "grupo se perder em horários sem perceber o drama"
    ]
  },
  {
    "envelope": "E2",
    "funcao": "recontextualizar a ausência e fechar motivo/autoria",
    "conclusao_esperada": "A presença final de Helena foi fabricada para atrasar ou impedir um anúncio; a pessoa responsável usou conhecimento social e espacial do hotel para criar uma saída voluntária falsa.",
    "pilares_obrigatorios": [
      "motivo humano",
      "meio de manipulação",
      "falso sinal de presença",
      "descarte dos red herrings fortes"
    ],
    "riscos": [
      "E2 apenas confirmar E1 sem virada",
      "culpado ficar óbvio por excesso de presença documental",
      "documentos explicarem demais a solução"
    ]
  }
]
```

## Plano documental provisório

Não é blueprint ainda. É uma lista de funções documentais.

### Envelope 1

| Código provisório | Tipo | Função | Observação |
|---|---|---|---|
| E1-01 | carta/programa do jantar | contexto | apresentar evento e tom social |
| E1-02 | lista de convidados/lugares | ferramenta | mostrar quem estava onde, sem entregar culpado |
| E1-03 | menu com horários de serviço | contexto/pista | dar ritmo do jantar e janela do brinde |
| E1-04 | depoimento 1 | red herring | aponta para gerente ou chef |
| E1-05 | depoimento 2 | contradição | cria conflito com E1-04 |
| E1-06 | planta do andar | ferramenta | mapa neutro, sem rota |
| E1-07 | registro de recepção/elevador/cartão | pista principal | mostra deslocamento ou uso de acesso |
| E1-08 | mensagem/bilhete parcial | pista ambígua | sugere chamado legítimo, mas incompleto |
| E1-09 | descrição de objeto pessoal | pista ambígua | não deve revelar ainda que foi plantado |

### Envelope 2

| Código provisório | Tipo | Função | Observação |
|---|---|---|---|
| E2-01 | depoimento revisado ou complemento | recontextualização | muda leitura de E1 |
| E2-02 | mensagem completa ou origem do bilhete | pista principal | revela manipulação sem checklist |
| E2-03 | registro de bastidor/serviço | confirmação | confirma meio físico |
| E2-04 | documento familiar/contrato/anúncio | motivo | explica por que impedir o brinde importava |
| E2-05 | objeto pessoal recontextualizado | virada | prova fabricação de presença |
| E2-06 | depoimento de descarte | descarta red herring forte |
| E2-07 | evidência final | confirmação independente | fecha autoria/motivo |
| E2-08 | guia do facilitador/dicas | separado | não entra como documento de jogador |

## Riscos de obviedade

```json
[
  {
    "risco": "Lívia concentrar motivo familiar e acesso demais desde o E1.",
    "impacto": "Jogadores acusam a culpada cedo demais.",
    "mitigacao": "Dar motivos fortes também ao gerente, chef e jornalista; segurar a prova de motivo familiar para E2."
  },
  {
    "risco": "Objeto pessoal parecer obviamente plantado.",
    "impacto": "Virada perde força.",
    "mitigacao": "No E1, objeto deve ter explicação inocente plausível. No E2, outro documento muda seu significado."
  },
  {
    "risco": "Cronologia virar checklist de horários.",
    "impacto": "Caso fica frio e mecânico.",
    "mitigacao": "Depoimentos precisam ter intenção emocional e contradições humanas, não só timestamps."
  }
]
```

## Riscos de injustiça

```json
[
  {
    "risco": "Jogadores não entenderem o espaço do hotel.",
    "impacto": "Travamento na mecânica espacial.",
    "mitigacao": "Planta simples, neutra, com poucos ambientes e acessos claros."
  },
  {
    "risco": "Contradição de depoimentos depender de detalhe pequeno demais.",
    "impacto": "Solução parece arbitrária.",
    "mitigacao": "Ter confirmação independente em registro de acesso ou serviço."
  },
  {
    "risco": "Motivo familiar parecer melodrama sem evidência.",
    "impacto": "Solução parece novela e não dedução.",
    "mitigacao": "Motivo deve aparecer por documento concreto no E2, não por confissão."
  }
]
```

## Pendências antes do blueprint

Antes de gerar JSON, ainda falta decidir:

1. culpado final: manter Lívia como articuladora principal ou escolher outro suspeito;
2. destino/estado de Helena: desaparecimento sem dano, retenção temporária, fuga induzida ou encenação parcial;
3. qual é o objeto pessoal com dupla interpretação;
4. qual é o documento de E2 que recontextualiza a motivação;
5. se o caso terá 2 ou 3 envelopes;
6. tom final: elegante/social, familiar sombrio ou suspense leve;
7. se haverá criança no público-alvo de teste ou se este canônico será mais adulto.

## Critério de aprovação do plano

O plano só pode virar blueprint JSON quando responder bem:

- A pergunta dramática é intrigante?
- Existe motivo humano forte?
- Há pelo menos 4 suspeitos plausíveis?
- Há pelo menos 2 red herrings fortes?
- O E1 gera hipótese incompleta?
- O E2 recontextualiza algo?
- Há momentos de descoberta reais?
- O caso é diferente do Mirante?
- Os documentos planejados parecem existir no mundo da história?
- O caso parece divertido em mesa?

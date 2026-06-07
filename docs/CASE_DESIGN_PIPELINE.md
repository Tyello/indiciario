# Pipeline de design de caso

Este documento define o processo editorial para criar casos investigativos no Indiciário antes de gerar qualquer blueprint JSON.

A principal lição do primeiro playtest é clara: o framework já consegue produzir documentos visualmente interessantes, mas isso não garante que o mistério seja intrigante. O próximo salto é fazer a história nascer forte antes dos documentos.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Princípio central

Um bom caso não é aquele que esconde a resposta.

Um bom caso é aquele que faz o grupo acreditar em uma resposta plausível antes de perceber a solução correta.

O pipeline de design editorial deve seguir esta ordem antes do JSON:

```text
história forte
→ verdade oculta
→ mentira plausível
→ suspeitos interessantes
→ curva de suspeita
→ momentos de descoberta
→ plano de envelopes
→ plano documental
→ blueprint JSON
```

Depois que o blueprint existir, o fluxo operacional oficial do Indiciário 2.0 inicial passa a ser:

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library / templates
→ Build Package
→ Baseline visual real
→ Playtest
→ Ajustes finos
```

Não iniciar um caso criando documentos finais nem pular direto do plano para PDFs. O Case Kernel e o Case Review devem tornar visível se a pergunta pública, a hipótese de E1, a recontextualização de E2, a motivação atual, as evidências obrigatórias e os falsos caminhos sustentam uma investigação jogável antes de qualquer polimento visual.

## Antiobjetivo

Evitar que o projeto vire apenas um gerador de documentos bonitos.

Documento bonito não salva história fraca. Template bom não compensa mistério óbvio. Validador estrutural não garante diversão.

O caso só deve avançar para blueprint quando tiver:

- pergunta pública clara;
- pergunta dramática central;
- motivo humano com consequência atual;
- suspeitos plausíveis;
- mentira aparente;
- virada investigativa;
- momentos de descoberta;
- objetivos por envelope;
- critérios de avanço por envelope;
- riscos de obviedade mapeados;
- riscos de injustiça mapeados.

## Etapa 1 — Premissas candidatas

Antes de escolher um caso, gerar múltiplas premissas curtas.

Cada premissa deve conter:

- cenário;
- incidente inicial;
- pergunta dramática;
- motivo humano;
- mecânica investigativa principal;
- tipo de documentos prováveis;
- por que seria divertido jogar.

Formato recomendado:

```markdown
## Premissa 1 — Título provisório

**Cenário:**

**Incidente:**

**Pergunta dramática:**

**Motivo humano:**

**Mecânica investigativa:**

**Documentos prováveis:**

**Por que é divertido:**

**Risco:**
```

Selecionar a premissa mais forte antes de continuar.

## Etapa 2 — Pergunta pública do caso

Antes do núcleo dramático, definir a pergunta pública que coloca os jogadores em ação.

A pergunta pública é diferente da pergunta central interna: ela é o mandato diegético apresentado ao grupo. Ela precisa explicar por que aquelas pessoas foram chamadas, por que aqueles documentos existem e que consequência concreta está em jogo.

Todo caso deve responder:

- quem pediu a apuração;
- por que pediu;
- qual impacto concreto existe se o caso não for esclarecido;
- por que os documentos foram reunidos e entregues ao grupo.

Formato obrigatório no schema atual:

```json
"conflito_central": {
  "pergunta_publica": "",
  "quem_pede_apuracao": "",
  "motivo_da_apuracao": "",
  "risco_concreto": "",
  "verdade_aparente": "",
  "verdade_real_resumida": ""
}
```

Sem pergunta pública, o grupo lê documentos sem saber qual decisão precisa tomar, qual urgência existe ou por que o dossiê foi montado. A pergunta pública deve estar em `conflito_central.pergunta_publica` e ser repetida em `guia_operacional.pergunta_publica`, com os demais campos do conflito central preenchendo solicitante, motivo, risco e verdades aparente/real.

## Etapa 3 — Núcleo dramático

Todo caso precisa de núcleo dramático explícito.

```json
"nucleo_dramatico": {
  "pergunta_central": "",
  "verdade_real": "",
  "mentira_aparente": "",
  "tema_humano": "",
  "motivo_emocional": "",
  "virada_principal": "",
  "sensacao_final_desejada": ""
}
```

### Pergunta central

A pergunta central deve gerar curiosidade, não apenas identificar culpado.

Fraco:

```text
Quem desviou o objeto?
```

Melhor:

```text
A peça foi roubada, substituída ou nunca esteve onde todos dizem que estava?
```

Fraco:

```text
Quem sabotou a reunião?
```

Melhor:

```text
O vazamento destruiu os documentos por acidente ou foi criado para impedir uma votação?
```

### Tema humano

Todo caso precisa de tensão humana.

Exemplos:

- ambição;
- medo de exposição;
- reputação;
- dívida;
- inveja profissional;
- lealdade familiar;
- vingança;
- proteção de alguém;
- orgulho ferido;
- humilhação pública.

Sem tema humano, o caso vira auditoria.

## Etapa 4 — Verdade real e mentira aparente

Separar a verdade do que parece verdade.

```markdown
## Verdade real

O que realmente aconteceu, em ordem causal.

## Mentira aparente

O que os jogadores provavelmente vão acreditar no começo.

## Por que a mentira é plausível

Quais evidências sustentam temporariamente essa leitura.

## Como a mentira cai

Quais documentos recontextualizam a hipótese inicial.
```

A mentira aparente não deve ser falsa por truque barato. Ela deve ser uma interpretação plausível dos fatos disponíveis.

## Etapa 5 — Suspeitos e curva de suspeita

Todo suspeito relevante precisa ter função dramática.

Para cada suspeito:

```json
{
  "personagem_id": "",
  "nome": "",
  "papel_publico": "",
  "segredo_ou_pressao": "",
  "motivo_aparente": "",
  "oportunidade_aparente": "",
  "comportamento_estranho": "",
  "evidencia_contra": [],
  "evidencia_que_descarta": [],
  "curva_de_suspeita": {
    "inicio": "baixo|medio|alto",
    "E1": "baixo|medio|alto",
    "E2": "baixo|medio|alto",
    "final": "culpado|complice|descartado|ambíguo"
  }
}
```

### Regra de red herring justo

Um falso suspeito forte precisa ter:

1. motivo aparente;
2. oportunidade aparente;
3. comportamento estranho;
4. evidência concreta que o descarta.

Se não tiver os quatro, é só ruído.

## Etapa 6 — Mecânica investigativa principal

Cada caso canônico deve testar uma mecânica investigativa diferente.

Exemplos:

- logs + mapa + credenciais;
- depoimentos contraditórios + cronologia;
- documento adulterado + versão original;
- ausência significativa de registro;
- rota espacial com falsa oportunidade;
- cadeia financeira indireta;
- objeto físico com dupla interpretação;
- álibi verdadeiro usado para encobrir outra ação.

A mecânica deve ser definida antes dos documentos.

```json
"mecanica_investigativa_principal": {
  "tipo": "depoimentos_contraditorios_e_cronologia",
  "descricao": "O grupo precisa perceber que duas versões não podem coexistir no mesmo horário.",
  "documentos_necessarios": ["depoimentos", "planta", "registro de horário", "mensagem"],
  "risco": "Virar caça-palavras de horário se não houver motivo humano forte."
}
```

## Etapa 7 — Momentos de descoberta

Todo caso precisa planejar seus “aha moments”.

```json
"momentos_de_descoberta": [
  {
    "momento": "O grupo percebe que um registro inicialmente neutro muda de significado.",
    "documentos": [],
    "emocao": "virada lógica",
    "risco": "Se estiver explícito demais, vira dica."
  }
]
```

Um bom momento de descoberta faz o grupo dizer:

> espera, a gente leu isso errado.

Sem momentos de descoberta, o jogo vira leitura burocrática.

## Etapa 8 — Plano de envelopes

Antes de documentos finais, definir o que cada envelope deve causar e quando o grupo deve avançar. Envelope não é pasta temática: é etapa de progressão investigativa.

Todo envelope precisa ter:

- pergunta diegética;
- resposta esperada;
- o que ainda não precisa ser resolvido;
- critério de avanço;
- forma diegética de apresentar esse avanço.

```json
"objetivos_por_envelope": [
  {
    "envelope": "E1",
    "funcao": "levantar hipótese boa, mas incompleta",
    "pergunta_diegetica": "",
    "resposta_esperada": "",
    "nao_precisa_resolver_ainda": [],
    "criterio_de_avanco": "",
    "forma_diegetica_de_avanco": "",
    "documentos_minimos": [],
    "riscos": []
  },
  {
    "envelope": "E2",
    "funcao": "recontextualizar algo do E1",
    "pergunta_diegetica": "",
    "resposta_esperada": "",
    "nao_precisa_resolver_ainda": [],
    "criterio_de_avanco": "",
    "forma_diegetica_de_avanco": "",
    "documentos_minimos": [],
    "riscos": []
  }
]
```

`objetivos_por_envelope` é campo schema-enforced do `Blueprint`. Reflita esses objetivos em `contratos_evidencia`, documentos e `dicas_contextuais`; `guia_operacional.resposta_esperada_por_envelope` deve espelhar os mesmos envelopes e respostas para validar a condução do facilitador.

### Regra do E1

O E1 não deve pedir a solução final.

Ele deve terminar com uma hipótese parcial, uma tensão entre versões ou uma recontextualização inicial.

Ruim:

```text
E1 já resolve quase tudo e E2 só confirma.
```

Bom:

```text
E1 revela oportunidade, mecanismo ou uma contradição forte, mas ainda não fecha motivo, benefício e cadeia de prova.
```

### Regra do E2

O E2 deve recontextualizar algo do E1.

Ele não deve apenas confirmar a hipótese inicial. Ele deve trazer uma virada real: motivo atual, prova concreta de benefício, versão original, descarte justo de falso suspeito ou cronologia que muda a leitura anterior.

### Forma diegética de avanço

O avanço deve existir dentro do mundo da história. Exemplos:

- o solicitante libera um lote de documentos antes retido;
- uma secretaria encontra a versão original de um anexo;
- um cartório responde a uma solicitação;
- a equipe recebe registros complementares após formular uma hipótese parcial;
- uma testemunha decide entregar material quando percebe risco concreto.

Evitar avanço artificial do tipo “agora abra o E2 porque o jogo precisa continuar” sem justificativa diegética.

## Etapa 9 — Plano documental

Só depois de definir história, suspeitos, virada e envelopes criar documentos.

Para cada documento:

```json
{
  "codigo": "E1-01",
  "tipo": "",
  "visibilidade": "jogador|facilitador|interno",
  "funcao_investigativa": "pista_principal|confirmacao|descarte|red_herring|contexto|ferramenta",
  "o_que_mostra": "",
  "o_que_nao_pode_entregar": [],
  "confirma": [],
  "confirmado_por": [],
  "risco_de_handholding": "baixo|medio|alto"
}
```

Documento de jogador deve mostrar evidência, não dizer como interpretar.

### Recados e bilhetes

Se um personagem já sabe uma informação, qualquer recado, bilhete, e-mail ou mensagem posterior precisa trazer algo novo: documento omitido, versão original, lista não repassada, prova concreta, risco imediato, mudança de prazo ou pressão nova.

Não usar recado posterior apenas para repetir informação que o destinatário já conhece. Isso soa como voz do autor falando com o jogador.

## Etapa 10 — Motivação com consequência atual

Motivação histórica precisa ter consequência atual.

Não basta haver uma carta antiga, trauma familiar ou segredo de décadas atrás. O passado precisa pressionar o presente do caso.

Fraco:

```text
Carta de 1968 explica uma mágoa antiga.
```

Forte:

```text
Carta de 1968 sustenta disputa atual de moradia, risco de expulsão, perda de herança ou exposição pública.
```

Consequências atuais possíveis:

- moradia;
- expulsão;
- dívida moral;
- herança;
- reputação;
- demissão;
- perda concreta;
- risco público;
- fechamento de instituição;
- rompimento familiar com efeito prático.

Sem consequência atual, motivação histórica vira lore, não urgência investigativa.

## Etapa 11 — Dicas contextuais

Dicas contextuais precisam destravar ações.

Cada dica deve indicar:

- condição de uso;
- intensidade;
- ação mental esperada;
- o que desbloqueia.

```json
"dicas_contextuais": [
  {
    "id": "DC-E1-EXEMPLO-01",
    "categoria": "logistica",
    "fase": "E1",
    "titulo": "Comparar log e escala",
    "condicao_uso": "Use se o grupo suspeita de várias pessoas, mas ainda não cruzou horário de credencial com a escala.",
    "texto": "Oriente o grupo a montar duas colunas: quem deveria estar em ronda e qual credencial aparece no intervalo crítico. Não nomeie suspeitos; peça que procurem incompatibilidades.",
    "nivel": "media",
    "contratos_relacionados": ["C-E1-OPORTUNIDADE"],
    "documentos_relacionados": ["E1-04", "E1-05"]
  }
]
```

No schema atual, `condicao_uso` registra a condição de uso, `nivel` registra a intensidade, `texto` deve explicitar a ação mental esperada e o desbloqueio pretendido, e `contratos_relacionados`/`documentos_relacionados` ligam a dica à cadeia de evidência. A dica pode orientar uma operação mental, como comparar horários, separar versão pública de versão real ou procurar consequência atual. Ela não deve entregar culpado, motivo e documentos obrigatórios em formato de checklist.

## Etapa 12 — Guia do facilitador operacional

O guia do facilitador deve permitir conduzir a sessão sem improvisar solução.

Conteúdo mínimo obrigatório:

- pergunta pública;
- resposta esperada por envelope;
- quando liberar o próximo envelope;
- linha do tempo aparente;
- linha do tempo real;
- red herrings e descartes;
- explicação da motivação;
- solução em síntese.

O guia pode explicar cruzamentos, citar códigos de documentos e usar linguagem analítica. Essa linguagem deve ficar fora dos documentos de jogador.

## Etapa 13 — Riscos de obviedade

Antes do blueprint final, listar riscos de caso fácil demais. Use `docs/ANTI_OBVIEDADE.md` como régua oficial e antecipe os achados que `generator/obviousness_checker.py` reportaria no validator (`OBV_001` a `OBV_012`).

```json
"riscos_de_obviedade": [
  {
    "risco": "Um personagem aparece como único decisor em muitos documentos.",
    "impacto": "Jogadores acusam cedo demais.",
    "mitigacao": "Adicionar outros nomes plausíveis no processo ou separar decisão em documentos diferentes."
  }
]
```

Riscos comuns:

- suspeito aparece em documentos demais;
- motivo financeiro explícito cedo demais;
- mapa mostra rota;
- chat parece confissão;
- orçamento vira quadro comparativo;
- um valor é muito diferente dos demais;
- documento diz quais evidências cruzar.

## Etapa 14 — Riscos de injustiça

Também mapear riscos de travamento injusto.

```json
"riscos_de_injustica": [
  {
    "risco": "Jogadores não conseguem ligar código de usuário à pessoa.",
    "impacto": "Travamento no E1.",
    "mitigacao": "Adicionar relação de credenciais ou tornar códigos mais explícitos na dificuldade Iniciante."
  }
]
```

Riscos comuns:

- confirmação está em envelope futuro;
- código não tem tradução acessível;
- pista depende de conhecimento externo;
- documento parece decorativo, mas é obrigatório;
- red herring não tem descarte justo;
- detalhe visual importante é pequeno demais no PDF.

## Etapa 15 — Autocrítica antes do JSON

Antes de gerar blueprint, produzir uma autoauditoria.

```json
"auto_auditoria": {
  "obvio_demais": [],
  "injusto_demais": [],
  "documentos_com_voz_do_autor": [],
  "suspeitos_subutilizados": [],
  "pistas_sem_confirmacao": [],
  "confirmacoes_em_envelope_errado": []
}
```

Se houver problemas graves, corrigir o plano antes de gerar JSON.

## Etapa 16 — Blueprint JSON

Só gerar o blueprint JSON depois que o plano Markdown estiver aprovado.

O blueprint deve ser a execução do design, não o lugar onde se descobre a história.

## Critérios mínimos para avançar para JSON

Antes de gerar o blueprint, o plano precisa responder:

- Qual é a pergunta pública e quem pediu a apuração?
- Qual é a pergunta dramática central?
- Qual é a verdade real?
- Qual é a mentira aparente?
- Quais são os 4 ou 5 suspeitos plausíveis?
- Como cada suspeito cresce ou cai ao longo dos envelopes?
- Quais são os momentos de descoberta?
- O que o E1 resolve sem pedir solução final?
- Qual é o critério de avanço do E1?
- O que o E2 recontextualiza?
- Qual consequência atual sustenta a motivação?
- Como as dicas destravam ações sem entregar solução?
- O guia do facilitador contém progressão operacional e linhas do tempo?
- Quais documentos são pista, confirmação, descarte, ruído ou ferramenta?
- O que pode ficar óbvio demais?
- O que pode ficar injusto demais?

Se essas respostas não estiverem boas, não gerar JSON.

## Aplicação aos canônicos

### Canônico Iniciante

Atual:

- `examples/caso_canonico_iniciante.json`
- “O Desvio da Reserva Mirante”
- validado em primeiro playtest como fácil, mas com documentos agradáveis.

Papel: régua introdutória.

### Próximo Canônico Intermediário

Não deve ser uma versão difícil do Mirante.

Deve nascer com:

- nova premissa;
- nova mecânica investigativa;
- mais ambiguidade estrutural;
- suspeitos mais equilibrados;
- E2 recontextualizando a leitura do E1;
- pergunta pública clara;
- objetivo e critério de avanço por envelope;
- motivação histórica com consequência atual concreta;
- guia do facilitador operacional;
- menos explicitação de códigos;
- pelo menos dois falsos caminhos fortes.

Usar o template de plano em `docs/canonical_plans/PLANO_CANONICO_INTERMEDIARIO.md` antes de gerar JSON.

# Guia de autoria de blueprint

Este guia define o contrato editorial mínimo para escrever blueprints de casos no Indiciário.

Use este documento junto com `docs/CASE_DESIGN_PIPELINE.md` para o processo de criação, `docs/DIRETRIZES_EDITORIAIS.md` para a fonte editorial, `docs/ANTI_OBVIEDADE.md` para o guardrail automático de obviedade e `docs/LLM_OPERATING_MANUAL.md` para operação de agentes. Ele não substitui o schema técnico: ele descreve o que o blueprint precisa conter para gerar uma experiência jogável, com progressão clara e sem documentos de jogador explicando a solução.

Nota de schema: `conflito_central`, `objetivos_por_envelope` e `guia_operacional` agora são campos estruturados e schema-enforced do `Blueprint`. Eles continuam podendo ser refletidos em `premissa`, documentos, `contratos_evidencia` e `dicas_contextuais`, mas a fonte de verdade para progressão e condução é o blueprint estruturado.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Objetivo do guia

Evitar que próximos casos sejam apenas coleções de bons documentos.

Um blueprint aceitável precisa deixar explícito:

- qual pergunta pública coloca o caso em movimento;
- qual objetivo cada envelope cumpre na mesa;
- quando o grupo deve avançar;
- por que a motivação importa agora;
- como o facilitador conduz o jogo sem improvisar gabarito;
- quais informações ficam em documentos de jogador e quais ficam em guia, dica ou metadados.

## Contrato obrigatório do caso

Todo caso precisa declarar uma pergunta pública clara antes do plano documental.

A pergunta pública deve responder:

1. **Quem pediu a apuração?**
2. **Por que pediu?**
3. **Qual impacto concreto existe se nada for esclarecido?**
4. **Por que estes documentos foram reunidos e entregues ao grupo?**

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

A pergunta pública não precisa revelar a verdade real. Ela precisa dar ao grupo um mandato diegético: por que estão lendo aquele dossiê e qual decisão, reparo, risco ou consequência está em jogo. Registre essa intenção em `conflito_central.pergunta_publica` e repita a mesma pergunta em `guia_operacional.pergunta_publica`, para que o facilitador e os relatórios usem a mesma fonte estruturada.

## Objetivo obrigatório por envelope

Todo envelope precisa ter função de progressão, não apenas agrupar documentos.

Para cada envelope, defina:

- **pergunta diegética:** a pergunta que o grupo deve tentar responder com aquele conjunto;
- **resposta esperada:** conclusão parcial aceitável para mesa seguir adiante;
- **o que ainda não precisa ser resolvido:** evita que o E1 cobre a solução final;
- **critério de avanço:** evidências, hipótese ou consenso mínimo que libera o próximo envelope;
- **forma diegética de apresentar o avanço:** como a liberação aparece dentro do mundo da história.

Formato obrigatório no schema atual:

```json
"objetivos_por_envelope": [
  {
    "envelope": "E1",
    "pergunta_diegetica": "",
    "resposta_esperada": "",
    "nao_precisa_resolver_ainda": [],
    "criterio_de_avanco": "",
    "forma_diegetica_de_avanco": "",
    "documentos_minimos": []
  }
]
```

Além de declarar esses objetivos, reflita-os em `contratos_evidencia`, na distribuição dos documentos por envelope e nas `dicas_contextuais`. `guia_operacional.resposta_esperada_por_envelope` deve espelhar os mesmos envelopes e respostas esperadas para permitir validação de consistência.

### Regra do E1

O E1 não deve pedir a solução final.

Ele deve gerar uma destas saídas:

- hipótese parcial forte;
- tensão entre versões;
- suspeita inicial plausível;
- recontextualização inicial de um fato público;
- pergunta mais precisa para investigar no E2.

Se o grupo consegue acusar corretamente, explicar motivo e fechar a cadeia de evidência apenas com E1, o envelope está grande ou explícito demais.

### Regra do E2

O E2 deve recontextualizar algo do E1.

Ele não deve apenas confirmar uma resposta que o E1 já entregou. O E2 deve acrescentar pelo menos uma virada real, como:

- motivo que muda a leitura de oportunidade;
- prova concreta de benefício;
- versão original de documento adulterado;
- cronologia que derruba a leitura inicial;
- descarte justo de falso suspeito forte;
- consequência atual que explica uma motivação histórica.

## Motivação com consequência atual

Motivação histórica só funciona se tiver consequência no presente do caso.

Fraco:

```text
Uma carta de 1968 revela uma mágoa antiga.
```

Forte:

```text
A carta de 1968 sustenta uma disputa atual de moradia e pode provocar expulsão, perda de herança e exposição pública de uma família.
```

Ao escrever o blueprint, toda motivação central deve indicar a consequência atual envolvida, por exemplo:

- moradia;
- expulsão;
- dívida moral;
- herança;
- reputação;
- demissão;
- perda financeira concreta;
- risco público;
- cassação de contrato;
- fechamento de instituição;
- rompimento familiar com efeito prático.

Sem consequência atual, o motivo vira lore e não urgência investigativa.

## Guardrail anti-obviedade no blueprint

Ao escrever `documentos[].conteudo`, trate `docs/ANTI_OBVIEDADE.md` como contrato obrigatório de evidência bruta. O checker automático integrado ao validator (`generator/obviousness_checker.py`) sinaliza confissões, linguagem conclusiva, chat confessional, depoimento onisciente, vazamento de campos internos e nome de culpado perto de ação incriminadora.

Isso afeta principalmente:

- `conteudo`, que vira PDF de jogador;
- `emocao_esperada` em E1, que não deve antecipar solução;
- `objetivo_narrativo`, que é interno, mas não deve contaminar o tom com culpado + ação;
- logs/sistemas/escalas em Intermediário ou superior, que devem preferir códigos operacionais.

Se o validator emitir `OBV_*`, corrija o documento para sugerir por evidência, não para concluir por texto.

## Recados, bilhetes e informação já conhecida

Se um personagem já sabe uma informação, qualquer recado, bilhete, e-mail ou mensagem posterior precisa trazer algo novo.

Algo novo pode ser:

- documento omitido;
- versão original;
- lista que não foi repassada;
- prova concreta;
- risco imediato;
- mudança de prazo;
- ameaça ou pressão nova;
- detalhe que contradiz uma versão anterior.

Não crie mensagem apenas para repetir ao jogador o que outro personagem já saberia. Repetição sem novidade parece voz do autor e enfraquece a diegese.

## Dicas contextuais operacionais

Dicas contextuais precisam destravar ações, não recitar gabarito.

Cada dica deve declarar:

- **condição de uso:** quando o facilitador deve oferecer;
- **intensidade:** leve, média ou forte;
- **ação mental esperada:** comparar horários, separar versão pública de versão real, mapear benefício, checar ausência de registro etc.;
- **o que desbloqueia:** qual travamento a dica deve resolver.

Formato compatível com o modelo atual:

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

No schema atual, `condicao_uso` registra a condição de uso, `nivel` registra a intensidade, `texto` deve explicitar a ação mental esperada e o desbloqueio pretendido, e `contratos_relacionados`/`documentos_relacionados` ligam a dica à cadeia de evidência. Dica pode orientar uma ação mental. Ela não deve listar resposta final, culpado, motivo e documentos em formato de checklist.

## Guia do facilitador operacional

Todo caso precisa de guia do facilitador capaz de conduzir a sessão sem improviso.

O guia deve conter:

- pergunta pública;
- resposta esperada por envelope;
- quando liberar o próximo envelope;
- linha do tempo aparente;
- linha do tempo real;
- red herrings e como descartá-los;
- explicação da motivação;
- solução em síntese.

O guia pode usar linguagem analítica, códigos de documentos e explicação de cruzamentos. Essa linguagem não deve vazar para documentos de jogador.

## Separação entre evidência e interpretação

Documento de jogador deve mostrar evidência bruta, não interpretação do autor.

Permitido em documento de jogador:

- registros;
- recibos;
- e-mails diegéticos;
- chats com ruído natural;
- propostas comerciais individuais;
- mapas neutros;
- atas, bilhetes, fotos, anexos e logs que existiriam no mundo da história.

Não permitido em documento de jogador:

- instrução para comparar documentos;
- explicação do que uma pista prova;
- frase que diga que algo não prova sozinho;
- lista dos documentos necessários para resolver;
- referência a `E1-01`, `E2-03` ou códigos internos como orientação de leitura;
- linguagem como “hipótese”, “gabarito”, “red herring” ou “ruído controlado”.

A interpretação pertence ao guia do facilitador, às dicas contextuais, ao gabarito e aos metadados internos.

## Checklist antes de aprovar um blueprint

Antes de gerar PDF, confirme:

1. Existe pergunta pública com solicitante, motivo, impacto e justificativa do dossiê?
2. Cada envelope tem pergunta diegética, resposta esperada, critério de avanço e forma diegética de avanço?
3. O E1 gera hipótese parcial, tensão ou recontextualização inicial sem pedir solução final?
4. O E2 recontextualiza algo do E1 e não apenas confirma?
5. Toda motivação histórica tem consequência atual concreta?
6. Recados posteriores trazem informação nova para quem os recebe?
7. Cada dica contextual tem condição de uso, intensidade, ação mental esperada e desbloqueio?
8. O guia do facilitador explica progressão, linhas do tempo, red herrings, motivação e síntese da solução?
9. Documentos de jogador mostram evidência bruta sem voz do autor?
10. O caso pode ser conduzido por um facilitador que não participou da escrita?

Se qualquer item falhar, corrija o plano antes de ajustar templates, renderer ou validator.

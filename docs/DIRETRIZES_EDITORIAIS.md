# Diretrizes editoriais do Indiciário

Este documento consolida decisões editoriais usadas para criar e revisar casos investigativos no Indiciário.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Regra principal

Documento de jogador deve conter evidência bruta, não interpretação do autor.

Separação de papéis:

- **documento do jogador** mostra o que aconteceu ou o que existe no mundo da história;
- **guia do facilitador** explica o que significa;
- **dica contextual** orienta quando o grupo trava;
- **gabarito** resolve;
- **metadados internos** podem usar linguagem analítica, mas não devem vazar para PDFs do jogador.

Nenhum documento de jogador deve soar como checklist de solução.

A progressão do caso deve estar no plano, nos envelopes, nas dicas contextuais e no guia do facilitador. Não resolva falhas de progressão colocando interpretação dentro do material do jogador.

## Guardrail anti-obviedade

Use `docs/ANTI_OBVIEDADE.md` como régua específica para impedir que documentos de jogador entreguem a solução cedo demais. O guia detalha regras para logs, chats, depoimentos, E1, linguagem conclusiva, campos internos e exemplos dos canônicos Mirante e Hotel Aurora.

O validator integra essas regras por meio de `generator/obviousness_checker.py`, com códigos `OBV_001` a `OBV_012`. Achados do checker devem ser tratados como revisão editorial do documento, não como convite para mover gabarito para outro documento de jogador.

## Contrato editorial de progressão

Todo caso precisa de uma pergunta pública clara, com:

- quem pediu a apuração;
- por que pediu;
- qual impacto concreto existe;
- por que os documentos foram reunidos.

Todo envelope precisa declarar:

- pergunta diegética;
- resposta esperada;
- o que ainda não precisa ser resolvido;
- critério de avanço;
- forma diegética de apresentar esse avanço.

O E1 não deve pedir a solução final. Ele deve produzir hipótese parcial, tensão, suspeita inicial plausível ou recontextualização inicial.

O E2 deve recontextualizar algo do E1, não apenas confirmar. A recontextualização pode vir de motivo atual, benefício concreto, versão original de documento, descarte justo de falso suspeito ou cronologia que muda a leitura anterior.


## Pistas por ausência

Quando a conclusão parcial depender de ausência, o caso precisa fornecer uma ferramenta de comparação. Ausência sem estrutura vira invisibilidade, não pista.

Pista por ausência ocorre quando o jogador precisa perceber:

- algo que não foi visto;
- um registro que não existe;
- uma coluna que fica vazia;
- uma pessoa que não aparece;
- uma confirmação direta que nunca acontece;
- uma evidência esperada que falta.

Ferramentas aceitáveis incluem folha de cruzamento, quadro de presença, linha do tempo incompleta, matriz de testemunhos, registro comparativo neutro, checklist em branco ou tabela de observações por categoria.

A ferramenta não deve dizer “observe a ausência”. Ela deve organizar categorias para que o vazio apareça. Documento de jogador não interpreta a ausência; o guia do facilitador pode explicar por que a ausência importa.

> Se a pista é uma ausência, o documento deve tornar o espaço da ausência visível, não explicar a ausência.

> Uma ausência só é jogável quando o grupo sabe onde ela deveria aparecer.

## Peso probatório: evidência direta, indireta e sistêmica

Quando o caso depender de presença, ausência, álibi ou deslocamento, o blueprint deve deixar claro quais evidências são diretas, indiretas e sistêmicas. Evidência indireta tratada como evidência direta pode tornar o caso injusto ou confuso.

- **Evidência direta:** alguém viu, ouviu, falou com, reconheceu ou interagiu diretamente com a pessoa, objeto ou evento. Exemplos: testemunha viu a pessoa de frente, funcionário falou com a pessoa, câmera mostra o rosto ou áudio é reconhecível.
- **Evidência indireta / por objeto:** um objeto, vestígio ou elemento associado sugere presença, mas não prova sozinho. Exemplos: echarpe, broche, copo, mala, assinatura duvidosa ou crachá encontrado.
- **Evidência sistêmica:** sistema registra evento, mas pode não provar presença humana direta. Exemplos: cartão de acesso, log de porta, sensor, reserva, abertura de suíte, registro sem imagem ou entrada sem permanência medida.

Documento de jogador pode mostrar esses registros de forma bruta. A classificação analítica deve ficar em contratos de evidência, guia, Case Kernel, Case Review ou notas editoriais, não em artefato diegético.

## Causalidade, relação prévia e credibilidade de ação

A solução final precisa ter mecanismo causal documentado. Motivo explica por quê. Oportunidade explica quando. Mecanismo explica como.

Ao revisar a solução, confirme:

- como a pessoa foi atraída;
- como o objeto foi movido;
- como o registro foi manipulado;
- como o falso sinal foi criado;
- como o grupo pode inferir isso por documentos;
- qual documento ancora essa inferência;
- se a solução depende de uma ação que não aparece em nenhum documento.

Se a solução depende de confiança, autoridade, hábito, obediência ou relação prévia, essa relação precisa ter pelo menos uma âncora documental antes da revelação final. A âncora pode ser discreta e não precisa explicar a solução.

Exemplos de âncoras aceitáveis:

- vítima atenderia chamado do zelador porque o consulta sobre acervo;
- funcionário aceitaria abrir sala porque a pessoa tem autoridade;
- suspeito consegue manipular alguém porque há relação familiar;
- alvo segue instrução porque já confiava no remetente;
- “Marta era uma das poucas pessoas que Helena ainda consultava sobre a ala antiga.”

> A revelação deve parecer inevitável depois de vista, não conveniente para o autor.

## Motivação e consequência atual

Motivação histórica precisa ter consequência atual.

Não basta existir carta antiga, trauma herdado ou segredo familiar. A motivação precisa pressionar o presente do caso com impacto concreto, como:

- moradia;
- expulsão;
- dívida moral;
- herança;
- reputação;
- demissão;
- perda concreta;
- risco público.

Sem consequência atual, a motivação vira lore e não objetivo investigativo.

## Informação nova em recados e bilhetes

Se um personagem já sabe uma informação, qualquer recado, bilhete, e-mail ou mensagem posterior precisa trazer algo novo.

A novidade pode ser:

- documento omitido;
- versão original;
- lista não repassada;
- prova concreta;
- risco imediato;
- mudança de prazo;
- pressão nova.

Não use mensagem posterior apenas para repetir ao jogador algo que o destinatário já saberia. Isso quebra a diegese e vira voz do autor.

## Linguagem permitida em documentos do jogador

Preferir linguagem diegética, administrativa, documental ou narrativa.

Exemplos aceitáveis:

```text
Contrato CAM-APC-44/26 vinculado à OS 0147/2026.
```

```text
Representante administrativo: Otávio Salles.
```

```text
Validade da proposta: 5 dias corridos a partir da emissão.
```

```text
Transporte condicionado à janela operacional disponibilizada pela contratante.
```

```text
Registro de acesso P-04 às 19h57.
```

Essas frases apresentam fatos, não conclusões.

## Linguagem proibida em documentos do jogador

Evitar frases que ensinem o jogador a resolver, indiquem quais documentos cruzar ou antecipem conclusão.

Exemplos a bloquear/revisar:

```text
A confirmação depende de recibo, extrato e conversa interna.
```

```text
Compare este contrato com o extrato.
```

```text
O preço isolado não decide a suspeita.
```

```text
Este documento prova que Otávio criou a cobertura.
```

```text
Sem o recibo e o extrato, este e-mail não basta para definir benefício.
```

```text
A decisão precisa citar escopo e prazo, não só valor.
```

```text
O quadro comparativo mostra qual fornecedor realmente importa.
```

## Voz do autor

Evitar qualquer frase que pareça escrita por quem desenhou o puzzle, e não por alguém do mundo ficcional.

Sinais de voz do autor:

- “compare com”;
- “cruze com”;
- “confirma que”;
- “não prova sozinho”;
- “não decide isoladamente”;
- “a solução depende de”;
- “red herring”;
- “ruído controlado”;
- “hipótese”;
- “autoria”;
- “gabarito”;
- referência direta a documentos como `E1-04`, `E2-02` dentro de material diegético.

Esses termos podem existir em:

- guia do facilitador;
- dicas contextuais;
- QA report;
- graph report;
- contratos de evidência;
- metadados internos;
- testes.

Não devem aparecer em documentos de jogador.

## Dificuldade e exposição de informação

### Iniciante

Pode ser mais claro e didático por estrutura.

Exemplos aceitáveis:

```text
P-04 — Doca de serviço
```

```text
USR-022 — Marina Vale — Curadoria operacional
```

Mas ainda não deve explicar a conclusão:

```text
P-04 mostra a rota usada pela carga.
```

### Intermediário

Preferir códigos brutos e tradução em documento separado.

Exemplos:

```text
P-04
USR-022
TERM-ADM-03
```

O jogador deve cruzar com mapa, relação de credenciais ou manual interno.

### Avançado ou superior

Usar códigos brutos, tradução parcial e mais inferência.

A progressão deve vir de cadeia lógica, não de texto explicativo.

## Mapas

Mapa do jogador deve ser planta baixa neutra.

Deve conter:

- ambientes;
- paredes;
- portas;
- janelas;
- câmeras neutras;
- nomes de ambientes;
- códigos de portas;
- norte e escala, se discretos.

Não deve conter:

- rota provável;
- seta da peça;
- destaque de área crítica;
- câmera offline;
- X vermelho;
- campo de visão;
- legenda explicativa de solução;
- cores fortes indicando suspeita;
- texto que explique por que ninguém viu ou por onde a peça saiu.

Se for útil ter uma versão analítica do mapa, ela deve ficar no guia do facilitador ou em material interno, nunca no envelope do jogador.

## Assinaturas e rubricas

Assinatura/rubrica é característica editorial do personagem.

Direção atual:

- cada personagem pode ter perfil de assinatura no blueprint;
- o renderer gera SVG a partir desse perfil;
- override SVG manual é permitido;
- fallback procedural existe para compatibilidade;
- documentos formais usam assinatura completa;
- registros rápidos podem usar rubrica/visto.

Evitar:

- nome digitado fingindo assinatura;
- todas as assinaturas com mesma estrutura visual;
- rubrica escrita literalmente como “rubrica”;
- assinatura genérica igual para personagens diferentes.

## E-mails, chats e conversas

Conversas devem sugerir, não confessar.

Bom chat investigativo:

- tem ruído controlado;
- cita termos operacionais;
- mostra tensão ou urgência;
- não lista documentos necessários;
- não explica a conclusão.

Evitar:

```text
Confiram etiqueta, recibo e extrato antes de responder.
```

Preferir algo diegético:

```text
Deixa os anexos na pasta da OS. Amanhã a diretoria confere o fechamento.
```

## Documentos comerciais

Orçamento deve ser orçamento de uma empresa.

Evitar colocar várias empresas dentro de um único orçamento.

Melhor estrutura:

- uma proposta/orçamento por empresa;
- contrato separado quando houver contratação;
- recibo separado quando houver pagamento;
- extrato separado quando houver movimentação financeira;
- e-mail/chat como evidência contextual.

Evitar quadro comparativo entregue ao jogador quando ele facilitar demais a solução.

Se houver comparativo interno, ele deve ser usado com cuidado e nunca deve funcionar como folha de resposta.

## Dicas contextuais

Dicas são permitidas, mas devem ficar separadas dos documentos do jogador.

Devem destravar o grupo, não substituir a investigação.

Cada dica deve indicar:

- condição de uso;
- intensidade;
- ação mental esperada;
- o que desbloqueia.

Dicas podem orientar cruzamento, desde que não entreguem a resposta final.

Exemplo aceitável:

```text
Voltem ao documento que registra a movimentação e observem se o horário conversa com a escala.
```

Exemplo forte demais:

```text
Compare E1-04, E1-06 e E2-04 para descobrir Marina e Otávio.
```

## Guia do facilitador

O guia do facilitador deve ser operacional, não apenas um gabarito final.

Ele deve conter:

- pergunta pública;
- resposta esperada por envelope;
- quando liberar o próximo envelope;
- linha do tempo aparente;
- linha do tempo real;
- red herrings e descartes;
- explicação da motivação;
- solução em síntese.

O guia pode explicar cruzamentos, citar códigos de documentos e usar linguagem analítica. Essa linguagem não deve aparecer em documentos de jogador.

## Guardrail automático implementado

O guardrail anti-obviedade está implementado em `generator/obviousness_checker.py` e documentado em `docs/ANTI_OBVIEDADE.md`.

O checker é integrado ao validator strict e emite achados editoriais com códigos `OBV_001` a `OBV_012`. Esses códigos cobrem as regras oficiais de obviedade para documentos de jogador, incluindo:

- uso de nomes em logs, sistemas ou escalas de casos Intermediário+ quando códigos operacionais seriam mais adequados;
- nome de culpado junto de verbo incriminador e contexto crítico;
- confissões em primeira pessoa;
- `objetivo_narrativo` com culpado e ação incriminadora;
- E1 antecipando solução, gabarito, confissão ou culpado revelado;
- linguagem conclusiva em conteúdo de jogador;
- chat confessional ou explicativo demais;
- depoimento onisciente sobre autoria, intenção ou plano de terceiros;
- documento único resolvendo quem, como, por quê e benefício;
- vazamento de campos internos ou rótulos de gabarito em `conteudo`;
- referência instrucional a códigos de documentos em conteúdo diegético;
- linguagem de facilitador/designer em documento de jogador.

Não invente novos códigos neste documento. Para severidades, exemplos e critérios detalhados, use `docs/ANTI_OBVIEDADE.md` como documentação oficial do guardrail.

## Checklist editorial antes de gerar PDF

Antes de considerar um caso pronto para playtest, revisar:

1. Existe pergunta pública clara com solicitante, motivo, impacto e justificativa do dossiê?
2. Cada envelope tem pergunta diegética, resposta esperada, critério de avanço e forma diegética de avanço?
3. Cada envelope oferece ferramenta investigativa prática para chegar à conclusão esperada?
4. Ausências relevantes ficam visíveis sem serem explicadas em documento de jogador?
5. Evidências diretas, indiretas e sistêmicas estão separadas no plano editorial?
6. A solução tem mecanismo causal ancorado em documentos?
7. Relações necessárias de confiança, autoridade ou hábito têm âncora documental?
8. O E1 evita pedir a solução final?
9. O E2 recontextualiza algo do E1?
10. Toda motivação histórica tem consequência atual concreta?
11. Recados posteriores trazem informação nova?
12. Cada dica contextual tem condição de uso, intensidade, ação mental esperada e desbloqueio?
13. O guia do facilitador explica progressão, linhas do tempo, descartes, motivação e solução?
14. Algum documento de jogador manda comparar documentos?
15. Algum documento cita `E1-XX` ou `E2-XX` dentro da diegese?
16. Algum documento explica a conclusão?
17. Algum mapa mostra rota, área crítica ou câmera offline?
18. Algum chat parece confissão?
19. Algum orçamento funciona como quadro comparativo de solução?
20. Alguma assinatura parece só nome digitado?
21. Alguma dica aparece dentro de documento que deveria ser evidência?
22. O guia do facilitador está separado dos documentos de jogador?
23. O gabarito não vazou para envelope, mapa, chat ou proposta?

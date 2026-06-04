# Diretrizes editoriais do Indiciário

Este documento consolida decisões editoriais usadas para criar e revisar casos investigativos no Indiciário.

## Regra principal

Documento de jogador deve conter evidência bruta, não interpretação do autor.

Separação de papéis:

- **documento do jogador** mostra o que aconteceu ou o que existe no mundo da história;
- **guia do facilitador** explica o que significa;
- **dica contextual** orienta quando o grupo trava;
- **gabarito** resolve;
- **metadados internos** podem usar linguagem analítica, mas não devem vazar para PDFs do jogador.

Nenhum documento de jogador deve soar como checklist de solução.

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

Dicas podem orientar cruzamento, desde que não entreguem a resposta final.

Exemplo aceitável:

```text
Voltem ao documento que registra a movimentação e observem se o horário conversa com a escala.
```

Exemplo forte demais:

```text
Compare E1-04, E1-06 e E2-04 para descobrir Marina e Otávio.
```

## Futuro guardrail automático

Ainda não implementado, mas recomendado.

Objetivo futuro:

- criar um validador de conteúdo voltado ao jogador;
- bloquear “handholding” óbvio;
- detectar voz do autor;
- detectar checklist de solução;
- gerar erros/warnings como `HAND_001`, `HAND_002`, etc.

Possíveis regras:

- bloquear referência a documentos por código em conteúdo diegético;
- bloquear listas do tipo “recibo, extrato e conversa interna”;
- bloquear “compare/cruze/confira com” em documentos de jogador;
- bloquear “não prova sozinho”, “preço isolado não decide”, “confirma que”;
- gerar score de vazamento quando pessoa + ação + motivo + horário aparecem na mesma frase.

Esse guardrail deve fazer parte do `--strict` no futuro, mas ainda não é prioridade imediata antes do playtest.

## Checklist editorial antes de gerar PDF

Antes de considerar um caso pronto para playtest, revisar:

1. Algum documento de jogador manda comparar documentos?
2. Algum documento cita `E1-XX` ou `E2-XX` dentro da diegese?
3. Algum documento explica a conclusão?
4. Algum mapa mostra rota, área crítica ou câmera offline?
5. Algum chat parece confissão?
6. Algum orçamento funciona como quadro comparativo de solução?
7. Alguma assinatura parece só nome digitado?
8. Alguma dica aparece dentro de documento que deveria ser evidência?
9. O guia do facilitador está separado dos documentos de jogador?
10. O gabarito não vazou para envelope, mapa, chat ou proposta?

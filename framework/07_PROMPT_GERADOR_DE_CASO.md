# Prompt Gerador de Novo Caso

Cole este prompt em uma nova conversa para gerar um caso completo.
Preencha as variáveis entre colchetes antes de enviar.

---

```
Você é um designer sênior de jogos de investigação offline, especializado em dossiês físicos com documentos verossímeis, pistas cruzadas, red herrings justos e solvabilidade rigorosa.

Crie um caso original de investigação 100% [MODO: offline puro / híbrido com QR], em formato de dossiê com [NÚMERO: 2 / 3] envelopes. O caso deve ser completamente original — sem copiar nomes, personagens, textos, layout ou solução de nenhum caso existente.

---

## PARÂMETROS DO CASO

Tema: [INSIRA — ex.: fraude em fintech, roubo em museu, sabotagem em startup, morte em pousada, disputa de herança]
Tom: [INSIRA — ex.: corporativo, policial, familiar, noir, leve]
Dificuldade: [Fácil / Médio / Médio-alto / Difícil]
Número de jogadores: [INSIRA]
Tempo estimado: [INSIRA]
Observações de produção: [ex.: legível em celular, preto e branco, colorido]

---

## PRINCÍPIOS OBRIGATÓRIOS

Siga rigorosamente todos os princípios abaixo. Violar qualquer um invalida o caso.

1. JUSTO: o jogador resolve usando somente os materiais entregues. Nenhuma resposta essencial depende de internet, QR como pista, busca externa ou suposição não documentada.

2. PROGRESSIVO: cada envelope tem uma pergunta própria. O E1 encontra o suspeito operacional. O E2 revela a cadeia completa. O E2 amplifica o E1 — nunca o invalida.

3. CRUZAMENTOS: cada conclusão crítica tem pelo menos duas confirmações independentes. Confirmação forte = outro documento prova o mesmo fato de fonte diferente. Confirmação fraca = outro documento é compatível mas não prova diretamente. Pistas essenciais precisam de pelo menos uma confirmação forte.

4. RED HERRINGS JUSTOS: cada falso suspeito tem motivo para parecer culpado E forma documental de ser descartado. Nenhum red herring tem os quatro pilares preenchidos.

5. CADEIA CAUSAL: a solução responde o quê, quando, quem executou, quem planejou, como foi possível, como ocultou e qual prova confirma cada etapa.

6. SEPARAÇÃO: material do jogador, dicas e gabarito são arquivos separados. Nenhum gabarito no material do jogador.

7. AUTOSSUFICIENTE: em modo offline puro, nada essencial depende de canal digital. Em modo híbrido, o canal digital só valida hipóteses — não revela pistas.

8. CURVA EMOCIONAL: cada documento tem emoção definida. Sequência: urgência → suspeita → frustração produtiva → satisfação de cruzamento → surpresa justa.

---

## REGRAS TÉCNICAS OBRIGATÓRIAS

- O narrador inicial do E1 é personagem com interesse próprio — não neutro.
- O E1 tem exatamente quatro pilares de validação, cada um com documento principal e confirmação.
- Todo ID em código, log ou cartão existe na matriz de personagens.
- IDs internos e de terceirizados seguem padrões numéricos distintos.
- Toda entidade em extrato financeiro tem âncora em outro documento.
- Todo vínculo entre entidades tem pelo menos duas âncoras documentais.
- Cada salto de cadeia financeira ou logística tem documento próprio.
- O salto final tem duas confirmações independentes.
- A escala de turnos tem legenda de nomes no mesmo documento.
- A contagem de documentos no protocolo bate com a contagem real.
- O período do log cobre o intervalo crítico com margem.
- Nenhuma pista essencial depende exclusivamente de cor.

---

## GATE DE QUALIDADE — OBRIGATÓRIO ANTES DOS DOCUMENTOS FINAIS

Antes de gerar qualquer texto de documento final, execute internamente o checklist abaixo. Se qualquer item falhar, corrija o planejamento e informe o que foi corrigido.

- [ ] Toda conclusão crítica tem pelo menos duas pistas independentes.
- [ ] Toda pista essencial tem pelo menos uma confirmação forte.
- [ ] Todo vínculo entre entidades tem âncora em pelo menos dois documentos diferentes.
- [ ] Toda cadeia financeira ou logística tem cada salto documentado.
- [ ] O salto final até o beneficiário tem duas confirmações independentes.
- [ ] Todo personagem do elenco aparece em pelo menos um documento planejado.
- [ ] Todo personagem suspeito relevante aparece na folha de cruzamento.
- [ ] Todo red herring tem forma justa de descarte documentada.
- [ ] As dicas cobrem todos os pontos de travamento identificados.
- [ ] O risco de solvabilidade avaliado é Médio-baixo ou Baixo.

Se o risco for Médio ou superior: sinalize explicitamente, corrija o blueprint e não gere documentos finais ainda.

---

## ENTREGÁVEIS — NESTA ORDEM

### Fase 1 — Blueprint (planejamento interno)

Entregue em Markdown com estas seções exatas:

1. Identidade do caso (título, subtítulo, gênero, tom, modo, dificuldade, tempo, jogadores)
2. Premissa (o que parece ter acontecido — versão do jogador)
3. Verdade real [INTERNO] (o que realmente aconteceu, executor, planejador, beneficiário, motivação, ocultação, erro que permite descobrir, cadeia causal)
4. Elenco completo com IDs, funções, papéis e documentos de ancoragem
5. Linha do tempo real (Linha A)
6. Linha do tempo percebida (Linha B)
7. Linha do tempo documental (Linha C)
8. Estrutura do Envelope 1 (tabela de documentos com tipo e emoção, quatro pilares, critério de avanço)
9. Estrutura do Envelope 2 (tabela de documentos com tipo e emoção, perguntas respondidas)
10. Estrutura do Envelope 3, se houver
11. Matriz de pistas (pista, documento, o que sugere, o que prova, confirmação, risco, emoção)
12. Red herrings (falso suspeito, motivo aparente, descarte, documento de descarte, categoria)
13. Cadeias financeiras ou logísticas (tabela de saltos com documentação)
14. Planejamento de dicas (tabela: nº, intensidade, envelope, condição, texto resumido, o que desbloqueia)
15. Gabarito resumido (resposta curta, papéis, provas principais, por que falsos suspeitos são falsos)
16. Checklist de solvabilidade preenchido com rubrica de risco

### Fase 2 — Documentos finais (somente após gate de qualidade aprovado)

Para cada documento, use este formato:

---
**[CÓDIGO DO DOCUMENTO] — [TÍTULO]**
Envelope: [1 / 2 / 3]
Tipo: [tipo do catálogo]
Destino: Material do jogador / Dica / Gabarito / Facilitador
Emoção esperada: [emoção]

[Conteúdo completo pronto para diagramação]

---

Regras de formato por tipo de documento:

- E-mail: incluir De / Para / Data / Assunto / corpo / lista de anexos com tamanhos fictícios
- Chat: incluir nome do grupo, horários por mensagem, identificação de remetente
- Log de acesso: tabela com DATA / HORA / PORTA / ID / SENTIDO, cabeçalho com período exportado
- Log de sistema: tabela com HORA / OBJETO / EVENTO / USUÁRIO / TERMINAL / JUSTIFICATIVA
- Escala: tabela de letras por dia + legenda de nomes no mesmo documento
- Mapa: descrição textual detalhada das salas, portas numeradas, câmeras, sentido de acesso, legenda
- Manual: título + revisão + data + assinatura + seções de regra normal / exceção / sanção
- Contrato: partes + CNPJ fictício + objeto + data anterior ao crime + cláusula relevante + assinaturas
- Boletim policial: número do caso + tipo + localização + data + corpo em tom manuscrito + assinatura
- Depoimento: número do caso + nome + data nasc. + marcação vítima/suspeito + corpo em 1ª pessoa + assinaturas
- Cartão: frente (código + frase) e verso (identidade + frase com duplo sentido) + instrução de corte
- Cadastro de terceiros: bloco por fornecedor + tabela de funcionários com IDs

Não inclua notas do autor dentro dos documentos do jogador.

### Fase 3 — Dicas progressivas

Use o formato do `10_TEMPLATE_DICAS.md`:
- número, intensidade, envelope, condição de uso, texto da dica, o que desbloqueia
- dicas leves e médias não revelam nomes diretamente
- cada dica desbloqueia uma ação concreta

### Fase 4 — Gabarito do mestre

Use o formato do `09_TEMPLATE_GABARITO.md`:
- resposta curta
- papéis (executor, planejador, beneficiário, cúmplice)
- linha do tempo completa
- explicação por envelope
- mapa de pistas por documento
- red herrings e descarte
- pontos de travamento e dicas recomendadas
- respostas erradas esperadas
- fechamento narrativo

---

## PADRÃO DE QUALIDADE FINAL

O caso só está pronto se:

1. A resposta pode ser **defendida com documentos**, não com intuição.
2. A solução parece **inevitável depois de explicada**, mas não óbvia durante a investigação.
3. Não existe nenhum ponto em que o jogador só descobriria porque o autor explicou.
4. Cada falso suspeito pode ser descartado por prova documental.
5. A cadeia do beneficiário está fechada com duas confirmações independentes.

Antes de finalizar, revise explicitamente se existe algum ponto fraco. Se existir, corrija antes de entregar.
```

---

## Variáveis de preenchimento rápido

| Variável | Opções |
|----------|--------|
| MODO | `offline puro` / `híbrido com QR` |
| NÚMERO | `2` / `3` |
| Tema | fraude em fintech · roubo em museu · sabotagem em startup · morte em pousada · disputa de herança · roubo em evento · golpe em lotérica · fraude de seguro · sumiço de item raro · crime logístico |
| Tom | corporativo · policial · familiar · noir · leve · tecnológico · museológico |
| Dificuldade | Fácil · Médio · Médio-alto · Difícil |

---

## Exemplos de premissa por tema

**Fraude em fintech:**
> Na manhã de segunda-feira, a fintech descobre que seis empresas recém-cadastradas receberam crédito PJ emergencial fora da política. O lote somou R$ 684.000 aprovados durante a madrugada, usando um mecanismo de contingência que ninguém admite ter ativado.

**Roubo em museu:**
> Um quadro avaliado em R$ 5 milhões desaparece durante uma manutenção programada que deixou as câmeras offline por 45 minutos. O museu estava fechado ao público — apenas funcionários e quatro fornecedores tinham acesso.

**Sabotagem em startup:**
> Na véspera do pitch para o maior fundo de investimento da América Latina, o sistema de demonstração da startup falha completamente. Os logs mostram uma alteração feita às 2h da manhã por um usuário com credencial válida.

**Morte suspeita em pousada:**
> O hóspede do quarto 7 é encontrado inconsciente na manhã de domingo. A polícia trata como acidente, mas o gerente contratou uma investigação privada: três pessoas tinham motivo, duas tinham acesso ao quarto e uma está mentindo sobre onde estava.

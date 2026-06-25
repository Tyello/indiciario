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
- [ ] Todo red herring tem documento de descarte E uma pista na matriz que aponta esse documento; sem isso, há ER_006.
- [ ] Cada um dos 4 pilares do E1 tem pelo menos 1 pista que o sustenta na matriz; sem isso, há ER_002.
- [ ] Todo contrato `obrigatoria_para_avanco: true` tem `prova_principal` no envelope atual; no gate E1→E2, a prova está em E1.
- [ ] Revelação ou solução do E2 está modelada como contrato E2/final NÃO obrigatório-para-avanço; sem isso, há ER_007.
- [ ] Nenhum documento isolado responde sozinho quem + como + por quê + benefício; a descoberta é distribuída; sem isso, há OBV_009.
- [ ] Suspeitos ficam dentro do recomendado para o nível em `docs/DIFFICULTY_FRAMEWORK.md`; Intermediário tem limite recomendado de até 6. Excesso gera PT_003 e deriva de dificuldade.
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
11. Matriz de pistas (pista, documento, o que sugere, o que prova, confirmação, risco, emoção). Inclua pelo menos 1 pista para cada pilar do E1 e uma pista para cada documento de descarte de red herring.
12. Red herrings (falso suspeito, motivo aparente, descarte, documento de descarte, pista da matriz que aponta esse descarte, categoria)
13. Cadeias financeiras ou logísticas (tabela de saltos com documentação)
14. Planejamento de dicas (tabela: nº, intensidade, envelope, condição, texto resumido, o que desbloqueia)
15. Gabarito resumido (resposta curta, papéis, provas principais, por que falsos suspeitos são falsos)
16. Contratos de evidência, marcando `obrigatoria_para_avanco` apenas quando a `prova_principal` estiver no envelope atual; revelação/solução do E2 entra como contrato E2/final não obrigatório-para-avanço.
17. Checklist de solvabilidade preenchido com rubrica de risco, OBV_009, PT_003, ER_002, ER_006 e ER_007 verificados

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

## Campo `conteudo` — OBRIGATÓRIO em cada documento

O campo `conteudo` deve estar presente em **todos** os documentos do blueprint.
Sem ele, o PDF não será gerado.

As chaves do `conteudo` preenchem os placeholders `{{VARIAVEL}}` do template HTML.
Use **exatamente** os nomes abaixo — diferença de maiúsculas ou underscore quebra a renderização.

---

### email_narrador / email_institucional → `01_email.html`

```json
"conteudo": {
  "REMETENTE_NOME":     "Nome do remetente",
  "REMETENTE_EMAIL":    "email@dominio.ficticio",
  "DESTINATARIO_EMAIL": "detetive@indiciarios.com",
  "DESTINATARIO_LABEL": "Investigação Interna",
  "DATA_HORA":          "01 de março de 2026 às 17:05",
  "ASSUNTO":            "Texto do assunto",
  "AVATAR_INICIAL":     "J",
  "AVATAR_COR":         "#1A2E4A",
  "CORPO_EMAIL":        "<p>Parágrafo 1.</p><p>Parágrafo 2.</p>",
  "NOTA_RODAPE":        "CONFIDENCIAL",
  "COPIA":              "",
  "TOTAL_ANEXOS":       "3",
  "ANEXOS":             true,
  "CADA_ANEXO": [
    { "NOME_ARQUIVO": "arquivo.pdf", "TAMANHO_KB": "88" }
  ]
}
```

Regras: `CORPO_EMAIL` deve ser HTML com `<p>`. Se não houver anexos, omitir `CADA_ANEXO` e definir `"ANEXOS": false`.

---

### chat → `02_whatsapp.html`

```json
"conteudo": {
  "HORA_TELA":          "16:57",
  "CONTADOR_NAOVISTOS": "139",
  "NOME_GRUPO":         "[Seg.] Turno da tarde",
  "MEMBROS_LISTA":      "José, Marcello, Márcio, Miguel",
  "DATA_CONVERSA":      "01 mar 2026",
  "MENSAGENS": [
    {
      "DIRECAO":        "in",
      "CLASSE_GAP":     "gap",
      "MOSTRAR_NOME":   true,
      "COR_REMETENTE":  "color-1",
      "NOME_REMETENTE": "Márcio - Museu SP",
      "TEXTO_MENSAGEM": "Texto da mensagem",
      "HORARIO":        "16:40",
      "DIRECAO_OUT":    false,
      "TICKS":          ""
    },
    {
      "DIRECAO":        "out",
      "CLASSE_GAP":     "gap",
      "MOSTRAR_NOME":   false,
      "COR_REMETENTE":  "",
      "NOME_REMETENTE": "",
      "TEXTO_MENSAGEM": "Resposta enviada",
      "HORARIO":        "16:41",
      "DIRECAO_OUT":    true,
      "TICKS":          "✓✓"
    }
  ]
}
```

Regras: `CLASSE_GAP: "gap"` apenas na primeira mensagem de cada remetente consecutivo. `COR_REMETENTE` de `color-1` a `color-6`, um por participante, consistente ao longo de toda a conversa.

---

### boletim / depoimento → `04_boletim.html`

```json
"conteudo": {
  "ORGAO_NOME":             "POLÍCIA CIVIL DO ESTADO",
  "ORGAO_SUBTITULO":        "Delegacia de Crimes Patrimoniais",
  "NUMERO_CASO":            "402FH",
  "TIPO_DOCUMENTO":         "BOLETIM DE INSPEÇÃO INICIAL",
  "TIPO_OCORRENCIA":        "Furto qualificado",
  "DATA":                   "01/03/2026",
  "LOCALIZACAO":            "São Paulo — SP",
  "HORA_OCORRENCIA":        "16h40",
  "DESCRICAO_OCORRENCIA":   "<p>Parágrafo 1.</p><p>Parágrafo 2.</p>",
  "NOME_RESPONSAVEL":       "Bruno Rodrigues Souto",
  "ASSINATURA_RESPONSAVEL": "Bruno R. Souto",
  "ASSINATURA_GLIFO":       "BRS",
  "DATA_HORA_ASSINATURA":   "01/03/2026 18h24",
  "CAMPO_NOME":             false,
  "MOSTRAR_CARIMBO":        true,
  "TEXTO_CARIMBO":          "PRELIMINAR"
}
```

Para depoimento: `"TIPO_DOCUMENTO": "TRANSCRIÇÃO DE DEPOIMENTO"`, `"CAMPO_NOME": true` e incluir `NOME_ENVOLVIDO`, `DATA_NASC`, `CONDICAO` (`"SUSPEITO"` ou `"VÍTIMA"`), `DOCUMENTO_PESSOAL`.

---

### protocolo / carta / manual / glossario / folha_cruzamento / contrato → `05_carta.html`

```json
"conteudo": {
  "NOME_ORGANIZACAO":      "Nome da instituição",
  "SUBTITULO_ORGANIZACAO": "Departamento ou tipo",
  "ENDERECO_LINHA1":       "Endereço fictício, nº 123",
  "ENDERECO_LINHA2":       "",
  "CONTATO":               "contato@ficticio.com",
  "CNPJ":                  "12.345.678/0001-90",
  "COR_TOPO":              "#1A2E4A",
  "ESTILO_LINHAS":         "",
  "LOCAL_DATA":            "São Paulo, 01 de março de 2026",
  "PROTOCOLO":             "REF-2026/001",
  "ASSUNTO":               "Protocolo de Investigação — Envelope 1",
  "SAUDACAO":              "Prezado(a) Investigador(a),",
  "CORPO_CARTA":           "<p>Parágrafo 1.</p><p>Parágrafo 2.</p>",
  "FORMULA_ENCERRAMENTO":  "Atenciosamente,",
  "ASSINATURA_CURSIVA":    "Nome Cursivo",
  "NOME_ASSINANTE":        "Nome Completo",
  "CARGO_ASSINANTE":       "Cargo ou Função",
  "CARIMBO":               false,
  "TEXTO_CARIMBO":         "",
  "ANOTACAO":              "",
  "NOTAS_RODAPE":          ""
}
```

Para `glossario`: `CORPO_CARTA` deve conter tabela HTML `<table>` com colunas Termo e Definição.

Para `folha_cruzamento`: `CORPO_CARTA` deve conter tabelas HTML com células vazias para preenchimento manual.

Para `protocolo`: `ASSUNTO` é obrigatório e deve nomear o objetivo do envelope.

---

### log_acesso / log_sistema / escala → `06_log_acesso.html`

```json
"conteudo": {
  "NOME_SISTEMA":        "CONTROLE DE ACESSOS — MUSEU SP",
  "SUBTITULO_SISTEMA":   "Exportação auditada — uso investigativo",
  "COR_SISTEMA":         "#1A2E4A",
  "COR_SISTEMA_DARK":    "#0d1a2e",
  "DATA_EXPORTACAO":     "01/03/2026",
  "HORA_EXPORTACAO":     "17:04",
  "OPERADOR_EXPORT":     "SISTEMA",
  "HASH_REGISTRO":       "a3f9c1d2",
  "PERIODO_INICIO":      "01/03/2026 09:50",
  "PERIODO_FIM":         "01/03/2026 17:04",
  "LOCALIZACAO_SISTEMA": "Andar 3 — Sala N3",
  "TOTAL_REGISTROS":     "3",
  "COLUNA_NOME":         true,
  "COLUNA_TERMINAL":     false,
  "COLUNA_METODO":       false,
  "COLUNA_OBS":          true,
  "TOTAL_USUARIOS":      "3",
  "TOTAL_ENTRADAS":      "3",
  "TOTAL_NEGADOS":       "0",
  "TOTAL_ANOMALIAS":     "1",
  "REGISTROS": [
    {
      "CLASSE_LINHA":  "",
      "DATA":          "01/03/2026",
      "HORA":          "09:58:02",
      "PORTA":         "1A",
      "ID_USUARIO":    "27",
      "NOME_USUARIO":  "Nome do Personagem",
      "TIPO_EVENTO":   "in",
      "EVENTO":        "ENTRADA",
      "OBSERVACAO":    ""
    },
    {
      "CLASSE_LINHA":  "anomaly",
      "DATA":          "01/03/2026",
      "HORA":          "15:22:11",
      "PORTA":         "4A",
      "ID_USUARIO":    "09",
      "NOME_USUARIO":  "Outro Personagem",
      "TIPO_EVENTO":   "in",
      "EVENTO":        "ENTRADA",
      "OBSERVACAO":    "sem saída correspondente"
    }
  ]
}
```

Regras: `TOTAL_REGISTROS` deve bater com o número de itens em `REGISTROS`. `TIPO_EVENTO` aceita `in`, `out` ou `denied`. `CLASSE_LINHA` aceita `""`, `"anomaly"` (vermelho) ou `"highlight"` (azul). IDs em `ID_USUARIO` devem existir no elenco.

---

### recibo → `07_recibo.html`

```json
"conteudo": {
  "NOME_EMPRESA":           "Razão Social Fictícia",
  "TAGLINE_EMPRESA":        "Tipo de serviço",
  "CNPJ":                   "12.345.678/0001-90",
  "ENDERECO_EMPRESA":       "Rua Fictícia, 100 — SP",
  "CONTATO_EMPRESA":        "contato@ficticio.com",
  "NUMERO_RECIBO":          "0042",
  "WATERMARK_TEXTO":        "RECIBO",
  "COR_EMPRESA":            "#1A2E4A",
  "NOME_CONTRATANTE":       "Museu de São Paulo",
  "ENDERECO_CONTRATANTE":   "Rua das Palmeiras, 410 — SP",
  "DOC_CONTRATANTE":        "12.345.678/0001-90",
  "CONTATO_CONTRATANTE":    "diretoria@msp.ficticio",
  "DATA_RECIBO":            "22/02/2026",
  "PERIODO_REFERENCIA":     "Serviços de fevereiro/2026",
  "VALOR_TOTAL":            "R$ 2.940,00",
  "VALOR_POR_EXTENSO":      "Dois mil, novecentos e quarenta reais",
  "FORMA_PAGAMENTO":        "TRANSFERÊNCIA",
  "DESCRICAO_PAGAMENTO":    "Transferência bancária conforme acordo",
  "ASSINATURA_PRESTADOR":   "Nome Cursivo",
  "ASSINATURA_CONTRATANTE": "",
  "DATA_ASSINATURA":        "22/02/2026",
  "ITENS": [
    {
      "DESCRICAO_ITEM":  "Serviço de pintura e acabamento",
      "QUANTIDADE":      "4",
      "VALOR_UNITARIO":  "R$ 500,00",
      "VALOR_ITEM":      "R$ 2.000,00"
    }
  ]
}
```

---

### orcamento → `08_orcamento.html`

```json
"conteudo": {
  "NOME_EMPRESA":           "TransCargas Brasil",
  "TIPO_EMPRESA":           "Transporte rodoviário especializado",
  "CNPJ":                   "31.313.431/0001-987",
  "ENDERECO":               "Av. Central, 1000 — BH, MG",
  "SITE_EMAIL":             "transcargasbr@ficticio.com",
  "COR_PRIMARIA":           "#E65100",
  "COR_SECUNDARIA":         "#BF360C",
  "NUMERO_ORCAMENTO":       "21321.02",
  "DATA_EMISSAO":           "20/02/2026",
  "DATA_VALIDADE":          "20/03/2026",
  "REVISAO":                "3",
  "NOME_CLIENTE":           "Museu de São Paulo",
  "ENDERECO_CLIENTE":       "Rua das Palmeiras, 410 — SP",
  "DOC_CLIENTE":            "12.345.678/0001-90",
  "CONTATO_CLIENTE":        "diretoria@msp.ficticio",
  "TITULO_PROJETO":         "BID Nº 1023 — Reforma Geral 2026",
  "DESCRICAO_REFERENCIA":   "Movimentação e armazenamento de cargas especiais",
  "VALOR_TOTAL":            "R$ 222.100,00",
  "ESCOPO":                 "Serviços conforme descrito no BID.",
  "CONDICOES": [
    { "CONDICAO": "Preços válidos apenas para dias úteis." },
    { "CONDICAO": "Não prestamos serviços em fins de semana." }
  ],
  "UNIDADES": true,
  "LISTA_UNIDADES": [
    { "UNIDADE": "São Paulo — SP" },
    { "UNIDADE": "Belo Horizonte — MG" }
  ],
  "NOTA_MANUSCRITA": "",
  "ASSINATURA_RESPONSAVEL": "Lucas Malta",
  "NOME_RESPONSAVEL":       "Lucas Malta",
  "CARGO_RESPONSAVEL":      "Gerente Comercial",
  "ASSINATURA_CLIENTE":     "",
  "DATA_APROVACAO":         "",
  "ITENS": [
    {
      "NUMERO_ITEM":      "1",
      "NOME_ITEM":        "Caminhão de Grande Porte",
      "DESC_ITEM":        "Por km rodado",
      "QUANTIDADE":       "1",
      "VALOR_UNITARIO":   "R$ 8,50/km",
      "VALOR_TOTAL_ITEM": "R$ 8.500,00"
    }
  ]
}
```

---

### extrato → `09_extrato.html`

```json
"conteudo": {
  "LOGO_SIGLA":           "BC",
  "NOME_BANCO":           "Banco Confiança",
  "TAGLINE_BANCO":        "Sua segurança em primeiro lugar",
  "COR_BANCO":            "#1A2E4A",
  "PERIODO_INICIO":       "01/08/2026",
  "PERIODO_FIM":          "15/08/2026",
  "DATA_GERACAO":         "15/08/2026",
  "HORA_GERACAO":         "09:14",
  "NOME_TITULAR":         "Nome do Titular",
  "DOC_TITULAR":          "***.456.789-**",
  "AGENCIA":              "0042",
  "NUMERO_CONTA":         "12345-6",
  "TIPO_CONTA":           "Conta Corrente",
  "SALDO_INICIAL":        "R$ 4.230,00",
  "DATA_SALDO_INICIAL":   "01/08/2026",
  "MOVIMENTACAO_LIQUIDA": "- R$ 3.800,00",
  "COR_MOVIMENTACAO":     "negative",
  "SALDO_FINAL":          "R$ 430,00",
  "DATA_SALDO_FINAL":     "15/08/2026",
  "COR_SALDO_FINAL":      "negative",
  "TOTAL_CREDITOS":       "R$ 0,00",
  "TOTAL_DEBITOS":        "R$ 3.800,00",
  "TOTAL_LANCAMENTOS":    "1",
  "NOTA_LEGAL":           "Documento gerado automaticamente — uso investigativo",
  "CNPJ_BANCO":           "00.000.000/0001-00",
  "ENDERECO_BANCO":       "Av. Fictícia, 1000 — São Paulo, SP",
  "LANCAMENTOS": [
    {
      "CLASSE_LINHA":    "flagged",
      "DATA":            "12/08/2026",
      "DESCRICAO":       "PIX ENVIADO",
      "DETALHE":         "Chave: ***.456.789-**",
      "TIPO":            "PIX",
      "TIPO_LOWER":      "pix",
      "DIRECAO":         "debit",
      "VALOR":           "- R$ 3.800,00",
      "COR_SALDO":       "negative",
      "SALDO_ACUMULADO": "R$ 430,00"
    }
  ]
}
```

Regras: `COR_MOVIMENTACAO` e `COR_SALDO_FINAL` aceitam `"positive"`, `"negative"` ou `"neutral"`. `CLASSE_LINHA: "flagged"` para lançamentos suspeitos, com destaque vermelho. `TOTAL_LANCAMENTOS` deve bater com o número de itens.

---

## Checklist antes de entregar o blueprint

Para cada documento, verifique:

* [ ] Campo `conteudo` presente e não vazio.
* [ ] Todas as chaves do tipo estão preenchidas.
* [ ] `CORPO_CARTA` / `CORPO_EMAIL` / `DESCRICAO_OCORRENCIA` usam HTML com `<p>`.
* [ ] Listas (`REGISTROS`, `LANCAMENTOS`, `ITENS`, `MENSAGENS`) têm ao menos 1 item.
* [ ] Totais de string (`TOTAL_REGISTROS`, `TOTAL_LANCAMENTOS`) batem com o tamanho da lista.
* [ ] IDs em `ID_USUARIO` existem no elenco do blueprint.
* [ ] Cores no formato `#RRGGBB`.
* [ ] Datas no formato `DD/MM/AAAA`.
* [ ] Valores monetários no formato `R$ X.XXX,XX`.

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

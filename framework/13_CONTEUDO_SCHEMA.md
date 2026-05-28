# Esquema de `conteudo` por tipo de documento

Este arquivo define **exatamente quais chaves** o campo `conteudo` de cada
documento deve ter. É a fonte da verdade para o LLM gerar blueprints corretos
e para o validador verificar automaticamente.

Cada chave marcada com `*` é **obrigatória** — o PDF não será gerado sem ela.
Chaves sem `*` são opcionais (omita se não se aplicar ao caso).

---

## Tipos e templates

| Tipo no blueprint | Template HTML |
|-------------------|---------------|
| `email_narrador` | `01_email.html` |
| `email_institucional` | `01_email.html` |
| `chat` | `02_whatsapp.html` |
| `boletim` | `04_boletim.html` |
| `depoimento` | `04_boletim.html` |
| `protocolo` | `05_carta.html` |
| `carta` | `05_carta.html` |
| `manual` | `05_carta.html` |
| `glossario` | `05_carta.html` |
| `folha_cruzamento` | `05_carta.html` |
| `contrato` | `05_carta.html` |
| `log_acesso` | `06_log_acesso.html` |
| `log_sistema` | `06_log_acesso.html` |
| `escala` | `06_log_acesso.html` |
| `recibo` | `07_recibo.html` |
| `orcamento` | `08_orcamento.html` |
| `extrato` | `09_extrato.html` |
| `outro` | `05_carta.html` |

---

## 01_email — `email_narrador` / `email_institucional`

```json
"conteudo": {
  "REMETENTE_NOME":     "*  Nome completo do remetente",
  "REMETENTE_EMAIL":    "*  email@dominio.ficticio",
  "DESTINATARIO_EMAIL": "*  detetive@indiciarios.com",
  "DESTINATARIO_LABEL": "*  Label na barra superior, ex: Investigação Interna",
  "DATA_HORA":          "*  01 de março de 2026 às 17:05",
  "ASSUNTO":            "*  Texto do assunto",
  "AVATAR_INICIAL":     "*  Inicial do remetente, ex: H",
  "AVATAR_COR":         "*  Cor hex do avatar, ex: #1A2E4A",
  "CORPO_EMAIL":        "*  HTML do corpo (use <p> para parágrafos)",
  "NOTA_RODAPE":        "*  Nota de rodapé, ex: CONFIDENCIAL",
  "COPIA":              "   Endereço em cópia (omita se não houver)",
  "TOTAL_ANEXOS":       "   Número total de anexos como string, ex: '3'",
  "ANEXOS":             "   true se houver anexos, omita ou false se não houver",
  "CADA_ANEXO": [
    {
      "NOME_ARQUIVO": "nome_do_arquivo.pdf",
      "TAMANHO_KB":   "142"
    }
  ]
}
```

**Regras:**
- `CORPO_EMAIL` deve ser HTML com `<p>` por parágrafo.
- `AVATAR_COR` deve ser cor hex válida compatível com o tema do caso.
- Se `ANEXOS` for `true`, `CADA_ANEXO` é obrigatório.
- `CADA_ANEXO` deve listar exatamente os documentos do mesmo envelope.

---

## 02_whatsapp — `chat`

```json
"conteudo": {
  "HORA_TELA":          "*  Hora exibida na barra de status, ex: 16:57",
  "CONTADOR_NAOVISTOS": "*  Número de mensagens não vistas, ex: 139",
  "NOME_GRUPO":         "*  Nome do grupo, ex: [Seg.] Turno da tarde",
  "MEMBROS_LISTA":      "*  Lista de nomes, ex: José, Marcello, Márcio, Miguel",
  "DATA_CONVERSA":      "*  Data separador, ex: 01 mar 2026",
  "MENSAGENS": [
    {
      "DIRECAO":       "* 'in' para mensagens recebidas, 'out' para enviadas",
      "CLASSE_GAP":    "* 'gap' para primeira mensagem de cada remetente, '' para demais",
      "MOSTRAR_NOME":  "* true para mostrar nome do remetente (apenas mensagens 'in' com 'gap')",
      "COR_REMETENTE": "  classe CSS de cor: color-1 a color-6 (um por participante)",
      "NOME_REMETENTE":"  Nome e contexto, ex: Márcio - Museu SP",
      "TEXTO_MENSAGEM":"* Texto da mensagem",
      "HORARIO":       "* Horário da mensagem, ex: 16:40",
      "DIRECAO_OUT":   "  true apenas para mensagens 'out' (exibe ticks)",
      "TICKS":         "  ✓✓ para entregue, ticks em azul para lido"
    }
  ]
}
```

**Regras:**
- Use `CLASSE_GAP: "gap"` somente na primeira mensagem de cada remetente consecutivo.
- `COR_REMETENTE` deve ser consistente por participante em toda a conversa.
- Mínimo de 4 mensagens, máximo de 20 por documento.

---

## 04_boletim — `boletim` / `depoimento`

```json
"conteudo": {
  "ORGAO_NOME":             "*  POLÍCIA CIVIL DO ESTADO DE SÃO PAULO",
  "ORGAO_SUBTITULO":        "*  Delegacia de Crimes Patrimoniais — 5ª Circunscrição",
  "NUMERO_CASO":            "*  402FH",
  "TIPO_DOCUMENTO":         "*  BOLETIM DE INSPEÇÃO INICIAL  (ou TRANSCRIÇÃO DE DEPOIMENTO)",
  "TIPO_OCORRENCIA":        "*  Furto qualificado",
  "DATA":                   "*  01/03/2026",
  "LOCALIZACAO":            "*  São Paulo — SP",
  "HORA_OCORRENCIA":        "*  16h40",
  "DESCRICAO_OCORRENCIA":   "*  Texto completo em prosa descritiva, tom manuscrito",
  "NOME_RESPONSAVEL":       "*  Nome do delegado ou entrevistador",
  "ASSINATURA_RESPONSAVEL": "*  Nome em cursiva, ex: Bruno Rodrigues Souto",
  "ASSINATURA_GLIFO":       "*  Iniciais, ex: BRS",
  "DATA_HORA_ASSINATURA":   "*  01/03/2026 18h24",
  "CAMPO_NOME":             "   true para incluir bloco de identificação do envolvido",
  "NOME_ENVOLVIDO":         "   Nome completo (apenas se CAMPO_NOME: true)",
  "DATA_NASC":              "   Data de nascimento (apenas se CAMPO_NOME: true)",
  "CONDICAO":               "   VÍTIMA ou SUSPEITO (apenas se CAMPO_NOME: true)",
  "DOCUMENTO_PESSOAL":      "   CPF ou RG (apenas se CAMPO_NOME: true)",
  "MOSTRAR_CARIMBO":        "   true para exibir carimbo (ex: PRELIMINAR, CONFIDENCIAL)",
  "TEXTO_CARIMBO":          "   Texto do carimbo (apenas se MOSTRAR_CARIMBO: true)"
}
```

**Regras:**
- `DESCRICAO_OCORRENCIA` deve estar em prosa contínua, tom formal manuscrito.
- Para depoimento, `CAMPO_NOME` deve ser `true` e `CONDICAO` deve ser `"SUSPEITO"` ou `"VÍTIMA"`.
- `TIPO_DOCUMENTO` deve dizer `"TRANSCRIÇÃO DE DEPOIMENTO"` para depoimentos.

---

## 05_carta — `protocolo` / `carta` / `manual` / `glossario` / `folha_cruzamento` / `contrato`

```json
"conteudo": {
  "NOME_ORGANIZACAO":     "*  Nome da organização ou instituição",
  "SUBTITULO_ORGANIZACAO":"*  Subtítulo ou departamento",
  "ENDERECO_LINHA1":      "*  Endereço fictício linha 1",
  "ENDERECO_LINHA2":      "   Endereço linha 2 (omita se não houver)",
  "CONTATO":              "*  E-mail ou telefone fictício",
  "CNPJ":                 "*  CNPJ fictício no formato XX.XXX.XXX/XXXX-XX",
  "COR_TOPO":             "*  Cor hex da borda superior, ex: #1A2E4A",
  "ESTILO_LINHAS":        "   'lined' para papel pautado, '' para liso",
  "LOCAL_DATA":           "*  São Paulo, 01 de março de 2026",
  "SAUDACAO":             "*  Prezado(a) Investigador(a),",
  "CORPO_CARTA":          "*  HTML do corpo com <p> por parágrafo",
  "FORMULA_ENCERRAMENTO": "*  Atenciosamente, / Cordialmente,",
  "ASSINATURA_CURSIVA":   "*  Nome em cursiva",
  "NOME_ASSINANTE":       "*  Nome completo do assinante",
  "CARGO_ASSINANTE":      "*  Cargo ou função",
  "PROTOCOLO":            "   Referência de protocolo, ex: RH-2026/031",
  "ASSUNTO":              "   Linha de assunto (omita se informal)",
  "ANOTACAO":             "   Texto de anotação manuscrita (omita se não houver)",
  "CARIMBO":              "   true para exibir carimbo",
  "TEXTO_CARIMBO":        "   Texto do carimbo (apenas se CARIMBO: true)",
  "NOTAS_RODAPE":         "   Texto de notas de rodapé (omita se não houver)"
}
```

**Regras:**
- `CORPO_CARTA` deve ser HTML com `<p>` por parágrafo.
- Para `folha_cruzamento`, o corpo deve conter tabelas HTML com células em branco.
- Para `glossario`, o corpo deve conter uma tabela com duas colunas: Termo e Definição.
- Para `protocolo`, `ASSUNTO` é obrigatório e deve nomear o objetivo do envelope.
- `COR_TOPO` deve ser consistente com o tema visual do caso.

---

## 06_log_acesso — `log_acesso` / `log_sistema` / `escala`

```json
"conteudo": {
  "NOME_SISTEMA":        "*  Nome do sistema, ex: CONTROLE DE ACESSOS — MUSEU SP",
  "SUBTITULO_SISTEMA":   "*  Subtítulo, ex: Exportação auditada — uso investigativo",
  "COR_SISTEMA":         "*  Cor hex primária, ex: #1A2E4A",
  "COR_SISTEMA_DARK":    "*  Cor hex escura para gradiente, ex: #0d1a2e",
  "DATA_EXPORTACAO":     "*  01/03/2026",
  "HORA_EXPORTACAO":     "*  17:04",
  "OPERADOR_EXPORT":     "*  Nome ou 'SISTEMA'",
  "HASH_REGISTRO":       "*  Hash fictício curto, ex: a3f9c1d2",
  "PERIODO_INICIO":      "*  01/03/2026 09:50",
  "PERIODO_FIM":         "*  01/03/2026 17:04",
  "LOCALIZACAO_SISTEMA": "*  Localização física ou lógica do sistema",
  "TOTAL_REGISTROS":     "*  Total de linhas na tabela como string",
  "COLUNA_NOME":         "*  true para exibir coluna Nome",
  "COLUNA_TERMINAL":     "*  true para exibir coluna Terminal",
  "COLUNA_METODO":       "*  true para exibir coluna Método",
  "COLUNA_OBS":          "*  true para exibir coluna Observação",
  "TOTAL_USUARIOS":      "*  Usuários únicos como string",
  "TOTAL_ENTRADAS":      "*  Total de entradas como string",
  "TOTAL_NEGADOS":       "*  Total de acessos negados como string",
  "TOTAL_ANOMALIAS":     "*  Total de linhas anomaly como string",
  "REGISTROS": [
    {
      "CLASSE_LINHA":  "* '' para normal, 'anomaly' para linha vermelha, 'highlight' para azul",
      "DATA":          "* 01/03/2026",
      "HORA":          "* 09:58:02",
      "PORTA":         "* Código da porta ou zona, ex: 1A",
      "ID_USUARIO":    "* ID do personagem, ex: 27",
      "EVENTO":        "* ENTRADA ou SAÍDA ou NEGADO ou OPERAÇÃO",
      "TIPO_EVENTO":   "* 'in' / 'out' / 'denied' (usado na classe CSS da célula)",
      "NOME_USUARIO":  "  Nome completo (apenas se COLUNA_NOME: true)",
      "TERMINAL":      "  Terminal, ex: NB-RSK-031 (apenas se COLUNA_TERMINAL: true)",
      "METODO":        "  Método, ex: SMS fallback (apenas se COLUNA_METODO: true)",
      "OBSERVACAO":    "  Nota livre (apenas se COLUNA_OBS: true)"
    }
  ]
}
```

**Regras:**
- O período deve cobrir o intervalo crítico do caso com margem antes e depois.
- Anomalias (`CLASSE_LINHA: "anomaly"`) não devem ter destaque visual prévio — o jogador deve encontrá-las.
- `TOTAL_REGISTROS` deve bater com o número real de itens em `REGISTROS`.
- IDs em `ID_USUARIO` devem existir na matriz de personagens do blueprint.

---

## 07_recibo — `recibo`

```json
"conteudo": {
  "NOME_EMPRESA":          "*  Razão social fictícia",
  "TAGLINE_EMPRESA":       "*  Slogan ou tipo de serviço",
  "CNPJ":                  "*  XX.XXX.XXX/XXXX-XX",
  "ENDERECO_EMPRESA":      "*  Endereço fictício",
  "CONTATO_EMPRESA":       "*  Telefone ou e-mail",
  "NUMERO_RECIBO":         "*  Número sequencial, ex: 0042",
  "WATERMARK_TEXTO":       "*  RECIBO ou PAGO (marca d'água, baixa opacidade)",
  "COR_EMPRESA":           "*  Cor hex primária da empresa, ex: #1A2E4A",
  "NOME_CONTRATANTE":      "*  Nome ou razão social do contratante",
  "ENDERECO_CONTRATANTE":  "*  Endereço do contratante",
  "DOC_CONTRATANTE":       "*  CPF ou CNPJ fictício",
  "CONTATO_CONTRATANTE":   "*  Telefone ou e-mail",
  "DATA_RECIBO":           "*  22/02/2026",
  "PERIODO_REFERENCIA":    "*  Período de referência, ex: Serviços de fevereiro/2026",
  "VALOR_TOTAL":           "*  R$ 2.940,00",
  "VALOR_POR_EXTENSO":     "*  Dois mil, novecentos e quarenta reais",
  "FORMA_PAGAMENTO":       "*  PIX / TRANSFERÊNCIA / DINHEIRO",
  "DESCRICAO_PAGAMENTO":   "*  Descrição complementar do pagamento",
  "ITENS": [
    {
      "DESCRICAO_ITEM":   "* Descrição do item ou serviço",
      "QUANTIDADE":       "* Quantidade como string",
      "VALOR_UNITARIO":   "* R$ 500,00",
      "VALOR_ITEM":       "* R$ 2.000,00"
    }
  ],
  "ASSINATURA_PRESTADOR":   "*  Nome em cursiva",
  "ASSINATURA_CONTRATANTE": "*  Nome em cursiva ou linha em branco",
  "DATA_ASSINATURA":        "*  22/02/2026"
}
```

**Regras:**
- `ITENS` deve ter pelo menos 1 item.
- A soma dos `VALOR_ITEM` deve bater com `VALOR_TOTAL`.

---

## 08_orcamento — `orcamento`

```json
"conteudo": {
  "NOME_EMPRESA":          "*  Razão social fictícia",
  "TIPO_EMPRESA":          "*  Tipo de negócio, ex: Transporte Especializado",
  "CNPJ":                  "*  XX.XXX.XXX/XXXX-XX",
  "ENDERECO":              "*  Endereço fictício",
  "SITE_EMAIL":            "*  Site ou e-mail fictício",
  "COR_PRIMARIA":          "*  Cor hex primária, ex: #1A2E4A",
  "COR_SECUNDARIA":        "*  Cor hex secundária para gradiente",
  "NUMERO_ORCAMENTO":      "*  Número, ex: 21321.02",
  "DATA_EMISSAO":          "*  20/02/2026",
  "DATA_VALIDADE":         "*  20/03/2026",
  "REVISAO":               "*  Revisão, ex: 3",
  "NOME_CLIENTE":          "*  Nome ou razão social do cliente",
  "ENDERECO_CLIENTE":      "*  Endereço",
  "DOC_CLIENTE":           "*  CNPJ ou CPF fictício",
  "CONTATO_CLIENTE":       "*  E-mail ou telefone",
  "TITULO_PROJETO":        "*  Nome do projeto ou BID",
  "DESCRICAO_REFERENCIA":  "*  Descrição da referência",
  "VALOR_TOTAL":           "*  R$ 222.100,00",
  "ITENS": [
    {
      "NUMERO_ITEM":       "* 1",
      "NOME_ITEM":         "* Nome do serviço",
      "DESC_ITEM":         "  Descrição complementar",
      "QUANTIDADE":        "* Quantidade ou equipe",
      "VALOR_UNITARIO":    "* R$ 8.000,00",
      "VALOR_TOTAL_ITEM":  "* R$ 8.000,00"
    }
  ],
  "ASSINATURA_RESPONSAVEL": "*  Nome em cursiva",
  "NOME_RESPONSAVEL":       "*  Nome completo",
  "CARGO_RESPONSAVEL":      "*  Cargo",
  "ESCOPO":                 "   Texto de escopo dos serviços (omita se não houver)",
  "SUBTOTAL":               "   Subtotal antes de descontos",
  "DESCONTO":               "   Valor de desconto",
  "IMPOSTOS":               "   Valor de impostos",
  "CONDICOES": [
    { "CONDICAO": "Texto da condição" }
  ],
  "UNIDADES": true,
  "LISTA_UNIDADES": [
    { "UNIDADE": "São Paulo — SP" }
  ],
  "NOTA_MANUSCRITA":        "   Anotação manuscrita no rodapé",
  "ASSINATURA_CLIENTE":     "   Assinatura do cliente (omita se não aprovado)",
  "DATA_APROVACAO":         "   Data de aprovação do cliente"
}
```

---

## 09_extrato — `extrato`

```json
"conteudo": {
  "LOGO_SIGLA":          "*  Sigla do banco, ex: BC",
  "NOME_BANCO":          "*  Nome fictício do banco",
  "TAGLINE_BANCO":       "*  Slogan",
  "COR_BANCO":           "*  Cor hex, ex: #1A2E4A",
  "PERIODO_INICIO":      "*  01/08/2026",
  "PERIODO_FIM":         "*  15/08/2026",
  "DATA_GERACAO":        "*  15/08/2026",
  "HORA_GERACAO":        "*  09:14",
  "NOME_TITULAR":        "*  Nome completo ou razão social",
  "DOC_TITULAR":         "*  CPF ou CNPJ com dígitos centrais mascarados",
  "AGENCIA":             "*  0042",
  "NUMERO_CONTA":        "*  12345-6",
  "TIPO_CONTA":          "*  Conta Corrente / Conta Poupança",
  "SALDO_INICIAL":       "*  R$ 4.230,00",
  "DATA_SALDO_INICIAL":  "*  01/08/2026",
  "MOVIMENTACAO_LIQUIDA":"*  + R$ X,XX  ou  - R$ X,XX",
  "COR_MOVIMENTACAO":    "*  'positive' para positivo, 'negative' para negativo",
  "SALDO_FINAL":         "*  R$ 430,00",
  "DATA_SALDO_FINAL":    "*  15/08/2026",
  "COR_SALDO_FINAL":     "*  'positive' ou 'negative' ou 'neutral'",
  "TOTAL_CREDITOS":      "*  R$ 0,00",
  "TOTAL_DEBITOS":       "*  R$ 3.800,00",
  "TOTAL_LANCAMENTOS":   "*  '1'",
  "NOTA_LEGAL":          "*  Documento gerado automaticamente — uso investigativo",
  "CNPJ_BANCO":          "*  XX.XXX.XXX/XXXX-XX",
  "ENDERECO_BANCO":      "*  Av. Fictícia, 1000 — São Paulo, SP",
  "LANCAMENTOS": [
    {
      "CLASSE_LINHA":     "* '' para normal, 'flagged' para linha suspeita em vermelho",
      "DATA":             "* 12/08/2026",
      "DESCRICAO":        "* PIX ENVIADO",
      "DETALHE":          "* Chave ou detalhes, ex: CPF 000.000.000-00",
      "TIPO":             "* PIX / TED / DOC / DEB / DEP",
      "TIPO_LOWER":       "* pix / ted / doc / deb / dep (versão minúscula para CSS)",
      "DIRECAO":          "* 'debit' para débito, 'credit' para crédito",
      "VALOR":            "* - R$ 3.800,00",
      "COR_SALDO":        "* 'negative' ou 'positive'",
      "SALDO_ACUMULADO":  "* R$ 430,00"
    }
  ]
}
```

**Regras:**
- Lançamentos suspeitos usam `CLASSE_LINHA: "flagged"` — não destacar no resumo nem no gabarito.
- `TOTAL_LANCAMENTOS` deve bater com o número de itens em `LANCAMENTOS`.
- Mascarar dados sensíveis: CPF com `***.***`.

---

## Checklist para o LLM antes de finalizar o `conteudo`

Para cada documento, verificar:

- [ ] Todas as chaves marcadas com `*` estão presentes.
- [ ] `CORPO_CARTA` ou `CORPO_EMAIL` é HTML com `<p>` — não texto simples.
- [ ] Listas (`REGISTROS`, `LANCAMENTOS`, `ITENS`, `MENSAGENS`) têm pelo menos 1 item.
- [ ] Totais numéricos como string batem com o número real de itens.
- [ ] IDs em `ID_USUARIO` existem no elenco do blueprint.
- [ ] Cores hex estão no formato `#RRGGBB`.
- [ ] Datas estão no formato brasileiro `DD/MM/AAAA`.
- [ ] Valores monetários usam formato `R$ X.XXX,XX`.

# Guia de Produção Visual e Impressão

O objetivo visual não é impressionar — é iludir. Cada documento deve parecer que existia antes do jogo existir.

---

## 1. Princípio central

**Sinais de que um documento está errado:**
- parece apresentação de PowerPoint;
- usa gradientes desnecessários;
- tem ícones decorativos sem função;
- tipografia bonita demais para o contexto;
- todas as páginas têm o mesmo estilo visual.

**Sinais de que um documento está certo:**
- o jogador tenta descobrir se é real antes de ler o conteúdo;
- a fonte parece escolhida por burocracia, não por design;
- há imperfeições propositais (assinatura manuscrita, carimbo torto, campo em branco);
- parece que alguém imprimiu, preencheu e escaneou.

---

## 2. Paletas de cores por universo temático

### Corporativo / Fintech / Tecnologia

| Nome | Hex | Uso |
|------|-----|-----|
| Azul institucional | `#1A2E4A` | Cabeçalhos, logos fictícios |
| Cinza médio | `#6B7280` | Texto secundário |
| Cinza claro | `#F3F4F6` | Fundo de tabelas alternadas |
| Vermelho de alerta | `#DC2626` | Carimbos PENDENTE, EXCEÇÃO, SUSPEITO |
| Branco | `#FFFFFF` | Fundo principal |
| Preto | `#111827` | Corpo de texto |

### Museu / Cultural / Arte

| Nome | Hex | Uso |
|------|-----|-----|
| Vermelho escuro | `#8B1A1A` | Cabeçalhos institucionais, logo do museu |
| Creme | `#F5F0E8` | Fundo de documentos formais |
| Marrom escuro | `#3D2B1F` | Texto de diplomas e documentos históricos |
| Dourado discreto | `#B8960C` | Detalhes decorativos, selos |
| Cinza quente | `#9CA3AF` | Legendas, rodapés |
| Branco | `#FFFFFF` | Fundo de documentos modernos |

### Policial / Criminal

| Nome | Hex | Uso |
|------|-----|-----|
| Amarelo desbotado | `#FEFCE8` | Fundo de boletins |
| Verde desbotado | `#F0FDF4` | Fundo de transcrições de depoimento |
| Azul oficial | `#1E3A5F` | Brasão, cabeçalho de órgão |
| Cinza grafite | `#374151` | Texto de relatório |
| Vermelho carimbo | `#B91C1C` | Carimbos, marcações urgentes |

### Familiar / Doméstico

| Nome | Hex | Uso |
|------|-----|-----|
| Bege claro | `#FEF9EF` | Cartas manuscritas |
| Azul pastel | `#DBEAFE` | Post-its, bilhetes |
| Verde suave | `#DCFCE7` | Anotações pessoais |

---

## 3. Tipografia por tipo de documento

Todas as fontes abaixo são gratuitas no Google Fonts.

| Contexto | Fonte principal | Alternativa | Uso |
|----------|----------------|-------------|-----|
| Corpo institucional | `Source Serif 4` | `Merriweather` | Contratos, relatórios, políticas |
| Interface digital simulada | `Inter` | `DM Sans` | E-mails, prints de sistema |
| Logs e registros técnicos | `JetBrains Mono` | `Courier New` | Logs de acesso, registros |
| Manuscrito / cursivo | `Caveat` | `Patrick Hand` | Assinaturas, anotações, depoimentos |
| Títulos institucionais | `Playfair Display` | `Libre Baskerville` | Museu, jurídico, corporativo clássico |
| Documentos informais | `Nunito` | `Poppins` | Orçamentos simples, recibos |
| Títulos de capa / envelope | `Bebas Neue` | `Oswald` | Capas, protocolos |

### Tamanhos mínimos

| Elemento | Impressão | Tela (celular) |
|----------|-----------|---------------|
| Corpo de texto | 11pt | 13pt |
| Tabelas | 10pt | 11pt |
| Rodapés e notas | 8pt | 10pt |
| Títulos de seção | 14pt | 15pt |
| Número de protocolo | 11pt | 12pt |

---

## 4. Templates de layout por tipo de documento

### Capa de envelope

```
┌─────────────────────────────────────────┐
│                           [ENVELOPE #N] │
│                                         │
│                                         │
│         [ÍCONE CENTRAL GRANDE]          │
│         (chapéu, lupa, símbolo)         │
│                                         │
│                                         │
│    ┌─────────────────────────────┐      │
│    │   NOME DO CASO / SÉRIE      │      │
│    └─────────────────────────────┘      │
│                                         │
│    ┌─────────────────────────────┐      │
│    │   SUBTÍTULO / TEMA          │      │
│    └─────────────────────────────┘      │
│                                         │
│              site ou URL                │
└─────────────────────────────────────────┘
```

**Specs:**
- Fundo: textura kraft `#C4A882` ou cor sólida escura
- Ícone: silhueta simples, alto contraste, preto sobre kraft
- Nome do caso: Bebas Neue bold, fundo vermelho escuro ou acento
- Tag `ENVELOPE #N`: canto superior direito, fundo vermelho, texto branco

---

### Protocolo de investigação

```
┌─────────────────────────────────────────┐
│  Protocolo da investigação              │
│  ─────────────────────────────────────  │
│  ┌──┐  Analise as evidências            │
│  │██│  Texto descritivo...              │
│  └──┘                                   │
│  ┌──┐  Primeiro Objetivo                │
│  │██│  Texto descritivo...              │
│  └──┘                                   │
│  ┌──┐  Como validar / Falar com [X]     │
│  │██│  [QR code ou critério offline]    │
│  └──┘                                   │
│  ─────────────────────────────────────  │
│  [Nota legal / offline / redes sociais] │
└─────────────────────────────────────────┘
```

**Specs:**
- Título: grande bold, palavra de destaque em cor de acento
- Blocos: borda arredondada, ícone em quadrado colorido à esquerda
- Rodapé: texto micro, cinza, separado por linha

---

### E-mail (simulação de cliente)

```
┌─────────────────────────────────────────┐
│  [LOGO CLIENTE E-MAIL]     [Destinatário]│
│  ─────────────────────────────────────  │
│  Assunto do e-mail                      │
│  1 mensagem                             │
│                                         │
│  Remetente <email@dominio>   [data hora]│
│  Para: destinatario@dominio             │
│                                         │
│  [Corpo em parágrafos curtos]           │
│                                         │
│  [N] anexos                             │
│  [📄 arq1 88K]  [📄 arq2 120K]          │
└─────────────────────────────────────────┘
```

**Specs:**
- Replicar visual de cliente de e-mail sem usar logo real
- Fonte sans-serif, 12–13pt, line-height 1.6
- Anexos: grid de ícones com nome e tamanho fictício em KB

---

### Print de conversa (grupo de mensagens)

```
┌─────────────────────────────────────────┐
│  HH:MM     ●●●  🔋                      │
│  < 139  [Nome do Grupo]   📷 📞         │
│  ─────────────────────────────────────  │
│    ┌──────────────────────┐             │
│    │ Nome - Contexto      │             │
│    │ Mensagem aqui...     │  HH:MM ✓✓  │
│    └──────────────────────┘             │
│              ┌──────────────────────┐   │
│              │ Resposta...          │   │
│              │              HH:MM ✓✓│   │
│              └──────────────────────┘   │
│  +  ○  📷  🎤                           │
└─────────────────────────────────────────┘
```

**Specs:**
- Fundo escuro: verde oliva ou cinza escuro
- Balões: branco para outros, cor de acento para o usuário
- Nome do remetente: cor distinta por pessoa (máx. 6 cores)
- Fonte sans-serif, 11–12pt

---

### Log de acesso (tabela técnica)

```
┌────────────────────────────────────────────────────┐
│  [LOGO]  CONTROLE DE ACESSOS        EXPORTADO EM  │
│          PERÍODO: [HH:MM DD/MM] A [HH:MM DD/MM]   │
│  ────────────────────────────────────────────────  │
│  DATA      │ HORA     │ PORTA │ ID   │ SENTIDO    │
│  ──────────┼──────────┼───────┼──────┼───────     │
│  01-03-2025│ 09:58:02 │ 1A   │ 39   │ ENTRADA    │
│  01-03-2025│ 09:58:30 │ 1A   │ 27   │ ENTRADA    │
└────────────────────────────────────────────────────┘
```

**Specs:**
- Fonte: `JetBrains Mono` ou `Courier New`
- Cabeçalho: cor primária, texto branco
- Linhas alternadas: `#FFFFFF` e `#F9FAFB`
- Bordas: `1px solid #E5E7EB`
- Anomalias sem destaque visual — o jogador deve encontrar

---

### Boletim / depoimento policial

```
┌─────────────────────────────────────────┐
│ [BRASÃO] POLÍCIA CIVIL DO ESTADO        │
│          TIPO DE DOCUMENTO  Nº DO CASO  │
│ ─────────────────────────────────────   │
│ TIPO DE OCORRÊNCIA │ DATA │ LOCALIZAÇÃO │
│ [manuscrito]       │      │ [manuscrito]│
│ ─────────────────────────────────────   │
│ [Corpo em fonte cursiva simulando       │
│  caligrafia — parágrafos separados]     │
│ ─────────────────────────────────────   │
│ RELATADO POR │ ASSINATURA │ DATA/HORA   │
│ [cursivo]    │ [cursivo]  │ [cursivo]   │
└─────────────────────────────────────────┘
```

**Specs:**
- Boletim: fundo `#FEFCE8` (amarelo claro)
- Depoimento: fundo `#F0FDF4` (verde claro)
- Cabeçalho: fundo `#1E3A5F`, logo institucional fictício
- Corpo: fonte Caveat 13pt simulando preenchimento manual
- Campos vazios: linhas pontilhadas

---

### Contrato ou apólice

```
┌─────────────────────────────────────────┐
│  [LOGO]               TIPO | VIGÊNCIA   │
│  ─────────────────────────────────────  │
│  ┌──────────────────┐                  │
│  │   PROPONENTE     │                  │
│  │ Razão Social:    │                  │
│  │ CNPJ:            │                  │
│  └──────────────────┘                  │
│  ┌───────────┐ ┌──────────────────┐    │
│  │COBERTURAS │ │ OBRIGAÇÕES       │    │
│  └───────────┘ └──────────────────┘    │
│  ┌───────────┐ ┌──────────────────┐    │
│  │  VALOR    │ │ OBJETO           │    │
│  └───────────┘ └──────────────────┘    │
│  [Assinatura A]      [Assinatura B]    │
└─────────────────────────────────────────┘
```

**Specs:**
- Cabeçalhos de seção: uppercase, letra-espaçada, fundo escuro, texto branco
- Grid de duas colunas para campos relacionados
- Assinaturas: fonte Caveat sobre linha

---

### Cartão de visita com código

```
FRENTE (lado da pista):
┌─────────────────────────────────────────┐
│  [Fundo escuro / padrão geométrico]     │
│  [CÓDIGO / GRID / TABELA / SEQUÊNCIA]   │
│  "Frase com duplo sentido"              │
│  [NOME DA EXPOSIÇÃO]   [QR decorativo]  │
└─────────────────────────────────────────┘

VERSO (identidade):
┌─────────────────────────────────────────┐
│  [LOGO DA EMPRESA]                      │
│  NOME DA EMPRESA                        │
│  "Slogan com duplo sentido"             │
└─────────────────────────────────────────┘

CORTAR AO REDOR DE CADA CARTÃO E DOBRAR AO MEIO
```

**Specs:**
- Dobrado: 8,5 × 5,5 cm; aberto: 17 × 5,5 cm
- Frente: fundo escuro, código legível mas não óbvio
- Verso: fundo claro, identidade corporativa fictícia

---

## 5. Imperfeições intencionais

Adicione ao menos 3 por envelope para aumentar o realismo. Escolha da lista:

| Imperfeição | Como implementar | Efeito |
|-------------|-----------------|--------|
| Campo em branco | Linha com `__________` sem preenchimento | Parece que faltou preencher |
| Data rasurada | Texto tachado + data corrigida em cursiva | Documento foi corrigido |
| Carimbo rotacionado | Rotate 2–4° | Carimbado por humano |
| Dobra simulada | Linha diagonal de baixo contraste | Documento físico digitalizado |
| Ruído de scanner | Pontos de baixo contraste nas bordas | Escaneado de papel |
| Assinatura cursiva | Fonte Caveat, traçado não uniforme | Assinado à mão |
| Marca de café | Círculo de baixa opacidade em canto | Documento manuseado |
| Sublinhado manual | Linha de baixa opacidade sob texto | Alguém leu e marcou |
| Post-it simulado | Retângulo amarelo levemente rotacionado, fonte cursiva | Anotação posterior |
| Grampo simulado | Dois círculos metálicos no canto superior | Conjunto de documentos |

---

## 6. Acessibilidade em preto e branco

Todo documento essencial deve funcionar em impressão P&B.

| Elemento colorido | Substituto em P&B |
|-------------------|-------------------|
| Cor de categoria no mapa | Hachura (pontilhado, diagonal, cruzado) |
| Linha vermelha de alerta | Negrito ou borda mais espessa |
| Fundo colorido de tabela | Alternância cinza claro `#F5F5F5` e branco |
| Carimbo vermelho | Carimbo preto com borda espessa |
| Destaque por cor | Negrito + sublinhado |
| Logo colorido | Versão monocromática |

**Regra absoluta:** nenhuma pista essencial depende exclusivamente de cor.

---

## 7. Design para tela de celular e tablet

Use quando a experiência for consumida em PDF digital visualizado em dispositivo móvel.

**Regras de layout:**
- páginas verticais (portrait), proporção A4 ou Letter;
- fonte mínima de 13pt para corpo, 11pt para tabelas;
- tabelas com no máximo 4–5 colunas sem scroll horizontal;
- tabelas largas quebradas em blocos temáticos em páginas separadas;
- margens mínimas de 15mm em todos os lados;
- alto contraste: texto escuro sobre fundo claro;
- nunca duas colunas de texto lado a lado;
- diagramas e mapas: máximo 6–8 elementos por página.

**Separação de arquivos para distribuição digital:**
- PDF do Envelope 1 (arquivo separado);
- PDF do Envelope 2 (arquivo separado, liberado pelo facilitador);
- PDF do Envelope 3, se houver;
- PDF de dicas (somente facilitador);
- PDF do gabarito (somente facilitador).

**Teste de legibilidade em celular:**
- [ ] Fonte do corpo legível sem zoom em tela de 6 polegadas.
- [ ] Tabelas não cortam colunas.
- [ ] Mapas e diagramas têm legenda visível.
- [ ] Logs técnicos não exigem scroll horizontal.
- [ ] Nenhuma pista essencial depende apenas de cor.

---

## 8. Envelopes físicos — marcação obrigatória

```
ENVELOPE 1 — FRENTE:
  ENVELOPE 1
  Abrir primeiro.
  Não abrir o Envelope 2 antes de validar a hipótese inicial.

ENVELOPE 2 — FRENTE:
  ENVELOPE 2
  Abrir somente após validar a resposta do Envelope 1.

ENVELOPE 3 — FRENTE (se houver):
  ENVELOPE 3
  Abrir somente após fechar a cadeia do Envelope 2.
```

---

## 9. Guia de impressão

| Configuração | Impressão doméstica | Gráfica |
|-------------|--------------------|----|
| Formato | A4 (210 × 297mm) | A4 ou Letter |
| Margens | 15mm todos os lados | 10mm |
| Resolução | 150 dpi mínimo | 300 dpi |
| Modo de cor | RGB / sRGB | CMYK |
| Sangria | Não necessária | 3mm |

**Sequência de montagem:**
1. Imprimir E1 e separar na ordem recomendada;
2. Imprimir E2 e lacrar fisicamente;
3. Imprimir E3, se houver, e lacrar;
4. Imprimir dicas (uma por folha) e guardar com o facilitador;
5. Imprimir gabarito e manter separado — nunca na mesa dos jogadores.

---

## 10. Checklist visual final

- [ ] Toda pista essencial é legível em preto e branco.
- [ ] Fontes de corpo têm mínimo 11pt (impressão) ou 13pt (tela).
- [ ] Tabelas têm no máximo 5–6 colunas visíveis sem scroll.
- [ ] O mapa tem legenda completa no mesmo documento.
- [ ] Logs usam fonte monoespaçada.
- [ ] Documentos manuscritos usam fonte cursiva legível (Caveat ou similar).
- [ ] Assinaturas são distintas entre personagens diferentes.
- [ ] Todos os logos são fictícios — nenhuma marca real copiada.
- [ ] Cada envelope tem protocolo com objetivo e critério de avanço.
- [ ] A folha de cruzamento está no Envelope 1.
- [ ] Dicas estão em arquivo/PDF separado.
- [ ] Gabarito está em arquivo/PDF separado.
- [ ] PDFs de envelopes diferentes são arquivos separados.
- [ ] Aberto em celular de 6 polegadas: texto legível sem zoom.
- [ ] Pelo menos 3 imperfeições intencionais por envelope.
- [ ] Nenhum documento do jogador contém notas do autor.

# Case Kernel

> Case Kernel é o DNA investigativo do caso. Documentos e templates vêm depois.

## O que é

O **Case Kernel** é uma camada conceitual e analítica que descreve o núcleo investigativo de um caso antes de qualquer decisão de documento, template, PDF, visual ou pacote final.

Ele responde, de forma explícita:

- qual é a pergunta pública do caso;
- qual é o conflito central investigável;
- qual é a verdade final interna;
- qual hipótese parcial o E1 deve permitir;
- como o E2 recontextualiza o E1;
- quais evidências são obrigatórias para avançar ou fechar;
- quais falsos caminhos são plausíveis;
- quais riscos editoriais o caso carrega.

## Por que existe

O blueprint atual já contém muitos campos editoriais importantes, mas eles vivem espalhados entre conflito central, objetivos por envelope, guia operacional, contratos de evidência, pistas, red herrings e solução interna.

O Case Kernel reúne esses sinais em uma visão menor e mais legível para revisão estrutural. Ele serve para perguntar se o mistério funciona como investigação antes de discutir diagramação, renderização, PDF, mapa, cartões ou estética.

## Relação com o Blueprint

Nesta fase, o Case Kernel **não é obrigatório no blueprint** e **não altera o contrato JSON dos casos canônicos**.

Ele é derivado conservadoramente a partir do `Blueprint` atual por `extract_case_kernel(blueprint)`. Quando uma informação não existe diretamente, a extração deve preferir string vazia ou lista vazia e deixar a validação emitir um finding. A regra é não inventar narrativa.

Fontes principais usadas na extração:

- `titulo`;
- `dificuldade`;
- `conflito_central`;
- `objetivos_por_envelope`;
- `guia_operacional`;
- `verdade_real`;
- `motivacao`;
- `contratos_evidencia`;
- `matriz_pistas`;
- `red_herrings`.

## Relação com Case Review

O Case Kernel é a base futura do **Case Review Report**.

A ordem esperada é:

1. extrair o Case Kernel;
2. validar o núcleo investigativo com códigos `CK_*`;
3. gerar uma revisão editorial estruturada;
4. só depois avaliar se documentos, envelopes, dicas, cartões e PDFs materializam bem esse núcleo.

O Case Review não deve começar pelo PDF. Ele deve começar pela pergunta: “o DNA investigativo está claro, progressivo e jogável?”.

## Campos mínimos

A implementação atual usa dataclasses em `generator/case_kernel.py`.

### `CaseKernel`

Campos principais:

- `case_id`: identificador derivado do título enquanto o blueprint não tiver um ID canônico;
- `titulo`: título do caso;
- `dificuldade`: dificuldade editorial normalizada, quando disponível;
- `pergunta_publica`: pergunta que justifica a investigação para os jogadores;
- `conflito_central`: síntese do conflito investigável;
- `verdade_final`: solução interna final;
- `hipotese_e1`: hipótese parcial que o primeiro envelope deve permitir;
- `recontextualizacao_e2`: mudança de leitura que o segundo envelope deve provocar;
- `motivacao_atual`: motivação com consequência presente no caso;
- `envelopes`: perguntas, respostas e critérios de avanço por envelope;
- `evidencias_obrigatorias`: contratos ou pilares indispensáveis;
- `red_herrings`: falsos caminhos plausíveis e seus descartes;
- `riscos`: riscos editoriais derivados de ambiguidade alta ou médio-alta.

### `EnvelopeKernel`

Representa o papel investigativo de um envelope:

- `id`;
- `pergunta`;
- `resposta_esperada`;
- `funcao_narrativa`;
- `criterio_avanco`.

### `EvidenceKernel`

Representa evidência obrigatória ou estruturante:

- `id`;
- `descricao`;
- `papel`;
- `envelope`.

## Códigos de validação `CK_*`

Todos os findings começam como `warning`. A validação do Case Kernel é analítica e não deve bloquear os canônicos nesta fase.

| Código | Significado |
|---|---|
| `CK_001` | Pergunta pública ausente ou fraca. |
| `CK_002` | Conflito central ausente. |
| `CK_003` | Verdade final ausente. |
| `CK_004` | Hipótese parcial do E1 ausente. |
| `CK_005` | Recontextualização do E2 ausente em caso com 2 ou mais envelopes. |
| `CK_006` | Motivação atual ausente. |
| `CK_007` | Envelope sem pergunta, resposta esperada ou critério de avanço. |
| `CK_008` | Evidências obrigatórias ausentes. |
| `CK_009` | Red herrings ausentes em dificuldade intermediária ou maior. |
| `CK_010` | Risco de E1 pedir solução final em vez de hipótese parcial. |

## Exemplos conceituais

### Bom núcleo de E1

O E1 deve permitir uma hipótese parcial, como:

- houve uma janela operacional real;
- a versão pública não explica todos os registros;
- ainda não é necessário fechar executor, planejamento e benefício final.

### Bom núcleo de E2

O E2 deve recontextualizar o E1, por exemplo:

- um detalhe operacional ganha motivação financeira;
- um objeto antes ambíguo vira sinal manipulado;
- um comportamento suspeito passa a ter descarte documental.

### Risco editorial típico

Um risco editorial aparece quando o primeiro envelope já exige solução final ou quando um falso caminho não tem descarte justo. O Kernel deve tornar esse risco visível antes de criar mais documentos explicativos para o jogador.


## Evolução desejada do Kernel

O Kernel deve passar a observar, inicialmente por derivação editorial e sem exigir novos campos obrigatórios no blueprint, conceitos que reduzem travamento narrativo em playtest:

- `mecanismo_causal`: como a ação central aconteceu, não apenas por que e quando;
- `tipo_evidencia_por_contrato`: separação entre evidência direta, indireta/por objeto e sistêmica;
- `relacoes_necessarias`: confiança, autoridade, hábito, obediência ou relação prévia indispensável para uma ação ser crível;
- `ausencias_relevantes`: ausências que precisam ser percebidas para uma conclusão parcial;
- `ferramentas_por_envelope`: estrutura concreta que permite ao jogador chegar à conclusão esperada;
- `pistas_por_ausencia`: pistas cuja força vem de algo que não foi visto, registrado ou confirmado.

Esses conceitos podem ser derivados a partir de `objetivos_por_envelope`, `contratos_evidencia`, `guia_operacional`, documentos e notas editoriais. Eles não precisam virar campos obrigatórios agora. O objetivo é melhorar a revisão editorial e a criação de novos casos antes de qualquer automação rígida.

Regras de referência:

- Quando a conclusão parcial depender de ausência, o caso precisa fornecer uma ferramenta de comparação. Ausência sem estrutura vira invisibilidade, não pista.
- A solução final precisa ter mecanismo causal documentado. Motivo explica por quê. Oportunidade explica quando. Mecanismo explica como.
- Se a solução depende de confiança, autoridade, hábito, obediência ou relação prévia, essa relação precisa ter pelo menos uma âncora documental antes da revelação final.

Perguntas úteis para extração futura:

- Qual ferramenta cada envelope oferece ao grupo para chegar à conclusão esperada?
- Alguma evidência indireta ou sistêmica está sendo tratada como evidência direta?
- A ausência importante fica visível em tabela, matriz, linha do tempo, registro comparativo ou estrutura equivalente?
- O grupo consegue inferir como a pessoa foi atraída, como o objeto foi movido, como o registro foi manipulado ou como o falso sinal foi criado?
- Qual documento ancora a relação necessária entre personagens quando a ação depende de confiança ou autoridade?

## O que não deve entrar no Kernel

O Case Kernel não deve conter:

- texto final de documentos de jogador;
- instruções de layout;
- templates HTML;
- CSS;
- decisões de PDF;
- mapas, cartões ou assets visuais;
- gabarito vazando para material diegético;
- frases instrucionais para o jogador comparar documentos;
- qualquer narrativa inventada pela extração.

O Kernel é interno, editorial e analítico. Ele organiza a lógica do caso; os documentos continuam responsáveis por apresentar evidência bruta dentro do mundo da história.

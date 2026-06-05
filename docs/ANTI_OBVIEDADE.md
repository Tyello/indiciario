# Anti-Obviedade — Guia de Geração de Documentos

Este arquivo define as regras que impedem documentos do jogador de entregar a solução prematuramente. Ele deve ser lido por LLMs antes de gerar qualquer documento e é verificado automaticamente pelo validador por meio de `generator/obviousness_checker.py`.

**Um bom documento de investigação sugere — não conclui.**

O jogador deve sentir que descobriu; não que foi avisado.

## Escopo do guardrail

O guardrail anti-obviedade protege apenas o material de jogador. Ele não proíbe análise no guia do facilitador, dicas contextuais, gabarito, contratos de evidência, QA, graph report, testes ou metadados internos.

Documentos de jogador devem conter evidência bruta:

- registros;
- versões parciais;
- mensagens operacionais;
- formulários;
- cartas diegéticas;
- logs;
- fichas;
- recibos;
- orçamentos;
- depoimentos limitados ao que a pessoa viu, ouviu ou fez.

Documentos de jogador não devem conter:

- conclusão de autoria;
- plano do culpado explicado;
- instrução de cruzamento;
- resumo do puzzle;
- confissão direta;
- interpretação de designer;
- gabarito disfarçado.

## Regras

### R01 — IDs operacionais em logs

Logs de acesso, sistemas e escalas devem preferir códigos, especialmente em Intermediário ou superior.

Em **Iniciante**, nomes podem aparecer quando a clareza fizer parte da dificuldade, desde que não estejam associados diretamente à ação criminosa.

Em **Intermediário ou superior**, prefira:

```text
USR-022
TERM-ADM-03
P-04
```

em vez de:

```text
Marina Vale — terminal administrativo — saída da carga
```

### R02 — Nome do culpado perto de ação incriminadora

Evitar nome do culpado junto de verbo incriminador e contexto crítico no mesmo trecho.

A regra não bloqueia nome do culpado com verbo cotidiano sem contexto incriminador.

Aceitável:

```text
Marta levou toalhas para a rouparia.
```

Obviedade:

```text
Marta tirou Helena do salão para impedir o brinde.
```

O problema não é “Marta” + “levou”. O problema é **Marta + tirou/impediu + Helena/salão/brinde** como cadeia já concluída.

### R03 — Confissões em primeira pessoa são proibidas

Nenhum documento do jogador pode ter personagem dizendo:

```text
Eu fiz.
Eu planejei.
Fui eu que...
Nós fizemos.
```

Mesmo em chat íntimo, a linguagem deve ser operacional, incompleta e contextual.

### R04 — `objetivo_narrativo` não nomeia culpado + ação

`objetivo_narrativo` é interno, mas pode contaminar o tom do documento. Se nomear culpado e ação do crime, o checker gera achado leve para revisão.

Ruim:

```text
Mostrar que Marta sabotou o brinde.
```

Melhor:

```text
Registrar uma fricção operacional que ganha sentido após o cruzamento com o E2.
```

### R05 — emoção esperada no E1 não antecipa solução

E1 deve criar urgência, curiosidade, suspeita e confusão produtiva. Não deve antecipar solução final, gabarito, confissão ou culpado revelado.

E1 pode gerar suspeita inicial plausível. E1 não deve permitir que o grupo responda sozinho:

- quem fez;
- como fez;
- por que fez;
- quem se beneficiou;
- qual evidência fecha a acusação.

### R06 — linguagem conclusiva é proibida em documento de jogador

Evitar:

```text
claramente foi
evidentemente
é culpado
foi provado
sem dúvida alguma
confessou
é o responsável
planejou o crime
```

Preferir evidência bruta:

```text
o registro indica
consta no relatório
não há anotação complementar
o campo está sem justificativa
```

Não use “a leitura conjunta sugere” em documento de jogador. Essa linguagem pertence ao guia do facilitador, não à evidência bruta.

### R07 — chats operacionais, não confessionais

Chats devem ter ruído, termos operacionais, cuidado de linguagem e mensagens que ganham sentido depois. Nunca devem explicar o crime diretamente.

Bom chat investigativo:

- parece exportação operacional;
- usa atalhos e nomes de tarefas;
- contém mensagens ambíguas;
- permite releitura posterior.

Chat ruim:

```text
O plano deu certo. Ninguém vai descobrir que trocamos a taça.
```

### R08 — depoimentos são versões, não laudos

Depoimento pode afirmar o que o declarante viu, ouviu ou fez.

Aceitável:

```text
Vi Renato fechar a janela por volta das 20h10.
```

```text
Ouvi Marta pedir que a rouparia fosse liberada antes do brinde.
```

Não pode afirmar autoria, intenção ou plano de terceiros como fato estabelecido.

Obviedade:

```text
Marta planejou tirar Helena do salão para impedir o brinde.
```

O declarante pode relatar percepção, dúvida ou versão. Não pode funcionar como laudo onisciente.

### R09 — nenhum documento único resolve o caso sozinho

Documento deve ser necessário, mas não suficiente. Se um documento sozinho responde quem, como, por quê e benefício, está fazendo demais.

A solução deve emergir da cadeia:

- documento A levanta hipótese;
- documento B recontextualiza;
- documento C confirma ou descarta;
- guia do facilitador explica a leitura esperada.

### R10 — campos internos nunca vão para `conteudo`

Campos como `verdade_real`, `observacoes_producao`, `gabarito`, `cadeia_causal` e `metodo_ocultacao` nunca devem aparecer no conteúdo de documentos do jogador.

Eles podem existir no blueprint ou nos relatórios internos. Não podem vazar para PDF de jogador.

## Checklist rápido antes de gerar documentos

Antes de salvar um documento de jogador, responda:

- Este documento mostra fato bruto ou interpreta a solução?
- Se eu entregar apenas este documento, o grupo já sabe quem fez?
- O E1 está criando pergunta ou fechando acusação?
- Há nome do culpado junto de ação incriminadora e contexto crítico?
- O chat parece trabalho operacional real ou conversa de vilão explicando plano?
- O depoimento relata o que alguém viu/ouviu/fez ou afirma intenção de terceiro?
- Alguma frase manda comparar, cruzar ou concluir?
- Algum campo interno vazou para `conteudo`?
- Em Intermediário ou superior, logs e escalas usam códigos sempre que possível?
- A motivação histórica tem consequência atual, mas sem virar explicação pronta no documento do jogador?

## Códigos do checker automático

| Código | Severidade | Regra | O que significa |
|---|---:|---|---|
| `OBV_001` | Aviso | R01 | Log, sistema ou escala em Intermediário+ usa nome em contexto crítico; prefira código operacional. |
| `OBV_002` | Moderado | R02 | Nome de culpado aparece com verbo incriminador e contexto crítico no mesmo trecho. |
| `OBV_003` | Crítico | R03 | Confissão em primeira pessoa detectada em documento de jogador. |
| `OBV_004` | Aviso | R04 | `objetivo_narrativo` nomeia culpado junto de ação potencialmente incriminadora. |
| `OBV_005` | Moderado | R05 | Documento de E1 antecipa solução, gabarito, confissão ou culpado revelado. |
| `OBV_006` | Moderado | R06 | Linguagem conclusiva detectada em conteúdo de jogador. |
| `OBV_007` | Crítico | R07 | Chat explica o crime diretamente ou assume tom confessional. |
| `OBV_008` | Moderado | R08 | Depoimento afirma autoria, intenção ou plano de terceiro como fato estabelecido. |
| `OBV_009` | Moderado | R09 | Documento parece resolver sozinho quem, como, por quê e benefício. |
| `OBV_010` | Crítico | R10 | Campo interno ou rótulo de gabarito vazou para `conteudo`. |
| `OBV_011` | Aviso | Voz do autor | Referência instrucional a código de documento apareceu em conteúdo diegético. |
| `OBV_012` | Moderado | Voz do autor | Linguagem de facilitador/designer apareceu em documento de jogador. |

## Exemplos do Iniciante — Mirante

### Logs podem ser mais claros, mas não conclusivos

No Mirante, por ser Iniciante, um dicionário de códigos pode mostrar nomes e funções quando a clareza ajuda a mesa. Ainda assim, o log bruto não deve dizer que Marina desviou a peça.

Bom:

```text
USR-022 — Marina Vale — Curadoria operacional.
```

Ruim:

```text
Marina Vale saiu pela doca com a peça desviada.
```

### E1 distribui suspeita

E1 deve mostrar divergência patrimonial, acessos, horários e ruído operacional. Não deve fechar Marina, Otávio, Celina ou qualquer outro personagem como solução.

### E2 confirma por cadeia

Contrato, recibo, extrato, etiquetas e nota técnica devem permanecer como evidências separadas. O jogador compara porque está investigando, não porque um documento manda comparar.

## Exemplos do Intermediário — Hotel Aurora

### Folha dobrada vista de relance

Boa pista:

```text
Caio relata ter visto uma folha dobrada na bandeja, sem conseguir ler todo o conteúdo.
```

Pista artificial:

```text
Caio anotou perfeitamente o texto da folha que revelava o plano do brinde.
```

### Rascunho de brinde em vez de e-mail explicativo

Bom documento:

```text
Rascunho com trechos riscados, ordem de agradecimentos e marcações de pausa.
```

Documento óbvio:

```text
E-mail explicando que a ordem do brinde foi alterada para isolar Helena.
```

### Carta de 1968 separada de ficha atual

A carta de 1968 deve sustentar motivo histórico. A ficha atual deve mostrar consequência presente. Se os dois elementos aparecem juntos como explicação pronta, o jogador não deduz: ele lê o gabarito.

### Chat como exportação operacional

Bom chat:

```text
20h04 — Rouparia liberada?
20h05 — Só depois da conferência.
20h06 — Preciso da dobra antes do salão.
```

Chat ruim:

```text
Troquei a taça e tirei Helena do salão para impedir o brinde.
```

### Renato/vento como red herring

Renato e o vento funcionam melhor como falso caminho quando aparecem por terceiro ou por registro operacional:

- alguém viu Renato perto de janela;
- uma porta bateu por corrente de ar;
- um registro de manutenção menciona vedação;
- outro documento descarta oportunidade ou intenção.

Não transforme o red herring em confissão ou descarte pronto no mesmo documento.

# Manual operacional para LLMs no Indiciário

Este documento orienta como uma LLM deve operar dentro do projeto Indiciário ao gerar, revisar, corrigir ou documentar casos investigativos.

O objetivo não é apenas produzir JSON válido. O objetivo é produzir mistérios jogáveis, solváveis, divertidos e sem vazamento de gabarito no material do jogador.

Após os playtests dos canônicos Iniciante e Intermediário, uma regra ficou explícita: bons documentos não bastam. A LLM deve exigir progressão jogável antes de gerar PDFs: pergunta pública, objetivo por envelope, critério de avanço, motivação com consequência atual e guia do facilitador operacional.

## Leitura obrigatória antes de qualquer tarefa

Antes de alterar qualquer arquivo, leia nesta ordem:

1. `AGENTS.md`
2. `README.md`
3. `docs/ESTADO_ATUAL.md`
4. `docs/DIRETRIZES_EDITORIAIS.md`
5. `docs/ANTI_OBVIEDADE.md`
6. `docs/CASE_DESIGN_PIPELINE.md`, se a tarefa envolver criação ou revisão estrutural de caso
7. `docs/BLUEPRINT_AUTHORING_GUIDE.md`, se a tarefa envolver blueprint ou novo caso
8. `examples/caso_canonico_iniciante.json`, se a tarefa tocar no caso canônico

Se a tarefa envolver revisão de PDF gerado, use também o feedback visual/playtest fornecido pelo usuário como fonte prioritária.

## Estado atual que deve guiar decisões

O caso canônico atual é:

- **O Desvio da Reserva Mirante**
- arquivo: `examples/caso_canonico_iniciante.json`
- dificuldade: **Iniciante**

A prioridade do projeto é realizar o primeiro playtest real.

Não crie novo caso, novo marketplace, dashboard, bot comercial, banco de dados ou editor visual sem pedido explícito.

## Diagnóstico inicial: que tipo de problema é?

Antes de modificar arquivos, classifique o problema.

### Problema de conteúdo

Sintomas:

- frase entrega solução;
- documento parece dica;
- personagem, motivo ou prova estão óbvios demais;
- orçamento, chat ou contrato parecem gabarito;
- documento deveria ser mais diegético.

Local provável:

- `examples/caso_canonico_iniciante.json`;
- documentação editorial.

Não comece por template ou renderer se o problema é texto.

### Problema de template

Sintomas:

- conteúdo correto, mas layout quebra;
- colunas sobrescrevem;
- assinatura aparece no lugar errado;
- campo renderiza mesmo quando falso;
- documento tem hierarquia visual ruim.

Local provável:

- `templates/*.html`;
- testes de renderer.

### Problema de renderer

Sintomas:

- assinatura/rubrica não é gerada corretamente;
- campo derivado não é injetado;
- template certo não é escolhido;
- HTML/PDF falha para um tipo de documento.

Local provável:

- `generator/renderer.py`.

### Problema de mapa/visual procedural

Sintomas:

- planta tem porta sem parede;
- câmera está solta;
- acesso físico não faz sentido;
- mapa entrega rota ou solução;
- mapa quebra a experiência de investigação.

Local provável:

- `generator/visual_procedural.py`;
- dados de `visual_procedural` no blueprint.

### Problema de validação

Sintomas:

- blueprint inválido passa;
- blueprint válido falha;
- erro de validação está errado ou ausente;
- regra editorial deve ser automatizada.

Local provável:

- `generator/validator.py`;
- testes em `tests/`;
- futuro guardrail editorial.

### Problema de progressão do caso

Sintomas:

- os jogadores não sabem por que estão investigando;
- o E1 tenta resolver o caso inteiro;
- o E2 apenas confirma algo já óbvio;
- não existe critério claro para liberar o próximo envelope;
- a motivação é histórica, mas não tem consequência atual;
- o facilitador precisa improvisar quando avançar, o que esperar ou como descartar falsos caminhos.

Local provável:

- plano Markdown do caso;
- blueprint JSON;
- `docs/CASE_DESIGN_PIPELINE.md`;
- `docs/BLUEPRINT_AUTHORING_GUIDE.md`;
- guia do facilitador.

Não resolva esse problema adicionando documentos explicativos ao jogador. Corrija o contrato editorial do caso.

### Problema de documentação

Sintomas:

- decisões do projeto só existem em chat;
- README está desatualizado;
- LLMs repetem erros já corrigidos;
- falta guia para novos casos.

Local provável:

- `README.md`;
- `AGENTS.md`;
- `docs/*.md`.

## Regra de ouro editorial

Documento de jogador mostra evidência. Não explica a investigação.

Nunca transforme um documento de jogador em:

- checklist de solução;
- comentário do autor;
- resumo do gabarito;
- orientação de cruzamento;
- justificativa explícita de suspeito.

A interpretação deve ficar em:

- guia do facilitador;
- dicas contextuais;
- gabarito;
- metadados internos;
- QA/Graph/LLM feedback.

## Exemplos de reescrita

### Ruim

```text
A confirmação depende de recibo, extrato e conversa interna.
```

### Melhor

```text
Documentação técnica será anexada ao fechamento administrativo da ordem.
```

---

### Ruim

```text
O preço isolado não decide a suspeita.
```

### Melhor

```text
Validade da proposta: 5 dias corridos a partir da emissão.
```

---

### Ruim

```text
Otávio aprovou o pacote único às 16h05 sob justificativa de prazo.
```

### Melhor

```text
Representante administrativo da contratante: Otávio Salles.
```

---

### Ruim

```text
Compare o contrato com o extrato e o recibo.
```

### Melhor

```text
Contrato vinculado à OS 0147/2026.
```

## Contrato mínimo para criar ou revisar blueprints

Antes de gerar ou aprovar um blueprint, confirme que o plano responde aos pontos abaixo.

Nota de schema: `pergunta_publica` e `objetivos_por_envelope` são contrato editorial de planejamento, ainda não campos schema-enforced do `Blueprint`. Enquanto o schema não for expandido, reflita esses conceitos em `premissa`, documentos, `contratos_evidencia`, `dicas_contextuais`, `observacoes_producao` e guia do facilitador.

### Pergunta pública

Todo caso precisa dizer:

1. quem pediu a apuração;
2. por que pediu;
3. qual impacto concreto existe;
4. por que os documentos foram reunidos.

Sem isso, o grupo recebe um dossiê sem mandato, urgência ou consequência.

### Objetivo por envelope

Todo envelope precisa declarar:

- pergunta diegética;
- resposta esperada;
- o que ainda não precisa ser resolvido;
- critério de avanço;
- forma diegética de apresentar esse avanço.

O E1 não deve pedir a solução final. Ele deve gerar hipótese parcial, tensão ou recontextualização inicial.

O E2 deve recontextualizar algo do E1. Ele não deve apenas confirmar uma conclusão que o E1 já entregou.

### Motivação atual

Motivação histórica precisa pressionar o presente. Não basta existir “carta de 1968”, segredo antigo ou mágoa familiar. Deve haver consequência atual: moradia, expulsão, dívida moral, herança, reputação, demissão, perda concreta ou risco público.

### Informação nova em recados

Se um personagem já sabe uma informação, qualquer recado posterior precisa trazer algo novo: documento omitido, versão original, lista não repassada, prova concreta ou risco imediato.

### Dicas contextuais

Cada dica deve informar condição de uso, intensidade, ação mental esperada e o que desbloqueia. Dica destrava ação; não substitui investigação.

### Guia do facilitador

Todo guia precisa conter pergunta pública, resposta esperada por envelope, quando liberar o próximo envelope, linha do tempo aparente, linha do tempo real, red herrings e descartes, explicação da motivação e solução em síntese.

## Como alterar o caso canônico

Ao alterar `examples/caso_canonico_iniciante.json`:

1. Preserve a dificuldade **Iniciante**.
2. Não recrie `caso_canonico_intermediario.json`.
3. Não adicione documentos apenas para explicar solução.
4. Prefira evidências curtas e diegéticas.
5. Verifique `confirma` e `confirmado_por` após remover/adicionar documentos.
6. Verifique contratos de evidência.
7. Verifique dicas contextuais.
8. Verifique `observacoes_producao`.
9. Atualize testes se o número de documentos mudar.
10. Rode validator strict.

## Como decidir se um documento deve existir

Antes de adicionar um documento, responda:

1. Ele existe naturalmente no mundo da história?
2. Ele traz uma evidência nova?
3. Ele melhora a experiência de mesa?
4. Ele reduz ambiguidade injusta sem entregar solução?
5. Ele não duplica outro documento?
6. Ele não é apenas um resumo para o jogador?

Se a resposta principal for “ajuda a explicar a solução”, não crie o documento. Coloque essa explicação no guia do facilitador ou em uma dica contextual.

## Como revisar documentos comerciais

Documentos comerciais devem parecer reais:

- orçamento/proposta é de uma empresa;
- recibo comprova pagamento/serviço;
- contrato formaliza relação;
- extrato mostra movimentação;
- e-mail/chat mostra contexto operacional.

Evite:

- orçamento com várias empresas dentro;
- quadro comparativo que funcione como resposta;
- condições que ensinem a investigar;
- frases como “comparação exige...”;
- lista “OS, recibo, extrato e conversa interna”.

Para o caso canônico iniciante, o documento `E2-03` foi removido porque facilitava demais a solução como mapa comparativo de propostas. Não o recrie sem instrução explícita.

## Como revisar mapas

Mapa do jogador deve ser planta baixa neutra.

Ao revisar ou alterar mapa:

1. Portas precisam estar em paredes.
2. Janelas precisam fazer sentido em paredes externas.
3. Câmeras devem estar em parede/canto plausível, não no meio da sala.
4. Área pública deve ter acesso coerente.
5. Galeria/Vitrine interna deve ter acesso pelo corredor.
6. Doca, depósito e reserva precisam ter divisões físicas coerentes.
7. Não desenhe rota da peça.
8. Não marque câmera offline.
9. Não destaque área crítica.
10. Não use legenda que explique a investigação.

Se uma versão analítica do mapa for útil, ela pertence ao guia do facilitador, não ao envelope do jogador.

## Como revisar assinaturas e rubricas

Assinatura/rubrica pertence ao personagem.

Ao mexer nisso:

1. Confira o perfil de assinatura no personagem.
2. Use `*_PERSONAGEM_ID` quando o documento souber quem assina.
3. Preserve fallback procedural.
4. Use override SVG apenas quando necessário.
5. Não volte a usar nome digitado como assinatura.
6. Assinatura completa e rubrica devem ser diferentes.
7. Personagens diferentes devem ter assinaturas visualmente diferentes.

## Como revisar dificuldade

O nível atual do Mirante é Iniciante.

Isso permite:

- códigos mais explícitos;
- relação ID → pessoa mais clara;
- mapas mais legíveis;
- dicas mais úteis;
- menor ambiguidade.

Mas não permite:

- documento explicando a solução;
- chat confessando crime;
- mapa mostrando rota;
- orçamento comparativo funcionando como resposta.

Para futuro caso Intermediário:

- usar mais códigos brutos;
- exigir mais cruzamento;
- aumentar red herrings justos;
- reduzir explicações;
- criar ambiguidade estrutural desde o planejamento.

Não tente transformar o Mirante em Intermediário apenas removendo textos. Ele é a régua Iniciante.

## Fluxo recomendado para PRs de correção

1. Leia o feedback do usuário.
2. Localize o arquivo responsável.
3. Identifique se o problema é conteúdo, template, renderer, mapa, validação ou documentação.
4. Faça a menor alteração possível.
5. Atualize testes quando a expectativa muda.
6. Rode comandos obrigatórios.
7. Explique no resumo da PR:
   - o que mudou;
   - por que mudou;
   - o que não foi mexido;
   - quais comandos foram executados;
   - limitações de ambiente, se houver.

## Fluxo recomendado para revisão de PR

Ao revisar uma PR:

1. Verifique se o escopo bate com a solicitação.
2. Verifique se não reabre problemas já resolvidos.
3. Verifique se não introduz voz do autor no material do jogador.
4. Verifique se documentos removidos não ficaram referenciados em `confirma`, `confirmado_por`, dicas, contratos ou testes.
5. Verifique se testes e validator foram executados.
6. Verifique se falha de Playwright é apenas ambiente ou regressão real.
7. Dê veredito claro: merge, pedir ajuste ou abandonar.

## Checklist rápido antes de considerar uma alteração boa

- O jogador consegue investigar sem receber checklist?
- O documento parece existir dentro do mundo da história?
- O mapa ajuda localização sem apontar solução?
- Existe pergunta pública com solicitante, motivo, impacto e justificativa do dossiê?
- Cada envelope tem pergunta diegética, resposta esperada, critério e forma diegética de avanço?
- O E1 evita pedir a solução final?
- O E2 recontextualiza algo do E1 em vez de apenas confirmar?
- A motivação histórica tem consequência atual?
- Recados posteriores trazem informação nova para quem os recebe?
- Dicas contextuais têm condição, intensidade, ação mental esperada e desbloqueio?
- O guia do facilitador é operacional para conduzir progressão e descartes?
- O E2 não entrega culpado por comparação pronta?
- As assinaturas pertencem aos personagens?
- A cadeia de evidência ainda fecha?
- O Envelope 1 não depende de documento do Envelope 2 para avanço?
- O guia do facilitador continua separado?
- O caso continua adequado para Iniciante?
- O primeiro playtest continua sendo o próximo objetivo?

## Futuro guardrail editorial

Ainda não implementar sem solicitação explícita, mas manter como próximo passo provável.

Ideia futura:

- criar `generator/player_content_guardrail.py`;
- integrar ao `validator.py` no modo strict;
- bloquear frases de handholding em documentos de jogador;
- permitir linguagem analítica em guia, dicas e metadados;
- gerar códigos como `HAND_001`, `HAND_002`, etc.

Enquanto esse guardrail não existe, use `docs/DIRETRIZES_EDITORIAIS.md` como regra manual.

## Quando pedir decisão humana

Peça decisão humana quando:

- a mudança altera dificuldade;
- a mudança remove documento importante;
- o ajuste muda solução/gabarito;
- há dúvida se uma pista ficou fácil demais;
- o mapa precisa de decisão editorial de espaço;
- a alteração envolve nova arquitetura;
- a tarefa entra em temas fora da prioridade atual.

Não invente direção nova quando o usuário já definiu o caminho.

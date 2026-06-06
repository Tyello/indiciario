# Manual operacional para LLMs no Indiciário

Este documento orienta como uma LLM deve operar dentro do projeto Indiciário ao gerar, revisar, corrigir ou documentar casos investigativos.

O objetivo não é apenas produzir JSON válido. O objetivo é produzir mistérios jogáveis, solváveis, divertidos e sem vazamento de gabarito no material do jogador.

Após os playtests dos canônicos Iniciante e Intermediário, uma regra ficou explícita: bons documentos não bastam. A LLM deve exigir progressão jogável antes de gerar PDFs: pergunta pública, objetivo por envelope, critério de avanço, motivação com consequência atual e guia do facilitador operacional.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Leitura obrigatória antes de qualquer tarefa

Antes de alterar qualquer arquivo, leia nesta ordem:

1. `AGENTS.md`
2. `README.md`
3. `docs/ESTADO_ATUAL.md`
4. `docs/ROADMAP.md`
5. `docs/DIRETRIZES_EDITORIAIS.md`
6. `docs/DIEGESE_DOCUMENTAL.md`
7. `docs/ANTI_OBVIEDADE.md`
8. `docs/VISUAL_SYSTEM.md`, se a tarefa envolver visual, templates ou PDF
9. `docs/PRINTABLES.md`, se a tarefa envolver cartões/material de mesa
10. `docs/SIGNATURES_AND_HANDWRITING.md`, se a tarefa envolver assinatura, rubrica ou manuscrito
11. `docs/FLOORPLANS.md`, se a tarefa envolver mapas/planta baixa
12. `docs/CASE_DESIGN_PIPELINE.md`, se a tarefa envolver criação ou revisão estrutural de caso
13. `docs/BLUEPRINT_AUTHORING_GUIDE.md`, se a tarefa envolver blueprint ou novo caso
14. `examples/caso_canonico_iniciante.json`, se a tarefa tocar em régua Iniciante
15. `examples/caso_canonico_intermediario.json`, se a tarefa tocar em régua Intermediária

Se a tarefa envolver revisão de PDF gerado, use também o feedback visual/playtest fornecido pelo usuário como fonte prioritária.

## Estado atual que deve guiar decisões

Réguas canônicas atuais:

- **O Desvio da Reserva Mirante** — `examples/caso_canonico_iniciante.json` — dificuldade **Iniciante**.
- **O Último Brinde do Hotel Aurora** — `examples/caso_canonico_intermediario.json` — dificuldade **Intermediário**.

Prioridade atual do projeto:

1. gerar baseline real dos PDFs dos dois canônicos com Playwright/Chromium local;
2. revisar visualmente os pacotes pós-P0/P1/P2/P3;
3. corrigir apenas falhas comprovadas de layout/renderização/pacote;
4. realizar novo playtest do Intermediário com pessoas novas;
5. só depois planejar o canônico Avançado.

Não crie novo caso Avançado, marketplace, dashboard, bot comercial, banco de dados, editor visual, app ou automação de venda sem pedido explícito.

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

- blueprint JSON;
- plano Markdown do caso;
- documentação editorial.

Não comece por template ou renderer se o problema é texto.

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
- `conflito_central`;
- `objetivos_por_envelope`;
- `guia_operacional`;
- `docs/CASE_DESIGN_PIPELINE.md`;
- `docs/BLUEPRINT_AUTHORING_GUIDE.md`.

Não resolva esse problema adicionando documentos explicativos ao jogador. Corrija o contrato editorial do caso.

### Problema de diegese documental

Sintomas:

- informação correta aparece no documento errado;
- e-mail explica demais;
- carta antiga traz anexo moderno artificial;
- chat parece conversa mágica da vítima;
- red herring parece autoincriminação.

Local provável:

- blueprint JSON;
- `docs/DIEGESE_DOCUMENTAL.md`;
- contratos de evidência;
- documentos do envelope.

Regra central:

> Uma boa pista no documento errado vira pista artificial.

### Problema de template

Sintomas:

- conteúdo correto, mas layout quebra;
- colunas sobrescrevem;
- assinatura aparece no lugar errado;
- campo renderiza mesmo quando falso;
- documento tem hierarquia visual ruim.

Local provável:

- `templates/*.html`;
- `templates/styles/document_system.css`;
- testes de renderer.

### Problema de renderer

Sintomas:

- assinatura/rubrica não é gerada corretamente;
- campo derivado não é injetado;
- template certo não é escolhido;
- HTML/PDF falha para um tipo de documento;
- manifest ou print manifest sai errado.

Local provável:

- `generator/renderer.py`;
- `generator/package_builder.py`;
- renderer específico do recurso afetado.

### Problema de mapa/planta baixa

Sintomas:

- planta tem porta sem parede;
- porta não abre gap real;
- janela não está na parede;
- câmera está solta;
- acesso físico não faz sentido;
- mapa entrega rota ou solução;
- mapa quebra a experiência de investigação.

Local provável:

- `generator/floorplan_renderer.py`;
- `templates/floorplan.html`;
- dados de `visual_procedural.mapas` no blueprint;
- `docs/FLOORPLANS.md`.

Regras críticas:

- A4 landscape;
- P&B first;
- portas somente em paredes e com gap real;
- portas entre áreas adjacentes devem abrir a parede compartilhada quando houver coincidência real;
- câmeras em parede/canto;
- sem rota, área crítica, campo de visão, câmera offline ou linguagem interpretativa.

### Problema de printables apartados

Sintomas:

- cartões de personagem, local ou objeto aparecem misturados aos envelopes;
- um cartão parece pista, checklist ou interpretação;
- falta orientação de impressão/recorte para apoio de mesa.

Local provável:

- `generator/models.py`;
- `generator/printable_cards.py`;
- `templates/printable_cards.html`;
- `generator/package_builder.py`;
- `generator/print_guide.py`;
- `docs/PRINTABLES.md`;
- campo `printable_cards` do blueprint.

Cartões são material público de mesa, mas não são evidência primária. Não inclua culpa, motivação secreta, gabarito, contratos de evidência ou orientação explícita de cruzamento.

### Problema de assinatura, rubrica ou manuscrito

Sintomas:

- assinaturas parecem iguais;
- rubrica parece assinatura reduzida sem identidade;
- manuscrito parece fonte decorativa;
- manuscrito está longo demais;
- override SVG não é respeitado.

Local provável:

- `generator/signature_renderer.py`;
- campos de perfil visual do personagem;
- templates que exibem assinatura/rubrica/manuscrito;
- `docs/SIGNATURES_AND_HANDWRITING.md`.

Assinatura, rubrica e manuscrito são características editoriais do personagem, não decoração genérica.

### Problema de sistema visual documental

Sintomas:

- documentos corretos parecem “HTML bonito” em vez de artefatos físicos;
- tabelas parecem genéricas ou dependem de cor;
- cabeçalhos, rodapés, carimbos e assinaturas não sustentam a diegese;
- guia do facilitador se confunde visualmente com material dos jogadores.

Local provável:

- `templates/styles/document_system.css`;
- templates HTML principais;
- `generator/renderer.py`, apenas para injeção sistêmica de classes/metadados;
- `docs/VISUAL_SYSTEM.md`.

Não peça “visual bonito” genérico. Preserve offline first, P&B first, evidência bruta e separação jogador/facilitador.

### Problema de validação

Sintomas:

- blueprint inválido passa;
- blueprint válido falha;
- erro de validação está errado ou ausente;
- regra editorial deve ser automatizada.

Local provável:

- `generator/validator.py`;
- testes em `tests/`;
- `generator/obviousness_checker.py`, quando a regra envolver obviedade editorial (`OBV_001` a `OBV_012`).

### Problema de documentação

Sintomas:

- decisões do projeto só existem em chat;
- README está desatualizado;
- LLMs repetem erros já corrigidos;
- falta guia para novos casos;
- roadmap ainda cita fase já concluída.

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

Nota de schema: `conflito_central`, `objetivos_por_envelope` e `guia_operacional` são campos schema-enforced do `Blueprint`. Reflita esses conceitos também em `premissa`, documentos, `contratos_evidencia` e `dicas_contextuais`, mas não dependa de texto livre para progressão.

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

## Como alterar casos canônicos

Ao alterar `examples/caso_canonico_iniciante.json`:

1. Preserve a dificuldade **Iniciante**.
2. Não tente transformá-lo em Intermediário por polimento incremental.
3. Não adicione documentos apenas para explicar solução.
4. Preserve sua função de régua introdutória e fixture de integração.
5. Verifique `confirma` e `confirmado_por` após remover/adicionar documentos.

Ao alterar `examples/caso_canonico_intermediario.json`:

1. Preserve a dificuldade **Intermediário**.
2. Preserve a decisão de manter Hotel Aurora sem mapa.
3. Não altere a solução sem novo playtest ou decisão explícita.
4. Preserve a progressão em dois envelopes com recontextualização no E2.
5. Verifique pergunta pública, objetivos por envelope e guia operacional.

## Antes de iniciar novo caso

Não iniciar novo canônico Avançado sem:

1. baseline real dos PDFs Iniciante e Intermediário com Playwright;
2. revisão visual pós-P0/P1/P2/P3;
3. novo playtest do Intermediário ou decisão explícita de pular essa etapa;
4. plano Markdown do Avançado aprovado antes do JSON.

# Estado atual do Indiciário

Este documento registra a situação atual do projeto após os playtests reais, consolidação das réguas canônicas e hardening editorial, técnico e visual até o P3 de assinaturas, rubricas e manuscritos.

## Hierarquia documental

Este documento participa da hierarquia documental oficial do projeto:

1. `docs/DIRETRIZES_EDITORIAIS.md` — fonte da verdade editorial.
2. `docs/ANTI_OBVIEDADE.md` — regras automáticas de obviedade.
3. `docs/BLUEPRINT_AUTHORING_GUIDE.md` — contrato do blueprint.
4. `docs/CASE_DESIGN_PIPELINE.md` — processo de criação.
5. `docs/LLM_OPERATING_MANUAL.md` — operação de agentes.
6. `docs/ESTADO_ATUAL.md` — snapshot do estado atual.

Em conflito editorial, `docs/DIRETRIZES_EDITORIAIS.md` prevalece. Em conflito sobre implementação ou estado do projeto, `docs/ESTADO_ATUAL.md` prevalece.

## Visão do produto

Indiciário é um framework e futuro produto para geração de mistérios investigativos jogáveis em grupo, em formato de dossiê, envelopes, documentos e materiais de apoio.

Referências de experiência:

- jogos investigativos físicos;
- dossiês investigativos;
- board games de dedução;
- escape rooms como referência de ritmo;
- experiências como “Sob Investigação” e “Uma Noite Sem Flores”.

Princípios atuais:

- offline first;
- sem QR code;
- sem internet obrigatória;
- sem aplicativos externos;
- sem links externos como parte da solução;
- jogável em mesa, notebook, tablet ou impressão;
- foco em dedução, investigação e experiência de grupo.

Slogan atual:

> Todo caso deixa sinais.

## Estado técnico

O framework está tecnicamente funcional.

Funcionalidades já existentes no repositório incluem:

- schemas YAML por template;
- `required_when`;
- bloqueio de placeholders residuais;
- QA Report;
- Graph Report;
- contratos de evidência;
- grafo de pistas;
- feedback para LLM;
- guia do facilitador;
- dicas contextuais;
- guia de impressão;
- visual procedural;
- métricas de playtest;
- guardrail anti-obviedade integrado ao validator;
- progressão por envelope schema-enforced;
- package builder;
- manifest;
- print manifest;
- Playwright como renderizador oficial;
- merge PDF com `pikepdf`;
- sistema visual documental P0 com tokens CSS globais, cabeçalho/rodapé documental, classes por tipo e família, tabelas P&B first e carimbos burocráticos opcionais;
- printables apartados P1 para cartões recortáveis de personagem, local e objeto, registrados no manifest e no guia de impressão como apoio de mesa;
- plantas baixas P2 com renderer dedicado, A4 paisagem, P&B first, portas, janelas, câmeras e validações `MAP_*`;
- suporte P3 a assinatura, rubrica e manuscrito curto por perfil de personagem no blueprint;
- possibilidade de override SVG para assinatura/rubrica.

Problemas já tratados e que não devem ser reabertos sem evidência nova:

- placeholders residuais como `COPIA`;
- placeholders em logs;
- schemas incompletos;
- PDFs consolidados em branco;
- merger usando apenas `pypdf`;
- build strict do caso canônico;
- dicas gerando apenas capas;
- mapa explicando rota/área crítica/câmera offline;
- E2 com mapa comparativo explícito de propostas;
- assinaturas puramente textuais;
- rubricas genéricas como “iniciais + risco” sem perfil;
- cartões misturados automaticamente nos envelopes;
- mapas com portas sem gap real ou câmeras flutuantes.

## Réguas canônicas atuais

O projeto mantém duas réguas canônicas validadas:

### Iniciante

- **O Desvio da Reserva Mirante**
- Arquivo: `examples/caso_canonico_iniciante.json`
- Dificuldade editorial atual: **Iniciante**
- Status: **régua canônica Iniciante**

O caso foi rebaixado de Intermediário para Iniciante por decisão editorial e confirmado pelo primeiro playtest como fácil demais para Intermediário.

Papel atual do Mirante:

- régua canônica Iniciante;
- referência técnica de build/package;
- fixture de integração;
- benchmark mínimo de qualidade visual/documental;
- exemplo de experiência introdutória;
- referência atual para mapa/planta baixa de jogador.

Não tentar transformar o Mirante em Intermediário por ajustes incrementais.

### Intermediário

- **O Último Brinde do Hotel Aurora**
- Arquivo: `examples/caso_canonico_intermediario.json`
- Dificuldade editorial atual: **Intermediário**
- Status: **régua canônica Intermediária validada após playtest e refinamento**

O Hotel Aurora passou por playtest, refinamentos editoriais e refinamento diegético. Para fins de régua canônica Intermediária, considerar o caso validado.

Papel atual do Hotel Aurora:

- régua canônica Intermediária validada;
- referência de progressão em 2 envelopes com recontextualização forte;
- referência de guia do facilitador operacional pós-playtest;
- referência de caso sem mapa por decisão de playtest.

Comando oficial para geração do baseline Intermediário:

```bash
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

A geração final do pacote deve ser confirmada em ambiente local com Chromium/Playwright disponível.

## Resultado dos playtests

Playtests reais já foram realizados.

Resultado resumido do Mirante:

- os jogadores gostaram dos documentos;
- a experiência documental foi positiva;
- o caso foi fácil demais para Intermediário;
- o material funciona como introdução.

Resultado resumido do Hotel Aurora:

- o plot foi bem recebido;
- a progressão em 2 envelopes ficou mais forte após refinamentos;
- o caso validou a necessidade de pergunta pública, objetivo por envelope, critério de avanço e guia do facilitador operacional;
- decidiu-se manter o caso sem mapa para não simplificar demais a investigação.

Interpretação de produto:

- o framework consegue gerar material atraente;
- o risco principal agora é gerar documentos bonitos para mistérios fracos, óbvios ou sem progressão operacional;
- bons documentos não bastam se faltar pergunta pública, objetivo por envelope, critério de avanço, motivação atual e guia do facilitador operacional;
- o pipeline de design de caso deve usar Mirante como régua Iniciante e Hotel Aurora como régua Intermediária validada.

## Decisões recentes relevantes

### Réguas canônicas

O antigo caso canônico intermediário foi renomeado/rebaixado para `caso_canonico_iniciante.json` e permanece como régua Iniciante.

O novo caso `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora** — passou por playtest e refinamentos, e agora é a régua Intermediária validada.

Referências canônicas devem diferenciar explicitamente:

- `examples/caso_canonico_iniciante.json` para Iniciante;
- `examples/caso_canonico_intermediario.json` para Intermediário.

### Progressão, motivação e guia operacional

`conflito_central`, `objetivos_por_envelope` e `guia_operacional` são campos schema-enforced do `Blueprint`.

Regras atuais:

- todo caso precisa de pergunta pública clara: quem pediu a apuração, por que pediu, qual impacto concreto existe e por que os documentos foram reunidos;
- todo envelope precisa de pergunta diegética, resposta esperada, o que ainda não precisa ser resolvido, critério de avanço e forma diegética de apresentar o avanço;
- E1 não deve pedir a solução final, apenas hipótese parcial, tensão ou recontextualização inicial;
- E2 deve recontextualizar algo do E1, não apenas confirmar;
- motivação histórica precisa ter consequência atual, como moradia, expulsão, herança, reputação, demissão, perda concreta ou risco público;
- dicas contextuais devem destravar ações e declarar condição de uso, intensidade, ação mental esperada e desbloqueio;
- o guia do facilitador deve conter pergunta pública, resposta esperada por envelope, liberação do próximo envelope, linha do tempo aparente, linha do tempo real, red herrings, descartes, motivação e síntese da solução.

Documento de jogador continua sendo evidência bruta. Interpretação, cruzamentos, gabarito e linguagem analítica pertencem ao guia, às dicas e aos metadados internos.

### Guardrail anti-obviedade

Foi adicionado um guardrail em duas camadas para proteger documentos de jogador contra obviedade excessiva:

- documentação editorial em `docs/ANTI_OBVIEDADE.md`;
- checker automático em `generator/obviousness_checker.py`, integrado ao validator com códigos `OBV_001` a `OBV_012`.

O objetivo é impedir confissões, conclusões prontas, chats explicativos, depoimentos oniscientes, vazamento de campos internos e nome do culpado associado a ação incriminadora em contexto crítico, sem bloquear a ambiguidade boa dos canônicos atuais.

### Diegese documental

Regra central:

> Uma boa pista no documento errado vira pista artificial.

Documentos de jogador precisam existir naturalmente no mundo da história. Se uma informação só está ali para ajudar o jogador a resolver, provavelmente está no documento errado.

### Sistema visual P0

Foi criada a base P0 do sistema visual documental em `templates/styles/document_system.css`, injetada automaticamente pelo renderer nos HTMLs finais.

A camada adiciona tokens tipográficos, escala de cinzas, espaçamentos, bordas, cabeçalho/rodapé documental para documentos de jogador, classes por tipo e família documental, padrões de tabela, carimbos opcionais e regras de impressão P&B.

### Printables apartados P1

O pacote pode gerar cartões recortáveis de personagem, local e objeto como apoio de mesa separado dos envelopes.

Os PDFs são gravados em `printables/`, aparecem no `manifest.json` e no `print_manifest.json`, e o guia de impressão informa recorte, papel recomendado e separação em relação a envelopes, dicas e material confidencial do facilitador.

Cartão é apoio de mesa, não evidência primária.

### Plantas baixas P2

Foi adicionada uma camada P2 para mapas procedurais:

- `generator/floorplan_renderer.py`;
- `templates/floorplan.html`;
- validações `MAP_*` no validator.

O canônico Iniciante mantém seu mapa como documento de jogador do E1, agora com portas, janelas e câmeras modeladas explicitamente. O canônico Intermediário/Hotel Aurora permanece sem mapa.

Padrão atual:

- A4 paisagem;
- P&B first;
- fundo branco;
- paredes fechadas;
- portas com gap real;
- portas entre áreas adjacentes devem abrir a parede compartilhada dos dois lados quando houver coincidência real;
- janelas paralelas na parede;
- câmeras presas em parede/canto;
- sem rotas, áreas críticas, câmera offline, campo de visão ou linguagem interpretativa.

O padrão está documentado em `docs/FLOORPLANS.md`.

### Assinaturas, rubricas e manuscritos P3

Assinatura/rubrica passou a ser característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica/manuscrito curto;
- o renderer gera SVG com base nesse perfil em `generator/signature_renderer.py`;
- override SVG manual é permitido;
- fallback procedural continua disponível para compatibilidade;
- assinatura/rubrica não deve ser apenas nome digitado nem “iniciais + risco” genérico;
- manuscrito deve ficar restrito a intervenções curtas, com limite recomendado de 120 caracteres.

## Roadmap atual

O roadmap detalhado está em `docs/ROADMAP.md`.

Resumo da ordem recomendada:

1. gerar baseline real dos PDFs dos canônicos com Playwright local;
2. revisar visualmente Iniciante e Intermediário após P0/P1/P2/P3;
3. corrigir apenas problemas comprovados de layout, renderização ou clareza operacional;
4. executar novo playtest do Intermediário com pessoas novas;
5. só depois planejar o canônico Avançado.

## O que não priorizar agora

Não priorizar neste momento:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- agentes autônomos;
- IA gerando imagens.

Antes disso, usar as réguas Iniciante e Intermediária para validar que o framework continua gerando casos interessantes, intrigantes e divertidos.

## Comandos úteis

Testes:

```bash
pytest tests/ -q
```

Lint:

```bash
ruff check generator/
```

Validator strict:

```bash
python -m generator.validator examples/caso_canonico_iniciante.json --strict
python -m generator.validator examples/caso_canonico_intermediario.json --strict
```

Build do pacote com Playwright/Chromium:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Fallback de build fake, apenas para validar pipeline quando Chromium não estiver disponível:

```bash
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Instalação do browser Playwright, se necessário:

```bash
python -m playwright install chromium
```

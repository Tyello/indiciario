# Estado atual do Indiciário

Este documento registra a situação atual do projeto após as rodadas de hardening editorial, visual e técnico do caso canônico e após o primeiro playtest real.

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
- package builder;
- manifest;
- print manifest;
- Playwright como renderizador oficial;
- merge PDF com `pikepdf`;
- mapa procedural canônico;
- suporte P3 a assinatura, rubrica e manuscrito curto por perfil de personagem no blueprint;
- possibilidade de override SVG para assinatura/rubrica.
- sistema visual documental v1 com tokens CSS globais, cabeçalho/rodapé documental, classes por tipo e família, tabelas P&B first e carimbos burocráticos opcionais;
- printables apartados P1 para cartões recortáveis de personagem, local e objeto, registrados no manifest e no guia de impressão como apoio de mesa.

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
- assinaturas puramente textuais.

## Réguas canônicas atuais

O projeto agora mantém duas réguas canônicas por dificuldade:

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
- exemplo de experiência introdutória.

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
- comando oficial para geração do baseline Intermediário.

Comando oficial para geração do baseline:

```bash
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

A geração final do pacote deve ser confirmada em ambiente local com Chromium/Playwright disponível.

## Resultado do primeiro playtest

Primeiro playtest real: **realizado**.

Resultado resumido:

- os jogadores gostaram dos documentos;
- a experiência documental foi positiva;
- o caso foi fácil demais;
- o material funciona como introdução, mas não como régua Intermediária;
- o próximo salto precisa vir de história, tensão, ambiguidade e mecânica investigativa, não de mais polimento visual.

Interpretação de produto:

- o framework consegue gerar material atraente;
- o risco principal agora é gerar documentos bonitos para mistérios fracos, óbvios ou sem progressão operacional;
- bons documentos não bastam se faltar pergunta pública, objetivo por envelope, critério de avanço, motivação atual e guia do facilitador operacional;
- o pipeline de design de caso deve usar Mirante como régua Iniciante e Hotel Aurora como régua Intermediária validada.

## Decisões recentes relevantes

### Réguas canônicas

O antigo caso canônico intermediário foi renomeado/rebaixado para `caso_canonico_iniciante.json` e permanece como régua Iniciante.

O novo caso `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora** — passou por playtest e refinamentos, e agora é a régua Intermediária validada.

A partir de agora, referências canônicas devem diferenciar explicitamente:

- `examples/caso_canonico_iniciante.json` para Iniciante;
- `examples/caso_canonico_intermediario.json` para Intermediário.

### Assinaturas e rubricas

Assinatura/rubrica passou a ser característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica/manuscrito curto;
- o renderer gera SVG com base nesse perfil em `generator/signature_renderer.py`;
- override SVG manual é permitido;
- fallback procedural continua disponível para compatibilidade;
- assinatura/rubrica não deve ser apenas nome digitado nem “iniciais + risco” genérico;
- manuscrito deve ficar restrito a intervenções curtas, com limite recomendado de 120 caracteres.

### Mapa

O mapa do jogador deve ser uma planta baixa neutra.

Deve conter:

- paredes;
- portas;
- janelas;
- câmeras neutras;
- nomes dos ambientes;
- códigos de portas;
- norte e escala se discretos/profissionais.

Não deve conter:

- rota da peça;
- destaque de área crítica;
- câmera offline;
- campo de visão;
- legenda explicativa;
- cores de categoria;
- texto que explique por que ninguém viu ou como a rota ocorreu.

A Galeria/Vitrine interna deve ter acesso visual pelo corredor, não depender de passagem por doca, depósito ou reserva técnica.

### Guardrail anti-obviedade

Foi adicionado um guardrail em duas camadas para proteger documentos de jogador contra obviedade excessiva:

- documentação editorial em `docs/ANTI_OBVIEDADE.md`;
- checker automático em `generator/obviousness_checker.py`, integrado ao validator com códigos `OBV_001` a `OBV_012`.

O objetivo é impedir confissões, conclusões prontas, chats explicativos, depoimentos oniscientes, vazamento de campos internos e nome do culpado associado a ação incriminadora em contexto crítico, sem bloquear a ambiguidade boa dos canônicos atuais.

### Progressão, motivação e guia operacional

Após playtests dos canônicos Iniciante e Intermediário, ficou estabelecido que todo novo caso precisa explicitar progressão antes de gerar documentos finais.

Regras atuais:

- todo caso precisa de pergunta pública clara: quem pediu a apuração, por que pediu, qual impacto concreto existe e por que os documentos foram reunidos;
- todo envelope precisa de pergunta diegética, resposta esperada, o que ainda não precisa ser resolvido, critério de avanço e forma diegética de apresentar o avanço;
- E1 não deve pedir a solução final, apenas hipótese parcial, tensão ou recontextualização inicial;
- E2 deve recontextualizar algo do E1, não apenas confirmar;
- motivação histórica precisa ter consequência atual, como moradia, expulsão, herança, reputação, demissão, perda concreta ou risco público;
- recados posteriores só devem existir se trouxerem algo novo para quem os recebe;
- dicas contextuais devem destravar ações e declarar condição de uso, intensidade, ação mental esperada e desbloqueio;
- o guia do facilitador deve conter pergunta pública, resposta esperada por envelope, liberação do próximo envelope, linha do tempo aparente, linha do tempo real, red herrings, descartes, motivação e síntese da solução.

`conflito_central`, `objetivos_por_envelope` e `guia_operacional` são agora campos schema-enforced do `Blueprint`. A validação exige pergunta pública consistente, objetivo por envelope, resposta esperada, critério de avanço, forma diegética de avanço e guia operacional para o facilitador.

Documento de jogador continua sendo evidência bruta. Interpretação, cruzamentos, gabarito e linguagem analítica pertencem ao guia, às dicas e aos metadados internos.

### E2 e documentos comerciais

O E2 não deve entregar a solução por comparação pronta.

Decisão atual:

- remover mapa/quadro interno de propostas recebidas do material do jogador;
- manter orçamentos/propostas individuais por empresa;
- contrato, recibo, extrato, e-mails e chats devem ser evidências separadas;
- o jogador deve comparar porque está investigando, não porque um documento mandou comparar.

Evitar em documentos do jogador:

- “compare com...”;
- “a confirmação depende de...”;
- “preço isolado não decide...”;
- “recibo, extrato e conversa interna...” como checklist;
- frases que concentrem pessoa, ação, motivo e horário em formato de conclusão.

## Roadmap atual

### Fase A — Playtest real do Mirante

Status: **concluído na primeira rodada**.

Resultado: bom material documental, caso fácil demais.

Não continuar polindo indefinidamente o Mirante. Ajustes futuros devem ser baseados em evidência concreta, não em busca de perfeição.

### Fase B — Pipeline de design de caso

Prioridade atual.

Objetivo: impedir que a LLM gere documentos antes de ter uma história investigativa forte.

Criar e usar:

- `docs/CASE_DESIGN_PIPELINE.md`;
- `docs/BLUEPRINT_AUTHORING_GUIDE.md`;
- plano Markdown antes de qualquer blueprint JSON;
- pergunta pública;
- objetivo e critério de avanço por envelope;
- núcleo dramático;
- curva de suspeita;
- momentos de descoberta;
- riscos de obviedade;
- riscos de injustiça;
- mecânica investigativa principal;
- motivação com consequência atual;
- guia do facilitador operacional.

### Fase C — Novo caso canônico Intermediário

O próximo canônico deve nascer do zero, não como ajuste do Mirante.

Direção:

- história mais humana;
- pergunta dramática forte;
- 4 a 5 suspeitos plausíveis;
- pelo menos 2 falsos caminhos fortes;
- pergunta pública forte e concreta;
- E1 com hipótese boa, mas incompleta, sem pedir solução final;
- E2 que recontextualiza, não apenas confirma;
- critério de avanço diegético por envelope;
- motivação histórica conectada a consequência atual;
- guia do facilitador operacional;
- mecânica investigativa diferente do Mirante.

Arquivo de planejamento:

- `docs/canonical_plans/PLANO_CANONICO_INTERMEDIARIO.md`

Só gerar `examples/caso_canonico_intermediario.json` depois que o plano Markdown estiver aprovado.

### Fase D — Biblioteca canônica

Após o novo Intermediário, evoluir para:

- `caso_canonico_avancado.json`;
- `caso_canonico_especialista.json`;
- `caso_canonico_mestre.json`.

Cada canônico deve testar uma mecânica investigativa diferente, não apenas uma dificuldade maior.

### Fase E — Inteligência editorial

Após existirem vários casos:

- benchmark report;
- comparador de casos;
- calibragem de dificuldade;
- validação de progressão;
- validação de red herrings;
- guardrail automático contra “voz do autor” em documentos de jogador;
- refinamento futuro das heurísticas sobre `conflito_central`, `objetivos_por_envelope` e `guia_operacional`, que já são campos estruturados do blueprint.

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

Validator strict:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
python -m generator.validator examples/caso_canonico_intermediario.json --strict
```

Build do pacote:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Instalação do browser Playwright, se necessário:

```bash
python -m playwright install chromium
```

## Sistema visual documental v1

Foi criada a base P0 do sistema visual documental em `templates/styles/document_system.css`, injetada automaticamente pelo renderer nos HTMLs finais. A camada adiciona tokens tipográficos, escala de cinzas, espaçamentos, bordas, cabeçalho/rodapé documental para documentos de jogador, classes por tipo e família documental, padrões de tabela, carimbos opcionais e regras de impressão P&B.

Essa mudança é sistêmica e não altera narrativa, solução, dificuldade nem mapas dos canônicos. O objetivo é aumentar a credibilidade material dos PDFs antes de novas rodadas de playtest, mantendo evidência bruta nos documentos de jogador e separação visual do material confidencial do facilitador.


## Printables apartados P1

O pacote agora pode gerar cartões recortáveis de personagem, local e objeto como apoio de mesa separado dos envelopes. Os canônicos Iniciante e Intermediário receberam cartões públicos e não interpretativos; os cartões não alteram solução, dificuldade ou cadeia de evidência.

Os PDFs são gravados em `printables/`, aparecem no `manifest.json` e no `print_manifest.json`, e o guia de impressão informa recorte, papel recomendado e separação em relação a envelopes, dicas e material confidencial do facilitador.

## Atualização P2 visual — plantas baixas

Foi adicionada uma camada P2 para mapas procedurais: `generator/floorplan_renderer.py`, template `templates/floorplan.html` e validações `MAP_*` no validator. O canônico Iniciante mantém seu mapa como documento de jogador do E1, agora com portas, janelas e câmeras modeladas explicitamente. O canônico Intermediário/Hotel Aurora permanece sem mapa.

O padrão está documentado em `docs/FLOORPLANS.md` e reforça A4 paisagem, P&B first, ausência de rotas/destaques de solução e separação correta no package builder/manifest.

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
- package builder;
- manifest;
- print manifest;
- Playwright como renderizador oficial;
- merge PDF com `pikepdf`;
- mapa procedural canônico;
- suporte a assinatura/rubrica por perfil de personagem no blueprint;
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
- assinaturas puramente textuais.

## Caso canônico atual

O caso canônico atual é:

- **O Desvio da Reserva Mirante**
- Arquivo: `examples/caso_canonico_iniciante.json`
- Dificuldade editorial atual: **Iniciante**

O caso foi rebaixado de Intermediário para Iniciante por decisão editorial e confirmado pelo primeiro playtest como fácil demais para Intermediário.

Papel atual do caso:

- régua canônica Iniciante;
- referência técnica de build/package;
- fixture de integração;
- benchmark mínimo de qualidade visual/documental;
- exemplo de experiência introdutória.

Não tentar transformar o Mirante em Intermediário por ajustes incrementais. O próximo caso Intermediário deve nascer de nova arquitetura investigativa.

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
- o risco principal agora é gerar documentos bonitos para mistérios fracos ou óbvios;
- o próximo foco deve ser pipeline de design de caso e criação planejada do canônico Intermediário.

## Decisões recentes relevantes

### Caso canônico iniciante

O antigo caso canônico intermediário foi renomeado/rebaixado para `caso_canonico_iniciante.json`.

A partir de agora, referências canônicas devem apontar para esse arquivo, salvo quando o objetivo for explicitamente criar uma nova régua Intermediária.

### Assinaturas e rubricas

Assinatura/rubrica passou a ser característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica;
- o renderer deve gerar SVG com base nesse perfil;
- override SVG manual é permitido;
- fallback procedural continua disponível para compatibilidade;
- assinatura/rubrica não deve ser apenas nome digitado nem “iniciais + risco” genérico.

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
- plano Markdown antes de qualquer blueprint JSON;
- núcleo dramático;
- curva de suspeita;
- momentos de descoberta;
- riscos de obviedade;
- riscos de injustiça;
- mecânica investigativa principal.

### Fase C — Novo caso canônico Intermediário

O próximo canônico deve nascer do zero, não como ajuste do Mirante.

Direção:

- história mais humana;
- pergunta dramática forte;
- 4 a 5 suspeitos plausíveis;
- pelo menos 2 falsos caminhos fortes;
- E1 com hipótese boa, mas incompleta;
- E2 que recontextualiza, não apenas confirma;
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
- guardrail automático contra “voz do autor” em documentos de jogador.

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

Antes disso, validar que o framework gera casos realmente interessantes, intrigantes e divertidos.

## Comandos úteis

Testes:

```bash
pytest tests/ -q
```

Validator strict:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
```

Build do pacote:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output --strict
```

Instalação do browser Playwright, se necessário:

```bash
python -m playwright install chromium
```

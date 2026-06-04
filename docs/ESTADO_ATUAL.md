# Estado atual do Indiciário

Este documento registra a situação atual do projeto após as rodadas de hardening editorial, visual e técnico do caso canônico.

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

## Stack atual

Linguagem e estrutura:

- Python;
- Blueprint JSON;
- Schemas YAML;
- Validator;
- Package Builder.

Renderização e PDF:

- HTML;
- CSS;
- Playwright;
- Chromium;
- Playwright PDF.

Merge de PDFs:

- `pikepdf` como backend oficial;
- `pypdf` apenas como fallback.

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

O caso foi rebaixado de Intermediário para Iniciante por decisão editorial. A estrutura ficou mais adequada como caso introdutório, com orientação mais clara, mas ainda deve preservar investigação real.

Papel do caso canônico iniciante:

- referência narrativa;
- referência técnica;
- fixture de integração;
- benchmark de qualidade mínima;
- primeiro material de validação com jogadores.

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

## Playtest

O primeiro playtest real ainda é a prioridade.

Grupo previsto:

- Marcelo;
- esposa;
- filha de 11 anos.

Objetivo do playtest:

- validar diversão;
- validar clareza;
- validar solvabilidade percebida;
- observar uso dos envelopes;
- observar uso do mapa;
- avaliar utilidade das dicas;
- avaliar participação da criança;
- medir tempo real.

Após o playtest, preencher/atualizar dados como:

```json
"playtest": {
  "status": "playtestado_com_ajustes",
  "rodadas": 1,
  "tempo_real_medio": 0,
  "jogadores_teste": 3,
  "travamentos": [],
  "hipoteses_erradas": [],
  "ajustes_pos_teste": []
}
```

## Roadmap atual

### Fase A — Playtest real

Prioridade máxima.

Itens:

1. gerar pacote atualizado do caso canônico iniciante;
2. revisar visualmente o PDF final;
3. realizar o primeiro playtest real;
4. registrar métricas reais em `playtest_session.json` ou estrutura equivalente;
5. ajustar o caso com base em evidência real de mesa.

### Fase B — Biblioteca canônica

Após o primeiro playtest, criar novas réguas editoriais:

- `caso_canonico_intermediario.json`;
- `caso_canonico_avancado.json`;
- `caso_canonico_especialista.json`;
- `caso_canonico_mestre.json`.

A criação de novo caso intermediário deve nascer com ambiguidade estrutural desde o planejamento, não apenas pela remoção de dicas óbvias.

### Fase C — Inteligência editorial

Após existirem vários casos:

- benchmark report;
- comparador de casos;
- calibragem de dificuldade;
- validação de progressão;
- validação de red herrings;
- guardrail automático contra “voz do autor” em documentos de jogador.

### Fase D — Biblioteca visual

Expansão futura:

- hotel;
- museu;
- biblioteca;
- apartamento;
- galeria;
- escritório;
- plantas e documentos específicos por cenário.

Sempre manter mapas em landscape e evitar dependência obrigatória de geração de imagem por IA.

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

Antes disso, validar que o caso é divertido, claro e jogável.

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

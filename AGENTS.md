# AGENTS.md — Guia operacional para agentes de IA

Este arquivo orienta agentes de IA, como Codex, Claude Code, Copilot Workspace e similares, sobre como trabalhar neste repositório sem quebrar a direção editorial do Indiciário.

Leia este arquivo antes de executar qualquer tarefa.

## O que é o Indiciário

Indiciário é um framework para geração de mistérios investigativos jogáveis em grupo, em formato de dossiê com envelopes, documentos, pistas, dicas, guia do facilitador e PDFs finais.

Princípios do produto:

- offline first;
- sem QR code obrigatório;
- sem internet obrigatória;
- sem aplicativos externos;
- sem links externos como parte da solução;
- jogável em mesa, notebook, tablet ou impressão;
- foco em dedução, investigação e experiência de grupo.

Slogan atual:

> Todo caso deixa sinais.

## Estado atual do projeto

O framework está tecnicamente funcional. A prioridade atual é validar a experiência real com jogadores, não criar muitas features novas.

Caso canônico atual:

- título: **O Desvio da Reserva Mirante**;
- arquivo: `examples/caso_canonico_iniciante.json`;
- dificuldade editorial: **Iniciante**;
- função: referência narrativa, técnica, fixture de integração e primeiro material de playtest.

O antigo caso canônico intermediário foi rebaixado/renomeado para `caso_canonico_iniciante.json`. Não recrie nem referencie `caso_canonico_intermediario.json` salvo se a tarefa pedir explicitamente a criação de um novo caso Intermediário.

## Documentação obrigatória antes de alterar o projeto

Antes de alterar conteúdo, blueprint, templates, renderer, validator ou package builder, leia:

1. `README.md`
2. `docs/ESTADO_ATUAL.md`
3. `docs/DIRETRIZES_EDITORIAIS.md`
4. `docs/LLM_OPERATING_MANUAL.md`, se existir
5. `examples/caso_canonico_iniciante.json`, quando a tarefa tocar no caso canônico

## Stack atual

- Python;
- Blueprint JSON;
- Schemas YAML;
- templates HTML/CSS;
- Playwright/Chromium para renderização;
- Playwright PDF;
- `pikepdf` como backend oficial de merge;
- `pypdf` apenas fallback;
- pytest para testes;
- ruff para lint.

Não assuma que Telegram, Mercado Pago, dashboard, banco de dados ou multiusuário fazem parte da prioridade atual. Esses temas não devem ser implementados sem instrução explícita.

## Arquivos e responsabilidades

Use esta separação antes de mexer em qualquer coisa:

| Problema | Local provável |
|---|---|
| Conteúdo do caso, personagens, documentos, pistas | `examples/caso_canonico_iniciante.json` |
| Estrutura de dados | `generator/models.py` |
| Validação narrativa/estrutural | `generator/validator.py` |
| Renderização de dados em HTML/PDF | `generator/renderer.py` |
| Mapas e visuais procedurais | `generator/visual_procedural.py` |
| Templates de documentos | `templates/*.html` |
| Montagem de pacote final | `scripts.build_package` e módulos relacionados |
| Estado e diretrizes do produto | `docs/ESTADO_ATUAL.md`, `docs/DIRETRIZES_EDITORIAIS.md` |

Se a tarefa é editorial, prefira mudar o blueprint e/ou documentação. Não refatore código sem necessidade.

## Regra editorial central

Documento de jogador deve conter evidência bruta, não interpretação do autor.

Separação de papéis:

- documento do jogador mostra fatos do mundo da história;
- guia do facilitador explica significado;
- dica contextual destrava grupos;
- gabarito resolve;
- metadados internos podem usar linguagem analítica, mas não devem vazar para PDFs de jogador.

Nunca coloque em documento de jogador frases como:

- “compare com...”;
- “a confirmação depende de...”;
- “não prova sozinho...”;
- “o preço isolado não decide...”;
- “recibo, extrato e conversa interna...” como checklist;
- “red herring”, “ruído controlado”, “hipótese”, “gabarito”;
- referências a códigos de documentos como `E1-04` ou `E2-02` dentro de conteúdo diegético.

Essas expressões podem existir em guia do facilitador, dicas, QA, graph report, testes e metadados internos, mas não nos documentos de jogador.

## Mapa

Mapa do jogador deve ser uma planta baixa neutra.

Deve conter:

- ambientes;
- paredes;
- portas;
- janelas;
- câmeras neutras;
- nomes de ambientes;
- códigos de portas;
- norte e escala, se discretos.

Não deve conter:

- rota da peça;
- seta de solução;
- área crítica destacada;
- câmera offline;
- campo de visão;
- legenda que explique a investigação;
- cores fortes que apontem suspeita;
- texto explicando por que ninguém viu.

A Galeria/Vitrine interna do caso canônico deve ter acesso visual pelo corredor. Não pode depender de passagem por doca, depósito ou reserva técnica.

## Assinaturas e rubricas

Assinatura/rubrica é característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica;
- o renderer gera SVG com base nesse perfil;
- override SVG manual é permitido;
- fallback procedural existe para compatibilidade.

Não volte para assinatura como simples texto cursivo ou “iniciais + risco” igual para todos.

## E2 e documentos comerciais

Para o caso canônico iniciante:

- não usar mapa/quadro comparativo de propostas como documento de jogador;
- manter propostas/orçamentos individuais por empresa;
- contrato, recibo, extrato, e-mails e chats devem ser evidências separadas;
- o jogador deve comparar porque está investigando, não porque um documento instrui a comparação.

Orçamento deve parecer documento real de uma empresa, não síntese do puzzle.

## O que não reabrir sem evidência nova

Não reabra estes temas sem evidência concreta em PDF/teste/playtest:

- placeholders residuais como `COPIA`;
- PDFs consolidados em branco;
- merge oficial com `pikepdf`;
- Playwright como renderizador oficial;
- caso canônico atual como Iniciante;
- remoção de E2-03 como quadro comparativo do jogador;
- mapa sem rota/área crítica/câmera offline;
- assinatura/rubrica como atributo de personagem.

## Prioridade atual

Prioridade máxima:

1. gerar pacote atualizado do caso canônico iniciante;
2. revisar visualmente o PDF final;
3. realizar o primeiro playtest real;
4. registrar travamentos, hipóteses erradas, tempo real e diversão percebida;
5. só depois decidir ajustes estruturais ou criação de novo caso canônico Intermediário.

Não priorizar agora:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- agentes autônomos;
- IA gerando imagens.

## Comandos obrigatórios

Testes:

```bash
pytest tests/ -q
```

Lint:

```bash
ruff check generator/
```

Validator strict do caso canônico:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
```

Build do pacote:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output --strict
```

Se Playwright/Chromium não estiver instalado:

```bash
python -m playwright install chromium
```

Se o build falhar apenas por ausência de Chromium no ambiente, registre isso explicitamente no relatório da PR.

## Critério de tarefa concluída

Uma tarefa só está concluída quando:

- `pytest tests/ -q` passa, ou a falha é explicada como limitação de ambiente;
- `ruff check generator/` passa quando a tarefa toca em Python;
- `python generator/validator.py examples/caso_canonico_iniciante.json --strict` passa quando a tarefa toca no blueprint;
- se a tarefa altera pacote/renderização, o build é tentado;
- mudanças editoriais não vazam gabarito para documentos de jogador;
- a PR explica claramente o que mudou, por que mudou e quais comandos foram executados.

## Como abrir PRs

Mantenha PRs pequenas e focadas.

Bons escopos:

- “corrigir linguagem de E2”;
- “ajustar mapa da galeria”;
- “adicionar perfil de assinatura por personagem”;
- “atualizar documentação”.

Escopos ruins:

- “melhorar tudo”;
- “refatorar framework inteiro”;
- “criar novo caso e mudar renderer e validator ao mesmo tempo”.

## Quando parar

Se a tarefa tocar no caso canônico e a mudança não for necessária para o primeiro playtest, prefira registrar como próximo passo em documentação, não implementar agora.

O primeiro playtest vale mais que várias PRs teóricas.

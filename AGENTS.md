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

O framework está tecnicamente funcional e já possui duas réguas canônicas validadas. A prioridade atual é gerar baseline visual real dos PDFs com Playwright/Chromium, revisar os pacotes canônicos e corrigir apenas falhas comprovadas de layout/renderização antes de novo playtest.

Casos canônicos atuais:

1. **O Desvio da Reserva Mirante**
   - arquivo: `examples/caso_canonico_iniciante.json`;
   - dificuldade editorial: **Iniciante**;
   - função: régua canônica iniciante, referência narrativa/técnica e fixture de integração.

2. **O Último Brinde do Hotel Aurora**
   - arquivo: `examples/caso_canonico_intermediario.json`;
   - dificuldade editorial: **Intermediário**;
   - função: régua canônica intermediária validada após playtest e refinamentos;
   - decisão importante: **Hotel Aurora deve continuar sem mapa**, salvo evidência nova de playtest ou instrução explícita.

Não rebaixe, ignore ou recrie o Hotel Aurora como se fosse arquivo legado. Ele faz parte do estado atual do projeto.

## Documentação obrigatória antes de alterar o projeto

Antes de alterar conteúdo, blueprint, templates, renderer, validator ou package builder, leia:

1. `README.md`
2. `docs/ESTADO_ATUAL.md`
3. `docs/ROADMAP.md`
4. `docs/DIRETRIZES_EDITORIAIS.md`
5. `docs/LLM_OPERATING_MANUAL.md`, se existir
6. `docs/VISUAL_SYSTEM.md`, quando a tarefa tocar visual/renderização
7. `docs/PRINTABLES.md`, quando a tarefa tocar cartões/apoios de mesa
8. `docs/FLOORPLANS.md`, quando a tarefa tocar mapas/planta baixa
9. `docs/SIGNATURES_AND_HANDWRITING.md`, quando a tarefa tocar assinaturas/rubricas/manuscritos
10. `examples/caso_canonico_iniciante.json`, quando a tarefa tocar o canônico Iniciante
11. `examples/caso_canonico_intermediario.json`, quando a tarefa tocar o canônico Intermediário ou baseline visual completo

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
| Conteúdo do caso iniciante, personagens, documentos, pistas | `examples/caso_canonico_iniciante.json` |
| Conteúdo do caso intermediário, personagens, documentos, pistas | `examples/caso_canonico_intermediario.json` |
| Estrutura de dados | `generator/models.py` |
| Validação narrativa/estrutural | `generator/validator.py` |
| Renderização de dados em HTML/PDF | `generator/renderer.py` |
| Mapas e visuais procedurais | `generator/visual_procedural.py`, `generator/floorplan_renderer.py` |
| Printables/cartões de apoio | `generator/printable_cards.py`, `templates/printable_cards.html` |
| Assinaturas/rubricas/manuscritos | `generator/signature_renderer.py` |
| Templates de documentos | `templates/*.html` |
| Montagem de pacote final | `scripts.build_package` e módulos relacionados |
| Estado e diretrizes do produto | `docs/ESTADO_ATUAL.md`, `docs/ROADMAP.md`, `docs/DIRETRIZES_EDITORIAIS.md` |

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

Mapas são plantas operacionais, não pistas visuais comentadas.

Para o canônico Intermediário **O Último Brinde do Hotel Aurora**, mantenha a decisão validada: **sem mapa**.

## Assinaturas e rubricas

Assinatura/rubrica é característica editorial do personagem no blueprint.

Direção atual:

- cada personagem pode ter perfil de assinatura/rubrica;
- o renderer gera SVG com base nesse perfil;
- override SVG manual é permitido;
- fallback procedural existe para compatibilidade.

Não volte para assinatura como simples texto cursivo ou “iniciais + risco” igual para todos.

## E2 e documentos comerciais

Para casos com documentos comerciais, financeiros, logísticos ou administrativos:

- não usar quadro comparativo como documento de jogador quando ele funcionar como síntese do puzzle;
- manter propostas, orçamentos, recibos, contratos, extratos, e-mails e chats como evidências separadas quando isso aumentar a investigação;
- o jogador deve comparar porque está investigando, não porque um documento instrui a comparação.

Documento comercial deve parecer documento real de uma empresa, não síntese do puzzle.

## O que não reabrir sem evidência nova

Não reabra estes temas sem evidência concreta em PDF/teste/playtest:

- placeholders residuais como `COPIA`;
- PDFs consolidados em branco;
- merge oficial com `pikepdf`;
- Playwright como renderizador oficial;
- existência dos dois canônicos atuais: Iniciante/Mirante e Intermediário/Aurora;
- Hotel Aurora sem mapa;
- remoção de quadros comparativos que funcionem como dica/gabarito para jogador;
- mapa sem rota/área crítica/câmera offline;
- assinatura/rubrica como atributo de personagem;
- cartões como apoio de mesa, não evidência principal.

## Prioridade atual

Prioridade máxima:

1. gerar baseline visual real dos dois canônicos com Playwright/Chromium;
2. revisar visualmente os PDFs finais, manifests e print manifests;
3. corrigir somente falhas comprovadas de layout/renderização;
4. realizar novo playtest do Intermediário com pessoas novas;
5. registrar travamentos, hipóteses erradas, tempo real, uso de dicas/cartões e diversão percebida;
6. só depois decidir ajustes finos ou planejar o canônico Avançado.

Não priorizar agora:

- marketplace;
- dashboard web;
- banco de dados;
- editor visual;
- multiusuário;
- Telegram comercial;
- agentes autônomos;
- geração em massa;
- pagamento;
- IA gerando imagens;
- canônico Avançado antes do baseline visual e novo playtest.

## Comandos obrigatórios

Testes:

```bash
pytest tests/ -q
```

Lint:

```bash
ruff check generator/
```

Validator strict dos canônicos:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
python generator/validator.py examples/caso_canonico_intermediario.json --strict
```

Build dos pacotes canônicos:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Se Playwright/Chromium não estiver instalado:

```bash
python -m playwright install chromium
```

Se o build falhar apenas por ausência de Chromium no ambiente, registre isso explicitamente no relatório da PR. Não use build fake como prova de baseline visual real.

## Critério de tarefa concluída

Uma tarefa só está concluída quando:

- `pytest tests/ -q` passa, ou a falha é explicada como limitação de ambiente;
- `ruff check generator/` passa quando a tarefa toca em Python;
- validators strict dos canônicos passam quando a tarefa toca em blueprint, documentação de estado, baseline ou pacote;
- se a tarefa altera pacote/renderização, o build real é tentado;
- se o build real não for possível por limitação de ambiente, isso fica explícito na PR;
- mudanças editoriais não vazam gabarito para documentos de jogador;
- a PR explica claramente o que mudou, por que mudou e quais comandos foram executados.

## Como abrir PRs

Mantenha PRs pequenas e focadas.

Bons escopos:

- “corrigir linguagem de E2”;
- “ajustar mapa do canônico iniciante”;
- “manter Hotel Aurora sem mapa e atualizar docs”;
- “adicionar perfil de assinatura por personagem”;
- “atualizar documentação”;
- “registrar baseline visual”.

Escopos ruins:

- “melhorar tudo”;
- “refatorar framework inteiro”;
- “criar novo caso e mudar renderer e validator ao mesmo tempo”;
- “criar canônico Avançado antes do baseline visual”.

## Quando parar

Se a tarefa tocar narrativa, dificuldade ou solução dos canônicos e a mudança não for necessária por evidência de PDF/teste/playtest, prefira registrar como próximo passo em documentação, não implementar agora.

Baseline visual real e playtest valem mais que várias PRs teóricas.
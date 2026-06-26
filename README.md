# Indiciário

Indiciário é um framework para geração de jogos de investigação offline em formato de dossiê com envelopes. O projeto combina blueprints estruturados, validação narrativa, templates HTML/CSS, renderização com Playwright/Chromium e montagem de PDFs para produzir casos jogáveis sem depender de QR code, aplicativos ou links externos.

Slogan atual:

> Todo caso deixa sinais.

## Estado atual

O framework está tecnicamente funcional, possui duas réguas canônicas validadas por playtest e consolidou a entrega inicial do fluxo operacional Indiciário 2.0.

Réguas canônicas validadas por playtest:

- **O Desvio da Reserva Mirante** — `examples/caso_canonico_iniciante.json` — régua **Iniciante**.
- **O Último Brinde do Hotel Aurora** — `examples/caso_canonico_intermediario.json` — régua **Intermediária** validada após playtest e refinamento.

Demais casos em `examples/` (existem, mas ainda não validados por playtest):

- **O Recado da Sala de Leitura** — `examples/caso_canonico_iniciante_b.json` — Iniciante (baseline visual + CI).
- **Plantão Sem Rosto** — `examples/caso_canonico_intermediario_ii.json` — Intermediário (plano editorial).
- **Desvio de Fundos na Acelerada Pagamentos** — `examples/caso_fintech.json` — Avançado (pipeline E2E).

Roster e status completos: [`docs/ESTADO_ATUAL.md`](docs/ESTADO_ATUAL.md).

Fluxo operacional oficial:

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library / templates
→ Build Package
→ Baseline visual real
→ Playtest
→ Ajustes finos
```

Use os dois arquivos canônicos como referência em testes, scripts, validações canônicas e geração de pacote.

## Documentação principal

- [`docs/INDICE_DOCUMENTACAO.md`](docs/INDICE_DOCUMENTACAO.md): índice de toda a documentação — o que cada doc serve, quando é lido e quando deve ser atualizado.
- [`docs/ESTADO_ATUAL.md`](docs/ESTADO_ATUAL.md): visão atual do produto, stack, decisões recentes, caso canônico e próximos passos.
- [`docs/DIRETRIZES_EDITORIAIS.md`](docs/DIRETRIZES_EDITORIAIS.md): regras editoriais para evitar documentos com dicas óbvias, voz do autor ou gabarito disfarçado.
- [`docs/CASE_DESIGN_PIPELINE.md`](docs/CASE_DESIGN_PIPELINE.md): pipeline para planejar pergunta pública, progressão por envelope, motivação e risco antes do blueprint.
- [`docs/CASE_KERNEL.md`](docs/CASE_KERNEL.md): camada de extração do DNA investigativo a partir do blueprint.
- [`docs/CASE_REVIEW.md`](docs/CASE_REVIEW.md): relatório editorial automático para revisar o núcleo antes do pacote.
- [`docs/VISUAL_LIBRARY_2_0.md`](docs/VISUAL_LIBRARY_2_0.md): biblioteca visual procedural mínima para plantas-base estruturadas.
- [`docs/BLUEPRINT_AUTHORING_GUIDE.md`](docs/BLUEPRINT_AUTHORING_GUIDE.md): contrato mínimo de autoria para blueprints jogáveis, com critérios de avanço, dicas e guia do facilitador operacional.
- [`docs/LLM_OPERATING_MANUAL.md`](docs/LLM_OPERATING_MANUAL.md): manual para LLMs criarem, revisarem e corrigirem casos sem repetir falhas editoriais.
- [`docs/AGENT_SKILLS.md`](docs/AGENT_SKILLS.md): playbook de skills para agentes/Codex, adaptado ao fluxo do Indiciário.

## Comandos principais

Validação estrutural e editorial do blueprint:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
python generator/validator.py examples/caso_canonico_intermediario.json --strict
```

Testes automatizados:

```bash
pytest tests/ -q
```

Geração do pacote jogável:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Se o ambiente ainda não tiver browser instalado, instale o Chromium usado pelo Playwright:

```bash
python -m playwright install chromium
```


## Automação de CI

O repositório possui dois workflows em `.github/workflows/`:

- **CI** (`ci.yml`): validação rápida em `pull_request` e em `push` para `main`. Instala dependências Python, executa `ruff check generator/ scripts/ tests/`, `pytest tests/ -q`, validators strict dos canônicos Iniciante, Intermediário e Iniciante B, Case Review em Markdown para os três casos e `visual_sanity_check` do Iniciante B sem instalar Chromium nem gerar PDFs.
- **Visual Build** (`visual-build.yml`): workflow mais pesado para `workflow_dispatch` e para PRs que alterem exemplos, templates, geradores, scripts, baselines visuais ou `requirements.txt`. Instala Playwright/Chromium, gera o pacote real do Iniciante B e publica o artifact `iniciante-b-visual-package` com PDFs, manifests, relatórios e HTML debug existentes em `output/iniciante_b/**`.

Para rodar manualmente o build visual, abra a aba **Actions** no GitHub, escolha **Visual Build** e use **Run workflow**. Quando o job passar, baixe o artifact na página da execução. Esse artifact apoia a revisão de baseline visual, mas não substitui inspeção humana dos PDFs nem playtest.

## Prioridade atual

A prioridade do projeto não é criar novas features nem novo caso imediatamente. O foco é:

1. operar casos pelo fluxo Blueprint → Case Kernel → Case Review → Visual Library/templates → Build Package;
2. gerar baseline visual real dos dois canônicos com Playwright/Chromium;
3. revisar visualmente PDFs finais, manifests e print manifests;
4. realizar novo playtest do Intermediário com pessoas novas;
5. registrar travamentos, hipóteses erradas, tempo real, uso de dicas/cartões e diversão percebida;
6. só depois decidir ajustes finos ou planejar o canônico Avançado.
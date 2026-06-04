# Indiciário

Indiciário é um framework para geração de jogos de investigação offline em formato de dossiê com envelopes. O projeto combina blueprints estruturados, validação narrativa, templates HTML/CSS, renderização com Playwright/Chromium e montagem de PDFs para produzir casos jogáveis sem depender de QR code, aplicativos ou links externos.

Slogan atual:

> Todo caso deixa sinais.

## Estado atual

O framework está tecnicamente funcional e o foco atual é validar a experiência real de jogo.

O caso canônico atual é **“O Desvio da Reserva Mirante”**, reclassificado editorialmente como **Iniciante**.

Arquivo principal:

- `examples/caso_canonico_iniciante.json`

Use este arquivo como referência principal em testes, scripts, validações canônicas e geração de pacote.

## Documentação principal

- [`docs/ESTADO_ATUAL.md`](docs/ESTADO_ATUAL.md): visão atual do produto, stack, decisões recentes, caso canônico e próximos passos.
- [`docs/DIRETRIZES_EDITORIAIS.md`](docs/DIRETRIZES_EDITORIAIS.md): regras editoriais para evitar documentos com dicas óbvias, voz do autor ou gabarito disfarçado.

## Comandos principais

Validação estrutural e editorial do blueprint:

```bash
python generator/validator.py examples/caso_canonico_iniciante.json --strict
```

Testes automatizados:

```bash
pytest tests/ -q
```

Geração do pacote jogável:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output --strict
```

Se o ambiente ainda não tiver browser instalado, instale o Chromium usado pelo Playwright:

```bash
python -m playwright install chromium
```

## Prioridade atual

A prioridade do projeto não é criar novas features nem novo caso imediatamente. O foco é:

1. gerar o pacote atualizado do caso canônico iniciante;
2. revisar visualmente o PDF final;
3. realizar o primeiro playtest real;
4. registrar travamentos, hipóteses erradas, tempo real e pontos de diversão;
5. só depois decidir ajustes estruturais ou criação de novo caso canônico intermediário.

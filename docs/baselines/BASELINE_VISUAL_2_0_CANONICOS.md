# Baseline visual 2.0 — Canônicos

## 1. Data e ambiente

- Data da execução: 2026-06-07.
- Sistema operacional: Ubuntu 24.04.4 LTS (Noble Numbat), kernel Linux 6.12.47, arquitetura x86_64.
- Python: 3.12.13.
- Playwright: 1.60.0 instalado como pacote Python.
- Chromium/Chrome de sistema: não encontrado por `command -v chromium || command -v chromium-browser || command -v google-chrome || command -v chrome || true`.
- Chromium do Playwright: não disponível no cache local; o executável esperado era `/root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
- Tentativa de instalar Chromium via Playwright: executada, mas bloqueada por HTTP 403 ao baixar Chrome for Testing `148.0.7778.96`.
- Branch usada: `work`.
- Commit base antes deste registro: `78d697e` (`Registrar tentativa de baseline visual real dos canônicos (2026-06-07)`).
- Escopo: registro documental/de baseline visual dos dois canônicos, sem correção visual e sem alteração de canônicos, narrativa, solução, dificuldade, documentos, templates, renderers, mapas, validator, Case Kernel, Case Review ou package builder.

Casos no escopo:

- `examples/caso_canonico_iniciante.json` — **O Desvio da Reserva Mirante**, régua canônica **Iniciante**.
- `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora**, régua canônica **Intermediária**.

Decisões editoriais confirmadas neste registro:

- Mirante continua sendo a régua Iniciante.
- Mirante continua usando a planta estruturada v2 por `build_mirante_planta()`.
- Hotel Aurora continua sendo a régua Intermediária.
- Hotel Aurora deve continuar sem mapa.

## 2. Comandos executados

| Comando | Resultado |
|---|---|
| `pytest tests/ -q` | **OK** — 314 testes passaram e 1 teste foi pulado. |
| `ruff check generator/` | **OK** — `All checks passed!`. |
| `python generator/validator.py examples/caso_canonico_iniciante.json --strict` | **OK** — risco baixo; pode gerar; 0 críticos; 0 moderados; 12 avisos. |
| `python generator/validator.py examples/caso_canonico_intermediario.json --strict` | **OK** — risco baixo; pode gerar; 0 críticos; 0 moderados; 7 avisos. |
| `python -m scripts.case_review examples/caso_canonico_iniciante.json --format markdown` | **OK** — relatório gerado; status `READY_FOR_BASELINE`; 0 críticos; 2 warnings. |
| `python -m scripts.case_review examples/caso_canonico_intermediario.json --format markdown` | **OK** — relatório gerado; status `READY_FOR_PLAYTEST`; 0 críticos; 0 warnings. |
| `python -m playwright install chromium` | **Falhou por limitação de ambiente** — download do Chrome for Testing `148.0.7778.96` retornou HTTP 403 em todas as tentativas. |
| `command -v chromium \|\| command -v chromium-browser \|\| command -v google-chrome \|\| command -v chrome \|\| true` | **Atenção** — nenhum Chromium/Chrome de sistema encontrado. |
| `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict` | **Falhou por limitação de ambiente** — executável Chromium do Playwright ausente. |
| `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict` | **Falhou por limitação de ambiente** — executável Chromium do Playwright ausente. |

## 3. Build Package

### Iniciante / Mirante

- Caso: `examples/caso_canonico_iniciante.json` — **O Desvio da Reserva Mirante**.
- Comando: `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict`.
- Resultado do build: **falhou por limitação de ambiente**.
- Caminho do output: `output/iniciante`.
- PDFs gerados: **0**.
- Manifest gerado: **não**.
- Print manifest gerado: **não**.
- Quantidade de arquivos gerados no output: **1** arquivo parcial (`html_debug/E1-01.html`).
- Observações:
  - A falha ocorreu ao tentar renderizar `E1-01 (05_carta.html)` em PDF.
  - Mensagem principal: `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
  - O artefato HTML parcial não foi usado como substituto de revisão visual real.
  - Não houve build fake.

### Intermediário / Aurora

- Caso: `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora**.
- Comando: `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict`.
- Resultado do build: **falhou por limitação de ambiente**.
- Caminho do output: `output/intermediario`.
- PDFs gerados: **0**.
- Manifest gerado: **não**.
- Print manifest gerado: **não**.
- Quantidade de arquivos gerados no output: **1** arquivo parcial (`html_debug/E1-01.html`).
- Observações:
  - A falha ocorreu ao tentar renderizar `E1-01 (05_carta.html)` em PDF.
  - Mensagem principal: `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
  - O artefato HTML parcial não foi usado como substituto de revisão visual real.
  - Não houve build fake.

## 4. Revisão visual — Mirante

Como o pacote real do Mirante não foi gerado, a revisão visual real dos PDFs não pôde ser executada. A classificação abaixo registra o estado da revisão nesta execução, sem inferir aprovação visual a partir de HTML parcial.

| Item | Classificação | Registro |
|---|---|---|
| Capa | problema | PDF não gerado; revisão visual real não executável. |
| Envelopes | problema | PDFs não gerados; revisão visual real não executável. |
| Documentos do jogador | problema | PDFs não gerados; revisão visual real não executável. |
| E-mail | problema | PDF não gerado; revisão visual real não executável. |
| WhatsApp | problema | PDF não gerado; revisão visual real não executável. |
| Registros/logs | problema | PDFs não gerados; revisão visual real não executável. |
| Mapa v2 | problema | PDF não gerado; não foi possível validar visualmente a planta v2 de `build_mirante_planta()`. |
| Pátio externo | problema | Não validado porque o mapa/PDF não foi gerado. |
| Portão | problema | Não validado porque o mapa/PDF não foi gerado. |
| Muro/perímetro | problema | Não validado porque o mapa/PDF não foi gerado. |
| Posto de controle | problema | Não validado porque o mapa/PDF não foi gerado. |
| Portas com cartão | problema | Não validado porque o mapa/PDF não foi gerado. |
| Assinaturas/rubricas | problema | PDFs não gerados; revisão visual real não executável. |
| Cartões apartados | problema | PDFs não gerados; revisão visual real não executável. |
| Guia do facilitador | problema | PDF não gerado; revisão visual real não executável. |
| Dicas | problema | PDFs não gerados; revisão visual real não executável. |
| Guia de impressão | problema | Não gerado; revisão não executável. |
| Manifest | problema | `manifest.json` não gerado. |
| Print manifest | problema | `print_manifest.json` não gerado. |

## 5. Revisão visual — Aurora

Como o pacote real do Aurora não foi gerado, a revisão visual real dos PDFs não pôde ser executada. A classificação abaixo registra o estado da revisão nesta execução, sem inferir aprovação visual a partir de HTML parcial.

| Item | Classificação | Registro |
|---|---|---|
| Capa | problema | PDF não gerado; revisão visual real não executável. |
| Envelopes | problema | PDFs não gerados; revisão visual real não executável. |
| Documentos do jogador | problema | PDFs não gerados; revisão visual real não executável. |
| E-mails | problema | PDFs não gerados; revisão visual real não executável. |
| Chats | problema | PDFs não gerados; revisão visual real não executável. |
| Registros/tabelas | problema | PDFs não gerados; revisão visual real não executável. |
| Assinaturas/rubricas | problema | PDFs não gerados; revisão visual real não executável. |
| Cartões apartados | problema | PDFs não gerados; revisão visual real não executável. |
| Guia do facilitador | problema | PDF não gerado; revisão visual real não executável. |
| Dicas | problema | PDFs não gerados; revisão visual real não executável. |
| Guia de impressão | problema | Não gerado; revisão não executável. |
| Manifest | problema | `manifest.json` não gerado. |
| Print manifest | problema | `print_manifest.json` não gerado. |
| Confirmação de que continua sem mapa | atenção | Decisão editorial confirmada neste registro; confirmação visual do pacote final não executável porque o build não gerou PDFs/manifests. |

## 6. Pendências encontradas

### Bloqueantes

1. Provisionar Chromium/Playwright funcional no ambiente de baseline. Sem o browser, o package builder não gera PDFs reais, `manifest.json` nem `print_manifest.json`.
2. Reexecutar os builds reais dos dois canônicos após provisionar Chromium:
   - `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict`
   - `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict`
3. Reexecutar a revisão visual real somente sobre PDFs/manifests gerados por Playwright/Chromium, sem usar build fake.

### Importantes

1. Revisar visualmente o mapa v2 do Mirante, incluindo pátio externo, portão, muro/perímetro, posto de controle e portas com cartão, assim que o PDF real for gerado.
2. Confirmar visualmente, no pacote final do Aurora, que o caso permanece sem mapa.
3. Revisar `manifest.json` e `print_manifest.json` dos dois pacotes após geração real.

### Cosméticos

- Nenhuma pendência cosmética foi identificada nesta execução, porque os PDFs finais não foram gerados e a revisão visual real não foi executável.

## 7. Decisão final

**Baseline visual não executado por limitação de ambiente.**

Justificativa: os controles técnicos prévios passaram, mas o build package real dos dois canônicos falhou por ausência de Chromium/Playwright funcional. Como não foram gerados PDFs finais, manifest nem print manifest, não há baseline visual real a aprovar nesta execução.

## Confirmação de restrições

- Nenhum canônico foi alterado.
- Nenhuma narrativa, solução, dificuldade, documento, template, renderer, mapa, validator, Case Kernel, Case Review ou package builder foi alterado.
- Problemas encontrados foram documentados como pendências; nenhuma correção visual foi feita nesta PR.

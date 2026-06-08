# Baseline visual 2.0 dos canônicos

## 1. Data e ambiente

- Data da execução: 2026-06-07.
- Sistema operacional: Linux `0aa764fcfba2 6.12.47 #1 SMP Mon Oct 27 10:01:15 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux`.
- Python: `Python 3.12.13`.
- Branch: `work`.
- Commit base usado na execução: `3b3e6a1`.
- Playwright: pacote Python disponível, versão `1.60.0`.
- Chromium/Playwright browser: **não disponível para execução real**.
  - O import de Playwright passou.
  - O build falhou porque o executável esperado não existia em `/root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
  - A tentativa de instalar Chromium com `python -m playwright install chromium` falhou por bloqueio HTTP `403 Forbidden` no download.
  - A tentativa de instalar Chromium via `apt-get` também falhou por bloqueio HTTP `403 Forbidden` nos repositórios Ubuntu.

## 2. Comandos executados

| Comando | Resultado |
|---|---|
| `pytest tests/ -q` | **passou** — `314 passed, 1 skipped in 27.04s`. |
| `ruff check generator/` | **passou** — `All checks passed!`. |
| `python generator/validator.py examples/caso_canonico_iniciante.json --strict` | **passou** — risco baixo, pode gerar, 0 críticos, 0 moderados, 12 avisos. |
| `python generator/validator.py examples/caso_canonico_intermediario.json --strict` | **passou** — risco baixo, pode gerar, 0 críticos, 0 moderados, 7 avisos. |
| `python -m scripts.case_review examples/caso_canonico_iniciante.json --format markdown` | **passou** — status `READY_FOR_BASELINE`, 0 críticos, 2 warnings. |
| `python -m scripts.case_review examples/caso_canonico_intermediario.json --format markdown` | **passou** — status `READY_FOR_PLAYTEST`, 0 críticos, 0 warnings. |
| `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict` | **falhou por limitação de ambiente** — Chromium/headless shell não instalado. |
| `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict` | **falhou por limitação de ambiente** — Chromium/headless shell não instalado. |
| `python -m playwright install chromium` | **falhou por limitação de ambiente/rede** — download retornou `403 Forbidden`. |
| `apt-get update && apt-get install -y chromium` | **falhou por limitação de ambiente/rede** — repositórios Ubuntu retornaram `403 Forbidden`. |

## 3. Build Package

### Iniciante / Mirante

- Caso: `examples/caso_canonico_iniciante.json`.
- Régua: Iniciante.
- Título: **O Desvio da Reserva Mirante**.
- Build: **falhou por limitação de ambiente**.
- Caminho de output solicitado: `output/iniciante`.
- Caminho parcial criado: `output/iniciante/o-desvio-da-reserva-mirante/html_debug/E1-01.html`.
- PDFs gerados: **0**.
- Manifest gerado: **não**.
- Print manifest gerado: **não**.
- Quantidade de arquivos gerados no output solicitado: **1 arquivo parcial de debug HTML**.
- Observações:
  - O pacote não chegou à etapa de baseline visual real porque o renderer não conseguiu abrir Chromium.
  - A planta v2 do Mirante não pôde ser revisada em PDF nesta execução.
  - Nenhum canônico foi alterado.

### Intermediário / Aurora

- Caso: `examples/caso_canonico_intermediario.json`.
- Régua: Intermediária.
- Título: **O Último Brinde do Hotel Aurora**.
- Build: **falhou por limitação de ambiente**.
- Caminho de output solicitado: `output/intermediario`.
- Caminho parcial criado: `output/intermediario/o-ultimo-brinde-do-hotel-aurora/html_debug/E1-01.html`.
- PDFs gerados: **0**.
- Manifest gerado: **não**.
- Print manifest gerado: **não**.
- Quantidade de arquivos gerados no output solicitado: **1 arquivo parcial de debug HTML**.
- Observações:
  - O pacote não chegou à etapa de baseline visual real porque o renderer não conseguiu abrir Chromium.
  - O Hotel Aurora continua registrado como canônico Intermediário e sem mapa.
  - Nenhum canônico foi alterado.

## 4. Revisão visual — Mirante

Como os PDFs reais não foram gerados, a revisão visual abaixo registra o estado de execução desta PR. Os itens não indicam falhas visuais comprovadas do material; indicam impossibilidade de inspeção visual real neste ambiente.

| Item | Classificação | Registro |
|---|---|---|
| Capa | atenção | Não revisada em PDF real; build bloqueado por ausência de Chromium. |
| Envelopes | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Documentos do jogador | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| E-mail | atenção | Não revisado em PDF real; build bloqueado por ausência de Chromium. |
| WhatsApp | atenção | Não revisado em PDF real; build bloqueado por ausência de Chromium. |
| Registros/logs | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Mapa v2 | atenção | Não revisado em PDF real; Mirante deve continuar usando `build_mirante_planta()`. |
| Pátio externo | atenção | Não revisado em PDF real; depende do mapa v2 gerado no pacote. |
| Portão | atenção | Não revisado em PDF real; depende do mapa v2 gerado no pacote. |
| Muro/perímetro | atenção | Não revisado em PDF real; depende do mapa v2 gerado no pacote. |
| Posto de controle | atenção | Não revisado em PDF real; depende do mapa v2 gerado no pacote. |
| Portas com cartão | atenção | Não revisadas em PDF real; depende do mapa v2 gerado no pacote. |
| Assinaturas/rubricas | atenção | Não revisadas em PDF real; build bloqueado por ausência de Chromium. |
| Cartões apartados | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Guia do facilitador | atenção | Não revisado em PDF real; build bloqueado por ausência de Chromium. |
| Dicas | atenção | Não revisadas em PDF real; build bloqueado por ausência de Chromium. |
| Guia de impressão | atenção | Não gerado nesta execução. |
| Manifest | atenção | Não gerado nesta execução. |
| Print manifest | atenção | Não gerado nesta execução. |

## 5. Revisão visual — Aurora

Como os PDFs reais não foram gerados, a revisão visual abaixo registra o estado de execução desta PR. Os itens não indicam falhas visuais comprovadas do material; indicam impossibilidade de inspeção visual real neste ambiente.

| Item | Classificação | Registro |
|---|---|---|
| Capa | atenção | Não revisada em PDF real; build bloqueado por ausência de Chromium. |
| Envelopes | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Documentos do jogador | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| E-mails | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Chats | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Registros/tabelas | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Assinaturas/rubricas | atenção | Não revisadas em PDF real; build bloqueado por ausência de Chromium. |
| Cartões apartados | atenção | Não revisados em PDF real; build bloqueado por ausência de Chromium. |
| Guia do facilitador | atenção | Não revisado em PDF real; build bloqueado por ausência de Chromium. |
| Dicas | atenção | Não revisadas em PDF real; build bloqueado por ausência de Chromium. |
| Guia de impressão | atenção | Não gerado nesta execução. |
| Manifest | atenção | Não gerado nesta execução. |
| Print manifest | atenção | Não gerado nesta execução. |
| Confirmação de ausência de mapa | OK | Nenhuma alteração foi feita no canônico; a decisão editorial permanece: Hotel Aurora continua sem mapa. |

## 6. Pendências encontradas

### Bloqueantes

- Disponibilizar Chromium/headless shell compatível com Playwright no ambiente de baseline. Sem isso, não há pacote PDF real, manifest, print manifest nem revisão visual comprovada.
- Reexecutar os dois comandos de build package após instalar Chromium:
  - `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict`
  - `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict`
- Registrar nova revisão visual página a página dos PDFs reais gerados.

### Importantes

- Nenhuma pendência visual importante foi comprovada, porque a inspeção em PDF real não pôde ocorrer.
- Manter a confirmação explícita, na próxima execução bem-sucedida, de que o Mirante usa a planta v2 e de que o Hotel Aurora permanece sem mapa.

### Cosméticos

- Nenhuma pendência cosmética foi comprovada, porque a inspeção em PDF real não pôde ocorrer.

## 7. Decisão final

**Baseline visual não executado por limitação de ambiente.**

Motivo: Playwright está instalado como pacote Python, mas Chromium/headless shell não está disponível; a instalação pelo Playwright e a instalação via `apt-get` falharam por bloqueio HTTP `403 Forbidden`. Portanto, esta PR registra a tentativa completa, os resultados dos comandos obrigatórios possíveis, os builds bloqueados e a pendência operacional para executar o baseline visual real em ambiente com Chromium funcional.

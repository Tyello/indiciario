# Baseline operacional 2.0 — Canônicos

## Data

- Execução registrada em: 2026-06-07.
- Escopo: baseline operacional dos dois casos canônicos atuais do Indiciário 2.0, sem alteração de narrativa, solução, dificuldade, documentos, mapas, templates, renderers, package builder, validator, Case Kernel ou Case Review.

## Commits / branch

- Branch usada na execução: `work`.
- Commit base usado antes do registro documental: `fd48ef544ef23c04d0bd554104d3725f4ed50c70` (`fd48ef5`).
- Casos validados:
  - `examples/caso_canonico_iniciante.json` — **O Desvio da Reserva Mirante**, régua **Iniciante**.
  - `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora**, régua **Intermediária**.

## Comandos executados

| Comando | Resultado |
|---|---|
| `pytest tests/ -q` | Passou: 314 testes passaram e 1 teste foi pulado. |
| `ruff check generator/` | Passou: `All checks passed!`. |
| `python generator/validator.py examples/caso_canonico_iniciante.json --strict` | Passou: risco baixo, pode gerar, 0 críticos, 0 moderados, 12 avisos. |
| `python generator/validator.py examples/caso_canonico_intermediario.json --strict` | Passou: risco baixo, pode gerar, 0 críticos, 0 moderados, 7 avisos. |
| `python -m scripts.case_review examples/caso_canonico_iniciante.json --format markdown` | Passou: relatório gerado em Markdown; status `READY_FOR_BASELINE`; 0 críticos; 2 warnings. |
| `python -m scripts.case_review examples/caso_canonico_intermediario.json --format markdown` | Passou: relatório gerado em Markdown; status `READY_FOR_PLAYTEST`; 0 críticos; 0 warnings. |
| `python -m scripts.case_review examples/caso_canonico_iniciante.json --format markdown --output output/iniciante/case_review.md` | Passou: relatório local gerado em `output/iniciante/case_review.md`. |
| `python -m scripts.case_review examples/caso_canonico_intermediario.json --format markdown --output output/intermediario/case_review.md` | Passou: relatório local gerado em `output/intermediario/case_review.md`. |
| `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict` | Falhou por limitação de ambiente: Chromium/Playwright ausente no cache local. |
| `python -m playwright install chromium` | Falhou por limitação de ambiente/rede: download do Chromium retornou HTTP 403 em todas as tentativas. |
| `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict` | Falhou por limitação de ambiente: Chromium/Playwright ausente no cache local. |
| `command -v chromium \|\| command -v chromium-browser \|\| command -v google-chrome \|\| true` | Nenhum Chromium/Chrome de sistema encontrado. |

## Resultado dos testes

- `pytest tests/ -q`: **aprovado**.
- `ruff check generator/`: **aprovado**.
- Validators strict dos dois canônicos: **aprovados**.
- Case Review dos dois canônicos: **gerado e aprovado como relatório heurístico**.
- Build package real: **tentado, mas bloqueado por ausência de Chromium e falha de download do browser do Playwright**.
- Revisão de manifests, print manifests e PDFs finais: **não executável neste ambiente**, porque o build não chegou a gerar pacote, manifest, print manifest nem PDFs.

## Validator strict

### Iniciante — O Desvio da Reserva Mirante

- Resultado: **passou**.
- Risco: **Baixo**.
- Pode gerar: **SIM**.
- Críticos: **0**.
- Moderados: **0**.
- Avisos: **12**.
- Avisos relevantes:
  - `GP_003`: documentos `E1-09`, `E2-08`, `E2-09`, `E2-10`, `E2-11` e `E2-12` não participam de contratos de evidência.
  - `GP_004`: contrato `C-E1-ABERTURA` não é obrigatório nem final.
  - `AUTO_001`: há logs técnicos sem glossário.
  - `PT_001`: volume documental acima do recomendado para a dificuldade iniciante: observado 20 documentos.
  - `PT_003`: suspeitos acima do recomendado para a dificuldade iniciante: observado 6 suspeitos.
  - `PT_007`: contratos obrigatórios acima do recomendado para a dificuldade iniciante: observado 5.
  - `PT_009`: dificuldade declarada diverge da estimada: declarada `iniciante`; estimada `avancado`.
- Decisão de baseline: os avisos são tratados como pontos de atenção heurísticos. Nenhuma alteração foi feita no canônico nesta PR, porque o escopo é registrar o baseline e não alterar narrativa/dificuldade por warning automático.

### Intermediário — O Último Brinde do Hotel Aurora

- Resultado: **passou**.
- Risco: **Baixo**.
- Pode gerar: **SIM**.
- Críticos: **0**.
- Moderados: **0**.
- Avisos: **7**.
- Avisos relevantes:
  - `ELENCO_001`: executor, planejador e beneficiário apontam para o mesmo personagem; aceito como concentração intencional quando validada editorialmente.
  - `GP_003`: documentos `E1-02` e `E2-08` não participam de contratos de evidência.
  - `GP_004`: contratos `C-E1-CIRCULACAO`, `C-E2-DESCARTES` e `C-E2-MOTIVO` não são obrigatórios nem finais.
  - `AUTO_001`: há logs técnicos sem glossário.
- Decisão de baseline: os avisos não exigem ação imediata nesta PR. O Hotel Aurora permanece régua Intermediária validada e continua sem mapa.

## Case Review

### Iniciante — O Desvio da Reserva Mirante

- Status: `READY_FOR_BASELINE`.
- Findings críticos: **0**.
- Warnings: **2**.
- Findings relevantes:
  - Nenhum finding específico de solvabilidade.
  - Nenhum finding específico de progressão por envelope.
  - Dificuldade declarada: `iniciante`.
  - Dificuldade estimada: `avancado`.
  - Documentos: 20.
  - Contratos obrigatórios: 5.
  - Carga cognitiva: `high`.
  - `CR_DIFF_001`: dificuldade declarada pode estar subestimada.
  - `CR_DIFF_003`: volume documental incompatível com a faixa editorial declarada.
- Decisão: manter como baseline canônico Iniciante nesta PR e registrar os warnings como atenção para revisão humana/playtest, sem alteração automática do caso.
- Relatório local gerado: `output/iniciante/case_review.md`.

### Intermediário — O Último Brinde do Hotel Aurora

- Status: `READY_FOR_PLAYTEST`.
- Findings críticos: **0**.
- Warnings: **0**.
- Findings relevantes:
  - Nenhum finding específico de Case Kernel.
  - Nenhum finding específico de solvabilidade.
  - Nenhum finding específico de progressão por envelope.
  - Dificuldade declarada: `intermediario`.
  - Dificuldade estimada: `intermediario`.
  - Documentos: 17.
  - Contratos obrigatórios: 5.
  - Carga cognitiva: `medium`.
- Decisão: manter como baseline canônico Intermediário e seguir para playtest/revisão visual real quando houver pacote gerado. Confirmada a decisão editorial atual: **Hotel Aurora continua sem mapa**.
- Relatório local gerado: `output/intermediario/case_review.md`.

## Build Package

### Iniciante — O Desvio da Reserva Mirante

- Resultado: **tentado, mas bloqueado por ambiente**.
- Comando: `python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict`.
- Output esperado: `output/iniciante`.
- Falha observada: `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
- Tentativa de correção: `python -m playwright install chromium`.
- Bloqueio: o download do Chromium `148.0.7778.96` pelo Playwright retornou HTTP 403 em todas as tentativas.
- Observações: sem Chromium local e sem Chrome/Chromium de sistema, não foi possível gerar PDF real, manifest ou print manifest neste ambiente.

### Intermediário — O Último Brinde do Hotel Aurora

- Resultado: **tentado, mas bloqueado por ambiente**.
- Comando: `python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict`.
- Output esperado: `output/intermediario`.
- Falha observada: `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
- Bloqueio: o mesmo bloqueio de Chromium/Playwright impediu a geração do pacote real.
- Observações: não houve build fake; o baseline visual real permanece pendente até disponibilidade de Chromium.

## Revisão de manifests e print manifests

### Iniciante

- Resultado: **não executável neste ambiente**.
- Motivo: o build package falhou antes de gerar `manifest.json`, `print_manifest.json` e PDFs.
- Arquivos locais gerados nesta execução: apenas `output/iniciante/case_review.md`.

### Intermediário

- Resultado: **não executável neste ambiente**.
- Motivo: o build package falhou antes de gerar `manifest.json`, `print_manifest.json` e PDFs.
- Arquivos locais gerados nesta execução: apenas `output/intermediario/case_review.md`.

## Revisão visual

### Iniciante — O Desvio da Reserva Mirante

- Resultado: **não executável neste ambiente**.
- Motivo: não foram gerados PDFs por ausência de Chromium.
- Itens esperados para a próxima execução com Chromium disponível:
  - capa;
  - envelope;
  - documentos do jogador;
  - e-mail;
  - WhatsApp;
  - registros/logs;
  - mapa v2 gerado por `build_mirante_planta()`;
  - pátio externo;
  - portão;
  - muro/perímetro;
  - posto de controle;
  - portas com cartão;
  - assinaturas/rubricas;
  - cartões apartados;
  - guia do facilitador;
  - dicas;
  - guia de impressão;
  - manifest;
  - print manifest.

### Intermediário — O Último Brinde do Hotel Aurora

- Resultado: **não executável neste ambiente**.
- Motivo: não foram gerados PDFs por ausência de Chromium.
- Itens esperados para a próxima execução com Chromium disponível:
  - capa;
  - envelopes;
  - documentos do jogador;
  - e-mails;
  - chats;
  - registros/tabelas;
  - assinaturas/rubricas;
  - cartões apartados;
  - guia do facilitador;
  - dicas;
  - guia de impressão;
  - manifest;
  - print manifest;
  - confirmação visual de que o caso continua sem mapa.

## Pendências

1. Reexecutar os dois comandos de build package em ambiente com Chromium/Playwright disponível.
2. Revisar `manifest.json` e `print_manifest.json` de ambos os pacotes após build real.
3. Revisar visualmente os PDFs finais de ambos os canônicos após build real.
4. Registrar o baseline visual real em complemento a este baseline operacional quando os PDFs puderem ser gerados.
5. Manter os warnings do Mirante como pontos de atenção heurísticos para revisão humana/playtest, sem alterar a régua canônica apenas por relatório automático.
6. Manter o Hotel Aurora sem mapa, salvo evidência nova de playtest ou instrução explícita.

## Confirmação de escopo

- Nenhum arquivo canônico foi alterado.
- Nenhuma narrativa, solução, dificuldade, documento de jogador, mapa, template, renderer, validator, Case Kernel, Case Review ou package builder foi alterado.
- Esta PR registra o estado real encontrado no fluxo Indiciário 2.0 no ambiente disponível.

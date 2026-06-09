# Baseline visual/operacional — Canônico Iniciante B

## Identificação

- Data da execução: 2026-06-09.
- Branch: `work`.
- Commit base observado antes do registro: `b71a96bc09c4e4f1ada642d9c37d2ef758c0471d`.
- Blueprint validado: `examples/caso_canonico_iniciante_b.json`.
- Caso: **O Recado da Sala de Leitura**.
- Dificuldade declarada: **Iniciante**.
- Escopo desta PR: validação e documentação de baseline.
- Restrições respeitadas: nenhuma alteração em narrativa, solução, dificuldade, documentos, templates, renderer, validator, Case Kernel, Case Review ou package builder.

## Resumo executivo

O fluxo operacional obrigatório foi executado até o ponto permitido pelo ambiente. Os testes automatizados, o lint, o validator strict do Canônico Iniciante B, o Case Review do Canônico Iniciante B e as validações/reviews dos canônicos existentes passaram sem bloqueios críticos.

O build package real foi tentado, mas não concluiu porque o Chromium/headless shell esperado pelo Playwright não está instalado no ambiente. A tentativa de instalar Chromium com `python -m playwright install chromium` também falhou por bloqueio HTTP `403 Forbidden` no download do browser. Portanto, nenhum PDF real, `manifest.json` ou `print_manifest.json` foi gerado nesta execução.

Decisão deste baseline: **não aprovado para playtest a partir desta PR**. A razão não é uma falha editorial comprovada no blueprint, mas a ausência de pacote PDF real para revisão visual/operacional. O caso deve ser reexecutado em ambiente com Chromium/Playwright funcional antes de ser considerado pronto para playtest.

## Comandos executados

| Comando | Resultado |
|---|---|
| `pytest tests/ -q` | Passou: 318 testes passaram e 1 teste foi pulado. |
| `ruff check generator/` | Passou: `All checks passed!`. |
| `python generator/validator.py examples/caso_canonico_iniciante_b.json --strict` | Passou: risco baixo, pode gerar, 0 críticos, 0 moderados, 8 avisos. |
| `python -m scripts.case_review examples/caso_canonico_iniciante_b.json --format markdown` | Passou: status `READY_FOR_PLAYTEST`, 0 críticos, 0 warnings. |
| `python generator/validator.py examples/caso_canonico_iniciante.json --strict` | Passou: risco baixo, pode gerar, 0 críticos, 0 moderados, 12 avisos. |
| `python generator/validator.py examples/caso_canonico_intermediario.json --strict` | Passou: risco baixo, pode gerar, 0 críticos, 0 moderados, 7 avisos. |
| `python -m scripts.case_review examples/caso_canonico_iniciante.json --format markdown` | Passou: status `READY_FOR_BASELINE`, 0 críticos, 2 warnings. |
| `python -m scripts.case_review examples/caso_canonico_intermediario.json --format markdown` | Passou: status `READY_FOR_PLAYTEST`, 0 críticos, 0 warnings. |
| `python -m scripts.build_package examples/caso_canonico_iniciante_b.json --output output/iniciante_b --strict` | Falhou por limitação de ambiente: Chromium/headless shell ausente. |
| `python -m playwright install chromium` | Falhou por limitação de ambiente/rede: download do Chromium retornou HTTP `403 Forbidden` em todas as tentativas. |
| `find output/iniciante_b -type f \| sort` | Encontrou apenas `output/iniciante_b/o-recado-da-sala-de-leitura/html_debug/E1-01.html`. |
| `find output/iniciante_b -type f \( -name '*.pdf' -o -name 'manifest.json' -o -name 'print_manifest.json' \) -print \| sort \| wc -l` | Confirmou `0` PDFs/manifests finais gerados. |

## Resultado dos testes e lint

- `pytest tests/ -q`: **aprovado**.
  - Resultado observado: `318 passed, 1 skipped in 20.43s`.
- `ruff check generator/`: **aprovado**.
  - Resultado observado: `All checks passed!`.

## Validator strict — Canônico Iniciante B

### Resultado

- Comando: `python generator/validator.py examples/caso_canonico_iniciante_b.json --strict`.
- Caso: **O Recado da Sala de Leitura**.
- Risco: **Baixo**.
- Pode gerar: **SIM**.
- Críticos: **0**.
- Moderados: **0**.
- Avisos: **8**.

### Avisos registrados

- `ELENCO_001`: executor, planejador e beneficiário apontam para o mesmo personagem; registrado pelo validator como válido quando a concentração dos papéis for intencional em caso com culpado único.
- `GP_004`: contratos não obrigatórios/não finais podem ser becos sem saída lógico:
  - `C-E1-ACESSO-OPORTUNIDADE`;
  - `C-E1-CONSEQUENCIA-AUSENCIA`;
  - `C-E1-CONTEXTO-CORRETO`;
  - `C-E1-DESCARTE-IARA`;
  - `C-E1-DESCARTE-TOMAS`;
  - `C-E1-MOMENTO-ENGANOSO`.
- `PT_006`: red herrings excessivos em relação aos contratos obrigatórios: 3 red herrings para 2 contratos obrigatórios.

### Interpretação para baseline

Os avisos não bloqueiam geração segundo o validator strict. Como esta PR não corrige narrativa ou estrutura, os pontos acima ficam registrados para observação em playtest/revisão futura, não para alteração nesta PR.

## Case Review — Canônico Iniciante B

### Resultado

- Comando: `python -m scripts.case_review examples/caso_canonico_iniciante_b.json --format markdown`.
- Status final: **`READY_FOR_PLAYTEST`**.
- Findings críticos: **0**.
- Warnings: **0**.
- Dificuldade declarada: `iniciante`.
- Dificuldade estimada: `iniciante`.
- Documentos: **9**.
- Contratos obrigatórios: **2**.
- Carga cognitiva: `low`.

### Núcleo registrado pelo relatório

- Pergunta pública: quem fez Nara sair da Sala de Leitura, por que o recado parecia legítimo e qual intenção havia por trás da mudança.
- Hipótese esperada no E1: o grupo deve sustentar que o recado aproveitou dados de uma versão preliminar sobre outra atividade, mas foi usado às 15h18 para afastar Nara da roda e da votação das 16h10.
- Motivação atual: Celso queria evitar constrangimento por ter prometido apoio à oficina de Tomás antes da votação e preservar o espaço de programação que já anunciara no balcão.
- Evidências obrigatórias extraídas:
  - `C-E1-ORIGEM-RECADO`: o recado deriva de versão preliminar e não de texto inventado do zero; provas `E1-04` e `E1-03`.
  - `C-FINAL-RECONSTRUCAO-RECADO`: a resposta final liga recado reaproveitado, contexto errado, balcão/apoio de Celso e votação sem Nara; provas `E1-06` e `E1-08`.

### Interpretação para baseline

O Case Review não apontou bloqueio crítico, warning de dificuldade, warning de solvabilidade ou warning de progressão por envelope. A conclusão automática é favorável ao playtest, mas o playtest ainda depende de pacote final renderizado e revisão visual real, que não foram possíveis nesta execução.

## Validação dos canônicos existentes

### Canônico Iniciante — O Desvio da Reserva Mirante

- Validator strict: **passou**.
  - Risco: baixo.
  - Pode gerar: sim.
  - Críticos: 0.
  - Moderados: 0.
  - Avisos: 12.
- Case Review: **passou como relatório heurístico**.
  - Status: `READY_FOR_BASELINE`.
  - Críticos: 0.
  - Warnings: 2.
  - Dificuldade declarada: `iniciante`.
  - Dificuldade estimada: `avancado`.
  - Documentos: 20.
  - Contratos obrigatórios: 5.
  - Carga cognitiva: `high`.
- Decisão nesta PR: os avisos já conhecidos do Mirante permanecem registrados; nenhum ajuste foi feito.

### Canônico Intermediário — O Último Brinde do Hotel Aurora

- Validator strict: **passou**.
  - Risco: baixo.
  - Pode gerar: sim.
  - Críticos: 0.
  - Moderados: 0.
  - Avisos: 7.
- Case Review: **passou**.
  - Status: `READY_FOR_PLAYTEST`.
  - Críticos: 0.
  - Warnings: 0.
  - Dificuldade declarada: `intermediario`.
  - Dificuldade estimada: `intermediario`.
  - Documentos: 17.
  - Contratos obrigatórios: 5.
  - Carga cognitiva: `medium`.
- Decisão nesta PR: o Hotel Aurora continua validado como canônico Intermediário e permanece sem mapa; nenhum ajuste foi feito.

## Build package — Canônico Iniciante B

### Comando

```bash
python -m scripts.build_package examples/caso_canonico_iniciante_b.json --output output/iniciante_b --strict
```

### Resultado

- Resultado: **tentado, mas bloqueado por ambiente**.
- Falha observada: `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell`.
- Mensagem do Playwright: o browser precisa ser instalado com `playwright install`.
- Tentativa de correção executada: `python -m playwright install chromium`.
- Falha da tentativa de correção: download de `Chrome for Testing 148.0.7778.96 (playwright chromium v1223)` retornou HTTP `403 Forbidden` em todas as tentativas.

### Arquivos gerados

O build não chegou a gerar pacote final. Arquivos observados em `output/iniciante_b`:

- `output/iniciante_b/o-recado-da-sala-de-leitura/html_debug/E1-01.html` — arquivo parcial de debug HTML gerado antes da falha do renderer.

Arquivos finais não gerados:

- PDFs: **0**.
- `manifest.json`: **não gerado**.
- `print_manifest.json`: **não gerado**.
- pacote consolidado: **não gerado**.

## Revisão visual do PDF

### Estado

**Não executável nesta execução.** Como o build real falhou antes da geração dos PDFs, não houve PDF final para revisão visual. O arquivo parcial `html_debug/E1-01.html` não substitui baseline visual real, porque o critério do projeto exige pacote renderizado com Playwright/Chromium.

### Checklist visual esperado para a próxima execução

| Item | Status nesta execução | Observação |
|---|---|---|
| Capa | Não revisado | PDF não gerado. |
| Envelope único | Não revisado | PDF não gerado. |
| Ordem dos documentos | Não revisado | Manifest/PDF não gerados. |
| Numeração contínua | Não revisado | PDF não gerado. |
| Ausência de documentos faltando | Não revisado | Pacote final não gerado. |
| Legibilidade geral | Não revisado | PDF não gerado. |
| Quebras de página | Não revisado | PDF não gerado. |
| Cabeçalhos e rodapés | Não revisado | PDF não gerado. |
| Aparência física de dossiê | Não revisado | PDF não gerado. |

## Revisão dos documentos do jogador

**Não executável visualmente em PDF real nesta execução.** A revisão abaixo registra os documentos esperados pelo blueprint e o status de inspeção visual.

| Documento esperado | Código | Status nesta execução |
|---|---:|---|
| Abertura de apuração interna | `E1-01` | Não revisado em PDF real. |
| Agenda pública e aviso corrigido do mural | `E1-02` | Não revisado em PDF real. |
| Recado entregue a Nara | `E1-03` | Não revisado em PDF real. |
| Rascunho preliminar de aviso | `E1-04` | Não revisado em PDF real. |
| Lista de presença da roda de leitura | `E1-05` | Não revisado em PDF real. |
| Relatos breves de balcão e sala | `E1-06` | Não revisado em PDF real. |
| Orientação interna sobre recados de evento | `E1-07` | Não revisado em PDF real. |
| Ata curta da votação de programação | `E1-08` | Não revisado em PDF real. |
| Folha de apoio da apuração — registro de horários e avisos | `E1-09` | Não revisado em PDF real. |

### Critérios editoriais/visuais pendentes de conferência em PDF

Na próxima execução com Chromium disponível, conferir explicitamente:

- se nenhum documento explica a solução;
- se nenhum documento usa linguagem de dica;
- se nenhum documento manda artificialmente “comparar X com Y”;
- se a folha de apoio organiza a apuração sem entregar a resposta;
- se Celso não fica óbvio demais por um único documento;
- se a consequência concreta da ausência fica clara;
- se a ausência da mediadora aparece de forma jogável;
- se a legibilidade da folha de apoio é adequada para mesa/impressão.

## Printables

### Itens esperados no blueprint

O blueprint registra cartões apartados de apoio de mesa:

- Cartões de personagem:
  - `CARD-P01` — Nara Bittencourt;
  - `CARD-P02` — Celso Diniz;
  - `CARD-P03` — Iara Mendonça;
  - `CARD-P04` — Tomás Vieira.
- Cartões de local:
  - `CARD-L01` — Sala de Leitura;
  - `CARD-L02` — Balcão cultural e mural;
  - `CARD-L03` — Sala Multiuso.

### Status nesta execução

- PDFs/cartões renderizados: **não gerados**.
- Guia de impressão: **não gerado**.
- Print manifest: **não gerado**.
- Validação de que cartões são apoio de mesa, não evidência principal: **pendente de revisão em pacote real**.

## Guia do facilitador

**Não revisado em PDF real nesta execução.** Como o pacote não foi gerado, a checagem visual/operacional do guia do facilitador permanece pendente.

Na próxima execução com PDF, conferir:

- pergunta pública;
- resposta esperada;
- critério de conclusão;
- linha do tempo aparente;
- linha do tempo real;
- red herrings;
- descartes;
- solução em síntese;
- dicas contextuais;
- separação entre guia/gabarito e documentos do jogador.

## Manifest e print manifest

### Manifest

- Status: **não gerado**.
- Motivo: build interrompido por ausência de Chromium/headless shell.
- Revisão de arquivos listados corretamente: **pendente**.
- Revisão de ordem de impressão: **pendente**.
- Revisão de segregação de material confidencial: **pendente**.

### Print manifest

- Status: **não gerado**.
- Motivo: build interrompido por ausência de Chromium/headless shell.
- Revisão de printables registrados: **pendente**.
- Revisão de cartões/folha de apoio: **pendente**.
- Revisão de guia de impressão: **pendente**.

## Pendências encontradas

### Bloqueante operacional

1. Reexecutar o build em ambiente com Chromium/Playwright funcional:

   ```bash
   python -m scripts.build_package examples/caso_canonico_iniciante_b.json --output output/iniciante_b --strict
   ```

2. Revisar os PDFs reais gerados, incluindo capa, envelope único, documentos do jogador, guia do facilitador, printables e guia de impressão.
3. Revisar `manifest.json` e `print_manifest.json` após geração real do pacote.
4. Registrar novo complemento de baseline visual quando o pacote real existir.

### Pendências editoriais/visuais potenciais a observar, sem correção nesta PR

Estas pendências não foram comprovadas por PDF real; são pontos obrigatórios de conferência na próxima execução:

- confirmar que a folha de apoio da apuração organiza sem entregar;
- confirmar que Celso não fica óbvio demais por um único documento;
- confirmar que a ausência da mediadora está visível e jogável;
- confirmar que a consequência concreta da votação com presença incompleta está clara;
- confirmar que os cartões continuam como apoio de mesa, não evidência principal;
- confirmar que não há vazamento de solução nos documentos do jogador.

### Pendências cosméticas

Nenhuma pendência cosmética foi comprovada nesta execução, porque não houve PDF real para inspeção.

## Decisão final

**Não aprovado para playtest a partir desta PR.**

Motivo: o validator strict e o Case Review do Canônico Iniciante B são favoráveis, mas o baseline visual/operacional real não foi concluído porque o ambiente não possui Chromium/headless shell e o download via Playwright retornou HTTP `403 Forbidden`. Sem PDF final, manifest e print manifest, não é possível afirmar que **O Recado da Sala de Leitura** está pronto para playtest.

Esta decisão não reprova a narrativa nem recomenda correções editoriais nesta PR. Ela apenas bloqueia o avanço operacional até que o pacote final seja gerado e revisado visualmente em ambiente adequado.

## Confirmação de escopo

- `examples/caso_canonico_iniciante_b.json` não foi alterado.
- `examples/caso_canonico_iniciante.json` não foi alterado.
- `examples/caso_canonico_intermediario.json` não foi alterado.
- Nenhum template foi alterado.
- Nenhum renderer foi alterado.
- Nenhum validator foi alterado.
- Nenhum módulo de Case Kernel ou Case Review foi alterado.
- Nenhum package builder foi alterado.
- Esta PR adiciona apenas o registro documental do baseline observado.

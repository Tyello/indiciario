# ISSUE-40.2 — Gate visual: detectar fallback de fonte

STATUS: done
CURRENT_STEP: STEP-05_FIX-01
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-05_FIX-01
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.2/STEP-05_FIX-01_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-40.2/STEP-04_REVIEW.md
BLOCKER: none

**Prioridade:** P0
**Depende de:** 40.1 (fontes vendorizadas + helper de font computado)
**Bloqueia:** nenhuma issue direta, mas é pré-requisito de doutrina para todo o lote (formaliza o gate visual que 40.3-40.6 vão querer reusar)

## Objetivo

40.1 resolve o problema uma vez, no momento em que foi feita. Sem um gate, nada impede que uma issue futura (ou um novo template) reintroduza a mesma falha silenciosa: fonte custom referenciada sem `@font-face` correspondente, degradando para fallback de sistema sem que ninguém perceba. Esta issue formaliza a detecção como parte permanente do pipeline de qualidade — mesma lógica de "falhas silenciosas são o risco mais caro" já aplicada nas 30.6/30.7, agora no domínio visual.

## Doc-impact declarado (STEP-05)

- Criar `framework/09_SISTEMA_VISUAL.md` — novo documento de doutrina, no mesmo espírito do `08_MODELO_REFERENCIA.md`. Nesta issue, registra apenas a regra do gate de fidelidade de fonte; será estendido nas 40.3 e 40.6 com o sistema de camadas e microidentidades.
- Cross-referenciar o novo doc a partir de `framework/07_PROMPT_GERADOR_DE_CASO.md`.

## Critério de aceite

1. O pipeline de qualidade (`canonical_quality_gate.py` ou equivalente) falha explicitamente se qualquer template renderizado usa uma fonte cujo `font-family` computado não bate com a família declarada no HTML/CSS.
2. O relatório do gate (run manifest) nomeia o template e a fonte específica que falhou — não um erro genérico.
3. Removendo deliberadamente um `@font-face` (teste de regressão), o gate falha; restaurando, o gate passa.
4. `framework/20_SISTEMA_VISUAL.md` existe e documenta a regra.

## Passos (referência para o executor)

Ver `ISSUE-40.2_SPEC.md` para o detalhamento técnico completo.

---

### STEP-01 — Levantamento

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler `generator/canonical_quality_gate.py`, `generator/gate_evaluator.py`, `generator/pipeline_runner.py`, `generator/run_manifest.py`, `generator/quality_comparative_reviewer.py`.
- Confirmar mecanismo real de registro de checks (hoje `canonical_quality_gate.py` calcula `QualificationCriterion` inline em `evaluate_for_canonical`, sem sistema plugável; `GP_0XX` citado na spec é ilustrativo e não existe nesse arquivo — `GP_001..GP_007` já existe, mas em `generator/clue_graph.py`, domínio de plausibilidade narrativa, não visual. Não reusar esse prefixo sem confirmar.).
- Confirmar onde/como `stages_completed` é populado e se há (ou falta) um estágio `visual_review` que hoje não roda (ver `docs/ESTADO_ATUAL.md` — pipeline_runner não invoca visual/accessibility reviewers).
- Localizar o helper de font measurement criado na 40.1 (`tests/test_font_vendoring.py`, função `_MEDIR_FONTE_JS` + `_montar_html`) e decidir se extrai para módulo compartilhado.
- Registrar no execution report: ponto de integração real recomendado (arquivo/função) e nome/ID definitivo do check a usar no STEP-03.

Contexto permitido:
- generator/canonical_quality_gate.py
- generator/gate_evaluator.py
- generator/pipeline_runner.py
- generator/run_manifest.py
- generator/quality_comparative_reviewer.py
- generator/renderer.py
- generator/clue_graph.py (só para confirmar que GP_0XX é de outro domínio)
- tests/test_canonical_quality_gate.py
- tests/test_font_vendoring.py
- templates/styles/document_system.css
- docs/CANONICAL_CRITERIA.md
- docs/ESTADO_ATUAL.md
- .ai/issues/ISSUE-40.2.md
- .ai/issues/ISSUE-40.2_SPEC.md

Arquivos editáveis:
- .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md (relatório apenas)

Comandos permitidos:
- rtk read, rtk grep (ou Read/Grep equivalentes) — só leitura

Proibido:
- Editar qualquer arquivo em generator/, tests/, templates/
- Rodar pytest/ruff
- Presumir a API (`GP_0XX`) da spec sem confirmar contra o código real

Done quando:
- Execution report responde às 3 perguntas do STEP-01 da spec (registro de checks, formato de saída, agregação no manifest) e recomenda ponto de integração + ID do check.

Revisão:
- (auto-approve, low-risk)

---

### STEP-02 — RED

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_gate_font_fidelity.py` com os dois testes do esqueleto da spec (`test_gate_currently_misses_font_fallback`, `test_gate_catches_font_fallback`), adaptados ao ponto de integração real confirmado no STEP-01.
- `test_gate_currently_misses_font_fallback` deve passar hoje (evidencia a lacuna: gate atual não pega fallback de fonte).
- `test_gate_catches_font_fallback` deve falhar hoje (é o critério real, vira GREEN só após STEP-03).

Contexto permitido:
- Tudo do STEP-01 + .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md
- tests/test_font_vendoring.py (reusar helper de medição de fonte)

Arquivos editáveis:
- tests/test_gate_font_fidelity.py (novo)

Comandos permitidos:
- pytest tests/test_gate_font_fidelity.py -q

Proibido:
- Alterar qualquer arquivo em generator/
- Alterar tests/test_font_vendoring.py

Done quando:
- Os dois testes existem; `test_gate_currently_misses_font_fallback` passa; `test_gate_catches_font_fallback` falha (RED documentado).

Revisão:
- Teste realmente evidencia a lacuna (não é tautológico)?
- Os dois testes usam a mesma montagem (fonte removida) para serem comparáveis?

---

### STEP-03 — GREEN

Status: pending
Owner: executor
Type: green

Objetivo:
- Implementar o check de fidelidade de fonte no ponto de integração decidido no STEP-01, reusando o helper de font measurement (extraído para módulo compartilhado se o STEP-01 recomendou).
- Registrar o check com o ID confirmado no STEP-01.
- Reportar falha nomeando template + fonte específica (não booleano agregado).

Contexto permitido:
- .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.2/STEP-02_EXECUTION.md
- generator/canonical_quality_gate.py, tests/test_gate_font_fidelity.py, tests/test_font_vendoring.py, generator/renderer.py, templates/styles/document_system.css

Arquivos editáveis:
- Arquivo(s) de generator/ indicados no STEP-01 como ponto de integração
- tests/test_font_vendoring.py (só se extrair helper compartilhado — não mudar asserts)

Comandos permitidos:
- pytest tests/test_gate_font_fidelity.py -q
- ruff check generator/

Proibido:
- Implementar outros checks visuais (camada, brand leakage, microidentidade — fora de escopo, 40.3/40.5/40.6)
- Expandir para além do check de fonte

Done quando:
- `test_gate_catches_font_fallback` passa; ruff limpo.

Revisão:
- Check nomeia template+fonte na falha (critério de aceite #2)?
- Escopo não vazou para outros checks visuais?

---

### STEP-03_FIX-01 — Wiring de evaluate_font_fidelity em evaluate_for_canonical

Status: pending
Owner: executor
Type: correction

Objetivo:
- Corrigir divergência do STEP-03 (ver .ai/runs/ISSUE-40.2/STEP-03_REVIEW.md): `evaluate_font_fidelity` existe mas não é chamada por `evaluate_for_canonical` nem pelo pipeline — função morta frente ao critério de aceite #1 da issue.
- Conectar via o mecanismo de parâmetro opcional já recomendado no STEP-01: `evaluate_for_canonical` passa a aceitar um parâmetro opcional (ex.: `font_fidelity_criterion: QualificationCriterion | None = None`) que, quando fornecido, é adicionado a `criteria_results` (afeta `qualification` normalmente via `has_blocker`/status, igual aos demais critérios).
- Preservar chamadas existentes sem esse parâmetro (`tests/test_canonical_quality_gate.py` não deve quebrar).
- Não fazer `evaluate_for_canonical` chamar Playwright diretamente — quem invoca (ex. pipeline_runner ou o caller do gate) constrói o critério via `evaluate_font_fidelity` e passa pronto.

Contexto permitido:
- .ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.2/STEP-03_EXECUTION.md, .ai/runs/ISSUE-40.2/STEP-03_REVIEW.md
- generator/canonical_quality_gate.py, generator/font_fidelity.py, tests/test_gate_font_fidelity.py, tests/test_canonical_quality_gate.py

Arquivos editáveis:
- generator/canonical_quality_gate.py
- tests/test_gate_font_fidelity.py (só se precisar ajustar teste para cobrir o wiring)

Comandos permitidos:
- pytest tests/test_gate_font_fidelity.py -q
- pytest tests/test_canonical_quality_gate.py -q
- ruff check generator/

Proibido:
- Reintroduzir Playwright dentro de evaluate_for_canonical
- Tocar pipeline_runner.py (fora do escopo desta correção; se achar necessário, sinalizar no report, não fazer)

Done quando:
- `evaluate_for_canonical` aceita e usa o critério de font fidelity quando fornecido; testes de STEP-02 e test_canonical_quality_gate.py passam; ruff limpo.

Revisão:
- Wiring resolve a rejeição do STEP-03_REVIEW.md?
- Chamadas antigas de evaluate_for_canonical (sem o novo parâmetro) continuam funcionando?

---

### STEP-04 — Verificação de regressão

Status: pending
Owner: executor
Type: validation

Objetivo:
- Confirmar os dois testes do STEP-02 no estado esperado pós-GREEN.
- Rodar suíte completa e confirmar ausência de regressão.
- Confirmar critério de aceite #3 (remover `@font-face` de propósito → gate falha; restaurar → gate passa).

Contexto permitido:
- Tudo dos steps anteriores

Arquivos editáveis:
- tests/test_gate_font_fidelity.py (só ajuste pequeno de docstring/histórico, se necessário)

Comandos permitidos:
- pytest tests/test_gate_font_fidelity.py -q
- pytest tests/ -q

Proibido:
- Alterar comportamento do check implementado no STEP-03

Done quando:
- `pytest tests/ -q` passa sem regressão.

Revisão:
- Segunda opinião sobre eventual falha na suíte completa.

---

### STEP-05 — Docs

Status: pending
Owner: executor
Type: documentation

Objetivo:
- Criar `framework/09_SISTEMA_VISUAL.md` com o conteúdo do esqueleto da spec, ajustado ao ID real do check confirmado no STEP-03.
- Adicionar cross-link em `framework/07_PROMPT_GERADOR_DE_CASO.md`, mesmo padrão da linha 62 (referência a `08_MODELO_REFERENCIA.md`).
- Resolver impacto documental declarado (`docs/INDICE_DOCUMENTACAO.md`).

Contexto permitido:
- framework/07_PROMPT_GERADOR_DE_CASO.md
- framework/08_MODELO_REFERENCIA.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/runs/ISSUE-40.2/STEP-03_EXECUTION.md

Arquivos editáveis:
- framework/09_SISTEMA_VISUAL.md (novo)
- framework/07_PROMPT_GERADOR_DE_CASO.md
- docs/INDICE_DOCUMENTACAO.md

Comandos permitidos:
- nenhum comando necessário

Proibido:
- Alterar código

Done quando:
- `framework/09_SISTEMA_VISUAL.md` existe com o ID real do check; cross-link presente em `framework/07`; impacto documental resolvido.

Revisão:
- (auto-approve, low-risk)

---

### STEP-05_FIX-01 — Renumerar doc de framework (colisão com 09_TEMPLATE_GABARITO.md)

Status: pending
Owner: executor
Type: correction

Objetivo:
- `framework/09_TEMPLATE_GABARITO.md` já existe. `framework/09_SISTEMA_VISUAL.md` (criado no STEP-05) colide de numeração — spec assumiu "09" livre sem checar `framework/` atual (numeração vai 00 a 19; próximo número livre é 20).
- Renomear `framework/09_SISTEMA_VISUAL.md` → `framework/20_SISTEMA_VISUAL.md` (mesmo conteúdo).
- Atualizar o cross-link em `framework/07_PROMPT_GERADOR_DE_CASO.md` para apontar `framework/20_SISTEMA_VISUAL.md`.
- Atualizar a entrada em `docs/INDICE_DOCUMENTACAO.md` para o novo nome de arquivo.
- Ajustar o texto do critério de aceite #4 nesta issue (seção "Critério de aceite") para refletir `framework/20_SISTEMA_VISUAL.md` — decisão do orquestrador, registrada aqui: correção de numeração stale do spec, não mudança de conteúdo/doutrina, não exige reabertura com humano.

Contexto permitido:
- framework/09_SISTEMA_VISUAL.md, framework/07_PROMPT_GERADOR_DE_CASO.md, docs/INDICE_DOCUMENTACAO.md, .ai/runs/ISSUE-40.2/STEP-05_EXECUTION.md

Arquivos editáveis:
- framework/09_SISTEMA_VISUAL.md → renomear para framework/20_SISTEMA_VISUAL.md
- framework/07_PROMPT_GERADOR_DE_CASO.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/issues/ISSUE-40.2.md (só a linha do critério de aceite #4, além dos campos de controle)

Comandos permitidos:
- nenhum comando necessário (rename + edit de texto)

Proibido:
- Alterar conteúdo doutrinário do documento
- Reusar qualquer outro número já ocupado

Done quando:
- framework/20_SISTEMA_VISUAL.md existe com o conteúdo do STEP-05; framework/09_SISTEMA_VISUAL.md não existe mais; cross-link e índice atualizados; critério de aceite #4 corrigido.

Revisão:
- (auto-approve, low-risk — correção de numeração, sem decisão de conteúdo)

---

## Histórico

- Orquestrador formalizou os 5 steps acima (campos de controle + contratos) a partir do resumo em prosa já existente. Não houve replanejamento de sequência — mesma ordem e escopo de STEP-01 a STEP-05 já definidos.
- STEP-03 executado; aguardando revisão.
- STEP-03 reprovado (major): `evaluate_font_fidelity` existe mas não é chamada por `evaluate_for_canonical` nem `pipeline_runner.py` — gate real nunca dispara, critério de aceite #1 não cumprido. Aponta para STEP-03_FIX-01 (não blocked, correção objetiva). Ver .ai/runs/ISSUE-40.2/STEP-03_REVIEW.md.
- STEP-03_FIX-01 executado: `evaluate_for_canonical` ganhou parâmetro opcional `font_fidelity_criterion`, anexado a `criteria_results` quando fornecido, participando de `has_blocker` como os demais critérios. Nenhuma chamada de Playwright dentro do gate; `pipeline_runner.py` não tocado (fora de escopo desta correção, por instrução). `pytest tests/test_gate_font_fidelity.py -q` → 3 passed; `pytest tests/test_canonical_quality_gate.py -q` → 21 passed (sem regressão); `ruff check generator/` limpo. Aguardando revisão. Ver .ai/runs/ISSUE-40.2/STEP-03_FIX-01_EXECUTION.md.
- STEP-03_FIX-01 aprovado (severidade none): DVG-001 do STEP-03_REVIEW.md resolvido — `evaluate_font_fidelity` deixou de ser função morta, `evaluate_for_canonical` agora a consome via parâmetro opcional; chamadas antigas preservadas; `pipeline_runner.py` intocado; comandos re-executados confirmam o relatado. Avançando para STEP-04. Ver .ai/runs/ISSUE-40.2/STEP-03_FIX-01_REVIEW.md.
- STEP-04 executado: os 3 testes de `tests/test_gate_font_fidelity.py` passam (`3 passed`), incluindo o teste de wiring do FIX-01. `pytest tests/ -q` → `5 failed, 1388 passed, 3 skipped` — as 5 falhas são pré-existentes (`OSError: [WinError 1314]`, privilégio de symlink no Windows local, em `tests/test_blind_bundle_*`, alheias a font/gate), sem regressão introduzida por esta issue. Critério de aceite #3 confirmado: remoção do `@font-face` → `evaluate_font_fidelity` retorna `status="blocker"` nomeando template+fonte (e propaga `NOT_READY` via `evaluate_for_canonical`); restauração (monkeypatch revertido pelo pytest) → `test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema` confirma fonte aplicada no CSS real, logo `status="ok"` para esse par. Docstring de `test_gate_currently_misses_font_fallback` atualizada (só nota histórica, nenhum assert alterado) para refletir que o check passou a existir desde o STEP-03/FIX-01, mas a chamada default de `evaluate_for_canonical` continua sem ele por design (parâmetro opcional). Aguardando revisão (Type: validation, high-risk). Ver .ai/runs/ISSUE-40.2/STEP-04_EXECUTION.md.
- STEP-04 aprovado (severidade none): git status confirma escopo — nenhum step desta issue tocou `tests/test_blind_bundle_*` ou `generator/pipeline_runner.py`, sustentando a alegação de falhas de symlink pré-existentes. Revisor encontrou 6ª falha não reportada pelo executor (`test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`); investigação (reexecução isolada 3x + `git stash` para `main` limpa) confirma teste flaky por si só, independente das mudanças desta issue — não é regressão, mas o relatório do executor ficou incompleto por não capturar essa flakiness na sua própria rodada. Não bloqueia por causa raiz estar fora do escopo tocado. Critério de aceite #3 confirmado por leitura direta de `tests/test_gate_font_fidelity.py` e `generator/font_fidelity.py`. Wiring do STEP-03_FIX-01 confirmado em `generator/canonical_quality_gate.py` (linhas 131, 256, 261, 372-373). Registrado como nota de housekeeping futuro (teste flaky em `test_pipeline_runner.py`, fora do escopo da 40.2). Avançando para STEP-05. Ver .ai/runs/ISSUE-40.2/STEP-04_REVIEW.md.
- STEP-05 executado: criado `framework/09_SISTEMA_VISUAL.md` com API real (`evaluate_font_fidelity`, `name="font_fidelity"`, wiring via `font_fidelity_criterion` em `evaluate_for_canonical`, confirmado no STEP-03_FIX-01) — não `GP_0XX_font_fidelity` ilustrativo da spec. Cross-link adicionado em `framework/07_PROMPT_GERADOR_DE_CASO.md` no mesmo padrão da referência a `08_MODELO_REFERENCIA.md`. `docs/INDICE_DOCUMENTACAO.md` atualizado com linha para o novo doc. Nenhum comando rodado (step documentation, só leitura). Observação para o revisor: `framework/09_TEMPLATE_GABARITO.md` já existia — este step introduz uma segunda entrada `09_*`, colisão de numeração não resolvida (fora do escopo editável do step, que não inclui `framework/00_README.md`); sinalizado para decisão do orquestrador/revisor. Aguardando revisão (Type: documentation, low-risk, auto-approve elegível). Ver .ai/runs/ISSUE-40.2/STEP-05_EXECUTION.md.
- STEP-05 reprovado (numeração): confirmada a colisão sinalizada pelo próprio executor — `framework/09_TEMPLATE_GABARITO.md` já ocupava `09`. Orquestrador decide renumerar para `20` (próximo livre em `framework/`, faixa 00–19 ocupada) em vez de reabrir com humano — correção de numeração stale do spec, não mudança de doutrina. Aponta para STEP-05_FIX-01.
- STEP-05_FIX-01 executado: `framework/09_SISTEMA_VISUAL.md` renomeado para `framework/20_SISTEMA_VISUAL.md` (conteúdo idêntico, nenhuma linha doutrinária alterada). Cross-link em `framework/07_PROMPT_GERADOR_DE_CASO.md` (linha na seção de referências, junto ao link para `08_MODELO_REFERENCIA.md`) atualizado para `framework/20_SISTEMA_VISUAL.md`. Entrada em `docs/INDICE_DOCUMENTACAO.md` (linha `09_SISTEMA_VISUAL.md`) atualizada para `20_SISTEMA_VISUAL.md`. Critério de aceite #4 desta issue corrigido para `framework/20_SISTEMA_VISUAL.md`. Grep por `09_SISTEMA_VISUAL` no repo pós-mudança: sem ocorrências nos 4 arquivos editáveis do step; restam referências stale fora do escopo editável (`.ai/issues/ISSUE-40.3.md`/`ISSUE-40.5.md`/`ISSUE-40.6.md` citando o doc futuro pelo nome antigo, `.ai/runs/ISSUE-40.2/STEP-05_EXECUTION.md` como relatório histórico imutável) — sinalizado, não corrigido, por estar fora de `Arquivos editáveis` deste step. Nenhum comando executado (rename + edit de texto, conforme contrato). Type: correction, mas seção Revisão do próprio step diz "(auto-approve, low-risk — correção de numeração, sem decisão de conteúdo)"; seguido o protocolo padrão do executor.md mesmo assim (executor não se auto-aprova) — STATUS/NEXT_ACTION/REVIEW_STATUS setados para waiting_review/review/pending, com a nota de auto-approve elegível registrada aqui para o orquestrador decidir fast-track, mesmo padrão usado no fechamento do STEP-05. Ver .ai/runs/ISSUE-40.2/STEP-05_FIX-01_EXECUTION.md.

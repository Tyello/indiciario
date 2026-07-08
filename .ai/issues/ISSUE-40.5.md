# ISSUE-40.5 — Isolar `--accent` da marca Indiciário na Camada 0

STATUS: done
CURRENT_STEP: STEP-05
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-05
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.5/STEP-05_EXECUTION.md
LAST_REVIEW_REPORT: n/a (auto-approve, low-risk, documentation)
BLOCKER: none

**Status:** especificada, pronta para execução
**Prioridade:** P1
**Depende de:** 40.3
**Bloqueia:** 40.6

## Objetivo

Hoje `--accent: #8b1a1a`, definido em `base.html`, vaza por herança CSS para dentro de documentos diegéticos. Isso confunde duas coisas que deveriam ser independentes: a identidade visual do *produto* Indiciário (que só deveria aparecer em envelope, protocolo, dicas, gabarito) e a identidade visual de cada *instituição fictícia dentro do caso* (que a 40.6 vai formalizar como microidentidade).

Esta issue inverte a herança atual: `--accent` passa a ser escopado à Camada 0. Documentos de evidência não herdam cor de marca por padrão.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar a regra "marca Indiciário nunca aparece em documento diegético".

## Critério de aceite

1. `--accent` só é aplicado dentro do escopo de templates de Camada 0.
2. Nenhum template de Camada 1/2 herda `--accent` por padrão (verificar computed style).
3. Teste automatizado comprova o item 2 para todos os templates existentes.

## Passos (referência para o executor)

1. STEP-01 — Mapear todos os usos atuais de `--accent` fora da Camada 0 (grep + inspeção visual).
2. STEP-02 — RED: teste que falha se qualquer elemento de Camada 1/2 tiver `--accent` (ou uma cor derivada dele) no computed style.
3. STEP-03 — GREEN: mover a definição de `--accent` de `:root` global para um escopo `.camada-0 { --accent: #8b1a1a; }`; garantir que templates de Camada 1/2 não têm fallback implícito para essa variável (definir uma cor neutra própria onde for necessária, sem depender da marca).
4. STEP-04 — Rodar contra todos os templates existentes.
5. STEP-05 — Docs: `templates/README.md`.

Ver `ISSUE-40.5_SPEC.md` para o detalhamento técnico.

---

### STEP-01 — Levantamento

Status: pending
Owner: executor
Type: reading

Objetivo:
- Confirmar (ou corrigir) os achados preliminares do orquestrador, feitos nesta sessão via `grep -rn -- "--accent" templates/ generator/`:
  1. `--accent` só existe em `templates/base.html` (definição em `:root` por volta da linha 24; uso em `.doc-code { color: var(--accent); }` por volta da linha 53). Nenhuma outra ocorrência em `templates/*.html`, `templates/styles/document_system.css` ou `generator/`.
  2. `templates/base.html` é órfão — achado já confirmado pela 40.3/STEP-01 e 40.3/STEP-03 ("0 templates estendem `base.html`, arquivo não carregado pelo pipeline"). Confirmar de novo neste repo (`grep -rln "extends.*base.html" templates/*.html`) porque a 40.5 depende diretamente disso: se `base.html` continua órfão, `--accent` **não vaza hoje** para nenhum template ativo — o critério de aceite #2 já está tecnicamente satisfeito antes de qualquer mudança de código, e o trabalho real desta issue é (a) escopar a definição em `base.html` mesmo assim, por disciplina/documentação de referência de Camada 0, e (b) criar o teste de regressão que garante que isso continua verdade se `base.html` deixar de ser órfão no futuro.
  3. `templates/08_orcamento.html` tem `.accent-bar` (linha 30) e usa `background: {{COR_PRIMARIA}}` — variável Jinja de instituição, não a CSS var `--accent`. Confirmar que isso é coincidência de nome, não uso disfarçado da marca (achado preliminar: é coincidência — `COR_PRIMARIA` é per-instituição, já é o mecanismo que a 40.6 vai formalizar).
- Reaproveitar a classificação de Camada 0/1/2 já feita pela 40.3 (`.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md`) em vez de reclassificar do zero: `PAPER_LAYER_TEMPLATES` (12), `SCREEN_LAYER_TEMPLATES` (4) formam o conjunto Camada 1/2 (16 templates diegéticos); `GAME_LAYER_TEMPLATES` (5: `00_envelope_capa.html`, `facilitator_guide.html`, `dicas_contextuais.html`, `print_guide.html`, `printable_cards.html`) mais `base.html` formam Camada 0. Confirmar que nenhum desses 16 templates diegéticos referencia `--accent` (bate com o achado 1 acima).
- Registrar no execution report: confirmação/correção dos 3 achados, lista final `NON_LAYER0_TEMPLATES` para o STEP-02 (os 16 diegéticos), e se o STEP-02 deve nascer RED de verdade ou GREEN-por-desenho (guarda de regressão) — precedente aceito na 40.4/STEP-02 para o teste de aging texture.

Contexto permitido:
- templates/*.html (todos)
- templates/styles/document_system.css
- generator/renderer.py
- .ai/issues/ISSUE-40.5.md
- .ai/issues/ISSUE-40.5_SPEC.md
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md (classificação de camada de referência)
- .ai/issues/ISSUE-40.3.md (histórico de referência)

Arquivos editáveis:
- .ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md (relatório apenas)

Comandos permitidos:
- rtk read, rtk grep (ou Read/Grep equivalentes) — só leitura

Proibido:
- Editar template, CSS ou renderer.py
- Rodar pytest/ruff

Done quando:
- Execution report confirma (ou corrige) os 3 achados preliminares acima, com citação de linha exata, e entrega a lista `NON_LAYER0_TEMPLATES` final para o STEP-02.

Revisão:
- (auto-approve, low-risk)

---

### STEP-02 — RED

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_brand_isolation.py`, seguindo o padrão Playwright/CSS computado de `tests/test_layer_rules.py` (não grep de string em arquivo-fonte).
- `NON_LAYER0_TEMPLATES` = lista confirmada pelo STEP-01 (os 16 templates de Camada 1/2: `PAPER_LAYER_TEMPLATES` + `SCREEN_LAYER_TEMPLATES` da 40.3).
- `test_diegetic_template_does_not_inherit_brand_accent`, parametrizado por `NON_LAYER0_TEMPLATES`: renderiza o template real (via `generator.font_fidelity._montar_html` ou equivalente já usado por `test_layer_rules.py`), inspeciona todos os elementos visíveis do body e falha se `getComputedStyle` de qualquer um resolver `color`, `background-color` ou `border-color` para `rgb(139, 26, 26)` (equivalente computado de `#8b1a1a`) ou se `getComputedStyle(document.documentElement).getPropertyValue('--accent')` retornar não-vazio dentro do escopo do template.
- Se o STEP-01 confirmar que `base.html` é órfão e `--accent` não aparece em nenhum dos 16 templates hoje, este teste nasce GREEN por desenho (guarda de regressão, mesmo precedente da 40.4/STEP-02) — documentar isso explicitamente no report, não forçar RED artificial.
- Adicionar também `test_accent_variable_scoped_to_camada_0`: falha se `templates/base.html` **não** tiver `--accent` declarado dentro de um seletor `.camada-0` (ou equivalente) — este teste é RED real hoje, porque `--accent` ainda está em `:root` global.

Contexto permitido:
- .ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md
- templates/base.html, templates/styles/document_system.css, generator/renderer.py
- tests/test_layer_rules.py (padrão de teste via Playwright)

Arquivos editáveis:
- tests/test_brand_isolation.py (novo)

Comandos permitidos:
- pytest tests/test_brand_isolation.py -q

Proibido:
- Alterar template, CSS ou renderer.py
- Teste tautológico (checar só presença de string no texto-fonte, não o computed style renderizado)

Done quando:
- `tests/test_brand_isolation.py` existe com os dois testes; execution report documenta output real do pytest (quais falham hoje e por quê, incluindo se o teste de herança nasce GREEN por desenho).

Revisão:
- Teste de herança inspeciona CSS computado real via Playwright, não grep?
- Parametrização cobre os 16 templates de Camada 1/2 confirmados pelo STEP-01, não uma lista arbitrária?
- Teste de escopo (`.camada-0`) é RED real hoje?

---

### STEP-03 — GREEN

Status: pending
Owner: executor
Type: green

Objetivo:
- Em `templates/base.html`: mover a declaração de `--accent: #8b1a1a` de `:root` para um seletor `.camada-0` (ex.: `.camada-0 { --accent: #8b1a1a; }`), aplicando a classe `camada-0` no elemento que hoje recebe o `:root`/`body` do template (`base.html` é o único consumidor — ajustar o próprio `body`/wrapper para carregar a classe).
- Confirmar que nenhum dos 16 templates de Camada 1/2 precisa de ajuste de fallback (achado esperado do STEP-01: nenhum usa `var(--accent)` hoje). Se o STEP-01 apontar algum uso legítimo de cor institucional disfarçado de `--accent` fora de `base.html`, decidir caso a caso conforme a spec: decorativo puro → cor neutra própria; função de instituição → `TODO(40.6)` explícito no CSS.
- Não tocar `.accent-bar`/`COR_PRIMARIA` de `08_orcamento.html` (confirmado no STEP-01 como mecanismo per-instituição, fora de escopo — é o que a 40.6 formaliza).

Contexto permitido:
- .ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.5/STEP-02_EXECUTION.md
- templates/base.html, templates/styles/document_system.css, tests/test_brand_isolation.py

Arquivos editáveis:
- templates/base.html
- templates/styles/document_system.css (só se o STEP-01/02 revelar uso legítimo fora de `base.html`)

Comandos permitidos:
- pytest tests/test_brand_isolation.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Introduzir a variável de microidentidade da 40.6
- Tocar `templates/08_orcamento.html` ou qualquer template de Camada 1/2 sem achado do STEP-01 que justifique
- Reintroduzir `--accent` em `:root` global

Done quando:
- `pytest tests/test_brand_isolation.py -q` passa 100%; `pytest tests/test_layer_rules.py -q` continua passando (sem regressão de camada).

Revisão:
- `--accent` realmente escopado a `.camada-0`, não mais em `:root` global?
- Nenhum template de Camada 1/2 tocado sem justificativa do STEP-01?
- Nenhuma regressão em `test_layer_rules.py`?

---

### STEP-04 — Verificação

Status: executed, aguardando revisão
Owner: executor
Type: validation

Objetivo:
- Rodar `tests/test_brand_isolation.py` contra todos os 16 templates de Camada 1/2 confirmados.
- Revisar visualmente (screenshot ou inspeção do CSS computado já coberta pelo teste) qualquer template que dependia de `--accent` para não sair "sem cor nenhuma" — achado esperado do STEP-01/03: nenhum dependia, então esta verificação é confirmação, não correção.
- Rodar suíte completa (`pytest tests/ -q`) e confirmar ausência de regressão nova.

Contexto permitido:
- Tudo dos steps anteriores

Arquivos editáveis:
- .ai/runs/ISSUE-40.5/ (execution report, screenshot se necessário)

Comandos permitidos:
- pytest tests/ -q
- pytest tests/test_brand_isolation.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Alterar comportamento implementado no STEP-03

Done quando:
- `pytest tests/ -q` sem regressão nova atribuível a esta issue (falhas pré-existentes de symlink no Windows, se aparecerem, documentar como não relacionadas, seguindo o precedente da 40.3/40.4 STEP-04).

Revisão:
- Segunda opinião sobre eventual falha na suíte completa; confirmar que nenhum template de Camada 1/2 ficou "sem cor" por regressão não prevista.

---

### STEP-05 — Docs

Status: pending
Owner: executor
Type: documentation

Objetivo:
- `templates/README.md`: adicionar seção "Isolamento de Marca" conforme esqueleto da spec, ajustada ao mecanismo real (`.camada-0` em `base.html`) confirmado no STEP-03.
- Resolver impacto documental declarado (`docs/INDICE_DOCUMENTACAO.md`) se aplicável.

Contexto permitido:
- templates/README.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/runs/ISSUE-40.5/STEP-03_EXECUTION.md

Arquivos editáveis:
- templates/README.md
- docs/INDICE_DOCUMENTACAO.md

Comandos permitidos:
- nenhum comando necessário

Proibido:
- Alterar código

Done quando:
- `templates/README.md` tem a seção "Isolamento de Marca"; impacto documental resolvido.

Revisão:
- (auto-approve, low-risk)

---

## Histórico

- STEP-01 executado (reading). Confirmou os 3 achados preliminares sem correção: `--accent` só existe em `templates/base.html` (def. linha 24, uso linha 53); `base.html` continua órfão (0 templates estendem), então `--accent` não vaza hoje; `.accent-bar` de `08_orcamento.html` usa `{{COR_PRIMARIA}}` (Jinja per-instituição), coincidência de nome. Entregou `NON_LAYER0_TEMPLATES` (16 templates) para o STEP-02, recomendou teste de herança nascer GREEN por desenho e teste de escopo `.camada-0` nascer RED real. Detalhe em `.ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md`. Auto-approved (low-risk, reading). Avança para STEP-02.
- STEP-02 executado (red). Criado `tests/test_brand_isolation.py` com 2 testes: `test_diegetic_template_does_not_inherit_brand_accent` (parametrizado pelos 16 `NON_LAYER0_TEMPLATES` — nasce GREEN por desenho, mesmo precedente da 40.4/STEP-02) e `test_accent_variable_scoped_to_camada_0` (RED real hoje — `--accent` ainda em `:root` global em `templates/base.html:24`, sem seletor `.camada-0`). `pytest tests/test_brand_isolation.py -q`: 16 passed, 1 failed, confirmando exatamente a previsão do STEP-01. Detalhe em `.ai/runs/ISSUE-40.5/STEP-02_EXECUTION.md`. Type red exige revisor — REVIEW_STATUS: pending, NEXT_ACTION: review. Não avança para STEP-03 sem revisão.
- STEP-02 aprovado; aguardando orquestrador.
- STEP-02 revisado. APROVADO sem findings. Teste de herança usa computed style real via Playwright, parametriza os 16 templates `NON_LAYER0_TEMPLATES`; teste de escopo `.camada-0` RED real hoje. Nenhum template/CSS/renderer.py tocado. Detalhe em `.ai/runs/ISSUE-40.5/STEP-02_REVIEW.md`. Avança para STEP-03 (GREEN).
- STEP-02 executado (red). Criado `tests/test_brand_isolation.py`: `test_diegetic_template_does_not_inherit_brand_accent` (16 templates, GREEN por desenho — `base.html` órfão, nada herda `--accent` hoje) e `test_accent_variable_scoped_to_camada_0` (RED real — `--accent` ainda em `:root` global). `pytest tests/test_brand_isolation.py -q` → 16 passed, 1 failed, conforme previsto. Detalhe em `.ai/runs/ISSUE-40.5/STEP-02_EXECUTION.md`. Aguardando revisão (type `red`, revisor obrigatório).
- STEP-03 executado (green). `templates/base.html`: removida `--accent: #8b1a1a` de `:root` global, criado `.camada-0 { --accent: #8b1a1a; }`, `<body>` recebeu classe `camada-0` (único consumidor de `--accent` hoje via `.doc-code`). Nenhum outro template/CSS tocado (STEP-01 confirmou nenhum dos 16 templates de Camada 1/2 referencia `--accent`; `08_orcamento.html` fora de escopo). `pytest tests/test_brand_isolation.py -q` → 17 passed (test de escopo `.camada-0`, RED no STEP-02, agora GREEN); `pytest tests/test_layer_rules.py -q` → 28 passed, sem regressão. Detalhe em `.ai/runs/ISSUE-40.5/STEP-03_EXECUTION.md`. Type green exige revisor — REVIEW_STATUS: pending, NEXT_ACTION: review. Não avança para STEP-04 sem revisão.
- STEP-03 revisado. APROVADO sem findings. Confirmado por grep direto em `templates/base.html`: `:root` (linha 19) sem `--accent`; `.camada-0` (linhas 30-31) declara `--accent: #8b1a1a`; `<body class="camada-0">` (linha 109). `git diff --name-only` mostra só `templates/base.html` tocado — nenhum dos 16 templates de Camada 1/2 ou `document_system.css` alterado. `pytest tests/test_brand_isolation.py tests/test_layer_rules.py -q` → 45 passed, sem regressão. Detalhe em `.ai/runs/ISSUE-40.5/STEP-03_REVIEW.md`. Avança para STEP-04 (Verificação).
- STEP-04 executado (validation). `pytest tests/test_brand_isolation.py -q` → 17 passed; `pytest tests/test_layer_rules.py -q` → 28 passed; `pytest tests/ -q` → 5 failed, 1437 passed, 3 skipped em 230.61s. As 5 falhas são todas `Path.symlink_to` com `OSError WinError 1314` (falta de privilégio de symlink no Windows) em `test_blind_bundle_generator.py`, `test_blind_bundle_leak_checker.py` (3) e `test_blind_bundle_sanitizer.py` — nenhuma toca `templates/`, `test_brand_isolation.py` ou `test_layer_rules.py`; mesmo padrão pré-existente documentado nas 40.3/40.4 STEP-04, não atribuível a esta issue. Verificação visual dispensada: os 17 testes de `test_brand_isolation.py` já inspecionam computed style real via Playwright e confirmam que nenhum dos 16 templates diegéticos ficou sem cor. Detalhe em `.ai/runs/ISSUE-40.5/STEP-04_EXECUTION.md`. Type validation exige revisor — REVIEW_STATUS: pending, NEXT_ACTION: review. Não avança para STEP-05 sem revisão.
- STEP-04 revisado. APROVADO sem findings. Confirmado por mtime: `templates/base.html` (21:40) e `tests/test_brand_isolation.py` (21:36) anteriores à criação do STEP-04_EXECUTION.md (21:48) — nenhum tocado neste step. Comandos rodados batem com allowlist (`pytest tests/test_brand_isolation.py -q`, `pytest tests/test_layer_rules.py -q`, `pytest tests/ -q`). 5 falhas de symlink Windows confirmadas como pré-existentes/não relacionadas, mesmo padrão 40.3/40.4. Detalhe em `.ai/runs/ISSUE-40.5/STEP-04_REVIEW.md`. Avança para STEP-05 (Docs).
- STEP-05 executado (documentation). Adicionada seção "Isolamento de Marca (ISSUE-40.5)" em `templates/README.md`: regra ("marca Indiciário só existe em Camada 0"), mecanismo real (`.camada-0` em `templates/base.html`, `<body class="camada-0">`), referência a `tests/test_brand_isolation.py`. `docs/INDICE_DOCUMENTACAO.md` conferido: sem entrada para `templates/README.md`, edição dispensada (mesmo padrão de 40.3/40.4). Nenhum código tocado. Detalhe em `.ai/runs/ISSUE-40.5/STEP-05_EXECUTION.md`. Auto-approved (low-risk, documentation). Todos os 3 critérios de aceite satisfeitos — issue concluída.
- STEP-04 revisado. APROVADO sem findings. Detalhe em `.ai/runs/ISSUE-40.5/STEP-04_REVIEW.md`. Avança para STEP-05 (docs).
- STEP-04 executado (validation). `pytest tests/test_brand_isolation.py -q` → 17 passed; `pytest tests/test_layer_rules.py -q` → 28 passed; `pytest tests/ -q` → 5 failed, 1437 passed, 3 skipped — as 5 falhas são pré-existentes (symlink Windows, `WinError 1314`, mesmo padrão 40.3/40.4), sem relação com `--accent`/`.camada-0`. Nenhum template de Camada 1/2 ficou sem cor. Detalhe em `.ai/runs/ISSUE-40.5/STEP-04_EXECUTION.md`. Aguardando revisão (type `validation`, revisor obrigatório).
- STEP-03 revisado. APROVADO sem findings. Confirmado via grep que `--accent` saiu de `:root` e vive só em `.camada-0` (linhas 30-31 de `base.html`), `<body class="camada-0">` preserva `.doc-code`. Só `templates/base.html` tocado. `pytest tests/test_brand_isolation.py tests/test_layer_rules.py -q` → 45 passed. Detalhe em `.ai/runs/ISSUE-40.5/STEP-03_REVIEW.md`. Avança para STEP-04.
- STEP-03 executado (green). `--accent: #8b1a1a` movida de `:root` global para `.camada-0` em `templates/base.html`; `<body class="camada-0">` adicionado (único consumidor, via `.doc-code`). `pytest tests/test_brand_isolation.py -q` → 17 passed; `pytest tests/test_layer_rules.py -q` → 28 passed. Nenhum outro template/CSS tocado. Detalhe em `.ai/runs/ISSUE-40.5/STEP-03_EXECUTION.md`. Aguardando revisão (type `green`, revisor obrigatório).
- Orquestrador formalizou os 5 steps acima (campos de controle + contratos) a partir do resumo em prosa em "Passos (referência para o executor)" e da `ISSUE-40.5_SPEC.md`. Não houve replanejamento de sequência — mesma ordem STEP-01 a STEP-05 já definida na issue/spec. Levantamento preliminar próprio (a confirmar formalmente pelo executor no STEP-01): `grep -rn -- "--accent" templates/ generator/` só encontra `templates/base.html` (definição em `:root` e uso em `.doc-code`); nenhum outro template ou `generator/` referencia `--accent`. `templates/base.html` é órfão (achado herdado da 40.3: "0 templates estendem base.html, arquivo não carregado pelo pipeline") — se confirmado, `--accent` não vaza hoje para nenhum template ativo, e o trabalho real da 40.5 é escopar a declaração por disciplina/regressão futura, não corrigir um vazamento em produção. `templates/08_orcamento.html` tem `.accent-bar` mas usa `{{COR_PRIMARIA}}` (Jinja, per-instituição), não a CSS var `--accent` — coincidência de nome, fora de escopo. Reaproveitada a classificação de Camada 0/1/2 da 40.3 (`.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md`): 16 templates diegéticos (`PAPER_LAYER_TEMPLATES` + `SCREEN_LAYER_TEMPLATES`) formam `NON_LAYER0_TEMPLATES` para o STEP-02.
- STEP-05 executado (documentation). Adicionada seção "Isolamento de Marca (ISSUE-40.5)" a `templates/README.md`, com regra, mecanismo real (`.camada-0` em `base.html`, achado STEP-01/03) e referência a `tests/test_brand_isolation.py`. `docs/INDICE_DOCUMENTACAO.md` verificado (`grep -n "templates/" docs/INDICE_DOCUMENTACAO.md` sem resultado) — arquivo não rastreia `templates/README.md`, impacto documental dispensado, não editado. Nenhum código tocado. Detalhe em `.ai/runs/ISSUE-40.5/STEP-05_EXECUTION.md`. Type documentation é auto-approve/low-risk conforme contrato do step, mas aguardando revisão/avanço do orquestrador.

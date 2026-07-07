# ISSUE-40.3 — Regras de camada: Tela vs. Papel + remoção do chrome do jogo

STATUS: done
CURRENT_STEP: STEP-05
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-05
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.3/STEP-05_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-40.3/STEP-04_REVIEW.md
BLOCKER: none

**Status:** especificada, pronta para execução
**Prioridade:** P1
**Depende de:** 40.1
**Bloqueia:** 40.4, 40.5, 40.6

## Objetivo

Formalizar a distinção entre dois vocabulários visuais hoje misturados:

- **Camada 1 (tela)** — e-mail, WhatsApp, rede social: são *prints de tela*, então sombra, `border-radius` e chrome de app são corretos e esperados.
- **Camada 2 (papel)** — boletim, orçamento, contrato, manual, etc.: são documentos impressos. Papel não projeta sombra de si mesmo, não tem `border-radius`, não tem gradiente.

Hoje o CSS mistura os dois vocabulários (ex.: `.accent-bar` do orçamento usa `linear-gradient`, `.orcamento-dates` tem `border-radius: 6px`, `.page` tem `box-shadow` — vocabulário de card web aplicado a um documento de papel).

Além disso, o `base.html` imprime `doc-code` (`DOC-000`), título e "Envelope N" em todo template que o estende — chrome de jogo vazando para dentro da evidência diegética. O `.doc-player { display:none }` mitiga parcialmente, mas o header é estrutural no `base.html`, não opcional.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar a distinção Camada 1 / Camada 2 como regra obrigatória para qualquer template novo.
- `framework/09_SISTEMA_VISUAL.md` (criado na 40.2): adicionar seção "Sistema de Camadas".

## Critério de aceite

1. Todo template de Camada 2 não usa `box-shadow`, `border-radius` nem `gradient` em elementos que representam a superfície do papel.
2. Templates de Camada 1 continuam podendo usar esses recursos (chrome de app é uma escolha correta ali).
3. Nenhum template diegético (Camada 1 ou 2) renderiza `doc-code`, título de jogo ou "Envelope N" na view do jogador — esse chrome só aparece na view do facilitador/protocolo (Camada 0).
4. Teste automatizado comprova os itens 1-3 para os templates existentes.

## Passos (referência para o executor)

1. STEP-01 — Mapear todos os templates existentes e classificá-los em Camada 0/1/2 (usar o inventário do diagnóstico como ponto de partida, confirmar contra o repo atual).
2. STEP-02 — RED: teste que inspeciona o CSS computado de cada template de Camada 2 e falha se encontrar `box-shadow`/`border-radius`/`gradient` na superfície do papel; teste que renderiza a view do jogador e falha se `doc-code`/"Envelope N" aparecer no DOM visível.
3. STEP-03 — GREEN: refatorar `document_system.css` introduzindo as classes utilitárias de camada; refatorar `base.html` para que o chrome de jogo só exista em templates de Camada 0 (extração do header para um partial próprio, não herança automática).
4. STEP-04 — Rodar toda a suíte de templates existentes contra os novos testes, ajustar cada template que falhar.
5. STEP-05 — Docs: `templates/README.md` + `framework/20_SISTEMA_VISUAL.md` (renomeado de `09_SISTEMA_VISUAL.md` na 40.2/STEP-05_FIX-01; spec ainda cita nome antigo, corrigido aqui).

Ver `ISSUE-40.3_SPEC.md` para o detalhamento técnico.

---

### STEP-01 — Mapeamento e classificação

Status: pending
Owner: executor
Type: reading

Objetivo:
- Listar todos os templates em `templates/` (não só os citados no diagnóstico) e classificar cada um em Camada 0 (jogo), 1 (tela) ou 2 (papel).
- Confirmar inventário real: `00_envelope_capa.html`; `01_email.html`, `02_whatsapp.html`, `02_whatsapp2.html`, `03_twitter.html`; `04_boletim.html` a `11_testamento_rascunho.html`; mais `base.html`, `facilitator_guide.html`, `dicas_contextuais.html`, `floorplan.html`, `print_guide.html`, `printable_cards.html`, `visual_character_card.html`, `visual_location_card.html`, `visual_map.html` — decidir camada de cada um (facilitator_guide/dicas/print_guide são candidatos a Camada 0; visual_*/floorplan a confirmar).
- Confirmar quais templates `{% extends %}` `base.html` e onde exatamente `doc-code`/título/"Envelope N" são impressos (`templates/base.html` linhas ~94-97 confirmadas nesta sessão).
- Registrar no execution report: tabela final de classificação por template, lista de quem estende `base.html`, e recomendação de mecanismo (extração de partial vs. flag `SHOW_GAME_CHROME`) com justificativa de esforço.

Contexto permitido:
- templates/*.html (todos)
- templates/base.html
- templates/styles/document_system.css
- templates/README.md
- .ai/issues/ISSUE-40.3.md
- .ai/issues/ISSUE-40.3_SPEC.md
- docs/ESTADO_ATUAL.md

Arquivos editáveis:
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md (relatório apenas)

Comandos permitidos:
- rtk read, rtk grep (ou Read/Grep equivalentes) — só leitura

Proibido:
- Editar qualquer template, CSS ou base.html
- Rodar pytest/ruff

Done quando:
- Execution report tem tabela de classificação completa (Camada 0/1/2) para todos os templates de `templates/*.html`, lista de quem estende `base.html`, e recomendação de mecanismo para STEP-03.

Revisão:
- (auto-approve, low-risk)

---

### STEP-02 — RED

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_layer_rules.py` com dois testes parametrizados, adaptados ao inventário real confirmado no STEP-01 (não à lista ilustrativa da spec):
  1. `test_paper_layer_has_no_screen_chrome` — para cada template de Camada 2, inspeciona CSS computado (ou regras aplicadas) da superfície do papel e falha se achar `box-shadow`/`border-radius`/`linear-gradient`/`radial-gradient` != `none`.
  2. `test_diegetic_view_has_no_game_chrome` — para cada template de Camada 1/2, renderiza a view do jogador e falha se `doc-code`, título de jogo ou "Envelope N" aparecerem no DOM visível (ausentes, não só `display:none`).
- Ambos os testes devem falhar hoje (RED real) — CSS atual mistura vocabulário (`.accent-bar` gradient, `.orcamento-dates` border-radius, `.page` box-shadow) e `base.html` imprime chrome estrutural.

Contexto permitido:
- Tudo do STEP-01 + .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md
- templates/*.html, templates/base.html, templates/styles/document_system.css
- tests/test_font_vendoring.py (referência de padrão de teste que renderiza template + inspeciona CSS computado via Playwright)

Arquivos editáveis:
- tests/test_layer_rules.py (novo)

Comandos permitidos:
- pytest tests/test_layer_rules.py -q

Proibido:
- Alterar templates, CSS ou base.html
- Tornar os testes tautológicos (ex.: checar só presença de classe, não o efeito CSS real)

Done quando:
- `tests/test_layer_rules.py` existe com os dois testes parametrizados por todo o inventário do STEP-01; ambos falham hoje (RED documentado no execution report com output real do pytest).

Revisão:
- Testes realmente inspecionam CSS computado / DOM renderizado, não só grep de string em arquivo-fonte?
- Parametrização cobre o inventário completo do STEP-01, não só os templates citados na spec?

---

### STEP-03 — GREEN

Status: pending
Owner: executor
Type: green

Objetivo:
- Em `templates/styles/document_system.css`: introduzir `.layer-screen` (Camada 1, permissivo) e `.layer-paper` (Camada 2, reset `box-shadow`/`border-radius`/`background-image`/gradient) conforme esqueleto da spec. Aplicar as classes nos templates certos (conforme classificação do STEP-01). Limpar as origens pontuais (`.accent-bar`, `.orcamento-dates`, `.page` etc.) que hoje usam esse vocabulário em templates de papel — não depender só do `!important` de rede de segurança.
- Em `templates/base.html`: extrair o header estrutural (`doc-code`, título, "Envelope N") para um partial próprio incluído apenas por templates de Camada 0, OU introduzir flag `SHOW_GAME_CHROME` (default `false`) — usar a recomendação do STEP-01, registrar no report qual caminho foi escolhido e por quê (decisão de arquitetura, não só CSS, conforme pedido da spec).
- Ajustar cada template que o STEP-02 apontar como falho.

Contexto permitido:
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.3/STEP-02_EXECUTION.md
- templates/*.html, templates/base.html, templates/styles/document_system.css, tests/test_layer_rules.py

Arquivos editáveis:
- templates/styles/document_system.css
- templates/base.html
- templates/*.html (qualquer template que precise da classe de camada ou ajuste pontual)
- generator/renderer.py (só se a flag `SHOW_GAME_CHROME` exigir passagem de contexto adicional — registrar se tocado)

Comandos permitidos:
- pytest tests/test_layer_rules.py -q
- ruff check generator/ (só se generator/ for tocado)

Proibido:
- Implementar paleta papel-cor por tipo de documento (40.4 — fora de escopo)
- Isolar `--accent` da marca (40.5 — fora de escopo)
- Adicionar mapa ao Hotel Aurora ou alterar narrativa de canônicos

Done quando:
- `pytest tests/test_layer_rules.py -q` passa 100%; decisão de arquitetura (partial vs. flag) registrada no report com justificativa.

Revisão:
- Camada 1 continua podendo usar sombra/radius/gradient (critério de aceite #2)?
- Chrome de jogo realmente ausente do DOM da view do jogador, não só oculto via CSS (critério de aceite #3)?
- Escopo não vazou para 40.4/40.5?

---

### STEP-04 — Verificação de regressão

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar `tests/test_layer_rules.py` contra todo o inventário do STEP-01 (não só os templates citados no diagnóstico) — confirmar que nada ficou de fora.
- Rodar suíte completa e confirmar ausência de regressão introduzida por esta issue.
- Rodar os builds reais dos dois canônicos (iniciante e intermediário) com `--strict` para confirmar que a extração de chrome/partial não quebrou o pipeline de build.

Contexto permitido:
- Tudo dos steps anteriores

Arquivos editáveis:
- tests/test_layer_rules.py (só ajuste pequeno, se necessário — não mudar critério)

Comandos permitidos:
- pytest tests/test_layer_rules.py -q
- pytest tests/ -q
- python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
- python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict

Proibido:
- Alterar comportamento implementado no STEP-03

Done quando:
- `pytest tests/ -q` passa sem regressão nova; os dois builds `--strict` completam sem erro.

Revisão:
- Segunda opinião sobre eventual falha na suíte completa ou no build.

---

### STEP-05 — Docs

Status: pending
Owner: executor
Type: documentation

Objetivo:
- `templates/README.md`: adicionar seção "Sistema de Camadas" (conforme esqueleto da spec, ajustado ao mecanismo real escolhido no STEP-03).
- Estender `framework/20_SISTEMA_VISUAL.md` (nome real pós-renumeração da 40.2 — não `09_SISTEMA_VISUAL.md` como a spec cita) com a mesma seção, linkando para o README.
- Resolver impacto documental declarado em `docs/INDICE_DOCUMENTACAO.md` se aplicável.

Contexto permitido:
- templates/README.md
- framework/20_SISTEMA_VISUAL.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/runs/ISSUE-40.3/STEP-03_EXECUTION.md

Arquivos editáveis:
- templates/README.md
- framework/20_SISTEMA_VISUAL.md
- docs/INDICE_DOCUMENTACAO.md

Comandos permitidos:
- nenhum comando necessário

Proibido:
- Alterar código
- Reintroduzir referência ao nome antigo `09_SISTEMA_VISUAL.md`

Done quando:
- `templates/README.md` tem a seção "Sistema de Camadas"; `framework/20_SISTEMA_VISUAL.md` estendido com a mesma seção linkando ao README; impacto documental resolvido.

Revisão:
- (auto-approve, low-risk)

---

## Histórico

- STEP-05 executado (docs). Seção "Sistema de Camadas" adicionada em
  `templates/README.md` e em `framework/20_SISTEMA_VISUAL.md` (linkando ao
  README), substituindo o placeholder de camada/microidentidade pela seção
  real de camada (microidentidade/40.6 segue como placeholder, não
  concluída). Conteúdo alinhado ao mecanismo real confirmado no
  STEP-03_EXECUTION.md (`_injetar_classes_body`,
  `TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER` em `generator/renderer.py`,
  `base.html` órfão). `docs/INDICE_DOCUMENTACAO.md` conferido: linha de
  `20_SISTEMA_VISUAL.md` já cobria 40.3/40.6 genericamente, sem edição
  necessária. Nenhum código alterado, só `.md`. Nenhuma reintrodução de
  `09_SISTEMA_VISUAL.md`. Detalhe completo em
  `.ai/runs/ISSUE-40.3/STEP-05_EXECUTION.md`. Aguardando revisão.
- STEP-04 aprovado; aguardando orquestrador.
- STEP-04 executado (validação). `pytest tests/test_layer_rules.py -q` → 28
  passed, cobre inventário completo do STEP-01. `pytest tests/ -q` → 5
  failed, 1416 passed, 3 skipped — as 5 falhas são pré-existentes,
  `OSError WinError 1314` em `Path.symlink_to` (falta privilégio de symlink
  no Windows local), em `test_blind_bundle_generator.py`,
  `test_blind_bundle_leak_checker.py` (3x) e
  `test_blind_bundle_sanitizer.py`, sem relação com templates/CSS/base.html
  tocados por 40.3 — nenhuma regressão nova. Build `--strict` do iniciante e
  do intermediário completam sem erro (QA/Graph passed nos dois). Detalhe
  completo em `.ai/runs/ISSUE-40.3/STEP-04_EXECUTION.md`. Aguardando
  revisão.
- STEP-03 revisado e aprovado (STEP-03_REVIEW.md). Reprodução independente
  confirmou GREEN real (28 passed) e `ruff check generator/` limpo. Origem
  limpa verificada por grep independente nos 8 templates de papel (1 falso
  positivo descartado: `border-radius: 0` em `06_log_acesso.html`, computa
  `0px`, conforme ao critério). Decisão de arquitetura sobre `base.html`
  (nem partial, nem flag `SHOW_GAME_CHROME`) aceita: justificada contra
  achado factual do STEP-01 (0 templates estendem `base.html`, arquivo não
  carregado pelo pipeline), não uma fuga do contrato — critério de aceite
  #3 permanece satisfeito pelo teste automatizado. Escopo 40.4/40.5
  confirmado sem vazamento. Nenhuma correção necessária. Avança para
  STEP-04.
- STEP-03 executado (GREEN). `.layer-screen`/`.layer-paper` adicionadas em
  `document_system.css` (reset `!important` como rede de segurança);
  injeção via `_injetar_classes_body` em `generator/renderer.py` (novo
  `TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER`), mesmo mecanismo de
  `doc-type-*`/`doc-family-*`, não herança Jinja. Origem de
  `box-shadow`/`border-radius`/gradiente limpa nos 8 templates de papel que
  violavam (`04_boletim.html` .. `11_testamento_rascunho.html`). Decisão de
  arquitetura sobre `base.html`: nem partial nem flag `SHOW_GAME_CHROME`
  (arquivo é órfão, achado do STEP-01) — mantido como scaffold documentado
  via comentário HTML, não deletado. `pytest tests/test_layer_rules.py -q`
  → 28 passed; `ruff check generator/` → all checks passed. Detalhe completo
  em `.ai/runs/ISSUE-40.3/STEP-03_EXECUTION.md`. Aguardando revisão.
- STEP-02 revisado e aprovado (STEP-02_REVIEW.md). Reprodução independente
  confirmou RED real (8 failed, 20 passed), bate com execution report.
  `test_diegetic_view_has_no_game_chrome` passar hoje aceito como esperado
  (achado factual do STEP-01, não teste fraco). Escopo amplo do teste de
  papel (todo elemento do body) aceito como leitura correta do critério de
  aceite #1. Nenhuma correção necessária. Avança para STEP-03.
- STEP-02 executado; aguardando revisão.
- Orquestrador formalizou os 5 steps acima (campos de controle + contratos) a partir do resumo em prosa já existente em "Passos (referência para o executor)". Não houve replanejamento de sequência — mesma ordem e escopo de STEP-01 a STEP-05 já definidos na issue/spec. Correção aplicada durante formalização: referência a `framework/09_SISTEMA_VISUAL.md` (issue e spec) trocada por `framework/20_SISTEMA_VISUAL.md`, nome real após renumeração feita na 40.2/STEP-05_FIX-01 (colisão com `09_TEMPLATE_GABARITO.md`). Inventário real de templates levantado nesta sessão (11 templates numerados + base.html + facilitator/dicas/print_guide/visual_*/floorplan/printable_cards), mais amplo que a lista ilustrativa da spec — STEP-01 formalizado para cobrir o inventário completo, não só os 3 templates de papel citados no diagnóstico.
- STEP-05 executado (documentation): seção "Sistema de Camadas (ISSUE-40.3)" adicionada em `templates/README.md` e em `framework/20_SISTEMA_VISUAL.md` (linkando ao README), `docs/INDICE_DOCUMENTACAO.md` conferido sem necessidade de edição. Nenhum código tocado, nenhum comando exigido pelo step. Auto-approved (low-risk, documentation). Sem próximo step — issue concluída.

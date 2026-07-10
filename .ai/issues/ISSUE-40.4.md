# ISSUE-40.4 — Papel-cor como taxonomia + remoção do envelhecimento artificial do boletim

STATUS: done
CURRENT_STEP: STEP-05
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-05
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.4/STEP-05_EXECUTION.md
LAST_REVIEW_REPORT: n/a (auto-approve, low-risk)
BLOCKER: none

**Status:** concluída (ver `STATUS: done` acima)
**Prioridade:** P1
**Depende de:** 40.3
**Bloqueia:** —

## Objetivo

Duas correções específicas do `04_boletim.html` e da família de documentos policiais/periciais:

1. **Remover a textura de "documento envelhecido"** (`radial-gradient` âmbar) e o `box-shadow` inset do boletim. Um documento datado de ontem é limpo — o que marca burocracia é o formulário (linhas, campos, carimbo), não o envelhecimento artificial. Envelhecer papel novo é tell clássico de prop de jogo.
2. **Implementar cor como taxonomia funcional**, não decorativa: boletim em verde (`#e4f2e4`), depoimento em amarelo (`#fdf7d8`), e reservar o token para laudo pericial (`#eef0f6`, azulado — o template do laudo em si é P3, fora deste lote, mas o token de cor é definido agora para não precisar retrabalhar a paleta depois). Cores chapadas, sem gradiente.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar a paleta papel-cor e o princípio "cor é taxonomia, não decoração".

## Critério de aceite

1. `04_boletim.html` não tem `radial-gradient` nem `box-shadow` inset.
2. Boletim e depoimento usam as cores de fundo definidas, chapadas.
3. Token de cor do laudo pericial existe em `document_system.css` (mesmo sem template consumindo ainda).
4. Teste visual comprova 1 e 2.

## Passos (referência para o executor)

1. STEP-01 — Confirmar que `.layer-paper` da 40.3 já está aplicado a `04_boletim.html` (pré-requisito).
2. STEP-02 — RED: teste que falha se `04_boletim.html` tiver `radial-gradient` ou `box-shadow` inset no CSS computado da superfície do papel.
3. STEP-03 — GREEN: remover a textura de envelhecimento; adicionar tokens `--paper-boletim`, `--paper-depoimento`, `--paper-laudo` em `document_system.css` e aplicá-los.
4. STEP-04 — Verificar visualmente (screenshot) o antes/depois do boletim.
5. STEP-05 — Docs: `templates/README.md`.

Ver `ISSUE-40.4_SPEC.md` para o detalhamento técnico.

---

### STEP-01 — Levantamento

Status: pending
Owner: executor
Type: reading

Objetivo:
- Confirmar se `04_boletim.html` tem template próprio para "depoimento" ou se é o mesmo arquivo físico usado para os dois tipos de documento. Achado preliminar do orquestrador a confirmar/corrigir: `generator/renderer.py` mapeia tanto `"boletim"` quanto `"depoimento"` para o mesmo arquivo `04_boletim.html` (dict perto da linha 774), e `TEMPLATE_DOCUMENT_CLASS["04_boletim.html"] = "depoimento"` (linha 62) só vale como fallback quando `dados["TIPO_DOCUMENTAL_SLUG"]` não é passado — ou seja, boletim e depoimento são o MESMO template HTML, diferenciados em runtime pela classe `doc-type-boletim`/`doc-type-depoimento` injetada por `_injetar_classes_body`. Confirmar isso lendo `generator/renderer.py` inteiro (função `_classe_tipo_documental`, `_familia_visual_documental`, dict perto da linha 774) e `templates/04_boletim.html`.
- Confirmar que `DOCUMENT_TYPE_FAMILIES` mapeia `"boletim"` e `"depoimento"` para a MESMA família `"admin"` (linhas ~110-111) — isso implica que a regra de cor não pode ser feita via `.doc-family-admin .page` (não diferencia os dois), precisa ser via `.doc-type-boletim .page` / `.doc-type-depoimento .page` especificamente.
- Confirmar se a textura de envelhecimento (`radial-gradient` + `box-shadow: inset`) ainda existe em `04_boletim.html` ou em `document_system.css` aplicada a ele. Achado preliminar do orquestrador a confirmar: `templates/04_boletim.html` hoje (pós-40.3) já tem `.page { background: #fefce8; ...}` chapado, sem `radial-gradient` nem `box-shadow` — a 40.3 já removeu a origem pontual desse efeito nos 8 templates de papel (ver histórico da 40.3, STEP-03). Se confirmado, o critério de aceite #1 desta issue já está satisfeito e o trabalho real desta issue é a taxonomia de cor (itens 2-3), não remoção adicional — registrar isso explicitamente no report para recalibrar STEP-02.
- Levantar os tokens de cor já existentes em `:root` de `document_system.css` (`--ind-paper`, `--ind-paper-warm`, `--ind-paper-cool` etc.) e as regras `.doc-family-admin .page { background: var(--ind-paper-cool); ...}` para não duplicar/colidir com os novos tokens `--paper-boletim`/`--paper-depoimento`/`--paper-laudo`.
- Confirmar se existe template de depoimento separado em `templates/*depoimento*` (Glob já rodado pelo orquestrador não achou nada — confirmar de novo no repo atual).

Contexto permitido:
- templates/04_boletim.html
- templates/styles/document_system.css
- generator/renderer.py
- templates/README.md
- tests/test_layer_rules.py
- .ai/issues/ISSUE-40.4.md
- .ai/issues/ISSUE-40.4_SPEC.md
- .ai/issues/ISSUE-40.3.md (histórico de referência)

Arquivos editáveis:
- .ai/runs/ISSUE-40.4/STEP-01_EXECUTION.md (relatório apenas)

Comandos permitidos:
- rtk read, rtk grep (ou Read/Grep equivalentes) — só leitura

Proibido:
- Editar template, CSS ou renderer.py
- Rodar pytest/ruff

Done quando:
- Execution report confirma (ou corrige) os quatro achados preliminares acima, com citação de linha exata, e recomenda o mecanismo de aplicação de cor (via `doc-type-*`, não `doc-family-*`) para o STEP-03.

Revisão:
- (auto-approve, low-risk)

---

### STEP-02 — RED

Status: done
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_paper_color_taxonomy.py`, seguindo o padrão de `tests/test_layer_rules.py` (renderiza template via `generator.font_fidelity._montar_html` + Playwright, inspeciona CSS computado — não grep de string em arquivo-fonte).
- `test_boletim_has_no_aging_texture`: falha se o `background-image` computado de `.page` em `04_boletim.html` (renderizado com `TIPO_DOCUMENTAL_SLUG="boletim"`) não for `none`, ou se `box-shadow` computado incluir `inset`. Ajustar a expectativa (falha ou já passa) conforme o achado real do STEP-01 — se a textura já foi removida pela 40.3, este teste nasce GREEN (documentar isso explicitamente no report, não forçar RED artificial) e funciona como guarda de regressão.
- `test_boletim_uses_taxonomy_color`: renderiza `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG="boletim"` e falha se o `background-color` computado de `.page` não corresponder a `#e4f2e4`. Este teste é RED real hoje — o token `--paper-boletim` ainda não existe.
- `test_depoimento_uses_taxonomy_color`: renderiza o MESMO `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG="depoimento"` e falha se o `background-color` computado de `.page` não corresponder a `#fdf7d8`. RED real hoje (mesma família `admin`, mesma cor que boletim).
- `test_paper_laudo_token_exists`: falha se `--paper-laudo: #eef0f6` não estiver declarado em `:root` de `document_system.css` (sem exigir template consumindo — critério de aceite #3). RED real hoje.

Contexto permitido:
- .ai/runs/ISSUE-40.4/STEP-01_EXECUTION.md
- templates/04_boletim.html, templates/styles/document_system.css, generator/renderer.py
- tests/test_layer_rules.py, tests/test_font_vendoring.py (padrão de teste via Playwright)

Arquivos editáveis:
- tests/test_paper_color_taxonomy.py (novo)

Comandos permitidos:
- pytest tests/test_paper_color_taxonomy.py -q

Proibido:
- Alterar template, CSS ou renderer.py
- Teste tautológico (checar só presença de variável CSS no texto-fonte, não o valor computado renderizado)

Done quando:
- `tests/test_paper_color_taxonomy.py` existe com os 4 testes; execution report documenta output real do pytest (quais falham hoje e por quê, incluindo se o teste de aging texture nasce GREEN).

Revisão:
- Testes inspecionam CSS computado via Playwright, não grep de string?
- Teste de depoimento realmente força `TIPO_DOCUMENTAL_SLUG="depoimento"` no mesmo arquivo físico, não assume template separado inexistente?

---

### STEP-03 — GREEN

Status: pending
Owner: executor
Type: green

Objetivo:
- Em `templates/styles/document_system.css`, dentro de `:root`, adicionar:
  ```css
  --paper-boletim: #e4f2e4;    /* verde — documentos policiais oficiais */
  --paper-depoimento: #fdf7d8; /* amarelo — depoimentos/transcrições */
  --paper-laudo: #eef0f6;      /* azulado — reservado para laudo pericial (P3) */
  ```
- Adicionar regras `.doc-type-boletim .page { background: var(--paper-boletim); }` e `.doc-type-depoimento .page { background: var(--paper-depoimento); }` em `document_system.css` (não em `.doc-family-admin`, que os dois tipos compartilham — ver achado do STEP-01). Confirmar que essas regras vencem `.doc-family-admin .page { background: var(--ind-paper-cool); ...}` na cascata (especificidade igual — ordem de declaração decide; colocar depois, ou aumentar especificidade se necessário) sem quebrar o `border: var(--ind-line-strong)` que a família admin também define.
- Em `templates/04_boletim.html`: remover `background: #fefce8` hardcoded de `.page` (se o STEP-01 confirmar que o token deve vencer) — deixar o background vir só do CSS injetado por `document_system.css` via classe `doc-type-*`. Se `04_boletim.html` não tiver mais nenhuma textura de envelhecimento (achado esperado do STEP-01), não há remoção adicional de `radial-gradient`/`box-shadow` a fazer — só ajustar a origem do background.
- Não tocar `.doc-family-admin` nem outros templates de papel fora de `04_boletim.html`.

Contexto permitido:
- .ai/runs/ISSUE-40.4/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.4/STEP-02_EXECUTION.md
- templates/04_boletim.html, templates/styles/document_system.css, tests/test_paper_color_taxonomy.py

Arquivos editáveis:
- templates/styles/document_system.css
- templates/04_boletim.html

Comandos permitidos:
- pytest tests/test_paper_color_taxonomy.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Criar template completo de laudo pericial (fora de escopo, P3)
- Tocar outros templates de papel (`05_carta.html` a `11_testamento_rascunho.html`)
- Reintroduzir `radial-gradient`/`box-shadow: inset` em `04_boletim.html`

Done quando:
- `pytest tests/test_paper_color_taxonomy.py -q` passa 100%; `pytest tests/test_layer_rules.py -q` continua passando (sem regressão de camada).

Revisão:
- Boletim e depoimento (mesmo arquivo físico) renderizam com cores diferentes de fato, via `doc-type-*`, não via `doc-family-*`?
- `--paper-laudo` existe em `:root` mesmo sem consumidor (critério de aceite #3)?
- Nenhuma regressão em `test_layer_rules.py` (camada/sombra/radius/gradiente continua zero em `04_boletim.html`)?

---

### STEP-04 — Verificação visual

Status: pending
Owner: executor
Type: validation

Objetivo:
- Renderizar `04_boletim.html` via `generator/renderer.py` (ou via o mesmo mecanismo Playwright usado nos testes) com `TIPO_DOCUMENTAL_SLUG="boletim"` e novamente com `"depoimento"`, capturar screenshot de cada, salvar em `.ai/runs/ISSUE-40.4/` (ex.: `boletim_depois.png`, `depoimento_depois.png`).
- Confirmar visualmente: fundo verde chapado no boletim, amarelo chapado no depoimento, sem gradiente/sombra, formulário (linhas, campos, carimbo) intacto.
- Rodar suíte completa (`pytest tests/ -q`) e confirmar ausência de regressão nova.

Contexto permitido:
- Tudo dos steps anteriores

Arquivos editáveis:
- .ai/runs/ISSUE-40.4/ (screenshots + execution report)

Comandos permitidos:
- pytest tests/ -q
- pytest tests/test_paper_color_taxonomy.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Alterar comportamento implementado no STEP-03

Done quando:
- Screenshots gerados e descritos no report; `pytest tests/ -q` sem regressão nova atribuível a esta issue (falhas pré-existentes de symlink no Windows, se aparecerem, documentar como não relacionadas, seguindo o precedente da 40.3/STEP-04).

Revisão:
- Segunda opinião sobre eventual falha na suíte completa; confirmar que os screenshots batem com o critério de aceite (cores chapadas, sem gradiente).

---

### STEP-05 — Docs

Status: pending
Owner: executor
Type: documentation

Objetivo:
- `templates/README.md`: adicionar seção "Paleta Papel-Cor" (conforme esqueleto da spec), explicando que boletim e depoimento são o MESMO template físico (`04_boletim.html`) diferenciado por `doc-type-*` — não dois arquivos.
- Resolver impacto documental declarado (`docs/INDICE_DOCUMENTACAO.md`) se aplicável.

Contexto permitido:
- templates/README.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/runs/ISSUE-40.4/STEP-03_EXECUTION.md

Arquivos editáveis:
- templates/README.md
- docs/INDICE_DOCUMENTACAO.md

Comandos permitidos:
- nenhum comando necessário

Proibido:
- Alterar código

Done quando:
- `templates/README.md` tem a seção "Paleta Papel-Cor"; impacto documental resolvido.

Revisão:
- (auto-approve, low-risk)

---

## Histórico

- STEP-01 executado (reading). Confirmou os 4 achados preliminares: boletim/depoimento é o mesmo arquivo físico `04_boletim.html`, diferenciado por `doc-type-*`; ambos caem na família CSS `admin`; textura de envelhecimento já removida pela 40.3 (critério de aceite #1 já satisfeito); tokens de cor ainda não existem. Detalhe em `.ai/runs/ISSUE-40.4/STEP-01_EXECUTION.md`. Auto-approved (low-risk, reading). Avança para STEP-02.
- Orquestrador formalizou os 5 steps acima (campos de controle + contratos) a partir do resumo em prosa em "Passos (referência para o executor)" e da `ISSUE-40.4_SPEC.md`. Levantamento próprio (fora do STEP-01, a confirmar formalmente pelo executor) encontrou dois achados que mudam a forma dos steps em relação ao texto original da spec: (1) a textura de envelhecimento (`radial-gradient`/`box-shadow: inset`) parece já ter sido removida de `04_boletim.html` pela 40.3 (histórico da 40.3/STEP-03 cita limpeza nos "8 templates de papel" incluindo `04_boletim.html`) — se confirmado, critério de aceite #1 já está satisfeito e o trabalho real é só a taxonomia de cor; (2) boletim e depoimento não são templates separados, são o MESMO arquivo `04_boletim.html`, diferenciado em runtime por `TIPO_DOCUMENTAL_SLUG`/classe `doc-type-*` — e ambos caem hoje na mesma família CSS `admin`, então a regra de cor precisa ser por `doc-type-*`, não por `doc-family-*`. STEP-01 reformulado para confirmar/corrigir esses dois achados antes de STEP-02 travar a forma do teste RED.
- STEP-02 executado (red). Criado `tests/test_paper_color_taxonomy.py` com 4 testes via Playwright/CSS computado (não grep). Como `font_fidelity._montar_html` não aceita override de dados, criada função local `_montar_html_com_tipo` replicando o pipeline (`_preparar_dados_documentais` → `_injetar_css_documental` → `_injetar_classes_body` → `_injetar_cabecalho_rodape_documental` → `renderizar_html`) para forçar `TIPO_DOCUMENTAL_SLUG="boletim"`/`"depoimento"` no mesmo arquivo físico. `pytest tests/test_paper_color_taxonomy.py -q` → 3 failed, 1 passed: `test_boletim_has_no_aging_texture` nasce GREEN (textura já removida pela 40.3, confirma achado do STEP-01, vira guarda de regressão); `test_boletim_uses_taxonomy_color`, `test_depoimento_uses_taxonomy_color` e `test_paper_laudo_token_exists` são RED real (boletim e depoimento produzem hoje a mesma cor `rgb(248, 249, 251)` herdada de `.doc-family-admin .page`; token `--paper-laudo` não existe). Detalhe completo em `.ai/runs/ISSUE-40.4/STEP-02_EXECUTION.md`, incluindo recomendação para STEP-03 (ordem de declaração das regras `.doc-type-*` na cascata). Aguarda revisão (type `red`, revisor obrigatório).
- STEP-02 revisado. APROVADO sem findings. Revisor rodou `py -m pytest tests/test_paper_color_taxonomy.py -q` de forma independente e confirmou exatamente o output reportado (3 failed, 1 passed — teste 1 GREEN por desenho, testes 2-4 RED real). Confirmou que os testes usam `getComputedStyle` real via Playwright (não grep), que `_montar_html_com_tipo` replica fielmente o pipeline de `font_fidelity._montar_html`, e que `git status` não mostra alteração em template/CSS/renderer.py (proibição do step respeitada). Detalhe em `.ai/runs/ISSUE-40.4/STEP-02_REVIEW.md`. Avança para STEP-03 (GREEN).
- STEP-03 executado (green). Adicionados `--paper-boletim: #e4f2e4`, `--paper-depoimento: #fdf7d8`, `--paper-laudo: #eef0f6` em `:root` de `document_system.css`; adicionadas regras `.doc-type-boletim .page { background: var(--paper-boletim); }` e `.doc-type-depoimento .page { background: var(--paper-depoimento); }` logo após `.doc-family-admin .page` (vencem o empate de especificidade pela ordem de declaração, sem sobrescrever `border`). Removida a linha `background: #fefce8` hardcoded de `.page` em `templates/04_boletim.html` — background passa a vir só do token via classe `doc-type-*`. Nenhum `radial-gradient`/`box-shadow: inset` reintroduzido (não havia nenhum a remover, confirmado desde STEP-01/STEP-02). `pytest tests/test_paper_color_taxonomy.py -q` → 4 passed (100%); `pytest tests/test_layer_rules.py -q` → 28 passed, sem regressão. Nenhum outro template de papel tocado. Detalhe completo em `.ai/runs/ISSUE-40.4/STEP-03_EXECUTION.md`. Aguarda revisão (type `green`, revisor obrigatório).
- STEP-03 revisado. APROVADO sem divergências (severidade none). `git diff` confirma alteração restrita a `templates/04_boletim.html` (1 linha removida: `background: #fefce8`) e `templates/styles/document_system.css` (5 linhas inseridas: 3 tokens em `:root` + 2 regras `.doc-type-boletim .page`/`.doc-type-depoimento .page`), exatamente a allowlist do step. Valores dos tokens conferem (`#e4f2e4`, `#fdf7d8`, `#eef0f6`), `.doc-family-admin .page` intocada (border preservada), nenhum `radial-gradient`/`box-shadow: inset` no diff. Nenhum arquivo fora do escopo alterado (`.ai/issues/ISSUE-40.4.md` é controle da issue, esperado). Detalhe em `.ai/runs/ISSUE-40.4/STEP-03_REVIEW.md`. Avança para orquestrador decidir STEP-04.
- STEP-04 executado (validation). Renderizado `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG="boletim"` e `"depoimento"` via réplica local de `_montar_html`, screenshots do elemento `.page` salvos em `.ai/runs/ISSUE-40.4/boletim_depois.png` e `depoimento_depois.png` — confirmam visualmente fundo verde chapado (boletim) e amarelo chapado (depoimento), sem gradiente/sombra, formulário (cabeçalho, campos, rodapé/assinaturas) intacto. `pytest tests/ -q` → 1420 passed, 3 skipped, 5 failed; as 5 falhas são `os.symlink`/`WinError 1314` pré-existentes em `test_blind_bundle_generator.py`/`test_blind_bundle_leak_checker.py`/`test_blind_bundle_sanitizer.py`, não relacionadas a esta issue, mesmo padrão do precedente 40.3/STEP-04. Script auxiliar de screenshot criado e apagado dentro do próprio step (não persiste no repo). Detalhe completo em `.ai/runs/ISSUE-40.4/STEP-04_EXECUTION.md`. Aguarda revisão (type `validation`, revisor obrigatório).
- STEP-04 revisado. APROVADO sem findings. Revisor confirmou `git status` limpo além dos artefatos esperados (nenhum código/template/CSS tocado além do STEP-03 já aprovado), leu os 2 screenshots diretamente (fundo verde/amarelo chapado, sem gradiente/sombra, formulário intacto), rodou independentemente `pytest tests/test_paper_color_taxonomy.py tests/test_layer_rules.py -q` → 32 passed, e reproduziu uma das 5 falhas de symlink (`test_symlink_source_is_rejected_and_not_followed`) confirmando `OSError: WinError 1314` (privilégio SeCreateSymbolicLinkPrivilege ausente na conta), ambiental e não relacionada à taxonomia de cor — mesmo padrão do precedente 40.3. Detalhe em `.ai/runs/ISSUE-40.4/STEP-04_REVIEW.md`. Avança para STEP-05 (docs).
- STEP-05 executado (documentation). Adicionada seção "Paleta Papel-Cor (ISSUE-40.4)" em `templates/README.md` (entre a seção de Sistema de Camadas e "Próximos templates recomendados"): lista dos 3 tokens (`--paper-boletim` #e4f2e4 verde, `--paper-depoimento` #fdf7d8 amarelo, `--paper-laudo` #eef0f6 azulado/reservado P3), princípio "cor é taxonomia, não decoração" (chapado, sem gradiente, envelhecimento artificial proibido), e explicação de que boletim/depoimento são o MESMO arquivo físico `04_boletim.html` diferenciado por `TIPO_DOCUMENTAL_SLUG` → classe `doc-type-*` (não `.doc-family-admin`, compartilhada pelos dois). `docs/INDICE_DOCUMENTACAO.md` verificado via grep — nenhuma entrada referencia `templates/` ou `templates/README.md`; doc-impact resolvido diretamente em `templates/README.md`, índice não precisa de alteração. Nenhum código tocado. Detalhe em `.ai/runs/ISSUE-40.4/STEP-05_EXECUTION.md`. Auto-approved (low-risk, documentation). Todos os 4 critérios de aceite da issue satisfeitos — issue pronta para o orquestrador fechar.

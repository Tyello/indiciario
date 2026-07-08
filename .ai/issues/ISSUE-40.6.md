# ISSUE-40.6 — Microidentidades institucionais

STATUS: done
CURRENT_STEP: STEP-06
NEXT_ACTION: none
REVIEW_STATUS: auto-approved (documentation, low-risk)
LAST_COMPLETED_STEP: STEP-06
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.6/STEP-06_EXECUTION.md
LAST_REVIEW_REPORT: n/a (auto-approve)
BLOCKER: none

**Status:** concluída (STATUS: done)
**Prioridade:** P1
**Depende de:** 40.3, 40.5
**Bloqueia:** —

## Objetivo

Criar o sistema de microidentidade que a 40.5 deixou como espaço em aberto: cada instituição fictícia dentro de um caso (o museu, uma empresa, um órgão) define sua própria cor, tipografia de destaque e forma de header — e todos os documentos daquela instituição herdam essa identidade, criando coesão intra-instituição e variação inter-instituição. É a mesma lição do benchmark: o jogador reconhece "isto veio do museu" em meio segundo porque manual, log de acesso, escala e cadastro compartilham o mesmo vermelho, o mesmo logotipo-busto, o mesmo recorte de header diagonal.

## Escopo

- Novo arquivo de tokens de microidentidade (path exato a confirmar no STEP-01 — spec cita `styles/institution_identity.css`, mas o repo usa `templates/styles/` para CSS, não `styles/` top-level).
- Biblioteca de 10-15 glifos abstratos de logo em `assets/logos/`.
- Aplicação aos templates institucionais existentes: manual, `06_log_acesso.html`, cadastro, listas (guarita).

**Achado preliminar do orquestrador (a confirmar/corrigir no STEP-01):** só `templates/06_log_acesso.html` existe hoje entre os templates institucionais citados. Não há `manual.html` nem `cadastro.html` em `templates/*.html` — o STEP-01 precisa confirmar isso exaustivamente e o STEP-03 provavelmente precisa **criar** esses dois templates, não só retrofitar tokens em templates existentes.

**Não inclui** os 4 arquétipos comerciais de orçamento nem a escala/planilha nova — isso é P2/P3, fora deste lote.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar o sistema de microidentidade.
- `framework/09_SISTEMA_VISUAL.md`: adicionar seção "Microidentidades Institucionais", fechando o documento de doutrina aberto pela 40.2/40.3.

## Critério de aceite

1. Arquivo de tokens de microidentidade define `--inst-color`, `--inst-font-display`, `--inst-header-shape` (reto | diagonal | faixa-dupla) como tokens configuráveis por instituição.
2. Biblioteca de glifos existe em `assets/logos/` com pelo menos 10 opções.
3. Manual, log de acesso e cadastro de uma mesma instituição fictícia (dado de teste) renderizam com a mesma cor, fonte de destaque e forma de header.
4. Manual tem "Revisão N — data" no header e assinatura do responsável no rodapé (achado específico do diagnóstico, seção 3.6).
5. Log de acesso tem carimbo de exportação com timestamp em segundos.
6. Teste automatizado comprova a coesão intra-instituição (item 3) usando dois conjuntos de dados de instituições diferentes.

## Passos (referência para o executor)

1. STEP-01 — Confirmar que 40.3 e 40.5 estão mescladas (dependência dura); mapear estado real dos templates institucionais e mecanismo de injeção de variáveis.
2. STEP-02 — RED: teste que renderiza os documentos de duas instituições fictícias de teste e falha se os documentos da mesma instituição não compartilharem cor/fonte/forma de header, ou se documentos de instituições diferentes compartilharem.
3. STEP-03 — GREEN: criar arquivo de tokens de microidentidade, a biblioteca de glifos, e aplicar aos templates institucionais (criando manual.html/cadastro.html se confirmado que não existem).
4. STEP-04 — Verificar visualmente com os dois conjuntos de teste.
5. STEP-05 — Docs: `templates/README.md` + fechar `framework/09_SISTEMA_VISUAL.md`.

Ver `ISSUE-40.6_SPEC.md` para o detalhamento técnico.

---

### STEP-01 — Levantamento

Status: pending
Owner: executor
Type: reading

Objetivo:
- Confirmar `STATUS: done` de `.ai/issues/ISSUE-40.3.md` e `.ai/issues/ISSUE-40.5.md` (já checado pelo orquestrador nesta sessão — ambas `done`; confirmar de novo por disciplina).
- Confirmar (ou corrigir) os achados preliminares do orquestrador:
  1. `grep -rn "manual\|cadastro" templates/` não encontra `manual.html` nem `cadastro.html` em `templates/*.html`. Listar exaustivamente os `templates/*.html` existentes e classificar quais são "institucionais" (documentos que pertencem a uma instituição fictícia dentro do caso, ex.: `06_log_acesso.html`) vs. quais não são.
  2. Não existe diretório `styles/` top-level — CSS vive em `templates/styles/` (ex.: `templates/styles/document_system.css`). Definir o path real do novo arquivo de tokens (recomendação do orquestrador: `templates/styles/institution_identity.css`, seguindo a convenção existente).
  3. Não existe `assets/logos/` — confirmar e listar convenção de outros assets (`assets/fonts/`, `assets/signatures/`) para manter o mesmo padrão de nomenclatura/estrutura.
  4. `templates/08_orcamento.html` usa `{{COR_PRIMARIA}}` via Jinja simples (achado orquestrador: `grep -n "COR_PRIMARIA" generator/renderer.py` não retorna nada — não é lógica especial do renderer, é variável de contexto comum). Confirmar que o mecanismo de renderização (`generator/renderer.py` e/ou `generator/font_fidelity._montar_html`, usado por `tests/test_layer_rules.py`) já aceita injetar variáveis arbitrárias de instituição no contexto do template sem alteração de infraestrutura — ou documentar exatamente o ajuste mínimo necessário se não aceitar.
  5. Confirmar interface de `generator/signature_renderer.py` (funções disponíveis, ex. `build_signature_svg`) para reuso no rodapé do manual (critério de aceite #4).
- Registrar no execution report: confirmação/correção dos 5 achados, path final do arquivo de tokens, lista final de templates institucionais existentes vs. a criar, e recomendação para o STEP-02 sobre `_montar_html`/contexto de teste.

Contexto permitido:
- templates/*.html (todos)
- templates/styles/*.css
- generator/renderer.py
- generator/font_fidelity.py
- generator/signature_renderer.py
- assets/ (estrutura)
- .ai/issues/ISSUE-40.6.md
- .ai/issues/ISSUE-40.6_SPEC.md
- .ai/issues/ISSUE-40.3.md, .ai/issues/ISSUE-40.5.md (histórico de referência)
- tests/test_layer_rules.py (padrão de renderização em teste)

Arquivos editáveis:
- .ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md (relatório apenas)

Comandos permitidos:
- rtk read, rtk grep (ou Read/Grep equivalentes) — só leitura

Proibido:
- Editar template, CSS, renderer.py ou qualquer arquivo de produção
- Rodar pytest/ruff

Done quando:
- Execution report confirma (ou corrige) os 5 achados preliminares acima, com citação de linha/path exato, e entrega a lista final de templates institucionais + path do arquivo de tokens + confirmação do mecanismo de injeção para o STEP-02.

Revisão:
- (auto-approve, low-risk)

---

### STEP-02 — RED

Status: done (aprovado)
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_institution_identity.py`, seguindo o padrão Playwright/CSS computado de `tests/test_layer_rules.py` (renderização real via `_montar_html` ou equivalente confirmado no STEP-01 — não grep de string em arquivo-fonte).
- Usar os dois conjuntos de dados de teste da spec (`museu_teste`: `#7a1f1f`, "Libre Baskerville", `diagonal`; `empresa_teste`: `#1f4a7a`, "DM Sans", `reto`) contra os templates institucionais confirmados no STEP-01 (mínimo `06_log_acesso.html`; `manual.html`/`cadastro.html` conforme decisão do STEP-01 — se ainda não existirem, o teste deve renderizar contra as versões que o STEP-03 vai criar, então pode nascer RED por ausência de arquivo até o GREEN).
- `test_documents_of_same_institution_share_identity`: renderiza os templates de `museu_teste` e falha se `getComputedStyle` não resolver a mesma cor/fonte/forma de header em todos.
- `test_documents_of_different_institutions_do_not_share_identity`: confirma que `museu_teste` e `empresa_teste` produzem identidades distintas nos mesmos templates.
- `test_manual_has_revision_and_signature`: falha se o manual não tiver "Revisão N — data" no header e assinatura do responsável no rodapé.
- `test_access_log_has_export_stamp_with_seconds`: falha se `06_log_acesso.html` não tiver carimbo de exportação com timestamp incluindo segundos (ex.: "EXPORTADOS EM DD/MM/AAAA ÀS HH:MM:SS").
- Documentar no execution report se cada teste nasce RED real ou GREEN-por-desenho, e por quê (precedente aceito nas 40.4/40.5).

Contexto permitido:
- .ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md
- templates/*.html, templates/styles/*.css, generator/renderer.py, generator/font_fidelity.py, generator/signature_renderer.py
- tests/test_layer_rules.py (padrão de teste via Playwright)
- ISSUE-40.6_SPEC.md (INSTITUTION_TEST_DATA de referência)

Arquivos editáveis:
- tests/test_institution_identity.py (novo)

Comandos permitidos:
- pytest tests/test_institution_identity.py -q

Proibido:
- Alterar template, CSS ou renderer.py
- Teste tautológico (checar só presença de string no texto-fonte, não o computed style/DOM renderizado)

Done quando:
- `tests/test_institution_identity.py` existe com os 4 testes; execution report documenta output real do pytest (o que falha hoje e por quê).

Revisão:
- Testes inspecionam CSS computado/DOM real via Playwright, não grep?
- Cobre os dois conjuntos de dados de teste da spec?
- Teste de assinatura/revisão e de carimbo de exportação testam o conteúdo renderizado, não só a existência do template?

---

### STEP-03 — GREEN

Status: done (aguardando revisão)
Owner: executor
Type: green

Objetivo:
- Criar o arquivo de tokens de microidentidade no path confirmado pelo STEP-01, com `--inst-color`, `--inst-font-display`, `--inst-header-shape` (reto | diagonal | faixa-dupla), conforme esqueleto da spec (fallbacks neutros, classes `.institution`, `.header.shape-diagonal`, `.header.shape-faixa-dupla`).
- Criar biblioteca de 10-15 glifos SVG abstratos e genéricos em `assets/logos/glifo-01.svg` ... `glifo-NN.svg` (formas geométricas simples — evitar qualquer semelhança com marcas/logos reais).
- Aplicar `.institution` + tokens injetados via contexto de renderização (mecanismo confirmado no STEP-01) a: `templates/06_log_acesso.html` (existente) e a `manual.html`/`cadastro.html` (criar se STEP-01 confirmou ausência).
- Manual: header com `{{INST_REVISAO}} — {{INST_REVISAO_DATA}}`; rodapé com bloco de assinatura do responsável reusando `generator/signature_renderer.py`.
- Log de acesso: carimbo `EXPORTADOS EM {{DATA}} ÀS {{HORA_COM_SEGUNDOS}}`; considerar múltiplas colunas só se a verificação visual do STEP-04 mostrar tabela excessivamente longa nos dados de teste.
- Cadastro/listas: `.institution` no wrapper.

Contexto permitido:
- .ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md, .ai/runs/ISSUE-40.6/STEP-02_EXECUTION.md
- templates/*.html, templates/styles/*.css, generator/renderer.py, generator/signature_renderer.py
- tests/test_institution_identity.py
- ISSUE-40.6_SPEC.md

Arquivos editáveis:
- Arquivo de tokens de microidentidade (path confirmado no STEP-01)
- assets/logos/*.svg (novos)
- templates/06_log_acesso.html
- manual.html / cadastro.html institucionais (novos, path/nome conforme convenção de `templates/`)
- generator/renderer.py (só se STEP-01 confirmar ajuste mínimo de infraestrutura necessário para injeção por-instituição)

Comandos permitidos:
- pytest tests/test_institution_identity.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Criar os 4 arquétipos comerciais de orçamento ou a escala/planilha nova (fora de escopo, P2/P3)
- Usar glifo reconhecível como marca/logo real existente
- Tocar templates de Camada 0 (`base.html`, `facilitator_guide.html`, etc.) fora do necessário

Done quando:
- `pytest tests/test_institution_identity.py -q` passa 100%; `pytest tests/test_layer_rules.py -q` continua passando (sem regressão de camada).

Revisão:
- Tokens realmente configuráveis por instituição (não hardcoded)?
- Glifos genéricos, sem semelhança com marcas reais?
- Manual tem revisão+data no header e assinatura no rodapé de verdade (não só CSS)?
- Log de acesso tem carimbo com segundos de verdade?
- Nenhuma regressão em `test_layer_rules.py`?

---

### STEP-04 — Verificação

Status: done (revisado — regressão encontrada, ver STEP-05)
Owner: executor
Type: validation

Objetivo:
- Rodar `tests/test_institution_identity.py` com os dois conjuntos de dados de teste (`museu_teste`, `empresa_teste`).
- Verificar visualmente (screenshot lado a lado dos dois conjuntos) que a diferenciação é perceptível, não só tecnicamente presente no CSS.
- Rodar suíte completa (`pytest tests/ -q`) e confirmar ausência de regressão nova.

Contexto permitido:
- Tudo dos steps anteriores

Arquivos editáveis:
- .ai/runs/ISSUE-40.6/ (execution report, screenshots)

Comandos permitidos:
- pytest tests/ -q
- pytest tests/test_institution_identity.py -q
- pytest tests/test_layer_rules.py -q

Proibido:
- Alterar comportamento implementado no STEP-03

Done quando:
- `pytest tests/ -q` sem regressão nova atribuível a esta issue (falhas pré-existentes de symlink no Windows, se aparecerem, documentar como não relacionadas, seguindo precedente 40.3/40.4/40.5 STEP-04).
- Screenshot ou evidência equivalente confirma diferenciação visual perceptível entre `museu_teste` e `empresa_teste`.

Revisão:
- Segunda opinião sobre eventual falha na suíte completa; confirmar que a diferenciação visual é real, não só CSS não exercitado.

---

### STEP-05 — Correção (fallback de tokens de instituição)

Status: done (aprovado)
Owner: executor
Type: correction

Objetivo:
- STEP-04 encontrou regressão real (confirmada por revisor, `.ai/runs/ISSUE-40.6/STEP-04_REVIEW.md`): `pytest tests/ -q` completo passou de 5 failed (pré-existente, symlink Windows) para 10 failed. As 5 falhas novas são `PlaceholderResidualError` em modo strict porque `{{INST_COLOR}}`, `{{INST_FONT_DISPLAY}}`, `{{INST_HEADER_SHAPE}}`, `{{HORA_COM_SEGUNDOS}}` (injetados em `templates/06_log_acesso.html` no STEP-03) sobrevivem literalmente no HTML quando o documento é renderizado sem contexto de instituição — caso de todo blueprint canônico hoje.
- Falhas a corrigir: `test_package_manifests.py::test_build_package_strict_nao_gera_pdf_fake_sem_env`, `test_renderer.py::test_caso_canonico_dicas_contextuais_aparecem_no_html_debug`, `test_renderer.py::test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador`, `test_renderer.py::test_renderizar_documento_usa_familia_visual_e_emissor_de_email`, `test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`.
- Causa raiz confirmada por revisor: `_preparar_dados_documentais` em `generator/renderer.py` já usa `setdefault(...)` para outros tokens (`DOC_CONTROLE`, `NOME_CASO`, etc.) mas não tem fallback para `INST_COLOR`, `INST_FONT_DISPLAY`, `INST_HEADER_SHAPE`, `HORA_COM_SEGUNDOS`.
- Corrigir: adicionar `setdefault` com valores neutros para os 4 tokens em `_preparar_dados_documentais` (ou local equivalente confirmado no STEP-01/03), preservando o comportamento já testado por `tests/test_institution_identity.py` (não quebrar os 4 testes que dependem dos valores reais quando o contexto de instituição É fornecido).
- Reexecutar `tests/test_institution_identity.py` e `tests/test_layer_rules.py` (sem regressão) e os 5 testes antes-falhos, mais `pytest tests/ -q` completo — esperado voltar a 5 failed (só symlink Windows, pré-existente).

Contexto permitido:
- .ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md, STEP-03_EXECUTION.md, STEP-04_EXECUTION.md, STEP-04_REVIEW.md
- generator/renderer.py
- templates/06_log_acesso.html, templates/manual.html, templates/cadastro.html
- tests/test_institution_identity.py, tests/test_renderer.py, tests/test_renderer_engine.py, tests/test_package_manifests.py

Arquivos editáveis:
- generator/renderer.py (fallback dos tokens)
- templates/06_log_acesso.html / manual.html / cadastro.html (só se o fallback exigir ajuste também no template, ex. valor default direto no template em vez de contexto)

Comandos permitidos:
- pytest tests/test_institution_identity.py -q
- pytest tests/test_layer_rules.py -q
- pytest tests/test_renderer.py tests/test_renderer_engine.py tests/test_package_manifests.py -q
- pytest tests/ -q

Proibido:
- Alterar tests/test_institution_identity.py (já aprovado, contrato fixo)
- Reintroduzir os placeholders sem fallback

Done quando:
- Os 5 testes antes-falhos voltam a passar.
- `tests/test_institution_identity.py` continua 4/4 passed (sem regressão do comportamento com contexto de instituição).
- `pytest tests/ -q` completo volta a 5 failed (só symlink Windows, pré-existente) / 1441 passed (ajustar contagem exata no relatório).

Revisão:
- Fallback é neutro e não quebra a coesão intra-instituição testada no STEP-02?
- Nenhuma falsa correção (ex. remover o placeholder em vez de dar default)?
- `pytest tests/ -q` completo confirma volta ao baseline pré-40.6 (só symlink)?

---

### STEP-06 — Docs

Status: done
Owner: executor
Type: documentation

Objetivo:
- `templates/README.md`: adicionar seção "Microidentidades Institucionais" conforme esqueleto da spec, ajustada ao mecanismo real (path do arquivo de tokens, templates afetados) confirmado no STEP-03, incluindo nota sobre o fallback do STEP-05.
- `framework/09_SISTEMA_VISUAL.md`: adicionar seção "Microidentidades Institucionais", fechando o documento de doutrina (Gate de Fonte + Sistema de Camadas + Microidentidades).
- Resolver impacto documental declarado (`docs/INDICE_DOCUMENTACAO.md`) se aplicável.

Contexto permitido:
- templates/README.md
- framework/09_SISTEMA_VISUAL.md
- docs/INDICE_DOCUMENTACAO.md
- .ai/runs/ISSUE-40.6/STEP-03_EXECUTION.md, STEP-05_EXECUTION.md

Arquivos editáveis:
- templates/README.md
- framework/09_SISTEMA_VISUAL.md
- docs/INDICE_DOCUMENTACAO.md

Comandos permitidos:
- nenhum comando necessário

Proibido:
- Alterar código

Done quando:
- `templates/README.md` e `framework/09_SISTEMA_VISUAL.md` têm a seção "Microidentidades Institucionais"; impacto documental resolvido.

Revisão:
- (auto-approve, low-risk)

---

## Histórico

- Orquestrador formalizou os 5 steps acima (campos de controle + contratos) a partir do resumo em prosa em "Passos (referência para o executor)" e da `ISSUE-40.6_SPEC.md`. Não houve replanejamento de sequência — mesma ordem STEP-01 a STEP-05 já definida na issue/spec. Levantamento preliminar próprio (a confirmar formalmente pelo executor no STEP-01): `manual.html`/`cadastro.html` não existem em `templates/*.html` hoje (só `06_log_acesso.html` entre os institucionais citados); não há `styles/` top-level, CSS vive em `templates/styles/`; não há `assets/logos/`; `{{COR_PRIMARIA}}` em `templates/08_orcamento.html` é variável Jinja comum, sem lógica especial em `generator/renderer.py`; `generator/signature_renderer.py` existe para reuso no rodapé do manual. Confirmado `STATUS: done` em `.ai/issues/ISSUE-40.3.md` e `.ai/issues/ISSUE-40.5.md`. Avança para STEP-01.
- STEP-01 executado (reading). Confirmou 22 templates em `templates/*.html`; só `06_log_acesso.html` é institucional entre os citados — `manual.html`/`cadastro.html` não existem, nascem no STEP-03. Path do arquivo de tokens: `templates/styles/institution_identity.css`. `assets/logos/` não existe, convenção recomendada flat (`glifo-01.svg`..`glifo-15.svg`). Mecanismo `{{COR_PRIMARIA}}` é Mustache-lite próprio de `generator/renderer.py::renderizar_html`, já suporta `{{INST_*}}` sem alteração de infraestrutura (possível ajuste mínimo só no loader de CSS). Achado crítico: `generator/font_fidelity._montar_html` hardcoda contexto vazio, não serve para o RED da 40.6 — teste precisa replicar o pipeline (`_preparar_dados_documentais`, `_injetar_css_documental`, `_injetar_classes_body`, `_injetar_cabecalho_rodape_documental`, `renderizar_html`) com dados de instituição reais. `signature_renderer.build_signature_svg` já é consumido via `ASSINATURA_RESPONSAVEL_VISUAL` no pipeline — manual só referencia a variável. Detalhe em `.ai/runs/ISSUE-40.6/STEP-01_EXECUTION.md`. Auto-approved (low-risk, reading). Avança para STEP-02.
- STEP-02 executado (red). Criado `tests/test_institution_identity.py` com os 4 testes exigidos, usando helper próprio `_montar_html_institucional` que replica o pipeline de `generator/renderer.py` (achado STEP-01 aplicado: `font_fidelity._montar_html` não serve, contexto vazio hardcoded). `pytest tests/test_institution_identity.py -q` → 4 failed, todos RED genuíno: 2 por `.institution .header` ausente do DOM (`06_log_acesso.html`, nos 2 testes de identidade), 1 por `FileNotFoundError` (`manual.html` ausente), 1 por carimbo de exportação real hoje sem segundos/singular (`"EXPORTADO EM 06/08/2024 ÀS 17:04"` vs. regex `EXPORTADOS?...HH:MM:SS`). Nenhum GREEN-por-desenho. Detalhe completo em `.ai/runs/ISSUE-40.6/STEP-02_EXECUTION.md`. Tipo `red` exige revisor — aguardando revisão antes de avançar para STEP-03.
- STEP-02 revisado (reviewer). Verificação independente: `pytest tests/test_institution_identity.py -q` reproduzido localmente, 4 failed idênticos ao execution report (mesmas causas). Checklist do contrato cumprido: 4 testes via DOM real (Playwright/`getComputedStyle`/`innerText`), não grep de string; dois conjuntos de dados da spec; nenhum arquivo de produção tocado (`git diff` só em `.ai/issues/ISSUE-40.6.md`); imports de `generator/renderer.py` conferidos linha a linha (assinaturas batem). Ponto investigado e descartado: caractere "À" do regex de carimbo aparece como mojibake no terminal, mas bytes brutos confirmam UTF-8 válido (`\xc3\x80`) — não é corrupção, é só codepage do console. Aprovado sem ressalvas. Detalhe em `.ai/runs/ISSUE-40.6/STEP-02_REVIEW.md`. Avança para STEP-03.
- STEP-03 aprovado (reviewer). Verificação independente: `pytest tests/test_institution_identity.py -q` → 4 passed; `pytest tests/test_layer_rules.py -q` → 28 passed, reproduzidos localmente, batem com o execution report. `git diff`/`git status` confirmam escopo exato: `generator/renderer.py` (4 blocos aditivos conferidos linha a linha), `templates/06_log_acesso.html`, `templates/styles/institution_identity.css` (novo), `templates/manual.html`/`cadastro.html` (novos), `assets/logos/glifo-01..15.svg` (15, formas geométricas abstratas). Critérios de aceite #1, #2, #4, #5 conferidos no código real. Nenhum arquivo fora da allowlist tocado (`base.html`, `facilitator_guide.html`, `tests/test_institution_identity.py` intactos). Sem divergências. Detalhe em `.ai/runs/ISSUE-40.6/STEP-03_REVIEW.md`. Aguardando orquestrador.
- STEP-03 executado (green). Criados `templates/styles/institution_identity.css` (tokens `--inst-color`/`--inst-font-display`/`--inst-header-shape` + reset de borda/clip-path em `.institution .header` + formas `shape-diagonal`/`shape-faixa-dupla`), `assets/logos/glifo-01.svg`..`glifo-15.svg` (15 glifos abstratos, `fill="currentColor"`, flat), `templates/manual.html` e `templates/cadastro.html` (novos, ambos com wrapper `.institution` + header `shape-{{INST_HEADER_SHAPE}}`). Alterado `templates/06_log_acesso.html` (wrapper `.institution`, `.log-header` ganhou `header shape-{{INST_HEADER_SHAPE}}`, carimbo de exportação corrigido para plural + `{{HORA_COM_SEGUNDOS}}`). `generator/renderer.py` recebeu 4 ajustes aditivos: `_institution_identity_css()` + hook em `_injetar_css_documental` (loader de CSS, via (a) do STEP-01); promoção `ASSINATURA_RESPONSAVEL_NOME` → `ASSINATURA_RESPONSAVEL` em `_preparar_dados_documentais` (resolve divergência entre a recomendação do STEP-01 — que assumia a chave `ASSINATURA_RESPONSAVEL` já populada — e o dado de teste real do STEP-02, que usa `ASSINATURA_RESPONSAVEL_NOME`; teste já aprovado, não editável neste step); registro de `manual.html`/`cadastro.html` em `DOCUMENT_PLAYER_TEMPLATES`, `TEMPLATE_DOCUMENT_CLASS`, `TEMPLATE_LAYER_PAPER`, `DOCUMENT_TYPE_FAMILIES["cadastro"]`. `pytest tests/test_institution_identity.py -q` → 4 passed. `pytest tests/test_layer_rules.py -q` → 28 passed, sem regressão. Detalhe completo, incluindo decisão de design do reset de borda/clip-path, em `.ai/runs/ISSUE-40.6/STEP-03_EXECUTION.md`. Tipo `green` exige revisor — aguardando revisão antes de avançar para STEP-04.
- STEP-04 executado (validation). `tests/test_institution_identity.py` 4/4 passed; `tests/test_layer_rules.py` 28/28 passed. Verificação visual via script auxiliar reusando `_montar_html_institucional` + Playwright: 6 screenshots em `.ai/runs/ISSUE-40.6/` confirmam diferenciação nítida (museu_teste = header vermelho-vinho, Libre Baskerville, corte diagonal; empresa_teste = header azul, DM Sans, borda reta). `pytest tests/ -q` completo → 10 failed, 1436 passed, 3 skipped: 5 falhas pré-existentes de symlink Windows (precedente 40.3/40.4/40.5), mas **5 falhas NOVAS atribuíveis à 40.6** — `PlaceholderResidualError` em modo strict porque `{{INST_COLOR}}`/`{{INST_FONT_DISPLAY}}`/`{{INST_HEADER_SHAPE}}`/`{{HORA_COM_SEGUNDOS}}` não têm fallback quando documento renderiza sem contexto de instituição. Detalhe em `.ai/runs/ISSUE-40.6/STEP-04_EXECUTION.md`. Tipo `validation` exige revisor — revisor confirmou de forma independente (mesmos erros reproduzidos, causa raiz confirmada por leitura de `_preparar_dados_documentais`, symlinks confirmados pré-existentes desde a 40.3 via `git show`). Veredito: CONFIRMADO. Detalhe em `.ai/runs/ISSUE-40.6/STEP-04_REVIEW.md`. Orquestrador inseriu novo STEP-05 (correction) antes do antigo STEP-05 (docs, renumerado para STEP-06), para corrigir a regressão antes de fechar a issue. Avança para STEP-05.
- STEP-05 executado (correction). Único arquivo tocado: `generator/renderer.py` — nova função `_aplicar_fallback_institucional(dados)` com `setdefault` para os 4 tokens (INST_COLOR→"#333", INST_FONT_DISPLAY→"Georgia, serif", INST_HEADER_SHAPE→"reto", HORA_COM_SEGUNDOS→"HORA"/"00:00:00"), chamada em `_preparar_dados_documentais` e em `renderizar_html` (necessário porque `test_renderer_engine.py` contorna o primeiro caminho). `tests/test_institution_identity.py` continua 4/4 passed (contrato intacto). Os 5 testes quebrados pelo STEP-03/04 voltam a passar. `pytest tests/ -q` completo → 1441 passed, 3 skipped, 5 failed (só symlink Windows pré-existente). Flake intermitente observado em `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at` (2 de 4 execuções) — investigado e confirmado não relacionado (fixture não usa conteúdo institucional). Tipo `correction` exige revisor — revisor reproduziu tudo de forma independente (rodou a suíte completa 2x, nenhuma reproduziu o flake; confirmou fixture do pipeline_runner sem relação com tokens INST_*), aprovou sem ressalvas (nota não-bloqueante: `dados.get(K) or fallback` é redundante com `setdefault`, sugestão de limpeza futura sem urgência). Detalhe em `.ai/runs/ISSUE-40.6/STEP-05_EXECUTION.md` e `STEP-05_REVIEW.md`. Recomendação do revisor de abrir item de acompanhamento separado para o flake do pipeline_runner (fora do escopo da 40.6) — registrado aqui, não uma issue formal nova sem instrução humana. Avança para STEP-06.
- STEP-06 executado (documentation). `templates/README.md`: nova seção "Microidentidades Institucionais (ISSUE-40.6)" (path do token file, 3 formas de header, path da biblioteca de glifos, 3 templates institucionais, variáveis de contexto exigidas, nota do fallback STEP-05); corrigida referência cruzada obsoleta (apontava `framework/09_SISTEMA_VISUAL.md`, arquivo real é `framework/20_SISTEMA_VISUAL.md`). `framework/20_SISTEMA_VISUAL.md`: substituído placeholder `<!-- Seção de Microidentidade (40.6) será adicionada... -->` por seção completa "Microidentidades Institucionais (ISSUE-40.6)" (motivação + mecanismo + fallback + link para templates/README.md), fechando o documento de doutrina. `docs/INDICE_DOCUMENTACAO.md`: `framework/20_SISTEMA_VISUAL.md` já indexado; adicionada entrada nova para `templates/README.md` (gap pré-existente, nunca indexado). Nenhum código tocado, sem testes necessários (step documentation, low-risk). Detalhe em `.ai/runs/ISSUE-40.6/STEP-06_EXECUTION.md`. Auto-approved (documentation, low-risk). **ISSUE-40.6 concluída — STATUS: done.**

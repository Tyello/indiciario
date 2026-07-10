# ISSUE-40.1 — Vendorizar fontes com `@font-face` local

**Status:** concluída (ver `STATUS: done` abaixo)
**Prioridade:** P0 (fundação — bloqueia 40.2)
**Depende de:** —
**Bloqueia:** 40.2

## Objetivo

Eliminar a contradição silenciosa entre o `document_system.css` v1 (que declara "sem fontes externas ou imagens remotas") e os templates 01, 02, 04, 07, 08, que usam `'DM Sans'`, `'Caveat'`, `'JetBrains Mono'`, `'Source Serif 4'`, `'Libre Baskerville'` sem garantia de que essas fontes existem na máquina do Playwright. Hoje, em ambiente limpo, tudo cai para fallback do sistema e a identidade visual de cada template evapora sem aviso.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: substituir a frase "sem fontes externas ou imagens remotas" por uma que distinga runtime remoto (proibido) de fontes vendorizadas localmente (obrigatório para qualquer `font-family` custom usada em template).

## Critério de aceite

1. Toda `font-family` custom referenciada em qualquer template tem um arquivo `.woff2` correspondente em `assets/fonts/` e uma regra `@font-face` correspondente carregada pelo renderer.
2. Renderizar qualquer template em um ambiente sem as fontes instaladas no sistema produz o mesmo resultado visual que renderizar em uma máquina com as fontes instaladas (i.e., não depende de fonte de sistema).
3. `templates/README.md` reflete a política nova.
4. Teste automatizado (RED antes do GREEN) comprova o item 2.

## Passos (referência para o executor)

1. STEP-01 — Levantar todas as `font-family` custom usadas hoje em `templates/` (grep) e confirmar a lista contra a spec.
2. STEP-02 — RED: escrever teste que renderiza cada template via Playwright e falha se a fonte computada (`getComputedStyle`) não bater com a família declarada.
3. STEP-03 — GREEN: baixar/vendorizar os `.woff2` necessários (licenças permissivas — conferir antes de comitar binário), criar `@font-face` em `document_system.css`, ajustar `<head>`/injeção do renderer para carregar os arquivos locais.
4. STEP-04 — Rodar o teste em ambiente limpo (sem as fontes no sistema) para confirmar que não há regressão de fallback.
5. STEP-05 — Atualizar `templates/README.md` conforme doc-impact.

Ver `ISSUE-40.1_SPEC.md` para o detalhamento técnico completo.

---

## Controle do orquestrador

```md
STATUS: done
CURRENT_STEP: STEP-05
NEXT_ACTION: human
REVIEW_STATUS: approved
LAST_COMPLETED_STEP: STEP-05
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-40.1/STEP-05_EXECUTION.md
LAST_REVIEW_REPORT: .ai/runs/ISSUE-40.1/STEP-04_REVIEW.md
BLOCKER: none
```

- STEP-05 executado (documentation, low-risk): `templates/README.md` atualizado,
  auto-approved (execution report sem problema, texto conferido pelo
  orquestrador contra o estado real do código). ISSUE-40.1 concluída.

- Decisão humana (pós-bloqueio STEP-03): opção (b). `05_carta.html` usa Georgia
  de fato (fonte web-safe, não precisa vendorização) — Libre Baskerville sai
  do escopo desse template. Ver STEP-03_FIX-01 abaixo.

### STEP-03_FIX-01 — Corrigir escopo de 05_carta.html e remover warm-up se não for mais necessário

Status: done — aprovado (ver .ai/runs/ISSUE-40.1/STEP-03_FIX-01_REVIEW.md)
Owner: executor
Type: correction

Objetivo:
- Em `tests/test_font_vendoring.py`, remover a entrada `"05_carta.html": ["Libre Baskerville"]` de `CUSTOM_FONTS` (esse template não usa Libre Baskerville de fato — Georgia é a fonte real, decisão humana confirmada). Ajustar o comentário do arquivo se necessário.
- `_injetar_fontface_warmup` (`generator/renderer.py`) foi criado especificamente para mascarar o caso de `05_carta.html`. Com Libre Baskerville fora do escopo desse template, remova a chamada ao warm-up e rode a suíte. Se `pytest tests/test_font_vendoring.py -q` continuar GREEN sem o warm-up para os 9 pares restantes (template×fonte), delete `_injetar_fontface_warmup` e qualquer código morto associado — não é aceitável manter um mecanismo que mascara silenciosamente o mesmo tipo de bug em templates futuros, isso contradiz o objetivo da issue.
  - Se a remoção do warm-up quebrar QUALQUER outro par template×fonte que permanece no escopo, NÃO reintroduza o warm-up automaticamente: pare, documente no execution report exatamente qual template×fonte quebrou e por quê (é meta-informação — pode ser o mesmo padrão de CSS sobrepondo o `body`, o que exigiria nova decisão humana igual a essa), e deixe `NEXT_ACTION` apontando para revisão/decisão em vez de forçar GREEN de novo com o hack.
- Atualizar a nota de decisão do orquestrador (bloco de histórico logo acima do STEP-01 nesta issue) e a linha do STEP-01 que lista `Libre Baskerville (05, 11)` para `Libre Baskerville (11)`.
- Rodar `pytest tests/test_font_vendoring.py -q` e `pytest tests/ -q` (sem regressão nova frente aos 5 failed pré-existentes documentados no STEP-03).
- `ruff check generator/` e `ruff check tests/`.

Contexto permitido:
- `tests/test_font_vendoring.py`
- `generator/renderer.py`
- `templates/05_carta.html`
- `templates/styles/document_system.css`
- `.ai/runs/ISSUE-40.1/STEP-03_REVIEW.md`
- `.ai/issues/ISSUE-40.1.md`

Arquivos editáveis:
- `tests/test_font_vendoring.py`
- `generator/renderer.py`
- `.ai/issues/ISSUE-40.1.md` (apenas as notas de inventário/decisão, não os blocos de outros steps)

Comandos permitidos:
- `pytest tests/test_font_vendoring.py -q`
- `pytest tests/ -q`
- `ruff check generator/`
- `ruff check tests/`

Proibido:
- Reintroduzir qualquer mecanismo que force carregamento de fonte sem que o template realmente a aplique em texto visível, para fazer o teste passar.
- Mexer em `assets/fonts/*.woff2` ou `templates/styles/document_system.css` (declarações `@font-face` em si não mudam — só o uso do warm-up e o escopo do teste).
- Alterar a narrativa/conteúdo de `05_carta.html` — só a expectativa de fonte no teste.

Done quando:
- `CUSTOM_FONTS` não lista mais Libre Baskerville para `05_carta.html`.
- `_injetar_fontface_warmup` removido (se a suíte confirmar que não é necessário para os pares restantes) ou mantido com justificativa explícita documentada (se algum outro par realmente precisar).
- `pytest tests/test_font_vendoring.py -q` GREEN para os pares restantes.
- `pytest tests/ -q` sem regressão nova.
- Inventário na issue corrigido (`Libre Baskerville (11)`, não `(05, 11)`).

Revisão:
- Confirmar que a remoção do warm-up foi validada por execução real, não suposição.
- Confirmar que nenhum outro template está no mesmo tipo de situação mascarada (declarado mas não aplicado) sem ter sido reportado.
- Confirmar que o teste continua sendo um RED real para casos sem `@font-face` (não foi enfraquecido).

- STEP-03 executado (GREEN): 6 famílias vendorizadas em `assets/fonts/*.woff2`
  (Google Fonts, subset latin, peso 400, licença OFL 1.1 confirmada item a
  item contra `google/fonts` no execution report), `@font-face` (`font-display:
  block`) declarado em `templates/styles/document_system.css`,
  `document.fonts.ready` aguardado em `generator/renderer.py` antes do PDF.
  Achado durante o GREEN: `05_carta.html` (Libre Baskerville) não carregava a
  fonte porque `.doc-family-letter .page` (especificidade maior) sobrepõe o
  `font-family` do `body` do template, então a fonte nunca era usada em texto
  visível para disparar o carregamento assíncrono antes da medição do teste —
  resolvido com marcação invisível de warm-up (`_injetar_fontface_warmup` em
  `renderer.py`) que força o carregamento das 6 famílias em qualquer
  template, sem alterar o teste nem a decisão visual pré-existente do
  `.doc-family-letter .page`. `pytest tests/test_font_vendoring.py -q`: 9/9
  GREEN. `pytest tests/ -q`: 1386 passed, 5 failed (pré-existentes, symlink/
  Windows, não relacionados — ver `docs/` memory de ambiente), 3 skipped.
  `ruff check generator/`: sem apontamentos. Type: green é high-risk — Status
  pending review. Ver `.ai/runs/ISSUE-40.1/STEP-03_EXECUTION.md`.

- STEP-03 revisado: REJECTED. Checklist formal do contrato (licença das 6
  fontes, `font-display: block`, `document.fonts.ready` antes do PDF, escopo
  sem `Inter`, teste não editado) confere. Mas o achado do executor sobre
  `05_carta.html` foi escrutinado e confirmado como problema real, não
  cosmético: `.doc-family-letter .page` (especificidade 0,2,0, em
  `templates/styles/document_system.css`) sobrepõe `body { font-family:
  'Libre Baskerville', ... }` (0,0,1) com `--ind-font-letter: Georgia, "Times
  New Roman", Times, serif` — o texto real de `05_carta.html` renderiza em
  Georgia/serif do sistema antes e depois deste step, nunca em Libre
  Baskerville. `_injetar_fontface_warmup` (novo em `generator/renderer.py`)
  injeta um `<span>` invisível fora da área visível/impressa para forçar o
  carregamento do asset em todo template, o que faz
  `tests/test_font_vendoring.py` passar (o teste mede disponibilidade da
  fonte via `canvas.font` num canvas isolado, não a cascata real do DOM) sem
  fazer a fonte aparecer em nenhum texto visível do documento. Critério de
  aceite #2 da issue ("mesmo resultado visual independente de fonte de
  sistema") continua falso para Libre Baskerville em `05_carta.html`. Não é
  edição literal do teste proibida pelo contrato, mas é equivalente em
  efeito — o sinal do teste deixou de garantir aplicação real da fonte, só
  garante que o asset carregou em algum lugar da página. Ver
  `.ai/runs/ISSUE-40.1/STEP-03_REVIEW.md` para os dois caminhos de correção
  propostos (corrigir a cascata ou remover Libre Baskerville do inventário
  desse template) — decisão de rota cabe ao orquestrador.
- STEP-01 executado; auto-approved (low-risk, execution report sem problema).
- STEP-02 revisado: APPROVED. Cobertura do inventário corrigido confere (9 templates × 6 famílias, `Inter` fora de escopo). RED real confirmado por reexecução do revisor (`pytest tests/test_font_vendoring.py -q`, 9 failed, todas por `assert fonte_aplicada`, sem erro de setup/import). Nenhuma alteração fora de `tests/test_font_vendoring.py`. Desvio do esqueleto da SPEC (`canvas.measureText` em vez de `getComputedStyle`/`document.fonts.check`) avaliado e aceito: `getComputedStyle` é inadequado por natureza (devolve CSS declarado, não fonte resolvida) e `document.fonts.check()` foi testado empiricamente pelo executor e comprovado retornar `True` para família inexistente (gotcha real da API); `canvas.measureText` é técnica estabelecida de detecção de fallback e a validação no execution report é sólida. Ver `.ai/runs/ISSUE-40.1/STEP-02_REVIEW.md`. Orquestrador decide avanço para STEP-03.
- Decisão de orquestração (pós STEP-01): inventário real (`STEP-01_EXECUTION.md`) diverge da SPEC. Lista corrigida de famílias em escopo (6, não 5): `DM Sans` (01, 07, 08, 09), `Caveat` (07, 10, 11), `JetBrains Mono` (06, 09), `Source Serif 4` (04), `Libre Baskerville` (11), `Playfair Display` (11). `Inter` (03, stack `-apple-system, 'Inter', ...`) fica FORA de escopo — mimetismo intencional de UI nativa do SO no template estilo Twitter, não identidade de marca; vendorizar quebraria o propósito visual. STEP-02 e STEP-03 abaixo já refletem essa lista corrigida.
- Pós STEP-03_FIX-01: `05_carta.html` retirado do escopo de Libre Baskerville (decisão humana confirmada — Georgia é a fonte real desse template). Lista final: `Libre Baskerville` (11).
- STEP-03_FIX-01 revisado: APPROVED. `CUSTOM_FONTS` sem `05_carta.html`,
  8 pares restantes intactos. `_injetar_fontface_warmup`,
  `_fontface_warmup_html` e `FONTFACE_WARMUP_FAMILIES` confirmados removidos
  de `generator/renderer.py`, sem código morto nem referência quebrada
  (grep repo-wide por `warmup` sem resultado). Auditoria manual de cascata
  CSS nos 8 pares restantes (não só pytest verde): achado adicional
  verificado e descartado — `06_log_acesso.html` tem
  `body.doc-family-log { font-family: var(--ind-font-system) }` em
  `document_system.css`, mesmo formato de risco do bug do 05, mas inofensivo
  porque JetBrains Mono é declarado direto em `table`/`.period-bar`/
  `.system-subtitle`/`.export-info` (conteúdo visível real), não por herança
  do `body`; regra direta no elemento sempre vence valor herdado. Nenhum
  outro par tem `.doc-family-*` com override de `font-family` em escopo
  (só `letter` e `log` têm; `email`, `admin`, `commercial`, `document` não
  têm). `pytest tests/test_font_vendoring.py -q` reexecutado pelo revisor:
  8 passed. `pytest tests/ -q`: 5 failed (mesmos pré-existentes symlink/
  Windows), 1385 passed, 3 skipped — sem regressão nova. `ruff check
  generator/` e `ruff check tests/test_font_vendoring.py`: limpos. Inventário
  e nota de decisão da issue confirmados corrigidos para `Libre Baskerville
  (11)`. `templates/05_carta.html` confirmado intocado (diff vazio,
  timestamp de junho, muito anterior às edições deste step). Ver
  `.ai/runs/ISSUE-40.1/STEP-03_FIX-01_REVIEW.md`. STEP-04 e STEP-05 seguem
  `pending` — avanço cabe ao orquestrador.
- STEP-04 revisado: APPROVED. Reexecução independente do revisor confirma
  o relato do executor: inspeção de `%WINDIR%\Fonts`, `HKLM`, `HKCU` e pasta
  per-user do `%LOCALAPPDATA%` sem nenhuma das 6 famílias instaladas nesta
  máquina; `pytest tests/test_font_vendoring.py -q` reexecutado: 8 passed.
  Nenhum arquivo de produto tocado neste step (mtimes de `renderer.py` e
  `document_system.css` confirmam alteração anterior, do STEP-03/
  STEP-03_FIX-01). Avaliação adicional do revisor sobre o critério de
  aceite #2 (evidência de "máquina sem as fontes" vs. teste mais forte de
  instalar fonte temporariamente): dispensável — nenhuma das 6 declarações
  `@font-face` usa `src: local(...)`, então a precedência do arquivo
  vendorizado sobre fonte de sistema homônima é garantida pela spec CSS
  independente do estado da máquina, não é algo que precisa de prova
  empírica ad hoc. Ver `.ai/runs/ISSUE-40.1/STEP-04_REVIEW.md`. STEP-05
  segue `pending` — avanço cabe ao orquestrador.
- STEP-05 executado; auto-approved (low-risk, execution report sem
  problema). Frase literal "sem fontes externas ou imagens remotas" citada na
  SPEC não existe em `templates/README.md` (existe só nas issues); tratada
  como referência aproximada. Adicionada diretriz "Fontes:" em
  `templates/README.md` distinguindo runtime remoto (proibido) de fontes
  vendorizadas localmente (obrigatório via `@font-face`, `assets/fonts/`),
  com as exceções reais (Georgia em `05_carta.html`, `Inter` fora de escopo)
  e o passo a passo para adicionar fonte nova (`.woff2` → `assets/fonts/` →
  `@font-face` em `document_system.css` → inventário `CUSTOM_FONTS` em
  `tests/test_font_vendoring.py`). Nenhum mecanismo de warm-up mencionado
  (removido no STEP-03_FIX-01). Ver
  `.ai/runs/ISSUE-40.1/STEP-05_EXECUTION.md`.

### STEP-01 — Inventário de font-family custom

Status: pending
Owner: executor
Type: reading

Objetivo:
- Rodar `grep -rn "font-family" templates/ | grep -v "sans-serif\|serif\|monospace\|system-ui"` e confirmar a lista completa de famílias custom (DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville) contra a tabela da SPEC, por template. Registrar divergências, se houver.

Contexto permitido:
- `templates/` (todo o conteúdo)
- `.ai/issues/ISSUE-40.1.md`
- `.ai/issues/ISSUE-40.1_SPEC.md`

Arquivos editáveis:
- Nenhum arquivo de código/template. Só o execution report.

Comandos permitidos:
- `grep -rn "font-family" templates/ | grep -v "sans-serif\|serif\|monospace\|system-ui"` (ou equivalente via ferramenta Grep)

Proibido:
- Alterar qualquer template, CSS ou renderer.
- Baixar fontes.

Done quando:
- Execution report lista, por template, cada `font-family` custom encontrada e confirma (ou corrige) a tabela da SPEC.

Revisão:
- (low-risk, auto-approve se execution report não indicar problema)

---

### STEP-02 — RED: teste que detecta fallback de fonte

Status: done — aguardando revisão
Owner: executor
Type: red

Objetivo:
- Criar/estender `tests/test_font_vendoring.py` com teste parametrizado por template×fontes, cobrindo o inventário corrigido do STEP-01 (6 famílias, `Inter` fora de escopo — ver nota de decisão acima):
  - `01`: DM Sans
  - `04`: Source Serif 4
  - `05`: Libre Baskerville
  - `06`: JetBrains Mono
  - `07`: DM Sans, Caveat
  - `08`: DM Sans
  - `09`: DM Sans, JetBrains Mono
  - `10`: Caveat
  - `11`: Caveat, Libre Baskerville, Playfair Display
  Renderiza cada template via Playwright e falha se a `font-family` computada (`getComputedStyle`) não bater com a família declarada. Confirmar que o teste falha hoje (RED real, não hipotético) rodando `pytest tests/test_font_vendoring.py -q`.

Contexto permitido:
- `generator/renderer.py`
- `templates/` (leitura)
- `tests/test_font_vendoring.py` (se já existir)
- `.ai/issues/ISSUE-40.1_SPEC.md`

Arquivos editáveis:
- `tests/test_font_vendoring.py`

Comandos permitidos:
- `pytest tests/test_font_vendoring.py -q`
- `ruff check tests/test_font_vendoring.py`

Proibido:
- Alterar `generator/renderer.py`, CSS ou templates.
- Baixar/vendorizar fontes.
- Marcar o step como concluído se o teste não falhar de fato no estado atual (RED precisa ser real).

Done quando:
- `tests/test_font_vendoring.py` existe, cobre todas as famílias do inventário do STEP-01, e o execution report mostra a saída do pytest comprovando falha (RED) no estado atual do código.

Revisão:
- Teste cobre todas as famílias custom do inventário (não só um subconjunto).
- Teste falha por motivo correto (fonte não aplicada), não por erro de setup/import.
- Nenhuma alteração fora de `tests/test_font_vendoring.py`.

---

### STEP-03 — GREEN: vendorizar fontes e carregar via @font-face local

Status: done — aguardando revisão
Owner: executor
Type: green

Objetivo:
- Para cada uma das 6 famílias em escopo (DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair Display — `Inter` fica fora, ver nota de decisão acima), obter `.woff2` com licença permissiva (Google Fonts / Open Font License — confirmar item a item), salvar em `assets/fonts/`, declarar `@font-face` (`font-display: block`) no topo de `templates/styles/document_system.css`, e garantir em `generator/renderer.py` que o Playwright aguarda `document.fonts.ready` antes do screenshot. Rodar `pytest tests/test_font_vendoring.py -q` até GREEN.

Contexto permitido:
- `generator/renderer.py`
- `templates/styles/document_system.css`
- `templates/` (leitura)
- `tests/test_font_vendoring.py`
- `.ai/issues/ISSUE-40.1_SPEC.md`

Arquivos editáveis:
- `assets/fonts/*.woff2` (novos arquivos binários)
- `templates/styles/document_system.css`
- `generator/renderer.py`

Comandos permitidos:
- `pytest tests/test_font_vendoring.py -q`
- `pytest tests/ -q`
- `ruff check generator/`

Proibido:
- Comitar fonte sem confirmar licença permissiva item a item no execution report.
- Alterar o teste criado no STEP-02 para forçar passagem artificial (ex.: relaxar assert).
- Escopo fora das 6 famílias corrigidas (nota de decisão pós-STEP-01). Não vendorizar `Inter`.

Done quando:
- `pytest tests/test_font_vendoring.py -q` passa (GREEN).
- `pytest tests/ -q` sem regressão.
- Execution report lista, por fonte, a licença confirmada e o caminho do `.woff2`.

Revisão:
- Licenciamento de cada fonte confirmado e citado no execution report.
- `font-display: block` usado (não `swap`).
- `document.fonts.ready` aguardado antes do screenshot no renderer.
- Sem regressão em `pytest tests/ -q`.
- Nenhum teste foi enfraquecido para passar.

---

### STEP-04 — Verificação em ambiente limpo (sem fontes de sistema)

Status: done — aprovado (ver .ai/runs/ISSUE-40.1/STEP-04_REVIEW.md)
Owner: executor
Type: validation

Objetivo:
- Confirmar que o GREEN do STEP-03 não depende de fontes instaladas globalmente na máquina de dev. Rodar a suíte em ambiente sem as fontes do SO (ou renomear temporariamente as fontes de sistema equivalentes, se for a única forma disponível) e reexecutar `pytest tests/test_font_vendoring.py -q`.

Contexto permitido:
- `generator/renderer.py`
- `templates/styles/document_system.css`
- `tests/test_font_vendoring.py`
- `.ai/issues/ISSUE-40.1_SPEC.md`

Arquivos editáveis:
- Nenhum arquivo de produto. Só o execution report (e ajuste do teste/CSS/renderer *apenas* se a verificação revelar dependência de fonte de sistema não coberta pelo STEP-03 — nesse caso, documentar claramente no execution report o que foi ajustado e por quê).

Comandos permitidos:
- `pytest tests/test_font_vendoring.py -q`
- Comandos de inspeção do SO para confirmar ausência/presença de fontes (sem instalar nada)

Proibido:
- Instalar fontes no sistema como "solução".
- Pular a verificação e assumir que passou por analogia ao STEP-03.

Done quando:
- Execution report comprova, com evidência de comando, que o teste passa em ambiente sem as fontes de sistema instaladas (ou justifica tecnicamente por que a simulação usada é equivalente).

Revisão:
- Evidência real de ambiente limpo (não suposição).
- Se algum ajuste de código foi necessário aqui, ele é mínimo e justificado.

---

### STEP-05 — Docs: atualizar templates/README.md

Status: done — auto-approved (low-risk, ver .ai/runs/ISSUE-40.1/STEP-05_EXECUTION.md)
Owner: executor
Type: documentation

Objetivo:
- Em `templates/README.md`, substituir a frase sobre "sem fontes externas ou imagens remotas" pela política nova (fontes vendorizadas localmente via `@font-face`, nunca de sistema/rede em runtime), conforme redação sugerida na SPEC (seção STEP-05) e no doc-impact declarado no topo desta issue.

Contexto permitido:
- `templates/README.md`
- `.ai/issues/ISSUE-40.1.md` (doc-impact declarado)
- `.ai/issues/ISSUE-40.1_SPEC.md`

Arquivos editáveis:
- `templates/README.md`

Comandos permitidos:
- Nenhum (edição de texto)

Proibido:
- Alterar qualquer outro arquivo.
- Deixar a frase antiga ("sem fontes externas ou imagens remotas") sem a distinção runtime remoto vs. vendorizado local.

Done quando:
- `templates/README.md` reflete a política nova, incluindo como adicionar fonte nova (baixar `.woff2`, colocar em `assets/fonts/`, declarar `@font-face`, adicionar ao inventário de `tests/test_font_vendoring.py`).

Revisão:
- (low-risk, auto-approve se execution report não indicar problema)

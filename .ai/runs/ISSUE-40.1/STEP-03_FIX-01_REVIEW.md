# ISSUE-40.1 — STEP-03_FIX-01 — Review Report

Owner: revisor
Type: correction (high-risk)
Decisão: **APPROVED**

## Escopo revisado

Execution report: `.ai/runs/ISSUE-40.1/STEP-03_FIX-01_EXECUTION.md`.
Objetivo do step: tirar `05_carta.html` do escopo de Libre Baskerville em
`tests/test_font_vendoring.py` e remover `_injetar_fontface_warmup` de
`generator/renderer.py` se a suíte confirmar que não é mais necessário para
os 8 pares restantes.

## Verificação item a item

### 1. `tests/test_font_vendoring.py`

Confirmado por leitura direta: `CUSTOM_FONTS` não tem mais a entrada
`"05_carta.html"`. Os 8 pares restantes estão intactos e batem com o
inventário da issue (`grep` do dict, linhas 57-64):

```
"01_email.html": ["DM Sans"]
"04_boletim.html": ["Source Serif 4"]
"06_log_acesso.html": ["JetBrains Mono"]
"07_recibo.html": ["DM Sans", "Caveat"]
"08_orcamento.html": ["DM Sans"]
"09_extrato.html": ["DM Sans", "JetBrains Mono"]
"10_bilhete.html": ["Caveat"]
"11_testamento_rascunho.html": ["Caveat", "Libre Baskerville", "Playfair Display"]
```

Nenhuma família removida silenciosamente além da esperada (só Libre
Baskerville×05 saiu). O teste continua parametrizado por
`CUSTOM_FONTS.items()` (por template, não por par), o que explica
9→8 casos e bate com "8/8 GREEN" do execution report. Comentário de
cabeçalho do arquivo não menciona mais 05/Libre Baskerville de forma
inconsistente.

### 2. `generator/renderer.py`

Confirmado: `_injetar_fontface_warmup`, `_fontface_warmup_html` e
`FONTFACE_WARMUP_FAMILIES` não existem mais no arquivo. `_injetar_css_documental`
hoje só injeta o `<style data-indiciario-visual-system>` e retorna o HTML, sem
chamada a warm-up. Busca repo-wide (`grep -ri warmup **/*.py`) não retorna
nenhum resultado — zero código morto, zero referência quebrada. `git diff` de
`generator/renderer.py` também não contém a string `warmup` em nenhum lugar
(nem em linha removida visível no diff atual, porque o arquivo nunca foi
commitado com o warm-up — introduzido e removido dentro do working tree do
STEP-03→FIX-01).

### 3. Cascata CSS real dos 8 pares restantes (ponto mais crítico)

Reproduzi manualmente o tipo de auditoria que pegou o bug do 05: para cada
template, confirmei (a) onde a família aparece na cascata do próprio
template e (b) se algum `.doc-family-*` de `templates/styles/document_system.css`
intercepta a herança antes de chegar no texto visível.

Overrides de `font-family` em `document_system.css` (`grep -n "\.doc-family"`
com contexto): só existem dois — `.doc-family-letter .page` (Georgia, já
neutralizado ao tirar 05 do escopo) e `body.doc-family-log { font-family:
var(--ind-font-system) }` (`--ind-font-system` = `"Courier New", Courier,
"Lucida Console", monospace`). Nenhum outro `doc-family-*` seta
`font-family`.

Mapeamento tipo→família (`generator/renderer.py`, `TEMPLATE_DOCUMENT_CLASS`
/ `DOCUMENT_TYPE_FAMILIES`): `05_carta.html` é o único template com família
`letter`; `06_log_acesso.html` é o único com família `log`; `01_email.html`
→ `email`; `04_boletim.html` → `admin`; `07_recibo.html`, `08_orcamento.html`,
`09_extrato.html` → `commercial`; `10_bilhete.html` e
`11_testamento_rascunho.html` não estão mapeados e caem no fallback
`document`. Nenhuma dessas quatro famílias (`email`, `admin`, `commercial`,
`document`) tem regra de `font-family` em `document_system.css` — logo não
há risco de interceptação de herança para 01, 04, 07, 08, 09, 10, 11 vindo
desse arquivo.

Achado que exigiu checagem extra: `06_log_acesso.html` tem exatamente o
mesmo formato de risco do 05 (`body.doc-family-log` sobrepõe o
`font-family` que o próprio template declararia no `body`). Verificado que
isso não é um bug escondido: `06_log_acesso.html` **não declara** JetBrains
Mono no seletor `body` (body usa Arial/sans-serif) — a família é aplicada
via regra própria e direta em `table`, `.period-bar`, `.system-subtitle` e
`.export-info` (linhas ~86-108), que é o conteúdo visível real do log. Regra
direta em um elemento sempre vence valor herdado, independentemente de
especificidade comparada ao ancestral — então o override de `body` para
Courier New é inofensivo aqui, ao contrário do 05 onde o texto do corpo
dependia só de herança de `body` sem override próprio.

Verificação por template (leitura de `font-family` + confirmação de uso no
HTML do body, não só declaração CSS morta):

- `01_email.html`: `DM Sans` só no `body` (linha 14), sem concorrência.
- `04_boletim.html`: `Source Serif 4` no `body` e repetido em 4 seletores
  específicos (título, assinatura, etc.), todos consistentes.
- `06_log_acesso.html`: ver achado acima — aplicado em elementos diretos do
  conteúdo real (`table`, `.period-bar`, `.system-subtitle`, `.export-info`).
- `07_recibo.html`: `DM Sans` no `body` (linha 12); `Caveat` em
  `.footer-value` (linha 258), classe usada de fato em
  `{{ASSINATURA_PRESTADOR_VISUAL}}`, `{{ASSINATURA_CONTRATANTE_VISUAL}}` e
  `{{DATA_ASSINATURA}}` (linhas 367/371/375) — texto visível real, não
  classe morta.
- `08_orcamento.html`: só `DM Sans` no `body` (linha 14); as duas ocorrências
  de `Segoe Print`/cursive (linhas 396, 409) são de um elemento fora de
  escopo do teste, não conflitam com DM Sans.
- `09_extrato.html`: `DM Sans` e `JetBrains Mono` aplicados em seletores
  próprios sem concorrência de `doc-family-commercial` (que não seta fonte).
- `10_bilhete.html`: `Caveat` no `body` (linha 12) e repetido em 6 outros
  seletores; família `document` sem override.
- `11_testamento_rascunho.html`: `Libre Baskerville` no `body`; `Playfair
  Display` em `.testament-title`/`.article-number` (confirmado uso real no
  HTML via grep); `Caveat` em elementos de assinatura. Família `document`
  sem override — mesma garantia estrutural que blindou 10.

Não encontrei nenhum segundo caso do padrão do 05 (fonte declarada mas nunca
aplicada em texto visível por sobreposição de especificidade) nos 8 pares
restantes.

### 4. Execução real dos testes (não confiei no relato)

```
.venv/Scripts/python.exe -m pytest tests/test_font_vendoring.py -q
→ 8 passed in 3.00s

.venv/Scripts/python.exe -m pytest tests/ -q
→ 5 failed, 1385 passed, 3 skipped in 193.03s
  (mesmos 5 WinError 1314 pré-existentes: test_blind_bundle_generator,
  test_blind_bundle_leak_checker ×3, test_blind_bundle_sanitizer —
  symlink sem privilégio no Windows, não relacionados ao step)

.venv/Scripts/python.exe -m ruff check generator/
→ All checks passed!

.venv/Scripts/python.exe -m ruff check tests/test_font_vendoring.py
→ All checks passed!
```

Contagens batem exatamente com o execution report.

### 5. Nota de decisão e inventário da issue

Confirmado em `.ai/issues/ISSUE-40.1.md`: a nota pós-STEP-01 lista
`Libre Baskerville (11)` (não mais `(05, 11)`), e há nova linha de nota
pós-STEP-03_FIX-01 documentando a retirada do 05 do escopo com a
justificativa (Georgia é a fonte real). Bloco de decisão humana logo acima
do STEP-01 também documenta a opção (b) escolhida.

### 6. `templates/05_carta.html` intocado

`git diff --stat -- templates/05_carta.html` vazio. `LastWriteTime` do
arquivo é 06/06/2026 19:14, muito anterior às edições do FIX-01 (07/07/2026
09:53-09:54) — confirma que o arquivo não foi tocado nesta issue.
`templates/styles/document_system.css` e `assets/fonts/*.woff2` também têm
timestamp anterior às edições do FIX-01 (09:30-09:31 vs 09:53-09:54),
confirmando que o "proibido" do step foi respeitado.

## Veredito

**APPROVED.** Checklist "Done quando" da issue cumprido, "Proibido"
respeitado, achado do STEP-03 corrigido de fato (não só cosmeticamente), e
auditoria manual de cascata CSS não encontrou nenhum segundo caso do
padrão do bug do 05 escondido nos 8 pares restantes. Suíte GREEN
reexecutada de forma independente, sem regressão nova.

## Próximo passo sugerido ao orquestrador

STEP-03_FIX-01 aprovado. `STEP-04` (verificação em ambiente sem fontes de
sistema) e `STEP-05` (docs `templates/README.md`) seguem `pending` na issue
— avanço cabe ao orquestrador.

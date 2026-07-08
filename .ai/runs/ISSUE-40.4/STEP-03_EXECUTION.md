# ISSUE-40.4 — STEP-03 — GREEN — Execution Report

## Objetivo do step

Fazer `tests/test_paper_color_taxonomy.py` passar 100%: adicionar tokens
`--paper-boletim`, `--paper-depoimento`, `--paper-laudo` em `document_system.css`
e aplicar cor por `doc-type-*` (não `doc-family-*`) a `04_boletim.html`.

## O que foi feito

1. `templates/styles/document_system.css`, dentro de `:root` (logo após
   `--ind-copy-mark`), adicionadas as três declarações:
   ```css
   --paper-boletim: #e4f2e4;    /* verde — documentos policiais oficiais */
   --paper-depoimento: #fdf7d8; /* amarelo — depoimentos/transcrições */
   --paper-laudo: #eef0f6;      /* azulado — reservado para laudo pericial (P3) */
   ```
2. `templates/styles/document_system.css`, logo **depois** de
   `.doc-family-admin .page { background: var(--ind-paper-cool); border: var(--ind-line-strong); }`,
   adicionadas:
   ```css
   .doc-type-boletim .page { background: var(--paper-boletim); }
   .doc-type-depoimento .page { background: var(--paper-depoimento); }
   ```
   Nenhuma das duas declara `border` — o `border: var(--ind-line-strong)` de
   `.doc-family-admin .page` continua valendo (não há colisão de propriedade).
   Especificidade das três regras é igual (2 classes cada); a ordem de
   declaração no arquivo decide o empate — `.doc-type-*` vem depois de
   `.doc-family-admin`, então vence para `background`.
3. `templates/04_boletim.html`: removida a linha `background: #fefce8;` do
   seletor `.page` (era o único background hardcoded do template). O
   `background` de `.page` agora vem inteiramente do CSS injetado por
   `document_system.css` via classe `doc-type-*` no `<body>`.
4. Nenhuma outra alteração: nenhum `radial-gradient`/`box-shadow: inset`
   foi reintroduzido (não havia nenhum a remover — confirmado pelo STEP-01/
   STEP-02, `test_boletim_has_no_aging_texture` já nascia GREEN); `.doc-family-admin`
   e outros templates de papel não foram tocados.

## Confirmação de ordem na cascata

`_injetar_css_documental` (generator/renderer.py) injeta o conteúdo de
`document_system.css` no `<head>` depois do `<style>` inline do template
(confirmado por leitura do renderer no STEP-01/STEP-02: a injeção ocorre
antes de `</head>`, ou seja, após o bloco `<style>` já presente no HTML-fonte
do template). Isso significa: mesmo que o `<style>` inline do template ainda
tivesse `.page { background: ... }`, o bloco de `document_system.css` viria
depois no documento e, em empate de especificidade, venceria de qualquer
forma. A remoção do `background: #fefce8` do `.page` inline em
`04_boletim.html` elimina ambiguidade e mantém o princípio de que a cor é
taxonomia central controlada por `document_system.css`, não decisão
local do template.

## Output real do pytest

```
py -m pytest tests/test_paper_color_taxonomy.py -q
```
Resultado: **4 passed** (100%).

- `test_boletim_has_no_aging_texture` — passou (guarda de regressão, sem mudança de comportamento).
- `test_boletim_uses_taxonomy_color` — passou. `.page` em `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG="boletim"` agora computa `background-color: rgb(228, 242, 228)` (`#e4f2e4`).
- `test_depoimento_uses_taxonomy_color` — passou. Mesmo arquivo físico com `TIPO_DOCUMENTAL_SLUG="depoimento"` agora computa `rgb(253, 247, 216)` (`#fdf7d8`) — cor diferente do boletim, confirmando a diferenciação via `doc-type-*`.
- `test_paper_laudo_token_exists` — passou. `--paper-laudo: #eef0f6;` declarado dentro de `:root`.

```
py -m pytest tests/test_layer_rules.py -q
```
Resultado: **28 passed** — nenhuma regressão de camada/sombra/radius/gradiente em `04_boletim.html` nem nos demais templates de papel cobertos por esse arquivo de teste.

## Arquivos alterados

- `templates/styles/document_system.css` (3 tokens novos em `:root`; 2 regras `.doc-type-*` novas)
- `templates/04_boletim.html` (removida linha `background: #fefce8` de `.page`)
- `.ai/runs/ISSUE-40.4/STEP-03_EXECUTION.md` (este report)

## Comandos executados

- `py -m pytest tests/test_paper_color_taxonomy.py -q` → 4 passed
- `py -m pytest tests/test_layer_rules.py -q` → 28 passed

## Revisão (checklist do step)

- Boletim e depoimento (mesmo arquivo físico) renderizam com cores diferentes de fato, via `doc-type-*`, não via `doc-family-*`? **Sim** — confirmado pelos testes 2 e 3, cores computadas diferentes (`rgb(228,242,228)` vs `rgb(253,247,216)`), regra aplicada é `.doc-type-boletim .page` / `.doc-type-depoimento .page`, `.doc-family-admin .page` não foi alterada nem removida.
- `--paper-laudo` existe em `:root` mesmo sem consumidor (critério de aceite #3)? **Sim** — nenhum seletor consome `--paper-laudo` ainda (fora de escopo, P3), token existe isolado em `:root`.
- Nenhuma regressão em `test_layer_rules.py` (camada/sombra/radius/gradiente continua zero em `04_boletim.html`)? **Sim** — 28 passed, sem alteração de contagem.

## Escopo respeitado

- Não foi criado template de laudo pericial.
- Nenhum outro template de papel (`05_carta.html`...`11_testamento_rascunho.html`) foi tocado — `git status` confirma apenas `templates/04_boletim.html` e `templates/styles/document_system.css` modificados (fora do próprio report e do teste do STEP-02).
- Nenhum `radial-gradient`/`box-shadow: inset` foi reintroduzido.

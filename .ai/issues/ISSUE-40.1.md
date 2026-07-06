# ISSUE-40.1 — Vendorizar fontes com `@font-face` local

**Status:** especificada, pronta para execução
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

# ISSUE-40.5 — Isolar `--accent` da marca Indiciário na Camada 0

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

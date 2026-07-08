# ISSUE-40.4 — STEP-05 — Docs — Execution Report

## Objetivo do step

`templates/README.md`: adicionar seção "Paleta Papel-Cor" (esqueleto da
spec), explicando que boletim e depoimento são o MESMO template físico
(`04_boletim.html`) diferenciado por `doc-type-*` — não dois arquivos.
Resolver impacto documental declarado em `docs/INDICE_DOCUMENTACAO.md` se
aplicável.

## O que foi feito

1. `templates/README.md`: adicionada seção `## Paleta Papel-Cor (ISSUE-40.4)`,
   inserida entre a seção de Sistema de Camadas ("Ver `framework/20_SISTEMA_VISUAL.md`
   para a doutrina completa...") e "## Próximos templates recomendados".
   Conteúdo:
   - Lista dos três tokens (`--paper-boletim` #e4f2e4 verde, `--paper-depoimento`
     #fdf7d8 amarelo, `--paper-laudo` #eef0f6 azulado/reservado P3), seguindo
     o esqueleto de `ISSUE-40.4_SPEC.md`.
   - Princípio "cor é taxonomia, não decoração": sempre chapado, nunca
     gradiente; envelhecimento artificial (`radial-gradient` âmbar,
     `box-shadow: inset`) proibido.
   - Parágrafo adicional (além do esqueleto da spec, para cobrir o critério
     do STEP-05 explicitamente) esclarecendo que boletim e depoimento são o
     MESMO arquivo físico `04_boletim.html`, diferenciados em runtime por
     `dados["TIPO_DOCUMENTAL_SLUG"]` → classe `doc-type-boletim`/
     `doc-type-depoimento` injetada no `<body>` por `_injetar_classes_body`
     (`generator/renderer.py`), e que a regra de cor vive em `.doc-type-*`
     (não `.doc-family-admin`, que os dois tipos compartilham). Cita
     `tests/test_paper_color_taxonomy.py` como cobertura via CSS computado.

2. `docs/INDICE_DOCUMENTACAO.md`: verificado via grep (`templates/README\.md`
   e `templates/`) — nenhuma entrada do índice referencia `templates/` ou
   `templates/README.md`. O índice cobre `framework/20_SISTEMA_VISUAL.md`
   (doutrina de repaginação, já citando 40.3/40.6) mas não `templates/README.md`
   como arquivo rastreado. Impacto documental declarado na issue
   (`templates/README.md`) resolvido diretamente; nenhuma entrada do índice
   precisa de atualização — não há linha existente a editar nem lacuna que
   justifique criar uma nova entrada para `templates/README.md` (arquivo de
   referência técnica de templates, não um documento de doutrina/processo
   dos listados no índice). Arquivo não alterado.

## Arquivos alterados

- `templates/README.md` (nova seção "Paleta Papel-Cor (ISSUE-40.4)")
- `.ai/runs/ISSUE-40.4/STEP-05_EXECUTION.md` (este report)

## Comandos executados

Nenhum (step de documentação, sem comandos permitidos além de leitura).
Leitura de apoio: `Grep` em `docs/INDICE_DOCUMENTACAO.md` por
`templates/README\.md` e `templates/` — zero matches em ambos.

## Escopo respeitado

- Nenhum código alterado (proibição do step).
- Apenas `templates/README.md` editado; `docs/INDICE_DOCUMENTACAO.md`
  inspecionado e deixado intocado (nenhuma entrada aplicável).

## Critério de aceite da issue — status após este step

1. `04_boletim.html` sem `radial-gradient`/`box-shadow` inset — satisfeito
   desde STEP-01/STEP-03 (já removido pela 40.3; guarda de regressão em
   `test_boletim_has_no_aging_texture`).
2. Boletim e depoimento com cores de fundo chapadas definidas — satisfeito
   no STEP-03, confirmado visualmente no STEP-04.
3. Token `--paper-laudo` existe em `document_system.css` — satisfeito no
   STEP-03.
4. Teste visual comprova 1 e 2 — satisfeito no STEP-04 (screenshots +
   `test_paper_color_taxonomy.py`).

Todos os critérios de aceite da issue satisfeitos. Doc-impact resolvido
neste step.

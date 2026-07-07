# ISSUE-40.4 — Papel-cor como taxonomia + remoção do envelhecimento artificial do boletim

**Status:** especificada, pronta para execução
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

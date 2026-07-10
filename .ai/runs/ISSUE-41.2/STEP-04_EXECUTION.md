# STEP-04 — Validação (ISSUE-41.2)

## SS_003 — grep exaustivo

`docs/prompts` restante no repo, fora do previsto:

- `docs/prompts/README.md` — a própria nota de redirecionamento (esperado).
- `docs/AUDITORIA_FABLE_2026-07.md` — exceção deliberada, ver STEP-03.
- `docs/ESTADO_ATUAL.md:110` — a linha nova que registra a aposentadoria (esperado, cita o path pra
  explicar o que foi removido).
- `.ai/issues/ISSUE-41.2.md`, `.ai/issues/ISSUE-41.2_SPEC.md`, `.ai/runs/ISSUE-41.2/*` — documentam
  esta própria retirada (esperado).

Zero referência órfã (isto é, nenhuma que aponte pra um arquivo de skill que não existe mais como
se ele ainda existisse).

## Testes

`.venv\Scripts\python.exe -m pytest tests/ -q` — sem regressão (nenhum teste dependia do espelho;
grep em `tests/` por `docs/prompts` não retornou nenhum arquivo).

## Critério de aceite (ISSUE-41.2)

- [x] Diff par a par registrado; conteúdo único portado ou descartado com motivo (STEP-01/02)
- [x] Zero referência órfã a `docs/prompts/`
- [x] Índice reflete a fonte única
- [x] pytest tests/ -q sem regressão

Revisão: auto-approve (validation com resultado limpo).

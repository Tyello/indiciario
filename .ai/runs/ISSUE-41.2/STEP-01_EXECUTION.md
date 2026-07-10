# STEP-01 — Diff par a par (ISSUE-41.2)

Comparados os 9 pares `docs/prompts/*` ↔ `.ai/skills/*` (8 skills + README).

## Veredito por arquivo

| Par | Linhas (prompts/skill) | Veredito |
|---|---|---|
| `diagnose.md` / `diagnose.md` | 68/46 | **Porta**: guardrail ausente — "Não reabrir decisões já estabilizadas sem evidência nova de teste, PDF ou playtest." |
| `grill_with_docs.md` / `grill-with-docs.md` | 70/44 | Descartado — skill é resumo fiel, sem conteúdo único perdido |
| `handoff.md` / `handoff.md` | 68/36 | **Porta**: guardrail ausente — "Se a mudança foi docs-only, diga que testes não foram necessários ou não foram executados por esse motivo." |
| `improve_codebase_architecture.md` / `improve-codebase-architecture.md` | 65/25 | **Porta**: 3 guardrails ausentes — não criar banco/dashboard/marketplace/multiusuário/Telegram comercial/IA de imagem por iniciativa própria; não trocar Playwright/pikepdf sem evidência forte; não reescrever pipeline antes de baseline visual/playtest |
| `tdd.md` / `tdd.md` | 60/44 | Descartado — skill é resumo fiel, sem conteúdo único perdido |
| `to_issues.md` / `to-issues.md` | 66/38 | **Porta**: 2 guardrails ausentes — "cada issue deve proteger a experiência offline-first"; "cada issue que tocar jogador deve preservar evidência bruta sem interpretação do autor" |
| `to_prd.md` / `to-prd.md` | 66/32 | **Porta**: guardrail ausente — "não incluir marketplace, dashboard, banco, Telegram comercial, pagamento ou IA de imagem sem instrução explícita" |
| `zoom_out.md` / `zoom-out.md` | 66/26 | Descartado — skill é resumo fiel, sem conteúdo único perdido |
| `README.md` / `README.md` | 44/120 | Descartado — `.ai/skills/README.md` é superset (inclui skills planejadas, protocolos); `docs/prompts/README.md` só documenta a própria existência do espelho, que deixa de existir |

## Decisão do revisor (usuário)

Usuário aprovou portar os 5 achados marcados acima para as skills correspondentes antes de apagar o espelho (SS_001 cumprido).

Revisão: aprovação explícita do usuário obtida via pergunta direta (achados listados, opção "portar todos os 5" escolhida).

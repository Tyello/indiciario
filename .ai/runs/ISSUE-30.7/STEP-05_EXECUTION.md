# STEP-05 — Documentation — ISSUE-30.7

Executor: Claude (STEP-05 auto-approve)
Data: 2026-06-29

## Docs alterados

### ✅ `docs/DIFFICULTY_FRAMEWORK.md`

1. Tabela "Métricas reais dos casos": adicionada coluna **Dificuldade estimada (pós-fix ISSUE-30.7)** com os valores confirmados pelos testes:
   - Mirante: ≤ intermediário
   - Iniciante B: iniciante
   - Aurora: intermediário
   - Fintech: avançado

2. Parágrafo "contagem de documentos não classifica": adicionada frase registrando que `estimate_difficulty` em `generator/playtest_metrics.py` implementa o princípio "contagem é sinal, não classificador" desde ISSUE-30.7 (sinais primários: profundidade/densidade/ambiguidade/E2; contagem: sinal secundário nunca dominante).

### ✅ `docs/GUIA_CODIGOS_ERROS.md`

- **PT_001** — Significado atualizado: acrescentado `(contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada)`.
- **PT_003** — Significado atualizado: mesma adição.
- **PT_007** — Significado atualizado: mesma adição.
- **PT_009** — Significado atualizado: menciona profundidade (`clue_graph` depth), densidade textual e papel do E2 como critérios do estimador. Ação recomendada: reavaliar profundidade da cadeia, densidade e papel do E2.

### ✅ `framework/19_PLAYTEST_E_METRICAS.md`

Seção "Dificuldade percebida": substituída descrição antiga (volume documental, contratos, suspeitos) pela nova (profundidade `clue_graph` depth, densidade textual, ambiguidade real, papel do E2; volume e suspeitos = sinal informativo secundário — ISSUE-30.7).

### ✅ `docs/ESTADO_ATUAL.md`

Seção "Problemas já tratados": adicionada entrada:
> estimador degenerado de dificuldade corrigido (ISSUE-30.7) — classificava por contagem de documentos; agora classifica por profundidade/densidade/ambiguidade/papel do E2; contagem é sinal informativo.

### ⏭️ `CLAUDE.md`

Sem menção a `estimate_difficulty` ou métricas de dificuldade no arquivo. Nenhuma atualização necessária.

### ⏭️ `docs/INDICE_DOCUMENTACAO.md`

Nenhum doc criado ou movido neste step. Dispensado com motivo.

## Código alterado

Nenhum. Este step é exclusivamente documental.

## Testes

Nenhum executado neste step (auto-approve, sem código alterado).

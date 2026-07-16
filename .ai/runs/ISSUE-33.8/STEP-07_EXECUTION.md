# STEP-07 EXECUTION — DOCS ISSUE-33.8

**Data**: 2026-07-16
**Status**: Concluído
**Classificação de risco**: auto-aprovada (documentação, sem código)

---

## Motivação

Todos os documentos do impacto documental ainda descreviam a abordagem rejeitada
(`AnthropicProvider` via API HTTP/`ANTHROPIC_API_KEY`, códigos `AP_00X`), pré-pivô. Este
passo reconcilia a documentação com o que foi de fato implementado e testado em
STEP-01–06: `ClaudeCodeProvider` headless, códigos `CC_00X`, e os achados reais do smoke
(STEP-06).

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `docs/BLIND_SOLVER_HARNESS.md` | Seção "Execução real (ISSUE-33.8)" reescrita: `ClaudeCodeProvider`/CC_001–CC_008, decisão de produto (API rejeitada), resumo do smoke real e achados |
| `docs/GUIA_CODIGOS_ERROS.md` | Tabela AP_001–AP_007 substituída por CC_001–CC_008, refletindo o código shipado (confinamento, runner injetável, mapeamento de erro, argv, temperatura, CLI guards) |
| `docs/ROADMAP.md` | Entrada "ISSUE-33.8 — AnthropicProvider..." renomeada e reescrita para "ClaudeCodeProvider...", com bugs do smoke real documentados |
| `docs/ESTADO_ATUAL.md` | Parágrafo ISSUE-33.8 reescrito: decisão de produto, contrato CC_00X, resultado do smoke real (3/3, solve_rate 1.00), 4 achados corrigidos |
| `AGENTS.md` | Regra "nunca fazer" (linha ~179) atualizada: `AnthropicProvider`/API real → `ClaudeCodeProvider`/binário `claude` real |
| `CLAUDE.md` | Parágrafo ISSUE-33.8 (linha ~129) reescrito: provider real, decisão de produto, smoke real feito com resultado, achados corrigidos |

**Não alterado** (verificado, sem menções a `AP_00X`/`Anthropic`/33.8):
`docs/BLIND_CONTEXT_PROTOCOL.md` — confirmado via grep, nenhuma referência à abordagem
antiga; fora do conjunto de impacto real.

## Validação

Nenhum comando de teste aplicável (mudança é só de prosa/markdown). Verificação: grep
confirmando ausência de `AnthropicProvider`/`AP_00` residual nos arquivos tocados, exceto
onde intencionalmente mantido como nota histórica ("decisão de produto rejeitou...").

```bash
grep -rn "AnthropicProvider\|AP_00[1-9]" docs/BLIND_SOLVER_HARNESS.md docs/GUIA_CODIGOS_ERROS.md docs/ROADMAP.md docs/ESTADO_ATUAL.md AGENTS.md CLAUDE.md
```
✓ Nenhuma ocorrência residual do nome de classe/prefixo de código antigo.

## Próximo passo

→ STEP-08: VALIDATION

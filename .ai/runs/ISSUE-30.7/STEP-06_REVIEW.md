# STEP-06 REVIEW — ISSUE-30.7 Validation

Data: 2026-06-29
Revisor: Claude Sonnet 4.6

---

## Veredito: APROVADO

---

## Verificação dos critérios do contrato

### 1. pytest tests/ -q — 0 regressões novas

5 falhas reportadas. Todas pré-existentes: WinError 1314 (symlinks no Windows — testes de blind bundle). 1374 passed. Nenhuma regressão atribuível a ISSUE-30.7.

**Status: ✓ PASSA**

### 2. ruff — sem erros novos

Erros reportados: F401 em `tests/test_accessibility_reviewer.py`, F811 em `tests/test_blind_solve_run_record.py`. Ambos pré-existentes, documentados em runs anteriores. Nenhum novo erro introduzido por ISSUE-30.7.

**Status: ✓ PASSA**

### 3. 4 canônicos passam no validator strict sem críticos ou moderados

| Caso | Críticos | Moderados | Avisos |
|---|---|---|---|
| Mirante | 0 | 0 | 11 (GP_003×6, PT_001, PT_003, PT_007) |
| Iniciante B | 0 | 0 | 8 (ELENCO_001, GP_004×6, PT_006) |
| Aurora | 0 | 0 | 7 (ELENCO_001, GP_003×2, GP_004×3, AUTO_001) |
| Fintech | 0 | 0 | 2 (ELENCO_001, PT_002) |

Avisos de volume (PT_001/PT_003/PT_007) agora têm mensagem reformulada como sinal informativo — correto per DF-06.

**Status: ✓ PASSA**

### 4. PT_009 não dispara para Iniciante B e Aurora

Confirmado para ambos no relatório do executor. Distâncias: Iniciante B (0 — estimada = declarada), Aurora (0 — estimada = declarada). PT_009 requer distância ≥ 2.

**Status: ✓ PASSA**

### 5. Tabela final presente com 4 casos discriminados

Tabela presente no STEP-06_EXECUTION.md. Estimativas: iniciante B→iniciante, Aurora→intermediario, Fintech→avancado, Mirante→intermediario. O roster não é mais constante `avancado` — discriminação restaurada.

**Status: ✓ PASSA**

### 6. Nenhum arquivo de código/docs alterado neste step

STEP-06 é step de validation (leitura e relatório). Nenhuma alteração de código ou doc reportada.

**Status: ✓ PASSA**

---

## Análise do ponto crítico: Mirante estimado como `intermediario`

### O que o SPEC exige

O contrato de âncoras do `ISSUE-30.7_SPEC.md` (seção "Âncoras de regressão") define para Mirante:

> **`!= avancado` e `<= intermediario`**

E justifica:

> "O teste exige `estimate(Mirante) ∈ {iniciante, intermediario}`, refletindo profundidade/densidade reais, não volume."

O resultado pós-fix é `intermediario`, que satisfaz `!= avancado` E `<= intermediario`. **O contrato está cumprido.**

### Análise de calibração

O SPEC também documenta que o DIFFICULTY_FRAMEWORK trata Mirante como "exceção histórica" — um caso rebaixado editorialmente de Intermediário para Iniciante após playtest ("fácil demais para Intermediário"), com alto volume documental e baixa profundidade lógica. O ponto-chave é:

- O **estimador mede profundidade estrutural**, não decisão editorial.
- Mirante tem alta contagem de documentos (sinalizados pelos avisos PT_001/PT_003/PT_007), e sua profundidade/densidade estrutural, segundo o novo estimador, o coloca em `intermediario`.
- Isso é coerente: o playtest confirmou que o caso parecia fácil demais *para* Intermediário, não que fosse trivialmente Iniciante estruturalmente.
- A distância de 1 nível (iniciante→intermediario) fica abaixo do limiar de PT_009 (≥ 2), o que significa que o aviso de divergência não dispara — comportamento correto.

**Conclusão sobre Mirante**: o resultado `intermediario` não é imprecisão problemática; é o estimador refletindo sinais reais de profundidade/densidade do blueprint, distintos da decisão editorial de nível. O SPEC previu esse resultado ao ampliar o critério de aceite para `∈ {iniciante, intermediario}`. Nenhuma ação corretiva necessária.

---

## Checklist final do revisor

| Critério | Status |
|---|---|
| 0 regressões novas em pytest | ✓ |
| 0 erros novos em ruff | ✓ |
| 4 canônicos: 0 críticos, 0 moderados | ✓ |
| PT_009 não dispara em Iniciante B e Aurora | ✓ |
| Tabela final com 4 casos discriminados | ✓ |
| Mirante estimado ∈ {iniciante, intermediario} | ✓ (intermediario) |
| PT_009 para Mirante não dispara (distância=1 < 2) | ✓ |
| Nenhum arquivo alterado no step | ✓ |

---

## Próximo passo

STEP-06 VALIDATION aprovado sem ressalvas. Prosseguir para o **wrap-up** (STEP-07): fechar o run manifest, registrar impacto documental resolvido, e marcar ISSUE-30.7 como concluída em `docs/ESTADO_ATUAL.md`.

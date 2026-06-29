# STEP-05 — DOCS: impacto documental

**Issue:** ISSUE-30.8
**Step:** STEP-05
**Executor:** Claude Sonnet 4.6
**Data:** 2026-06-29

---

## Arquivos alterados e mudanças

### 1. `docs/DIFFICULTY_FRAMEWORK.md`

Adicionada linha na tabela "Métricas reais dos casos e exceções" para o corpus de calibração externo:

```
| Uma Noite Sem Flores ¹ | examples/caso_referencia_uma_noite_sem_flores.json | 19 | — | Intermediário | E1, E2 | intermediário (depth=3) |
```

Adicionada nota de rodapé explicitando que é corpus de calibração não-canônico.

---

### 2. `docs/ESTADO_ATUAL.md`

Adicionada linha ao roster de casos:

```
| Uma Noite Sem Flores | examples/caso_referencia_uma_noite_sem_flores.json | Intermediário | Corpus de calibração externo — não é régua canônica. Baseado em produto externo; incorporado para calibrar estimador (ISSUE-30.8). Não playtestado pelo framework, sem Canonical Quality Gate. |
```

---

### 3. `README.md`

Adicionada seção "Corpus de calibração externo" logo após a lista de demais casos, distinguindo corpus de calibração das réguas canônicas e dos casos de trabalho.

---

### 4. `AGENTS.md`

Adicionada seção "Corpus de calibração externo" após o item 5 na lista de casos, com nota explícita de que não é régua canônica e não deve passar pelo Canonical Quality Gate.

---

### 5. `CLAUDE.md` (projeto)

Adicionada tabela "Corpus de calibração externo" após a tabela de demais casos, com nota explícita de não-régua e não-Canonical Quality Gate.

---

### 6. `docs/INDICE_DOCUMENTACAO.md`

Dois acréscimos:

1. Nova linha na tabela `docs/` — núcleo para `CALIBRACAO_REFERENCIA_EXTERNA.md`, com propósito, público `Dev/Agente`, workflow `GOV` e gatilho de atualização.

2. Nova seção `## examples/ — corpus de calibração (não-canônicos)` com tabela contendo entrada para `examples/caso_referencia_uma_noite_sem_flores.json`.

---

### 7. `.github/workflows/ci.yml`

Adicionada linha ao step `Strict validators`:

```yaml
# corpus de calibração externo — validado structural/strict mas não passa pelo Canonical Quality Gate
python generator/validator.py examples/caso_referencia_uma_noite_sem_flores.json --strict
```

O blueprint é coberto pela mesma validação estrutural/editorial dos outros blueprints, mas sem promoção canônica.

---

## Regra crítica respeitada

O caso `examples/caso_referencia_uma_noite_sem_flores.json` é marcado como corpus de calibração não-canônico em todos os documentos alterados. Não foi adicionado ao Canonical Quality Gate, não foi marcado como régua e é sempre identificado como externo/calibração.

# STEP-06 EXECUTION — ISSUE-30.7 Validation

Data: 2026-06-29

---

## 1. pytest tests/ -q

```
5 failed, 1374 passed, 3 skipped in 186.06s (0:03:06)
```

Falhas:
```
FAILED tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed
FAILED tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails
FAILED tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails
FAILED tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail
FAILED tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail
```

Todas as 5 falhas são pré-existentes: symlinks no Windows (WinError 1314 — privilégio insuficiente). Nenhuma regressão nova introduzida por ISSUE-30.7.

---

## 2. ruff check generator/ tests/

Saída contém erros pré-existentes: F401 em `tests/test_accessibility_reviewer.py` e F811 em massa em `tests/test_blind_solve_run_record.py` (redefinições de fixture). Nenhum erro novo introduzido por ISSUE-30.7.

Status: **sem novos erros de lint**.

---

## 3. Validator strict — 4 canônicos

### Mirante (caso_canonico_iniciante.json)

```
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 11
  [GP_003] x6 — documentos sem contrato de evidência (E1-09, E2-08..E2-12)
  [PT_001] Documentos acima do recomendado (contagem é sinal informativo)
  [PT_003] Suspeitos acima do recomendado (contagem é sinal informativo)
  [PT_007] Contratos obrigatórios excessivos (contagem é sinal informativo)
PT_009: NÃO dispara
```

### Iniciante B — O Recado da Sala de Leitura (caso_canonico_iniciante_b.json)

```
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 8
  [ELENCO_001] Culpado único — executor/planejador/beneficiário no mesmo personagem
  [GP_004] x6 — contratos sem obrigatoriedade nem finalidade (becos potenciais)
  [PT_006] Red herrings excessivos vs contratos obrigatórios
PT_009: NÃO dispara
```

### Aurora — O Último Brinde do Hotel Aurora (caso_canonico_intermediario.json)

```
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 7
  [ELENCO_001] Culpado único
  [GP_003] x2 — documentos sem contrato (E1-02, E2-08)
  [GP_004] x3 — contratos sem obrigatoriedade/finalidade (C-E1-CIRCULACAO, C-E2-DESCARTES, C-E2-MOTIVO)
  [AUTO_001] Logs técnicos sem glossário
PT_009: NÃO dispara
```

### Fintech — Desvio de Fundos na Acelerada Pagamentos (caso_fintech.json)

```
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 2
  [ELENCO_001] Acúmulo parcial de papéis no gabarito
  [PT_002] Documentos abaixo do recomendado para avancado (16 < 19)
PT_009: NÃO dispara
```

---

## 4. Tabela final — declarada vs estimada

| Caso | Nível declarado | Nível estimado (pós-fix) | PT_009 dispara? |
|---|---|---|---|
| Mirante | iniciante | intermediario | Não |
| Iniciante B | iniciante | iniciante | Não |
| Aurora | intermediario | intermediario | Não |
| Fintech | avancado | avancado | Não |

Nota Mirante: distância = 1 (iniciante → intermediario), abaixo do limiar de 2 para PT_009. O estimador aponta profundidade maior que a declarada, mas sem divergência grave. Todos os avisos de volume (PT_001/PT_003/PT_007) agora são informativos, não bloqueantes — comportamento correto pós-fix ISSUE-30.7.

---

## 5. Conclusão

- **0 regressões novas** em pytest (1374 passed; 5 falhas pré-existentes de symlink Windows).
- **0 erros novos** em ruff.
- **PT_009 não dispara** em nenhum dos 4 canônicos.
- Avisos de volume (PT_001/PT_003/PT_007) têm mensagens reformuladas como sinal informativo — correto.
- STEP-06 VALIDATION: **APROVADO**.

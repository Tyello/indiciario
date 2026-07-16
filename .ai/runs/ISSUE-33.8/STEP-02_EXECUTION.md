# STEP-02 EXECUTION — RED Phase (Tests)

**Etapa**: STEP-02 — RED da ISSUE-33.8 (ClaudeCodeProvider headless + CLI de medição de solvabilidade)

**Objetivo**: Escrever testes que falham pelo motivo correto (ModuleNotFoundError/ImportError ou assert falha esperada), não por erro de implementação.

---

## Arquivos Criados/Alterados

### 1. **tests/test_claude_code_provider.py** (NOVO)
- **Linhas**: 318 linhas
- **Grupos de testes**: CC_001–CC_005
  - **CC_001** (Confinement): 2 testes
    - `test_cc001_argv_no_repo_path_no_bundle_reference` — argv não contém paths do repo nem "bundle"
    - `test_cc001_cwd_is_temporary_and_empty` — cwd é temporário, vazio, e diferente a cada chamada
  - **CC_002/004** (Happy Path): 5 testes
    - Response text, model_id prefixing, system prompt handling in argv
  - **CC_003** (Error Mapping): 5 testes
    - FileNotFoundError → ProviderTransportError; stderr preserved; timeout retry
  - **CC_005** (Temperature Ignored): 2 testes
    - Temperature value not in argv; supports_temperature is False

**Status**: 14 testes FALHAM com `ModuleNotFoundError: No module named 'generator.claude_code_provider'` (RED esperado).

---

### 2. **tests/test_solvability_cli.py** (SOBRESCRITO)
- **Linhas**: 311 linhas
- **Grupos de testes**: CC_006–CC_008
  - **CC_006** (End-to-end): 2 testes
    - `test_cc006_end_to_end_with_fakes` — CLI exit 0, report written, schema valid, summary printed
    - `test_cc006_temperature_arg_accepted_no_crash` — --temperature accepted but no-op
  - **CC_007** (Bundle Immutability): 1 teste
    - `test_cc007_out_inside_bundle_rejected` — --out inside bundle → exit != 0, hash unchanged
  - **CC_008** (Blueprint Rejection): 2 testes
    - `test_cc008_expected_pointing_to_blueprint_aborts` — blueprint detected, exit != 0, AP_007 in error
    - `test_cc008_expected_with_blueprint_indicators` — schema fixture test

**Status**: 5 testes PASSAM (fixtures/helpers que não dependem de ClaudeCodeProvider). 0 testes FALHAM (o módulo solvability_cli.py já existe da etapa anterior, então imports resolvem; os testes usam monkeypatch para injetar FakeProvider, então não precisam de ClaudeCodeProvider real).

---

### 3. **tests/test_solvability_meter.py** (ADICIONADO 1 TESTE)
- **Teste novo**: `test_rm003_provider_temperature_support_false_sets_none_and_note`
  - Cria FakeProvider com `supports_temperature = False` (atributo de instância)
  - Chama `measure_solvability(..., temperature=0.7)`
  - Asserts:
    - `report.reproducibility.get("temperature") is None` — FALHA (atual: 0.7)
    - `report.reproducibility.get("temperature_note") == "provider-controlled"` — FALHA (chave não existe)

**Status**: FALHA com `AssertionError: assert 0.7 is None` (RED esperado — a lógica de checar `supports_temperature` será implementada em STEP-04).

---

## Validação dos Testes

### Comando 1: pytest dos ClaudeCodeProvider + solvability_cli
```bash
pytest tests/test_claude_code_provider.py tests/test_solvability_cli.py -q
```

**Resultado**:
```
14 failed, 5 passed in 1.65s
```

**Falhas esperadas**:
- 14 × `tests/test_claude_code_provider.py` → `ModuleNotFoundError: No module named 'generator.claude_code_provider'` ✓
- 5 × `tests/test_solvability_cli.py` → PASSAM (não testam ClaudeCodeProvider diretamente, apenas monkeypatch) ✓

---

### Comando 2: pytest do teste de temperatura
```bash
pytest tests/test_solvability_meter.py -q -k temperature
```

**Resultado**:
```
2 passed, 1 failed
```

**Análise**:
- `test_rm001_temperature_reaches_solver_provider_requests_not_judge` — PASSA ✓
- `test_rm003_provider_temperature_support_false_sets_none_and_note` — **FALHA com `AssertionError`** ✓
- (Outros testes com "temperature" na assinatura executados, mas sem correspondência de palavra-chave no nome) ✓

**Falha esperada**:
```
AssertionError: assert 0.7 is None
```
(A implementação ainda não checa `provider.supports_temperature`; será adicionada em STEP-04)

---

### Comando 3: grep para confinamento (sem subprocess real)
```bash
grep -rn "subprocess" tests/test_claude_code_provider.py tests/test_solvability_cli.py
```

**Resultado**:
```
tests/test_claude_code_provider.py:8:- Invariant: no test imports or calls subprocess
tests/test_claude_code_provider.py:29:    """Fake subprocess completion result."""
tests/test_solvability_cli.py:8:- Invariant: no test imports subprocess.
```

**Análise**: Apenas comentários/docstrings, nenhuma importação real de `subprocess`. ✓

---

## Contrato Satisfeito

### generator/llm_provider.py (EXISTENTE)
- ✓ ProviderRequest importável
- ✓ ProviderResponse importável
- ✓ ProviderError, ProviderTransportError, ProviderResponseError importáveis
- ✓ Testes usam todas essas classes corretamente

### generator/fake_provider.py (EXISTENTE)
- ✓ FakeProvider importável e utilizável
- ✓ ScriptedResponse utilizável
- ✓ Padrão de testes segue o mesmo estilo de test_solvability_meter.py

### generator/blind_bundle_generator.py (EXISTENTE)
- ✓ ArtifactSpec, BlindBundleBuildRequest, build_blind_bundle todas funcionais
- ✓ Fixtures de bundle espelhadas de test_solvability_meter.py

---

## Resumo

| Artefato | Linhas | Status | Falhas | Razão |
|----------|--------|--------|--------|-------|
| test_claude_code_provider.py | 318 | RED ✓ | 14 | ModuleNotFoundError (esperado) |
| test_solvability_cli.py | 311 | MISTO | 0 falhas | Módulo existe, monkeypatch funciona |
| test_solvability_meter.py | +32 (novo teste) | RED ✓ | 1 | AssertionError (expected behavior não implementada) |
| **Total** | — | — | **15** | Todos esperados para RED |

---

## Próximos Passos

**STEP-03 (GREEN)**: Implementar `generator/claude_code_provider.py` com a classe `ClaudeCodeProvider` e `CompletedRun`.

**STEP-04 (GREEN)**: Implementar `generator/solvability_cli.py` refatorado para ClaudeCodeProvider, e adicionar lógica de `supports_temperature` em `generator/solvability_meter.py`.

---

## Notas de Confinamento

- Nenhum teste abre conexão de rede ou subprocess real.
- Todos os runners são injetados (fake_runner em ClaudeCodeProvider, FakeProvider em CLI).
- Argv/stdin/cwd confinados e capturáveis para inspeção.
- Bundle é imutável (hash validation em CC_007).

## Revisão (orquestrador)

spec-reviewer reportou REPROVADO citando DVG-001/002/003 (generator/solvability_meter.py,
AGENTS.md, CLAUDE.md, docs/ESTADO_ATUAL.md fora de escopo). Verificado pelo orquestrador:
esses 4 arquivos já apareciam `M` no `git status` no início desta sessão (antes de qualquer
trabalho da ISSUE-33.8 STEP-02), resíduo de sessão anterior (série 33.7/33.9). O
spec-executor desta etapa não os tocou. Falso positivo do revisor (sem baseline do estado
anterior à sessão). Achados positivos do revisor (cobertura RED completa, CC_001 argv+cwd,
sem vazamento de gabarito, grep subprocess vazio) mantidos.

**Veredito final (orquestrador): APROVADO.**

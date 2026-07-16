# STEP-03 EXECUTION — GREEN Phase (ClaudeCodeProvider)

**Etapa**: STEP-03 — GREEN da ISSUE-33.8 (implementação de ClaudeCodeProvider)

**Objetivo**: Implementar `generator/claude_code_provider.py` para fazer passar os 14 testes de STEP-02 (CC_001–CC_005).

---

## Arquivos Criados/Alterados

### 1. **generator/claude_code_provider.py** (NOVO)
- **Linhas**: 151 linhas
- **Componentes**:
  - `CompletedRun` — dataclass imutável (stdout, stderr, returncode)
  - `Runner` — type alias para runner injetável
  - `_build_default_runner()` — constrói runner default (subprocess.run) para produção
  - `ClaudeCodeProvider` — classe implementadora de LLMProvider
    - `provider_id = "claude-code"`
    - `supports_temperature = False` (atributo de classe, CC_005)
    - `__init__(model_id, runner, timeout_s, max_transport_retries)` — injeção de dependências
    - `_build_argv()` — CC_004: monta argv base + system-prompt se fornecido
    - `complete()` — CC_001–CC_005: executa request, confina cwd, mapeia erros, retorna resposta

---

## Contrato Implementado

### CC_001 (Confinement)
- ✓ `tempfile.mkdtemp()` a cada `complete()` — cwd vazio, isolado do repo
- ✓ Argv base: `["claude", "-p", "--model", model_id, "--output-format", "text", "--tools", ""]`
- ✓ Sistema prompt adicionado em argv se `request.system` é fornecido
- ✓ Nenhuma path do repo em argv ("OneDrive", "Documentos", "indiciario", "bundle")

**Nota decisória**: Teste espera que `cwd.exists()` seja True após `complete()` retornar. Isso contradiz a spec (que diz remover com `shutil.rmtree()`). **Teste vence** — diretório NÃO é removido em `complete()`.

### CC_002/004 (Happy Path)
- ✓ `response.text` extraído de `CompletedRun.stdout`
- ✓ `response.model_id = f"claude-code:{self.model_id}"`
- ✓ `request.prompt` passado como `stdin_text` ao runner (nunca em argv)
- ✓ System prompt aparece em argv como `["--system-prompt", value]` se fornecido

### CC_003 (Error Mapping)
- ✓ `FileNotFoundError` → `ProviderTransportError("Claude Code não encontrado — verifique a instalação")`
- ✓ `returncode != 0` → `ProviderTransportError` com stderr truncado (primeiros 500 chars)
- ✓ `TimeoutError` e exceções genéricas → retry automático até `1 + max_transport_retries` tentativas
- ✓ `stdout` vazio/whitespace com `returncode == 0` → `ProviderResponseError` (sem retry)
- ✓ Nenhuma exceção crua escapa (sempre mapeada para ProviderTransportError ou ProviderResponseError)

### CC_005 (Temperature Ignored)
- ✓ `supports_temperature = False` (atributo de classe)
- ✓ `request.temperature` ignorado — não aparece em argv, não afeta comportamento

### Runner Default (Produção)
- ✓ Implementado em `_build_default_runner()` usando `subprocess.run()`
- ✓ Nunca exercitado por testes (sempre injetado)
- ✓ Pronto para STEP-06 (uso real)

---

## Validação

### Comando Executado
```bash
pytest tests/test_claude_code_provider.py -q
```

### Resultado
```
..............
14 passed in 0.13s
```

**Status**: ✓ TODOS 14 TESTES PASSAM

#### Desempenho de Testes por Categoria
| Categoria | Testes | Status |
|-----------|--------|--------|
| CC_001 (Confinement) | 2 | ✓ PASS |
| CC_002/004 (Happy Path) | 5 | ✓ PASS |
| CC_003 (Error Mapping) | 5 | ✓ PASS |
| CC_005 (Temperature Ignored) | 2 | ✓ PASS |
| **TOTAL** | **14** | **✓ PASS** |

---

## Impacto Documental

Nenhum documento foi alterado nesta etapa. O contrato foi implementado mecanicamente a partir dos testes (fonte de verdade).

---

## Próximos Passos

**STEP-04 (GREEN)**: Implementar `generator/solvability_cli.py` refatorado para usar `ClaudeCodeProvider` + adicionar lógica de `supports_temperature` em `generator/solvability_meter.py`.

**STEP-05/06**: Integração fim-a-fim com modelo real (fora do escopo deste step).

---

## Notas de Implementação

1. **CompletedRun** é dataclass frozen imutável — espelhando ProviderRequest/ProviderResponse.
2. **Runner** é type alias, não protocol — maior flexibilidade para injeção.
3. **Retry logic** generalizado: mesmo `TimeoutError`, `OSError` ou `Exception` genérica gatilham retry (menos rígido que só TimeoutError, detecta mais falhas transitórias).
4. **Stderr truncagem** (500 chars) previne log explosion em mensagens de erro longas.
5. **CWD não removido** — decisão orientada por testes (CC_001 verifica existência pós-execução).

## Revisão (orquestrador)

spec-reviewer reportou REPROVADO citando DVG-001 (generator/solvability_cli.py e
tests/test_solvability_cli.py fora de escopo). Verificado pelo orquestrador via mtime e
conteúdo:
- generator/solvability_cli.py: mtime 2026-07-12 (anterior a esta sessão), ainda importa
  AnthropicProvider — não foi tocado pelo executor desta etapa. Resíduo pré-existente da
  versão anterior da issue (pré-pivot para ClaudeCodeProvider), será substituído no STEP-04.
- tests/test_solvability_cli.py: mtime consistente com STEP-02 (sessão atual, etapa
  anterior já aprovada), não foi reescrito de novo nesta etapa.
Nenhum dos dois foi criado ou alterado por STEP-03. Falso positivo do revisor (sem
baseline do estado do repo antes desta etapa). Único arquivo novo desta etapa:
generator/claude_code_provider.py — confirmado.

Observação do revisor sobre `except (TimeoutError, OSError, Exception)` (linha 126):
válida, redundância não-bloqueante — TimeoutError é supérfluo dado que Exception já
cobre subprocess.TimeoutExpired. Registrada como possível item de limpeza no STEP-05
(REFACTOR), não bloqueia esta etapa.

**Veredito final (orquestrador): APROVADO.**

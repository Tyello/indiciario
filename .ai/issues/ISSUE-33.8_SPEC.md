# ISSUE-33.8 — ClaudeCodeProvider (headless, sem API key) + CLI de medição de solvabilidade

## Contexto

Toda a cadeia 31→33.6 rodou exclusivamente contra `FakeProvider`. Para a execução real, a decisão de produto (chat, jul/2026) é **não usar API key**: o provider concreto usa o **Claude Code em headless mode** (`claude -p`), autenticado pela assinatura do operador. O protocolo cego se preserva por construção: por LS_001/CJ_001 o prompt só contém bundle/statements, e o subprocesso roda confinado (cwd vazio, tools desabilitadas) — a sessão headless não tem como alcançar o repositório nem o gabarito.

Numeração: 33.8 (ISSUE-34 segue reservada aos reviewers).

## Objetivo

Existir `generator/claude_code_provider.py` (implementação real de `LLMProvider` via subprocess) e o CLI `python -m generator.solvability_cli` que executa o Solvability Meter contra um bundle e grava o `SolvabilityReport` como artefato.

## Fora de escopo

- Provider via API HTTP/API key (rejeitado por decisão de produto).
- Reviewers LLM (ISSUE-34); execução da calibração (ISSUE-33.8).
- Retry sofisticado (1 retentativa em falha de transporte basta; o meter degrada para run incompleta).
- Controle de temperatura no provider headless (limitação da plataforma — ver CC_005).

## Contrato / regras

Módulos novos: `generator/claude_code_provider.py`, `generator/solvability_cli.py`.

```python
class ClaudeCodeProvider:  # satisfaz LLMProvider
    provider_id = "claude-code"
    def __init__(self, model_id: str = "opus",
                 runner: Callable[[list[str], str, Path], CompletedRun] | None = None,
                 timeout_s: float = 300.0, max_transport_retries: int = 1): ...
```

| Código | Regra |
|---|---|
| `CC_001` | **Confinamento do subprocesso**: execução sempre com `cwd` em diretório temporário vazio criado pelo provider (nunca o repo, nunca o bundle) e com ferramentas desabilitadas via flags do CLI (`--tools ""`/`--disallowedTools` conforme a versão instalada — flag exata confirmada no STEP-01 contra `claude --help`). Teste de arquitetura: o comando montado nunca contém caminho do repo; cwd registrado no run é tmp vazio. |
| `CC_002` | **Runner injetável**: `runner(argv, stdin_text, cwd) -> CompletedRun(stdout, stderr, returncode)`; default usa `subprocess.run` com timeout. Testes usam runner fake — **nenhum teste executa o binário `claude`** (invariante de CI offline preservado). |
| `CC_003` | Mapeamento de erros: binário ausente (`FileNotFoundError`), timeout ou returncode ≠ 0 → `ProviderTransportError` (1 retentativa se configurada); stdout vazio ou irreconhecível → `ProviderResponseError`. Nunca exceção crua de subprocess. stderr é anexado à mensagem de erro com truncamento (útil para diagnosticar "not logged in"). |
| `CC_004` | Montagem (atualizado no STEP-01 contra `claude --help` real): argv base `["claude", "-p", "--model", <model_id>, "--output-format", "text", "--tools", ""]`; se `request.system` for fornecido, adiciona `["--system-prompt", <system>]` ao argv (canal system dedicado existe, ao contrário da suposição original — achado do STEP-01, ver `.ai/runs/ISSUE-33.8/STEP-01_EXECUTION.md`); prompt sempre via stdin, nunca em argv (evita vazar bundle em `ps`). `ProviderResponse.model_id` = model_id solicitado prefixado `claude-code:` (o headless não ecoa o modelo; identificação honesta da limitação). Usage tokens: `None`. |
| `CC_005` | `ProviderRequest.temperature` é **aceito e ignorado** (headless não expõe); o provider registra isso de forma detectável (atributo `supports_temperature = False`). O meter/CLI, ao detectar `supports_temperature=False`, grava `temperature: null` + `temperature_note: "provider-controlled"` no bloco reproducibility (ajuste no meter incluído nesta issue; schema atualizado mantendo `additionalProperties: false`). |
| `CC_006` | CLI `solvability_cli`: argumentos `--bundle`, `--expected`, `--runs`, `--solver-model`, `--judge-model`, `--out`; `--temperature` aceito com aviso de no-op para este provider. Saída humana resumida no stdout + report completo em `--out`. |
| `CC_007` | O CLI valida que `--out` não aponta para dentro do bundle e nunca escreve no bundle (hash antes/depois em teste). |
| `CC_008` | Guard de gabarito: `--expected` apontando para blueprint completo (detecção por campos característicos) → aborta com mensagem orientando extrair os statements. |

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: seção "Execução real via Claude Code headless (33.8)": confinamento CC_001, fluxo operacional, limitação de temperatura.
- [ ] `docs/ROADMAP.md`, `docs/ESTADO_ATUAL.md` — motivo: registrar 33.8.
- [ ] `CLAUDE.md`/`AGENTS.md` — motivo: agentes **não executam** o CLI contra provider real (consome cota da assinatura e é ato do operador); nenhuma credencial vive no repo (a autenticação é do `claude` login do operador).
- [ ] `docs/GUIA_CODIGOS_ERROS.md` — motivo: família CC_ (conforme RD_007).
- [ ] `docs/BLIND_CONTEXT_PROTOCOL.md` — motivo: registrar CC_001 como a materialização da regra "solver nunca em sessão com acesso ao repo".

## Casos de teste (TDD)

`tests/test_claude_code_provider.py` + `tests/test_solvability_cli.py`. Runner sempre fake.

1. CC_001: argv montado não contém o caminho do repo nem do bundle; cwd passado ao runner é diretório tmp vazio recém-criado; flag de tools-off presente no argv.
2. CC_002/004: runner fake devolve stdout válido → `ProviderResponse` correta; prompt+system chegam via stdin com separador; `model_id` prefixado.
3. CC_003: runner levanta `FileNotFoundError` → `ProviderTransportError` com mensagem citando instalação do Claude Code; returncode 1 com stderr "not logged in" → mensagem preserva o stderr truncado; timeout → retry 1x → sucesso na 2ª; duas falhas → erro.
4. CC_005: request com `temperature=0.7` → nenhum parâmetro de temperatura no argv; `supports_temperature=False`; report do meter com `temperature: null` + note, válido contra o schema atualizado.
5. CC_006–008: CLI fim-a-fim com providers fake → exit 0, report válido em `--out`; `--out` dentro do bundle → erro; bundle hash-idêntico; `--expected` com blueprint → aborta orientando.
6. Invariante: nenhum teste invoca o binário real (grep por `subprocess` fora do default runner; runner fake em todos os testes).

## Restrições arquiteturais

Herdar as padrão + exceção da fase: execução real somente em produção via runner default; testes 100% offline. Zero dependência nova (stdlib subprocess). Sem credenciais no repo em qualquer forma. `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `CC_001`–`CC_008` implementadas e cobertas
- [ ] Confinamento provado por teste (caso 1) — é a materialização do protocolo cego em produção
- [ ] CLI fim-a-fim verde com fakes; bundle imutável provado por hash
- [ ] pytest tests/ -q sem regressão; ruff limpo; CI verde
- [ ] impacto documental resolvido

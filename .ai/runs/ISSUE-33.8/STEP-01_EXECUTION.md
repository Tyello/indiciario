# STEP-01 — Leitura (ISSUE-33.8)

Status: done | Owner: orquestrador | Type: reading | Review: auto-approve

## Lido

- `.ai/issues/ISSUE-33.8_SPEC.md`
- `generator/llm_provider.py` (contrato `LLMProvider`, `ProviderRequest/Response`, `ProviderTransportError/ProviderResponseError`, `validate_provider_request`)
- `generator/anthropic_provider.py` + `generator/solvability_cli.py` (implementação anterior, pré-pivot, ainda no working tree, não commitada — serve de esqueleto para a versão headless: `_looks_like_blueprint`/CC_008, `_validate_out_path`/CC_007, `_build_default_transport` pattern → equivalente a runner default)
- `generator/solvability_meter.py` (bloco `reproducibility` construído em `measure_solvability`, linhas ~208-224; hoje sempre grava `temperature: <valor>`)
- `schemas/solvability_report.schema.yaml` (bloco `reproducibility`, `additionalProperties: false`)
- `examples/caso_canonico_iniciante.json` (campos de blueprint completo: `verdade_real`, `matriz_pistas`, `documentos`, `personagens`, `titulo`, `contratos_evidencia` — já usados como assinatura em `_BLUEPRINT_SIGNATURE_KEYS` da versão anterior; reaproveitar para CC_008)

## `claude --help` — achados

Comando rodado: `claude --help` (só help, nenhuma execução de prompt real).

- **CC_001 (tools off):** flag real é `--tools <tools...>`. Uso: `"" ` desabilita todas ("Use \"\" to disable all tools, \"default\" to use all tools, or specify tool names"). Não existe `--disallowedTools` como flag separada nesta versão — existe `--allowedTools`/`--allowed-tools` (allowlist), mas para confinamento total usamos `--tools ""`.
  **Decisão fixada:** argv contém `["--tools", ""]`.
- **CC_004 (prompt via stdin):** `Usage: claude [options] [command] [prompt]` — `prompt` é argumento posicional opcional. Quando omitido e stdin não é TTY, o padrão documentado do Claude Code é ler o prompt de stdin em modo `-p`. **Decisão:** não passar prompt como argv (evita vazar o bundle em `ps`/listagem de processos); enviar via `stdin_text` do runner.
- **CC_004 (canal system):** achado importante — **existe canal system dedicado**: flag `--system-prompt <prompt>`. Isso corrige a premissa da SPEC ("headless não tem canal system dedicado"). **Decisão atualizada (substitui a redação original de CC_004):** usar `--system-prompt <system>` como argv separado em vez de concatenar system+prompt no stdin. Mais honesto e mais simples. `ProviderRequest.system`, quando presente, vira `--system-prompt <texto>` no argv; quando ausente, a flag não é incluída.
- **Model:** `--model <model>` aceita alias (`opus`, `sonnet`, `fable`) ou nome completo. Confirma `model_id: str = "opus"` do contrato.
- **Output format:** `--output-format text` é o default, mas será passado explicitamente por clareza/estabilidade (`--print`/`-p` + `--output-format text`).
- Nenhuma flag de temperatura exposta no `--help` (confirma CC_005: headless não expõe controle de temperatura).

## Campos característicos de blueprint (CC_008)

Reaproveitados de `_BLUEPRINT_SIGNATURE_KEYS` (versão anterior, `generator/solvability_cli.py`):
`titulo`, `documentos`, `personagens`, `verdade_real`, `contratos_evidencia`, `matriz_pistas`. Guard: `dict` com 2+ dessas chaves → blueprint completo → abortar (CC_008).

## Decisões fixadas para STEP-02+ (atualizam a SPEC)

1. Argv base do provider: `["claude", "-p", "--model", <model_id>, "--output-format", "text", "--tools", ""]`, mais `["--system-prompt", <system>]` se `request.system` for fornecido. Prompt vai por stdin, nunca por argv.
2. `cwd`: diretório temporário vazio criado por chamada (`tempfile.mkdtemp()`), removido após a chamada (sucesso ou erro) — nunca o repo, nunca o bundle.
3. `CompletedRun` (dataclass local): `stdout: str`, `stderr: str`, `returncode: int`.
4. Runner default usa `subprocess.run(argv, input=stdin_text, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)`.
5. `supports_temperature = False` (atributo de classe em `ClaudeCodeProvider`); `ProviderRequest.temperature` nunca vira argv.
6. `measure_solvability`: ao montar `reproducibility`, checar `getattr(provider, "supports_temperature", True)`; se `False` → `temperature: None` + `temperature_note: "provider-controlled"`; caso contrário, comportamento atual (sem a chave `temperature_note`).
7. Schema `reproducibility.temperature`: `type: ["number", "null"]` (mantém min/max para o caso number); nova propriedade opcional `temperature_note` (`type: string`, não em `required`).

Estas decisões substituem a redação original de CC_004 (canal system) na SPEC — atualizada abaixo.

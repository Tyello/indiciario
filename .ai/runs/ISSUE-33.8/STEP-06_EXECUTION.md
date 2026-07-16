# STEP-06 EXECUTION — Smoke real (HUMANO) ISSUE-33.8

**Data**: 2026-07-16
**Status**: Concluído
**Owner**: Marcelo (ação humana, conforme CLAUDE.md — agentes de IA não executam este CLI contra a API real por conta própria)

---

## Step A — Sanidade do binário headless

Executado pelo operador humano diretamente:

```bash
claude -p "responda apenas OK" --model sonnet --output-format text --tools ""
```

Resultado: `OK` (stdout limpo, sem erro).

## Step B em diante — Smoke fim-a-fim via `solvability_cli`

Bundle disponível: `BUNDLE_SMOKE_001` (fixture disponível, não canônica; construída em
`scratchpad/build_smoke_bundle.py`, fora do repo). Comando alvo:

```bash
py -m generator.solvability_cli --bundle <BUNDLE_SMOKE_001> --expected <expected_smoke.json> \
  --runs 3 --solver-model sonnet --judge-model sonnet --out <report.json>
```

Três tentativas reais expuseram três defeitos reais, cada um investigado e resolvido (ou
tratado por decisão explícita do usuário via AskUserQuestion) antes de prosseguir:

### Bug 1 — Windows PATHEXT `FileNotFoundError` (in-scope, `claude_code_provider.py`)

`subprocess.run(["claude", ...])` sem `shell=True` não resolve `claude.CMD` (shim npm) via
PATHEXT no Windows — só o shell faz essa resolução. `ClaudeCodeProvider` recebia
`FileNotFoundError` e mapeava para `ProviderTransportError` (CC_003), mesmo com o binário
instalado. **Fix**: `shutil.which(argv[0]) or argv[0]` no runner default
(`generator/claude_code_provider.py`), mantendo o fallback textual `"claude"` para que um
binário genuinamente ausente ainda dispare CC_003.

### Bug 2 — JSON com fence markdown não parseado (fora do escopo 33.8, aprovado pelo usuário)

Respostas reais de modelo vêm envolvidas em ` ```json ... ``` `, mas
`generator/llm_blind_solver.py` e `generator/conclusion_judge.py` faziam
`json.loads(response.text)` cru, falhando com `Expecting value: line 1 column 1` e
degradando silenciosamente para `SolvabilityMeterError: all N runs failed`. **Fix**:
helper `_strip_markdown_fence()` (regex) adicionado independentemente aos dois arquivos,
aplicado antes de cada `json.loads()`. Usuário aprovou corrigir via AskUserQuestion
("Corrigir agora (fora do escopo 33.8)").

### Bug 3 — `UnicodeEncodeError` no stdin do subprocess (in-scope, `claude_code_provider.py`)

`subprocess.run(..., text=True)` sem `encoding=` explícito usa a codificação padrão do
console Windows (cp1252), que não cobre todo o alfabeto usado em respostas/prompts reais
em português (ex.: caractere fora do cp1252 no prompt do judge). Isso derrubava a chamada
com `UnicodeEncodeError`, mapeado para `ProviderTransportError` genérico. **Fix**:
`encoding="utf-8"` explícito no `subprocess.run()` do runner default.

### Achado 4 — Judge aceita só 4 valores de `classification`, fora do repair-loop (registrado, não corrigido)

Modelo real respondeu `classification: "inconclusivo"` (fora do enum
`resolvido|nao_resolvido|vazamento|ambiguo`); `_validate_verdict_schema` falha e essa
falha NÃO entra no `_call_provider_with_repair` (que só repara erro de parse JSON, não
falha de schema pós-parse). Decisão do usuário: **não mexer em `conclusion_judge.py`**
agora — trocar a fixture de smoke por um caso com evidência suficiente para veredito
inequívoco (cofre roubado, testemunho de dois suspeitos, câmera confirmando um deles).
Registrado aqui como achado de robustez pré-existente do módulo `conclusion_judge.py`,
exposto apenas por modelo real (stub/fake provider nunca produz esse valor). Não é bloqueio
de ISSUE-33.8; candidato a issue própria se o padrão se repetir em uso real.

### Bug 5 — RV_004 sistemático: `confidence=high` + `open_questions` não vazio (fora do escopo 33.8, aprovado pelo usuário)

Mesmo com fixture reforçada, 3/3 runs reais falharam em
`generator/llm_blind_solver.py::solve()` na validação final
(`generator/blind_solver_report_validator.py`, regra RV_004): modelos reais tendem a manter
uma pergunta residual mesmo quando confiantes. Não era variância de amostragem — era
sistemático porque `generator/prompts/blind_solver_v1.md` nunca instruía o modelo sobre
essa regra (só haveria descoberta com provider real, nunca com fake/stub). Usuário aprovou
corrigir a causa raiz: adicionada regra 6 ao prompt ("Coerência entre confidence e
open_questions" — `confidence: "high"` exige `open_questions` vazio). Hash SHA256 do
template mudou; nenhum teste depende do hash literal (todos recalculam via leitura do
arquivo), então nenhuma regressão de teste.

---

## Resultado final do smoke real

Após os 5 fixes/achados acima, o comando completo rodou com sucesso:

```
meter_id: METER_1784237823847
bundle_id: BUNDLE_SMOKE_001
runs: 3/3
solve_rate: 1.00
difficulty_estimate: facil
flags: (nenhuma)
report gravado em: <scratchpad>/smoke/report.json
```

`report.json` confirma: `provider_id: "claude-code"`, `temperature: null` com
`temperature_note: "provider-controlled"` (CC_005 refletido corretamente no relatório),
hashes reais de prompt (solver e judge) presentes no bloco `reproducibility`.

## Validação de não regressão

```bash
pytest tests/ -q
```
✓ **1552 passed, 8 skipped in 225.57s**

```bash
ruff check generator/ scripts/ tests/
```
✓ **All checks passed!**

## Arquivos alterados nesta etapa

| Arquivo | Mudança |
|---|---|
| `generator/claude_code_provider.py` | `shutil.which` (Bug 1, já do STEP-05/06) + `encoding="utf-8"` no `subprocess.run` (Bug 3) |
| `generator/llm_blind_solver.py` | `_strip_markdown_fence()` antes do `json.loads()` (Bug 2) |
| `generator/conclusion_judge.py` | `_strip_markdown_fence()` antes do `json.loads()` (Bug 2) |
| `generator/prompts/blind_solver_v1.md` | regra 6 — coerência confidence/open_questions (Bug 5) |
| `.ai/runs/ISSUE-33.8/STEP-06_EXECUTION.md` | criado (este documento) |

Nenhum arquivo de fixture do smoke (`scratchpad/build_smoke_bundle.py`,
`scratchpad/expected_smoke.json`) faz parte do repositório — são descartáveis, fora do
escopo de versionamento desta issue.

## Próximo passo

→ STEP-07: DOCS

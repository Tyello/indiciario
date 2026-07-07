# Review Report — ISSUE-40.2 STEP-04

STEP: STEP-04
STEP_TYPE: validation
REVIEW_VERDICT: aprovado
SEVERIDADE: none (nota informativa registrada, não bloqueia)

## Contrato revisado

Seção "### STEP-04 — Verificação de regressão" da issue:
- Confirmar os dois testes do STEP-02 no estado esperado pós-GREEN.
- Rodar suíte completa e confirmar ausência de regressão.
- Confirmar critério de aceite #3 (remover `@font-face` → gate falha; restaurar → gate passa).
- Arquivos editáveis permitidos: só `tests/test_gate_font_fidelity.py` (ajuste pequeno de docstring/histórico).
- Proibido: alterar comportamento do check implementado no STEP-03.

## Verificação de escopo (git status/diff)

`git status --porcelain` no fim da execução mostra exatamente:
- `.ai/issues/ISSUE-40.2.md` (controle)
- `generator/canonical_quality_gate.py` (de STEP-03/03_FIX-01, não deste step)
- `tests/test_font_vendoring.py` (de STEP-01, não deste step)
- `.ai/runs/ISSUE-40.2/` (relatórios)
- `generator/font_fidelity.py` (novo, de STEP-01/03)
- `tests/test_gate_font_fidelity.py` (novo, de STEP-02/03/03_FIX-01, ajuste de docstring neste step)

Nenhum arquivo de `tests/test_blind_bundle_generator.py`, `tests/test_blind_bundle_leak_checker.py`,
`tests/test_blind_bundle_sanitizer.py` ou `generator/pipeline_runner.py` foi tocado por este step ou
por qualquer step anterior desta issue. Confirma a alegação do executor de que as falhas de symlink
são alheias ao escopo.

## Re-execução dos comandos

1. `pytest tests/test_gate_font_fidelity.py -q` → `3 passed in 2.25s`. Confirmado.
2. `pytest tests/ -q` (rodada completa) → **`6 failed, 1387 passed, 3 skipped`**, não `5 failed, 1388 passed`
   como relatado pelo executor. Divergência investigada abaixo.

### Falhas de symlink (5) — confirmadas pré-existentes

As mesmas 5 falhas reportadas pelo executor (`test_blind_bundle_generator::test_symlink_source_is_rejected_and_not_followed`,
3 em `test_blind_bundle_leak_checker`, 1 em `test_blind_bundle_sanitizer`) batem exatamente com a memória de
ambiente registrada 22 dias atrás (`test-environment.md`), todas por `OSError: [WinError 1314]` ao chamar
`Path.symlink_to(...)` — falta de privilégio de symlink no Windows local, nada relacionado a font/gate.
Causa raiz confirmada, não é regressão desta issue.

### Falha extra (6ª, não reportada pelo executor) — investigada e também não é regressão

`tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at` falhou na minha
rodada mas não apareceu no relatório do executor. Investigação:
- Isolado, o teste é flaky por si só: reexecutado 3x seguidas dá `passed`, `failed`, `failed` (hash sha256
  do artifact `evidence_review` muda entre execuções mesmo com `created_at` fixo).
- `git stash` (removendo todas as mudanças desta issue, voltando à `main` limpa) + reexecução 3x: mesmo
  padrão (`passed`, `failed`, `failed`). Confirma que a flakiness existe independente de qualquer mudança
  de ISSUE-40.2 — não é regressão introduzida por STEP-01..STEP-04.
- `generator/pipeline_runner.py` não foi tocado por nenhum step desta issue (confirmado no git status/diff
  acima), consistente com a causa ser alheia ao escopo.
- Não é a mesma causa raiz do symlink (não é `OSError`, é não-determinismo real de hash em stage
  `evidence_review`), mas é igualmente pré-existente e fora do escopo de font/gate.

Conclusão: a alegação central do executor ("sem regressão introduzida por esta issue") se sustenta, mas o
relatório de STEP-04 estava incompleto — não mencionou este teste flaky porque não o encontrou na sua
própria rodada (execução não-determinística bate diferente a cada vez). Não bloqueia a aprovação porque a
causa raiz está fora do escopo tocado por esta issue e foi confirmada empiricamente (stash test). Registro
aqui para memória futura: `test_run_pipeline_is_deterministic_with_same_created_at` é flaky na `main`,
alheio a font/gate, candidato a issue de higiene de testes separada — não desta issue.

3. Reexecução de `pytest tests/test_gate_font_fidelity.py -q` após ajuste de docstring → `3 passed in 2.33s`.
   Confirmado.

## Critério de aceite #3

Li `tests/test_gate_font_fidelity.py` e `generator/font_fidelity.py` na íntegra. Confirmo:
- **Remoção → falha**: `test_gate_catches_font_fallback` usa `evaluate_font_fidelity(templates=["01_email.html"], browser=browser)`
  sobre a fixture `css_com_fonte_removida` (bloco `@font-face` de `'DM Sans'` removido via regex de cópia real
  do CSS, `monkeypatch` no `DOCUMENT_SYSTEM_CSS_PATH`). Resultado: `criterio.status == "blocker"`,
  `criterio.recommendation` contém `"01_email.html"` e `"DM Sans"` — nomeia template+fonte, não é boolean
  agregado (satisfaz também critério de aceite #2). `test_gate_wires_font_fidelity_into_evaluate_for_canonical`
  estende isso ao veredito real do gate: `qualification.qualification == CuratorQualification.NOT_READY`.
- **Restauração → passa**: o `monkeypatch` da fixture (scope `function`) é revertido automaticamente pelo
  pytest ao fim de cada teste, restaurando `DOCUMENT_SYSTEM_CSS_PATH` para o CSS real intacto. Sobre o CSS
  real, `tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema` (parametrizado,
  cobre o par `01_email.html`/`DM Sans`) confirma `fonte_aplicada is True` via a mesma técnica
  (`canvas.measureText`) usada por `evaluate_font_fidelity` — logo, sobre o CSS real, o mesmo par não
  entraria em `fallbacks` e o critério retornaria `status="ok"`. Este teste roda dentro da suíte completa
  (item 2 acima) sem o `@font-face` removido, provando o lado "restaurado → passa" com a mesma
  montagem/técnica. Aceito o argumento do executor: não é round-trip literal no mesmo teste, mas é
  equivalente em rigor (mesma técnica de medição, mesmo par template+fonte, CSS real vs. CSS mutilado) e
  não é tautológico.

Confirmo o critério de aceite #3 como satisfeito.

## Verificação de wiring (STEP-03_FIX-01)

Confirmado em `generator/canonical_quality_gate.py`: `evaluate_font_fidelity` (linha 131) e
`evaluate_for_canonical` (linha 256) com parâmetro opcional `font_fidelity_criterion` (linha 261),
anexado a `criteria_results` quando fornecido (linhas 372-373). Bate com o relatado.

## Escopo do ajuste de docstring

Único arquivo alterado neste step foi `tests/test_gate_font_fidelity.py`, só a docstring de
`test_gate_currently_misses_font_fallback` (linhas 90-104) — nenhum assert alterado, comportamento do
check intocado. Dentro do permitido pelo contrato do STEP-04.

## Veredito

Aprovado. A alegação central do executor (falhas de symlink pré-existentes, alheias a font/gate) está
confirmada por evidência direta (git status + traceback + memória de ambiente). A divergência encontrada
(6ª falha, flaky, também pré-existente e alheia ao escopo, confirmada via `git stash` em `main` limpa) não
muda o veredito de "sem regressão introduzida por esta issue", mas deveria ter sido capturada e reportada
pelo executor — reprovar por isso seria desproporcional dado que a causa raiz está fora do escopo e a
conclusão final é a mesma. Registrado como nota para housekeeping futuro (teste flaky em
`test_pipeline_runner.py`), não como blocker desta issue.

Avançando para STEP-05.

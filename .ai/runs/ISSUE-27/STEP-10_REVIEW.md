# Review Report — ISSUE-27 STEP-10

STEP: STEP-10
STEP_TYPE: red
REVIEW_STATUS: rejected
SEVERITY: minor

## Arquivos esperados
- tests/test_run_manifest.py (casos 46–55 adicionados)

## Arquivos alterados encontrados
- tests/test_run_manifest.py (untracked; via git status --short)
- .ai/issues/ISSUE-27.md (controle de estado; permitido)

Nota: arquivos untracked (generator/run_manifest.py, schemas/run_manifest.schema.yaml,
tests/fixtures/run_manifest/, tests/test_run_manifest_schema.py) sao de steps
anteriores ja aprovados; git diff nao mostra conteudo untracked. Verificacao por
leitura direta + grep.

## Verificacoes
- [x] Execution report existe
- [x] Type valido (red)
- [x] Apenas tests/test_run_manifest.py alterado no escopo do step
- [x] NENHUMA alteracao em generator/run_manifest.py (grep "def build_run_manifest" = sem match)
- [x] build_run_manifest NAO implementado; sem GREEN
- [x] Testes falham por funcao ausente (ImportError build_run_manifest na coleta, linha 23)
- [x] Casos 46–49 cobrem findings_by_artifact vazio, source_type narrative_review,
      source_type evidence_review, nao-mutacao (copy.deepcopy + assert)
- [x] Casos 54–55 cobrem validate_run_manifest e round-trip manifest_to_dict
- [ ] Casos 50–53 (next_steps) alinhados com a tabela de derivacao da spec
- [x] Nada fora da allowlist

## Divergencias

### DVG-001 — next_steps com asserts de igualdade exata em strings ASCII-folded divergem da spec
Severidade: minor
Esperado:
- Tabela de derivacao de next_steps na spec (ISSUE-27_SPEC.md, linhas ~258–266) usa
  texto acentuado:
  - linha 263: "Ingerir blind_solver_report para avancar..." -> spec: "avançar"
  - linha 264: "Ingerir gate_evaluation para avancar..." -> spec: "avançar"
  - linha 261: "...registrar decisão de rollback ou desbloqueio." -> spec: "decisão"
- RED deve travar GREEN no texto da spec (acentuado) OU usar assert por substring/keyword,
  para que GREEN (STEP-11) possa emitir o texto exato da tabela.

Encontrado:
- Casos usam `assert next_steps == [...]` (igualdade exata) com strings ASCII-folded:
  - Caso 51 (linha 905): "Ingerir blind_solver_report para avancar para gate_evaluation."
  - Caso 52 (linha 927): "Ingerir gate_evaluation para avancar para narrative_review."
  - Caso 53 (linhas 954–955): "...registrar decisao de rollback ou desbloqueio."
- Igualdade exata + folding forca GREEN a emitir next_steps SEM acento ("avancar",
  "decisao"), divergindo da tabela acentuada da spec.
- Caso 50 (linha 888–890) NAO diverge: a linha da spec (260) ja e sem acentos
  ("Pipeline completo. Revisar findings e prosseguir para ISSUE-28."); aceitavel.

Correcao exigida:
- Em tests/test_run_manifest.py, casos 51, 52, 53: alinhar os asserts ao texto exato
  da tabela da spec (com acento: "avançar", "decisão") OU trocar igualdade exata por
  asserts de substring/keyword (ex.: `assert "blind_solver_report" in next_steps[0]`)
  para que GREEN possa emitir o texto acentuado da spec sem divergencia.
- Caso 50 pode permanecer como esta (ja casa com a spec).
- Nenhuma alteracao em generator/run_manifest.py. Manter RED (sem GREEN).

Arquivos autorizados: tests/test_run_manifest.py
Comandos autorizados: pytest tests/test_run_manifest.py -q

## Decisao
REJECTED

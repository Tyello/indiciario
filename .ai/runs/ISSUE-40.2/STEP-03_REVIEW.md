# Review Report — ISSUE-40.2 STEP-03

STEP: STEP-03
STEP_TYPE: green
REVIEW_STATUS: rejected
SEVERITY: major

## Arquivos esperados

- generator/canonical_quality_gate.py (ponto de integração decidido no STEP-01)
- módulo novo para helper extraído (STEP-01 recomendou `generator/font_fidelity.py`)
- tests/test_font_vendoring.py (só se extrair helper, sem mudar asserts)

## Arquivos alterados encontrados (`git diff --name-only` + untracked)

- generator/canonical_quality_gate.py (M)
- generator/font_fidelity.py (novo)
- tests/test_font_vendoring.py (M)
- tests/test_gate_font_fidelity.py (novo, herdado do STEP-02)
- .ai/issues/ISSUE-40.2.md (M, controle)

Dentro do escopo de arquivos editáveis do STEP-03. Sem vazamento de escopo de arquivo.

## Comandos re-executados nesta revisão

- `pytest tests/test_gate_font_fidelity.py -q` → `2 passed in 1.76s`. Confirma o relatado.
- `ruff check generator/` → `All checks passed!`. Confirma o relatado.

## Verificações

- [x] Execution report existe
- [x] Type válido (green)
- [x] Arquivos alterados dentro da allowlist do STEP-03
- [x] Comandos executados dentro do permitido
- [x] `test_gate_catches_font_fallback` passa (Done quando, item 1)
- [x] ruff limpo (Done quando, item 2)
- [x] Check nomeia template+fonte na falha (`recommendation` lista pares, não booleano — critério de aceite #2 da issue)
- [x] Nenhum outro check visual implementado (camada, brand leakage, microidentidade) — escopo de checks não vazou
- [ ] **Ponto de integração implementado conforme decidido no STEP-01**

## Divergências

### DVG-001 — `evaluate_font_fidelity` não integrado ao gate real; contraria a própria decisão do STEP-01 e deixa o critério de aceite #1 da issue não cumprido

Severidade: major

Esperado: STEP-01_EXECUTION.md não apresentou a injeção via parâmetro opcional
como uma possibilidade entre outras — apresentou como a resolução da "tensão
de design" registrada: "Recomendação: função nova e independente
`evaluate_font_fidelity(...) -> QualificationCriterion` dentro de
`canonical_quality_gate.py`, **injetada via parâmetro opcional em
`evaluate_for_canonical`**". O objetivo do STEP-03 é explícito: "Implementar
o check de fidelidade de fonte no ponto de integração decidido no STEP-01" —
o ponto decidido incluía a injeção, não só a existência da função isolada.
Isso não é escopo novo (checks visuais adicionais); é completar o ponto de
integração já decidido.

Encontrado: `evaluate_font_fidelity` existe em
`generator/canonical_quality_gate.py`, mas não é chamada por
`evaluate_for_canonical`, nem por `pipeline_runner.py`, nem por nenhum
consumidor real do gate. `evaluate_for_canonical` continua sem
`"font_fidelity"` em `criteria_results` — o próprio
`test_gate_currently_misses_font_fallback` (STEP-02) continua passando
inalterado, contradizendo a expectativa registrada no relatório do STEP-02
("`test_gate_currently_misses_font_fallback` ficará sem sentido depois do
STEP-03 ... o STEP-04 já prevê essa revisão/remoção"). A trajetória
planejada pelos próprios executores anteriores previa que, após o STEP-03,
o gate real passaria a enxergar `font_fidelity`. Isso não aconteceu.

Contra o critério de aceite #1 da issue: "O pipeline de qualidade
(`canonical_quality_gate.py` ou equivalente) falha explicitamente se
qualquer template renderizado usa uma fonte cujo `font-family` computado
não bate com a família declarada." Uma função nunca chamada por nada que
rode no pipeline real não cumpre isso — ninguém vê o gate falhar em uso
normal (`evaluate_for_canonical`, que é o que `pipeline_runner.py` e
`quality_comparative_reviewer.py` de fato consultam). É função morta do
ponto de vista do critério de aceite, ainda que testável isoladamente.

Correção exigida: em STEP-03_FIX-01, conectar `evaluate_font_fidelity` a
`evaluate_for_canonical` pelo mecanismo já decidido no STEP-01 (parâmetro
opcional, ex. `font_fidelity_criterion: QualificationCriterion | None =
None`, apppend a `criteria_results` quando fornecido) — preserva as
chamadas existentes em `tests/test_canonical_quality_gate.py` sem esse
argumento, como o próprio STEP-01 antecipou. Revisar/atualizar
`test_gate_currently_misses_font_fallback` conforme a trajetória já prevista
no STEP-02/STEP-04 (documentar ou remover, já que o comportamento que ele
evidencia deixa de ser verdade quando o parâmetro é passado).

Arquivos autorizados: generator/canonical_quality_gate.py,
tests/test_gate_font_fidelity.py (ajuste do teste 1 se necessário para
refletir a integração)

Comandos autorizados: pytest tests/test_gate_font_fidelity.py -q,
ruff check generator/

## Decisão

REJECTED

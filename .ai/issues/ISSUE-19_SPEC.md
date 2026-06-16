# ISSUE-19+20_SPEC — Gate Evaluator (schema + harness)

## Identificação

- **Issues:** ISSUE-19 + ISSUE-20 (agrupadas em uma PR)
- **Título:** Gate Evaluator — schema de avaliação + harness de avaliação privada
- **Fase:** D
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-gate-evaluator`
- **Título sugerido da PR:** `feat: add gate evaluator schema and harness`
- **Commit sugerido:** `feat: add gate evaluator schema and harness`

## Decisão de agrupamento

ISSUE-19 (schema) e ISSUE-20 (harness) são entregues juntas porque:

1. O schema `gate_evaluation.schema.yaml` só pode ser validado contra fixtures reais
   ao existir o harness que o produz.
2. O harness sem o schema é uma implementação sem contrato verificável.
3. O agrupamento foi aprovado na nota de handoff (junho/2026).

A separação entre `schemas/` e `generator/` é mantida internamente; são apenas
entregues na mesma PR.

---

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py` + `schemas/blind_solver_report.schema.yaml`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py` (RV_001–RV_008)
- ✅ ISSUE-18: `schemas/blind_solve_run_record.schema.yaml` + `generator/blind_solve_run_record.py`

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia `.ai/skills/diagnose.md`.
7. Leia integralmente:
   - `generator/blind_solver_harness.py`
   - `generator/blind_solve_run_record.py`
   - `generator/blind_solver_report_validator.py`
   - `schemas/blind_solve_run_record.schema.yaml`
   - `schemas/blind_solver_report.schema.yaml`
   - `schemas/blind_bundle_manifest.schema.yaml`
   - `tests/test_blind_solve_run_record.py`
   - `tests/test_blind_solve_run_record_schema.py`
   - `tests/test_blind_solver_harness.py`
   - `docs/BLIND_SOLVER_HARNESS.md`
   - `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`
   - `docs/BLIND_CONTEXT_PROTOCOL.md`
   - `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` (seções ISSUE-19 e ISSUE-20)
8. Execute antes de alterar:
   ```bash
   pytest tests/test_blind_solve_run_record.py -q
   pytest tests/test_blind_solve_run_record_schema.py -q
   pytest tests/ -q
   ```

---

## Objetivo

Criar o **Gate Evaluator**: o único componente autorizado a comparar uma solução
cega congelada com a solução privada do autor, e emitir uma decisão formal de
aprovação, rejeição ou rollback.

O Gate Evaluator:

- recebe um `BlindSolveRunRecord` já produzido e congelado (ISSUE-18);
- recebe acesso explícito à **solução privada** do caso (autor-only, fora do bundle);
- compara conclusão, evidências e confiança do solver contra as expectativas do autor;
- emite uma `GateEvaluation` estruturada com decisão, justificativa, lacunas e
  hipóteses inesperadas válidas;
- **nunca** modifica o run record, o bundle ou qualquer artefato existente;
- **nunca** chama LLM, nunca acessa rede;
- **nunca** é executado pelo solver (sem autocertificação).

O Gate Evaluator é o **único ponto** onde conteúdo privado do autor (solução,
gabarito) entra em contato com o output cego do solver. Todo o resto do pipeline
opera sem esse contato.

---

## Modelo conceitual

### gate_evaluation.schema.yaml

```yaml
schema_version: "1.0"
evaluation_id: "GE-aurora-20260616-001"       # neutral_id
run_id: "RUN-aurora-20260615-001"              # referência ao run record
bundle_id: "BUNDLE-aurora-v1"                 # confirma o bundle avaliado
evaluator_id: "human-marcelo"                 # quem avaliou
created_at: "2026-06-16T14:00:00Z"
created_by: "orchestrator"

private_solution_ref: "examples/caso_canonico_intermediario.json"
# caminho para a solução privada usada na avaliação; fora do bundle

decision: "approved"
# enum: approved | rejected | rollback

justification: "Solver identificou culpado e mecanismo corretamente..."
# >= 10 chars; obrigatório sempre

expected_conclusions:
  - id: "EC-01"
    description: "Identificar Marta como culpada"
    required: true
    met: true
    evidence: "conclusion contém 'Marta'"
  - id: "EC-02"
    description: "Identificar envenenamento como mecanismo"
    required: true
    met: true
    evidence: "evidence_used contém laudo_medico"

unexpected_valid_hypotheses: []
# hipóteses que o solver levantou, não estavam nas expected_conclusions,
# mas são válidas segundo o autor; indica riqueza investigativa

gaps:
  - id: "GAP-01"
    description: "Solver não identificou motivo financeiro"
    required_conclusion_id: null  # pode ser null
    severity: "minor"             # enum: critical | major | minor
    impact: "Não bloqueia aprovação neste caso"
# lacunas entre o que era esperado e o que foi concluído

leak_detected: false
# true se o avaliador identificou evidência de que o solver acessou
# conteúdo privado (gabarito vazou para o bundle)

rollback_target: null
# preenchido apenas se decision = "rollback"
# indica a etapa para qual o pipeline deve retroceder
# enum: bundle_preparation | blind_solve | gate_evaluation | null

confidence_assessment:
  solver_confidence: "medium"      # espelhado do report
  evaluator_agreement: "agree"     # enum: agree | disagree | partial
  notes: ""

notes: ""
```

---

## Campos obrigatórios do schema

| Campo | Tipo | Regra |
|---|---|---|
| `schema_version` | const `"1.0"` | Imutável nesta versão |
| `evaluation_id` | neutral_id | Único para esta avaliação |
| `run_id` | neutral_id | Liga ao `blind_solve_run_record` |
| `bundle_id` | neutral_id | Confirma qual bundle foi avaliado |
| `evaluator_id` | string ≥ 2 chars | Quem avaliou |
| `created_at` | date-time | ISO 8601 com timezone |
| `created_by` | string ≥ 1 char | Orchestrator, humano etc. |
| `private_solution_ref` | string ≥ 1 char | Caminho da solução privada |
| `decision` | enum | `approved` / `rejected` / `rollback` |
| `justification` | string ≥ 10 chars | Sempre obrigatória |
| `expected_conclusions` | array | ≥ 0 itens; cada item é um objeto |
| `unexpected_valid_hypotheses` | array | ≥ 0 itens |
| `gaps` | array | ≥ 0 itens |
| `leak_detected` | boolean | Obrigatório |
| `rollback_target` | string \| null | Obrigatório quando `decision = rollback` |
| `confidence_assessment` | object | Sempre obrigatório |
| `notes` | string | Pode ser vazio |

### expected_conclusions — cada item

| Campo | Tipo | Regra |
|---|---|---|
| `id` | string ≥ 1 | Identificador único dentro da avaliação |
| `description` | string ≥ 1 | O que era esperado |
| `required` | boolean | Crítico para aprovação? |
| `met` | boolean | O solver atendeu? |
| `evidence` | string | Como foi determinado; pode ser vazio |

### gaps — cada item

| Campo | Tipo | Regra |
|---|---|---|
| `id` | string ≥ 1 | Identificador único dentro da avaliação |
| `description` | string ≥ 1 | O que está faltando |
| `required_conclusion_id` | string \| null | Referência a expected_conclusions[].id |
| `severity` | enum | `critical` / `major` / `minor` |
| `impact` | string | Consequência; pode ser vazio |

### confidence_assessment — campos obrigatórios

| Campo | Tipo | Regra |
|---|---|---|
| `solver_confidence` | enum | `low` / `medium` / `high` (espelhado do report) |
| `evaluator_agreement` | enum | `agree` / `disagree` / `partial` |
| `notes` | string | Pode ser vazio |

---

## Regras semânticas (validação além do schema JSON)

O harness deve aplicar estas regras APÓS validação estrutural:

| Código | Campo | Regra |
|---|---|---|
| GE_001 | `rollback_target` | Se `decision = rollback`, `rollback_target` não pode ser null |
| GE_002 | `rollback_target` | Se `decision != rollback`, `rollback_target` deve ser null |
| GE_003 | `leak_detected` | Se `leak_detected = true`, `decision` NÃO pode ser `approved` |
| GE_004 | `expected_conclusions` | Se `decision = approved`, todas as `required = true` devem ter `met = true` |
| GE_005 | `expected_conclusions` | Se existir alguma `required = true` com `met = false`, `decision` não pode ser `approved` |
| GE_006 | `gaps` | Se existir gap com `severity = critical`, `decision` não pode ser `approved` |
| GE_007 | `confidence_assessment.solver_confidence` | Deve ser igual a `report.confidence` no run record |
| GE_008 | `run_id` | Deve referenciar um run record válido (verificado em runtime pelo harness) |

Regras GE_001–GE_006 são **bloqueantes** (errors).
Regra GE_007 é **aviso** (warning), não bloqueia.
Regra GE_008 é **bloqueante** em runtime; nos testes de schema, a referência é
estrutural apenas.

---

## API pública esperada

```python
# generator/gate_evaluator.py

@dataclass(frozen=True)
class ExpectedConclusion:
    id: str
    description: str
    required: bool
    met: bool
    evidence: str

@dataclass(frozen=True)
class GapItem:
    id: str
    description: str
    required_conclusion_id: str | None
    severity: str   # "critical" | "major" | "minor"
    impact: str

@dataclass(frozen=True)
class ConfidenceAssessment:
    solver_confidence: str   # "low" | "medium" | "high"
    evaluator_agreement: str # "agree" | "disagree" | "partial"
    notes: str

@dataclass(frozen=True)
class GateEvaluationRequest:
    run_record: Mapping[str, Any]        # BlindSolveRunRecord já construído
    private_solution_ref: str            # caminho para solução privada
    evaluator_id: str
    evaluation_id: str
    created_by: str = "orchestrator"
    created_at: str | None = None        # ISO 8601; se None usa timestamp real

@dataclass(frozen=True)
class GateEvaluationResult:
    evaluation: dict[str, Any]           # GateEvaluation serializada
    semantic_errors: tuple[str, ...]     # GE_001–GE_008 errors
    semantic_warnings: tuple[str, ...]   # GE_007 warnings
    valid: bool                          # True se sem semantic_errors


def validate_gate_evaluation(evaluation: Mapping[str, Any]) -> list[str]:
    """Valida estruturalmente contra gate_evaluation.schema.yaml.
    Retorna lista de erros (vazia = válido)."""
    ...


def validate_gate_evaluation_semantics(
    evaluation: Mapping[str, Any],
    run_record: Mapping[str, Any] | None = None,
) -> GateEvaluationResult:
    """Aplica regras GE_001–GE_008.
    run_record opcional: se fornecido, valida GE_007 e GE_008.
    Retorna GateEvaluationResult com errors/warnings e valid."""
    ...


def build_gate_evaluation(
    request: GateEvaluationRequest,
    expected_conclusions: list[ExpectedConclusion],
    unexpected_valid_hypotheses: list[str],
    gaps: list[GapItem],
    confidence_assessment: ConfidenceAssessment,
    decision: str,            # "approved" | "rejected" | "rollback"
    justification: str,
    leak_detected: bool = False,
    rollback_target: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Constrói uma GateEvaluation serializada pronta para validate_gate_evaluation.
    Não valida semântica — chame validate_gate_evaluation_semantics depois.
    Não muta os inputs."""
    ...
```

---

## Escopo permitido

Criar:
- `schemas/gate_evaluation.schema.yaml`
- `generator/gate_evaluator.py`
- `tests/test_gate_evaluation_schema.py`
- `tests/test_gate_evaluator.py`
- `tests/fixtures/gate_evaluation/valid/`
- `tests/fixtures/gate_evaluation/invalid/`

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — seção sobre Gate Evaluator (opcional)
- `schemas/blind_solve_run_record.schema.yaml` — **somente** para tipificar
  melhor o campo `gate_decision` (que já existe como `type: object | null`).
  Se alterar, rodar suíte completa antes e depois.

---

## Fora de escopo

**Não implementar:**
- Revisores (ISSUE-21+)
- Workspace / orquestrador manual (ISSUE-25+)
- Skill `blind-solve` ou `gate-evaluator` em `.ai/skills/`
- Execução automática de LLM
- Chamada de internet
- Alteração de casos canônicos
- Alterar `blind_solver_harness.py`
- Alterar `blind_solver_report_validator.py`
- Alterar `blind_solve_run_record.py`
- CLI complexa (não é P1 nesta issue)

---

## Testes obrigatórios

### `tests/test_gate_evaluation_schema.py` (schema — 20 casos)

Testes 1–10: fixtures válidas e estrutura

1. fixture `valid_approved.yaml` passa no schema
2. fixture `valid_rejected.yaml` passa no schema
3. fixture `valid_rollback.yaml` passa no schema (com `rollback_target` preenchido)
4. fixture `valid_no_gaps.yaml` passa (gaps: [])
5. fixture `valid_unexpected_hypotheses.yaml` passa (unexpected_valid_hypotheses preenchido)
6. `expected_conclusions` vazio é válido ([]  — nenhuma expectativa declarada)
7. `leak_detected: true` é válido no schema (sem restrição estrutural)
8. `confidence_assessment.evaluator_agreement: "partial"` é válido
9. `notes` vazio é válido (`notes: ""`)
10. `unexpected_valid_hypotheses` com strings é válido

Testes 11–20: rejeições estruturais

11. `schema_version` errada (`"2.0"`) falha
12. `decision` com valor inválido (`"pending"`) falha
13. `evaluation_id` ausente falha
14. `run_id` ausente falha
15. `justification` ausente falha
16. `rollback_target` com valor inválido (`"unknown_stage"`) falha (enum)
17. `expected_conclusions` item sem `id` falha
18. `gaps` item sem `severity` falha
19. `gaps` item com `severity` inválida (`"trivial"`) falha
20. campo extra no topo falha (`additionalProperties: false`)

### `tests/test_gate_evaluator.py` (semântica + builder — 30 casos)

Testes 21–30: regras semânticas GE_001–GE_008

21. `decision: rollback` sem `rollback_target` → GE_001 error
22. `decision: rollback` com `rollback_target` preenchido → sem GE_001
23. `decision: approved` com `rollback_target` preenchido → GE_002 error
24. `decision: approved` com `rollback_target: null` → sem GE_002
25. `leak_detected: true` + `decision: approved` → GE_003 error
26. `leak_detected: true` + `decision: rejected` → sem GE_003
27. `decision: approved` com `required=true` e `met=false` → GE_004 error
28. `decision: approved` com todos `required=true` e `met=true` → sem GE_004
29. `decision: approved` com gap `severity: critical` → GE_006 error
30. `decision: rejected` com gap `severity: critical` → sem GE_006

Testes 31–36: GE_007 / GE_008 (aviso + referência ao run record)

31. `solver_confidence` diverge de `report.confidence` no run record → GE_007 warning (não bloqueia)
32. `solver_confidence` igual a `report.confidence` → sem GE_007
33. run record fornecido com `run_id` matching → sem GE_008
34. run record fornecido com `run_id` diferente → GE_008 error
35. run record `None` fornecido → GE_007 e GE_008 ignorados (sem run_record, sem checagem)
36. `validate_gate_evaluation_semantics` retorna `valid=False` quando há errors, `valid=True` sem errors

Testes 37–50: `build_gate_evaluation` e integração

37. `build_gate_evaluation` retorna dict
38. dict retornado passa `validate_gate_evaluation`
39. `evaluation_id` do resultado bate com o `request.evaluation_id`
40. `run_id` do resultado bate com o `request.run_record["run_id"]`
41. `bundle_id` do resultado bate com o `request.run_record["bundle_id"]`
42. `decision: approved` com conclusões válidas + sem gaps críticos → sem errors semânticos
43. `decision: rejected` com conclusão faltando `required=true` → sem errors semânticos (rejected é consistente)
44. `decision: rollback` com `rollback_target: "blind_solve"` → sem errors semânticos
45. `build_gate_evaluation` não muta os inputs
46. `unexpected_valid_hypotheses` é preservado como lista no resultado
47. `gaps` é preservado como lista de objetos no resultado
48. `confidence_assessment` é preservado como objeto no resultado
49. `notes` vazio é preservado como string vazia
50. `pytest tests/ -q` passa sem regressão (990+ testes)

---

## Fixtures necessárias

### `tests/fixtures/gate_evaluation/valid/`

- `valid_approved.yaml` — decisão approved, todas required met, sem gaps críticos,
  leak_detected: false, rollback_target: null
- `valid_rejected.yaml` — decisão rejected, pelo menos uma required não met, gap major,
  rollback_target: null
- `valid_rollback.yaml` — decisão rollback, rollback_target: "bundle_preparation",
  justificativa de falha de segurança
- `valid_no_gaps.yaml` — gaps: [], unexpected_valid_hypotheses: [], decisão approved
- `valid_unexpected_hypotheses.yaml` — unexpected_valid_hypotheses preenchido,
  decisão approved

### `tests/fixtures/gate_evaluation/invalid/`

- `invalid_decision.yaml` — decision: "pending" (valor inválido)
- `missing_evaluation_id.yaml` — evaluation_id ausente
- `missing_justification.yaml` — justification ausente
- `invalid_rollback_target.yaml` — rollback_target: "unknown_stage"
- `extra_top_field.yaml` — campo extra no topo (`is_final: true`)
- `invalid_gap_severity.yaml` — gaps[0].severity: "trivial"

---

## Anti-regras

A implementação NÃO DEVE:

- Avaliar se a conclusão do solver está correta por qualquer heurística automática
  (o Gate Evaluator é uma estrutura de dados com validação, não um oráculo de IA)
- Chamar LLM, chamar internet, ler PDFs, fazer OCR
- Modificar o run record, o bundle, o manifest ou qualquer artefato existente
- Implementar resolução automática (a comparação é feita por humano ou agente
  com acesso explícito; o harness apenas valida a estrutura resultante)
- Alterar `blind_solver_harness.py`, `blind_solver_report_validator.py`,
  `blind_solve_run_record.py`
- Criar skills em `.ai/skills/`
- Alterar casos canônicos
- Propor ou implementar decisão de aprovação automática sem avaliação humana ou
  agente com contexto privado explícito

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/gate_evaluation.schema.yaml`
2. existir `generator/gate_evaluator.py`
3. existir função pública `validate_gate_evaluation(evaluation) -> list[str]`
4. existir função pública `validate_gate_evaluation_semantics(evaluation, run_record=None) -> GateEvaluationResult`
5. existir função pública `build_gate_evaluation(request, ...) -> dict`
6. existir dataclass pública `GateEvaluationRequest`
7. existir dataclass pública `GateEvaluationResult`
8. schema ter `additionalProperties: false` no topo
9. `decision` ter enum `approved | rejected | rollback`
10. `rollback_target` ter enum `bundle_preparation | blind_solve | gate_evaluation | null`
11. `expected_conclusions[].required` e `expected_conclusions[].met` serem booleans
12. `gaps[].severity` ter enum `critical | major | minor`
13. `confidence_assessment.evaluator_agreement` ter enum `agree | disagree | partial`
14. regras GE_001–GE_006 implementadas como errors bloqueantes
15. regra GE_007 implementada como warning não bloqueante
16. regra GE_008 implementada como error quando run_record fornecido
17. `build_gate_evaluation` não mutar inputs
18. fixtures válidas passarem no schema
19. fixtures inválidas falharem com mensagem correta
20. todos os 30 testes de `test_gate_evaluation_schema.py` passarem
21. todos os 30 testes de `test_gate_evaluator.py` passarem
22. nenhum arquivo existente alterado (exceto atualização opcional de doc)
23. `pytest tests/ -q` passar sem regressão (990+ testes)
24. `ruff check generator/gate_evaluator.py` passar
25. nenhum LLM/internet usado
26. nenhum caso canônico alterado
27. nenhuma skill criada em `.ai/skills/`

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Confirmar que falham pelo motivo certo
(ImportError ou NameError em `generator.gate_evaluator`, FileNotFoundError no schema).

**GREEN:** implementar o mínimo para passar (schema → `validate_gate_evaluation` →
`validate_gate_evaluation_semantics` → `build_gate_evaluation`).

**REFACTOR:** organizar helpers, dataclasses, regras semânticas.

---

## Validação final

```bash
ruff check generator/gate_evaluator.py

pytest tests/test_gate_evaluation_schema.py -q
pytest tests/test_gate_evaluator.py -q

pytest tests/test_blind_solve_run_record.py -q
pytest tests/test_blind_solve_run_record_schema.py -q
pytest tests/test_blind_solver_harness.py -q
pytest tests/test_blind_solver_report_validator.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- fixture `valid_approved.yaml` passa no schema
- `build_gate_evaluation` + `validate_gate_evaluation` produzem resultado válido
- `validate_gate_evaluation_semantics` detecta GE_001–GE_008 corretamente
- nenhum arquivo existente alterado (exceto doc opcional)
- nenhum caso canônico alterado
- `pytest tests/ -q` passa sem regressão (990+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, enums)
- como a GateEvaluation liga o run record ao contexto privado
- regras semânticas implementadas (GE_001–GE_008)
- fixtures criadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed, Z warnings)
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum LLM/internet foi usado
- confirmação de que nenhuma skill foi criada
- próxima PR recomendada: ISSUE-21+22 — Narrative + Evidence Reviewer

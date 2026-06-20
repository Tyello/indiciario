# Blind Solver Harness (ISSUE-16)

## Objetivo

O Blind Solver Harness simula, de forma **offline, determinística e auditável**, a
execução de um solver cego sobre um blind bundle já gerado e sanitizado. Esta
issue cria o **harness e o contrato de saída**, não a inteligência real do solver.

## O que o harness faz

- Recebe um diretório de blind bundle (`BlindSolverHarnessRequest`).
- Valida o bundle com o leak checker estrutural
  (`generator/blind_bundle_leak_checker.py`); bundle inválido bloqueia a execução.
- Carrega o `blind_bundle_manifest.yaml`.
- Expõe ao solver **somente** os artefatos declarados em `included_artifacts`,
  através de um `BlindSolverContext` controlado.
- Executa `solver.solve(context)` e obtém um `BlindSolverReport`.
- Valida o relatório contra `schemas/blind_solver_report.schema.yaml` e aplica
  verificações semânticas mínimas contra o manifest.
- Registra os artefatos lidos (`accessed_artifacts`) e tentativas de acesso
  negadas (`denied_access_attempts`).

## O que o harness NÃO faz

- Não chama LLM nem provider (OpenAI/Claude/Ollama).
- Não acessa a internet.
- Não lê arquivos fora do bundle nem `excluded_artifacts`.
- Não permite path traversal.
- Não usa OCR e não parseia PDF semanticamente (apenas texto UTF-8 bruto).
- Não altera o bundle nem o manifest.
- Não avalia se a conclusão está correta — isso é função do futuro Gate
  Evaluator.

## Relação com bundle, sanitizer e leak checker

O harness é o **consumidor** do que o gerador
(`generator/blind_bundle_generator.py`) e o sanitizer
(`generator/blind_bundle_sanitizer.py`) produzem. Antes de qualquer leitura, ele
reusa `check_blind_bundle` para garantir que o pacote é estruturalmente íntegro
(hashes, arquivos declarados, ausência de symlinks e de `excluded_artifacts`
físicos). O acesso por path reusa o `_bundle_child` do leak checker para impedir
escapes do diretório do bundle.

## Contrato do report

Campos obrigatórios (`schema_version` fixo em `"1.0"`):

`solver_run_id`, `solver_id`, `bundle_id`, `manifest_id`, `created_at`,
`conclusion`, `confidence` (`low`/`medium`/`high`), `reasoning_summary`,
`evidence_used`, `open_questions`, `assumptions`, `warnings`.

Cada item de `evidence_used`: `artifact_id`, `path`, `quote_or_summary`,
`relevance`, `confidence`.

O schema usa `additionalProperties: false`, então campos privados como
`final_solution_private`, `answer_key`, `raw_prompt`, `chain_of_thought` ou
`other_agent_outputs` são automaticamente rejeitados. O campo de raciocínio é o
`reasoning_summary`, **curto e auditável** — chain-of-thought não é exigido nem
permitido.

### Validações semânticas do harness (além do schema)

- `bundle_id`, `manifest_id` e `solver_run_id` do report têm de bater com o
  manifest/request.
- `reasoning_summary` não pode ser vazio; `confidence` tem de ser enum.
- Se há `conclusion`, `evidence_used` não pode estar vazio.
- Cada `evidence_used` tem de referenciar um `artifact_id`/`path` realmente
  presente em `included_artifacts`.

## Limites

- `max_artifacts` (default `100`): bundles maiores são bloqueados antes do solver.
- `max_bytes_per_artifact` (default `1_000_000`): artefatos maiores são
  bloqueados antes (e também no momento da leitura).

## Acesso controlado

`BlindSolverContext` expõe `list_artifacts()`, `read_artifact(artifact_id)` /
`read_artifact_text(artifact_id)` e `read_artifact_path(path)`. Ele nunca entrega
o `bundle_path` bruto nem objetos `Path` ao solver. Qualquer leitura fora da lista
declarada (arquivo não declarado, `excluded_artifact`, path traversal, arquivo
externo) é registrada como acesso negado e **falha** com `BlindSolverHarnessError`,
porque acesso proibido é quebra do protocolo cego.

## Validator standalone do report (ISSUE-17)

`generator/blind_solver_report_validator.py` é um validador **standalone** que pode
ser chamado independentemente do harness. Ele opera **somente sobre o dict do
report**: não precisa de bundle, manifest nem context. Não chama LLM, não acessa a
internet, não julga se a conclusão está *correta* e **não modifica** o report
recebido. Sobre a validação estrutural já feita pelo schema, ele adiciona uma
camada semântica (coerência interna) e uma camada de qualidade (warnings).

### API pública

```python
def validate_report(report: Mapping[str, Any]) -> ReportValidationResult: ...
```

- Aceita `dict` ou qualquer `Mapping` (uma cópia rasa é passada ao schema
  validator para suportar mappings somente-leitura sem mutar a entrada).
- Retorna um `ReportValidationResult` imutável.

```python
class ReportValidationErrorKind(str, Enum):
    STRUCTURAL = "structural"   # violação de schema
    SEMANTIC   = "semantic"     # incoerência interna (blocante)
    QUALITY    = "quality"      # report válido mas provavelmente inútil (warning)

@dataclass(frozen=True)
class ReportValidationError:
    kind: ReportValidationErrorKind
    code: str        # ex: "RV_001"
    field: str       # campo afetado, ex: "reasoning_summary"
    message: str     # mensagem legível

@dataclass(frozen=True)
class ReportValidationResult:
    valid: bool
    errors: tuple[ReportValidationError, ...]    # apenas blocantes
    warnings: tuple[ReportValidationError, ...]  # apenas quality
```

`ReportValidationError` e `ReportValidationResult` são `frozen=True` (imutáveis).
`valid` é `True` quando não há `errors` blocantes — `warnings` nunca tornam o
report inválido.

### Categorias structural / semantic / quality

- **structural** — `RV_001`. Delega a
  `validate_blind_solver_report` (do harness). Se há erro de schema, ele vira o
  único finding (`valid=False`) e **curto-circuita** as checagens semânticas e de
  qualidade, porque elas assumem um report estruturalmente válido.
- **semantic** — `RV_002`–`RV_005` e `RV_008`. São **blocantes**: qualquer um
  deles faz `valid=False`. Detectam incoerências internas do report.
- **quality** — `RV_006` e `RV_007`. São **warnings**: vão para `warnings`, nunca
  para `errors`, e **não** tornam `valid=False`.

### Códigos RV_001–RV_008

| Código | Categoria | Campo (`field`) | Condição | Efeito |
|---|---|---|---|---|
| `RV_001` | structural | `<schema>` | Schema inválido (delegado a `validate_blind_solver_report`). | `valid=False`; único finding; curto-circuita o resto. |
| `RV_002` | semantic | `evidence_used` | `conclusion` não vazia e `evidence_used` vazio. | `valid=False` |
| `RV_003` | semantic | `confidence` | `confidence == "high"` e `evidence_used` vazio. | `valid=False` |
| `RV_004` | semantic | `open_questions` | `confidence == "high"` e `open_questions` não vazio. | `valid=False` |
| `RV_005` | semantic | `conclusion` | `conclusion` vazia e `open_questions` vazio. | `valid=False` |
| `RV_006` | quality | `reasoning_summary` | `reasoning_summary` contém apenas um placeholder vago (match de substring, case-insensitive). | warning; `valid` inalterado |
| `RV_007` | quality | `conclusion` | `evidence_used` não vazio e `conclusion` vazia. | warning; `valid` inalterado |
| `RV_008` | semantic | `confidence` | `confidence == "low"` e `evidence_used` tem 3+ itens com `confidence: high`. | `valid=False` |

Placeholders vagos considerados em `RV_006` (substring, case-insensitive):
`"inconclusivo"`, `"sem conclusão"`, `"não foi possível"`, `"insuficiente"`,
`"n/a"`, `"pendente"`, `"a definir"`.

O limiar de `RV_008` é 3 itens de evidência com `confidence: high`; com
`confidence: medium` (ou menos de 3 evidências high) a condição não dispara.

## Blind Solve Run Record (ISSUE-18)

O **run record** é o registro rastreável de uma execução cega completa. Ele
liga, em um único artefato auditável, o bundle usado, o manifest, o solver, o
report produzido, os artefatos efetivamente acessados, as tentativas de acesso
negadas, os warnings do harness e o resultado da validação semântica do report.
Não chama LLM, não acessa a internet e **não muta** os inputs.

### API pública

`generator/blind_solve_run_record.py` expõe duas funções:

```python
def build_run_record(harness_result, request, validator_result,
                     created_by=None, notes=None) -> dict: ...
def validate_run_record(record) -> list[str]: ...
```

- `build_run_record` monta o dict do run record a partir do
  `BlindSolverHarnessResult`, do `BlindSolverHarnessRequest` e do
  `ReportValidationResult` (ISSUE-17). Não muta os inputs.
- `validate_run_record` valida o record contra
  `schemas/blind_solve_run_record.schema.yaml` e retorna uma lista de erros
  (vazia quando o record é válido).

### O que o run record liga

- `bundle_id` / `manifest_id` — copiados do report embutido (batem com o
  manifest do bundle).
- `solver_id` e `run_id` — identidade do solver e da execução; `run_id` bate com
  o `solver_run_id` do report.
- `report` — o `BlindSolverReport` embutido na íntegra.
- `accessed_artifacts` — artefatos efetivamente lidos pelo solver, refletindo os
  acessos registrados pelo harness.
- `denied_access_attempts` — tentativas de acesso bloqueadas pelo harness.
- `harness_warnings` — warnings emitidos pelo harness durante a execução.
- `validation` — resultado da validação do report: `report_schema_valid`,
  `report_semantic_valid`, `semantic_errors`, `semantic_warnings`.
- `environment` — defaults honestos da execução cega offline:
  `offline=True`, `llm_used=False`, `internet_used=False`.
- `execution` — `status` (`completed` por padrão), `duration_seconds` (inteiro
  `>= 0`) e `failure_reason` (obrigatório quando `status != completed`).

### Campos preenchidos por agentes posteriores

- `gate_decision` — `null` por padrão. Será preenchido pelo **Gate Evaluator**
  (Fase E, ISSUE-19+), que decide se o caso é justo dado o bundle cego.
- `reviewer_findings` — lista vazia por padrão. Será preenchida pelos revisores
  especializados (Fase F): narrative, evidence, visual, accessibility.

O run record é, portanto, o ponto de junção entre a execução cega (ISSUE-16/17)
e as decisões de avaliação posteriores: o harness produz o output cego, o run
record o torna rastreável, e os agentes de gate/review anexam suas decisões sem
reabrir a execução.

## Gate Evaluator (ISSUE-19+20)

O **Gate Evaluator** é o único ponto onde a **solução privada do autor** encontra
o **output cego do solver**. Ele registra uma avaliação privada de um run
congelado e decide se o caso é justo dado o bundle cego. Não chama LLM, não acessa
a internet e **não muta** artefatos (run record, report, inputs).

### API pública

`generator/gate_evaluator.py` expõe:

```python
def validate_gate_evaluation(evaluation) -> list[str]: ...
def validate_gate_evaluation_semantics(evaluation, run_record=None) -> GateEvaluationResult: ...
def build_gate_evaluation(request, ...) -> dict: ...
```

- `validate_gate_evaluation` valida o dict da evaluation contra
  `schemas/gate_evaluation.schema.yaml` e retorna lista de erros (vazia quando
  válido).
- `validate_gate_evaluation_semantics` aplica as regras semânticas GE_001–GE_008
  e retorna um `GateEvaluationResult`. Com `run_record` fornecido, ativa também a
  checagem de runtime GE_008.
- `build_gate_evaluation` monta o dict da evaluation a partir de um
  `GateEvaluationRequest` (ligando `evaluation_id`, `run_id`, `bundle_id` do
  `request.run_record`, serializando `expected_conclusions`, `gaps`,
  `confidence_assessment`, `decision`, `justification`, `rollback_target`). Não
  muta inputs.

### Dataclasses

- `GateEvaluationRequest` — entrada do builder (run record + dados da avaliação).
- `GateEvaluationResult` — resultado imutável da validação semântica.
- `ExpectedConclusion` — conclusão esperada do autor (`id`, `met`, `required`).
- `GapItem` — lacuna detectada (`severity`).
- `ConfidenceAssessment` — `evaluator_agreement` e dados de confiança.

### Enums

| Campo | Valores |
|---|---|
| `decision` | `approved` \| `rejected` \| `rollback` |
| `rollback_target` | `bundle_preparation` \| `blind_solve` \| `gate_evaluation` \| `null` |
| `severity` | `critical` \| `major` \| `minor` |
| `evaluator_agreement` | `agree` \| `disagree` \| `partial` |

### Regras GE_001–GE_008

| Código | Efeito | Condição |
|---|---|---|
| `GE_001` | error (blocante) | `decision: rollback` sem `rollback_target`. |
| `GE_002` | error (blocante) | `decision: approved` com `rollback_target` preenchido. |
| `GE_003` | error (blocante) | `leak_detected: true` com `decision: approved`. |
| `GE_004` | error (blocante) | `decision: approved` com `expected_conclusion` `required=true` e `met=false`. |
| `GE_005` | error (blocante) | `decision: approved` sem cobertura de conclusões requeridas. |
| `GE_006` | error (blocante) | `decision: approved` com gap `severity: critical`. |
| `GE_007` | warning | aviso de coerência; não torna a evaluation inválida. |
| `GE_008` | error em runtime | inconsistência entre evaluation e `run_record` (só dispara com `run_record` fornecido). |

GE_001–GE_006 são erros blocantes. GE_007 é warning. GE_008 só é avaliado em
runtime quando `run_record` é passado.

## Próximos passos

- **ISSUE-17 — Blind Solver Report Validator**: validador dedicado que aprofunda
  a checagem de utilidade/rastreabilidade do report.
- **ISSUE-18 — Blind Solve Run Record**: registrar a execução cega como run
  rastreável.
- O Gate Evaluator (Fase E) é quem decide se o caso é justo; o harness apenas
  produz o output cego.

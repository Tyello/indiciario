# Execution Report — ISSUE-25+26 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos

- `.ai/issues/ISSUE-25+26.md`
- `.ai/issues/ISSUE-25+26_SPEC.md`
- `.ai/skills/README.md`
- `.ai/skills/tdd.md`
- `generator/gate_evaluator.py`
- `generator/blind_solve_run_record.py`
- `generator/narrative_reviewer.py`
- `schemas/gate_evaluation.schema.yaml`
- `schemas/review_report.schema.yaml`
- `schemas/blind_solve_run_record.schema.yaml`
- `tests/test_gate_evaluator.py`
- `tests/test_gate_evaluation_schema.py`

## Arquivos alterados

- `.ai/runs/ISSUE-25+26/STEP-01_EXECUTION.md` (este report)

## Comandos executados

- nenhum

## Resultado

### Padrão de carga de schema (`validate_*`)

Identico em `gate_evaluator.py`, `blind_solve_run_record.py`, `narrative_reviewer.py`:

- Constante de path no topo do modulo:
  `_X_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "X.schema.yaml"`.
- Funcao `validate_<thing>(obj: Mapping[str, Any]) -> list[str]`:
  1. `schema = yaml.safe_load(_X_SCHEMA_PATH.read_text(encoding="utf-8"))`
  2. `Draft202012Validator.check_schema(schema)`
  3. `validator = Draft202012Validator(schema, format_checker=FormatChecker())`
  4. `return sorted(error.message for error in validator.iter_errors(dict(obj)))`
- Import: `import yaml` + `from jsonschema import Draft202012Validator, FormatChecker`.
- `dict(obj)` defensivo: nunca muta a entrada (Mapping).
- Lista vazia retornada == estruturalmente valido.
- Para `workspace.py`: replicar com
  `_WORKSPACE_RUN_SCHEMA_PATH = ... / "schemas" / "workspace_run.schema.yaml"`
  e `validate_workspace_run(run) -> list[str]`.

### Formato das mensagens de erro

- Erros estruturais (schema): vem direto de `error.message` do jsonschema,
  ordenados com `sorted(...)`. Sem prefixo de codigo.
- Erros/warnings semanticos (regras GE_/NR_/WS_/OR_): strings construidas a mao,
  SEMPRE com prefixo de codigo no inicio. Padrao exato visto em `gate_evaluator.py`:
  `"GE_001: decision='rollback' requires a non-null rollback_target"`.
  Codigo + `: ` + descricao. Testes detectam via substring (`code in error`),
  ex. `_has_code(errors, "GE_001")` em `test_gate_evaluator.py`.
- Para WS_*/OR_*: usar mesmo formato `"WS_001: <descricao>"` / `"OR_002: <descricao>"`.

### Helper `neutral_id`

Definido como `$defs` no rodape de cada schema YAML, identico em
`gate_evaluation`, `blind_solve_run_record`:

```yaml
$defs:
  neutral_id:
    type: string
    minLength: 2
    maxLength: 64
    pattern: '^[A-Z0-9][A-Z0-9_-]{1,63}$'
  timestamp:
    type: string
    format: date-time
    pattern: '^(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))$'
```

- Referenciado por campos id via `$ref: '#/$defs/neutral_id'` (ex. `run_id`,
  `bundle_id`, `artifact_id`, `decision_id`).
- Campos date-time via `$ref: '#/$defs/timestamp'` (ex. `created_at`,
  `ingested_at`, `decided_at`).
- `review_report.schema.yaml` NAO usa `$defs neutral_id` (report_id e string
  minLength:1, created_at inline). Para `workspace_run.schema.yaml`: seguir o
  modelo gate_evaluation/run_record (com `$defs neutral_id` + `timestamp`),
  pois a spec exige neutral_id para run_id/artifact_id/decision_id e date-time
  para created_at/ingested_at/decided_at.

### Padrao de schema YAML

- Cabecalho: `$schema`, `$id` (`https://indiciario.local/schemas/<name>/1.0`),
  `title`, `description` (`>-`).
- `type: object` + `additionalProperties: false` no topo.
- `required:` lista todos campos de topo.
- `properties:` com `schema_version: const: '1.0'`.
- Arrays de objetos: cada item `type: object`, `additionalProperties: false`,
  `required:`, `properties:`. Aplicar em `artifacts[]` e `decisions[]`.
- Enums: bloco `enum:` com itens. Para nullable: `type: [string, 'null']` OU
  `enum:` incluindo `null` (gate usa `enum` com `- null` em rollback_target;
  run_record usa `type: [string, 'null']` em failure_reason). Para
  `decisions[].rollback_to_stage` (string|null): usar `type: [string, 'null']`.

### Serializacao de dataclasses

Dois padroes vistos:

1. Builder `build_*` que retorna `dict` diretamente (gate_evaluator
   `build_gate_evaluation`, run_record `build_run_record`). Monta dict literal,
   converte listas de dataclasses em listas de dicts com list-comprehension
   por campo. Nunca muta entradas (gate usa list() / dict comprehension;
   run_record usa `_deep_copy`).
2. Serializer `*_to_dict(obj)` que recebe a dataclass agregada e devolve dict
   pronto pra `validate_*` (narrative_reviewer `report_to_dict`). Converte
   tuple de dataclasses-finding em lista de dicts campo a campo.

Para `workspace.py`:
- `build_workspace_run(...) -> dict` (padrao 1): status/current_stage
  `"initialized"`, `artifacts: []`, `decisions: []`, `notes`. `created_at`
  default via helper de timestamp ISO se None.
- `run_to_dict(run: WorkspaceRun) -> dict` (padrao 2): serializa artifacts e
  decisions campo a campo; `visible_to` tuple -> list.

### Dataclasses

- Todas `@dataclass(frozen=True)`.
- Tuplas (nao listas) para colecoes internas: ex.
  `findings: tuple[ReviewFinding, ...]` (narrative),
  e na spec `artifacts: tuple[WorkspaceArtifact, ...]`,
  `decisions: tuple[WorkspaceDecision, ...]`, `visible_to: tuple[str, ...]`.
- Resultado semantico padrao: dataclass com
  `errors/warnings: tuple[str, ...]` + `valid: bool` + copia do objeto
  (`evaluation`/`run`). Ver `GateEvaluationResult`. Espelhar em
  `WorkspaceSemanticResult` (campos `run`, `errors`, `warnings`, `valid`).

### Helpers `_now_iso` / timestamp

- `gate_evaluator.build_gate_evaluation` e `narrative_reviewer._now_iso` usam:
  `datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")`.
- Imports: `from datetime import datetime, timezone`.
- Reusar identico em `build_workspace_run` (default created_at) e nos builders
  do orchestrator (default ingested_at / decided_at).

### Logica de resultado semantico (replicar em WS_*)

- `valid = not errors` (qualquer erro => False).
- Warnings registrados mesmo com `valid: True` (ver
  `validate_gate_evaluation_semantics`). Confirma regra da spec WS_006/WS_007
  (warnings, valid=True) e separacao error vs warning.

### Padrao de teste de schema (`test_gate_evaluation_schema.py`)

- Fixtures YAML em `tests/fixtures/<name>/valid/` e `.../invalid/`.
- `_load_fixture(*parts)`: abre YAML via `yaml.safe_load`.
- `_valid_<thing>(**overrides)`: carrega fixture valida base e aplica
  `.update(overrides)` para variacoes; caso com mutacao profunda usa
  `copy.deepcopy`.
- Casos validos: `assert validate_*(obj) == []`.
- Casos invalidos: `assert validate_*(obj) != []`.
- Guard final: helper de override nao muta a fixture em disco.
- Replicar em `test_workspace_run_schema.py` (casos 1-20) com fixtures em
  `tests/fixtures/workspace_run/{valid,invalid}/`.

### Padrao de teste semantico (`test_gate_evaluator.py`)

- Helper `_<thing>(**overrides)` com `copy.deepcopy` + `.update`.
- `_errors(obj)` chama `validate_*_semantics` e retorna
  `tuple(result.semantic_errors)`.
- `_has_code(errors, code)`: `any(code in error for error in errors)`.
- Um teste por regra (par positivo/negativo: dispara / nao dispara).
- Teste do flag `valid` (True sem erro, False com erro).
- Teste de nao-mutacao da entrada via `copy.deepcopy` antes/depois.
- Replicar em `test_workspace.py` (WS_001-WS_008) e
  `test_manual_orchestrator.py` (OR_001-OR_008).

## Divergencias

- nenhuma

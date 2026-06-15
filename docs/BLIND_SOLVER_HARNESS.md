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

## Próximos passos

- **ISSUE-17 — Blind Solver Report Validator**: validador dedicado que aprofunda
  a checagem de utilidade/rastreabilidade do report.
- **ISSUE-18 — Blind Solve Run Record**: registrar a execução cega como run
  rastreável.
- O Gate Evaluator (Fase E) é quem decide se o caso é justo; o harness apenas
  produz o output cego.

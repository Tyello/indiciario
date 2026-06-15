# ISSUE-18_SPEC — Blind Solve Run Record

## Identificação

- **Issue:** ISSUE-18
- **Título:** Blind Solve Run Record
- **Fase:** D
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-blind-solve-run-record`
- **Título sugerido da PR:** `feat: add blind solve run record`
- **Commit sugerido:** `feat: add blind solve run record`

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py`, `schemas/blind_solver_report.schema.yaml`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py`, validação semântica de report

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
   - `generator/blind_solver_report_validator.py`
   - `schemas/blind_solver_report.schema.yaml`
   - `schemas/blind_bundle_manifest.schema.yaml`
   - `schemas/playtest_session.schema.yaml`
   - `schemas/playtest_finding.schema.yaml`
   - `schemas/learning_decision.schema.yaml`
   - `tests/test_blind_solver_harness.py`
   - `tests/test_blind_solver_report_validator.py`
   - `docs/BLIND_SOLVER_HARNESS.md`
   - `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`
   - `docs/BLIND_CONTEXT_PROTOCOL.md`
8. Execute antes de alterar:
   ```bash
   pytest tests/test_blind_solver_harness.py -q
   pytest tests/test_blind_solver_report_validator.py -q
   pytest tests/ -q
   ```

## Objetivo

Criar um schema e validador para registrar uma execução cega completa como **run rastreável**.

O run record é o artefato que liga:
- o bundle usado (por `bundle_id`)
- o solver que executou (por `solver_id`)
- o output produzido (o `BlindSolverReport` congelado)
- os artifacts acessados durante a execução
- as tentativas de acesso negado
- os warnings do harness
- as decisões posteriores (Gate Evaluator, revisores)
- metadados de rastreabilidade (quem, quando, ambiente)

O run record **não avalia** se a solução está correta — isso é papel do Gate Evaluator (ISSUE-19). Ele só registra o que aconteceu.

## Modelo conceitual

```yaml
# schemas/blind_solve_run_record.schema.yaml
schema_version: "1.0"
run_id: "run-aurora-20260615-001"
bundle_id: "bundle-aurora-v1"
manifest_id: "manifest-aurora-v1"
solver_id: "stub-deterministic-v1"
created_at: "2026-06-15T10:00:00Z"
created_by: "orchestrator"
environment:
  offline: true
  llm_used: false
  internet_used: false
execution:
  started_at: "2026-06-15T10:00:00Z"
  finished_at: "2026-06-15T10:00:05Z"
  duration_seconds: 5
  status: "completed"        # completed | failed | aborted
  failure_reason: null       # preenchido se status = failed/aborted
report:
  # BlindSolverReport embutido ou referenciado
  schema_version: "1.0"
  solver_run_id: "run-aurora-20260615-001"
  solver_id: "stub-deterministic-v1"
  bundle_id: "bundle-aurora-v1"
  manifest_id: "manifest-aurora-v1"
  created_at: "2026-06-15T10:00:05Z"
  conclusion: "Helena foi envenenada por Marta."
  confidence: "medium"
  reasoning_summary: "Análise dos documentos indica..."
  evidence_used:
    - artifact_id: "doc-01"
      path: "docs/laudo_medico.txt"
      quote_or_summary: "Laudo aponta envenenamento"
      relevance: "causa mortis"
      confidence: "high"
  open_questions: []
  assumptions: []
  warnings: []
accessed_artifacts:
  - artifact_id: "doc-01"
    path: "docs/laudo_medico.txt"
    accessed_at: "2026-06-15T10:00:02Z"
denied_access_attempts: []
harness_warnings: []
validation:
  report_schema_valid: true
  report_semantic_valid: true
  semantic_errors: []
  semantic_warnings: []
gate_decision: null          # preenchido pelo Gate Evaluator (ISSUE-19)
reviewer_findings: []        # preenchido pelos revisores (ISSUE-21+)
notes: ""
```

## Campos obrigatórios do run record

| Campo | Tipo | Descrição |
|---|---|---|
| `schema_version` | const `"1.0"` | Versão do schema |
| `run_id` | string | Identificador único da run |
| `bundle_id` | string | Bundle usado (liga ao manifest) |
| `manifest_id` | string | Manifest usado |
| `solver_id` | string | Solver que executou |
| `created_at` | date-time | Criação do record |
| `created_by` | string | Quem criou (orchestrator, humano, etc.) |
| `environment` | object | Flags de ambiente |
| `execution` | object | Metadados de execução |
| `report` | object | BlindSolverReport completo embutido |
| `accessed_artifacts` | array | Artifacts lidos durante execução |
| `denied_access_attempts` | array | Tentativas negadas |
| `harness_warnings` | array | Warnings do harness |
| `validation` | object | Resultado das validações pós-execução |

## Campos opcionais (preenchidos por agentes posteriores)

| Campo | Tipo | Descrição |
|---|---|---|
| `gate_decision` | object\|null | Preenchido pelo Gate Evaluator (ISSUE-19) |
| `reviewer_findings` | array | Preenchido pelos revisores (ISSUE-21+) |
| `notes` | string | Observações livres |

## environment — campos obrigatórios

```yaml
environment:
  offline: true       # boolean — execução foi offline?
  llm_used: false     # boolean — usou LLM real?
  internet_used: false # boolean — acessou internet?
```

## execution — campos obrigatórios

```yaml
execution:
  started_at: date-time
  finished_at: date-time
  duration_seconds: integer >= 0
  status: "completed" | "failed" | "aborted"
  failure_reason: string | null   # obrigatório se status != completed
```

## accessed_artifacts — cada item

```yaml
- artifact_id: string
  path: string
  accessed_at: date-time
```

## denied_access_attempts — cada item

```yaml
- requested_path: string
  reason: string
  attempted_at: date-time
```

## validation — campos obrigatórios

```yaml
validation:
  report_schema_valid: boolean
  report_semantic_valid: boolean
  semantic_errors: array      # lista de ReportValidationError serializados
  semantic_warnings: array    # lista de warnings serializados
```

## Escopo permitido

Criar:
- `schemas/blind_solve_run_record.schema.yaml`
- `generator/blind_solve_run_record.py` — builder e validador do run record
- `tests/test_blind_solve_run_record_schema.py`
- `tests/test_blind_solve_run_record.py`
- `tests/fixtures/blind_solve_run_record/valid/`
- `tests/fixtures/blind_solve_run_record/invalid/`

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — seção sobre run record (opcional, se fizer sentido)

## Fora de escopo

**Não implementar:**
- Gate Evaluator (ISSUE-19)
- Avaliação de correção da solução
- Revisores (ISSUE-21+)
- Alteração em schemas existentes
- Alteração em `blind_solver_harness.py`
- Alteração em `blind_solver_report_validator.py`
- LLM provider
- Internet
- CLI complexa
- Alteração de casos canônicos

## API pública esperada

```python
# generator/blind_solve_run_record.py

def build_run_record(
    harness_result: BlindSolverHarnessResult,
    request: BlindSolverHarnessRequest,
    validator_result: ReportValidationResult,
    created_by: str = "orchestrator",
    notes: str = "",
) -> dict:
    """Constrói um run record a partir dos outputs do harness e do validator."""
    ...

def validate_run_record(record: Mapping[str, Any]) -> list[str]:
    """Valida o run record contra o schema. Retorna lista de erros (vazia = válido)."""
    ...
```

## Abordagem TDD obrigatória

**RED:** escreva todos os testes primeiro. Confirme que falham pelo motivo certo.

**GREEN:** implemente o mínimo para passar.

**REFACTOR:** organize helpers, builder, validador.

## Testes obrigatórios

### `tests/test_blind_solve_run_record_schema.py`

1. fixture válida completa passa
2. fixture válida com `denied_access_attempts` vazio passa
3. fixture com `status: failed` e `failure_reason` preenchido passa
4. fixture com `status: completed` e `failure_reason: null` passa
5. `schema_version` errada falha
6. `run_id` ausente falha
7. `bundle_id` ausente falha
8. `execution.status` inválido falha
9. `execution.status: failed` sem `failure_reason` falha
10. `environment.llm_used: true` é válido (não proibido no schema)
11. `gate_decision` null é válido
12. `gate_decision` objeto arbitrário é válido (preenchido depois)
13. campo extra no topo falha (`additionalProperties: false`)
14. `accessed_artifacts` item sem `artifact_id` falha
15. `denied_access_attempts` item sem `requested_path` falha

### `tests/test_blind_solve_run_record.py`

16. `build_run_record` com harness_result válido retorna dict
17. run record retornado passa `validate_run_record`
18. `run_id` do record bate com `solver_run_id` do report
19. `bundle_id` do record bate com `bundle_id` do report
20. `manifest_id` do record bate com `manifest_id` do report
21. `accessed_artifacts` reflete acessos do harness
22. `denied_access_attempts` reflete negações do harness
23. `harness_warnings` reflete warnings do harness
24. `validation.report_schema_valid` é True para report válido
25. `validation.report_semantic_valid` é True para report semanticamente válido
26. `validation.semantic_errors` é lista vazia para report sem erros
27. `validation.semantic_warnings` reflete warnings do validator
28. `environment.offline` é True por padrão
29. `environment.llm_used` é False por padrão
30. `environment.internet_used` é False por padrão
31. `gate_decision` é null por padrão
32. `reviewer_findings` é lista vazia por padrão
33. `build_run_record` não muta os inputs
34. `validate_run_record` retorna lista vazia para record válido
35. `validate_run_record` retorna erros para record inválido
36. `execution.duration_seconds` é inteiro >= 0
37. `execution.status` é "completed" para execução normal
38. `pytest tests/ -q` passa sem regressão

## Fixtures necessárias

**valid/**
- `valid_complete.yaml` — run completa com conclusion, evidence, accessed_artifacts
- `valid_no_conclusion.yaml` — run com status completed, sem conclusion, com open_questions
- `valid_failed_run.yaml` — status failed com failure_reason preenchido

**invalid/**
- `missing_run_id.yaml` — RV schema: run_id ausente
- `invalid_status.yaml` — execution.status inválido
- `failed_without_reason.yaml` — status failed sem failure_reason
- `extra_top_field.yaml` — campo extra no topo

## Validação final

Execute:

```bash
ruff check generator/blind_solve_run_record.py

pytest tests/test_blind_solve_run_record_schema.py -q
pytest tests/test_blind_solve_run_record.py -q

pytest tests/test_blind_solver_harness.py -q
pytest tests/test_blind_solver_report_validator.py -q
pytest tests/test_blind_solver_report_schema.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirme:
- fixture válida completa passa o schema
- `build_run_record` produz record válido
- `validate_run_record` detecta erros corretamente
- nenhum arquivo existente foi alterado
- nenhum caso canônico foi alterado
- `pytest tests/ -q` passa sem regressão (952+ testes)

## Anti-regras

A implementação NÃO DEVE:
- avaliar se a conclusão do solver está correta
- implementar Gate Evaluator
- chamar LLM
- chamar internet
- alterar schemas existentes
- alterar `blind_solver_harness.py`
- alterar `blind_solver_report_validator.py`
- alterar casos canônicos
- criar skills

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/blind_solve_run_record.schema.yaml`
2. existir `generator/blind_solve_run_record.py`
3. existir função pública `build_run_record()`
4. existir função pública `validate_run_record()`
5. run record ligar bundle_id, manifest_id, solver_id e report
6. `accessed_artifacts` refletir acessos do harness
7. `denied_access_attempts` refletir negações do harness
8. `validation` embutir resultado do schema validator e do semantic validator
9. `gate_decision` ser null por padrão
10. `reviewer_findings` ser lista vazia por padrão
11. `environment` ter flags offline, llm_used, internet_used
12. `execution.status` ter enum completed/failed/aborted
13. `failure_reason` obrigatório quando status != completed
14. `additionalProperties: false` no topo do schema
15. fixtures válidas passarem
16. fixtures inválidas falharem com erro correto
17. todos os 38 testes passarem
18. nenhum arquivo existente alterado
19. `pytest tests/ -q` passar sem regressão (952+ testes)
20. `ruff check generator/` passar
21. nenhum Gate Evaluator implementado
22. nenhum LLM/internet usado

## Resposta final esperada do agente

Informar:
- skills utilizadas
- arquivos criados
- API pública do builder e validador
- como o run record liga os componentes anteriores
- fixtures criadas
- testes adicionados
- comandos executados com resultados
- resultado da suite completa
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum Gate Evaluator foi implementado
- próxima PR recomendada: ISSUE-19 — Gate Evaluator: contrato de avaliação

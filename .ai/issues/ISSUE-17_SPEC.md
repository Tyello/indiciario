# ISSUE-17_SPEC — Blind Solver Report Validator

## Identificação

- **Issue:** ISSUE-17
- **Título:** Blind Solver Report Validator
- **Fase:** D
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-blind-solver-report-validator`
- **Título sugerido da PR:** `feat: add blind solver report validator`
- **Commit sugerido:** `feat: add blind solver report validator`

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py`, `schemas/blind_solver_report.schema.yaml`, `validate_blind_solver_report()` existem e passam em 918 testes.

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
   - `schemas/blind_solver_report.schema.yaml`
   - `tests/test_blind_solver_harness.py`
   - `tests/test_blind_solver_report_schema.py`
   - `tests/fixtures/blind_solver_report/valid/valid_complete.yaml`
   - `tests/fixtures/blind_solver_report/valid/valid_minimal_no_conclusion.yaml`
   - `docs/BLIND_SOLVER_HARNESS.md`
   - `docs/BLIND_CONTEXT_PROTOCOL.md`
   - `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`
8. Execute antes de alterar:
   ```bash
   pytest tests/test_blind_solver_harness.py -q
   pytest tests/test_blind_solver_report_schema.py -q
   pytest tests/ -q
   ```

## Objetivo

Criar um validador standalone para `BlindSolverReport` que:

- pode ser chamado independentemente do harness completo;
- separa erros estruturais (schema) de erros semânticos (coerência interna);
- valida que `reasoning_summary` tem substância mínima (não é placeholder vago);
- valida coerência entre `confidence` e `evidence_used`;
- valida que `open_questions` é usado quando `conclusion` está vazia;
- expõe função pública com retorno estruturado de erros categorizados;
- não precisa de bundle, manifest ou context para funcionar — opera só sobre o dict do report.

## O que já existe e NÃO deve ser duplicado

`validate_blind_solver_report()` em `generator/blind_solver_harness.py` já faz validação estrutural via schema. O novo validador **usa** essa função internamente e adiciona camada semântica por cima. Não reimplementar o schema validator.

## Modelo conceitual

```python
# Categorias de erro
class ReportValidationErrorKind(str, Enum):
    STRUCTURAL = "structural"   # violação de schema
    SEMANTIC   = "semantic"     # incoerência interna do report
    QUALITY    = "quality"      # report válido mas provavelmente inútil

@dataclass(frozen=True)
class ReportValidationError:
    kind: ReportValidationErrorKind
    code: str        # ex: "RV_001"
    field: str       # campo afetado, ex: "reasoning_summary"
    message: str     # mensagem legível

@dataclass(frozen=True)
class ReportValidationResult:
    valid: bool
    errors: tuple[ReportValidationError, ...]
    warnings: tuple[ReportValidationError, ...]  # kind=quality não bloqueia

def validate_report(report: Mapping[str, Any]) -> ReportValidationResult:
    """Validador standalone. Não requer bundle, manifest ou context."""
    ...
```

## Códigos de erro obrigatórios

| Código | Kind | Condição |
|---|---|---|
| `RV_001` | structural | schema inválido (delegar a `validate_blind_solver_report`) |
| `RV_002` | semantic | `conclusion` não vazia e `evidence_used` vazio |
| `RV_003` | semantic | `confidence: high` e `evidence_used` vazio |
| `RV_004` | semantic | `confidence: high` e `open_questions` não vazio |
| `RV_005` | semantic | `conclusion` vazia e `open_questions` vazio |
| `RV_006` | quality | `reasoning_summary` contém apenas placeholder vago |
| `RV_007` | quality | `evidence_used` não vazio mas `conclusion` vazia |
| `RV_008` | semantic | `confidence: low` mas `evidence_used` tem 3+ itens com confidence `high` |

**Placeholders vagos para RV_006** (case-insensitive, substring match):
- `"inconclusivo"`
- `"sem conclusão"`
- `"não foi possível"`
- `"insuficiente"`
- `"n/a"`
- `"pendente"`
- `"a definir"`

`RV_006` e `RV_007` são `kind=quality` — geram `warnings`, não `errors`. O report ainda pode ser `valid=True` com warnings.

`RV_001` a `RV_005` e `RV_008` são blocantes: `valid=False`.

## Escopo permitido

Criar:
- `generator/blind_solver_report_validator.py`
- `tests/test_blind_solver_report_validator.py`
- `tests/fixtures/blind_solver_report_validator/valid/` (fixtures)
- `tests/fixtures/blind_solver_report_validator/invalid/` (fixtures)
- `tests/fixtures/blind_solver_report_validator/warnings/` (fixtures com warnings quality)

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — adicionar seção sobre o validator standalone (opcional, se fizer sentido)

## Fora de escopo

**Não implementar:**
- Alteração em `schemas/blind_solver_report.schema.yaml`
- Alteração em `generator/blind_solver_harness.py`
- Alteração em testes existentes
- Gate Evaluator
- LLM provider
- Análise semântica do conteúdo da conclusão
- Scoring de qualidade da investigação
- CLI complexa
- Banco de dados
- Alteração de casos canônicos
- Novas skills

## Abordagem TDD obrigatória

**RED:** escreva todos os testes primeiro. Confirme que falham pelo motivo certo.

**GREEN:** implemente o mínimo para passar.

**REFACTOR:** organize helpers, códigos de erro, lista de placeholders vagos.

## Testes obrigatórios

Criar `tests/test_blind_solver_report_validator.py`.

Casos mínimos:

1. report válido completo → `valid=True`, sem errors, sem warnings
2. report válido mínimo sem conclusão → `valid=True`
3. schema inválido (campo obrigatório ausente) → `valid=False`, `RV_001`
4. `conclusion` não vazia, `evidence_used` vazio → `valid=False`, `RV_002`
5. `confidence: high`, `evidence_used` vazio → `valid=False`, `RV_003`
6. `confidence: high`, `open_questions` não vazio → `valid=False`, `RV_004`
7. `conclusion` vazia, `open_questions` vazio → `valid=False`, `RV_005`
8. `reasoning_summary` é "inconclusivo" → `valid=True`, warning `RV_006`
9. `reasoning_summary` é "N/A" → `valid=True`, warning `RV_006`
10. `reasoning_summary` é "Pendente" → `valid=True`, warning `RV_006`
11. `evidence_used` não vazio, `conclusion` vazia → `valid=True`, warning `RV_007`
12. `confidence: low`, 3 evidências com `confidence: high` → `valid=False`, `RV_008`
13. `confidence: medium`, 3 evidências com `confidence: high` → `valid=True` (RV_008 só bloqueia `low`)
14. report com múltiplos erros → todos os códigos aparecem no resultado
15. `errors` são instâncias de `ReportValidationError` com `kind`, `code`, `field`, `message`
16. `warnings` são instâncias de `ReportValidationError` com `kind=quality`
17. `kind=quality` não torna `valid=False`
18. `reasoning_summary` com texto real ("A análise indica...") → sem RV_006
19. `open_questions` com itens e `conclusion` vazia → sem RV_005
20. `valid=True` com warnings ainda é `valid=True`
21. função aceita `dict` e `Mapping`
22. função não modifica o report recebido
23. resultado é imutável (`frozen=True`)
24. fixtures válidas passam todas
25. fixtures inválidas falham com código correto
26. fixtures de warnings produzem `valid=True` com warnings esperados
27. `pytest tests/ -q` passa sem regressão

## Fixtures necessárias

**valid/**
- `valid_complete.yaml` — report completo com conclusion, evidências, high confidence, sem open_questions
- `valid_no_conclusion.yaml` — sem conclusion, com open_questions, confidence low

**invalid/**
- `conclusion_without_evidence.yaml` — RV_002
- `high_confidence_no_evidence.yaml` — RV_003
- `high_confidence_with_open_questions.yaml` — RV_004
- `no_conclusion_no_open_questions.yaml` — RV_005
- `low_confidence_all_high_evidence.yaml` — RV_008
- `missing_required_field.yaml` — RV_001

**warnings/**
- `vague_reasoning_summary.yaml` — RV_006
- `evidence_without_conclusion.yaml` — RV_007

## Validação final

Execute:

```bash
ruff check generator/blind_solver_report_validator.py

pytest tests/test_blind_solver_report_validator.py -q

pytest tests/test_blind_solver_harness.py -q
pytest tests/test_blind_solver_report_schema.py -q
pytest tests/test_blind_bundle_sanitizer.py -q
pytest tests/test_blind_bundle_leak_checker.py -q
pytest tests/test_blind_bundle_generator.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirme:
- `valid_complete` passa sem errors e sem warnings
- `RV_001`–`RV_005`, `RV_008` geram `valid=False`
- `RV_006`, `RV_007` geram `valid=True` com warnings
- nenhum arquivo existente foi alterado
- nenhum caso canônico foi alterado
- `pytest tests/ -q` passa sem regressão

## Anti-regras

A implementação NÃO DEVE:
- reimplementar validação de schema (usar `validate_blind_solver_report` existente)
- alterar `blind_solver_harness.py`
- alterar `blind_solver_report.schema.yaml`
- implementar Gate Evaluator
- chamar LLM
- chamar internet
- analisar conteúdo semântico da conclusão (ex: "a conclusão está correta?")
- alterar casos canônicos
- criar skills

## Critérios de aceitação

A PR estará concluída quando:

1. existir `generator/blind_solver_report_validator.py`
2. existir função pública `validate_report(report) -> ReportValidationResult`
3. `ReportValidationResult` tiver `valid`, `errors` e `warnings`
4. `ReportValidationError` tiver `kind`, `code`, `field`, `message`
5. RV_001 delegar ao schema validator existente
6. RV_002 bloquear conclusion sem evidence
7. RV_003 bloquear high confidence sem evidence
8. RV_004 bloquear high confidence com open_questions
9. RV_005 bloquear conclusion vazia e open_questions vazio
10. RV_006 gerar warning (não erro) para reasoning_summary vago
11. RV_007 gerar warning (não erro) para evidence sem conclusion
12. RV_008 bloquear low confidence com evidências majoritariamente high
13. warnings não tornam `valid=False`
14. função não modificar o report recebido
15. resultado ser imutável
16. todos os 27 casos de teste passarem
17. fixtures criadas nas três categorias (valid, invalid, warnings)
18. nenhum arquivo existente alterado
19. `pytest tests/ -q` passar sem regressão (918+ testes)
20. `ruff check generator/` passar

## Resposta final esperada do agente

Informar:
- skills utilizadas
- arquivos criados
- API pública do validator
- códigos implementados (RV_001–RV_008)
- como RV_006/RV_007 são tratados como warnings
- fixtures criadas
- testes adicionados
- comandos executados com resultados
- resultado da suite completa
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum LLM/Gate Evaluator foi implementado
- próxima PR recomendada: ISSUE-18 — Blind Solve Run Record

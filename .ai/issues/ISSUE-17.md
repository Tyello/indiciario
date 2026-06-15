# ISSUE-17 — Blind Solver Report Validator

## Estado

```
STATUS: waiting_review
CURRENT_STEP: STEP-01
NEXT_ACTION: review
REVIEW_STATUS: pending
LAST_COMPLETED_STEP: STEP-00
LAST_EXECUTION_REPORT: .ai/runs/ISSUE-17/STEP-01_EXECUTION.md
LAST_REVIEW_REPORT: none
BLOCKER: none
```

## Contexto

A ISSUE-16 entregou:
- `generator/blind_solver_harness.py` — harness com acesso controlado
- `schemas/blind_solver_report.schema.yaml` — contrato estrutural do report
- Validação estrutural via `validate_blind_solver_report()` já integrada ao harness

O que ainda não existe:
- Validador standalone que pode ser chamado independentemente do harness
- Separação semântica entre fatos, hipóteses e conclusão no report
- Validação de que `reasoning_summary` não é vago (ex: apenas "inconclusivo")
- Validação de que `confidence` é coerente com presença/ausência de evidências
- Função pública para validar um report YAML/JSON sem rodar o harness completo
- Fixtures demonstrando report com hipótese com evidência e informação ausente declarada

## Spec completa

Ver `.ai/issues/ISSUE-17_SPEC.md`

## Skill recomendada

`tdd` (mudança em código com testes). `diagnose` apenas se aparecer causa desconhecida.

## Ponteiros principais

- `generator/blind_solver_harness.py` (`validate_blind_solver_report` — reusar, não reimplementar)
- `schemas/blind_solver_report.schema.yaml` (não alterar)
- `tests/fixtures/blind_solver_report/valid/` (referência de formato de report)
- Códigos de erro RV_001–RV_008: ver tabela na spec.

## Steps

### STEP-01 — Leitura e diagnose inicial

Status: pending
Owner: executor
Type: reading

Objetivo:
- Ler todo o contexto obrigatório da spec e mapear o contrato de `validate_blind_solver_report`, o schema do report e o formato das fixtures existentes, sem alterar nada.
- Produzir relatório de leitura listando: estrutura do report, campos relevantes (`conclusion`, `evidence_used`, `confidence`, `open_questions`, `reasoning_summary`), e como reusar o schema validator.

Contexto permitido:
- AGENTS.md
- CLAUDE.md
- docs/LLM_CONTEXT.md
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- .ai/skills/README.md
- .ai/skills/tdd.md
- .ai/skills/diagnose.md
- generator/blind_solver_harness.py
- schemas/blind_solver_report.schema.yaml
- tests/test_blind_solver_harness.py
- tests/test_blind_solver_report_schema.py
- tests/fixtures/blind_solver_report/valid/valid_complete.yaml
- tests/fixtures/blind_solver_report/valid/valid_minimal_no_conclusion.yaml
- docs/BLIND_SOLVER_HARNESS.md
- docs/BLIND_CONTEXT_PROTOCOL.md
- docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md

Arquivos editáveis:
- .ai/runs/ISSUE-17/STEP-01_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Criar ou alterar código, testes ou fixtures.
- Rodar a suíte (isso é o STEP-02).

Done quando:
- O relatório de execução descreve o contrato de `validate_blind_solver_report`, os campos do report e o plano de reuso.

Revisão:
- Confirmar que nenhum arquivo de código/teste/fixture foi alterado.
- Confirmar que o relatório cobre os campos e a forma de reuso do schema validator.

Dependências:
- nenhuma

### STEP-02 — Baseline da suíte

Status: pending
Owner: executor
Type: baseline

Objetivo:
- Estabelecer baseline verde antes de qualquer alteração, registrando contagem de testes e resultado.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/runs/ISSUE-17/STEP-01_EXECUTION.md

Arquivos editáveis:
- .ai/runs/ISSUE-17/STEP-02_EXECUTION.md (somente relatório)

Comandos permitidos:
- `pytest tests/test_blind_solver_harness.py -q`
- `pytest tests/test_blind_solver_report_schema.py -q`
- `pytest tests/ -q`

Proibido:
- Criar ou alterar código, testes ou fixtures.

Done quando:
- O relatório registra a saída dos três comandos e confirma baseline verde (sem falhas).

Revisão:
- Confirmar que a baseline está verde e a contagem registrada.
- Confirmar que nenhum arquivo de produção/teste foi alterado.

Dependências:
- STEP-01

### STEP-03 — RED: validade e códigos blocantes semânticos (inline)

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar `tests/test_blind_solver_report_validator.py` com testes (reports inline) cobrindo: report válido completo; válido mínimo sem conclusão; schema inválido (RV_001); RV_002; RV_003; RV_004; RV_005; RV_008 (low + 3 evidências high); e medium + 3 evidências high não bloqueia (negativo de RV_008).
- Os testes devem falhar por ausência de `generator/blind_solver_report_validator.py` / `validate_report`.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/fixtures/blind_solver_report/valid/valid_complete.yaml
- tests/fixtures/blind_solver_report/valid/valid_minimal_no_conclusion.yaml
- generator/blind_solver_harness.py

Arquivos editáveis:
- tests/test_blind_solver_report_validator.py
- .ai/runs/ISSUE-17/STEP-03_EXECUTION.md

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar `generator/blind_solver_report_validator.py` ou qualquer implementação.
- Criar fixtures (esta etapa usa reports inline).
- Cobrir mais de 10 casos de teste.

Done quando:
- Os ~9 testes existem e falham pelo motivo certo (módulo/símbolo inexistente).
- O relatório registra a saída de pytest mostrando a falha esperada.

Revisão:
- Confirmar que os testes falham por ausência da implementação, não por erro de teste.
- Confirmar que nenhuma implementação foi criada.

Dependências:
- STEP-02

### STEP-04 — RED: warnings, múltiplos erros e negativos (inline)

Status: pending
Owner: executor
Type: red

Objetivo:
- Adicionar a `tests/test_blind_solver_report_validator.py` testes (inline) para: RV_006 com "inconclusivo"; RV_006 com "N/A"; RV_006 com "Pendente"; RV_007 (evidência sem conclusão) como warning; report com múltiplos erros (todos os códigos aparecem); `reasoning_summary` real → sem RV_006; `open_questions` com itens e conclusão vazia → sem RV_005; `valid=True` com warnings ainda é `valid=True`.
- Os novos testes devem falhar por ausência da implementação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py

Arquivos editáveis:
- tests/test_blind_solver_report_validator.py
- .ai/runs/ISSUE-17/STEP-04_EXECUTION.md

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar implementação.
- Criar fixtures.
- Cobrir mais de 10 casos de teste neste step.

Done quando:
- Os ~8 testes novos existem e falham pelo motivo certo.
- O relatório registra a saída de pytest.

Revisão:
- Confirmar falha por ausência da implementação.
- Confirmar que nenhuma implementação ou fixture foi criada.

Dependências:
- STEP-03

### STEP-05 — RED: contrato de API e imutabilidade (inline)

Status: pending
Owner: executor
Type: red

Objetivo:
- Adicionar a `tests/test_blind_solver_report_validator.py` testes para: `errors` são `ReportValidationError` com `kind`,`code`,`field`,`message`; `warnings` têm `kind=quality`; `kind=quality` não torna `valid=False`; função aceita `dict` e `Mapping`; função não modifica o report recebido; resultado imutável (`frozen=True`).
- Os novos testes devem falhar por ausência da implementação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py

Arquivos editáveis:
- tests/test_blind_solver_report_validator.py
- .ai/runs/ISSUE-17/STEP-05_EXECUTION.md

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar implementação.
- Criar fixtures.
- Cobrir mais de 10 casos de teste neste step.

Done quando:
- Os ~6 testes novos existem e falham pelo motivo certo.
- O relatório registra a saída de pytest.

Revisão:
- Confirmar falha por ausência da implementação.
- Confirmar que nenhuma implementação foi criada.

Dependências:
- STEP-04

### STEP-06 — RED: fixtures valid + warnings e seus testes

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures `valid/valid_complete.yaml`, `valid/valid_no_conclusion.yaml`, `warnings/vague_reasoning_summary.yaml`, `warnings/evidence_without_conclusion.yaml` em `tests/fixtures/blind_solver_report_validator/`.
- Adicionar testes que carregam essas fixtures: válidas → `valid=True` sem warnings; warnings → `valid=True` com warning esperado (RV_006, RV_007).
- Testes devem falhar por ausência da implementação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py
- tests/fixtures/blind_solver_report/valid/valid_complete.yaml
- tests/fixtures/blind_solver_report/valid/valid_minimal_no_conclusion.yaml

Arquivos editáveis:
- tests/fixtures/blind_solver_report_validator/valid/valid_complete.yaml
- tests/fixtures/blind_solver_report_validator/valid/valid_no_conclusion.yaml
- tests/fixtures/blind_solver_report_validator/warnings/vague_reasoning_summary.yaml
- tests/fixtures/blind_solver_report_validator/warnings/evidence_without_conclusion.yaml
- tests/test_blind_solver_report_validator.py

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar implementação.
- Editar mais de 5 arquivos.

Done quando:
- As 4 fixtures existem e os testes que as carregam falham por ausência da implementação.

Revisão:
- Confirmar formato válido das fixtures conforme schema do report.
- Confirmar falha por ausência da implementação.

Dependências:
- STEP-05

### STEP-07 — RED: fixtures invalid (parte 1) e teste

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures inválidas em `tests/fixtures/blind_solver_report_validator/invalid/`: `conclusion_without_evidence.yaml` (RV_002), `high_confidence_no_evidence.yaml` (RV_003), `high_confidence_with_open_questions.yaml` (RV_004).
- Adicionar/estender teste parametrizado que carrega essas fixtures e espera `valid=False` com o código correto.
- Testes devem falhar por ausência da implementação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py
- tests/fixtures/blind_solver_report/valid/valid_complete.yaml

Arquivos editáveis:
- tests/fixtures/blind_solver_report_validator/invalid/conclusion_without_evidence.yaml
- tests/fixtures/blind_solver_report_validator/invalid/high_confidence_no_evidence.yaml
- tests/fixtures/blind_solver_report_validator/invalid/high_confidence_with_open_questions.yaml
- tests/test_blind_solver_report_validator.py

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar implementação.
- Editar mais de 5 arquivos.

Done quando:
- As 3 fixtures existem e o teste falha por ausência da implementação.

Revisão:
- Confirmar que cada fixture corresponde ao código de erro esperado.
- Confirmar falha por ausência da implementação.

Dependências:
- STEP-06

### STEP-08 — RED: fixtures invalid (parte 2) e teste

Status: pending
Owner: executor
Type: red

Objetivo:
- Criar fixtures inválidas restantes em `tests/fixtures/blind_solver_report_validator/invalid/`: `no_conclusion_no_open_questions.yaml` (RV_005), `low_confidence_all_high_evidence.yaml` (RV_008), `missing_required_field.yaml` (RV_001).
- Estender o teste parametrizado para cobrir essas fixtures esperando `valid=False` com o código correto.
- Testes devem falhar por ausência da implementação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py
- schemas/blind_solver_report.schema.yaml

Arquivos editáveis:
- tests/fixtures/blind_solver_report_validator/invalid/no_conclusion_no_open_questions.yaml
- tests/fixtures/blind_solver_report_validator/invalid/low_confidence_all_high_evidence.yaml
- tests/fixtures/blind_solver_report_validator/invalid/missing_required_field.yaml
- tests/test_blind_solver_report_validator.py

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`

Proibido:
- Criar implementação.
- Editar mais de 5 arquivos.

Done quando:
- As 3 fixtures existem e o teste falha por ausência da implementação.

Revisão:
- Confirmar que `missing_required_field.yaml` realmente viola o schema (RV_001).
- Confirmar falha por ausência da implementação.

Dependências:
- STEP-07

### STEP-09 — GREEN: implementar o validator

Status: pending
Owner: executor
Type: green

Objetivo:
- Criar `generator/blind_solver_report_validator.py` com `ReportValidationErrorKind`, `ReportValidationError` (frozen), `ReportValidationResult` (frozen) e `validate_report(report)`.
- Implementar RV_001 (delegando a `validate_blind_solver_report`), RV_002–RV_005, RV_008 como blocantes e RV_006/RV_007 como warnings (kind=quality).
- Não modificar o report recebido. Fazer o mínimo para todos os testes RED passarem.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- tests/test_blind_solver_report_validator.py
- generator/blind_solver_harness.py
- schemas/blind_solver_report.schema.yaml

Arquivos editáveis:
- generator/blind_solver_report_validator.py
- .ai/runs/ISSUE-17/STEP-09_EXECUTION.md

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`
- `ruff check generator/blind_solver_report_validator.py`

Proibido:
- Criar novos testes ou fixtures (apenas ajustes mínimos de compatibilidade, se estritamente necessários).
- Alterar `generator/blind_solver_harness.py` ou `schemas/blind_solver_report.schema.yaml`.
- Reimplementar a validação de schema.

Done quando:
- Todos os testes em `tests/test_blind_solver_report_validator.py` passam.
- `ruff` passa no novo módulo.

Revisão:
- Confirmar reuso de `validate_blind_solver_report` para RV_001.
- Confirmar que RV_006/RV_007 são warnings e não tornam `valid=False`.
- Confirmar que o report não é modificado e os dataclasses são `frozen`.

Dependências:
- STEP-08

### STEP-10 — REFACTOR: organizar helpers e códigos

Status: pending
Owner: executor
Type: refactor

Objetivo:
- Sem alterar comportamento, organizar: lista de placeholders vagos, mapeamento de códigos RV_*, helpers de extração de campos. Melhorar legibilidade e remover duplicação.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- generator/blind_solver_report_validator.py
- tests/test_blind_solver_report_validator.py

Arquivos editáveis:
- generator/blind_solver_report_validator.py
- .ai/runs/ISSUE-17/STEP-10_EXECUTION.md

Comandos permitidos:
- `pytest tests/test_blind_solver_report_validator.py -q`
- `ruff check generator/blind_solver_report_validator.py`

Proibido:
- Adicionar comportamento novo ou novos códigos de erro.
- Alterar testes ou fixtures.

Done quando:
- Refactor aplicado, todos os testes ainda passam, `ruff` limpo.

Revisão:
- Confirmar que nenhum comportamento mudou (mesmos testes, sem novos).
- Confirmar melhoria de organização sem escopo novo.

Dependências:
- STEP-09

### STEP-11 — DOCUMENTATION: seção do validator standalone

Status: pending
Owner: executor
Type: documentation

Objetivo:
- Adicionar a `docs/BLIND_SOLVER_HARNESS.md` uma seção sobre o validator standalone: API pública (`validate_report`), códigos RV_001–RV_008 e a distinção structural/semantic/quality (warnings).

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- generator/blind_solver_report_validator.py
- docs/BLIND_SOLVER_HARNESS.md

Arquivos editáveis:
- docs/BLIND_SOLVER_HARNESS.md
- .ai/runs/ISSUE-17/STEP-11_EXECUTION.md

Comandos permitidos:
- nenhum

Proibido:
- Alterar código, testes ou fixtures.
- Vazar gabarito de caso para documento de jogador (n/a aqui, mas manter a regra).

Done quando:
- A seção documenta API, códigos e categorias de erro de forma consistente com a implementação.

Revisão:
- Confirmar que a doc reflete a API e os códigos reais.
- Confirmar que apenas a doc foi alterada.

Dependências:
- STEP-10

### STEP-12 — VALIDATION: suíte completa e checagens

Status: pending
Owner: executor
Type: validation

Objetivo:
- Rodar a bateria final de validação e registrar resultados, confirmando que nenhum arquivo existente (fora do escopo permitido) foi alterado.

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md

Arquivos editáveis:
- .ai/runs/ISSUE-17/STEP-12_EXECUTION.md (somente relatório)

Comandos permitidos:
- `ruff check generator/`
- `pytest tests/test_blind_solver_report_validator.py -q`
- `pytest tests/test_blind_solver_harness.py -q`
- `pytest tests/test_blind_solver_report_schema.py -q`
- `pytest tests/test_blind_bundle_sanitizer.py -q`
- `pytest tests/test_blind_bundle_leak_checker.py -q`
- `pytest tests/test_blind_bundle_generator.py -q`
- `pytest tests/ -q`
- `git diff --check`
- `git status --short`
- `git diff --stat`

Proibido:
- Alterar código, testes ou fixtures.
- Corrigir falhas aqui (se houver falha, reportar para correção via orquestrador).

Done quando:
- Todos os comandos registrados com saída.
- `pytest tests/ -q` verde sem regressão.
- `git` confirma que apenas arquivos do escopo permitido foram criados/alterados.

Revisão:
- Confirmar suíte completa verde e diff restrito ao escopo.

Dependências:
- STEP-11

### STEP-13 — WRAP-UP: relatório final da issue

Status: pending
Owner: executor
Type: wrap-up

Objetivo:
- Produzir o relatório final exigido pela spec: skills usadas, arquivos criados, API pública, códigos RV_001–RV_008, tratamento de RV_006/RV_007 como warnings, fixtures criadas, testes adicionados, comandos executados com resultados, confirmação de não alteração de arquivos existentes e de ausência de LLM/Gate Evaluator, e próxima PR recomendada (ISSUE-18).

Contexto permitido:
- .ai/issues/ISSUE-17.md
- .ai/issues/ISSUE-17_SPEC.md
- .ai/runs/ISSUE-17/STEP-09_EXECUTION.md
- .ai/runs/ISSUE-17/STEP-12_EXECUTION.md

Arquivos editáveis:
- .ai/runs/ISSUE-17/STEP-13_EXECUTION.md (somente relatório)

Comandos permitidos:
- nenhum

Proibido:
- Alterar código, testes ou fixtures.

Done quando:
- O relatório final cobre todos os itens da seção "Resposta final esperada do agente" da spec.

Revisão:
- Confirmar que o relatório final contempla todos os critérios de aceitação.

Dependências:
- STEP-12

## Histórico

- Issue criada; aguardando orquestração inicial.
- STEP-00 orquestrado: spec quebrada em 13 steps pequenos (reading, baseline, 6 RED separados por grupo/fixtures, GREEN, refactor, documentation, validation, wrap-up); sem `Type: Red-Green`; RED e GREEN separados; validação e wrap-up isolados. Próximo passo é STEP-01.
- STEP-01 executado pelo executor (reading); contrato/schema/fixtures mapeados; aguardando revisão.

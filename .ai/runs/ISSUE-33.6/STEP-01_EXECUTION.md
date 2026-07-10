# STEP-01 — Leitura (ISSUE-33.6)

## Numeração RV confirmada

`grep -n "RV_0" generator/blind_solver_report_validator.py` → códigos usados: RV_001–RV_008 (RV_001 estrutural, RV_002–RV_005/RV_008 semânticos bloqueantes, RV_006–RV_007 warnings de qualidade). `blind_solver_harness.py` não define códigos RV_ hoje.

**RV_009 está livre.** Numeração da spec confirmada sem alteração.

## Onde a checagem deve viver

`blind_solver_report_validator.py` opera *só* sobre o mapping do report (doc string: "requires no bundle, manifest or context") — não tem acesso a `accessed_artifacts`. Quem tem acesso a `context.accessed_artifacts` é `run_blind_solver_harness` em `generator/blind_solver_harness.py`, via `_validate_report_semantics`/`_result_warnings`.

Decisão: implementar RV_009 em `blind_solver_harness.py`, dentro de `_result_warnings` (ou helper chamado por ela), comparando `evidence_used[].artifact_id` contra `context.accessed_artifacts`. Mantém a família RV_ (nome/prefixo), mas o código físico fica no harness porque é o único lugar com o dado necessário — consistente com o texto da spec ("família do blind_solver_report_validator/harness").

## Canal de warnings do run record (RV_010)

`generator/blind_solve_run_record.py:98` já faz `"harness_warnings": list(harness_result.warnings)`. Schema (`schemas/blind_solve_run_record.schema.yaml:134`) declara `harness_warnings` como `array of string`, sem enum fechado.

**Conclusão: RV_010 é automático.** Bastar adicionar a mensagem RV_009 em `BlindSolverHarnessResult.warnings` (retornado por `run_blind_solver_harness`) que ela já flui para `harness_warnings` no run record, sem tocar `blind_solve_run_record.py` nem o schema.

## Arquivos a tocar no STEP-03

- `generator/blind_solver_harness.py` — nova checagem em `_result_warnings` (precisa passar `context` para ela, hoje só recebe `report, bundle_report`).
- Nenhuma mudança em `blind_solve_run_record.py` ou schemas.

Done.

# ISSUE-33 STEP-02 — Execução

## Sumário
Arquivo `tests/test_llm_blind_solver.py` criado com 8 casos de teste sentinel para `generator.llm_blind_solver` (módulo será implementado em STEP-03).

## Testes criados

1. **LS_003** (`test_ls_003_happy_path_id_override`): FakeProvider com JSON válido, IDs sobrescritos do context
2. **LS_001** (`test_ls_001_sentinel_leaked_content_not_in_prompt`): Sentinela de arquitetura — conteúdo do bundle no prompt, conteúdo vazado excluído
3. **LS_002a** (`test_ls_002_json_repair_valid_on_second_attempt`): Primeira resposta JSON inválida, segunda válida, reparo com 2 chamadas
4. **LS_002b** (`test_ls_002_both_responses_invalid_raises_error`): Ambas respostas inválidas, levanta BlindSolverHarnessError
5. **LS_004** (`test_ls_004_extra_field_discarded_warning_added`): Campo extra no JSON descartado, warning adicionado
6. **LS_005** (`test_ls_005_prompt_template_hash_audited`): Hash sha256 do template registrado no report
7. **LS_006** (`test_ls_006_prompt_includes_exact_artifact_list`): Prompt inclui lista EXATA de artifacts, sem extras
8. **LS_007** (`test_ls_007_integration_with_harness`): Integração com run_blind_solver_harness, fim-a-fim válido
9. **LS_008** (`test_ls_008_pipeline_regression_without_solver_param`): Regressão — marcado com `@pytest.mark.skip` (STEP-04)

## Validação

```bash
$ pytest tests/test_llm_blind_solver.py -q

=================================== ERRORS ====================================
_______________ ERROR collecting tests/test_llm_blind_solver.py _______________
ImportError while importing test module 'C:\Users\Marcelo\OneDrive\Documentos\Projetos\indiciario\tests\test_llm_blind_solver.py'.

tests\test_llm_blind_solver.py:41: in <module>
    from generator.llm_blind_solver import LLMBlindSolver  # Will fail until STEP-03
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'generator.llm_blind_solver'
=========================== short test summary info ===========================
ERROR tests/test_llm_blind_solver.py
Interrupted: 1 error during collection
```

**Status**: ✅ Falha pelo motivo correto (módulo não existe).

## Arquivos alterados
- `tests/test_llm_blind_solver.py` (novo)

## Próximo passo
STEP-03 — implementar `generator/llm_blind_solver.py` e `generator/prompts/blind_solver_v1.md`.

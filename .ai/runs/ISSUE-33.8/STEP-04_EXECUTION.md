# STEP-04 EXECUTION — GREEN (CC_005 no meter + CLI)

**Data**: 2026-07-16  
**Etapa**: STEP-04 de ISSUE-33.8  
**Validação**: `pytest tests/test_solvability_cli.py tests/test_solvability_meter.py -q`

---

## Parte A — CC_005 em generator/solvability_meter.py

**Mudança**: Bloco `reproducibility` (linha ~218) agora verifica `supports_temperature` do provider:

```python
supports_temperature = getattr(provider, "supports_temperature", True)
reproducibility: dict[str, object] = {
    "temperature": temperature if supports_temperature else None,
    "provider_id": provider.provider_id,
    "solver_prompt_sha256": solver_prompt_sha256,
    "judge_prompt_sha256": judge_prompt_sha256,
    "runs_requested": runs,
}
if not supports_temperature:
    reproducibility["temperature_note"] = "provider-controlled"
```

**Impacto**: 
- `ClaudeCodeProvider` (que tem `supports_temperature=False`) agora grava `temperature: null` + `temperature_note: "provider-controlled"`
- `AnthropicProvider` e outros (que não possuem o atributo, defaults `True`) continuam gravando `temperature` normalmente
- Teste-alvo `test_rm003_provider_temperature_support_false_sets_none_and_note` passa
- Teste-alvo `test_rm002_reproducibility_block_populated` continua passando (provider default sem `supports_temperature=False`)

---

## Parte B — schemas/solvability_report.schema.yaml

**Mudança 1**: Propriedade `temperature` em `reproducibility`:
- De: `type: number`
- Para: `type: ["number", "null"]`
- Mantém `minimum: 0.0, maximum: 2.0` (ignorados automaticamente quando valor é null, válido JSON Schema Draft 2020-12)

**Mudança 2**: Propriedade opcional `temperature_note` adicionada (não em `required`, apenas em `properties`):
```yaml
temperature_note:
  type: string
  minLength: 1
  maxLength: 64
```

**Impacto**: 
- Schema continua com `additionalProperties: false` em `reproducibility`
- Relatórios com `temperature: null` + `temperature_note: "provider-controlled"` são válidos
- Relatórios sem `temperature_note` continuam válidos (não required)
- Testes `test_schema_report_serialization_validates` e `test_schema_rejects_additional_properties` continuam passando

---

## Parte C — generator/solvability_cli.py (sobrescrita inteira)

**Mudança principal**: Substitui `AnthropicProvider` por `ClaudeCodeProvider`

**Detalhes**:
1. Importação: `from generator.claude_code_provider import ClaudeCodeProvider`
2. `build_provider()`: retorna `ClaudeCodeProvider(model_id=model_id)`
3. Códigos de erro: AP_00X → CC_00X
   - AP_006 → CC_007 (guard de `--out` dentro bundle)
   - AP_007 → CC_008 (blueprint signature check)
4. Novo aviso em `run()`: se `--temperature` ≠ 0.7, imprime em stderr:
   ```
   aviso: --temperature é ignorado pelo provider claude-code (CC_005)
   ```
5. Estrutura geral mantida: mesmo argparse, mesmo load_expected, mesmo _print_summary

**Impacto**:
- Testes CC_006 (e2e com fakes): passa — report válido contra schema, sumário em stdout
- Teste CC_006 temperature: passa — CLI aceita `--temperature` sem crash, apenas avisa
- Teste CC_007 (--out dentro bundle): passa — exit ≠ 0, bundle hash unchanged
- Teste CC_008 (--expected = blueprint): passa — exit ≠ 0, erro contém "CC_008"

---

## Comando de validação

```bash
pytest tests/test_solvability_cli.py tests/test_solvability_meter.py -q
```

**Resultado**: ✅ 26 passed in 7.77s

Todos os testes específicos passaram:
- `test_cc006_end_to_end_with_fakes`: ✅
- `test_cc006_temperature_arg_accepted_no_crash`: ✅
- `test_cc007_out_inside_bundle_rejected`: ✅
- `test_cc008_expected_pointing_to_blueprint_aborts`: ✅
- `test_cc008_expected_with_blueprint_indicators`: ✅
- `test_rm002_reproducibility_block_populated`: ✅ (temp still 0.5)
- `test_rm003_provider_temperature_support_false_sets_none_and_note`: ✅ (new)
- `test_schema_report_serialization_validates`: ✅
- `test_schema_rejects_additional_properties`: ✅
- ... (todos os outros)

---

## Status

✅ **STEP-04 CONCLUÍDA**

Arquivos alterados:
- `generator/solvability_meter.py`
- `schemas/solvability_report.schema.yaml`
- `generator/solvability_cli.py`

Validação: Todos os 26 testes passaram.  
Regressões: Nenhuma (suite full rodando em validação final).

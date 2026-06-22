# Execution Report — ISSUE-27 STEP-10

STEP: STEP-10
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Criar testes casos 46–55 (findings_by_artifact, next_steps, round-trip) em tests/test_run_manifest.py; falham por build_run_manifest ausente.

## Arquivos lidos
- .ai/issues/ISSUE-27.md
- .ai/issues/ISSUE-27_SPEC.md
- tests/test_run_manifest.py
- .ai/workflows/executor.md

## Arquivos alterados
- tests/test_run_manifest.py (ADICIONADOS casos 46–55 + imports de build_run_manifest, manifest_to_dict, validate_run_manifest, RunManifest, ManifestArtifactSummary, ManifestDecisionSummary, ManifestFinding, ManifestGateOutcome)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_run_manifest.py -q` — RED: 1 error during collection; ImportError: cannot import name 'build_run_manifest' from 'generator.run_manifest'

## O que foi feito
- Helper `_ws_finding` adicionado (code/severity/field/message).
- Caso 46: findings_by_artifact vazio → findings [].
- Caso 47: finding em artefato narrative_review (NR-001) → source_type narrative_review.
- Caso 48: finding em artefato evidence_review (ER-001) → source_type evidence_review.
- Caso 49: build_run_manifest não muta run nem findings_by_artifact (copy.deepcopy + assert igual).
- Caso 50: run done → next_steps == ["Pipeline completo. Revisar findings e prosseguir para ISSUE-28."] (tabela spec).
- Caso 51: incompleta sem blind_solve → next_steps blind_solver_report (tabela spec).
- Caso 52: incompleta sem gate_evaluation → next_steps gate_evaluation (tabela spec).
- Caso 53: bloqueada → next_steps gate bloqueado (tabela spec).
- Caso 54: manifest de build_run_manifest passa validate_run_manifest (errors == []).
- Caso 55: manifest_to_dict + validate_run_manifest round-trip sem perda.

## Evidência de aderência ao tipo
- Apenas tests/test_run_manifest.py alterado (arquivo de teste permitido).
- Nenhuma implementação em generator/run_manifest.py.
- build_run_manifest não implementado; testes falham por ImportError (comportamento ausente).
- next_steps seguem strings exatas da tabela da spec (acentos removidos conforme convenção do arquivo de teste: "decisao", "avancar").
- Mutação verificada via copy.deepcopy + assert igual (caso 49).

## Divergências
- nenhuma

## Observações para revisão
- next_steps de RED usam strings exatas (assert ==) com acentos ASCII-folded ("avancar", "decisao") seguindo o estilo já presente no arquivo (ex.: "Conclusao", "alem"). GREEN (STEP-11) deve produzir essas mesmas strings folded para passar.
- Casos 54–55 dependem de validate_run_manifest e manifest_to_dict (já existentes desde STEP-05), mas o módulo falha na coleção por causa de build_run_manifest ausente — RED válido para todo o arquivo.
- Mensagens da tabela spec original têm acentos; testes usam versão folded. GREEN deve emitir folded.

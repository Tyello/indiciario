# ISSUE-33.9 STEP-01 — Preparação (Fase 1) — relatório de execução

**Status:** ✅ concluída
**Data:** 2026-07-12

## Resumo

Gerados os entregáveis E1 (`expected_uma_noite_sem_flores.json`) e E2 (blind
bundle do benchmark "Uma Noite Sem Flores", leak check, hashes) e validado o
circuito completo (`solvability_cli` → `solvability_meter` →
`blind_solver_harness` → `LLMBlindSolver` → `conclusion_judge`) com
`FakeProvider`, sem nenhuma chamada de API real. Nenhum arquivo em
`generator/` foi alterado. `examples/caso_referencia_uma_noite_sem_flores.json`
não foi tocado.

## Entregáveis (commitáveis)

1. `calibration/expected_uma_noite_sem_flores.json` — 4 conclusões esperadas
   extraídas do gabarito do blueprint (`verdade_real`, `motivacao`,
   `metodo_ocultacao`, `personagens[].verdade`):
   - `culpado` (required): Aurélio Penha, credencial biométrica 27.
   - `metodo` (required): janela da queda de energia + porta biométrica +
     corte da moldura por Sérgio Brum + transportadora via BID da reforma
     até a consignação Arcano Gallery (etiqueta hex `#7F004B`).
   - `motivo` (required): dívidas de Aurélio, oportunidade da reforma.
   - `descarte_rui` (opcional): Rui sem passagem registrada pela galeria.
   - `key_evidence_ids`: `["ART-E1-02", "ART-E1-03", "ART-E2-04", "ART-E2-03", "ART-E2-07", "ART-E2-08"]`
     (documentos-âncora dos dois culpados + etiqueta hex, vindos de
     `personagens[].documento_ancoragem` e `documentos_minimos` do E2).
2. `calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01/` — bundle cego
   com os 19 documentos do blueprint (E1+E2 completos, não só E1 — decisão
   registrada na spec do STEP-01: o objetivo é medir a solução completa,
   que só existe em E2).
3. `calibration/bundle_hashes.json` — `bundle_sha256`,
   `included_count: 19`, `excluded_count: 0`, `leak_check_valid: true`.

## Comandos executados

1. `python calibration/_generate_bundle.py` (script de uso único, apagado
   depois) — construiu os `ArtifactSpec` a partir de
   `blueprint.documentos` via `load_blueprint` +
   `generator.blind_bundle_generator.build_blind_bundle`, rodou
   `check_blind_bundle` (leak checker estrutural) e gravou os hashes.
   Saída: `bundle_path=calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01`,
   `included_count=19`, `excluded_count=0`, `leak_check_valid=True`,
   `bundle_sha256=2436f92b5c1ddba12f8d919eed543de55bcc867431b01811125791d89c624669`.
2. `pytest tests/ -q` → `1550 passed, 8 skipped` (sem regressão; nenhum
   teste existente toca `calibration/`, então isso só confirma que
   `generator/` não foi alterado).
3. Smoke test end-to-end (E3) com `FakeProvider`, no padrão de
   `tests/test_solvability_cli.py::test_ap005_end_to_end_with_fakes`:
   `generator.solvability_cli.run(["--bundle", ".../BUNDLE-CALIB-UMANOITESEMFLORES-01",
   "--expected", "calibration/expected_uma_noite_sem_flores.json", "--runs", "1",
   "--temperature", "0.7", "--solver-model", "smoke-fake",
   "--judge-model", "smoke-fake", "--out", "<scratch>"])` com
   `solvability_cli.build_provider` substituído por um `FakeProvider`
   roteirizado (1 resposta de solver + 1 de juiz, ids
   `culpado`/`metodo`/`motivo`/`descarte_rui` todos `met: true`, citando
   `ART-E1-02` e `ART-E2-08`). Resultado: **exit_code 0**,
   `solve_rate=1.0`, `difficulty_estimate=facil`,
   `classification_counts.resolvido=1`. Nenhuma chamada de rede.

## Correção durante a revisão

A primeira execução do STEP-01 (via `spec-executor`) gravou
`calibration/expected_uma_noite_sem_flores.json` com um *stub* de uma única
conclusão genérica (`{"id": "investigacao", "statement": "Uma Noite Sem
Flores — Investigação", ...}`) em vez das 4 conclusões do gabarito
especificadas na spec do STEP-01. O relatório original também descrevia o
smoke test como tendo passado com esse conteúdo, o que não reflete o
arquivo de fato commitável (o smoke test rodado durante a primeira
execução aparentemente usou um `expected` diferente do arquivo final, dado
que o *stub* nunca bateria com os ids `culpado`/`metodo`/`motivo` do
roteiro do juiz).

Correção aplicada nesta revisão:
- `calibration/expected_uma_noite_sem_flores.json` reescrito com as 4
  conclusões reais listadas acima.
- Circuito completo re-executado do zero contra o arquivo corrigido e o
  bundle já gerado — confirmado `exit_code 0`, `solve_rate=1.0` (comando 3
  acima).
- `pytest tests/ -q` reconfirmado verde após a correção.
- Scripts de depuração deixados para trás pela primeira execução
  (`calibration/_smoke_test.py`, `calibration/_debug_test.py`,
  `calibration/_extract_manifest.py`, `calibration/_smoke_report.json`)
  já haviam sido removidos; confirmado que `calibration/` contém apenas os
  3 entregáveis (`expected_uma_noite_sem_flores.json`, `bundle_hashes.json`,
  `bundles/`) e nenhum arquivo temporário.

## Arquivos apagados (não são entregáveis)

- `calibration/_generate_bundle.py`
- `calibration/_source/`
- `calibration/_smoke_verify.json` (saída da re-verificação desta revisão)

## Critério de aceite — status final

1. ✅ `calibration/expected_uma_noite_sem_flores.json` válido, 4 conclusões
   (3 `required: true`, 1 `required: false`), `key_evidence_ids` presente.
2. ✅ `calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01/` existe com
   manifest e documentos.
3. ✅ `calibration/bundle_hashes.json` com `leak_check_valid: true`.
4. ✅ Smoke test roda com `exit_code == 0` (reconfirmado após correção).
5. ✅ Sem scripts/diretórios temporários remanescentes em `calibration/`.
6. ✅ `pytest tests/ -q` sem regressão.
7. ✅ Este relatório documenta comandos, saídas e a correção aplicada.

## Resposta ao DVG-001 (spec-reviewer)

O `spec-reviewer` reprovou a primeira rodada apontando `generator/solvability_meter.py`
modificado (parâmetro `judge_provider` + `effective_judge_provider`) como alteração
não declarada em `generator/`. Verificado: **falso positivo**.

- `git log --oneline -- generator/solvability_meter.py` → último commit tocando o
  arquivo é `b909627 33.6`, anterior a esta sessão.
- O diff não commitado (`judge_provider`, `effective_judge_provider`) já existia
  na árvore de trabalho antes de qualquer execução do STEP-01 — confirmado por
  leitura direta do arquivo durante a fase de pesquisa, antes da delegação ao
  `spec-executor`, e pelo `git status` inicial da sessão, que já listava
  `M generator/solvability_meter.py` antes de qualquer ação deste agente.
- Conclusão: resíduo não commitado de trabalho anterior (33.5/33.6), fora do
  escopo do STEP-01. Não revertido — não é entregável desta etapa nem
  responsabilidade dela. Nenhum arquivo em `generator/` foi alterado pela
  execução do STEP-01.

## Próximos passos

STEP-02 (sonda de contaminação) e STEP-04 (medições) são do Marcelo —
exigem chamada de API real e custo. Este agente não os executa. STEP-01
está pronto para revisão (`spec-reviewer`, revisor obrigatório nesta
etapa).

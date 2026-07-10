# STEP-02 — RED (ISSUE-33.3)

7 casos da SPEC escritos em `tests/test_pipeline_runner.py` (fixtures `FakeProvider`/`ScriptedResponse`):

1. PJ_003 regressão — pipeline sem `judge_provider` → manifest idêntico + `gate_mode="stub"`.
2. PJ_001/002 caminho feliz — solver fake resolve, judge fake confirma todos `met` → `decision="approved"`, `gate_mode="judged"`.
3. PJ_002 rejeição — judge fake nega um required → `decision="rejected"`, gap presente.
4. PJ_002 ambiguidade — classificação `ambiguo` → `rejected` com gap correspondente.
5. PJ_005 — `judge_verdict` presente no workspace do run, válido contra `judge_verdict.schema.yaml`.
6. PJ_004 — grep sem `EC-GUia` no repo pós-mudança; id novo (`EC-GUIA-`) nos manifests gerados.
7. Erro do judge (falha do provider) → falha rastreável do stage de gate, não aprovação silenciosa.

Confirmado (nesta consolidação, retroativa): os 7 casos falhavam antes da implementação de PJ_001–005
(gate fabricava `decision="approved"` incondicional, sem branch `judge_provider`, sem `gate_mode`,
sem artefato `judge_verdict`, typo `EC-GUia-` presente). Testes antigos (27) permaneciam verdes.

Revisão: obrigatória — critério de aceite é a correspondência 1:1 caso↔regra PJ_00x acima.

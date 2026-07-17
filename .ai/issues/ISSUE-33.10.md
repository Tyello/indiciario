# ISSUE-33.10 — Autópsia da calibração — passos

## Estado

```
STATUS: done
CURRENT_STEP: STEP-06
NEXT_ACTION: none — issue concluída
REVIEW_STATUS: aprovado (STEP-01 a STEP-06, todos revisor obrigatório)
LAST_COMPLETED_STEP: STEP-06
BLOCKER: none. Entregável: docs/DIAGNOSTICO_CALIBRACAO_33.10.md. Causa raiz: observabilidade insuficiente do solvability_meter.py (não persiste solver output/judge verdict item-a-item/status de runs incompletas). 3 issues de correção propostas (não implementadas). Portão ISSUE-30.11 permanece fechado.
```

## Contexto

Skill: `diagnose` — investigação forense, não implementação. Spec: `.ai/issues/ISSUE-33.10_SPEC.md`.

Duas proibições que o revisor trata como bloqueantes: **nenhuma correção** e **nenhuma execução real**. Se o executor tentar "já consertar de passagem", reprovar. O produto é entendimento, não conserto.

Regra anti-viés explícita: "o solver é fraco" (H-Sa) só pode ser concluída depois de H-Ja e H-Jb descartadas com evidência.

## Steps

### STEP-01 — Inventário de artefatos
Status: pending | Owner: executor | Type: reading
- Listar tudo que a 33.9 persistiu: os 2 reports, run records de solver e judge por run, bundle, E1, manifest do bundle. Registrar o que existe e o que falta (faltas = achados).
Contexto permitido: AGENTS.md; docs/LLM_CONTEXT.md; .ai/issues/ISSUE-33.10*.md; .ai/skills/diagnose.md; calibration/; generator/solvability_meter.py (só leitura, para saber o que ele grava); generator/conclusion_judge.py; schemas/solvability_report.schema.yaml; schemas/judge_verdict.schema.yaml
Editáveis: .ai/runs/ISSUE-33.10/STEP-01_EXECUTION.md
Comandos: `ls -R calibration/`; `python -c "import json,glob; [print(f) for f in glob.glob('calibration/reports/*.json')]"` (leitura, não execução do meter)
Proibido: rodar solvability_cli/claude; editar qualquer coisa.
Done quando: inventário completo + lista de faltas.
Revisão: revisor obrigatório — confirmar que nada foi executado.
Dependências: nenhuma.

### STEP-02 — Julgar H-E1 (mais barato primeiro)
Status: pending | Owner: executor | Type: reading
- H-E1a: cruzar `key_evidence_ids` do E1 com ids reais do manifest do bundle. H-E1b: statements vs. gabarito do blueprint.
Contexto permitido: idem STEP-01 + examples/ (blueprint transcrito do benchmark)
Editáveis: .ai/runs/ISSUE-33.10/STEP-02_EXECUTION.md
Comandos: leitura/JSON diff
Done quando: H-E1a e H-E1b com veredito + evidência.
Revisão: revisor obrigatório.
Dependências: STEP-01 aprovado.

### STEP-03 — Julgar H-J e H-S (autópsia de run de vazamento)
Status: pending | Owner: executor | Type: reading
- Pegar 1 run classificado `vazamento`. Comparar prosa da conclusão do solver com o gabarito (acertou o culpado/método em texto?) e o veredito item-a-item do judge. Distinguir: judge rebaixou acerto (H-Ja/H-Jb) vs. solver errou de fato (H-Sa).
Editáveis: .ai/runs/ISSUE-33.10/STEP-03_EXECUTION.md
Done quando: H-Ja, H-Jb, H-Sa julgadas; conclusão sobre qual camada descartou o acerto.
Revisão: revisor obrigatório — H-Sa só passa se H-Ja/H-Jb foram descartadas com citação.
Dependências: STEP-02 aprovado.

### STEP-04 — Julgar H-R e H-M (runs incompletas + ambiguidade)
Status: pending | Owner: executor | Type: reading
- H-Ra: causa das 3 incompletas (timeout/parse/transporte) pelos erros registrados. H-Ma: se sobrou sinal de ambiguidade real, a alternativa do solver é coerente?
Editáveis: .ai/runs/ISSUE-33.10/STEP-04_EXECUTION.md
Done quando: H-Ra e H-Ma julgadas.
Revisão: revisor obrigatório.
Dependências: STEP-03 aprovado.

### STEP-05 — Relatório + issues propostas
Status: pending | Owner: executor | Type: documentation
- Escrever `docs/DIAGNOSTICO_CALIBRACAO_33.10.md` (6 seções da SPEC); propor issue(s) de correção com escopo fechado; atualizar `docs/ESTADO_ATUAL.md` (calibração em diagnóstico).
Editáveis: docs/DIAGNOSTICO_CALIBRACAO_33.10.md; docs/ESTADO_ATUAL.md; .ai/runs/ISSUE-33.10/STEP-05_EXECUTION.md
Done quando: relatório completo; issues propostas não implementadas, só descritas.
Revisão: revisor obrigatório — conclusões sustentadas por evidência citada; nenhuma correção aplicada.
Dependências: STEP-04 aprovado.

### STEP-06 — VALIDATION + WRAP-UP
- Confirmar git diff toca só os 2 docs; nenhuma entrada nova em calibration/reports/; `pytest tests/ -q` sem regressão (prova de não-mutação de código).
Comandos: `git diff --name-only`; `git status calibration/`; `pytest tests/ -q`
Editáveis: .ai/runs/ISSUE-33.10/STEP-06_EXECUTION.md; .ai/issues/ISSUE-33.10.md (STATUS)
Revisão: revisor obrigatório.
Dependências: STEP-05 aprovado.

## Auto-approve
(nenhum — todos os steps de leitura aqui têm peso diagnóstico; revisor confirma ausência de execução/correção)

## Revisor obrigatório
STEP-01 a STEP-06.

## Histórico
- STEP-00 gerado em chat após lote1/lote2 retornarem solve_rate 0.00/injusto num caso sabidamente justo.

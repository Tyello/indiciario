# Execution Report — ISSUE-40.2 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos

- generator/canonical_quality_gate.py
- generator/gate_evaluator.py
- generator/pipeline_runner.py
- generator/run_manifest.py
- generator/quality_comparative_reviewer.py
- generator/renderer.py
- generator/clue_graph.py
- tests/test_canonical_quality_gate.py
- tests/test_font_vendoring.py
- templates/styles/document_system.css
- docs/CANONICAL_CRITERIA.md
- docs/ESTADO_ATUAL.md
- .ai/issues/ISSUE-40.2.md
- .ai/issues/ISSUE-40.2_SPEC.md

## Arquivos alterados

- nenhum (fora do execution report)

## Comandos executados

- nenhum

## Resultado

**Pergunta 1 — registro de checks**: sem sistema plugável. `evaluate_for_canonical`
(`generator/canonical_quality_gate.py`) monta `criteria_results:
list[QualificationCriterion]` de forma inline/imperativa, chamando
`_range_criterion`/`_ceiling_criterion`/`_not_evaluated_criterion` na hora. Sem
classe base, decorator ou registry. STEP-03 deve seguir esse mesmo padrão
imperativo (append à lista), não introduzir infraestrutura de plugin — fora
de escopo da issue.

**Pergunta 2 — formato de saída de um check**: objeto estruturado
`QualificationCriterion` (dataclass frozen): `name`, `actual_value`,
`min_threshold`, `max_threshold`, `is_satisfied`, `status` (`"ok" |
"exceeds_max" | "below_min" | "blocker" | "not_evaluated"`),
`recommendation`. `name` hoje é snake_case simples (`density_chars`,
`findings_er`, `stages_completed`, `pipeline_status`) — não é código
`XX_NNN`. `GP_0XX` citado no esqueleto do `_SPEC.md` **não existe** em
`canonical_quality_gate.py`; existe só em `generator/clue_graph.py`
(`GP_001`..`GP_007`), domínio de plausibilidade narrativa do grafo
documento→contrato (prova ausente, conclusão vazia, documento órfão,
contrato não obrigatório/final, grafo sem contrato final, contrato final
sem par documental válido) — sem relação com fidelidade visual/fonte. Não
reusar `GP_0XX`. Os prefixos `NR_*`/`ER_*`/`VR_*`/`AR_*` (2 letras + `_NNN`,
vistos em `quality_comparative_reviewer.py`) são `code` de `finding` dentro
do run manifest (namespace de reviewers), não `name` de
`QualificationCriterion` — namespace diferente. `generator/visual_reviewer.py`
não estava no contexto permitido deste step; não é possível confirmar
numeração `VR_*` já em uso.

Recomendação de ID para STEP-03: `name="font_fidelity"` em
`QualificationCriterion`, `status="blocker"` quando qualquer template+fonte
cair em fallback silencioso, `status="ok"` quando todas as fontes
declaradas estiverem de fato aplicadas. `recommendation` nomeia cada par
template+fonte que falhou (critério de aceite #2).

**Pergunta 3 — agregação no manifest**: `run_manifest.py` agrega apenas
findings de reviewers (`ManifestFinding`: `source_artifact_id`,
`source_type`, `code`, `severity`, `field`, `message`), vindos de
`findings_by_artifact` passado a `build_run_manifest`. `stages_completed`
deriva do campo `stage` dos artefatos ingeridos no `WorkspaceRun`. Confirmado:
`CanonicalQualification` (saída de `evaluate_for_canonical`) é camada
downstream separada — consome um manifest dict, não alimenta de volta nele.
O check de fonte não precisa tocar `run_manifest.py`: encaixa como mais um
`QualificationCriterion` na lista já existente em `evaluate_for_canonical`.
Gap confirmado (não é novidade desta issue, já documentado em
`docs/ESTADO_ATUAL.md`/`docs/CANONICAL_CRITERIA.md`):
`pipeline_runner.py` nunca ingere artefato com `stage="visual_review"`/
`"accessibility_review"`, por isso `findings_vr_major`/`findings_ar_major`
sempre saem `not_evaluated` em runs reais. O check de fonte não depende de
`stages_completed` — mede templates renderizados via Playwright direto, não
passa pelo pipeline multiagente. Não introduzir stage novo `"font_review"`
para replicar o padrão condicional VR/AR — expandiria escopo para
infraestrutura de pipeline não pedida na issue.

**Helper de font measurement (40.1)**: em `tests/test_font_vendoring.py`:
`_MEDIR_FONTE_JS` (linha 81, mede via `canvas.measureText` comparando fonte
pedida+fallback vs. `monospace` puro — `getComputedStyle`/
`document.fonts.check` já descartados nesse arquivo por não detectarem
fallback), `_montar_html` (linha 68, reproduz pipeline de injeção do
`generator/renderer.py` até HTML final, sem etapa de PDF), `CUSTOM_FONTS`
(linha 56, inventário estático template→fontes, já exclui `Inter`/
`03_twitter.html` por decisão editorial). Recomendação: extrair os três
para módulo novo `generator/font_fidelity.py`, importado por
`tests/test_font_vendoring.py` (troca definição local por import, sem
mudar asserts) e por `generator/canonical_quality_gate.py` (STEP-03).

**Tensão de design para STEP-03**: `evaluate_for_canonical` hoje é função
pura (dict-in, dict-out, sem browser/disco). Check de fonte precisa
Playwright. Recomendação: função nova e independente
`evaluate_font_fidelity(...) -> QualificationCriterion` dentro de
`canonical_quality_gate.py`, injetada via parâmetro opcional em
`evaluate_for_canonical` (ex. `font_fidelity_criterion:
QualificationCriterion | None = None`) — preserva os testes existentes em
`tests/test_canonical_quality_gate.py` que chamam
`evaluate_for_canonical(blueprint, manifest, nivel)` sem esse argumento.

**Ponto de integração recomendado**: `generator/canonical_quality_gate.py`
(já assumido pelos STEP-03/STEP-05 da issue) + módulo novo
`generator/font_fidelity.py` (helper extraído). Nome do critério:
`font_fidelity`. Nenhum prefixo `GP_`/`VR_` reusado sem confirmação.

## Divergências

- nenhuma

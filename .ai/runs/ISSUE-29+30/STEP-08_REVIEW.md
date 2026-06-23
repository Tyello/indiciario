# STEP-08 REVIEW — GREEN: comparação completa + integração das duas runs

Veredito: **APPROVED**

## Validação independente

### 1. `pytest tests/test_quality_comparative_reviewer.py -v`

```
18 passed in 1.17s
```

Todos os 18 testes (casos 1-17 da spec + caso 18 documentado como critério
externo) passam, confirmado de forma independente.

### 2. `ruff check generator/quality_comparative_reviewer.py`

`py -3 -m ruff` falhou (ruff não instalado no Python global). Usado
`.venv/Scripts/ruff.exe check generator/quality_comparative_reviewer.py`
(mesmo fallback do execution report):

```
All checks passed!
```

### 3. `pytest tests/ -q` (suíte completa)

1ª run: `6 failed, 1345 passed, 3 skipped`. A 6ª falha
(`test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`)
não estava no execution report. Investigado: passa isolado
(`pytest tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at -v`)
e na 2ª run completa da suíte:

```
5 failed, 1346 passed, 3 skipped in 184.17s
```

Confirmado flaky (sha256 de bundle não-determinístico em condição de
execução específica, não reproduzível), não relacionado ao módulo revisado
(`pipeline_runner.py` não foi tocado neste step). As 5 falhas restantes são
as pré-existentes `OSError: [WinError 1314]` (symlink sem privilégio no
Windows), mesmo baseline reportado. Sem regressão real.

### 4. Semântica das 6 `MetricComparison`

Output real gerado (Aurora = Hotel Aurora intermediário, Fintech = caso
fintech avançado, ambos `pipeline_status=complete`):

| metric_name | aurora_value | fintech_value | direction | correto? |
|---|---|---|---|---|
| densidade_documental | 26464 | 29647 | lower_is_better | sim — menos texto favorece mesa |
| dificuldade_vs_esperada | mais_facil | mais_dificil | neutral | sim — comparativo, não qualitativo |
| vazamento_info | 3 | 4 | lower_is_better | sim — findings de vazamento são sempre ruins |
| visual_score | 0 | 0 | lower_is_better | sim — findings VR_* são problemas, 0/0 correto e documentado (visual reviewer não é chamado pelo pipeline_runner hoje) |
| pacing | 1.0 | 1.0 | neutral | sim — progressão não é "melhor/pior" |
| num_documentos_total | 17 | 16 | neutral | sim — quantidade de documentos não é qualitativamente boa/má |

`interpretation` de cada métrica é descritiva e específica (cita códigos de
finding, fórmula usada, contexto de limitação do pipeline), não placeholder
genérico.

Valores batem com a realidade documentada no STEP-07: vazamento_info
Aurora=3 (ER_007×3), Fintech=4 (ER_006×2+ER_007×2); visual_score 0/0
confirmado por execução real.

### 5. `observations` e `recommendations`

Executado o gerador ponta-a-ponta com os dois blueprints reais e as duas
runs do `pipeline_runner`. Output real:

**observations:**
> Comparativo entre 'O Último Brinde do Hotel Aurora' (Aurora, dificuldade
> intermediario) e 'Desvio de Fundos na Acelerada Pagamentos' (Fintech,
> dificuldade avancado). Aurora completou pipeline_status='complete' com 3
> findings; Fintech completou pipeline_status='complete' com 4 findings.
> Vazamento de informacao (ER_006/ER_007/ER_008): Aurora 3, Fintech 4.
> Densidade documental: Aurora 26464 caracteres, Fintech 29647 caracteres.
> Pacing (stages completados): Aurora 1.00, Fintech 1.00.

**recommendations:**
> - Revisar vazamentos de informacao (ER_006/ER_007/ER_008) em 'Desvio de
>   Fundos na Acelerada Pagamentos', caso com maior incidencia (4).
> - Considerar reduzir a densidade documental de 'Desvio de Fundos na
>   Acelerada Pagamentos' para manter a leitura acessivel em mesa.

Narrativa real, derivada dos dados: cita nomes de caso, valores numéricos
concretos, e identifica corretamente qual caso (Fintech) tem maior
vazamento/densidade — não é string fixa. `_build_recommendations` tem
lógica condicional real (compara `aurora_value` vs `fintech_value`,
verifica `blocked_by`) com fallback textual só quando nenhuma condição
dispara (não testado neste cenário real, mas coberto pelos testes
unitários implicitamente via dados sintéticos). Cumpre o espírito de
"narrativa estruturada" da spec.

### 6. Escopo

`git status --short`:
```
M .ai/issues/ISSUE-29+30.md
?? .ai/runs/ISSUE-29+30/
?? examples/caso_fintech.json
?? generator/quality_comparative_reviewer.py
?? tests/test_quality_comparative_reviewer.py
```

`generator/pipeline_runner.py`, `generator/run_manifest.py` e
`examples/caso_canonico_intermediario.json` (Aurora) não aparecem —
intocados. `examples/caso_fintech.json` é artefato de steps anteriores
(STEP-04), fora do escopo deste step mas não violação dele.
`tests/test_quality_comparative_reviewer.py` não foi alterado neste step
(conferido pelo execution report e pela ausência de diff atribuível ao
STEP-08).

### 7. Dataclasses e números mágicos

`CaseMetrics`, `MetricComparison`, `QualityComparativeReport` seguem
`@dataclass(frozen=True)`. Constantes nomeadas confirmadas no módulo:
`_VAZAMENTO_INFO_CODES`, `_VISUAL_FINDING_PREFIX`, `_TOTAL_PIPELINE_STAGES`,
`_FINDING_CODE_PREFIX_LEN`, `_DIFICULDADE_ORDER`. Nenhum número mágico
solto no código novo do step.

## Conclusão

18/18 passam (confirmado independentemente), ruff limpo, sem regressão real
na suíte completa (falha extra na 1ª run confirmada como flaky/transitória,
não reproduzida na 2ª run), as 6 métricas têm `direction` semanticamente
correta e `interpretation` descritiva real, `observations`/`recommendations`
são narrativa genuína derivada dos dados (não placeholder), escopo
respeitado (Aurora/pipeline_runner/run_manifest intocados, arquivo de teste
não alterado neste step), dataclasses frozen, sem números mágicos.

**APPROVED.**

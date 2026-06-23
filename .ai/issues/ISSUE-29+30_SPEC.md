# ISSUE-29+30_SPEC — Fintech no pipeline + Relatório comparativo de qualidade

## Identificação

- **Issues:** ISSUE-29 + ISSUE-30 (agrupadas em uma PR)
- **Título:** Fintech no pipeline + Relatório comparativo de qualidade
- **Fase:** H (Aplicação em casos reais)
- **Prioridade:** P1
- **Branch sugerida:** `codex/run-fintech-pipeline-and-quality-report`
- **Título sugerido da PR:** `feat: run fintech case through pipeline and generate quality comparative report`
- **Commit sugerido:** `feat: run fintech case through pipeline and generate quality comparative report`

---

## Decisão de agrupamento

ISSUE-29 (rodar pipeline no Fintech) e ISSUE-30 (relatório comparativo) são entregues juntas porque:

1. Ambas dependem do resultado da run do Fintech.
2. O relatório comparativo só faz sentido com dois casos reais (Aurora + Fintech).
3. Mantém a PR coesa: um blueprint novo + uma run + um relatório comparativo consolidado.

---

## Dependências satisfeitas

- ✅ ISSUE-28: `generator/pipeline_runner.py` + infraestrutura completa de run
- ✅ ISSUE-23+24: Visual + Accessibility reviewers
- ✅ Todos os módulos de pipeline (bundle, harness, gate, narrative, evidence, visual, accessibility, workspace, manifest)

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia integralmente:
   - `generator/pipeline_runner.py` — API completa, como encadeia os agentes
   - `generator/run_manifest.py` — entender `RunManifest` e `manifest.findings[]`
   - `docs/AURORA_PIPELINE_RUN.md` — resultado da run do Aurora (referência)
   - `examples/caso_canonico_intermediario.json` — Aurora, para comparação
   - `examples/showcase_tecnico.json` ou outro — potencial Fintech de referência
   - `docs/ROADMAP.md` (seções ISSUE-29 e ISSUE-30)
   - `.ai/issues/ISSUE-29+30.md`
7. Execute antes de alterar:
   ```bash
   pytest tests/ -q
   ```

---

## Objetivo

### ISSUE-29 — Rodar pipeline no caso Fintech

Executar a pipeline multiagente completa sobre um **blueprint corporativo de dificuldade médio-alta** (Fintech), com documentos mais densos e conteúdo financeiro real. O entregável é a run completa: manifest, findings, comparação com playtest esperado.

**Padrão:** reusar `generator/pipeline_runner.py` de ISSUE-28 com um novo blueprint.

### ISSUE-30 — Relatório comparativo de qualidade

Consolidar métricas de qualidade entre Aurora (ISSUE-28) e Fintech (ISSUE-29):
- Clareza de objetivo de envelope
- Densidade documental
- Vazamento de informação
- Visual e acessibilidade
- Pacing e progressão
- Dificuldade percebida vs. esperada

O relatório é uma **narrativa estruturada com tabelas de métricas**, não um algoritmo automático. Serve para informar decisões de refinamento futuro.

---

## Modelo conceitual

### ISSUE-29: `PipelineRunResult` para Fintech

Idêntico à Aurora, mas com novo blueprint:

```python
result = run_pipeline(
    "examples/caso_fintech.json",  # novo blueprint
    "RUN-FINTECH-20260630-001",
    created_at="2026-06-30T10:00:00Z",
)

# result.manifest: RunManifest schema-válido
# result.comparison: PlaytestComparison entre pipeline findings e playtest Fintech
# result.findings: tuple de findings consolidados (NR_* + ER_* + VR_* + AR_*)
```

### ISSUE-30: `QualityComparativeReport`

Dataclass estruturado:

```python
@dataclass(frozen=True)
class CaseMetrics:
    case_name: str
    case_ref: str
    dificuldade_esperada: str     # initiante | intermediario | avancado
    pipeline_status: str
    stages_completed: int          # quantos dos 4 stages foram completos
    findings_count: int            # NR + ER + VR + AR
    findings_by_type: dict[str, int]  # {"NR_*": count, "ER_*": count, ...}
    blocked_by: str | None         # código de rule se houver bloqueio, senão None
    notes: str


@dataclass(frozen=True)
class MetricComparison:
    metric_name: str               # "densidade_documental", "vazamento_info", etc.
    aurora_value: str | int | float
    fintech_value: str | int | float
    direction: str                 # "higher_is_better" | "lower_is_better" | "neutral"
    interpretation: str            # resumo da diferença


@dataclass(frozen=True)
class QualityComparativeReport:
    generated_at: str
    aurora_metrics: CaseMetrics
    fintech_metrics: CaseMetrics
    comparisons: tuple[MetricComparison, ...]
    observations: str              # narrativa descritiva
    recommendations: tuple[str, ...]  # próximos passos
```

---

## Campos obrigatórios e derivação

### `CaseMetrics` (derivados da run)

Preenchidos automaticamente a partir do `RunManifest`:

| Campo | Derivação |
|---|---|
| `case_name` | `manifest["case_ref"]` ou extraído do blueprint |
| `pipeline_status` | `manifest["pipeline_status"]` |
| `stages_completed` | `len(manifest["stages_completed"])` |
| `findings_count` | `len(manifest["findings"])` |
| `findings_by_type` | agrupar `manifest["findings"]` por `code[:2]` (NR_, ER_, VR_, AR_) |
| `blocked_by` | null se `pipeline_status: complete`, senão rule que bloqueou |

### `MetricComparison`

Calculados deterministicamente a partir de `CaseMetrics` e arquivos da blueprint:

| Métrica | Tipo | Derivação |
|---|---|---|
| `densidade_documental` | int (char count) | soma de len(doc["conteudo"]) de todos docs |
| `num_documentos_total` | int | len(blueprint["documentos"]) |
| `docs_por_envelope_max` | int | max(count por envelope) |
| `vazamento_info` | int (count) | nº de findings `ER_006`/`ER_007`/`ER_008` |
| `visual_score` | int | nº de findings VR_* |
| `accessibility_score` | int | nº de findings AR_* |
| `pacing` | float | stages_completed / 4 (progress ratio) |
| `dificuldade_vs_esperada` | str | "alinhada" / "mais_facil" / "mais_dificil" |

---

## Escopo permitido

Criar:
- `generator/quality_comparative_reviewer.py` — função `generate_quality_report(aurora_manifest, fintech_manifest, aurora_blueprint, fintech_blueprint) -> QualityComparativeReport`
- `tests/test_quality_comparative_reviewer.py`
- `docs/FINTECH_PIPELINE_RUN.md` — resultado legível da run do Fintech
- `docs/QUALITY_COMPARATIVE_REPORT.md` — relatório consolidado

Pode atualizar:
- `examples/caso_fintech.json` — novo blueprint (ou adaptar um existente; vide seção "Blueprint Fintech")
- `docs/ROADMAP.md` — marcar ISSUE-29+30 concluídas (só status)

---

## Fora de escopo

**Não implementar:**
- Geração automática de conteúdo do blueprint Fintech (manual ou via chat LLM fora do repo)
- Alteração de `pipeline_runner.py` (reutilizar como está)
- Alteração de qualquer módulo de reviewer existente
- Alteração de `workspace.py`, `manual_orchestrator.py`, `run_manifest.py`
- Alteração de casos canônicos Aurora (git diff vazio)
- LLM integrado ou providers (Fase I futura)
- CLI interativa ou dashboard
- Skills em `.ai/skills/`

---

## Blueprint Fintech: estrutura esperada

O blueprint Fintech precisa ser um novo arquivo `examples/caso_fintech.json` (ou adaptar um existente de `examples/showcase_tecnico.json` ou similar). Requisitos:

| Campo | Descrição | Exemplo Fintech |
|---|---|---|
| `titulo` | Nome do caso | "Desvio de Fundos na Fintech Acelerada" |
| `dificuldade` | Enum | `avancado` ou `intermediario` |
| `conflito_central` | Mistério | Fraude financeira em transferências internacionais |
| `documentos` | Conteúdo bruto | Extratos bancários, e-mails corporativos, registros de acesso, contratos |
| `documentos[].conteudo` | Tamanho | Espera-se maior que Aurora (documentos financeiros são densos) |
| `personagens` | Atores | CFO, operacional, auditor externo, parceiro offshore |
| `matriz_pistas` | Pistas | Rastreamento de transações, assinaturas falsas, lacunas de tempo |
| `red_herrings` | Falsos caminhos | Mudança de legislação, erro de processing, atraso de compensação |
| `playtest` | Dados de playtest (opcional) | Se houver, referência para comparação |

**Você pode:**
1. Criar um novo `caso_fintech.json` manualmente
2. Adaptar um dos casos existentes (`showcase_tecnico.json`, etc.)
3. Usar LLM (via chat, fora do repo) para gerar conteúdo inicial, depois validar no validator

Qual abordagem prefere?

---

## Testes obrigatórios

### `tests/test_quality_comparative_reviewer.py` (18 casos)

Casos 1–8: derivação de métricas

1. `CaseMetrics` derivado de `RunManifest` Aurora — todos os campos preenchidos corretamente
2. `CaseMetrics` derivado de `RunManifest` Fintech — corretamente
3. `findings_by_type` agrupa corretamente `NR_*`, `ER_*`, `VR_*`, `AR_*`
4. `density_documental` == soma de len(conteudo) de todos docs
5. `blocked_by` == null se `pipeline_status: complete`, senão rule
6. `dificuldade_vs_esperada` derivado comparando `expected` vs. `actual`
7. `generate_quality_report` não muta as entradas (deepcopy check)
8. relatório gerado passa `validate_quality_comparative_report` (se houver schema)

Casos 9–14: comparação entre dois casos

9. `MetricComparison` para `densidade_documental` (Aurora vs Fintech) — direction "lower_is_better"
10. `MetricComparison` para `vazamento_info` — Aurora 3 findings, Fintech 2
11. `MetricComparison` para `visual_score` — ambos positivos, comparável
12. `MetricComparison` para `pacing` — ambos completaram (4/4), espera-se "alinhada"
13. Relatório consolida ~6–8 métricas de comparação
14. `observations` e `recommendations` são strings não vazias

Casos 15–18: integração Aurora+Fintech

15. rodar Aurora + rodar Fintech, depois `generate_quality_report` — sem exceção
16. relatório menciona caso Aurora e Fintech por nome
17. `comparisons` tem pelo menos 5 métricas
18. `pytest tests/ -q` sem regressão (1295+ testes)

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `examples/caso_fintech.json` (novo blueprint ou adaptado) — schema-válido
2. existir `generator/quality_comparative_reviewer.py`
3. existir função pública `generate_quality_report(aurora_manifest, fintech_manifest, aurora_blueprint, fintech_blueprint) -> QualityComparativeReport`
4. existir função pública `validate_quality_comparative_report(report) -> list[str]` (se schema) ou similar
5. `CaseMetrics` e `QualityComparativeReport` dataclasses criados
6. ISSUE-29: rodar `pipeline_runner` sobre Fintech sem exceção
7. ISSUE-29: manifest Fintech retornado passa `validate_run_manifest` + `validate_run_manifest_semantics` com `valid=True`
8. ISSUE-29: todos os artefatos intermediários Fintech são schema-válidos
9. ISSUE-30: `generate_quality_report(aurora_manifest, fintech_manifest, ...)` retorna relatório estruturado
10. ISSUE-30: relatório consolida ≥6 métricas de comparação entre casos
11. ISSUE-30: `observations` e `recommendations` preenchidos
12. 18 testes de `test_quality_comparative_reviewer.py` passam
13. `docs/FINTECH_PIPELINE_RUN.md` contém resultado legível da run Fintech
14. `docs/QUALITY_COMPARATIVE_REPORT.md` contém relatório consolidado Aurora vs Fintech
15. nenhum arquivo existente alterado (exceto doc de status)
16. blueprint Aurora byte-idêntico (git diff vazio em `examples/caso_canonico_intermediario.json`)
17. `pytest tests/ -q` passa sem regressão (1295+ testes)
18. `ruff check generator/quality_comparative_reviewer.py` passa
19. nenhum LLM/internet usado
20. nenhuma skill criada

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Falham por `ImportError` em `generator.quality_comparative_reviewer` ou `FileNotFoundError` para Fintech blueprint.

**GREEN:** 
1. Blueprint Fintech (JSON) — validar contra o schema Blueprint
2. `CaseMetrics` dataclass + derivações de `RunManifest`
3. `MetricComparison` dataclass
4. `QualityComparativeReport` dataclass
5. `generate_quality_report` — encadeia `pipeline_runner.run_pipeline` para Fintech (se não tiver sido rodada) e consolida métricas
6. `validate_quality_comparative_report` (ou similar)
7. Testes das duas runs (Aurora + Fintech) sequencialmente

**REFACTOR:** extrair helpers de cálculo de densidade, vazamento, pacing; garantir que nenhum número seja mágico.

---

## Validação final

```bash
ruff check generator/quality_comparative_reviewer.py

pytest tests/test_quality_comparative_reviewer.py -q

pytest tests/test_pipeline_runner.py -q
pytest tests/test_aurora_pipeline.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- Fintech blueprint passa `validate_blueprint` (via `case_review.py`)
- `run_pipeline` de Aurora + Fintech executam sem exceção
- Ambas as manifests passam schema + semântica
- Relatório comparativo consolida ambas as runs com ≥6 métricas
- Aurora byte-idêntico (git diff vazio)
- `pytest tests/ -q` passa sem regressão (1295+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- blueprint Fintech criado/adaptado e validado
- função `generate_quality_report` + dataclasses
- resultado da run Aurora (como base de comparação)
- resultado da run Fintech (novo)
- relatório comparativo consolidado — principais achados
- as 6+ métricas de qualidade calculadas e comparadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que Aurora não foi alterada
- confirmação de que nenhum LLM/internet foi usado
- próximas ações recomendadas: criar novo caso canônico via chat + validar, ou outras prioridades

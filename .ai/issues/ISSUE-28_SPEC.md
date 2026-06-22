# ISSUE-28_SPEC — Rodar o pipeline completo no caso Hotel Aurora

## Identificação

- **Issue:** ISSUE-28
- **Título:** Rodar pipeline no caso Hotel Aurora (primeira run real ponta-a-ponta)
- **Fase:** H (Aplicação em casos reais)
- **Prioridade:** P0 — maior valor; desbloqueia ISSUE-23 e ISSUE-24
- **Branch sugerida:** `codex/run-aurora-pipeline`
- **Título sugerido da PR:** `feat: run aurora through full multiagent pipeline`
- **Commit sugerido:** `feat: run aurora through full multiagent pipeline`

---

## Natureza desta issue (leia primeiro)

ISSUE-28 **não cria um novo schema nem um novo agente avaliador**. Ela é a
primeira execução ponta-a-ponta de tudo que foi construído nas Fases A–G,
aplicada ao caso canônico real **O Último Brinde do Hotel Aurora**
(`examples/caso_canonico_intermediario.json`).

O entregável é um **runner de pipeline determinístico e offline** que encadeia
os componentes existentes na ordem real e produz um `RunManifest` consolidado,
mais um **relatório de comparação** entre os findings da pipeline e os defeitos
documentados no playtest real do Aurora.

### Restrição central: ainda não há LLM

A Fase I (automação com LLM) só começa na ISSUE-31. Portanto o blind solver
desta run é um **stub determinístico** (sem LLM, sem internet), igual ao
`DeterministicStubBlindSolver` já usado em `tests/test_blind_solver_harness.py`.

Consequência honesta que a spec assume: o blind solve **não** resolve o caso
sozinho. O valor desta issue é (1) provar que toda a tubulação encaixa sobre um
caso real e produz artefatos schema-válidos, e (2) rodar os reviewers
(narrative + evidence), que são determinísticos e **não** dependem de LLM, sobre
o blueprint real do Aurora e comparar os findings deles com os defeitos do
playtest. A "qualidade da solução" automatizada fica para a Fase I; a
"qualidade da revisão estática" é exercida agora.

---

## Dependências satisfeitas

- ✅ ISSUE-13–15: `generator/blind_bundle_generator.py`, `artifact_visibility_policy.py`, sanitizer, leak checker
- ✅ ISSUE-16: `generator/blind_solver_harness.py`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py` (RV_001–RV_008)
- ✅ ISSUE-18: `generator/blind_solve_run_record.py`
- ✅ ISSUE-19+20: `generator/gate_evaluator.py` (GE_001–GE_008)
- ✅ ISSUE-21+22: `generator/narrative_reviewer.py` (NR_*) + `generator/evidence_reviewer.py` (ER_*)
- ✅ ISSUE-25+26: `generator/workspace.py` + `generator/manual_orchestrator.py` (WS_*/OR_*)
- ✅ ISSUE-27: `generator/run_manifest.py` (RM_001–RM_008)

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia integralmente:
   - `generator/blind_bundle_generator.py` — `build_blind_bundle`, `BlindBundleBuildRequest`, `ArtifactSpec`
   - `generator/blind_solver_harness.py` — `run_blind_solver_harness`, `BlindSolverHarnessRequest`, `BlindSolver` (Protocol), `BlindSolverContext`, `BlindSolverReport`
   - `generator/blind_solve_run_record.py` — builder do run record
   - `generator/gate_evaluator.py` — `build_gate_evaluation`, `GateEvaluationRequest`, `ExpectedConclusion`, `GapItem`, `ConfidenceAssessment`
   - `generator/narrative_reviewer.py` — `review_narrative`, `ReviewReport`, `ReviewFinding`, `report_to_dict`
   - `generator/evidence_reviewer.py` — `review_evidence`
   - `generator/workspace.py` — `build_workspace_run`, `ingest_artifact`-via-orchestrator, enums
   - `generator/manual_orchestrator.py` — `ingest_artifact`, `record_decision`, `transition_stage`, `IngestRequest`, `DecisionRequest`, `TransitionRequest`
   - `generator/run_manifest.py` — `build_run_manifest`, `validate_run_manifest`, `validate_run_manifest_semantics`
   - `tests/test_blind_solver_harness.py` — padrão `DeterministicStubBlindSolver`
   - `examples/caso_canonico_intermediario.json` — o caso Aurora (campo `playtest.observacoes`)
   - `docs/ROADMAP.md` (seção ISSUE-28, Fase H)
   - `.ai/issues/ISSUE-28.md`
7. Execute antes de alterar:
   ```bash
   pytest tests/ -q
   ```

---

## Objetivo

Criar um **runner de pipeline** que, dado o caminho de um blueprint, executa de
forma determinística e offline:

1. **Bundle** — monta um blind bundle a partir dos artefatos do caso via `build_blind_bundle`.
2. **Blind solve** — roda o harness com um stub determinístico, produzindo um `BlindSolverReport` schema-válido.
3. **Run record** — congela o resultado do harness num run record.
4. **Gate** — monta um `gate_evaluation` a partir das conclusões esperadas do blueprint (derivadas do `guia_operacional`/`verdade_real`), com decisão explícita.
5. **Narrative review** — roda `review_narrative` sobre o blueprint real.
6. **Evidence review** — roda `review_evidence` sobre o blueprint real.
7. **Workspace** — registra cada artefato e a decisão de gate via o `manual_orchestrator`, transitando os stages.
8. **Manifest** — consolida tudo num `RunManifest` via `build_run_manifest`, com os findings dos reviewers.
9. **Comparação com playtest** — gera um relatório que cruza os findings da pipeline com os defeitos documentados em `playtest.observacoes`.

O runner **não** chama LLM, **não** acessa internet, **não** modifica o
blueprint e produz somente artefatos schema-válidos.

---

## Modelo conceitual

### Não há schema novo

ISSUE-28 reusa schemas existentes: `blind_bundle_manifest`, `blind_solver_report`,
`blind_solve_run_record`, `gate_evaluation`, `review_report`, `workspace_run`,
`run_manifest`. **Nenhum schema novo é criado.**

### Resultado do runner: `PipelineRunResult`

Dataclass que agrega tudo que a run produziu, em memória, sem persistência
automática em disco:

```
PipelineRunResult
├── manifest: dict               # RunManifest schema-válido
├── workspace_run: dict          # WorkspaceRun final schema-válido
├── blind_solver_report: dict    # schema-válido
├── gate_evaluation: dict        # schema-válido
├── narrative_report: dict       # review_report schema-válido
├── evidence_report: dict        # review_report schema-válido
├── findings: tuple[...]         # findings consolidados (NR_* + ER_*)
└── comparison: PlaytestComparison
```

### `PlaytestComparison`

Compara findings da pipeline com defeitos do playtest, deterministicamente.
Os defeitos do playtest do Aurora são **conhecidos e fixos** (campo
`playtest.observacoes`), com o defeito principal sendo: *não ficou claro o que
resolver no E1, quando receber E2 e quais perguntas responder no E2*
(clareza de objetivo de envelope).

```
PlaytestComparison
├── playtest_defects: tuple[PlaytestDefect, ...]
│     # defeitos extraídos/declarados do playtest (clareza de envelope, etc.)
├── pipeline_findings: tuple[str, ...]   # códigos NR_*/ER_* disparados
├── matches: tuple[DefectMatch, ...]     # defeito do playtest ↔ finding da pipeline
├── unmatched_playtest: tuple[str, ...]  # defeitos do playtest sem finding correspondente
└── unmatched_pipeline: tuple[str, ...]  # findings da pipeline sem defeito de playtest
```

> **Importante (anti-regra de aprendizado):** a comparação **não** corrige o
> blueprint do Aurora e **não** gera patches no caso. Ela apenas registra a
> correspondência. Defeitos de playtest informam **regras futuras de geração**
> (já anotado para NR_002/005/007 pós-ISSUE-28), nunca patches manuais ao caso.

---

## Mapeamento de defeitos do playtest (fixo, declarado no runner)

Os defeitos do playtest do Aurora são declarados explicitamente como dados no
runner (não inferidos de texto livre por heurística frágil):

| ID | Defeito do playtest | Categoria | Finding esperado da pipeline |
|---|---|---|---|
| PD_01 | Não ficou claro o que resolver no E1 | objetivo de envelope | NR (clareza de objetivo) se a regra existir; senão `unmatched_playtest` |
| PD_02 | Não ficou claro quando receber o E2 | progressão entre envelopes | `unmatched_playtest` (sem regra correspondente ainda) |
| PD_03 | Não ficou claro quais perguntas responder no E2 | objetivo de envelope | NR (clareza de objetivo) se a regra existir; senão `unmatched_playtest` |

> A tabela é declarada como constante no módulo do runner. O agente **não**
> deve inventar defeitos novos nem alterar a redação do playtest. Se nenhuma
> regra NR/ER atual cobre um defeito, ele aparece em `unmatched_playtest` —
> isso é um resultado **válido e esperado**, e confirma a nota de backlog de que
> regras como NR_002/005/007 (clareza/escopo de documentos) ainda não foram
> implementadas.

---

## API pública esperada

```python
# generator/pipeline_runner.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class PlaytestDefect:
    defect_id: str          # "PD_01"
    description: str
    category: str           # "objetivo_envelope" | "progressao" | ...


@dataclass(frozen=True)
class DefectMatch:
    defect_id: str
    finding_code: str       # NR_* ou ER_*


@dataclass(frozen=True)
class PlaytestComparison:
    playtest_defects: tuple[PlaytestDefect, ...]
    pipeline_findings: tuple[str, ...]
    matches: tuple[DefectMatch, ...]
    unmatched_playtest: tuple[str, ...]
    unmatched_pipeline: tuple[str, ...]


@dataclass(frozen=True)
class PipelineRunResult:
    manifest: dict[str, Any]
    workspace_run: dict[str, Any]
    blind_solver_report: dict[str, Any]
    gate_evaluation: dict[str, Any]
    narrative_report: dict[str, Any]
    evidence_report: dict[str, Any]
    findings: tuple[dict[str, Any], ...]
    comparison: PlaytestComparison


# Aurora playtest defects, declared as data (not inferred).
AURORA_PLAYTEST_DEFECTS: tuple[PlaytestDefect, ...] = (...)


class DeterministicPipelineSolver:
    """Offline, no-LLM stub solver reused for the Aurora run.
    Mirrors the harness Protocol; reads declared artifacts only."""
    def solve(self, context: Any) -> Any: ...


def run_pipeline(
    blueprint_path: str | Path,
    run_id: str,
    *,
    output_root: str | Path | None = None,
    created_at: str | None = None,
) -> PipelineRunResult:
    """Run the full multiagent pipeline over a blueprint, offline and
    deterministically. Builds bundle → blind solve → run record → gate →
    narrative review → evidence review → workspace → manifest, then compares
    findings to the documented playtest defects.

    Never calls an LLM, never accesses the network, never mutates the blueprint.
    ``output_root`` defaults to a temporary directory; bundle artifacts are
    written there only (no canonical paths touched)."""
    ...


def compare_to_playtest(
    findings: tuple[Mapping[str, Any], ...],
    playtest_defects: tuple[PlaytestDefect, ...],
    defect_to_codes: Mapping[str, tuple[str, ...]],
) -> PlaytestComparison:
    """Deterministically cross-reference pipeline findings against declared
    playtest defects. Pure function; no filesystem, no mutation."""
    ...
```

`run_pipeline` orquestra usando exclusivamente as APIs públicas existentes; não
reimplementa nenhuma regra de gate, review ou manifest.

---

## Escopo permitido

Criar:
- `generator/pipeline_runner.py` — `run_pipeline`, `compare_to_playtest`, dataclasses, `AURORA_PLAYTEST_DEFECTS`, `DeterministicPipelineSolver`
- `tests/test_pipeline_runner.py`
- `tests/test_aurora_pipeline.py` — testes específicos da run do Aurora
- `docs/AURORA_PIPELINE_RUN.md` — relatório legível da primeira run real (resultado da execução, manifest resumido, comparação playtest)
- `tests/fixtures/pipeline_runner/` — se necessário, um blueprint mínimo sintético para testes unitários do runner (não-canônico)

Pode atualizar:
- `docs/ROADMAP.md` — marcar ISSUE-28 como concluída e registrar que ISSUE-23/24 estão desbloqueadas (somente seção de status)

---

## Fora de escopo

**Não implementar:**
- Qualquer chamada a LLM, provider, ou internet (isso é Fase I, ISSUE-31+)
- Qualquer alteração ao blueprint do Aurora ou a qualquer caso canônico
- Patches/correções ao caso a partir dos defeitos de playtest
- Visual Reviewer (ISSUE-23) ou Accessibility Reviewer (ISSUE-24) — esta issue os **desbloqueia**, não os implementa
- Schema novo
- Alteração de qualquer módulo existente em `generator/` (bundle, harness, gate, reviewers, workspace, orchestrator, manifest)
- CLI interativa (uma função `run_pipeline` chamável basta; um `if __name__` mínimo é opcional)
- Persistência automática em caminhos canônicos; bundles vão só para `output_root`/tmp
- Skills em `.ai/skills/`
- Inferência heurística de defeitos a partir de texto livre do playtest (os defeitos são declarados como dados)

---

## Anti-regras

A implementação NÃO DEVE:

- Chamar LLM, provider ou internet
- Modificar o blueprint do Aurora ou qualquer caso canônico
- Gerar correções/patches ao caso a partir do playtest
- Reimplementar regras GE_*, NR_*, ER_*, WS_*, OR_* ou RM_* — sempre usar as APIs públicas
- Duplicar enums/constantes — importar de `workspace.py`/`run_manifest.py`
- Inventar defeitos de playtest fora de `AURORA_PLAYTEST_DEFECTS`
- Escrever artefatos em caminhos canônicos (só em `output_root`/tmp)
- Marcar `unmatched_playtest` como falha de teste — defeitos sem regra correspondente são resultado esperado
- Criar skills em `.ai/skills/`
- Lançar exceção quando um reviewer não retorna findings (lista vazia é válida)

---

## Testes obrigatórios

### `tests/test_pipeline_runner.py` (22 casos)

Casos 1–8: `compare_to_playtest` (função pura)

1. defeito com finding correspondente → entra em `matches`
2. defeito sem finding correspondente → entra em `unmatched_playtest`
3. finding sem defeito correspondente → entra em `unmatched_pipeline`
4. `compare_to_playtest` não muta os argumentos de entrada
5. lista de findings vazia → todos os defeitos em `unmatched_playtest`
6. lista de defeitos vazia → todos os findings em `unmatched_pipeline`
7. múltiplos findings mapeados ao mesmo defeito → todos viram `matches`
8. resultado é determinístico (duas chamadas iguais → resultado igual)

Casos 9–22: `run_pipeline` sobre blueprint sintético mínimo

9. `run_pipeline` retorna `PipelineRunResult` com todos os campos preenchidos
10. `blind_solver_report` retornado passa `validate_blind_solver_report`
11. `gate_evaluation` retornado passa `validate_gate_evaluation`
12. `narrative_report` retornado passa `validate_review_report`
13. `evidence_report` retornado passa `validate_review_report`
14. `workspace_run` retornado passa `validate_workspace_run`
15. `manifest` retornado passa `validate_run_manifest`
16. `manifest` retornado passa `validate_run_manifest_semantics` com `valid=True`
17. `run_pipeline` não muta o blueprint de entrada (comparar com `deepcopy`)
18. `run_pipeline` não escreve em caminhos canônicos (output só em `output_root`/tmp)
19. `manifest.findings` consolida findings de narrative + evidence
20. `manifest.stages_completed` contém os 4 stages após run completa
21. `manifest.pipeline_status` é `complete` quando a decisão de gate é `approved`
22. duas execuções com mesmo `created_at` produzem manifests equivalentes (determinismo)

### `tests/test_aurora_pipeline.py` (10 casos)

Casos 23–32: run real do Aurora

23. `run_pipeline(examples/caso_canonico_intermediario.json, ...)` executa sem exceção
24. resultado do Aurora produz `manifest` que passa `validate_run_manifest`
25. resultado do Aurora produz `manifest` que passa `validate_run_manifest_semantics`
26. `comparison.playtest_defects` == `AURORA_PLAYTEST_DEFECTS` (3 defeitos PD_01–PD_03)
27. `comparison` é determinística para o Aurora (duas runs → mesma comparação)
28. narrative review do Aurora retorna um `ReviewReport` schema-válido (com ou sem findings)
29. evidence review do Aurora retorna um `ReviewReport` schema-válido
30. nenhum artefato é escrito em `examples/` durante a run do Aurora
31. blueprint do Aurora não é mutado pela run (hash/deepcopy idêntico antes e depois)
32. defeitos do playtest sem regra correspondente aparecem em `unmatched_playtest` (resultado esperado, não falha)

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `generator/pipeline_runner.py`
2. existir função pública `run_pipeline(blueprint_path, run_id, ...) -> PipelineRunResult`
3. existir função pública `compare_to_playtest(...) -> PlaytestComparison`
4. existirem os dataclasses `PlaytestDefect`, `DefectMatch`, `PlaytestComparison`, `PipelineRunResult`
5. existir a constante `AURORA_PLAYTEST_DEFECTS` com PD_01–PD_03
6. existir `DeterministicPipelineSolver` (sem LLM, sem internet)
7. `run_pipeline` encadear bundle → blind solve → run record → gate → narrative → evidence → workspace → manifest usando **apenas** APIs públicas existentes
8. nenhuma regra GE_*/NR_*/ER_*/WS_*/OR_*/RM_* ser reimplementada
9. nenhum schema novo criado
10. nenhum módulo existente em `generator/` alterado
11. o `manifest` produzido passar `validate_run_manifest` e `validate_run_manifest_semantics` (valid=True)
12. todos os artefatos intermediários serem schema-válidos (blind_solver_report, gate_evaluation, review_report ×2, workspace_run)
13. `run_pipeline` nunca chamar LLM/internet
14. `run_pipeline` nunca mutar o blueprint
15. `run_pipeline` nunca escrever em caminhos canônicos (`examples/`, `output/` canônico) — só `output_root`/tmp
16. `compare_to_playtest` ser função pura e determinística
17. defeitos de playtest sem regra correspondente irem para `unmatched_playtest` sem falhar testes
18. existir `docs/AURORA_PIPELINE_RUN.md` com o relatório legível da run
19. todos os 22 testes de `test_pipeline_runner.py` passarem
20. todos os 10 testes de `test_aurora_pipeline.py` passarem
21. `pytest tests/ -q` passar sem regressão (1248+ testes)
22. `ruff check generator/pipeline_runner.py` passar
23. `VALID_STAGES`/`VALID_ARTIFACT_TYPES`/`VALID_OUTCOMES` importados (não duplicados)
24. nenhum caso canônico alterado
25. nenhuma skill criada em `.ai/skills/`
26. `docs/ROADMAP.md` registrar ISSUE-28 concluída e ISSUE-23/24 desbloqueadas (só status)

---

## Abordagem TDD obrigatória

**RED:** escrever os testes primeiro. `compare_to_playtest` e `run_pipeline`
ausentes → `ImportError`. Confirmar falha por símbolo ausente.

**GREEN, em ordem de tubulação:**
1. `compare_to_playtest` + dataclasses + `AURORA_PLAYTEST_DEFECTS` (função pura primeiro — mais fácil de fechar em verde).
2. `DeterministicPipelineSolver`.
3. `run_pipeline`: bundle → harness → run record.
4. gate (`build_gate_evaluation` com conclusões derivadas do blueprint).
5. reviewers (`review_narrative`, `review_evidence`).
6. workspace via orchestrator (ingest de cada artefato + decisão de gate + transições).
7. `build_run_manifest` com `findings_by_artifact`.
8. montagem do `PipelineRunResult` + comparação.

**REFACTOR:** extrair helpers privados por etapa (`_build_bundle`,
`_blind_solve`, `_run_gate`, `_run_reviews`, `_assemble_workspace`,
`_consolidate_manifest`); garantir que cada helper só chame API pública.

---

## Validação final

```bash
ruff check generator/pipeline_runner.py

pytest tests/test_pipeline_runner.py -q
pytest tests/test_aurora_pipeline.py -q

pytest tests/test_run_manifest.py -q
pytest tests/test_workspace.py -q
pytest tests/test_manual_orchestrator.py -q
pytest tests/test_gate_evaluator.py -q
pytest tests/test_narrative_reviewer.py -q
pytest tests/test_evidence_reviewer.py -q
pytest tests/test_blind_solver_harness.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- a run do Aurora executa ponta-a-ponta sem exceção
- o `manifest` final passa schema + semântica (valid=True)
- todos os artefatos intermediários são schema-válidos
- `examples/caso_canonico_intermediario.json` permanece byte-idêntico (git diff vazio)
- nenhum módulo existente de `generator/` alterado
- defeitos do playtest sem regra atual aparecem em `unmatched_playtest`
- `pytest tests/ -q` passa sem regressão (1248+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, constante de defeitos)
- ordem real de encadeamento da pipeline (qual API foi chamada em cada etapa)
- confirmação de que nenhuma regra foi reimplementada (só APIs públicas)
- resultado da run do Aurora: pipeline_status, stages_completed, nº de findings narrative, nº de findings evidence
- resultado da comparação com playtest: matches, unmatched_playtest, unmatched_pipeline
- interpretação honesta: quais defeitos do playtest a pipeline atual captura e quais ainda não (confirmando backlog NR_002/005/007)
- fixtures criadas (se houver)
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que o blueprint do Aurora não foi alterado (git diff vazio)
- confirmação de que nenhum LLM/internet foi usado
- confirmação de que nenhuma skill foi criada e nenhum caso canônico alterado
- próxima PR recomendada: ISSUE-23+24 (Visual + Accessibility Reviewer) — agora desbloqueadas — ou ISSUE-29 (Fintech), conforme prioridade do Marcelo

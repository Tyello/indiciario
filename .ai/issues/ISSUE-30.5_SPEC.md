# ISSUE-30.5_SPEC — Quality Gate para Canonical Intermediário II

## Identificação

- **Issue:** ISSUE-30.5
- **Título:** Quality Gate — Definir e validar critérios de curadoria para promover casos a canônicos
- **Fase:** H (Aplicação em casos reais — ponte para Fase I)
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-canonical-quality-gate`
- **Título sugerido da PR:** `feat: add canonical quality gate and criteria`
- **Commit sugerido:** `feat: add canonical quality gate and criteria`

---

## Contexto

ISSUE-29+30 rodou Aurora (intermediário I) e Fintech (avançado) pela pipeline completa e consolidou métricas de qualidade. Agora você quer criar um novo intermediário II validado como canônico.

Para isso, você precisa de:
1. **Definição explícita** do que torna um caso "bom para Intermediário"
2. **Função de curadoria** que valida se um novo caso qualifica
3. **Comparação com Aurora** (baseline intermediário I)

Esta issue cria essas três coisas. Depois, você usa a função para validar novos casos antes de promovê-los a canônicos.

---

## Dependências satisfeitas

- ✅ ISSUE-28: Pipeline ponta-a-ponta + manifests + findings
- ✅ ISSUE-29+30: Aurora vs Fintech comparação + métricas consolidadas
- ✅ Análise honesta: Aurora é intermediário I validado por playtest humano

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`, `CLAUDE.md`, `docs/LLM_CONTEXT.md`.
2. Leia integralmente:
   - `docs/QUALITY_COMPARATIVE_REPORT.md` — métricas Aurora vs Fintech (baseline)
   - `docs/AURORA_PIPELINE_RUN.md` — resultado Aurora (intermediário validado)
   - `docs/FINTECH_PIPELINE_RUN.md` — resultado Fintech (avançado)
   - `generator/quality_comparative_reviewer.py` — como as métricas são calculadas
   - `generator/run_manifest.py` — estrutura do manifest
   - `.ai/issues/ISSUE-30.5.md`
3. Execute antes de alterar:
   ```bash
   pytest tests/ -q
   ```

---

## Objetivo

Criar uma **Quality Gate determinística** que diga: "Este novo caso qualifica como canônico para Intermediário?" respondendo com uma avaliação estruturada:

```
✅ APROVADO COMO INTERMEDIÁRIO
   Alinhado com Aurora (intermediário I) em:
   - Densidade: 26.464 ± 15%
   - Documentos: 17 ± 3
   - Findings ER: ≤5
   - Pacing: 100% (4/4 stages)
   - Sem bloqueios

❌ PRECISA REFINAMENTO — Intermediário
   Excedem threshold Aurora:
   - Densidade: 32.000 chars (Aurora 26.464, limite 30.433)
   - Reduzir: conteúdo de documentos não-críticos

⚠️  NÃO PRONTO — Não é Intermediário
   Blockers detectados:
   - pipeline_status: blocked (gate rejection)
   - Resolver gate antes de reavaliar
```

---

## Modelo conceitual

### `CANONICAL_CRITERIA` (constantes, data-driven)

```python
CANONICAL_CRITERIA = {
    "iniciante": {
        "description": "Caso com duração esperada 45-60 min, documentos poucos, muito claros.",
        "density_chars_min": 12000,
        "density_chars_max": 18000,
        "documents_min": 8,
        "documents_max": 14,
        "findings_er_max": 2,
        "findings_vr_major_max": 2,
        "findings_ar_major_max": 2,
        "stages_completed_min": 4,  # deve completar os 4
        "no_pipeline_blocks": True,
    },
    "intermediario": {
        "description": "Caso com duração esperada 60-90 min, documentos médios, mistura clareza com ambigüidade controlada.",
        "density_chars_min": 22000,
        "density_chars_max": 30000,
        "documents_min": 15,
        "documents_max": 20,
        "findings_er_max": 5,
        "findings_vr_major_max": 3,
        "findings_ar_major_max": 3,
        "stages_completed_min": 4,
        "no_pipeline_blocks": True,
    },
    "avancado": {
        "description": "Caso com duração esperada 90-120+ min, documentos densos, pistas ambíguas e red herrings fortes.",
        "density_chars_min": 28000,
        "density_chars_max": 45000,
        "documents_min": 18,
        "documents_max": 30,
        "findings_er_max": 8,
        "findings_vr_major_max": 5,
        "findings_ar_major_max": 5,
        "stages_completed_min": 4,
        "no_pipeline_blocks": True,
    },
}
```

**Origem dos valores:**

| Nível | Origem | Valores |
|---|---|---|
| **Intermediário** | Aurora playtest validado | density 26.464 (22k–30k range); 17 docs (15–20); ER_* ≤5; VR/AR_major ≤3; 4/4 stages; no blocks |
| **Avançado** | Fintech (após ISSUE-29+30) | density 29.647 (28k–45k range, margem para mais); 16 docs (18–30 range, menos é ok se mais denso); ER_* ≤8; VR/AR_major ≤5; 4/4 stages; no blocks |
| **Iniciante** | `caso_canonico_iniciante.json` existente | density ~15k–18k; 8–12 docs; ER_* ≤2; VR/AR_major ≤2; 4/4 stages; no blocks |

---

## Dataclasses e enums

```python
from enum import Enum

class CuratorQualification(str, Enum):
    APPROVED = "approved"
    NEEDS_REFINEMENT = "needs_refinement"
    NOT_READY = "not_ready"


@dataclass(frozen=True)
class QualificationCriterion:
    name: str                    # "density_chars", "documents", etc.
    actual_value: int | float
    min_threshold: int | float
    max_threshold: int | float
    is_satisfied: bool
    status: str                  # "ok" | "exceeds_max" | "below_min" | "blocker"
    recommendation: str


@dataclass(frozen=True)
class CanonicalQualification:
    blueprint_ref: str
    difficulty_level: str        # "iniciante" | "intermediario" | "avancado"
    qualification: CuratorQualification  # approved | needs_refinement | not_ready
    criteria_results: tuple[QualificationCriterion, ...]
    summary: str
    detailed_feedback: str
    action_if_approved: str      # "Promover para caso_canonico_intermediario_novo.json"
    refinement_steps: tuple[str, ...] if needs_refinement else ()
```

---

## API pública

```python
# generator/canonical_quality_gate.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


CANONICAL_CRITERIA: dict[str, dict[str, Any]] = {
    # ... (constantes acima)
}


class CuratorQualification(str, Enum):
    APPROVED = "approved"
    NEEDS_REFINEMENT = "needs_refinement"
    NOT_READY = "not_ready"


@dataclass(frozen=True)
class QualificationCriterion:
    name: str
    actual_value: int | float
    min_threshold: int | float
    max_threshold: int | float
    is_satisfied: bool
    status: str                  # "ok" | "exceeds_max" | "below_min" | "blocker"
    recommendation: str


@dataclass(frozen=True)
class CanonicalQualification:
    blueprint_ref: str
    difficulty_level: str
    qualification: CuratorQualification
    criteria_results: tuple[QualificationCriterion, ...]
    summary: str
    detailed_feedback: str
    action_if_approved: str
    refinement_steps: tuple[str, ...] if not tuple else ()


def evaluate_for_canonical(
    blueprint: Mapping[str, Any],
    pipeline_result: Any,  # PipelineRunResult de ISSUE-28
    difficulty_level: str,
) -> CanonicalQualification:
    """Avaliar se um blueprint qualifica para ser canônico.
    
    Verifica:
    - Métricas de densidade, documentos, findings vs. threshold por nível
    - Status de pipeline (sem bloqueios)
    - Alinhamento com critérios de curadoria
    
    Retorna CanonicalQualification com detailed_feedback.
    """
    ...


def get_canonical_criteria(difficulty_level: str) -> dict[str, Any]:
    """Retornar critérios para um nível."""
    ...
```

---

## Escopo permitido

Criar:
- `docs/CANONICAL_CRITERIA.md` — documento público dos critérios por nível (valores, racional, origem)
- `generator/canonical_quality_gate.py` — função `evaluate_for_canonical` + dataclasses
- `tests/test_canonical_quality_gate.py` — 12 testes
- Opcionalmente, `docs/CANONICAL_QUALIFICATION_REPORT_<case_name>.md` — template para relatar qualificação de novo caso

Pode atualizar:
- `docs/ROADMAP.md` — marcar ISSUE-30.5 concluída (só status)

---

## Fora de escopo

- Alterar qualquer módulo existente (pipeline, reviewers, workspace, manifest)
- Gerar novos casos (ISSUE-30.5 só *avalia*, não *cria*)
- Alterar casos canônicos existentes
- LLM ou internet
- Skills em `.ai/skills/`

---

## Testes obrigatórios (12 casos)

### `tests/test_canonical_quality_gate.py`

1. `evaluate_for_canonical` com Aurora → qualification: APPROVED como intermediario
2. `evaluate_for_canonical` com Fintech → qualification: APPROVED como avancado
3. Caso teste com density exceeding max → NEEDS_REFINEMENT (exceeds_max)
4. Caso teste com documents abaixo do min → NOT_READY (below_min)
5. Caso teste com pipeline_status: blocked → NOT_READY (blocker)
6. Caso teste com ER_findings acima do max → NEEDS_REFINEMENT
7. `get_canonical_criteria("intermediario")` retorna dict com thresholds corretos
8. Criteria resultado com status "ok" tem is_satisfied=True
9. Criteria resultado com status "exceeds_max" tem recommendation não vazio
10. CanonicalQualification com APPROVED tem action_if_approved preenchido
11. CanonicalQualification com NEEDS_REFINEMENT tem refinement_steps não vazio
12. `pytest tests/ -q` sem regressão (1295+ testes)

---

## Critérios de aceitação

1. existir `docs/CANONICAL_CRITERIA.md` com valores por nível (iniciante/intermediario/avancado)
2. existir `generator/canonical_quality_gate.py`
3. existir função pública `evaluate_for_canonical(blueprint, pipeline_result, difficulty_level) -> CanonicalQualification`
4. dataclasses `CanonicalQualification`, `QualificationCriterion`, enum `CuratorQualification` criados
5. `CANONICAL_CRITERIA` com thresholds de density, documents, findings ER/VR/AR, stages, pipeline_status
6. Aurora qualifica como intermediario: APPROVED
7. Fintech qualifica como avancado: APPROVED
8. Caso teste fora de range → NEEDS_REFINEMENT ou NOT_READY apropriado
9. 12 testes de `test_canonical_quality_gate.py` passam
10. nenhum arquivo existente alterado (exceto doc de status)
11. `pytest tests/ -q` passa sem regressão (1295+ testes)
12. `ruff check generator/canonical_quality_gate.py` passa

---

## Abordagem TDD

**RED:** testes falham por `ImportError` em `generator.canonical_quality_gate`.

**GREEN:** 
1. CANONICAL_CRITERIA constante
2. Dataclasses
3. `evaluate_for_canonical` — derivar métricas de blueprint + pipeline_result
4. Lógica de comparação vs thresholds
5. Montagem de CanonicalQualification com feedback

**REFACTOR:** extrair helpers de cálculo de métricas (density, documents, findings count); garantir que nenhum threshold seja número mágico fora de CANONICAL_CRITERIA.

---

## Validação final

```bash
ruff check generator/canonical_quality_gate.py

pytest tests/test_canonical_quality_gate.py -q

pytest tests/test_quality_comparative_reviewer.py -q
pytest tests/ -q

git diff --check
git status --short
```

Confirmar:
- Aurora qualifica: APPROVED como intermediario
- Fintech qualifica: APPROVED como avancado
- `docs/CANONICAL_CRITERIA.md` documenta racional (origem dos values)
- 12 testes passam
- nenhum arquivo existente alterado
- `pytest tests/ -q` passa sem regressão

---

## Resposta final esperada do agente

- Skill utilizada e motivo
- `CANONICAL_CRITERIA` com thresholds (densidade, docs, findings, pacing)
- Aurora/Fintech qualificações (confirmado APPROVED para seus níveis)
- Casos teste criados (exceeding max, below min, blockers)
- Feedback textual de CanonicalQualification (observations + refinement steps)
- Testes adicionados (contagem)
- Resultado suite (X passed, Y failed)
- Próxima PR recomendada: Novo Intermediário II (via chat LLM + validate_for_canonical)

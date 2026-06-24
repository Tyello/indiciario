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
   - Densidade: 26.464 (faixa 22.500–30.500, ±15% do baseline)
   - Findings ER: ≤5
   - Pacing: 100% (4/4 stages)
   - Sem bloqueios
   Sinal informativo: 17 documentos (faixa informativa intermediário: 11–18)

❌ PRECISA REFINAMENTO — Intermediário
   Excede critério duro:
   - Densidade: 32.000 chars (Aurora 26.464, limite 30.500)
   - Reduzir: conteúdo de documentos não-críticos

⚠️  NÃO PRONTO — Não é Intermediário
   Blockers detectados:
   - pipeline_status: blocked (gate rejection)
   - Resolver gate antes de reavaliar
```

**Necessário, não suficiente:** `APPROVED` aqui significa "estruturalmente elegível ao nível" — não substitui playtest humano registrado. Promover um caso a canônico exige teste cego humano (ver `docs/DIFFICULTY_FRAMEWORK.md` e Learning Ledger).

---

## Fonte única de calibração

Os thresholds abaixo derivam diretamente da seção **"Métricas reais dos casos e exceções"** de
`docs/DIFFICULTY_FRAMEWORK.md` (reconciliada na ISSUE-30.5 etapa 1), não de números novos
inventados nesta spec. Essa seção documenta:

- Mirante (`caso_canonico_iniciante.json`): 20 docs / 36.568 chars / Iniciante — **exceção
  histórica**, foi concebido como Intermediário e rebaixado por decisão editorial. **Não é a
  referência métrica de Iniciante.**
- Iniciante B (`caso_canonico_iniciante_b.json`): 9 docs / 12.981 chars / Iniciante —
  **referência métrica real de Iniciante**.
- Aurora (`caso_canonico_intermediario.json`): 17 docs / 26.464 chars / Intermediário, ER
  findings=3 — referência de Intermediário.
- Fintech (`caso_fintech.json`): 16 docs / 29.647 chars / Avançado, ER findings=4 — referência
  de Avançado.

**Constatação central:** contagem de documentos não classifica dificuldade de forma confiável
(Mirante=20 docs é Iniciante; Fintech=16 docs é Avançado). Por isso este gate separa os
critérios em dois grupos:

- **Critérios duros** (bloqueiam `APPROVED`): densidade dentro da faixa do nível, findings
  `ER_*` ≤ teto do nível, `stages_completed == 4`, `pipeline_status != blocked`.
- **Sinais informativos** (não bloqueiam, geram observação no feedback): contagem de
  documentos, número de envelopes. Comparados contra a faixa da tabela de calibração em
  `docs/DIFFICULTY_FRAMEWORK.md`, mas fora da faixa não impede `APPROVED`.

**Reuso, não duplicação:** a aritmética de densidade (`sum(len(str(doc["conteudo"])) ...)`) e
contagem de documentos já existe em `generator/quality_comparative_reviewer.py`
(`_case_metrics` e funções vizinhas). `canonical_quality_gate.py` deve importar/extrair um
helper comum a partir desse módulo, não reimplementar o cálculo.

---

## Modelo conceitual

### `CANONICAL_CRITERIA` (constantes, data-driven)

```python
CANONICAL_CRITERIA = {
    "iniciante": {
        "description": "Caso com duração esperada 45-70 min, documentos poucos, muito claros.",
        "density_chars_min": 11000,
        "density_chars_max": 15000,
        "findings_er_max": 2,
        "findings_vr_major_max": 2,
        "findings_ar_major_max": 2,
        "stages_completed_min": 4,  # deve completar os 4
        "no_pipeline_blocks": True,
        # Sinais informativos (não bloqueiam): faixa da tabela de calibração
        "documents_informational_min": 8,
        "documents_informational_max": 10,
    },
    "intermediario": {
        "description": "Caso com duração esperada 75-110 min, documentos médios, mistura clareza com ambiguidade controlada.",
        "density_chars_min": 22500,
        "density_chars_max": 30500,
        "findings_er_max": 5,
        "findings_vr_major_max": 3,
        "findings_ar_major_max": 3,
        "stages_completed_min": 4,
        "no_pipeline_blocks": True,
        "documents_informational_min": 11,
        "documents_informational_max": 18,
    },
    "avancado": {
        "description": "Caso com duração esperada 110-150 min, documentos densos, pistas ambíguas e red herrings fortes.",
        "density_chars_min": 25000,
        "density_chars_max": 45000,
        "findings_er_max": 8,
        "findings_vr_major_max": 5,
        "findings_ar_major_max": 5,
        "stages_completed_min": 4,
        "no_pipeline_blocks": True,
        "documents_informational_min": 19,
        "documents_informational_max": 24,
    },
}
```

`documents_informational_min/max` **nunca** mudam `qualification` para `NOT_READY` ou
`NEEDS_REFINEMENT` por si só — apenas adicionam uma entrada em `observations` quando o caso
está fora da faixa. Isso é deliberado: Mirante (20 docs, Iniciante) e Fintech (16 docs,
Avançado) provam que volume documental isolado não classifica dificuldade.

**Origem dos valores:**

| Nível | Origem | Valores |
|---|---|---|
| **Iniciante** | Iniciante B (referência métrica real, não o Mirante) | density 12.981 (faixa 11.000–15.000, ±15%); ER_* ≤2; VR/AR_major ≤2; 4/4 stages; no blocks; docs informativo 8–10 |
| **Intermediário** | Aurora playtest validado | density 26.464 (faixa 22.500–30.500, ±15%); ER_* ≤5 (Aurora real=3); VR/AR_major ≤3; 4/4 stages; no blocks; docs informativo 11–18 |
| **Avançado** | Fintech (após ISSUE-29+30) | density 29.647 (faixa 25.000–45.000: piso ±15% do baseline, teto generoso porque avançado é o nível-teto modelado por este gate); ER_* ≤8 (Fintech real=4); VR/AR_major ≤5; 4/4 stages; no blocks; docs informativo 19–24 (Fintech tem 16, fora da faixa — só gera observação, não bloqueia) |

**Mirante como caso de teste documentado:** density 36.568 está bem acima da faixa de Iniciante
(11.000–15.000) → o gate retorna `NEEDS_REFINEMENT` (critério duro `density_chars` em
`exceeds_max`) com uma observação explícita explicando que o Mirante é uma exceção histórica já
validada como canônico por playtest, antes da existência deste gate. O gate não decanoniza o
Mirante retroativamente; ele só sinaliza que um caso *novo* com essa densidade não se qualificaria
automaticamente como Iniciante sem refinamento ou justificativa equivalente.

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
    observations: tuple[str, ...]  # sinais informativos (documents fora da faixa, etc.) — nunca bloqueiam
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
    observations: tuple[str, ...]
    summary: str
    detailed_feedback: str
    action_if_approved: str
    refinement_steps: tuple[str, ...]


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
- `tests/test_canonical_quality_gate.py` — mínimo 13 testes (ver lista acima)
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

## Testes obrigatórios (mínimo 13 casos)

### `tests/test_canonical_quality_gate.py`

1. `evaluate_for_canonical` com Aurora → qualification: APPROVED como intermediario
2. `evaluate_for_canonical` com Fintech → qualification: APPROVED como avancado (apesar de 16
   docs estar fora da faixa informativa 19–24 — confirma que isso não bloqueia)
3. `evaluate_for_canonical` com Iniciante B → qualification: APPROVED como iniciante
4. `evaluate_for_canonical` com Mirante (density real 36.568) avaliado como iniciante →
   NEEDS_REFINEMENT (density `exceeds_max`), com observação textual citando a exceção histórica
5. Caso teste com density exceeding max → NEEDS_REFINEMENT (exceeds_max)
6. Caso teste com documents fora da faixa informativa, mas critérios duros OK → ainda APPROVED,
   com entrada em `observations` (não bloqueia)
7. Caso teste com pipeline_status: blocked → NOT_READY (blocker)
8. Caso teste com ER_findings acima do max → NEEDS_REFINEMENT
9. `get_canonical_criteria("intermediario")` retorna dict com thresholds corretos
10. Criteria resultado com status "ok" tem is_satisfied=True
11. Criteria resultado com status "exceeds_max" tem recommendation não vazio
12. CanonicalQualification com APPROVED tem action_if_approved preenchido
13. CanonicalQualification com NEEDS_REFINEMENT tem refinement_steps não vazio
14. `pytest tests/ -q` sem regressão (baseline atual, ver `docs/ESTADO_ATUAL.md`)

---

## Critérios de aceitação

1. existir `docs/CANONICAL_CRITERIA.md` com valores por nível (iniciante/intermediario/avancado)
2. existir `generator/canonical_quality_gate.py`
3. existir função pública `evaluate_for_canonical(blueprint, pipeline_result, difficulty_level) -> CanonicalQualification`
4. dataclasses `CanonicalQualification`, `QualificationCriterion`, enum `CuratorQualification` criados
5. `CANONICAL_CRITERIA` com thresholds duros de density, findings ER/VR/AR, stages,
   pipeline_status, e sinais informativos de documents
6. Aurora qualifica como intermediario: APPROVED
7. Fintech qualifica como avancado: APPROVED (sem contradição com documents_informational)
8. Iniciante B qualifica como iniciante: APPROVED
9. Mirante avaliado como iniciante: NEEDS_REFINEMENT, tratado como caso de teste documentado de
   exceção (não quebra o teste, só confirma o comportamento esperado)
10. Caso teste fora de range de critério duro → NEEDS_REFINEMENT ou NOT_READY apropriado
11. documents fora da faixa informativa → gera observação, não bloqueia `APPROVED`
12. todos os testes de `test_canonical_quality_gate.py` passam
13. nenhum arquivo existente alterado (exceto doc de status)
14. `pytest tests/ -q` passa sem regressão
15. `ruff check generator/canonical_quality_gate.py` passa

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
- Iniciante B qualifica: APPROVED como iniciante
- Mirante (iniciante): NEEDS_REFINEMENT, tratado como exceção documentada
- `docs/CANONICAL_CRITERIA.md` documenta racional (origem dos values)
- todos os testes de `test_canonical_quality_gate.py` passam
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

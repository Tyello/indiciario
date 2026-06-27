# Canonical Quality Gate — critérios por nível

Implementação: `generator/canonical_quality_gate.py` (`evaluate_for_canonical`,
`get_canonical_criteria`, `CANONICAL_CRITERIA`). Spec: `.ai/issues/ISSUE-30.5_SPEC.md`.
Testes: `tests/test_canonical_quality_gate.py`.

## Necessário, não suficiente

`APPROVED` significa **estruturalmente elegível ao nível**, não "canônico". Promover um caso a
canônico ainda exige teste cego humano registrado — ver `docs/DIFFICULTY_FRAMEWORK.md` e o
Learning Ledger (`examples/learning/retrospective/`). Nenhum gate automatizado substitui essa
exigência.

## Origem dos valores

Todos os thresholds derivam da seção "Métricas reais dos casos e exceções" de
`docs/DIFFICULTY_FRAMEWORK.md`, não de números inventados nesta issue.

| Nível | Caso de referência | Densidade real | Faixa de densidade (±15%) | ER findings real | Docs (informativo) |
|---|---|---:|---|---:|---|
| Iniciante | Iniciante B (`caso_canonico_iniciante_b.json`) | 12.981 chars | 11.000–15.000 | — | 9 (faixa 8–10) |
| Intermediário | Aurora (`caso_canonico_intermediario.json`) | 26.464 chars | 22.500–30.500 | 3 | 17 (faixa 11–18) |
| Avançado | Fintech (`caso_fintech.json`) | 29.647 chars | 25.000–45.000* | 4 | 16 (faixa 19–24, **fora** — não bloqueia) |

\* Avançado é o nível-teto modelado por este gate hoje; o piso segue ±15% do baseline Fintech,
mas o teto é deliberadamente generoso para não forçar revisão imediata de threshold a cada novo
caso avançado mais denso.

**Mirante é exceção histórica, não referência de Iniciante.** O Mirante
(`caso_canonico_iniciante.json`, 20 docs / 36.568 chars) foi concebido como Intermediário e
rebaixado a Iniciante por decisão editorial, antes da existência deste gate. Avaliado por
`evaluate_for_canonical` como Iniciante, ele recebe `NEEDS_REFINEMENT` (densidade excede o
teto) — isso não decanoniza o Mirante, só documenta que um caso *novo* com essa densidade não
se qualificaria automaticamente.

## Critérios duros (bloqueiam `APPROVED`)

Avaliados em `evaluate_for_canonical` como `QualificationCriterion` com `status` em
`"ok" | "exceeds_max" | "below_min" | "blocker" | "not_evaluated"`:

- `density_chars` — dentro de `[density_chars_min, density_chars_max]` do nível.
- `findings_er` — findings `ER_*` (evidence reviewer) ≤ `findings_er_max`.
- `findings_vr_major` — findings `VR_*` (visual reviewer) ≤ `findings_vr_major_max`.
  **Condicional a stage:** só avaliado quando `"visual_review" in stages_completed`; caso
  contrário recebe `status="not_evaluated"`.
- `findings_ar_major` — findings `AR_*` (accessibility reviewer) ≤ `findings_ar_major_max`.
  **Condicional a stage:** só avaliado quando `"accessibility_review" in stages_completed`; caso
  contrário recebe `status="not_evaluated"`.
- `stages_completed` — ≥ `stages_completed_min` (4 em todos os níveis hoje).
- `pipeline_status` — `status="blocker"` quando o manifesto indica `pipeline_status` bloqueado
  (`blocked_by is not None`); qualquer blocker força `NOT_READY`.

Qualquer critério duro fora da faixa (sem blocker) resulta em `NEEDS_REFINEMENT`. Um blocker
resulta em `NOT_READY`.

### Status `not_evaluated`

Quando um stage obrigatório para derivar um critério não está presente em `stages_completed`, o
critério recebe `status="not_evaluated"`, `is_satisfied=False`, `actual_value=None`. O campo
`recommendation` explica qual stage está ausente. Critérios `not_evaluated` **não entram** no
predicado `has_out_of_range` (não geram `NEEDS_REFINEMENT`), mas ativam `has_unevaluated`.

### Veredito `INCOMPLETE_EVALUATION`

Precedência de vereditos (da mais urgente para a menos urgente):

1. **`NOT_READY`** — qualquer critério com `status="blocker"`.
2. **`NEEDS_REFINEMENT`** — qualquer critério com `status` em `"exceeds_max" | "below_min"`.
3. **`INCOMPLETE_EVALUATION`** — pelo menos um critério obrigatório com `status="not_evaluated"`.
4. **`APPROVED`** — todos os critérios obrigatórios avaliados E satisfeitos.

Quando o veredito é `INCOMPLETE_EVALUATION`:
- `summary` e `detailed_feedback` enumeram os critérios não avaliados e o stage ausente.
- `action_if_approved` fica vazio (não há aprovação real).
- Uma observação orienta o usuário a rodar a pipeline completa antes de reavaliar.

**Nota sobre VR/AR no pipeline atual:** `generator/pipeline_runner.py` não invoca os reviewers
visual/accessibility, portanto manifests gerados por ele não incluem `"visual_review"` nem
`"accessibility_review"` em `stages_completed`. Nesses casos o gate reporta
`findings_vr_major` e `findings_ar_major` como `not_evaluated` e emite `INCOMPLETE_EVALUATION`
— não `APPROVED`. Isso impede que evidência não coletada seja tratada como ausência de problemas.
Ver limitações completas em `docs/ESTADO_ATUAL.md`.

## Sinais informativos (não bloqueiam)

- `documents_informational_min/max` — contagem de documentos comparada com a faixa da tabela de
  calibração em `docs/DIFFICULTY_FRAMEWORK.md`. Fora da faixa gera uma entrada em
  `observations`, nunca muda `qualification`.

Esta separação existe porque contagem de documentos não classifica dificuldade de forma
confiável: Mirante tem 20 documentos e é Iniciante; Fintech tem 16 documentos e é Avançado.

## Valores completos

```python
CANONICAL_CRITERIA = {
    "iniciante": {
        "density_chars_min": 11000, "density_chars_max": 15000,
        "findings_er_max": 2, "findings_vr_major_max": 2, "findings_ar_major_max": 2,
        "stages_completed_min": 4,
        "documents_informational_min": 8, "documents_informational_max": 10,
    },
    "intermediario": {
        "density_chars_min": 22500, "density_chars_max": 30500,
        "findings_er_max": 5, "findings_vr_major_max": 3, "findings_ar_major_max": 3,
        "stages_completed_min": 4,
        "documents_informational_min": 11, "documents_informational_max": 18,
    },
    "avancado": {
        "density_chars_min": 25000, "density_chars_max": 45000,
        "findings_er_max": 8, "findings_vr_major_max": 5, "findings_ar_major_max": 5,
        "stages_completed_min": 4,
        "documents_informational_min": 19, "documents_informational_max": 24,
    },
}
```

Use `get_canonical_criteria(nivel)` em vez de ler esta constante diretamente — ela retorna uma
cópia e valida o nível.

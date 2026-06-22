# ISSUE-23+24_SPEC — Visual Reviewer + Accessibility Reviewer

## Identificação

- **Issues:** ISSUE-23 + ISSUE-24 (agrupadas em uma PR)
- **Título:** Visual Reviewer + Accessibility Reviewer
- **Fase:** E (Revisores especializados) — desbloqueada pela ISSUE-28
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-visual-accessibility-reviewer`
- **Título sugerido da PR:** `feat: add visual and accessibility reviewers`
- **Commit sugerido:** `feat: add visual and accessibility reviewers`

---

## Decisão de agrupamento

ISSUE-23 (Visual Reviewer) e ISSUE-24 (Accessibility Reviewer) são entregues
juntas, exatamente como ISSUE-21+22:

1. Ambas produzem um review report com o mesmo schema base.
2. O schema comum não pode ser validado com fixtures reais sem ao menos um
   reviewer que o produza.
3. As regras semânticas das duas são independentes — sem risco de entrelaçamento.
4. Mantém a PR pequena: um schema + dois módulos + testes.

---

## Decisão arquitetural central (leia antes de implementar)

O schema existente `review_report.schema.yaml` tem
`reviewer_type: enum [narrative, evidence]` — **fechado**. Além disso, há
acoplamento de testes existentes que **dependem** de `visual_review` ser um
valor **inválido**:

- `tests/test_run_manifest_schema.py` casos 15 e 17 afirmam que
  `source_type: "visual_review"` e `artifact_type: "visual_review"` são
  **rejeitados** pelo schema do manifest.
- `schemas/workspace_run.schema.yaml` e `schemas/run_manifest.schema.yaml` têm
  enums de `artifact_type`/`source_type` que **não** incluem visual/accessibility.

**Portanto, esta issue NÃO altera** `review_report.schema.yaml`, nem os enums de
`workspace_run`/`run_manifest`, nem os módulos `narrative_reviewer.py`/
`evidence_reviewer.py`, nem qualquer teste existente.

**Decisão:** criar um **schema novo e independente**
`visual_accessibility_review_report.schema.yaml` com
`reviewer_type: enum [visual, accessibility]`, estruturalmente idêntico ao
`review_report.schema.yaml` exceto pelo enum de `reviewer_type`. A integração
desses artefatos no workspace/manifest (estender os enums lá) fica para uma
**issue futura de integração** (anotada no backlog), exatamente como a run do
Aurora (ISSUE-28) só consolidou narrative+evidence.

> Racional: mantém a PR puramente aditiva, preserva todos os testes existentes
> verdes, e não acopla a entrega dos reviewers a uma migração de enums que
> tocaria múltiplos schemas e suas suítes.

---

## Dependências satisfeitas

- ✅ ISSUE-21+22: `generator/narrative_reviewer.py` + `generator/evidence_reviewer.py` + `schemas/review_report.schema.yaml` — padrão de reviewer e contrato base
- ✅ ISSUE-28: pipeline ponta-a-ponta provado; visual/accessibility desbloqueados

---

## Protocolo inicial obrigatório

Antes de alterar qualquer arquivo:

1. Leia `AGENTS.md`.
2. Leia `CLAUDE.md`.
3. Leia `docs/LLM_CONTEXT.md`.
4. Leia `.ai/skills/README.md`.
5. Leia `.ai/skills/tdd.md`.
6. Leia `.ai/skills/diagnose.md`.
7. Leia integralmente:
   - `generator/narrative_reviewer.py` — padrão completo: `ReviewFinding`, `ReviewReport`, `report_to_dict`, `validate_review_report`, `_status_for`, `_summary_for`, `_SEVERITY_ORDER`, `_now_iso`, `_enum_value`, `_document_codes`
   - `generator/evidence_reviewer.py` — padrão de reviewer que **importa** helpers de `narrative_reviewer.py` sem duplicar
   - `schemas/review_report.schema.yaml` — base estrutural a espelhar
   - `tests/test_narrative_reviewer.py` — padrão de teste semântico de reviewer
   - `tests/test_evidence_reviewer.py` — padrão de teste de reviewer importado
   - `generator/models.py` — campos do Blueprint: `documentos` (com `conteudo`, `tipo`), `printable_cards` (com `codigo_visual`, `tags_visuais`, `tipo`), `visual_procedural` (`mapas`, `personagens`, `locais`)
   - `examples/caso_canonico_intermediario.json` — caso Aurora real (campos `printable_cards`, `documentos[].conteudo`, `visual_procedural`)
   - `docs/ROADMAP.md` (seções ISSUE-23 e ISSUE-24)
   - `.ai/issues/ISSUE-23+24.md`
8. Execute antes de alterar:
   ```bash
   pytest tests/test_narrative_reviewer.py -q
   pytest tests/test_evidence_reviewer.py -q
   pytest tests/ -q
   ```

---

## Objetivo

Criar dois revisores especializados que operam sobre um **Blueprint** e produzem
um review report estruturado (schema novo), com findings codificados, severidade
e recomendação. Ambos são **determinísticos, offline, sem LLM**, e nunca mutam o
blueprint — exatamente como narrative/evidence.

### Visual Reviewer (VR)

Avalia a camada de apresentação visual do material impresso/renderizado, a
partir dos campos visuais do blueprint (`printable_cards`, `documentos[].tipo`/
`conteudo`, `visual_procedural`):

- **Densidade documental:** documento com `conteudo` excessivamente longo/denso para um único card (risco de ilegibilidade).
- **Cobertura de cards:** personagens/locais citados sem `printable_card` correspondente.
- **Código visual duplicado:** dois `printable_cards` com o mesmo `codigo_visual`.
- **Tags visuais ausentes:** card sem `tags_visuais` (perda de dica visual de agrupamento).
- **Mapa ausente declarado:** caso referencia locais mas `visual_procedural.mapas` está vazio — **info**, não erro (Aurora é sem mapa por decisão de playtest; ver anti-regra).
- **Tipo documental sem template visual conhecido:** `documentos[].tipo` fora do conjunto de tipos com tratamento visual previsto.

### Accessibility Reviewer (AR)

Avalia legibilidade e carga cognitiva do material, a partir dos mesmos campos:

- **Sobrecarga cognitiva por envelope:** número de documentos num único envelope acima de um limiar (`> N`), dificultando leitura mobile/tablet.
- **Texto muito longo para tela pequena:** `conteudo` de um documento acima de um limiar de tamanho (risco de rolagem/contraste em mobile).
- **Falta de subtítulo/descrição curta:** `printable_card` sem `subtitulo` ou `descricao_curta` (perda de âncora de leitura rápida).
- **Densidade de códigos cruzados:** documento com muitos `codigos_citados`/`ids_citados` (carga de correlação alta).
- **Ausência de hierarquia textual:** documento cujo `conteudo` não tem campo de título/assunto identificável (dificulta navegação).

> Os limiares (`N`, tamanho de texto) são **constantes nomeadas** no módulo,
> não números mágicos espalhados. Valores iniciais sugeridos: máximo de 8
> documentos por envelope (`MAX_DOCS_PER_ENVELOPE = 8`); texto longo acima de
> 2000 caracteres concatenados (`MAX_CONTEUDO_CHARS = 2000`); muitos códigos
> cruzados acima de 6 (`MAX_CROSS_REFS = 6`). O agente pode ajustar com
> justificativa, mas devem ser constantes.

---

## Modelo conceitual

### `visual_accessibility_review_report.schema.yaml`

Estruturalmente idêntico a `review_report.schema.yaml`, **exceto** o enum de
`reviewer_type`:

```yaml
schema_version: "1.0"
report_id: "VR-aurora-20260622-001"     # string >= 1
reviewer_type: "visual"                  # enum: visual | accessibility
blueprint_ref: "examples/caso_canonico_intermediario.json"
created_at: "2026-06-22T10:00:00Z"
created_by: "orchestrator"
status: "needs_revision"                 # enum: approved | needs_revision | blocked
summary: "Dois cards compartilham o mesmo código visual..."   # >= 10 chars
findings:
  - id: "VR-001"
    code: "VR_003"
    severity: "major"                    # enum: critical | major | minor | info
    field: "printable_cards"
    message: "codigo_visual 'P-01' duplicado em dois cards."
    recommendation: "Atribuir códigos visuais únicos por card."
overall_confidence: "medium"             # enum: low | medium | high
notes: ""
```

Campos obrigatórios, tipos, enums de `status`/`severity`/`overall_confidence`,
`additionalProperties: false` no topo e em `findings[]`: **idênticos** ao
`review_report.schema.yaml`. A **única** diferença é
`reviewer_type: enum [visual, accessibility]`.

---

## Regras semânticas

### Visual Reviewer (VR_001–VR_006)

| Código | Regra | Severidade |
|---|---|---|
| VR_001 | `documentos[].conteudo` concatenado acima de `MAX_CONTEUDO_CHARS` | major |
| VR_002 | Personagem/local citado em `documentos` sem `printable_card` correspondente | minor |
| VR_003 | Dois `printable_cards` com o mesmo `codigo_visual` | major |
| VR_004 | `printable_card` sem `tags_visuais` (lista vazia/ausente) | minor |
| VR_005 | Caso cita locais mas `visual_procedural.mapas` vazio | info |
| VR_006 | `documentos[].tipo` fora do conjunto de tipos visuais conhecidos | minor |

### Accessibility Reviewer (AR_001–AR_006)

| Código | Regra | Severidade |
|---|---|---|
| AR_001 | Mais de `MAX_DOCS_PER_ENVELOPE` documentos num único envelope | major |
| AR_002 | `documentos[].conteudo` de um doc acima de `MAX_CONTEUDO_CHARS` | major |
| AR_003 | `printable_card` sem `subtitulo` E sem `descricao_curta` | minor |
| AR_004 | `documentos[]` com mais de `MAX_CROSS_REFS` códigos/ids citados | minor |
| AR_005 | `documentos[].conteudo` sem campo de título/assunto identificável | info |
| AR_006 | Nenhum `printable_card` no caso (perda total de âncora visual) | major |

**Lógica de status (reuso do padrão narrative/evidence):**
- `blocked` se houver finding `critical`.
- `needs_revision` se houver `major` (e nenhum `critical`).
- `approved` se só `minor`/`info` ou nenhum finding.

Findings ordenados por severidade (critical → info), igual aos reviewers existentes.

---

## API pública esperada

```python
# generator/visual_reviewer.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "1.0"

# Limiares nomeados (constantes, não números mágicos)
MAX_CONTEUDO_CHARS = 2000
VISUAL_DOC_TYPES: tuple[str, ...] = (
    "boletim", "chat", "depoimento", "folha_cruzamento",
    "log_acesso", "manual", "protocolo",
)


@dataclass(frozen=True)
class ReviewFinding:   # mesma forma de narrative_reviewer.ReviewFinding
    id: str
    code: str
    severity: str
    field: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class VisualAccessibilityReviewReport:
    report_id: str
    reviewer_type: str   # "visual" | "accessibility"
    blueprint_ref: str
    created_at: str
    created_by: str
    status: str
    summary: str
    findings: tuple[ReviewFinding, ...]
    overall_confidence: str
    notes: str


def validate_visual_accessibility_review_report(
    report: Mapping[str, Any],
) -> list[str]:
    """Validate against visual_accessibility_review_report.schema.yaml.
    Returns sorted list of error messages (empty == valid). Never mutates input."""
    ...


def report_to_dict(report: VisualAccessibilityReviewReport) -> dict[str, Any]:
    """Serialize ready for validate_visual_accessibility_review_report."""
    ...


def review_visual(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> VisualAccessibilityReviewReport:
    """Apply rules VR_001–VR_006. Offline, no LLM, never mutates blueprint."""
    ...
```

```python
# generator/accessibility_reviewer.py

from __future__ import annotations
from typing import Any

from generator.visual_reviewer import (
    MAX_CONTEUDO_CHARS,
    ReviewFinding,
    VisualAccessibilityReviewReport,
    report_to_dict,
    validate_visual_accessibility_review_report,
    _now_iso,
    _status_for,
    _summary_for,
    _SEVERITY_ORDER,
)

MAX_DOCS_PER_ENVELOPE = 8
MAX_CROSS_REFS = 6


def review_accessibility(
    blueprint: Any,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> VisualAccessibilityReviewReport:
    """Apply rules AR_001–AR_006. Offline, no LLM, never mutates blueprint."""
    ...
```

`ReviewFinding`, `VisualAccessibilityReviewReport`, `report_to_dict`,
`validate_visual_accessibility_review_report`, `_status_for`, `_summary_for`,
`_SEVERITY_ORDER`, `_now_iso` são definidos em `visual_reviewer.py` e
**importados** em `accessibility_reviewer.py` — nunca duplicados. Mesmo padrão
de `evidence_reviewer.py` importando de `narrative_reviewer.py`.

> **Nota:** definir um `ReviewFinding` próprio em `visual_reviewer.py` (em vez de
> importar de `narrative_reviewer.py`) mantém os dois subsistemas de review
> desacoplados — visual/accessibility usam schema próprio. Se preferir reusar o
> `ReviewFinding` de `narrative_reviewer.py` (são idênticos em forma), é
> aceitável **desde que** não se altere `narrative_reviewer.py`; apenas importe.
> A spec aceita qualquer uma das duas, com preferência por importar o
> `ReviewFinding` existente de `narrative_reviewer.py` para evitar duas
> dataclasses idênticas no projeto.

---

## Escopo permitido

Criar:
- `schemas/visual_accessibility_review_report.schema.yaml`
- `generator/visual_reviewer.py` — VR_001–VR_006 + dataclasses/helpers (ou import de `ReviewFinding`)
- `generator/accessibility_reviewer.py` — AR_001–AR_006; importa de `visual_reviewer.py`
- `tests/test_visual_accessibility_review_report_schema.py`
- `tests/test_visual_reviewer.py`
- `tests/test_accessibility_reviewer.py`
- `tests/fixtures/visual_accessibility_review_report/valid/`
- `tests/fixtures/visual_accessibility_review_report/invalid/`

Pode atualizar:
- `docs/ROADMAP.md` — marcar ISSUE-23 e ISSUE-24 como concluídas (só status)

---

## Fora de escopo

**Não implementar:**
- Alteração de `review_report.schema.yaml`
- Alteração dos enums em `workspace_run.schema.yaml` ou `run_manifest.schema.yaml`
- Alteração de `narrative_reviewer.py`, `evidence_reviewer.py`, `run_manifest.py`, `workspace.py`, `manual_orchestrator.py`, `pipeline_runner.py`
- Alteração de qualquer teste existente (incl. `test_run_manifest_schema.py` casos 15/17)
- Integração de visual/accessibility no workspace/manifest (issue futura)
- Renderização real, geração de imagem, screenshot, Playwright/Chromium
- LLM, internet, OCR
- CLI interativa
- Alteração de casos canônicos
- Skills em `.ai/skills/`

---

## Anti-regras

A implementação NÃO DEVE:

- Chamar LLM, internet, renderizador ou ferramenta visual (Playwright/Chromium)
- Tratar **ausência de mapa como erro** — Aurora é sem mapa por decisão validada de playtest; VR_005 é `info`, nunca `major`/`critical`
- Modificar o blueprint ou qualquer caso canônico
- Alterar `review_report.schema.yaml` ou os enums de workspace/manifest
- Alterar qualquer módulo ou teste existente
- Reimplementar ou duplicar lógica de status/summary/severidade — importar de `visual_reviewer.py` (que pode importar `ReviewFinding`/helpers de `narrative_reviewer.py`)
- Usar números mágicos — limiares são constantes nomeadas
- Criar skills em `.ai/skills/`
- Lançar exceção quando um reviewer não retorna findings (lista vazia é válida e vira `status: approved`)
- Tentar inserir visual/accessibility nos enums de `artifact_type`/`source_type` (quebraria testes existentes)

---

## Testes obrigatórios

### `tests/test_visual_accessibility_review_report_schema.py` (16 casos)

Casos 1–8: válidas

1. fixture `valid_visual_approved.yaml` passa (reviewer_type: visual, findings: [])
2. fixture `valid_visual_needs_revision.yaml` passa (1 finding major)
3. fixture `valid_accessibility_approved.yaml` passa (reviewer_type: accessibility)
4. fixture `valid_accessibility_blocked.yaml` passa (1 finding critical)
5. `reviewer_type: "visual"` é válido
6. `reviewer_type: "accessibility"` é válido
7. `findings: []` é válido
8. `notes: ""` é válido

Casos 9–16: rejeições estruturais

9. `schema_version: "2.0"` falha
10. `reviewer_type: "narrative"` falha (não pertence a este schema)
11. `reviewer_type: "evidence"` falha
12. `status: "rejected"` falha
13. `findings[].severity: "warning"` falha
14. `summary` com menos de 10 chars falha
15. campo extra no topo falha (`additionalProperties: false`)
16. `findings[].recommendation` ausente falha

### `tests/test_visual_reviewer.py` (16 casos)

Casos 17–22: regras VR_001–VR_006

17. blueprint com doc de `conteudo` enorme → VR_001 (major)
18. personagem citado sem printable_card → VR_002 (minor)
19. dois cards com mesmo `codigo_visual` → VR_003 (major)
20. card sem `tags_visuais` → VR_004 (minor)
21. caso cita locais mas `visual_procedural.mapas` vazio → VR_005 (info)
22. doc com `tipo` desconhecido → VR_006 (minor)

Casos 23–32: comportamento de `review_visual`

23. blueprint limpo → `status: approved`, findings: ()
24. finding `major` presente → `status: needs_revision`
25. finding `critical` presente → `status: blocked`
26. findings ordenados por severidade (critical primeiro)
27. `review_visual` não muta o blueprint (comparar deepcopy)
28. report retornado passa `validate_visual_accessibility_review_report`
29. `report_to_dict` round-trip + validate sem perda
30. `reviewer_type` do report é `"visual"`
31. VR_005 nunca eleva severidade acima de `info` (anti-regra do mapa)
32. blueprint sem `printable_cards` não quebra `review_visual` (degrada graciosamente)

### `tests/test_accessibility_reviewer.py` (16 casos)

Casos 33–38: regras AR_001–AR_006

33. envelope com mais de `MAX_DOCS_PER_ENVELOPE` docs → AR_001 (major)
34. doc com `conteudo` acima de `MAX_CONTEUDO_CHARS` → AR_002 (major)
35. card sem subtitulo e sem descricao_curta → AR_003 (minor)
36. doc com mais de `MAX_CROSS_REFS` códigos/ids citados → AR_004 (minor)
37. doc sem título/assunto identificável → AR_005 (info)
38. caso sem nenhum printable_card → AR_006 (major)

Casos 39–48: comportamento de `review_accessibility`

39. blueprint limpo → `status: approved`
40. finding major presente → `status: needs_revision`
41. `review_accessibility` importa `ReviewFinding`/helpers de `visual_reviewer.py` (sem duplicar)
42. `review_accessibility` não muta o blueprint
43. report retornado passa `validate_visual_accessibility_review_report`
44. `reviewer_type` do report é `"accessibility"`
45. findings ordenados por severidade
46. `report_to_dict` round-trip + validate sem perda
47. limiares são constantes nomeadas importáveis (`MAX_DOCS_PER_ENVELOPE`, `MAX_CROSS_REFS`)
48. blueprint do Aurora (`examples/caso_canonico_intermediario.json`) → `review_accessibility` retorna report schema-válido (com ou sem findings)

---

## Fixtures necessárias

### `tests/fixtures/visual_accessibility_review_report/valid/`

- `valid_visual_approved.yaml` — reviewer_type: visual, status: approved, findings: []
- `valid_visual_needs_revision.yaml` — reviewer_type: visual, 1 finding VR_003 major
- `valid_accessibility_approved.yaml` — reviewer_type: accessibility, status: approved
- `valid_accessibility_blocked.yaml` — reviewer_type: accessibility, 1 finding critical

### `tests/fixtures/visual_accessibility_review_report/invalid/`

- `invalid_reviewer_type_narrative.yaml` — reviewer_type: "narrative"
- `invalid_status.yaml` — status: "rejected"
- `invalid_severity.yaml` — findings[0].severity: "warning"
- `short_summary.yaml` — summary com < 10 chars
- `extra_top_field.yaml` — campo extra no topo
- `missing_recommendation.yaml` — findings[0].recommendation ausente

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/visual_accessibility_review_report.schema.yaml`
2. existir `generator/visual_reviewer.py`
3. existir `generator/accessibility_reviewer.py`
4. `VisualAccessibilityReviewReport` definido em `visual_reviewer.py`
5. `accessibility_reviewer.py` importar dataclasses/helpers de `visual_reviewer.py` (sem duplicar)
6. existir `validate_visual_accessibility_review_report(report) -> list[str]`
7. existir `report_to_dict(report) -> dict`
8. existir `review_visual(...) -> VisualAccessibilityReviewReport`
9. existir `review_accessibility(...) -> VisualAccessibilityReviewReport`
10. schema ter `reviewer_type: enum [visual, accessibility]` e `additionalProperties: false` no topo e em `findings[]`
11. `status` enum `approved | needs_revision | blocked`; `severity` enum `critical | major | minor | info`; `overall_confidence` enum `low | medium | high`
12. regras VR_001–VR_006 implementadas
13. regras AR_001–AR_006 implementadas
14. limiares como constantes nomeadas (`MAX_CONTEUDO_CHARS`, `MAX_DOCS_PER_ENVELOPE`, `MAX_CROSS_REFS`)
15. VR_005 (mapa ausente) é sempre `info`, nunca eleva status
16. lógica de status segue o padrão narrative/evidence (blocked/needs_revision/approved)
17. `review_visual` e `review_accessibility` nunca mutam o blueprint
18. nenhum LLM/internet/renderizador usado
19. `review_report.schema.yaml` NÃO alterado
20. enums de `workspace_run`/`run_manifest` NÃO alterados
21. `narrative_reviewer.py`/`evidence_reviewer.py` NÃO alterados
22. nenhum teste existente alterado (incl. `test_run_manifest_schema.py` casos 15/17 continuam verdes)
23. fixtures válidas passam; inválidas falham com mensagem correta
24. 16 testes de `test_visual_accessibility_review_report_schema.py` passam
25. 16 testes de `test_visual_reviewer.py` passam
26. 16 testes de `test_accessibility_reviewer.py` passam
27. `pytest tests/ -q` passa sem regressão (1279+ testes)
28. `ruff check generator/visual_reviewer.py generator/accessibility_reviewer.py` passa
29. nenhum caso canônico alterado
30. nenhuma skill criada em `.ai/skills/`
31. `docs/ROADMAP.md` marca ISSUE-23 e ISSUE-24 concluídas (só status)

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Falham por `ImportError` em
`generator.visual_reviewer`/`generator.accessibility_reviewer` ou
`FileNotFoundError` no schema.

**GREEN:** schema → `visual_reviewer.py` (dataclasses/helpers + `validate` +
`report_to_dict` + `review_visual` com VR_001–VR_006) → `accessibility_reviewer.py`
(importa de visual + `review_accessibility` com AR_001–AR_006).

**REFACTOR:** extrair helpers de varredura de documentos/cards por envelope
reutilizados em VR e AR; garantir que nenhum limiar seja número mágico; garantir
que `accessibility_reviewer.py` não duplique nenhuma dataclass/helper.

---

## Validação final

```bash
ruff check generator/visual_reviewer.py generator/accessibility_reviewer.py

pytest tests/test_visual_accessibility_review_report_schema.py -q
pytest tests/test_visual_reviewer.py -q
pytest tests/test_accessibility_reviewer.py -q

pytest tests/test_narrative_reviewer.py -q
pytest tests/test_evidence_reviewer.py -q
pytest tests/test_run_manifest_schema.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- `review_report.schema.yaml` byte-idêntico (git diff vazio)
- `test_run_manifest_schema.py` casos 15/17 continuam verdes (visual_review ainda inválido lá)
- `review_visual`/`review_accessibility` do Aurora retornam reports schema-válidos
- nenhum módulo/teste existente alterado
- `pytest tests/ -q` passa sem regressão (1279+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, constantes de limiar)
- regras VR_001–VR_006 e AR_001–AR_006 implementadas (breve descrição)
- como `accessibility_reviewer.py` reusa `visual_reviewer.py` (lista de imports)
- confirmação de que `review_report.schema.yaml` e os enums de workspace/manifest NÃO foram tocados
- confirmação de que `test_run_manifest_schema.py` casos 15/17 continuam verdes
- resultado de `review_visual` e `review_accessibility` sobre o Aurora (status + nº de findings por código)
- fixtures criadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que nenhum LLM/internet/renderizador foi usado
- confirmação de que nenhuma skill foi criada e nenhum caso canônico alterado
- nota de backlog: integração de visual/accessibility nos enums de workspace/manifest fica para issue futura de integração
- próxima PR recomendada: ISSUE-29 (Fintech no pipeline) ou a issue de integração visual/accessibility, conforme prioridade do Marcelo

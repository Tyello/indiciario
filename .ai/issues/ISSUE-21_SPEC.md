# ISSUE-21+22_SPEC — Narrative Reviewer + Evidence Reviewer

## Identificação

- **Issues:** ISSUE-21 + ISSUE-22 (agrupadas em uma PR)
- **Título:** Narrative Reviewer + Evidence Reviewer
- **Fase:** E (Revisores especializados)
- **Prioridade:** P1
- **Branch sugerida:** `codex/add-narrative-evidence-reviewer`
- **Título sugerido da PR:** `feat: add narrative and evidence reviewers`
- **Commit sugerido:** `feat: add narrative and evidence reviewers`

## Decisão de agrupamento

ISSUE-21 (Narrative Reviewer) e ISSUE-22 (Evidence Reviewer) são entregues
juntas porque:

1. Ambas produzem um `ReviewReport` com o mesmo schema base.
2. O schema comum (`review_report.schema.yaml`) não pode ser validado com
   fixtures reais sem ao menos um reviewer que o produza.
3. As regras semânticas dos dois revisores são independentes entre si — não
   há risco de entrelaçamento que justifique separação.
4. O agrupamento mantém a mesma PR pequena da ISSUE-19+20 em termos de
   superfície: um schema + dois módulos + testes.

---

## Dependências satisfeitas

- ✅ ISSUE-16: `generator/blind_solver_harness.py`
- ✅ ISSUE-17: `generator/blind_solver_report_validator.py` (RV_001–RV_008)
- ✅ ISSUE-18: `generator/blind_solve_run_record.py` + `schemas/blind_solve_run_record.schema.yaml`
- ✅ ISSUE-19+20: `generator/gate_evaluator.py` + `schemas/gate_evaluation.schema.yaml`

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
   - `generator/blind_solver_report_validator.py` — padrão de código/erros/warnings
   - `generator/gate_evaluator.py` — padrão de dataclasses + builder
   - `generator/case_review.py` — padrão de finding/review editorial existente
   - `generator/case_kernel.py` — campos do CaseKernel disponíveis
   - `generator/models.py` — campos do Blueprint (documentos, personagens, dicas, red_herrings, matriz_pistas)
   - `schemas/blind_solve_run_record.schema.yaml`
   - `schemas/gate_evaluation.schema.yaml`
   - `tests/test_gate_evaluator.py` — padrão de teste de validador semântico
   - `tests/test_gate_evaluation_schema.py` — padrão de teste de schema
   - `docs/IMPLEMENTATION_PLAN_MULTIAGENT_PIPELINE.md` (seções ISSUE-21 e ISSUE-22)
8. Execute antes de alterar:
   ```bash
   pytest tests/test_gate_evaluator.py -q
   pytest tests/test_gate_evaluation_schema.py -q
   pytest tests/ -q
   ```

---

## Objetivo

Criar dois revisores especializados que operam sobre um **Blueprint** (já
existente, acessível publicamente) e produzem um `ReviewReport` estruturado
com findings codificados, severidades e recomendações.

### Narrative Reviewer (NR)

Avalia a camada narrativa e diegética do caso:

- **Imersão:** documentos parecem reais ou parecem puzzles?
- **Diegese:** algum documento de jogador contém interpretação do autor
  em vez de evidência bruta?
- **Motivação:** o motivo do executor está sustentado por documentos?
- **Tom:** consistência de tom entre personagens e documentos.
- **Personagens:** pelo menos um personagem tem papel ambíguo (suspeito
  plausível além do executor)?
- **Documentos-dica:** algum documento parece dica disfarçada de documento
  real (nome, tom, conteúdo óbvio demais)?

### Evidence Reviewer (ER)

Avalia a cadeia lógica de evidências:

- **Pistas órfãs:** pistas na `matriz_pistas` não suportadas por nenhum documento.
- **Buracos lógicos:** conclusão esperada sem evidência suficiente na
  `cadeia_causal` + `matriz_pistas`.
- **Suporte à conclusão:** cada pilar de validação tem pelo menos uma pista?
- **Red herrings justos:** red herrings são descartáveis com evidência
  disponível, não apenas por ausência de prova?
- **Redundância excessiva:** mais de N pistas apontam para o mesmo fato
  sem adicionar contexto (risco de óbvio demais).
- **Cobertura de envelopes:** cada envelope tem pelo menos uma pista
  designada?

---

## Modelo conceitual

### review_report.schema.yaml

```yaml
schema_version: "1.0"
report_id: "NR-aurora-20260620-001"      # neutral_id
reviewer_type: "narrative"               # enum: narrative | evidence
blueprint_ref: "examples/caso_canonico_intermediario.json"
created_at: "2026-06-20T10:00:00Z"
created_by: "orchestrator"

status: "needs_revision"
# enum: approved | needs_revision | blocked

summary: "Dois documentos de jogador contêm interpretação autoral..."
# resumo livre; obrigatório; >= 10 chars

findings:
  - id: "NR-001"
    code: "NR_003"          # código de regra; NR_* ou ER_*
    severity: "major"       # enum: critical | major | minor | info
    field: "documentos[2]"  # campo ou caminho no blueprint
    message: "Documento 'Carta de Helena' contém conclusão autoral..."
    recommendation: "Reescrever como evidência bruta sem interpretação."

overall_confidence: "medium"
# enum: low | medium | high
# confiança do reviewer nas próprias conclusões

notes: ""
```

---

## Campos obrigatórios do schema

| Campo | Tipo | Regra |
|---|---|---|
| `schema_version` | const `"1.0"` | Imutável nesta versão |
| `report_id` | neutral_id | Único para este report |
| `reviewer_type` | enum | `narrative` / `evidence` |
| `blueprint_ref` | string ≥ 1 | Caminho do blueprint avaliado |
| `created_at` | date-time | ISO 8601 com timezone |
| `created_by` | string ≥ 1 | Quem gerou |
| `status` | enum | `approved` / `needs_revision` / `blocked` |
| `summary` | string ≥ 10 | Resumo obrigatório |
| `findings` | array | ≥ 0 itens; cada item é um objeto |
| `overall_confidence` | enum | `low` / `medium` / `high` |
| `notes` | string | Pode ser vazio |

### findings — cada item

| Campo | Tipo | Regra |
|---|---|---|
| `id` | string ≥ 1 | Identificador único dentro do report |
| `code` | string ≥ 1 | Código da regra: `NR_*` ou `ER_*` |
| `severity` | enum | `critical` / `major` / `minor` / `info` |
| `field` | string | Campo ou caminho no blueprint; pode ser vazio |
| `message` | string ≥ 1 | Descrição do problema |
| `recommendation` | string | Sugestão de correção; pode ser vazia |

---

## Regras do Narrative Reviewer (NR_*)

Todas operam sobre o `Blueprint` diretamente. Nenhuma acessa arquivos externos.

| Código | Campo avaliado | Regra | Severidade padrão |
|---|---|---|---|
| NR_001 | `documentos[].conteudo` | Documento de jogador contém linguagem interpretativa do autor ("portanto", "claramente", "isso prova") | major |
| NR_002 | `documentos[].tipo` | Documento com `tipo` que revela papel investigativo no próprio nome (ex: "PISTA", "EVIDÊNCIA" literal) | minor |
| NR_003 | `personagens` | Nenhum personagem tem papel `suspeito` além do `executor_id` | major |
| NR_004 | `motivacao` | Motivação do executor não é sustentada por nenhum documento na lista de documentos | major |
| NR_005 | `tom` + `documentos` | Tom declarado no blueprint diverge do tom dos documentos (heurística: documentos com linguagem informal quando tom = "sério/policial") | minor |
| NR_006 | `dicas` | Alguma dica referencia um documento que não existe na lista de documentos | critical |
| NR_007 | `documentos` | Menos de 2 documentos pertencem a personagens que não são executor nem vítima | minor |
| NR_008 | `red_herrings` | Red herring não tem nenhum documento associado que o sustente | major |

Regras NR_001, NR_003, NR_004, NR_006 são **bloqueantes** (critical/major que
disparam `status: blocked` ou `needs_revision`).
Regras NR_002, NR_005, NR_007, NR_008 são warnings que geram `needs_revision`
mas não `blocked`.

### Lógica de status do Narrative Reviewer

- `blocked`: qualquer finding `critical`
- `needs_revision`: qualquer finding `major` sem `critical`
- `approved`: só findings `minor` / `info` ou sem findings

---

## Regras do Evidence Reviewer (ER_*)

| Código | Campo avaliado | Regra | Severidade padrão |
|---|---|---|---|
| ER_001 | `matriz_pistas` | Pista referencia documento que não existe na lista de documentos | critical |
| ER_002 | `pilares_validacao` | Pilar de validação não tem nenhuma pista na `matriz_pistas` que o suporte | major |
| ER_003 | `cadeia_causal` | Cadeia causal tem menos de 3 elos | major |
| ER_004 | `objetivos_por_envelope` | Envelope declarado em `objetivos_por_envelope` sem nenhuma pista designada para ele | major |
| ER_005 | `matriz_pistas` | Mais de 60% das pistas apontam para o mesmo documento (concentração excessiva) | minor |
| ER_006 | `red_herrings` | Red herring não pode ser descartado com evidência disponível — nenhuma pista contradiz ou contextualiza o red herring | major |
| ER_007 | `matriz_pistas` | Pista marcada como obrigatória (`obrigatoria: true`) não está em nenhum documento do E1 | major |
| ER_008 | `documentos` | Menos de 40% dos documentos contribuem para pelo menos uma pista na `matriz_pistas` | minor |

Regras ER_001, ER_002, ER_004, ER_006, ER_007 são **bloqueantes**.
Regras ER_003, ER_005, ER_008 geram `needs_revision` mas não `blocked`.

### Lógica de status do Evidence Reviewer

- `blocked`: qualquer finding `critical`
- `needs_revision`: qualquer finding `major` sem `critical`
- `approved`: só findings `minor` / `info` ou sem findings

---

## API pública esperada

```python
# generator/narrative_reviewer.py

@dataclass(frozen=True)
class ReviewFinding:
    id: str
    code: str          # "NR_*" ou "ER_*"
    severity: str      # "critical" | "major" | "minor" | "info"
    field: str
    message: str
    recommendation: str

@dataclass(frozen=True)
class ReviewReport:
    report_id: str
    reviewer_type: str           # "narrative" | "evidence"
    blueprint_ref: str
    created_at: str
    created_by: str
    status: str                  # "approved" | "needs_revision" | "blocked"
    summary: str
    findings: tuple[ReviewFinding, ...]
    overall_confidence: str      # "low" | "medium" | "high"
    notes: str


def review_narrative(
    blueprint: Blueprint,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> ReviewReport:
    """Aplica regras NR_001–NR_008 e retorna ReviewReport.
    Nunca chama LLM. Nunca muta o blueprint."""
    ...


def validate_review_report(report: Mapping[str, Any]) -> list[str]:
    """Valida estruturalmente contra review_report.schema.yaml.
    Retorna lista de erros (vazia = válido)."""
    ...


def report_to_dict(report: ReviewReport) -> dict[str, Any]:
    """Serializa ReviewReport para dict pronto para validate_review_report."""
    ...
```

```python
# generator/evidence_reviewer.py

def review_evidence(
    blueprint: Blueprint,
    blueprint_ref: str,
    report_id: str,
    created_by: str = "orchestrator",
    overall_confidence: str = "medium",
    notes: str = "",
) -> ReviewReport:
    """Aplica regras ER_001–ER_008 e retorna ReviewReport.
    Nunca chama LLM. Nunca muta o blueprint."""
    ...
```

`ReviewFinding`, `ReviewReport`, `validate_review_report` e `report_to_dict`
são definidos em `generator/narrative_reviewer.py` e importados em
`generator/evidence_reviewer.py`. Não duplicar.

---

## Escopo permitido

Criar:
- `schemas/review_report.schema.yaml`
- `generator/narrative_reviewer.py` — regras NR_001–NR_008, dataclasses compartilhadas, `validate_review_report`, `report_to_dict`
- `generator/evidence_reviewer.py` — regras ER_001–ER_008, importa dataclasses de `narrative_reviewer`
- `tests/test_review_report_schema.py`
- `tests/test_narrative_reviewer.py`
- `tests/test_evidence_reviewer.py`
- `tests/fixtures/review_report/valid/`
- `tests/fixtures/review_report/invalid/`

Pode atualizar:
- `docs/BLIND_SOLVER_HARNESS.md` — seção sobre revisores (opcional)

---

## Fora de escopo

**Não implementar:**
- Visual Reviewer (ISSUE-23 — só após ISSUE-28)
- Accessibility Reviewer (ISSUE-24 — só após ISSUE-28)
- Workspace / orquestrador (ISSUE-25+)
- Integração automática com o pipeline de build
- Alteração de casos canônicos
- Alteração de `blind_solver_harness.py`, `gate_evaluator.py`, `blind_solve_run_record.py`
- LLM, internet, OCR
- CLI complexa
- Heurísticas de NLP (regex simples é permitido para NR_001/NR_005)

---

## Testes obrigatórios

### `tests/test_review_report_schema.py` (20 casos)

Casos 1–10: fixtures válidas e variações

1. fixture `valid_narrative_approved.yaml` passa
2. fixture `valid_narrative_needs_revision.yaml` passa
3. fixture `valid_evidence_blocked.yaml` passa
4. fixture `valid_no_findings.yaml` passa (`findings: []`, `status: approved`)
5. `reviewer_type: "evidence"` é válido
6. `overall_confidence: "low"` é válido
7. `findings` com `severity: "info"` é válido
8. `findings[].recommendation` vazia é válida (`""`)
9. `findings[].field` vazia é válida (`""`)
10. `notes` vazia é válida

Casos 11–20: rejeições estruturais

11. `schema_version: "2.0"` falha
12. `reviewer_type: "visual"` falha (enum não existe ainda)
13. `status: "pending"` falha
14. `report_id` ausente falha
15. `summary` ausente falha
16. `overall_confidence: "very_high"` falha
17. `findings[].severity: "warning"` falha (não é enum válido)
18. `findings[].code` ausente falha
19. campo extra no topo falha (`additionalProperties: false`)
20. `findings[].id` ausente falha

### `tests/test_narrative_reviewer.py` (25 casos)

Casos 21–28: regras NR_001–NR_008

21. blueprint com documento contendo "portanto isso prova" → NR_001 finding
22. blueprint sem linguagem interpretativa → sem NR_001
23. blueprint sem personagem `suspeito` além do executor → NR_003 finding
24. blueprint com pelo menos um `suspeito` → sem NR_003
25. blueprint com motivação não sustentada por nenhum documento → NR_004 finding
26. dica referenciando documento inexistente → NR_006 finding (critical)
27. red_herring sem documento associado → NR_008 finding
28. todos documentos de jogador com evidência bruta → sem NR_001

Casos 29–38: `review_narrative` e status

29. `review_narrative` retorna `ReviewReport`
30. `ReviewReport` serializado passa `validate_review_report`
31. finding NR_006 (critical) → `status: "blocked"`
32. finding NR_003 (major) sem critical → `status: "needs_revision"`
33. nenhum finding major/critical → `status: "approved"`
34. `report_to_dict` retorna dict com todos os campos obrigatórios
35. `review_narrative` não muta o blueprint
36. `report_id` no resultado bate com o passado como argumento
37. `reviewer_type` no resultado é `"narrative"`
38. `blueprint_ref` no resultado bate com o argumento

Casos 39–45: `validate_review_report` e integração

39. `validate_review_report` retorna lista vazia para report válido
40. `validate_review_report` retorna erros para report inválido (status ausente)
41. findings com codes NR_* são preservados na serialização
42. `overall_confidence` padrão é `"medium"`
43. `notes` padrão é `""`
44. findings são ordenados por severidade (critical primeiro) no report
45. `pytest tests/ -q` sem regressão (parcial — será confirmado no STEP de validation)

### `tests/test_evidence_reviewer.py` (25 casos)

Casos 46–53: regras ER_001–ER_008

46. pista referenciando documento inexistente → ER_001 finding (critical)
47. pista com documento existente → sem ER_001
48. pilar de validação sem pista associada → ER_002 finding
49. todos pilares com pista → sem ER_002
50. envelope em `objetivos_por_envelope` sem pista designada → ER_004 finding
51. red herring sem pista que o descarte → ER_006 finding
52. pista obrigatória não disponível no E1 → ER_007 finding
53. mais de 60% das pistas no mesmo documento → ER_005 finding (minor)

Casos 54–63: `review_evidence` e status

54. `review_evidence` retorna `ReviewReport`
55. `ReviewReport` serializado passa `validate_review_report`
56. finding ER_001 (critical) → `status: "blocked"`
57. finding ER_002 (major) sem critical → `status: "needs_revision"`
58. nenhum finding major/critical → `status: "approved"`
59. `report_to_dict` retorna dict com todos os campos obrigatórios
60. `review_evidence` não muta o blueprint
61. `report_id` no resultado bate com o argumento
62. `reviewer_type` no resultado é `"evidence"`
63. `blueprint_ref` no resultado bate com o argumento

Casos 64–70: integração e edge cases

64. `validate_review_report` funciona para report de evidence reviewer
65. findings com codes ER_* são preservados na serialização
66. blueprint mínimo válido (sem red_herrings, sem dicas) não lança exceção
67. blueprint dos canônicos não lança exceção em nenhum reviewer
68. `review_narrative` e `review_evidence` importam do mesmo módulo de dataclasses
69. `report_to_dict` + `validate_review_report` forma round-trip sem perda
70. `pytest tests/ -q` passa sem regressão (1033+ testes)

---

## Fixtures necessárias

### `tests/fixtures/review_report/valid/`

- `valid_narrative_approved.yaml` — reviewer_type: narrative, status: approved, findings: []
- `valid_narrative_needs_revision.yaml` — reviewer_type: narrative, status: needs_revision, 2 findings minor/major
- `valid_evidence_blocked.yaml` — reviewer_type: evidence, status: blocked, 1 finding critical
- `valid_no_findings.yaml` — findings: [], status: approved, notes: ""

### `tests/fixtures/review_report/invalid/`

- `invalid_reviewer_type.yaml` — reviewer_type: "visual"
- `invalid_status.yaml` — status: "pending"
- `missing_report_id.yaml` — report_id ausente
- `missing_summary.yaml` — summary ausente
- `invalid_severity.yaml` — findings[0].severity: "warning"
- `extra_top_field.yaml` — campo extra no topo

---

## Anti-regras

A implementação NÃO DEVE:

- Chamar LLM ou internet
- Fazer parsing semântico profundo de texto (regex simples permitido)
- Modificar o blueprint ou qualquer artefato existente
- Avaliar qualidade visual (isso é ISSUE-23)
- Avaliar acessibilidade (isso é ISSUE-24)
- Alterar `blind_solver_harness.py`, `gate_evaluator.py`, `blind_solve_run_record.py`
- Duplicar dataclasses entre `narrative_reviewer.py` e `evidence_reviewer.py`
- Criar skills em `.ai/skills/`
- Alterar casos canônicos
- Lançar exceção para blueprint com campos opcionais ausentes (tratar como lista vazia)

---

## Critérios de aceitação

A PR estará concluída quando:

1. existir `schemas/review_report.schema.yaml`
2. existir `generator/narrative_reviewer.py`
3. existir `generator/evidence_reviewer.py`
4. `ReviewFinding` e `ReviewReport` definidos em `narrative_reviewer.py`
5. `evidence_reviewer.py` importa dataclasses de `narrative_reviewer.py` (sem duplicação)
6. existir função pública `review_narrative(blueprint, ...) -> ReviewReport`
7. existir função pública `review_evidence(blueprint, ...) -> ReviewReport`
8. existir função pública `validate_review_report(report) -> list[str]`
9. existir função pública `report_to_dict(report) -> dict`
10. schema ter `additionalProperties: false` no topo
11. `reviewer_type` ter enum `narrative | evidence`
12. `status` ter enum `approved | needs_revision | blocked`
13. `findings[].severity` ter enum `critical | major | minor | info`
14. regras NR_001–NR_008 implementadas
15. regras ER_001–ER_008 implementadas
16. lógica de status derivada das severidades dos findings
17. nenhum reviewer muta o blueprint
18. fixtures válidas passam no schema
19. fixtures inválidas falham com mensagem correta
20. todos os 20 testes de `test_review_report_schema.py` passam
21. todos os 25 testes de `test_narrative_reviewer.py` passam
22. todos os 25 testes de `test_evidence_reviewer.py` passam
23. nenhum arquivo existente alterado (exceto doc opcional)
24. `pytest tests/ -q` passa sem regressão (1033+ testes)
25. `ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py` passa
26. nenhum LLM/internet usado
27. nenhum caso canônico alterado
28. nenhuma skill criada em `.ai/skills/`

---

## Abordagem TDD obrigatória

**RED:** escrever todos os testes primeiro. Confirmar que falham por
`ImportError` ou `ModuleNotFoundError` em `generator.narrative_reviewer` /
`generator.evidence_reviewer`, ou `FileNotFoundError` no schema.

**GREEN:** schema → `validate_review_report` → `review_narrative` (NR_001–NR_008) → `review_evidence` (ER_001–ER_008).

**REFACTOR:** organizar helpers de extração de campos do blueprint, dedup
de lógica de status entre os dois revisores.

---

## Validação final

```bash
ruff check generator/narrative_reviewer.py generator/evidence_reviewer.py

pytest tests/test_review_report_schema.py -q
pytest tests/test_narrative_reviewer.py -q
pytest tests/test_evidence_reviewer.py -q

pytest tests/test_gate_evaluator.py -q
pytest tests/test_gate_evaluation_schema.py -q
pytest tests/test_blind_solve_run_record.py -q
pytest tests/ -q

git diff --check
git status --short
git diff --stat
```

Confirmar:
- fixture `valid_narrative_approved.yaml` passa no schema
- `review_narrative` no blueprint do Aurora não lança exceção
- `review_evidence` no blueprint do Aurora não lança exceção
- `validate_review_report` detecta erros estruturais corretamente
- nenhum arquivo existente alterado (exceto doc opcional)
- nenhum caso canônico alterado
- `pytest tests/ -q` passa sem regressão (1033+ testes)

---

## Resposta final esperada do agente

Informar:
- skill utilizada e motivo
- arquivos criados
- API pública (funções, dataclasses, enums)
- regras NR_001–NR_008 implementadas (breve descrição de cada)
- regras ER_001–ER_008 implementadas (breve descrição de cada)
- lógica de status derivada
- fixtures criadas
- testes adicionados (contagem por arquivo)
- comandos executados com resultados
- resultado da suite completa (X passed, Y failed)
- confirmação de que nenhum arquivo existente foi alterado
- confirmação de que nenhum LLM/internet foi usado
- confirmação de que nenhuma skill foi criada
- próxima PR recomendada: ISSUE-25+26 — Workspace + Manual Orchestrator

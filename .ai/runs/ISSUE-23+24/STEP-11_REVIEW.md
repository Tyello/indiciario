# STEP-11 — REVIEW: `accessibility_reviewer.py` (AR_001–AR_006)

## Veredito: APROVADO (lógica). Blocker de coleta confirmado, fora do controle do executor.

## Escopo desta revisão

Revisei só `generator/accessibility_reviewer.py` (único arquivo editável da
allowlist do STEP-11) contra a spec (AR_001–AR_006,
`.ai/issues/ISSUE-23+24_SPEC.md` linhas 181–196, 423–430) e contra os 16 casos
de teste (33–48) já escritos em `tests/test_accessibility_reviewer.py`,
lendo o código diretamente.

## Método

`pytest tests/test_accessibility_reviewer.py -q` aborta na coleta (confirmado,
ver abaixo). Para validar a lógica sem editar nenhum arquivo do repo, executei
os 16 `test_caseNN_*` manualmente fora do pytest: carreguei o módulo de teste
via `exec()` num script standalone em `/tmp`, com o guard
`with pytest.raises(ModuleNotFoundError): import generator.accessibility_reviewer`
substituído por um `import` direto (script temporário, fora do repo, removido
ao final; nenhum arquivo do projeto tocado).

Resultado: **16/16 passam** (test_case33 a test_case48).

## Confirmação do blocker

```
$ .venv/Scripts/python.exe -m pytest tests/test_accessibility_reviewer.py -q
ERROR collecting tests/test_accessibility_reviewer.py
tests\test_accessibility_reviewer.py:51: in <module>
    with pytest.raises(ModuleNotFoundError):
E   Failed: DID NOT RAISE <class 'ModuleNotFoundError'>
Interrupted: 1 error during collection
```

Bate exatamente com o relatado no execution report. Causa raiz: guard RED do
STEP-09 (linhas 51–52), sem função após o GREEN deste step. Arquivo fora da
allowlist editável do STEP-11 — executor corretamente não o tocou.

## Validação ponto a ponto contra a spec (AR_001–AR_006)

| Regra | Severidade spec | Implementação | Caso de teste | Veredito |
|---|---|---|---|---|
| AR_001 | major | envelope com `count > MAX_DOCS_PER_ENVENVELOPE` (8), agrupado por `_enum_value(envelope)` | 33 (9 docs em E1) + 39 (8 docs, boundary, sem finding) | correto — `>` estrito confirmado pelo boundary do blueprint base (8 docs, 0 findings) |
| AR_002 | major | `_document_text(document)` (importado de visual_reviewer, não duplicado) acima de `MAX_CONTEUDO_CHARS` | 34 | correto, reusa helper VR_001 como documentado |
| AR_003 | minor | `not subtitulo and not descricao_curta` | 35 | correto, condição "E" (ambos ausentes) conforme spec |
| AR_004 | minor | `len(ids_citados) + len(codigos_citados) > MAX_CROSS_REFS` (6) | 36 | correto |
| AR_005 | info | `conteudo` vazio (`not conteudo`) | 37 (conteudo={}, dispara) + 39 (conteudo={"CORPO":...}, não dispara) | correto — decisão registrada no execution report é a única leitura consistente com os dois casos; severidade `info` confere com a spec |
| AR_006 | major | `not printable_cards` | 38 | correto |

Status/summary/ordenação (`_status_for`, `_summary_for`, `_SEVERITY_ORDER`) e
não-mutação (`getattr`/list comprehension, sem escrita no blueprint) batem com
casos 39–48:

- caso 39 (blueprint limpo → `approved`): confirmado.
- caso 40 (major presente → `needs_revision`): confirmado.
- caso 41 (import sem duplicar): `accessibility_reviewer.py` importa
  `ReviewFinding`, `VisualAccessibilityReviewReport`,
  `validate_visual_accessibility_review_report`, `report_to_dict`,
  `_SEVERITY_ORDER`, `_status_for`, `_summary_for`, `_now_iso`, `_enum_value`,
  `_document_text`, `MAX_CONTEUDO_CHARS` de `generator/visual_reviewer.py`;
  nenhuma dataclass/helper redefinida no arquivo novo — caso 41 usa
  identidade (`is`) para provar isso, e passa.
- caso 42 (não-mutação): passa com comparação de deepcopy.
- caso 43 (round-trip de validação de schema via
  `validate_visual_accessibility_review_report`): passa.
- caso 44 (`reviewer_type == "accessibility"`): confirmado no retorno de
  `review_accessibility`.
- caso 45 (ordenação por severidade): `findings.sort(key=...
  _SEVERITY_ORDER...)` aplicado antes do retorno — confirmado.
- caso 46 (`report_to_dict` round-trip): passa.
- caso 47 (limiares são constantes nomeadas no módulo,
  `MAX_DOCS_PER_ENVELOPE`/`MAX_CROSS_REFS`, sem números mágicos no corpo das
  regras): confirmado por leitura — todos os limiares usados em `_ar_findings`
  vêm de constante nomeada (`MAX_DOCS_PER_ENVELOPE`, `MAX_CONTEUDO_CHARS`
  importado, `MAX_CROSS_REFS`).
- caso 48 (caso real do Aurora, report passa no schema): passa.

## Confirmação de não-regressão dos outros dois arquivos do step

- `tests/test_visual_reviewer.py` → 16 passed (intacto, não tocado pelo STEP-11).
- `tests/test_visual_accessibility_review_report_schema.py` → 16 passed
  (intacto, não tocado pelo STEP-11).

## Allowlist

Único arquivo novo desta allowlist: `generator/accessibility_reviewer.py`.
`git status --short` confirma: nenhum arquivo fora da allowlist do STEP-11 foi
alterado (`generator/visual_reviewer.py`, `narrative_reviewer.py`,
`evidence_reviewer.py`, `review_report.schema.yaml` intactos;
`tests/test_accessibility_reviewer.py` não tocado, blocker preservado como
está, conforme protocolo).

## Conclusão

Implementação de `generator/accessibility_reviewer.py` (AR_001–AR_006) está
correta, completa e bate 1:1 com os 16 casos de teste 33–48 e com a tabela de
regras da spec. Decisão de design AR_005 ("conteudo vazio" em vez de "sem
campo TITULO/ASSUNTO") é a única leitura que satisfaz simultaneamente os
casos 37 e 39 — aprovada como registrada.

`Done quando` do step (lógica correta, 48 testes passando) está
**logicamente satisfeito** mas **não mecanicamente verificável** via
`pytest tests/test_accessibility_reviewer.py -q` por causa do guard obsoleto
fora da allowlist. STEP-11-FIX (já presente na issue) é o caminho correto
para destravar a execução mecânica do pytest sem reabrir o STEP-11.

Não implementei, não corrigi, não alterei nenhum arquivo do repo nesta
revisão (script de checagem manual ficou em `/tmp`, fora do repo, removido).

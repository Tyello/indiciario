# STEP-08 — EXECUTION: GREEN `review_visual` (VR_001–VR_006)

## Objetivo

Implementar `review_visual` em `generator/visual_reviewer.py` aplicando
VR_001–VR_006, suficiente para passar os 32 testes RED criados nos STEP-06/07
(`tests/test_visual_reviewer.py`) e os 16 do STEP-03/04
(`tests/test_visual_accessibility_review_report_schema.py`).

## Arquivo alterado

- `generator/visual_reviewer.py`

## O que foi adicionado

Constantes nomeadas (sem números mágicos):
- `MAX_CONTEUDO_CHARS = 2000` — limiar de VR_001.
- `VISUAL_DOC_TYPES = ("boletim", "chat", "depoimento", "folha_cruzamento", "log_acesso", "manual", "protocolo")` — conjunto de VR_006.

Helpers de leitura (espelhando `narrative_reviewer.py`, sem importar de lá —
módulos independentes por decisão arquitetural da spec):
- `_enum_value(value)` — valor plano de enum/string.
- `_document_text(document)` — concatena strings de `Documento.conteudo`.

Função semântica nova:
- `_vr_findings(blueprint) -> list[ReviewFinding]` — aplica as 6 regras.
- `review_visual(blueprint, blueprint_ref, report_id, created_by="orchestrator", overall_confidence="medium", notes="") -> VisualAccessibilityReviewReport` — monta o report final (ordena findings por severidade, deriva status via `_status_for` já existente, nunca muta o blueprint).

## Regras implementadas

| Código | Lógica | Severidade |
|---|---|---|
| VR_001 | `len(_document_text(documento)) > MAX_CONTEUDO_CHARS` por documento | major |
| VR_002 | Para cada id citado em `documentos[].ids_citados`, resolve o personagem por `id`; se `personagem.nome` não está nos `titulo` de `printable_cards`, finding | minor |
| VR_003 | `printable_cards[].codigo_visual` repetido (contagem por valor; finding por código duplicado, não por card) | major |
| VR_004 | `printable_cards[].tags_visuais` vazio/ausente | minor |
| VR_005 | `visual_procedural.locais` não vazio e `visual_procedural.mapas` vazio; severidade fixa `info`, nunca escalada (anti-regra do mapa do Aurora) | info |
| VR_006 | `documentos[].tipo` (valor de enum) fora de `VISUAL_DOC_TYPES` | minor |

Nota sobre VR_002: `PrintableCard` no `generator/models.py` não tem campo de
ligação direta a `personagem_id` (só `codigo_visual`/`titulo`/`tags_visuais`).
A correspondência usada é `personagem.nome == card.titulo`, que é exatamente
o padrão das fixtures de teste (`tests/test_visual_reviewer.py`, função
`_personagem`/`_printable_card`: "Narrador", "Executor", "Suspeito Alt",
"Testemunha" em ambos).

## Decisões de design

- `_vr_findings` segue fielmente o padrão `_nr_findings` de
  `generator/narrative_reviewer.py`: contador local `_next_id`, lista de
  `ReviewFinding`, sem mutar `blueprint`.
- `review_visual` reusa os helpers já existentes no módulo
  (`_status_for`, `_summary_for`, `_now_iso`, `_SEVERITY_ORDER`) criados no
  STEP-05 — nenhuma duplicação.
- VR_005 nunca eleva `status` acima de `approved` quando é o único finding,
  pois sua severidade é sempre `"info"` e `_status_for` só reage a
  `critical`/`major`.
- Sem números mágicos: limiares (`MAX_CONTEUDO_CHARS`) e conjuntos
  (`VISUAL_DOC_TYPES`) são constantes nomeadas no topo do módulo.
- `generator/narrative_reviewer.py`, `generator/evidence_reviewer.py` e
  `schemas/review_report.schema.yaml` não foram tocados.
- `generator/accessibility_reviewer.py` não foi criado (fora do escopo deste
  step).

## Comandos executados

```
pytest tests/test_visual_reviewer.py -q
→ 16 passed in 0.69s

pytest tests/test_visual_accessibility_review_report_schema.py -q
→ 16 passed in 0.47s
```

Total: 32/32 testes verdes, conforme "Done quando" do step.

## Confirmações

- `narrative_reviewer.py`/`evidence_reviewer.py`/`review_report.schema.yaml`: não alterados.
- `generator/accessibility_reviewer.py`: não criado.
- Nenhum número mágico solto fora de `MAX_CONTEUDO_CHARS`/`VISUAL_DOC_TYPES`.
- VR_005 nunca usa severidade acima de `info`.
- `review_visual` não muta o blueprint (sem `setattr`/mutação de listas; leitura pura).
- Nenhum LLM, rede ou renderizador usado.

## Próximo passo

Aguardando revisão do STEP-08 antes de avançar para STEP-09 (RED: regras
AR_001–AR_006).

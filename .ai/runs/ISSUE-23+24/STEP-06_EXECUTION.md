# Execution Report — ISSUE-23+24 STEP-06

STEP: STEP-06
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Criar `tests/test_visual_reviewer.py` com os casos 17-22 (uma regra VR por caso, testando que o finding correto é/não é emitido).

## Arquivos lidos
- .ai/issues/ISSUE-23+24_SPEC.md (tabela VR_001-VR_006, assinatura de review_visual, MAX_CONTEUDO_CHARS, VISUAL_DOC_TYPES)
- tests/test_narrative_reviewer.py (padrão de fixture/blueprint mínimo)
- generator/models.py (Blueprint, Personagem, Documento, Pista, Pilar, RedHerring, PrintableCard, VisualProcedural, LocalVisual, PapelPersonagem, TipoDocumento)
- generator/visual_reviewer.py (base já criada no STEP-05)

## Arquivos alterados
- tests/test_visual_reviewer.py (criado; somente casos 17-22)

## Comandos executados
- `.venv/Scripts/python.exe -m pytest tests/test_visual_reviewer.py -q` — 6 failed (RED esperado)

## O que foi feito
Criado `tests/test_visual_reviewer.py` com factory de blueprint mínimo (mesmo padrão de
`test_narrative_reviewer.py`: `_personagem`, `_documento`, `_pista`, `_objetivo`, `_dica`,
mais `_printable_card` novo) e 6 testes, um por regra:

- caso 17 — VR_001: conteúdo de documento concatenado acima de `MAX_CONTEUDO_CHARS` (importado
  do módulo, não número mágico no teste) deve emitir `VR_001`.
- caso 18 — VR_002: personagem citado em `ids_citados` de um documento sem `printable_card`
  correspondente deve emitir `VR_002`.
- caso 19 — VR_003: dois `printable_cards` com o mesmo `codigo_visual` deve emitir `VR_003`.
- caso 20 — VR_004: `printable_card` com `tags_visuais` vazio deve emitir `VR_004`.
- caso 21 — VR_005: `visual_procedural.locais` não vazio com `visual_procedural.mapas` vazio
  deve emitir `VR_005`.
- caso 22 — VR_006: documento com `tipo` fora do conjunto visual conhecido (`auditoria`, que
  existe em `TipoDocumento` mas não é um tipo com representação visual) deve emitir `VR_006`.

Todos os testes chamam `review_visual` via import local dentro do helper `_review`, garantindo
que a falha apareça como `ImportError`/`AttributeError` puro, não como erro de coleção do
arquivo (os imports de topo do arquivo trazem apenas símbolos já existentes em
`generator.models`).

## Evidência de aderência ao tipo (RED)
- 6 testes existem, todos falham por `ImportError: cannot import name 'review_visual' from
  'generator.visual_reviewer'` — ausência do símbolo, não erro de sintaxe/coleção.
- Nenhum caso 23-32 escrito neste step.
- `review_visual` não foi implementado.

## Divergências
- nenhuma

## Observações para revisão
- Cada caso corresponde a exatamente uma regra VR_001-VR_006 da tabela da spec.
- Próximo step (STEP-07) deve completar `tests/test_visual_reviewer.py` com os casos 23-32
  (status, ordenação, não-mutação, validação de schema, anti-regra VR_005, degradação graciosa
  sem `printable_cards`), ainda em RED.

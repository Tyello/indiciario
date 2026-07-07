# Review Report — ISSUE-40.2 STEP-02

STEP: STEP-02
STEP_TYPE: red
REVIEW_VERDICT: approved

## Verificação executada

- `.venv/Scripts/python.exe -m pytest tests/test_gate_font_fidelity.py -q`
  → `1 failed, 1 passed in 1.64s` (reprodução independente, não só leitura do
  execution report).
  - `test_gate_currently_misses_font_fallback` PASSOU.
  - `test_gate_catches_font_fallback` FALHOU: `ImportError: cannot import
    name 'evaluate_font_fidelity' from 'generator.canonical_quality_gate'`
    em `tests/test_gate_font_fidelity.py:131` — mesma linha/motivo do
    relatado no execution report.
- `git status --short` / `git diff --name-only`: só `.ai/issues/ISSUE-40.2.md`
  (tracked, modificado), `tests/test_gate_font_fidelity.py` (novo),
  `.ai/runs/ISSUE-40.2/` (novo). Nenhum arquivo em `generator/` tocado.
  `tests/test_font_vendoring.py` não modificado (linha 37 só importa
  `_MEDIR_FONTE_JS`, `_montar_html`, `browser`).

## Contra o contrato do STEP-02

1. **Dois testes em `tests/test_gate_font_fidelity.py`**: presentes —
   `test_gate_currently_misses_font_fallback`, `test_gate_catches_font_fallback`.
2. **Mesma montagem/template/fonte nos dois**: confirmado. Ambos recebem a
   fixture `css_com_fonte_removida` (mesmo `document_system.css` real com o
   bloco `@font-face` de `'DM Sans'` removido via monkeypatch). Ambos usam
   `TEMPLATE_COM_FONTE_QUEBRADA = "01_email.html"` e
   `FONTE_REMOVIDA = "DM Sans"` como constantes de módulo compartilhadas —
   não há duplicação com valores diferentes.
3. **`test_gate_currently_misses_font_fallback` passa hoje**: confirmado
   por execução. Não é tautológico: primeiro mede via Chromium real
   (`canvas.measureText`, reuso de `_MEDIR_FONTE_JS`/`_montar_html` da
   40.1) que a fonte de fato caiu em fallback nesta montagem — se essa
   asserção falhasse, o teste apontaria erro de setup, não do gate. Só
   depois verifica que `"font_fidelity"` está ausente de
   `qualification.criteria_results` do gate real
   (`evaluate_for_canonical` sobre `run_pipeline` de
   `examples/caso_canonico_iniciante.json`). Evidencia a lacuna real, não
   um assert vazio.
4. **`test_gate_catches_font_fallback` falha hoje**: confirmado — `ImportError`
   por função inexistente, não por bug de teste. Import feito dentro da
   função (não no topo do módulo), então não quebra a coleta do teste 1.
5. **Nada em `generator/` ou `tests/test_font_vendoring.py` alterado**:
   confirmado via git status/diff.

## Consistência com STEP-01

STEP-01 recomendou `name="font_fidelity"` em `QualificationCriterion`,
função nova `evaluate_font_fidelity(...) -> QualificationCriterion` em
`generator/canonical_quality_gate.py`, sem reuso de prefixo `GP_0XX`, sem
stage novo. O teste 2 chama exatamente
`generator.canonical_quality_gate.evaluate_font_fidelity(templates=[...],
browser=browser)` e assert `criterio.name == "font_fidelity"` — alinhado.
STEP-01 também recomendou extrair `_MEDIR_FONTE_JS`/`_montar_html` para
`generator/font_fidelity.py`; STEP-02 não fez essa extração (reusa via
import direto de `tests/test_font_vendoring.py`), o que é aceitável neste
step — a extração é tarefa de infraestrutura do STEP-03 (implementação),
não do RED. Não é divergência do contrato do STEP-02.

## Observação (não bloqueante)

- Os marcadores `Status: pending` por-step dentro do corpo de
  `.ai/issues/ISSUE-40.2.md` (linhas 40, 88 — STEP-01 e STEP-02) não foram
  atualizados para refletir conclusão, só os campos de controle no topo do
  arquivo (`CURRENT_STEP`, `LAST_COMPLETED_STEP`) o foram. Não é critério
  do contrato de STEP-02 e não bloqueia aprovação; sinalizado para
  consistência de rastreamento caso o orquestrador queira ajustar.

## Veredito

STEP-02 aprovado. RED real, evidencia a lacuna, não tautológico, escopo
respeitado (nada em `generator/` ou `tests/test_font_vendoring.py`
tocado). Libera avanço para STEP-03 — GREEN.

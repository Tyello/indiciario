# Execution Report — ISSUE-40.5 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos
- templates/base.html (linhas 1-60)
- templates/08_orcamento.html (grep `accent-bar|COR_PRIMARIA`)
- generator/renderer.py (grep `--accent`, 0 matches)
- .ai/issues/ISSUE-40.5.md
- .ai/issues/ISSUE-40.5_SPEC.md
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md
- (grep de varredura, não leitura integral) templates/*.html, templates/styles/document_system.css

## Arquivos alterados
- nenhum

## Comandos executados
- `Grep -- "--accent" templates/` → só `templates/base.html:24` (def em `:root`) e `templates/base.html:53` (`.doc-code { color: var(--accent); }`)
- `Grep -- "--accent" generator/` → 0 matches
- `Grep "extends.*base.html" templates/*.html` → 0 matches
- `Grep "accent-bar|COR_PRIMARIA" templates/08_orcamento.html` → 10 matches, todos `{{COR_PRIMARIA}}` (Jinja per-instituição), nenhum `var(--accent)`

## Resultado

**Achado 1 confirmado sem correção**: `--accent` só existe em `templates/base.html` — definição `:root { ... --accent: #8b1a1a; }` (linha 24, bloco `:root` inicia linha 19), uso único `.doc-code { color: var(--accent); }` (linha 53). Zero ocorrências em outros templates, em `templates/styles/document_system.css` ou em `generator/`.

**Achado 2 confirmado sem correção**: 0 templates `{% extends %}` `base.html` neste repo (mesmo resultado da 40.3/STEP-01). `base.html` continua órfão — `--accent` não vaza hoje para nenhum template ativo. Critério de aceite #2 já satisfeito antes de qualquer mudança de código; trabalho real da 40.5 é escopar `--accent` em `base.html` por disciplina de Camada 0 e criar teste de regressão.

**Achado 3 confirmado sem correção**: `.accent-bar` em `08_orcamento.html` (linha 30) usa exclusivamente `{{COR_PRIMARIA}}` (variável Jinja per-instituição, 9 outras ocorrências no arquivo), nunca a CSS var `--accent`. Coincidência de nome de classe, não uso disfarçado da marca. `COR_PRIMARIA` é o mecanismo per-instituição da 40.6 — fora de escopo, não tocar em `08_orcamento.html` no STEP-03.

**Classificação de Camada reaproveitada da 40.3** (`.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md`), sem reclassificar do zero. `NON_LAYER0_TEMPLATES` final para o STEP-02 (16 templates diegéticos = `PAPER_LAYER_TEMPLATES` + `SCREEN_LAYER_TEMPLATES`):

```python
NON_LAYER0_TEMPLATES = [
    "04_boletim.html", "05_carta.html", "06_log_acesso.html", "07_recibo.html",
    "08_orcamento.html", "09_extrato.html", "10_bilhete.html",
    "11_testamento_rascunho.html", "floorplan.html", "visual_map.html",
    "visual_character_card.html", "visual_location_card.html",
    "01_email.html", "02_whatsapp.html", "02_whatsapp2.html", "03_twitter.html",
]
```

Confirmado por grep: nenhum dos 16 referencia `--accent` (bate com achado 1, que só encontra a variável em `base.html`).

**Recomendação para STEP-02**: `test_diegetic_template_does_not_inherit_brand_accent` (parametrizado pelos 16 `NON_LAYER0_TEMPLATES`) nasce **GREEN por desenho** — nenhum template referencia `--accent` hoje, mesmo precedente da 40.4/STEP-02 (aging texture); documentar como guarda de regressão, não forçar RED artificial. `test_accent_variable_scoped_to_camada_0` é **RED real hoje** — `--accent` ainda está em `:root` global em `base.html`, não em `.camada-0`.

## Divergências
- nenhuma

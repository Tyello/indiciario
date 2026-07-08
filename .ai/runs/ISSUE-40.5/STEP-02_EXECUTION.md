# ISSUE-40.5 / STEP-02 — Execution report (RED)

**Tipo:** red
**Status:** concluído

## O que foi feito

Criado `tests/test_brand_isolation.py`, seguindo o padrão Playwright/CSS
computado de `tests/test_layer_rules.py` (renderização real via
`generator.font_fidelity._montar_html`, não grep de string em
arquivo-fonte).

Dois testes:

1. `test_diegetic_template_does_not_inherit_brand_accent` — parametrizado
   pelos 16 templates de `NON_LAYER0_TEMPLATES` (`PAPER_LAYER_TEMPLATES` +
   `SCREEN_LAYER_TEMPLATES`, reaproveitados de
   `.ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md` / `tests/test_layer_rules.py`).
   Renderiza cada template, varre todo elemento visível do `body` e falha se
   `color`, `background-color` ou qualquer `border-*-color` computado
   resolver para `rgb(139, 26, 26)` (equivalente computado de `#8b1a1a`), ou
   se `getComputedStyle(document.documentElement).getPropertyValue('--accent')`
   retornar não-vazio.
2. `test_accent_variable_scoped_to_camada_0` — lê `templates/base.html` e
   falha se não existir um seletor `.camada-0 { ... --accent ... }`, ou se
   `--accent` ainda estiver declarada dentro de `:root`.

## Output real do pytest

```
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[04_boletim.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[05_carta.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[06_log_acesso.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[07_recibo.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[08_orcamento.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[09_extrato.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[10_bilhete.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[11_testamento_rascunho.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[floorplan.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[visual_map.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[visual_character_card.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[visual_location_card.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[01_email.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[02_whatsapp.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[02_whatsapp2.html] PASSED
tests/test_brand_isolation.py::test_diegetic_template_does_not_inherit_brand_accent[03_twitter.html] PASSED
tests/test_brand_isolation.py::test_accent_variable_scoped_to_camada_0 FAILED

FAILED tests/test_brand_isolation.py::test_accent_variable_scoped_to_camada_0
  AssertionError: templates/base.html: nenhum seletor .camada-0 encontrado
  -- --accent precisa estar escopado a .camada-0, não em :root global
1 failed, 16 passed in 3.93s
```

Confirma exatamente a previsão do STEP-01:

- Teste de herança (16 parametrizações): **GREEN por desenho**, mesmo
  precedente da 40.4/STEP-02 — nenhum dos 16 templates diegéticos referencia
  `--accent` hoje (`base.html` é órfão), então não há nada para pegar ainda;
  serve como guarda de regressão para o STEP-03 e para o futuro.
- Teste de escopo `.camada-0`: **RED real hoje** — `--accent` continua
  declarada em `:root` global em `templates/base.html:24`, sem seletor
  `.camada-0`.

## Arquivos alterados

- `tests/test_brand_isolation.py` (novo)

## Comandos executados

- `.venv/Scripts/python.exe -m pytest tests/test_brand_isolation.py -q`
  (via PowerShell — `python` sem venv não resolvia no ambiente; documentado
  em memória de ambiente de teste)

## Revisão (checklist do STEP-02)

- Teste de herança inspeciona CSS computado real via Playwright, não grep?
  **Sim** — `page.evaluate` sobre `getComputedStyle` de cada elemento
  renderizado.
- Parametrização cobre os 16 templates de Camada 1/2 confirmados pelo
  STEP-01, não uma lista arbitrária? **Sim** — `NON_LAYER0_TEMPLATES`
  idêntica à lista entregue em `.ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md`.
- Teste de escopo (`.camada-0`) é RED real hoje? **Sim**, confirmado pelo
  output acima.

## Doc-impact

Nenhum nesta etapa — resolvido no STEP-05 (`templates/README.md`).

## Divergências

Nenhuma.

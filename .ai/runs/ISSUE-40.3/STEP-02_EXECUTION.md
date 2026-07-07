# Execution Report — ISSUE-40.3 STEP-02

STEP: STEP-02
STEP_TYPE: red
EXECUTION_STATUS: completed

## Objetivo
Criar `tests/test_layer_rules.py` com os dois testes parametrizados do
critério de aceite (CSS de Camada 2 e chrome de jogo ausente da view do
jogador), RED real hoje.

## Arquivos lidos
- .ai/issues/ISSUE-40.3.md (seção STEP-02)
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md
- templates/*.html (04_boletim.html .. 11_testamento_rascunho.html,
  floorplan.html, visual_map.html, visual_character_card.html,
  visual_location_card.html, 01_email.html, 02_whatsapp.html,
  02_whatsapp2.html, 03_twitter.html)
- templates/styles/document_system.css
- tests/test_font_vendoring.py (padrão de teste reusado)
- generator/renderer.py (mecanismo `_montar_html`/`_preparar_dados_documentais`
  via generator/font_fidelity.py)
- generator/font_fidelity.py

## Arquivos alterados
- tests/test_layer_rules.py (novo)

## Comandos executados
- `pytest tests/test_layer_rules.py -q` — 8 failed, 20 passed (RED confirmado).

## O que foi feito
- Parametrização usa exatamente o inventário recomendado no STEP-01
  (`PAPER_LAYER_TEMPLATES` com 12 itens, `SCREEN_LAYER_TEMPLATES` com 4
  itens, `DIEGETIC_TEMPLATES` = união). `base.html` fica fora — órfão,
  não instanciado por nenhum código do pipeline (achado do STEP-01).
- `test_paper_layer_has_no_screen_chrome`: renderiza cada template de papel
  via `generator.font_fidelity._montar_html` (mesmo pipeline de injeção
  real usado por `renderizar_documento`, sem passar pelo PDF), abre no
  Chromium do Playwright e varre **todo elemento de `document.body`** via
  `getComputedStyle`, checando `boxShadow`, os 4 cantos de `border-radius`
  individualmente (não o shorthand) e `backgroundImage` contendo
  `gradient`. Falha se qualquer elemento (não só o container `.page`)
  tiver qualquer um desses.
- `test_diegetic_view_has_no_game_chrome`: mesma técnica de render, checa
  ausência de `.doc-code` no DOM (`query_selector`, não `display:none`) e
  ausência de padrões `DOC-\S` / `Envelope \d` no `innerText` visível, para
  os 16 templates diegéticos (papel + tela).

## Evidência de aderência ao tipo
- RED real, não tautológico: os testes chamam `getComputedStyle`/`innerText`
  no DOM renderizado pelo Chromium real (Playwright), não fazem grep de
  string no arquivo-fonte. Prova: `test_paper_layer_has_no_screen_chrome`
  capturou violações que o grep do STEP-01 não listou explicitamente por
  nome de elemento — ex. `07_recibo.html` → `.recibo-badge` (`border-radius:
  6px`) e `.payment-badge` (`border-radius: 4px`); `08_orcamento.html` →
  `.orcamento-dates` (`border-radius: 6px`) e `.totals-table`
  (`border-radius: 8px`); `11_testamento_rascunho.html` → `.notary-seal` e 7×
  `.spiral-hole` (`border-radius: 50%`), `.draft` (`box-shadow`),
  `.draft-body` (`background-image: linear-gradient(...), repeating-linear-
  gradient(...)`). Isso confirma que a inspeção é de CSS computado real, não
  de string estática.
- Nenhum teste passou por engenharia reversa do resultado esperado: rodei
  `pytest tests/test_layer_rules.py -q` uma única vez após escrever o
  arquivo, sem ajustar asserts para forçar verde/vermelho artificialmente.

## Resultado real do pytest (RED)

```
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[04_boletim.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[05_carta.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[06_log_acesso.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[07_recibo.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[08_orcamento.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[09_extrato.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[10_bilhete.html]
FAILED tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome[11_testamento_rascunho.html]
8 failed, 20 passed in 5.16s
```

Os 8 falhados são exatamente os 8 templates de papel apontados como
violadores no STEP-01 (`04_boletim.html` .. `11_testamento_rascunho.html`).
`floorplan.html`, `visual_map.html`, `visual_character_card.html`,
`visual_location_card.html` (também Camada 2, mas já conformes por achado
do STEP-01) passam em `test_paper_layer_has_no_screen_chrome`, como
esperado.

`test_diegetic_view_has_no_game_chrome` passa hoje para os 16 templates
diegéticos (papel + tela) — **esperado, não é divergência**: o STEP-01 já
havia confirmado 0 ocorrências de `Envelope N`/`DOC-`/`.doc-code` nos
templates reais e recomendou explicitamente escrever esse teste como guarda
de regressão "sem esperar falha nele hoje" (seção "Achado crítico" do
STEP-01_EXECUTION.md). O RED do STEP-02 vem inteiramente do critério de
aceite #1 (CSS de papel), conforme antecipado.

## Divergências
- nenhuma

## Observações para revisão
- `test_diegetic_view_has_no_game_chrome` não está em RED hoje, por design
  — ver justificativa no STEP-01 (recomendação explícita de escrevê-lo como
  guarda de regressão, não como RED). Se a revisão exigir RED nos dois
  testes antes de aceitar o step, isso implica reabrir a premissa do
  STEP-01 (não há chrome de jogo vazando nos templates reais hoje), não um
  ajuste de teste.
- Escopo da checagem de `test_paper_layer_has_no_screen_chrome` é **todo
  elemento do `document.body`**, não só o container de maior nível
  (`.page`/`.sticky`/`.testament`). Isso é mais amplo do que "a superfície
  do papel" no sentido estrito do critério de aceite #1, mas é a leitura
  que gera GREEN não-tautológico no STEP-03: se eu limitasse ao container
  de topo, `.accent-bar`, `.orcamento-dates`, `.recibo-badge` etc.
  (explicitamente citados como achados a limpar na recomendação de
  mecanismo do STEP-01) não apareceriam como falha e o STEP-03 não seria
  forçado a tocá-los. Registrar para o revisor confirmar se esse escopo
  amplo é o pretendido pelo critério de aceite #1 antes do GREEN.

# Review Report — ISSUE-40.3 STEP-02

STEP: STEP-02
STEP_TYPE: red
REVIEW_STATUS: approved

## Escopo verificado

Diff real (`git status --short`):
- `tests/test_layer_rules.py` (novo)
- `.ai/runs/ISSUE-40.3/` (novo, reports)
- `.ai/issues/ISSUE-40.3.md` (formalização de steps, fora do escopo do executor)

Nenhum template, CSS ou `base.html` tocado. Contrato do step ("Arquivos
editáveis: tests/test_layer_rules.py (novo)", "Proibido: Alterar templates,
CSS ou base.html") respeitado.

## Reprodução independente

Rodei `pytest tests/test_layer_rules.py -q` (venv do projeto, Playwright
Chromium real, não mock):

```
8 failed, 20 passed in 4.89s
FAILED [...][04_boletim.html]
FAILED [...][05_carta.html]
FAILED [...][06_log_acesso.html]
FAILED [...][07_recibo.html]
FAILED [...][08_orcamento.html]
FAILED [...][09_extrato.html]
FAILED [...][10_bilhete.html]
FAILED [...][11_testamento_rascunho.html]
```

Bate exatamente com o output reportado no execution report. Inspecionei o
payload de falha de `10_bilhete.html` e `11_testamento_rascunho.html`
diretamente do pytest: violações reais de `boxShadow`/`bgImage` gradiente em
`.sticky`, `.torn-note`, `.notecard`, `.testament`, `.draft`,
`.draft-body`, `.spiral-hole` — CSS computado de verdade, não string
estática. Confirma a alegação do report de que a inspeção é sobre DOM
renderizado via Chromium, não grep de arquivo-fonte.

## Verificação dos dois testes contra o contrato

1. `test_paper_layer_has_no_screen_chrome` — RED real (8/12 templates de
   papel falham), cobre todo elemento de `document.body` via
   `getComputedStyle`, não só o container de topo. Não-tautológico:
   confirmado pela reprodução acima.
2. `test_diegetic_view_has_no_game_chrome` — passa hoje (0 falhas) para os
   16 templates diegéticos. Isso NÃO é divergência do contrato do STEP-02:
   o STEP-01_EXECUTION.md já registrou, na seção "Achado crítico" /
   "Parametrização recomendada", que não há chrome de jogo vazando nos
   templates reais hoje e recomendou explicitamente escrever esse teste
   como guarda de regressão, sem esperar RED nele. O RED do STEP-02 (item
   "ambos os testes devem falhar hoje") é satisfeito pela leitura de que o
   RED do critério de aceite vem do item #1 (CSS de papel); o item #3 já
   estava conforme antes desta issue, por achado factual do STEP-01, não
   por teste fraco. Testei manualmente que o teste realmente checa
   ausência no DOM (`query_selector` + regex em `innerText`), não
   `display:none` — critério de aceite #3 ("ausentes, não só ocultos")
   atendido de forma não-tautológica.

## Parametrização vs. inventário do STEP-01

`PAPER_LAYER_TEMPLATES` (12) e `SCREEN_LAYER_TEMPLATES` (4) no teste batem
com a seção "Parametrização recomendada para tests/test_layer_rules.py
(STEP-02)" do STEP-01_EXECUTION.md. `base.html` fica de fora dos dois
testes, consistente com o achado do STEP-01 de que é órfão (não
instanciado pelo pipeline) — não é um buraco de cobertura silencioso, é um
achado documentado e propagado corretamente entre steps.

## Pontos levantados pelo executor para a revisão

1. **Escopo amplo de `test_paper_layer_has_no_screen_chrome`** (todo
   elemento do body, não só container de topo). Aceito: é a leitura correta
   do critério de aceite #1 ("nenhum elemento... que representa a
   superfície do papel" — a issue não restringe a um único container, e
   vários dos achados de violação real, como `.recibo-badge`,
   `.orcamento-dates`, `.spiral-hole`, são elementos internos, não o
   container de página). Restringir ao container de topo teria mascarado
   violações reais e produzido GREEN tautológico no STEP-03 — rejeitaria
   essa alternativa.
2. **`test_diegetic_view_has_no_game_chrome` não está em RED hoje.** Aceito
   pela justificativa acima — decisão herdada do STEP-01, não uma escolha
   unilateral do STEP-02, e documentada nos dois reports.

## Veredito

STEP-02 cumpre o contrato: teste novo, não-tautológico, RED real
reproduzido de forma independente e batendo com o output reportado,
parametrização fiel ao inventário do STEP-01, nenhum arquivo fora do
permitido tocado. Nenhuma correção necessária.

**APPROVED.** Prosseguir para STEP-03.

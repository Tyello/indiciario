# STEP-02 EXECUTION — ISSUE-40.1

**Step:** STEP-02 — RED: teste que detecta fallback de fonte
**Type:** red
**Owner:** executor
**Status:** done

## O que foi feito

Criado `tests/test_font_vendoring.py`, parametrizado por template × fontes,
cobrindo o inventário corrigido do STEP-01 (nota de decisão na ISSUE-40.1.md,
6 famílias, `Inter` fora de escopo):

| Template | Fontes testadas |
|---|---|
| `01_email.html` | DM Sans |
| `04_boletim.html` | Source Serif 4 |
| `05_carta.html` | Libre Baskerville |
| `06_log_acesso.html` | JetBrains Mono |
| `07_recibo.html` | DM Sans, Caveat |
| `08_orcamento.html` | DM Sans |
| `09_extrato.html` | DM Sans, JetBrains Mono |
| `10_bilhete.html` | Caveat |
| `11_testamento_rascunho.html` | Caveat, Libre Baskerville, Playfair Display |

Cobertura: 9 templates, 6 famílias, todas as ocorrências do inventário STEP-02
da issue.

## Como o teste renderiza

`_montar_html()` reproduz o pipeline de injeção de
`generator.renderer.renderizar_documento` (CSS documental, classes de body,
cabeçalho/rodapé) até obter o HTML final, sem passar pela etapa de PDF —
permite inspecionar a fonte computada com o Chromium do Playwright
diretamente via `page.set_content`, sem depender de `_fake_pdf_permitido()`
nem gerar arquivo de saída.

## Desvio do esqueleto da SPEC — justificado por evidência empírica

O esqueleto em `ISSUE-40.1_SPEC.md` (STEP-02) sugere `getComputedStyle()`
para detectar a fonte aplicada. Isso não funciona: `getComputedStyle(el)
.fontFamily` devolve a pilha de fontes tal como declarada no CSS (string),
não a fonte de fato usada para desenhar o texto.

Testei em seguida `document.fonts.check("16px 'X'")` (citado no objetivo do
STEP-02 da issue) diretamente contra este Chromium (via Playwright,
`chromium-1223`, versão `148.0.7778.96`):

```
bogus: True
DM Sans: True
```

`document.fonts.check()` retorna `True` mesmo para uma família **inexistente**
(`'ThisFontDoesNotExist12345'`) — inútil para este teste, teria dado falso
GREEN em STEP-02 e mascarado o defeito que a issue quer capturar.

Troquei para a técnica clássica de detecção de fonte via
`canvas.measureText`: mede a largura de um texto de amostra com
`font-family: '<Fonte>', monospace` e compara com a largura do mesmo texto
usando só `monospace`. Larguras iguais = fallback (fonte não aplicada).
Validação do método antes de usar no teste:

```
DM Sans                    {'w1': 712.546875, 'w2': 712.546875, 'differs': False}
Arial                      {'w1': 850.78125,  'w2': 712.546875, 'differs': True}
Times New Roman            {'w1': 802.6640625,'w2': 712.546875, 'differs': True}
ThisFontDoesNotExist12345  {'w1': 712.546875, 'w2': 712.546875, 'differs': False}
JetBrains Mono             {'w1': 712.546875, 'w2': 712.546875, 'differs': False}
```

Fontes reais do SO (Arial, Times New Roman) produzem largura diferente do
fallback `monospace`; fontes ausentes (DM Sans, JetBrains Mono, família
bogus) produzem a mesma largura — método distingue corretamente presença
de ausência. Escrito no docstring do arquivo de teste para o revisor.

## RED real — confirmado rodando pytest

Comando: `.venv\Scripts\python.exe -m pytest tests/test_font_vendoring.py -q`
(ambiente local, `.venv` com Playwright + chromium já instalado — ver
`C:\Users\Marcelo\.claude\projects\...\memory\test-environment.md`).

Saída (resumo — 9 falhas, uma por template, todas por causa correta):

```
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[01_email.html-fontes0]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[04_boletim.html-fontes1]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[05_carta.html-fontes2]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[06_log_acesso.html-fontes3]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[07_recibo.html-fontes4]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[08_orcamento.html-fontes5]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[09_extrato.html-fontes6]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[10_bilhete.html-fontes7]
FAILED tests/test_font_vendoring.py::test_template_nao_cai_em_fallback_de_fonte_de_sistema[11_testamento_rascunho.html-fontes8]
9 failed in 1.88s
```

Exemplo de mensagem de falha (motivo correto — fonte não aplicada, não erro
de setup/import):

```
E   AssertionError: 09_extrato.html: fonte 'DM Sans' não foi de fato aplicada pelo Chromium — fallback silencioso para fonte de sistema (sem @font-face local declarado ainda, ISSUE-40.1)
E   assert False
```

Nenhuma falha por `ImportError`/`ModuleNotFoundError`/erro de fixture —
todas as 9 falham no `assert fonte_aplicada`, ou seja, pelo motivo que o
teste existe para capturar.

## Lint

```
.venv\Scripts\python.exe -m ruff check tests/test_font_vendoring.py
All checks passed!
```

## Arquivos alterados

- `tests/test_font_vendoring.py` (novo)

Nenhuma alteração em `generator/renderer.py`, CSS ou templates (proibido
neste step). Nenhuma fonte baixada/vendorizada (proibido neste step).

## Done-check contra a issue

- [x] `tests/test_font_vendoring.py` existe, cobre todas as famílias do
      inventário corrigido do STEP-01 (6 famílias, 9 templates).
- [x] Execution report mostra saída do pytest comprovando falha (RED) real
      no estado atual do código.
- [x] Falha por motivo correto (fonte não aplicada), não erro de
      setup/import.
- [x] Nenhuma alteração fora de `tests/test_font_vendoring.py`.

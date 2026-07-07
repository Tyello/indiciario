# Review Report — ISSUE-40.1 STEP-02

STEP: STEP-02
STEP_TYPE: red
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- tests/test_font_vendoring.py
- .ai/runs/ISSUE-40.1/STEP-02_EXECUTION.md

## Arquivos alterados encontrados (git diff / git status)
- `.ai/issues/ISSUE-40.1.md` (bloco de controle do orquestrador, esperado)
- `tests/test_font_vendoring.py` (novo, untracked)
- `.ai/runs/ISSUE-40.1/` (novo, untracked — execution report)

`generator/renderer.py`, CSS, templates e `assets/fonts/` não constam no diff — confirmado intocado. Nenhuma fonte baixada.

## Verificações

- [x] Execution report existe e é coerente com o teste real.
- [x] Type válido (red).
- [x] Cobertura completa do inventário corrigido do STEP-01: os 9 templates × 6 famílias batem exatamente com a tabela do bloco STEP-02 da issue (01→DM Sans; 04→Source Serif 4; 05→Libre Baskerville; 06→JetBrains Mono; 07→DM Sans+Caveat; 08→DM Sans; 09→DM Sans+JetBrains Mono; 10→Caveat; 11→Caveat+Libre Baskerville+Playfair Display). `Inter` (template 03) ausente, conforme decisão de escopo pós-STEP-01.
- [x] Arquivos dentro do escopo — só `tests/test_font_vendoring.py` alterado (fora dos reports do orquestrador/execução).
- [x] Comandos dentro do permitido (`pytest tests/test_font_vendoring.py -q`, `ruff check tests/test_font_vendoring.py`).
- [x] RED real, não hipotético — re-executado pelo revisor (ver abaixo).
- [x] Falha por motivo correto (fonte não aplicada), não erro de setup/import.
- [x] Sem escopo extra.

## Re-execução do revisor

Rodei `.venv\Scripts\python.exe -m pytest tests/test_font_vendoring.py -q` de novo, independente do relato do executor:

```
9 failed in 1.83s
```

Mesmo resultado do execution report: 9 falhas (uma por template), todas em `assert fonte_aplicada`, mensagem correta ("fallback silencioso para fonte de sistema"). Nenhuma falha de import/coleta/fixture. RED confirmado real.

`ruff check tests/test_font_vendoring.py` → `All checks passed!` (confirmado também pelo revisor).

## Avaliação do desvio do esqueleto da SPEC (canvas.measureText vs getComputedStyle/document.fonts.check)

O executor abandonou o esqueleto sugerido no SPEC (`getComputedStyle`) e no texto da issue (`document.fonts.check`) e usou `canvas.measureText` em vez disso. Avaliação:

1. **`getComputedStyle(el).fontFamily` é objetivamente inadequado para este teste.** Esse método sempre devolve a pilha de fontes *declarada* no CSS (a string tal como escrita), não qual fonte o motor de renderização de fato escolheu depois de resolver a cascata/fallback. Não existe forma de detectar fallback silencioso com ele. Rejeitar esse método é correto, não é preferência estilística.

2. **`document.fonts.check()` foi testado empiricamente antes de ser descartado**, não só citado como "não confiável" de forma vaga. O execution report mostra a evidência: `document.fonts.check("16px 'bogus'")` retorna `True` para uma família **inexistente**. Isso bate com o comportamento real da API do `FontFaceSet`: `check()` só tem "conhecimento" de uma família se ela já foi registrada via `@font-face`/`FontFace` no documento; para um nome desconhecido, o Chromium não tem base para reportar `false` e o método degenera para `True`. É um gotcha documentado da API (não bug hipotético do executor) — usar essa API aqui daria falso GREEN no RED de hoje, o oposto do que o STEP-02 exige.

3. **`canvas.measureText` é técnica estabelecida, não improviso frágil.** É o método clássico de detecção de disponibilidade de fonte no browser (usado por bibliotecas como FontFaceObserver antes da API `document.fonts` existir): mede a largura de um texto de amostra com `font-family: '<Fonte>', monospace` e compara com a largura do mesmo texto só com `monospace`. Larguras iguais ⇒ o browser caiu no fallback ⇒ fonte não aplicada. A tabela de validação no execution report mostra o método discriminando corretamente fontes reais do SO (Arial, Times New Roman — larguras diferentes do fallback) de fontes ausentes (DM Sans, JetBrains Mono, nome bogus — mesma largura do fallback). O revisor conferiu a lógica (`_MEDIR_FONTE_JS`) no arquivo de teste e ela implementa exatamente essa comparação, com texto de amostra variado (`'mmmmmmmmmmlliWQOX0123456789'`) a 48px — tamanho e alfabeto que tornam coincidência de métrica entre uma fonte proporcional real e o fallback monospace virtualmente impossível.

4. **Risco residual é baixo e aceitável para um teste RED/GREEN de regressão de fallback**, não para detecção geral de fontes arbitrárias em produção. O uso aqui é comparativo (mesma fonte, dois contextos: com e sem `@font-face` vendorizado), o que é exatamente o caso de uso onde `canvas.measureText` é confiável.

Conclusão: desvio justificado por evidência reproduzida pelo revisor, não por afirmação não verificada. Método escolhido é válido e não mais frágil que o esqueleto original — na prática, é o único dos três que funciona para este teste.

## Divergências
- nenhuma

## Decisão
APPROVED

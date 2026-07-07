# Execution Report — ISSUE-40.1 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos
- templates/ (todo o conteúdo, via grep)
- templates/styles/document_system.css
- .ai/issues/ISSUE-40.1.md
- .ai/issues/ISSUE-40.1_SPEC.md

## Arquivos alterados
- nenhum

## Comandos executados
- `grep -rn "font-family" templates/ | grep -v "sans-serif\|serif\|monospace\|system-ui"` — comando literal do STEP-01/SPEC. Resultado: **inadequado**, filtra por substring em qualquer parte da linha, então elimina quase todas as fontes custom reais porque seus fallbacks contêm "serif"/"sans-serif"/"monospace" (ex.: `'DM Sans', 'Helvetica Neue', Arial, sans-serif` é descartado). Só sobram ocorrências de `Caveat`/`Segoe Print` (fallback `cursive`, não capturado pelo filtro).
- `grep -rn "font-family" templates/` (sem o `grep -v`) — usado para levantar o inventário real, revisado manualmente linha a linha.

## Resultado

Inventário real de `font-family` custom (fonte web, não stack de sistema) por template, confirmado manualmente:

| Template | Fonte(s) custom encontrada(s) | Linha(s) |
|---|---|---|
| `01_email.html` | `DM Sans` | 14 |
| `02_whatsapp.html` / `02_whatsapp2.html` | nenhuma — só `"Segoe UI", Helvetica, Arial, sans-serif` (stack de sistema) | 47 |
| `03_twitter.html` | `Inter` (dentro de stack `-apple-system, 'Inter', 'Helvetica Neue', sans-serif`) | 12 |
| `04_boletim.html` | `Source Serif 4` | 12, 146, 175, 227, 235 |
| `05_carta.html` | `Libre Baskerville`; também `Segoe Print`/`Lucida Handwriting` (stack de sistema, cursive) | 14; 210 |
| `06_log_acesso.html` | `JetBrains Mono` | 72, 77, 91, 111, 227 |
| `07_recibo.html` | `DM Sans`; `Caveat`; também `Segoe Print`/`Lucida Handwriting` (sistema) | 12; 259; 154 |
| `08_orcamento.html` | `DM Sans`; também `Segoe Print`/`Lucida Handwriting` (sistema) | 14; 396, 409 |
| `09_extrato.html` | `DM Sans`; `JetBrains Mono` | 14; 61, 89, 116, 191, 207, 225, 235, 265 |
| `10_bilhete.html` | `Caveat` | 12, 115, 134, 141, 170, 187, 195 |
| `11_testamento_rascunho.html` | `Libre Baskerville`; `Playfair Display`; `Caveat` | 12; 73, 111; 214, 263, 375, 384, 395, 411, 424, 438, 547 |
| `templates/styles/document_system.css` | nenhuma das 5 famílias — só stacks de sistema via variáveis (`--ind-font-institutional`: Arial/Helvetica/Segoe UI; `--ind-font-technical`/`--ind-font-system`: Courier New; `--ind-font-letter`: Georgia/Times; `--ind-font-signature`: Segoe Script/Lucida Handwriting/Brush Script MT) | 4–8, várias |

Famílias custom únicas em uso: **DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair Display, Inter**.

## Divergências
- DVG-EXEC-001: comando literal do STEP-01 (`grep -rn "font-family" templates/ | grep -v "sans-serif\|serif\|monospace\|system-ui"`) é ineficaz — filtra por substring em qualquer trecho da linha, não isola stacks 100% genéricos. Elimina praticamente todas as ocorrências reais de fontes custom porque os fallbacks das próprias declarações custom contêm essas palavras. Inventário real acima foi obtido por `grep -rn "font-family" templates/` sem o `-v` e revisão manual.
- DVG-EXEC-002: tabela da SPEC (`ISSUE-40.1_SPEC.md`, seção Contexto) está desatualizada frente ao estado real do repo (a própria SPEC já avisa: "diagnóstico foi lido em 05/07/2026 e o repo pode ter mudado desde então"):
  - SPEC diz "04 (boletim) → Caveat"; real: `04_boletim.html` usa `Source Serif 4`, não tem `Caveat`.
  - SPEC diz "07 → Libre Baskerville"; real: `Libre Baskerville` está em `05_carta.html` e `11_testamento_rascunho.html`, não em `07_recibo.html` (que usa `DM Sans` + `Caveat`).
  - SPEC diz "08 (orçamento) → DM Sans, JetBrains Mono, Source Serif 4"; real: `08_orcamento.html` só usa `DM Sans`. `JetBrains Mono` está em `06_log_acesso.html` e `09_extrato.html` (que também usa `DM Sans`); `Source Serif 4` está só em `04_boletim.html`.
  - SPEC pergunta se `02 (WhatsApp)` também usa DM Sans; real: não — só stack de sistema (`Segoe UI`).
- DVG-EXEC-003: duas famílias custom em uso **não constam** na lista de 5 da SPEC/issue: `Playfair Display` (`11_testamento_rascunho.html`) e `Inter` (`03_twitter.html`, dentro de stack que também tem `-apple-system` — caso limítrofe, decisão de escopo fica para STEP-02/03: se `Inter` deve ser tratado como custom a vendorizar ou como fallback de UI de sistema aceitável).
- DVG-EXEC-004: `templates/styles/document_system.css` não declara nenhuma das famílias custom hoje — usa só stacks de sistema via variáveis CSS. Não há `@font-face` nenhum no arquivo atualmente (confirma o diagnóstico da issue: v1 não vendoriza nada).

Nenhuma alteração de código/CSS/template feita neste step, conforme escopo.

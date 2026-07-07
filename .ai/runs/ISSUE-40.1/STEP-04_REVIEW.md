# Review Report — ISSUE-40.1 STEP-04

STEP: STEP-04
STEP_TYPE: validation
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- Nenhum arquivo de produto (execution report apenas), salvo dependência de fonte de sistema revelada (não foi o caso).

## Arquivos alterados encontrados
- `git diff --name-only` (working tree, acumulado desde HEAD): `.ai/issues/ISSUE-40.1.md`, `generator/renderer.py`, `templates/styles/document_system.css`.
- `generator/renderer.py` e `templates/styles/document_system.css` têm mtime anterior ao STEP-04 (renderer.py 09:54, css 09:31 — ambos antes de `STEP-03_FIX-01_REVIEW.md` às 10:15 e de `STEP-04_EXECUTION.md` às 10:17). Confirmado: pertencem ao STEP-03/STEP-03_FIX-01, não foram tocados neste step.
- `tests/test_font_vendoring.py` também sem alteração desde STEP-03_FIX-01 (mtime 09:53, anterior ao STEP-04).
- `.ai/runs/ISSUE-40.1/` e `assets/fonts/` untracked de steps anteriores, não deste review.

## Verificação independente (reprodução, não confiança no relato)

1. Inspeção de fontes de sistema, reexecutada pelo revisor (PowerShell, `%WINDIR%\Fonts`, `HKLM`, `HKCU`, pasta per-user de `%LOCALAPPDATA%`) filtrando pelas 6 famílias (DM Sans, Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair Display): **zero resultados em todos os quatro locais**. Confirma a alegação do executor — nenhuma das 6 famílias está instalada nesta máquina, nem como fonte de sistema nem por usuário.
2. `pytest tests/test_font_vendoring.py -q` reexecutado pelo revisor: **8 passed in 2.03s**. Bate com o relato do executor (8 passed in 2.06s).
3. Inspeção de `templates/styles/document_system.css`: todas as 6 regras `@font-face` usam `src: url('../../assets/fonts/*.woff2') format('woff2')` — **nenhuma usa `local(...)`**. Isso é estruturalmente relevante para o critério de aceite #2: sem `local()`, o navegador nunca consulta uma fonte homônima instalada no SO para resolver essas `font-family`; o arquivo vendorizado é a única fonte de verdade sempre que o `@font-face` carrega com sucesso, independente de o SO ter ou não uma fonte de mesmo nome instalada. Isso é comportamento padrão de CSS/@font-face (não experimental), não uma suposição do executor.

## Avaliação do ponto crítico levantado (item 4 do pedido de revisão)

A pergunta era: "máquina já não tem as fontes" é evidência suficiente do critério de aceite #2, ou faltava instalar uma das 6 fontes temporariamente no SO e confirmar que `@font-face` ainda vence (prova mais forte)?

Resposta: a evidência apresentada é suficiente, e o teste adicional sugerido (instalar fonte temporariamente) seria redundante, não mais forte, dado o achado do item 3 acima. A pergunta "o `@font-face` vence uma fonte de sistema homônima?" só é um risco real quando o `@font-face` declara `src: local('Nome Da Fonte')` como fallback — nesse caso sim, o navegador poderia preferir a instalação do SO. Como nenhuma das 6 declarações usa `local()`, a precedência de `@font-face` sobre fonte de sistema homônima é garantida pela especificação CSS em qualquer navegador Chromium moderno, não depende de estado da máquina de teste. A verificação real que importava — "o teste falha (RED) se `@font-face` não estiver correto, e passa (GREEN) quando está" — já foi estabelecida no ciclo RED (STEP-02, 9 failed reais) → GREEN (STEP-03/STEP-03_FIX-01, 8 passed). O que o STEP-04 precisava confirmar é que esse GREEN não é um artefato de coincidência com fonte de sistema presente — e isso está confirmado: a máquina não tem as 6 fontes, então o GREEN observado não pode ser explicado por fallback de sistema mascarando o resultado.
Nota: o teste em si mede resolução de fonte via `canvas.measureText` num canvas isolado (não a cascata real do DOM/texto visível) — essa limitação já foi identificada e tratada no ciclo STEP-03/STEP-03_FIX-01 (bug do `05_carta.html`, auditoria manual de cascata CSS nos 8 pares restantes). Está fora do escopo do STEP-04 reabrir essa auditoria; o STEP-04 valida especificamente a dimensão "sem fonte de sistema", que é o que foi pedido e o que foi entregue.

## Verificações
- [x] Execution report existe e contém evidência bruta de comando (não apenas afirmação)
- [x] Type `validation` — só comandos de validação/inspeção executados
- [x] Nenhum arquivo de produto alterado neste step (mtimes confirmam que as alterações em `renderer.py`/`document_system.css` são do STEP-03/STEP-03_FIX-01)
- [x] Nenhuma fonte instalada no SO como parte da verificação
- [x] Verificação não foi pulada por analogia — reexecutada de fato pelo executor e pelo revisor
- [x] Resultados batem entre relato e reexecução independente do revisor (fontes ausentes, 8/8 GREEN)
- [x] Critério de aceite #2 avaliado com profundidade além do relato (checagem de `local()` nas declarações `@font-face`)

## Divergências
- nenhuma

## Decisão
APPROVED

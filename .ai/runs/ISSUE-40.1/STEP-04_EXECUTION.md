# ISSUE-40.1 — STEP-04 — Execution Report

Owner: executor
Type: validation (high-risk)
Status: done — aguardando revisão

## Objetivo do step

Confirmar que o GREEN do STEP-03 (+ STEP-03_FIX-01) não depende de fontes
instaladas globalmente na máquina de dev. Rodar `pytest
tests/test_font_vendoring.py -q` em ambiente sem as fontes do SO (DM Sans,
Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair
Display) — ou, se isso não for possível de forma isolada (container/venv
limpo), renomear temporariamente fontes de sistema equivalentes se
estiverem instaladas, rodar o teste, e restaurar depois.

## O que foi feito

### 1. Checagem do estado real do SO (antes de qualquer simulação)

Não presumi que as fontes estivessem ausentes — confirmei via inspeção do
sistema, sem instalar nada:

```
Get-ChildItem "$env:WINDIR\Fonts" | Where-Object { $_.Name -match
  "DM Sans|DMSans|Caveat|JetBrains|Source Serif|SourceSerif|Playfair|
   Libre Baskerville|LibreBaskerville" }
→ (nenhum resultado)

Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
  | filtro no mesmo padrão
→ (nenhum resultado)

Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
→ 1 entrada apenas: "Ubuntu Mono (TrueType)" (não relacionada ao escopo)

Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
→ 1 arquivo apenas: "UbuntuMono[wght].ttf" (não relacionado ao escopo)
```

Resultado: nenhuma das 6 famílias do inventário (DM Sans, Caveat,
JetBrains Mono, Source Serif 4, Libre Baskerville, Playfair Display) está
instalada nesta máquina — nem como fonte de sistema (`%WINDIR%\Fonts` /
`HKLM`), nem como fonte por usuário (`HKCU` / pasta per-user do
`%LOCALAPPDATA%`). Esta máquina de dev já é, por padrão, um "ambiente
limpo" em relação a essas 6 famílias — não houve necessidade de renomear
nada nem de montar container/venv isolado à parte: a condição pedida pelo
step (rodar sem as fontes do SO instaladas) já é o estado real da máquina.

### 2. Execução da suíte nesse ambiente

```
.venv/Scripts/python.exe -m pytest tests/test_font_vendoring.py -q
→ ........                                                                 [100%]
  8 passed in 2.06s
```

8/8 GREEN, consistente com o resultado documentado no
`STEP-03_FIX-01_EXECUTION.md` (8 pares template×fonte no escopo pós-fix).
Isso confirma que o `@font-face` local declarado em
`templates/styles/document_system.css` (com `font-display: block`) e a
espera por `document.fonts.ready` em `generator/renderer.py` garantem a
fonte correta independentemente de qualquer fonte de sistema — nesta
máquina, nenhuma das 6 famílias existe no SO, e mesmo assim o teste (que
mede a fonte resolvida via `canvas.measureText`, não a string CSS
declarada) confirma aplicação real de cada família.

Nenhum ajuste de código, teste ou CSS foi necessário — nenhuma dependência
de fonte de sistema não coberta pelo STEP-03 foi revelada.

## Verificação do "proibido"

- Nenhuma fonte foi instalada no sistema.
- Não pulei a verificação: rodei o teste de fato após confirmar via
  inspeção real do SO que as fontes estão ausentes (não assumi por
  analogia ao STEP-03).

## Done quando (checklist do step)

- [x] Execution report comprova, com evidência de comando, que o teste
  passa em ambiente sem as fontes de sistema instaladas — evidência dupla:
  (a) inspeção do SO confirmando ausência das 6 famílias em
  `%WINDIR%\Fonts`, `HKLM`, `HKCU` e pasta per-user; (b) `pytest
  tests/test_font_vendoring.py -q` GREEN (8/8) nesse mesmo estado.

## Transição

`Type: validation` é high-risk. `STATUS`, `NEXT_ACTION` e `REVIEW_STATUS`
atualizados na issue para review obrigatória (`NEXT_ACTION: review`,
`REVIEW_STATUS: pending`). STEP-05 segue `pending` — avanço cabe ao
orquestrador/revisor.

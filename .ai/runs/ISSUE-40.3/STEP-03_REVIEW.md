# Review Report — ISSUE-40.3 STEP-03

STEP: STEP-03
STEP_TYPE: green
REVIEW_STATUS: approved

## Escopo verificado

`git diff --stat` real:
- `generator/renderer.py` (+33)
- `templates/04_boletim.html` .. `11_testamento_rascunho.html` (8 templates, -88 total)
- `templates/base.html` (+11, comentário)
- `templates/styles/document_system.css` (+21)
- `tests/test_layer_rules.py` (novo, do STEP-02)
- `.ai/runs/ISSUE-40.3/` (novo, reports)

Bate com "Arquivos alterados" declarado no execution report. Nenhum arquivo
fora do contrato do step (`Arquivos editáveis`) tocado. `generator/renderer.py`
foi tocado, autorizado pelo contrato ("só se a flag `SHOW_GAME_CHROME`
exigir... registrar se tocado") — divergência da razão original (flag não foi
implementada) mas o toque é da injeção de classe de camada, dentro do
mecanismo já existente (`_injetar_classes_body`), registrado no report.

## Reprodução independente

`.venv/Scripts/python.exe -m pytest tests/test_layer_rules.py -q` →
**28 passed** (5.16s local). Bate com o output do execution report.

`.venv/Scripts/python.exe -m ruff check generator/` → **All checks passed**.
Bate com o report.

## Verificação do CSS (`document_system.css`)

`.layer-screen` (Camada 1) não introduz regra de reset — sem restrição,
critério de aceite #2 preservado. `.layer-paper`/`.layer-paper *` reseta
`box-shadow`/`border-radius`/`background-image` com `!important`, descrito
como rede de segurança, não mecanismo principal. Confirmado por escopo:
diff não toca `--accent`, paleta por família de documento nem nenhuma
variável de marca — 40.4/40.5 não vazaram.

## Verificação da origem limpa nos 8 templates de papel

Reproduzi via grep independente
(`box-shadow|border-radius|linear-gradient|radial-gradient`, case-insensitive)
nos 8 templates apontados como GREEN:
- 7 templates → 0 ocorrências.
- `06_log_acesso.html` → 1 ocorrência: `border-radius: 0;` (linha 271).
  Não é violação: é override explícito para zero, e o teste checa
  `cantos !== '0px'` — `0` computa para `0px`, portanto conforme. Não
  contradiz a alegação do report de "0 ocorrências de vocabulário de card
  web"; a leitura correta é "0 ocorrências que sobrevivem ao computed style
  check", que é o que importa para o critério de aceite.

Inspecionei o diff completo de `08_orcamento.html`: remoções são
line-precise (`box-shadow`, `border-radius: 2px/6px/10px/8px/4px`,
`linear-gradient` → `background: {{COR_PRIMARIA}}` sólido). Nenhuma mudança
de texto, estrutura ou dado do documento — só vocabulário visual, como
declarado.

## Verificação da injeção de camada (`renderer.py`)

`TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER` batem exatamente com
`PAPER_LAYER_TEMPLATES`/`SCREEN_LAYER_TEMPLATES` de `tests/test_layer_rules.py`
(STEP-02, já revisado/aprovado) e com o inventário do STEP-01. Mecanismo
reutiliza `_injetar_classes_body`, mesmo padrão já usado para
`doc-type-*`/`doc-family-*`/`doc-player` — não introduz mecanismo novo de
template engine, coerente com o achado do STEP-01 de que o motor é
substituição por string, não Jinja2.

## Verificação da decisão de arquitetura sobre `base.html`

Terceira opção (nem partial, nem flag) é justificada e não é evasão do
contrato: o STEP-01 já havia estabelecido, via grep real, que 0 templates
`{% extends %}` `base.html` e que `generator/renderer.py` não carrega o
arquivo — a premissa da issue original (herança vazando chrome) não se
sustenta contra o repo atual. Diante disso, implementar partial ou flag
seria mecanismo morto (nada os consumiria). A decisão foi registrada como
comentário HTML no próprio arquivo, rastreável, e não altera comportamento
(arquivo continua órfão, conforme declarado). Critério de aceite #3
continua satisfeito pelo teste automatizado (`test_diegetic_view_has_no_game_chrome`,
16/16 passando), que é o que a issue realmente exige — o mecanismo
específico (partial vs. flag) era meio, não fim.

## Critérios de aceite (1-4) — confirmação

1. Confirmado: `test_paper_layer_has_no_screen_chrome`, 12/12 papel passa;
   origem limpa nos 8 que violavam (verificado por grep independente acima).
2. Confirmado: nenhum template de Camada 1 tocado; `.layer-screen` sem
   regra de reset.
3. Confirmado: já satisfeito antes da issue (achado STEP-01), agora coberto
   por teste automatizado como guarda de regressão — leitura já aceita na
   revisão do STEP-02, não reaberta aqui.
4. Confirmado: `tests/test_layer_rules.py`, 28/28 passed, reproduzido
   independentemente.

## Escopo — confirmação de não-vazamento

- Nenhuma paleta papel-cor por tipo de documento introduzida (40.4).
- Nenhum isolamento de `--accent` tocado (40.5).
- Hotel Aurora / narrativa de canônicos não tocados.
- `generator/renderer.py`: só a injeção de classe de camada (dict novo +
  3 linhas em `_injetar_classes_body`), confirmado no diff.

## Pontos levantados pelo executor

Observação sobre `border-radius: 50%` removido por completo em vez de
redesenhado (selo notarial, spiral-hole) aceita: é leitura literal e
correta do critério de aceite #1 ("papel... não tem `border-radius`"), sem
abrir exceção semântica não pedida pela issue. Redesenho em SVG seria
gold-plating fora do escopo desta issue.

## Veredito

STEP-03 cumpre o contrato: GREEN real e não-tautológico (origem limpa,
não só mascarada por `!important`, confirmado por reprodução independente),
decisão de arquitetura sobre `base.html` justificada contra o repo real
(não uma fuga do contrato), escopo não vazou para 40.4/40.5, nenhum arquivo
fora do permitido tocado. Nenhuma correção necessária.

**APPROVED.** Prosseguir para STEP-04.

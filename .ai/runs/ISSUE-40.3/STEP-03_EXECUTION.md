# Execution Report — ISSUE-40.3 STEP-03

STEP: STEP-03
STEP_TYPE: green
EXECUTION_STATUS: completed

## Objetivo
GREEN: introduzir `.layer-screen`/`.layer-paper` em `document_system.css`,
aplicar às classificações do STEP-01, limpar as origens pontuais de
`box-shadow`/`border-radius`/gradiente nos 8 templates de papel, e resolver
a questão do chrome de jogo em `base.html` (decisão de arquitetura).

## Arquivos lidos
- .ai/runs/ISSUE-40.3/STEP-01_EXECUTION.md, STEP-02_EXECUTION.md
- tests/test_layer_rules.py
- templates/styles/document_system.css
- templates/base.html
- generator/renderer.py
- templates/04_boletim.html .. 11_testamento_rascunho.html (inline `<style>`)

## Arquivos alterados
- `templates/styles/document_system.css` — adicionadas `.layer-screen`
  (Camada 1, sem restrição) e `.layer-paper`/`.layer-paper *` (Camada 2,
  reset `!important` de `box-shadow`/`border-radius`/`background-image`,
  rede de segurança).
- `generator/renderer.py` — novos `TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER`
  (16 templates diegéticos, cópia do inventário do STEP-01/STEP-02) e injeção
  da classe `layer-screen`/`layer-paper` no `<body>` dentro de
  `_injetar_classes_body` — mesmo mecanismo já usado para `doc-type-*`/
  `doc-family-*`/`doc-player`, não edição manual de cada template.
- `templates/04_boletim.html`, `05_carta.html`, `06_log_acesso.html`,
  `07_recibo.html`, `08_orcamento.html`, `09_extrato.html`, `10_bilhete.html`,
  `11_testamento_rascunho.html` — removidas as declarações pontuais de
  `box-shadow`/`border-radius`/`linear-gradient`/`radial-gradient`/
  `repeating-linear-gradient` do `<style>` inline (origem limpa, não só
  coberta pelo `!important` de `document_system.css`). Nenhuma mudança de
  layout/conteúdo textual — só remoção de sombra, cantos arredondados e
  textura em gradiente (aged-paper, lined-paper, spiral binding, selos/
  emblemas circulares, tarja de destaque).
- `templates/base.html` — comentário HTML no topo do arquivo documentando a
  decisão de arquitetura (ver seção abaixo). Nenhuma mudança de
  comportamento (arquivo continua órfão).

## Decisão de arquitetura: `base.html` (partial vs. flag `SHOW_GAME_CHROME`)

**Nenhuma das duas opções da issue original foi implementada.** O STEP-01
já havia confirmado, via `Grep "extends"` em `templates/*.html`, que **0
templates estendem `base.html`** — a premissa da issue (chrome de jogo
vazando por herança de `base.html`) não se sustenta contra o repo atual. O
motor de render (`generator/renderer.py`) não é Jinja2 com herança; é
substituição por string sobre cada `.html` standalone. `base.html` não é
carregado por nenhum código do pipeline (`generator/`, `scripts/`).

Optei pela opção (b) do STEP-01 ("manter como scaffold/exemplo documentado,
Camada 0 apenas, nunca instanciado por Camada 1/2"), não pela opção (a)
("apagar como código morto"):
- Deletar um arquivo referenciado só em documentação (`templates/README.md`,
  outras issues) fora do escopo desta issue seria uma decisão maior do que
  o necessário para satisfazer o critério de aceite #3 — o critério já está
  satisfeito (chrome de jogo não vaza para a view do jogador hoje, achado
  do STEP-01/STEP-02).
- Registrei a decisão como comentário HTML no topo de `templates/base.html`
  para que a próxima pessoa que abrir o arquivo entenda imediatamente por
  que ele contém `doc-code`/"Envelope N" sem violar o critério de aceite.
- Não introduzi a flag `SHOW_GAME_CHROME` em `generator/renderer.py`: seria
  mecanismo novo para um problema que não existe no pipeline ativo (nenhum
  ponto de código hoje injeta esse header a partir de `base.html`).

Isso cumpre o critério de aceite #3 pela via mais simples que reflete o
estado real do repo, sem gold-plating de um mecanismo de herança que não
existe.

## Comandos executados
- `pytest tests/test_layer_rules.py -q` → **28 passed** (100%, GREEN real).
- `ruff check generator/` → **All checks passed** (só `generator/renderer.py`
  tocado em código Python).

## Evidência de GREEN não-tautológico
- Verifiquei via `grep -c "box-shadow\|border-radius:.*[1-9]\|linear-gradient\|radial-gradient"`
  nos 8 templates de papel → 0 ocorrências em todos, confirmando que a
  origem foi limpa (não só mascarada pelo reset CSS).
- Verifiquei via script Python (`generator.font_fidelity._montar_html` +
  regex no `<body>`) que a classe `layer-paper`/`layer-screen` é injetada
  corretamente em `01_email.html` (`layer-screen`), `02_whatsapp2.html`
  (`layer-screen`), `03_twitter.html` (`layer-screen`), `04_boletim.html`
  (`layer-paper`) e `floorplan.html` (`layer-paper`) — inclusive os dois
  templates com gap pré-existente em `DOCUMENT_PLAYER_TEMPLATES` (achado do
  STEP-01, fora de escopo desta issue), confirmando que a nova injeção de
  camada é independente desse gap.
- O reset `.layer-paper *` em `document_system.css` é rede de segurança
  (`!important`) intencional — a limpeza de origem nos 8 templates é o que
  efetivamente resolve o critério de aceite #1; se removida a classe/reset
  CSS, os templates continuariam conformes.

## Verificação dos critérios de aceite

1. **Todo template de Camada 2 não usa `box-shadow`/`border-radius`/gradiente
   na superfície do papel** — confirmado: `pytest tests/test_layer_rules.py::test_paper_layer_has_no_screen_chrome`
   passa para os 12 templates de papel; origem limpa nos 8 que violavam.
2. **Templates de Camada 1 continuam podendo usar esses recursos** —
   confirmado: nenhuma alteração em `01_email.html`, `02_whatsapp.html`,
   `02_whatsapp2.html`, `03_twitter.html`; `.layer-screen` não aplica
   nenhuma restrição CSS (classe documental, sem regras de reset).
3. **Nenhum template diegético renderiza `doc-code`/título/"Envelope N" na
   view do jogador** — já satisfeito antes desta issue (achado do STEP-01);
   `test_diegetic_view_has_no_game_chrome` (16 templates) confirma como
   guarda de regressão, agora cobrindo também a explicação formal de por
   que `base.html` não conta como violação.
4. **Teste automatizado comprova os itens 1-3** — `tests/test_layer_rules.py`,
   28/28 passed.

## Escopo — confirmação de não-vazamento

- Não toquei paleta papel-cor por tipo de documento (40.4).
- Não toquei isolamento de `--accent` da marca (40.5).
- Não adicionei mapa ao Hotel Aurora nem alterei narrativa de canônicos.
- `generator/renderer.py` só recebeu a injeção de classe de camada (novo
  dict + 3 linhas em `_injetar_classes_body`), nenhuma outra função tocada.

## Divergências
- Nenhuma. A decisão de arquitetura sobre `base.html` diverge da redação
  literal da issue ("partial vs. flag `SHOW_GAME_CHROME`"), mas segue
  explicitamente a recomendação registrada no STEP-01_EXECUTION.md, que já
  havia sido aceita sem correção na revisão do STEP-02.

## Observações para revisão
- O reset `.layer-paper *` em `document_system.css` é intencionalmente amplo
  (todo elemento descendente, não só `.page`), espelhando o escopo do teste
  do STEP-02 (decisão já revisada/aprovada no STEP-02_REVIEW.md).
- Elementos que usavam `border-radius: 50%` para representar formas físicas
  plausíveis em papel impresso (selo notarial, furos de espiral, marca de
  círculo à caneta) tiveram o raio removido por completo (viram quadrados/
  retângulos), não redesenhados como formas equivalentes sem `border-radius`
  (ex.: SVG). Decisão deliberada: a regra do critério de aceite #1 não abre
  exceção semântica, e qualquer redesenho ficaria fora do escopo de
  "remover vocabulário de card web" desta issue.

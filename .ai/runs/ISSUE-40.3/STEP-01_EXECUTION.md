# ISSUE-40.3 / STEP-01 — Execution Report

Tipo: reading. Owner: executor.

## Método

Inventário via `Glob templates/*.html` (21 arquivos + `base.html` = 22). Para cada
um: `Grep` de `extends`/`base.html` (heranca), `box-shadow|border-radius|linear-
gradient|radial-gradient` (violação Camada 2), `Envelope|DOC-|doc-code` (chrome de
jogo hardcoded). Leitura de `generator/renderer.py` (mecanismo real de render) e
`templates/styles/document_system.css` (CSS global compartilhado).

## Achado crítico: premissa da issue sobre `base.html` está desatualizada

`Grep "extends"` (case-insensitive) em `templates/*.html` → **0 matches**.
`Grep "base.html"` no repo inteiro → só aparece em `.ai/issues/*` e
`templates/README.md`, nunca em código (`generator/renderer.py`, `scripts/`, ou
qualquer `.html`).

Conclusão: **nenhum template estende `base.html`**. O engine de render não é Jinja2
com herança — é motor de substituição próprio (`generator/renderer.py`, funções
`_injetar_css_documental`, `_injetar_classes_body`, `_injetar_cabecalho_rodape_
documental`) que lê cada `.html` como string standalone e injeta CSS/classes via
regex. `base.html` é órfão: não carregado por nenhum código do pipeline atual.

Além disso, `_injetar_cabecalho_rodape_documental` (linhas 181-189 de
`generator/renderer.py`) já é hoje um no-op — os dois ramos (`if template_nome in
DOCUMENT_PLAYER_TEMPLATES` / `else`) retornam `html` inalterado. Comentário no
código já declara a intenção ("Documentos diegéticos do jogador não exibem
códigos, envelope, paginação..."), mas a função não injeta nada, então também não
remove nada — é vestígio morto, não um mecanismo ativo de vazamento.

`Grep "Envelope|DOC-|doc-code"` em cada um dos 8 templates de papel e 4 de tela
(`01_email`, `02_whatsapp`, `02_whatsapp2`, `03_twitter`, `04_boletim` .. `11_
testamento_rascunho`) → **0 matches** em todos. Nenhum template diegético tem
chrome de jogo hardcoded no próprio HTML. As únicas ocorrências de `Envelope`/
`doc-code`/`DOC-` no diretório `templates/` estão em `base.html` (órfão) e
`facilitator_guide.html` (Camada 0, uso correto — "Envelope 1", "{{TOTAL_
ENVELOPES}}").

**Implicação para STEP-02/03**: o critério de aceite #3 (chrome de jogo ausente da
view do jogador) já está satisfeito hoje pelos templates reais, não pelo mecanismo
descrito na issue original. O RED real do STEP-02 vem do critério #1 (CSS de
papel), não do #3. Recomendo ainda escrever o teste #3 como guarda de regressão
(especialmente cobrindo `base.html`, ver recomendação de mecanismo abaixo), mas
sem esperar falha nele hoje para os templates de papel/tela existentes.

## Tabela de classificação

| Template | Camada | Motivo |
|---|---|---|
| `00_envelope_capa.html` | 0 (jogo) | capa física do envelope, prop do produto; usa `box-shadow`/gradiente para textura de papel do envelope — aceitável em Camada 0 (não é "documento de papel" avaliado pela regra #1) |
| `facilitator_guide.html` | 0 (jogo) | guia do facilitador, imprime "Envelope N" e `{{TOTAL_ENVELOPES}}` — uso correto, só facilitador vê |
| `dicas_contextuais.html` | 0 (jogo) | dicas para facilitador |
| `print_guide.html` | 0 (jogo) | guia técnico de impressão para facilitador |
| `printable_cards.html` | 0 (jogo) | ficha administrativa de cartões para impressão, uso do facilitador, não é evidência diegética; usa `linear-gradient` (linha 98) — aceitável em Camada 0 |
| `base.html` | órfão / não classificável em 0-1-2 | não referenciado por nenhum código ou template ativo; contém o header `doc-code`/`doc-title`/`doc-meta` (Envelope) que a issue supôs vazar — na prática não vaza porque nada o herda |
| `01_email.html` | 1 (tela) | print de cliente de e-mail; `box-shadow`/`border-radius` presentes (linhas 58-59, 91, 184) — correto para Camada 1 |
| `02_whatsapp.html` | 1 (tela) | print de chat; `box-shadow`/`border-radius` presentes — correto |
| `02_whatsapp2.html` | 1 (tela) | variante de chat; mesmo padrão — correto. **Não está em `DOCUMENT_PLAYER_TEMPLATES`/`TEMPLATE_DOCUMENT_CLASS` do `renderer.py`** (gap pré-existente, não introduzido por esta issue — registrar, não corrigir aqui) |
| `03_twitter.html` | 1 (tela) | print de rede social; `border-radius` presente (várias) — correto. Também ausente de `DOCUMENT_PLAYER_TEMPLATES` (mesmo gap) |
| `04_boletim.html` | 2 (papel) | documento impresso; **viola regra**: `box-shadow` (linha 26), `border-radius` (linhas 28, 102, 236, 280, 361) |
| `05_carta.html` | 2 (papel) | carta; **viola regra**: `box-shadow` (linha 25), `border-radius` (linhas 58, 86, 247) |
| `06_log_acesso.html` | 2 (papel) | log de acesso; **viola regra**: `border-radius` (linhas 27, 53, 178); já tem reset `border-radius: 0` em media query de impressão (linha 274) — reset parcial pré-existente |
| `07_recibo.html` | 2 (papel) | recibo; **viola regra**: `box-shadow` (linha 28), `border-radius` (linha 185) |
| `08_orcamento.html` | 2 (papel) | orçamento; **viola regra** (citado no diagnóstico original): `box-shadow` (linha 26), `border-radius` (linhas 28, 102, 236, 280, 361 — mesmo padrão de `04_boletim`, provável origem compartilhada), `linear-gradient` em `.accent-bar`, `.orcamento-dates` com `border-radius: 6px` |
| `09_extrato.html` | 2 (papel) | extrato bancário; **viola regra**: `box-shadow` (linha 25), `border-radius` (linhas 27, 46) |
| `10_bilhete.html` | 2 (papel) | bilhete manuscrito; **viola regra**: `box-shadow` (linhas 29, 81, 152), `border-radius` (linhas 216, 235), gradiente (linha 49) |
| `11_testamento_rascunho.html` | 2 (papel) | rascunho de testamento; **viola regra**: `box-shadow` (linhas 28, 314, 340), `border-radius` (linhas 139, 286, 337, 444), gradiente (linhas 39-40) |
| `floorplan.html` | 2 (papel) | planta física entregue como prop impresso; sem `box-shadow`/`border-radius`/gradiente hoje — já conforme |
| `visual_map.html` | 2 (papel) | mapa físico entregue como prop impresso; sem violações — já conforme |
| `visual_character_card.html` | 2 (papel) | cartão de personagem impresso; sem violações — já conforme |
| `visual_location_card.html` | 2 (papel) | cartão de local impresso; sem violações — já conforme |

Templates que `{% extends %}` `base.html`: **nenhum** (achado acima).

`templates/styles/document_system.css`: já usa vocabulário corretamente escopado
em alguns pontos — `.doc-family-email .email-container { border-radius: 2mm;
box-shadow: ... }` (linha 202) é Camada 1 correta. Não há `box-shadow`/`border-
radius` global em `.page` neste arquivo — todas as violações de Camada 2
encontradas estão em `<style>` inline dentro de cada template de papel (`04_
boletim.html` .. `11_testamento_rascunho.html`), não no CSS compartilhado.

## Recomendação de mecanismo para STEP-03

**Não usar nem "extração de partial" nem flag `SHOW_GAME_CHROME`** no sentido
literal da spec — a premissa de que templates herdam chrome de `base.html` não
se sustenta contra o repo atual (0 templates estendem `base.html`). Forçar esse
refactor criaria trabalho sem efeito (nada consome `base.html` hoje).

Proposta de menor esforço, mesmo resultado:

1. **CSS (regra #1, o problema real)**: adicionar `.layer-screen`/`.layer-paper`
   em `document_system.css` conforme esqueleto da spec (rede de segurança
   `!important`), E remover as declarações pontuais de `box-shadow`/`border-
   radius`/gradiente dos `<style>` inline nos 8 templates de papel listados acima
   (`04_boletim` .. `11_testamento_rascunho`) — é edição direta de cada template,
   não herança.
2. **Chrome de jogo (regra #3)**: manter o teste de regressão do STEP-02
   cobrindo os templates diegéticos reais (já conformes) mais um caso específico
   para `base.html` — decisão a registrar no STEP-03: ou (a) apagar `base.html`
   por ser código morto não referenciado, ou (b) mantê-lo como exemplo/scaffold
   documentado como Camada 0 apenas, nunca instanciado por templates de Camada
   1/2. Não recomendo introduzir a flag `SHOW_GAME_CHROME` em `generator/
   renderer.py` porque não há nenhum ponto de código que hoje injete esse
   header — seria mecanismo novo para um problema que não existe no pipeline
   ativo.
3. Gap secundário registrado (fora do escopo desta issue, não corrigir aqui):
   `02_whatsapp2.html` e `03_twitter.html` ausentes de `DOCUMENT_PLAYER_
   TEMPLATES`/`TEMPLATE_DOCUMENT_CLASS` em `generator/renderer.py` — não recebem
   classe `doc-player`/`doc-type-*`. Não afeta os critérios de aceite desta issue
   (nenhum tem chrome hardcoded), mas pode ser relevante para 40.4 (paleta por
   tipo de documento).

## Parametrização recomendada para `tests/test_layer_rules.py` (STEP-02)

```
PAPER_LAYER_TEMPLATES = [
    "04_boletim.html", "05_carta.html", "06_log_acesso.html", "07_recibo.html",
    "08_orcamento.html", "09_extrato.html", "10_bilhete.html",
    "11_testamento_rascunho.html", "floorplan.html", "visual_map.html",
    "visual_character_card.html", "visual_location_card.html",
]
SCREEN_LAYER_TEMPLATES = [
    "01_email.html", "02_whatsapp.html", "02_whatsapp2.html", "03_twitter.html",
]
DIEGETIC_TEMPLATES = PAPER_LAYER_TEMPLATES + SCREEN_LAYER_TEMPLATES
GAME_LAYER_TEMPLATES = [
    "00_envelope_capa.html", "facilitator_guide.html", "dicas_contextuais.html",
    "print_guide.html", "printable_cards.html",
]
```

`base.html` fora de todas as listas de parametrização (não é renderizado
standalone no pipeline); tratar sua remoção/documentação como decisão explícita
no STEP-03, não como item de teste parametrizado.

## Done

Tabela de classificação completa para os 22 arquivos de `templates/*.html`
(incluindo `base.html`), lista de heranças de `base.html` (vazia, achado
documentado), e recomendação de mecanismo com justificativa registradas acima.

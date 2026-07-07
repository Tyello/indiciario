# SPEC — ISSUE-40.3: Regras de camada (Tela vs. Papel) + remoção do chrome do jogo

## Contexto

Do diagnóstico, achados #2 e #3 da crítica (seção 2):

> Gradientes e border-radius em papel. `.accent-bar` com `linear-gradient`, `.orcamento-dates` com `border-radius: 6px`, `.page` do orçamento com `border-radius: 2px` e `box-shadow` — vocabulário de web card, não de documento impresso.

> O chrome do jogo vaza para a evidência. `base.html` imprime `doc-code` (`DOC-000`), título e "Envelope N" num header de todas as páginas que o estendem. O `.doc-player { display:none }` mitiga, mas o header do `base.html` em si é estrutural.

Esta issue resolve as duas coisas juntas porque ambas são refactors do mesmo par de arquivos (`document_system.css` + `base.html`) e faz sentido revisar a cascata uma única vez.

## Escopo

- Introduzir o conceito formal de Camada 1 (tela) vs. Camada 2 (papel) no CSS.
- Remover chrome de jogo (`doc-code`, título, "Envelope N") de qualquer view diegética.
- **Não inclui** ainda a separação de `--accent` da marca (isso é a 40.5, que depende desta) nem a paleta papel-cor por tipo de documento (40.4).

## Passo a passo técnico

### STEP-01 — Classificação

Confirmar contra o repo atual (o inventário abaixo vem do diagnóstico, pode ter mudado):

| Camada | Templates |
|---|---|
| 0 (jogo) | `00_envelope_capa.html`, protocolo, dicas, gabarito, guia do facilitador |
| 1 (tela) | `01_email.html` (e variantes), `02_whatsapp.html`, `03_twitter.html` |
| 2 (papel) | `04_boletim.html`, `06_log_acesso.html`, `08_orcamento.html`, manual, cadastro, contrato, demais |

### STEP-02 — RED

```python
# tests/test_layer_rules.py

PAPER_LAYER_TEMPLATES = [
    "04_boletim.html", "06_log_acesso.html", "08_orcamento.html",
    # completar conforme STEP-01
]

FORBIDDEN_PAPER_CSS_PROPERTIES = ["box-shadow", "border-radius", "linear-gradient", "radial-gradient"]

@pytest.mark.parametrize("template", PAPER_LAYER_TEMPLATES)
def test_paper_layer_has_no_screen_chrome(template):
    """
    Falha se qualquer regra CSS aplicada à superfície do papel
    (classe .page / .paper-surface, a confirmar nome real) usar
    sombra, radius ou gradiente.
    """
    ...

DIEGETIC_TEMPLATES = PAPER_LAYER_TEMPLATES + ["01_email.html", "02_whatsapp.html", "03_twitter.html"]

@pytest.mark.parametrize("template", DIEGETIC_TEMPLATES)
def test_diegetic_view_has_no_game_chrome(template):
    """
    Renderiza a view do JOGADOR (não a do facilitador) e falha se
    doc-code, título de jogo ou 'Envelope N' aparecerem visíveis no DOM
    (não apenas escondidos via display:none — devem estar ausentes
    da view do jogador, não só ocultos).
    """
    ...
```

Confirmar RED real antes de prosseguir.

### STEP-03 — GREEN

**CSS (`document_system.css`):**

```css
/* Camada 1 — tela: chrome de app é correto aqui */
.layer-screen {
  /* box-shadow, border-radius e gradientes são permitidos nesta camada */
}

/* Camada 2 — papel: reset explícito, documento impresso não tem sombra de si mesmo */
.layer-paper {
  box-shadow: none !important;
  border-radius: 0 !important;
  background-image: none !important; /* mata gradientes usados como fundo */
}
.layer-paper * {
  box-shadow: none;
  border-radius: 0;
}
```

Aplicar `.layer-screen` em `01_email.html`/`02_whatsapp.html`/`03_twitter.html` e `.layer-paper` nos templates de papel. Remover os usos pontuais de `border-radius`/`box-shadow`/`gradient` que hoje estão espalhados em `.accent-bar`, `.orcamento-dates`, `.page` (o `!important` acima é rede de segurança, mas o ideal é também limpar a origem de cada regra, não só sobrescrever).

**`base.html` (chrome do jogo):**

Extrair o header hoje estrutural (`doc-code`, título, "Envelope N") para um partial próprio (ex.: `_facilitator_chrome.html`), incluído explicitamente apenas pelos templates de Camada 0. Templates de Camada 1/2 deixam de estender o `base.html` que carrega esse header por padrão — ou o `base.html` passa a receber uma flag (`{{SHOW_GAME_CHROME}}`, default `false`) que só a Camada 0 ativa.

Preferir a segunda abordagem (flag) se o esforço de reestruturar toda a árvore de herança de templates for desproporcional — mas registrar no PR qual caminho foi escolhido e por quê, porque isso é uma decisão de arquitetura, não só de CSS.

### STEP-04 — Verificação

Rodar `test_layer_rules.py` contra todos os templates existentes (não só os citados no diagnóstico) — o inventário do STEP-01 pode estar incompleto.

### STEP-05 — Docs

`templates/README.md`, nova seção "Sistema de Camadas":

```markdown
## Sistema de Camadas

- **Camada 0 (jogo)**: envelope, protocolo, dicas, gabarito. Único lugar com
  chrome de produto (doc-code, título, numeração de envelope) e marca Indiciário.
- **Camada 1 (tela)**: e-mail, chat, rede social. São prints de tela — sombra,
  border-radius e chrome de app são corretos. Classe CSS: `.layer-screen`.
- **Camada 2 (papel)**: todo o resto. Documento impresso não tem sombra de
  si mesmo. Classe CSS: `.layer-paper` (reset automático de shadow/radius/gradiente).

Todo template novo declara sua camada explicitamente.
```

Estender `framework/09_SISTEMA_VISUAL.md` (criado na 40.2) com a mesma seção, linkando para o README.

## Fora de escopo

- Paleta papel-cor por tipo de documento → 40.4.
- Isolamento de `--accent` da marca → 40.5 (mas usa a mesma extração de chrome feita aqui como base).

## Riscos / atenção do revisor

- Esta é a issue de maior superfície de mudança do lote — toca `base.html`, que é herdado por praticamente todo template. Rodar a suíte completa de regressão visual, não só os testes novos.
- Se `base.html` tiver lógica além de chrome (ex.: meta tags, scripts) misturada no mesmo arquivo, a extração do header precisa ser cirúrgica para não quebrar o resto.

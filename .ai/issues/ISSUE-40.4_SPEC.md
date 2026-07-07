# SPEC — ISSUE-40.4: Papel-cor como taxonomia + remoção do envelhecimento do boletim

## Contexto

Do diagnóstico, achado #5 da crítica:

> Boletim com direção de arte de "documento envelhecido". `04_boletim.html` aplica textura de papel envelhecido (`radial-gradient` âmbar) num boletim datado de ontem. [...] Envelhecer papel novo é tell clássico de prop de jogo.

E da seção 3.5:

> Papel-cor como taxonomia: boletim `#e4f2e4` (verde), depoimento `#fdf7d8` (amarelo), laudo pericial (novo) `#eef0f6` (azulado). Chapado, sem gradiente.

No benchmark, o jogador aprende a taxonomia de documento pela cor do papel (verde = boletim, amarelo = depoimento) em segundos — é um dispositivo funcional, não estético.

## Escopo

Apenas `04_boletim.html` e o depoimento (se já existir como template separado — confirmar no STEP-01; se depoimento ainda não tem template próprio, criar o token de cor mas não é obrigatório criar o template completo nesta issue, que é de repaginação, não de novo tipo de documento).

## Passo a passo técnico

### STEP-01 — Levantamento

Confirmar no repo:
- Se existe um template de depoimento separado do boletim, ou se depoimento é uma variação de blueprint do mesmo template.
- A regra CSS exata do envelhecimento hoje aplicada (`radial-gradient` + `box-shadow: inset ...`) para remoção cirúrgica.

### STEP-02 — RED

```python
# tests/test_paper_color_taxonomy.py

def test_boletim_has_no_aging_texture():
    """Falha se o CSS computado da superfície do boletim contiver
    radial-gradient ou box-shadow inset."""
    ...

def test_boletim_uses_taxonomy_color():
    """Falha se o background do boletim não for exatamente --paper-boletim (#e4f2e4)."""
    ...
```

### STEP-03 — GREEN

Em `document_system.css`:

```css
:root {
  --paper-boletim: #e4f2e4;    /* verde — documentos policiais oficiais */
  --paper-depoimento: #fdf7d8; /* amarelo — depoimentos/transcrições */
  --paper-laudo: #eef0f6;      /* azulado — reservado para laudo pericial (P3) */
}
```

Em `04_boletim.html`:
- Remover a regra de `radial-gradient` (textura de envelhecimento) e o `box-shadow: inset ...`.
- Trocar o background da superfície do papel para `var(--paper-boletim)`, chapado.
- Se depoimento já existir como template, aplicar `var(--paper-depoimento)` do mesmo jeito.

O que **permanece**: linhas de formulário, campos, carimbo, rodapé de LGPD em corpo 6 — esses são os elementos que de fato comunicam burocracia, e não devem ser tocados nesta issue.

### STEP-04 — Verificação visual

Gerar screenshot antes/depois do boletim e confirmar visualmente que o documento parece "formulário oficial limpo", não "prop envelhecido".

### STEP-05 — Docs

`templates/README.md`, seção "Paleta Papel-Cor":

```markdown
## Paleta Papel-Cor

A cor de fundo de documentos de Camada 2 (papel) codifica o tipo de documento,
não é decoração:
- `--paper-boletim` (#e4f2e4, verde) — boletins e formulários policiais oficiais.
- `--paper-depoimento` (#fdf7d8, amarelo) — depoimentos e transcrições.
- `--paper-laudo` (#eef0f6, azulado) — reservado para laudo pericial (ver framework/09, P3).

Sempre chapado, nunca gradiente. Envelhecimento artificial (radial-gradient
"amarelado", sombra inset) é proibido — documento recente é limpo; o que
comunica burocracia é o formulário, não a textura do papel.
```

## Fora de escopo

- Criar o template completo do laudo pericial (P3, issue própria).
- Família manuscrita distinta por escrivão (issue de arquétipos/manuscritas, P2, fora deste lote).

## Riscos / atenção do revisor

- Confirmar que nenhum outro template compartilha a mesma regra CSS de envelhecimento antes de remover — se for uma classe global reusada, o refactor precisa ser mais cuidadoso do que uma remoção pontual em `04_boletim.html`.

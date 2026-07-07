# SPEC — ISSUE-40.5: Isolar `--accent` da marca Indiciário na Camada 0

## Contexto

Do diagnóstico, decisão de produto #5 (seção 0):

> O `--accent: #8b1a1a` do `base.html` hoje vaza para dentro de documentos diegéticos. Proposta: a marca Indiciário só existe em envelope, protocolo, dicas e gabarito; documentos de evidência nunca herdam cor da marca. [...] Isso inverte a herança atual de `base.html`.

Marcelo confirmou essa decisão. Esta issue é o refactor de CSS que a implementa.

## Escopo

Apenas a variável `--accent` e qualquer cor derivada dela (ex.: tints/shades calculados a partir dela em SCSS/CSS, se existirem). **Não inclui** ainda a atribuição de cor própria por instituição fictícia — isso é a 40.6, que consome o espaço que esta issue libera.

## Passo a passo técnico

### STEP-01 — Levantamento

```bash
grep -rn "\-\-accent" templates/ generator/
```

Listar todo uso — direto (`var(--accent)`) e indireto (propriedades que dependem de `--accent` sem chamar explicitamente, se o CSS usar alguma técnica de composição de cor). Classificar cada uso: pertence à Camada 0 (manter) ou vazou para Camada 1/2 (remover/substituir).

### STEP-02 — RED

```python
# tests/test_brand_isolation.py

NON_LAYER0_TEMPLATES = [
    # todos os templates de Camada 1 e 2, conforme classificação da 40.3
]

@pytest.mark.parametrize("template", NON_LAYER0_TEMPLATES)
def test_diegetic_template_does_not_inherit_brand_accent(template):
    """
    Falha se qualquer elemento visível do template tiver
    --accent (#8b1a1a) ou uma cor derivada dela no computed style.
    """
    ...
```

### STEP-03 — GREEN

Em `base.html` / `document_system.css`:

```css
/* Antes: --accent definido em :root, herdado por tudo */
/* Depois: escopado à Camada 0 */
.camada-0 {
  --accent: #8b1a1a;
}
```

Para cada template de Camada 1/2 que hoje usa `var(--accent)` (levantado no STEP-01), decidir caso a caso:
- Se o uso era puramente decorativo e não tinha função narrativa → substituir por uma cor neutra própria do documento (ex.: preto/cinza padrão de texto/borda).
- Se o uso na prática *deveria* ser uma cor de instituição fictícia (ex.: uma cor de destaque no orçamento que hoje pega emprestado o vermelho da marca por falta de alternativa) → deixar um `TODO(40.6)` explícito no CSS, porque a 40.6 vai introduzir a variável de microidentidade que substitui esse uso.

### STEP-04 — Verificação

Rodar `test_brand_isolation.py` contra todos os templates de Camada 1/2. Revisar visualmente qualquer template que dependia de `--accent` para não sair sem cor nenhuma (regressão de "documento sem graça" não é o objetivo — o objetivo é não usar a cor *da marca*, a instituição ainda pode ter cor própria via 40.6).

### STEP-05 — Docs

`templates/README.md`, seção "Isolamento de Marca":

```markdown
## Isolamento de Marca

A cor de marca do Indiciário (`--accent`, vermelho institucional) só existe
dentro da Camada 0 (envelope, protocolo, dicas, gabarito). Nenhum documento
diegético herda essa variável. Identidade visual dentro do caso (cor de uma
empresa fictícia, de uma instituição do caso) é function da microidentidade
de cada entidade (ver framework/09_SISTEMA_VISUAL.md), nunca da marca do produto.
```

## Fora de escopo

- Definir a variável de microidentidade que substitui os usos legítimos de cor institucional → 40.6.

## Riscos / atenção do revisor

- Esta issue pode deixar temporariamente alguns templates "sem cor de destaque" entre a 40.5 e a 40.6 (o `TODO(40.6)` é esperado, não é bug) — comunicar isso no PR para não gerar confusão em playtest intermediário.

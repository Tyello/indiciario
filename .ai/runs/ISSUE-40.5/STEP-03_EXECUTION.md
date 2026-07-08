# ISSUE-40.5 / STEP-03 — Execution Report (GREEN)

Type: green
Owner: executor

## O que foi feito

Editado `templates/base.html`:

1. Removida `--accent: #8b1a1a;` do bloco `:root` global (antiga linha 24).
2. Criado bloco `.camada-0 { --accent: #8b1a1a; }` logo após o `:root`, com
   comentário explicando o isolamento (ISSUE-40.5).
3. Adicionada classe `camada-0` ao `<body>` do template
   (`<body class="camada-0">`), já que `base.html` é o único consumidor de
   `--accent` hoje (`.doc-code { color: var(--accent); }`) — mantém o
   comportamento visual de `base.html` intacto, só muda o escopo da
   variável.

Nenhum outro template ou `document_system.css` tocado — STEP-01 confirmou
que nenhum dos 16 templates de Camada 1/2 referencia `--accent` hoje, então
não havia fallback a corrigir. `08_orcamento.html` (`.accent-bar` /
`{{COR_PRIMARIA}}`) não foi tocado — confirmado no STEP-01 como mecanismo
per-instituição, fora de escopo (é o que a 40.6 formaliza).

## Diff (resumo)

```css
:root {
  --paper: #f7f1e6;
  --ink: #161616;
  --muted: #666666;
  --line: #c8bda8;
  /* --accent removida daqui */
}

/* Marca Indiciário (ISSUE-40.5): --accent só existe dentro do escopo
   .camada-0 (envelope, protocolo, dicas, gabarito). Documentos
   diegéticos (Camada 1/2) não herdam esta variável -- não a declare
   em :root global. */
.camada-0 {
  --accent: #8b1a1a;
}
```

```html
<body class="camada-0">
```

## Comandos executados

```
.venv/Scripts/python.exe -m pytest tests/test_brand_isolation.py -q
→ 17 passed in 3.44s

.venv/Scripts/python.exe -m pytest tests/test_layer_rules.py -q
→ 28 passed in 5.35s
```

Ambos os testes passam 100%. `test_accent_variable_scoped_to_camada_0`
(RED real no STEP-02) agora GREEN: `--accent` está dentro de `.camada-0`,
não mais em `:root`. `test_diegetic_template_does_not_inherit_brand_accent`
(GREEN por desenho no STEP-02) continua GREEN — nenhuma regressão nos 16
templates de Camada 1/2. `test_layer_rules.py` sem regressão de camada.

## Verificação dos critérios de aceite (parcial, formal no STEP-04)

1. `--accent` só aplicado dentro de `.camada-0` — sim (único ponto de
   declaração em `templates/base.html`).
2. Nenhum template de Camada 1/2 herda `--accent` por padrão — confirmado
   por `test_diegetic_template_does_not_inherit_brand_accent` (16/16
   passam).
3. Teste automatizado comprova item 2 para todos os templates existentes —
   `tests/test_brand_isolation.py`, parametrizado pelos 16
   `NON_LAYER0_TEMPLATES`.

Confirmação final da suíte completa (`pytest tests/ -q`) fica para o
STEP-04, conforme contrato da issue.

## Arquivos alterados

- `templates/base.html`

## Proibições respeitadas

- Não introduzida variável de microidentidade da 40.6.
- `templates/08_orcamento.html` e demais templates de Camada 1/2 não
  tocados.
- `--accent` não reintroduzida em `:root` global.

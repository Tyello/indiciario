# ISSUE-40.5 / STEP-05 — Execution Report (Docs)

Type: documentation
Owner: executor

## O que foi feito

Adicionada seção "Isolamento de Marca (ISSUE-40.5)" a `templates/README.md`,
entre "Paleta Papel-Cor (ISSUE-40.4)" e "Próximos templates recomendados",
seguindo o esqueleto de `.ai/issues/ISSUE-40.5_SPEC.md` (STEP-05), ajustado
ao mecanismo real confirmado no STEP-03:

- Regra: `--accent` (`#8b1a1a`) só existe na Camada 0 (envelope, protocolo,
  dicas, gabarito); documento diegético nunca herda a cor de marca;
  identidade dentro do caso é microidentidade por entidade
  (`framework/09_SISTEMA_VISUAL.md`), não marca do produto.
- Mecanismo real: `--accent` declarada em `templates/base.html` dentro de
  `.camada-0` (não em `:root`); `base.html` é órfão e único consumidor hoje
  (`.doc-code`), via `<body class="camada-0">`; nenhum dos 16 templates
  diegéticos referencia `var(--accent)`; `.accent-bar` de
  `08_orcamento.html` usa `{{COR_PRIMARIA}}` (Jinja per-instituição, sem
  relação com a CSS var `--accent`) — coincidência de nome documentada
  explicitamente para evitar confusão futura.
- Teste de regressão: `tests/test_brand_isolation.py`, os dois testes
  (`test_diegetic_template_does_not_inherit_brand_accent`,
  `test_accent_variable_scoped_to_camada_0`) e quando rodar.

## Impacto documental (`docs/INDICE_DOCUMENTACAO.md`)

Verificado: `docs/INDICE_DOCUMENTACAO.md` não tem entrada para
`templates/README.md` (`grep -n "templates/" docs/INDICE_DOCUMENTACAO.md`
sem resultado — arquivo não é rastreado nesse índice hoje). A única entrada
relacionada ao tema é `20_SISTEMA_VISUAL.md` (linha 83), que já cita
"camada e microidentidade (40.3/40.6)" como gatilho de atualização — 40.5 é
refactor de CSS/teste sem mudança de doutrina em `framework/20_...`, não
dispara esse gatilho. **Dispensado**: não há linha em
`docs/INDICE_DOCUMENTACAO.md` referente a `templates/README.md` para
atualizar, e nenhuma outra linha do índice é afetada por esta issue.
`docs/INDICE_DOCUMENTACAO.md` não foi editado.

## Arquivos alterados

- `templates/README.md`

## Comandos executados

Nenhum (STEP-05 não exige comando, conforme contrato da issue).

## Proibições respeitadas

- Nenhum código alterado (`templates/base.html`, CSS, `generator/`,
  `tests/` intocados).

## Critério de aceite da issue (confirmação final)

1. `--accent` só aplicado dentro do escopo de templates de Camada 0 —
   confirmado no STEP-03 (`.camada-0` em `base.html`).
2. Nenhum template de Camada 1/2 herda `--accent` por padrão — confirmado
   no STEP-01/02/04.
3. Teste automatizado comprova o item 2 para todos os templates
   existentes — `tests/test_brand_isolation.py` (17 testes, STEP-02/03/04).

Documentação de referência (`templates/README.md`) agora reflete o
mecanismo implementado.

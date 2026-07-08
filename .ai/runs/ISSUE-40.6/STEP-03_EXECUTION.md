# ISSUE-40.6 — STEP-03 EXECUTION (GREEN)

Type: green
Owner: executor

## Objetivo

Implementar o sistema de microidentidade institucional para fazer
`tests/test_institution_identity.py` (STEP-02, 4 testes) passar, sem
regressão em `tests/test_layer_rules.py`.

## Arquivos criados

- `templates/styles/institution_identity.css` — tokens `--inst-color`,
  `--inst-font-display`, `--inst-header-shape` (fallbacks neutros em
  `.institution`), regra `.institution .header` (background/font-family a
  partir dos tokens + **reset de borda/clip-path**, ver "Decisão de design"
  abaixo), `.institution .header.shape-diagonal` (clip-path),
  `.institution .header.shape-faixa-dupla` (borda dupla). `shape-reto` é o
  default do reset — sem regra própria.
- `assets/logos/glifo-01.svg` .. `glifo-15.svg` — 15 glifos SVG abstratos
  (círculo, losango, triângulo, hexágono, chevron, cruz, anel, barras,
  crescente, grade de pontos, pentágono, ziguezague, estrela de 4 pontas,
  trapézio, quadrados concêntricos), todos `fill="currentColor"` (herdam a
  cor de texto do header, hoje branco fixo — ver CSS), flat na pasta (sem
  subpastas), seguindo convenção de `assets/fonts/`. Nenhuma semelhança com
  marca/logo real — formas geométricas puras.
- `templates/manual.html` — novo. Header institucional (`.institution
  .header shape-{{INST_HEADER_SHAPE}}`) com `{{INST_REVISAO}} —
  {{INST_REVISAO_DATA}}`; corpo com seções (`{{#SECOES}}`, com fallback
  `{{^SECOES}}` para caso de blueprint sem lista); rodapé com bloco
  `.assinatura-responsavel` (classe contém "assinatura", ver Achado do
  STEP-02 sobre o seletor de teste) contendo `{{ASSINATURA_RESPONSAVEL_VISUAL}}`
  + `{{ASSINATURA_RESPONSAVEL_NOME}}`.
- `templates/cadastro.html` — novo. Header institucional igual ao padrão
  acima; tabela `{{#CADASTRADOS}}` (nome/cargo/identificador/situação);
  rodapé com contagem de registros.
- `.ai/runs/ISSUE-40.6/STEP-03_EXECUTION.md` (este relatório).

## Arquivos alterados

- `templates/06_log_acesso.html`:
  - Envolveu `.page` num novo wrapper `<div class="institution" style="--inst-color:{{INST_COLOR}}; --inst-font-display:'{{INST_FONT_DISPLAY}}';">`.
  - `.log-header` ganhou as classes adicionais `header shape-{{INST_HEADER_SHAPE}}`
    (manteve a classe `log-header` original para não quebrar o CSS de
    layout existente — ver "Decisão de design").
  - Badge do sistema ganhou slot opcional `{{#INST_LOGO_SVG}}...{{/INST_LOGO_SVG}}`.
  - Carimbo de exportação: `"EXPORTADO EM {{DATA_EXPORTACAO}} ÀS
    {{HORA_EXPORTACAO}}"` → `"EXPORTADOS EM {{DATA_EXPORTACAO}} ÀS
    {{HORA_COM_SEGUNDOS}}"` (plural + variável nova com segundos, conforme
    recomendação do STEP-02 e critério de aceite #5).
- `generator/renderer.py` — 4 ajustes mínimos, todos aditivos (nenhuma
  assinatura pública alterada):
  1. `INSTITUTION_IDENTITY_CSS_PATH = TEMPLATES_DIR / "styles" /
     "institution_identity.css"` (constante, ao lado de
     `DOCUMENT_SYSTEM_CSS_PATH`).
  2. `_institution_identity_css()` (nova função, espelha
     `_document_system_css()`) + hook em `_injetar_css_documental` (`css =
     _document_system_css() + _institution_identity_css()`) — via (a) do
     Achado 2 do STEP-01, path recomendado.
  3. `_preparar_dados_documentais`: se `ASSINATURA_RESPONSAVEL_NOME` está
     presente e `ASSINATURA_RESPONSAVEL` ainda não foi definido, promove o
     nome para a chave que `preparar_assinaturas_visuais`/`ASSINATURA_KEYS`
     já sabem consumir — sem isso o rodapé do manual não geraria SVG
     nenhum, porque os dados de teste do STEP-02 (já revisados/aprovados)
     usam `ASSINATURA_RESPONSAVEL_NOME`, não `ASSINATURA_RESPONSAVEL` (ver
     "Divergência STEP-01 vs. STEP-02" abaixo). Não sobrescreve um
     `ASSINATURA_RESPONSAVEL` explícito já presente nos dados.
  4. Registro de `manual.html`/`cadastro.html` em `DOCUMENT_PLAYER_TEMPLATES`,
     `TEMPLATE_DOCUMENT_CLASS` (`"manual"`, `"cadastro"`),
     `TEMPLATE_LAYER_PAPER`, e `DOCUMENT_TYPE_FAMILIES["cadastro"] =
     "admin"` (`"manual"` já existia mapeado para `"letter"`) — para que os
     dois templates novos participem do sistema de camadas/família visual
     (`_injetar_classes_body`) do mesmo jeito que os demais documentos
     institucionais, em vez de cair só no fallback `"documento"`/`"document"`.
- `.ai/issues/ISSUE-40.6.md` — campos de controle e histórico (ver rodapé).

## Divergência STEP-01 vs. STEP-02 (registrada, não é bug)

O STEP-01 recomendou popular `dados["ASSINATURA_RESPONSAVEL"]` diretamente
(uma das `ASSINATURA_KEYS`) para o manual herdar o SVG automaticamente sem
código novo. O STEP-02 (já aprovado) implementou os dados de teste com
`ASSINATURA_RESPONSAVEL_NOME` (não `ASSINATURA_RESPONSAVEL`) — provavelmente
porque semanticamente "nome do responsável" é mais claro que reusar
diretamente uma chave de assinatura. Como o arquivo de teste está fora do
escopo editável do STEP-03, resolvi a divergência no lado do renderer (item
3 acima: promoção `NOME → chave-pipeline` dentro de
`_preparar_dados_documentais`), preservando o mecanismo existente
(`preparar_assinaturas_visuais`) sem gerar SVG fora do pipeline padrão, como
o STEP-01 já recomendava evitar.

## Decisão de design — reset de borda/clip-path em `.institution .header`

`06_log_acesso.html` já tinha `.log-header { border-bottom: 1px solid
#b9b2a6; ...}` antes desta issue. Se `institution_identity.css` só
adicionasse regras para as formas diagonal/faixa-dupla sem resetar o estado
base, o log de acesso teria sempre 1px de borda inferior (herdada de
`.log-header`) mesmo quando a instituição é `shape-reto` ou `shape-diagonal`
— enquanto `manual.html`/`cadastro.html` (sem essa borda legada) ficariam
com 0px nas mesmas condições. Isso quebraria a comparação de identidade
`getComputedStyle` entre os 3 templates do teste
`test_documents_of_same_institution_share_identity` mesmo com cor/fonte
corretas. Resolvido declarando `.institution .header { border-top: 0;
border-bottom: 0; clip-path: none; ... }` como reset de base — essa regra
tem 2 classes de especificidade (`.institution .header`), maior que a 1
classe de `.log-header`, então vence independente da ordem de carregamento
no `<head>`; as regras `.shape-diagonal`/`.shape-faixa-dupla` (3 classes)
sobrepõem o reset quando aplicável.

## Verificação de escopo (proibições do contrato)

- Não criei os 4 arquétipos comerciais de orçamento nem escala/planilha
  (fora de escopo, P2/P3).
- Nenhum glifo se parece com marca/logo real — formas geométricas puras
  (círculo, losango, hexágono, cruz, etc.).
- Não toquei `base.html`, `facilitator_guide.html` nem outros templates de
  Camada 0/fora do escopo institucional.
- `generator/renderer.py` só recebeu os 4 ajustes aditivos listados acima
  (loader de CSS, promoção de assinatura, registro nos dicts de
  camada/família) — nenhuma assinatura pública mudou, nenhum template
  pré-existente fora dos institucionais foi afetado por essas mudanças
  (confirmado pela ausência de regressão em `test_layer_rules.py`).

## Comandos executados

```
./.venv/Scripts/python.exe -m pytest tests/test_institution_identity.py -q
→ 4 passed in 2.41s

./.venv/Scripts/python.exe -m pytest tests/test_layer_rules.py -q
→ 28 passed in 4.74s (sem regressão de camada)
```

## Não fiz

- Não editei `.ai/issues/ISSUE-40.6_SPEC.md`, `tests/test_institution_identity.py`
  nem `templates/08_orcamento.html`.
- Não adicionei entrada `"manual"`/`"cadastro"` em `TIPO_PARA_TEMPLATE`
  (linha ~791, mapeia `"manual"` → `05_carta.html` hoje) — os testes desta
  issue chamam os templates diretamente pelo nome de arquivo, não por essa
  tabela de roteamento por tipo. Fica registrado como limitação conhecida:
  se algum blueprint futuro gerar documento pelo tipo lógico `"manual"` via
  `renderizar_caso`, ainda cairá em `05_carta.html`, não em
  `templates/manual.html`, até uma issue própria decidir esse roteamento
  (fora do critério de aceite desta issue, que fala em "templates
  institucionais", não em geração ponta-a-ponta a partir de blueprint).

## Próximo passo

STEP-04 — verificação visual com os dois conjuntos de teste (`museu_teste`,
`empresa_teste`) + suíte completa `pytest tests/ -q`.

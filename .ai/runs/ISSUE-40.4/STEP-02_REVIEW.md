# ISSUE-40.4 — STEP-02 — RED — Review Report

## Veredito

APROVADO.

## Checklist do contrato (STEP-02)

1. Testes inspecionam CSS computado via Playwright, não grep de string?
   **Sim.** Testes 1-3 usam `_computed_style_da_page` → `page.set_content` +
   `getComputedStyle` real via `page.evaluate`. Teste 4 é exceção justificada
   (não há elemento consumindo `--paper-laudo` ainda, logo não há computed
   style possível) e isolado ao bloco `:root` via regex não-gulosa
   (`:root\s*\{(.*?)\}`), não grep livre no arquivo inteiro — evita
   falso-positivo com token comentado ou fora de `:root`. Confirmado por
   leitura direta de `tests/test_paper_color_taxonomy.py`.

2. Teste de depoimento força `TIPO_DOCUMENTAL_SLUG="depoimento"` no mesmo
   arquivo físico, não assume template separado inexistente?
   **Sim.** `_montar_html_com_tipo("04_boletim.html", "depoimento")` —
   mesmo `TEMPLATE_BOLETIM` usado no teste de boletim, só variando o dado
   injetado. Consistente com o achado do STEP-01 (mesmo arquivo físico,
   `doc-type-*` como diferenciador).

3. `_montar_html_com_tipo` replica fielmente o pipeline de
   `font_fidelity._montar_html`?
   **Sim**, comparado lado a lado com `generator/font_fidelity.py` linhas
   47-54: mesma sequência (`_preparar_dados_documentais` →
   `_injetar_css_documental` → `_injetar_classes_body` →
   `_injetar_cabecalho_rodape_documental` → `renderizar_html`), única
   diferença é passar `{"TIPO_DOCUMENTAL_SLUG": tipo_slug}` em vez de dict
   vazio — mudança mínima e correta para o objetivo do step.

## Verificação independente (não apenas confiança no report)

Rodei `py -m pytest tests/test_paper_color_taxonomy.py -q` localmente
(nota: `python` não resolve neste shell — usar `py` launcher). Resultado
bate exatamente com o reportado:

- `test_boletim_has_no_aging_texture` — PASSOU (GREEN, guarda de regressão,
  confirma que a 40.3 já removeu a textura de envelhecimento).
- `test_boletim_uses_taxonomy_color` — FALHOU. Obtido `rgb(248, 249, 251)`,
  esperado `rgb(228, 242, 228)`.
- `test_depoimento_uses_taxonomy_color` — FALHOU. Obtido
  `rgb(248, 249, 251)` (idêntico ao boletim), esperado
  `rgb(253, 247, 216)`.
- `test_paper_laudo_token_exists` — FALHOU. `--paper-laudo` ausente do
  bloco `:root`.

Total: 3 failed, 1 passed. Idêntico ao STEP-02_EXECUTION.md.

## Escopo dos arquivos alterados

`git status --porcelain` confirma escopo respeitado:
- `tests/test_paper_color_taxonomy.py` (novo, permitido)
- `.ai/issues/ISSUE-40.4.md` (campos de controle/histórico, permitido)
- `.ai/runs/ISSUE-40.4/` (reports, permitido)

Nenhuma alteração em `templates/04_boletim.html`,
`templates/styles/document_system.css` ou `generator/renderer.py` —
proibição do step respeitada.

## Observações

- Teste 1 nasce GREEN por desenho, não é RED forçado artificialmente —
  documentado com clareza no report e nos comentários do próprio arquivo
  de teste. Correto: forçar RED artificial aqui violaria o achado real do
  STEP-01 (textura já removida pela 40.3).
- Cores hex→rgb convertidas corretamente: `#e4f2e4` = `rgb(228,242,228)`,
  `#fdf7d8` = `rgb(253,247,216)` — conferido por cálculo direto do hex.
- Recomendação para STEP-03 (ordem de declaração das regras `.doc-type-*`
  depois de `.doc-family-admin .page` na cascata, para vencer por ordem de
  declaração em especificidade empatada) é tecnicamente correta e
  necessária — sem isso o GREEN do STEP-03 não é alcançável com a
  especificidade indicada na spec.

## Findings

Nenhum. Nada a corrigir. Step cumpre o contrato integralmente.

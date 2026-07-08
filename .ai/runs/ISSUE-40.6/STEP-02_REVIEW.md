# ISSUE-40.6 — STEP-02 REVIEW (RED)

Reviewer verdict: APROVADO

## Checklist do contrato (STEP-02)

- [x] `tests/test_institution_identity.py` criado com os 4 testes exigidos:
      `test_documents_of_same_institution_share_identity`,
      `test_documents_of_different_institutions_do_not_share_identity`,
      `test_manual_has_revision_and_signature`,
      `test_access_log_has_export_stamp_with_seconds`.
- [x] Usa os dois conjuntos de dados literais da spec (`museu_teste` #7a1f1f/
      Libre Baskerville/diagonal, `empresa_teste` #1f4a7a/DM Sans/reto).
- [x] Inspeção via DOM renderizado real (Playwright `page.set_content` +
      `page.evaluate`/`getComputedStyle`/`innerText`/`querySelector`), não
      grep de string em arquivo-fonte. Segue o padrão de
      `tests/test_layer_rules.py`.
- [x] `_montar_html_institucional` corretamente evita o helper hardcoded
      `font_fidelity._montar_html` (achado STEP-01) e replica o pipeline real
      de `generator/renderer.py` (`_preparar_dados_documentais` →
      `_injetar_css_documental` → `_injetar_classes_body` →
      `_injetar_cabecalho_rodape_documental` → `renderizar_html`). Verifiquei
      as 4 assinaturas e `TEMPLATES_DIR` em `generator/renderer.py:34,159,
      183,214,239,548` — batem com os imports do teste.
- [x] Testes de assinatura/revisão e carimbo de exportação inspecionam
      conteúdo renderizado (`document.body.innerText`, `querySelector` de
      `svg` de assinatura), não só existência de arquivo.
- [x] Nenhum arquivo de produção tocado: `git diff --name-only` mostra só
      `.ai/issues/ISSUE-40.6.md` modificado (campos de controle/histórico);
      `git diff --stat -- templates/ generator/ assets/` vazio.
- [x] Execution report documenta output real do pytest, por teste, com causa
      de falha.

## Verificação independente

Rodei `./.venv/Scripts/python.exe -m pytest tests/test_institution_identity.py -q`
localmente. Resultado: **4 failed**, idêntico ao reportado no execution
report — mesmas 4 falhas, mesmas causas:
- `test_documents_of_same_institution_share_identity` → `.institution
  .header` ausente em `06_log_acesso.html`.
- `test_documents_of_different_institutions_do_not_share_identity` →
  `FileNotFoundError` em `templates/manual.html`.
- `test_manual_has_revision_and_signature` → `FileNotFoundError` em
  `templates/manual.html`.
- `test_access_log_has_export_stamp_with_seconds` → `AssertionError`, texto
  renderizado real mostra `"EXPORTADO EM 06/08/2024 ÀS 17:04"` (singular,
  sem segundos) contra o regex `EXPORTADOS?...HH:MM:SS`.

Nenhum GREEN-por-desenho. RED genuíno confirmado de forma independente.

## Ponto investigado e descartado

O terminal exibe o caractere "À" do regex de carimbo de exportação como
"�" (mojibake aparente) tanto no código-fonte quanto na saída do pytest.
Inspecionei os bytes brutos de `tests/test_institution_identity.py`: a
sequência é `\xc3\x80` = UTF-8 válido para U+00C0 (À). É só a codepage do
console Windows falhando ao exibir o caractere — não é corrupção real do
arquivo nem risco de regex nunca casar após o GREEN do STEP-03. Não é
achado, registrado aqui só para descartar a hipótese.

## Observação para STEP-03 (não bloqueante)

O execution report já lista recomendações corretas e específicas (path do
CSS, criar `manual.html`/`cadastro.html`, trocar `.log-header` por
`.institution .header`, usar `HORA_COM_SEGUNDOS` em vez de
`HORA_EXPORTACAO`). Nada a acrescentar.

## Decisão

STEP-02 cumpre o contrato integralmente. Aprovado. Avança para STEP-03.

# STEP-04 — Verificação visual — Execution Report

**Issue:** ISSUE-40.4
**Step:** STEP-04
**Type:** validation
**Owner:** executor

## O que foi feito

1. Renderizei `templates/04_boletim.html` duas vezes, usando o mesmo mecanismo
   de `tests/test_paper_color_taxonomy.py` (`_montar_html_com_tipo`, que
   replica `generator.font_fidelity._montar_html` mas aceita override de
   `TIPO_DOCUMENTAL_SLUG`):
   - `TIPO_DOCUMENTAL_SLUG="boletim"`
   - `TIPO_DOCUMENTAL_SLUG="depoimento"`
   Script auxiliar temporário em `.ai/runs/ISSUE-40.4/_step04_screenshot.py`,
   criado só para este step e apagado ao final (não faz parte da suíte).
2. Capturei screenshot do elemento `.page` de cada render via Playwright
   (`page.query_selector(".page").screenshot(...)`), salvos em:
   - `.ai/runs/ISSUE-40.4/boletim_depois.png`
   - `.ai/runs/ISSUE-40.4/depoimento_depois.png`
3. Rodei a suíte completa: `pytest tests/ -q` (via `py -3 -m pytest tests/ -q`
   com `PYTHONPATH` apontando pra raiz do repo, mesmo padrão usado nos steps
   anteriores desta issue neste ambiente Windows).

## Confirmação visual

- **`boletim_depois.png`**: fundo do `.page` verde chapado (`#e4f2e4`), sem
  gradiente, sem sombra. Formulário intacto: cabeçalho azul com brasão e
  número do caso, faixa `TIPO_DOCUMENTO`, campos "Tipo de Ocorrência" / "Data"
  / "Localização" / "Hora da Ocorrência" com linhas pontilhadas, bloco
  "Descrição da Ocorrência", rodapé com "Relatado por" / "Conferência" /
  "Data e Hora" e linhas de assinatura.
- **`depoimento_depois.png`**: mesmo layout de formulário (mesmo arquivo
  físico `04_boletim.html`), fundo do `.page` amarelo chapado (`#fdf7d8`),
  sem gradiente, sem sombra. Cor visivelmente diferente do boletim — confirma
  que a diferenciação por `TIPO_DOCUMENTAL_SLUG`/`doc-type-*` funciona no
  mesmo template.
- Nenhum dos dois screenshots mostra textura radial/manchas de
  envelhecimento ou sombra inset — consistente com o achado do STEP-01/STEP-02
  de que a 40.3 já havia removido essa textura.
- Os campos aparecem como placeholders `{{CAMPO}}` não substituídos — esperado,
  porque o render foi feito sem dados de conteúdo reais (só
  `TIPO_DOCUMENTAL_SLUG` foi injetado, igual ao teste RED/GREEN do
  STEP-02/03). Isso não afeta o critério deste step, que é sobre cor de fundo
  e ausência de textura, não sobre conteúdo preenchido.

## Resultado da suíte completa

`pytest tests/ -q` → **1420 passed, 3 skipped, 5 failed** em 198.92s.

As 5 falhas são todas em `os.symlink` no Windows
(`OSError: [WinError 1314] O cliente não tem o privilégio necessário`),
pré-existentes e não relacionadas a esta issue — mesmo padrão documentado
como precedente em 40.3/STEP-04:

- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Todas exigem `os.symlink`/`Path.symlink_to`, que requer privilégio elevado
(SeCreateSymbolicLinkPrivilege) não concedido nesta conta Windows — nada a
ver com `04_boletim.html`, `document_system.css` ou a taxonomia de cor.
`tests/test_paper_color_taxonomy.py` (4/4) e `tests/test_layer_rules.py`
(28/28) continuam passando dentro dessa rodada completa, sem regressão nova
atribuível a esta issue.

## Comandos executados

```
py -3 .ai/runs/ISSUE-40.4/_step04_screenshot.py     # gera os 2 screenshots
py -3 -m pytest tests/ -q                            # 1420 passed, 3 skipped, 5 failed (symlink, pré-existente)
```

## Arquivos alterados/criados neste step

- `.ai/runs/ISSUE-40.4/boletim_depois.png` (novo)
- `.ai/runs/ISSUE-40.4/depoimento_depois.png` (novo)
- `.ai/runs/ISSUE-40.4/_step04_screenshot.py` (criado e apagado no mesmo step, script auxiliar temporário — não persiste)
- `.ai/runs/ISSUE-40.4/STEP-04_EXECUTION.md` (este report)

Nenhum arquivo de código/template/CSS tocado neste step (proibido pelo
contrato: "Alterar comportamento implementado no STEP-03").

## Done quando (contrato do step)

- [x] Screenshots gerados e descritos no report.
- [x] `pytest tests/ -q` sem regressão nova atribuível a esta issue (falhas
      de symlink pré-existentes documentadas como não relacionadas, seguindo
      o precedente da 40.3/STEP-04).

## Revisão pendente

Type `validation` — revisor obrigatório. Pontos para segunda opinião:
- Confirmar que os 2 screenshots batem com o critério de aceite (cores
  chapadas `#e4f2e4`/`#fdf7d8`, sem gradiente/sombra).
- Confirmar que as 5 falhas de symlink são de fato pré-existentes e não
  relacionadas (rodar `git stash` + suíte, ou inspecionar se os testes falham
  também na branch antes desta issue, se necessário para segunda opinião).

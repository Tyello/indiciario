# SPEC — ISSUE-40.1: Vendorizar fontes com `@font-face` local

## Contexto

`generator/renderer.py` usa Playwright para renderizar HTML → imagem/PDF. `templates/styles/document_system.css` (v1) declara a política "sem fontes externas ou imagens remotas", mas os templates abaixo dependem de fontes que só existem se instaladas no sistema operacional local — o que não é garantido em CI, em outra máquina, ou na máquina de outro colaborador:

| Template | Fonte(s) usada(s) |
|---|---|
| 01 (e-mail) | `'DM Sans'` |
| 02 (WhatsApp) | fonte de UI de sistema — confirmar se também usa DM Sans |
| 04 (boletim) | `'Caveat'` (preenchimento manuscrito) |
| 07 | `'Libre Baskerville'` |
| 08 (orçamento) | `'DM Sans'`, `'JetBrains Mono'`, `'Source Serif 4'` |

Isso é a mesma classe de falha silenciosa das ISSUE-30.6/30.7 (critério passa sem ter sido de fato avaliado), só que no domínio visual: hoje nada detecta quando um template "degrada" para fallback.

## Escopo desta issue

Apenas a vendorização e o carregamento local. **Não** inclui o gate de detecção de fallback (isso é a 40.2, que depende desta).

## Passo a passo técnico

### STEP-01 — Inventário

```bash
grep -rn "font-family" templates/ | grep -v "sans-serif\|serif\|monospace\|system-ui"
```
Confirmar a lista completa de famílias custom contra a tabela acima antes de prosseguir — o diagnóstico foi lido em 05/07/2026 e o repo pode ter mudado desde então.

### STEP-02 — RED

Criar (ou estender) `tests/test_font_vendoring.py`:

```python
import pytest
from generator.renderer import render_template_to_image  # ajustar import ao nome real

CUSTOM_FONTS = {
    "01_email_pessoal.html": ["DM Sans"],
    "04_boletim.html": ["Caveat"],
    "08_orcamento.html": ["DM Sans", "JetBrains Mono", "Source Serif 4"],
    # completar com o inventário do STEP-01
}

@pytest.mark.parametrize("template,fonts", CUSTOM_FONTS.items())
def test_template_does_not_fallback_to_system_font(template, fonts, tmp_path):
    """
    Renderiza o template e inspeciona, via Playwright, o font-family
    computado dos elementos que deveriam usar cada fonte custom.
    Deve FALHAR hoje (v1) porque não há @font-face local.
    """
    result = render_template_to_image(template, output_dir=tmp_path, headless=True)
    computed_fonts = result.get_computed_font_families()  # método a criar no renderer/teste
    for f in fonts:
        assert f in computed_fonts, (
            f"{template}: fonte '{f}' não foi aplicada — "
            f"provável fallback silencioso para fonte de sistema"
        )
```

Ajustar nomes de função/import ao código real do `generator/renderer.py` — o trecho acima é o esqueleto do teste, não código pronto para colar sem revisão.

Confirmar que este teste **falha** no estado atual antes de prosseguir (RED real, não hipotético).

### STEP-03 — GREEN

1. Para cada fonte da tabela, obter o arquivo `.woff2` de fonte com licença permissiva (Google Fonts serve todas as listadas sob Open Font License — confirmar item a item antes de comitar o binário).
2. Salvar em `assets/fonts/<nome-arquivo>.woff2`.
3. Adicionar ao topo de `templates/styles/document_system.css`:

```css
@font-face {
  font-family: 'DM Sans';
  src: url('../../assets/fonts/dm-sans-regular.woff2') format('woff2');
  font-weight: 400;
  font-display: block; /* evita FOUC alterar o screenshot */
}
/* repetir para cada peso/família usado, incluindo Caveat, JetBrains Mono, Source Serif 4, Libre Baskerville */
```

   Usar `font-display: block` (não `swap`) porque o renderer tira screenshot — queremos que o Playwright espere a fonte carregar, não capture o fallback temporário.

4. No `generator/renderer.py`, garantir que o Playwright aguarda o carregamento de fontes antes do screenshot (`page.evaluate("document.fonts.ready")` antes de `page.screenshot(...)`, se ainda não existir essa espera).
5. Ajustar caminhos relativos de `url()` no CSS para o layout real de `assets/` vs. `templates/styles/` — validar caminho absoluto/relativo conforme como o renderer serve os arquivos (file:// vs. servidor local).

### STEP-04 — Verificação em ambiente limpo

Rodar a suíte de testes em um container/venv sem as fontes instaladas no SO (ou renomear temporariamente as fontes de sistema, se for a única forma disponível de simular isso) para garantir que o teste GREEN não está passando "por acaso" porque a máquina de dev tem as fontes instaladas globalmente.

### STEP-05 — Docs

Em `templates/README.md`, localizar a frase atual sobre "sem fontes externas ou imagens remotas" e substituir por algo como:

> **Fontes:** todo template usa apenas fontes vendorizadas em `assets/fonts/` via `@font-face` local — nunca fontes de sistema nem carregadas de rede em runtime. Para adicionar uma fonte nova a um template, baixe o `.woff2`, adicione em `assets/fonts/`, declare o `@font-face` em `document_system.css` e adicione o template ao inventário de `tests/test_font_vendoring.py`.

## Fora de escopo (não fazer aqui)

- Gate automatizado de detecção de fallback no `canonical_quality_gate.py` → ISSUE-40.2.
- Escolha de famílias manuscritas múltiplas (hoje `Caveat` é usado uniformemente em 6 templates) → tratado na issue de arquétipos comerciais (P2, fora deste lote).

## Riscos / atenção do revisor

- Confirmar licenciamento de cada fonte antes de comitar o binário no repo.
- `font-display: block` pode aumentar o tempo de renderização em lote (geração de muitos documentos) — medir impacto se o pipeline gerar centenas de páginas por caso.

# SPEC — ISSUE-40.6: Microidentidades institucionais

## Contexto

Do diagnóstico, seção 3.6:

> Criar `styles/institution_identity.css` com o conceito de microidentidade: cada instituição do caso define `--inst-color`, `--inst-font-display`, `--inst-header-shape` (reto | diagonal | faixa dupla) e um glifo de logo [...]. Todos os documentos da mesma instituição herdam a microidentidade → coesão intra-fonte, variação inter-fontes, que é a assinatura visual do benchmark.

E da seção 1.2, sobre o benchmark:

> Documentos institucionais do museu [...] Uma família visual coesa: mesmo vermelho, mesmo busto-logotipo, mesmo header com recorte diagonal. Isso é deliberado: o jogador aprende a reconhecer "isto veio do museu" em meio segundo.

## Escopo

Sistema de tokens + biblioteca de glifos + aplicação aos templates institucionais que já existem hoje (manual, log de acesso, cadastro, listas). Novos tipos de documento institucional (escala/planilha) ficam para P3.

## Passo a passo técnico

### STEP-01 — Pré-requisitos

Confirmar que `.layer-paper`/`.layer-screen` (40.3) e o isolamento de `--accent` (40.5) já estão mesclados — esta issue assume que o espaço de cor está livre de herança de marca.

### STEP-02 — RED

```python
# tests/test_institution_identity.py

INSTITUTION_TEST_DATA = {
    "museu_teste": {
        "inst_color": "#7a1f1f",
        "inst_font_display": "Libre Baskerville",
        "inst_header_shape": "diagonal",
        "templates": ["manual.html", "06_log_acesso.html", "cadastro.html"],
    },
    "empresa_teste": {
        "inst_color": "#1f4a7a",
        "inst_font_display": "DM Sans",
        "inst_header_shape": "reto",
        "templates": ["manual.html", "06_log_acesso.html", "cadastro.html"],
    },
}

def test_documents_of_same_institution_share_identity():
    """Renderiza os 3 templates de museu_teste e confirma que todos usam
    a mesma cor, fonte de destaque e forma de header."""
    ...

def test_documents_of_different_institutions_do_not_share_identity():
    """Confirma que museu_teste e empresa_teste produzem identidades visuais
    distintas nos mesmos templates."""
    ...

def test_manual_has_revision_and_signature():
    """Falha se o manual não tiver 'Revisão N — data' no header e
    assinatura do responsável no rodapé."""
    ...

def test_access_log_has_export_stamp_with_seconds():
    """Falha se o log de acesso não tiver carimbo de exportação com
    timestamp incluindo segundos (ex.: 'EXPORTADOS EM DD/MM/AAAA ÀS HH:MM:SS')."""
    ...
```

### STEP-03 — GREEN

**`styles/institution_identity.css`:**

```css
/* Tokens de microidentidade — definidos por instituição no blueprint,
   injetados como custom properties no wrapper do documento */
.institution {
  --inst-color: var(--inst-color, #333);          /* fallback neutro se blueprint não definir */
  --inst-font-display: var(--inst-font-display, Georgia, serif);
  --inst-header-shape: var(--inst-header-shape, reto);
}

.institution .header {
  background: var(--inst-color);
  font-family: var(--inst-font-display);
}

.institution .header.shape-diagonal {
  clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
}
.institution .header.shape-faixa-dupla {
  border-top: 4px solid var(--inst-color);
  border-bottom: 2px solid var(--inst-color);
}
/* shape-reto: sem clip-path, sem borda dupla — default */
```

**Biblioteca de glifos:** criar 10-15 SVGs simples e abstratos (formas geométricas, não ilustrações complexas) em `assets/logos/glifo-01.svg` ... `glifo-15.svg`. Cada instituição do blueprint referencia um glifo por índice ou nome — não gerar glifo novo por caso, reusar da biblioteca (mantém consistência e evita custo de design ad-hoc por caso).

**Aplicação aos templates existentes:**
- Manual: adicionar ao header `{{INST_REVISAO}} — {{INST_REVISAO_DATA}}` (ex.: "Revisão 2, 06/08/2024") e, no rodapé, bloco de assinatura do responsável (reusar `signature_renderer.py` já existente).
- Log de acesso (`06_log_acesso.html`): adicionar carimbo `EXPORTADOS EM {{DATA}} ÀS {{HORA_COM_SEGUNDOS}}`; se o log for longo, considerar múltiplas colunas lado a lado em vez de uma tabela quilométrica (ajuste de layout, não de identidade — fazer apenas se o teste de verificação visual mostrar tabela excessivamente longa nos dados de teste).
- Cadastro/listas: aplicar `.institution` no wrapper para herdar cor/fonte/forma de header.

Cada template envolvido recebe a classe `.institution` no elemento raiz e os custom properties são injetados pelo renderer a partir dos dados da instituição no blueprint (mecanismo de injeção a confirmar com o padrão real de `generator/renderer.py` — provavelmente já existe um mecanismo de variável Mustache-like usado nos outros templates).

### STEP-04 — Verificação

Rodar os 4 testes do STEP-02 com os dois conjuntos de dados de teste (`museu_teste`, `empresa_teste`). Verificar visualmente que a diferenciação é perceptível (não só tecnicamente presente no CSS) — screenshot lado a lado.

### STEP-05 — Docs

`templates/README.md`, seção "Microidentidades Institucionais":

```markdown
## Microidentidades Institucionais

Cada instituição fictícia de um caso define, no blueprint:
- `inst_color` — cor de destaque única da instituição.
- `inst_font_display` — fonte de título/header (deve estar vendorizada, ver
  política de fontes).
- `inst_header_shape` — reto | diagonal | faixa-dupla.
- `inst_logo` — referência a um glifo da biblioteca em `assets/logos/`.

Todo documento institucional (manual, log de acesso, cadastro, listas) herda
esses tokens via classe `.institution`. Documentos da mesma instituição são
visualmente coesos entre si; instituições diferentes não compartilham identidade.
Isso é o que permite ao jogador reconhecer a origem de um documento em segundos,
sem precisar ler o cabeçalho.
```

Fechar `framework/09_SISTEMA_VISUAL.md` com a seção "Microidentidades Institucionais", consolidando o documento (Gate de Fonte + Sistema de Camadas + Microidentidades) como a doutrina visual completa deste lote.

## Fora de escopo

- Arquétipos comerciais de orçamento (4 templates) — usam o mesmo princípio de microidentidade, mas com esqueletos de documento distintos, não só troca de token. P2, issue própria.
- Escala/planilha operacional (novo tipo de documento) — P3.

## Riscos / atenção do revisor

- Biblioteca de glifos: evitar qualquer semelhança com marcas/logos reais existentes — devem ser formas abstratas genéricas, não paródias reconhecíveis de empresas reais.
- Se `generator/renderer.py` não tiver hoje um mecanismo de variável por-instituição (só por-documento), pode ser necessário um pequeno ajuste de infraestrutura de injeção de dados — sinalizar no PR se for o caso.

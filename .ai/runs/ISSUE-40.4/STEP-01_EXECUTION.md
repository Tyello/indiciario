# STEP-01 — Execution Report — ISSUE-40.4

Type: reading
Owner: executor

## Achado 1 — boletim/depoimento é o MESMO arquivo físico

Confirmado. `generator/renderer.py`:

- Linha 62: `TEMPLATE_DOCUMENT_CLASS["04_boletim.html"] = "depoimento"` (fallback quando `TIPO_DOCUMENTAL_SLUG` não vem em `dados`).
- Linhas 773-774 (dict `TIPO_PARA_TEMPLATE`, começa ~766):
  ```
  773:    "boletim": "04_boletim.html",
  774:    "depoimento": "04_boletim.html",
  ```
  Ambos os slugs `"boletim"` e `"depoimento"` apontam para o mesmo arquivo `04_boletim.html`. Não existe template `templates/*depoimento*` separado — confirmado via Glob (`templates/*depoimento*` → 0 resultados).
- `_classe_tipo_documental` (linha 166) resolve `tipo = dados.get("TIPO_DOCUMENTAL_SLUG") or TEMPLATE_DOCUMENT_CLASS.get(template_nome)`, sanitiza via `re.sub(r"[^a-z0-9_-]+", ...)`.
- `_injetar_classes_body` (linha 174-224) monta `classes = ["doc-system", f"doc-type-{tipo}", f"doc-family-{familia}"]`, mais `"doc-player"`, `"facilitator-doc"`, `"layer-paper"` condicionalmente, e injeta essas classes no `<body>` via regex.

Confirmação: renderizar `04_boletim.html` com `TIPO_DOCUMENTAL_SLUG="boletim"` produz `<body class="doc-system doc-type-boletim doc-family-admin layer-paper ...">`; com `"depoimento"` produz `doc-type-depoimento` no lugar de `doc-type-boletim`. Mesmo arquivo, classe de runtime diferente.

## Achado 2 — família visual compartilhada (`admin`)

Confirmado. `generator/renderer.py`, dict `DOCUMENT_TYPE_FAMILIES` (começa linha 102):
```
110:    "boletim": "admin",
111:    "depoimento": "admin",
```
Os dois tipos caem na família `"admin"`. Logo `.doc-family-admin .page { ... }` em `document_system.css` (linha 232) não diferencia boletim de depoimento — a regra de cor por taxonomia **precisa** ser via `.doc-type-boletim .page` / `.doc-type-depoimento .page`, não via `.doc-family-admin`. Confirma recomendação da issue.

## Achado 3 — textura de envelhecimento já removida (pós-40.3)

Confirmado, com reforço adicional (dois mecanismos independentes garantem isso hoje):

1. **Fonte do template**: `grep -n "radial-gradient\|box-shadow\|inset" templates/04_boletim.html` → nenhum resultado. `.page` em `04_boletim.html` (linha 20 da seção `<style>`) hoje é:
   ```css
   .page { background: #fefce8; max-width: 760px; margin: 0 auto; border: 1px solid #d4c89a; position: relative; overflow: hidden; }
   ```
   Chapado, sem gradiente nem sombra inset.

2. **Reset global `.layer-paper`** (`document_system.css`, linhas ~225-229, ISSUE-40.3): `04_boletim.html` está listado em `TEMPLATE_LAYER_PAPER` (linha 88 de `renderer.py`), então `_injetar_classes_body` sempre adiciona `layer-paper` ao `<body>`. A regra `.layer-paper, .layer-paper *` em `document_system.css` força `box-shadow: none !important; border-radius: 0 !important; background-image: none !important;` — um cinto-e-suspensório que neutralizaria qualquer gradiente/sombra reintroduzida, mesmo que o CSS local do template regredisse.

**Conclusão**: critério de aceite #1 desta issue (`04_boletim.html` não tem `radial-gradient` nem `box-shadow` inset) **já está satisfeito hoje**, antes de qualquer edição desta issue. Recalibração para STEP-02: o teste `test_boletim_has_no_aging_texture` deve nascer GREEN (guarda de regressão), não RED artificial. O trabalho real da issue é a taxonomia de cor (itens 2-3 do objetivo).

## Achado 4 — tokens de cor existentes, sem colisão

`document_system.css`, bloco `:root` (linhas ~80-82):
```css
--ind-paper: #fffdf8;
--ind-paper-warm: #f7f2e8;
--ind-paper-cool: #f8f9fb;
```
Nenhum token `--paper-boletim`, `--paper-depoimento` ou `--paper-laudo` existe hoje (grep confirma zero ocorrências). Regras de família relevantes:
```css
204: .doc-family-chat .page { background: var(--ind-paper-cool); }
232: .doc-family-admin .page { background: var(--ind-paper-cool); border: var(--ind-line-strong); }
233: .doc-family-commercial .page { background: var(--ind-paper); border: var(--ind-line); }
```
`.doc-family-admin .page` (linha 232) define `background` E `border`. Os novos tokens/regras não colidem em nome, mas colidem em **especificidade** com essa linha: `.doc-family-admin .page` e `.doc-type-boletim .page` têm especificidade igual (0,2,0). Recomendação para STEP-03: declarar `.doc-type-boletim .page` / `.doc-type-depoimento .page` **depois** de `.doc-family-admin .page` no arquivo (ordem de declaração decide o empate), sobrescrevendo apenas `background` — não redeclarar `border`, preservando `border: var(--ind-line-strong)` herdado da família admin.

## Mecanismo recomendado para STEP-03

Usar `.doc-type-boletim .page` e `.doc-type-depoimento .page` (não `.doc-family-admin`), posicionadas após a regra `.doc-family-admin .page` em `document_system.css`, cada uma sobrescrevendo só `background: var(--paper-boletim)` / `background: var(--paper-depoimento)`. Adicionar `--paper-laudo: #eef0f6` em `:root` sem consumidor (satisfaz critério de aceite #3, reservado para P3).

Em `04_boletim.html`: `.page` hoje tem `background: #fefce8` hardcoded na linha 20 — isso tem maior especificidade (estilo local do documento, dentro do próprio `<style>` do template) e venceria a cascata contra as novas regras em `document_system.css` salvo reordenação/`!important`. Recomendação: remover esse `background: #fefce8` hardcoded de `04_boletim.html`, deixando o background vir só das novas regras `doc-type-*` injetadas via `document_system.css`.

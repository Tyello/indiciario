# STEP-05 EXECUTION — ISSUE-40.1

Owner: executor
Type: documentation (low-risk)

## Objetivo

Atualizar `templates/README.md` conforme doc-impact declarado no topo da issue:
substituir a frase sobre "sem fontes externas ou imagens remotas" pela política
nova (fontes vendorizadas localmente via `@font-face`, nunca de sistema/rede em
runtime), incluindo como adicionar fonte nova.

## Desvio confirmado da SPEC

A frase exata "sem fontes externas ou imagens remotas" citada na SPEC
(`ISSUE-40.1_SPEC.md`, seção STEP-05) e no doc-impact da issue **não existe
literalmente** em `templates/README.md`. O texto real mais próximo, na seção
`## Diretriz`, é:

> Evite scripts remotos, `&nbsp;`, QR decorativo e dependências externas obrigatórias.

Confirmado via `grep -rn "fontes externas" .` (repo-wide): a frase aparece só
em `.ai/issues/ISSUE-40.1.md` e `.ai/issues/ISSUE-40.1_SPEC.md` (a própria
issue/spec citando o problema), não em `templates/README.md`. Tratado como
citação aproximada da SPEC, não como string literal a localizar — a ação
correta é adicionar a política de fontes nova ao lado da diretriz existente
sobre dependências externas, sem inventar uma frase antiga que nunca existiu.

## Mudança aplicada

Adicionada nova linha de diretriz logo após a linha sobre scripts
remotos/dependências externas, em `templates/README.md`:

> **Fontes:** todo template usa apenas fontes vendorizadas em `assets/fonts/`
> via `@font-face` local (`font-display: block`) — nunca fonte de sistema nem
> carregada de rede em runtime. Exceções documentadas: `05_carta.html` usa
> Georgia (fonte web-safe, decisão humana registrada em
> `.ai/issues/ISSUE-40.1.md`), não precisa vendorização; `Inter` (usado em
> `03_...`) fica fora de escopo por decisão de design (mimetismo intencional
> de UI nativa do SO). O renderer (`generator/renderer.py`) aguarda
> `document.fonts.ready` antes do screenshot/PDF. Para adicionar uma fonte
> nova a um template: baixe o `.woff2` com licença permissiva, coloque em
> `assets/fonts/`, declare o `@font-face` em
> `templates/styles/document_system.css` e adicione o template ao inventário
> de `CUSTOM_FONTS` em `tests/test_font_vendoring.py`.

Ajustes frente à redação sugerida na SPEC (por refletir estado real, não
copiado cegamente):
- Removida menção a warm-up (mecanismo `_injetar_fontface_warmup` foi
  removido no STEP-03_FIX-01, não existe mais no código).
- Explicitada a exceção `05_carta.html`/Georgia, decidida por humano após o
  STEP-03 (não estava na SPEC original, que ainda listava Libre Baskerville
  para o template 05).
- Explicitada a exceção `Inter` (fora de escopo por decisão de design,
  registrada na nota de decisão pós-STEP-01 da issue).
- Trocado "adicione o template ao inventário de `tests/test_font_vendoring.py`"
  por "adicione o template ao inventário de `CUSTOM_FONTS` em
  `tests/test_font_vendoring.py`" — nome real da estrutura de dados no teste
  (confirmado nas notas do STEP-02/STEP-03_FIX-01: `CUSTOM_FONTS`).

## Arquivo alterado

- `templates/README.md`

## Comandos executados

Nenhum (edição de texto, conforme contrato do step — "Comandos permitidos:
Nenhum").

## Verificação

- Frase antiga (aproximada) sobre dependências externas mantida (não é sobre
  fontes, é sobre scripts/QR — continua válida e não conflita com a nova
  linha de fontes).
- Nova linha distingue explicitamente runtime remoto (proibido) de fontes
  vendorizadas localmente (obrigatório), conforme objetivo do STEP-05.
- Nenhum outro arquivo tocado.

## Status

Done. Sem problema encontrado — low-risk, elegível para auto-approve
conforme protocolo do step (`Revisão: (low-risk, auto-approve se execution
report não indicar problema)`).

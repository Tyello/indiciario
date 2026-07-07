# ISSUE-40.3 / STEP-05 — Execution Report (Docs)

Type: documentation
Owner: executor

## Objetivo

Documentar o Sistema de Camadas (Camada 0/1/2) implementado no STEP-03, em
`templates/README.md` e `framework/20_SISTEMA_VISUAL.md`, e resolver o
impacto documental declarado em `docs/INDICE_DOCUMENTACAO.md`.

## O que foi feito

1. `templates/README.md`: adicionada seção "Sistema de Camadas (ISSUE-40.3)",
   entre a nota sobre `00_envelope_capa.html` e "Próximos templates
   recomendados". Cobre:
   - Camada 1 (tela, `layer-screen`): e-mail/WhatsApp/Twitter, chrome de app
     permitido.
   - Camada 2 (papel, `layer-paper`): boletim..testamento + evidências
     físicas, sem sombra/radius/gradiente; origem limpa nos templates, reset
     `!important` só como rede de segurança.
   - Camada 0 (jogo/facilitador): chrome (`doc-code`/título/"Envelope N")
     restrito a essa camada; `templates/base.html` documentado como código
     órfão (nenhum template ativo estende, `generator/renderer.py` não
     carrega), não deletado por estar fora do escopo desta issue.
   - Mecanismo real (confirmado contra STEP-03_EXECUTION.md): injeção da
     classe no `<body>` via `generator/renderer.py`
     (`_injetar_classes_body`, tabelas `TEMPLATE_LAYER_SCREEN`/
     `TEMPLATE_LAYER_PAPER`) — mesmo mecanismo de `doc-type-*`/
     `doc-family-*`/`doc-player`, não herança Jinja.
   - Referência ao teste de regressão `tests/test_layer_rules.py`.
   - Link para `framework/20_SISTEMA_VISUAL.md`.

2. `framework/20_SISTEMA_VISUAL.md`: substituído o placeholder
   `<!-- Seções de Camada (40.3) e Microidentidade (40.6) serão adicionadas
   quando essas issues forem concluídas. -->` por seção "Sistema de Camadas
   (ISSUE-40.3)" com o mesmo conteúdo doutrinário (resumido) e link de volta
   para `templates/README.md#sistema-de-camadas-issue-403`. Placeholder da
   Microidentidade (40.6, ainda não concluída) mantido, isolado da seção 40.3.
   Nome do arquivo usado é `20_SISTEMA_VISUAL.md` (real, pós-renumeração
   40.2/STEP-05_FIX-01) — não reintroduzida referência a
   `09_SISTEMA_VISUAL.md`.

3. `docs/INDICE_DOCUMENTACAO.md`: conferida a linha da tabela para
   `20_SISTEMA_VISUAL.md` (linha 83) — já cobre genericamente "camada e
   microidentidade (40.3/40.6)" desde antes deste step, sem texto de status
   por issue que precisasse de atualização. Nenhuma edição necessária;
   impacto documental já estava corretamente escopado nessa linha.

## Comandos executados

Nenhum (STEP-05 não exige comandos — só edição de docs).

## Critério de aceite / Done

- `templates/README.md` tem a seção "Sistema de Camadas": sim.
- `framework/20_SISTEMA_VISUAL.md` estendido com a mesma seção linkando ao
  README: sim.
- Impacto documental resolvido (`docs/INDICE_DOCUMENTACAO.md`): verificado,
  já correto, sem edição necessária.
- Nenhum código alterado: confirmado (só `.md`).
- Nenhuma reintrodução de `09_SISTEMA_VISUAL.md`: confirmado.

## Arquivos alterados

- `templates/README.md`
- `framework/20_SISTEMA_VISUAL.md`

## Próximo passo

Aguardando revisão do STEP-05 (auto-approve, low-risk conforme contrato da
issue).

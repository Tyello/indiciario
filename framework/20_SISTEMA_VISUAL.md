# Sistema Visual — Doutrina de Repaginação Documental

> Origem: `DIAGNOSTICO_VISUAL_DOCUMENTAL.md` (calibração 30.8, benchmark "Uma Noite Sem Flores"), lote de issues 40.x.

## Gate de fidelidade de fonte (ISSUE-40.2)

Todo template que declara uma `font-family` custom deve ter um `@font-face` local
correspondente em `templates/styles/document_system.css`, apontando para
`assets/fonts/` (vendorização feita na ISSUE-40.1).

O gate de qualidade canônico (`generator/canonical_quality_gate.py`) expõe o
check `evaluate_font_fidelity(*, templates=None, browser)`, que mede o
`font-family` computado no render real (Chromium via Playwright, reusando
`generator.font_fidelity.CUSTOM_FONTS` e `fonte_aplicada`) e compara contra a
família declarada. Se algum par template+fonte cair em fallback silencioso
para fonte de sistema, o check retorna `status="blocker"` com `name="font_fidelity"`,
nomeando explicitamente cada template e fonte que falhou na `recommendation` —
nunca um booleano agregado.

Este check não roda por padrão dentro de `evaluate_for_canonical` — quem
invoca o gate (ex.: pipeline ou script de build) precisa construir o critério
chamando `evaluate_font_fidelity` com um `Browser` do Playwright vivo e passar
o resultado via parâmetro opcional `font_fidelity_criterion` de
`evaluate_for_canonical`. Quando fornecido, o critério é anexado a
`criteria_results` e participa da qualificação normalmente (bloqueia
`APPROVED` como qualquer outro critério via `has_blocker`). Chamadas de
`evaluate_for_canonical` sem esse parâmetro continuam funcionando sem o check
de fonte (comportamento pré-40.2 preservado por compatibilidade).

`evaluate_for_canonical` não chama Playwright diretamente — a integração com
browser vivo é responsabilidade do caller do gate, não do gate em si.

## Sistema de Camadas (ISSUE-40.3)

Todo template diegético pertence a uma de duas camadas visuais — misturar os
dois vocabulários (chrome de app aplicado a papel, ou vice-versa) é o defeito
que a 40.3 corrigiu.

- **Camada 1 — Tela** (`layer-screen`): documentos que simulam print de tela
  (e-mail, WhatsApp, rede social). Sombra, `border-radius` e chrome de app são
  corretos e esperados: é vocabulário de UI, não de papel.
- **Camada 2 — Papel** (`layer-paper`): documentos impressos (boletim, carta,
  log de acesso, recibo, orçamento, extrato, bilhete, testamento e demais
  evidências físicas). Papel não projeta sombra de si mesmo, não tem cantos
  arredondados nem gradiente. A origem desses efeitos foi removida
  diretamente de cada template; `.layer-paper` em `document_system.css`
  reseta `box-shadow`/`border-radius`/`background-image` com `!important`
  como rede de segurança, não como mecanismo primário.
- **Camada 0 — Jogo/facilitador**: chrome de protocolo (`doc-code`, título de
  envelope, "Envelope N") só pode aparecer aqui, nunca em Camada 1 ou 2.
  `templates/base.html` contém esse chrome mas é código órfão — nenhum
  template ativo o estende e `generator/renderer.py` não o carrega.

Mecanismo: a classe `layer-screen`/`layer-paper` é injetada no `<body>` de
cada template por `generator/renderer.py` (`_injetar_classes_body`, tabelas
`TEMPLATE_LAYER_SCREEN`/`TEMPLATE_LAYER_PAPER`), o mesmo mecanismo usado para
`doc-type-*`/`doc-family-*`/`doc-player`. Não é herança Jinja.

Teste de regressão: `tests/test_layer_rules.py`
(`test_paper_layer_has_no_screen_chrome`,
`test_diegetic_view_has_no_game_chrome`). Doutrina completa e checklist de
template novo: `templates/README.md#sistema-de-camadas-issue-403`.

<!-- Seção de Microidentidade (40.6) será adicionada quando essa issue for
     concluída. -->

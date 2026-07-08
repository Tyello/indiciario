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

## Microidentidades Institucionais (ISSUE-40.6)

Motivação: dentro de um caso, uma instituição fictícia (museu, empresa,
órgão) emite vários documentos diegéticos diferentes — log de acesso,
manual, cadastro — e hoje eles se pareciam entre si só pelo texto. O jogador
não tinha nenhum sinal visual imediato de "isto veio da mesma fonte". A
40.6 fecha essa lacuna: documentos da mesma instituição compartilham cor,
tipografia de destaque, forma de header e logotipo abstrato, de modo que o
reconhecimento "isto veio do museu" aconteça em meio segundo, sem depender
de reler o remetente — o mesmo papel que a paleta papel-cor (40.4) cumpre
por *tipo* de documento, a microidentidade cumpre por *instituição emissora*.

Mecanismo: três tokens CSS configuráveis por instituição, declarados em
`templates/styles/institution_identity.css` e injetados automaticamente em
todo documento (mesmo hook de `_document_system_css`, via
`_institution_identity_css` em `generator/renderer.py`):

- `--inst-color` — cor de destaque do header.
- `--inst-font-display` — fonte de destaque do header.
- `--inst-header-shape` — forma do header: `reto` (default), `diagonal`
  (clip-path) ou `faixa-dupla` (borda dupla).

Quem monta o blueprint fornece os valores via variáveis de contexto
(`INST_COLOR`, `INST_FONT_DISPLAY`, `INST_HEADER_SHAPE`) — o mesmo trio para
todos os documentos de uma instituição. Um logotipo abstrato reforça a
identidade: `assets/logos/glifo-01.svg`..`glifo-15.svg`, formas geométricas
puras sem semelhança com marca real.

Quando o blueprint não fornece esses tokens (caso de todo blueprint
canônico hoje, que ainda não usa microidentidade), o renderer aplica
fallback neutro (`_aplicar_fallback_institucional`) em vez de deixar
placeholder residual no HTML — a ausência de identidade institucional não é
erro, é o estado padrão até um caso optar por usá-la.

Templates institucionais hoje: `templates/06_log_acesso.html`,
`templates/manual.html`, `templates/cadastro.html`. Doutrina completa,
checklist e detalhe de fallback: `templates/README.md#microidentidades-institucionais-issue-406`.

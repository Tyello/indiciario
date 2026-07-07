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

<!-- Seções de Camada (40.3) e Microidentidade (40.6) serão adicionadas
     quando essas issues forem concluídas. -->

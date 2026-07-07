# ISSUE-40.3 — Regras de camada: Tela vs. Papel + remoção do chrome do jogo

**Status:** especificada, pronta para execução
**Prioridade:** P1
**Depende de:** 40.1
**Bloqueia:** 40.4, 40.5, 40.6

## Objetivo

Formalizar a distinção entre dois vocabulários visuais hoje misturados:

- **Camada 1 (tela)** — e-mail, WhatsApp, rede social: são *prints de tela*, então sombra, `border-radius` e chrome de app são corretos e esperados.
- **Camada 2 (papel)** — boletim, orçamento, contrato, manual, etc.: são documentos impressos. Papel não projeta sombra de si mesmo, não tem `border-radius`, não tem gradiente.

Hoje o CSS mistura os dois vocabulários (ex.: `.accent-bar` do orçamento usa `linear-gradient`, `.orcamento-dates` tem `border-radius: 6px`, `.page` tem `box-shadow` — vocabulário de card web aplicado a um documento de papel).

Além disso, o `base.html` imprime `doc-code` (`DOC-000`), título e "Envelope N" em todo template que o estende — chrome de jogo vazando para dentro da evidência diegética. O `.doc-player { display:none }` mitiga parcialmente, mas o header é estrutural no `base.html`, não opcional.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar a distinção Camada 1 / Camada 2 como regra obrigatória para qualquer template novo.
- `framework/09_SISTEMA_VISUAL.md` (criado na 40.2): adicionar seção "Sistema de Camadas".

## Critério de aceite

1. Todo template de Camada 2 não usa `box-shadow`, `border-radius` nem `gradient` em elementos que representam a superfície do papel.
2. Templates de Camada 1 continuam podendo usar esses recursos (chrome de app é uma escolha correta ali).
3. Nenhum template diegético (Camada 1 ou 2) renderiza `doc-code`, título de jogo ou "Envelope N" na view do jogador — esse chrome só aparece na view do facilitador/protocolo (Camada 0).
4. Teste automatizado comprova os itens 1-3 para os templates existentes.

## Passos (referência para o executor)

1. STEP-01 — Mapear todos os templates existentes e classificá-los em Camada 0/1/2 (usar o inventário do diagnóstico como ponto de partida, confirmar contra o repo atual).
2. STEP-02 — RED: teste que inspeciona o CSS computado de cada template de Camada 2 e falha se encontrar `box-shadow`/`border-radius`/`gradient` na superfície do papel; teste que renderiza a view do jogador e falha se `doc-code`/"Envelope N" aparecer no DOM visível.
3. STEP-03 — GREEN: refatorar `document_system.css` introduzindo as classes utilitárias de camada; refatorar `base.html` para que o chrome de jogo só exista em templates de Camada 0 (extração do header para um partial próprio, não herança automática).
4. STEP-04 — Rodar toda a suíte de templates existentes contra os novos testes, ajustar cada template que falhar.
5. STEP-05 — Docs: `templates/README.md` + `framework/09_SISTEMA_VISUAL.md`.

Ver `ISSUE-40.3_SPEC.md` para o detalhamento técnico.

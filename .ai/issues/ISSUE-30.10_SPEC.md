# ISSUE-30.10 — Codificar padrões importados do corpus de calibração

## Contexto

A calibração da ISSUE-30.8 ("Uma Noite Sem Flores") destilou técnicas reutilizáveis que tornam um caso bom — mas elas vivem hoje só dentro do blueprint `examples/caso_referencia_uma_noite_sem_flores.json`. Não estão nomeadas em lugar nenhum que o gerador consulte. Resultado: o gerador pode alcançá-las por sorte, não de propósito.

Este é o gap 3 do balanço pós-calibração: **padrões importáveis ainda não codificados**. É o de maior valor por menor custo — não exige código nem schema novo, só transforma conhecimento tácito (preso num JSON) em padrão explícito no documento que é fonte de verdade do gerador.

`framework/08_MODELO_REFERENCIA.md` já tem estrutura madura (Parte 1 "o que funciona", Parte 2 anti-padrões, Parte 3 fórmula, Partes 4–5 checklists). Alguns padrões da calibração têm sobreposição parcial com a Parte 1 existente (1.2 vetores convergentes, 1.3 mecanismo de exceção, 1.5 terceirizados). Esta issue **integra e nomeia**, sem duplicar.

**Origem:** balanço de calibração 2026-06-29. Conhecimento destilado vira regra de geração; não é patch de caso.

## Objetivo

`framework/08_MODELO_REFERENCIA.md` passa a conter quatro padrões nomeados, reutilizáveis e referenciáveis pelo gerador; e `framework/07_PROMPT_GERADOR_DE_CASO.md` os referencia explicitamente, instruindo o gerador a alcançá-los de propósito.

## Fora de escopo

- **Não** introduzir código, campo de schema ou métrica nova.
- **Não** alterar blueprints existentes (canônicos ou de calibração).
- **Não** criar padrões inéditos não observados em caso real — apenas codificar os que a calibração e os canônicos já demonstram.
- **Não** transformar os checklists (Partes 4–5) — só a Parte 1 e o cross-link no 07.

## Contrato / regras

Adicionar quatro padrões. Cada um, no mesmo formato da Parte 1 existente (título + prosa curta), DEVE conter: **definição** (uma frase), **quando usar**, **campos do blueprint que o materializam**, **exemplo** (apontando o caso de calibração e/ou um canônico que já o usa), e **modo de falha** (como o padrão vira anti-padrão se mal aplicado, com cross-ref à Parte 2 quando houver).

- **PAT-01 — Pilar de presença (credencial × regra).** Um registro de presença (log de acesso: ator + ponto + horário) só vira prova quando confirmado por um documento de regra independente (manual que define que a credencial é pessoal/intransferível e que um ponto exige autenticação exclusiva). Campos: `pilares_validacao` (documento_principal = log, confirmacao = manual, personagem_id = ator), `documentos` tipo `log_acesso` + `manual`. Exemplo: calibração (E1-03 × E1-02, credencial na porta biométrica). Integra/aprofunda 1.3 (mecanismo de exceção). Modo de falha: log sem regra de confirmação → presença vira coincidência (cross-ref 2.7 período do log).
- **PAT-02 — Descarte por motivo-sem-oportunidade.** O suspeito aparente tem motivo e está presente, mas um documento prova que não teve a oportunidade física (posto/credencial não o colocam no local no intervalo crítico). Campos: `red_herrings` (categoria `motivo_sem_oportunidade`) + `contratos_evidencia` (tipo `descarte`) + documento de descarte. Exemplo: calibração (Rui na sala de segurança, sem passagem pela galeria). Modo de falha: descarte sem documento que o ancore → vira afirmação do facilitador, não dedução do jogador.
- **PAT-03 — Pista-código offline (elemento em A, chave em B).** Um código impresso num documento (etiqueta, sequência, cor→hex) só se resolve cruzando com a chave de decodificação em outro documento — pista não óbvia, 100% offline. Campos: `codigos` (documento = onde aparece, chave_em = onde decodifica, elementos), `documentos` que carregam ambos. Exemplo: calibração (#7F004B no orçamento de corte × catálogo da Arcano). Modo de falha: chave no mesmo documento → deixa de ser dedução (cross-ref 2.4 critério misto).
- **PAT-04 — Virada de envelope: suspeito presente / objeto ausente.** O E1 fecha num suspeito plausível e presente; o E2 vira a leitura ao constatar que o objeto do crime já não está onde o suspeito está, reorientando de "quem parece" para "como saiu / para onde". Campos: `objetivos_por_envelope` (E1 = suspeito; E2 = culpado + destino), `conflito_central.verdade_aparente` vs `verdade_real_resumida`, salto em `cadeia_financeira`. Exemplo: calibração (E1 nomeia a credencial interna; E2 segue a obra pela logística). Modo de falha: E2 que só confirma o E1 sem virar a leitura → o segundo envelope não justifica sua existência.

- **PAT-05 (cross-link no 07).** `framework/07_PROMPT_GERADOR_DE_CASO.md` ganha uma referência explícita: ao gerar, considerar deliberadamente os padrões PAT-01..04 de `08_MODELO_REFERENCIA.md`, citando-os pelo nome. Sem reescrever o prompt — só um ponteiro acionável.

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilho: "muda metodologia/conteúdo do modelo de referência" e "qualquer doc alterado de forma relevante").

- [ ] `framework/08_MODELO_REFERENCIA.md` — **primário**: adicionar PAT-01..04 na Parte 1 (subseções 1.8–1.11 ou bloco "Padrões destilados do corpus de calibração"), com cross-refs à Parte 2.
- [ ] `framework/07_PROMPT_GERADOR_DE_CASO.md` — adicionar o ponteiro PAT-05.
- [ ] `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` — uma linha apontando que os padrões destilados foram codificados no 08 (fecha o ciclo do relatório).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — atualizar a descrição/coluna "Atualizar quando" do 08 se a estrutura mudou materialmente; senão ⏭️ com motivo.
- [ ] `docs/ESTADO_ATUAL.md` — uma linha: padrões da calibração agora codificados no modelo de referência.

## Casos de teste

Issue de autoria/documentação; verificações objetivas (sem TDD de código):

- Os quatro padrões existem no 08, cada um com os cinco elementos exigidos (definição, quando usar, campos, exemplo, modo de falha).
- Cada exemplo aponta para um caso real do repo (calibração e/ou canônico) e os campos citados existem de fato no schema (`pilares_validacao`, `red_herrings.categoria`, `codigos`, `objetivos_por_envelope`, `cadeia_financeira`).
- O 07 referencia PAT-01..04 pelo nome.
- `pytest tests/ -q` sem regressão (não deve haver alteração de código; confirma que nada quebrou).

## Restrições arquiteturais

Sem código, sem schema novo, sem métrica. Não duplicar conteúdo já presente na Parte 1 — integrar com cross-ref. Linguagem dos padrões em PT-BR, no tom do 08.

## Critério de aceite

- [ ] PAT-01..04 no `framework/08`, cada um completo (5 elementos), sem duplicar a Parte 1 existente.
- [ ] PAT-05: `framework/07` referencia os padrões pelo nome.
- [ ] Exemplos rastreáveis a casos reais; campos citados existem no schema.
- [ ] Impacto documental resolvido (✅/⏭️ por item).
- [ ] `pytest tests/ -q` sem regressão.

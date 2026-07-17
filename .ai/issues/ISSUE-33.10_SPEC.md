# ISSUE-33.10 — Autópsia da calibração: por que o benchmark saiu "injusto"

## Contexto

A primeira execução real do Solvability Meter (33.9) rodou contra "Uma Noite Sem Flores" — caso com playtest comercial, portanto **comprovadamente justo**. O meter retornou `solve_rate 0.00 / injusto` nos dois lotes, com `AMBIGUIDADE_DETECTADA` + `VAZAMENTO_DETECTADO` no lote 1 e 3 de 8 runs incompletas. Como o caso é justo por evidência externa, um veredito `injusto` é **defeito do instrumento**, não do caso. Esta issue descobre em qual camada a corrente arrebenta, **sem corrigir nada** — a correção será uma issue separada, informada por este diagnóstico.

Regra anti-viés: o diagnóstico não pode assumir "o solver é fraco" como hipótese default. As flags (`vazamento` = conclusão atingida mas sem citar evidência-chave) sugerem o oposto — que o solver resolve e o julgamento descarta. As hipóteses são testadas do mais barato/provável ao mais caro.

Origem: resultado do STEP-04 da ISSUE-33.9 (jul/2026).

## Objetivo

Um relatório `docs/DIAGNOSTICO_CALIBRACAO_33.10.md` que identifica, com evidência dos artefatos já gerados, a(s) camada(s) causadora(s) do falso `injusto`, e propõe a issue de correção correspondente — sem tocar código, prompts, E1 ou limiares nesta issue.

## Fora de escopo — CRÍTICO

- **Nenhuma correção**: proibido editar `solvability_meter.py`, prompts v1, `expected_*.json`, limiares SM_003, judge ou solver.
- **Nenhuma execução nova**: proibido rodar `solvability_cli`, `claude -p` ou qualquer chamada real. O diagnóstico usa exclusivamente `calibration/reports/calib_lote1.json`, `calib_lote2.json`, os run records/artefatos de solver e judge já persistidos, o bundle e o E1.
- Se algum artefato necessário não tiver sido persistido, isso **é um achado** (observabilidade insuficiente), não motivo para reexecutar.

## Hipóteses (testar nesta ordem, parar de aprofundar quando confirmada mas registrar todas)

| # | Hipótese | Como testar (só leitura de artefatos) | Se verdadeira → correção futura |
|---|---|---|---|
| H-E1a | `key_evidence_ids` do E1 não correspondem a `artifact_id` reais do bundle | Cruzar cada id de `key_evidence_ids` com os ids presentes no manifest do bundle | toda conclusão vira "vazamento" por construção → corrigir E1 |
| H-E1b | Statements do E1 exigem fraseologia/granularidade que o gabarito real não expressa | Ler statements vs. solução do blueprint transcrito | reescrever statements |
| H-Ja | Judge rebaixa `met` de conclusões corretas por falha de casamento semântico em PT (paráfrase legítima tratada como divergência) | Ler, num run, a `conclusion` do solver + o veredito do judge item a item; o solver acertou em prosa mas judge marcou não-met? | ajustar prompt do judge (v2) |
| H-Jb | CJ_005 rebaixa em massa: solver conclui mas `evidence_cited` vazio/formato incompatível | Contar quantos itens viraram `met=false` por evidence vazia no veredito | ajustar contrato de citação solver↔judge |
| H-Sa | Solver realmente não resolve (culpado/método errados na prosa, não só na forma) | Só depois de H-J descartadas: a `conclusion` textual do solver diverge do gabarito? | caso mais sério: prompt do solver ou expressividade do bundle |
| H-Ra | Runs incompletas por timeout (dossiê grande) vs. parse-fail vs. transporte | Ler stderr/erro registrado das 3 runs incompletas; classificar a causa | ajustar timeout/repair (issue de robustez) |
| H-Ma | Ambiguidade real: dois suspeitos satisfazem as evidências no bundle cego | Só se H-E1/H-J descartadas: a solução alternativa relatada pelo solver é de fato coerente? | achado de design do caso, não do meter |

## Entregável — `docs/DIAGNOSTICO_CALIBRACAO_33.10.md`

1. Inventário de artefatos disponíveis (o que foi persistido; o que faltou = achado de observabilidade)
2. Tabela das 7 hipóteses com veredito (confirmada / descartada / indeterminada por falta de dado) + evidência citada (id, trecho, número)
3. Autópsia detalhada de **1 run de vazamento** e **1 run incompleta**, passo a passo
4. Camada(s) culpada(s), em ordem de contribuição
5. Issue(s) de correção proposta(s): título, objetivo em 1 frase, escopo, e se exige nova execução de calibração após corrigir
6. Recomendação sobre observabilidade: que campo/artefato o meter deveria persistir para que a próxima autópsia não dependa de sorte

## Impacto documental

- [ ] `docs/DIAGNOSTICO_CALIBRACAO_33.10.md` — novo (o entregável).
- [ ] `docs/ESTADO_ATUAL.md` — motivo: registrar que a calibração 33.9 está em diagnóstico (meter não validado ainda; portão da 30.11 permanece fechado).
- [ ] Nada mais: esta issue não altera roadmap de correção — as issues propostas entram depois, com sua aprovação.

## Critério de aceite

- [ ] As 7 hipóteses julgadas com evidência ou marcadas indeterminadas com o dado faltante nomeado
- [ ] Autópsia de 1 run de vazamento + 1 incompleta presente
- [ ] Camada culpada identificada OU lista explícita do que falta observar para concluir
- [ ] Issue(s) de correção proposta(s) com escopo fechado
- [ ] Zero alteração em código/prompts/E1/limiares (git diff só toca os 2 docs); zero execução real (sem novas entradas em calibration/reports/)

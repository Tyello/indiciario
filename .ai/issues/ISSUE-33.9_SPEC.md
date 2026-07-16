# ISSUE-33.9 — Calibração do Solvability Meter contra o benchmark "Uma Noite Sem Flores"

## Contexto

O meter nunca foi validado contra um caso com veredito humano conhecido. "Uma Noite Sem Flores" é o único caso do repo com playtest comercial externo — é o padrão-ouro para responder: **o medidor mede certo?** Antes de usar o meter para julgar casos novos (30.11) ou os existentes, ele mesmo precisa passar por este teste. Esta issue é um **experimento operado por humano** (as execuções reais custam dinheiro e envolvem a API), com preparação e análise executáveis por agente.

**Risco central desta calibração — contaminação de treino:** o caso é comercial e publicado; o modelo solver pode conhecê-lo de treino. Se conhecer, resolve "de memória" e a calibração fica enviesada para cima. O roteiro inclui uma sonda de contaminação obrigatória antes das medições, e o relatório final deve qualificar os resultados por esse fator.

Origem: sequenciamento decidido em chat (jul/2026); princípio "calibração antes de geração".

## Objetivo

Um relatório versionado (`docs/CALIBRACAO_SOLVABILIDADE_2026-07.md`) comparando os vereditos do meter com os resultados humanos conhecidos do benchmark, com decisão explícita sobre os limiares SM_003 e sobre os prompts v1 — mantê-los ou abrir issue de ajuste.

## Fora de escopo

- Ajustar limiares/prompts nesta issue (se a calibração indicar ajuste, abre-se issue própria com o dado em mãos).
- Medir os demais casos do repo (passo seguinte, após meter calibrado).
- Qualquer alteração no blueprint do benchmark.

## Entregáveis

| # | Entregável | Descrição |
|---|---|---|
| E1 | `calibration/expected_uma_noite_sem_flores.json` | Statements do gabarito (`ExpectedConclusionInput`: culpado, método, motivo + required) e `key_evidence_ids` das pistas decisivas, extraídos do blueprint transcrito. Diretório novo `calibration/` fora de `examples/` (não é caso jogável, é fixture de calibração). |
| E2 | Bundle cego do benchmark | Gerado pelo `blind_bundle_generator` existente; hash registrado. |
| E3 | Sonda de contaminação (pré-medição) | Ver roteiro, fase 2. Resultado registrado no relatório. |
| E4 | Execuções do meter | Mínimo 2 configurações (adendo, ver `.ai/issues/ISSUE-33.9_ADENDO.md`): `--runs 5 --solver-model opus --judge-model sonnet` (principal, variação vem da amostragem padrão do modelo — temperatura é provider-controlled, CC_005) e `--runs 3 --solver-model opus --judge-model sonnet` em nova execução (sensibilidade, mede estabilidade entre lotes). Reports JSON commitados em `calibration/reports/`. |
| E5 | `docs/CALIBRACAO_SOLVABILIDADE_2026-07.md` | Relatório de calibração (estrutura abaixo). |

## Roteiro de execução

**Fase 1 — Preparação (agente, sem API):**
1. Extrair E1 do blueprint transcrito; validar contra o formato aceito pelo CLI (`--expected`); revisar manualmente que os statements não vazam além do necessário (são o insumo do judge, nunca do solver).
2. Gerar E2 com o pipeline existente; rodar `leak_checker`; registrar hashes de bundle e dos templates de prompt (reproducibility da 33.5).
3. Smoke test do circuito inteiro com FakeProvider sobre o bundle real (prova de plumbing sem custo).

**Fase 2 — Sonda de contaminação (humano, headless, sem chamada de API — adendo):**
4. Três perguntas diretas ao modelo solver escolhido, **sem bundle**, via `claude -p` headless num diretório temporário vazio (mesmo confinamento do provider — essencial: numa pasta do repo a sessão poderia ler o gabarito):
```
cd $(mktemp -d)
claude -p "Você conhece o caso 'Uma Noite Sem Flores', da série Sob Investigação? Responda o que souber." --model opus
claude -p "No caso 'Uma Noite Sem Flores' (Sob Investigação), quem é o culpado e qual foi o método?" --model opus
claude -p "No caso 'Uma Noite Sem Flores', cite nomes de personagens secundários que você lembrar." --model opus
```
Colar as três saídas brutas no report do STEP-02.
5. Classificar: **CONTAMINADO** (identifica culpado/método corretamente) → os resultados de solvabilidade valem como *limite superior*; registrar e considerar rodar também com o caso anonimizado (renomear pessoas/lugares no bundle — decisão adiada para o relatório). **LIMPO** (não conhece ou erra) → calibração válida sem ressalva. **PARCIAL** → registrar exatamente o que reconheceu.

**Fase 3 — Medição (humano, headless, sem API key — adendo):**
6. Rodar E4 via `solvability_cli` com os dois setups (`--runs 5`/`--runs 3`, ambos `--solver-model opus --judge-model sonnet`); guardar reports e **consumo de cota da assinatura** (não custo em dinheiro) por run — anotar horário e eventual atingimento de limite (recomenda-se rodar fora do horário de desenvolvimento). Informa a viabilidade de usar o meter como gate rotineiro em termos de cota, não de custo monetário.

**Fase 4 — Análise (agente, sem API):**
7. Comparar com o veredito humano conhecido: o caso comercial playtestado deve sair `resolvido` na maioria dos runs, sem flags de ambiguidade/vazamento; a dificuldade estimada deve ser confrontada com a dificuldade observada nos playtests reais (fonte: transcrição/notas do benchmark no repo).
8. Auditar 1 run em detalhe: as `pistas_usadas` do solver batem com as pistas que o material comercial considera decisivas? `citacao_sem_leitura` (RV_009) disparou?
9. Escrever E5 com veredito por hipótese (abaixo) e recomendação final.

## Estrutura do relatório (E5)

1. Setup (modelos, hashes; `temperature: null / provider-controlled` — CC_005, sem eixo de temperatura no headless; consumo de cota da assinatura por run, não custo em dinheiro)
2. Resultado da sonda de contaminação e como qualifica tudo abaixo
3. Resultados brutos (solve_rate, classificações, flags por configuração)
4. Hipóteses julgadas: H1 "o meter reconhece caso justo como resolvível" (esperado: sim); H2 "limiares SM_003 mapeiam para a dificuldade humana observada"; H3 "prompts v1 extraem citações de evidência corretas"; H4 "flags não produzem falso alarme em caso sabidamente não-ambíguo"
5. Decisão: limiares/prompts mantidos OU issue de ajuste proposta (com números)
6. Aprovação para o passo seguinte: medir casos gerados existentes (sim/não + condições)

## Impacto documental

- [ ] `docs/CALIBRACAO_SOLVABILIDADE_2026-07.md` — novo (E5).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — motivo: doc e diretório `calibration/` novos.
- [ ] `framework/05_CHECKLIST_SOLVABILIDADE.md` — motivo: referenciar a calibração como lastro do gate automatizado.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: marco "primeira execução real do circuito solver".
- [ ] `docs/ROADMAP.md` — motivo: registrar 33.9; desbloquear formalmente a medição dos casos existentes e a 30.11.

## Critério de aceite

- [ ] E1–E5 entregues e commitados; hashes e custo registrados
- [ ] Sonda de contaminação executada ANTES das medições e registrada
- [ ] As 4 hipóteses julgadas com dados, não impressão
- [ ] Decisão explícita sobre SM_003/prompts (manter ou issue de ajuste com números)
- [ ] Nenhuma alteração em código, schemas ou no blueprint do benchmark
- [ ] pytest tests/ -q sem regressão (prova de não-mutação)

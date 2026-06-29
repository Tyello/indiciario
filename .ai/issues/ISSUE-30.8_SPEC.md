# ISSUE-30.8 — "Uma Noite Sem Flores" como terceiro ponto de calibração

## Contexto

Temos duas réguas validadas (Mirante/Iniciante, Aurora/Intermediário) e três casos não validados em `examples/`. Falta um **caso externo, já validado por playtest real, independente da nossa geração**, para ancorar o que "bom" deveria parecer nas nossas métricas. "Uma Noite Sem Flores" (jogo físico "Sob Investigação") é esse caso: playtest reconhecido como envolvente, mapa bom, dicas boas, pistas não óbvias e — o que mais importa para nós — **resolução por cruzamento de documentos** (log de acessos × manual de crachá × escala de turnos × mapa), com um humano por trás de cada texto.

Sondagem prévia (ver ISSUE-30.7) mostrou que nosso estimador de dificuldade é volumétrico e degenerado. Rodar um caso querido e validado pela nossa pipeline é um **teste de calibração**: mede se a nossa noção automática de qualidade bate com a qualidade real de mesa. Predição a confirmar: as checagens de volume tenderão a superdimensionar a dificuldade desse caso (muitos documentos, vários suspeitos), embora ele seja envolvente-mas-justo. Se isso se confirmar, o objeto descalibrado é a métrica, não o caso.

A espinha dedutiva do caso (resumo spoiler-safe para o spec; o gabarito completo vai no blueprint, não aqui): o suspeito aparente (E1) está fisicamente no museu, mas o quadro não está mais lá (E2); o crime exige acesso interno por crachá/biometria registrado em log; a obra de alto valor sai disfarçada na logística da reforma (BID, transporte, serviço de corte/solda aplicável à moldura-relíquia). É um caso de **pilar de presença + descarte (motivo sem oportunidade) + salto logístico**, que mapeia quase 1:1 no nosso schema de `Blueprint`.

**Origem:** decisão de produto 2026-06-28 — adotar um caso externo validado como corpus de calibração. Não é caso canônico nem candidato a régua.

## Objetivo

Existir em `examples/` um blueprint **não canônico** de "Uma Noite Sem Flores" que passa no `validator --strict`, e um relatório de calibração (`docs/CALIBRACAO_REFERENCIA_EXTERNA.md`) registrando o que a pipeline aponta sobre ele — separando sinal real de artefato de codificação e de falso positivo de métrica.

## Fora de escopo

- **Não** promover a canônico, não gerar régua, não rodar Canonical Quality Gate como certificação. É corpus de calibração.
- **Não** gerar pacote de impressão/PDF nem baseline visual nesta issue (pode virar follow-up).
- **Não** reproduzir os mecanismos digitais do original (QR code, "falar com o delegado" via site, pistas restritas a telefone/e-mail da compra). Tradução offline obrigatória; o que não traduz vira **finding registrado**, não é importado.
- **Não** copiar texto literal do material original além do mínimo necessário; os documentos do blueprint são **reescritos** preservando função e tom, não transcritos. Nomes/CNPJs/empresas são recriados como ficção própria do Indiciário.
- **Não** rodar playtest (continua sendo a única prova real de solvabilidade; esta issue não a substitui).

## Contrato / regras

### Fidelidade investigativa (o que precisa sobreviver à codificação)

- **FF-01** — Preservar a espinha de dois envelopes: E1 produz hipótese/recontextualização parcial (suspeito aparente + por que ele não basta), E2 vira a leitura (o quadro já saiu; quem e para onde).
- **FF-02** — Preservar o cruzamento central como **pilar de presença**: documento principal = log de acessos (porta + ID de credencial + horário); confirmação independente = manual de controle de acesso (crachá pessoal/intransferível; porta de biometria não aceita crachá); contexto = escala de turnos + mapa.
- **FF-03** — Preservar pelo menos um **descarte** do tipo `motivo_sem_oportunidade` (o suspeito aparente está no local, mas a obra não — presença não é culpa).
- **FF-04** — Preservar o **salto logístico** da obra para fora: BID/reforma → transporte/armazenagem → serviço aplicável à moldura-relíquia, cada elo com `documento_prova` e, onde houver, `confirmacao_independente`.
- **FF-05** — Preservar ambiguidade boa: o caso não pode ter confissão, conclusão pronta nem nome-do-culpado-associado-a-ação-incriminadora (respeitar `OBV_001..012`). Pistas permanecem não óbvias.
- **FF-06** — Manter ao menos um **código/cruzamento** análogo ao cartão "cor → código" do original, traduzido para pista offline legítima (ex.: código hex impresso que indexa outro documento), declarado em `codigos` do blueprint.

### Tradução offline (ganchos digitais → equivalente, ou finding)

- **TR-01** — "Falar com o delegado via QR/site" → **não traduz**: é loop de validação externo. Substituir pela mecânica nativa do Indiciário (objetivo por envelope + critério de avanço + guia do facilitador). Registrar como gancho não importável.
- **TR-02** — "Pistas restritas ao telefone/e-mail da compra" → **não traduz**: registrar como gancho não importável (viola "offline first, sem dependência externa").
- **TR-03** — Cartão "toda cor tem um código" (hex) → **traduz**: vira `codigos` offline (elementos impressos num documento, chave em outro). Importável.
- **TR-04** — Mapa do museu → **traduz**: vira documento de jogador do E1 no padrão P2 de plantas (`docs/FLOORPLANS.md`) ou referência espacial textual; decidir no STEP-01 conforme custo.
- **TR-05** — Cada decisão TR vira uma linha no relatório de calibração: importado / adaptado / descartado, com motivo.

### Artefatos e schema

- **AF-01** — Arquivo: `examples/caso_referencia_uma_noite_sem_flores.json`. Campo de dificuldade declarada: decidir no STEP-01 a partir do framework (provável Intermediário), mas registrar que a **declaração é uma hipótese a ser testada pela calibração**, não uma régua.
- **AF-02** — O blueprint respeita o schema estrito (`additionalProperties: false`, `required_when`, `conflito_central`, `objetivos_por_envelope`, `guia_operacional` schema-enforced). Passa `validator --strict` (avisos permitidos; zero erros).
- **AF-03** — Marcação não-canônica explícita: incluir em metadados internos / nota do caso que é **corpus de calibração externo, não régua, não canônico**.

### Relatório de calibração

- **CR-01** — `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` registra: tabela TR (importado/adaptado/descartado), saída do `validator --strict`, do `case_review`, do `clue_graph` (depth, GP_*), e do estimador de dificuldade **antes e depois** de ISSUE-30.7 (se já mergeada).
- **CR-02** — Para cada finding da pipeline, classificar em: **sinal real** (defeito de fato no caso), **artefato de codificação** (limitação da nossa tradução, não do caso), ou **falso positivo de métrica** (a métrica está errada, não o caso). Esta classificação é o entregável de valor.
- **CR-03** — Conclusão explícita: o caso confirma ou refuta a predição de que nossas métricas superdimensionam dificuldade de casos ricos? Recomendações para o framework (sem patch retroativo de casos).

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilho "qualquer doc novo ou movido" → este índice; e "novo caso em examples/" → rosters/DIFFICULTY/ESTADO).

- [ ] `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` — **novo doc** (relatório de calibração).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — **obrigatório**: registrar o novo doc e o novo exemplo de calibração.
- [ ] `docs/DIFFICULTY_FRAMEWORK.md` — adicionar o caso externo como linha na tabela de métricas (documentos, densidade, depth), marcado como corpus de calibração.
- [ ] `docs/ESTADO_ATUAL.md` — no roster, registrar o caso de referência como **não-régua, corpus de calibração externo**; deixar claro que não é validado pela nossa geração.
- [ ] `README.md` / `AGENTS.md` / `CLAUDE.md` — avaliar nota de roster: distinguir réguas canônicas de corpus de calibração. Provável uma linha cada, ou ⏭️ justificado se a distinção já estiver clara.
- [ ] `examples/` (CI) — incluir o novo blueprint na cobertura de `validator --strict` da CI, **sem** incluí-lo na promoção canônica.

## Casos de teste

Esta issue é de **geração + análise**, não de TDD de código. Verificações objetivas:

- `validator --strict examples/caso_referencia_uma_noite_sem_flores.json` → 0 erros (avisos permitidos e registrados).
- `clue_graph` produz pelo menos um contrato final com `depth ≥ 2` e nenhum `GP_007` (contrato final sem caminho mínimo).
- Os pilares FF-02/FF-03/FF-04 existem como entidades no blueprint (presença, descarte `motivo_sem_oportunidade`, salto com `documento_prova`).
- `obviousness_checker` não acusa `OBV_001`/`OBV_009` (sem confissão/nome-do-culpado em ação incriminadora).
- `pytest tests/ -q` sem regressão (a issue não deve quebrar nada existente).

## Restrições arquiteturais

Herdar as padrão: sem LLM em runtime, sem rede, sem mutação de artefatos existentes; `additionalProperties: false`; `ruff` limpo em qualquer script novo (não deve haver). **Não** alterar canônicos nem baselines. A autoria do blueprint segue o fluxo de geração do `framework/07_PROMPT_GERADOR_DE_CASO.md` e o contrato de `docs/BLUEPRINT_AUTHORING_GUIDE.md`.

> **Nota de tamanho / decomposição:** um blueprint fiel pode passar de 1000 linhas. Se não couber numa PR revisável, decompor: **30.8a** = E1 (pilar de presença + descarte) válido em strict; **30.8b** = E2 (salto logístico) + relatório de calibração. Decidir no STEP-01.

> **Nota de execução:** a autoria do JSON é o passo mais pesado e é candidata a ser produzida **em chat** (fluxo "LLM gera o blueprint", como nos canônicos) e então commitada, deixando para o Claude Code a validação, a análise e o relatório. O STEP-02 admite as duas vias; registrar qual foi usada.

## Critério de aceite

- [ ] `examples/caso_referencia_uma_noite_sem_flores.json` existe e passa `validator --strict` (0 erros).
- [ ] FF-01..06 e TR-01..05 satisfeitos e rastreáveis no blueprint/relatório.
- [ ] `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` com tabela TR, saídas da pipeline e a classificação CR-02 (sinal real / artefato de codificação / falso positivo de métrica).
- [ ] Caso marcado como não-canônico; não entra na promoção canônica.
- [ ] `docs/INDICE_DOCUMENTACAO.md` atualizado (novo doc + novo exemplo).
- [ ] `pytest tests/ -q` sem regressão; `ruff` limpo.
- [ ] Impacto documental resolvido (✅/⏭️ por item).

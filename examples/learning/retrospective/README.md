# Learning Ledger retrospectivo — ISSUE-10

Estes exemplos são retrospectivos e foram reconstruídos a partir de fontes documentais já versionadas no repositório.
Eles **não** representam transcrição integral das sessões, não são novos casos canônicos, não corrigem os casos analisados nesta PR, não criam regras globais e não promovem automaticamente heurísticas, validators ou guardrails.
Informações ausentes não foram inventadas: lacunas de horário, ratings e sequência de eventos aparecem em `record_quality.missing_information`.

Os problemas do Hotel Aurora que as fontes declaram incorporados ou consolidados aparecem como `RESOLVED` para preservar o estado histórico real. `RESOLVED` aqui significa que a fonte documental registra incorporação/consolidação no caso analisado; não significa regra global, guardrail, nem revalidação independente nova criada pela ISSUE-10.

## Cardinalidade e anonimização

A rodada documentada do Hotel Aurora informa três participantes: dois adultos e uma criança de 11 anos. Os ledgers preservam essa cardinalidade com IDs neutros (`PARTICIPANT-RETRO-01`, `PARTICIPANT-RETRO-02`, `PARTICIPANT-RETRO-03`) e não reproduzem nomes reais, experiência de jogo ou relação com o projeto quando a fonte não sustenta esses dados.

## Convenções temporais

- A fonte registra data e duração total de 100 minutos para a rodada; `started_at` e `finished_at` usam uma janela técnica `2026-06-05T00:00:00+00:00` → `2026-06-05T01:40:00+00:00`.
- Esses horários técnicos não são observação histórica real e a lacuna aparece em `record_quality.missing_information`.
- `created_at`, `updated_at`, `resolved_at` e campos técnicos de implementação usam o timestamp da migração da ISSUE-10 (`2026-06-12T00:00:00+00:00`).

## source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01.md
- docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md

## Ledgers

### aurora-envelope-goals

- Caso: O Último Brinde do Hotel Aurora.
- Fonte: [INTERMEDIARIO_RODADA_01.md](../../../docs/playtests/INTERMEDIARIO_RODADA_01.md).
- Fatos preservados: o registro informa que a maior parte do tempo ficou no Envelope 1, que os objetivos dos envelopes não estavam claros e que o grupo não sabia quando abrir o Envelope 2.
- Inferência registrada: a progressão provavelmente precisava de objetivo/critério de abertura mais claro.
- Lacunas: horário real, sequência detalhada de mesa e ratings não foram documentados.
- Status histórico: `RESOLVED`, porque a fonte declara que os problemas P0 foram incorporados ao blueprint/guia operacional e que o caso foi validado como régua canônica Intermediária.
- Decisão: `case_review_candidate`, escopo `case_only`, `implementation_status: implemented`.
- Não generalização: a resolução vale para o caso documentado e não cria regra global.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/aurora-envelope-goals`.

source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01.md

### aurora-document-diegesis

- Caso: O Último Brinde do Hotel Aurora.
- Fonte: [INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md](../../../docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md).
- Fatos preservados: a fonte registra que informações corretas estavam no documento errado e lista recipientes documentais que soavam artificiais.
- Inferência registrada: o recipiente documental pode prejudicar diegese mesmo quando a informação é correta.
- Lacunas: horário real do refinamento, ratings e revalidação independente nova.
- Status histórico: `RESOLVED`, porque a fonte declara refinamento consolidado, decisões editoriais específicas e preservação da régua canônica.
- Decisão: `example_only`, escopo `case_only`, `implementation_status: implemented`.
- Não generalização: o exemplo ilustra um problema real do Hotel Aurora, mas não prova recorrência global.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/aurora-document-diegesis`.

source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md

### aurora-hints-guidance

- Caso: O Último Brinde do Hotel Aurora.
- Fonte: [INTERMEDIARIO_RODADA_01.md](../../../docs/playtests/INTERMEDIARIO_RODADA_01.md).
- Fatos preservados: a fonte registra que as dicas quase não foram usadas e, quando usadas, quase não deram direção; também recomenda reescrevê-las em camadas para tirar grupos do travamento.
- Inferência registrada: as dicas provavelmente precisavam de orientação operacional mais clara sem substituir investigação.
- Lacunas: pedidos individuais de dica, momento exato de uso e ratings não foram documentados.
- Status histórico: `RESOLVED`, porque a reescrita de dicas foi listada como P0 e a fonte declara incorporação dos P0 no blueprint/guia operacional.
- Decisão: `case_review_candidate`, escopo `case_only`, `implementation_status: implemented`.
- Não generalização: a decisão serve como exemplo e pergunta de revisão futura, não como guardrail global.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/aurora-hints-guidance`.

source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01.md

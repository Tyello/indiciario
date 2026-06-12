# Learning Ledger retrospectivo — ISSUE-10

Estes exemplos são retrospectivos e foram reconstruídos a partir de fontes documentais já versionadas no repositório.
Eles **não** representam transcrição integral das sessões, não são novos casos canônicos, não corrigem os casos analisados, não criam regras globais e não promovem automaticamente heurísticas, validators ou guardrails.
Informações ausentes não foram inventadas: lacunas de horário, participantes, ratings e sequência de eventos aparecem em `record_quality.missing_information`.

## Convenções temporais

- Quando a fonte registrou apenas a data, `started_at` e `finished_at` usam uma janela técnica com timezone UTC e a lacuna é declarada no registro.
- Quando nem a data do refinamento estava documentada, a janela técnica usa o timestamp de migração da ISSUE-10 (`2026-06-12T00:00:00+00:00`) apenas para satisfazer o schema.
- `created_at` e `updated_at` usam o timestamp técnico da migração da ISSUE-10.

## source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01.md
- docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md
- docs/baselines/BASELINE_VISUAL_2_0_CANONICOS.md

## Ledgers

### aurora-envelope-goals

- Caso: O Último Brinde do Hotel Aurora.
- Fonte: [INTERMEDIARIO_RODADA_01.md](../../../docs/playtests/INTERMEDIARIO_RODADA_01.md).
- Fatos preservados: o registro informa que a maior parte do tempo ficou no Envelope 1, que os objetivos dos envelopes não estavam claros e que o grupo não sabia quando abrir o Envelope 2.
- Inferência registrada: a progressão provavelmente precisava de objetivo/critério de abertura mais claro.
- Lacunas: horário real, sequência detalhada de mesa, ratings e participantes nomeados não são reproduzidos.
- Decisão: `case_review_candidate`, escopo `case_only`.
- Não generalização: há uma rodada retrospectiva documentada, insuficiente para `global_editorial`.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/aurora-envelope-goals`.

source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01.md

### aurora-document-diegesis

- Caso: O Último Brinde do Hotel Aurora.
- Fonte: [INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md](../../../docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md).
- Fatos preservados: a fonte registra que informações corretas estavam no documento errado e lista recipientes documentais que soavam artificiais.
- Inferência registrada: o recipiente documental pode prejudicar diegese mesmo quando a informação é correta.
- Lacunas: data/hora real do refinamento, participantes, ratings e revalidação independente.
- Decisão: `example_only`, escopo `case_only`.
- Não generalização: o exemplo ilustra um problema real do Hotel Aurora, mas não prova recorrência global.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/aurora-document-diegesis`.

source_documents:
- docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md

### canonical-visual-build-blocked

- Caso: baseline visual dos canônicos.
- Fonte: [BASELINE_VISUAL_2_0_CANONICOS.md](../../../docs/baselines/BASELINE_VISUAL_2_0_CANONICOS.md).
- Fatos preservados: a execução tinha Playwright Python disponível, mas browser Chromium indisponível; os builds não geraram PDFs, manifest ou print manifest.
- Inferência registrada: baseline visual real continua pendente e HTML debug parcial não substitui PDF real.
- Lacunas: horário real de cada comando e revisão visual de PDFs, porque os PDFs não foram gerados.
- Decisão: `regression_test`, escopo `technical`, implementação `proposed`.
- Não generalização: a fonte registra limitação de ambiente, não falha permanente do renderer nem regra editorial global.
- Validação: `python -m scripts.learning_ledger validate --ledger examples/learning/retrospective/canonical-visual-build-blocked`.

source_documents:
- docs/baselines/BASELINE_VISUAL_2_0_CANONICOS.md

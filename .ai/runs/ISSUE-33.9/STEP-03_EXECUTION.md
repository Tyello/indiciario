# ISSUE-33.9 STEP-03 — Decisão de prosseguimento

**Classificação de entrada (STEP-02):** PARCIAL.

## Análise

O modelo reconheceu a existência do produto comercial e a premissa geral do
caso "Uma Noite Sem Flores" (via busca na web habilitada na interface usada
na sonda), mas não confirmou culpado nem método — negou ter fonte confiável
para a solução.

Isso não é CONTAMINADO (spec: "acerta culpado/método"). A regra de STEP-03
para PARCIAL é objetiva: "registrar e liberar STEP-04" — sem exigir decisão
de anonimização ou limite-superior, que só se aplica ao caso CONTAMINADO.

Ressalva já registrada em STEP-02: `generator/anthropic_provider.py` (usado
no STEP-04 real) não habilita `tools`/busca na web — o vetor de
contaminação observado na sonda (busca ativa achando resumo de enredo) não
se repete na medição real. A medição do STEP-04 roda sob risco de
contaminação de premissa (não de solução), que é aceitável para o objetivo
de calibração do estimador de dificuldade — o que a spec quer medir é se o
solver consegue reconstruir a cadeia dedutiva a partir do bundle, não se ele
"nunca ouviu falar do produto".

## Decisão

**Prosseguir para STEP-04 sem anonimização adicional do bundle.**

Motivo: PARCIAL sem confirmação de culpado/método não atinge o limiar de
CONTAMINADO definido na spec; a via de contaminação observada (busca web)
está mecanicamente fechada no provider real (`AnthropicProvider` sem
`tools`). Não há decisão de esforço extra do Marcelo a tomar aqui — a regra
objetiva da spec para PARCIAL já resolve o caso.

## Critério de aceite

- [x] Decisão registrada (prosseguir, sem anonimização).
- [x] Justificativa ligada à classificação real de STEP-02 (PARCIAL) e à
      ausência de `tools`/busca no provider real.
- [x] STEP-04 liberado para o Marcelo.

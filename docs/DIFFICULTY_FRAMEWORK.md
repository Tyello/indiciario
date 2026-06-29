# Framework de dificuldade editorial do Indiciário

Este documento calibra a dificuldade editorial dos próximos casos do Indiciário. Os números abaixo são **régua editorial**, não regra rígida: um caso pode sair da faixa se playtest, baseline visual e revisão editorial justificarem a decisão.

Fontes usadas: `docs/ESTADO_ATUAL.md`, `docs/DIRETRIZES_EDITORIAIS.md`, `docs/ANTI_OBVIEDADE.md`, `docs/CASE_DESIGN_PIPELINE.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`, `docs/playtests/` e as faixas heurísticas existentes em `generator/playtest_metrics.py`.

Canônicos de referência:

- **Iniciante:** *O Desvio da Reserva Mirante* — clareza, baixa carga cognitiva e mais handholding estrutural.
- **Intermediário:** *O Último Brinde do Hotel Aurora* — recontextualização em E2, maior densidade textual, orientação espacial sem mapa e solução que exige articulação do grupo.

> Decisão consolidada: **Hotel Aurora permanece sem mapa**. Não usar este framework para reabrir essa decisão sem evidência nova.

## Tabela de calibração

| Nível | Quantidade aproximada de documentos | Número de suspeitos | Contratos/evidências obrigatórias | Tempo esperado | Tipo de ambiguidade | Papel do E1 | Papel do E2 | Handholding aceitável |
|---|---:|---:|---:|---|---|---|---|---|
| Iniciante | 8–10 | até 4 | até 2 contratos obrigatórios | 45–70 min | Ambiguidade local e controlada; poucos cruzamentos simultâneos | Apresentar pergunta pública, orientar leitura inicial e produzir hipótese parcial clara | Confirmar/recontextualizar com baixa carga inferencial | Alto: nomes podem aparecer em logs quando não entregam ação criminosa; códigos explicados; dicas mais diretas |
| Intermediário | 11–18 | até 6 | até 5 contratos obrigatórios | 75–110 min | Ambiguidade por cronologia, ausência, versões contraditórias e descarte de falso suspeito | Levantar contradição produtiva sem pedir culpado ou motivo completo | Recontextualizar E1 com consequência atual, motivo concreto ou documento original | Médio: códigos operacionais, glossário ou tradução separada; dicas em camadas; orientação sem checklist de solução |
| Avançado | 19–24 | até 7 | até 8 contratos obrigatórios | 110–150 min | Ambiguidade sistêmica com múltiplas cadeias e confirmação independente mais distante | Isolar eixo investigativo e falso padrão inicial | Virar leitura do E1 e exigir síntese entre documentos de naturezas diferentes | Baixo-médio: pistas brutas, tradução parcial, dicas menos prescritivas |
| Especialista | 25–30 | até 8 | até 10 contratos obrigatórios | 150–210 min | Ambiguidade acumulativa; múltiplas hipóteses plausíveis e descartes tardios | Mapear campo de investigação e criar pressão sem fechamento | Reorganizar a teoria do caso; pode exigir revisão de documentos anteriores | Baixo: facilitação robusta, mas documentos com pouca explicação interna |
| Mestre | 31+ | até 10 | até 12 contratos obrigatórios | 210+ min ou múltiplas sessões | Ambiguidade estrutural; solução depende de cadeia longa, prioridades e releituras | Abrir várias linhas de investigação sem resolver a tese central | Mudar tese, peso de evidências ou escopo do conflito | Muito baixo nos documentos; alto apenas no guia do facilitador e em dicas opcionais bem calibradas |

## Métricas reais dos casos e exceções

Métricas computadas diretamente dos blueprints (`sum(len(str(doc["conteudo"])))` para densidade e contagem de `documentos`):

| Caso | Arquivo | Documentos | Densidade (chars) | Dificuldade declarada | Envelopes | Dificuldade estimada (pós-fix ISSUE-30.7) |
|---|---|---:|---:|---|---|---|
| Mirante | `examples/caso_canonico_iniciante.json` | 20 | 36.568 | Iniciante | E1, E2 | ≤ intermediário |
| Iniciante B | `examples/caso_canonico_iniciante_b.json` | 9 | 12.981 | Iniciante | E1 | iniciante |
| Aurora | `examples/caso_canonico_intermediario.json` | 17 | 26.464 | Intermediário | E1, E2 | intermediário |
| Fintech | `examples/caso_fintech.json` | 16 | 29.647 | Avançado | E1, E2 | avançado |

**Mirante é exceção histórica, não referência métrica do nível Iniciante.** O Mirante foi concebido como caso Intermediário e rebaixado a Iniciante por decisão editorial (simplicidade da história, facilidade de resolução, confirmação pelo primeiro playtest). Por isso seu volume documental (20 docs / 36.568 chars) fica acima da faixa esperada de Iniciante (8–10 docs na tabela de calibração). Não usar o Mirante para calibrar limites métricos de Iniciante — usar o **Iniciante B** (9 docs / 12.981 chars), que está dentro da faixa.

**Contagem de documentos não classifica dificuldade de forma confiável.** A tabela acima mostra o problema diretamente: Mirante tem 20 documentos e é Iniciante; Fintech tem 16 documentos e é Avançado. Volume documental por si só não separa os níveis. O que separa os níveis, na prática observada:

- densidade de texto por documento (caracteres por documento, não só contagem total);
- ambiguidade e quantidade de cruzamentos simultâneos exigidos;
- findings de evidência (cadeias órfãs, suporte por conclusão);
- papel do E2 (confirmação simples vs. recontextualização forte vs. síntese entre documentos de naturezas diferentes).

Qualquer critério automatizado de dificuldade (ex.: Gate Evaluator de canonização) deve tratar contagem de documentos e número de envelopes como **sinal informativo**, não como critério duro de aprovação/rejeição.

`estimate_difficulty` em `generator/playtest_metrics.py` implementa esse princípio desde ISSUE-30.7: profundidade da cadeia de solução (`clue_graph` depth), densidade textual, ambiguidade real e papel do E2 são os sinais primários; contagem de documentos e suspeitos são sinal informativo secundário que nunca domina a classificação sozinho.

## Notas editoriais por eixo

### Quantidade de documentos

A faixa de documentos mede carga de leitura, não qualidade. Documento curto, visual e fácil pode pesar menos que depoimento longo; documento técnico sem glossário pode pesar mais que sua contagem sugere.

### Suspeitos

Contar suspeitos pela função de mesa: personagens com suspeita aparente, pressão ou oportunidade que o grupo realmente precisa considerar. Figurantes sem hipótese plausível não devem inflar dificuldade.

### Contratos/evidências obrigatórias

Contratos obrigatórios devem representar passos reais de solução. Se um contrato não muda hipótese, não recontextualiza documento, não confirma independente nem descarta alternativa, ele provavelmente é excesso de modelagem.

### Tempo esperado

O tempo esperado deve considerar leitura em voz alta, discussão, montagem de hipótese, uso de dicas e pausas do facilitador. Playtest real prevalece sobre estimativa heurística.

### Tipo de ambiguidade

Ambiguidade boa nasce de fatos parciais plausíveis. Ambiguidade ruim nasce de falta de objetivo, documento artificial, lacuna injusta ou red herring sem descarte.

### Papel do E1

E1 não deve pedir solução final. Ele deve criar pergunta parcial, suspeita inicial plausível, tensão ou recontextualização inicial suficiente para justificar avanço.

### Papel do E2

E2 deve recontextualizar algo do E1. Não deve apenas confirmar o que o grupo já sabia; precisa adicionar motivo atual, consequência concreta, versão original, descarte justo ou cronologia que muda a leitura.

### Handholding

Handholding aceitável depende do local:

- **Documentos de jogador:** apenas fatos brutos, estrutura e clareza diegética.
- **Dicas contextuais:** podem orientar ação mental e tipo de cruzamento, sem listar gabarito.
- **Guia do facilitador:** pode explicar cadeia completa, códigos, documentos relacionados, descarte de hipóteses e condução.

## Uso recomendado

1. Escolha a dificuldade antes de escrever documentos finais.
2. Compare premissa, mentira aparente e curva de suspeita com o nível pretendido.
3. Planeje E1 e E2 antes de multiplicar documentos.
4. Rode validações automáticas e leia os relatórios como sinais editoriais, não como substituto de playtest.
5. Se o playtest contradizer a régua, registre a evidência e ajuste a régua do caso, não apenas a contagem de documentos.

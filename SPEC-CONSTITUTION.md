# SPEC-CONSTITUTION — Indiciário

Princípios inegociáveis herdados por toda spec deste repositório. O spec-kit lê este arquivo antes de escrever qualquer spec T2/T3. Alterações aqui exigem decisão explícita do mantenedor — nenhum executor ou resolvedor pode flexibilizar estas regras para "destravar" uma etapa.

## 1. Contratos de dados (JSON é a fronteira sagrada)

- Todo blueprint de caso e todo artefato intermediário do pipeline é JSON validado por schema. Nenhuma etapa produz JSON "informal": se o schema não existe, criar o schema É parte da etapa.
- Schemas vivem versionados no repo, junto do código que os consome. Mudança de schema é sempre etapa própria na spec, nunca efeito colateral.
- Saída de LLM nunca é confiada crua, seja local ou cloud: todo consumo de output de modelo passa por parse + validação de schema + tratamento de falha explícito (retry ou rejeição registrada). "O modelo geralmente responde certo" não é contrato.
- Campos de texto narrativo do jogo são sempre em português brasileiro; chaves e identificadores de schema, sempre em inglês. Não misturar.

## 2. TDD como critério executável

- Fluxo test-first: em specs T2/T3, o plano de testes é escrito antes das etapas de implementação e os testes são o critério de aceitação primário. "Passa na validação de schema" complementa, não substitui, testes de comportamento.
- Todo bug corrigido ganha antes um teste que o reproduz (variante T1-bugfix obrigatória para correções).
- Testes de geração via LLM validam propriedades estruturais (schema, campos obrigatórios, consistência interna do caso), nunca igualdade exata de texto gerado — saída de modelo é não-determinística por natureza.

## 3. Uso de LLM no pipeline

- A atribuição de modelo por papel do pipeline (qual modelo orquestra, executa, revisa) vive em UM ponto de configuração versionado no repo. Nenhuma etapa hardcoda nome de modelo em código de orquestração; trocar de provedor ou modelo é mudança de configuração, não de código.
- Prompts enviados aos modelos são artefatos versionados (arquivos no repo), nunca strings embutidas em código de orquestração.
- Toda chamada de LLM tem tratamento explícito de falha (timeout, erro de API, resposta fora do schema): retry com limite ou rejeição registrada. Nenhuma etapa assume que a chamada sempre responde.
- Chamadas de LLM têm custo por token: etapas não reenviam contexto que o destinatário não precisa, e transformações que podem ser código determinístico não viram chamada de modelo.

## 4. Pipeline multiagente

- Papéis orquestrador/executor/revisor têm fronteiras rígidas: executor não decide, revisor não implementa, orquestrador não gera conteúdo final. Etapa que mistura papéis é defeito de spec.
- Toda passagem de dados entre agentes é JSON estruturado (ver princípio 1), nunca prosa livre a ser reinterpretada.
- Falha de agente é sempre registrada com entrada + saída + motivo, para permitir replay e futura curadoria de dataset de fine-tuning (LoRA sobre saídas validadas é caminho planejado — não descartar dados de execução válidos).

## 5. Higiene de execução (regras para o executor Haiku)

- Ambiente: Windows. Comandos de validação em specs devem funcionar no shell do projeto; não assumir utilitários unix-only sem verificação prévia.
- Nenhuma etapa toca `opencode.json`, configurações de Ollama ou definição de modelos como efeito colateral — só como etapa explícita e isolada.
- Determinismo primeiro: lógica que pode ser código determinístico não vira chamada de LLM. Modelo é usado onde há geração criativa ou julgamento, não para transformação mecânica de dados.
- Suíte de testes completa verde é critério de aceitação global implícito de toda spec T2/T3, mesmo quando não repetido por escrito.

---

*Manutenção: revisar este arquivo quando (a) o stack de modelos mudar, (b) um mesmo tipo de escalação ocorrer 2+ vezes por conflito de convenção não coberta aqui, ou (c) o pipeline ganhar novo papel de agente.*

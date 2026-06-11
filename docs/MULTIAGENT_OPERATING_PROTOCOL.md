# Protocolo operacional multiagente manual-first

## 1. Propósito

Este protocolo define como uma criação ou revisão multiagente de casos do Indiciário deve ser conduzida em modo **manual-first**, antes de qualquer automação de orquestração, providers, schemas executáveis ou CLIs específicas.

Ele estabelece:

- como uma criação multiagente é conduzida, desde a concepção inicial até o aprendizado pós-playtest;
- quem pode criar, revisar, resolver às cegas, avaliar gates, moderar interações ou controlar o fluxo;
- quando uma etapa pode avançar para a próxima;
- quando uma etapa deve retornar para correção ou revisão anterior;
- quais decisões permanecem humanas, especialmente as decisões editoriais sobre diversão, ritmo, emoção, justiça percebida e prioridade de produto;
- como manter separação de responsabilidades entre autoria, crítica, resolução cega, avaliação de gate, moderação e governança;
- como preservar o pipeline atual do Indiciário enquanto a camada multiagente é adotada de forma incremental.

> Este protocolo não substitui o pipeline oficial atual e não torna o sistema multiagente obrigatório para builds existentes.

O fluxo oficial continua sendo:

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library / templates
→ Build Package
→ Baseline visual real
→ Playtest
→ Ajustes finos
```

A camada multiagente descrita aqui existe para melhorar rastreabilidade editorial, revisão independente, cegueira operacional e aprendizado estruturado. Ela não autoriza alterar os canônicos, schemas, validator, renderer, package builder, templates, PDFs ou CI sem tarefa específica.

### Convenções normativas

Neste documento:

- **deve** indica regra obrigatória para uma rodada que declare seguir este protocolo;
- **não deve** indica prática proibida, salvo exceção registrada conforme o procedimento de desvios;
- **pode** indica possibilidade operacional permitida, mas não exigida;
- **recomendado** indica prática preferencial quando não houver restrição de escopo, segurança de contexto ou custo;
- regras deste protocolo são normativas para o processo manual-first, mas não criam validação automática, schema executável ou obrigação para builds existentes.

## 2. Princípios fundamentais

### Manual-first

- Nenhuma chamada automática a LLM é necessária para executar este protocolo.
- Agentes podem ser executados manualmente em sessões separadas, por pessoas diferentes ou por LLMs operadas individualmente.
- Outputs são recebidos como artefatos versionáveis, revisáveis e comparáveis.
- Providers futuros, adapters de modelo, workers automáticos e integrações com APIs não fazem parte deste protocolo inicial.
- A ausência de automação não reduz o rigor: cada etapa ainda precisa registrar entrada, saída, papel exercido, decisão e motivo de avanço ou retorno.

### Separação de responsabilidades

- Autor cria, estrutura ou corrige artefatos.
- Revisor critica o artefato recebido e registra findings, sem alterar silenciosamente o material revisado.
- Blind Solver tenta resolver usando apenas o material autorizado para aquele momento da experiência do jogador.
- Gate Evaluator compara outputs congelados com expectativas privadas autorizadas, sem participar da resolução cega.
- Moderador organiza a conversa, controla turnos e evita vazamento de informação, mas não decide a solução.
- Operador humano controla o fluxo, escolhe quando avançar, pausar, retornar ou encerrar uma rodada.
- Nenhum papel acumula autoridade total sobre criação, crítica, aprovação e decisão final.

### Cegueira por contexto

- Agentes cegos recebem somente material autorizado para o seu papel e para a etapa em execução.
- “Finja que não sabe” não é isolamento suficiente.
- A cegueira deve ser tratada como obrigação operacional: preparar contexto separado, retirar gabaritos, remover metadados reveladores e evitar nomes de arquivos que entreguem solução.
- Detalhes técnicos do Context Firewall serão definidos em tarefa própria posterior.
- Este protocolo apenas estabelece a obrigação de isolamento: quem opera a rodada precisa garantir que o agente cego não recebeu solução, Bíblia narrativa privada, verdade real, contratos de evidência, guia do facilitador, envelopes futuros ou classificações de pista.

### Imutabilidade da revisão

- Um revisor não altera silenciosamente o artefato avaliado.
- Outputs originais são preservados como referência de revisão.
- Correções geram nova versão, novo patch ou novo artefato derivado, conforme o fluxo manual definido para a rodada.
- Findings devem ser rastreáveis até o artefato e a etapa onde foram observados.
- Uma aprovação não apaga findings anteriores: ela apenas registra que eles foram aceitos como resolvidos, mitigados, não aplicáveis ou conscientemente adiados.

### Playtest humano soberano

- Agentes ajudam a detectar riscos lógicos, ambiguidades, dependências frágeis, vazamento de solução, excesso de interpretação autoral e falhas de progressão.
- Agentes não certificam diversão, emoção, ritmo de mesa, fricção física do material impresso ou justiça percebida por pessoas reais.
- Mesa investigativa simulada não substitui playtest humano.
- A decisão editorial final permanece humana, especialmente quando houver conflito entre eficiência lógica e experiência de grupo.

### Reversibilidade

- O sistema multiagente não pode quebrar o pipeline atual.
- Um caso existente continua podendo seguir o fluxo oficial sem passar por todas as etapas multiagente futuras.
- Novas etapas devem ser adotadas incrementalmente, com rollback claro para o ponto correto.
- Nenhuma etapa multiagente deve exigir internet, aplicativo externo, QR code obrigatório, banco de dados, dashboard, marketplace ou geração automática por IA.
- Se uma etapa nova não melhorar solvabilidade, clareza, revisão, rastreabilidade ou aprendizado, ela deve ser removida, adiada ou simplificada.

## 3. Glossário operacional

### Skill

Procedimento operacional reutilizável que orienta como um agente deve executar uma classe de tarefa. Uma skill descreve passos, cuidados, critérios e validações. Ela não é, por si só, um papel nem um executor.

### Papel de agente

Responsabilidade exercida em uma execução específica. Um mesmo executor pode assumir papéis diferentes em rodadas diferentes, desde que a separação de contexto seja preservada.

### Agente

Executor humano ou LLM que assume um papel durante uma etapa. O termo não implica autonomia total, acesso irrestrito nem permissão para decidir qualidade editorial sozinho.

### Agente autor

Agente que cria, reestrutura ou corrige um artefato. Pode conhecer a solução quando isso for necessário ao trabalho autoral, mas não deve certificar sozinho a qualidade final do próprio material.

### Agente revisor

Agente que avalia um artefato, procura falhas e registra findings. Pode ou não conhecer a solução, conforme o tipo de revisão, mas não altera diretamente o artefato revisado.

### Agente cego

Agente que recebe apenas o contexto autorizado para simular uma perspectiva limitada. Pode atuar como Blind Solver, participante de mesa simulada, crítico adversarial cego ou leitor de envelope.

### Blind Solver

Agente cego que tenta resolver uma pergunta, envelope ou recorte do caso sem acesso à solução, gabarito, guia do facilitador, Bíblia narrativa privada ou metadados reveladores. Sua função é demonstrar o que é inferível a partir do material disponível.

### Gate Evaluator

Agente ou pessoa autorizada a comparar um output congelado com expectativas privadas da etapa, como solução esperada, critérios de avanço ou riscos conhecidos. Não participa da tentativa cega que está avaliando.

### Moderador

Pessoa ou agente que conduz uma conversa multiagente, controla turnos, resume impasses, solicita explicitação de evidências e evita vazamento de contexto. O moderador não precisa conhecer a solução e, em mesas simuladas cegas, não deve conhecê-la.

### Crítico adversarial

Agente encarregado de testar a robustez de uma hipótese, apontar alternativas plausíveis, expor saltos lógicos e procurar contradições. Pode operar com ou sem solução, mas essa condição precisa ser declarada antes da rodada.

### Operador humano

Pessoa responsável pela governança da rodada: preparar materiais, distribuir contexto, registrar decisões, aprovar avanço ou retorno, resolver conflitos e preservar o alinhamento com o pipeline oficial.

### Artefato

Qualquer saída versionável usada no processo: brief, premissa, Bíblia narrativa, arquitetura do mistério, planejamento de envelopes, planejamento documental, Blueprint, Case Kernel, Case Review, relatório de Blind Solver, relatório de gate, pacote renderizado, observação de playtest ou síntese de aprendizado.

### Etapa

Unidade operacional do pipeline com objetivo, entradas, papel responsável, saída esperada e critério de avanço ou retorno. Uma etapa pode ser manual, parcialmente assistida por LLM ou, no futuro, automatizada.

### Run

Execução concreta de uma etapa por um ou mais agentes. Neste protocolo, o termo é operacional e não define formato obrigatório, identificador, manifesto ou contrato executável.

### Bundle

Conjunto preparado de materiais entregues a um agente para uma etapa. Em contexto cego, o bundle deve conter somente o que o papel pode conhecer. Neste protocolo, o termo é descritivo e não define estrutura de diretórios, manifesto ou schema.

### Gate

Ponto de decisão em que uma etapa recebe um dos quatro estados canônicos: `PASS`, `REVISE`, `BLOCK` ou `INCONCLUSIVE`. Um gate deve considerar evidência, findings, risco editorial, julgamento humano e etapa correta de rollback quando aplicável.

### Finding

Observação rastreável de problema, risco, inconsistência, lacuna, ambiguidade, vazamento, quebra de progressão ou oportunidade de melhoria. Um finding deve indicar o artefato afetado, o motivo e a severidade operacional esperada.

### Rollback

Retorno para uma etapa anterior adequada, em vez de remendar tardiamente o sintoma. O rollback deve mirar a origem provável do problema: premissa, narrativa, arquitetura, envelope, documento, visual, pacote ou aprendizado.

### Output congelado

Saída preservada sem edição após uma execução, especialmente quando será avaliada por Gate Evaluator ou comparada com expectativas privadas. Pode ser copiada para gerar versão corrigida, mas o original permanece disponível para rastreabilidade.

### Lineage

Relação histórica entre artefatos, versões, findings, decisões e correções. O objetivo é saber de onde uma decisão veio, que problema tentou resolver e qual etapa a originou, sem exigir ainda um formato técnico obrigatório.

### Playtest

Teste com pessoas reais jogando ou facilitando o caso. Mede compreensão, engajamento, ritmo, diversão, uso de dicas, fricção física, hipóteses erradas e justiça percebida. Não é substituído por revisão automatizada ou mesa simulada.

### Learning Loop

Processo de transformar observações de playtest em findings, hipóteses causais, correções localizadas, revalidação e, apenas quando houver recorrência ou justificativa forte, aprendizado editorial generalizável.

### Orquestrador

Mecanismo futuro que prepara contexto, registra runs e controla gates. O orquestrador não deve decidir sozinho a qualidade editorial do caso, não substitui o operador humano e não deve fundir autoria, revisão, resolução cega e aprovação em uma autoridade única.

## 4. Autoridade e responsabilidade

| Papel | Pode conhecer solução? | Pode alterar artefato? | Pode aprovar gate? | Responsabilidade |
|---|---:|---:|---:|---|
| Autor | Sim, quando necessário | Sim, por nova versão | Não sozinho | Criar, estruturar ou corrigir artefatos |
| Revisor | Depende do tipo de revisão | Não diretamente | Pode recomendar | Encontrar falhas, lacunas, riscos e contradições |
| Blind Solver | Não | Não | Não | Tentar resolver com material autorizado e registrar raciocínio |
| Gate Evaluator | Sim, quando autorizado | Não | Sim, dentro do gate designado | Comparar output congelado com expectativa privada |
| Moderador | Não, salvo rodada não cega explicitamente definida | Não | Não | Conduzir interação, preservar escopo e evitar vazamentos |
| Crítico adversarial | Depende da rodada | Não | Pode recomendar | Derrubar hipóteses frágeis e expor alternativas plausíveis |
| Operador humano | Conforme necessidade | Controla fluxo e solicita novas versões | Sim | Governança, decisão final, rollback e alinhamento editorial |
| Orquestrador futuro | Apenas o mínimo necessário por papel | Não por autoridade própria | Não sozinho | Preparar contexto, registrar execução e organizar gates |

Regras de autoridade:

- Nenhum agente automatizado tem autoridade absoluta para aprovar qualidade editorial.
- Quem cria não aprova sozinho o que criou.
- Quem resolve às cegas não deve receber solução depois para “corrigir” seu próprio raciocínio no mesmo output.
- Quem avalia com expectativa privada não participa da rodada cega avaliada.
- O operador humano pode encerrar, repetir, dividir ou reverter uma etapa quando houver risco de vazamento, confusão de papel ou perda de rastreabilidade.

### Responsabilidades consolidadas do operador humano

O operador humano deve:

- selecionar a etapa, o objetivo e a skill operacional antes da rodada;
- definir papéis e confirmar quem pode conhecer material privado;
- preparar ou revisar o conjunto de materiais autorizado para cada papel;
- preservar outputs congelados e registrar a decisão de gate;
- decidir avanço, retorno, pausa, repetição ou encerramento;
- impedir que um agente automatizado acumule autoria, revisão, resolução cega e aprovação;
- registrar exceções, desvios, limitações e riscos residuais;
- manter o fluxo alinhado ao pipeline oficial e às prioridades atuais do projeto.

O operador humano pode delegar execução e análise, mas não deve delegar a responsabilidade final de governança editorial da rodada.

O operador humano não deve:

- aprovar sozinho um artefato quando também atuou como autor principal;
- reclassificar uma rodada contaminada como revisão cega válida;
- transformar recomendação de agente em decisão editorial automática;
- ocultar findings críticos para permitir avanço;
- usar exceção de processo para contornar playtest humano, baseline visual real ou revisão obrigatória;
- iniciar adoção técnica futura sem escopo próprio e evidência mínima de benefício.

### Ciclo autor–revisor

O ciclo mínimo recomendado para qualquer artefato novo ou corrigido é:

```text
Autor produz versão
→ output é congelado para revisão
→ Revisor registra findings sem editar o artefato
→ Operador humano decide gate
→ Autor cria nova versão quando houver retorno
→ revisão é repetida somente no escopo necessário
```

Regras do ciclo:

- o autor deve responder a findings por nova versão, nota de mitigação ou justificativa de não alteração;
- o revisor deve apontar problema, evidência e impacto, evitando reescrever silenciosamente o material;
- o operador humano deve separar findings críticos, recomendações e preferências editoriais;
- uma nova versão não apaga o output revisado anteriormente;
- ciclos sucessivos devem buscar a menor correção coerente, não expansão automática de escopo.

Estados manuais de finding no ciclo autor–revisor:

- **aberto**: finding registrado e ainda sem resposta do autor;
- **em correção**: autor aceitou o finding e está produzindo nova versão;
- **resolvido**: nova versão removeu o problema e o revisor ou operador confirmou;
- **mitigado**: risco permanece, mas foi reduzido e aceito conscientemente no gate;
- **não aplicável**: revisão concluiu que o finding não se aplica ao escopo ou artefato;
- **adiado**: finding real foi postergado com responsável, motivo e etapa futura de revalidação;
- **bloqueador**: finding impede `PASS` enquanto não houver correção ou rollback.

Esses estados são vocabulário operacional manual, não schema executável. Finding bloqueador deve levar o gate a `REVISE` ou `BLOCK`, conforme severidade e etapa de origem.

## 5. Pipeline operacional

A camada multiagente futura deve ser entendida como expansão incremental antes, durante e depois do fluxo oficial, não como substituição imediata:

```text
Brief
→ Laboratório de premissas
→ Bíblia narrativa
→ Arquitetura do mistério
→ Planejamento de envelopes
→ Planejamento documental
→ Produção documental
→ Blueprint
→ Case Kernel
→ Case Review
→ Blind Review lógico
→ Visual Library/templates
→ Build Package
→ Blind Review renderizado
→ Baseline visual
→ Playtest humano
→ Learning Loop
```

### Unidade operacional de etapa

Cada etapa manual-first deve ser tratada como uma unidade operacional pequena o suficiente para revisão independente. Antes de iniciar, o operador humano deve conseguir declarar:

- objetivo da etapa;
- entradas autorizadas;
- materiais privados proibidos para papéis cegos;
- visibilidade da rodada: pública, privada, cega ou híbrida;
- papel executor;
- papel revisor, avaliador ou gate esperado;
- saída esperada;
- formato livre esperado da saída, quando necessário, sem impor schema executável;
- critérios de avanço;
- critérios de retorno e etapa provável de rollback;
- restrições de cegueira, se houver;
- estado de gate esperado ao final: `PASS`, `REVISE`, `BLOCK` ou `INCONCLUSIVE`;
- riscos conhecidos e decisão humana necessária.

Ao encerrar, a etapa deve produzir uma decisão explícita, mesmo que seja `INCONCLUSIVE`. Uma etapa não deve misturar, na mesma execução sem registro, criação de conteúdo, revisão crítica, resolução cega e aprovação de gate. Se isso acontecer por necessidade operacional, a rodada deve ser marcada como desvio e não deve ser usada como evidência cega.

### 5.1 Brief

Define intenção, público, régua de dificuldade, restrições offline-first, formato esperado, tema, limites editoriais e promessa de experiência. Avança quando o operador humano consegue explicar por que o caso deve existir e qual experiência pretende entregar.

Retorna quando a proposta depende de app, internet, QR code obrigatório, solução externa, tema incompatível ou ambição maior que a capacidade atual de revisão e playtest.

### 5.2 Laboratório de premissas

Explora alternativas de mistério, conflitos, ambientes, mecânicas investigativas e riscos de repetição dos canônicos. Avança quando há premissa promissora, distinta o suficiente, jogável em mesa e compatível com documentos físicos.

Retorna quando a premissa só funciona como conto, exige conhecimento externo, depende de coincidência excessiva ou repete mecanicamente arquitetura já usada.

### 5.3 Bíblia narrativa

Consolida verdade privada, personagens, linha do tempo, motivações, relações e limites de revelação. É material privado de autoria e revisão não cega, não documento de jogador.

Avança quando a verdade do caso é coerente e consegue sustentar documentos diegéticos com evidência bruta. Retorna quando a solução depende de intenção autoral não evidenciada, contradição temporal ou motivação invisível.

### 5.4 Arquitetura do mistério

Define pergunta investigativa, solução, hipóteses plausíveis, evidências necessárias, falsos caminhos justos e dependências entre pistas. Avança quando a solução pode ser inferida por cruzamento de evidências, não por gabarito disfarçado.

Retorna quando há caminho único frágil, pista indispensável escondida demais, red herring injusto ou dedução baseada em conhecimento externo. Hipóteses alternativas plausíveis são desejáveis para sustentar investigação, mas devem ser refutáveis por evidência disponível; o problema ocorre quando a alternativa errada fica tão ou mais sustentada que a solução correta, ou quando não há caminho evidencial para distingui-las.

### 5.5 Planejamento de envelopes

Define progressão de revelação, critérios de abertura, função de cada envelope e carga cognitiva por etapa. Avança quando cada envelope tem papel claro e não entrega a solução por voz do autor.

Retorna quando envelope serve apenas para despejar explicação, quando o próximo passo depende de permissão ambígua ou quando a progressão substitui investigação por instrução.

### 5.6 Planejamento documental

Lista documentos previstos, função diegética, evidência bruta que cada um contém, risco de interpretação autoral, dependências e relação com dicas ou guia do facilitador. Avança quando cada documento parece documento real do mundo do caso.

Retorna quando um documento comercial vira síntese de puzzle, quando texto de jogador explica o raciocínio esperado ou quando o material só existe para confirmar gabarito.

### 5.7 Produção documental

Redige os documentos de jogador, mantendo voz diegética, evidência bruta e plausibilidade material. Relatórios, dicas e guia do facilitador podem explicar; documentos de jogador não.

Avança quando os documentos sustentam investigação, não vazam solução indevida e podem entrar no Blueprint sem quebrar o fluxo atual.

### 5.8 Blueprint

Converte a produção editorial para a representação já esperada pelo pipeline atual. Avança quando o Blueprint pode ser validado pelo fluxo existente e preserva a intenção editorial aprovada.

Retorna quando a conversão para Blueprint altera progressão, mistura material privado com material de jogador ou força mudança incompatível com schema atual.

### 5.9 Case Kernel

Estrutura a visão lógica do caso para análise de perguntas, fatos, documentos, envelopes e riscos. Avança quando o Kernel permite revisar coerência sem substituir o julgamento editorial.

Retorna quando o Kernel revela lacunas que pertencem a arquitetura, envelope ou documento, em vez de serem tratadas como ajuste tardio.

### 5.10 Case Review

Aplica revisão estruturada sobre solvabilidade, progressão, clareza, dicas, documentos e riscos. Avança quando findings críticos foram resolvidos, aceitos conscientemente ou encaminhados para teste humano.

Retorna quando há quebra de dedução, vazamento de gabarito em documento de jogador, dica que substitui investigação ou contradição não mitigada.

### 5.11 Blind Review lógico

Blind Solvers recebem material lógico autorizado, sem solução ou metadados reveladores, e tentam resolver perguntas ou envelopes. Outputs são congelados antes de avaliação.

Avança quando o raciocínio cego encontra caminho justo ou quando dificuldades são entendidas e aceitas como parte da régua. Retorna quando a resolução exige chute, conhecimento externo, leitura de intenção autoral ou informação ainda não liberada.

### 5.12 Visual Library/templates

Seleciona ou prepara tratamento visual, templates, plantas e elementos procedurais compatíveis com o caso e com as regras visuais. Avança quando a camada visual serve legibilidade, impressão e verossimilhança, sem virar solução visual.

Retorna quando visual destaca culpado, marca área crítica, transforma mapa em diagrama de solução ou introduz dependência externa.

### 5.13 Build Package

Gera o pacote com os mecanismos existentes, respeitando separação física entre documentos de jogador, facilitador, dicas, printables e materiais apartados. Avança quando o build real é possível e não há resíduos técnicos ou quebra estrutural.

Retorna quando o pacote altera a experiência, mistura materiais privados, quebra impressão ou produz artefato que não pode ser revisado visualmente.

### 5.14 Blind Review renderizado

Blind Solvers avaliam PDFs ou materiais renderizados como jogadores, com acesso apenas ao que estaria disponível na mesa. A revisão considera leitura, ordem física, pistas visuais involuntárias, ambiguidade de abertura e uso de dicas.

Avança quando o pacote renderizado preserva a solvabilidade aprovada logicamente. Retorna quando a renderização corta texto, aproxima indevidamente materiais, vaza solução por layout ou torna evidência ilegível.

### 5.15 Baseline visual

Revisão visual real com Playwright/Chromium quando aplicável ao build, sem aceitar PDF fake como prova de qualidade. Avança quando o material impresso ou renderizado é legível, separado, coerente e sem falhas graves.

Retorna para template, renderização, pacote ou documento conforme a origem do problema visual.

### 5.16 Playtest humano

Pessoas reais jogam, facilitam ou observam o caso. O objetivo é medir compreensão, ritmo, fricção, diversão, emoção, justiça percebida, uso de dicas e hipóteses erradas.

Avança para ajustes finos quando os problemas são localizados e corrigíveis. Retorna para etapas anteriores quando o playtest revela falha estrutural de premissa, arquitetura, envelope ou documento.

### 5.17 Learning Loop

Organiza aprendizados pós-playtest em findings, hipóteses causais, correções, revalidação e decisões de generalização. Um aprendizado local não vira regra global automaticamente.

Avança quando há decisão explícita sobre o que corrigir agora, o que registrar para casos futuros e o que não generalizar.

## 6. Gates e critérios de avanço

Um gate é avaliado quando há evidência suficiente para decidir se a etapa cumpriu seu objetivo sem violar princípios do Indiciário. Em modo manual-first, o gate pode ser uma decisão registrada em Markdown, issue, comentário de PR ou relatório, desde que seja compreensível e rastreável.

### Estados formais de gate

Todo gate deve terminar em um dos quatro estados canônicos do PRD:

- **PASS**: a etapa pode avançar; findings críticos estão resolvidos, mitigados ou aceitos conscientemente, e o avanço não depende de inferência inexistente nem de vazamento;
- **REVISE**: há problema corrigível na etapa atual ou em etapa anterior; o gate deve indicar finding, responsável e etapa de rollback;
- **BLOCK**: há falha que impede avanço justo, compromete a integridade do mistério ou torna inválida a evidência produzida;
- **INCONCLUSIVE**: a execução não permite decisão confiável; requer nova rodada, contexto corrigido, revisor adequado, solver novo ou evidência adicional.

`PASS` pode registrar ressalvas, mas essas ressalvas não são um quinto estado. Vazamento de contexto deve resultar em `BLOCK` quando comprometer a integridade da rodada, ou `INCONCLUSIVE` quando apenas impedir decisão confiável. Um gate não deve ficar implícito. Se a rodada avançar sem registro, o operador humano deve registrar posteriormente que houve desvio de processo e qual risco foi aceito.

Critérios mínimos para avançar:

- a saída da etapa existe e está preservada;
- o papel executor e o papel avaliador estão identificados;
- findings críticos foram resolvidos, mitigados ou aceitos conscientemente;
- não houve vazamento de solução para agente cego;
- documentos de jogador preservam evidência bruta e não voz do autor;
- o fluxo continua offline-first e jogável sem app, internet ou QR code obrigatório;
- o operador humano entende o risco residual e decide avançar.

Critérios mínimos para retornar:

- solução depende de chute, conhecimento externo ou metadado;
- etapa posterior revela problema de etapa anterior;
- revisor encontrou contradição central não mitigada;
- Blind Solver não consegue formular hipótese justa com o material autorizado;
- Gate Evaluator identifica divergência entre output congelado e expectativa privada;
- playtest humano mostra fricção, tédio, injustiça percebida ou confusão estrutural;
- houve vazamento de contexto que invalida uma rodada cega.

## 7. Regras para revisão cega

- Preparar o contexto antes de iniciar a rodada; não confiar em instruções para ignorar informação já vista.
- Entregar somente documentos, perguntas, envelopes e ferramentas públicas disponíveis naquele ponto da experiência.
- Remover solução, Bíblia narrativa privada, verdade real, guia do facilitador, contratos de evidência e metadados reveladores.
- Congelar o output do Blind Solver antes de qualquer avaliação com expectativa privada.
- Separar a pessoa ou agente que resolveu às cegas de quem compara com a solução.
- Registrar hipóteses, evidências usadas, evidências ignoradas, pontos de confusão e momento em que o solver acha que poderia avançar.
- Invalidar ou repetir a rodada se houver vazamento de contexto relevante.

## 8. Regras para mesa investigativa simulada

A mesa simulada é uma ferramenta de diagnóstico, não um substituto de playtest humano.

Fluxo recomendado:

1. cada participante cego recebe o mesmo material autorizado;
2. cada participante produz hipótese individual congelada;
3. o moderador conduz uma conversa sem revelar solução;
4. o grupo explicita fatos, inferências, discordâncias e perguntas abertas;
5. um crítico adversarial tenta derrubar a hipótese coletiva;
6. o output coletivo é congelado;
7. um Gate Evaluator autorizado compara o resultado com expectativa privada.

A mesa deve retornar findings quando:

- participantes convergem por palpite sem evidência;
- uma hipótese errada parece mais bem sustentada que a correta;
- a conversa depende de conhecimento externo;
- o grupo pede dica para informação que deveria estar evidente;
- o moderador precisa explicar regra ou objetivo que o material deveria comunicar.

## 9. Rollback e versionamento editorial

Rollback deve corrigir a origem do problema, não apenas seu sintoma. Exemplos:

- problema de motivação retorna à Bíblia narrativa;
- problema de inferência retorna à arquitetura do mistério;
- problema de ordem de descoberta retorna ao planejamento de envelopes;
- documento que explica demais retorna ao planejamento ou produção documental;
- pista ilegível retorna a visual/templates ou Build Package;
- frustração de mesa pode retornar a envelope, dica, documento ou até premissa.

Regras:

- preservar o output original que recebeu finding;
- criar nova versão ou correção derivada;
- registrar o motivo do rollback;
- reexecutar apenas as etapas necessárias para recuperar confiança;
- não transformar correção local em regra global sem Learning Loop.

## 10. Decisões humanas preservadas

Permanecem humanas:

- aprovação final de premissa e tema;
- decisão de iniciar ou não um novo caso canônico;
- decisão de alterar dificuldade, quantidade de envelopes ou curva de revelação;
- julgamento de diversão, emoção, ritmo e justiça percebida;
- decisão de generalizar aprendizado de playtest;
- decisão de aceitar risco editorial residual;
- priorização entre baseline visual, playtest, ajustes finos e novas iniciativas.

Agentes podem recomendar, sintetizar, criticar e comparar. Eles não devem substituir a responsabilidade editorial humana.

## 11. Exceções e desvios

Exceções são permitidas apenas quando tornam a rodada mais segura, mais simples ou mais fiel ao estado real do projeto. Um desvio deve ser registrado quando qualquer regra operacional não puder ser seguida. Exceção não pode converter `BLOCK` em `PASS`, transformar vazamento em evidência cega válida nem dispensar decisão humana final.

Procedimento mínimo:

1. declarar qual regra não será seguida;
2. explicar o motivo do desvio;
3. registrar quem aprovou a exceção;
4. indicar risco editorial, risco de cegueira ou risco de rastreabilidade;
5. definir se o output ainda pode ser usado como evidência, recomendação ou apenas nota exploratória;
6. registrar o estado de gate compatível com o desvio;
7. planejar revalidação quando o desvio afetar solvabilidade, gate ou playtest.

Uma exceção não deve virar precedente automático. Para virar prática recorrente, precisa passar pelo Learning Loop ou por atualização documental explícita.

## 12. Critérios para adoção futura

Uma etapa, skill, automação, schema, CLI ou orquestrador futuro só deve ser adotado quando:

- preservar o pipeline oficial e a operação offline-first;
- reduzir risco real de erro editorial, vazamento, retrabalho ou perda de rastreabilidade;
- manter separação entre autoria, revisão, resolução cega e aprovação;
- produzir benefício observável em piloto, revisão ou playtest;
- não transformar playtest humano em etapa opcional;
- não iniciar itens P3, providers, RAG, ML, dashboard, banco de dados ou geração massiva sem decisão futura explícita;
- permitir rollback para o fluxo manual quando falhar;
- usar `PASS`, `REVISE`, `BLOCK` e `INCONCLUSIVE` como estados de gate;
- preservar outputs originais e findings rastreáveis;
- tiver escopo próprio, revisão própria e documentação própria.

Adoção futura deve ser incremental: primeiro procedimento manual claro, depois contrato conceitual, depois implementação pequena, depois piloto, e só então ampliação.

## 13. Limitações explícitas

Este protocolo tem limites deliberados:

- não prova que um caso é divertido;
- não garante solvabilidade sem playtest e revisão humana;
- não impede vazamento se o operador humano preparar contexto errado;
- não substitui o validator, o Case Kernel, o Case Review, o build real ou a baseline visual;
- não define segurança técnica do Context Firewall;
- não define formato de manifest, identificador, diretório, schema ou output automatizado;
- não resolve priorização de produto nem autoriza iniciar canônico Avançado;
- não transforma mesa simulada em evidência equivalente a pessoas reais jogando.

Essas limitações são parte da segurança do desenho manual-first: o protocolo orienta governança, mas não finge maturidade técnica ou validação editorial que ainda não existem.

## 14. Compatibilidade com o repositório atual

Este protocolo é deliberadamente documental. Ele não cria contratos executáveis, não define schemas, não exige diretórios novos de outputs e não muda comandos existentes.

Compatibilidades obrigatórias:

- o fluxo oficial existente permanece válido;
- `Blueprint`, `Case Kernel`, `Case Review`, `Build Package`, baseline visual real e playtest continuam como referências centrais;
- skills existentes continuam sendo procedimentos operacionais, não agentes autônomos;
- o validator, os scripts, o renderer e os casos canônicos não são alterados por este protocolo;
- qualquer implementação futura de Context Firewall, manifests, IDs, schemas, bundles técnicos, CLIs ou orquestrador deve ser tratada em issues próprias.

## 15. Anti-regras

Este protocolo não autoriza:

- automatizar providers de LLM nesta etapa;
- definir contratos executáveis de identificadores, manifests, outputs ou diretórios;
- substituir playtest humano por mesa simulada;
- tornar multiagente obrigatório para builds existentes;
- reabrir narrativa dos canônicos sem evidência de playtest ou tarefa explícita;
- misturar solução privada em material de jogador;
- transformar documento diegético em explicação do puzzle;
- criar dependência de internet, app, dashboard, banco de dados ou QR code obrigatório;
- conceder aprovação editorial final a agente automatizado.

## 16. Checklist manual-first por rodada

Antes da rodada:

- selecionar etapa e objetivo;
- escolher skill operacional adequada;
- definir papel de cada participante;
- preparar bundle ou conjunto de materiais autorizado;
- confirmar se a rodada é cega, não cega ou híbrida;
- remover contexto proibido para papéis cegos.

Durante a rodada:

- manter papéis separados;
- registrar dúvidas, hipóteses e findings;
- não editar silenciosamente output sob revisão;
- interromper se houver vazamento de solução;
- evitar decisões editoriais automáticas.

Depois da rodada:

- congelar output relevante;
- avaliar gate com papel apropriado;
- decidir avançar, retornar, pausar ou rejeitar;
- registrar motivo da decisão;
- criar nova versão quando houver correção;
- encaminhar aprendizados de playtest para o Learning Loop, sem generalização automática.

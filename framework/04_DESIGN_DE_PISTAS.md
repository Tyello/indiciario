# Design de Pistas, Red Herrings e Códigos

---

## 1. Matriz de pistas — criar antes de escrever qualquer documento

Antes de escrever os documentos finais, crie uma matriz interna com todas as pistas críticas.

| Pista | Documento onde aparece | O que sugere | O que realmente prova | Confirmação independente | Risco de ambiguidade | Emoção esperada |
|-------|----------------------|-------------|----------------------|------------------------|---------------------|----------------|
| Ex.: terminal N3 | Log de sistema | Origem da ação | Ação ocorreu dentro da sala N3 | Acesso físico à sala N3 | Médio | Cruzamento |

**Regra:** nenhuma pista crítica fica sem confirmação independente.

---

## 2. Pistas essenciais

São as pistas sem as quais o caso não fecha.

**Regras:**
- devem aparecer com clareza suficiente para leitura normal;
- devem ter pelo menos uma confirmação forte (outro documento prova o mesmo fato de forma independente);
- não podem depender de interpretação estética subjetiva (cor, fonte, posição visual);
- não devem estar escondidas em texto ilegível ou elemento decorativo;
- devem ser compreensíveis sem conhecimento externo ao dossiê.

### Regra de âncora de vínculo

Um vínculo entre duas entidades — pessoas, empresas, endereços, contas, veículos ou locais — é **documentalmente suficiente** quando pelo menos **dois** dos critérios abaixo aparecem em **documentos diferentes**:

| Critério | Exemplo |
|----------|---------|
| Mesmo responsável formal ou signatário | "Marina Salgado" assina dois contratos com empresas diferentes |
| Mesmo endereço, telefone ou domínio de e-mail | `@aresia.com` no cadastro e no extrato |
| Referência cruzada explícita | "indicado por", "representado por", "controlado por" |
| Mesmo protocolo, CNPJ ou conta bancária em dois documentos independentes | CNPJ aparece no cadastro e no extrato de repasse |
| Data de criação compatível com a linha do tempo | Empresa criada um mês antes do crime |
| Valor, percentual ou cláusula que só faz sentido com o vínculo | 88% de repasse só faz sentido se há relação societária |
| Documento externo confirmando a ligação | Cartão de visita + cadastro = mesmo endereço |

❌ **Iniciais, sobrenome parecido, cidade igual ou cargo compatível são pistas de suporte — nunca âncoras únicas de culpa ou vínculo.**

---

## 3. Pistas de suporte

Ajudam a reforçar a hipótese, mas não são prova suficiente sozinhas.

**Exemplos:**
- comportamento estranho no chat;
- frase ambígua em depoimento;
- coincidência de sobrenome;
- relação comercial não documentada formalmente;
- valor estranho sem função narrativa clara;
- cidade repetida em documentos diferentes.

Pistas de suporte criam textura e suspeita. Use para enriquecer o universo e plantar red herrings. Nunca como prova única de nada crítico.

---

## 4. Red herrings

Red herrings bons desviam sem trapacear. O jogador deve poder descartá-los por evidência — não porque o autor disse que são falsos.

**Tipos de red herring úteis:**

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| Motivo sem oportunidade | O personagem tinha razão para agir, mas não estava no local | Dívida, mas álibi no registro de acesso |
| Oportunidade sem benefício | Estava no local, mas não ganhou nada | Acesso à sala, mas sem relação com o objeto |
| Erro real não criminoso | Fez algo errado que parece crime | Deploy que causou instabilidade mas não aprovou nada |
| Acusação por personalidade | Antipático, estranho, histórico ruim | Histórico com polícia, mas sem relação com o caso |
| Conversa ambígua | Parece confissão mas é sobre outro assunto | Mensagem sobre "esquema" = esquema legal |
| Fornecedor suspeito | Empresa estranha com acesso | Documentado corretamente, prestou serviço legítimo |

**Checklist do red herring justo:**
- [ ] Tem motivo legítimo para parecer suspeito.
- [ ] Tem limite claro quando os documentos são cruzados.
- [ ] Não possui mais evidências que a solução real.
- [ ] Pode ser descartado por prova, não por opinião do autor.
- [ ] Não tem os quatro pilares de validação preenchidos.

---

## 5. Regra de consistência de códigos

Antes de criar qualquer código, número de protocolo ou cartão com puzzle, responda:

| Pergunta | Verificação |
|----------|------------|
| Qual é o critério deste código? | IDs / endereços / datas / cores / coordenadas / outro |
| Todos os elementos seguem o mesmo critério? | Sim — se não, cada camada está documentada separadamente |
| A chave de leitura está acessível ao jogador? | Sim — no mesmo ou em documento anterior |
| O código é confirmado por outro documento? | Sim — nunca é prova única |
| Existe elemento sem correspondência? | Não — todo elemento tem referência documental |
| Foi testado por alguém que não criou o caso? | Sim (obrigatório antes da produção final) |

**Regras obrigatórias:**
1. Não misture critérios dentro do mesmo código sem indicar documentalmente.
2. Não use número decorativo que se pareça com pista crítica.
3. Não coloque ID inexistente para "dar mistério".
4. Não dependa de cifra externa que o jogador precisaria pesquisar.
5. Se o código for difícil, entregue uma pista de **método** antes da pista de **conteúdo**.

✅ **Exemplo correto:** `AR-31-18-22-12` onde 31, 18, 22 e 12 são IDs existentes na matriz.

❌ **Exemplo errado:** `CHAVE 09/14/22/31` onde 14 não existe na matriz de personagens.

---

## 6. Cadeias financeiras e logísticas

Em casos com transferência de dinheiro, objeto ou prova por múltiplas etapas, cada salto precisa de âncora documental própria.

**Regras:**
- cada salto aparece em pelo menos um documento (extrato, recibo, contrato, cadastro);
- o salto final — que chega ao beneficiário — precisa de duas confirmações independentes;
- cadeias com mais de três saltos precisam de documento organizador (extrato consolidado, linha do tempo, auditoria);
- nunca deixe um salto dependendo de dedução por exclusão;
- não use valores ou percentuais sem função narrativa;
- quando houver empresa intermediária, explique documentalmente por que ela existe e quem a controla.

**Checklist por salto:**

| Salto | Documento que prova | Confirmação independente | Risco de ambiguidade |
|-------|---------------------|------------------------|---------------------|
| Origem → Destino 1 | | | |
| Destino 1 → Destino 2 | | | |
| Destino final → Beneficiário | | | (precisa de 2 confirmações) |

---

## 7. Linha do tempo — as três linhas obrigatórias

A linha do tempo é a espinha dorsal do caso. Crie internamente antes de escrever qualquer documento.

**Linha A — Verdade real (interna, nunca entregue):**
```
Data/Hora | Evento real | Quem | Documento que prova | Confirmação independente
```

**Linha B — O que os suspeitos contam (percebida):**
```
Data/Hora | Versão declarada | Por quem | Onde aparece | Contradição com Linha A
```

**Linha C — O que os documentos provam (documental):**
```
Data/Hora | Fato verificável | Qual documento | Lacuna ainda aberta
```

A diversão investigativa está nos **desalinhamentos** entre A, B e C.

**Checklist de linha do tempo:**
- [ ] O intervalo crítico está claro (início e fim).
- [ ] O jogador sabe quais horários comparar.
- [ ] Toda contradição importante é intencional e detectável.
- [ ] Deslocamentos impossíveis são demonstráveis por mapa ou escala.
- [ ] A linha do tempo real completa está no gabarito.

---

## 8. Calibragem de dificuldade

### Fácil
- 3–4 suspeitos;
- pistas diretas com um único cruzamento principal;
- poucos documentos técnicos;
- red herring fraco.

### Médio
- 5–6 suspeitos;
- dois envelopes;
- uma camada de red herrings;
- necessidade de tabela de horários.

### Médio-alto
- 6–8 suspeitos;
- dois envelopes com 9–11 documentos cada;
- duas ou mais camadas de red herrings;
- ao menos um documento técnico (log, extrato, auditoria);
- cadeia financeira ou logística com pelo menos dois saltos documentados;
- código ou numeração com chave detectável no material;
- separação clara entre executor, planejador e beneficiário;
- necessidade de linha do tempo ativa para resolver.

### Difícil
- 7+ suspeitos;
- múltiplos papéis (executor, planejador, beneficiário, cúmplice);
- cadeia de colaboração com documentação densa;
- código consistente mas não óbvio;
- pistas financeiras e logísticas com 3+ saltos.

### Sinais de calibragem observáveis

| Sinal observado | O que indica | Ajuste |
|----------------|-------------|--------|
| Grupo resolve E1 em menos de 15 min | Fácil demais | Adicionar red herring justo ou remover pista direta demais |
| Grupo trava mais de 30 min em E1 | Difícil demais | Adicionar documento de suporte ou dica estrutural |
| Grupo chega ao culpado errado em E1 | Red herring forte demais | Reduzir evidências do falso suspeito ou fortalecer descarte |
| Grupo não percebe a cadeia do E2 | Motivação mal plantada | Adicionar documento anterior ao evento |
| Grupo acerta por intuição mas não prova | Pistas fracas ou dispersas | Reforçar matriz e critério de validação |
| Grupo lê tudo mas ignora código | Código pouco sinalizado | Inserir chave de leitura ou pista de método |
| Grupo depende de conhecimento externo | Caso não autossuficiente | Adicionar glossário, tabela ou regra impressa |

---

## 9. Ritmo de revelação

Distribua as pistas para que a experiência tenha camadas:

- **Primeira leitura:** contexto, suspeitos, urgência, mundo do caso.
- **Segunda leitura:** inconsistências percebidas, início de cruzamentos.
- **Terceira leitura:** descarte de falsos suspeitos, foco em candidatos fortes.
- **Fechamento do envelope:** hipótese defendida por documentos.

**Evite concentrar todas as pistas críticas em um único documento.** Se o caso fecha com um só log, o jogo não é investigação — é busca.

---

## 10. Anti-padrões — nunca faça

- ❌ Criar pista crítica ilegível ou escondida em decoração.
- ❌ Usar código sem chave acessível ao jogador.
- ❌ Criar personagem oculto essencial para a solução.
- ❌ Depender de internet em modo offline puro.
- ❌ Colocar gabarito no material do jogador.
- ❌ Usar coincidência como prova única.
- ❌ Deixar entidade citada no extrato sem âncora documental.
- ❌ Esconder a única prova em elemento visual ambíguo (cor, posição, tamanho).
- ❌ Deixar o E2 contradizer injustamente uma conclusão correta do E1.
- ❌ Usar ID inexistente em código ou log.
- ❌ Criar vínculo entre entidades baseado apenas em sobrenome ou iniciais.
- ❌ Deixar salto de cadeia financeira sem documento próprio.

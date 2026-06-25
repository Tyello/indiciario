# 14 — Grafo de Pistas e Solvabilidade Estrutural

Este documento define a primeira versão do grafo lógico de pistas do Indiciário.
Ele não descreve uma visualização: não há SVG, PNG, HTML, Mermaid, dashboard ou
qualquer representação gráfica obrigatória. O objetivo é produzir um relatório
serializável (`graph_report.json`) que ajude a medir se a estrutura documental do
caso sustenta as conclusões esperadas.

---

## O que é o grafo de pistas

O grafo de pistas é uma camada técnica de leitura do blueprint. Ele conecta
**documentos** a **contratos de evidência** para verificar se cada conclusão
investigativa importante tem lastro documental mínimo.

Nesta versão, o grafo é propositalmente simples:

- documento vira nó do tipo `document`;
- contrato de evidência vira nó do tipo `contract`;
- prova principal cria aresta `document -> contract` com relação `proves`;
- confirmação independente cria aresta `document -> contract` com relação
  `confirms`;
- documentos que descartam alternativas criam aresta `document -> contract` com
  relação `discards`;
- contratos finais ou de tipo `solucao_final` são alvos de solvabilidade.

---

## Documento, pista, contrato e conclusão

**Documento** é o artefato entregue ao jogador: e-mail, log, extrato, boletim,
contrato, recibo, carta ou outro tipo de peça do dossiê.

**Pista** é a informação interpretável dentro de um documento. Uma pista pode
apontar para presença, oportunidade, motivo, benefício, descarte de suspeito ou
outro fato relevante.

**Contrato de evidência** é a declaração estruturada de que uma conclusão só pode
ser aceita quando há prova principal e confirmação independente. Ele é a ponte
entre narrativa e validação técnica.

**Conclusão** é o enunciado que o contrato pretende sustentar: por exemplo, que
uma pessoa teve oportunidade, que uma alternativa foi descartada, que houve
benefício ou que a solução final combina executor, planejador e beneficiário.

---

## Por que o grafo existe

O grafo existe para detectar problemas estruturais antes da produção final:

- contratos sem prova principal;
- contratos sem conclusão;
- documentos que não participam de nenhum contrato;
- contratos que não ajudam avanço nem solução final;
- ausência de solução final declarada;
- solução final sem prova e confirmação independentes.

Ele complementa o validador CE_* e o checklist de solvabilidade. Redundância
controlada é aceitável porque o `graph_report.json` tem função diagnóstica e deve
mostrar o problema no vocabulário do grafo.

Blueprints legados sem `contratos_evidencia` recebem `graph_report.status` igual
a `skipped`. Esse estado preserva compatibilidade com casos antigos e não deve,
sozinho, impedir o empacotamento quando o QA técnico passa. Para casos novos, o
recomendado é sempre preencher `contratos_evidencia` para que o grafo consiga
avaliar a solvabilidade estrutural.

---


## Pilares, descartes e falhas ER

O grafo também deve ser usado como disciplina de autoria para impedir lacunas de cadeia de evidência:

- **Pilar sem pista = ER_002.** Cada pilar de validação do E1 precisa aparecer como pista rastreável: `pista -> documento -> pilar`. Não basta o pilar existir no gabarito ou na explicação do facilitador.
- **Descarte solto = ER_006.** Cada red herring precisa de uma pista que aponte para o documento de descarte: `pista -> documento -> descarte`. Descarte escrito apenas na prosa do red herring não conta como cadeia investigável.

Forma correta de modelar: declarar a pista na `matriz_pistas`, apontar o documento onde ela aparece e explicitar qual pilar ou descarte ela sustenta. Assim o jogador cruza evidência real em vez de depender de interpretação do autor.

## Documento órfão

Documento órfão é um documento que não aparece em nenhum contrato como:

- `prova_principal`;
- `confirmacao_independente`;
- item de `descarta_alternativas`.

Nem todo documento órfão é erro. Alguns documentos podem existir para ambientação,
ritmo, emoção ou instrução. Ainda assim, o relatório deve listá-los para revisão
humana, porque documentos órfãos em excesso podem indicar dispersão ou material
que não ajuda a solução.

---

## Contrato órfão

Contrato órfão é um contrato que, nesta versão conservadora:

- não é `obrigatoria_para_avanco`;
- não está em fase `final`;
- não tem `tipo` igual a `solucao_final`.

Como ainda não há dependência explícita contrato -> contrato, o sistema não sabe
se esse contrato alimenta uma cadeia posterior. Por isso, ele é marcado como
warning e também listado em `dead_ends`, sem bloquear automaticamente a produção.

---

## Caminho de solução

Caminho de solução é a trilha lógica mínima que aponta para um contrato final.
Nesta primeira versão, ele lista:

- o contrato final alvo;
- documentos diretamente usados por esse contrato;
- contratos obrigatórios anteriores e o próprio contrato final;
- uma profundidade simples baseada na quantidade de contratos do caminho.

Esse caminho não substitui análise narrativa humana. Ele é um resumo técnico para
ver se a solução final tem âncoras documentais declaradas.

---

## Regras GP_*

### GP_001 — Contrato sem prova principal

- Severidade no grafo: `critical`.
- Ocorre quando um contrato não define `prova_principal`.

### GP_002 — Contrato sem conclusão

- Severidade no grafo: `critical`.
- Ocorre quando `conclusao` está vazia ou só contém espaços.

### GP_003 — Documento órfão

- Severidade no grafo: `warning`.
- Ocorre quando um documento não é usado por prova principal, confirmação
  independente ou descarte de alternativas.
- Não bloqueia por padrão, pois pode representar ambientação intencional.

### GP_004 — Contrato sem utilização posterior

- Severidade no grafo: `warning`.
- Ocorre quando um contrato não é obrigatório para avanço e não é final.
- Nesta versão também entra em `orphan_contracts` e `dead_ends`.

### GP_005 — Dependência circular

- Preparado para evolução futura.
- Nesta versão, `cycles` deve permanecer lista vazia porque ainda não há campo de
  dependência explícita contrato -> contrato.
- Não se deve inventar ciclo a partir de documentos.

### GP_006 — Solução final ausente

- Severidade no grafo: `critical`.
- Ocorre quando nenhum contrato tem `fase == "final"` ou `tipo == "solucao_final"`.
- Blueprints sem `contratos_evidencia` retornam `status: skipped` com GP_006 em
  severidade `warning`, preservando compatibilidade com casos legados.
- Quando contratos existem, ausência de contrato final retorna `status: failed` e
  GP_006 em severidade `critical`.

### GP_007 — Contrato final sem caminho documental mínimo

- Severidade no grafo: `critical`.
- Ocorre quando um contrato final não tem prova principal existente, confirmação
  independente existente ou usa o mesmo documento para prova e confirmação.

---

## Limitações da versão atual

- Não há visualização.
- Não há SVG, PNG, HTML, Mermaid ou dashboard.
- Não há dependência explícita contrato -> contrato.
- A detecção de ciclos existe apenas como campo preparado (`cycles: []`) e só será
  útil quando dependências explícitas forem adicionadas ao blueprint.
- O caminho de solução é um resumo conservador, não um motor completo de inferência.

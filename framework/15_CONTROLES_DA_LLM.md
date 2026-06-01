# 15 — Controles da LLM e feedback estruturado

## 1. Objetivo

A LLM não é a fonte final de verdade do Indiciários. Ela pode gerar e corrigir
blueprints, mas a validade operacional do caso é determinada por três guard rails
técnicos:

- `BlueprintValidator.validar()` e seus códigos de erro;
- `qa_report.json`, que verifica o pacote final e o manifest;
- `graph_report.json`, que verifica o grafo lógico de pistas e contratos.

O artefato `llm_feedback.json` traduz essas validações em instruções claras para
correção futura do blueprint. Ele é técnico, interno, não é material de jogador,
não é impresso e não autoriza a LLM a ignorar as regras do framework.

## 2. O que a LLM pode fazer

A LLM pode:

- criar personagens;
- criar documentos;
- criar pistas;
- criar contratos de evidência;
- criar linhas do tempo;
- criar red herrings;
- propor dicas;
- reorganizar envelopes;
- corrigir campos técnicos;
- corrigir inconsistências apontadas pelo validator.

## 3. O que a LLM não pode fazer

A LLM não pode:

- ignorar erro crítico;
- remover contrato de evidência só para passar validação;
- inventar documento referenciado sem criar o documento correspondente;
- usar a mesma evidência como prova principal e confirmação independente;
- fazer E1 depender de E2;
- criar QR code, link, app ou dependência de internet em modo offline;
- criar placeholder genérico;
- resolver erro apagando conteúdo importante;
- mover spoiler para envelope anterior;
- burlar validator/QA/grafo.

## 4. Estratégia obrigatória de correção

Ao receber feedback estruturado, a LLM deve:

- ler todos os erros críticos primeiro;
- corrigir erros estruturais antes de estilo;
- preservar intenção narrativa;
- preservar IDs existentes quando possível;
- criar novos IDs apenas quando necessário;
- garantir documentos citados existem;
- garantir contratos têm prova principal e confirmação independente;
- garantir solução final existe;
- garantir que o blueprint final valide sem críticos.

## 5. Prioridades

### Prioridade alta

- `CONT_*`;
- `DOC_*`;
- `ENV_*`;
- `CE_*`;
- `GP_*` crítico;
- `QA_*` erro.

### Prioridade média

- warnings de solvabilidade;
- documentos órfãos;
- contratos órfãos;
- dicas fracas;
- risco alto em contrato obrigatório.

### Prioridade baixa

- estilo;
- melhorias opcionais;
- densidade narrativa;
- refinamentos visuais.

## 6. Exemplos de feedback

### `CE_005`

> A prova principal e a confirmação independente são o mesmo documento. Escolha um
> segundo documento independente.

### `GP_006`

> Não há contrato de solução final. Crie um contrato final que conecte documentos
> e conclusões dos envelopes.

### `ENV_005`

> O blueprint declara menos envelopes do que usa. Ajuste formato_envelopes ou
> remova documentos do envelope excedente.

### `CONT_003`

> Campo obrigatório ausente no conteúdo do documento. Preencha o campo sem usar
> placeholder.

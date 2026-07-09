---
name: spec-kit
description: Classifica toda tarefa de código em tiers de complexidade (T0-T3), gera specs proporcionais ao tier e roteia a execução automaticamente para o modelo mais barato (Haiku por padrão; Sonnet apenas em decisões e desbloqueios). Use esta skill em TODA tarefa de código — implementação, refatoração, correção de bug, feature nova, script — mesmo que o usuário não mencione "spec", "planejamento" ou "modelo". Ela decide sozinha quando a spec vale a pena, quando pular direto para a execução, e quando escalar de modelo.
---

# Spec-Kit: Especificação proporcional por tier + roteamento automático de modelo

## Objetivo

Toda tarefa de código passa primeiro por uma **classificação de tier**. O tier determina quanto esforço de especificação vale a pena antes de executar. A lógica econômica: specs profundas custam tokens no planejamento, mas permitem que a execução rode **inteiramente no Haiku** com baixa taxa de retrabalho. O Sonnet só entra em dois momentos: (1) escrever a spec e tomar decisões, (2) resolver escalações quando o Haiku trava.

Regras de ouro:
1. **Quanto maior a tarefa, mais profunda a spec; quanto menor, mais direto ao código.**
2. **Haiku é o executor padrão. Sempre. Sonnet é exceção, nunca rota principal de execução.**

## Roteamento automático de modelo

Esta skill vem com dois subagentes prontos (instale-os em `.claude/agents/` do projeto — ver seção "Instalação"):

- **`spec-executor`** (`model: haiku`) — executa etapas da spec. Recebe APENAS: a etapa atual, os arquivos que ela toca e o critério de validação. Nunca recebe o histórico da conversa.
- **`spec-resolver`** (`model: sonnet`) — acionado SOMENTE quando o executor devolve um relatório de escalação. Resolve a decisão/bloqueio, atualiza a spec e devolve a etapa corrigida ao executor.

O ciclo automático é:

```
planejar (sonnet) → executar etapa (haiku) → validou? → próxima etapa (haiku)
                                          ↘ escalou? → resolver (sonnet) → volta ao haiku
```

**Regra dura:** o orquestrador NUNCA envia uma etapa direto ao Sonnet "por precaução". Se a etapa parece exigir julgamento, isso é sinal de que a spec está incompleta — volte ao planejamento e elimine o julgamento, depois mande ao Haiku. A única exceção: uma etapa que já escalou 2 vezes vai direto ao Sonnet para execução completa (limite de ping-pong).

### Protocolo de escalação (o que faz o Haiku parar)

O executor escala se, e somente se, ocorrer um destes gatilhos mecânicos:

1. **Validação falhou 2x** — o critério de aceitação da etapa não passa após 2 tentativas de correção.
2. **Realidade ≠ spec** — arquivo, função, schema ou dependência citada na spec não existe ou tem assinatura diferente.
3. **Decisão residual** — a etapa exige uma escolha que a spec não resolveu (qualquer "depende").
4. **Condição de escalação da etapa** — o gatilho explícito escrito na própria spec disparou.

O relatório de escalação é estruturado (formato em `agents/spec-executor.md`) para que o Sonnet resolva sem reler tudo.

## Passo 1 — Classificar o tier

Avalie a tarefa nestes 5 eixos e some os pontos:

| Eixo | 0 pontos | 1 ponto | 2 pontos |
|---|---|---|---|
| **Arquivos tocados** | 1 | 2–4 | 5+ ou arquitetura nova |
| **Decisões em aberto** | nenhuma (caminho óbvio) | 1–2 escolhas locais | escolhas de design/API/schema |
| **Risco de quebra** | isolado, sem consumidores | afeta módulo existente | afeta contratos, dados, ou público |
| **Novidade** | padrão já existente no repo | variação de padrão existente | território novo (lib nova, domínio novo) |
| **Verificabilidade** | trivial de testar manualmente | testável com testes existentes | exige novos testes/critérios |

**Mapeamento:** 0–1 → **T0** | 2–4 → **T1** | 5–7 → **T2** | 8–10 → **T3**

Em dúvida entre dois tiers, escolha o **menor** — subir de tier no meio (escalação) é mais barato que spec desnecessária.

Declare o tier em uma linha: `[spec-kit: T2 — 6pts: arquivos=1, decisões=2, risco=1, novidade=1, verif=1]`

## Passo 2 — Clarificar (T2/T3 apenas, e só se houver ambiguidade)

Antes de escrever spec T2/T3, liste mentalmente as ambiguidades do pedido. Se houver alguma cuja resposta errada invalidaria a spec, faça **no máximo 3 perguntas objetivas** ao usuário de uma vez só (nunca em série). Se não houver, siga direto. T0/T1 nunca param para clarificar — assumem a interpretação óbvia e a declaram em 1 linha.

## Passo 3 — Executar o protocolo do tier

### T0 — Trivial (typo, one-liner, ajuste de config)
**Sem spec, sem subagente, sem cerimônia.** Execute direto e mostre o diff.

### T1 — Pequena (função nova, bugfix localizado, refactor de 1 arquivo)
**Micro-spec inline** (3–6 linhas): objetivo, arquivos, critério de pronto. Depois delegue ao `spec-executor` (Haiku) em uma única chamada. Bugfix usa a variante bugfix (comportamento atual / esperado / intocável) de `references/spec-templates.md`.

### T2 — Média (feature multi-arquivo, refactor com consumidores, integração)
**Spec compacta** (template em `references/spec-templates.md`): objetivo, não-objetivos, arquivos e mudanças, **todas as decisões tomadas**, critérios de aceitação em formato EARS, condições de escalação por etapa. Execute etapa a etapa via `spec-executor`.

### T3 — Grande (subsistema novo, mudança arquitetural, pipeline)
**Spec profunda** (template em `references/spec-templates.md`): tudo do T2, mais contratos/schemas por extenso, exemplos de entrada/saída, plano de testes escrito ANTES da implementação (os testes são o critério executável que dispensa julgamento do Haiku), grafo de dependências entre etapas (etapas independentes podem rodar em executores paralelos), e **passo de análise de consistência** antes de liberar (ver abaixo).

**Análise de consistência (obrigatória no T3):** antes da primeira etapa, releia a spec inteira procurando: critérios que não cobrem algum requisito, etapas que dependem de artefatos que nenhuma etapa anterior cria, contradições entre contratos e exemplos, e frases que delegam julgamento. Corrija antes de executar — cada furo encontrado aqui custa centavos; encontrado pelo Haiku, custa uma escalação.

## Constituição do projeto (opcional, recomendado)

Se existir um arquivo `SPEC-CONSTITUTION.md` na raiz do repo, trate-o como princípios inegociáveis que toda spec herda automaticamente (ex.: "todo endpoint tem teste de contrato", "nunca usar ORM X", "logs sempre em JSON"). Isso evita repetir as mesmas decisões em toda spec e reduz escalações por conflito de convenção. Se não existir e você notar decisões se repetindo entre tarefas, sugira criá-lo.

## Escalação de tier no meio do caminho

Se durante a execução aparecer algo que a classificação não previu, **pare e reclassifique**:
1. Declare: `[spec-kit: escalando T1→T2 — motivo: <1 frase>]`
2. Gere a spec do tier novo apenas para a parte restante
3. Continue no ciclo normal (Haiku executa)

## Anti-padrões

- **Spec-teatro**: spec T3 para tarefa T1. O custo do planejamento tem que ser menor que o retrabalho que evita.
- **Spec-código**: se a spec é praticamente o código, escreva o código.
- **Decisão delegada**: "escolha a melhor abordagem" numa spec é bug da spec.
- **Sonnet preventivo**: mandar etapa ao Sonnet "porque parece difícil". Difícil para o Haiku = spec rasa. Aprofunde a spec.
- **Contexto gordo**: passar histórico da conversa ao executor. Ele recebe etapa + arquivos + critério, nada mais.
- **Critério vago**: "deve funcionar corretamente" não é critério. Critério é comando + resultado esperado.

## Instalação (uma vez por projeto)

Copie os subagentes para o projeto:
```bash
mkdir -p .claude/agents
cp <skill>/agents/spec-executor.md .claude/agents/
cp <skill>/agents/spec-resolver.md .claude/agents/
```
Fora do Claude Code (sem subagentes), simule o roteamento: escreva a spec com todo o rigor, execute as etapas mecanicamente como se fosse o executor, e trate escalações explicitamente no fluxo.

## Referências

- `references/spec-templates.md` — templates T1/T2/T3 + variante bugfix + checklist de qualidade. Leia ao gerar qualquer spec T2/T3.
- `agents/spec-executor.md` — definição do subagente executor (Haiku) e formato do relatório de escalação.
- `agents/spec-resolver.md` — definição do subagente resolvedor (Sonnet).

# 18 — Playtest e métricas de qualidade narrativa

## Objetivo

A camada de playtest e métricas existe para sinalizar riscos de experiência investigativa antes de um teste humano. Ela não substitui as validações já existentes:

- **QA** verifica estrutura de pacote, arquivos, manifests, PDFs e confidencialidade técnica.
- **Graph** verifica solvabilidade estrutural, conexões entre documentos e contratos de evidência.
- **Playtest** verifica risco de experiência: ritmo, carga cognitiva, volume de material e coerência entre escopo declarado e densidade observada.

O objetivo não é declarar que um caso é bom ou ruim. O objetivo é criar um relatório técnico de sinais que ajudem revisão editorial, produção e futuras rodadas de correção.

## Limitações

As métricas são heurísticas simples. Elas usam contagens e faixas de referência, sem LLM, sem interpretação semântica profunda e sem julgamento autoral.

Essas métricas:

- não substituem playtest humano;
- não determinam qualidade narrativa;
- não provam diversão, tensão ou satisfação;
- não bloqueiam geração de casos;
- servem apenas para sinalização e revisão.

Um warning de playtest pode ser aceitável quando o design do caso exige uma escolha incomum, desde que a intenção esteja clara para a equipe humana.

## Métricas analisadas

A análise inicial observa:

- **documentos** — total de documentos jogáveis no dossiê;
- **envelopes** — quantidade e distribuição entre fases;
- **contratos** — contratos obrigatórios para avanço;
- **suspeitos** — suspeitos aparentes inferidos do elenco quando houver dados suficientes;
- **red herrings** — desvios explícitos ou inferidos por contratos de descarte;
- **dificuldade** — comparação entre dificuldade declarada e dificuldade percebida estimada;
- **tempo estimado** — estimativa automática por volume de documentos, contratos e envelopes;
- **densidade de pistas** — relação aproximada entre material disponível e carga de conclusões obrigatórias.

## Carga cognitiva

Carga cognitiva é uma estimativa do esforço que o grupo precisará gastar para ler, organizar, comparar e lembrar evidências. Ela é calculada por faixas simples de documentos e ajustada levemente por contratos obrigatórios.

- **Baixa**: poucos documentos, baixa pressão de cruzamento e progressão mais direta.
- **Média**: volume intermediário, cruzamentos suficientes para investigação sem excesso aparente.
- **Alta**: muitos documentos ou muitos contratos obrigatórios, exigindo maior organização do grupo.

Carga alta não é erro. Ela apenas indica que o caso pode precisar de mais tempo, melhor facilitação ou materiais de apoio.

## Dificuldade percebida

A dificuldade percebida é uma estimativa automática baseada em profundidade da cadeia de solução (`clue_graph` depth), densidade textual, ambiguidade real e papel do E2; volume documental e suspeitos são sinal informativo secundário (ISSUE-30.7). Ela pode divergir da dificuldade declarada pelo autor.

Essa divergência não significa falha narrativa. Ela sinaliza que a promessa feita ao jogador talvez precise ser revisada: um caso declarado como iniciante pode ter densidade de intermediário, ou um caso declarado como avançado pode parecer curto demais para essa etiqueta.

## Solvability Meter (ISSUE-33.2)

Além das métricas heurísticas acima (sem LLM), existe uma segunda camada opcional
de sinalização pré-playtest: o **Solvability Meter** (`generator/solvability_meter.py`),
que roda N execuções blind solver → Conclusion Judge (ISSUE-33/33.1) sobre o mesmo
bundle cego, variando apenas a execução do provider, e agrega a taxa de resolução
(`solve_rate`) numa estimativa de dificuldade (`facil`/`medio`/`dificil`/`injusto`).

Nota de honestidade: essa estimativa mede dificuldade **para um solver LLM**, que é
proxy — assim como as métricas heurísticas desta seção, ela sinaliza, não decide.
**O teste cego humano continua sendo o veredito real de dificuldade e solvabilidade.**
Os limiares usados (`SM_003` em `generator/solvability_meter.py`) são iniciais e
calibráveis contra playtests futuros, do mesmo jeito que a dificuldade percebida
por heurística acima também é. Cross-link de faixas: `docs/DIFFICULTY_FRAMEWORK.md`.

## Interpretação

Warnings de playtest não são falhas. Eles são sinais para revisão.

Ao interpretar `playtest_report.json`, trate cada warning como pergunta editorial:

- o volume de documentos combina com a dificuldade prometida?
- a distribuição de envelopes cria ritmo equilibrado?
- há suspeitos demais para o tempo estimado?
- há red herrings suficientes para desvio justo, mas não tantos que virem ruído?
- o tempo declarado é compatível com a densidade do caso?

A decisão final permanece humana e deve considerar intenção de design, público-alvo, formato de facilitação e resultados de playtests reais.

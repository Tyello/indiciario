# ISSUE-30.12 — Gate estrutural entre blueprint e documentos finais

## Contexto

A ISSUE-30.11 (geração-do-zero) produziu evidência concreta de um modo de falha que hoje não tem regra escrita em lugar nenhum. No STEP-02, o blueprint de `examples/caso_gerado_cooperativa.json` foi gerado em uma única passada — elenco, envelopes, pilares, contratos de evidência, red herrings, códigos e os 17 documentos finais completos, tudo na mesma execução. O STEP-02_REVIEW aprovou o conteúdo (sem vazamento, padrões PAT rastreáveis). Só no STEP-03 — já com os documentos todos escritos — a tentativa de `Blueprint(**json)` revelou **327 erros de construção Pydantic**: nomes de campo errados, `envelope` como string em vez de int, `verdade_real` como dict quando deveria ser outro shape, `linha_tempo_real`/`linha_tempo_documental` com chaves trocadas, `contratos_evidencia`/`pilares_validacao`/`dicas` fora do formato esperado. A correção não foi um ajuste pontual — foi reescrita estrutural completa do arquivo (`STEP-03_EXECUTION.md`), descartando a validação de forma que deveria ter acontecido antes da prosa final.

`framework/07_PROMPT_GERADOR_DE_CASO.md` já tem um gate obrigatório entre a Fase 1 (blueprint) e a Fase 2 (documentos finais) — mas esse gate (`## GATE DE QUALIDADE`) cobre exclusivamente critérios narrativos e de solvabilidade (cruzamento de pistas, red herrings, contratos de evidência por sentido semântico). Nenhuma linha do 07, do `BLUEPRINT_AUTHORING_GUIDE.md` ou do `CASE_GENERATION_WORKFLOW.md` instrui a checar, antes da Fase 2, se o esqueleto do JSON **instancia contra o schema** — isso só é mencionado como etapa 3 (validação estrutural), que no fluxo documentado hoje acontece depois de tudo escrito, não antes.

Este não é o mesmo problema que a 30.9 (falso-positivo de métrica) nem a 30.10 (padrão narrativo não codificado). É um terceiro tipo de gap: **ordem de verificação**. A forma do JSON é mais barata de corrigir com o esqueleto vazio do que com 17 documentos inteiros escritos por cima de uma estrutura errada.

**Origem:** achado do STEP-02/STEP-03 da ISSUE-30.11 (execução em 2026-07). Não depende do resultado do playtest humano pendente da 30.11 — é uma correção de processo de autoria, independente do veredito de qualidade do caso gerado.

## Objetivo

`framework/07_PROMPT_GERADOR_DE_CASO.md` passa a exigir um **gate estrutural** entre a Fase 1 e a Fase 2: o esqueleto do blueprint deve ser verificado contra o schema (nomes de campo, tipos, shapes) antes de qualquer documento final ser escrito. `docs/CASE_GENERATION_WORKFLOW.md` e `docs/BLUEPRINT_AUTHORING_GUIDE.md` passam a referenciar esse gate como uma etapa distinta do gate narrativo existente.

## Fora de escopo

- **Não** alterar, renomear ou fundir o `## GATE DE QUALIDADE` narrativo já existente no 07 — são gates complementares (forma vs. conteúdo/solvabilidade), não um substituto do outro.
- **Não** escrever código novo, script novo ou teste automático de shape dentro de `generator/`. O gate usa o comando que já existe (`python -m generator.validator ... --strict`, que por sua vez depende da construção Pydantic já existente em `generator/models.py`).
- **Não** reabrir nem depender do resultado da ISSUE-30.11 (playtest humano pendente). É correção de processo, não de conteúdo do caso gerado.
- **Não** exigir que o esqueleto tenha o campo `conteudo` de cada documento com texto final — placeholder de uma linha basta para passar o gate estrutural; conteúdo completo é responsabilidade da Fase 2.
- **Não** tornar o gate estrutural obrigatório apenas quando há execução de código disponível — a instrução precisa valer também para quem gera só em chat, sem terminal (ver contrato).

## Contrato / regras

### Localização
Inserir, em `framework/07_PROMPT_GERADOR_DE_CASO.md`, uma nova subseção **entre** o fim do `## GATE DE QUALIDADE — OBRIGATÓRIO ANTES DOS DOCUMENTOS FINAIS` (após a linha "Se o risco for Médio ou superior: sinalize explicitamente...") **e** o início de `## ENTREGÁVEIS — NESTA ORDEM`.

### Texto a inserir (verbatim, ajustável só por clareza de redação, não de conteúdo)

```markdown
---

## GATE ESTRUTURAL — OBRIGATÓRIO ENTRE A FASE 1 E A FASE 2

O gate acima cobre solvabilidade e narrativa. Este cobre forma: antes de escrever o conteúdo final de qualquer documento (Fase 2), confirme que o esqueleto do blueprint — elenco, `objetivos_por_envelope`, `pilares_validacao`, `contratos_evidencia`, `red_herrings`, `codigos`, `linha_tempo_real`/`linha_tempo_percebida`/`linha_tempo_documental`, `cadeia_financeira`/cadeia logística — instancia contra o schema do projeto. Documentos podem ter `conteudo` placeholder de uma linha nesta etapa; o que precisa estar certo agora é a forma, não a prosa final.

Motivo: escrever os documentos finais sobre uma estrutura que ainda pode estar errada custa caro — o erro só aparece depois de todo o texto pronto, e a correção vira reescrita estrutural completa em vez de ajuste pontual no esqueleto.

Como executar o gate, dependendo de quem está gerando:

- **Com Claude Code ou outro agente com acesso ao repositório:** salve o esqueleto e rode `python -m generator.validator <arquivo>.json --strict`. Erros de schema (nome de campo errado, tipo errado, `envelope` como texto em vez de número, chave trocada em linha do tempo) aparecem antes de qualquer prosa final ser escrita.
- **Gerando só em chat, sem execução de código:** releia cada campo do esqueleto contra os nomes exatos de `framework/CONTEUDO_SCHEMA.md` e a lista de tipos em `framework/03_TIPOS_DE_DOCUMENTOS.md`; declare explicitamente, campo por campo, que o nome e o tipo batem, antes de prosseguir para a Fase 2.

Se o esqueleto falhar o gate: corrija a estrutura primeiro. Não escreva conteúdo final de documento sobre uma estrutura que ainda pode mudar de forma.

---
```

### Ajuste de enquadramento em `## ENTREGÁVEIS — NESTA ORDEM`

Sem reescrever a lista de Fases 1–4 existente, adicionar uma frase logo abaixo do título `## ENTREGÁVEIS — NESTA ORDEM` deixando explícito que a Fase 1 só termina depois do gate estrutural acima:

```markdown
A Fase 1 só está concluída depois do GATE ESTRUTURAL acima. Não pule para a Fase 2 com um esqueleto ainda não verificado contra o schema.
```

### Cross-referências (sem duplicar conteúdo)

- **`docs/CASE_GENERATION_WORKFLOW.md`**, seção `### 2. Geração (framework, em chat)`: adicionar uma linha apontando que o mesmo comando da etapa 3 (`python -m generator.validator ... --strict`) pode e deve ser corrido antes, sobre o esqueleto, como gate estrutural do 07 — mais barato do que descobrir o erro depois de tudo escrito.
- **`docs/BLUEPRINT_AUTHORING_GUIDE.md`**, próximo ao `## Checklist antes de aprovar um blueprint` ou ao `## Guardrails visuais de autoria`: uma nota curta de que existe um gate de forma (schema/Pydantic), distinto do checklist ali presente (que é editorial/narrativo), e que ele mora no `framework/07`.

## Impacto documental

Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilhos: "muda entregáveis, formato ou gate da geração" para o 07; "muda a fronteira geração↔validação" para o `CASE_GENERATION_WORKFLOW.md`; "conclusão/abertura de issue, próxima issue" para `CLAUDE.md`/`docs/ROADMAP.md`).

- [ ] `framework/07_PROMPT_GERADOR_DE_CASO.md` — **primário**: inserir o GATE ESTRUTURAL e a frase de enquadramento em `## ENTREGÁVEIS`.
- [ ] `docs/CASE_GENERATION_WORKFLOW.md` — nota na seção 2 (Geração) apontando o novo gate.
- [ ] `docs/BLUEPRINT_AUTHORING_GUIDE.md` — nota de cross-referência distinguindo o gate de forma do checklist narrativo existente.
- [ ] `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` — uma linha fechando o ciclo: o achado do STEP-02/STEP-03 (327 erros Pydantic) virou regra de processo via ISSUE-30.12.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — confirmar se a coluna "Atualizar quando" do `07_PROMPT_GERADOR_DE_CASO.md` já cobre o caso (provavelmente sim: "Muda entregáveis, formato ou gate da geração") — ✅ se não precisar de edição, com o motivo registrado.
- [ ] `docs/ESTADO_ATUAL.md` — uma linha registrando o novo gate.
- [ ] `CLAUDE.md` — atualizar o ponteiro de "próxima frente de trabalho" se a 30.12 for a issue ativa no momento do merge.

## Casos de teste

Issue de autoria/documentação; verificações objetivas (sem TDD de código):

- O `## GATE ESTRUTURAL` existe no 07, no local certo (entre o gate de qualidade narrativo e `## ENTREGÁVEIS`), sem alterar o gate narrativo existente.
- A frase de enquadramento aparece em `## ENTREGÁVEIS — NESTA ORDEM`.
- O comando citado no gate (`python -m generator.validator <arquivo>.json --strict`) é real e funciona: confirmar rodando contra um blueprint válido existente (ex. `examples/caso_canonico_iniciante.json`) sem erro de construção.
- Confirmar que o mesmo comando, contra uma cópia temporária deliberadamente malformada (um campo com tipo trocado, não persistida no repo), produz erro de construção — evidenciando que o gate captura exatamente a classe de problema observada na 30.11.
- `docs/CASE_GENERATION_WORKFLOW.md` e `docs/BLUEPRINT_AUTHORING_GUIDE.md` referenciam o gate pelo nome/local exato no 07, sem duplicar o texto do gate.
- `pytest tests/ -q` sem regressão (confirma que nenhum código foi tocado).

## Restrições arquiteturais

Sem código, sem schema novo, sem script novo. O gate usa exclusivamente comandos e mecanismos já existentes (`generator.validator`, construção Pydantic de `generator/models.py`). Linguagem em PT-BR, no tom imperativo já usado no restante do `framework/07`.

## Critério de aceite

- [ ] `GATE ESTRUTURAL` presente no `framework/07`, entre a Fase 1 e a Fase 2, sem alterar o gate narrativo existente.
- [ ] Frase de enquadramento presente em `## ENTREGÁVEIS — NESTA ORDEM`.
- [ ] Comando do gate confirmado funcional (positivo contra blueprint válido, negativo contra cópia malformada temporária).
- [ ] `docs/CASE_GENERATION_WORKFLOW.md` e `docs/BLUEPRINT_AUTHORING_GUIDE.md` referenciam o gate sem duplicar conteúdo.
- [ ] Impacto documental resolvido (✅/⏭️ por item), incluindo o fechamento de ciclo em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md`.
- [ ] `pytest tests/ -q` sem regressão.

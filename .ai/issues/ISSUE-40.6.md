# ISSUE-40.6 — Microidentidades institucionais

**Status:** especificada, pronta para execução
**Prioridade:** P1
**Depende de:** 40.3, 40.5
**Bloqueia:** —

## Objetivo

Criar o sistema de microidentidade que a 40.5 deixou como espaço em aberto: cada instituição fictícia dentro de um caso (o museu, uma empresa, um órgão) define sua própria cor, tipografia de destaque e forma de header — e todos os documentos daquela instituição herdam essa identidade, criando coesão intra-instituição e variação inter-instituição. É a mesma lição do benchmark: o jogador reconhece "isto veio do museu" em meio segundo porque manual, log de acesso, escala e cadastro compartilham o mesmo vermelho, o mesmo logotipo-busto, o mesmo recorte de header diagonal.

## Escopo

- Novo arquivo `styles/institution_identity.css` com os tokens de microidentidade.
- Biblioteca de 10-15 glifos abstratos de logo em `assets/logos/`.
- Aplicação aos templates institucionais existentes: manual, `06_log_acesso.html`, cadastro, listas (guarita).

**Não inclui** os 4 arquétipos comerciais de orçamento nem a escala/planilha nova — isso é P2/P3, fora deste lote.

## Doc-impact declarado (STEP-05)

- `templates/README.md`: documentar o sistema de microidentidade.
- `framework/09_SISTEMA_VISUAL.md`: adicionar seção "Microidentidades Institucionais", fechando o documento de doutrina aberto pela 40.2/40.3.

## Critério de aceite

1. `styles/institution_identity.css` define `--inst-color`, `--inst-font-display`, `--inst-header-shape` (reto | diagonal | faixa-dupla) como tokens configuráveis por instituição.
2. Biblioteca de glifos existe em `assets/logos/` com pelo menos 10 opções.
3. Manual, log de acesso e cadastro de uma mesma instituição fictícia (dado de teste) renderizam com a mesma cor, fonte de destaque e forma de header.
4. Manual tem "Revisão N — data" no header e assinatura do responsável no rodapé (achado específico do diagnóstico, seção 3.6).
5. Log de acesso tem carimbo de exportação com timestamp em segundos.
6. Teste automatizado comprova a coesão intra-instituição (item 3) usando dois conjuntos de dados de instituições diferentes.

## Passos (referência para o executor)

1. STEP-01 — Confirmar que 40.3 e 40.5 estão mescladas (dependência dura).
2. STEP-02 — RED: teste que renderiza os documentos de duas instituições fictícias de teste e falha se os documentos da mesma instituição não compartilharem cor/fonte/forma de header, ou se documentos de instituições diferentes compartilharem.
3. STEP-03 — GREEN: criar `institution_identity.css`, a biblioteca de glifos, e aplicar aos templates institucionais.
4. STEP-04 — Verificar visualmente com os dois conjuntos de teste.
5. STEP-05 — Docs: `templates/README.md` + fechar `framework/09_SISTEMA_VISUAL.md`.

Ver `ISSUE-40.6_SPEC.md` para o detalhamento técnico.

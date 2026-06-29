# Relatório de Calibração — Corpus de Referência Externo
**Caso:** Uma Noite Sem Flores
**Blueprint:** `examples/caso_referencia_uma_noite_sem_flores.json`
**ISSUE:** 30.8 — STEP-04
**Data:** 2026-06-29

> Este caso é corpus de **calibração externo, não canônico, não régua**. Não entra na promoção canônica. Não valida o framework; o framework é usado para analisar este caso.

---

## CR-01 — Tabela TR (tradução offline)

| ID | Gancho original | Decisão | Motivo | Implementação no blueprint |
|----|-----------------|---------|--------|---------------------------|
| TR-01 | "Falar com o delegado via QR/site" | **DESCARTADO** | Loop de validação externo; viola "offline first, sem dependência externa". | Substituído pela mecânica nativa: `criterio_de_avanco` por envelope + guia do facilitador. |
| TR-02 | Pistas restritas ao telefone/e-mail da compra | **DESCARTADO** | Conteúdo inacessível offline. Viola contrato offline-first. | Informação equivalente incorporada em documentos físicos (cartas, relatório). |
| TR-03 | Cartão "toda cor tem um código" (hex) | **IMPORTADO** | Traduz diretamente para pista offline legítima: código impresso num documento, chave em outro. | Campo `codigos` no blueprint com etiqueta `#7F004B`; chave de decodificação em E2-08 (catálogo da Arcano). |
| TR-04 | Mapa do museu | **ADIADO** | Custo de produção de planta P2 não justificado para corpus de calibração; referência espacial textual suficiente para o cruzamento central. | Mapa não presente no blueprint (registrado em `observacoes_producao`). Pode ser adicionado em iteração futura sem alterar lógica. |
| TR-05 | Registro das decisões | **FEITA** (meta) | Exigência da spec (TR-05 = esta tabela). | Este documento. |

---

## CR-02 — Saídas da pipeline

### Resultado por ferramenta

| Ferramenta | Comando | Status | Finding relevante | Classificação |
|------------|---------|--------|-------------------|---------------|
| `validator --strict` | `python -m generator.validator ... --strict` | ✅ exit 0 | 0 erros, 0 moderados, 14 avisos | — |
| `case_review` | `python scripts/case_review.py ...` | ✅ READY_FOR_BASELINE | 0 críticos, 1 warning (CR_DIFF_003) | — |
| `clue_graph` | `analyze_clue_graph(g, bp)` | ✅ passed | 1 path, depth=3; 11 GP_003; 1 GP_004; 0 GP_007 | — |
| `playtest_metrics` | `estimate_difficulty(bp)` | ✅ intermediario | match com declarado | — |
| `analyze_playtest` | — | warnings | 1 warning PT_001; cognitive_load: high | — |
| `obviousness_checker` | `check_obviousness(caso)` | ✅ limpo | findings: [] | — |

### Classificação dos findings individuais

| Código | Ferramenta | Mensagem | Classificação | Justificativa |
|--------|------------|----------|---------------|---------------|
| GP_003 × 11 | validator / clue_graph | Documentos E1-00, E1-01, E1-05, E1-06, E1-07, E1-08, E1-09, E2-00, E2-01, E2-04, E2-06 não participam de contratos de evidência | **Artefato de codificação** | Documentos de contexto, protocolo, escala, glossário, chat e depoimento por design não formam contrato. A métrica não distingue "documento de pista" de "documento de atmosfera/contexto". |
| GP_004 | validator / clue_graph | C-E1-DESCARTE não obrigatório nem final | **Falso positivo de métrica** | O contrato de descarte é design intencional: guia o grupo a descartar o red herring Rui sem ser gate de avanço. A métrica não reconhece o padrão "contrato de descarte". |
| ELENCO_001 | validator | Executor, planejador e beneficiário em apenas dois personagens | **Artefato de codificação** | Acúmulo de papéis Aurélio (planejador + beneficiário) + Sérgio (executor) é design editorial consciente para elenco enxuto. A métrica não distingue acúmulo intencional de falha estrutural. |
| PT_001 | validator / playtest_metrics | 19 documentos vs recomendado ≤ 18 para intermediário | **Falso positivo de métrica** | Um documento acima do limiar superior. O validator ele mesmo indica "contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada" (ISSUE-30.7). |
| CR_DIFF_003 | case_review | Volume documental incompatível com faixa editorial (19 vs 11–18) | **Falso positivo de métrica** | Mesma causa que PT_001. Métrica de volume, não de profundidade dedutiva. |

### Dados brutos das métricas

**analyze_playtest:**
```
difficulty_declared:  intermediario
difficulty_estimated: intermediario  ← MATCH
documents:            19
envelopes:            2
contracts (obrig.):   3
suspects:             6
red_herrings:         3
estimated_minutes:    90
cognitive_load:       high
warnings:             [PT_001]
issues (erros):       []
```

**clue_graph (analyze_clue_graph):**
```
status:               passed
nodes:                23
edges:                11
solution_targets:     1
solution_paths:       1  (depth = 3, atinge contrato final)
orphan_documents:     11  (todos GP_003)
orphan_contracts:     1   (C-E1-DESCARTE, GP_004)
GP_007 (caminho inexistente para contrato final): 0
```

**obviousness_checker:**
```
findings: []  (zero ocorrências OBV_*)
```

---

## CR-03 — Conclusão sobre a predição

**Pergunta:** As métricas de volume superdimensionam a dificuldade de um caso rico e validado externamente?

### Resposta: Sim, antes de ISSUE-30.7. Não, depois.

#### Antes de ISSUE-30.7 (estimador volumétrico)

O caso possui 19 documentos — um acima do limite superior de 18 para "intermediário". O estimador antigo usava contagem de documentos como sinal primário. Com 19 docs, a predição seria **"avançado"**, em conflito com a dificuldade declarada e com a estrutura real do caso (depth=3, que corresponde à faixa intermediária).

Resultado esperado antes de 30.7: **falso positivo de dificuldade** — o caso seria rotulado "avançado" por volume, não por profundidade dedutiva.

#### Depois de ISSUE-30.7 (estimador por profundidade)

O estimador retorna **"intermediario"** corretamente:
- Sinal primário: depth=3 → depth_score=1.0 (faixa baixa-intermediária)
- Outros sinais (ambiguidade, e2_score, density, mandatory_bonus) compõem o score total que mapeia para "intermediario"
- PT_001 é preservado como *aviso editorial informativo*, mas não conduz o estimate

O corpus externo, construído por fonte independente e considerado "intermediário" pelo material original, é classificado identicamente pelo estimador pós-30.7.

#### Sinal real identificado

O único finding que pode ser **sinal real** é o tempo estimado: `analyze_playtest` aponta 90 minutos enquanto o blueprint declara 100. Esta diferença de 10% pode indicar que o estimador de tempo subestima casos com documentos de contexto extensos (que consomem tempo de leitura mas não são contratos formais). Recomendação: não corrigir agora; registrar como dado de calibração para ISSUE-31+ (ajuste do estimador de tempo).

### Recomendações ao framework

| Recomendação | Ação | Prioridade |
|--------------|------|------------|
| **Manter PT_001 como aviso informativo** — nunca como bloqueante ou driver de estimate | Já implementado (ISSUE-30.7). Confirmar que nenhum código usa PT_001 para bloquear geração. | ✅ Feita |
| **Adicionar categoria "documento de contexto"** — distinguir pistas de atmosfera/protocolo nos contratos de evidência | Reducer da taxa de GP_003. Sem urgência editorial; aguardar evidência de mais casos. | Baixa |
| **Adicionar padrão "contrato de descarte"** — GP_004 não deveria disparar para contratos marcados como `tipo: descarte` | Requer mudança de schema. Aguardar mais casos antes de introduzir campo. | Baixa |
| **Calibrar estimador de tempo com docs de contexto** | Registrar delta 90min (estimado) vs 100min (declarado) como dado para ISSUE-31+. | ISSUE-31+ |

---

*Documento gerado automaticamente pelo STEP-04 da ISSUE-30.8. Não altera blueprint nem código.*

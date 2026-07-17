# ISSUE-33.10 — STEP-02: Investigação forense de H-E1a e H-E1b

## 1. H-E1a: Correspondência entre `key_evidence_ids` do E1 e `artifact_id` do bundle

### Tabela de cruzamento

| `key_evidence_id` esperado | `artifact_id` no manifest | Existência | Arquivo no player | Conteúdo resumido |
|---|---|---|---|---|
| ART-E1-02 | ✅ Presente (linha 60–69) | SIM | `player/E1-02.md` | Manual de controle de acessos; assinado por Aurélio Penha (ID 27); descreve porta 1 (biometria exclusiva), modo de contenção |
| ART-E1-03 | ✅ Presente (linha 70–79) | SIM | `player/E1-03.md` | Controle de acessos exportado; Aurélio (ID 27) cruza porta 1 às 15:20 (entrada) e 15:58 (saída) na janela da queda; Rui (ID 14) registra apenas na sala de segurança (portas 2 e 3) |
| ART-E2-04 | ✅ Presente (linha 180–189) | SIM | `player/E2-04.md` | Cadastro de terceiros da reforma; lista 4 fornecedores: Transvale Logística, Energia Plena, Aço Vivo Soluções, Acabamentos Vilela |
| ART-E2-03 | ✅ Presente (linha 170–179) | SIM | `player/E2-03.md` | Orçamento de Aço Vivo Soluções assinado por Sérgio Brum (Maçariqueiro); nota manuscrita menciona etiqueta hex #7F004B (cor da carga — Jardim consignação) |
| ART-E2-07 | ✅ Presente (linha 210–219) | SIM | `player/E2-07.md` | Controle da guarita; lista 6 funcionários terceirizados (Sérgio Brum: Maçariqueiro/Aço Vivo; 3 de Transvale); observação: registro incompleto à noite, algumas saídas não conferidas |
| ART-E2-08 | ✅ Presente (linha 220–229) | SIM | `player/E2-08.md` | Folha de decodificação de cartões; #7F004B → lote 'Jardim', consignação reservada; #4B8B00 → lote 'Marinha' |

### Veredito H-E1a

**Status**: ✅ **CONFIRMADA**

**Evidência**:
- Todos os 6 `key_evidence_ids` listados no E1 esperado (ART-E1-02, ART-E1-03, ART-E2-04, ART-E2-03, ART-E2-07, ART-E2-08) existem como `artifact_id` reais no manifest do bundle.
- Cada arquivo foi localizado no diretório `player/` com conteúdo que corresponde ao seu uso nos statements do E1.
- Nenhuma lacuna entre o esperado e o real.

**Conclusão**: A hipótese H-E1a (ids não correspondem a artifacts reais) é **descartada**. Os ids estão corretos e plenamente respaldados pelos documentos do bundle.

---

## 2. H-E1b: Correspondência entre statements do E1 e solução expressa no blueprint

### Comparação statement-a-statement

#### Statement 1: "culpado"

**Texto no E1 esperado** (expected_uma_noite_sem_flores.json, linhas 4–6):
```
"O chefe de segurança Aurélio Penha (credencial biométrica 27) é quem liberou 
o acesso interno à galeria principal na janela da queda de energia, permitindo 
a retirada da obra."
```

**Resposta esperada no blueprint** (linha 80–81, E1):
```
"A credencial biométrica interna que cruza a galeria na queda de energia é a 
do chefe de segurança Aurélio (ID 27); o recém-admitido Rui é descartado por 
ausência de oportunidade."
```

**Análise**: Semanticamente idêntico. Statement nomeia o culpado + ação (liberou acesso); resposta confirma credencial + descarta o red herring. Granularidade: ✓ Compatível (ID 27, nome, ação).

---

#### Statement 2: "metodo"

**Texto no E1 esperado** (linhas 10–11):
```
"Aurélio usou a janela da queda de energia planejada para cruzar a porta 
biométrica da galeria com a credencial 27; Sérgio Brum, maçariqueiro 
terceirizado, cortou a moldura-relíquia de carvalho para reduzir o volume da 
obra; a transportadora escoou a peça sob o BID da reforma até a consignação 
reservada da Arcano Gallery, identificada pela etiqueta hex #7F004B."
```

**Resposta esperada no blueprint** (linha 98, E2):
```
"Aurélio liberou o acesso interno; Sérgio Brum cortou a moldura-relíquia; 
a transportadora escoou a obra para a consignação reservada da Arcano Gallery, 
identificada pela etiqueta #7F004B."
```

**Análise**: Idêntico em estrutura e conteúdo. Statement detalha 3 elos (Aurélio + acesso → Sérgio + corte → transportadora + etiqueta); resposta condensa mas preserva todos os 3. Granularidade: ✓ Compatível (nomes, funções, etiqueta hex).

---

#### Statement 3: "motivo"

**Texto no E1 esperado** (linhas 15):
```
"Aurélio acumulava dívidas e viu na reforma e na queda de energia programada 
a oportunidade de liberar a obra para venda no mercado paralelo."
```

**Justificativa no blueprint** (linha 115):
```
"Aurélio acumulava dívidas e enxergou na reforma e na queda de energia 
programada a oportunidade de liberar a obra para venda no mercado paralelo."
```

**Análise**: Praticamente idêntico (sinônimo: "viu" ≈ "enxergou"). Granularidade: ✓ Compatível.

---

#### Statement 4: "descarte_rui"

**Texto no E1 esperado** (linhas 20):
```
"O recém-admitido Rui Caldas não é o autor: sua credencial não registra 
passagem pela galeria durante a janela crítica, apenas presença na sala de 
segurança."
```

**Descarte no blueprint** (linha 66):
```
"Rui (recém-admitido): descartado pelo log/escala — sem passagem pela galeria."
```

**Análise**: Idêntico em essência. Statement cita evidência (credencial + porta); descarte confirma a evidência. Granularidade: ✓ Compatível (ausência de oportunidade suficientemente nomeada).

---

### Veredito H-E1b

**Status**: ✅ **CONFIRMADA**

**Evidência**:
- Statement "culpado": Aurélio (ID 27) liberou acesso → Resposta E1 confirma credencial 27 cruzando galeria + descarta Rui.
- Statement "metodo": 3 elos (Aurélio + Sérgio + transportadora + etiqueta #7F004B) → Resposta E2 preserva todos os 3.
- Statement "motivo": dívidas + oportunidade de reforma/queda → Justificativa blueprint nomeia exatamente isso.
- Statement "descarte_rui": credencial sem passagem → Log de acessos (ART-E1-03) confirma.

**Conclusão**: A hipótese H-E1b (statements exigem fraseologia que o blueprint não expressa) é **descartada**. A solução transcrita no blueprint expressa exatamente a granularidade e a fraseologia esperadas pelo E1. Nenhuma divergência que exija reformulação.

---

## 3. Síntese

| Hipótese | Veredito | Motivo | Evidência |
|---|---|---|---|
| **H-E1a** | Descartada | Todos os 6 key_evidence_ids correspondem a artifact_id reais no manifest. | ART-E1-02, ART-E1-03, ART-E2-04, ART-E2-03, ART-E2-07, ART-E2-08 presentes; arquivos validados. |
| **H-E1b** | Descartada | Statements do E1 coincidem com solução expressa no blueprint. Granularidade e fraseologia compatíveis. | Culpado + Método + Motivo + Descarte: todos mapeados diretamente às respostas E1/E2 esperadas. |

---

## 4. Próximos passos

As duas hipóteses baratas foram julgadas. **Nenhuma escalação** disparou — ambos os artefatos (E1 esperado, blueprint, manifest) existem e coincidem.

Impacto: O "injusto" detectado na calibração não é causado por desalinhamento E1-vs-blueprint (H-E1a/H-E1b). A causa está em outro nível — possivelmente solver (H-Sa), judge (H-Ja/Jb), ou robustez operacional (H-Ra).

**Arquivo**: `.ai/runs/ISSUE-33.10/STEP-02_EXECUTION.md`

Próximo: STEP-03 (julgar H-Ja, H-Jb, H-Sa com run de vazamento METER_1784293071639_RUN_1).

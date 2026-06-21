# Execution Report — ISSUE-21 STEP-01

STEP: STEP-01
STEP_TYPE: reading
EXECUTION_STATUS: completed

## Arquivos lidos
- .ai/issues/ISSUE-21+22.md
- .ai/issues/ISSUE-21_SPEC.md
- generator/models.py
- generator/case_review.py
- generator/gate_evaluator.py

## Arquivos alterados
- nenhum (somente este execution report criado)

## Comandos executados
- nenhum

## Resultado

### Campos exatos do Blueprint (generator/models.py, class Blueprint)

Top-level relevantes:
- `tom: str`
- `objetivos_por_envelope: list[ObjetivoEnvelope]` (>=1)
- `executor_id: str`
- `planejador_id: str`
- `beneficiario_id: str`
- `motivacao: str`
- `cadeia_causal: list[str]` (>=3)
- `personagens: list[Personagem]` (>=4)
- `pilares_validacao: list[Pilar]` (==4)
- `documentos: list[Documento]` (>=8)
- `matriz_pistas: list[Pista]` (>=3)
- `red_herrings: list[RedHerring]` (>=2)
- `dicas: list[Dica]` (>=6)

Subcampos exatos:
- `Documento.codigo` (ex: "E1-01"), `.titulo`, `.envelope` (str "E1"/"E2"/"E3"), `.tipo` (TipoDocumento enum), `.pistas_contidas: list[str]`, `.conteudo: dict[str, Any]` (texto real em valores do dict — NAO existe campo plano `conteudo` string; conteudo e dict de placeholders), `.ids_citados: list[str]`, `.red_herring_potencial: Optional[str]`.
- `Personagem.id`, `.nome`, `.funcao`, `.papel` (PapelPersonagem enum), `.suspeita_aparente`, `.verdade`, `.documento_ancoragem: list[str]`.
- `Pista.descricao`, `.documento` (codigo doc), `.o_que_sugere`, `.o_que_prova`, `.confirmacao` (codigo doc), `.risco_ambiguidade`, `.emocao_esperada`. NAO existe campo `obrigatoria` em Pista.
- `Pilar.nome`, `.documento_principal` (codigo), `.confirmacao` (codigo), `.personagem_id`.
- `RedHerring.personagem_id`, `.motivo_aparente`, `.como_descartar`, `.documento_descarte` (codigo), `.categoria`.
- `Dica.numero`, `.intensidade` (Intensidade enum), `.envelope` (str), `.condicao_uso`, `.texto`, `.o_que_desbloqueia`. Dica NAO referencia documento por campo dedicado; eventual referencia a doc esta em texto livre `.texto`/`.condicao_uso`/`.o_que_desbloqueia`.
- `ObjetivoEnvelope.envelope` (str), `.pergunta_diegetica`, `.resposta_esperada`, `.nao_precisa_resolver_ainda: list[str]`, `.criterio_de_avanco`, `.forma_diegetica_de_avanco`, `.documentos_minimos: list[str]`.

### PapelPersonagem enum (valores exatos)
executor | planejador | beneficiario | narrador | red_herring | testemunha | cumplice | intermediario.
NAO existe papel literal "suspeito" nem "vitima". NR_003 ("papel suspeito") e NR_007 ("vitima") devem mapear para heuristica sobre papeis existentes — registrar como ponto de atencao para STEP-06/07.

### Mapa por regra NR_* (campos acessados)

- NR_001 — `documentos[].conteudo` (valores do dict `Documento.conteudo`). Regex linguagem interpretativa ("portanto", "claramente", "isso prova"). Filtrar docs de jogador (todos `documentos` sao de jogador; nao ha flag).
- NR_002 — `documentos[].tipo` (TipoDocumento). Checar nome/tipo que revela papel investigativo ("PISTA"/"EVIDENCIA" literal). Tambem pode usar `Documento.titulo`.
- NR_003 — `personagens` (`Personagem.papel`) + `executor_id`. Heuristica: nenhum personagem com papel suspeito plausivel alem do executor. Sem papel "suspeito": usar red_herring/intermediario/cumplice como proxy de suspeito alternativo.
- NR_004 — `motivacao` + `documentos`. Motivacao do executor nao sustentada por nenhum documento (busca textual de termos da `motivacao` em `Documento.conteudo`/`Documento.objetivo_narrativo`).
- NR_005 — `tom` + `documentos`. Tom declarado vs tom dos documentos (heuristica: linguagem informal em `Documento.conteudo` quando `tom` serio/policial).
- NR_006 — `dicas` + `documentos`. Dica referencia documento inexistente. Referencia em texto livre de `Dica.texto`/`.condicao_uso`/`.o_que_desbloqueia`; comparar codigos contra `{d.codigo}`.
- NR_007 — `documentos` + `personagens` + `executor_id`. Menos de 2 documentos pertencem a personagens que nao sao executor nem vitima. Pertencimento via `Documento.ids_citados`/`Documento.codigo` mapeado a `Personagem.documento_ancoragem`; "vitima" nao e papel — derivar (ex.: personagem citado na pergunta/conflito) ou tratar como nao-executor.
- NR_008 — `red_herrings` + `documentos`. Red herring sem documento associado: `RedHerring.documento_descarte` ausente de `{d.codigo}`, ou `RedHerring.personagem_id` sem `documento_ancoragem` valido.

### Mapa por regra ER_* (campos acessados)

- ER_001 — `matriz_pistas[].documento` (e `.confirmacao`) vs `{d.codigo for d in documentos}`. Pista referencia documento inexistente.
- ER_002 — `pilares_validacao` + `matriz_pistas`. Pilar sem pista que o suporte. Liga `Pilar.documento_principal`/`.confirmacao`/`.personagem_id` a `Pista.documento`/`.confirmacao`.
- ER_003 — `cadeia_causal: list[str]`. len < 3 elos.
- ER_004 — `objetivos_por_envelope[].envelope` + `matriz_pistas`. Envelope sem pista designada. Pista nao tem campo envelope direto; derivar via `Pista.documento` -> `Documento.envelope`.
- ER_005 — `matriz_pistas[].documento`. >60% das pistas no mesmo documento (concentracao).
- ER_006 — `red_herrings` + `matriz_pistas`. Red herring sem pista que contradiga/contextualize. Liga `RedHerring.documento_descarte`/`.personagem_id` a `Pista.documento`/`.o_que_prova`.
- ER_007 — `matriz_pistas` + `documentos` (E1). Pista marcada obrigatoria nao disponivel no E1. ATENCAO: `Pista` NAO tem campo `obrigatoria`. Proxy: `ContratoEvidencia.obrigatoria_para_avanco` (Blueprint.contratos_evidencia) ou tratar todas como nao-obrigatorias. Registrar divergencia de campo para STEP-08/09.
- ER_008 — `documentos` + `matriz_pistas`. <40% dos documentos contribuem para >=1 pista. Doc contribui se `d.codigo` aparece em `Pista.documento`/`.confirmacao` (ou via `Documento.pistas_contidas`).

### Padroes de finding/dataclass/builder capturados

- gate_evaluator.py: `@dataclass(frozen=True)` para todos os tipos publicos; SCHEMA carregado via `yaml.safe_load(Path(...).read_text("utf-8"))`; validacao via `Draft202012Validator(schema, format_checker=FormatChecker())`; `iter_errors(dict(...))`; retorno `sorted(error.message ...)`; regras codificadas como funcoes privadas retornando `list[str]` com prefixo de codigo na mensagem ("GE_001: ..."); status/decision derivado das severidades (critical bloqueia). SCHEMA_VERSION = "1.0".
- case_review.py: `@dataclass(frozen=True)` `CaseReviewFinding(code, severity, message, section, detail)`; helper `_finding(...)`; helpers de leitura de blueprint: `_document_codes(bp) -> {d.codigo}`, `_objective_envelopes(bp) -> {o.envelope}`; status derivado por severidade em `_status_for` (critical -> BLOCKED; N warnings -> NEEDS_REVIEW); serializacao via `asdict`. Modelo direto para `ReviewFinding`/`ReviewReport`/`report_to_dict` da spec.

## Divergências
- DVG-EXEC-001: `Pista` (matriz_pistas) NAO possui campo `obrigatoria` citado em ER_007 da spec. `Documento` tampouco. Flag de obrigatoriedade existe apenas em `ContratoEvidencia.obrigatoria_para_avanco`. Impacto: nao impede STEP-01; exige decisao de mapeamento em STEP-08/09 (usar contratos_evidencia como proxy ou neutralizar ER_007). Nenhuma alteracao feita.
- DVG-EXEC-002: PapelPersonagem nao tem valores "suspeito" (NR_003) nem "vitima" (NR_007/NR_008). Impacto: nao impede STEP-01; NR_003/NR_007 precisam heuristica sobre papeis existentes (red_herring/intermediario/cumplice como suspeito; vitima derivada). Registrado para STEP-06/07.
- DVG-EXEC-003: `Documento.conteudo` e `dict[str, Any]` (placeholders), nao string plana. NR_001/NR_004/NR_005 devem varrer valores str do dict, nao um campo `conteudo` textual unico. Impacto: ajuste de leitura em STEP-07.

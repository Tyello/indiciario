# Auditoria técnica — Indiciário — julho/2026 (Fable)

Auditoria somente-leitura de código, documentação e arquitetura. Executada em 2026-07-09, branch `main` limpa (HEAD `e7fd22b`). Nenhum arquivo alterado além deste relatório. Blind solver LLM **não** foi executado (sessão tem acesso ao gabarito — rodar violaria protocolo cego).

---

## 1. Sumário executivo

Núcleo técnico é sólido: validator strict passa nos dois canônicos, protocolo cego bem implementado (harness nega leitura fora do bundle, LS_003 sobrescreve ids, CJ_004/SM_003 derivados em Python puro, zero código de rede em `generator/` e `tests/`), schemas de pipeline todos com `additionalProperties: false`, não-mutação de canônicos garantida em runtime (`pipeline_runner.py:295`).

Problema central: **CI está vermelha no `main` desde pelo menos 2026-07-07** (8+ runs consecutivas falhando no step Lint). Como o Lint falha antes de `pytest` e dos validators, **nenhum teste roda em CI há dias** — os commits recentes (33.2, 40.5, 40.6) entraram sem prova automatizada. Documentação de estado descolou do código: a série ISSUE-40.x inteira (6 issues, código entregue) não existe em `ROADMAP.md` nem em `ESTADO_ATUAL.md`; contagens de teste divergem (CLAUDE.md ~1385, ESTADO_ATUAL ~1464, real 1511); o espelho `docs/prompts/` diverge de `.ai/skills/` em todos os 9 pares. Segundo risco real: `pipeline_runner.py` aprova o gate com `decision="approved"` e `met=True` **hardcoded**, mesmo quando um solver LLM real é injetado — o Conclusion Judge (33.1) existe mas não está ligado ao runner.

## 2. Verificações executadas

| Comando | Resultado bruto |
|---|---|
| `pytest tests/ -q` (venv local, Windows) | **5 failed, 1503 passed, 3 skipped** em 222s (1511 coletados). Falhas: todas `OSError [WinError 1314]` ao criar symlink sem privilégio (`test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`, `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`, `::test_symlink_manifest_fails`, `::test_bundle_path_missing_file_and_symlink_fail`, `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`) |
| `ruff check generator/` | **All checks passed** |
| `ruff check tests/` | **55 erros**: 51× F811 (`test_blind_solve_run_record.py`), 4× F401 (`test_accessibility_reviewer.py:35`, `test_gate_font_fidelity.py:31`, `test_pipeline_runner.py:16`, `test_quality_comparative_reviewer.py:22`) |
| `python -m generator.validator examples/caso_canonico_iniciante.json --strict` | Risco Baixo, PODE GERAR. 11 avisos (6× GP_003, GP_004, AUTO_001, PT_001/003/007) |
| `python -m generator.validator examples/caso_canonico_intermediario.json --strict` | Risco Baixo, PODE GERAR. 7 avisos (ELENCO_001, 2× GP_003, 3× GP_004, AUTO_001) |
| `grep TODO\|FIXME\|XXX\|HACK` em generator/tests/framework/docs | Zero TODO/FIXME real em código (só falsos positivos: `COLUNA_METODO`, menções editoriais a "TODO proibido") |
| `gh run list` | **CI failure no `main` nas 8 runs mais recentes** (2026-07-07 a 2026-07-09). Log da última: falha no step Lint com exatamente os 55 erros acima |

## 3. BUGS — defeitos reais

### BUG-01 — CRITICO — CI vermelha no `main`; testes não rodam em CI desde ≥ 07/jul
- **Arquivo:** `.github/workflows/ci.yml:34` + `tests/test_blind_solve_run_record.py:38-48` + 4 arquivos com F401.
- **Evidência:** CI roda `ruff check generator/ scripts/ tests/`; `tests/` tem 55 erros. `test_blind_solve_run_record.py` importa fixtures (`source_tree`, `output_root` com `# noqa: F401`) e as reusa como nome de parâmetro em 25+ funções → F811. Log do run `2026-07-09T20:13` falha no Lint; steps Tests/Strict validators nunca executam.
- **Por que importa:** commits das ISSUE-33.2, 40.5, 40.6 entraram no `main` sem nenhuma execução de `pytest`/validator em CI. O pipeline verde que o projeto exibe como garantia não existe hoje.
- **Correção:** mover import de fixtures para `tests/conftest.py` (elimina F811 por design — fixtures em conftest ficam disponíveis sem import) ou renomear parâmetros das helpers; remover os 4 imports não usados (`ruff check tests/ --fix` resolve os F401). Rodar `ruff check generator/ scripts/ tests/` localmente antes de push (comando obrigatório em CLAUDE.md cobre só `generator/` — ver DIV-08).

### BUG-02 — ALTO — 5 testes de symlink quebram em Windows sem guard de skip
- **Arquivo:** `tests/test_blind_bundle_generator.py`, `tests/test_blind_bundle_leak_checker.py:357`, `tests/test_blind_bundle_sanitizer.py:249`.
- **Evidência:** `link_dir.symlink_to(real_dir, ...)` → `OSError: [WinError 1314] O cliente não tem o privilégio necessário`. O padrão correto já existe no próprio repo: `tests/test_learning_ledger_cli.py:206` faz `pytest.skip("symlinks not supported")` no mesmo cenário.
- **Por que importa:** `pytest tests/ -q` (comando obrigatório) nunca fica verde na máquina de desenvolvimento Windows; run da ISSUE-33.2 (STEP-07) já registrou essas falhas como "pré-existentes" e seguiu adiante — normalização de suite vermelha.
- **Correção:** capturar `OSError` na criação do symlink e `pytest.skip`, igual aos testes do learning ledger.

### BUG-03 — MEDIO — `LLMBlindSolver` estoura com exceção crua se o LLM devolver JSON não-objeto ou `warnings` não-lista
- **Arquivo:** `generator/llm_blind_solver.py:109-112`.
- **Evidência:** `_parse_json_with_repair` retorna qualquer `json.loads` válido (lista, string, número). Em seguida `result_dict.pop("warnings", [])` → `AttributeError` se lista; se `warnings` vier como string, `warnings_list.extend(...)`/`append` corrompe ou estoura.
- **Por que importa:** contrato do módulo promete `BlindSolverHarnessError` em falha de parsing/validação; um modelo real vai eventualmente devolver `[...]` ou `"warnings": "nenhum"` e o meter (SM_002) só captura `ProviderError/BlindSolverHarnessError/ConclusionJudgeError` — `AttributeError` mata a medição inteira em vez de contar run incompleta.
- **Correção:** após parse, exigir `isinstance(result, dict)` (senão disparar reparo/`BlindSolverHarnessError`); normalizar `warnings` para lista de str.

### BUG-04 — MEDIO — `evidence_used` malformado vira `TypeError` cru
- **Arquivo:** `generator/llm_blind_solver.py:127-129`.
- **Evidência:** `BlindSolverEvidence(**evidence)` — item com campo extra (ex.: `"page": 2`) ou item não-dict → `TypeError: unexpected keyword argument`. `_discard_extra_fields` (linha 224) só limpa campos extras do nível raiz.
- **Por que importa:** mesma consequência do BUG-03: quebra o contrato de erro e derruba `measure_solvability`.
- **Correção:** filtrar chaves de cada item de evidência pelos `fields(BlindSolverEvidence)` com warning, e validar tipo dict antes do unpack.

### BUG-05 — MEDIO — `max_repair_attempts` aceita N mas executa no máximo 1 reparo
- **Arquivo:** `generator/llm_blind_solver.py:58`, `:190-216`.
- **Evidência:** docstring "Repairs invalid JSON responses (up to max_repair_attempts)"; implementação: `if self.max_repair_attempts > 0:` → um único retry, sem loop. `LLMBlindSolver(provider, max_repair_attempts=3)` se comporta igual a `=1`.
- **Correção:** loop `for attempt in range(self.max_repair_attempts)` (o judge em `conclusion_judge.py` tem loop de reparo de verdade — usar como referência) ou renomear parâmetro para booleano honesto.

### BUG-06 — BAIXO — `temperature` do Solvability Meter é parâmetro morto
- **Arquivo:** `generator/solvability_meter.py:98`, `:123-127`.
- **Evidência:** docstring "Recorded for reproducibility"; o valor é validado (SM_001) e depois **nunca usado**: não vai no `SolvabilityReport` (schema `solvability_report.schema.yaml` não tem campo), não é repassado ao solver/judge (ambos hardcodam `temperature=0.0` no `ProviderRequest`).
- **Por que importa:** com temperature efetiva 0.0 e mesmo bundle, N runs contra um provider determinístico produzem o mesmo resultado — `solve_rate` degenera para 0 ou 1 e o meter mede quase nada além de variância do provider. A premissa da ISSUE-33.2 ("executá-lo N vezes **com temperatura**") não está implementada.
- **Correção:** registrar `temperature` no report e/ou repassar ao `ProviderRequest` do solver (decisão de escopo a registrar).

### BUG-07 — BAIXO — Substituição de placeholder após injeção de conteúdo de artefato
- **Arquivo:** `generator/llm_blind_solver.py:87-94`.
- **Evidência:** `{included_artifacts}` é substituído primeiro; `{solver_run_id}`/`{bundle_id}`/etc. são substituídos depois, sobre o prompt já contendo texto dos artefatos. Artefato contendo o literal `{bundle_id}` teria o valor real injetado.
- **Por que importa:** superfície mínima de injeção via conteúdo do bundle; ids não são segredo, mas viola higiene do protocolo.
- **Correção:** substituir ids primeiro, artefatos por último.

### BUG-08 — BAIXO — Typo em id de conclusão esperada
- **Arquivo:** `generator/pipeline_runner.py:646`.
- **Evidência:** `id=f"EC-GUia-{index}"` (casing "GUia").
- **Por que importa:** ids aparecem em manifests e relatórios comparativos; typo se propaga para artefatos versionados.

## 4. RISCOS — invariantes

### RISCO-01 — ALTO — Gate do pipeline aprova hardcoded, mesmo com solver real
- **Arquivo:** `generator/pipeline_runner.py:409` (`decision="approved"`), `:635` e `:649` (`met=True`).
- **Evidência:** `_run_gate` fabrica decisão aprovada e todas as conclusões esperadas com `met=True`, incondicionalmente. O parâmetro `solver` (ISSUE-33) troca o stub, mas o veredito do gate continua fabricado; `judge_conclusions` (ISSUE-33.1, criado exatamente para alimentar `met`) não é invocado em nenhum ponto do runner.
- **Por que importa:** um run com `LLMBlindSolver` real produz manifest com gate "approved" que não reflete o desempenho do solver. As limitações documentadas em `ESTADO_ATUAL.md:84-89` citam o stub e os reviewers ausentes, mas **não** citam o gate fabricado — é a lacuna mais enganosa do pipeline hoje. Um manifest desses alimentado no Canonical Quality Gate conta `stages_completed` e `pipeline_status` sem bloqueio.
- **Correção:** quando `solver` real for injetado, rotear report → `judge_conclusions` → `met` real (proposta EVO-01); enquanto não fizer, adicionar a limitação em `ESTADO_ATUAL.md` e `CLAUDE.md`.

### RISCO-02 — MEDIO — Harness não exige que evidência citada tenha sido lida
- **Arquivo:** `generator/blind_solver_harness.py:434-445`.
- **Evidência:** `_validate_report_semantics` valida que `evidence_used.artifact_id` existe no bundle e que o path bate, mas não cruza com `context.accessed_artifacts`. Solver pode citar artefato incluído que nunca abriu.
- **Por que importa:** enfraquece a auditabilidade do run cego (o log de acessos existe justamente para isso); um solver LLM pode "chutar" citações plausíveis pelos metadados listados no prompt.
- **Correção:** warning (ou erro RV novo) quando `evidence_used` cita artifact_id ∉ `accessed_artifacts`. Nota: no `LLMBlindSolver` atual todos os artefatos são lidos para montar o prompt, então hoje é teórico — vira real com solvers de leitura seletiva.

### RISCO-03 — BAIXO — Lint local obrigatório não cobre o que o CI cobre
- **Arquivo:** `CLAUDE.md` ("Comandos obrigatórios": `ruff check generator/`) vs `.github/workflows/ci.yml:34` (`ruff check generator/ scripts/ tests/`).
- **Por que importa:** é a causa-raiz do BUG-01 — o agente cumpre o protocolo local, o CI quebra depois. Regra local mais fraca que o gate remoto é armadilha estrutural.
- **Correção:** alinhar CLAUDE.md/AGENTS.md para `ruff check generator/ scripts/ tests/`.

### RISCO-04 — BAIXO — Verdict do judge não é revalidado contra o schema na saída
- **Arquivo:** `generator/conclusion_judge.py:194-203`.
- **Evidência:** schema é aplicado ao JSON cru do modelo (`_validate_verdict_schema(raw_verdict_dict)`), mas o `JudgeVerdict` final é construído com defaults (`verdict_id=f"VERDICT_{timestamp}"`, `report_run_id` pode ser `""` se o report não tiver `solver_run_id`/`run_id`) que podem violar `minLength: 2` do `judge_verdict.schema.yaml` sem detecção.
- **Correção:** serializar o verdict final e revalidar, ou garantir defaults conformes.

Invariantes verificados e **OK**:
- **LS_001** — teste-sentinela real em `tests/test_llm_blind_solver.py:234-280` (arquivo fora do bundle com string única; assert de ausência no prompt). Harness nega leitura fora de `included_artifacts` com trilha de negações (`blind_solver_harness.py:204-247`); path traversal bloqueado via `_bundle_child` (resolve + is_relative_to) e symlinks rejeitados.
- **LS_003** — ids sempre sobrescritos do contexto (`llm_blind_solver.py:133-139`), com revalidação pós-override.
- **CJ_004/CJ_005** — classificação e rebase derivados em Python puro (`conclusion_judge.py:169-191`, `:321-358`); CJ_003 exige toda conclusão esperada presente (`:153-157`).
- **SM_003/SM_004** — `estimate_difficulty` e flags em Python puro (`solvability_meter.py:82-90`, `:184-190`).
- **CI offline** — zero import de rede/provider real/API key em `tests/` e `generator/` (grep `requests|httpx|socket|api_key|anthropic|openai`: só docstrings). `FakeProvider` cobre a fase LLM.
- **additionalProperties: false** — presente nos 13 schemas JSON-Schema de `schemas/`; nenhum `additionalProperties: true` em lugar algum. (`generator/schemas/*.yaml` são contratos de template em formato próprio, não JSON Schema — fora do escopo do invariante.)
- **Não-mutação de canônicos** — nenhum path `examples/` hardcoded em `generator/`; `pipeline_runner.py:225,295` compara bytes do blueprint antes/depois e levanta `RuntimeError` se mudou.

## 5. DIVERGÊNCIAS DOC↔CÓDIGO

| # | Divergência | Evidência | Correção |
|---|---|---|---|
| DIV-01 | Série **ISSUE-40.1–40.6 inteira ausente** de `ROADMAP.md` e `ESTADO_ATUAL.md` | `grep "40\." docs/ROADMAP.md docs/ESTADO_ATUAL.md` → zero. Código entregue: `generator/font_fidelity.py`, `evaluate_font_fidelity` no gate, `framework/20_SISTEMA_VISUAL.md`, runs em `.ai/runs/ISSUE-40.*`, commits `40.5`/`40.6` no topo do log. CLAUDE.md manda "confirmar estado em ESTADO_ATUAL antes de iniciar" — o doc que prevalece sobre estado não sabe da frente mais recente | Seção "Fase — Sistema visual 40.x" no ROADMAP + parágrafo no ESTADO_ATUAL |
| DIV-02 | CLAUDE.md: "ISSUE-30.12 **em andamento**" | `.ai/issues/ISSUE-30.12.md:6` `STATUS: done`; run até STEP-06; gate estrutural já presente em `framework/07_PROMPT_GERADOR_DE_CASO.md:63` | Atualizar ponteiro de próxima issue no CLAUDE.md |
| DIV-03 | Contagem de testes: CLAUDE.md "~1385", ESTADO_ATUAL "~1464", real **1511 coletados** | `pytest -q`: 5+1503+3 | Atualizar ambos (ou parar de fixar número em dois lugares — deixar só no ESTADO_ATUAL) |
| DIV-04 | `framework/00_README.md` tabela de ordem termina em 19 + CONTEUDO_SCHEMA; **`20_SISTEMA_VISUAL.md` fora da tabela** | `framework/00_README.md:38-59`; índice manda: "Ordem/numeração de arquivos do framework/ → reveja framework/00_README.md" | Adicionar linha 20 |
| DIV-05 | `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` **fora do INDICE_DOCUMENTACAO** | único doc de `docs/*.md` sem menção no índice (verificação exaustiva); regra do próprio índice: "criar doc novo sempre obriga atualizar este índice" | Adicionar entrada |
| DIV-06 | `examples/caso_gerado_cooperativa.json` fora do roster de `ESTADO_ATUAL.md` e `AGENTS.md` (CLAUDE.md tem) | ESTADO_ATUAL:113 diz "existem outros **três** casos"; tabela :117-124 lista 6, sem o Grão que Faltou. `examples/` também contém `showcase_tecnico.json` e `sinal_verde_demo_blueprint.json` não classificados em doc nenhum | Roster único no ESTADO_ATUAL (que prevalece) incluindo cooperativa; classificar/aposentar showcase e sinal_verde |
| DIV-07 | `docs/GUIA_CODIGOS_ERROS.md` **sem nenhum código RV_/PV_/FP_/LS_/CJ_/SM_** | grep → zero; gatilho reverso do índice: "novos códigos de erro/aviso → GUIA_CODIGOS_ERROS.md". Seis famílias de código nasceram das ISSUE-17/31/32/33/33.1/33.2 e só existem em docstrings/specs | Ou registrar as famílias no guia, ou declarar no guia que ele cobre só códigos do validator (e onde ficam os demais) |
| DIV-08 | Comando lint obrigatório (CLAUDE.md/AGENTS.md: `ruff check generator/`) ≠ CI (`generator/ scripts/ tests/`) | ver RISCO-03 | Alinhar docs |
| DIV-09 | Espelho `docs/prompts/` diverge de `.ai/skills/` em **9 de 9 pares** | `Compare-Object` por par: 69–120 linhas diferentes cada (diagnose 92, README 120, tdd 79…). Índice: "manter em sincronia" | Regravar espelho a partir de `.ai/skills/` (fonte de verdade) ou aposentar o espelho no índice |
| DIV-10 | `.ai/runs/ISSUE-32` **não existe** (31, 33, 33.1, 33.2 existem) | listagem de `.ai/runs/` | Aceitável (índice marca runs como transientes), mas registrar a lacuna na issue |
| DIV-11 | Headers de status contraditórios nas issues 40.x | `ISSUE-40.1.md:3` "especificada, pronta para execução" vs `:58` "Status: done — aprovado"; 40.3/40.4/40.5 têm `STATUS: done` + "especificada" simultâneos | Normalizar um campo STATUS único |
| DIV-12 | ROADMAP/ESTADO: judge "alimenta campo met do Gate Evaluator" | capacidade existe (`judge_conclusions`), mas nenhum chamador real: `pipeline_runner` hardcoda `met=True` (RISCO-01) | Reescrever como "pode alimentar" + limitação explícita |

## 6. MELHORIAS — dívida técnica priorizada

1. **Padrão de import de fixtures** (`tests/test_blind_solve_run_record.py`): mover fixtures compartilhadas para `tests/conftest.py` em vez de import + `noqa`. Elimina a classe inteira de F811/F401 que derrubou o CI.
2. **Nome duplicado `estimate_difficulty`** em `generator/playtest_metrics.py:124` (blueprint→nível) e `generator/solvability_meter.py:82` (solve_rate→nível). Semânticas diferentes, mesmo nome público — renomear um (ex.: `estimate_difficulty_from_solve_rate`).
3. **Reprodutibilidade do SolvabilityReport**: gravar `temperature`, `prompt_template_sha256` do solver e `prompt_hash` do judge no report (hoje só o judge registra hash; o meter não registra nada do setup).
4. **Encoding do CLI do validator no Windows**: saída com mojibake (`VALIDA��O`) em console cp1252 — `sys.stdout.reconfigure(encoding="utf-8")` no entrypoint.
5. **Worktree órfão** `.claude/worktrees/agent-adcf344320e399483/` com cópia parcial do repo — lixo de agente; remover (`git worktree prune` + delete).
6. **Dois entrypoints do validator** (`python -m generator.validator` no CLAUDE.md, `python generator/validator.py` no AGENTS.md/CI) — funcionam, mas padronizar em `-m` evita dupla manutenção de sys.path.
7. **`_density_and_document_count`** (`canonical_quality_gate.py:182-188`) chama helpers de comparação passando o mesmo blueprint duas vezes e lê `.aurora_value` — funciona, mas o acoplamento com privates `_case_metrics`/`_densidade_documental_comparison` merece extração de função pública compartilhada.

## 7. EVOLUÇÕES — propostas coerentes com o roadmap

Numeração sugerida: série **33.x** continua a fase Provider; **41.x** abre frente de saúde de engenharia (40.x já ocupada pela frente visual).

| Issue candidata | Objetivo (1 frase) | Dependências | Esforço |
|---|---|---|---|
| **ISSUE-41.1 — CI verde de novo** | Corrigir os 55 erros de lint em `tests/`, adicionar skip-guard de symlink nos 5 testes Windows e alinhar comando de lint local↔CI, devolvendo prova automatizada ao `main`. | nenhuma | **P** |
| **ISSUE-33.3 — Ligar Conclusion Judge ao pipeline_runner** | Quando `solver` real for injetado, substituir `met=True`/`decision="approved"` hardcoded por veredito real via `judge_conclusions`, mantendo o stub como default backward-compatible. | 33.1 (pronta) | **M** |
| **ISSUE-33.4 — Hardening do adapter LLM** | Fechar BUG-03/04/05/07: JSON não-objeto, evidência malformada, loop real de reparo e ordem de substituição de placeholders, tudo coberto com `FakeProvider`. | 33 | **P** |
| **ISSUE-33.5 — Metadados de reprodutibilidade no Solvability Meter** | Registrar temperature/prompt-hashes/provider-id no `SolvabilityReport` (e decidir se temperature é repassada ao solver), atualizando o schema. | 33.2 | **P** |
| **ISSUE-41.2 — Guard de sincronia do espelho docs/prompts** | Script offline (rodando no CI) que falha quando `docs/prompts/` divergir de `.ai/skills/`, ou decisão de aposentar o espelho. | 41.1 | **P** |
| **ISSUE-41.3 — Reconciliação de estado documental** | Uma passada única: 40.x no ROADMAP/ESTADO, ponteiro 30.12, contagem de testes, roster com cooperativa/showcase/sinal_verde, framework/00 linha 20, EXPERIMENTO no índice, famílias de código no GUIA_CODIGOS_ERROS. | nenhuma | **M** |
| **ISSUE-33.6 — Evidência citada ⊆ evidência lida** | Warning/erro no harness quando `evidence_used` referencia artefato nunca acessado no round (fecha RISCO-02 antes de solvers seletivos). | 33 | **P** |

Não proposto de propósito: provider concreto de rede (é a ISSUE-34+ existente e exige decisão humana de custo/segredo), qualquer mudança editorial nos canônicos, e qualquer coisa da lista "nunca fazer por iniciativa própria".

## 8. TOP 5

1. **ISSUE-41.1 (CI verde)** — enquanto o Lint derruba o workflow, todo o resto da auditoria é teórico: não há prova automatizada de nada que entrou no `main` desde 07/jul. Custo P, destrava tudo.
2. **Skip-guard de symlink nos 5 testes** (parte da 41.1) — devolve `pytest tests/ -q` verde na máquina real de desenvolvimento; suite local vermelha "conhecida" treina o time a ignorar vermelho.
3. **ISSUE-33.3 (judge no runner)** — é a diferença entre um pipeline que *parece* avaliar solvers reais e um que avalia; sem isso, qualquer run com `LLMBlindSolver` gera manifest com aprovação fabricada (RISCO-01), o tipo exato de autoengano que o protocolo cego existe para impedir.
4. **ISSUE-41.3 (reconciliação documental)** — ESTADO_ATUAL é declarado fonte de verdade e hoje desconhece a frente 40.x inteira, o caso cooperativa e a contagem real de testes; agentes que obedecem o protocolo leem estado errado a cada tarefa.
5. **ISSUE-33.4 (hardening do adapter)** — os bugs de parsing (BUG-03/04) são os primeiros que um modelo real vai acionar em produção, e hoje derrubam o Solvability Meter inteiro em vez de degradar para run incompleta.

---

*Gerado por auditoria somente-leitura em 2026-07-09. Nenhum código corrigido durante a auditoria, conforme instrução.*

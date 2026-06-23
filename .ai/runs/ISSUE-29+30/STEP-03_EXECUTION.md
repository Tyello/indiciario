# STEP-03 — Preparação do blueprint Fintech — Execution Report

Type: green (high-risk). Status: in_review. Aguarda revisão antes de avançar para STEP-04.

## Contexto lido antes de escrever

- `generator/models.py` (íntegro, linhas 1-625): modelo Pydantic `Blueprint` e todos os modelos aninhados (`Documento`, `Personagem`, `Pilar`, `RedHerring`, `Pista`, `Dica`, `ContratoEvidencia`, `SaltoFinanceiro`, etc.), enums (`Dificuldade`, `PapelPersonagem`, `TipoDocumento`, `Envelope`).
- `examples/caso_canonico_intermediario.json` (íntegro, Aurora) — referência estrutural real e válida.
- `.ai/issues/ISSUE-29+30_SPEC.md` seção "Blueprint Fintech: estrutura esperada" — tema, personagens, documentos exigidos.
- `.ai/runs/ISSUE-29+30/STEP-01_EXECUTION.md` — mapeamento prévio do schema e comando de validação.
- `generator/validator.py` (regras `_verificar_*`) — guardrails editoriais acima da validação Pydantic: elenco, documentos, grafo de pistas (`clue_graph.py`), pilares, pistas, red herrings, linha do tempo, dicas, dicas contextuais, autossuficiência, schema de conteúdo por tipo de documento (`generator/schemas/*.yaml`), manuscritos, anti-obviedade (`obviousness_checker.py`).
- `generator/schemas/*.yaml` (extrato, contrato, email_institucional, log_acesso, depoimento, chat, boletim, folha_cruzamento, glossario, manual, protocolo) — campos obrigatórios exatos de `conteudo` por tipo de documento.
- `generator/clue_graph.py` — regras `GP_001`–`GP_007` (grafo de pistas/contratos de evidência), incluindo exigência de um contrato com `fase=="final"` ou `tipo=="solucao_final"` (`GP_006`) e de que todo documento participe de algum contrato via `prova_principal`/`confirmacao_independente`/`descarta_alternativas` (`GP_003`).

Comando de validação confirmado (igual ao mapeado em STEP-01):
```bash
python -m generator.validator examples/caso_fintech.json --strict
```
No Windows local, executado via `.\.venv\Scripts\python.exe -m generator.validator ...` (sem `python`/`python3` no PATH do shell; `py`/`python3.exe` e `.venv` confirmados via `Get-Command`).

## Blueprint criado: `examples/caso_fintech.json`

Criado do zero (Opção B), sem copiar/adaptar `showcase_tecnico.json`. Resumo estrutural:

| Campo | Valor |
|---|---|
| `titulo` | "Desvio de Fundos na Acelerada Pagamentos" |
| `dificuldade` | `avancado` |
| `genero`/`tom` | "fraude corporativa financeira" / "corporativo, tenso, técnico" |
| `formato_envelopes` | 2 (E1, E2) |
| `personagens` | 7 (min 4) |
| `documentos` | 16 (min 8) |
| `pilares_validacao` | 4 (exatamente 4, todos apontando para o executor "02" Tiago Mendes — mesmo padrão do Aurora) |
| `matriz_pistas` | 5 (min 3) |
| `red_herrings` | 3 (min 2) |
| `dicas` | 6 (min 6, inclui 1 `quase_gabarito`) |
| `dicas_contextuais` | 4 |
| `contratos_evidencia` | 4 (3 com `fase` E1/E2 + 1 com `fase: "final"`, `tipo: "solucao_final"`, exigido por `GP_006`) |
| `cadeia_financeira` | 2 saltos (Acelerada→Solenne Capital; Solenne Capital→Greymont Holdings, `is_salto_final: true`) |

### Enredo

Fintech "Acelerada Pagamentos" (instituição de pagamento B2B). CFO Beatriz Lacerda (`planejador_id`/`beneficiario_id` = "01") estrutura um contrato de consultoria fictício com a "Solenne Capital Partners" (Malta) e instrui o Diretor de Operações Tiago Mendes (`executor_id` = "02") a autorizar quatro remessas trimestrais de R$ 1.050.000,00 sem exigir entregável. O representante comercial da Solenne, Diego Salum (cúmplice), redireciona 40% de cada remessa para a "Greymont Holdings" (offshore de fachada vinculada a Beatriz), mediante acordo de retrocomissão registrado apenas em planilha pessoal recuperada do backup do notebook corporativo de Beatriz. CEO Renato Aguilar (narrador) pede a apuração de boa-fé após o achado da auditora externa Helga Brandt (testemunha). Red herrings: analista de compliance Júlia Prado (aprovou cadastro de fornecedor com checklist incompleto, mas sem acesso ao mecanismo de retorno) e controller Marcos Vidal (erro de reconciliação genuíno e isolado, sem ligação com o desvio); guia operacional também cita mudança de legislação cambial e atraso de compensação SWIFT como explicações genéricas descartadas.

### Documentos (16, envelopes E1/E2)

E1 (10 docs): `E1-01` email_institucional (abertura da apuração), `E1-02` depoimento (memorando da auditora), `E1-03` contrato (consultoria fictícia CS-2025-118), `E1-04` depoimento (Marcos, red herring), `E1-05` depoimento (Tiago, autorização), `E1-06` depoimento (Júlia, red herring), `E1-07` extrato (remessas SWIFT), `E1-08` protocolo (abertura formal — exigido por `DOC_003`), `E1-09` folha_cruzamento (papéis e alçadas — exigido por `DOC_004`), `E1-10` glossario (termos técnicos — evita `AUTO_001`).

E2 (6 docs): `E2-01` extrato (conta Greymont Holdings, recebimentos de 40%), `E2-02` chat (instrução Beatriz→Tiago), `E2-03` email_institucional (confirmação Diego Salum), `E2-04` boletim (laudo de TI — planilha pessoal recuperada), `E2-05` log_acesso (correção isolada de Marcos — descarte), `E2-06` folha_cruzamento (consolidação de descartes Júlia/Marcos).

### Densidade documental vs Aurora

Medido via `len(json.dumps(doc["conteudo"]))` somado por documento:

| Caso | Documentos | Caracteres totais em `conteudo` | Média por documento |
|---|---|---|---|
| Aurora (`caso_canonico_intermediario.json`) | 17 | 26.464 | 1.556 |
| Fintech (`caso_fintech.json`) | 16 | 29.647 | 1.852 |

Fintech tem média ~19% mais densa por documento que Aurora, conforme requisito explícito da spec (ISSUE-30 comparará essa métrica).

### Regra editorial — documentos de jogador sem vazamento de gabarito

Nenhum documento de jogador narra a conclusão (quem desviou, por que, ou veredito). A ligação final entre Beatriz e a conta beneficiária só é estabelecida pelo jogador ao cruzar: (1) quem assina o contrato fictício (`E1-03`), (2) quem instrui Tiago a dispensar entregável (`E2-02`), (3) de quem é o equipamento onde a planilha de retrocomissão foi recuperada (`E2-04`, que cita apenas "notebook corporativo atribuído a Beatriz Lacerda" como fato de custódia, não como acusação). Campos manuscritos (`ANOTACAO`/`NOTA_MANUSCRITA`) não foram usados — evita a checagem `HAND_003` (linguagem de solução em manuscrito) por construção.

## Validação

Comando:
```bash
.\.venv\Scripts\python.exe -m generator.validator examples/caso_fintech.json --strict
```

Resultado final (após iteração):
```
============================================================
VALIDAÇÃO DE BLUEPRINT — Desvio de Fundos na Acelerada Pagamentos
============================================================
Risco: Baixo
Pode gerar: SIM
Críticos: 0
Moderados: 0
Avisos: 2

AVISOS
[ELENCO_001] Executor, planejador e beneficiário usam apenas dois personagens.
  - Verifique se o acúmulo parcial de papéis no gabarito foi intencional.
[PT_002] Documentos abaixo do recomendado para a dificuldade declarada.
  - avancado: recomendado a partir de 19; observado: 16.
```

Ambos os avisos são decisões editoriais intencionais e não bloqueiam geração (`pode_gerar: SIM`, risco baixo mesmo em modo `--strict`):
- `ELENCO_001`: planejador e beneficiário são a mesma pessoa (Beatriz) por design — ela arquiteta o esquema e é beneficiária final; o executor (Tiago) é pessoa distinta. Padrão aceito pelo próprio validator como aviso, não erro.
- `PT_002`: 16 documentos está acima do mínimo estrutural (8) e mais denso por documento que Aurora; heurística de contagem para "avancado" recomenda 19+, mas não é um requisito do schema Pydantic nem do `BlueprintValidator` em nível crítico/moderado.

### Iterações até zero críticos/moderados

Principais erros corrigidos durante a iteração (do primeiro `risco: alto` ao `risco: baixo`):
1. `DOC_003` (crítico): faltava documento tipo `protocolo` no E1 → adicionado `E1-08`.
2. `CONT_003`/`CONT_ITEM_001` (críticos): campos obrigatórios do schema `extrato.yaml` incompletos nos documentos `E1-07`/`E2-01` (faltavam `LOGO_SIGLA`, `NOME_BANCO`, `TAGLINE_BANCO`, `COR_BANCO`, `PERIODO_INICIO/FIM`, `DATA_GERACAO`, etc., e nos itens de `LANCAMENTOS` faltavam `CLASSE_LINHA`, `COR_SALDO`, `DETALHE`, `DIRECAO`, `TIPO_LOWER`) → schema completo aplicado conforme `generator/schemas/extrato.yaml`.
3. `CONT_003` (crítico): `COPIA` vazio no email `E2-03` (schema `email_institucional.yaml` exige campo não vazio) → preenchido.
4. `DOC_004` (moderado): faltava `folha_cruzamento` no E1 → adicionado `E1-09`.
5. `GP_006` (moderado→crítico após correções anteriores): nenhum contrato de evidência informado, depois nenhum contrato com `fase=="final"`/`tipo=="solucao_final"` → adicionados 4 `contratos_evidencia`, com `C-E2-BENEFICIARIO` ajustado para `fase: "final"`, `tipo: "solucao_final"`.
6. `PILAR_006` (moderado): os 4 pilares apontavam para personagens diferentes → corrigido para todos apontarem ao executor "02" (mesmo padrão usado no Aurora, onde os 4 pilares apontam só para Marta).
7. `DC_000` (moderado): havia `contratos_evidencia` sem `dicas_contextuais` → adicionadas 4 dicas contextuais.
8. `GP_003` (aviso, mantido como aviso residual aceitável só até ser zerado): 6 documentos (`E1-07`, `E1-08`, `E1-09`, `E1-10`, `E2-02`, `E2-03`) não participavam de nenhum contrato de evidência → conectados via `descarta_alternativas` nos contratos existentes.

## `pytest tests/ -q`

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

Resultado: **1327 passed, 6 failed, 3 skipped** (184.17s).

Falhas (idênticas ao baseline de STEP-02, todas pré-existentes/ambiente Windows, nenhuma nova):
- `tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`
- `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`

As 5 primeiras são falhas de symlink em ambiente Windows (sem suporte/privilégio de symlink no filesystem local). A última (`test_run_pipeline_is_deterministic_with_same_created_at`) é falha de determinismo de hash já presente no baseline STEP-02, não relacionada a `examples/caso_fintech.json` (esse teste nem referencia o blueprint Fintech — usa `minimal_blueprint_path` próprio). Nenhum teste novo falhou; nenhuma regressão introduzida pela criação do blueprint.

## Confirmação: Aurora intocado

```bash
git diff --stat examples/caso_canonico_intermediario.json
```
Saída: vazia (nenhuma alteração). Confirmado também `examples/caso_canonico_iniciante.json` não tocado (não editado em nenhum momento desta tarefa).

## Arquivos alterados nesta execução

- Criado: `examples/caso_fintech.json` (único arquivo de conteúdo criado/editado).
- Criado: `.ai/runs/ISSUE-29+30/STEP-03_EXECUTION.md` (este relatório).
- Atualizado: `.ai/issues/ISSUE-29+30.md` (seção "## Estado" e "## Histórico").

Nenhum módulo em `generator/` foi alterado. Nenhum schema, validator ou pipeline_runner foi tocado.

## Resultado

Blueprint Fintech válido, schema-conforme (`Blueprint` Pydantic + `BlueprintValidator` editorial), passa `--strict` com risco baixo e `pode_gerar: SIM`. Pronto para uso em STEP-04 (rodar `run_pipeline` sobre `examples/caso_fintech.json`) após revisão humana deste step, por se tratar de step `green`/high-risk.

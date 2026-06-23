# STEP-03 — Preparação do blueprint Fintech — Review Report

Reviewer: independente do executor. Verificação direta de cada item do contrato STEP-03, sem confiar no texto do execution report.

## 1. Arquivo existe, JSON válido

```bash
./.venv/Scripts/python.exe -c "import json; json.load(open('examples/caso_fintech.json', encoding='utf-8'))"
```
Resultado: OK, parse sem erro.

## 2. Validator strict

```bash
./.venv/Scripts/python.exe -m generator.validator examples/caso_fintech.json --strict
```
Output real:
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
Idêntico ao reportado pelo executor. Confirmado em `generator/validator.py`: `_calcular_risco` (linha ~1710) determina nível de risco e `pode_gerar` apenas a partir de `criticos`/`moderados` — avisos (`AVISOS`) nunca entram nesse cálculo. Com 0 críticos e 0 moderados, `nivel_risco = BAIXO` e `pode_gerar = True` incondicionalmente (independe de `--strict`). Confirma que os 2 avisos são não bloqueantes por construção do validator, não por leniência do executor.

## 3. Estrutura mínima do schema (medido diretamente do JSON, não do report)

```python
titulo: "Desvio de Fundos na Acelerada Pagamentos"
dificuldade: "avancado"
genero: "fraude corporativa financeira"
n_personagens: 7        (min 4)  -> OK
n_documentos: 16         (min 8)  -> OK
n_matriz_pistas: 5       (min 3)  -> OK
n_red_herrings: 3        (min 2)  -> OK
n_dicas: 6               (min 6)  -> OK
n_pilares_validacao: 4   (exatamente 4) -> OK, todos com personagem_id == "02" (Tiago, executor)
papeis personagens: ['beneficiario','executor','narrador','testemunha','cumplice','red_herring','red_herring']
```
Tema correto: fraude financeira corporativa (consultoria fictícia, retrocomissão via offshore), transferências internacionais (remessas SWIFT Brasil→Malta→offshore). Personagens cobrem CFO (Beatriz, beneficiária/planejadora), operacional (Tiago, executor/Diretor de Operações), auditor externo (Helga, testemunha), parceiro/conexão offshore (Diego Salum, representante comercial da Solenne Capital/cúmplice ligado à Greymont Holdings). Mínimo de 4 papéis-chave coberto, com 7 personagens no total (excede mínimo).

## 4. Densidade documental vs Aurora (cálculo independente)

```python
def stats(path):
    docs = json.load(open(path, encoding='utf-8'))['documentos']
    lens = [len(json.dumps(doc['conteudo'], ensure_ascii=False)) for doc in docs]
    return len(lens), sum(lens), sum(lens)/len(lens)
```
Resultado:
| Caso | n docs | total chars | média/doc |
|---|---|---|---|
| Aurora (`caso_canonico_intermediario.json`) | 17 | 26.464 | 1.556,7 |
| Fintech (`caso_fintech.json`) | 16 | 29.647 | 1.852,9 |

Confirma exatamente os números do execution report. Fintech ~19% mais denso por documento que Aurora. Critério "documentos densos (maior que Aurora)" do contrato de revisão satisfeito.

## 5. Vazamento de gabarito em documentos de jogador

Amostra lida na íntegra: `E1-03` (contrato de consultoria fictícia), `E2-02` (chat Beatriz→Tiago), `E2-04` (boletim/laudo forense de TI).

- `E1-03` (contrato): apresenta cláusulas formais (objeto, remuneração R$ 1.050.000,00/trimestre, ausência de cronograma de entregáveis, vigência, representante Diego Salum). Não narra fraude nem rotula o contrato como fictício — é evidência bruta que o jogador deve cruzar com outros documentos para inferir a fictícia natureza do serviço.
- `E2-02` (chat): diálogo operacional puro ("Tiago, preciso que a remessa da Solenne saia até amanhã"; "Não precisa, eu acompanho o conteúdo direto com eles. O contrato não exige cronograma fixo"). Não há confissão, não há rótulo de "fraude" ou "desvio" no texto — fala-se em termos operacionais ambíguos por design.
- `E2-04` (boletim forense): descreve fato de custódia ("foi localizado o arquivo 'controle_pessoal_retorno.xlsx'... atribuído a Beatriz Lacerda... valores de R$ 1.050.000,00 na coluna 'enviado' e R$ 420.000,00 na coluna 'retorno 40%'") sem veredito autoral — relata achado técnico (hash, cadeia de custódia), não conclusão de culpa.

Nenhum dos três documentos contém interpretação explícita do autor ou rótulo de gabarito. A ligação final exige cruzamento pelo jogador. Critério "nenhum vazamento de gabarito óbvio" satisfeito na amostra revisada. Execução também evitou campos manuscritos (`ANOTACAO`/`NOTA_MANUSCRITA`) por construção, reduzindo superfície de risco para `HAND_003`.

## 6. Aurora e iniciante intocados

```bash
git diff --stat examples/caso_canonico_intermediario.json examples/caso_canonico_iniciante.json
```
Saída: vazia. Confirmado.

## 7. `generator/` intocado

```bash
git status --short generator/
```
Saída: vazia. Confirmado.

```bash
git status --short
```
Saída:
```
 M .ai/issues/ISSUE-29+30.md
?? .ai/runs/ISSUE-29+30/
?? examples/caso_fintech.json
```
Escopo exatamente conforme contrato (arquivo editável único: `examples/caso_fintech.json`; demais alterações são artefatos de processo — issue tracker e execution/review reports).

## 8. `pytest tests/ -q` — não-regressão

Baseline STEP-02 (`.ai/runs/ISSUE-29+30/STEP-02_EXECUTION.md`): **1327 passed, 6 failed, 3 skipped**.
Falhas baseline: 5 testes de symlink (`test_blind_bundle_generator.py`, `test_blind_bundle_leak_checker.py` x3, `test_blind_bundle_sanitizer.py`) + `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`.

Execução independente desta revisão:
```bash
./.venv/Scripts/python.exe -m pytest tests/ -q
```
Resultado real: **1328 passed, 5 failed, 3 skipped** (185.35s).

Falhas reais (idênticas, subconjunto do baseline):
```
FAILED tests/test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed
FAILED tests/test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails
FAILED tests/test_blind_bundle_leak_checker.py::test_symlink_manifest_fails
FAILED tests/test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail
FAILED tests/test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail
```
`test_run_pipeline_is_deterministic_with_same_created_at` passou nesta execução (não falhou). O execution report já descrevia essa falha como flake de determinismo de ambiente, pré-existente, não relacionada ao blueprint Fintech (o teste usa `minimal_blueprint_path` próprio, não `caso_fintech.json`). Resultado: nenhuma falha nova; mesmo conjunto de 5 falhas de symlink do baseline presentes; zero regressão introduzida pela criação do blueprint Fintech. Discrepância pontual (6 vs 5 falhas) é flake conhecido do teste de determinismo, não efeito do step.

## Veredito

**APPROVED**

Todos os critérios de revisão do contrato STEP-03 confirmados de forma independente:
- Schema-válido (Pydantic + `BlueprintValidator`, 0 críticos/0 moderados, `pode_gerar: SIM`).
- Dificuldade `avancado` plausível e tema correto (fraude financeira corporativa, transferências internacionais).
- Estrutura mínima satisfeita com margem: personagens 7≥4, documentos 16≥8, matriz_pistas 5≥3, red_herrings 3≥2, dicas 6≥6, pilares_validacao =4.
- Documentos mais densos que Aurora (1.852,9 vs 1.556,7 chars/doc médio, ~19% maior), calculado de forma independente.
- Amostra de documentos de jogador sem vazamento de gabarito (evidência bruta, sem veredito autoral).
- `examples/caso_canonico_intermediario.json` e `examples/caso_canonico_iniciante.json` intocados (diff vazio).
- `generator/` intocado (status vazio).
- `pytest tests/ -q` sem regressão nova (mesmas falhas pré-existentes de symlink; uma falha de determinismo flaky ausente nesta execução, não nova falha).

Os dois avisos do validator (`ELENCO_001`, `PT_002`) são decisões editoriais documentadas e não bloqueiam geração — confirmado via leitura do código-fonte do validator (`_calcular_risco`), não apenas pela alegação do executor.

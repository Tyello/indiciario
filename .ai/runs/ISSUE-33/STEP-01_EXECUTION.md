# ISSUE-33 STEP-01 — Leitura
Status: concluído | Executor: haiku-spec-executor | Data: 2026-07-09

---

## 1. Protocol `BlindSolver` (generator/blind_solver_harness.py)

**Localização**: linhas 116–125

```python
@runtime_checkable
class BlindSolver(Protocol):
    """A blind solver consumes a controlled context and returns a report.

    Implementations may return a :class:`BlindSolverReport` or a plain mapping
    with the same fields. No solver intelligence is provided by this module.
    """

    def solve(self, context: "BlindSolverContext") -> "BlindSolverReport | Mapping[str, Any]":
        ...
```

**Assinatura exata**:
- Atributo: nenhum atributo obrigatório (não é `@property`).
- Método único: `solve(self, context: BlindSolverContext) -> BlindSolverReport | Mapping[str, Any]`
  - Parâmetro: `context` do tipo `BlindSolverContext`
  - Retorno: `BlindSolverReport | Mapping[str, Any]` (dataclass ou dict)

**Uso no pipeline** (linhas 356–359 em `generator/pipeline_runner.py`):
```python
harness_result = run_blind_solver_harness(
    harness_request,
    DeterministicPipelineSolver(created_at=timestamp),
)
```

---

## 2. Estrutura de `BlindSolverContext` (linhas 128–233)

**Dataclass**: não é dataclass, é classe regular.

**Inicializador** (`__init__`, linhas 136–155):
```python
def __init__(
    self,
    *,
    manifest: Mapping[str, Any],
    bundle_path: Path,
    solver_id: str,
    solver_run_id: str,
    max_bytes_per_artifact: int,
) -> None:
```
- Parâmetros: `manifest`, `bundle_path` (Path), `solver_id`, `solver_run_id`, `max_bytes_per_artifact`.
- Armazena internamente: `_bundle_path`, `_solver_id`, `_solver_run_id`, `_bundle_id`, `_manifest_id`, `_max_bytes_per_artifact`, `_descriptors`, `_by_id`, `_by_path`, `_accessed`, `_denied`.

**Propriedades públicas** (linhas 158–180):
- `solver_id: str` (property, line 159)
- `solver_run_id: str` (property, line 163)
- `bundle_id: str` (property, line 167)
- `manifest_id: str` (property, line 171)
- `accessed_artifacts: tuple[str, ...]` (property, line 175)
- `denied_access_attempts: tuple[str, ...]` (property, line 179)

**Métodos públicos** (linhas 182–206):
- `list_artifacts() -> tuple[ArtifactDescriptor, ...]` (line 182)
- `read_artifact(artifact_id: str) -> str` (line 185, alias para `read_artifact_text`)
- `read_artifact_text(artifact_id: str) -> str` (line 190)
  - Lêa o artefato por `artifact_id`; nega se não declarado.
  - Retorna texto UTF-8.
- `read_artifact_path(path: str) -> str` (line 199)
  - Lêa o artefato por `path`; nega se não declarado ou fora do bundle.
  - Retorna texto UTF-8.

**Método privado** (linha 209):
- `_read_descriptor(descriptor: ArtifactDescriptor) -> str`
  - Valida path com `_bundle_child`, lê bytes, decodifica UTF-8, registra em `_accessed`, retorna texto.

---

## 3. Estrutura de `BlindSolverReport` (linhas 86–102)

**Tipo**: dataclass congelada (`@dataclass(frozen=True)`)

**Campos obrigatórios** (sem `=` após o nome):
```python
schema_version: str
solver_run_id: str
solver_id: str
bundle_id: str
manifest_id: str
created_at: str
conclusion: str
confidence: str
reasoning_summary: str
evidence_used: tuple[BlindSolverEvidence, ...]
```

**Campos opcionais** (com default, linhas 100–102):
```python
open_questions: tuple[str, ...] = ()
assumptions: tuple[str, ...] = ()
warnings: tuple[str, ...] = ()
```

**Tipo de `evidence_used`**: `tuple[BlindSolverEvidence, ...]`
- Cada item é um `BlindSolverEvidence` (linhas 75–83):
  ```python
  @dataclass(frozen=True)
  class BlindSolverEvidence:
      artifact_id: str
      path: str
      quote_or_summary: str
      relevance: str
      confidence: str
  ```

---

## 4. Schema completo de `schemas/blind_solver_report.schema.yaml`

**Estrutura**:
```yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://indiciario.local/schemas/blind_solver_report/1.0
title: Indiciário Blind Solver Report
type: object
additionalProperties: false  # Rejeita campos extras
```

**Campos `required`** (linha 11–24):
```
- schema_version
- solver_run_id
- solver_id
- bundle_id
- manifest_id
- created_at
- conclusion
- confidence
- reasoning_summary
- evidence_used
- open_questions
- assumptions
- warnings
```

**Properties**:
- `schema_version`: `const: '1.0'` (linha 34)
- `solver_run_id`, `solver_id`, `bundle_id`, `manifest_id`: `$ref: '#/$defs/neutral_id'`
  - Pattern: `^[A-Z0-9][A-Z0-9_-]{1,63}$`
  - Length: 2–64 chars
- `created_at`: `$ref: '#/$defs/timestamp'`
  - Format: RFC3339 (ISO 8601 datetime)
  - Pattern: `^(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))$`
- `conclusion`: `type: string`, `maxLength: 4000`
- `confidence`: `$ref: '#/$defs/confidence'`
  - Enum: `low` | `medium` | `high`
- `reasoning_summary`: `type: string`, `minLength: 1`, `maxLength: 4000`
- `evidence_used`: `type: array`, items: `$ref: '#/$defs/evidence_item'`
  - Cada item é um object com:
    - `artifact_id`: `$ref: '#/$defs/neutral_id'`
    - `path`: `$ref: '#/$defs/safe_path'` (pattern: `^[A-Za-z0-9._/-]+$`, proíbe `/`, `..`, `//`)
    - `quote_or_summary`: `$ref: '#/$defs/short_text'` (1–2000 chars)
    - `relevance`: `$ref: '#/$defs/short_text'`
    - `confidence`: `$ref: '#/$defs/confidence'`
    - `additionalProperties: false`
- `open_questions`: `type: array`, items: `$ref: '#/$defs/short_text'`
- `assumptions`: `type: array`, items: `$ref: '#/$defs/short_text'`
- `warnings`: `type: array`, items: `$ref: '#/$defs/short_text'`

**Notas**:
- `additionalProperties: false` em raiz + em `evidence_item` rejeita campos privados como `chain_of_thought`, `raw_prompt`, etc.
- Schema é **estrutural apenas** — não valida se artifact_ids/paths realmente existem no bundle (isso fica para o harness).

---

## 5. Função de validação em `generator/blind_solver_report_validator.py`

**Função principal** (linhas 151–256):
```python
def validate_report(report: Mapping[str, Any]) -> ReportValidationResult:
```

**Parâmetros**:
- `report`: `Mapping[str, Any]` (dict ou qualquer Mapping, aceita read-only)

**Retorno**:
```python
@dataclass(frozen=True)
class ReportValidationResult:
    valid: bool
    errors: tuple[ReportValidationError, ...] = field(default=())
    warnings: tuple[ReportValidationError, ...] = field(default=())
```

**Campos de `ReportValidationError`** (linhas 66–73):
```python
@dataclass(frozen=True)
class ReportValidationError:
    kind: ReportValidationErrorKind  # enum: STRUCTURAL, SEMANTIC, QUALITY
    code: str  # ex: "RV_001", "RV_002", etc.
    field: str  # campo afetado, ex: "reasoning_summary"
    message: str  # mensagem legível
```

**Códigos emitidos** (linhas 48–55):
- `RV_001`: structural (delegado a `validate_blind_solver_report` — erro de schema)
- `RV_002`: semantic — conclusão presente mas sem evidência
- `RV_003`: semantic — confiança alta mas sem evidência
- `RV_004`: semantic — confiança alta mas com perguntas abertas
- `RV_005`: semantic — sem conclusão e sem perguntas abertas
- `RV_006`: quality warning — reasoning_summary é só placeholder vago
- `RV_007`: quality warning — evidência presente mas conclusão vazia
- `RV_008`: semantic — confiança baixa mas 3+ evidências com alta confiança

**Chamada interna** (linha 163):
```python
schema_errors = validate_blind_solver_report(dict(report))
```
- Reutiliza `validate_blind_solver_report` do harness (linhas 297–304 em `blind_solver_harness.py`)
  - Carrega schema YAML, valida com `Draft202012Validator`
  - Retorna `tuple[str, ...]` (mensagens de erro, vazio se válido)

**Exceções**: nenhuma (retorna `ReportValidationResult` sempre)

---

## 6. Ponto exato de injeção do solver em `generator/pipeline_runner.py`

**Localização**: função `_blind_solve` (linhas 341–367)

**Instanciação do solver** (linhas 356–359):
```python
harness_result = run_blind_solver_harness(
    harness_request,
    DeterministicPipelineSolver(created_at=timestamp),
)
```

**Classe atual** (linhas 132–164):
```python
class DeterministicPipelineSolver:
    """Offline, no-LLM stub solver reused for pipeline runs."""

    def __init__(self, created_at: str = FIXED_PIPELINE_CREATED_AT) -> None:
        self.created_at = created_at

    def solve(self, context: BlindSolverContext) -> BlindSolverReport:
        artifacts = context.list_artifacts()
        first = artifacts[0]
        text = context.read_artifact_text(first.artifact_id)
        return BlindSolverReport(
            schema_version="1.0",
            solver_run_id=context.solver_run_id,
            solver_id=context.solver_id,
            bundle_id=context.bundle_id,
            manifest_id=context.manifest_id,
            created_at=self.created_at,
            conclusion=f"Read {len(artifacts)} artifact(s); first has {len(text)} chars.",
            confidence="low",
            reasoning_summary="Deterministic stub: inspected only the first bundled artifact.",
            evidence_used=(
                BlindSolverEvidence(
                    artifact_id=first.artifact_id,
                    path=first.path,
                    quote_or_summary=text.strip()[:60],
                    relevance="First declared artifact in the bundle.",
                    confidence="low",
                ),
            ),
            open_questions=(),
            assumptions=(),
            warnings=(),
        )
```

**Como será expandido** (para STEP-04):
- Adicionar parâmetro opcional `solver: BlindSolver | None = None` à função `run_pipeline` (linha 208).
- Se `solver is None`, usar `DeterministicPipelineSolver` (comportamento atual preservado).
- Se `solver` fornecido, passar para `run_blind_solver_harness` no lugar do stub.

---

## 7. Fixtures reutilizáveis de bundle em `tests/test_blind_solver_harness.py`

**Fixtures de source e output** (linhas 41–54):

```python
@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    """Cria árore de fontes com documentos públicos e privados."""
    source = tmp_path / "source"
    write(source / "public/envelope_1/depoimento.md", "Depoimento publico bruto\n")
    write(source / "public/envelope_1/recibo.md", "Recibo publico bruto\n")
    write(source / "private/solution.md", "Solucao privada\n")
    return source

@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    """Cria diretório de saída para bundles."""
    root = tmp_path / "bundles"
    root.mkdir()
    return root
```

**Builders de spec e request** (linhas 57–128):

```python
def public_spec(**overrides: object) -> ArtifactSpec:
    """Retorna ArtifactSpec padrão para um documento público."""
    # Valores padrão: artifact_id="ART_PUBLIC_001", source_path="public/envelope_1/depoimento.md", ...
    # Aceita overrides para customização.

def second_public_spec(**overrides: object) -> ArtifactSpec:
    """Retorna segundo ArtifactSpec padrão."""
    # Valores padrão: artifact_id="ART_PUBLIC_002", source_path="public/envelope_1/recibo.md", ...

def build_request(source_tree: Path, output_root: Path, **overrides: object) -> BlindBundleBuildRequest:
    """Monta um BlindBundleBuildRequest com valores padrão."""
    # Parâmetros padrão: manifest_id="MANIFEST_TEST_001", run_id="RUN_TEST_001", bundle_id="BUNDLE_TEST_001", ...

def make_bundle(source_tree: Path, output_root: Path, **overrides: object) -> Path:
    """Atalho: cria um bundle usando build_request + build_blind_bundle, retorna Path."""
    return build_blind_bundle(build_request(source_tree, output_root, **overrides)).output_path
```

**Builder de harness request** (linhas 118–127):

```python
@pytest.fixture  # NÃO é fixture, é função normal
def harness_request(bundle_path: Path, **overrides: object) -> BlindSolverHarnessRequest:
    """Monta um BlindSolverHarnessRequest com valores padrão."""
    # Parâmetros padrão: solver_id="SOLVER_STUB_001", run_id="SOLVER_RUN_001", created_at=FIXED_CREATED_AT, ...
    # Aceita overrides.
```

**Stubs de solver para testes** (linhas 133–199):

```python
class DeterministicStubBlindSolver:
    """Simula um solver que lê apenas o primeiro artefato."""
    def __init__(self, created_at: str = FIXED_CREATED_AT) -> None: ...
    def solve(self, context: BlindSolverContext) -> BlindSolverReport: ...

class PathReadingStubSolver(DeterministicStubBlindSolver):
    """Lê por path em vez de artifact_id."""
    def solve(self, context: BlindSolverContext) -> BlindSolverReport: ...

class AccessAttemptSolver:
    """Tenta um acesso descrito por callable, para testes negativos."""
    def __init__(self, attempt) -> None: ...
    def solve(self, context: BlindSolverContext) -> BlindSolverReport: ...

class ReportMutatingSolver(DeterministicStubBlindSolver):
    """Produz um report base e depois aplica uma mutação."""
    def __init__(self, mutate, created_at: str = FIXED_CREATED_AT) -> None: ...
    def solve(self, context: BlindSolverContext): ...
```

**Helper functions** (linhas 29–38):

```python
def write(path: Path, content: str) -> Path:
    """Escreve conteúdo em arquivo."""

def write_bytes(path: Path, content: bytes) -> Path:
    """Escreve bytes em arquivo."""
```

---

## 8. Interface de `generator/llm_provider.py`

**Protocol `LLMProvider`** (linhas 35–41):

```python
@runtime_checkable
class LLMProvider(Protocol):
    """Interface que um provider de LLM real deve implementar."""

    provider_id: str

    def complete(self, request: ProviderRequest) -> ProviderResponse: ...
```

**Atributo**:
- `provider_id: str` (atributo de classe ou instância)

**Método**:
- `complete(self, request: ProviderRequest) -> ProviderResponse`
  - Parâmetro: `request` do tipo `ProviderRequest` (dataclass frozen)
  - Retorno: `ProviderResponse` (dataclass frozen)

**Estruturas de dados** (linhas 13–32):

```python
@dataclass(frozen=True)
class ProviderRequest:
    """Requisição imutável para um provider de LLM."""
    prompt: str
    system: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    request_id: str | None = None

@dataclass(frozen=True)
class ProviderResponse:
    """Resposta imutável de um provider de LLM."""
    text: str
    model_id: str
    request_id: str | None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
```

**Exceções** (linhas 44–53):

```python
class ProviderError(RuntimeError):
    """Erro base de provider."""

class ProviderTransportError(ProviderError):
    """Erro de transporte/rede ao comunicar com o provider."""

class ProviderResponseError(ProviderError):
    """Erro de resposta inválida ou inesperada do provider."""
```

**Validação** (linhas 56–75):

```python
def validate_provider_request(request: ProviderRequest) -> list[str]:
    """Valida uma ProviderRequest sem mutá-la.
    
    Retorna lista de mensagens de erro (vazia se válida).
    """
    # Checagens:
    # PV_001: prompt vazio ou só whitespace
    # PV_002: max_tokens <= 0
    # PV_003: temperature fora de [0.0, 2.0]
    # PV_004: system fornecido mas vazio/whitespace
```

---

## 9. Interface de `generator/fake_provider.py`

**Classe `FakeProvider`** (linhas 27–97):

```python
class FakeProvider:
    """Provider fake que satisfaz LLMProvider com respostas pré-roteirizadas."""

    provider_id = "fake"  # class attribute

    def __init__(self, responses: Sequence[ScriptedResponse | ProviderError]):
        """Inicializa com roteiro de respostas/erros."""
        self._responses = responses
        self._index = 0
        self._calls: list[ProviderRequest] = []

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Completa uma requisição usando o roteiro pré-escrito."""
        # FP_001: valida request; inválido → ProviderResponseError, não registra em calls
        # FP_002: verifica se roteiro esgotado → ProviderResponseError("script exhausted")
        # Registra request em calls
        # FP_003: se item é ProviderError, levanta (mas já registrou em calls)
        # FP_004: ProviderResponse.request_id ecoa o request_id recebido
        return ProviderResponse(
            text=current_response.text,
            model_id=current_response.model_id,
            request_id=request.request_id,
        )

    @property
    def calls(self) -> tuple[ProviderRequest, ...]:
        """Retorna tupla imutável dos requests registrados."""
        return tuple(self._calls)
```

**Estrutura de dados** (linhas 19–24):

```python
@dataclass(frozen=True)
class ScriptedResponse:
    """Resposta pré-roteirizada para o FakeProvider."""
    text: str
    model_id: str = "fake-model"
```

**Comportamento**:
- Mantém um `_index` interno que avança a cada chamada válida.
- Comportamentos designados (FP_001–FP_004):
  - **FP_001**: request inválido (falha `validate_provider_request`) → `ProviderResponseError`, **não** registra em `_calls`.
  - **FP_002**: roteiro esgotado (índice >= len) → `ProviderResponseError("script exhausted")`.
  - **FP_003**: item no roteiro é um `ProviderError` → levanta o erro **depois de** registrar em `_calls`.
  - **FP_004**: resposta ecoa o `request_id` do request recebido.
- Propriedade `calls` retorna tupla **imutável** dos requests registrados, para inspeção em testes.

---

## Resumo de integração para STEP-02 onwards

**Ponto de entrada para novo solver**:
- `LLMBlindSolver(provider: LLMProvider, prompt_version: str = "v1")` implementará `BlindSolver.solve(context)`.
- Usará `context.list_artifacts()` + `context.read_artifact_text(artifact_id)` para ler o bundle.
- Montará prompt **apenas** a partir do bundle + template (regra **LS_001**).
- Chamará `provider.complete(ProviderRequest(...))`.
- Coercerá resposta JSON em `BlindSolverReport`, sobrescrevendo ids do context (**LS_003**).

**Validação de report**:
- Harness chama `validate_blind_solver_report` (schema).
- Fora do harness, `validate_report` (semântica).

**Integração no pipeline**:
- Adicionar parâmetro `solver: BlindSolver | None = None` a `run_pipeline`.
- Default `None` → `DeterministicPipelineSolver` (preserva comportamento).
- Com solver → usar no `run_blind_solver_harness`.

---

**Documento preparado para**: STEP-02 RED (escrita de testes) e STEP-03 GREEN (implementação).

"""Provider concreto contra Claude Code em headless mode (ISSUE-33.8).

Implementa LLMProvider via subprocess headless (claude -p), autenticado pela
sessão do operador. Confinamento garantido: cwd vazio + --tools "" previnem
acesso ao repo ou gabarito. Runner injetável para testes offline (nenhum teste
invoca o binário real).

Regras CC_001–CC_005: confinement, injeção, error mapping, argv, temperatura.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from generator.llm_provider import (
    ProviderRequest,
    ProviderResponse,
    ProviderResponseError,
    ProviderTransportError,
)


@dataclass(frozen=True)
class CompletedRun:
    """Resultado imutável de execução do runner."""

    stdout: str
    stderr: str
    returncode: int


Runner = Callable[[list[str], str, Path], CompletedRun]


def _build_default_runner(timeout_s: float) -> Runner:
    """Constrói o runner default (subprocess.run) para uso em produção.

    CC_002: default contra o binário real `claude`; nenhum teste usa esta
    função (testes injetam runner fake).
    """

    def _runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
        # No Windows o `claude` global (npm) e um shim .CMD; subprocess.run sem
        # shell=True nao faz resolucao de PATHEXT (so o shell faz), entao
        # ["claude", ...] cru gera FileNotFoundError mesmo com o binario
        # instalado. shutil.which resolve a extensao certa; se nao encontrar,
        # mantem "claude" para que o FileNotFoundError real (nao instalado)
        # ainda dispare o mapeamento de CC_003.
        resolved = shutil.which(argv[0]) or argv[0]
        result = subprocess.run(
            [resolved, *argv[1:]],
            input=stdin_text,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_s,
        )
        return CompletedRun(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    return _runner


class ClaudeCodeProvider:
    """Provider concreto contra Claude Code headless. Satisfaz LLMProvider."""

    provider_id = "claude-code"
    supports_temperature = False

    def __init__(
        self,
        model_id: str = "opus",
        runner: Runner | None = None,
        timeout_s: float = 300.0,
        max_transport_retries: int = 1,
    ) -> None:
        self.model_id = model_id
        self.timeout_s = timeout_s
        self.max_transport_retries = max_transport_retries
        self._runner = runner or _build_default_runner(timeout_s)

    def _build_argv(self, request: ProviderRequest) -> list[str]:
        """CC_004: monta argv base + system prompt se fornecido.

        Base: ["claude", "-p", "--model", model_id, "--output-format", "text",
               "--tools", ""]
        Se request.system: adiciona ["--system-prompt", system]
        """
        argv = [
            "claude",
            "-p",
            "--model",
            self.model_id,
            "--output-format",
            "text",
            "--tools",
            "",
        ]
        if request.system:
            argv.extend(["--system-prompt", request.system])
        return argv

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        """CC_001–CC_005: executa request, mapeia erros, retorna resposta."""

        # CC_001: confinamento - cwd temporário
        cwd = Path(tempfile.mkdtemp())

        argv = self._build_argv(request)

        # Retry logic: até 1 + max_transport_retries tentativas
        max_attempts = 1 + max(self.max_transport_retries, 0)
        attempt = 0

        while True:
            attempt += 1
            try:
                result = self._runner(argv, request.prompt, cwd)
            except FileNotFoundError as exc:
                # CC_003: binário ausente → ProviderTransportError com hint
                if attempt >= max_attempts:
                    raise ProviderTransportError(
                        "Claude Code não encontrado — verifique a instalação"
                    ) from exc
                continue
            except Exception as exc:
                # CC_003: timeout ou exceção genérica → retry ou falha
                if attempt >= max_attempts:
                    exc_name = type(exc).__name__
                    raise ProviderTransportError(
                        f"Falha de transporte ao chamar Claude Code: {exc_name}"
                    ) from exc
                continue

            # Validar resultado
            if result.returncode != 0:
                # CC_003: returncode != 0 → ProviderTransportError com stderr
                stderr_snippet = (
                    result.stderr[:500]
                    if result.stderr
                    else "(sem stderr)"
                )
                if attempt >= max_attempts:
                    raise ProviderTransportError(
                        f"Claude Code retornou {result.returncode}: {stderr_snippet}"
                    )
                continue

            # CC_003: stdout vazio → ProviderResponseError (sem retry)
            if not result.stdout or not result.stdout.strip():
                raise ProviderResponseError("Claude Code retornou resposta vazia")

            # CC_002/004: resposta válida
            return ProviderResponse(
                text=result.stdout,
                model_id=f"claude-code:{self.model_id}",
                request_id=request.request_id,
                usage_input_tokens=None,
                usage_output_tokens=None,
            )

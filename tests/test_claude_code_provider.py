"""Tests for ClaudeCodeProvider (ISSUE-33.8, STEP-02 RED).

Cases cover:
- CC_001: confinement - argv, cwd isolation, --tools empty
- CC_002/004: happy path - response text, model_id prefixing, system prompt handling
- CC_003: error mapping - FileNotFoundError, stderr preservation, timeout retry, empty response
- CC_005: temperature ignored (not in argv)
- Invariant: no test imports or calls subprocess
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from generator.llm_provider import (
    ProviderRequest,
    ProviderResponse,
    ProviderResponseError,
    ProviderTransportError,
)


@dataclass(frozen=True)
class CompletedRun:
    """Fake subprocess completion result."""
    stdout: str
    stderr: str
    returncode: int


# Will be imported from generator.claude_code_provider (module not yet created; import fails for RED)
# This is expected behavior for the RED phase


class TestCC001Confinement:
    """CC_001: argv/cwd isolation, --tools empty."""

    def test_cc001_argv_no_repo_path_no_bundle_reference(self) -> None:
        """Argv must not contain repo paths or 'bundle' string."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_argv = None
        captured_cwd = None

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal captured_argv, captured_cwd
            captured_argv = argv
            captured_cwd = cwd
            return CompletedRun(stdout="CONCLUSAO: X", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="pergunta")
        provider.complete(request)

        assert captured_argv is not None
        argv_str = " ".join(captured_argv)

        # Assert no repo path substring in argv
        assert "OneDrive" not in argv_str
        assert "Documentos" not in argv_str
        assert "indiciario" not in argv_str
        assert "bundle" not in argv_str

        # Assert --tools is present with empty string following
        assert "--tools" in captured_argv
        tools_idx = captured_argv.index("--tools")
        assert tools_idx + 1 < len(captured_argv)
        assert captured_argv[tools_idx + 1] == ""

    def test_cc001_cwd_is_temporary_and_empty(self) -> None:
        """CWD must be temporary, exist, be empty, and differ between calls."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_cwds = []

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            captured_cwds.append(cwd)
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)

        # First call
        provider.complete(ProviderRequest(prompt="P1"))
        cwd1 = captured_cwds[0]

        # Second call
        provider.complete(ProviderRequest(prompt="P2"))
        cwd2 = captured_cwds[1]

        # Both must exist
        assert cwd1.exists()
        assert cwd2.exists()

        # Both must be empty (no files inside)
        assert list(cwd1.iterdir()) == []
        assert list(cwd2.iterdir()) == []

        # Must be different from each other
        assert cwd1 != cwd2

        # Must not be the current working directory or repo root
        repo_root = Path(__file__).resolve().parents[1]
        assert cwd1 != Path.cwd()
        assert cwd1 != repo_root
        assert cwd2 != Path.cwd()
        assert cwd2 != repo_root


class TestCC002004HappyPath:
    """CC_002/004: response text, model_id prefixing, system prompt handling."""

    def test_cc002_response_text_extracted_from_stdout(self) -> None:
        """Response text should be taken directly from stdout."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            return CompletedRun(stdout="CONCLUSAO: X", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")
        response = provider.complete(request)

        assert isinstance(response, ProviderResponse)
        assert response.text == "CONCLUSAO: X"

    def test_cc002_model_id_prefixed_with_claude_code(self) -> None:
        """Model ID should be prefixed as 'claude-code:<model_id>'."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")
        response = provider.complete(request)

        assert response.model_id == "claude-code:opus"

    def test_cc004_system_prompt_in_argv_when_provided(self) -> None:
        """System prompt should appear in argv as --system-prompt <value>."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_argv = None

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal captured_argv
            captured_argv = argv
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P", system="S")
        provider.complete(request)

        assert captured_argv is not None
        assert "--system-prompt" in captured_argv
        prompt_idx = captured_argv.index("--system-prompt")
        assert captured_argv[prompt_idx + 1] == "S"

    def test_cc004_no_system_prompt_when_not_provided(self) -> None:
        """System prompt should NOT appear in argv when request has no system."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_argv = None

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal captured_argv
            captured_argv = argv
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")
        provider.complete(request)

        assert captured_argv is not None
        assert "--system-prompt" not in captured_argv

    def test_cc002_prompt_in_stdin_only_not_argv(self) -> None:
        """Prompt should go to stdin, not appear in argv."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_stdin = None
        captured_argv = None

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal captured_stdin, captured_argv
            captured_stdin = stdin_text
            captured_argv = argv
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")
        provider.complete(request)

        assert captured_stdin == "P"
        argv_str = " ".join(captured_argv)
        assert "P" not in argv_str


class TestCC003ErrorMapping:
    """CC_003: error mapping - FileNotFoundError, stderr, timeout retry, empty response."""

    def test_cc003a_filenotfounderror_to_transport_error_with_installation_hint(self) -> None:
        """FileNotFoundError should become ProviderTransportError with installation/claude mention."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            raise FileNotFoundError("claude binary not found")

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")

        with pytest.raises(ProviderTransportError) as exc_info:
            provider.complete(request)

        error_msg = str(exc_info.value).lower()
        # Should mention something about installation or "not found"
        assert any(
            keyword in error_msg
            for keyword in ["instala", "not found", "not installed", "claude"]
        )

    def test_cc003b_stderr_preserved_in_transport_error(self) -> None:
        """Stderr from failed run should be preserved in ProviderTransportError message."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            return CompletedRun(stdout="", stderr="not logged in", returncode=1)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")

        with pytest.raises(ProviderTransportError) as exc_info:
            provider.complete(request)

        error_msg = str(exc_info.value)
        assert "not logged in" in error_msg

    def test_cc003c_timeout_retry_succeeds_on_second_attempt(self) -> None:
        """TimeoutError on 1st attempt, success on 2nd (max_transport_retries=1) -> OK."""
        from generator.claude_code_provider import ClaudeCodeProvider

        call_count = 0

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("timeout")
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner, max_transport_retries=1)
        request = ProviderRequest(prompt="P")
        response = provider.complete(request)

        assert response.text == "OK"
        assert call_count == 2

    def test_cc003d_timeout_always_raises_after_retries_exhausted(self) -> None:
        """TimeoutError on all attempts -> ProviderTransportError after max retries."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            raise TimeoutError("timeout")

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner, max_transport_retries=1)
        request = ProviderRequest(prompt="P")

        with pytest.raises(ProviderTransportError):
            provider.complete(request)

    def test_cc003e_empty_stdout_raises_response_error(self) -> None:
        """Empty stdout (success code but no content) -> ProviderResponseError."""
        from generator.claude_code_provider import ClaudeCodeProvider

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            return CompletedRun(stdout="", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P")

        with pytest.raises(ProviderResponseError):
            provider.complete(request)


class TestCC005TemperatureIgnored:
    """CC_005: temperature parameter is ignored."""

    def test_cc005_temperature_not_in_argv(self) -> None:
        """Temperature value should not appear in argv."""
        from generator.claude_code_provider import ClaudeCodeProvider

        captured_argv = None

        def fake_runner(argv: list[str], stdin_text: str, cwd: Path) -> CompletedRun:
            nonlocal captured_argv
            captured_argv = argv
            return CompletedRun(stdout="OK", stderr="", returncode=0)

        provider = ClaudeCodeProvider(model_id="opus", runner=fake_runner)
        request = ProviderRequest(prompt="P", temperature=0.9)
        provider.complete(request)

        assert captured_argv is not None
        argv_str = " ".join(captured_argv)
        assert "0.9" not in argv_str
        assert "temperature" not in argv_str
        assert "--temperature" not in captured_argv

    def test_cc005_supports_temperature_is_false(self) -> None:
        """Class attribute supports_temperature should be False."""
        from generator.claude_code_provider import ClaudeCodeProvider

        assert ClaudeCodeProvider.supports_temperature is False

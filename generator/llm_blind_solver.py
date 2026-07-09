"""LLM-based blind solver adapter (ISSUE-33 STEP-03).

This module implements LLMBlindSolver, which:
- Builds a prompt from a template + included artifacts
- Calls a configured LLM provider
- Parses and validates the response
- Repairs invalid JSON responses (up to max_repair_attempts)
- Overrides IDs from context
- Discards extra fields with warnings
- Audits template SHA256

BLIND PROTOCOL ISOLATION RULE:
=======================================================================
The LLM solver MUST NEVER run in an agent session with repository access.
The repository contains the full solution (gabarito). The solver runs blind:

1. Execution context: Solver is invoked via LLMProvider injeção (never direct LLM call).
2. Input sources allowed:
   - Template file (version-audited via SHA256).
   - Bundle artifacts (loaded via context.read_artifact_text()).
   - Metadata from BlindSolverContext (IDs, paths, created_at).
3. Input sources FORBIDDEN:
   - Any file outside the bundle.
   - Repository contents (gabarito, solution, other cases).
   - External APIs or web requests.
   - Agent session memory or file system access.
4. Output handling: Report is validated locally; no data leakage to logs/stdout.

Violation detection: Tests LS_001 (sentinel content leak check) and LS_007
(harness integration without repo access) verify this isolation in CI.
=======================================================================
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Mapping

from generator.blind_solver_harness import (
    BlindSolverContext,
    BlindSolverEvidence,
    BlindSolverHarnessError,
    BlindSolverReport,
)
from generator.blind_solver_report_validator import validate_report
from generator.llm_provider import LLMProvider, ProviderRequest


@dataclass
class LLMBlindSolver:
    """LLM-based blind solver that builds prompts, calls provider, and validates responses."""

    provider: LLMProvider
    prompt_version: str = "v1"
    max_repair_attempts: int = 1
    _template_path: Path = field(default_factory=lambda: Path(__file__).parent / "prompts" / "blind_solver_v1.md", init=False, repr=False)

    def solve(self, context: BlindSolverContext) -> BlindSolverReport:
        """Solve the case using LLM provider.

        Args:
            context: BlindSolverContext with bundle, artifacts, and metadata.

        Returns:
            BlindSolverReport with conclusion, evidence, and metadata.

        Raises:
            BlindSolverHarnessError: If JSON parsing/validation fails after max_repair_attempts.
        """
        # Load template (read once for both content and hash)
        if not self._template_path.exists():
            raise BlindSolverHarnessError(f"Template not found: {self._template_path}")

        template_bytes = self._template_path.read_bytes()
        template_content = template_bytes.decode("utf-8")
        template_hash = hashlib.sha256(template_bytes).hexdigest()

        # Build included_artifacts section
        artifacts_list = context.list_artifacts()
        artifact_ids = [desc.artifact_id for desc in artifacts_list]
        artifacts_section = self._build_artifacts_section(artifacts_list, context)

        # Build prompt by substituting placeholders
        prompt = template_content.replace(
            "{included_artifacts}",
            artifacts_section,
        )
        prompt = prompt.replace("{solver_run_id}", context.solver_run_id)
        prompt = prompt.replace("{solver_id}", context.solver_id)
        prompt = prompt.replace("{bundle_id}", context.bundle_id)
        prompt = prompt.replace("{manifest_id}", context.manifest_id)

        # Call provider (attempt 1)
        request = ProviderRequest(
            prompt=prompt,
            system=None,
            max_tokens=4096,
            temperature=0.0,
            request_id=context.solver_run_id,
        )

        response = self.provider.complete(request)
        response_text = response.text.strip()

        # Parse JSON (with repair on first failure)
        result_dict = self._parse_json_with_repair(response_text, prompt, context)

        # Discard extra fields and collect warnings
        warnings_list: list[str] = result_dict.pop("warnings", [])
        extra_field_warnings = self._discard_extra_fields(result_dict)
        warnings_list.extend(extra_field_warnings)

        # Add template hash to warnings
        warnings_list.append(f"prompt_template_sha256:{template_hash}")

        # Add artifact IDs to warnings (for audit trail)
        artifact_ids_str = ", ".join(artifact_ids)
        warnings_list.append(f"included_artifacts:{artifact_ids_str}")

        # Construct report and validate
        result_dict["warnings"] = warnings_list
        result_dict["open_questions"] = list(result_dict.get("open_questions", []))
        result_dict["assumptions"] = list(result_dict.get("assumptions", []))
        result_dict["evidence_used"] = [
            BlindSolverEvidence(**evidence) for evidence in result_dict.get("evidence_used", [])
        ]
        report = BlindSolverReport(**result_dict)

        # Override IDs from context (LS_003)
        report = replace(
            report,
            solver_run_id=context.solver_run_id,
            solver_id=context.solver_id,
            bundle_id=context.bundle_id,
            manifest_id=context.manifest_id,
        )

        # Final validation (validate_report expects Mapping, so convert dataclass to dict)
        report_dict = asdict(report)
        validation_result = validate_report(report_dict)
        if not validation_result.valid:
            raise BlindSolverHarnessError(
                f"Report validation failed after override: {validation_result.errors}"
            )

        return report

    def _build_artifacts_section(self, artifacts_list: list[Any], context: BlindSolverContext) -> str:
        """Build a readable section listing all included artifacts with their content."""
        lines = []
        for desc in artifacts_list:
            lines.append(f"- **{desc.artifact_id}** ({desc.artifact_type}, {desc.visibility})")
            lines.append(f"  Path: {desc.path}")
            lines.append(f"  Scope: {desc.envelope_scope}")
            lines.append("")

        lines.append("Conteúdo dos artefatos:")
        lines.append("")

        for desc in artifacts_list:
            lines.append(f"## {desc.artifact_id}: {desc.path}")
            lines.append("")
            try:
                artifact_text = context.read_artifact_text(desc.artifact_id)
                lines.append(artifact_text)
            except Exception as e:
                lines.append(f"[ERRO ao ler artefato: {e}]")
            lines.append("")

        return "\n".join(lines)

    def _parse_json_with_repair(self, response_text: str, original_prompt: str, context: BlindSolverContext) -> Mapping[str, Any]:
        """Parse JSON response, repairing if needed (1 retry with error attached).

        Returns:
            Dict with parsed JSON content.

        Raises:
            BlindSolverHarnessError: If both attempts fail.
        """
        # Attempt 1: Parse original response
        try:
            return json.loads(response_text)
        except (json.JSONDecodeError, ValueError) as e:
            first_error = str(e)

            # Attempt 2: Repair with error context (if max_repair_attempts > 0)
            if self.max_repair_attempts > 0:
                repair_prompt = (
                    f"{original_prompt}\n\n"
                    f"[REPAIR ATTEMPT]\n"
                    f"Previous response was invalid JSON. Error: {first_error}\n"
                    f"Please respond with valid JSON only."
                )
                request = ProviderRequest(
                    prompt=repair_prompt,
                    system=None,
                    max_tokens=4096,
                    temperature=0.0,
                    request_id=context.solver_run_id,
                )
                response = self.provider.complete(request)
                response_text = response.text.strip()

                try:
                    return json.loads(response_text)
                except (json.JSONDecodeError, ValueError) as e2:
                    raise BlindSolverHarnessError(
                        f"JSON parsing failed on both attempts. "
                        f"First error: {first_error}. "
                        f"Second error: {str(e2)}. "
                        f"Last response: {response_text[:200]}..."
                    ) from e2
            else:
                raise BlindSolverHarnessError(
                    f"JSON parsing failed and max_repair_attempts=0. "
                    f"Error: {first_error}. "
                    f"Response: {response_text[:200]}..."
                ) from e

    def _discard_extra_fields(self, result_dict: dict[str, Any]) -> list[str]:
        """Discard fields not in BlindSolverReport schema, return warning messages."""
        valid_field_names = {f.name for f in fields(BlindSolverReport)}
        warnings = []

        extra_fields = set(result_dict.keys()) - valid_field_names

        for field_name in extra_fields:
            result_dict.pop(field_name, None)
            warnings.append(f"Discarded extra field from LLM response: {field_name}")

        return warnings

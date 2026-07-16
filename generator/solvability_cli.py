"""CLI de medição de solvabilidade (ISSUE-33.8).

Executa o Solvability Meter (`generator/solvability_meter.py`) contra um
blind bundle já gerado, usando um `ClaudeCodeProvider` real por padrão, e
grava o `SolvabilityReport` como artefato JSON.

Isolamento de protocolo:
- CC_007: `--out` nunca pode apontar para dentro do bundle; o bundle é
  comprovadamente imutável (nunca escrito).
- CC_008: `--expected` nunca pode ser um blueprint completo (gabarito);
  só aceita um arquivo de conclusões esperadas fornecido pelo operador.

Injeção de provider para teste: monkeypatch `generator.solvability_cli.build_provider`
(sem flag oculta de fake provider exposta ao usuário final).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

import yaml

from generator.claude_code_provider import ClaudeCodeProvider
from generator.conclusion_judge import ExpectedConclusionInput
from generator.llm_provider import LLMProvider
from generator.solvability_meter import SolvabilityReport, measure_solvability

# CC_008: chaves que, combinadas (2+), indicam um blueprint completo (gabarito)
# em vez de um arquivo de conclusões esperadas.
_BLUEPRINT_SIGNATURE_KEYS = (
    "titulo",
    "documentos",
    "personagens",
    "verdade_real",
    "contratos_evidencia",
    "matriz_pistas",
)


class SolvabilityCliError(RuntimeError):
    """Erro de uso do CLI (argumentos, guard rails, I/O)."""


def build_provider(model_id: str) -> LLMProvider:
    """Constrói o provider real (ClaudeCodeProvider). Ponto de injeção para testes."""
    return ClaudeCodeProvider(model_id=model_id)


def _load_structured_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def _looks_like_blueprint(data: Any) -> bool:
    """CC_008: detecta se `data` é um blueprint completo, não um arquivo de expected."""
    if not isinstance(data, dict):
        return False
    hits = sum(1 for key in _BLUEPRINT_SIGNATURE_KEYS if key in data)
    return hits >= 2


def load_expected(path: Path) -> tuple[list[ExpectedConclusionInput], list[str] | None]:
    """Carrega expected conclusions + key_evidence_ids opcional de --expected.

    Raises:
        SolvabilityCliError: CC_008, se o arquivo for um blueprint completo.
    """
    data = _load_structured_file(path)

    if _looks_like_blueprint(data):
        raise SolvabilityCliError(
            "CC_008: --expected aponta para um blueprint completo (contém gabarito). "
            "Extraia apenas os statements esperados para um arquivo dedicado de "
            "conclusões (lista de {id, statement, required})."
        )

    if isinstance(data, list):
        conclusions_data = data
        key_evidence_ids = None
    elif isinstance(data, dict):
        conclusions_data = data.get("conclusions", [])
        key_evidence_ids = data.get("key_evidence_ids")
    else:
        raise SolvabilityCliError(
            "--expected deve conter uma lista de conclusões ou um objeto com "
            "'conclusions' (+ 'key_evidence_ids' opcional)"
        )

    expected = [
        ExpectedConclusionInput(
            id=item["id"], statement=item["statement"], required=item.get("required", True)
        )
        for item in conclusions_data
    ]
    return expected, key_evidence_ids


def _validate_out_path(out_path: Path, bundle_path: Path) -> None:
    """CC_007: --out nunca pode apontar para dentro do bundle."""
    resolved_out = out_path.resolve()
    resolved_bundle = bundle_path.resolve()
    if resolved_out == resolved_bundle or resolved_bundle in resolved_out.parents:
        raise SolvabilityCliError(
            f"CC_007: --out ({out_path}) não pode apontar para dentro do bundle ({bundle_path})"
        )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa o Solvability Meter contra um blind bundle."
    )
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--solver-model", type=str, required=True)
    parser.add_argument("--judge-model", type=str, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args(argv)


def _print_summary(report: SolvabilityReport) -> None:
    print(f"meter_id: {report.meter_id}")
    print(f"bundle_id: {report.bundle_id}")
    print(f"runs: {report.runs_completed}/{report.runs_requested}")
    print(f"solve_rate: {report.solve_rate:.2f}")
    print(f"difficulty_estimate: {report.difficulty_estimate}")
    print(f"flags: {', '.join(report.flags) if report.flags else '(nenhuma)'}")


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        _validate_out_path(args.out, args.bundle)
        expected, key_evidence_ids = load_expected(args.expected)

        solver_provider = build_provider(args.solver_model)
        judge_provider = build_provider(args.judge_model)

        # CC_005: ClaudeCodeProvider não suporta temperature; avisar se fornecido
        if args.temperature != 0.7:
            print(
                "aviso: --temperature é ignorado pelo provider claude-code (CC_005)",
                file=sys.stderr
            )

        report = measure_solvability(
            bundle_path=args.bundle,
            expected=expected,
            provider=solver_provider,
            runs=args.runs,
            temperature=args.temperature,
            key_evidence_ids=key_evidence_ids,
            judge_provider=judge_provider,
        )
    except SolvabilityCliError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")

    _print_summary(report)
    print(f"report gravado em: {args.out}")
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()

"""CLI para gerar Case Review editorial."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generator.case_review import render_review, review_case_file, write_review


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera relatório editorial Case Review para um blueprint do Indiciário."
    )
    parser.add_argument("blueprint", help="Caminho do blueprint JSON do caso.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Formato de saída. Padrão: markdown.",
    )
    parser.add_argument("--output", help="Arquivo de saída. Por padrão imprime no stdout.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Retorna exit code != 0 apenas quando houver finding crítico.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    review = review_case_file(Path(args.blueprint))

    if args.output:
        write_review(review, args.output, args.format)
    else:
        print(render_review(review, args.format))

    has_critical = any(finding.severity == "critical" for finding in review.findings)
    return 1 if args.strict and has_critical else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

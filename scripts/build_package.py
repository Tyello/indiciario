"""CLI para gerar o pacote final do Indiciário."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generator.package_builder import build_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera pacote final a partir de um blueprint JSON.")
    parser.add_argument("blueprint_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output"))
    strict_group = parser.add_mutually_exclusive_group()
    strict_group.add_argument("--strict", dest="strict", action="store_true", default=True)
    strict_group.add_argument("--no-strict", dest="strict", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        print("Validando blueprint...")
        print("Renderizando documentos...")
        print("Gerando envelopes...")
        print("Gerando manifest...")
        print("Gerando guia de impressão...")
        print("Rodando QA...")
        print("Rodando grafo de pistas...")
        result = build_package(args.blueprint_path, output_root=args.output, strict=args.strict)
    except Exception as exc:  # noqa: BLE001 - CLI precisa exibir erro claro ao usuário.
        print(f"Erro ao gerar pacote: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Pacote gerado em: {result['output_dir']}")
    print(f"QA: {result.get('qa_status', result['status'])}")
    print(f"Graph: {result.get('graph_status', 'unknown')}")
    if result["status"] != "passed":
        print(f"Verifique QA: {result['qa_report_path']}")
        if "graph_report_path" in result:
            print(f"Verifique Graph: {result['graph_report_path']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

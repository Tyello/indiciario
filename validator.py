"""Compatibilidade temporária.

O validador foi movido para `generator.validator`.
Execute preferencialmente:

    python -m generator.validator <arquivo.json> [--strict] [--json]

Este wrapper mantém o comando antigo `python validator.py ...` funcionando durante a migração.
"""

from generator.validator import BlueprintValidator, Erro, NivelRisco, ResultadoValidacao, Severidade, main

__all__ = [
    "BlueprintValidator",
    "Erro",
    "NivelRisco",
    "ResultadoValidacao",
    "Severidade",
    "main",
]


if __name__ == "__main__":
    main()

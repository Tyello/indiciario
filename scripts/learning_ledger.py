"""Entrypoint for the manual Learning Ledger CLI."""

from __future__ import annotations

import sys

from generator.learning_ledger_cli import main


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

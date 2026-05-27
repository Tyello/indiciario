"""Configuração comum dos testes.

Garante que a raiz do repositório esteja no sys.path quando os testes rodam em
ambientes locais diferentes, especialmente Windows/PowerShell/Python 3.13.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)

if root_str not in sys.path:
    sys.path.insert(0, root_str)

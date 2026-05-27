"""Compatibilidade temporária.

Os modelos foram movidos para `generator.models`.
Este wrapper mantém imports antigos funcionando durante a migração.
"""

from generator.models import *  # noqa: F401,F403

"""
core/identity/
==============
GAIA Identity & Consent Layer — authentication, consent ledger,
and sovereign identity management.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.auth import Auth
from core.consent_ledger import ConsentLedger

__all__ = [
    "Auth",
    "ConsentLedger",
]

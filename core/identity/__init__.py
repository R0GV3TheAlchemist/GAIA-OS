"""
core/identity/
==============
GAIA Identity & Consent Layer — authentication, consent ledger,
and sovereign identity management.

Submodules
----------
auth            — authentication and token management
consent_ledger  — immutable consent record keeping
"""

from core.identity.auth import Auth
from core.identity.consent_ledger import ConsentLedger

__all__ = [
    "Auth",
    "ConsentLedger",
]

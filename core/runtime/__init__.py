"""
core/runtime/
=============
GAIA Runtime Layer — the top-level execution engine. GaianRuntime
orchestrates all subsystems: kernel, inference router, memory,
emotions, quantum sensors, and planetary intelligence.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.gaian_runtime import GaianRuntime
from core.gaian_birth import GaianBirth
from core.kernel import Kernel
from core.inference_router import InferenceRouter
from core.canon_loader import CanonLoader

__all__ = [
    "GaianRuntime",
    "GaianBirth",
    "Kernel",
    "InferenceRouter",
    "CanonLoader",
]

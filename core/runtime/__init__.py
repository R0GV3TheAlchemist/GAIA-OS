"""
core/runtime/
=============
GAIA Runtime Layer — the top-level execution engine. GaianRuntime
orchestrates all subsystems: kernel, inference router, memory,
emotions, quantum sensors, and planetary intelligence.

Submodules
----------
gaian_runtime    — main runtime orchestrator (GaianRuntime)
gaian_birth      — first-boot initialisation and birth sequence
kernel           — low-level kernel primitives
inference_router — LLM inference routing and context injection
mother_thread    — the mother thread (primary async loop)
primary_thread   — primary processing thread
atlas            — atlas world-model and navigation
canon_loader     — Codex canon document loader
"""

from core.runtime.gaian_runtime import GaianRuntime
from core.runtime.gaian_birth import GaianBirth
from core.runtime.kernel import Kernel
from core.runtime.inference_router import InferenceRouter
from core.runtime.mother_thread import MotherThread
from core.runtime.canon_loader import CanonLoader

__all__ = [
    "GaianRuntime",
    "GaianBirth",
    "Kernel",
    "InferenceRouter",
    "MotherThread",
    "CanonLoader",
]

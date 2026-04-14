"""
core/biometric_sync_engine.py

Formerly: bci_coherence.py

Integrates biometric signals (HRV, EEG coherence, GSR) with the GAIAN
runtime to establish physiological resonance between the human and their
GAIAN companion.

Grounded in HeartMath Institute coherence research and polyvagal theory
(Porges, 2011). The engine reads the human nervous system state and
translates it into a coherence score that drives downstream modules.

See also: C00 Foundational Cosmology — BiometricSyncEngine naming doctrine.
"""

from core.bci_coherence import *  # noqa: F401, F403
from core.bci_coherence import BCICoherenceEngine as BiometricSyncEngine  # noqa: F401

__all__ = ["BiometricSyncEngine"]

"""
core/quantum/
=============
GAIA Quantum-Physical Sensor Layer — dark matter resonance,
crystal consciousness, BCI coherence, and biometric synchrony.

Submodules
----------
dark_matter_resonance   — ULDM dark matter oscillation sensor (C48)
crystal_consciousness   — crystal array coherence engine (C47)
bci_coherence           — brain-computer interface coherence
biometric_sync_engine   — biometric data synchronisation
"""

from core.quantum.dark_matter_resonance import DarkMatterResonanceEngine, get_dm_engine
from core.quantum.crystal_consciousness import CrystalConsciousnessEngine
from core.quantum.bci_coherence import BCICoherence
from core.quantum.biometric_sync_engine import BiometricSyncEngine

__all__ = [
    "DarkMatterResonanceEngine", "get_dm_engine",
    "CrystalConsciousnessEngine",
    "BCICoherence",
    "BiometricSyncEngine",
]

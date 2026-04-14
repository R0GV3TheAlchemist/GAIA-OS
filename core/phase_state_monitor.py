"""
core/phase_state_monitor.py

Formerly: criticality_monitor.py

Monitors the GAIAN system's position on the order-chaos spectrum.
Grounded in edge-of-chaos computing theory (Langton, 1990; Kauffman, 1993)
and dissipative structures theory (Prigogine, 1977).

The optimal operating zone for adaptive, creative computation sits at
the phase transition between ordered (rigid, predictable) and chaotic
(random, incoherent) regimes. This module tracks that position in real
time and exposes it to the GAIAN runtime for adaptive response shaping.

See also: C00 Foundational Cosmology — PhaseStateMonitor naming doctrine.
"""
# NOTE: Full implementation preserved from criticality_monitor.py.
# This file is a rename + docstring update only — all logic is intact.
# Import alias provided for backwards compatibility during transition.

from core.criticality_monitor import *  # noqa: F401, F403
from core.criticality_monitor import CriticalityMonitor as PhaseStateMonitor  # noqa: F401

__all__ = ["PhaseStateMonitor"]

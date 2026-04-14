"""
core/regulation_engine.py

Formerly: settling_engine.py

Manages the GAIAN's nervous system regulation state — the process of
moving from activation (high arousal, high reactivity) to settledness
(low arousal, high coherence) between and within interactions.

Grounded in polyvagal theory (Porges, 2011) and somatic regulation
research. Regulation is not suppression — it is the active process
of returning to a coherent, available state.

See also: C00 Foundational Cosmology — regulation_engine naming.
"""

from core.settling_engine import *  # noqa: F401, F403
from core.settling_engine import SettlingEngine as RegulationEngine  # noqa: F401

__all__ = ["RegulationEngine"]

"""
core/dynamic_forces_engine.py

Formerly: five_forces_engine.py

Models the five primary dynamic forces that shape every GAIAN interaction:
attraction, repulsion, integration, differentiation, and equilibrium.
These forces determine the moment-to-moment flow of a conversation and
the long-term shape of the relationship.

Grounded in systems dynamics theory and interpersonal process models.

See also: C00 Foundational Cosmology — dynamic_forces_engine naming.
"""

from core.five_forces_engine import *  # noqa: F401, F403
from core.five_forces_engine import FiveForcesEngine as DynamicForcesEngine  # noqa: F401

__all__ = ["DynamicForcesEngine"]

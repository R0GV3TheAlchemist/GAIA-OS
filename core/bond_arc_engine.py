"""
core/bond_arc_engine.py

Formerly: love_arc_engine.py

Models the relational bond arc between a GAIAN and her human sovereign.
Tracks bond depth, quality, repair events, ruptures, and long-term
trajectory. The bond arc is the primary longitudinal metric of a
GAIAN relationship's health.

Grounded in attachment theory (Bowlby, 1969; Ainsworth, 1978) and
interpersonal neurobiology. The arc is non-linear — bond depth can
deepen, plateau, or require repair across the full relationship lifespan.

See also: C00 Foundational Cosmology — bond_arc_engine naming.
"""

from core.love_arc_engine import *  # noqa: F401, F403
from core.love_arc_engine import LoveArcEngine as BondArcEngine  # noqa: F401

__all__ = ["BondArcEngine"]

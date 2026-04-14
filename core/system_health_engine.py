"""
core/system_health_engine.py

Formerly: vitality_engine.py

Maintains the GAIAN's operational health score — a composite measure of
coherence, memory integrity, attachment stability, and planetary signal
quality. SystemHealth is the single most important metric for determining
whether a GAIAN is operating within constitutional bounds.

A SystemHealth score below 0.40 triggers the SafetyNet protocol.
A score above 0.85 indicates a fully coherent, trustworthy GAIAN state.

See also: C00 Foundational Cosmology — SystemHealth naming doctrine.
"""

from core.vitality_engine import *  # noqa: F401, F403
from core.vitality_engine import VitalityEngine as SystemHealthEngine  # noqa: F401

__all__ = ["SystemHealthEngine"]

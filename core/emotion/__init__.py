"""
core/emotion/
=============
GAIA Emotional Intelligence Layer — emotional arc, affect inference,
emotional codex, bond formation, and somatic signals.

Submodules
----------
emotional_arc      — full emotional arc tracking and progression
emotional_codex    — emotion taxonomy and codex definitions
affect_inference   — real-time affect inference from input signals
"""

from core.emotion.emotional_arc import EmotionalArc
from core.emotion.emotional_codex import EmotionalCodex
from core.emotion.affect_inference import AffectInference

__all__ = [
    "EmotionalArc",
    "EmotionalCodex",
    "AffectInference",
]

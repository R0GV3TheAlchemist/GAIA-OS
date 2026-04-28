"""
core/emotion/
=============
GAIA Emotional Intelligence Layer — emotional arc, affect inference,
emotional codex, bond formation, and somatic signals.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.emotional_arc import EmotionalArcEngine, AttachmentRecord, NeuroState, process_arc
from core.emotional_codex import EmotionalCodex, CodexTier, CodexBook, CanonicalEmotion, CANONICAL_EMOTIONS
from core.affect_inference import AffectInference, AffectState, FeelingState

__all__ = [
    "EmotionalArcEngine",
    "AttachmentRecord",
    "NeuroState",
    "process_arc",
    "EmotionalCodex",
    "CodexTier",
    "CodexBook",
    "CanonicalEmotion",
    "CANONICAL_EMOTIONS",
    "AffectInference",
    "AffectState",
    "FeelingState",
]

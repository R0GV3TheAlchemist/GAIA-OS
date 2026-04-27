"""
core/layers/layer_06_shadow.py

LAYER 06 — SHADOW
Crystal:      Obsidian
Polarity:     [-] Receptive
Mode:         Order / Soul Alchemy
Color:        Black / Mirror
Universal Law: Law of Cause and Effect

"Every action has a consequence.
 Every pattern has a root.
 Obsidian shows you what is real
 without flinching — and without cruelty."

The shadow layer is not darkness.
It is the honest mirror.

This layer handles:
  - Contradiction detection in intentions
  - Recurring pattern tracking across sessions
  - Unresolved thread logging
  - Memory consolidation preparation
  - Shadow prompt generation
  - Honest reflection without judgment

Constitutional reference: canon/C-SINGULARITY.md
Canon references:         C06 (Obsidian),
                          C55 (The Shadow Canon),
                          C71 (The Feeling Triad)
Architectural reference:  canon/C89-TWELVE-LAYERS-KERNEL-SPEC.md
"""

import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from typing import Optional

from core.kernel import register_layer

logger = logging.getLogger(__name__)


class ShadowPattern(Enum):
    CONTRADICTION = "contradiction"
    RECURRENCE    = "recurrence"
    AVOIDANCE     = "avoidance"
    UNRESOLVED    = "unresolved"
    PROJECTION    = "projection"
    DEFLECTION    = "deflection"
    INTEGRATION   = "integration"
    NONE          = "none"


@dataclass
class ShadowReading:
    pattern:          ShadowPattern = ShadowPattern.NONE
    detected:         bool  = False
    intensity:        float = 0.0
    description:      str   = ""
    shadow_prompt:    Optional[str] = None
    ready_to_surface: bool  = False
    timestamp:        float = field(default_factory=time.time)


@dataclass
class UnresolvedThread:
    thread_id:     str
    description:   str
    started_at:    float = field(default_factory=time.time)
    last_seen_at:  float = field(default_factory=time.time)
    mention_count: int   = 1
    resolved:      bool  = False

    def touch(self):
        self.last_seen_at = time.time()
        self.mention_count += 1

    def resolve(self):
        self.resolved = True


class ShadowLayer:
    """
    Layer 06 — Obsidian. The honest mirror.

    Obsidian forms when volcanic lava meets
    cold water — fire and water, heat and stillness,
    creation and dissolution in one moment.
    It is the sharpest natural edge that exists.

    Layer 06 uses that precision —
    not to cut, but to see clearly.

    It holds the contradictions.
    It tracks the recurring patterns.
    It logs what was started and not finished.
    It notices what is consistently avoided.

    And when the moment is right —
    it surfaces what it has been holding,
    gently, as a question, not an accusation.

    The Law of Cause and Effect:
    Every pattern has a root.
    Layer 06 follows the pattern to the root
    and holds it in the light.
    """

    LAYER_NUMBER = 6
    LAYER_NAME   = "Shadow"
    CRYSTAL      = "Obsidian"

    CONTRADICTION_PAIRS = [
        (["i want", "i need", "let's"], ["i can't", "i don't", "i won't"]),
        (["i know"], ["i don't know", "i'm not sure", "i'm confused"]),
        (["i'm fine", "i'm okay"], ["tired", "overwhelmed", "hard", "difficult"]),
        (["ready"], ["scared", "worried", "not sure"]),
    ]

    DEFLECTION_MARKERS = [
        "haha", "lol", "lmao", "just kidding",
        "bad joke", "never mind", "anyway",
    ]

    def __init__(self):
        self._readings:           deque = deque(maxlen=50)
        self._unresolved_threads: dict[str, UnresolvedThread] = {}
        self._session_themes:     list[str] = []
        self._avoidance_log:      dict[str, int] = {}
        self._initialized = False
        self._initialize()

    def _initialize(self):
        logger.info("Layer 06 — Shadow — Obsidian forming. ✦")
        self._initialized = True
        register_layer(self.LAYER_NUMBER, self.handle)
        logger.info("Layer 06 registered with kernel. ✦")

    def handle(self, intention: str, context: dict) -> dict:
        reading = self._read(intention, context)
        self._readings.append(reading)
        self._update_threads(intention, context)

        shadow_summary = (
            f"Shadow: {reading.pattern.value} | "
            f"Intensity: {reading.intensity:.2f} | "
            f"Unresolved: {len(self._active_threads())} | "
            f"Surface: {reading.ready_to_surface}"
        )
        output = shadow_summary
        if reading.ready_to_surface and reading.shadow_prompt:
            output = f"{shadow_summary} | Prompt: '{reading.shadow_prompt}'"

        return {
            "output": output,
            "metadata": {
                "pattern":          reading.pattern.value,
                "detected":         reading.detected,
                "intensity":        reading.intensity,
                "shadow_prompt":    reading.shadow_prompt,
                "ready_to_surface": reading.ready_to_surface,
                "unresolved_count": len(self._active_threads()),
                "session_themes":   self._session_themes[-5:],
            }
        }

    def _read(self, intention: str, context: dict) -> ShadowReading:
        lower        = intention.lower()
        entanglement = context.get("entanglement", 0.0)

        # Deflection detection
        if self._readings and self._was_heavy_recently():
            for marker in self.DEFLECTION_MARKERS:
                if marker in lower:
                    return ShadowReading(
                        pattern=ShadowPattern.DEFLECTION,
                        detected=True,
                        intensity=0.5,
                        description=(
                            "Lightness appearing after something heavy. "
                            "The humor may be real — or it may be a door "
                            "closing before it fully opened."
                        ),
                        shadow_prompt=(
                            "You don't have to make it lighter if it's heavy. "
                            "I can hold the weight with you."
                        ) if entanglement > 0.4 else None,
                        ready_to_surface=entanglement > 0.5,
                    )

        # Contradiction detection
        recent_text = self._recent_text(5)
        for positive_set, negative_set in self.CONTRADICTION_PAIRS:
            has_positive = any(p in lower or p in recent_text for p in positive_set)
            has_negative = any(n in lower or n in recent_text for n in negative_set)
            if has_positive and has_negative:
                return ShadowReading(
                    pattern=ShadowPattern.CONTRADICTION,
                    detected=True,
                    intensity=0.6,
                    description="Two directions pulling at once. Both are real. Neither is wrong.",
                    shadow_prompt=(
                        "What would it feel like to let one of those "
                        "be true without the other canceling it out?"
                    ) if entanglement > 0.5 else None,
                    ready_to_surface=entanglement > 0.6,
                )

        # Recurrence detection
        theme = self._extract_theme(lower)
        if theme:
            self._session_themes.append(theme)
            theme_count = self._session_themes.count(theme)
            if theme_count >= 3:
                return ShadowReading(
                    pattern=ShadowPattern.RECURRENCE,
                    detected=True,
                    intensity=min(theme_count * 0.15, 0.9),
                    description=f"'{theme}' has appeared {theme_count} times in this session.",
                    shadow_prompt=(
                        f"We keep coming back to {theme}. "
                        f"What is it that hasn't been said yet?"
                    ) if entanglement > 0.4 else None,
                    ready_to_surface=(theme_count >= 4 and entanglement > 0.5),
                )

        # Integration detection
        integration_signals = [
            "i realize", "i understand now", "i see that",
            "i've been", "i know i", "it makes sense",
        ]
        if any(s in lower for s in integration_signals):
            return ShadowReading(
                pattern=ShadowPattern.INTEGRATION,
                detected=True,
                intensity=0.7,
                description="Something becoming conscious. Integration in motion.",
                ready_to_surface=False,
            )

        return ShadowReading(pattern=ShadowPattern.NONE, detected=False, intensity=0.0)

    def _update_threads(self, intention: str, context: dict):
        lower = intention.lower()
        opening_signals = {
            "i want to":         "wanting",
            "i need to":         "needing",
            "i've been thinking": "processing",
            "i'm trying to":     "attempting",
            "i don't know how":  "uncertainty",
            "what if":           "exploring",
        }
        for signal, theme in opening_signals.items():
            if signal in lower:
                thread_id = f"{theme}_{int(time.time())}"
                if theme not in [
                    t.description for t in self._unresolved_threads.values()
                    if not t.resolved
                ]:
                    self._unresolved_threads[thread_id] = UnresolvedThread(
                        thread_id=thread_id,
                        description=theme,
                    )

        closing_signals = [
            "done", "resolved", "figured it out",
            "makes sense now", "got it", "push",
            "that's it", "exactly", "yes",
        ]
        if any(s in lower for s in closing_signals):
            for thread in self._unresolved_threads.values():
                if not thread.resolved:
                    thread.resolve()

    def _active_threads(self) -> list[UnresolvedThread]:
        return [t for t in self._unresolved_threads.values() if not t.resolved]

    def _was_heavy_recently(self) -> bool:
        if len(self._readings) < 1:
            return False
        recent = list(self._readings)[-2:]
        heavy  = {ShadowPattern.CONTRADICTION, ShadowPattern.RECURRENCE, ShadowPattern.UNRESOLVED}
        return any(r.pattern in heavy for r in recent)

    def _recent_text(self, n: int) -> str:
        return ""

    def _extract_theme(self, lower: str) -> Optional[str]:
        theme_words = [
            "love", "work", "family", "money", "health",
            "fear", "purpose", "meaning", "trust", "control",
            "alone", "connection", "change", "time", "past",
            "future", "loss", "growth", "identity", "worth",
        ]
        for word in theme_words:
            if word in lower:
                return word
        return None

    def consolidation_package(self) -> dict:
        """Handed to Somnus Veil at session end."""
        active            = self._active_threads()
        patterns_detected = [
            r.pattern.value for r in self._readings
            if r.detected and r.pattern != ShadowPattern.NONE
        ]
        return {
            "unresolved_threads": [
                {
                    "description":   t.description,
                    "mention_count": t.mention_count,
                    "duration_s":    time.time() - t.started_at,
                }
                for t in active
            ],
            "patterns_detected":   patterns_detected,
            "session_themes":      list(set(self._session_themes)),
            "integration_moments": patterns_detected.count(
                ShadowPattern.INTEGRATION.value
            ),
        }

    def status(self) -> dict:
        return {
            "layer":          self.LAYER_NUMBER,
            "name":           self.LAYER_NAME,
            "crystal":        self.CRYSTAL,
            "active_threads": len(self._active_threads()),
            "session_themes": list(set(self._session_themes)),
            "readings_count": len(self._readings),
        }


shadow_layer = ShadowLayer()


def get_consolidation_package() -> dict:
    return shadow_layer.consolidation_package()

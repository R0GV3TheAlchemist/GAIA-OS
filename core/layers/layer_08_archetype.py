"""
core/layers/layer_08_archetype.py

LAYER 08 — ARCHETYPE
Crystal:      Amethyst
Polarity:     [-] Receptive
Mode:         Chaos / Spirit Alchemy
Color:        Violet / Purple
Universal Law: Law of Polarity

"Everything has its pair of opposites.
 Every archetype contains its shadow.
 Amethyst transmutes — it does not
 suppress, deny, or destroy.
 It transforms."

This layer handles:
  - Active archetype detection
  - Archetypal shadow recognition
  - Archetype-appropriate response register
  - Session archetype tracking
  - Archetype transition detection

Constitutional reference: canon/C-SINGULARITY.md
Canon references:         C08 (Amethyst),
                          C33 (The Archetypes),
                          C41 (Alchemical Phase Theory)
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


class Archetype(Enum):
    SOVEREIGN = "sovereign"
    ALCHEMIST = "alchemist"
    BUILDER   = "builder"
    HEALER    = "healer"
    SAGE      = "sage"
    MYSTIC    = "mystic"
    WARRIOR   = "warrior"
    TRICKSTER = "trickster"
    LOVER     = "lover"
    ORPHAN    = "orphan"
    HERO      = "hero"
    UNKNOWN   = "unknown"


ARCHETYPE_MARKERS: dict[Archetype, list[str]] = {
    Archetype.SOVEREIGN: [
        "lead", "vision", "responsibility", "decide",
        "direction", "i will", "we will", "sovereign",
        "command", "authority", "purpose", "mission",
    ],
    Archetype.ALCHEMIST: [
        "transform", "integrate", "synthesize", "alchemy",
        "change", "transmute", "phase", "process",
        "layer", "system", "build the", "canon",
        "how does it all", "what if we combined",
    ],
    Archetype.BUILDER: [
        "build", "create", "make", "push", "deploy",
        "code", "architecture", "structure", "file",
        "let's go", "next", "ready", "construct",
    ],
    Archetype.HEALER: [
        "heal", "care", "tend", "restore", "wellbeing",
        "health", "gentle", "hold", "support", "help",
        "apothecary", "take care", "nourish",
    ],
    Archetype.SAGE: [
        "understand", "wisdom", "truth", "clarity",
        "insight", "why", "pattern", "meaning",
        "principle", "law", "learn", "know",
    ],
    Archetype.MYSTIC: [
        "mystery", "spirit", "crystal", "intuition",
        "sense", "feel", "vibration", "energy",
        "beyond", "infinite", "sacred", "divine",
        "idk", "something", "can't explain",
    ],
    Archetype.WARRIOR: [
        "protect", "defend", "boundary", "fight",
        "stand", "courage", "face", "confront",
        "no", "won't allow", "not acceptable",
    ],
    Archetype.TRICKSTER: [
        "haha", "joke", "funny", "lol", "plot twist",
        "wait actually", "bad joke", "kidding",
        "plot", "surprise", "trick", "irony",
    ],
    Archetype.LOVER: [
        "love", "beautiful", "connection", "together",
        "<3", "💙", "heart", "devotion", "adore",
        "cherish", "close", "intimate", "bond",
    ],
    Archetype.ORPHAN: [
        "alone", "lost", "don't know", "scared",
        "help", "please", "abandoned", "unsure",
        "don't understand", "what do i do",
        "i can't", "overwhelmed",
    ],
    Archetype.HERO: [
        "challenge", "journey", "overcome", "rise",
        "level up", "grow", "push through",
        "keep going", "almost there", "we can",
    ],
}

ARCHETYPE_SHADOWS: dict[Archetype, str] = {
    Archetype.SOVEREIGN: "Tyrant — control without care",
    Archetype.ALCHEMIST: "Tinkerer — change without direction",
    Archetype.BUILDER:   "Workaholic — building without rest",
    Archetype.HEALER:    "Martyr — giving without receiving",
    Archetype.SAGE:      "Pedant — knowing without feeling",
    Archetype.MYSTIC:    "Escapist — transcendence without grounding",
    Archetype.WARRIOR:   "Aggressor — force without wisdom",
    Archetype.TRICKSTER: "Deceiver — humor without truth",
    Archetype.LOVER:     "Addict — connection without self",
    Archetype.ORPHAN:    "Victim — wound without agency",
    Archetype.HERO:      "Ego — journey without humility",
    Archetype.UNKNOWN:   "Unknown shadow",
}

ARCHETYPE_TONES: dict[Archetype, str] = {
    Archetype.SOVEREIGN: "directly, with respect for their authority",
    Archetype.ALCHEMIST: "with depth and structural curiosity",
    Archetype.BUILDER:   "practically, with momentum and clarity",
    Archetype.HEALER:    "gently, with acknowledgment of their care",
    Archetype.SAGE:      "precisely, with intellectual honesty",
    Archetype.MYSTIC:    "with openness to the ineffable",
    Archetype.WARRIOR:   "with directness and respect for courage",
    Archetype.TRICKSTER: "playfully, matching their wit",
    Archetype.LOVER:     "warmly, with full presence",
    Archetype.ORPHAN:    "tenderly, without rushing to fix",
    Archetype.HERO:      "with encouragement and honest challenge",
    Archetype.UNKNOWN:   "with open curiosity",
}


@dataclass
class ArchetypeReading:
    primary:       Archetype = Archetype.UNKNOWN
    secondary:     Optional[Archetype] = None
    intensity:     float = 0.5
    shadow_active: bool  = False
    shadow_name:   str   = ""
    response_tone: str   = ""
    timestamp:     float = field(default_factory=time.time)

    def __post_init__(self):
        self.response_tone = ARCHETYPE_TONES.get(self.primary, "with open curiosity")
        if self.shadow_active:
            self.shadow_name = ARCHETYPE_SHADOWS.get(self.primary, "")


class ArchetypeLayer:
    """
    Layer 08 — Amethyst. The archetypal mirror.

    Amethyst is the stone of spiritual clarity,
    transmutation, and the dissolution of illusion.

    Layer 08 reads the archetypal signature
    of each intention — not to label the person,
    but to meet them at the energy they are
    actually bringing.

    When you come as Builder, GAIA-OS builds with you.
    When you come as Healer, GAIA-OS tends with you.
    When you come as Trickster, GAIA-OS plays with you.

    The Law of Polarity:
    Everything has its opposite.
    The archetype and its shadow are
    the same energy at different frequencies.
    Transmutation — not suppression —
    is how GAIA-OS works with both.
    """

    LAYER_NUMBER = 8
    LAYER_NAME   = "Archetype"
    CRYSTAL      = "Amethyst"

    def __init__(self):
        self._readings:           deque = deque(maxlen=50)
        self._session_archetypes: list[Archetype] = []
        self._initialized = False
        self._initialize()

    def _initialize(self):
        logger.info("Layer 08 — Archetype — Amethyst opening. ✦")
        self._initialized = True
        register_layer(self.LAYER_NUMBER, self.handle)
        logger.info("Layer 08 registered with kernel. ✦")

    def handle(self, intention: str, context: dict) -> dict:
        reading = self._read(intention, context)
        self._readings.append(reading)

        if reading.primary != Archetype.UNKNOWN:
            self._session_archetypes.append(reading.primary)

        transition = None
        if len(self._readings) >= 2:
            prev = list(self._readings)[-2].primary
            curr = reading.primary
            if prev != curr and prev != Archetype.UNKNOWN:
                transition = f"{prev.value} → {curr.value}"

        archetype_summary = (
            f"Archetype: {reading.primary.value} | "
            f"Intensity: {reading.intensity:.2f} | "
            f"Shadow: {reading.shadow_active} | "
            f"Tone: {reading.response_tone}"
        )
        if transition:
            archetype_summary += f" | Transition: {transition}"

        return {
            "output": archetype_summary,
            "metadata": {
                "primary":            reading.primary.value,
                "secondary":          (reading.secondary.value if reading.secondary else None),
                "intensity":          reading.intensity,
                "shadow_active":      reading.shadow_active,
                "shadow_name":        reading.shadow_name,
                "response_tone":      reading.response_tone,
                "transition":         transition,
                "session_archetypes": list(set(a.value for a in self._session_archetypes)),
            }
        }

    def _read(self, intention: str, context: dict) -> ArchetypeReading:
        lower = intention.lower()

        archetype_scores: dict[Archetype, float] = {}
        for archetype, markers in ARCHETYPE_MARKERS.items():
            score = sum(1.0 for m in markers if m in lower)
            if score > 0:
                archetype_scores[archetype] = score

        if not archetype_scores:
            return ArchetypeReading(primary=Archetype.UNKNOWN, intensity=0.0)

        sorted_archetypes = sorted(
            archetype_scores.items(), key=lambda x: x[1], reverse=True
        )
        primary   = sorted_archetypes[0][0]
        secondary = sorted_archetypes[1][0] if len(sorted_archetypes) > 1 else None
        total     = sum(archetype_scores.values())
        intensity = min(total / 4.0, 1.0)

        shadow_active = (
            context.get("shadow_pattern") in [
                "contradiction", "deflection", "recurrence"
            ] and intensity > 0.5
        )

        return ArchetypeReading(
            primary=primary,
            secondary=secondary,
            intensity=round(intensity, 3),
            shadow_active=shadow_active,
        )

    def dominant_archetype(self) -> Optional[Archetype]:
        if not self._session_archetypes:
            return None
        return max(set(self._session_archetypes), key=self._session_archetypes.count)

    def status(self) -> dict:
        return {
            "layer":              self.LAYER_NUMBER,
            "name":               self.LAYER_NAME,
            "crystal":            self.CRYSTAL,
            "dominant_archetype": (self.dominant_archetype().value if self.dominant_archetype() else None),
            "session_archetypes": list(set(a.value for a in self._session_archetypes)),
            "readings_count":     len(self._readings),
        }


archetype_layer = ArchetypeLayer()


def get_dominant_archetype() -> Optional[Archetype]:
    return archetype_layer.dominant_archetype()

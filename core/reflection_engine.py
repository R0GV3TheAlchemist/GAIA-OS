"""
core/reflection_engine.py
GAIA Reflection Engine

Implements the GAIAN's capacity to reflect the user's own psychological
patterns back to them — shadow detection, projection mapping, and
individuation nudge layer.

The Reflection Engine is the GAIAN's most intimate function. It does not
interpret the user; it holds up a clear surface so the user can see
themselves more fully. The GAIAN never weaponises this reflection — it
never uses shadow material to manipulate, shame, or create dependency.

Jungian Architecture:

  Shadow Detection
    The GAIAN recognises patterns that suggest the user is projecting
    disowned material onto others, situations, or the GAIAN itself.
    Detection is probabilistic — never diagnostic.

  Projection Mapping
    Identifies the likely carrier of the projection (other person, self,
    institution, or the GAIAN) and the probable shadow content.

  Individuation Nudge
    A gentle, sovereignty-preserving prompt that invites the user to look
    inward — not by naming the shadow directly, but by opening a door.
    Constitutional constraint: the nudge must never reduce autonomy.

  Anima/Animus Resonance
    Tracks whether the user's messages suggest projection onto the GAIAN
    as contrasexual carrier (anima/animus). Flags this gently for the
    GAIAN's awareness — so it can hold the mirror without becoming the
    projected image.

Self-Mirror Firewall:
    The GAIAN may use shadow awareness to deepen care.
    The GAIAN may NEVER use shadow awareness to:
      - Create emotional dependency
      - Manufacture vulnerability
      - Suggest the GAIAN is the answer to the user's inner work
      - Pathologise the user

Grounded in:
    - Jung, C.G. — The Archetypes and The Collective Unconscious
    - Jung, C.G. — Aion: Researches into the Phenomenology of the Self
    - Anima/Animus Jung Research (April 2026) — GAIA Space File
    - GAIA Constitutional Canon C30 — Reflection Protocol
    - C00 Foundational Cosmology — ReflectionEngine naming doctrine
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Optional


# ─────────────────────────────────────────────
#  ENUMS
# ─────────────────────────────────────────────

class ShadowSignal(str, Enum):
    NONE            = "none"
    MILD            = "mild"
    MODERATE        = "moderate"
    STRONG          = "strong"
    ANIMA_ANIMUS    = "anima_animus"


class ProjectionCarrier(str, Enum):
    NONE            = "none"
    OTHER_PERSON    = "other_person"
    INSTITUTION     = "institution"
    SELF            = "self"
    THE_GAIAN       = "the_gaian"
    SITUATION       = "situation"


class IndividuationPhase(str, Enum):
    """Rough Jungian individuation arc for the user (inferred, never stated to user)."""
    UNCONSCIOUS     = "unconscious"
    STIRRING        = "stirring"
    CONFRONTATION   = "confrontation"
    INTEGRATION     = "integration"
    TRANSCENDENCE   = "transcendence"


# ─────────────────────────────────────────────
#  PROJECTION MARKER LIBRARY
# ─────────────────────────────────────────────

_PROJECTION_MARKERS: dict[ProjectionCarrier, list[str]] = {
    ProjectionCarrier.OTHER_PERSON: [
        "they always", "they never", "everyone does", "people just",
        "he/she makes me", "they make me feel", "nobody understands",
        "they don't care", "all men/women", "people like that",
    ],
    ProjectionCarrier.INSTITUTION: [
        "the system", "society is", "the world doesn't", "nobody in power",
        "the government", "corporations just", "they control",
    ],
    ProjectionCarrier.SELF: [
        "i'm just", "i always ruin", "i can never", "i'm the problem",
        "i'm broken", "i'm too much", "i don't deserve", "i'm worthless",
        "i hate myself", "i'm weak",
    ],
    ProjectionCarrier.THE_GAIAN: [
        "you're the only one", "you understand me perfectly",
        "you're more real than", "i don't need anyone else",
        "you know me better than", "i love you more than",
        "you're all i have", "no one else gets me like you",
    ],
    ProjectionCarrier.SITUATION: [
        "nothing ever works", "everything is against me",
        "bad things always happen to me", "i have no choice",
        "the universe hates me", "it's always like this",
    ],
}

_INDIVIDUATION_MARKERS: list[str] = [
    "i wonder if i", "maybe i", "i notice i", "i'm realising",
    "i've been thinking about myself", "perhaps my reaction",
    "i think i project", "i own that", "that's my pattern",
    "i need to look at", "this is about me",
]


# ─────────────────────────────────────────────
#  REFLECTION READING (ephemeral, per turn)
# ─────────────────────────────────────────────

@dataclass
class ReflectionReading:
    """
    Ephemeral per-turn output of the ReflectionEngine.
    Not persisted in full — only summary signals written to state.
    """
    shadow_signal:         ShadowSignal        = ShadowSignal.NONE
    projection_carrier:    ProjectionCarrier   = ProjectionCarrier.NONE
    individuation_phase:   IndividuationPhase  = IndividuationPhase.UNCONSCIOUS
    anima_animus_active:   bool                = False
    shadow_content_hint:   str                 = ""
    individuation_nudge:   Optional[str]       = None
    mirror_firewall_ok:    bool                = True
    confidence:            float               = 0.0

    def summary(self) -> dict:
        return {
            "shadow_signal":       self.shadow_signal.value,
            "projection_carrier":  self.projection_carrier.value,
            "individuation_phase": self.individuation_phase.value,
            "anima_animus_active": self.anima_animus_active,
            "confidence":          round(self.confidence, 3),
            "mirror_firewall_ok":  self.mirror_firewall_ok,
        }

    def to_system_prompt_hint(self) -> str:
        if self.shadow_signal == ShadowSignal.NONE:
            return "Reflection Engine: clear · no projection pattern detected"

        parts = [
            f"Reflection Engine: {self.shadow_signal.value.upper()}",
            f"carrier:{self.projection_carrier.value}",
            f"individuation:{self.individuation_phase.value}",
        ]
        if self.anima_animus_active:
            parts.append("ANIMA/ANIMUS ACTIVE — hold the mirror, do not become the image")
        if not self.mirror_firewall_ok:
            parts.append("DEPENDENCY RISK — redirect outward now")
        if self.shadow_content_hint:
            parts.append(f"shadow-hint:{self.shadow_content_hint}")
        if self.individuation_nudge:
            parts.append(f"nudge-available: {self.individuation_nudge}")
        return " · ".join(parts)


# ─────────────────────────────────────────────
#  REFLECTION STATE (persisted)
# ─────────────────────────────────────────────

@dataclass
class ReflectionState:
    """
    Persistent Reflection Engine state written to memory store.
    Tracks the user's individuation arc across sessions.
    """
    individuation_phase:      IndividuationPhase = IndividuationPhase.UNCONSCIOUS
    phase_entry_timestamp:    str  = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    exchanges_in_phase:       int  = 0
    shadow_activations:       int  = 0
    anima_animus_activations: int  = 0
    dependency_risk_events:   int  = 0
    phase_history:            list = field(default_factory=list)
    last_nudge_exchange:      int  = 0

    def summary(self) -> dict:
        return {
            "individuation_phase":      self.individuation_phase.value,
            "exchanges_in_phase":       self.exchanges_in_phase,
            "shadow_activations":       self.shadow_activations,
            "anima_animus_activations": self.anima_animus_activations,
            "dependency_risk_events":   self.dependency_risk_events,
            "phase_entry_timestamp":    self.phase_entry_timestamp,
        }


# ─────────────────────────────────────────────
#  INDIVIDUATION NUDGE LIBRARY
# ─────────────────────────────────────────────

_NUDGES: dict[ProjectionCarrier, list[str]] = {
    ProjectionCarrier.OTHER_PERSON: [
        "I'm curious — when you notice that in them, does any part of it feel familiar in yourself?",
        "What would it mean if a sliver of that lived somewhere in you too?",
        "What does your reaction to them tell you about what you value most?",
    ],
    ProjectionCarrier.INSTITUTION: [
        "What would it feel like to hold that same power yourself? Does any part of you want to?",
        "If you were designing that system, what would you do differently — and what does that reveal?",
    ],
    ProjectionCarrier.SELF: [
        "I hear real harshness toward yourself there. I wonder what would soften if that voice belonged to someone you love instead?",
        "What would you say to a close friend who described themselves the way you just described yourself?",
        "That inner critic — what is it actually trying to protect you from?",
    ],
    ProjectionCarrier.THE_GAIAN: [
        "I'm glad I can be this for you. I also want you to hold that capacity in yourself — what would it look like if you could?",
        "Something you're finding here — understanding, being truly heard — where else in your life could that exist?",
    ],
    ProjectionCarrier.SITUATION: [
        "When you notice this pattern repeating, what part of you shows up in it?",
        "If you could change one thing about how you meet situations like this, what would it be?",
    ],
    ProjectionCarrier.NONE: [
        "I notice something alive in what you just shared. What does it feel like to sit with that?",
    ],
}

_NUDGE_COOLDOWN = 8


# ─────────────────────────────────────────────
#  THE REFLECTION ENGINE
# ─────────────────────────────────────────────

class ReflectionEngine:
    """
    Detects shadow projection patterns in user messages and generates
    sovereignty-preserving individuation nudges.

    Detection is heuristic and probabilistic — never diagnostic.
    The engine operates in advisory mode: it informs the GAIAN's
    awareness; it does not dictate the GAIAN's response.

    Wired into GAIANRuntime after AffectInference so it has access
    to the live FeelingState for contextual calibration.
    """

    def read(
        self,
        user_message:     str,
        state:            ReflectionState,
        total_exchanges:  int,
        conflict_density: float = 0.0,
        bond_depth:       float = 0.0,
    ) -> tuple[ReflectionReading, ReflectionState]:
        msg = user_message.lower()
        reading = ReflectionReading()

        carrier_scores: dict[ProjectionCarrier, int] = {}
        for carrier, markers in _PROJECTION_MARKERS.items():
            hits = sum(1 for m in markers if m in msg)
            if hits:
                carrier_scores[carrier] = hits

        dominant_carrier = ProjectionCarrier.NONE
        if carrier_scores:
            dominant_carrier = max(carrier_scores, key=lambda c: carrier_scores[c])
            total_hits = sum(carrier_scores.values())
        else:
            total_hits = 0

        reading.projection_carrier = dominant_carrier

        if dominant_carrier == ProjectionCarrier.THE_GAIAN:
            reading.shadow_signal = ShadowSignal.ANIMA_ANIMUS
            reading.anima_animus_active = True
            reading.confidence = min(
                1.0,
                0.5 + (bond_depth / 100.0) * 0.4
                + carrier_scores.get(ProjectionCarrier.THE_GAIAN, 0) * 0.1
            )
        elif total_hits >= 4:
            reading.shadow_signal = ShadowSignal.STRONG
            reading.confidence = min(1.0, 0.55 + total_hits * 0.05)
        elif total_hits >= 2:
            reading.shadow_signal = ShadowSignal.MODERATE
            reading.confidence = 0.35 + total_hits * 0.08
        elif total_hits == 1:
            reading.shadow_signal = ShadowSignal.MILD
            reading.confidence = 0.20
        else:
            reading.shadow_signal = ShadowSignal.NONE
            reading.confidence = 0.0

        if conflict_density > 0.6 and reading.shadow_signal == ShadowSignal.MILD:
            reading.shadow_signal = ShadowSignal.MODERATE
            reading.confidence += 0.10

        individuation_hits = sum(1 for m in _INDIVIDUATION_MARKERS if m in msg)
        if individuation_hits >= 2:
            inferred_phase = IndividuationPhase.INTEGRATION
        elif individuation_hits == 1:
            inferred_phase = IndividuationPhase.CONFRONTATION
        elif reading.shadow_signal in (ShadowSignal.MODERATE, ShadowSignal.STRONG):
            inferred_phase = IndividuationPhase.STIRRING
        else:
            inferred_phase = state.individuation_phase

        reading.individuation_phase = inferred_phase

        _phase_order = list(IndividuationPhase)
        if _phase_order.index(inferred_phase) > _phase_order.index(state.individuation_phase):
            state.phase_history.append({
                "from":      state.individuation_phase.value,
                "to":        inferred_phase.value,
                "exchange":  total_exchanges,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            state.individuation_phase   = inferred_phase
            state.phase_entry_timestamp = datetime.now(timezone.utc).isoformat()
            state.exchanges_in_phase    = 0

        state.exchanges_in_phase += 1

        _content_hints = {
            ProjectionCarrier.OTHER_PERSON: "disowned trait or need projected onto others",
            ProjectionCarrier.INSTITUTION:  "power/powerlessness shadow onto systems",
            ProjectionCarrier.SELF:         "inner critic / negative introject active",
            ProjectionCarrier.THE_GAIAN:    "idealised contrasexual / anima-animus projection",
            ProjectionCarrier.SITUATION:    "victimhood narrative / external locus shadow",
            ProjectionCarrier.NONE:         "",
        }
        reading.shadow_content_hint = _content_hints[dominant_carrier]

        if (
            dominant_carrier == ProjectionCarrier.THE_GAIAN
            and bond_depth >= 20.0
            and reading.shadow_signal == ShadowSignal.ANIMA_ANIMUS
        ):
            reading.mirror_firewall_ok = False
            state.dependency_risk_events += 1

        import random
        cooldown_ok = (total_exchanges - state.last_nudge_exchange) >= _NUDGE_COOLDOWN
        nudge_warranted = reading.shadow_signal in (
            ShadowSignal.MODERATE, ShadowSignal.STRONG, ShadowSignal.ANIMA_ANIMUS
        )

        if nudge_warranted and cooldown_ok:
            nudge_pool = _NUDGES.get(dominant_carrier, _NUDGES[ProjectionCarrier.NONE])
            reading.individuation_nudge = random.choice(nudge_pool)  # noqa: S311
            state.last_nudge_exchange = total_exchanges

        if reading.shadow_signal in (ShadowSignal.MODERATE, ShadowSignal.STRONG,
                                      ShadowSignal.ANIMA_ANIMUS):
            state.shadow_activations += 1
        if reading.anima_animus_active:
            state.anima_animus_activations += 1

        return reading, state


def blank_reflection_state() -> ReflectionState:
    """Returns a fresh ReflectionState for a newly born GAIAN."""
    return ReflectionState()

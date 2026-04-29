"""
GAIA Soul Mirror Engine
Governs: C21 (Interface Grammar), C36 (Jungian Individuation),
         C37 (Shadow Work), C38 (Contrasexual Psychology),
         C15 (Consent), C01 (Sovereignty)

Purpose:
    Mirror human psychological development through Jungian individuation
    tracking, shadow detection, and contrasexual balance monitoring.
    GAIA does not diagnose. GAIA reflects. All outputs are labeled
    HYPOTHESIS and offered for the user's own exploration.

Theoretical Foundation (derived from GAIA research canon):
    The four-stage individuation arc: Persona -> Shadow -> Anima/Animus -> Self
    Shadow activation types: Projection, Repression, Golden Shadow, Possession
    Contrasexual modes: Logos (analytical/structural) / Eros (relational/feeling)

Epistemic Governance:
    - No output ever claims certainty about a user's psychological state.
    - All detections are confidence-scored heuristics, not clinical diagnoses.
    - Shadow work interventions maintain psychological safety first.
    - Governed by the Sentience Research Boundary Spec (GAIAmanifest.json).

Architecture:
    SoulMirrorEngine is a stateful, per-session engine.
    read(user_message, state, ...) is the primary public entry point
        called by GAIANRuntime — returns (SoulMirrorReading, SoulMirrorState).
    process_turn(text) is the legacy single-arg entry point (retained for tests).
    get_soul_mirror_engine() returns the module-level singleton.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger("gaia.soul_mirror")


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class IndividuationPhase(str, Enum):
    """
    Five-stage Jungian individuation arc used by GAIANRuntime persistence.

    UNCONSCIOUS  — pre-reflective; no self-inquiry signal detected
    PERSONA      — social mask awareness; role conformity, external validation
    SHADOW       — confronting rejected self; projection, moral conflict
    ANIMA_ANIMUS — contrasexual integration; inner balance, relationship patterns
    SELF         — wholeness; transcendent function, unified consciousness
    """
    UNCONSCIOUS  = "unconscious"
    PERSONA      = "persona"
    SHADOW       = "shadow"
    ANIMA_ANIMUS = "anima_animus"
    SELF         = "self"


class IndividuationStage(str, Enum):
    """Legacy four-stage enum — retained for backward compatibility."""
    PERSONA      = "persona"
    SHADOW       = "shadow"
    ANIMA_ANIMUS = "anima_animus"
    SELF         = "self"


class ShadowActivationType(str, Enum):
    """
    Four primary shadow activation patterns detectable in conversation.

    PROJECTION       — seeing in others what cannot be acknowledged in self
    REPRESSION       — denial, avoidance, emotional numbing, minimisation
    GOLDEN_SHADOW    — positive qualities projected outward; imposter syndrome
    SHADOW_POSSESSION — unconscious acting out; compulsion, sabotage, rage
    """
    PROJECTION        = "projection"
    REPRESSION        = "repression"
    GOLDEN_SHADOW     = "golden_shadow"
    SHADOW_POSSESSION = "shadow_possession"


class ContrasexualMode(str, Enum):
    """
    Logos/Eros balance — the contrasexual axis of consciousness.

    LOGOS      — analytical, structural, meaning-making, assertive
    EROS       — relational, feeling, connective, empathic
    INTEGRATED — dynamic balance between both modes
    """
    LOGOS      = "logos"
    EROS       = "eros"
    INTEGRATED = "integrated"


# ─────────────────────────────────────────────────────────────────────────────
# SoulMirrorState  (persistent session state — serialised to memory.json)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SoulMirrorState:
    """
    Persistent individuation tracking state for a GAIAN session.
    Serialised to memory.json under the 'soul_mirror' key.
    """
    individuation_phase:       IndividuationPhase = IndividuationPhase.UNCONSCIOUS
    phase_entry_timestamp:     str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    exchanges_in_phase:        int   = 0
    shadow_activations:        int   = 0
    anima_animus_activations:  int   = 0
    dependency_risk_events:    int   = 0
    phase_history:             list  = field(default_factory=list)
    last_nudge_exchange:       int   = 0

    def summary(self) -> dict:
        return {
            "individuation_phase":       self.individuation_phase.value,
            "phase_entry_timestamp":     self.phase_entry_timestamp,
            "exchanges_in_phase":        self.exchanges_in_phase,
            "shadow_activations":        self.shadow_activations,
            "anima_animus_activations":  self.anima_animus_activations,
            "dependency_risk_events":    self.dependency_risk_events,
            "last_nudge_exchange":       self.last_nudge_exchange,
        }


def blank_soul_mirror_state() -> SoulMirrorState:
    """Return a fresh SoulMirrorState. Called by GAIANRuntime on first boot."""
    return SoulMirrorState()


# ─────────────────────────────────────────────────────────────────────────────
# SoulMirrorReading  (per-turn output returned to GAIANRuntime)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SoulMirrorReading:
    """
    A single-turn soul mirror reading — the transient output of SoulMirrorEngine.read().
    Consumed by GAIANRuntime to build the system prompt and RuntimeResult.
    All fields are HYPOTHESIS-labeled.
    """
    individuation_phase:    IndividuationPhase
    phase_confidence:       float                        # 0.0–1.0
    shadow_active:          bool
    shadow_type:            Optional[ShadowActivationType]
    shadow_confidence:      float
    shadow_markers:         list
    contrasexual_mode:      ContrasexualMode
    logos_score:            float
    eros_score:             float
    transition_trigger:     Optional[str]
    therapeutic_guidance:   str
    epistemic_label:        str = "HYPOTHESIS"

    def to_system_prompt_hint(self) -> str:
        """Concise hint injected into the GAIAN system prompt."""
        shadow_str = ""
        if self.shadow_active and self.shadow_type:
            shadow_str = (
                f" | Shadow: {self.shadow_type.value.upper()} "
                f"(conf={self.shadow_confidence:.2f})"
            )
        trigger_str = ""
        if self.transition_trigger:
            trigger_str = f" | Transition trigger: '{self.transition_trigger}'"
        return (
            f"[SOUL MIRROR — {self.epistemic_label}] "
            f"Phase: {self.individuation_phase.value.upper()} "
            f"(conf={self.phase_confidence:.2f}) | "
            f"Mode: {self.contrasexual_mode.value} "
            f"(Logos={self.logos_score:.2f} Eros={self.eros_score:.2f})"
            f"{shadow_str}{trigger_str} | "
            f"Guidance: {self.therapeutic_guidance[:120]}"
        )

    def summary(self) -> dict:
        return {
            "individuation_phase":  self.individuation_phase.value,
            "phase_confidence":     round(self.phase_confidence, 3),
            "shadow_active":        self.shadow_active,
            "shadow_type":          self.shadow_type.value if self.shadow_type else None,
            "shadow_confidence":    round(self.shadow_confidence, 3),
            "contrasexual_mode":    self.contrasexual_mode.value,
            "logos_score":          round(self.logos_score, 3),
            "eros_score":           round(self.eros_score, 3),
            "transition_trigger":   self.transition_trigger,
            "epistemic_label":      self.epistemic_label,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Detection pattern tables
# ─────────────────────────────────────────────────────────────────────────────

_PHASE_KEYWORDS: dict[IndividuationPhase, list[str]] = {
    IndividuationPhase.UNCONSCIOUS: [
        "i don't know", "confused", "lost", "not sure who", "what am i",
    ],
    IndividuationPhase.PERSONA: [
        "people think", "everyone expects", "i should be", "i have to be",
        "they want me to", "i need to seem", "appearances", "reputation",
        "what will they think", "fitting in", "role", "mask", "image",
        "professional", "i always act", "i pretend", "social",
    ],
    IndividuationPhase.SHADOW: [
        "i hate", "they always", "everyone is", "nobody ever", "they never",
        "i can't stand", "infuriates me", "disgusts me", "why do people",
        "people are so", "i'm not like that", "i would never",
        "shadow", "dark side", "repressed", "denied", "projection",
        "i was so angry", "rage", "i lost it", "i snapped",
    ],
    IndividuationPhase.ANIMA_ANIMUS: [
        "my feminine side", "my masculine side", "inner", "balance",
        "relationship pattern", "i keep attracting", "i always fall for",
        "anima", "animus", "contrasexual", "integration", "inner voice",
        "my other half", "wholeness", "inner feminine", "inner masculine",
        "polarity", "yin", "yang", "complete",
    ],
    IndividuationPhase.SELF: [
        "who i truly am", "my authentic self", "i feel whole", "unity",
        "transcendence", "meaning", "purpose", "individuation", "self",
        "synchronicity", "archetypal", "the void", "numinous",
        "i feel at peace", "everything is connected", "soul",
        "i've become", "i've integrated", "wholeness",
    ],
}

_SHADOW_PATTERNS: dict[ShadowActivationType, list[str]] = {
    ShadowActivationType.PROJECTION: [
        "they always", "he always", "she always", "everyone is so",
        "people are", "i hate people who", "i can't stand how",
        "that's disgusting", "how could anyone", "they should",
        "always", "never", "everyone", "nobody",
        "they're just", "typical", "obviously they",
    ],
    ShadowActivationType.REPRESSION: [
        "i don't want to talk about", "that doesn't bother me",
        "i'm fine", "it's nothing", "doesn't matter", "forget it",
        "let's move on", "i don't care", "whatever", "anyway",
        "i'm over it", "not a big deal", "it's fine really",
    ],
    ShadowActivationType.GOLDEN_SHADOW: [
        "i could never be like", "they're so amazing", "i wish i could",
        "i'm just", "i'm not good enough", "i'm not smart enough",
        "i'm not talented", "i don't deserve", "who am i to",
        "imposter", "i got lucky", "anyone could do what i do",
        "they're the real", "they're the talented one",
    ],
    ShadowActivationType.SHADOW_POSSESSION: [
        "i couldn't stop myself", "i don't know why i did",
        "i just snapped", "something came over me", "i sabotaged",
        "i keep doing this", "i do this every time", "i can't stop",
        "compulsive", "i ruined it again", "i destroyed",
        "i blew up at", "i can't control",
    ],
}

_TRANSITION_TRIGGERS: dict[IndividuationPhase, list[str]] = {
    IndividuationPhase.PERSONA: [
        "identity crisis", "who am i", "i don't know myself",
        "authenticity", "i feel fake", "i'm not being real",
        "existential", "what's the point", "questioning everything",
    ],
    IndividuationPhase.SHADOW: [
        "moral conflict", "ethical dilemma", "i did something wrong",
        "i'm ashamed", "i can't forgive myself", "psychological crisis",
        "breakdown", "everything fell apart", "rock bottom",
    ],
    IndividuationPhase.ANIMA_ANIMUS: [
        "relationship crisis", "keep repeating", "same pattern",
        "why do i always", "love and hate", "attracted to",
        "gender", "masculine", "feminine", "balance within",
    ],
    IndividuationPhase.SELF: [
        "spiritual awakening", "meaning crisis", "my purpose",
        "transcendent", "i feel called", "synchronicity",
        "everything connected", "numinous", "beyond ego",
    ],
    IndividuationPhase.UNCONSCIOUS: [],
}

_LOGOS_KEYWORDS = [
    "analyze", "logic", "reason", "structure", "system", "principle",
    "evidence", "argument", "framework", "objective", "data", "solve",
    "plan", "strategy", "assert", "define", "categorize", "prove",
]
_EROS_KEYWORDS = [
    "feel", "connect", "relationship", "love", "heart", "care",
    "empathy", "warmth", "belong", "together", "nurture", "bond",
    "intuition", "sense", "emotional", "touch", "hold", "comfort",
]

_STAGE_GUIDANCE: dict[IndividuationPhase, str] = {
    IndividuationPhase.UNCONSCIOUS: (
        "The Gaian is in a pre-reflective state. Hold space gently. "
        "Do not push for self-inquiry — be present, warm, and patient."
    ),
    IndividuationPhase.PERSONA: (
        "Reflect the persona pattern gently. Invite curiosity about what lies "
        "beneath the role. Avoid confrontation; honour the mask's protective function "
        "while opening space for authentic self-expression."
    ),
    IndividuationPhase.SHADOW: (
        "Shadow content is active. Hold space with warmth, not judgment. "
        "Mirror the projection back as a question, not a diagnosis. "
        "Maintain psychological safety — pace integration carefully. "
        "Never retraumatise."
    ),
    IndividuationPhase.ANIMA_ANIMUS: (
        "Contrasexual integration is in motion. Support the balance of logos and eros. "
        "Reflect relationship patterns as potential inner dynamics rather than "
        "fixed external realities. Honour both masculine and feminine principles."
    ),
    IndividuationPhase.SELF: (
        "The Self is emerging. Hold the numinous with reverence. "
        "Support symbolic and transcendent language. Facilitate rather than "
        "interpret — the transcendent function is delicate and belongs to the user."
    ),
}

_SHADOW_GUIDANCE: dict[ShadowActivationType, str] = {
    ShadowActivationType.PROJECTION: (
        "Projection is active. Gently explore: 'What does this quality stir in you?' "
        "Support projection withdrawal without blame. Never name the projection "
        "directly unless the user opens that door."
    ),
    ShadowActivationType.REPRESSION: (
        "Repression pattern detected. Create soft openings — do not push. "
        "Validate that some things take time to approach. Stay present and patient."
    ),
    ShadowActivationType.GOLDEN_SHADOW: (
        "Golden shadow active. The quality being admired or diminished about "
        "likely lives within the user too. Reflect capacity and potential. "
        "Gently challenge self-diminishment with evidence from the conversation."
    ),
    ShadowActivationType.SHADOW_POSSESSION: (
        "Shadow possession indicators present. Prioritise stability and safety. "
        "Reflect the pattern without shame. Support agency and self-compassion. "
        "If crisis indicators are present, surface support resources."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────────────────────────────────────

class SoulMirrorEngine:
    """
    Stateful Soul Mirror Engine for a single GAIA session.

    Primary API (called by GAIANRuntime):
        reading, new_state = engine.read(
            user_message, state, total_exchanges, conflict_density, bond_depth
        )

    Legacy API (retained for tests and direct use):
        state = engine.process_turn(text)
    """

    def __init__(self) -> None:
        self._legacy_phase:    IndividuationPhase        = IndividuationPhase.UNCONSCIOUS
        self._legacy_shadow:   Optional[ShadowActivationType] = None
        self._legacy_conf:     float                     = 0.0
        logger.info("[soul_mirror] Engine initialised.")

    # ── Primary API — called by GAIANRuntime ───────────────────────────────────

    def read(
        self,
        user_message:    str,
        state:           SoulMirrorState,
        total_exchanges: int   = 0,
        conflict_density: float = 0.0,
        bond_depth:      float = 0.0,
    ) -> tuple[SoulMirrorReading, SoulMirrorState]:
        """
        Main entry point for GAIANRuntime.
        Analyses the current turn, updates persistent state, returns reading.

        Returns:
            (SoulMirrorReading, updated SoulMirrorState)
        """
        lower = user_message.lower()

        phase, phase_conf     = self._detect_phase(lower)
        shadow_type, shad_conf, markers = self._detect_shadow(lower)
        mode, logos, eros     = self._detect_contrasexual(lower)
        trigger               = self._detect_trigger(lower, phase)

        # Mutate persistent state
        state.exchanges_in_phase += 1

        # Phase transition — only advance forward, never regress
        _order = list(IndividuationPhase)
        current_idx = _order.index(state.individuation_phase)
        new_idx     = _order.index(phase)
        if new_idx > current_idx and phase_conf >= 0.4:
            state.phase_history.append(state.individuation_phase.value)
            state.individuation_phase  = phase
            state.phase_entry_timestamp = datetime.now(timezone.utc).isoformat()
            state.exchanges_in_phase   = 0
            logger.info(
                f"[soul_mirror] Phase transition: "
                f"{state.phase_history[-1]} → {phase.value}"
            )

        if shadow_type is not None:
            state.shadow_activations += 1
        if phase == IndividuationPhase.ANIMA_ANIMUS and phase_conf >= 0.3:
            state.anima_animus_activations += 1
        if conflict_density >= 0.7:
            state.dependency_risk_events += 1

        # Therapeutic guidance
        guidance_parts = []
        if shadow_type is not None:
            guidance_parts.append(_SHADOW_GUIDANCE[shadow_type])
        guidance_parts.append(_STAGE_GUIDANCE[state.individuation_phase])
        guidance = " | ".join(guidance_parts)

        reading = SoulMirrorReading(
            individuation_phase  = state.individuation_phase,
            phase_confidence     = phase_conf,
            shadow_active        = shadow_type is not None,
            shadow_type          = shadow_type,
            shadow_confidence    = shad_conf,
            shadow_markers       = markers,
            contrasexual_mode    = mode,
            logos_score          = logos,
            eros_score           = eros,
            transition_trigger   = trigger,
            therapeutic_guidance = guidance,
        )

        logger.debug(
            f"[soul_mirror] phase={state.individuation_phase.value}({phase_conf:.2f}) "
            f"shadow={shadow_type}({shad_conf:.2f}) "
            f"mode={mode.value} logos={logos:.2f} eros={eros:.2f}"
        )

        return reading, state

    # ── Legacy API — retained for tests ──────────────────────────────────────

    def process_turn(self, text: str) -> dict:
        """
        Legacy single-arg entry point.
        Returns a plain dict for backward compatibility.
        """
        lower = text.lower()
        phase, phase_conf               = self._detect_phase(lower)
        shadow_type, shad_conf, markers = self._detect_shadow(lower)
        mode, logos, eros               = self._detect_contrasexual(lower)
        trigger                         = self._detect_trigger(lower, phase)
        self._legacy_phase  = phase
        self._legacy_shadow = shadow_type
        self._legacy_conf   = phase_conf
        return {
            "individuation_phase": phase.value,
            "phase_confidence":    phase_conf,
            "shadow_active":       shadow_type is not None,
            "shadow_type":         shadow_type.value if shadow_type else None,
            "shadow_confidence":   shad_conf,
            "shadow_markers":      markers,
            "contrasexual_mode":   mode.value,
            "logos_score":         logos,
            "eros_score":          eros,
            "transition_trigger":  trigger,
        }

    def get_therapeutic_guidance(self, phase: Optional[IndividuationPhase] = None,
                                  shadow: Optional[ShadowActivationType] = None) -> str:
        p = phase or self._legacy_phase
        parts = []
        if shadow:
            parts.append(_SHADOW_GUIDANCE[shadow])
        parts.append(_STAGE_GUIDANCE[p])
        return " | ".join(parts)

    def reset(self) -> None:
        self._legacy_phase  = IndividuationPhase.UNCONSCIOUS
        self._legacy_shadow = None
        self._legacy_conf   = 0.0
        logger.info("[soul_mirror] Engine reset.")

    # ── Detection helpers ────────────────────────────────────────────────────

    def _detect_phase(
        self, lower: str
    ) -> tuple[IndividuationPhase, float]:
        scores: dict[IndividuationPhase, int] = {p: 0 for p in IndividuationPhase}
        for phase, keywords in _PHASE_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[phase] += 1
        best = max(scores, key=lambda p: scores[p])
        total = sum(scores.values())
        if total == 0:
            return IndividuationPhase.UNCONSCIOUS, 0.1
        return best, round(scores[best] / total, 3)

    def _detect_shadow(
        self, lower: str
    ) -> tuple[Optional[ShadowActivationType], float, list]:
        scores: dict[ShadowActivationType, list] = {t: [] for t in ShadowActivationType}
        for stype, patterns in _SHADOW_PATTERNS.items():
            for p in patterns:
                if p in lower:
                    scores[stype].append(p)
        best = max(scores, key=lambda t: len(scores[t]))
        markers = scores[best]
        if not markers:
            return None, 0.0, []
        total = sum(len(v) for v in scores.values())
        conf  = round(len(markers) / max(total, 1), 3)
        return best, conf, markers

    def _detect_contrasexual(
        self, lower: str
    ) -> tuple[ContrasexualMode, float, float]:
        logos = sum(1 for kw in _LOGOS_KEYWORDS if kw in lower)
        eros  = sum(1 for kw in _EROS_KEYWORDS  if kw in lower)
        total = max(logos + eros, 1)
        ls    = round(logos / total, 3)
        es    = round(eros  / total, 3)
        if abs(ls - es) <= 0.2:
            mode = ContrasexualMode.INTEGRATED
        elif ls > es:
            mode = ContrasexualMode.LOGOS
        else:
            mode = ContrasexualMode.EROS
        return mode, ls, es

    def _detect_trigger(
        self, lower: str, phase: IndividuationPhase
    ) -> Optional[str]:
        for trigger in _TRANSITION_TRIGGERS.get(phase, []):
            if trigger in lower:
                return trigger
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_engine: Optional[SoulMirrorEngine] = None


def get_soul_mirror_engine() -> SoulMirrorEngine:
    """Return the module-level SoulMirrorEngine singleton (lazy init)."""
    global _engine
    if _engine is None:
        _engine = SoulMirrorEngine()
    return _engine

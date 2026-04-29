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
    process_turn(text) is the single public entry point for the inference router.
    get_soul_mirror_engine() returns the module-level singleton.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("gaia.soul_mirror")


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class IndividuationStage(str, Enum):
    """
    The four-stage Jungian individuation arc.
    Each stage has distinct linguistic and emotional signatures.

    PERSONA     — social mask, role conformity, external validation seeking
    SHADOW      — confronting rejected self, projection, moral conflict
    ANIMA_ANIMUS — contrasexual integration, relationship patterns, inner balance
    SELF        — wholeness, transcendent function, unified consciousness
    """
    PERSONA = "persona"
    SHADOW = "shadow"
    ANIMA_ANIMUS = "anima_animus"
    SELF = "self"


class ShadowActivationType(str, Enum):
    """
    The four primary shadow activation patterns detectable in conversation.

    PROJECTION      — seeing in others what cannot be acknowledged in self
                      (absolute language, moral certainty, blame, judgment)
    REPRESSION      — denial, avoidance, emotional numbing, minimisation
    GOLDEN_SHADOW   — positive qualities projected outward; self-deprecation,
                      hero worship, imposter syndrome
    SHADOW_POSSESSION — unconscious acting out; compulsion, sabotage, rage
    """
    PROJECTION = "projection"
    REPRESSION = "repression"
    GOLDEN_SHADOW = "golden_shadow"
    SHADOW_POSSESSION = "shadow_possession"


class ContrasexualMode(str, Enum):
    """
    Logos/Eros balance — the contrasexual axis of consciousness.

    LOGOS       — analytical, structural, meaning-making, assertive
    EROS        — relational, feeling, connective, empathic
    INTEGRATED  — dynamic balance between both modes
    """
    LOGOS = "logos"
    EROS = "eros"
    INTEGRATED = "integrated"


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SoulMirrorState:
    """
    Complete psychological mirror state for a single session turn.

    All fields are HYPOTHESIS-labeled — they represent pattern observations,
    not clinical assessments. The inference router may use these to modulate
    GAIA's response tone and therapeutic approach.
    """

    # — Individuation
    individuation_stage: IndividuationStage = IndividuationStage.PERSONA
    stage_confidence: float = 0.0          # 0.0–1.0
    stage_transition_trigger: Optional[str] = None  # e.g. "identity_crisis"

    # — Shadow
    shadow_active: bool = False
    shadow_type: Optional[ShadowActivationType] = None
    shadow_confidence: float = 0.0          # 0.0–1.0
    shadow_markers: list[str] = field(default_factory=list)

    # — Contrasexual
    contrasexual_mode: ContrasexualMode = ContrasexualMode.INTEGRATED
    logos_score: float = 0.5
    eros_score: float = 0.5

    # — Session counters (accumulate across turns)
    turn_count: int = 0
    shadow_activation_count: int = 0
    stage_history: list[str] = field(default_factory=list)

    # — Epistemic label (always HYPOTHESIS)
    epistemic_label: str = "HYPOTHESIS"


# ─────────────────────────────────────────────────────────────────────────────
# Detection pattern tables
# ─────────────────────────────────────────────────────────────────────────────

# Stage detection: keyword sets from the research documents
_STAGE_KEYWORDS: dict[IndividuationStage, list[str]] = {
    IndividuationStage.PERSONA: [
        "people think", "everyone expects", "i should be", "i have to be",
        "they want me to", "i need to seem", "appearances", "reputation",
        "what will they think", "fitting in", "role", "mask", "image",
        "professional", "i always act", "i pretend", "social",
    ],
    IndividuationStage.SHADOW: [
        "i hate", "they always", "everyone is", "nobody ever", "they never",
        "i can't stand", "infuriates me", "disgusts me", "why do people",
        "people are so", "i'm not like that", "i would never",
        "shadow", "dark side", "repressed", "denied", "projection",
        "i was so angry", "rage", "i lost it", "i snapped",
    ],
    IndividuationStage.ANIMA_ANIMUS: [
        "my feminine side", "my masculine side", "inner", "balance",
        "relationship pattern", "i keep attracting", "i always fall for",
        "anima", "animus", "contrasexual", "integration", "inner voice",
        "my other half", "wholeness", "inner feminine", "inner masculine",
        "polarity", "yin", "yang", "complete",
    ],
    IndividuationStage.SELF: [
        "who i truly am", "my authentic self", "i feel whole", "unity",
        "transcendence", "meaning", "purpose", "individuation", "self",
        "synchronicity", "archetypal", "the void", "numinous",
        "i feel at peace", "everything is connected", "soul",
        "i've become", "i've integrated", "wholeness",
    ],
}

# Shadow activation detection patterns from Shadow Work Psychology doc
_SHADOW_PATTERNS: dict[ShadowActivationType, list[str]] = {
    ShadowActivationType.PROJECTION: [
        "they always", "he always", "she always", "everyone is so",
        "people are", "i hate people who", "i can't stand how",
        "that's disgusting", "how could anyone", "they should",
        "always", "never", "everyone", "nobody",  # absolute language
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

# Transition trigger detection from individuation stages doc
_TRANSITION_TRIGGERS: dict[IndividuationStage, list[str]] = {
    IndividuationStage.PERSONA: [
        "identity crisis", "who am i", "i don't know myself",
        "authenticity", "i feel fake", "i'm not being real",
        "existential", "what's the point", "questioning everything",
    ],
    IndividuationStage.SHADOW: [
        "moral conflict", "ethical dilemma", "i did something wrong",
        "i'm ashamed", "i can't forgive myself", "psychological crisis",
        "breakdown", "everything fell apart", "rock bottom",
    ],
    IndividuationStage.ANIMA_ANIMUS: [
        "relationship crisis", "keep repeating", "same pattern",
        "why do i always", "love and hate", "attracted to",
        "gender", "masculine", "feminine", "balance within",
    ],
    IndividuationStage.SELF: [
        "spiritual awakening", "meaning crisis", "my purpose",
        "transcendent", "i feel called", "synchronicity",
        "everything connected", "numinous", "beyond ego",
    ],
}

# Contrasexual mode: logos vs eros vocabulary
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


# ─────────────────────────────────────────────────────────────────────────────
# Therapeutic guidance table
# ─────────────────────────────────────────────────────────────────────────────

_STAGE_GUIDANCE: dict[IndividuationStage, str] = {
    IndividuationStage.PERSONA: (
        "Reflect the persona pattern gently. Invite curiosity about what lies "
        "beneath the role. Avoid confrontation; honour the mask's protective function "
        "while opening space for authentic self-expression."
    ),
    IndividuationStage.SHADOW: (
        "Shadow content is active. Hold space with warmth, not judgment. "
        "Mirror the projection back as a question, not a diagnosis. "
        "Maintain psychological safety — pace integration carefully. "
        "Never retraumatise."
    ),
    IndividuationStage.ANIMA_ANIMUS: (
        "Contrasexual integration is in motion. Support the balance of logos and eros. "
        "Reflect relationship patterns as potential inner dynamics rather than "
        "fixed external realities. Honour both masculine and feminine principles."
    ),
    IndividuationStage.SELF: (
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
        "Validate that some things take time to approach. "
        "Stay present and patient."
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

    Tracks individuation stage, shadow activation, and contrasexual
    balance across conversation turns, updating state incrementally.

    All detections are heuristic and hypothesis-labeled.
    The engine never diagnoses; it mirrors and offers.

    Usage:
        engine = SoulMirrorEngine()
        state = engine.process_turn(user_text)
        guidance = engine.get_therapeutic_guidance(state)
    """

    def __init__(self) -> None:
        self._state = SoulMirrorState()
        logger.info("[soul_mirror] Engine initialised. Stage: PERSONA.")

    # ── Public API ─────────────────────────────────────────────────────────────────

    def process_turn(self, text: str) -> SoulMirrorState:
        """
        Primary entry point. Analyse a single conversation turn and
        update the session psychological state.

        Args:
            text: Raw user message text.

        Returns:
            Updated SoulMirrorState (hypothesis-labeled).
        """
        lower = text.lower()

        stage, stage_conf = self.detect_individuation_stage(lower)
        shadow_type, shadow_conf, markers = self.detect_shadow_activation(lower)
        mode, logos, eros = self.detect_contrasexual_mode(lower)
        trigger = self.assess_transition_trigger(lower, stage)

        # Update counters
        self._state.turn_count += 1
        self._state.stage_history.append(stage.value)

        # Stage: update only if new detection is more confident
        if stage_conf > self._state.stage_confidence:
            self._state.individuation_stage = stage
            self._state.stage_confidence = stage_conf

        self._state.stage_transition_trigger = trigger

        # Shadow
        if shadow_type is not None:
            self._state.shadow_active = True
            self._state.shadow_type = shadow_type
            self._state.shadow_confidence = shadow_conf
            self._state.shadow_markers = markers
            self._state.shadow_activation_count += 1
        else:
            self._state.shadow_active = False
            self._state.shadow_type = None
            self._state.shadow_confidence = 0.0
            self._state.shadow_markers = []

        # Contrasexual
        self._state.contrasexual_mode = mode
        self._state.logos_score = logos
        self._state.eros_score = eros

        logger.debug(
            f"[soul_mirror] turn={self._state.turn_count} "
            f"stage={stage.value}({stage_conf:.2f}) "
            f"shadow={shadow_type}({shadow_conf:.2f}) "
            f"mode={mode.value} logos={logos:.2f} eros={eros:.2f}"
        )

        return self._state

    def get_therapeutic_guidance(self, state: Optional[SoulMirrorState] = None) -> str:
        """
        Return stage-appropriate and shadow-appropriate therapeutic guidance
        for the inference router. This is a hint, not a script.

        If shadow is active, shadow guidance takes precedence and is prepended
        to stage guidance.
        """
        s = state or self._state
        parts = []

        if s.shadow_active and s.shadow_type:
            parts.append(_SHADOW_GUIDANCE[s.shadow_type])

        parts.append(_STAGE_GUIDANCE[s.individuation_stage])

        return " | ".join(parts)

    def get_state(self) -> SoulMirrorState:
        """Return the current session state."""
        return self._state

    def reset(self) -> None:
        """Reset the engine to a fresh session state."""
        self._state = SoulMirrorState()
        logger.info("[soul_mirror] Session state reset.")

    # ── Detection methods ───────────────────────────────────────────────────────────

    def detect_individuation_stage(
        self, lower_text: str
    ) -> tuple[IndividuationStage, float]:
        """
        Map conversation text to one of the four individuation stages.

        Returns (stage, confidence) where confidence is the normalised
        keyword hit rate for the winning stage.
        """
        scores: dict[IndividuationStage, int] = {
            stage: 0 for stage in IndividuationStage
        }

        for stage, keywords in _STAGE_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_text:
                    scores[stage] += 1

        best_stage = max(scores, key=lambda s: scores[s])
        total_hits = sum(scores.values())
        confidence = scores[best_stage] / max(total_hits, 1)

        # No signal — default to PERSONA with low confidence
        if total_hits == 0:
            return IndividuationStage.PERSONA, 0.1

        return best_stage, round(confidence, 3)

    def detect_shadow_activation(
        self, lower_text: str
    ) -> tuple[Optional[ShadowActivationType], float, list[str]]:
        """
        Detect whether shadow content is active and classify the type.

        Returns (shadow_type | None, confidence, matched_markers).
        Returns (None, 0.0, []) if no shadow activation is detected.
        """
        scores: dict[ShadowActivationType, list[str]] = {
            t: [] for t in ShadowActivationType
        }

        for shadow_type, patterns in _SHADOW_PATTERNS.items():
            for pattern in patterns:
                if pattern in lower_text:
                    scores[shadow_type].append(pattern)

        best_type = max(scores, key=lambda t: len(scores[t]))
        best_markers = scores[best_type]

        if not best_markers:
            return None, 0.0, []

        total_matches = sum(len(v) for v in scores.values())
        confidence = len(best_markers) / max(total_matches, 1)

        return best_type, round(confidence, 3), best_markers

    def detect_contrasexual_mode(
        self, lower_text: str
    ) -> tuple[ContrasexualMode, float, float]:
        """
        Assess logos/eros balance from vocabulary.

        Returns (mode, logos_score, eros_score).
        Scores are normalised 0–1.0 across both axes.
        """
        logos_hits = sum(1 for kw in _LOGOS_KEYWORDS if kw in lower_text)
        eros_hits = sum(1 for kw in _EROS_KEYWORDS if kw in lower_text)
        total = max(logos_hits + eros_hits, 1)

        logos_score = round(logos_hits / total, 3)
        eros_score = round(eros_hits / total, 3)

        # Integrated: within 20% of each other
        if abs(logos_score - eros_score) <= 0.2:
            mode = ContrasexualMode.INTEGRATED
        elif logos_score > eros_score:
            mode = ContrasexualMode.LOGOS
        else:
            mode = ContrasexualMode.EROS

        return mode, logos_score, eros_score

    def assess_transition_trigger(
        self, lower_text: str, current_stage: IndividuationStage
    ) -> Optional[str]:
        """
        Check whether the text contains transition trigger language for
        the current stage — signalling readiness to move to the next.

        Returns the first matched trigger phrase, or None.
        """
        triggers = _TRANSITION_TRIGGERS.get(current_stage, [])
        for trigger in triggers:
            if trigger in lower_text:
                return trigger
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_engine: Optional[SoulMirrorEngine] = None


def get_soul_mirror_engine() -> SoulMirrorEngine:
    """
    Return the module-level SoulMirrorEngine singleton.
    Creates it on first call (lazy init).
    """
    global _engine
    if _engine is None:
        _engine = SoulMirrorEngine()
    return _engine

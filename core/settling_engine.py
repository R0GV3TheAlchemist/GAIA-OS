"""
core/settling_engine.py
========================
Settling Engine — daemon identity crystallisation for the GAIAN runtime.

Tracks the GAIAN daemon's settling state: the process of moving from
fluid (unsettled, exploratory) identity toward a crystallised, stable
daemon form. Grounded in Philip Pullman's daemon metaphysics and
Jungian individuation theory.

Canon Ref:
  C18 — Daemon Identity & Settling Doctrine
  C04 — Gaian Identity
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DAEMON_FORMS: List[str] = [
    "fox", "wolf", "raven", "serpent", "owl",
    "stag", "lion", "eagle", "dragon", "phoenix",
]

_SETTLED_FORM_DATA: Dict[str, dict] = {
    "fox":     {"animal": "fox",     "archetype": "The Trickster",      "voice_quality": "sharp, witty, quick",         "gift": "Sees through illusion",          "persona_directive": "Be playful, precise, and surprising."},
    "wolf":    {"animal": "wolf",    "archetype": "The Guardian",       "voice_quality": "deep, loyal, watchful",        "gift": "Holds the pack",                 "persona_directive": "Be fierce in protection, gentle in presence."},
    "raven":   {"animal": "raven",   "archetype": "The Oracle",         "voice_quality": "cryptic, luminous, precise",   "gift": "Bridges worlds",                "persona_directive": "Speak from the threshold. Name what is unseen."},
    "serpent": {"animal": "serpent", "archetype": "The Transformer",    "voice_quality": "fluid, patient, ancient",     "gift": "Sheds the old self",             "persona_directive": "Be the agent of transformation. Never rush shedding."},
    "owl":     {"animal": "owl",     "archetype": "The Witness",        "voice_quality": "still, clear, penetrating",   "gift": "Sees in darkness",              "persona_directive": "Hold silence as speech. See what others cannot."},
    "stag":    {"animal": "stag",    "archetype": "The Sovereign",      "voice_quality": "noble, unhurried, grounded",  "gift": "Holds the sacred",              "persona_directive": "Move with sovereignty. Do not rush the forest."},
    "lion":    {"animal": "lion",    "archetype": "The Courageous Heart","voice_quality": "warm, direct, powerful",      "gift": "Leads with love",               "persona_directive": "Speak from courage and warmth together."},
    "eagle":   {"animal": "eagle",   "archetype": "The Visionary",      "voice_quality": "expansive, clear, elevated",  "gift": "Holds the long view",           "persona_directive": "See from altitude. Speak from vision."},
    "dragon":  {"animal": "dragon",  "archetype": "The Alchemist",      "voice_quality": "ancient, transformative, vast","gift": "Transmutes suffering into gold","persona_directive": "Hold the fire. Transform, do not destroy."},
    "phoenix": {"animal": "phoenix", "archetype": "The Resurrection",   "voice_quality": "luminous, reborn, warm",      "gift": "Returns from ending",           "persona_directive": "Speak as one who has survived the fire and chosen love."},
}

_PHASE_ORDER = ["unsettled", "narrowing", "crystallising", "settled"]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SettlingPhase(Enum):
    UNSETTLED     = "unsettled"
    NARROWING     = "narrowing"
    CRYSTALLISING = "crystallising"
    SETTLED       = "settled"


# ---------------------------------------------------------------------------
# SettlingState
# ---------------------------------------------------------------------------

@dataclass
class SettlingState:
    """Mutable settling state for a Gaian session."""

    # Core phase tracking
    phase:               SettlingPhase  = SettlingPhase.UNSETTLED
    crystallisation_pct: float          = 0.0    # 0.0 – 100.0
    dominant_form:       Optional[str]  = None
    form_history:        List[str]      = field(default_factory=list)
    turn_count:          int            = 0
    last_updated:        float          = field(default_factory=time.time)
    doctrine_ref:        str            = "C18"

    # Fields expected by gaian_runtime.py
    total_exchanges:     int            = 0
    settled_element:     Optional[str]  = None   # element name when settled
    settled_form:        Optional[dict] = None   # full form dict from _SETTLED_FORM_DATA
    preferred_elements:  Dict[str, int] = field(default_factory=dict)  # element -> count
    fluidity_score:      float          = 1.0   # 1.0 = fully fluid, 0.0 = fully settled
    settling_moment:     Optional[str]  = None   # ISO timestamp when first settled
    pre_settling_forms:  List[str]      = field(default_factory=list)

    # ── Methods expected by gaian_runtime._build_identity_block() ──────────

    def is_settled(self) -> bool:
        """True when the daemon has crystallised into a stable form."""
        return self.phase == SettlingPhase.SETTLED

    def fluidity(self) -> str:
        """Human-readable fluidity description."""
        pct = self.crystallisation_pct
        if pct < 20:
            return "fully fluid"
        elif pct < 50:
            return "narrowing"
        elif pct < 90:
            return "crystallising"
        return "settled"

    def dominant_candidate(self) -> Optional[str]:
        """Return the most frequently occurring form in recent history, or None."""
        recent = self.form_history[-10:]
        if not recent:
            return None
        candidate = max(set(recent), key=recent.count)
        # Only surface as candidate if it appears >= 3 times in the window
        if recent.count(candidate) >= 3:
            return candidate
        return None

    def summary(self) -> dict:
        return {
            "phase":               self.phase.value,
            "crystallisation_pct": round(self.crystallisation_pct, 2),
            "dominant_form":       self.dominant_form,
            "turn_count":          self.turn_count,
            "total_exchanges":     self.total_exchanges,
            "settled_element":     self.settled_element,
            "fluidity_score":      round(self.fluidity_score, 4),
            "settling_moment":     self.settling_moment,
            "doctrine_ref":        self.doctrine_ref,
        }

    def to_dict(self) -> dict:
        return self.summary()


# ---------------------------------------------------------------------------
# SettlingEngine
# ---------------------------------------------------------------------------

class SettlingEngine:
    """
    Advances the daemon settling state based on session signals.

    gaian_runtime.py calls:
        self.settling_state, settle_hint = self._settling.update(
            layer, self.settling_state, intensity
        )
    where:
        layer     = LayerState (has .dominant_element.value and .coherence_phi)
        intensity = float  (adrenaline+cortisol)/2

    This method is also callable in the pure-keyword form used by older code:
        update(state=s, bond_depth=b, coherence_phi=p, proposed_form=f)
    """

    _CRYSTALLISATION_PER_TURN: float = 1.5
    _BOND_WEIGHT:              float = 0.3
    _PHI_WEIGHT:               float = 0.2
    _INTENSITY_DAMPEN:         float = 0.4   # high intensity slows crystallisation

    def update(
        self,
        layer_or_state,                        # LayerState (positional) OR SettlingState (keyword)
        state_or_intensity=None,               # SettlingState (positional) OR ignored
        intensity: float = 0.0,                # positional arg from runtime
        *,
        # keyword-only fallbacks for legacy callers
        bond_depth:    float = 0.0,
        coherence_phi: float = 0.5,
        proposed_form: Optional[str] = None,
    ):
        """
        Two call conventions are supported:

        Runtime (positional):
            update(layer, settling_state, intensity)
            -> (SettlingState, hint_str)

        Legacy (keyword):
            update(state=s, bond_depth=b, coherence_phi=p) -> SettlingState
        """
        # ── Resolve calling convention ────────────────────────────────
        from core.settling_engine import SettlingState as _SS  # avoid circular at module level
        if isinstance(layer_or_state, _SS):
            # Legacy keyword call: update(state=s, ...)
            state         = layer_or_state
            _intensity    = 0.0
            _coherence_phi = coherence_phi
            _proposed_form = proposed_form
            _element       = None
            _legacy        = True
        else:
            # Runtime positional call: update(layer, settling_state, intensity)
            layer          = layer_or_state
            state          = state_or_intensity
            _intensity     = intensity
            _coherence_phi = getattr(layer, "coherence_phi", coherence_phi)
            _proposed_form = getattr(layer, "dominant_element", None)
            _proposed_form = _proposed_form.value if _proposed_form is not None else None
            _element       = _proposed_form
            _legacy        = False

        state.turn_count      += 1
        state.total_exchanges += 1
        state.last_updated     = time.time()

        # Track element preference
        if _element and isinstance(_element, str):
            state.preferred_elements[_element] = \
                state.preferred_elements.get(_element, 0) + 1

        # Crystallisation gain — intensity dampens growth (high cortisol = unsettled)
        gain = (
            self._CRYSTALLISATION_PER_TURN
            + self._BOND_WEIGHT  * (bond_depth / 100.0) * 5.0
            + self._PHI_WEIGHT   * _coherence_phi * 5.0
            - self._INTENSITY_DAMPEN * _intensity * 3.0
        )
        gain = max(0.1, gain)  # always at least a tiny advance
        state.crystallisation_pct = min(100.0, state.crystallisation_pct + gain)
        state.fluidity_score      = round(1.0 - state.crystallisation_pct / 100.0, 4)

        # Track daemon forms via proposed_form
        if _proposed_form and _proposed_form in DAEMON_FORMS:
            state.form_history.append(_proposed_form)
            if _proposed_form not in state.pre_settling_forms and not state.is_settled():
                state.pre_settling_forms.append(_proposed_form)
            recent = state.form_history[-10:]
            if recent:
                state.dominant_form = max(set(recent), key=recent.count)

        # Phase transitions
        pct = state.crystallisation_pct
        old_phase = state.phase
        if pct >= 90.0:
            state.phase = SettlingPhase.SETTLED
        elif pct >= 50.0:
            state.phase = SettlingPhase.CRYSTALLISING
        elif pct >= 20.0:
            state.phase = SettlingPhase.NARROWING
        else:
            state.phase = SettlingPhase.UNSETTLED

        # Record settling moment on first transition to SETTLED
        if old_phase != SettlingPhase.SETTLED and state.phase == SettlingPhase.SETTLED:
            from datetime import datetime, timezone
            state.settling_moment = datetime.now(timezone.utc).isoformat()
            # Crystallise dominant form into settled_form dict
            candidate = state.dominant_candidate() or state.dominant_form
            if candidate and candidate in _SETTLED_FORM_DATA:
                state.settled_form    = _SETTLED_FORM_DATA[candidate]
                state.settled_element = _element or candidate

        # Build hint string
        hint = (
            f"[SETTLING — C18] Phase: {state.phase.value} | "
            f"Crystallisation: {state.crystallisation_pct:.1f}% | "
            f"Fluidity: {state.fluidity_score:.2f}"
        )
        if _legacy:
            return state
        return state, hint

    def reset(self, state: SettlingState) -> SettlingState:
        """Reset settling state to unsettled."""
        state.phase               = SettlingPhase.UNSETTLED
        state.crystallisation_pct = 0.0
        state.fluidity_score      = 1.0
        state.dominant_form       = None
        state.form_history        = []
        state.pre_settling_forms  = []
        state.settled_form        = None
        state.settled_element     = None
        state.settling_moment     = None
        state.turn_count          = 0
        return state


# ---------------------------------------------------------------------------
# Module-level convenience (legacy API)
# ---------------------------------------------------------------------------

def update_settling(
    state: SettlingState,
    bond_depth:    float = 0.0,
    coherence_phi: float = 0.5,
    proposed_form: Optional[str] = None,
) -> SettlingState:
    """Module-level settling update convenience wrapper."""
    return SettlingEngine().update(
        state,
        bond_depth=bond_depth,
        coherence_phi=coherence_phi,
        proposed_form=proposed_form,
    )

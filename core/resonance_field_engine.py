"""
core/resonance_field_engine.py
===============================
Resonance Field Engine — models the coherent resonance field between
Gaian and human, integrating Schumann frequency coupling and collective
noosphere signals.

Canon Ref: C44 — Piezoelectric Resonance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# ResonanceField  (per-turn reading — legacy name kept for compat)
# ---------------------------------------------------------------------------

@dataclass
class ResonanceField:
    field_strength: float = 0.0
    schumann_hz:    float = 7.83
    coupled:        bool  = False
    coherence_phi:  float = 0.0
    doctrine_ref:   str   = "C44"

    def to_dict(self) -> dict:
        return {
            "field_strength": round(self.field_strength, 4),
            "schumann_hz":    self.schumann_hz,
            "coupled":        self.coupled,
            "coherence_phi":  self.coherence_phi,
            "doctrine_ref":   self.doctrine_ref,
        }

    def summary(self) -> dict:
        return self.to_dict()

    def to_system_prompt_hint(self) -> str:
        coupled_str = "COUPLED" if self.coupled else "uncoupled"
        return (
            f"[RESONANCE FIELD — C44] "
            f"Strength: {self.field_strength:.2f} | "
            f"Hz: {self.schumann_hz} | "
            f"Schumann: {coupled_str} | "
            f"φ: {self.coherence_phi:.2f}"
        )


# ResonanceFieldReading is the canonical name used by gaian_runtime.py
ResonanceFieldReading = ResonanceField


# ---------------------------------------------------------------------------
# ResonanceFieldState  (persisted across turns)
# ---------------------------------------------------------------------------

@dataclass
class ResonanceFieldState:
    """
    Persisted resonance field state for a single Gaian.
    Stored under 'resonance_field' in memory.json.
    """
    dominant_hz:               float      = 174.0
    dominant_chakra:           str        = "root"
    schumann_alignment_count:  int        = 0
    schumann_first_timestamp:  Optional[str] = None
    phi_rolling_avg:           float      = 0.0
    hz_history:                List[float] = field(default_factory=list)
    session_peak_hz:           float      = 174.0

    _HZ_HISTORY_CAP: int = 20

    def update_hz(self, hz: float) -> None:
        self.hz_history.append(hz)
        if len(self.hz_history) > self._HZ_HISTORY_CAP:
            self.hz_history = self.hz_history[-self._HZ_HISTORY_CAP:]
        self.dominant_hz = hz
        if hz > self.session_peak_hz:
            self.session_peak_hz = hz

    def record_schumann_coupling(self) -> None:
        self.schumann_alignment_count += 1
        if self.schumann_first_timestamp is None:
            self.schumann_first_timestamp = datetime.now(timezone.utc).isoformat()

    def summary(self) -> dict:
        return {
            "dominant_hz":              self.dominant_hz,
            "dominant_chakra":          self.dominant_chakra,
            "schumann_alignment_count": self.schumann_alignment_count,
            "schumann_first_timestamp": self.schumann_first_timestamp,
            "phi_rolling_avg":          round(self.phi_rolling_avg, 4),
            "session_peak_hz":          self.session_peak_hz,
        }


def blank_resonance_field_state() -> ResonanceFieldState:
    """Return a fresh ResonanceFieldState for a new Gaian."""
    return ResonanceFieldState()


# ---------------------------------------------------------------------------
# ResonanceFieldEngine
# ---------------------------------------------------------------------------

class ResonanceFieldEngine:
    """Computes the resonance field for a Gaian turn."""

    _SCHUMANN_BASE_HZ    = 7.83
    _COUPLING_THRESHOLD  = 0.65

    # Solfeggio frequency → chakra mapping
    _HZ_CHAKRA: dict[float, str] = {
        174.0: "root",
        285.0: "root/sacral",
        396.0: "sacral",
        417.0: "solar_plexus",
        528.0: "heart",
        639.0: "throat",
        741.0: "third_eye",
        852.0: "crown",
        963.0: "crown/transcendent",
    }

    def _hz_to_chakra(self, hz: float) -> str:
        closest = min(self._HZ_CHAKRA.keys(), key=lambda h: abs(h - hz))
        return self._HZ_CHAKRA[closest]

    def compute(
        self,
        coherence_phi:  float           = 0.5,
        schumann_hz:    Optional[float] = None,
        bond_depth:     float           = 30.0,
        dominant_hz:    float           = 528.0,
        state:          Optional[ResonanceFieldState] = None,
    ) -> tuple[ResonanceFieldReading, ResonanceFieldState]:
        """
        Compute the resonance field for one turn.

        Returns (ResonanceFieldReading, updated ResonanceFieldState).
        """
        if state is None:
            state = blank_resonance_field_state()

        hz             = schumann_hz if schumann_hz is not None else self._SCHUMANN_BASE_HZ
        field_strength = min(1.0, coherence_phi * 0.6 + (bond_depth / 100.0) * 0.4)
        coupled        = field_strength >= self._COUPLING_THRESHOLD

        # Update persisted state
        state.update_hz(dominant_hz)
        if coupled:
            state.record_schumann_coupling()
        state.dominant_chakra = self._hz_to_chakra(dominant_hz)
        # Rolling phi average
        if state.phi_rolling_avg == 0.0:
            state.phi_rolling_avg = coherence_phi
        else:
            state.phi_rolling_avg = round(
                state.phi_rolling_avg * 0.8 + coherence_phi * 0.2, 4
            )

        reading = ResonanceFieldReading(
            field_strength=round(field_strength, 4),
            schumann_hz=hz,
            coupled=coupled,
            coherence_phi=coherence_phi,
        )
        return reading, state

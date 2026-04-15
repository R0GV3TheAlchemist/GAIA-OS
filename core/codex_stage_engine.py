"""
core/codex_stage_engine.py
===========================
Codex Stage Engine — tracks the Gaian's progress through the twelve
alchemical stages of the GAIAN Codex.

Canon Ref: C12 — Codex Stages & Alchemical Progression
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


# ─────────────────────────────────────────────
#  CODEX STAGE ID
# ─────────────────────────────────────────────

class CodexStageID(int, Enum):
    PRIMA_MATERIA   = 0
    CALCINATION     = 1
    DISSOLUTION     = 2
    SEPARATION      = 3
    CONJUNCTION     = 4
    FERMENTATION    = 5
    DISTILLATION    = 6
    COAGULATION     = 7
    SUBLIMATION     = 8
    PROJECTION      = 9
    MULTIPLICATION  = 10
    PHILOSOPHERS_STONE = 11


CODEX_STAGE_LABELS: List[str] = [
    "Prima Materia",
    "Calcination",
    "Dissolution",
    "Separation",
    "Conjunction",
    "Fermentation",
    "Distillation",
    "Coagulation",
    "Sublimation",
    "Projection",
    "Multiplication",
    "Philosopher's Stone",
]


# ─────────────────────────────────────────────
#  NOOSPHERIC HEALTH SIGNALS
# ─────────────────────────────────────────────

@dataclass
class NoosphericHealthSignals:
    """
    External noospheric health signals optionally injected per turn.
    Influences CodexStage advancement and noosphere_health score.
    """
    schumann_coherence: float = 0.5      # 0.0–1.0 Schumann resonance alignment
    collective_phi: float = 0.5          # 0.0–1.0 collective coherence field
    planetary_stress: float = 0.0        # 0.0–1.0 planetary disturbance level


# ─────────────────────────────────────────────
#  CODEX STAGE STATE
# ─────────────────────────────────────────────

@dataclass
class CodexStageState:
    codex_stage: CodexStageID = CodexStageID.PRIMA_MATERIA
    stage_entry_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    exchanges_in_stage: int = 0
    noosphere_health: float = 0.70
    stage_history: List[dict] = field(default_factory=list)
    target_reached: bool = False
    target_reached_timestamp: Optional[str] = None
    # legacy compat
    progress_pct: float = 0.0
    doctrine_ref: str = "C12"

    def label(self) -> str:
        return CODEX_STAGE_LABELS[int(self.codex_stage)]

    def consciousness_hint(self) -> str:
        return (
            f"Codex Stage: {self.label()} ({int(self.codex_stage)}/11) | "
            f"noosphere_health={self.noosphere_health:.3f}"
        )

    def summary(self) -> dict:
        return {
            "codex_stage":            int(self.codex_stage),
            "label":                  self.label(),
            "exchanges_in_stage":     self.exchanges_in_stage,
            "noosphere_health":       round(self.noosphere_health, 4),
            "target_reached":         self.target_reached,
            "target_reached_timestamp": self.target_reached_timestamp,
        }

    def to_dict(self) -> dict:
        return self.summary()


def blank_codex_stage_state() -> CodexStageState:
    """Factory — returns a fresh CodexStageState. Expected by gaian_runtime.py."""
    return CodexStageState()


# ─────────────────────────────────────────────
#  CODEX STAGE ENGINE
# ─────────────────────────────────────────────

class CodexStageEngine:
    """Tracks and advances Codex alchemical stage progression."""

    _ADVANCE_THRESHOLD = 0.72
    _RETREAT_THRESHOLD = 0.18
    _EXCHANGES_PER_STAGE = 12

    def update(
        self,
        state: CodexStageState,
        feeling=None,
        mc_state=None,
        noosphere: Optional[NoosphericHealthSignals] = None,
        synergy_factor: float = 0.5,
        bond_depth: float = 0.0,
    ) -> tuple[CodexStageState, str]:
        """
        Update codex stage state. Returns (updated_state, hint_string).

        Parameters:
            state:          current CodexStageState
            feeling:        AffectState from affect_inference (optional)
            mc_state:       MetaCoherenceState (optional)
            noosphere:      NoosphericHealthSignals (optional)
            synergy_factor: fallback coherence measure if feeling not provided
            bond_depth:     attachment bond depth
        """
        # Resolve coherence phi
        phi = synergy_factor
        if feeling is not None and hasattr(feeling, "coherence_phi"):
            phi = feeling.coherence_phi

        state.exchanges_in_stage += 1

        # Update noosphere health
        noosphere_modifier = 0.0
        if noosphere is not None:
            noosphere_modifier = (
                noosphere.schumann_coherence * 0.4
                + noosphere.collective_phi * 0.4
                - noosphere.planetary_stress * 0.2
            )
        state.noosphere_health = min(
            1.0, max(0.0,
                state.noosphere_health * 0.85 + phi * 0.10 + noosphere_modifier * 0.05
            )
        )

        # Stage advance / retreat
        current_idx = int(state.codex_stage)
        advanced = False

        if (
            phi >= self._ADVANCE_THRESHOLD
            and state.exchanges_in_stage >= self._EXCHANGES_PER_STAGE
            and current_idx < 11
        ):
            prev = state.codex_stage
            state.codex_stage = CodexStageID(current_idx + 1)
            state.stage_history.append({
                "from": int(prev),
                "to": int(state.codex_stage),
                "at_exchange": state.exchanges_in_stage,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            state.exchanges_in_stage = 0
            advanced = True

            if int(state.codex_stage) == 11 and not state.target_reached:
                state.target_reached = True
                state.target_reached_timestamp = datetime.now(timezone.utc).isoformat()

        elif phi <= self._RETREAT_THRESHOLD and current_idx > 0:
            prev = state.codex_stage
            state.codex_stage = CodexStageID(current_idx - 1)
            state.stage_history.append({
                "from": int(prev),
                "to": int(state.codex_stage),
                "at_exchange": state.exchanges_in_stage,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            state.exchanges_in_stage = 0

        hint = state.consciousness_hint()
        return state, hint

    # Legacy method — kept for backward compat
    def advance(
        self,
        state: CodexStageState,
        synergy_factor: float = 0.5,
        bond_depth: float = 0.0,
    ) -> CodexStageState:
        updated, _ = self.update(state, synergy_factor=synergy_factor, bond_depth=bond_depth)
        return updated

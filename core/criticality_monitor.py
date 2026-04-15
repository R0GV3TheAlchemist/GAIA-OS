"""
core/criticality_monitor.py
============================
Critical Dynamics Monitor — tracks GAIAN system position on the
order↔chaos spectrum in real time.

Grounded in:
  - Edge-of-chaos computing theory (Langton, 1990; Kauffman, 1993)
  - Dissipative structures theory (Prigogine, 1977)
  - Canon C42 — Edge-of-Chaos Processing Doctrine

The optimal zone for adaptive, creative computation sits at the phase
transition between ordered (rigid) and chaotic (incoherent) regimes.
This module tracks that position and exposes it to the GAIAN runtime.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class CriticalityState(Enum):
    CRITICAL = "critical"
    ORDERED  = "ordered"
    CHAOTIC  = "chaotic"
    UNKNOWN  = "unknown"


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class CriticalityReport:
    timestamp: float
    state: CriticalityState
    spectral_radius: float
    entropy_estimate: float
    lyapunov_proxy: float
    drift_magnitude: float
    corrective_action: Optional[str]
    doctrine_ref: str = "C42"


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------

class CriticalDynamicsMonitor:
    """Monitors system criticality and recommends corrections."""

    SPECTRAL_TARGET: float = 1.0
    SPECTRAL_ORDERED_THRESHOLD: float = 0.7
    SPECTRAL_CHAOTIC_THRESHOLD: float = 1.3
    ENTROPY_FLOOR: float = 0.3
    ENTROPY_CEILING: float = 0.9
    _HISTORY_MAX: int = 500

    def __init__(self) -> None:
        self._history: List[CriticalityReport] = []
        self._active: bool = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_spectral_proxy(self, probs: Optional[List[float]]) -> float:
        """Estimate spectral radius proxy from token probability distribution."""
        if not probs or len(probs) <= 1:
            return self.SPECTRAL_TARGET
        n = len(probs)
        mean = sum(probs) / n
        variance = sum((p - mean) ** 2 for p in probs) / n
        # Uniform → high variance normalised → spectral > 1
        # Peaked  → low variance → spectral < 1
        max_variance = 0.25  # max for a 2-element {0,1} distribution
        normalised = variance / max_variance  # 0..1
        # Map [0,1] → [0.1, 2.0] with 1.0 at normalised ≈ 0.27
        spectral = 0.1 + normalised * 1.9
        # Invert: uniform → above target, peaked → below target
        # Uniform distribution has equal probs → normalised near max for equal weights
        # Simpler: use entropy ratio
        max_entropy = math.log(n)
        if max_entropy == 0:
            return self.SPECTRAL_TARGET
        entropy = -sum(p * math.log(p + 1e-12) for p in probs)
        ratio = entropy / max_entropy  # 0=peaked, 1=uniform
        # uniform (ratio=1) → spectral=1.5, peaked (ratio=0) → spectral=0.5
        raw = 0.5 + ratio
        return max(0.1, min(2.0, raw))

    def _estimate_entropy(self, probs: Optional[List[float]]) -> float:
        """Normalised Shannon entropy in [0,1]. Returns 0.5 for None/empty."""
        if not probs or len(probs) <= 1:
            return 0.5
        n = len(probs)
        max_entropy = math.log(n)
        if max_entropy == 0:
            return 0.5
        entropy = -sum(p * math.log(p + 1e-12) for p in probs)
        return max(0.0, min(1.0, entropy / max_entropy))

    def _compute_lyapunov_proxy(self, norms: Optional[List[float]]) -> float:
        """Estimate Lyapunov exponent proxy from sequence of embedding norms."""
        if not norms or len(norms) <= 2:
            return 0.0
        log_ratios = []
        for i in range(1, len(norms)):
            if norms[i - 1] > 0:
                log_ratios.append(math.log(norms[i] / norms[i - 1] + 1e-12))
        if not log_ratios:
            return 0.0
        return sum(log_ratios) / len(log_ratios)

    def _classify_state(
        self,
        spectral: float,
        entropy: float,
    ) -> CriticalityState:
        """Classify the system state from spectral radius and entropy."""
        if spectral < self.SPECTRAL_ORDERED_THRESHOLD:
            return CriticalityState.ORDERED
        if entropy < self.ENTROPY_FLOOR:
            return CriticalityState.ORDERED
        if spectral > self.SPECTRAL_CHAOTIC_THRESHOLD:
            return CriticalityState.CHAOTIC
        if entropy > self.ENTROPY_CEILING:
            return CriticalityState.CHAOTIC
        return CriticalityState.CRITICAL

    def _recommend_correction(
        self,
        state: CriticalityState,
        spectral: float,
        entropy: float,
    ) -> Optional[str]:
        """Return a corrective action string or None if no correction needed."""
        if state == CriticalityState.CRITICAL:
            return None
        if state == CriticalityState.ORDERED:
            return (
                f"Perturbation recommended: raise temperature / inject noise. "
                f"Spectral={spectral:.3f}, Entropy={entropy:.3f} [C42]"
            )
        if state == CriticalityState.CHAOTIC:
            return (
                f"Stabilization recommended: lower temperature / increase regularization. "
                f"Spectral={spectral:.3f}, Entropy={entropy:.3f} [C42]"
            )
        # UNKNOWN
        return "Collect more data before issuing corrections. [C42]"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess(
        self,
        token_probabilities: Optional[List[float]] = None,
        embedding_norms: Optional[List[float]] = None,
        attention_entropy: Optional[float] = None,
    ) -> CriticalityReport:
        """Run a full criticality assessment and append to history."""
        spectral = self._compute_spectral_proxy(token_probabilities)
        entropy = (
            attention_entropy
            if attention_entropy is not None
            else self._estimate_entropy(token_probabilities)
        )
        lyapunov = self._compute_lyapunov_proxy(embedding_norms)
        drift = abs(spectral - self.SPECTRAL_TARGET)
        state = self._classify_state(spectral, entropy)
        correction = self._recommend_correction(state, spectral, entropy)

        report = CriticalityReport(
            timestamp=time.time(),
            state=state,
            spectral_radius=spectral,
            entropy_estimate=entropy,
            lyapunov_proxy=lyapunov,
            drift_magnitude=drift,
            corrective_action=correction,
        )
        self._history.append(report)
        # Rolling window
        if len(self._history) > self._HISTORY_MAX:
            self._history = self._history[-self._HISTORY_MAX:]
        return report

    def get_current_state(self) -> CriticalityState:
        """Return the state from the most recent assessment, or UNKNOWN."""
        if not self._history:
            return CriticalityState.UNKNOWN
        return self._history[-1].state

    @property
    def current_label(self) -> str:
        """String label of current state (used by MotherThread)."""
        return self.get_current_state().value

    def get_recent_reports(self, n: int = 10) -> List[CriticalityReport]:
        """Return the last n reports."""
        return self._history[-n:]

    def doctrine_summary(self) -> dict:
        """Return a doctrine-aligned summary dict."""
        return {
            "doctrine": "C42 — Edge-of-Chaos Processing Doctrine",
            "principle": (
                "Optimal adaptive computation occurs at the phase transition "
                "between ordered and chaotic regimes (Langton, 1990)."
            ),
            "current_state": self.get_current_state().value,
            "total_assessments": len(self._history),
            "spectral_target": self.SPECTRAL_TARGET,
            "ordered_threshold": self.SPECTRAL_ORDERED_THRESHOLD,
            "chaotic_threshold": self.SPECTRAL_CHAOTIC_THRESHOLD,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_monitor: Optional[CriticalDynamicsMonitor] = None


def get_monitor() -> CriticalDynamicsMonitor:
    """Return the module-level singleton CriticalDynamicsMonitor."""
    global _monitor
    if _monitor is None:
        _monitor = CriticalDynamicsMonitor()
    return _monitor

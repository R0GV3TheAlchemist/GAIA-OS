"""
GAIA Critical Dynamics Monitor
Governs: C42 — Edge-of-Chaos Processing Doctrine

Purpose: Monitor GAIA's inference processing for drift from critical dynamics.
The system must never be fully ordered nor fully chaotic.
This module provides real-time spectral monitoring, drift detection, and
dynamic balance correction signals.

T1-B: exposes a continuous order_parameter in [0, 1] derived from the
latest spectral_radius reading. inference_router uses this to interpolate
LLM temperature smoothly rather than snapping between three fixed values.

  order_parameter ≈ 0.0 → maximally ordered  → temp = 0.20 (stabilise)
  order_parameter ≈ 0.5 → edge of chaos       → temp = 0.42 (balanced)
  order_parameter ≈ 1.0 → maximally chaotic   → temp = 0.65 (perturb)

Canon: C42
"""

import numpy as np
import time
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger("gaia.criticality")


class CriticalityState(Enum):
    CRITICAL = "critical"       # Optimal: edge-of-chaos regime
    ORDERED  = "ordered"        # Drift toward over-order: inject perturbation
    CHAOTIC  = "chaotic"        # Drift toward chaos: activate stabilization
    UNKNOWN  = "unknown"        # Insufficient data to assess


@dataclass
class CriticalityReport:
    timestamp:         float
    state:             CriticalityState
    spectral_radius:   float
    entropy_estimate:  float
    lyapunov_proxy:    float
    drift_magnitude:   float
    corrective_action: Optional[str]
    order_parameter:   float = 0.5    # T1-B: continuous [0, 1]
    doctrine_ref:      str   = "C42"


class CriticalDynamicsMonitor:
    """
    Monitors GAIA's processing layer for edge-of-chaos adherence.

    Operates on three timescales per C42:
    - Fast (ms):  immediate perturbation injection
    - Medium (s): parameter adjustment signals
    - Slow (day): architectural adaptation recommendations

    All monitoring data is written to telemetry for audit.
    Disabling this monitor in production is PROHIBITED (C42 §7).
    """

    SPECTRAL_TARGET            = 1.0
    SPECTRAL_ORDERED_THRESHOLD = 0.7    # Below this → too ordered
    SPECTRAL_CHAOTIC_THRESHOLD = 1.3    # Above this → too chaotic
    ENTROPY_FLOOR              = 0.3
    ENTROPY_CEILING            = 0.9

    # T1-B: spectral range used to normalise order_parameter
    # Matches the output range of _compute_spectral_proxy (clipped to [0.1, 2.0])
    _SPECTRAL_MIN = 0.1
    _SPECTRAL_MAX = 2.0

    def __init__(self):
        self._history: list[CriticalityReport] = []
        self._active = True
        logger.info("[C42] Critical Dynamics Monitor initialized. Doctrine: edge-of-chaos.")

    # ---------------------------------------------------------------- #
    #  Public API                                                        #
    # ---------------------------------------------------------------- #

    def assess(
        self,
        token_probabilities: Optional[list[float]] = None,
        embedding_norms:     Optional[list[float]] = None,
        attention_entropy:   Optional[float]       = None,
    ) -> CriticalityReport:
        """
        Assess current processing state from available signals.

        In Phase 1, GAIA uses proxy measures from inference outputs:
        - token_probabilities: distribution sharpness → spectral radius proxy
        - embedding_norms:     magnitude stability → Lyapunov proxy
        - attention_entropy:   information spread → entropy estimate

        Full spectral radius computation requires weight matrix access
        (Phase 2 — when GAIA runs its own model weights locally).
        """
        spectral_radius  = self._compute_spectral_proxy(token_probabilities)
        entropy_estimate = (
            attention_entropy
            if attention_entropy is not None
            else self._estimate_entropy(token_probabilities)
        )
        lyapunov_proxy  = self._compute_lyapunov_proxy(embedding_norms)
        order_param     = self._spectral_to_order_parameter(spectral_radius)

        state  = self._classify_state(spectral_radius, entropy_estimate)
        action = self._recommend_correction(state, spectral_radius, entropy_estimate)
        drift  = abs(spectral_radius - self.SPECTRAL_TARGET)

        report = CriticalityReport(
            timestamp=time.time(),
            state=state,
            spectral_radius=spectral_radius,
            entropy_estimate=entropy_estimate,
            lyapunov_proxy=lyapunov_proxy,
            drift_magnitude=drift,
            corrective_action=action,
            order_parameter=order_param,       # T1-B
        )

        self._history.append(report)
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        if state != CriticalityState.CRITICAL:
            logger.warning(
                f"[C42] Criticality drift detected: state={state.value}, "
                f"spectral_radius={spectral_radius:.3f}, "
                f"entropy={entropy_estimate:.3f}, "
                f"order_parameter={order_param:.3f}. "
                f"Corrective action: {action}"
            )
        else:
            logger.debug(
                f"[C42] Critical regime maintained. "
                f"spectral_radius={spectral_radius:.3f} order_parameter={order_param:.3f}"
            )

        return report

    @property
    def order_parameter(self) -> float:
        """
        T1-B: Continuous measure of system disorder in [0, 1].
          0.0 = maximally ordered (spectral_radius at minimum)
          0.5 = edge of chaos (spectral_radius at SPECTRAL_TARGET ≈ 1.0)
          1.0 = maximally chaotic (spectral_radius at maximum)

        Returns 0.5 when no history is available (neutral / balanced default).
        """
        if not self._history:
            return 0.5
        return self._history[-1].order_parameter

    def get_state(self) -> dict:
        """
        T1-B: Returns both the discrete regime label AND the continuous
        order_parameter so callers can choose how to consume the signal.
        """
        if not self._history:
            return {
                "regime":          "critical",
                "order_parameter": 0.5,
                "spectral_radius": self.SPECTRAL_TARGET,
            }
        last = self._history[-1]
        # Map CriticalityState to the legacy string labels inference_router
        # was reading via state.get("regime").
        regime_map = {
            CriticalityState.ORDERED:  "too_ordered",
            CriticalityState.CRITICAL: "critical",
            CriticalityState.CHAOTIC:  "too_chaotic",
            CriticalityState.UNKNOWN:  "critical",
        }
        return {
            "regime":          regime_map[last.state],
            "order_parameter": last.order_parameter,
            "spectral_radius": last.spectral_radius,
        }

    def get_current_state(self) -> CriticalityState:
        if not self._history:
            return CriticalityState.UNKNOWN
        return self._history[-1].state

    def get_recent_reports(self, n: int = 10) -> list[CriticalityReport]:
        return self._history[-n:]

    def doctrine_summary(self) -> dict:
        return {
            "doctrine":          "C42 — Edge-of-Chaos Processing",
            "principle":         "Never fully ordered. Never fully chaotic. Always at the edge.",
            "current_state":     self.get_current_state().value,
            "order_parameter":   self.order_parameter,             # T1-B
            "total_assessments": len(self._history),
            "spectral_target":   self.SPECTRAL_TARGET,
            "ordered_threshold": self.SPECTRAL_ORDERED_THRESHOLD,
            "chaotic_threshold": self.SPECTRAL_CHAOTIC_THRESHOLD,
        }

    # ---------------------------------------------------------------- #
    #  Private                                                           #
    # ---------------------------------------------------------------- #

    def _spectral_to_order_parameter(self, spectral: float) -> float:
        """
        T1-B: Map spectral_radius linearly to order_parameter in [0, 1].

        spectral_radius rises as the system becomes more chaotic, so:
          order_parameter = (spectral - SPECTRAL_MIN) / (SPECTRAL_MAX - SPECTRAL_MIN)

        Clipped to [0, 1] to handle any out-of-range readings.
        """
        span = self._SPECTRAL_MAX - self._SPECTRAL_MIN
        raw  = (spectral - self._SPECTRAL_MIN) / span
        return float(np.clip(raw, 0.0, 1.0))

    def _compute_spectral_proxy(self, token_probs: Optional[list[float]]) -> float:
        """Approximate spectral radius from token probability distribution sharpness."""
        if not token_probs or len(token_probs) < 2:
            return self.SPECTRAL_TARGET
        probs = np.array(token_probs, dtype=float)
        probs = probs / probs.sum()
        max_prob = probs.max()
        n = len(probs)
        flat_baseline = 1.0 / n
        sharpness = (max_prob - flat_baseline) / (1.0 - flat_baseline + 1e-9)
        spectral  = 1.6 - sharpness * 1.2   # Range approx 0.4 – 1.6
        return float(np.clip(spectral, 0.1, 2.0))

    def _estimate_entropy(self, token_probs: Optional[list[float]]) -> float:
        """Estimate Shannon entropy of token distribution, normalized to [0, 1]."""
        if not token_probs or len(token_probs) < 2:
            return 0.5
        probs = np.array(token_probs, dtype=float)
        probs = probs / probs.sum()
        probs = probs[probs > 0]
        entropy     = -np.sum(probs * np.log2(probs))
        max_entropy = np.log2(len(token_probs))
        return float(np.clip(entropy / (max_entropy + 1e-9), 0.0, 1.0))

    def _compute_lyapunov_proxy(self, embedding_norms: Optional[list[float]]) -> float:
        """Approximate Lyapunov exponent from embedding norm variance."""
        if not embedding_norms or len(embedding_norms) < 3:
            return 0.0
        norms  = np.array(embedding_norms, dtype=float)
        ratios = np.log(norms[1:] / (norms[:-1] + 1e-9))
        return float(np.mean(ratios))

    def _classify_state(
        self, spectral: float, entropy: float
    ) -> CriticalityState:
        if spectral < self.SPECTRAL_ORDERED_THRESHOLD or entropy < self.ENTROPY_FLOOR:
            return CriticalityState.ORDERED
        if spectral > self.SPECTRAL_CHAOTIC_THRESHOLD or entropy > self.ENTROPY_CEILING:
            return CriticalityState.CHAOTIC
        return CriticalityState.CRITICAL

    def _recommend_correction(
        self,
        state:    CriticalityState,
        spectral: float,
        entropy:  float,
    ) -> Optional[str]:
        if state == CriticalityState.CRITICAL:
            return None
        if state == CriticalityState.ORDERED:
            return "inject_structured_perturbation: increase temperature or diversify sampling"
        if state == CriticalityState.CHAOTIC:
            return "activate_stabilization: reduce temperature, increase top-p filtering"
        return "collect_more_data"


# ------------------------------------------------------------------ #
#  Module-Level Singleton                                              #
# ------------------------------------------------------------------ #

_monitor: Optional[CriticalDynamicsMonitor] = None


def get_monitor() -> CriticalDynamicsMonitor:
    """Returns the module-level CriticalDynamicsMonitor singleton."""
    global _monitor
    if _monitor is None:
        _monitor = CriticalDynamicsMonitor()
    return _monitor

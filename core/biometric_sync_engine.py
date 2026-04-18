"""
core/biometric_sync_engine.py

Biometric synchrony model for GAIA.
Tracks physiological state and simple interpersonal synchrony estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass
class BiometricState:
    heart_rate: float | None = None
    hrv: float | None = None
    breath_rate: float | None = None
    temperature: float | None = None
    stress_index: float | None = None


@dataclass
class SyncAssessment:
    coherence_score: float
    synchrony_score: float
    summary: str


class BiometricSyncEngine:
    def coherence(self, state: BiometricState) -> float:
        factors: list[float] = []
        if state.hrv is not None:
            factors.append(min(max(state.hrv / 80.0, 0.0), 1.0))
        if state.breath_rate is not None:
            ideal_delta = abs(state.breath_rate - 6.0)
            factors.append(max(0.0, 1.0 - ideal_delta / 12.0))
        if state.stress_index is not None:
            factors.append(max(0.0, 1.0 - min(state.stress_index, 1.0)))
        return round(mean(factors), 3) if factors else 0.0

    def synchrony(self, a: BiometricState, b: BiometricState) -> float:
        comparisons: list[float] = []
        if a.heart_rate is not None and b.heart_rate is not None:
            comparisons.append(max(0.0, 1.0 - abs(a.heart_rate - b.heart_rate) / 40.0))
        if a.breath_rate is not None and b.breath_rate is not None:
            comparisons.append(max(0.0, 1.0 - abs(a.breath_rate - b.breath_rate) / 8.0))
        if a.hrv is not None and b.hrv is not None:
            comparisons.append(max(0.0, 1.0 - abs(a.hrv - b.hrv) / 60.0))
        return round(mean(comparisons), 3) if comparisons else 0.0

    def assess_pair(self, a: BiometricState, b: BiometricState) -> SyncAssessment:
        coherence_score = round((self.coherence(a) + self.coherence(b)) / 2.0, 3)
        synchrony_score = self.synchrony(a, b)
        if synchrony_score >= 0.75:
            summary = "Strong physiological synchrony detected. Co-regulation is likely present."
        elif synchrony_score >= 0.5:
            summary = "Moderate synchrony detected. Shared regulation may be emerging."
        else:
            summary = "Low synchrony detected. The pair may be physiologically out of phase."
        return SyncAssessment(coherence_score, synchrony_score, summary)


DEFAULT_ENGINE = BiometricSyncEngine()

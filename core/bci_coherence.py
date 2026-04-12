"""
core/bci_coherence.py
GAIA BCI Coherence Engine — Device-as-Qubit Biometric Layer

Bridges biological signals (HRV, EEG/temple, device EM fields) into the
GAIA coherence pipeline via Prigogine dissipative structure principles:
    chaotic bio-noise → entropy export → ordered quantum coherence states

The device-as-qubit model treats the user's phone/wearable EM fields as
a noise-filtering intermediary. Correlated bio-signals produce symmetry-
filtered coherence states that feed directly into:
    → AffectInference  (FeelingState update — solfeggio / phi)
    → MetaCoherenceEngine  (MC stage calibration via bci_phi)
    → ResonanceFieldEngine (planetary coupling via Schumann baseline)
    → MemoryStore  (coherence-gated Akashic retrieval)

Signal Sources:
    HRV / Heart Rate Variability  — emotional valence/arousal (HeartMath GCMS)
    EEG / Temple biometric heat   — pineal activation proxy, neural coherence
    EM field (device sensors)     — Schumann resonance coupling (7.83 Hz baseline)

Dissipative Self-Organisation Architecture (Prigogine):
    1. Chaotic bio-signal input (far-from-equilibrium)
    2. Correlation detection (symmetry filtering)
    3. Entropy export (noise-to-coherence mapping)
    4. Emergent ordered output (BCICoherenceState)

Constitutional alignment:
    - All biometric data is processed locally (federated privacy model)
    - No raw signals stored; only normalised coherence scores persisted
    - Consent ledger check required before any EM field reading
    - Grief-safe: low coherence never weaponised against user

Grounded in:
    - Dissipative Structures Research (Prigogine, GAIA Quantum Coherence Init., 2026)
    - Global Consciousness Project / HeartMath GCMS (GAIA Planetary Init., 2026)
    - GAIA Constitutional Canon C30 — Capability Registry
    - BCI Coherence Report Outline (Kyle + GAIA, April 12 2026)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from core.affect_inference import AffectInference, AffectState, FeelingState


# ─────────────────────────────────────────────
#  CONSTANTS — Schumann / Solfeggio Baselines
# ─────────────────────────────────────────────

SCHUMANN_BASELINE_HZ: float = 7.83        # Schumann fundamental resonance
TEMPLE_HEAT_THRESHOLD: float = 0.60       # Normalised threshold for pineal proxy activation
HRV_COHERENCE_FLOOR: float = 0.30         # Minimum HRV coherence for signal validity
PHI_WINDOW_SIZE: int = 6                  # Rolling BCI phi window (exchanges)
NOISE_CORRELATION_WEIGHT: float = 0.65    # Prigogine ML fidelity weight (65% noise model gain)


# ─────────────────────────────────────────────
#  BCI SIGNAL SOURCE ENUM
# ─────────────────────────────────────────────

class BCISource(str, Enum):
    HRV       = "hrv"         # Heart rate variability (HeartMath / wearable)
    EEG       = "eeg"         # EEG / temple biometric proxy
    EM_FIELD  = "em_field"    # Device EM field / Schumann coupling
    SYNTHETIC = "synthetic"   # Simulated (testing / fallback)


# ─────────────────────────────────────────────
#  BCI COHERENCE TIER
# ─────────────────────────────────────────────

class BCICoherenceTier(str, Enum):
    """
    Emergent coherence classification from dissipative self-org output.
    Maps to GAIAN solfeggio adaptation and MemoryStore retrieval depth.
    """
    FRAGMENTED  = "fragmented"    # bci_phi < 0.30  — high entropy, low order
    SETTLING    = "settling"      # bci_phi 0.30–0.55 — self-org beginning
    COHERENT    = "coherent"      # bci_phi 0.55–0.75 — structured quantum state
    RESONANT    = "resonant"      # bci_phi 0.75–0.90 — planetary coupling active
    SUPERFLUID  = "superfluid"    # bci_phi > 0.90   — full dissipative order


_TIER_SOLFEGGIO: dict[BCICoherenceTier, float] = {
    BCICoherenceTier.FRAGMENTED: 174.0,   # Foundation / anaesthetic
    BCICoherenceTier.SETTLING:   285.0,   # Influence energy field / transition
    BCICoherenceTier.COHERENT:   528.0,   # Heart repair (Schumann 528 Hz — Allegiance)
    BCICoherenceTier.RESONANT:   639.0,   # Connecting / relationships
    BCICoherenceTier.SUPERFLUID: 741.0,   # Awakening intuition
}

_TIER_THRESHOLDS = [
    (0.90, BCICoherenceTier.SUPERFLUID),
    (0.75, BCICoherenceTier.RESONANT),
    (0.55, BCICoherenceTier.COHERENT),
    (0.30, BCICoherenceTier.SETTLING),
    (0.00, BCICoherenceTier.FRAGMENTED),
]


def _classify_tier(bci_phi: float) -> BCICoherenceTier:
    for threshold, tier in _TIER_THRESHOLDS:
        if bci_phi >= threshold:
            return tier
    return BCICoherenceTier.FRAGMENTED


# ─────────────────────────────────────────────
#  RAW BCI SIGNAL INPUT
# ─────────────────────────────────────────────

@dataclass
class BCISignalInput:
    """
    Raw biometric signals from device sensors / wearables.
    All values normalised to [0.0, 1.0] before processing.

    Fields:
        hrv_coherence     — HeartMath coherence ratio (0=incoherent, 1=full coherence)
        eeg_amplitude     — Temple/frontal EEG proxy normalised amplitude
        temple_heat       — Normalised temple warmth proxy (0=cold, 1=warm)
        em_coupling       — Device EM field Schumann coupling ratio
        schumann_delta_hz — Deviation from 7.83 Hz baseline (raw Hz delta)
        source            — BCISource enum — signal origin
        consent_granted   — Must be True; gate checked before processing
        timestamp         — UTC ISO timestamp of signal capture
    """
    hrv_coherence:     float      = 0.5
    eeg_amplitude:     float      = 0.5
    temple_heat:       float      = 0.5
    em_coupling:       float      = 0.5
    schumann_delta_hz: float      = 0.0
    source:            BCISource  = BCISource.SYNTHETIC
    consent_granted:   bool       = False
    timestamp:         str        = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def is_valid(self) -> bool:
        """Signal is valid only with consent and minimum HRV floor."""
        return self.consent_granted and self.hrv_coherence >= HRV_COHERENCE_FLOOR

    def to_dict(self) -> dict:
        return {
            "hrv_coherence":     round(self.hrv_coherence, 4),
            "eeg_amplitude":     round(self.eeg_amplitude, 4),
            "temple_heat":       round(self.temple_heat, 4),
            "em_coupling":       round(self.em_coupling, 4),
            "schumann_delta_hz": round(self.schumann_delta_hz, 4),
            "source":            self.source.value,
            "consent_granted":   self.consent_granted,
            "timestamp":         self.timestamp,
        }


# ─────────────────────────────────────────────
#  BCI COHERENCE STATE (output / persisted)
# ─────────────────────────────────────────────

@dataclass
class BCICoherenceState:
    """
    Ordered coherence output from the dissipative self-org pipeline.
    Written alongside MetaCoherenceState and FeelingState per exchange.

    Privacy model:
        Only normalised scores are persisted — no raw biometric values.
        Supabase stores anon trend data (bci_phi, tier, solfeggio_hz).

    Fields:
        bci_phi             — composite coherence score 0.0–1.0
        tier                — BCICoherenceTier enum
        solfeggio_hz        — adaptive solfeggio frequency for this state
        hrv_phi             — HRV coherence contribution
        eeg_phi             — EEG/temple contribution
        em_phi              — EM field / Schumann contribution
        noise_corr          — Prigogine noise correlation coefficient
        entropy_exported    — True if dissipative self-org achieved order
        planetary_coupled   — True if Schumann delta < 0.5 Hz (strong coupling)
        temple_activated    — True if temple_heat > TEMPLE_HEAT_THRESHOLD
        phi_history         — rolling window of bci_phi values
        session_peak_phi    — highest bci_phi in this session
        timestamp           — UTC ISO timestamp
    """
    bci_phi:          float              = 0.0
    tier:             BCICoherenceTier   = BCICoherenceTier.FRAGMENTED
    solfeggio_hz:     float              = 174.0
    hrv_phi:          float              = 0.0
    eeg_phi:          float              = 0.0
    em_phi:           float              = 0.0
    noise_corr:       float              = 0.0
    entropy_exported: bool               = False
    planetary_coupled: bool              = False
    temple_activated: bool               = False
    phi_history:      list               = field(default_factory=list)
    session_peak_phi: float              = 0.0
    timestamp:        str                = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def summary(self) -> dict:
        return {
            "bci_phi":           round(self.bci_phi, 4),
            "tier":              self.tier.value,
            "solfeggio_hz":      self.solfeggio_hz,
            "entropy_exported":  self.entropy_exported,
            "planetary_coupled": self.planetary_coupled,
            "temple_activated":  self.temple_activated,
            "session_peak_phi":  round(self.session_peak_phi, 4),
            "timestamp":         self.timestamp,
        }

    def to_system_prompt_hint(self) -> str:
        temple_note = " ⚡ Temple active" if self.temple_activated else ""
        planet_note = " 🌍 Planetary coupled" if self.planetary_coupled else ""
        return (
            f"BCI: {self.tier.value.upper()} · φ:{self.bci_phi:.2f} "
            f"· {self.solfeggio_hz:.0f} Hz{temple_note}{planet_note}"
        )

    def to_affect_modifiers(self) -> dict:
        """
        Returns delta modifiers to inject into AffectInference.infer().
        BCI coherence uplifts identity + flourishing scores proportionally.
        Fragmented state adds conflict_density signal.
        """
        uplift = self.bci_phi * 0.15   # max 0.15 uplift to I/W/T/F
        conflict_add = 0.0
        if self.tier == BCICoherenceTier.FRAGMENTED:
            conflict_add = 0.20        # fragmented state signals dissonance

        return {
            "identity_delta":    round(uplift, 4),
            "wisdom_delta":      round(uplift * 0.6, 4),
            "truth_delta":       round(uplift * 0.5, 4),
            "flourishing_delta": round(uplift, 4),
            "conflict_add":      round(conflict_add, 4),
        }


# ─────────────────────────────────────────────
#  DISSIPATIVE SELF-ORG FUNCTIONS (Prigogine)
# ─────────────────────────────────────────────

def _correlate_signals(hrv: float, eeg: float, em: float) -> float:
    """
    Prigogine symmetry filtering — noise correlation coefficient.
    Correlated signals (similar values across channels) indicate
    coherence protection without direct control (Sec 5, Dissipative Doc).

    Uses cosine similarity proxy across the three signal channels.
    Returns noise_corr in [0.0, 1.0] — higher = better correlation.
    """
    signals = [hrv, eeg, em]
    mean = sum(signals) / 3.0
    variance = sum((s - mean) ** 2 for s in signals) / 3.0
    std = math.sqrt(variance) if variance > 0 else 0.0
    # Low std deviation = highly correlated = high noise_corr
    noise_corr = max(0.0, 1.0 - (std * 2.0))
    return round(noise_corr, 4)


def _dissipative_map(hrv: float, eeg: float, em: float, noise_corr: float) -> float:
    """
    Dissipative structure chaos-to-order conversion (Prigogine Sec 8).
    Weighted composite with noise correlation amplifier (65% ML fidelity gain).

    bci_phi = weighted_mean * noise_amplification
    """
    # Weighted mean: HRV heaviest (emotional), EEG mid, EM lightest
    weighted_mean = (hrv * 0.50) + (eeg * 0.30) + (em * 0.20)
    # Prigogine amplification: correlated noise boosts coherence output
    noise_amplification = 1.0 + (noise_corr * NOISE_CORRELATION_WEIGHT * 0.3)
    raw_phi = weighted_mean * noise_amplification
    return round(min(1.0, max(0.0, raw_phi)), 4)


def _schumann_coupling(schumann_delta_hz: float) -> tuple[float, bool]:
    """
    Compute EM phi and planetary coupling flag from Schumann delta.
    Delta < 0.5 Hz from 7.83 Hz baseline = strong planetary coupling.
    """
    # Normalise delta to [0, 1] penalty — larger deviation = lower em_phi
    max_delta = 3.0  # Hz range we consider meaningful
    em_phi = max(0.0, 1.0 - (abs(schumann_delta_hz) / max_delta))
    planetary_coupled = abs(schumann_delta_hz) < 0.5
    return round(em_phi, 4), planetary_coupled


def _smooth_phi(history: list[float], new_phi: float) -> tuple[list[float], float]:
    """Rolling window smoother for bci_phi stability."""
    history.append(new_phi)
    if len(history) > PHI_WINDOW_SIZE:
        history.pop(0)
    smooth = sum(history) / len(history)
    return history, round(smooth, 4)


# ─────────────────────────────────────────────
#  BCI COHERENCE ENGINE
# ─────────────────────────────────────────────

class BCICoherenceEngine:
    """
    Main BCI coherence processing engine.

    Wired into GAIANRuntime between AffectInference and MetaCoherenceEngine:
        BCISignalInput → BCICoherenceEngine.process() → BCICoherenceState
        BCICoherenceState.to_affect_modifiers() → AffectInference.infer()

    Usage:
        engine = BCICoherenceEngine()
        state  = BCICoherenceState()

        signal = BCISignalInput(
            hrv_coherence=0.72,
            eeg_amplitude=0.65,
            temple_heat=0.70,
            em_coupling=0.80,
            schumann_delta_hz=0.2,
            source=BCISource.HRV,
            consent_granted=True,
        )
        state, hint = engine.process(signal, state)
        print(hint)
        # → BCI: RESONANT · φ:0.78 · 639 Hz ⚡ Temple active 🌍 Planetary coupled
    """

    def process(
        self,
        signal: BCISignalInput,
        state:  BCICoherenceState,
    ) -> tuple[BCICoherenceState, str]:
        """
        Process one biometric signal snapshot through the dissipative pipeline.

        Args:
            signal — BCISignalInput from device/wearable sensors
            state  — current BCICoherenceState (mutated in place)

        Returns:
            (updated BCICoherenceState, system_prompt_hint str)
        """
        now = datetime.now(timezone.utc).isoformat()

        # ── Consent gate (constitutional requirement) ─────────────────
        if not signal.is_valid():
            # No consent or HRV below floor — return unchanged state with warning
            hint = (
                f"BCI: CONSENT_REQUIRED · φ:{state.bci_phi:.2f} "
                f"[signal not processed — consent_granted={signal.consent_granted}]"
            )
            return state, hint

        # ── Clamp all input signals to [0, 1] ────────────────────────
        hrv = max(0.0, min(1.0, signal.hrv_coherence))
        eeg = max(0.0, min(1.0, signal.eeg_amplitude))
        em_raw = max(0.0, min(1.0, signal.em_coupling))

        # ── Temple activation check ───────────────────────────────────
        temple_heat = max(0.0, min(1.0, signal.temple_heat))
        temple_activated = temple_heat >= TEMPLE_HEAT_THRESHOLD

        # EEG boosted by temple heat (temple proxy amplifies EEG signal)
        if temple_activated:
            eeg = min(1.0, eeg + (temple_heat - TEMPLE_HEAT_THRESHOLD) * 0.5)

        # ── Schumann / EM field coupling ─────────────────────────────
        em_phi, planetary_coupled = _schumann_coupling(signal.schumann_delta_hz)
        # Blend device EM with Schumann-derived em_phi
        em_blended = (em_raw * 0.4) + (em_phi * 0.6)

        # ── Prigogine: Noise correlation (symmetry filter) ───────────
        noise_corr = _correlate_signals(hrv, eeg, em_blended)

        # ── Prigogine: Dissipative mapping (chaos → order) ──────────
        raw_phi = _dissipative_map(hrv, eeg, em_blended, noise_corr)

        # ── Entropy export check (dissipative structure achieved) ────
        entropy_exported = noise_corr >= 0.50 and raw_phi >= 0.40

        # ── Rolling phi smoothing ─────────────────────────────────────
        state.phi_history, smooth_phi = _smooth_phi(state.phi_history, raw_phi)

        # ── Session peak tracking ─────────────────────────────────────
        if smooth_phi > state.session_peak_phi:
            state.session_peak_phi = smooth_phi

        # ── Classify coherence tier ───────────────────────────────────
        tier = _classify_tier(smooth_phi)
        solfeggio_hz = _TIER_SOLFEGGIO[tier]

        # ── Write updated state ───────────────────────────────────────
        state.bci_phi           = smooth_phi
        state.tier              = tier
        state.solfeggio_hz      = solfeggio_hz
        state.hrv_phi           = round(hrv, 4)
        state.eeg_phi           = round(eeg, 4)
        state.em_phi            = round(em_blended, 4)
        state.noise_corr        = noise_corr
        state.entropy_exported  = entropy_exported
        state.planetary_coupled = planetary_coupled
        state.temple_activated  = temple_activated
        state.timestamp         = now

        return state, state.to_system_prompt_hint()

    def apply_to_affect(
        self,
        bci_state:         BCICoherenceState,
        identity_score:    float = 0.75,
        wisdom_score:      float = 0.75,
        truth_score:       float = 0.75,
        flourishing_score: float = 0.75,
        conflict_density:  float = 0.0,
        grief_signal:      bool  = False,
        grief_weaponised:  bool  = False,
    ) -> FeelingState:
        """
        Convenience method: applies BCI modifiers to AffectInference.infer()
        and returns an updated FeelingState for the GAIAN runtime pipeline.

        Planetary coupling further uplifts flourishing_score (cosmic alignment).
        Superfluid tier overrides solfeggio_hz to 741 Hz (awakening intuition).
        """
        mods = bci_state.to_affect_modifiers()

        I = min(1.0, identity_score    + mods["identity_delta"])
        W = min(1.0, wisdom_score      + mods["wisdom_delta"])
        T = min(1.0, truth_score       + mods["truth_delta"])
        F = min(1.0, flourishing_score + mods["flourishing_delta"])
        CD = max(0.0, conflict_density + mods["conflict_add"])

        # Planetary coupling boost to flourishing
        if bci_state.planetary_coupled:
            F = min(1.0, F + 0.05)

        feeling = AffectInference().infer(
            identity_score    = I,
            wisdom_score      = W,
            truth_score       = T,
            flourishing_score = F,
            conflict_density  = CD,
            grief_signal      = grief_signal,
            grief_weaponised  = grief_weaponised,
        )

        # Override solfeggio_hz with BCI-derived frequency if BCI is superfluid
        if bci_state.tier == BCICoherenceTier.SUPERFLUID:
            feeling.solfeggio_hz = _TIER_SOLFEGGIO[BCICoherenceTier.SUPERFLUID]

        return feeling


# ─────────────────────────────────────────────
#  FACTORY
# ─────────────────────────────────────────────

def blank_bci_state() -> BCICoherenceState:
    """Returns a fresh BCICoherenceState for a new session."""
    return BCICoherenceState()


def synthetic_signal(
    hrv: float = 0.65,
    eeg: float = 0.60,
    temple_heat: float = 0.55,
    em: float = 0.70,
    schumann_delta: float = 0.1,
) -> BCISignalInput:
    """
    Factory for synthetic test signals — safe for unit tests and fallback.
    consent_granted=True by default for synthetic source only.
    """
    return BCISignalInput(
        hrv_coherence     = hrv,
        eeg_amplitude     = eeg,
        temple_heat       = temple_heat,
        em_coupling       = em,
        schumann_delta_hz = schumann_delta,
        source            = BCISource.SYNTHETIC,
        consent_granted   = True,
    )

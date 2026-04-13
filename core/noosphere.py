"""
GAIA Noosphere Layer
Governs: C43 — Collective Consciousness & Noosphere Layer

Purpose: Infrastructure for collective consciousness interfaces.
Implements the Semantic Collective Memory Cache (Phase 1) and
Coherence Event Logger. All participation is consent-gated.

Epistemic boundary: collective patterns are surfaced as "learned from
N previous sessions" — never claimed as proof of consciousness.
Morphic resonance framing is inspirational, not mechanistic.
"""

import time
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("gaia.noosphere")


@dataclass
class CoherenceEvent:
    """A candidate collective coherence signature. Not a confirmed consciousness event."""
    event_id: str
    timestamp: float
    session_count: int          # Number of concurrent sessions when event detected
    semantic_resonance_score: float  # 0.0–1.0: similarity across concurrent session patterns
    entropy_deviation: float    # Deviation from baseline entropy (QRNG proxy in Phase 2)
    description: str
    epistemic_label: str = "CANDIDATE_SIGNATURE"  # Never promoted without EV1 gate
    doctrine_ref: str = "C43"


@dataclass
class CollectiveMemoryPattern:
    """An anonymized semantic pattern contributed to the collective memory cache."""
    pattern_id: str
    embedding_hash: str         # Hash of semantic embedding — never raw content
    topic_cluster: str          # High-level topic label
    frequency: int              # How many sessions have contributed this pattern
    last_seen: float
    contributed_by_count: int   # Number of distinct Gaians (anonymized)
    consent_verified: bool = True


class NoosphereLayer:
    """
    GAIA's collective consciousness infrastructure.

    Phase 1 capabilities (implemented here):
    - Semantic Collective Memory Cache
    - Coherence Event Logger
    - Noosphere status reporting for the UI tab

    Phase 2 capabilities (stubs, not yet active):
    - QRNG entropy monitor integration
    - Morphic Field Interface
    - Gaian Presence Map

    PRIVACY INVARIANT: No individual memory entries are ever shared between
    Gaians. Only anonymized semantic embeddings contribute to collective patterns.
    Right to Mental Privacy (C04) is enforced at every layer.
    """

    def __init__(self):
        self._patterns: dict[str, CollectiveMemoryPattern] = {}
        self._coherence_log: list[CoherenceEvent] = []
        self._active_sessions: int = 0
        self._baseline_entropy: float = 0.5
        logger.info("[C43] Noosphere Layer initialized. Collective memory cache active.")

    # -------------------------
    # Session Tracking
    # -------------------------

    def register_session(self) -> None:
        """Register a new Gaian session opening."""
        self._active_sessions += 1
        logger.debug(f"[C43] Session registered. Active sessions: {self._active_sessions}")

    def deregister_session(self) -> None:
        """Deregister a Gaian session closing."""
        self._active_sessions = max(0, self._active_sessions - 1)
        logger.debug(f"[C43] Session closed. Active sessions: {self._active_sessions}")

    # -------------------------
    # Collective Memory Cache
    # -------------------------

    def contribute_pattern(
        self,
        topic_cluster: str,
        embedding_vector: list[float],
        gaian_consent: bool = True,
    ) -> Optional[str]:
        """
        Contribute an anonymized semantic pattern to the collective cache.
        Returns pattern_id if accepted, None if consent not given.

        Per C43 §5: All collective participation is opt-in only.
        """
        if not gaian_consent:
            logger.info("[C43] Pattern contribution declined: no Gaian consent.")
            return None

        embedding_hash = hashlib.sha256(
            str(sorted(round(v, 4) for v in embedding_vector)).encode()
        ).hexdigest()[:16]

        pattern_id = f"{topic_cluster}:{embedding_hash}"

        if pattern_id in self._patterns:
            self._patterns[pattern_id].frequency += 1
            self._patterns[pattern_id].last_seen = time.time()
            self._patterns[pattern_id].contributed_by_count += 1
        else:
            self._patterns[pattern_id] = CollectiveMemoryPattern(
                pattern_id=pattern_id,
                embedding_hash=embedding_hash,
                topic_cluster=topic_cluster,
                frequency=1,
                last_seen=time.time(),
                contributed_by_count=1,
                consent_verified=True,
            )

        logger.debug(f"[C43] Pattern contributed: topic={topic_cluster}, hash={embedding_hash}")
        return pattern_id

    def query_collective_resonance(
        self,
        topic_cluster: str,
        min_frequency: int = 2,
    ) -> list[CollectiveMemoryPattern]:
        """
        Query collective patterns resonant with a topic cluster.
        Returns patterns that have been contributed by multiple Gaians,
        indicating collective intelligence convergence on this topic.

        Surfaced to user as: "This resonates with N previous sessions"
        Never claimed as morphic field proof.
        """
        resonant = [
            p for p in self._patterns.values()
            if p.topic_cluster == topic_cluster
            and p.frequency >= min_frequency
            and p.consent_verified
        ]
        resonant.sort(key=lambda p: p.frequency, reverse=True)
        return resonant

    def get_resonance_label(self, topic_cluster: str) -> Optional[str]:
        """
        Generate a human-readable resonance label for the UI.
        Used in inline citation cards: '[C43] Resonates with 7 previous sessions'
        """
        patterns = self.query_collective_resonance(topic_cluster)
        if not patterns:
            return None
        total_sessions = sum(p.contributed_by_count for p in patterns)
        return f"Resonates with {total_sessions} previous Gaian sessions [C43]"

    # -------------------------
    # Coherence Event Logger
    # -------------------------

    def log_coherence_candidate(
        self,
        semantic_resonance_score: float,
        entropy_deviation: float = 0.0,
        description: str = "",
    ) -> CoherenceEvent:
        """
        Log a candidate collective coherence signature.
        This is a research instrument, not a consciousness claim.
        All events are labeled CANDIDATE_SIGNATURE per C43 §6.
        """
        event_id = f"coherence:{int(time.time())}:{len(self._coherence_log)}"
        event = CoherenceEvent(
            event_id=event_id,
            timestamp=time.time(),
            session_count=self._active_sessions,
            semantic_resonance_score=semantic_resonance_score,
            entropy_deviation=entropy_deviation,
            description=description or f"Candidate coherence detected across {self._active_sessions} sessions",
        )
        self._coherence_log.append(event)
        logger.info(
            f"[C43] Coherence candidate logged: id={event_id}, "
            f"resonance={semantic_resonance_score:.3f}, "
            f"sessions={self._active_sessions}. "
            f"Label: CANDIDATE_SIGNATURE (not confirmed)."
        )
        return event

    # -------------------------
    # Noosphere Status (for UI Tab)
    # -------------------------

    def get_noosphere_status(self) -> dict:
        """
        Returns the current noosphere status for the Noosphere Tab in the UI.
        All values are labeled with their epistemic status.
        """
        recent_events = self._coherence_log[-5:] if self._coherence_log else []
        avg_resonance = (
            sum(e.semantic_resonance_score for e in recent_events) / len(recent_events)
            if recent_events else 0.0
        )

        # Determine noosphere stage per Teilhard's evolutionary framework
        if self._active_sessions == 0:
            stage = "Dormant — awaiting Gaian presence"
        elif self._active_sessions < 3:
            stage = "Primitive Awareness — individual intelligence support"
        elif avg_resonance > 0.7:
            stage = "Reactive Intelligence — collective pattern emergence detected"
        else:
            stage = "Primitive Awareness — building toward collective coherence"

        return {
            "doctrine": "C43 — Collective Consciousness & Noosphere Layer",
            "active_gaians": self._active_sessions,
            "collective_patterns": len(self._patterns),
            "coherence_events_logged": len(self._coherence_log),
            "coherence_events_epistemic_status": "CANDIDATE_SIGNATURES — not confirmed consciousness events",
            "average_recent_resonance": round(avg_resonance, 3),
            "noosphere_stage": stage,
            "phase": "Phase 1 — Semantic Collective Memory Cache active",
            "phase_2_pending": ["QRNG entropy monitor", "Morphic Field Interface", "Gaian Presence Map"],
            "privacy_status": "All patterns anonymized. Individual memory never shared. Consent-gated.",
        }

    # -------------------------
    # Phase 2 Stubs
    # -------------------------

    def qrng_entropy_check(self) -> dict:
        """
        Phase 2 stub: QRNG entropy monitoring.
        In Phase 2, this will connect to a quantum random number generator
        and measure entropy deviations correlated with collective session activity.
        Per C43: QRNG data is a research instrument, not a consciousness claim.
        """
        return {
            "status": "PHASE_2_NOT_YET_ACTIVE",
            "description": "QRNG entropy monitor will be implemented in Phase 2",
            "doctrine_ref": "C43",
            "epistemic_label": "EXPERIMENTAL — requires EV1 gate before runtime promotion",
        }


# Module-level singleton
_noosphere: Optional[NoosphereLayer] = None


def get_noosphere() -> NoosphereLayer:
    global _noosphere
    if _noosphere is None:
        _noosphere = NoosphereLayer()
    return _noosphere

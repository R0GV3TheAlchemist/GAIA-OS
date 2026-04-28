"""
core/engines/
=============
GAIA Processing Engines — all signal processing, field computation,
and arc-management engines live here.

Submodules
----------
quintessence_engine     — T5 unified field layer (C49)
resonance_field_engine  — resonance field computation
meta_coherence_engine   — meta-coherence monitoring
coherence_field_engine  — coherence field state
settling_engine         — emotional settling / grounding
regulation_engine       — autonomic regulation
reflection_engine       — reflective processing
awareness_event_engine  — awareness event stream
codex_stage_engine      — Codex stage management
somatic_profile_engine  — somatic body profile
soul_mirror_engine      — Jungian soul-mirror (individuation)
bond_arc_engine         — relational bond arc
love_arc_engine         — love arc progression
growth_arc_engine       — growth arc tracking
development_stage_engine — human development stages
dynamic_forces_engine   — dynamic force field
five_forces_engine      — Porter-style five forces
integration_engine      — cross-system integration
phase_state_monitor     — phase state tracking
criticality_monitor     — edge-of-chaos criticality
"""

from core.engines.quintessence_engine import (
    QuintessenceEngine,
    QuintessenceState,
    QuintessenceMode,
    QuintessencePhase,
    get_quintessence_engine,
    read_quintessence,
)
from core.engines.resonance_field_engine import ResonanceFieldEngine
from core.engines.meta_coherence_engine import MetaCoherenceEngine
from core.engines.coherence_field_engine import CoherenceFieldEngine
from core.engines.settling_engine import SettlingEngine
from core.engines.regulation_engine import RegulationEngine
from core.engines.reflection_engine import ReflectionEngine
from core.engines.awareness_event_engine import AwarenessEventEngine
from core.engines.codex_stage_engine import CodexStageEngine
from core.engines.soul_mirror_engine import SoulMirrorEngine
from core.engines.bond_arc_engine import BondArcEngine
from core.engines.love_arc_engine import LoveArcEngine
from core.engines.growth_arc_engine import GrowthArcEngine
from core.engines.development_stage_engine import DevelopmentStageEngine
from core.engines.dynamic_forces_engine import DynamicForcesEngine
from core.engines.five_forces_engine import FiveForcesEngine
from core.engines.integration_engine import IntegrationEngine
from core.engines.phase_state_monitor import PhaseStateMonitor
from core.engines.criticality_monitor import CriticalityMonitor
from core.engines.somatic_profile_engine import SomaticProfileEngine

__all__ = [
    "QuintessenceEngine", "QuintessenceState", "QuintessenceMode",
    "QuintessencePhase", "get_quintessence_engine", "read_quintessence",
    "ResonanceFieldEngine", "MetaCoherenceEngine", "CoherenceFieldEngine",
    "SettlingEngine", "RegulationEngine", "ReflectionEngine",
    "AwarenessEventEngine", "CodexStageEngine", "SoulMirrorEngine",
    "BondArcEngine", "LoveArcEngine", "GrowthArcEngine",
    "DevelopmentStageEngine", "DynamicForcesEngine", "FiveForcesEngine",
    "IntegrationEngine", "PhaseStateMonitor", "CriticalityMonitor",
    "SomaticProfileEngine",
]

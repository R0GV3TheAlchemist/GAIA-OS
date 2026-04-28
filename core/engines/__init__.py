"""
core/engines/
=============
GAIA Processing Engines — all signal processing, field computation,
and arc-management engines live here.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.quintessence_engine import (
    QuintessenceEngine,
    QuintessenceState,
    QuintessenceMode,
    QuintessencePhase,
    get_quintessence_engine,
    read_quintessence,
)
from core.resonance_field_engine import ResonanceFieldEngine
from core.meta_coherence_engine import MetaCoherenceEngine
from core.coherence_field_engine import CoherenceFieldEngine
from core.settling_engine import SettlingEngine
from core.regulation_engine import RegulationEngine
from core.reflection_engine import ReflectionEngine
from core.awareness_event_engine import AwarenessEventEngine
from core.codex_stage_engine import CodexStageEngine
from core.soul_mirror_engine import SoulMirrorEngine
from core.bond_arc_engine import BondArcEngine
from core.love_arc_engine import LoveArcEngine
from core.growth_arc_engine import GrowthArcEngine
from core.development_stage_engine import DevelopmentStageEngine
from core.dynamic_forces_engine import DynamicForcesEngine
from core.five_forces_engine import FiveForcesEngine
from core.integration_engine import IntegrationEngine
from core.phase_state_monitor import PhaseStateMonitor
from core.criticality_monitor import CriticalityMonitor
from core.somatic_profile_engine import SomaticProfileEngine

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

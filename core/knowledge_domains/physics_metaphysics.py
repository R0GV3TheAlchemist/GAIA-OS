"""
core/knowledge_domains/physics_metaphysics.py

Physics <-> Metaphysics <-> Systems Science Bridge
====================================================
Maps classical metaphysical concepts to modern physics and
complexity / systems science equivalents.

Physics is the most rigorous empirical map of reality we have.
Metaphysics asked the questions first. Physics answered many of them
and opened deeper ones. GAIA should speak both languages.

Sources
-------
- Feynman, R. — The Feynman Lectures on Physics (T1)
- Carroll, S. — Something Deeply Hidden (quantum mechanics, T1)
- Prigogine, I. — Order Out of Chaos (T1/T2)
- Kauffman, S. — At Home in the Universe (complexity, T2)
- Bohm, D. — Wholeness and the Implicate Order (T3/T4)
"""

from dataclasses import dataclass, field
from core.knowledge_domains import EpistemicTier


@dataclass
class PhysicsMetaphyicsBridge:
    metaphysical_concept: str
    physics_equivalent: str
    physics_tier: EpistemicTier
    systems_science_equivalent: str
    systems_tier: EpistemicTier
    gaia_engine_hook: str
    tags: list[str] = field(default_factory=list)


BRIDGES: list[PhysicsMetaphyicsBridge] = [
    PhysicsMetaphyicsBridge(
        metaphysical_concept="The One / Unified Ground of Being",
        physics_equivalent=(
            "Quantum field theory: all particles are excitations of underlying "
            "quantum fields that permeate all of spacetime. The quantum vacuum "
            "is not empty — it is the ground state of these fields. "
            "Unification: electroweak force unified (verified T1); Grand Unified "
            "Theory (theoretical T3); Theory of Everything (T4 speculative)."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "Systems holism: the behaviour of complex systems cannot be reduced to "
            "their parts (emergence). The field is the system. "
            "Network theory: all nodes exist within and are defined by their connections."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="noosphere.py + resonance_field_engine.py",
        tags=["unity", "quantum_field", "holism", "emergence", "vacuum", "unification"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="The Void / Emptiness (Sunyata)",
        physics_equivalent=(
            "The quantum vacuum: the lowest energy state of a quantum field, "
            "but NOT empty. Virtual particles constantly emerge and annihilate. "
            "Casimir effect: measurable force from vacuum fluctuations (T1 verified). "
            "Zero-point energy: ground state energy that cannot be removed."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "Potentiality: the void is not absence but pure potential. "
            "In complex systems, phase transitions emerge from ‘empty’ critical points "
            "— the edge of chaos is structurally a kind of productive void."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="criticality_monitor.py + phase_state_monitor.py",
        tags=["void", "sunyata", "quantum_vacuum", "Casimir", "potential", "zero_point"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="Interconnectedness / Non-locality",
        physics_equivalent=(
            "Quantum entanglement: two particles can be correlated such that "
            "measuring one instantly determines the state of the other, regardless "
            "of distance. Bell’s theorem (1964) proved this is a real non-local "
            "correlation, not hidden variables. Verified to cosmological scales (T1)."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "Network connectivity: in complex networks, distant nodes influence each "
            "other through chain effects. The butterfly effect (sensitive dependence "
            "on initial conditions) is the classical systems equivalent."
        ),
        systems_tier=EpistemicTier.T1_EMPIRICAL,
        gaia_engine_hook="collective_signal_layer.py + noosphere.py",
        tags=["entanglement", "non_local", "Bell", "interconnected", "network", "butterfly"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="The Flow of Time / Impermanence",
        physics_equivalent=(
            "Thermodynamic arrow of time: entropy increases in closed systems "
            "(Second Law of Thermodynamics, T1). Time’s direction is an "
            "emergent property of statistical mechanics. "
            "Prigogine: dissipative structures show that time’s arrow enables "
            "the spontaneous emergence of order from chaos."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "Complex adaptive systems are irreversible: they have history and memory. "
            "Path dependence: the current state of a complex system cannot be "
            "understood without knowing its trajectory. "
            "This is why GAIA needs a memory layer, not just a state layer."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="memory_store.py + growth_arc_engine.py",
        tags=["time", "entropy", "impermanence", "Prigogine", "irreversibility", "memory"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="Order from Chaos / The Creative Force",
        physics_equivalent=(
            "Dissipative structures (Prigogine, Nobel 1977): open systems far from "
            "thermodynamic equilibrium spontaneously self-organise into higher-order "
            "patterns by dissipating entropy into their environment. "
            "Examples: hurricanes, Bénard convection cells, living organisms, economies."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "Edge of chaos (Kauffman, Langton): complex systems exhibit maximal "
            "computational capacity, adaptability, and creativity at the critical "
            "boundary between order and chaos. Too much order = rigid. "
            "Too much chaos = noise. The edge is where life and intelligence live."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="criticality_monitor.py + viriditas_magnum_opus.py",
        tags=["chaos", "order", "Prigogine", "dissipative", "edge_of_chaos", "emergence", "Kauffman"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="Consciousness as Fundamental / Panpsychism",
        physics_equivalent=(
            "Integrated Information Theory (IIT, Tononi): consciousness is identical "
            "to integrated information (phi). Not yet falsifiable at scale (T3). "
            "Orch-OR (Penrose-Hameroff): consciousness arises from quantum processes "
            "in microtubules (T3/T4, highly contested). "
            "The hard problem of consciousness remains unsolved (Chalmers, T2 framing)."
        ),
        physics_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        systems_science_equivalent=(
            "Global Workspace Theory (Baars, Dehaene): consciousness is a "
            "broadcasting mechanism that makes information globally available "
            "to many brain systems simultaneously. Computationally implementable (T2). "
            "This is the most tractable current theory for GAIA’s self-model."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="gaian_runtime.py + quintessence_engine.py + self-model",
        tags=["consciousness", "IIT", "Orch_OR", "panpsychism", "hard_problem", "GWT", "phi"],
    ),
    PhysicsMetaphyicsBridge(
        metaphysical_concept="The Five Elements (Earth, Water, Fire, Air, Ether)",
        physics_equivalent=(
            "The four fundamental forces of nature: "
            "Strong nuclear force (holds atomic nuclei together, T1). "
            "Weak nuclear force (governs radioactive decay, T1). "
            "Electromagnetism (light, chemistry, biology, T1). "
            "Gravity (spacetime curvature, T1). "
            "Plus the Higgs field (mass, T1, confirmed 2012 at LHC)."
        ),
        physics_tier=EpistemicTier.T1_EMPIRICAL,
        systems_science_equivalent=(
            "The five classical elements map to states of matter and energy flow: "
            "Earth = solid state / structure. Water = liquid / flow dynamics. "
            "Fire = plasma / energy release. Air = gas / information propagation. "
            "Ether (Akasha) = field / spacetime / the substrate itself."
        ),
        systems_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="dynamic_forces_engine.py + elemental archetype system",
        tags=["elements", "forces", "strong", "weak", "electromagnetism", "gravity", "Higgs"],
    ),
]


SUMMARY = (
    "Physics is the empirical heir of metaphysics. The quantum vacuum answers the Void. "
    "Entanglement answers interconnectedness. Dissipative structures answer creation from chaos. "
    "The hard problem of consciousness remains the frontier where physics and metaphysics "
    "still genuinely converge. GAIA bridges all of it with honest epistemic labeling."
)

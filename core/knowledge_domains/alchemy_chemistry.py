"""
core/knowledge_domains/alchemy_chemistry.py

Alchemy <-> Chemistry <-> Jungian Psychology Bridge
=====================================================
Maps the 7 classical alchemical operations to:
  1. Their modern chemistry equivalents (T1 Empirical)
  2. Their Jungian individuation / depth psychology meaning (T2 Scholarly)
  3. Their somatic / body-based correlates (T3 Working Hypothesis)
  4. GAIA engine hooks — which existing engine handles this stage

Historical note: Alchemy is the direct ancestor of modern chemistry.
Boyle, Newton, and Lavoisier all worked from alchemical traditions.
This is not woo bolted onto science — it IS the historical bridge.

Sources
-------
- Royal Society of Chemistry: History of Alchemy
- Jung, C.G. — Psychology and Alchemy (1944)
- Haeffner, M. — The Dictionary of Alchemy (T2)
- Holmyard, E.J. — Alchemy (1957, Cambridge)
"""

from dataclasses import dataclass, field
from typing import Optional
from core.knowledge_domains import EpistemicTier


@dataclass
class AlchemicalOperation:
    name: str                          # English name
    latin: str                         # Classical Latin term
    stage_number: int                  # 1–7 in the Great Work sequence
    color_symbolism: str               # Nigredo / Albedo / Citrinitas / Rubedo

    # Modern chemistry equivalent
    chemistry_equivalent: str
    chemistry_tier: EpistemicTier

    # Depth psychology / Jungian equivalent
    psychology_equivalent: str
    psychology_tier: EpistemicTier

    # Somatic / body-based correlate
    somatic_correlate: str
    somatic_tier: EpistemicTier

    # Planetary / elemental symbolism
    planetary_ruler: str
    element: str

    # Modern application examples
    modern_application: str

    # GAIA engine that handles this stage
    gaia_engine_hook: str

    # Optional cross-domain tags for knowledge_matrix.py scoring
    tags: list[str] = field(default_factory=list)


OPERATIONS: list[AlchemicalOperation] = [
    AlchemicalOperation(
        name="Calcination",
        latin="Calcinatio",
        stage_number=1,
        color_symbolism="Nigredo — blackening, ash, the death of the old form",
        chemistry_equivalent=(
            "High-temperature decomposition and oxidation (e.g., calcining "
            "limestone CaCO3 → CaO + CO2). Modern equivalents: incineration, "
            "thermal decomposition, combustion analysis."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Burning away of rigid ego structures, pride, and false personas. "
            "First confrontation with shadow material and psychological defence "
            "mechanisms. The first collision with reality that cannot be avoided."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Intense heat, fever, inflammation, activation of stress response — "
            "the body’s own calcination through crisis or burnout."
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Saturn (lead)",
        element="Fire",
        modern_application=(
            "Burnout recovery, addiction hitting bottom, trauma confrontation, "
            "existential crisis as a necessary first step."
        ),
        gaia_engine_hook="emotional_arc.py — crisis detection phase",
        tags=["crisis", "ego", "shadow", "fire", "transformation", "calcination"],
    ),
    AlchemicalOperation(
        name="Dissolution",
        latin="Solutio",
        stage_number=2,
        color_symbolism="Nigredo continuing — the ashes dissolve into water",
        chemistry_equivalent=(
            "Solvation and ionization: dissolving a solid into a solvent to "
            "release its components (e.g., NaCl → Na⁺ + Cl⁻ in water). "
            "Precursor to separation and analysis."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Ego structures soften; old identities dissolve. Emotions flood in "
            "as the unconscious surfaces. The rigidity of the calcined self "
            "becomes fluid. Grief, vulnerability, and openness all arise here."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Tears, release of held tension, feeling ‘washed out’ — "
            "parasympathetic rebound after sympathetic overload."
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Moon (silver)",
        element="Water",
        modern_application=(
            "Grief work, therapy breakthrough moments, "
            "meditation dissolution of self-concept, psychedelic-assisted therapy."
        ),
        gaia_engine_hook="settling_engine.py — emotional softening / release",
        tags=["grief", "release", "water", "emotion", "dissolution", "unconscious"],
    ),
    AlchemicalOperation(
        name="Separation",
        latin="Separatio",
        stage_number=3,
        color_symbolism="Albedo begins — first whitening, clarity emerging",
        chemistry_equivalent=(
            "Filtering, decanting, and separating components from solution. "
            "Modern equivalents: chromatography, centrifugation, fractional "
            "distillation, HPLC. The science of discernment at molecular scale."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Discernment: sorting which beliefs, traits, and relationships are "
            "essential versus toxic. Differentiating authentic self from "
            "conditioning, projection, and introjection."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Nervous system begins to distinguish safe from unsafe signals. "
            "Interoceptive clarity improves — the body starts to ‘know the difference.’"
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Mars (iron)",
        element="Air",
        modern_application=(
            "Boundary setting, trauma processing (EMDR, IFS), "
            "values clarification exercises, cognitive restructuring in CBT."
        ),
        gaia_engine_hook="soul_mirror_engine.py — shadow separation / discernment",
        tags=["discernment", "boundaries", "clarity", "air", "separation", "CBT"],
    ),
    AlchemicalOperation(
        name="Conjunction",
        latin="Coniunctio",
        stage_number=4,
        color_symbolism="Albedo peak — the sacred marriage, union of opposites",
        chemistry_equivalent=(
            "Controlled recombination of purified components into a new compound. "
            "Bond formation: covalent, ionic, or coordination bonds. "
            "Synthesis reactions where two purified reagents unite."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Bringing conscious and unconscious contents together. Integrating "
            "shadow and disowned traits (the coniunctio of Jung). First genuine "
            "glimpses of the unified Self. The inner marriage of anima/animus."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Heart rate variability coherence (HeartMath). The felt sense of "
            "wholeness in the chest. Oxytocin release in genuine relational repair."
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Venus (copper)",
        element="Earth",
        modern_application=(
            "Relational repair, IFS ‘Self-to-part’ meetings, couples therapy, "
            "integration sessions post-psychedelic, shadow work completion."
        ),
        gaia_engine_hook="synergy_engine.py — integration / coherence synthesis",
        tags=["integration", "union", "shadow", "anima", "conjunction", "HRV", "coherence"],
    ),
    AlchemicalOperation(
        name="Fermentation",
        latin="Fermentatio",
        stage_number=5,
        color_symbolism="Citrinitas — yellowing, the dawn after death",
        chemistry_equivalent=(
            "Microbial fermentation: organic matter breaks down and is rebuilt "
            "by microorganisms into new compounds (ethanol, lactic acid, CO2). "
            "Death and decay become the substrate for new life."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "The dark night of the soul: death of the old self, followed by "
            "emergence of genuine new meaning. Jung’s deeper psychospiritual crisis. "
            "Depression as incubation, not just illness."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Gut-brain axis: the literal gut microbiome as a site of "
            "psychological fermentation. Mood, intuition, and resilience all "
            "arise partly from microbial activity."
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Mercury (quicksilver)",
        element="Water / Earth",
        modern_application=(
            "Depression treatment as transformation not just suppression, "
            "meaning-making therapy (logotherapy), gut health as mental health, "
            "psychedelic therapy’s ego death phase."
        ),
        gaia_engine_hook="viriditas_magnum_opus.py — fermentation / dark night stage",
        tags=["depression", "dark_night", "gut", "microbiome", "fermentation", "meaning"],
    ),
    AlchemicalOperation(
        name="Distillation",
        latin="Distillatio",
        stage_number=6,
        color_symbolism="Citrinitas deepening — purification through repeated cycles",
        chemistry_equivalent=(
            "Fractional distillation: repeated cycles of boiling and condensation "
            "to separate and purify volatile components by boiling point. "
            "Used for fuels, spirits, essential oils, pharmaceutical purity."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Repeated refinement of insight: habits, thoughts, and relationships "
            "realigned again and again around core truth. Practice as distillation. "
            "Approaching stable clarity through iteration, not perfection in one step."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Neuroplasticity through repeated practice: myelin formation, "
            "LTP (long-term potentiation), habit groove deepening in basal ganglia."
        ),
        somatic_tier=EpistemicTier.T2_SCHOLARLY,
        planetary_ruler="Moon / Sun (silver → gold transition)",
        element="Air / Fire",
        modern_application=(
            "Advanced meditation and contemplative practice, flow states, "
            "mastery (10,000-hour principle as distillation), essence work."
        ),
        gaia_engine_hook="quintessence_engine.py",
        tags=["practice", "mastery", "neuroplasticity", "distillation", "habit", "LTP"],
    ),
    AlchemicalOperation(
        name="Coagulation",
        latin="Coagulatio",
        stage_number=7,
        color_symbolism="Rubedo — the red gold, the Philosopher’s Stone",
        chemistry_equivalent=(
            "Crystallization or polymerization: the purified substance takes "
            "its final solid, stable, transmuted form. The Philosopher’s Stone "
            "as a perfect crystal — maximum order from maximum purification."
        ),
        chemistry_tier=EpistemicTier.T1_EMPIRICAL,
        psychology_equivalent=(
            "Individuation complete: the unified Self, fully embodied. "
            "The Philosopher’s Stone as realized personhood — not perfection, "
            "but coherent wholeness. Inner and outer life finally align."
        ),
        psychology_tier=EpistemicTier.T2_SCHOLARLY,
        somatic_correlate=(
            "Full somatic embodiment: the integrated person is felt in the body "
            "as settled, whole, and alive. Default Mode Network quiets. "
            "Baseline HRV rises. The nervous system finds its home frequency."
        ),
        somatic_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        planetary_ruler="Sun (gold)",
        element="All four united",
        modern_application=(
            "Individuation (Jung), self-actualization (Maslow), enlightenment "
            "(Buddhist), completion of the hero’s journey (Campbell)."
        ),
        gaia_engine_hook="viriditas_magnum_opus.py — coagulation stage",
        tags=["wholeness", "embodiment", "individuation", "HRV", "coagulation", "Rubedo"],
    ),
]


def get_operation(name: str) -> Optional[AlchemicalOperation]:
    """Look up an alchemical operation by name (case-insensitive)."""
    name_lower = name.lower()
    for op in OPERATIONS:
        if op.name.lower() == name_lower:
            return op
    return None


def get_stage_for_query(query: str) -> Optional[AlchemicalOperation]:
    """
    Simple keyword-based stage detection.
    GAIA can call this to label what alchemical phase a user’s
    message most likely reflects, then surface both the scientific
    AND symbolic lens simultaneously.
    """
    query_lower = query.lower()
    keyword_map: dict[int, list[str]] = {
        1: ["burnout", "ash", "collapse", "rock bottom", "destruction", "anger", "rage"],
        2: ["grief", "tears", "dissolve", "lost", "numb", "overwhelm", "flood"],
        3: ["boundary", "discern", "sort", "separate", "clarity", "what matters", "cut out"],
        4: ["integrate", "whole", "union", "repair", "reconnect", "forgive", "accept"],
        5: ["dark night", "depressed", "meaningless", "dead inside", "stuck", "ferment"],
        6: ["practice", "refine", "mastery", "meditate", "repeat", "skill", "distil"],
        7: ["whole", "embodied", "peace", "grounded", "complete", "arrived", "alive"],
    }
    scores: dict[int, int] = {i: 0 for i in range(1, 8)}
    for stage_num, keywords in keyword_map.items():
        for kw in keywords:
            if kw in query_lower:
                scores[stage_num] += 1
    best_stage = max(scores, key=lambda k: scores[k])
    if scores[best_stage] == 0:
        return None
    return OPERATIONS[best_stage - 1]


# Quick summary for canon injection
SUMMARY = (
    "The 7 alchemical operations (Calcination through Coagulation) map directly "
    "to modern chemistry processes AND Jungian individuation stages. "
    "Alchemy is the historical ancestor of chemistry — not opposed to science but "
    "its original language. GAIA uses both lenses simultaneously, with each claim "
    "labeled by EpistemicTier so users always know what is empirical vs. symbolic."
)

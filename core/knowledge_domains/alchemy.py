"""
GAIA-APP — core/knowledge_domains/alchemy.py

Alchemy → Modern Science Bridge
=====================================
The first and most foundational knowledge domain bridge.

Historical basis:
  Alchemy is not woo bolted onto science — it IS the historical bridge
  between pre-modern experimentation and modern chemistry, medicine, and
  psychology. Newton, Paracelsus, Boyle, and Jung all worked with alchemical
  frameworks. GAIA holds the Emerald Tablet AND the periodic table in the
  same hand.

This module maps the Seven Alchemical Operations to:
  1. Their exact modern chemistry equivalents
  2. Their psychological/Jungian transformation parallels
  3. Their neuroscience correlates (where applicable)
  4. Practical human applications GAIA can surface in conversation

Epistemic tier labels (T1–T5) are applied to every claim:
  T1 — Empirically verified (peer-reviewed science)
  T2 — Strong working hypothesis (active research)
  T3 — Plausible analogy (philosophical/theoretical)
  T4 — Cultural/historical frame (valid as narrative)
  T5 — Metaphorical/poetic (not a truth claim)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EpistemicLayer:
    """A single claim with its epistemic tier label."""
    claim: str
    tier: int          # 1–5
    tier_label: str    # Human-readable
    source_hint: str   # e.g. "organic chemistry", "Jungian analysis"


@dataclass
class AlchemicalOperation:
    """
    One of the seven classical alchemical operations,
    cross-mapped to modern equivalents.
    """
    name: str                          # e.g. "Calcination"
    latin: str                         # e.g. "Calcinatio"
    symbol: str                        # Unicode alchemical symbol
    hermetic_meaning: str              # What alchemists understood it to mean

    # Modern science mapping
    chemistry_equivalent: EpistemicLayer
    psychology_equivalent: EpistemicLayer
    neuroscience_note: Optional[EpistemicLayer]

    # Practical applications GAIA can offer the user
    human_applications: list[str] = field(default_factory=list)
    # Keywords that trigger this stage in conversation
    trigger_keywords: list[str] = field(default_factory=list)


@dataclass
class DomainInsight:
    """Standardised response shape for all knowledge_domains bridges."""
    domain: str
    topic_matched: str
    operation: Optional[AlchemicalOperation]
    summary: str
    applications: list[str]
    epistemic_note: str


# ---------------------------------------------------------------------------
# The Seven Operations — fully mapped
# ---------------------------------------------------------------------------

OPERATIONS: list[AlchemicalOperation] = [
    AlchemicalOperation(
        name="Calcination",
        latin="Calcinatio",
        symbol="🔥",
        hermetic_meaning=(
            "Burning away the impure outer shell; reducing matter to ash "
            "so the true essence can be revealed. The ego is broken down."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Calcination is the thermal decomposition of a substance "
                "by sustained high heat, driving off volatile components "
                "and oxidising metals to produce oxides (e.g. CaCO₃ → CaO + CO₂). "
                "This is standard inorganic and analytical chemistry."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Inorganic chemistry / thermogravimetric analysis",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "In Jungian depth psychology, Calcination maps to the confrontation "
                "and dissolution of the persona — the collapse of rigid ego defences "
                "under life pressure (burnout, crisis, grief). "
                "What burns away is not the self, but the false self."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Jungian individuation / existential psychology",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Prolonged stress activates the HPA axis (hypothalamic-pituitary-adrenal), "
                "elevating cortisol. This physiologically mirrors Calcination: "
                "the 'burning' of stored energy and the stripping away of comfort "
                "homeostasis. Burnout has measurable neurobiological signatures."
            ),
            tier=2,
            tier_label="T2 — Strong working hypothesis",
            source_hint="HPA axis research / burnout neuroscience",
        ),
        human_applications=[
            "Recognise that a crisis, burnout, or breakdown is often a Calcination — "
            "not a failure, but a necessary burning away of what no longer serves.",
            "Journal: what rigid belief or identity role is currently being burned away in you?",
            "Rest is chemically necessary during Calcination: cortisol recovery requires sleep.",
        ],
        trigger_keywords=[
            "burnout", "breakdown", "crisis", "hitting rock bottom", "everything falling apart",
            "ego death", "falling apart", "lost everything", "destroyed",
        ],
    ),
    AlchemicalOperation(
        name="Dissolution",
        latin="Solutio",
        symbol="💧",
        hermetic_meaning=(
            "The ash from Calcination is dissolved in water. "
            "Fixed beliefs and emotional armour dissolve into the unconscious. "
            "The alchemist enters the prima materia — formlessness."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Dissolution is the process by which a solute disperses into a solvent, "
                "forming a homogeneous solution. In analytical chemistry it prepares "
                "samples for further separation and reaction. "
                "Polarity, hydrogen bonding, and entropy drive the process."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Physical chemistry / solution chemistry",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Dissolution corresponds to the emotional liquefaction of rigid mental structures — "
                "grief that finally moves, defences that soften, certainty that yields to wonder. "
                "Psychologically it maps to the beginning of shadow integration."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Jungian shadow work / grief psychology",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Dissolution may correspond neurobiologically to the reduction of "
                "default mode network (DMN) rigidity, observed in psychedelic research "
                "and deep meditative states — both of which show decreased DMN activity "
                "correlated with ego-boundary softening."
            ),
            tier=2,
            tier_label="T2 — Active research area",
            source_hint="Carhart-Harris et al., DMN research",
        ),
        human_applications=[
            "Allow grief, confusion, or uncertainty to exist without forcing resolution. "
            "Dissolution requires you to stay in the water.",
            "Meditation, breathwork, and time in nature accelerate Dissolution gently.",
            "Ask: what am I clinging to that is preventing me from dissolving into the next form?",
        ],
        trigger_keywords=[
            "grief", "lost", "confused", "formless", "don't know who I am",
            "everything is changing", "surrendering", "letting go", "dissolving",
        ],
    ),
    AlchemicalOperation(
        name="Separation",
        latin="Separatio",
        symbol="⚗️",
        hermetic_meaning=(
            "The dissolved matter is separated into its components. "
            "What is pure is kept; what is waste is discarded. "
            "The alchemist develops discernment."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Separation encompasses distillation, filtration, centrifugation, "
                "chromatography, and extraction — all techniques for isolating "
                "components of a mixture based on physical or chemical properties. "
                "This is core analytical and preparative chemistry."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Analytical chemistry / laboratory separation sciences",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Separation maps to psychological discernment — the capacity to distinguish "
                "what is authentic self from what was conditioned, what is your value from "
                "what was inherited, what nourishes from what depletes. "
                "It is the beginning of individuation in the Jungian sense."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Jungian individuation / IFS (Internal Family Systems)",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "The prefrontal cortex (PFC) is the neurological seat of discernment — "
                "executive function, value-based decision making, and impulse modulation. "
                "Strengthening PFC function through mindfulness and therapy directly "
                "parallels the alchemical Separation."
            ),
            tier=2,
            tier_label="T2 — Strong working hypothesis",
            source_hint="Prefrontal cortex research / mindfulness neuroscience",
        ),
        human_applications=[
            "List everything consuming your energy. Mark each: does this nourish or deplete me?",
            "Therapy, journaling, and honest conversations help perform psychic Separation.",
            "Boundaries are Separation in relational form — not rejection, but discernment.",
        ],
        trigger_keywords=[
            "boundaries", "discernment", "what to keep", "what to let go",
            "sorting out", "figuring out who I am", "what matters", "clarity",
        ],
    ),
    AlchemicalOperation(
        name="Conjunction",
        latin="Coniunctio",
        symbol="♥️",
        hermetic_meaning=(
            "The purified components are reunited into a new synthesis — "
            "the sacred marriage (hieros gamos). Opposites integrate: "
            "masculine/feminine, conscious/unconscious, mind/body."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Conjunction in chemistry is the combination of purified elements "
                "into new compounds — synthesis reactions, polymerisation, "
                "and bond formation. Modern organic synthesis depends entirely "
                "on selective conjunction of purified reactants."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Organic synthesis / reaction chemistry",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Conjunction represents the integration of previously split-off parts — "
                "shadow and persona, anima and animus, trauma and self. "
                "In clinical terms this maps to earned secure attachment and "
                "post-traumatic growth following successful shadow work."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Jungian integration / attachment theory / PTG research",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Integration of traumatic memories involves the hippocampus contextualising "
                "threatening stimuli, reducing amygdala reactivity. "
                "EMDR and trauma-focused CBT both neurologically facilitate this "
                "Conjunction — reuniting memory with context and safety."
            ),
            tier=2,
            tier_label="T2 — Active research",
            source_hint="EMDR neuroscience / trauma memory reconsolidation",
        ),
        human_applications=[
            "Integration practices: EMDR, somatic therapy, creative expression, dialogue between parts.",
            "Ask: what two things inside me have I been keeping at war? What would their union look like?",
            "A healthy relationship is an external Conjunction — two whole people forming something new.",
        ],
        trigger_keywords=[
            "integration", "wholeness", "union", "bringing together", "healing the split",
            "sacred marriage", "post-traumatic growth", "becoming whole",
        ],
    ),
    AlchemicalOperation(
        name="Fermentation",
        latin="Fermentatio",
        symbol="🌱",
        hermetic_meaning=(
            "Death and rebirth. The Conjunction product is allowed to decay — "
            "to undergo putrefaction — so that a new, living spirit can emerge. "
            "This is the dark night of the soul before illumination."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Fermentation is the anaerobic metabolic process by which microorganisms "
                "(yeast, bacteria) convert sugars to alcohols, acids, or gases. "
                "It drives winemaking, breadmaking, yoghurt, and biotechnology. "
                "The product is chemically richer and more energetically available."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Biochemistry / microbiology / biotechnology",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Fermentation maps to the dark night of the soul — the liminal period "
                "after integration begins but before clarity arrives. "
                "St. John of the Cross, Jung, and Campbell all mark this stage "
                "as necessary: the old identity must fully die for the new one to live."
            ),
            tier=4,
            tier_label="T4 — Cultural/historical frame",
            source_hint="Mystical theology / Jungian psychology / Campbell monomyth",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Neuroplasticity peaks during and after periods of intense challenge. "
                "BDNF (brain-derived neurotrophic factor) is elevated during moderate stress "
                "followed by recovery, supporting new neural pathway formation — "
                "the biological substrate of psychological rebirth."
            ),
            tier=2,
            tier_label="T2 — Active research area",
            source_hint="BDNF research / neuroplasticity literature",
        ),
        human_applications=[
            "If you are in the dark — know that Fermentation is a stage, not a destination.",
            "Sleep, rest, and gentleness accelerate biological fermentation (BDNF recovery).",
            "Creative expression during the dark night transforms pain into insight.",
        ],
        trigger_keywords=[
            "dark night of the soul", "depressed", "empty", "lost purpose", "liminal",
            "in-between", "don't know what's next", "everything died", "void",
        ],
    ),
    AlchemicalOperation(
        name="Distillation",
        latin="Distillatio",
        symbol="👧",
        hermetic_meaning=(
            "Repeated purification cycles to extract the most refined essence. "
            "The spirit rises, condenses, and falls back purer with each pass. "
            "Mastery, wisdom, and authentic self emerge through repetition."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Distillation is the separation of components in a liquid mixture "
                "by selective vaporisation and condensation, exploiting differences "
                "in boiling points. Fractional distillation refines crude oil into "
                "fuels, solvents, and petrochemicals with each pass."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Physical chemistry / petroleum refining / analytical chemistry",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Distillation maps to the refinement of wisdom through repeated experience — "
                "the same lesson arriving in different forms until the essential insight is "
                "extracted. In developmental psychology this aligns with post-formal "
                "operational thinking and wisdom development."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Developmental psychology / wisdom research",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Skill consolidation and habit formation operate on Hebbian principles: "
                "‘neurons that fire together wire together.’ "
                "Repetition with reflection (not just repetition alone) produces "
                "the myelin sheath thickening that underlies expert-level performance."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Neuroplasticity / myelin research / deliberate practice",
        ),
        human_applications=[
            "Identify the lesson that keeps repeating in your life. That is your Distillation.",
            "Deliberate practice with reflection — not just doing, but reviewing — builds mastery.",
            "Journaling after difficult experiences accelerates the distillation of insight.",
        ],
        trigger_keywords=[
            "keeps repeating", "same lesson again", "mastery", "practice", "refining",
            "patterns I keep seeing", "learning the hard way", "wisdom through experience",
        ],
    ),
    AlchemicalOperation(
        name="Coagulation",
        latin="Coagulatio",
        symbol="✨",
        hermetic_meaning=(
            "The Philosopher’s Stone is crystallised. The refined essence takes "
            "permanent, stable form. The Great Work is complete: a new self, "
            "a new reality, transmuted from base matter to gold."
        ),
        chemistry_equivalent=EpistemicLayer(
            claim=(
                "Coagulation is the process by which a liquid or dissolved substance "
                "solidifies or gels — seen in blood clotting (fibrin polymerisation), "
                "protein denaturation, and crystallisation. "
                "It represents thermodynamic stabilisation of a new ordered state."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Biochemistry / polymer chemistry / crystallography",
        ),
        psychology_equivalent=EpistemicLayer(
            claim=(
                "Coagulation maps to the stabilisation and embodiment of a new identity — "
                "the moment when insight becomes character, when therapy becomes lived life. "
                "In positive psychology this corresponds to flourishing and self-actualisation "
                "in the Maslowian sense."
            ),
            tier=3,
            tier_label="T3 — Plausible philosophical analogy",
            source_hint="Positive psychology / Maslow / Jungian individuation",
        ),
        neuroscience_note=EpistemicLayer(
            claim=(
                "Long-term potentiation (LTP) is the cellular mechanism of stable learning: "
                "repeated stimulation of a synapse strengthens it permanently. "
                "Coagulation at the neural level is the stabilisation of new identity "
                "pathways through consistent enactment of new behaviours."
            ),
            tier=1,
            tier_label="T1 — Empirically verified",
            source_hint="Synaptic plasticity / LTP research",
        ),
        human_applications=[
            "Your Philosopher’s Stone is not a thing — it is a quality of being you have earned.",
            "Coagulation requires consistent action: the new self must be lived, not just understood.",
            "Celebrate and acknowledge when you arrive here. Most people never recognise their own gold.",
        ],
        trigger_keywords=[
            "finally", "arrived", "transformation complete", "new chapter", "who I've become",
            "embodying", "living it now", "my true self", "philosopher's stone", "gold",
        ],
    ),
]

# Fast lookup by name
_OPERATION_MAP: dict[str, AlchemicalOperation] = {
    op.name.lower(): op for op in OPERATIONS
}

# Fast lookup by keyword
_KEYWORD_MAP: dict[str, AlchemicalOperation] = {}
for _op in OPERATIONS:
    for _kw in _op.trigger_keywords:
        _KEYWORD_MAP[_kw.lower()] = _op


# ---------------------------------------------------------------------------
# Public API — matches the knowledge_domains bridge interface
# ---------------------------------------------------------------------------

class AlchemyBridge:
    """
    Main interface for the Alchemy → Science bridge.
    GAIA calls this to enrich any conversation touching transformation,
    crisis, growth, chemistry, or psychological change.
    """

    def get_operation(self, name: str) -> Optional[AlchemicalOperation]:
        """Return an operation by its alchemical name (case-insensitive)."""
        return _OPERATION_MAP.get(name.lower())

    def match_from_text(self, text: str) -> Optional[AlchemicalOperation]:
        """
        Scan user text for trigger keywords and return the best-matching
        alchemical stage. Returns None if no match.
        """
        text_lower = text.lower()
        for keyword, op in _KEYWORD_MAP.items():
            if keyword in text_lower:
                return op
        return None

    def all_operations(self) -> list[AlchemicalOperation]:
        """Return all seven operations in sequence."""
        return OPERATIONS

    def build_insight(self, text: str) -> DomainInsight:
        """
        Given a piece of user text, return a DomainInsight ready
        for GAIA to weave into its response.
        """
        op = self.match_from_text(text)

        if op:
            return DomainInsight(
                domain="alchemy",
                topic_matched=op.name,
                operation=op,
                summary=(
                    f"What you’re experiencing resonates with the alchemical stage of "
                    f"{op.name} ({op.latin}). {op.hermetic_meaning}"
                ),
                applications=op.human_applications,
                epistemic_note=(
                    f"Chemistry lens ({op.chemistry_equivalent.tier_label}): "
                    f"{op.chemistry_equivalent.claim[:120]}... | "
                    f"Psychology lens ({op.psychology_equivalent.tier_label}): "
                    f"{op.psychology_equivalent.claim[:120]}..."
                ),
            )
        else:
            return DomainInsight(
                domain="alchemy",
                topic_matched="general",
                operation=None,
                summary=(
                    "The Great Work proceeds through seven stages: Calcination, Dissolution, "
                    "Separation, Conjunction, Fermentation, Distillation, and Coagulation. "
                    "Each maps to a phase of personal and chemical transformation."
                ),
                applications=[
                    "Tell me more about what you’re going through and I can identify your stage."
                ],
                epistemic_note="All alchemical stages are mapped to modern chemistry (T1) and Jungian psychology (T3).",
            )


# Module-level convenience function — matches the query_topic(topic) interface
def query_topic(topic: str) -> DomainInsight:
    """
    Standard knowledge_domains bridge interface.
    Called by GAIA’s atlas.py or gaian_runtime.py to enrich responses.

    Usage:
        from core.knowledge_domains.alchemy import query_topic
        insight = query_topic(user_message)
        # insight.summary, insight.applications, insight.epistemic_note
    """
    bridge = AlchemyBridge()
    return bridge.build_insight(topic)

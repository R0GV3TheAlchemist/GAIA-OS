"""
core/knowledge_domains/psychology_depth.py

Depth Psychology <-> Modern Clinical Psychology Bridge
=======================================================
Maps depth psychology traditions (Jung, Freud, Adler, existential)
to modern empirically-supported therapeutic frameworks and
neuroscience findings.

The old way: treating depth psychology as mysticism.
The new way: recognising it as proto-clinical science that anticipated
many findings now verified by neuroscience, attachment research,
trauma studies, and affective neuroscience.

Sources
-------
- Jung, C.G. — Collected Works (T2 Scholarly)
- Bowlby, J. — Attachment and Loss (T1 Empirical)
- Van der Kolk, B. — The Body Keeps the Score (T1/T2)
- Schwartz, R. — Internal Family Systems (T2)
- Porges, S. — Polyvagal Theory (T1)
- Siegel, D. — Interpersonal Neurobiology (T1/T2)
"""

from dataclasses import dataclass, field
from core.knowledge_domains import EpistemicTier


@dataclass
class PsychologyBridge:
    depth_concept: str
    depth_tradition: str
    modern_equivalent: str
    modern_framework: str
    evidence_tier: EpistemicTier
    clinical_application: str
    neuroscience_basis: str
    neuro_tier: EpistemicTier
    gaia_engine_hook: str
    tags: list[str] = field(default_factory=list)


BRIDGES: list[PsychologyBridge] = [
    PsychologyBridge(
        depth_concept="The Unconscious",
        depth_tradition="Freud (1900) / Jung (collective unconscious)",
        modern_equivalent=(
            "Implicit memory and non-conscious processing. 95% of cognition occurs "
            "below conscious awareness (Bargh & Chartrand, 1999). "
            "The cognitive unconscious (Kihlstrom) is T1 empirical. "
            "Jung’s collective unconscious (shared archetypal patterns) is T2-T3."
        ),
        modern_framework="Cognitive neuroscience / implicit learning research",
        evidence_tier=EpistemicTier.T1_EMPIRICAL,
        clinical_application=(
            "Implicit bias training, trauma-informed care (body holds implicit trauma "
            "memories not accessible to verbal recall), mindfulness as a tool to "
            "observe non-conscious patterns, somatic experiencing."
        ),
        neuroscience_basis=(
            "Amygdala processes emotional threats before cortical awareness. "
            "The basal ganglia runs habitual behaviour without conscious direction. "
            "Declarative vs. procedural memory systems (hippocampus vs. basal ganglia)."
        ),
        neuro_tier=EpistemicTier.T1_EMPIRICAL,
        gaia_engine_hook="memory_store.py + soul_mirror_engine.py",
        tags=["unconscious", "implicit", "Freud", "Jung", "amygdala", "trauma", "memory"],
    ),
    PsychologyBridge(
        depth_concept="Shadow Integration",
        depth_tradition="Jung — the shadow as rejected self",
        modern_equivalent=(
            "Psychological acceptance (ACT: Acceptance and Commitment Therapy). "
            "IFS exiles and firefighters. Self-compassion research (Neff). "
            "Cognitive dissonance reduction. Repression and suppression in emotion regulation."
        ),
        modern_framework="IFS / ACT / Emotion Regulation research",
        evidence_tier=EpistemicTier.T1_EMPIRICAL,
        clinical_application=(
            "Identifying projections (what we criticise in others often lives in us). "
            "Welcoming difficult emotions rather than suppressing them (ACT). "
            "IFS ‘U-turning’ to meet the exiled part. Shadow journaling."
        ),
        neuroscience_basis=(
            "Suppression increases amygdala activation (Gross, 2002). "
            "Acceptance and labeling emotions reduces amygdala reactivity. "
            "Prefrontal-amygdala regulation is the neurological shadow integration pathway."
        ),
        neuro_tier=EpistemicTier.T1_EMPIRICAL,
        gaia_engine_hook="soul_mirror_engine.py (shadow detection + integration)",
        tags=["shadow", "Jung", "IFS", "ACT", "projection", "integration", "acceptance"],
    ),
    PsychologyBridge(
        depth_concept="Individuation",
        depth_tradition="Jung — the lifelong process of becoming fully oneself",
        modern_equivalent=(
            "Self-actualization (Maslow’s hierarchy). Post-traumatic growth (Tedeschi). "
            "Erikson’s psychosocial development stages. "
            "Positive psychology: flourishing, eudaimonia (Seligman). "
            "Adult development theory (Kegan’s orders of mind)."
        ),
        modern_framework="Positive psychology / adult developmental psychology",
        evidence_tier=EpistemicTier.T2_SCHOLARLY,
        clinical_application=(
            "Life review therapy. Narrative therapy (constructing coherent life story). "
            "Meaning-making in existential therapy. "
            "Values clarification in ACT. The ‘good life’ as a clinical goal."
        ),
        neuroscience_basis=(
            "Neuroplasticity supports lifelong development. Default Mode Network "
            "activity correlates with self-referential processing and narrative identity "
            "construction. Coherent autobiographical memory = psychological health."
        ),
        neuro_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="codex_stage_engine.py + growth_arc_engine.py + soul_mirror_engine.py",
        tags=["individuation", "Jung", "Maslow", "growth", "Kegan", "DMN", "narrative"],
    ),
    PsychologyBridge(
        depth_concept="Attachment and the Core Wound",
        depth_tradition="Bowlby / Ainsworth (attachment theory)",
        modern_equivalent=(
            "Adult attachment styles (secure, anxious, avoidant, disorganised). "
            "Interpersonal neurobiology (Siegel): the brain is shaped by relationships. "
            "Polyvagal theory: the ANS carries the history of early relational safety. "
            "Adverse Childhood Experiences (ACEs) research."
        ),
        modern_framework="Attachment theory / interpersonal neurobiology",
        evidence_tier=EpistemicTier.T1_EMPIRICAL,
        clinical_application=(
            "Identifying attachment patterns in current relationships. "
            "Earned secure attachment through therapy. "
            "Co-regulation before self-regulation. "
            "EMDR and somatic experiencing for attachment trauma."
        ),
        neuroscience_basis=(
            "Early attachment shapes the right hemisphere and limbic system development. "
            "Secure attachment is correlated with larger hippocampal volume, better HRV, "
            "and more robust prefrontal-amygdala regulation circuits (Siegel, T1)."
        ),
        neuro_tier=EpistemicTier.T1_EMPIRICAL,
        gaia_engine_hook="bond_arc_engine.py + attachment engine in gaian_runtime.py",
        tags=["attachment", "Bowlby", "ACEs", "secure", "polyvagal", "EMDR", "neurobiology"],
    ),
    PsychologyBridge(
        depth_concept="Trauma and the Body",
        depth_tradition="Janet (dissociation) / Freud (repression) / Reich (body armour)",
        modern_equivalent=(
            "Polyvagal theory (Porges): trauma as ANS dysregulation. "
            "Somatic Experiencing (Levine): trauma stored in the body as incomplete "
            "defensive responses. EMDR (Shapiro, T1 verified): bilateral stimulation "
            "for trauma processing. MDMA-assisted therapy (Phase 3 trials, T1 emerging)."
        ),
        modern_framework="Trauma-informed care / somatic therapies / EMDR",
        evidence_tier=EpistemicTier.T1_EMPIRICAL,
        clinical_application=(
            "Titrated exposure to trauma material within window of tolerance. "
            "Somatic tracking: noticing body sensations without narrative. "
            "Pendulation between activation and settling. "
            "Community and relational healing as trauma treatment."
        ),
        neuroscience_basis=(
            "Trauma reduces hippocampal volume, dysregulates HPA axis, "
            "creates hyperactive amygdala, and impairs prefrontal regulation. "
            "EMDR and somatic therapy show measurable neurological reversal "
            "of these effects (van der Kolk, T1)."
        ),
        neuro_tier=EpistemicTier.T1_EMPIRICAL,
        gaia_engine_hook="regulation_engine.py + subtle_body_engine.py + settling_engine.py",
        tags=["trauma", "EMDR", "somatic", "polyvagal", "body", "ACEs", "MDMA", "healing"],
    ),
    PsychologyBridge(
        depth_concept="The Anima / Animus (Contrasexual Self)",
        depth_tradition="Jung — the inner feminine in men, inner masculine in women",
        modern_equivalent=(
            "Gender psychology: psychological androgyny (Bem’s Sex Role Inventory). "
            "Integration of traditionally gendered qualities regardless of gender identity. "
            "Modern framing: every person contains all qualities — the work is "
            "integrating what was split off by cultural gender conditioning."
        ),
        modern_framework="Gender psychology / contrasexual integration",
        evidence_tier=EpistemicTier.T2_SCHOLARLY,
        clinical_application=(
            "Men integrating emotional attunement and relational sensitivity. "
            "Women integrating assertion, direction, and autonomous agency. "
            "Non-binary and trans individuals often pioneer this integration consciously."
        ),
        neuroscience_basis=(
            "Gender differences in brain structure are smaller than popular culture "
            "suggests and highly overlapping (Rippon, 2019). "
            "Psychological androgyny correlates with higher wellbeing, resilience, "
            "and creativity (Bem, multiple studies)."
        ),
        neuro_tier=EpistemicTier.T2_SCHOLARLY,
        gaia_engine_hook="contrasexual psychology bridge in gaian_runtime.py personality",
        tags=["anima", "animus", "Jung", "gender", "androgyny", "integration", "Bem"],
    ),
]


SUMMARY = (
    "Depth psychology anticipated modern neuroscience by 50-100 years. "
    "The unconscious (Freud/Jung) = implicit cognition (T1 empirical). "
    "Shadow integration = ACT/IFS emotion regulation (T1). "
    "Attachment theory = interpersonal neurobiology (T1). "
    "Trauma body storage = polyvagal theory + EMDR (T1). "
    "GAIA’s psychological engines are grounded in this full bridge layer."
)

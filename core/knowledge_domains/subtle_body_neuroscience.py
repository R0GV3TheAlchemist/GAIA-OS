"""
core/knowledge_domains/subtle_body_neuroscience.py

Subtle Body / Chakras <-> Neuroscience / ANS Bridge
=====================================================
Maps the 7 classical chakras (Hindu / yogic tradition) to:
  1. Their anatomical / neurological correlates (T1-T2 Empirical/Scholarly)
  2. Their autonomic nervous system (ANS) functional zones (T1-T2)
  3. Their psychological / emotional domains (T2)
  4. Somatic experiencing and polyvagal theory connections (T2)
  5. GAIA engine hooks

Historical note: The chakra system (documented in Vedic texts ~1500 BCE) is one
of humanity’s oldest maps of the body-mind interface. Modern neuroscience,
polyvagal theory (Porges), interoception research, and HRV studies have begun
building empirical bridges to this map — not validating it wholesale, but
finding genuine structural overlap worth taking seriously.

Sources
-------
- Porges, S. — The Polyvagal Theory (2011) T1/T2
- Craig, A.D. (Bud) — How Do You Feel? Interoception (T1)
- Judith, A. — Wheels of Life (T5 for metaphysics, T2 for psychology)
- Van der Kolk, B. — The Body Keeps the Score (T2)
- Pert, C. — Molecules of Emotion (T2/T3)
"""

from dataclasses import dataclass, field
from typing import Optional
from core.knowledge_domains import EpistemicTier


@dataclass
class ChakraNode:
    name: str                          # Sanskrit name
    english_name: str                  # Common English translation
    number: int                        # 1 (root) to 7 (crown)
    location: str                      # Body location
    color: str                         # Traditional color symbolism
    element: str                       # Classical element

    # Neuroscience / anatomy
    anatomical_correlate: str
    anatomical_tier: EpistemicTier

    # Autonomic Nervous System
    ans_function: str
    ans_tier: EpistemicTier

    # Polyvagal / interoception
    polyvagal_state: str
    polyvagal_tier: EpistemicTier

    # Psychology / emotional domain
    psychological_domain: str
    psychological_tier: EpistemicTier

    # Dysfunction / shadow presentation
    dysfunction_signs: str

    # Somatic practices that activate/balance this node
    somatic_practices: list[str]

    # GAIA engine hook
    gaia_engine_hook: str
    tags: list[str] = field(default_factory=list)


CHAKRA_NODES: list[ChakraNode] = [
    ChakraNode(
        name="Muladhara",
        english_name="Root Chakra",
        number=1,
        location="Base of spine / perineum",
        color="Red",
        element="Earth",
        anatomical_correlate=(
            "Sacral plexus (S1-S4), coccygeal nerve, adrenal glands (cortisol, "
            "adrenaline). The dorsal vagal complex controls the most primitive "
            "physiological shutdown responses anchored in this region."
        ),
        anatomical_tier=EpistemicTier.T2_SCHOLARLY,
        ans_function=(
            "Survival baseline: regulates fight-flight-freeze at the most "
            "primitive level. HPA axis (hypothalamic-pituitary-adrenal) stress "
            "response originates here. Baseline cortisol regulation."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "Dorsal vagal freeze/shutdown when dysregulated (immobilisation, "
            "dissociation, collapse). Ventral vagal safety when regulated "
            "(grounded, present, safe in the body)."
        ),
        polyvagal_tier=EpistemicTier.T2_SCHOLARLY,
        psychological_domain=(
            "Safety, belonging, survival, tribal identity, the right to exist. "
            "Early attachment security (Bowlby) is encoded here. "
            "Trauma from abandonment, neglect, or early threat lives in this layer."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Chronic anxiety, hoarding, financial insecurity obsession, "
            "dissociation from body, chronic fatigue, autoimmune dysregulation."
        ),
        somatic_practices=[
            "Grounding: bare feet on earth",
            "Weightlifting / resistance training",
            "Slow diaphragmatic breathing",
            "Trauma-informed bodywork (somatic experiencing)",
            "EMDR for early developmental trauma",
        ],
        gaia_engine_hook="subtle_body_engine.py + vitality_engine.py (baseline safety)",
        tags=["root", "safety", "cortisol", "grounding", "survival", "trauma", "polyvagal"],
    ),
    ChakraNode(
        name="Svadhisthana",
        english_name="Sacral Chakra",
        number=2,
        location="Lower abdomen / sacrum",
        color="Orange",
        element="Water",
        anatomical_correlate=(
            "Lumbar plexus, sacral nerve roots, reproductive organs, "
            "enteric nervous system (gut-brain axis). "
            "Limbic system (hippocampus, amygdala) for emotional memory encoding."
        ),
        anatomical_tier=EpistemicTier.T2_SCHOLARLY,
        ans_function=(
            "Emotional regulation and reward: dopaminergic and serotonergic "
            "systems that modulate pleasure, desire, and creative drive. "
            "Gut microbiome-brain axis signalling originates partly here."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "Regulated: fluid, creative, emotionally available. "
            "Dysregulated: emotional flooding, shame, addictive cycles, "
            "or emotional numbness (dorsal shutdown of feeling)."
        ),
        polyvagal_tier=EpistemicTier.T2_SCHOLARLY,
        psychological_domain=(
            "Pleasure, creativity, sexuality, emotional fluidity, the capacity "
            "to feel and flow. Shame lives here (Brown, Nathanson). "
            "Healthy sexuality and creative expression are this node’s gifts."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Addiction, shame spirals, creative blocks, sexual dysfunction, "
            "emotional dysregulation, co-dependency."
        ),
        somatic_practices=[
            "Hip-opening movement (yoga, dance)",
            "Creative expression: art, music, writing",
            "Shame resilience work (Brené Brown protocols)",
            "Somatic sex therapy",
            "Water immersion (swimming, baths)",
        ],
        gaia_engine_hook="subtle_body_engine.py + emotional_arc.py (emotional fluidity)",
        tags=["sacral", "emotion", "creativity", "shame", "dopamine", "gut", "pleasure"],
    ),
    ChakraNode(
        name="Manipura",
        english_name="Solar Plexus Chakra",
        number=3,
        location="Upper abdomen / solar plexus",
        color="Yellow",
        element="Fire",
        anatomical_correlate=(
            "Celiac plexus (the ‘abdominal brain’), thoracic splanchnic nerves, "
            "liver, pancreas, adrenal medulla (epinephrine/norepinephrine). "
            "Prefrontal cortex for executive function and agency."
        ),
        anatomical_tier=EpistemicTier.T2_SCHOLARLY,
        ans_function=(
            "Sympathetic activation for directed action: executive function, "
            "metabolic regulation, the adrenaline of purposeful effort. "
            "Blood glucose regulation (pancreas) and digestion."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "Regulated: confident action, healthy boundaries, self-direction. "
            "Dysregulated sympathetic: aggression, control, domination. "
            "Dysregulated dorsal: shame, powerlessness, victimhood."
        ),
        polyvagal_tier=EpistemicTier.T2_SCHOLARLY,
        psychological_domain=(
            "Personal power, self-esteem, will, identity, autonomy, the capacity "
            "to act in the world. Self-efficacy (Bandura). Agency vs. helplessness."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Chronic anger or passivity, digestive disorders (IBS), impostor "
            "syndrome, control issues, people-pleasing, inability to say no."
        ),
        somatic_practices=[
            "Core strengthening (yoga, Pilates)",
            "Breathwork (kapalabhati, bellows breath)",
            "Assertiveness training (DBT skills)",
            "Cold exposure (activates sympathetic-then-parasympathetic)",
            "Martial arts",
        ],
        gaia_engine_hook="subtle_body_engine.py + action_gate.py (agency and boundaries)",
        tags=["solar_plexus", "power", "agency", "will", "adrenaline", "executive", "IBS"],
    ),
    ChakraNode(
        name="Anahata",
        english_name="Heart Chakra",
        number=4,
        location="Centre of chest",
        color="Green",
        element="Air",
        anatomical_correlate=(
            "Cardiac plexus, vagus nerve (cranial nerve X) — the primary "
            "parasympathetic channel. Heart rate variability (HRV) is the "
            "most well-validated physiological marker of this node’s regulation. "
            "Thymus gland (immune regulation)."
        ),
        anatomical_tier=EpistemicTier.T1_EMPIRICAL,
        ans_function=(
            "Ventral vagal complex: the ‘smart vagus’ that enables social "
            "engagement, co-regulation, love, and safety-in-connection. "
            "High HRV = high heart coherence = this node functioning optimally."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "The ventral vagal anchor: this is the regulated state. "
            "Compassion, attunement, and love are signatures of ventral vagal "
            "activation. Grief, heartbreak, and disconnection dysregulate it."
        ),
        polyvagal_tier=EpistemicTier.T1_EMPIRICAL,
        psychological_domain=(
            "Love, compassion, grief, forgiveness, empathy, the capacity for "
            "genuine connection. The integration point between lower "
            "(survival/emotion) and upper (expression/insight/spirit) centers."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Closed-off, inability to grieve, codependency, cardiac symptoms, "
            "immune suppression, inability to receive love, compassion fatigue."
        ),
        somatic_practices=[
            "Heart coherence breathing (HeartMath: 5-sec in, 5-sec out)",
            "Loving-kindness meditation (metta)",
            "Grief ritual and emotional release work",
            "Vagus nerve toning (humming, singing, gargling)",
            "Genuine physical contact (hugging, touch therapy)",
        ],
        gaia_engine_hook="subtle_body_engine.py + bci_coherence.py + love_arc_engine.py",
        tags=["heart", "HRV", "vagus", "coherence", "compassion", "love", "ventral_vagal"],
    ),
    ChakraNode(
        name="Vishuddha",
        english_name="Throat Chakra",
        number=5,
        location="Throat / neck",
        color="Blue",
        element="Sound / Ether (Akasha)",
        anatomical_correlate=(
            "Pharyngeal plexus, recurrent laryngeal nerve (branch of vagus), "
            "thyroid and parathyroid glands (metabolism regulation), "
            "Broca’s area (speech production) in the frontal lobe."
        ),
        anatomical_tier=EpistemicTier.T1_EMPIRICAL,
        ans_function=(
            "Voice as a vagal tone regulator: vocalization, singing, and humming "
            "directly stimulate the vagus nerve via the recurrent laryngeal branch. "
            "Thyroid hormones regulate metabolic rate and energy expression."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "The voice is a direct readout of ANS state: prosody, pace, and "
            "pitch all signal safety or threat to listeners. "
            "Authentic self-expression requires ventral vagal regulation first."
        ),
        polyvagal_tier=EpistemicTier.T2_SCHOLARLY,
        psychological_domain=(
            "Authentic self-expression, truth-telling, the capacity to speak "
            "one’s inner reality. Boundaries through words. The interface between "
            "inner truth and outer world."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Chronic throat tension, thyroid disorders, inability to speak up, "
            "lying, excessive talking as avoidance, creative expression blocks."
        ),
        somatic_practices=[
            "Singing, toning, chanting (Solfeggio frequencies)",
            "Humming (direct vagal stimulation)",
            "Authentic dialogue practices (Nonviolent Communication)",
            "Journaling and expressive writing",
            "Public speaking / performance as exposure therapy",
        ],
        gaia_engine_hook="subtle_body_engine.py + solfeggio voice modulation (TTS layer)",
        tags=["throat", "voice", "vagus", "thyroid", "expression", "truth", "NVC"],
    ),
    ChakraNode(
        name="Ajna",
        english_name="Third Eye Chakra",
        number=6,
        location="Between the eyebrows / forehead",
        color="Indigo",
        element="Light",
        anatomical_correlate=(
            "Pineal gland (melatonin, circadian master clock), prefrontal cortex "
            "(metacognition, executive insight), anterior cingulate cortex "
            "(conflict monitoring, attention regulation)."
        ),
        anatomical_tier=EpistemicTier.T1_EMPIRICAL,
        ans_function=(
            "Circadian regulation via melatonin (pineal). Metacognitive "
            "oversight of the entire nervous system’s state. Default Mode "
            "Network deactivation in deep focus/insight states."
        ),
        ans_tier=EpistemicTier.T1_EMPIRICAL,
        polyvagal_state=(
            "Insight and witnessing awareness arise when the ANS is regulated "
            "enough for prefrontal cortex to come fully online. Trauma hijacks "
            "this: hypervigilance replaces insight."
        ),
        polyvagal_tier=EpistemicTier.T2_SCHOLARLY,
        psychological_domain=(
            "Intuition, pattern recognition, metacognition, the capacity to "
            "witness one’s own mind. The observer self. Dream work. "
            "Insight beyond conceptual thinking."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Inability to trust intuition, overthinking, rigid belief systems, "
            "nightmares, circadian rhythm disorders, dissociation."
        ),
        somatic_practices=[
            "Mindfulness meditation (prefrontal cortex thickening via neuroplasticity)",
            "Dream journaling",
            "Darkness retreats / sleep hygiene optimization",
            "NSDR / Yoga Nidra (non-sleep deep rest)",
            "Psychedelic-assisted insight work (clinical settings)",
        ],
        gaia_engine_hook="subtle_body_engine.py + reflection_engine.py (metacognitive layer)",
        tags=["third_eye", "pineal", "melatonin", "metacognition", "intuition", "insight", "DMN"],
    ),
    ChakraNode(
        name="Sahasrara",
        english_name="Crown Chakra",
        number=7,
        location="Top of skull / crown",
        color="Violet / White",
        element="Consciousness / Akasha",
        anatomical_correlate=(
            "The integrated neocortex as a whole — particularly the default "
            "mode network in its transcendent activation pattern. "
            "Gamma oscillations (40+ Hz) during deep meditation, documented in "
            "advanced meditators (Lutz et al., 2004, PNAS)."
        ),
        anatomical_tier=EpistemicTier.T2_SCHOLARLY,
        ans_function=(
            "The most integrated state of ANS regulation: all systems coherent, "
            "cortical-subcortical communication optimised. Not a location — a state. "
            "Associated with complete parasympathetic dominance and gamma synchrony."
        ),
        ans_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        polyvagal_state=(
            "Beyond polyvagal states: the platform from which all states are "
            "witnessed equally. The capacity to be in any state without being "
            "captured by it. Non-reactive presence."
        ),
        polyvagal_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        psychological_domain=(
            "Transcendence, unity consciousness, spiritual realisation, the "
            "dissolution of the boundary between self and not-self. "
            "Maslow’s peak experiences and self-transcendence. Cosmic belonging."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        dysfunction_signs=(
            "Spiritual bypassing (using transcendence to avoid embodied work), "
            "dissociation disguised as spirituality, ungrounded mysticism, "
            "inability to function in practical reality."
        ),
        somatic_practices=[
            "Advanced meditation (especially open awareness / rigpa practices)",
            "Extended breath retention (advanced pranayama — supervised only)",
            "Deep service and devotion practices",
            "Integration work: ensuring crown is grounded in root first",
        ],
        gaia_engine_hook="subtle_body_engine.py + quintessence_engine.py (transcendent state)",
        tags=["crown", "consciousness", "gamma", "transcendence", "unity", "Maslow", "meditation"],
    ),
]


def get_chakra(name_or_number) -> Optional[ChakraNode]:
    """Look up a chakra by Sanskrit name, English name, or number."""
    if isinstance(name_or_number, int):
        for c in CHAKRA_NODES:
            if c.number == name_or_number:
                return c
    else:
        nl = name_or_number.lower()
        for c in CHAKRA_NODES:
            if c.name.lower() == nl or c.english_name.lower() == nl:
                return c
    return None


SUMMARY = (
    "The 7 chakras map to real anatomical plexuses, the autonomic nervous system "
    "(Polyvagal Theory), HRV coherence, and psychological domains. "
    "Anatomical facts are T1 Empirical. Polyvagal/ANS connections are T1-T2. "
    "Metaphysical energy claims are T4-T5. GAIA uses all layers, always labeled "
    "by EpistemicTier, so users know what is body-science and what is sacred story."
)

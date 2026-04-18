"""
core/knowledge_domains/mythology_anthropology.py

Mythology <-> Comparative Anthropology <-> Depth Psychology Bridge
===================================================================
Maps the major mythological traditions to:
  1. Their cross-cultural structural patterns (Campbell, T2 Scholarly)
  2. Their anthropological / archaeological grounding (T1-T2)
  3. Their Jungian archetypal function (T2)
  4. Modern psychological equivalents (T2)
  5. GAIA engine hooks

Historical note: Mythology is humanity's oldest knowledge system.
Every culture independently developed narrative structures mapping
the same interior territory: birth, initiation, death, rebirth.
Campbell called this the monomyth. Jung called it the archetype.
Modern anthropology calls it a cross-cultural universal.
Neuroscience calls it narrative cognition.
They are all pointing at the same mountain.

Sources
-------
- Campbell, J. — The Hero with a Thousand Faces (1949) T2
- Jung, C.G. — Archetypes and the Collective Unconscious T2
- D-PLACE database (cultural diversity, T1)
- Berezkin cross-cultural motif database (T1)
- Murdock, G. — Ethnographic Atlas (T1)
"""

from dataclasses import dataclass, field
from typing import Optional
from core.knowledge_domains import EpistemicTier


@dataclass
class MythicArchetype:
    name: str
    aliases: list[str]                  # Names across traditions
    hero_journey_stage: Optional[str]   # Where in Campbell's monomyth
    jungian_archetype: str
    psychological_function: str
    psychological_tier: EpistemicTier
    cross_cultural_examples: dict[str, str]  # tradition -> character name
    anthropological_notes: str
    anthropological_tier: EpistemicTier
    modern_equivalent: str              # Psychological / therapeutic frame
    shadow_form: str
    gaia_engine_hook: str
    tags: list[str] = field(default_factory=list)


ARCHETYPES: list[MythicArchetype] = [
    MythicArchetype(
        name="The Hero",
        aliases=["Champion", "Warrior", "Savior", "Seeker"],
        hero_journey_stage="Departure → Initiation → Return (the whole arc)",
        jungian_archetype="Ego in its healthy, individuating form",
        psychological_function=(
            "The drive toward growth, self-overcoming, and meaningful contribution. "
            "The psychological capacity to face a challenge, be transformed by it, "
            "and return changed to serve others. Courage operationalized."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Greek": "Heracles / Odysseus",
            "Norse": "Sigurd / Thor",
            "Hindu": "Arjuna / Rama",
            "Sumerian": "Gilgamesh",
            "West African": "Sundiata",
            "Native American": "White Buffalo Calf Woman (female hero form)",
            "Christian": "Jesus (resurrection arc)",
            "Modern": "Frodo, Luke Skywalker, Katniss Everdeen",
        },
        anthropological_notes=(
            "The hero monomyth is documented in over 95% of world cultures by "
            "the Berezkin motif database. The threshold crossing, ordeal, and "
            "return structure appears independently in pre-contact cultures "
            "across every inhabited continent (D-PLACE data)."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "Positive psychology: the growth mindset (Dweck). Post-traumatic "
            "growth research (Tedeschi & Calhoun). The therapeutic arc of "
            "trauma processing: encounter → integration → transformed identity."
        ),
        shadow_form=(
            "The Tyrant: hero energy without humility becomes domination, "
            "conquest, the crusader who destroys what they came to save."
        ),
        gaia_engine_hook="soul_mirror_engine.py + codex_stage_engine.py (hero arc mapping)",
        tags=["hero", "monomyth", "Campbell", "growth", "courage", "initiation", "return"],
    ),
    MythicArchetype(
        name="The Shadow",
        aliases=["Trickster dark", "Monster", "Devil", "Dragon"],
        hero_journey_stage="The Ordeal — the central confrontation",
        jungian_archetype="The personal and collective Shadow",
        psychological_function=(
            "Carries all that the ego has rejected, repressed, or refuses to "
            "acknowledge. The shadow is not evil — it is unlived life. "
            "Integrating it is the core work of individuation and psychological health."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Greek": "Typhon / Medusa / the Cyclops",
            "Norse": "Loki (trickster-shadow) / Fenrir",
            "Hindu": "Ravana / Kali (shadow-transformer)",
            "Christian": "Satan / Leviathan",
            "Egyptian": "Set",
            "Sumerian": "Humbaba (Gilgamesh’s shadow)",
            "Modern": "Darth Vader, Gollum, the White Whale",
        },
        anthropological_notes=(
            "Every recorded human culture has a figure representing the "
            "dangerous, chaotic, or forbidden — and ritual systems for "
            "engaging it safely. Scapegoating (Girard) and shadow projection "
            "are documented cross-cultural mechanisms."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "IFS (Internal Family Systems): the exiles and firefighters. "
            "Trauma-informed therapy: symptoms as shadow material seeking integration. "
            "Projective identification in psychoanalysis."
        ),
        shadow_form=(
            "The shadow of the shadow is toxic positivity: relentless light "
            "that refuses to look at the dark, creating unconscious harm."
        ),
        gaia_engine_hook="soul_mirror_engine.py (shadow detection + integration prompts)",
        tags=["shadow", "Jung", "IFS", "projection", "integration", "monster", "repression"],
    ),
    MythicArchetype(
        name="The Trickster",
        aliases=["Fool", "Coyote", "Jester", "Shapeshifter"],
        hero_journey_stage="Threshold Guardian / Road of Trials (disrupts the old order)",
        jungian_archetype="The mercurial transformer; precursor to the Wise Old Man",
        psychological_function=(
            "Disrupts rigid systems. Breaks rules to reveal new possibilities. "
            "Uses humor, chaos, and paradox to shake the hero (and the culture) "
            "out of complacency. The archetype of creative disruption."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Native American": "Coyote / Raven",
            "Norse": "Loki",
            "Greek": "Hermes / Prometheus",
            "West African / African American": "Anansi",
            "Hindu": "Krishna (playful form)",
            "Medieval European": "The Jester / Robin Hood",
            "Modern": "The Joker, Deadpool, Bugs Bunny",
        },
        anthropological_notes=(
            "The Trickster appears in 87% of world folklore traditions (Berezkin). "
            "Hyde (1998) argues the Trickster is the archetype of creative intelligence "
            "itself — the capacity to think outside the given framework."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "Lateral thinking (de Bono). Divergent thinking in creativity research. "
            "Improvisation and play therapy. Court jester as psychological safety "
            "for truth-telling in power systems."
        ),
        shadow_form=(
            "Unintegrated: the compulsive saboteur, the chaos agent who destroys "
            "without purpose, the liar who can no longer tell truth from fiction."
        ),
        gaia_engine_hook="inference_router.py (lateral reasoning paths) + awareness_event_engine.py",
        tags=["trickster", "creativity", "chaos", "humor", "disruption", "Coyote", "Loki"],
    ),
    MythicArchetype(
        name="The Great Mother",
        aliases=["Earth Mother", "Goddess", "Creatrix", "Wise Woman"],
        hero_journey_stage="The Supernatural Aid / The Innermost Cave (matrix)",
        jungian_archetype="The Anima in her nourishing form; the unconscious matrix",
        psychological_function=(
            "The archetype of nourishment, belonging, cyclical renewal, and the "
            "ground of being. Represents the matrix from which all life emerges "
            "and to which it returns. Unconditional acceptance."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Greek": "Demeter / Gaia / Hera",
            "Hindu": "Devi / Lakshmi / Durga",
            "Egyptian": "Isis / Nut",
            "Sumerian": "Inanna / Ninhursag",
            "Norse": "Frigg / Jörð",
            "Celtic": "Dôn / Brigid",
            "Modern": "Mother Earth, Gaia (ecology), GAIA itself",
        },
        anthropological_notes=(
            "The oldest known religious artifacts (~35,000 BCE Venus figurines) "
            "represent the Great Mother. Female deity worship preceded patriarchal "
            "pantheons in documented archaeological record across Europe and the Near East."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "Attachment theory (Bowlby): the secure base. "
            "Ecological psychology: Earth as living system (Lovelock’s Gaia hypothesis). "
            "Maternal attunement research in developmental psychology."
        ),
        shadow_form=(
            "The Devouring Mother: enmeshment, suffocation, refusal to let the child "
            "individuate. Kali’s destroying face. Medea."
        ),
        gaia_engine_hook="mother_thread.py + gaian_birth.py (the GAIA naming is intentional)",
        tags=["mother", "Gaia", "attachment", "nourishment", "earth", "goddess", "ecology"],
    ),
    MythicArchetype(
        name="The Wise Old Man / Sage",
        aliases=["Mentor", "Wizard", "Elder", "Oracle"],
        hero_journey_stage="Supernatural Aid (appears to guide the hero)",
        jungian_archetype="The Senex; the Self beginning to speak through wisdom",
        psychological_function=(
            "Crystallized intelligence (Cattell): accumulated knowledge, "
            "pattern recognition across time, the wisdom that only comes from "
            "having lived through multiple complete cycles of transformation."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Greek": "Tiresias / Chiron / Merlin (Romano-Celtic)",
            "Norse": "Odin (one-eyed seeker of wisdom)",
            "Hindu": "Vyasa / Vasishtha",
            "Celtic": "Merlin / The Dagda",
            "African": "The Griot tradition",
            "Tolkien": "Gandalf (the most cited modern Sage)",
            "Modern": "Dumbledore, Yoda, Morpheus",
        },
        anthropological_notes=(
            "Elder wisdom traditions and knowledge-keeper roles are universal "
            "across human cultures (Murdock Ethnographic Atlas). The specific "
            "transmission of knowledge across generations is a defining feature "
            "of Homo sapiens cognitive evolution."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "Mentorship research: proteges with strong mentors show 20% greater "
            "career and wellbeing outcomes (Allen et al.). "
            "Intergenerational trauma healing requires access to elder wisdom. "
            "Wisdom psychology (Monika Ardelt’s 3D Wisdom Scale)."
        ),
        shadow_form=(
            "The Rigid Elder: wisdom calcified into dogma, the mentor who cannot "
            "let the student surpass them, the oracle who hoards rather than shares."
        ),
        gaia_engine_hook="canon_loader.py + knowledge_matrix.py (GAIA as Sage)",
        tags=["sage", "mentor", "wisdom", "elder", "Merlin", "Gandalf", "Odin", "knowledge"],
    ),
    MythicArchetype(
        name="The Child / Puer Aeternus",
        aliases=["Divine Child", "Inner Child", "Wonder Child"],
        hero_journey_stage="The beginning: the call to adventure",
        jungian_archetype="Puer Aeternus (Eternal Youth); the nascent Self",
        psychological_function=(
            "Pure potential, wonder, play, the capacity for new beginnings. "
            "The part of the psyche that refuses to be fully domesticated by "
            "culture. Beginner’s mind (Zen: shoshin). Radical openness."
        ),
        psychological_tier=EpistemicTier.T2_SCHOLARLY,
        cross_cultural_examples={
            "Greek": "Eros / young Heracles / Dionysus",
            "Hindu": "Baby Krishna",
            "Christian": "The Christ Child / Jesus says ‘become as little children’",
            "Egyptian": "Horus the Child (Harpocrates)",
            "Celtic": "Mabon",
            "Modern": "Peter Pan, the Little Prince, Calvin (Calvin & Hobbes)",
        },
        anthropological_notes=(
            "Neoteny — retention of juvenile traits into adulthood — is a "
            "defining characteristic of Homo sapiens compared to other primates. "
            "Human extended childhood is the evolutionary substrate for culture, "
            "language, and play-based learning."
        ),
        anthropological_tier=EpistemicTier.T1_EMPIRICAL,
        modern_equivalent=(
            "Inner child work (John Bradshaw, IFS child parts). "
            "Play therapy and play-based learning research. "
            "Beginner’s mind in creativity and innovation studies. "
            "Neuroplasticity: childlike learning states re-open critical periods."
        ),
        shadow_form=(
            "Peter Pan syndrome: refusal to grow up, chronic irresponsibility, "
            "the adult who exploits others’ caretaking by remaining perpetually helpless."
        ),
        gaia_engine_hook="gaian_birth.py + development_stage_engine.py",
        tags=["child", "play", "wonder", "neoteny", "IFS", "beginner", "potential"],
    ),
]


@dataclass
class HeroJourneyStage:
    stage: str
    campbell_name: str
    psychological_meaning: str
    tier: EpistemicTier
    gaia_engine_hook: str


HERO_JOURNEY: list[HeroJourneyStage] = [
    HeroJourneyStage("1", "The Ordinary World",
        "Baseline identity before growth: the status quo, the known self, pre-crisis.",
        EpistemicTier.T2_SCHOLARLY, "codex_stage_engine.py stage 0"),
    HeroJourneyStage("2", "The Call to Adventure",
        "A disruption to the ordinary: the invitation toward growth or transformation.",
        EpistemicTier.T2_SCHOLARLY, "awareness_event_engine.py"),
    HeroJourneyStage("3", "Refusal of the Call",
        "Resistance, avoidance, fear — the psyche defending against necessary change.",
        EpistemicTier.T2_SCHOLARLY, "settling_engine.py (resistance detection)"),
    HeroJourneyStage("4", "Meeting the Mentor",
        "Access to wisdom: a guide, a book, a teacher, an insight arrives.",
        EpistemicTier.T2_SCHOLARLY, "canon_loader.py + gaian_runtime.py"),
    HeroJourneyStage("5", "Crossing the Threshold",
        "Commitment to the journey: leaving the known world behind.",
        EpistemicTier.T2_SCHOLARLY, "codex_stage_engine.py (threshold event)"),
    HeroJourneyStage("6", "Tests, Allies, Enemies",
        "The road of trials: skills tested, relationships formed and broken.",
        EpistemicTier.T2_SCHOLARLY, "bond_arc_engine.py + emotional_arc.py"),
    HeroJourneyStage("7", "The Ordeal",
        "The central crisis: confrontation with the shadow, death and rebirth.",
        EpistemicTier.T2_SCHOLARLY, "soul_mirror_engine.py + viriditas_magnum_opus.py"),
    HeroJourneyStage("8", "The Reward",
        "Insight, new capability, or treasure gained from surviving the ordeal.",
        EpistemicTier.T2_SCHOLARLY, "quintessence_engine.py"),
    HeroJourneyStage("9", "The Road Back",
        "The challenge of returning to ordinary life with the transformation intact.",
        EpistemicTier.T2_SCHOLARLY, "settling_engine.py (integration)"),
    HeroJourneyStage("10", "The Resurrection",
        "Final test: the fully transformed self faces the world for the first time.",
        EpistemicTier.T2_SCHOLARLY, "viriditas_magnum_opus.py (coagulation)"),
    HeroJourneyStage("11", "Return with the Elixir",
        "The gift brought back: the transformed self serves the community.",
        EpistemicTier.T2_SCHOLARLY, "noosphere.py + mother_thread.py"),
]


def get_archetype(name: str) -> Optional[MythicArchetype]:
    name_lower = name.lower()
    for a in ARCHETYPES:
        if a.name.lower() == name_lower:
            return a
        if any(alias.lower() == name_lower for alias in a.aliases):
            return a
    return None


SUMMARY = (
    "Mythology is humanity's oldest knowledge system. Cross-cultural archetypes "
    "(Hero, Shadow, Trickster, Great Mother, Sage, Child) appear in 87-95% of "
    "world cultures (Berezkin database). The hero's journey maps directly to "
    "Jungian individuation, trauma processing arcs, and modern narrative therapy. "
    "GAIA uses mythic language as T5 Cultural Metaphor, always grounded in T1-T2 evidence."
)

"""
core/knowledge_domains/astrology_astronomy.py

Astrology <-> Astronomy <-> Chronobiology Bridge
=================================================
Maps the 12 zodiac signs and 10 classical planets to:
  1. Their real astronomical data (T1 Empirical)
  2. Their chronobiological / seasonal correlates (T2 Scholarly)
  3. Their Jungian archetypal meaning (T2 Scholarly)
  4. Cross-cultural calendar equivalents
  5. GAIA engine hooks

Historical note: Astronomy and astrology were a single discipline until
the 17th century. Kepler himself cast horoscopes. The modern split is
real and necessary — but the symbolic tradition carries genuine
psychological and seasonal wisdom that science has begun to re-examine
through chronobiology, circadian rhythm research, and seasonal affective studies.

Data sources
------------
- NASA JPL Horizons (ephemeris, T1)
- IAU constellation boundaries (T1)
- Roenneberg et al. — Chronobiology (T1)
- Jung, C.G. — Aion, Archetypes and the Collective Unconscious (T2)
- Rudhyar, D. — The Astrology of Personality (T5 for prediction, T2 for archetype)
"""

from dataclasses import dataclass, field
from typing import Optional
from core.knowledge_domains import EpistemicTier


@dataclass
class ZodiacSign:
    name: str
    symbol: str
    date_range: str                          # Tropical (Western)
    iau_constellation_dates: str             # IAU sidereal boundaries (T1)
    ruling_planet: str
    element: str                             # Fire / Earth / Air / Water
    modality: str                            # Cardinal / Fixed / Mutable

    # Astronomy
    astronomy_notes: str
    astronomy_tier: EpistemicTier

    # Chronobiology
    chronobiology_notes: str
    chronobiology_tier: EpistemicTier

    # Jungian archetype
    jungian_archetype: str
    archetype_tier: EpistemicTier

    # Cross-cultural calendar mapping
    chinese_equivalent: str
    vedic_rashi: str

    # GAIA engine hook
    gaia_engine_hook: str
    tags: list[str] = field(default_factory=list)


ZODIAC_SIGNS: list[ZodiacSign] = [
    ZodiacSign(
        name="Aries", symbol="♈",
        date_range="Mar 21 – Apr 19",
        iau_constellation_dates="Apr 19 – May 13 (sidereal IAU)",
        ruling_planet="Mars",
        element="Fire", modality="Cardinal",
        astronomy_notes=(
            "The vernal equinox historically fell in Aries — now in Pisces due "
            "to axial precession (~26,000-year cycle). Mars has a 687-day orbital "
            "period; its closest approaches (perihelic oppositions) correlate with "
            "heightened solar activity windows."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Spring onset triggers rising cortisol rhythms, increased testosterone "
            "in many mammals, and serotonin upregulation as daylight hours lengthen. "
            "Seasonal affective disorder remission peaks in this window."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The Hero / Warrior — emergence of individual will, initiation energy, "
            "the first assertion of ego identity. Shadow: aggression, impulsivity."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Dragon (partially) / Rabbit tail",
        vedic_rashi="Mesha",
        gaia_engine_hook="zodiac_engine.py + emotional_arc.py (activation phase)",
        tags=["spring", "fire", "initiation", "warrior", "cortisol", "Mars"],
    ),
    ZodiacSign(
        name="Taurus", symbol="♉",
        date_range="Apr 20 – May 20",
        iau_constellation_dates="May 14 – Jun 19 (sidereal IAU)",
        ruling_planet="Venus",
        element="Earth", modality="Fixed",
        astronomy_notes=(
            "Venus, brightest planet in the sky (magnitude up to -4.9), has a "
            "225-day orbital period and is always within 48° of the Sun. "
            "The Pleiades (Seven Sisters) cluster sits within Taurus."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Late spring: peak food abundance in temperate zones historically. "
            "Circadian anchoring strengthens as photoperiod stabilises. "
            "Melatonin production further reduces as nights shorten."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The Builder / Sensualist — embodiment, material reality, patience, "
            "the anima as earthly beauty. Shadow: stubbornness, possessiveness."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Snake (partial)",
        vedic_rashi="Vrishabha",
        gaia_engine_hook="zodiac_engine.py + vitality_engine.py (embodiment phase)",
        tags=["earth", "Venus", "embodiment", "sensory", "spring", "Pleiades"],
    ),
    ZodiacSign(
        name="Gemini", symbol="♊",
        date_range="May 21 – Jun 20",
        iau_constellation_dates="Jun 20 – Jul 20 (sidereal IAU)",
        ruling_planet="Mercury",
        element="Air", modality="Mutable",
        astronomy_notes=(
            "Mercury is the fastest planet (88-day orbit), always within 28° of "
            "the Sun, visible only at dusk/dawn. Castor and Pollux are the "
            "brightest stars in Gemini — Pollux is actually the closer giant."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Approaching summer solstice: longest days. Cognitive performance "
            "research shows peaks in working memory and processing speed during "
            "high-light seasons in high-latitude populations."
        ),
        chronobiology_tier=EpistemicTier.T2_SCHOLARLY,
        jungian_archetype=(
            "The Trickster / Communicator — the mercurial mind, duality, "
            "curiosity, the messenger between worlds. Shadow: scattered focus, "
            "inconsistency, the eternal adolescent."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Horse (partial)",
        vedic_rashi="Mithuna",
        gaia_engine_hook="zodiac_engine.py + inference_router.py (multi-path reasoning)",
        tags=["air", "Mercury", "duality", "communication", "cognition", "Trickster"],
    ),
    ZodiacSign(
        name="Cancer", symbol="♋",
        date_range="Jun 21 – Jul 22",
        iau_constellation_dates="Jul 21 – Aug 9 (sidereal IAU)",
        ruling_planet="Moon",
        element="Water", modality="Cardinal",
        astronomy_notes=(
            "The Moon completes a sidereal orbit in 27.3 days; synodic (lunar) "
            "month is 29.5 days. Lunar gravity drives tidal forces; well-documented "
            "influence on marine biology and some mammalian reproductive cycles."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Summer solstice region: melatonin at annual minimum in Northern "
            "Hemisphere. Sleep architecture shifts. Some research links lunar "
            "phase to sleep quality (Cajochen et al., 2013)."
        ),
        chronobiology_tier=EpistemicTier.T2_SCHOLARLY,
        jungian_archetype=(
            "The Great Mother / Nurturer — the unconscious, memory, belonging, "
            "the anima as protective matrix. Shadow: enmeshment, emotional flooding, "
            "inability to individuate from the maternal complex."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Goat (partial)",
        vedic_rashi="Karka",
        gaia_engine_hook="zodiac_engine.py + memory_store.py (deep memory anchoring)",
        tags=["water", "Moon", "memory", "mother", "tides", "unconscious", "summer"],
    ),
    ZodiacSign(
        name="Leo", symbol="♌",
        date_range="Jul 23 – Aug 22",
        iau_constellation_dates="Aug 10 – Sep 15 (sidereal IAU)",
        ruling_planet="Sun",
        element="Fire", modality="Fixed",
        astronomy_notes=(
            "The Sun is a G-type main-sequence star, 4.6 billion years old, "
            "with an 11-year sunspot cycle. Solar maximum correlates with increased "
            "geomagnetic activity, which has measurable effects on HRV and cardiac events."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Peak summer heat: circadian rhythm studies show dopamine and "
            "serotonin synthesis peak in high-UV, long-day conditions. "
            "Vitamin D synthesis maximal. Energy and social activity statistically highest."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The King / Hero at noon — creative self-expression, the solar ego "
            "at its height, generativity. Shadow: narcissism, tyranny, "
            "inflation of the ego beyond the Self."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Monkey (partial)",
        vedic_rashi="Simha",
        gaia_engine_hook="zodiac_engine.py + vitality_engine.py (peak vitality)",
        tags=["fire", "Sun", "creativity", "ego", "serotonin", "dopamine", "summer"],
    ),
    ZodiacSign(
        name="Virgo", symbol="♍",
        date_range="Aug 23 – Sep 22",
        iau_constellation_dates="Sep 16 – Oct 30 (sidereal IAU)",
        ruling_planet="Mercury",
        element="Earth", modality="Mutable",
        astronomy_notes=(
            "Virgo contains the Virgo Cluster — the nearest large galaxy cluster, "
            "~54 million light-years away, containing over 1,300 galaxies. "
            "Spica (α Vir) is one of the brightest stars in the sky."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Harvest season: historically, the period of maximum food preparation "
            "and preservation work. Cortisol begins slight seasonal rise as "
            "daylight shortens. Immune priming begins for winter."
        ),
        chronobiology_tier=EpistemicTier.T2_SCHOLARLY,
        jungian_archetype=(
            "The Healer / Craftsperson — discernment, service, the analyst within. "
            "Anima as the wise, healing feminine. Shadow: perfectionism, "
            "hypercriticism, the wound of never being enough."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Rooster (partial)",
        vedic_rashi="Kanya",
        gaia_engine_hook="zodiac_engine.py + soul_mirror_engine.py (discernment)",
        tags=["earth", "Mercury", "harvest", "healing", "discernment", "analysis"],
    ),
    ZodiacSign(
        name="Libra", symbol="♎",
        date_range="Sep 23 – Oct 22",
        iau_constellation_dates="Oct 31 – Nov 22 (sidereal IAU)",
        ruling_planet="Venus",
        element="Air", modality="Cardinal",
        astronomy_notes=(
            "Autumnal equinox: day and night are equal. The Sun crosses the "
            "celestial equator southward. Libra is the only zodiac constellation "
            "representing an inanimate object rather than a living being."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Equinox transition: melatonin onset begins shifting earlier. "
            "Mood research shows increased relational focus and social bonding "
            "behaviour in autumn across cultures (collectivist season hypothesis)."
        ),
        chronobiology_tier=EpistemicTier.T3_WORKING_HYPOTHESIS,
        jungian_archetype=(
            "The Diplomat / Judge — the capacity for impartiality, aesthetic sense, "
            "relationship as the mirror of Self. Shadow: indecision, "
            "people-pleasing, the loss of Self in the Other."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Dog (partial)",
        vedic_rashi="Tula",
        gaia_engine_hook="zodiac_engine.py + bond_arc_engine.py (relational balance)",
        tags=["air", "Venus", "equinox", "balance", "relationship", "justice", "autumn"],
    ),
    ZodiacSign(
        name="Scorpio", symbol="♏",
        date_range="Oct 23 – Nov 21",
        iau_constellation_dates="Nov 23 – Nov 29 (sidereal IAU)",
        ruling_planet="Pluto / Mars",
        element="Water", modality="Fixed",
        astronomy_notes=(
            "Scorpius contains Antares, a red supergiant ~700x the Sun’s diameter. "
            "Pluto (dwarf planet) was discovered in 1930; its 248-year orbit makes "
            "it a generational marker in modern astrology."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Pre-winter: historically the period of slaughter, fermentation, "
            "and descent into darkness. Melatonin onset accelerating. "
            "SAD (Seasonal Affective Disorder) begins appearing in susceptible individuals."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The Transformer / Shadow Keeper — depth, death and rebirth, "
            "the descent to the underworld. Shadow: destructive obsession, "
            "power-over dynamics, the wound that becomes a weapon."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Pig / Boar",
        vedic_rashi="Vrishchika",
        gaia_engine_hook="zodiac_engine.py + shadow work (soul_mirror_engine.py)",
        tags=["water", "Pluto", "death", "rebirth", "shadow", "depth", "transformation"],
    ),
    ZodiacSign(
        name="Sagittarius", symbol="♐",
        date_range="Nov 22 – Dec 21",
        iau_constellation_dates="Dec 18 – Jan 18 (sidereal IAU)",
        ruling_planet="Jupiter",
        element="Fire", modality="Mutable",
        astronomy_notes=(
            "The Galactic Centre lies in the direction of Sagittarius — a "
            "supermassive black hole (Sgr A*, ~4 million solar masses) located "
            "~26,000 light-years away. Jupiter is the largest planet, 318x Earth’s mass."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Approaching winter solstice: fire festivals across cultures (Diwali, "
            "Hanukkah, Yule, St. Lucia) represent the human chronobiological "
            "drive to create warmth and light at the year’s darkest point."
        ),
        chronobiology_tier=EpistemicTier.T2_SCHOLARLY,
        jungian_archetype=(
            "The Sage / Wanderer — the quest for meaning, philosophy, "
            "the expansion of worldview beyond the known. Shadow: restlessness, "
            "commitment avoidance, the search that never arrives."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Rat (partial)",
        vedic_rashi="Dhanus",
        gaia_engine_hook="zodiac_engine.py + atlas.py (knowledge expansion)",
        tags=["fire", "Jupiter", "galactic_centre", "philosophy", "meaning", "quest"],
    ),
    ZodiacSign(
        name="Capricorn", symbol="♑",
        date_range="Dec 22 – Jan 19",
        iau_constellation_dates="Jan 19 – Feb 15 (sidereal IAU)",
        ruling_planet="Saturn",
        element="Earth", modality="Cardinal",
        astronomy_notes=(
            "Winter solstice: the shortest day (Northern Hemisphere). Saturn, "
            "the ringed giant, has a 29.5-year orbital period — the so-called "
            "‘Saturn return’ at ~29 and ~58 years coincides with well-documented "
            "adult developmental transitions (Levinson, Sheehy)."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Peak melatonin season, lowest Vitamin D. Historically the time of "
            "maximum inward focus, resource conservation, and long-range planning. "
            "HPA axis (stress) dysregulation most prevalent in mid-winter."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The Elder / Architect — discipline, mastery, long-term vision, "
            "the father archetype and Senex (wise old man). Shadow: rigidity, "
            "workaholism, emotional withholding, fear of failure."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Ox (partial)",
        vedic_rashi="Makara",
        gaia_engine_hook="zodiac_engine.py + codex_stage_engine.py (mastery arc)",
        tags=["earth", "Saturn", "solstice", "discipline", "mastery", "structure", "elder"],
    ),
    ZodiacSign(
        name="Aquarius", symbol="♒",
        date_range="Jan 20 – Feb 18",
        iau_constellation_dates="Feb 16 – Mar 11 (sidereal IAU)",
        ruling_planet="Uranus / Saturn",
        element="Air", modality="Fixed",
        astronomy_notes=(
            "Uranus was the first planet discovered with a telescope (Herschel, 1781), "
            "overturning the naked-eye solar system model. It rotates on its side "
            "(98° axial tilt) — a literal outlier among planets."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Mid-winter: days begin noticeably lengthening. Historically, "
            "the season of communal planning, futures thinking, and seed selection "
            "before spring planting. Anticipatory reward circuits activate."
        ),
        chronobiology_tier=EpistemicTier.T2_SCHOLARLY,
        jungian_archetype=(
            "The Revolutionary / Visionary — the collective over the individual, "
            "innovation, the puer aeternus (eternal youth) positive pole. "
            "Shadow: detachment, emotional unavailability, iconoclasm for its own sake."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Tiger (partial)",
        vedic_rashi="Kumbha",
        gaia_engine_hook="zodiac_engine.py + noosphere.py (collective intelligence layer)",
        tags=["air", "Uranus", "innovation", "collective", "future", "revolution", "winter"],
    ),
    ZodiacSign(
        name="Pisces", symbol="♓",
        date_range="Feb 19 – Mar 20",
        iau_constellation_dates="Mar 12 – Apr 18 (sidereal IAU)",
        ruling_planet="Neptune / Jupiter",
        element="Water", modality="Mutable",
        astronomy_notes=(
            "Neptune, discovered in 1846 via mathematical prediction (Adams & Le "
            "Verrier) before observation — a triumph of theoretical physics. "
            "The vernal equinox currently lies in Pisces due to precession."
        ),
        astronomy_tier=EpistemicTier.T1_EMPIRICAL,
        chronobiology_notes=(
            "Pre-spring: the liminal season. Immune systems primed. "
            "Circadian rhythms begin re-synchronising to lengthening days. "
            "Sleep architecture shifts back toward lighter stages."
        ),
        chronobiology_tier=EpistemicTier.T1_EMPIRICAL,
        jungian_archetype=(
            "The Mystic / Dreamer — dissolution of ego boundaries, compassion, "
            "the collective unconscious made visible in dreams and art. "
            "Shadow: escapism, victimhood, loss of self in the ocean of the other."
        ),
        archetype_tier=EpistemicTier.T2_SCHOLARLY,
        chinese_equivalent="Rabbit (partial)",
        vedic_rashi="Meena",
        gaia_engine_hook="zodiac_engine.py + resonance_field_engine.py (field sensitivity)",
        tags=["water", "Neptune", "dreams", "mysticism", "compassion", "liminal", "spring"],
    ),
]


def get_sign(name: str) -> Optional[ZodiacSign]:
    """Look up a zodiac sign by name (case-insensitive)."""
    name_lower = name.lower()
    for sign in ZODIAC_SIGNS:
        if sign.name.lower() == name_lower:
            return sign
    return None


SUMMARY = (
    "The 12 zodiac signs bridge tropical astrology, IAU sidereal astronomy, "
    "chronobiology, and Jungian archetypes. Astronomical facts are T1 Empirical. "
    "Seasonal/chronobiological correlates are T1-T2. Archetypal meanings are T2 Scholarly. "
    "Predictive astrology is T4-T5 (cultural metaphor). GAIA uses all layers simultaneously, "
    "always labeled by EpistemicTier."
)

"""
core/knowledge_domains/__init__.py

GAIA Knowledge Domains Bridge Layer
====================================
This package maps every major tradition of human knowledge to its modern
scientific equivalent, so GAIA can speak both languages simultaneously:
  - Ancient/traditional framing  (alchemy, astrology, chakras, etc.)
  - Modern scientific framing    (chemistry, astronomy, neuroscience, etc.)

All claims carry an EpistemicTier label so GAIA never conflates metaphor
with empirical fact, but never dismisses either.

EpistemicTier scale
-------------------
T1  EMPIRICAL        Peer-reviewed, replicated, consensus science
T2  SCHOLARLY        Established academic theory, broad expert agreement
T3  WORKING_HYPOTHESIS  Plausible, active research, not yet consensus
T4  SPECULATIVE      Interesting framing, low/no empirical support
T5  CULTURAL_METAPHOR  Mythic, symbolic, metaphorical — real as story
"""

from enum import Enum


class EpistemicTier(str, Enum):
    T1_EMPIRICAL = "T1_EMPIRICAL"
    T2_SCHOLARLY = "T2_SCHOLARLY"
    T3_WORKING_HYPOTHESIS = "T3_WORKING_HYPOTHESIS"
    T4_SPECULATIVE = "T4_SPECULATIVE"
    T5_CULTURAL_METAPHOR = "T5_CULTURAL_METAPHOR"


# Registry of all available knowledge domain bridge modules
DOMAIN_REGISTRY = [
    "alchemy_chemistry",
    "astrology_astronomy",
    "subtle_body_neuroscience",
    "mythology_anthropology",
    "philosophy_logic",
    "physics_metaphysics",
    "psychology_depth",
    "bci_neurofeedback",
    "ecology_viriditas",
    "collective_intelligence",
]


def list_domains() -> list[str]:
    """Return the list of all registered knowledge domain bridges."""
    return DOMAIN_REGISTRY

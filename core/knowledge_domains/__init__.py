"""
core/knowledge_domains — GAIA-APP Knowledge Domain Bridge package.

This is the crown jewel of the GAIA modernization.
Each module bridges an ancient/traditional knowledge tradition
to its modern scientific, psychological, or philosophical equivalent.

GAIA does not replace old wisdom — it TRANSLATES it.

Domain bridges:
  alchemy         — Hermetic operations → Chemistry + Neuroscience + Psychology
  astrology       — Zodiac cycles → Astronomy + Chronobiology + Jungian archetypes
  subtle_body     — Chakras/Nadis → Autonomic Nervous System + Interoception
  noosphere       — Collective consciousness → Network theory + GCP data
  cosmology       — Dark matter / metaphysics → Quantum field theory + Epistemics
  mythology       — Archetypes → Comparative anthropology + Campbell monomyth
  psyche          — Soul Mirror / Jungian shadow → Depth psychology + Affective neuroscience
  viriditas       — Magnum Opus / Paracelsus → Ecology + Complexity theory
  crystalline     — Crystal consciousness → Crystallography + Materials science
  forces          — Five dynamic forces → Physics + Systems theory
  bci             — BCI coherence → Neurofeedback + EEG research

All domains expose a query_topic(topic: str) → DomainInsight interface.
"""

from .alchemy import AlchemyBridge, query_topic as alchemy_query

__all__ = ["AlchemyBridge", "alchemy_query"]

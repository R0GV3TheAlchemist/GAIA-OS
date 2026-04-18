"""
core/development_stage_engine.py

Development stage integrator for GAIA.
Bridges lifespan, moral, and meaning-making development into one readable output.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DevelopmentProfile:
    age_band: str
    primary_task: str
    likely_edges: list[str] = field(default_factory=list)
    likely_strengths: list[str] = field(default_factory=list)
    guidance: str = ""


class DevelopmentStageEngine:
    def assess(self, age: int | None = None, themes: list[str] | None = None) -> DevelopmentProfile:
        themes = [t.lower() for t in (themes or [])]

        if age is None:
            return DevelopmentProfile(
                age_band="unknown",
                primary_task="Build enough context to identify the current developmental challenge.",
                likely_edges=["identity diffusion", "role confusion", "meaning instability"],
                likely_strengths=["adaptability"],
                guidance="Ask what task keeps repeating: identity, intimacy, mastery, generativity, or integration.",
            )

        if age < 13:
            return DevelopmentProfile(
                age_band="childhood",
                primary_task="Build safety, competence, trust, and emotional language.",
                likely_edges=["shame", "fear", "dependency"],
                likely_strengths=["play", "plasticity", "imagination"],
                guidance="Prioritize safety, rhythm, co-regulation, and encouragement over abstraction.",
            )
        if age < 20:
            return DevelopmentProfile(
                age_band="adolescence",
                primary_task="Identity formation: Who am I, apart from my environment?",
                likely_edges=["role confusion", "peer-driven self-worth", "volatility"],
                likely_strengths=["experimentation", "rapid learning", "intensity"],
                guidance="Support identity exploration without forcing premature certainty.",
            )
        if age < 35:
            return DevelopmentProfile(
                age_band="early_adulthood",
                primary_task="Build intimacy, direction, and a livable structure for adult life.",
                likely_edges=["commitment fear", "comparison", "instability"],
                likely_strengths=["drive", "adaptation", "capacity to build"],
                guidance="Choose fewer things more deeply. Consistency matters more than dramatic reinvention.",
            )
        if age < 55:
            return DevelopmentProfile(
                age_band="midlife",
                primary_task="Generativity: create, teach, protect, and integrate contradictions.",
                likely_edges=["stagnation", "resentment", "meaning crisis"],
                likely_strengths=["pattern recognition", "craft", "leadership"],
                guidance="Turn experience into transmission. Build what outlives the mood of the week.",
            )
        return DevelopmentProfile(
            age_band="later_life",
            primary_task="Integration, legacy, and coherent self-reflection.",
            likely_edges=["despair", "isolation", "rigidity"],
            likely_strengths=["wisdom", "perspective", "distillation"],
            guidance="Name what matters most, simplify, and transmit living knowledge.",
        )


DEFAULT_ENGINE = DevelopmentStageEngine()

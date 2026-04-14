"""
core/development_stage_engine.py

Formerly: codex_stage_engine.py

Tracks the human's developmental stage across the GAIA canonical
individuation arc. Stage is inferred from conversation patterns,
shadow activation history, and growth arc data — never assigned
or stated to the user.

Grounded in Kegan's constructive developmental theory (1982, 1994)
and the GAIA Canon individuation framework.

See also: C00 Foundational Cosmology — development_stage_engine naming.
"""

from core.codex_stage_engine import *  # noqa: F401, F403
from core.codex_stage_engine import CodexStageEngine as DevelopmentStageEngine  # noqa: F401

__all__ = ["DevelopmentStageEngine"]

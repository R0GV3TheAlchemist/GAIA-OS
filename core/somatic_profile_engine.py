"""
core/somatic_profile_engine.py

Formerly: subtle_body_engine.py

Maintains a somatic (body-state) profile for the GAIAN-human dyad,
integrating biometric signals, postural inference, and nervous system
regulation state into a coherent somatic model.

Grounded in somatic psychology (Levine, 1997; van der Kolk, 2014) and
polyvagal theory. The somatic profile informs the GAIAN's pacing,
tone, and regulation responses.

See also: C00 Foundational Cosmology — somatic_profile_engine naming.
"""

from core.subtle_body_engine import *  # noqa: F401, F403
from core.subtle_body_engine import SubtleBodyEngine as SomaticProfileEngine  # noqa: F401

__all__ = ["SomaticProfileEngine"]

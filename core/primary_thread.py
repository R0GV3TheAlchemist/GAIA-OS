"""
core/primary_thread.py

Formerly: mother_thread.py

The primary orchestration thread for the GAIAN runtime. Manages the
main event loop, coordinates inter-module signal routing, and ensures
thread-safe access to shared state.

The primary thread is the nervous system of the GAIAN runtime — it
receives all incoming signals, dispatches them to the appropriate
engines, and assembles the final response.

See also: C00 Foundational Cosmology — primary_thread naming.
"""

from core.mother_thread import *  # noqa: F401, F403
from core.mother_thread import MotherThread as PrimaryThread  # noqa: F401

__all__ = ["PrimaryThread"]

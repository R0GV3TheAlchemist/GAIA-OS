"""
core/session_memory.py — STUB (Phase C)

Physical implementation has moved to core/memory/session_memory.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.
"""
from core.memory.session_memory import *         # noqa: F401, F403
from core.memory.session_memory import (         # noqa: F401
    SessionTurn,
    SessionMemory,
    SESSION_TTL,
    get_or_create_session,
    get_session,
    delete_session,
    _cleanup_expired_sessions,
    _sessions,
)

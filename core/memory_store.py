"""
core/memory_store.py — STUB (Phase C)

Physical implementation has moved to core/memory/memory_store.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.
"""
from core.memory.memory_store import *           # noqa: F401, F403
from core.memory.memory_store import (           # noqa: F401
    MemoryStore,
    MemoryEntry,
    get_memory_store,
    _default_store_path,
)

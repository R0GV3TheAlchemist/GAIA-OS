"""
core/memory_chroma.py — STUB (Phase C)

Physical implementation has moved to core/memory/memory_chroma.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.
"""
from core.memory.memory_chroma import *          # noqa: F401, F403
from core.memory.memory_chroma import (          # noqa: F401
    ChromaMemory,
    get_chroma,
    store_turn,
    recall_for_prompt,
    _chroma_path,
    _CHROMA_AVAILABLE,
)

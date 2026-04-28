"""
core/memory/
============
GAIA Memory Layer — persistent memory stores, vector memory,
session context, and the knowledge matrix.

Phase C: Files physically live here. Flat core/ stubs re-export from here
for zero-breakage backward compatibility.
"""

from .memory_store import MemoryStore, MemoryEntry, get_memory_store
from .memory_chroma import (
    ChromaMemory,
    get_chroma,
    store_turn,
    recall_for_prompt,
)
from .session_memory import (
    SessionTurn,
    SessionMemory,
    SESSION_TTL,
    get_or_create_session,
    get_session,
    delete_session,
)
from .knowledge_matrix import (
    EpistemicTier,
    KnowledgeDomain,
    KnowledgeMatrixEngine,
    KNOWLEDGE_MATRIX,
    get_knowledge_engine,
)

__all__ = [
    # memory_store
    "MemoryStore", "MemoryEntry", "get_memory_store",
    # memory_chroma
    "ChromaMemory", "get_chroma", "store_turn", "recall_for_prompt",
    # session_memory
    "SessionTurn", "SessionMemory", "SESSION_TTL",
    "get_or_create_session", "get_session", "delete_session",
    # knowledge_matrix
    "EpistemicTier", "KnowledgeDomain", "KnowledgeMatrixEngine",
    "KNOWLEDGE_MATRIX", "get_knowledge_engine",
]

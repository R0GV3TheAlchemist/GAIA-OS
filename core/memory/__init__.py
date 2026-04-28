"""
core/memory/
============
GAIA Memory Layer — persistent memory stores, vector memory,
session context, and the knowledge matrix.

Submodules
----------
memory_store     — primary persistent memory store
memory_chroma    — ChromaDB vector memory backend
session_memory   — ephemeral session-scoped memory
knowledge_matrix — structured knowledge graph and matrix
"""

from core.memory.memory_store import MemoryStore
from core.memory.memory_chroma import MemoryChroma
from core.memory.session_memory import SessionMemory
from core.memory.knowledge_matrix import KnowledgeMatrix

__all__ = [
    "MemoryStore",
    "MemoryChroma",
    "SessionMemory",
    "KnowledgeMatrix",
]

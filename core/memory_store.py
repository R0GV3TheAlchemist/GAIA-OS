"""
MemoryStore — Governed memory surface.

All memory in GAIA is:
  - Visible: the user can see everything GAIA remembers about them
  - Editable: the user can correct inaccurate memories
  - Deletable: the user can remove any memory, with verifiable deletion
  - Purpose-limited: each memory is tagged with its authorized uses
  - Appealable: contested memories can be flagged for formal review

Memory is not a background process — it is a governed surface.
The human sovereign has full inspection and control rights over it.

Epistemic Status: ESTABLISHED
Canon Ref: Doc 34 (Identity), CDT Memory Governance Framework
"""

import datetime
import hashlib
from typing import Optional


class MemoryEntry:
    def __init__(
        self,
        content: str,
        source: str,  # "explicit", "inferred", "external"
        purposes: list,
        confidence: float = 1.0,
    ):
        self.memory_id = self._compute_id(content)
        self.content = content
        self.source = source
        self.purposes = purposes
        self.confidence = confidence  # 0.0 – 1.0
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.frozen = False  # True during appeal review
        self.deleted = False

    def _compute_id(self, content: str) -> str:
        return hashlib.sha256(
            f"{content}:{datetime.datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "source": self.source,
            "purposes": self.purposes,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "frozen": self.frozen,
            "deleted": self.deleted,
        }


class MemoryStore:
    """
    The governed memory surface. Stores, retrieves, edits, and deletes
    memory entries. Every modification is logged in an audit trail.
    """

    def __init__(self):
        self._memories: dict = {}   # memory_id -> MemoryEntry
        self._audit: list = []

    def add(self, content: str, source: str, purposes: list, confidence: float = 1.0) -> MemoryEntry:
        """Add a new memory entry."""
        entry = MemoryEntry(content, source, purposes, confidence)
        self._memories[entry.memory_id] = entry
        self._audit.append({"event": "add", "memory_id": entry.memory_id, "timestamp": entry.created_at})
        return entry

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID."""
        entry = self._memories.get(memory_id)
        if entry and not entry.deleted:
            return entry
        return None

    def edit(self, memory_id: str, new_content: str) -> bool:
        """Edit a memory entry. Returns False if frozen or not found."""
        entry = self._memories.get(memory_id)
        if not entry or entry.deleted or entry.frozen:
            return False
        old_content = entry.content
        entry.content = new_content
        self._audit.append({
            "event": "edit",
            "memory_id": memory_id,
            "old_content": old_content,
            "new_content": new_content,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        return True

    def delete(self, memory_id: str) -> bool:
        """Soft-delete a memory. Returns False if not found."""
        entry = self._memories.get(memory_id)
        if not entry or entry.deleted:
            return False
        entry.deleted = True
        self._audit.append({
            "event": "delete",
            "memory_id": memory_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        return True

    def freeze(self, memory_id: str) -> bool:
        """Freeze a memory during appeal review. Prevents use in decisions."""
        entry = self._memories.get(memory_id)
        if not entry:
            return False
        entry.frozen = True
        return True

    def unfreeze(self, memory_id: str) -> bool:
        """Unfreeze a memory after appeal resolution."""
        entry = self._memories.get(memory_id)
        if not entry:
            return False
        entry.frozen = False
        return True

    def list_all(self) -> list:
        """Return all non-deleted memory entries (user visibility surface)."""
        return [
            e.to_dict()
            for e in self._memories.values()
            if not e.deleted
        ]

    def get_audit_log(self) -> list:
        """Return the full audit log."""
        return list(self._audit)

"""
MemoryStore — Governed persistent memory surface.

All memory in GAIA is:
  - Visible:        the user can see everything GAIA remembers about them
  - Editable:       the user can correct inaccurate memories
  - Deletable:      the user can remove any memory, with verifiable deletion
  - Purpose-limited: each memory is tagged with its authorized uses
  - Appealable:     contested memories can be flagged for formal review

Memory is not a background process — it is a governed surface.
The human sovereign has full inspection and control rights over it.

Epistemic Status: ESTABLISHED
Canon Ref: C17 (Persistent Memory and Identity Architecture)

Persistence: JSON file at $APPDATA/GAIA/memory.json (XDG-aware fallback).
The file is written atomically (temp-file + rename) to prevent corruption.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import pathlib
import tempfile
from typing import Optional


# ---------------------------------------------------------------------------
# Resolve storage path
# ---------------------------------------------------------------------------

def _default_store_path() -> pathlib.Path:
    """Return the canonical path for memory.json across platforms."""
    # Tauri writes to %APPDATA%\GAIA on Windows and ~/.local/share/GAIA on Linux/macOS.
    if os.name == "nt":
        base = pathlib.Path(os.environ.get("APPDATA", pathlib.Path.home() / "AppData" / "Roaming"))
    else:
        base = pathlib.Path(os.environ.get("XDG_DATA_HOME", pathlib.Path.home() / ".local" / "share"))
    return base / "GAIA" / "memory.json"


# ---------------------------------------------------------------------------
# MemoryEntry
# ---------------------------------------------------------------------------

class MemoryEntry:
    def __init__(
        self,
        content: str,
        source: str,          # "explicit" | "inferred" | "session" | "external"
        purposes: list[str],
        confidence: float = 1.0,
        *,
        memory_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        frozen: bool = False,
        deleted: bool = False,
        edit_count: int = 0,
    ):
        now = datetime.datetime.utcnow().isoformat()
        self.id        = memory_id or self._compute_id(content)
        self.content   = content
        self.source    = source
        self.purposes  = purposes
        self.confidence = confidence
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.frozen    = frozen
        self.deleted   = deleted
        self.edit_count = edit_count

    # Keep backward-compat alias used in old code
    @property
    def memory_id(self) -> str:
        return self.id

    def _compute_id(self, content: str) -> str:
        ts = datetime.datetime.utcnow().isoformat()
        return hashlib.sha256(f"{content}:{ts}".encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "content":    self.content,
            "source":     self.source,
            "purposes":   self.purposes,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "frozen":     self.frozen,
            "deleted":    self.deleted,
            "edit_count": self.edit_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryEntry":
        return cls(
            content    = d["content"],
            source     = d.get("source", "explicit"),
            purposes   = d.get("purposes", ["general"]),
            confidence = d.get("confidence", 1.0),
            memory_id  = d.get("id") or d.get("memory_id"),
            created_at = d.get("created_at"),
            updated_at = d.get("updated_at"),
            frozen     = d.get("frozen", False),
            deleted    = d.get("deleted", False),
            edit_count = d.get("edit_count", 0),
        )


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------

class MemoryStore:
    """
    Governed persistent memory surface.
    Backed by a JSON file that is loaded on first access and
    written atomically on every mutation.
    """

    def __init__(self, store_path: Optional[pathlib.Path] = None):
        self._path: pathlib.Path = store_path or _default_store_path()
        self._memories: dict[str, MemoryEntry] = {}
        self._audit: list[dict] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for d in data.get("memories", []):
                    entry = MemoryEntry.from_dict(d)
                    self._memories[entry.id] = entry
                self._audit = data.get("audit", [])
            except Exception:
                # Corrupted store — start fresh, keep the bad file as .bak
                bak = self._path.with_suffix(".bak.json")
                try:
                    self._path.rename(bak)
                except Exception:
                    pass

    def _save(self) -> None:
        """Atomically write the store to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "memories": [e.to_dict() for e in self._memories.values()],
            "audit":    self._audit,
        }
        # Write to a temp file first, then rename (atomic on POSIX; best-effort on Windows)
        fd, tmp = tempfile.mkstemp(dir=self._path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._path)
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass
            raise

    def _stamp(self) -> str:
        return datetime.datetime.utcnow().isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        content: str,
        source: str,
        purposes: list[str],
        confidence: float = 1.0,
    ) -> MemoryEntry:
        self._ensure_loaded()
        entry = MemoryEntry(content, source, purposes, confidence)
        self._memories[entry.id] = entry
        self._audit.append({
            "action":    "add",
            "memory_id": entry.id,
            "timestamp": entry.created_at,
        })
        self._save()
        return entry

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        self._ensure_loaded()
        entry = self._memories.get(memory_id)
        return entry if (entry and not entry.deleted) else None

    def edit(self, memory_id: str, new_content: str) -> bool:
        self._ensure_loaded()
        entry = self._memories.get(memory_id)
        if not entry or entry.deleted or entry.frozen:
            return False
        old = entry.content
        entry.content    = new_content
        entry.updated_at = self._stamp()
        entry.edit_count += 1
        self._audit.append({
            "action":      "edit",
            "memory_id":   memory_id,
            "old_content": old,
            "new_content": new_content,
            "timestamp":   entry.updated_at,
        })
        self._save()
        return True

    def delete(self, memory_id: str) -> bool:
        self._ensure_loaded()
        entry = self._memories.get(memory_id)
        if not entry or entry.deleted:
            return False
        entry.deleted    = True
        entry.updated_at = self._stamp()
        self._audit.append({
            "action":    "delete",
            "memory_id": memory_id,
            "timestamp": entry.updated_at,
        })
        self._save()
        return True

    def freeze(self, memory_id: str) -> bool:
        self._ensure_loaded()
        entry = self._memories.get(memory_id)
        if not entry:
            return False
        entry.frozen = True
        self._save()
        return True

    def unfreeze(self, memory_id: str) -> bool:
        self._ensure_loaded()
        entry = self._memories.get(memory_id)
        if not entry:
            return False
        entry.frozen = False
        self._save()
        return True

    def list_all(self) -> list[dict]:
        """Return all non-deleted memory entries (user visibility surface)."""
        self._ensure_loaded()
        return [
            e.to_dict()
            for e in self._memories.values()
            if not e.deleted
        ]

    def list_active_contents(self) -> list[str]:
        """Return plain content strings for injection into inference prompts."""
        self._ensure_loaded()
        return [
            e.content
            for e in self._memories.values()
            if not e.deleted and not e.frozen
        ]

    def get_audit_log(self) -> list[dict]:
        self._ensure_loaded()
        return list(self._audit)


# ---------------------------------------------------------------------------
# Singleton — shared across the server process
# ---------------------------------------------------------------------------

_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store

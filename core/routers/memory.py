"""
core/routers/memory.py

C17-governed persistent memory endpoints:
  GET    /memory/list          — list all active memories
  POST   /memory/add           — add a new memory
  PUT    /memory/{id}          — edit a memory (new_content query param)
  DELETE /memory/{id}          — soft-delete a memory
  GET    /memory/audit         — full audit log
  POST   /memory/{id}/freeze   — freeze for appeal review
  POST   /memory/{id}/unfreeze — lift freeze after resolution

All endpoints are intentionally unauthenticated at the router level
so the local Tauri frontend can call them without a token.
Add `Depends(require_auth)` here if you want to gate them behind auth.

Canon Ref: C17 (Persistent Memory and Identity Architecture)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.memory_store import get_memory_store

router = APIRouter(prefix="/memory", tags=["memory"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class AddMemoryRequest(BaseModel):
    content: str
    source: str = "explicit"       # explicit | inferred | session
    purposes: list[str] = ["general"]
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/list")
def memory_list():
    """Return all active (non-deleted) memory entries."""
    store = get_memory_store()
    return store.list_all()


@router.post("/add")
def memory_add(req: AddMemoryRequest):
    """Add a new governed memory entry."""
    if not req.content.strip():
        raise HTTPException(status_code=422, detail="content must not be empty")
    store = get_memory_store()
    entry = store.add(
        content    = req.content.strip(),
        source     = req.source,
        purposes   = req.purposes,
        confidence = max(0.0, min(1.0, req.confidence)),
    )
    return entry.to_dict()


@router.put("/{memory_id}")
def memory_edit(memory_id: str, new_content: str):
    """Edit the content of a memory entry."""
    if not new_content.strip():
        raise HTTPException(status_code=422, detail="new_content must not be empty")
    store = get_memory_store()
    ok = store.edit(memory_id, new_content.strip())
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Memory '{memory_id}' not found, deleted, or frozen.",
        )
    return {"status": "updated", "id": memory_id}


@router.delete("/{memory_id}")
def memory_delete(memory_id: str):
    """Soft-delete a memory entry. Guaranteed within 24 h per C17."""
    store = get_memory_store()
    ok = store.delete(memory_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Memory '{memory_id}' not found or already deleted.",
        )
    return {"status": "deleted", "id": memory_id}


@router.get("/audit")
def memory_audit():
    """Return the full immutable audit log."""
    store = get_memory_store()
    return store.get_audit_log()


@router.post("/{memory_id}/freeze")
def memory_freeze(memory_id: str):
    """Freeze a memory during an appeal review."""
    store = get_memory_store()
    ok = store.freeze(memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    return {"status": "frozen", "id": memory_id}


@router.post("/{memory_id}/unfreeze")
def memory_unfreeze(memory_id: str):
    """Lift a freeze after appeal resolution."""
    store = get_memory_store()
    ok = store.unfreeze(memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    return {"status": "unfrozen", "id": memory_id}

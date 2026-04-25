"""
core/routers/memory.py

C17-governed persistent memory endpoints:
  GET    /memory/list          — list all active memories
  POST   /memory/add           — add a new memory
  POST   /memory/store         — store a raw text fragment to ChromaDB
  GET    /memory/recall        — semantic similarity search (?q=&top_k=5)
  PUT    /memory/{id}          — edit a memory (new_content query param)
  DELETE /memory/{id}          — soft-delete a memory (+ ChromaDB forget)
  GET    /memory/audit         — full audit log
  POST   /memory/{id}/freeze   — freeze for appeal review
  POST   /memory/{id}/unfreeze — lift freeze after resolution

All endpoints are intentionally unauthenticated at the router level
so the local Tauri frontend can call them without a token.

Canon Ref: C17 (Persistent Memory and Identity Architecture)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.memory_chroma import get_chroma, store_turn
from core.memory_store import get_memory_store

router = APIRouter(prefix="/memory", tags=["memory"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class AddMemoryRequest(BaseModel):
    content: str
    source: str = "explicit"       # explicit | inferred | session | conversation
    purposes: list[str] = ["general"]
    confidence: float = 1.0


class StoreMemoryRequest(BaseModel):
    text: str
    source: str = "conversation"
    emotion: str = "neutral"
    gaian_slug: str = "gaia"
    session_id: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/list")
def memory_list():
    """Return all active (non-deleted) C17-governed memory entries."""
    store = get_memory_store()
    return store.list_all()


@router.post("/add")
def memory_add(req: AddMemoryRequest):
    """Add a new governed memory entry (JSON store + ChromaDB)."""
    if not req.content.strip():
        raise HTTPException(status_code=422, detail="content must not be empty")
    store = get_memory_store()
    entry = store.add(
        content    = req.content.strip(),
        source     = req.source,
        purposes   = req.purposes,
        confidence = max(0.0, min(1.0, req.confidence)),
    )
    # Mirror to ChromaDB for semantic recall
    chroma = get_chroma()
    chroma.store(
        text=entry.content,
        memory_id=entry.id,
        source=entry.source,
        gaian_slug="gaia",
    )
    return entry.to_dict()


@router.post("/store")
def memory_store(req: StoreMemoryRequest):
    """
    Store a raw text fragment directly to ChromaDB.
    Used by auto-store after conversation turns.
    Does NOT create a C17 governed entry — use /add for that.
    """
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    chroma = get_chroma()
    if not chroma.available:
        return {"status": "skipped", "reason": "ChromaDB not available"}
    import hashlib, datetime
    uid = hashlib.sha256(f"{req.gaian_slug}:{req.session_id}:{req.text[:64]}:{datetime.datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
    ok = chroma.store(
        text=req.text,
        memory_id=uid,
        source=req.source,
        emotion=req.emotion,
        gaian_slug=req.gaian_slug,
        session_id=req.session_id,
    )
    return {"status": "stored" if ok else "failed", "id": uid, "chroma_count": chroma.count()}


@router.get("/recall")
def memory_recall(q: str, top_k: int = 5, gaian_slug: str = "gaia"):
    """
    Semantic similarity search over ChromaDB.
    Returns top_k most relevant memory fragments for the query.
    """
    if not q.strip():
        raise HTTPException(status_code=422, detail="q must not be empty")
    chroma = get_chroma()
    if not chroma.available:
        return {"results": [], "chroma_available": False}
    hits = chroma.recall(query=q, top_k=min(top_k, 20), gaian_slug=gaian_slug)
    return {
        "results": hits,
        "count": len(hits),
        "chroma_available": True,
        "chroma_total": chroma.count(),
    }


@router.put("/{memory_id}")
def memory_edit(memory_id: str, new_content: str):
    """Edit the content of a governed memory entry."""
    if not new_content.strip():
        raise HTTPException(status_code=422, detail="new_content must not be empty")
    store = get_memory_store()
    ok = store.edit(memory_id, new_content.strip())
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Memory '{memory_id}' not found, deleted, or frozen.",
        )
    # Update ChromaDB with new content
    chroma = get_chroma()
    chroma.store(text=new_content.strip(), memory_id=memory_id, source="explicit")
    return {"status": "updated", "id": memory_id}


@router.delete("/{memory_id}")
def memory_delete(memory_id: str):
    """Soft-delete a governed memory. Also removes from ChromaDB. C17 24h guarantee."""
    store = get_memory_store()
    ok = store.delete(memory_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Memory '{memory_id}' not found or already deleted.",
        )
    # Mirror deletion to ChromaDB
    get_chroma().forget(memory_id)
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

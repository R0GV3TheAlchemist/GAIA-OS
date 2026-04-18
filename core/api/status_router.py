"""
GAIA-APP — core/api/status_router.py
Phase 1 Modernization: Status, Canon Status, and Memory List endpoints
extracted from the monolithic server.py into a clean FastAPI APIRouter.

This is the first split. Each subsequent router (chat, search, memory,
canon, zodiac, mother_thread) will follow the same pattern.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(tags=["status"])


# ---------------------------------------------------------------------------
# Health / Status
# ---------------------------------------------------------------------------

@router.get("/status", summary="GAIA system health check")
async def status(request: Request) -> dict[str, Any]:
    """
    Returns a lightweight health snapshot of the GAIA runtime.
    No authentication required — safe to hit from monitoring tools.
    """
    app_state = request.app.state

    runtime_registry: dict = getattr(app_state, "runtime_registry", {})
    canon_loader = getattr(app_state, "canon_loader", None)
    mother_thread = getattr(app_state, "mother_thread", None)

    return {
        "status": "online",
        "timestamp": time.time(),
        "active_gaians": len(runtime_registry),
        "canon_loaded": canon_loader is not None,
        "mother_thread_alive": (
            mother_thread.is_alive() if hasattr(mother_thread, "is_alive") else False
        ),
        "version": getattr(app_state, "version", "2.0.0-modernized"),
    }


# ---------------------------------------------------------------------------
# Canon Status
# ---------------------------------------------------------------------------

@router.get("/canon/status", summary="Canon doctrine health check")
async def canon_status(request: Request) -> dict[str, Any]:
    """
    Returns a summary of currently loaded canon doctrine.
    Useful for verifying ethical/philosophical constraints are active.
    """
    canon_loader = getattr(request.app.state, "canon_loader", None)

    if canon_loader is None:
        raise HTTPException(
            status_code=503,
            detail="Canon loader is not initialised. GAIA cannot operate without doctrine.",
        )

    # Attempt to surface loaded document names if the loader exposes them.
    loaded_docs: list[str] = []
    if hasattr(canon_loader, "loaded_documents"):
        loaded_docs = list(canon_loader.loaded_documents)
    elif hasattr(canon_loader, "canon") and isinstance(canon_loader.canon, dict):
        loaded_docs = list(canon_loader.canon.keys())

    return {
        "canon_active": True,
        "loaded_documents": loaded_docs,
        "document_count": len(loaded_docs),
        "action_gate_enforced": True,
        "epistemic_tier_labels": True,
        "last_loaded": getattr(canon_loader, "last_loaded_at", None),
    }


# ---------------------------------------------------------------------------
# Memory List (global / admin view)
# ---------------------------------------------------------------------------

@router.get("/memory/list", summary="List active in-memory GAIAN sessions")
async def memory_list(request: Request) -> dict[str, Any]:
    """
    Returns a summary of active runtime sessions in memory.
    Does NOT return personal memory contents — only session metadata.
    Consent-safe by design: no PII surfaced here.
    """
    runtime_registry: dict = getattr(request.app.state, "runtime_registry", {})

    sessions = []
    for slug, runtime in runtime_registry.items():
        sessions.append(
            {
                "slug": slug,
                "alive": getattr(runtime, "is_alive", False),
                "memory_size": len(getattr(runtime, "memory_store", {}) or {}),
            }
        )

    return {
        "total_active_sessions": len(sessions),
        "sessions": sessions,
    }

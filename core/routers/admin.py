"""
core/routers/admin.py

Admin / operator endpoints (require_auth enforced on every route):
  GET  /admin/me               — authenticated user identity
  GET  /admin/runtimes         — list all active runtimes + snapshots
  POST /admin/runtimes/reload  — hot-reload a named runtime
  GET  /admin/canon/reload     — reload canon from disk
  GET  /admin/mother/restart   — restart the MotherThread

Canon Refs: C01, C04, C42, C43, C44, C47, C48
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth import require_auth
from core.server_state import (
    _RUNTIME_REGISTRY,
    _mother_thread,
    canon,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class ReloadRuntimeRequest(BaseModel):
    gaian: str


@router.get("/me")
async def admin_me(user=Depends(require_auth)):
    """Return the identity of the authenticated caller."""
    return {"user": user}


@router.get("/runtimes")
async def list_runtimes(_user=Depends(require_auth)):
    """Return a snapshot of every active Gaian runtime."""
    snapshots = {}
    for slug, rt in _RUNTIME_REGISTRY.items():
        try:
            snapshots[slug] = rt.get_status()
        except Exception as exc:
            snapshots[slug] = {"error": str(exc)}
    return {"active_runtimes": len(_RUNTIME_REGISTRY), "snapshots": snapshots}


@router.post("/runtimes/reload")
async def reload_runtime(body: ReloadRuntimeRequest, _user=Depends(require_auth)):
    """Hot-reload a named Gaian runtime."""
    rt = _RUNTIME_REGISTRY.get(body.gaian)
    if rt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active runtime for gaian '{body.gaian}'",
        )
    try:
        await rt.reload()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return {"status": "reloaded", "gaian": body.gaian}


@router.get("/canon/reload")
async def reload_canon(_user=Depends(require_auth)):
    """Reload the Canon from disk without restarting the server."""
    try:
        canon.load()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return {
        "status": "reloaded",
        "canon_status": canon.status,
        "doc_count": len(canon.list_documents()),
    }


@router.get("/mother/restart")
async def restart_mother(_user=Depends(require_auth)):
    """Restart the MotherThread (non-destructive warm restart)."""
    try:
        await _mother_thread.restart()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return {"status": "restarted", "mother_thread": _mother_thread.get_status()}

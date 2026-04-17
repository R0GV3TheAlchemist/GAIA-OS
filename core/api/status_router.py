"""
core/api/status_router.py

Public read-only status endpoints.

Endpoints
---------
GET /status          — full system snapshot
GET /canon/status    — canon document count and load state
GET /memory/list     — session turn list (query-param: session_id)

Canon Ref: C01, C04, C12
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

router = APIRouter(tags=["Status"])


# ------------------------------------------------------------------ #
#  These three dependencies are injected at mount time from server.py  #
#  via router.dependency_overrides or module-level setters.            #
#  For now they default to None and server.py calls set_dependencies() #
# ------------------------------------------------------------------ #

_canon                = None
_inference_router_ref = None
_mother_thread_ref    = None
_runtime_registry_ref = None
_magnum_opus_ref      = None
_admin_identity       = {}
_server_version       = "2.1.0"


def set_dependencies(
    canon,
    inference_router,
    mother_thread,
    runtime_registry: dict,
    magnum_opus_getter,
    admin_identity: dict,
    server_version: str,
) -> None:
    """Called once from server.py startup to inject shared singletons."""
    global _canon, _inference_router_ref, _mother_thread_ref
    global _runtime_registry_ref, _magnum_opus_ref
    global _admin_identity, _server_version

    _canon                = canon
    _inference_router_ref = inference_router
    _mother_thread_ref    = mother_thread
    _runtime_registry_ref = runtime_registry
    _magnum_opus_ref      = magnum_opus_getter
    _admin_identity       = admin_identity
    _server_version       = server_version


# ------------------------------------------------------------------ #
#  GET /status                                                         #
# ------------------------------------------------------------------ #

@router.get("/status", summary="Full system snapshot")
async def status():
    """
    Returns a complete snapshot of the running GAIA system:
    - Core active/version info
    - Canon load state and document count
    - Active GAIAN runtimes
    - InferenceRouter stats (G-8)
    - MotherThread status (G-8)
    - Viriditas Magnum Opus boot report (C47)
    """
    from core.gaian import list_gaians
    from core.gaian.base_forms import list_base_forms

    doc_count  = len(_canon.list_documents()) if _canon else 0
    doc_names  = _canon.list_documents() if _canon else []
    gaians     = list_gaians()

    runtime_snapshots = {}
    if _runtime_registry_ref:
        for slug, rt in _runtime_registry_ref.items():
            try:
                runtime_snapshots[slug] = rt.get_status()
            except Exception:
                pass

    # C47: Viriditas snapshot
    viriditas_snap = None
    report = _magnum_opus_ref() if _magnum_opus_ref else None
    if report:
        viriditas_snap = {
            "phi":               round(report.post_phi_global, 4),
            "delta_phi":         round(report.delta_phi_global, 4),
            "threshold_crossed": report.threshold_crossed,
            "viriditas_state":   report.viriditas_state.name,
            "stages_greened":    f"{report.stages_greened}/5",
            "covenant_stable":   report.dual_stability_maintained,
            "run_id":            report.run_id,
        }

    return {
        "core":              "active",
        "version":           _server_version,
        "runtime_version":   _server_version,
        "schema_version":    "1.6",
        "engines":           12,
        "sovereignty":       "enforced",
        "auth":              "jwt-hs256",
        "logging":           "structured",
        "rate_limiting":     "sliding-window",
        "admin":             _admin_identity.get("handle", ""),
        "canon_status":      _canon.status if _canon else "unloaded",
        "canon_loaded":      _canon.is_loaded if _canon else False,
        "canon_doc_count":   doc_count,
        "canon_docs":        doc_names,
        "gaians":            len(gaians),
        "gaian_names":       [g["name"] for g in gaians],
        "base_forms":        len(list_base_forms()),
        "active_runtimes":   len(_runtime_registry_ref) if _runtime_registry_ref else 0,
        "runtime_snapshots": runtime_snapshots,
        "inference_router":  _inference_router_ref.get_stats() if _inference_router_ref else {},
        "mother_thread":     _mother_thread_ref.get_status() if _mother_thread_ref else {},
        "viriditas":         viriditas_snap,
    }


# ------------------------------------------------------------------ #
#  GET /canon/status                                                   #
# ------------------------------------------------------------------ #

@router.get("/canon/status", summary="Canon load state")
async def canon_status():
    """Returns canon load state, document count, and document names."""
    doc_count = len(_canon.list_documents()) if _canon else 0
    return {
        "status":    _canon.status if _canon else "unloaded",
        "loaded":    _canon.is_loaded if _canon else False,
        "doc_count": doc_count,
        "docs":      _canon.list_documents() if _canon else [],
    }


# ------------------------------------------------------------------ #
#  GET /memory/list                                                    #
# ------------------------------------------------------------------ #

@router.get("/memory/list", summary="Session turn history")
async def memory_list(session_id: Optional[str] = None):
    """Returns the list of turns for a given session_id."""
    if not session_id:
        return {"memories": [], "count": 0}

    from core.session_memory import get_session
    session = get_session(session_id)
    if not session:
        return {"memories": [], "count": 0}

    memories = [
        {"query": t.query, "timestamp": t.timestamp, "source_count": t.source_count}
        for t in session.turns
    ]
    return {"memories": memories, "count": len(memories)}

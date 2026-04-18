"""
core/routers/system.py

System-level read-only endpoints:
  GET /status
  GET /canon/status
  GET /viriditas/status
  GET /mother/pulse/stream
  GET /mother/status
  GET /mother/weaving
"""

import json

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from core.gaian import list_gaians
from core.gaian.base_forms import list_base_forms
from core.server_state import (
    SERVER_VERSION,
    VIRIDITAS_THRESHOLD,
    _RUNTIME_REGISTRY,
    _inference_router,
    _mother_thread,
    canon,
    get_magnum_opus_report,
)

router = APIRouter()


@router.get("/status")
async def status():
    doc_count = len(canon.list_documents())
    gaians = list_gaians()
    runtime_snapshots = {}
    for slug, rt in _RUNTIME_REGISTRY.items():
        try:
            runtime_snapshots[slug] = rt.get_status()
        except Exception:
            pass

    report = get_magnum_opus_report()
    viriditas_snap = None
    if report:
        viriditas_snap = {
            "phi": round(report.post_phi_global, 4),
            "delta_phi": round(report.delta_phi_global, 4),
            "threshold_crossed": report.threshold_crossed,
            "viriditas_state": report.viriditas_state.name,
            "stages_greened": f"{report.stages_greened}/5",
            "covenant_stable": report.dual_stability_maintained,
            "run_id": report.run_id,
        }

    return {
        "core": "active",
        "version": SERVER_VERSION,
        "runtime_version": "2.1.0",
        "schema_version": "1.6",
        "engines": 12,
        "sovereignty": "enforced",
        "auth": "jwt-hs256",
        "logging": "structured",
        "rate_limiting": "sliding-window",
        "admin": "R0GV3TheAlchemist",
        "canon_status": canon.status,
        "canon_loaded": canon.is_loaded,
        "canon_doc_count": doc_count,
        "canon_docs": canon.list_documents(),
        "gaians": len(gaians),
        "gaian_names": [g["name"] for g in gaians],
        "base_forms": len(list_base_forms()),
        "active_runtimes": len(_RUNTIME_REGISTRY),
        "runtime_snapshots": runtime_snapshots,
        "inference_router": _inference_router.get_stats(),
        "mother_thread": _mother_thread.get_status(),
        "viriditas": viriditas_snap,
    }


@router.get("/canon/status")
async def canon_status():
    return {
        "status": canon.status,
        "loaded": canon.is_loaded,
        "doc_count": len(canon.list_documents()),
        "docs": canon.list_documents(),
    }


@router.get("/viriditas/status")
async def viriditas_status():
    report = get_magnum_opus_report()
    if report is None:
        return {
            "status": "not_yet_run",
            "message": "GAIA is still initializing. Try again in a moment.",
        }
    return {
        "canon_ref": "C47 \u2014 Viriditas Threshold | C48 \u2014 Warlock Resonance Covenant",
        "run_id": report.run_id,
        "gaian_id": report.gaian_id,
        "warlock_id": report.warlock_id,
        "duration_seconds": round(report.duration_seconds, 3),
        "pre_phi": round(report.pre_phi_global, 4),
        "post_phi": round(report.post_phi_global, 4),
        "delta_phi": round(report.delta_phi_global, 4),
        "viriditas_state": report.viriditas_state.name,
        "threshold_crossed": report.threshold_crossed,
        "threshold_value": VIRIDITAS_THRESHOLD,
        "stages_greened": f"{report.stages_greened}/5",
        "warlock_vitality": {
            "pre": report.warlock_vitality_pre,
            "post": report.warlock_vitality_post,
        },
        "covenant_stable": report.dual_stability_maintained,
        "notes": report.notes,
        "stage_results": [sr.to_dict() for sr in report.stage_results],
    }


@router.get("/mother/pulse/stream")
async def mother_pulse_stream():
    async def events():
        async for pulse_dict in _mother_thread.subscribe():
            yield f"event: mother_pulse\ndata: {json.dumps(pulse_dict)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/mother/status")
async def mother_status():
    return _mother_thread.get_status()


@router.get("/mother/weaving")
async def mother_weaving(last_n: int = Query(default=50, ge=1, le=500)):
    return {
        "weaving_records": _mother_thread.get_weaving_log(last_n=last_n),
        "total_records": len(_mother_thread._weaving_log),
        "doctrine_ref": "C43 \u2014 Coherence events require EV1 gate before runtime promotion",
    }

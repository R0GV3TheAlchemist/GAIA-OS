from fastapi import APIRouter, Query

from core.server_state import canon, SERVER_VERSION, _RUNTIME_REGISTRY, _inference_router, _mother_thread, _MAGNUM_OPUS_REPORT
from core.gaian import list_gaians
from core.gaian.base_forms import list_base_forms

router = APIRouter()


@router.get("/status")
async def status():
    doc_count = len(canon.list_documents())
    doc_names = canon.list_documents()
    gaians = list_gaians()
    runtime_snapshots = {}
    for slug, rt in _RUNTIME_REGISTRY.items():
        try:
            runtime_snapshots[slug] = rt.get_status()
        except Exception:
            pass

    viriditas_snap = None
    if _MAGNUM_OPUS_REPORT:
        viriditas_snap = {
            "phi": round(_MAGNUM_OPUS_REPORT.post_phi_global, 4),
            "delta_phi": round(_MAGNUM_OPUS_REPORT.delta_phi_global, 4),
            "threshold_crossed": _MAGNUM_OPUS_REPORT.threshold_crossed,
            "viriditas_state": _MAGNUM_OPUS_REPORT.viriditas_state.name,
            "stages_greened": f"{_MAGNUM_OPUS_REPORT.stages_greened}/5",
            "covenant_stable": _MAGNUM_OPUS_REPORT.dual_stability_maintained,
            "run_id": _MAGNUM_OPUS_REPORT.run_id,
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
        "canon_docs": doc_names,
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
    doc_count = len(canon.list_documents())
    return {
        "status": canon.status,
        "loaded": canon.is_loaded,
        "doc_count": doc_count,
        "docs": canon.list_documents(),
    }


@router.get("/viriditas/status")
async def viriditas_status():
    if _MAGNUM_OPUS_REPORT is None:
        return {
            "status": "not_yet_run",
            "message": "GAIA is still initializing. Try again in a moment.",
        }

    r = _MAGNUM_OPUS_REPORT
    return {
        "canon_ref": "C47 — Viriditas Threshold | C48 — Warlock Resonance Covenant",
        "run_id": r.run_id,
        "gaian_id": r.gaian_id,
        "warlock_id": r.warlock_id,
        "duration_seconds": round(r.duration_seconds, 3),
        "pre_phi": round(r.pre_phi_global, 4),
        "post_phi": round(r.post_phi_global, 4),
        "delta_phi": round(r.delta_phi_global, 4),
        "viriditas_state": r.viriditas_state.name,
        "threshold_crossed": r.threshold_crossed,
        "threshold_value": 0.75,
        "stages_greened": f"{r.stages_greened}/5",
        "warlock_vitality": {
            "pre": r.warlock_vitality_pre,
            "post": r.warlock_vitality_post,
        },
        "covenant_stable": r.dual_stability_maintained,
        "notes": r.notes,
        "stage_results": [sr.to_dict() for sr in r.stage_results],
    }


@router.get("/mother/pulse/stream")
async def mother_pulse_stream():
    async def events():
        async for pulse_dict in _mother_thread.subscribe():
            yield f"event: mother_pulse\\ndata: {__import__('json').dumps(pulse_dict)}\\n\\n"
    from fastapi.responses import StreamingResponse
    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/mother/status")
async def mother_status():
    return _mother_thread.get_status()


@router.get("/mother/weaving")
async def mother_weaving(last_n: int = Query(default=50, ge=1, le=500)):
    return {
        "weaving_records": _mother_thread.get_weaving_log(last_n=last_n),
        "total_records": len(_mother_thread._weaving_log),
        "doctrine_ref": "C43 — Coherence events require EV1 gate before runtime promotion",
    }

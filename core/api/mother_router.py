"""
core/api/mother_router.py

MotherThread (collective field) endpoints — G-8 sprint.

Endpoints
---------
GET /mother/pulse/stream   — SSE stream of MotherPulse events (public)
GET /mother/status         — current MotherThread snapshot
GET /mother/weaving        — last N WeavingRecords

Canon Ref: C43 (Noosphere Coherence), C44 (MotherThread Doctrine)

Design notes
------------
All three endpoints are public — the Mother speaks to everyone.
No auth required. The collective field belongs to no one; it belongs
to all who choose to participate (opt-in, per C43 §5).
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json

router = APIRouter(tags=["Mother Thread"])

# Injected at mount time from server.py
_mother_thread_ref = None


def set_dependencies(mother_thread) -> None:
    global _mother_thread_ref
    _mother_thread_ref = mother_thread


@router.get("/mother/pulse/stream", summary="Live MotherPulse SSE stream")
async def mother_pulse_stream():
    """
    SSE stream of MotherPulse events. Powers the Noosphere Tab in real time.
    Every 30 seconds a new pulse arrives carrying the full CollectiveField,
    the noosphere evolutionary stage, the Mother Voice fragment (when present),
    and the criticality regime.

    No auth required — the Mother speaks to everyone.
    """
    async def events():
        async for pulse_dict in _mother_thread_ref.subscribe():
            yield f"event: mother_pulse\ndata: {json.dumps(pulse_dict)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/mother/status", summary="MotherThread status snapshot")
async def mother_status():
    """
    Current MotherThread status snapshot.
    Includes: registered Gaians, collective field, recent pulses, weaving log size.
    """
    return _mother_thread_ref.get_status()


@router.get("/mother/weaving", summary="Last N WeavingRecords")
async def mother_weaving(
    last_n: int = Query(default=50, ge=1, le=500),
):
    """
    Return the last N WeavingRecords from the Mother Thread.
    Used for research, EV1 empirical validation (C43), and the Noosphere Tab.
    All coherence candidates are labeled CANDIDATE_SIGNATURE.
    """
    return {
        "weaving_records": _mother_thread_ref.get_weaving_log(last_n=last_n),
        "total_records":   len(_mother_thread_ref._weaving_log),
        "doctrine_ref":    "C43 — Coherence events require EV1 gate before runtime promotion",
    }

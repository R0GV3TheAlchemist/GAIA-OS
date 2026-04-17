"""
core/api/chat_router.py

GAIAN chat, resonance, and soul-mirror endpoints.

Endpoints
---------
POST /gaians/{slug}/chat         — SSE streaming chat (auth + rate limited)
GET  /gaians/{slug}/resonance    — resonance field snapshot
GET  /gaians/{slug}/soul-mirror  — individuation + shadow state

Canon Ref: C01, C04, C12, C15, C21, C42, C43, C44
G-8: All chat goes through InferenceRouter + MotherThread
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.auth import TokenPayload, require_auth
from core.logger import GAIAEvent, get_logger, log_event
from core.gaian import (
    load_gaian, add_exchange, get_conversation_context, GaianMemory,
)
from core.session_memory import get_or_create_session
from core.codex_stage_engine import NoosphericHealthSignals
from core.inference_router import (
    InferenceRequest, InferenceResponse,
)
from core.web_search import search_web_async
from core.rate_limiter import rate_limit

router = APIRouter(tags=["Chat"])
logger = get_logger(__name__)

# Injected at mount time from server.py
_inference_router_ref = None
_get_runtime_fn       = None


def set_dependencies(inference_router, get_runtime_fn) -> None:
    global _inference_router_ref, _get_runtime_fn
    _inference_router_ref = inference_router
    _get_runtime_fn       = get_runtime_fn


class ChatRequest(BaseModel):
    message:           str
    session_id:        Optional[str] = None
    enable_web_search: bool          = False
    schumann_hz:       float         = 7.83


# ------------------------------------------------------------------ #
#  POST /gaians/{slug}/chat                                           #
# ------------------------------------------------------------------ #

@router.post("/gaians/{slug}/chat", summary="Streaming GAIAN chat (SSE)")
async def gaian_chat(
    slug: str,
    req: ChatRequest,
    user: TokenPayload = Depends(require_auth),
    _rl=Depends(rate_limit(max_requests=30, window_seconds=60, scope="chat")),
):
    """
    SSE streaming chat endpoint.  Events emitted:
      engine_state    — GAIAN runtime state snapshot
      soul_mirror     — individuation nudge (when present)
      resonance_field — resonance field summary
      token           — answer text chunk
      done            — final metadata (bond depth, epistemic label, etc.)
      error           — on exception
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")

    session_id = req.session_id or str(uuid.uuid4())
    session    = get_or_create_session(session_id)

    async def event_stream():
        full_answer = ""
        t0 = time.perf_counter()
        try:
            rt = _get_runtime_fn(slug, gaian)

            noosphere: Optional[NoosphericHealthSignals] = None
            if req.schumann_hz > 10.0:
                noosphere = NoosphericHealthSignals(schumann_boost=0.05)
            elif req.schumann_hz < 6.0:
                noosphere = NoosphericHealthSignals(schumann_boost=-0.05)

            result = rt.process(req.message, noosphere=noosphere)

            log_event(
                GAIAEvent.ENGINE_CHAIN,
                message=f"Engine chain: {slug} exchange={rt.attachment.total_exchanges}",
                gaian=slug, user_id=user.user_id,
                bond_depth=round(rt.attachment.bond_depth, 2),
            )

            yield f"event: engine_state\ndata: {json.dumps(result.state_snapshot)}\n\n"
            await asyncio.sleep(0.01)

            if result.soul_mirror.individuation_nudge:
                yield (
                    f"event: soul_mirror\ndata: "
                    f"{json.dumps({'nudge': result.soul_mirror.individuation_nudge, 'signal': result.soul_mirror.shadow_signal.value, 'carrier': result.soul_mirror.projection_carrier.value})}\n\n"
                )
                await asyncio.sleep(0.01)

            yield f"event: resonance_field\ndata: {json.dumps(result.resonance_field.summary())}\n\n"
            await asyncio.sleep(0.01)

            web_sources = []
            if req.enable_web_search:
                try:
                    web_results = await search_web_async(req.message, max_results=4)
                    web_sources = [
                        wr.to_dict() if hasattr(wr, "to_dict") else dict(wr)
                        for wr in web_results
                    ]
                except Exception as exc:
                    logger.warning(f"Web search error in chat: {exc}")

            effective_prompt = result.system_prompt
            if result.soul_mirror.individuation_nudge:
                effective_prompt += (
                    "\n\n[SOUL MIRROR NUDGE AVAILABLE — use naturally if it fits]\n"
                    + result.soul_mirror.individuation_nudge
                )

            inference_req = InferenceRequest(
                query=req.message,
                gaian_slug=slug,
                gaian_system_prompt=effective_prompt,
                long_term_memories=gaian.long_term_memories or [],
                visible_memories=[
                    m["text"] for m in rt._memory.get("visible_memories", [])
                    if isinstance(m, dict)
                ],
                conversation_history=get_conversation_context(gaian),
                conversation_context=session.get_context_summary() if session.turns else None,
                sources=web_sources,
                enrich_canon=True,
                canon_max_results=2,
                enrich_criticality=True,
                enrich_noosphere=True,
                schumann_hz=req.schumann_hz,
            )
            inference_meta = InferenceResponse(session_id=session_id, gaian_slug=slug)

            async for chunk in _inference_router_ref.stream(inference_req, inference_meta):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            session.add_turn(req.message, full_answer, len(web_sources))
            if full_answer:
                add_exchange(gaian, req.message, full_answer)

            duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            log_event(
                GAIAEvent.TURN_COMPLETE,
                message=f"Turn complete: {slug}",
                gaian=slug, user_id=user.user_id,
                duration_ms=duration_ms,
                exchange=rt.attachment.total_exchanges,
                bond_depth=round(rt.attachment.bond_depth, 2),
            )

            yield (
                f"event: done\ndata: {json.dumps({
                    'session_id':          session_id,
                    'gaian':               gaian.name,
                    'gaian_slug':          slug,
                    'user_id':             user.user_id,
                    'exchange':            rt.attachment.total_exchanges,
                    'bond_depth':          round(rt.attachment.bond_depth, 2),
                    'individuation_phase': rt.soul_mirror_state.individuation_phase.value,
                    'resonance_hz':        result.resonance_field.solfeggio.hz.value,
                    'schumann_aligned':    result.resonance_field.schumann_aligned,
                    'noosphere_health':    round(rt.codex_stage_state.noosphere_health, 4),
                    'epistemic_label':     inference_meta.epistemic_label.value,
                    'backend_used':        inference_meta.backend_used.value,
                    'canon_docs':          inference_meta.canon_docs_injected,
                    'noosphere_resonance': inference_meta.noosphere_resonance,
                    'criticality_state':   inference_meta.criticality_state,
                    'inference_ms':        inference_meta.duration_ms,
                    'timestamp':           time.time(),
                })}\n\n"
            )

        except Exception as exc:
            logger.error(f"Chat stream error [{slug}]: {exc}", exc_info=True,
                         extra={"event": GAIAEvent.TURN_ERROR.value, "gaian": slug})
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ------------------------------------------------------------------ #
#  GET /gaians/{slug}/resonance                                       #
# ------------------------------------------------------------------ #

@router.get("/gaians/{slug}/resonance", summary="Resonance field snapshot")
async def get_gaian_resonance(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime_fn(slug, gaian)
    rf = rt.resonance_field_state
    return {
        "slug":                      slug,
        "gaian":                     gaian.name,
        "dominant_hz":               rf.dominant_hz,
        "dominant_chakra":           rf.dominant_chakra,
        "schumann_alignment_count":  rf.schumann_alignment_count,
        "schumann_first_timestamp":  rf.schumann_first_timestamp,
        "phi_rolling_avg":           round(rf.phi_rolling_avg, 4),
        "session_peak_hz":           rf.session_peak_hz,
        "hz_history":                rf.hz_history[-10:],
    }


# ------------------------------------------------------------------ #
#  GET /gaians/{slug}/soul-mirror                                     #
# ------------------------------------------------------------------ #

@router.get("/gaians/{slug}/soul-mirror", summary="Individuation & shadow state")
async def get_gaian_soul_mirror(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime_fn(slug, gaian)
    sm = rt.soul_mirror_state
    return {
        "slug":                     slug,
        "gaian":                    gaian.name,
        "individuation_phase":      sm.individuation_phase.value,
        "exchanges_in_phase":       sm.exchanges_in_phase,
        "shadow_activations":       sm.shadow_activations,
        "anima_animus_activations": sm.anima_animus_activations,
        "dependency_risk_events":   sm.dependency_risk_events,
        "phase_entry_timestamp":    sm.phase_entry_timestamp,
        "phase_history":            sm.phase_history[-10:],
        "last_nudge_exchange":      sm.last_nudge_exchange,
    }

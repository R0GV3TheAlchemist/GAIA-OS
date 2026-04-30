"""
core/api/query_router.py

Perplexity-style answer-engine query stream.

Endpoints
---------
POST /query/stream   — canon search + web search + InferenceRouter SSE

Canon Ref: C01, C12, C27, C30
G-8: Routed through InferenceRouter

Modernization notes
-------------------
This is GAIA's core "Answer Engine".  Future Phase 2 additions:
  - knowledge_domains/ bridge: every answer enriched with the relevant
    alchemy/astrology/subtle-body/mythology domain context.
  - Epistemic tier labels (T1-T5) surfaced in every source citation.
  - Multi-language response support (Phase 4 i18n).
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.auth import TokenPayload, require_auth
from core.logger import GAIAEvent, get_logger, log_event
from core.gaian import (
    load_gaian, add_exchange, get_conversation_context, GaianMemory,
)
from core.session_memory import get_or_create_session
from core.inference_router import InferenceRequest, InferenceResponse
from core.web_search import search_web_async
from core.rate_limiter import rate_limit

router = APIRouter(tags=["Query"])
logger = get_logger(__name__)

# Injected at mount time from server.py
_canon                = None
_inference_router_ref = None
_get_runtime_fn       = None


def set_dependencies(canon, inference_router, get_runtime_fn) -> None:
    global _canon, _inference_router_ref, _get_runtime_fn
    _canon                = canon
    _inference_router_ref = inference_router
    _get_runtime_fn       = get_runtime_fn


class QueryRequest(BaseModel):
    query:             str
    session_id:        Optional[str] = None
    gaian_slug:        Optional[str] = None
    enable_web_search: bool          = True
    max_sources:       int           = 8


def _generate_suggestions(query: str, sources: list[dict]) -> list[str]:
    suggestions = []
    for s in sources[:2]:
        title = s.get("title", "")
        if title:
            short = title.split(":")[-1].strip()[:40]
            if short:
                suggestions.append(f"Tell me more about {short}")
    suggestions.append("What does GAIA's canon say about this?")
    suggestions.append("What are the practical implications?")
    return suggestions[:3]


@router.post("/query/stream", summary="Perplexity-style answer stream (SSE)")
async def query_stream(
    req: QueryRequest,
    user: TokenPayload = Depends(require_auth),
    _rl=Depends(rate_limit(max_requests=20, window_seconds=60, scope="query")),
):
    """
    Streaming answer endpoint.  Events emitted:
      citation     — canon search result
      web_result   — web search result
      engine_state — GAIAN runtime snapshot (when active GAIAN)
      token        — answer text chunk
      suggestions  — follow-up question suggestions
      done         — final metadata
      error        — on exception
    """
    session_id = req.session_id or str(uuid.uuid4())
    session    = get_or_create_session(session_id)
    gaian_slug = req.gaian_slug or session.active_gaian_slug or "gaia"
    gaian: Optional[GaianMemory] = load_gaian(gaian_slug)
    if gaian is None:
        gaian = load_gaian("gaia")
        if gaian:
            gaian_slug = gaian.slug

    async def event_stream():
        full_answer  = ""
        sources      = []
        canon_results = []
        t0 = time.perf_counter()
        try:
            canon_results = _canon.search(req.query, max_results=3) if _canon else []
            log_event(GAIAEvent.CANON_SEARCH,
                      message=f"Canon search: {len(canon_results)} results",
                      gaian=gaian_slug, user_id=user.user_id,
                      results=len(canon_results))

            for result in canon_results:
                src = {
                    "tier":    "T1",
                    "title":   result.get("title", ""),
                    "doc_id":  result.get("doc_id", ""),
                    "excerpt": result.get("excerpt", ""),
                }
                sources.append(src)
                yield f"event: citation\ndata: {json.dumps(result)}\n\n"
                await asyncio.sleep(0.01)

            if req.enable_web_search:
                try:
                    web_results = await search_web_async(req.query, max_results=5)
                    for wr in web_results:
                        src = wr.to_dict() if hasattr(wr, "to_dict") else dict(wr)
                        src["tier"] = src.get("source_tier", "T4")
                        sources.append(src)
                        yield f"event: web_result\ndata: {json.dumps(src)}\n\n"
                        await asyncio.sleep(0.01)
                except Exception as exc:
                    logger.warning(f"Web search failed: {exc}")

            runtime_system_prompt = None
            conversation_history  = None
            long_term_memories    = []
            visible_memories      = []

            if gaian:
                rt = _get_runtime_fn(gaian_slug, gaian)
                rt.canon_text = (
                    "\n\n".join(
                        "[{title}]\n{excerpt}".format(
                            title=r.get("title", ""), excerpt=r.get("excerpt", "")
                        )
                        for r in canon_results[:2]
                    )
                ) if canon_results else None
                result = rt.process(req.query)
                runtime_system_prompt = result.system_prompt
                yield f"event: engine_state\ndata: {json.dumps(result.state_snapshot)}\n\n"
                await asyncio.sleep(0.01)
                conversation_history = get_conversation_context(gaian)
                long_term_memories   = gaian.long_term_memories or []
                visible_memories     = [
                    m["text"] for m in rt._memory.get("visible_memories", [])
                    if isinstance(m, dict)
                ]

            inference_req = InferenceRequest(
                query=req.query,
                gaian_slug=gaian_slug,
                gaian_system_prompt=runtime_system_prompt,
                long_term_memories=long_term_memories,
                visible_memories=visible_memories,
                conversation_history=conversation_history or [],
                conversation_context=session.get_context_summary() if session.turns else None,
                sources=sources,
                enrich_canon=True,
                canon_max_results=2,
                enrich_criticality=True,
                enrich_noosphere=True,
            )
            inference_meta = InferenceResponse(session_id=session_id, gaian_slug=gaian_slug)

            async for chunk in _inference_router_ref.stream(inference_req, inference_meta):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            suggestions = _generate_suggestions(req.query, sources)
            yield f"event: suggestions\ndata: {json.dumps({'items': suggestions})}\n\n"

            session.add_turn(req.query, full_answer, len(sources))
            if gaian and full_answer:
                add_exchange(gaian, req.query, full_answer)

            duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            log_event(
                GAIAEvent.TURN_COMPLETE,
                message="Query stream complete",
                gaian=gaian_slug, user_id=user.user_id,
                duration_ms=duration_ms,
                canon_refs=len(canon_results),
                web_results=len(sources) - len(canon_results),
            )

            done_data = {
                'canon_status':        _canon.status if _canon else 'unloaded',
                'docs_searched':       len(_canon.list_documents()) if _canon else 0,
                'refs_found':          len(canon_results),
                'web_results':         len(sources) - len(canon_results),
                'session_id':          session_id,
                'user_id':             user.user_id,
                'gaian':               gaian.name if gaian else None,
                'gaian_slug':          gaian_slug,
                'epistemic_label':     inference_meta.epistemic_label.value,
                'backend_used':        inference_meta.backend_used.value,
                'canon_docs':          inference_meta.canon_docs_injected,
                'noosphere_resonance': inference_meta.noosphere_resonance,
                'criticality_state':   inference_meta.criticality_state,
                'inference_ms':        inference_meta.duration_ms,
                'timestamp':           time.time(),
            }
            yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

        except Exception as exc:
            logger.error(f"Stream error: {exc}", exc_info=True,
                         extra={"event": GAIAEvent.TURN_ERROR.value})
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

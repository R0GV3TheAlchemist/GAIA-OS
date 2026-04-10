"""
GAIA API Server — FastAPI + SSE streaming v0.4.2

Endpoints:
  GET  /status                     — system health + canon status
  GET  /canon/status               — canon-specific status (UI compatibility)
  GET  /memory/list                — session memory list (UI compatibility)
  POST /query/stream               — main SSE query pipeline
  GET  /gaians                     — list all personal GAIANs
  POST /gaians                     — create a new GAIAN
  GET  /gaians/{slug}              — get a GAIAN's profile
  POST /gaians/{slug}/remember     — add a long-term memory
  POST /session/{session_id}/gaian — set active GAIAN for session

Canon Ref: C15, C21
"""

import asyncio
import json
import logging
import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.canon_loader import CanonLoader
from core.web_search import search_web_async
from core.synthesizer import stream_synthesis
from core.gaian import (
    list_gaians, create_gaian, load_gaian, ensure_default_gaian,
    add_exchange, get_conversation_context, build_gaian_system_prompt,
    GaianMemory, _save_gaian,
)
from core.session_memory import get_or_create_session

# ------------------------------------------------------------------ #
#  Bootstrap                                                           #
# ------------------------------------------------------------------ #

app = FastAPI(title="GAIA API", version="0.4.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

canon = CanonLoader()
canon.load()   # load canon docs at startup

try:
    ensure_default_gaian()
    logger.info("Default GAIAN (GAIA) ready.")
except Exception as e:
    logger.warning(f"Could not initialise default GAIAN: {e}")


# ------------------------------------------------------------------ #
#  Models                                                              #
# ------------------------------------------------------------------ #

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    gaian_slug: Optional[str] = None
    enable_web_search: bool = True
    max_sources: int = 8


class CreateGaianRequest(BaseModel):
    name: str
    personality: str
    avatar_color: str = "#4ade80"
    user_name: Optional[str] = None


class RememberRequest(BaseModel):
    memory: str


class SetGaianRequest(BaseModel):
    gaian_slug: str


# ------------------------------------------------------------------ #
#  Status Endpoints                                                    #
# ------------------------------------------------------------------ #

@app.get("/status")
async def status():
    doc_count = len(canon.list_documents())
    gaians = list_gaians()
    return {
        "core": "active",
        "version": "0.4.2",
        "sovereignty": "enforced",
        "canon_status": canon.status,
        "canon_loaded": canon.is_loaded,
        "canon_doc_count": doc_count,
        "gaians": len(gaians),
        "gaian_names": [g["name"] for g in gaians],
    }


@app.get("/canon/status")
async def canon_status():
    """Canon-specific status endpoint — used by the UI status bar."""
    doc_count = len(canon.list_documents())
    return {
        "status": canon.status,
        "loaded": canon.is_loaded,
        "doc_count": doc_count,
        "docs": canon.list_documents(),
    }


@app.get("/memory/list")
async def memory_list(session_id: Optional[str] = None):
    """Session memory list — used by the UI memory panel."""
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


# ------------------------------------------------------------------ #
#  Query Stream                                                        #
# ------------------------------------------------------------------ #

@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    session_id = req.session_id or str(uuid.uuid4())
    session = get_or_create_session(session_id)

    gaian_slug = req.gaian_slug or session.active_gaian_slug or "gaia"
    gaian: Optional[GaianMemory] = load_gaian(gaian_slug)
    if gaian is None:
        gaian = load_gaian("gaia")

    async def event_stream():
        full_answer = ""
        sources = []
        canon_results = []

        try:
            # 1. Canon search — correct param is max_results, not top_k
            canon_results = canon.search(req.query, max_results=3)
            for result in canon_results:
                src = {
                    "tier": "T1",
                    "title": result.get("title", ""),
                    "doc_id": result.get("doc_id", ""),
                    "excerpt": result.get("excerpt", ""),
                }
                sources.append(src)
                yield f"event: citation\ndata: {json.dumps(result)}\n\n"
                await asyncio.sleep(0.01)

            # 2. Web search
            if req.enable_web_search:
                try:
                    web_results = await search_web_async(req.query, max_results=5)
                    for wr in web_results:
                        src = wr.to_dict() if hasattr(wr, 'to_dict') else dict(wr)
                        src["tier"] = src.get("source_tier", "T4")
                        sources.append(src)
                        yield f"event: web_result\ndata: {json.dumps(src)}\n\n"
                        await asyncio.sleep(0.01)
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")

            # 3. GAIAN context
            gaian_prompt = None
            conversation_history = None
            conversation_context = None
            if gaian:
                gaian_prompt = build_gaian_system_prompt(gaian)
                conversation_history = get_conversation_context(gaian)
                if session.turns:
                    conversation_context = session.get_context_summary()

            # 4. Stream synthesis
            async for chunk in stream_synthesis(
                query=req.query,
                sources=sources,
                gaian_prompt=gaian_prompt,
                conversation_history=conversation_history,
                conversation_context=conversation_context,
            ):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            # 5. Suggestions
            suggestions = _generate_suggestions(req.query, sources)
            yield f"event: suggestions\ndata: {json.dumps({'items': suggestions})}\n\n"

            # 6. Persist
            session.add_turn(req.query, full_answer, len(sources))
            if gaian and full_answer:
                add_exchange(gaian, req.query, full_answer)

            # 7. Done
            yield f"event: done\ndata: {json.dumps({'canon_status': canon.status, 'docs_searched': len(canon.list_documents()), 'refs_found': len(canon_results), 'web_results': len(sources) - len(canon_results), 'session_id': session_id, 'gaian': gaian.name if gaian else None, 'timestamp': time.time()})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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


# ------------------------------------------------------------------ #
#  GAIAN Endpoints                                                     #
# ------------------------------------------------------------------ #

@app.get("/gaians")
async def get_gaians():
    return {"gaians": list_gaians()}


@app.post("/gaians")
async def post_create_gaian(req: CreateGaianRequest):
    try:
        gaian = create_gaian(
            name=req.name,
            personality=req.personality,
            avatar_color=req.avatar_color,
            user_name=req.user_name,
        )
        return {"status": "created", "id": gaian.id, "name": gaian.name, "slug": gaian.slug}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gaians/{slug}")
async def get_gaian(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    return {
        "id": gaian.id,
        "name": gaian.name,
        "slug": gaian.slug,
        "personality": gaian.personality,
        "avatar_color": gaian.avatar_color,
        "relationship_depth": gaian.relationship_depth,
        "total_exchanges": gaian.total_exchanges,
        "user_name": gaian.user_name,
        "last_active": gaian.last_active,
        "created_at": gaian.created_at,
        "long_term_memories": gaian.long_term_memories,
        "recent_turns": len(gaian.conversation_history) // 2,
    }


@app.post("/gaians/{slug}/remember")
async def post_remember(slug: str, req: RememberRequest):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    gaian.long_term_memories.append(req.memory)
    if len(gaian.long_term_memories) > 50:
        gaian.long_term_memories = gaian.long_term_memories[-50:]
    _save_gaian(gaian)
    return {"status": "remembered", "total_memories": len(gaian.long_term_memories)}


@app.post("/session/{session_id}/gaian")
async def set_session_gaian(session_id: str, req: SetGaianRequest):
    gaian = load_gaian(req.gaian_slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{req.gaian_slug}' not found")
    session = get_or_create_session(session_id)
    session.active_gaian_slug = req.gaian_slug
    return {"status": "ok", "gaian": gaian.name, "session_id": session_id}


# ------------------------------------------------------------------ #
#  Entry Point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "core.server:app",
        host="127.0.0.1",
        port=8008,
        reload=False,
        log_level="info",
    )

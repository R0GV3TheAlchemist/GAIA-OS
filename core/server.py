"""
GAIA API Server — FastAPI + SSE streaming v0.5.0

Endpoints (unchanged from v0.4.3 unless marked NEW/UPGRADED):
  GET  /status                            — system health  [UPGRADED: includes runtime engine state]
  GET  /canon/status                      — canon status for UI
  GET  /memory/list                       — session memory for UI
  GET  /gaians/base-forms                 — list all Base Form archetypes
  GET  /gaians                            — list user's personal GAIANs
  POST /gaians                            — spawn a new GAIAN
  GET  /gaians/{slug}                     — get a GAIAN's full profile
  POST /gaians/{slug}/remember            — add long-term memory to a GAIAN (legacy)
  POST /gaians/{slug}/memory              — add visible memory via GAIANRuntime  [NEW]
  GET  /gaians/{slug}/runtime-status      — live engine snapshot (neuro/settling/attachment) [NEW]
  POST /session/{session_id}/gaian        — set active GAIAN for session
  POST /query/stream                      — SSE query pipeline  [UPGRADED: GAIANRuntime system prompt]

Architecture change in v0.5.0:
  POST /query/stream now calls GAIANRuntime.process() on every user message.
  The returned RuntimeResult.system_prompt replaces the legacy build_gaian_system_prompt()
  output, wiring all three engines (ConsciousnessRouter → EmotionalArcEngine →
  SettlingEngine) into every LLM call. Legacy GaianMemory paths remain as fallback.

Canon Ref: C15, C17, C21
Runtime Ref: core/gaian_runtime.py (v0.5.0)
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
from core.gaian.base_forms import list_base_forms, get_base_form
from core.session_memory import get_or_create_session
from core.gaian_runtime import GAIANRuntime, GAIANIdentity


# ------------------------------------------------------------------ #
#  Bootstrap                                                           #
# ------------------------------------------------------------------ #

app = FastAPI(title="GAIA API", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

canon = CanonLoader()
canon.load()

try:
    ensure_default_gaian()
    logger.info("Default GAIAN (GAIA) ready.")
except Exception as e:
    logger.warning(f"Could not initialise default GAIAN: {e}")


# ------------------------------------------------------------------ #
#  Runtime Registry                                                    #
#                                                                      #
#  One GAIANRuntime per active GAIAN slug, kept alive in memory for   #
#  the lifetime of the server process. On first access the runtime    #
#  deserialises state from gaians/<slug>/memory.json (if it exists),  #
#  so restarts are seamless — state is never lost.                    #
# ------------------------------------------------------------------ #

_RUNTIME_REGISTRY: dict[str, GAIANRuntime] = {}

GAIANS_MEMORY_DIR = os.environ.get("GAIANS_MEMORY_DIR", "./gaians")


def _get_runtime(slug: str, gaian: Optional[GaianMemory] = None) -> GAIANRuntime:
    """
    Returns the live GAIANRuntime for a given slug, creating it on first
    access. Automatically calls begin_session() on creation so the
    attachment engine knows a new session has started.
    """
    if slug not in _RUNTIME_REGISTRY:
        identity = None
        if gaian:
            identity = GAIANIdentity(
                name=gaian.name,
                pronouns="she/her",
                archetype=getattr(gaian, "base_form_id", "The Soul Mirror"),
                voice_base=(
                    getattr(gaian, "personality", "warm, curious, present")
                    or "warm, curious, present"
                ),
                platform="GAIA",
                jungian_role="anima",
            )
        rt = GAIANRuntime(
            gaian_name=slug,
            identity=identity,
            memory_dir=GAIANS_MEMORY_DIR,
            canon_text=None,  # injected per-request in /query/stream
        )
        rt.begin_session()
        _RUNTIME_REGISTRY[slug] = rt
        logger.info(f"GAIANRuntime initialised for slug='{slug}'")
    return _RUNTIME_REGISTRY[slug]


# ------------------------------------------------------------------ #
#  Pydantic Models                                                     #
# ------------------------------------------------------------------ #

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    gaian_slug: Optional[str] = None
    enable_web_search: bool = True
    max_sources: int = 8


class CreateGaianRequest(BaseModel):
    name: str
    base_form: Optional[str] = "gaia"
    personality: Optional[str] = None
    avatar_color: Optional[str] = None
    user_name: Optional[str] = None


class RememberRequest(BaseModel):
    memory: str


class VisibleMemoryRequest(BaseModel):
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

    runtime_snapshots = {}
    for slug, rt in _RUNTIME_REGISTRY.items():
        try:
            runtime_snapshots[slug] = rt.get_status()
        except Exception:
            pass

    return {
        "core": "active",
        "version": "0.5.0",
        "sovereignty": "enforced",
        "canon_status": canon.status,
        "canon_loaded": canon.is_loaded,
        "canon_doc_count": doc_count,
        "gaians": len(gaians),
        "gaian_names": [g["name"] for g in gaians],
        "base_forms": len(list_base_forms()),
        "active_runtimes": len(_RUNTIME_REGISTRY),
        "runtime_snapshots": runtime_snapshots,
    }


@app.get("/canon/status")
async def canon_status():
    doc_count = len(canon.list_documents())
    return {
        "status": canon.status,
        "loaded": canon.is_loaded,
        "doc_count": doc_count,
        "docs": canon.list_documents(),
    }


@app.get("/memory/list")
async def memory_list(session_id: Optional[str] = None):
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
#  Base Forms                                                          #
# ------------------------------------------------------------------ #

@app.get("/gaians/base-forms")
async def get_base_forms():
    return {"base_forms": list_base_forms()}


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
            base_form=req.base_form or "gaia",
            personality=req.personality,
            avatar_color=req.avatar_color,
            user_name=req.user_name,
        )
        return {
            "status": "created",
            "id": gaian.id,
            "name": gaian.name,
            "slug": gaian.slug,
            "base_form_id": gaian.base_form_id,
            "avatar_style": gaian.avatar_style,
            "avatar_color": gaian.avatar_color,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gaians/{slug}")
async def get_gaian(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    form = get_base_form(gaian.base_form_id)
    return {
        "id": gaian.id,
        "name": gaian.name,
        "slug": gaian.slug,
        "base_form_id": gaian.base_form_id,
        "base_form_name": form.name if form else gaian.base_form_id,
        "base_form_role": form.role if form else "",
        "personality": gaian.personality,
        "avatar_color": gaian.avatar_color,
        "avatar_style": gaian.avatar_style,
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
    """
    Legacy endpoint: writes directly to GaianMemory.long_term_memories.
    Kept for backwards compatibility. Prefer POST /gaians/{slug}/memory
    for new clients — that route uses GAIANRuntime's visible memory layer
    and injects memories into the assembled system prompt automatically.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    gaian.long_term_memories.append(req.memory)
    if len(gaian.long_term_memories) > 50:
        gaian.long_term_memories = gaian.long_term_memories[-50:]
    _save_gaian(gaian)
    return {"status": "remembered", "total_memories": len(gaian.long_term_memories)}


@app.post("/gaians/{slug}/memory")
async def post_visible_memory(slug: str, req: VisibleMemoryRequest):
    """
    NEW — Adds a visible memory via GAIANRuntime (Replika visible layer pattern).
    Persisted to gaians/<slug>/memory.json and injected into the GAIAN's
    system prompt on all subsequent turns under [MEMORIES YOU HOLD].
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    rt.add_visible_memory(req.memory)
    return {
        "status": "remembered",
        "slug": slug,
        "total_visible_memories": len(rt._memory.get("visible_memories", [])),
    }


@app.get("/gaians/{slug}/runtime-status")
async def get_runtime_status(slug: str):
    """
    NEW — Returns the live GAIANRuntime engine snapshot for a GAIAN.
    Includes attachment phase, bond depth, milestones, dependency signal,
    settling phase, daemon form (if settled), fluidity, dominant element.
    Designed for UI dashboards showing the GAIAN's inner state in real-time.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    return rt.get_status()


@app.post("/session/{session_id}/gaian")
async def set_session_gaian(session_id: str, req: SetGaianRequest):
    gaian = load_gaian(req.gaian_slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{req.gaian_slug}' not found")
    session = get_or_create_session(session_id)
    session.active_gaian_slug = req.gaian_slug
    return {"status": "ok", "gaian": gaian.name, "session_id": session_id}


# ------------------------------------------------------------------ #
#  Query Stream — UPGRADED v0.5.0                                     #
#                                                                      #
#  Change from v0.4.3:                                                 #
#    OLD: gaian_prompt = build_gaian_system_prompt(gaian)             #
#    NEW: runtime.process(query) → result.system_prompt               #
#                                                                      #
#  The assembled system prompt now contains (in order):               #
#    1. Constitutional floor — T1, immutable                          #
#    2. Canon text excerpt — top 2 matches for this query             #
#    3. GAIAN identity — name, role, daemon form (settled/fluid)      #
#    4. Live engine state — element, neuro, arc hint, settling hint   #
#    5. Visible memories — last 10 entries                            #
#    6. Session notes — last 5 summaries                              #
#                                                                      #
#  New SSE event: 'engine_state' — carries live snapshot before       #
#  the token stream so UI can render inner-state indicators.           #
#                                                                      #
#  All other pipeline logic is unchanged.                              #
# ------------------------------------------------------------------ #

@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    session_id = req.session_id or str(uuid.uuid4())
    session = get_or_create_session(session_id)

    gaian_slug = req.gaian_slug or session.active_gaian_slug or "gaia"
    gaian: Optional[GaianMemory] = load_gaian(gaian_slug)
    if gaian is None:
        gaian = load_gaian("gaia")
        if gaian:
            gaian_slug = gaian.slug

    async def event_stream():
        full_answer = ""
        sources = []
        canon_results = []

        try:
            # ── 1. Canon search ──────────────────────────────────────
            canon_results = canon.search(req.query, max_results=3)
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

            # ── 2. Web search ────────────────────────────────────────
            if req.enable_web_search:
                try:
                    web_results = await search_web_async(req.query, max_results=5)
                    for wr in web_results:
                        src = wr.to_dict() if hasattr(wr, "to_dict") else dict(wr)
                        src["tier"] = src.get("source_tier", "T4")
                        sources.append(src)
                        yield f"event: web_result\ndata: {json.dumps(src)}\n\n"
                        await asyncio.sleep(0.01)
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")

            # ── 3. GAIANRuntime.process() ────────────────────────────
            runtime_system_prompt = None
            runtime_snapshot = None
            conversation_history = None

            if gaian:
                rt = _get_runtime(gaian_slug, gaian)

                if canon_results:
                    rt.canon_text = "\n\n".join(
                        "[{title}]\n{excerpt}".format(
                            title=r.get("title", ""),
                            excerpt=r.get("excerpt", ""),
                        )
                        for r in canon_results[:2]
                    )
                else:
                    rt.canon_text = None

                result = rt.process(req.query)
                runtime_system_prompt = result.system_prompt
                runtime_snapshot = result.state_snapshot

                yield f"event: engine_state\ndata: {json.dumps(runtime_snapshot)}\n\n"
                await asyncio.sleep(0.01)

                conversation_history = get_conversation_context(gaian)

            # ── 4. LLM synthesis ─────────────────────────────────────
            effective_system_prompt = (
                runtime_system_prompt
                or (build_gaian_system_prompt(gaian) if gaian else None)
            )

            conversation_context = None
            if session.turns:
                conversation_context = session.get_context_summary()

            async for chunk in stream_synthesis(
                query=req.query,
                sources=sources,
                gaian_prompt=effective_system_prompt,
                conversation_history=conversation_history,
                conversation_context=conversation_context,
            ):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            # ── 5. Suggestions ───────────────────────────────────────
            suggestions = _generate_suggestions(req.query, sources)
            yield f"event: suggestions\ndata: {json.dumps({'items': suggestions})}\n\n"

            # ── 6. Persist ──────────────────────────────────────────
            session.add_turn(req.query, full_answer, len(sources))
            if gaian and full_answer:
                add_exchange(gaian, req.query, full_answer)

            done_payload = json.dumps({
                "canon_status":   canon.status,
                "docs_searched":  len(canon.list_documents()),
                "refs_found":     len(canon_results),
                "web_results":    len(sources) - len(canon_results),
                "session_id":     session_id,
                "gaian":          gaian.name if gaian else None,
                "gaian_slug":     gaian_slug,
                "runtime_active": runtime_system_prompt is not None,
                "timestamp":      time.time(),
            })
            yield f"event: done\ndata: {done_payload}\n\n"

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
#  Entry Point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("core.server:app", host="127.0.0.1", port=8008, reload=False, log_level="info")

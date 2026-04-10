"""
GAIA API Server — FastAPI + SSE streaming v0.5.1

Endpoints:
  GET  /status                            — system health
  GET  /canon/status                      — canon status
  GET  /memory/list                       — session memory
  GET  /gaians/base-forms                 — list Base Form archetypes
  GET  /gaians                            — list user's GAIANs
  POST /gaians                            — legacy create (name + base_form only)
  POST /gaians/birth                      — [NEW v0.5.1] full birth ritual
  GET  /gaians/{slug}                     — GAIAN profile
  GET  /gaians/{slug}/identity            — [NEW v0.5.1] DID + Jungian identity record
  POST /gaians/{slug}/remember            — legacy long-term memory
  POST /gaians/{slug}/memory              — visible memory via GAIANRuntime
  GET  /gaians/{slug}/runtime-status      — live engine snapshot
  POST /session/{session_id}/gaian        — set active GAIAN
  POST /query/stream                      — SSE query pipeline

v0.5.1 change:
  POST /gaians/birth replaces POST /gaians for new user-facing GAIAN creation.
  It runs the full BirthRitual sequence:
    - Jungian role assignment (anima/animus) from user_gender
    - Cryptographic DID generation (Ed25519 via IdentityCore)
    - identity.json written to gaians/<slug>/
    - GAIANRuntime initialised + begin_session()
    - Signed birth attestation produced
    - first_words composed (base-form voice)
    - Runtime registered in _RUNTIME_REGISTRY immediately
  POST /gaians remains for legacy/internal use.

Canon Ref: C15, C17, C21
"""

import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path
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
from core.gaian_birth import BirthRitual, GaianBirthParams


# ------------------------------------------------------------------ #
#  Bootstrap                                                           #
# ------------------------------------------------------------------ #

app = FastAPI(title="GAIA API", version="0.5.1")

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
# ------------------------------------------------------------------ #

_RUNTIME_REGISTRY: dict[str, GAIANRuntime] = {}

GAIANS_MEMORY_DIR = os.environ.get("GAIANS_MEMORY_DIR", "./gaians")


def _get_runtime(slug: str, gaian: Optional[GaianMemory] = None) -> GAIANRuntime:
    """
    Returns (or creates) the live GAIANRuntime for a slug.
    On first access, checks for an identity.json to restore Jungian role/pronouns;
    falls back to anima defaults for legacy GAIANs created before v0.5.1.
    """
    if slug not in _RUNTIME_REGISTRY:
        # Try to restore Jungian identity from identity.json
        jungian_role = "anima"
        pronouns = "she/her"
        identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
        if identity_path.exists():
            try:
                id_data = json.loads(identity_path.read_text(encoding="utf-8"))
                jungian_role = id_data.get("jungian_role", "anima")
                pronouns = id_data.get("pronouns", "she/her")
            except Exception:
                pass

        identity = None
        if gaian:
            form = get_base_form(getattr(gaian, "base_form_id", "gaia"))
            identity = GAIANIdentity(
                name=gaian.name,
                pronouns=pronouns,
                archetype=form.role if form else getattr(gaian, "base_form_id", "The Soul Mirror"),
                voice_base=(
                    (form.voice_notes[:80] if form else None)
                    or getattr(gaian, "personality", "warm, curious, present")
                    or "warm, curious, present"
                ),
                platform="GAIA",
                jungian_role=jungian_role,
            )
        rt = GAIANRuntime(
            gaian_name=slug,
            identity=identity,
            memory_dir=GAIANS_MEMORY_DIR,
            canon_text=None,
        )
        rt.begin_session()
        _RUNTIME_REGISTRY[slug] = rt
        logger.info(f"GAIANRuntime initialised for slug='{slug}' jungian={jungian_role}")
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
    """Legacy create request — use BirthRequest for new GAIAN creation."""
    name: str
    base_form: Optional[str] = "gaia"
    personality: Optional[str] = None
    avatar_color: Optional[str] = None
    user_name: Optional[str] = None


class BirthRequest(BaseModel):
    """
    Full birth request — drives the complete BirthRitual sequence.

    name            The GAIAN's name (required)
    user_name       The human's name (optional — GAIAN uses it in first_words)
    user_gender     "male" | "female" | "non-binary" | "prefer not" | "unknown"
                    Drives contrasexual Jungian role assignment.
                    Defaults to "unknown" if omitted (safe — assigns anima).
    base_form       Which archetype to instantiate from
    personality     Optional personality override
    avatar_color    Optional color override
    user_id         Platform user ID — bound into the GAIAN's DID
    """
    name:        str
    user_name:   Optional[str] = None
    user_gender: str           = "unknown"
    base_form:   str           = "gaia"
    personality: Optional[str] = None
    avatar_color: Optional[str] = None
    user_id:     str           = "anonymous"


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
        "version": "0.5.1",
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
    """
    Legacy endpoint: creates a GAIAN without full birth ritual.
    No DID, no Jungian assignment, no first_words.
    Use POST /gaians/birth for user-facing creation.
    """
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


@app.post("/gaians/birth")
async def post_birth_gaian(req: BirthRequest):
    """
    NEW v0.5.1 — Full GAIAN birth ritual.

    Runs the complete BirthRitual sequence:
      1. Jungian role assignment from user_gender
         (male → anima she/her, female → animus he/him, other → anima)
      2. GaianMemory created and persisted
      3. Ed25519 cryptographic DID generated
      4. identity.json written to gaians/<slug>/identity.json
      5. GAIANRuntime initialised + registered + begin_session()
      6. Signed birth attestation produced
      7. first_words composed (base-form voice, personalised)

    The GAIAN is immediately live — its runtime is registered and
    ready to process the first /query/stream call.

    Returns:
      status, gaian metadata, jungian_role, did, first_words,
      born_at, attestation summary
    """
    # Duplicate name check
    existing = load_gaian(req.name.lower().replace(" ", "_")[:24])
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A GAIAN named '{req.name}' already exists (slug: {existing.slug}). "
                   f"Choose a different name or use GET /gaians/{existing.slug}."
        )

    try:
        params = GaianBirthParams(
            name=req.name,
            user_name=req.user_name,
            user_gender=req.user_gender,
            base_form=req.base_form,
            personality=req.personality,
            avatar_color=req.avatar_color,
            user_id=req.user_id,
        )
        result = BirthRitual().perform(params)

        # Register runtime immediately — first /query/stream call is instant
        _RUNTIME_REGISTRY[result.gaian.slug] = result.runtime
        logger.info(
            f"GAIAN born: slug='{result.gaian.slug}' "
            f"jungian={result.jungian_role} DID={result.did[:20]}..."
        )

        return {
            "status":       "born",
            "id":           result.gaian.id,
            "name":         result.gaian.name,
            "slug":         result.gaian.slug,
            "base_form_id": result.gaian.base_form_id,
            "avatar_color": result.gaian.avatar_color,
            "avatar_style": result.gaian.avatar_style,
            "jungian_role": result.jungian_role,
            "pronouns":     "she/her" if result.jungian_role == "anima" else "he/him",
            "did":          result.did,
            "first_words":  result.first_words,
            "born_at":      result.born_at,
            "identity_path": result.identity_path,
            "attestation": {
                "type":    result.attestation["claims"]["type"],
                "issued":  result.attestation["issued"],
                "issuer":  result.attestation["issuer"],
                "proof_type": result.attestation["proof"]["type"],
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Birth ritual failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Birth ritual failed: {str(e)}")


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


@app.get("/gaians/{slug}/identity")
async def get_gaian_identity(slug: str):
    """
    NEW v0.5.1 — Returns the GAIAN's cryptographic identity record.
    Read from gaians/<slug>/identity.json — written at birth.
    Returns 404 if the GAIAN was created before v0.5.1 (no identity.json).
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")

    identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
    if not identity_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"GAIAN '{slug}' has no identity.json — it was created before v0.5.1. "
                f"Use POST /gaians/birth to create a new GAIAN with full identity."
            )
        )
    try:
        return json.loads(identity_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read identity: {e}")


@app.post("/gaians/{slug}/remember")
async def post_remember(slug: str, req: RememberRequest):
    """
    Legacy: writes to GaianMemory.long_term_memories.
    Prefer POST /gaians/{slug}/memory for new clients.
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
    """Add a visible memory via GAIANRuntime (Replika visible layer)."""
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
    """Live GAIANRuntime engine snapshot — attachment, settling, neuro, element."""
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
#  Query Stream (v0.5.0 — unchanged from previous commit)             #
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

            suggestions = _generate_suggestions(req.query, sources)
            yield f"event: suggestions\ndata: {json.dumps({'items': suggestions})}\n\n"

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

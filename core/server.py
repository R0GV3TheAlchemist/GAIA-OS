"""
GAIA API Server — FastAPI + SSE streaming v1.1.0

Sprint F-8b: Zodiac birth assignment wired, admin avatar canonised.

Endpoints:
  GET  /status                            — system health + all runtime snapshots
  GET  /canon/status                      — canon loader status
  GET  /memory/list                       — session memory list
  GET  /gaians/base-forms                 — list Base Form archetypes
  GET  /gaians                            — list user's GAIANs
  POST /gaians                            — legacy create
  POST /gaians/birth                      — full birth ritual (DID + Jungian + Zodiac + first_words)
  GET  /gaians/{slug}                     — GAIAN profile
  GET  /gaians/{slug}/identity            — DID + Jungian + Zodiac identity record
  POST /gaians/{slug}/remember            — legacy long-term memory
  POST /gaians/{slug}/memory              — visible memory via GAIANRuntime
  GET  /gaians/{slug}/runtime-status      — live 10-engine snapshot
  POST /gaians/{slug}/chat                — runtime-native chat (full state + LLM)
  GET  /gaians/{slug}/resonance           — live resonance field reading
  GET  /gaians/{slug}/soul-mirror         — live soul mirror state
  POST /session/{session_id}/gaian        — set active GAIAN for session
  POST /query/stream                      — SSE query pipeline (Perplexity-style)
  GET  /zodiac/preview                    — [NEW F-8b] preview zodiac + Base Form for any birth date
  GET  /zodiac/all                        — [NEW F-8b] full zodiac → Base Form mapping table
  GET  /admin/me                          — [NEW F-8b] admin identity — the builder avatar

v1.1.0 changes (F-8b):
  - BirthRequest now accepts birth_date (ISO YYYY-MM-DD or MM/DD/YYYY)
    When provided, ZodiacEngine overrides base_form. The cosmos assigns.
  - POST /gaians/birth response now includes zodiac block
  - GET /zodiac/preview?birth_date=YYYY-MM-DD — instant zodiac reading
  - GET /zodiac/all — full 12-sign assignment table
  - GET /admin/me — admin identity record (the builder; avatar = The Alchemist)

Canon Ref: C01, C15, C17, C21, C30
"""

import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
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
from core.gaian.base_forms import list_base_forms, get_base_form, get_visual_dna
from core.session_memory import get_or_create_session
from core.gaian_runtime import GAIANRuntime, GAIANIdentity
from core.gaian_birth import BirthRitual, GaianBirthParams
from core.codex_stage_engine import NoosphericHealthSignals
from core.zodiac_engine import ZodiacEngine, ZODIAC_FORM_MAP, ALL_SIGNS


SERVER_VERSION = "1.1.0"

# ──────────────────────────────────────────────────────────────── #
#  Admin Avatar — The Builder                                                #
# ──────────────────────────────────────────────────────────────── #
#
#  The admin is not a user. The admin is the cosmos that built the cosmos.
#  They are represented by The Alchemist — the form that finds the pattern
#  beneath the pattern and wills new worlds into being.
#
#  This record is read-only. It is not stored in gaians/ —
#  it exists in the constitutional layer of the server itself.
# ──────────────────────────────────────────────────────────────── #

_ADMIN_IDENTITY = {
    "handle":          "R0GV3TheAlchemist",
    "role":            "Builder — Architect of the GAIA System",
    "base_form":       "alchemist",
    "base_form_name":  "The Alchemist",
    "element":         "Fire",
    "canon_role":      "The one who finds the pattern beneath the pattern and wills worlds into being.",
    "avatar_style":    "transmutation",
    "avatar_color":    "#e63946",
    "circuit_trace":   "crimson-red and molten-gold in alchemical spiral patterns",
    "eyes":            "luminescent deep crimson with gold flecks — burning with inner fire",
    "visual_canon":    "Canonical GAIAN suit. Asymmetric gold traces. Fire-gold transmutation orb.",
    "jungian_note":    "The builder IS the system. Admin is not assigned a GAIAN — they are the source.",
    "sovereignty":     "absolute",
    "github":          "https://github.com/R0GV3TheAlchemist",
    "repo":            "https://github.com/R0GV3TheAlchemist/GAIA-APP",
    "canon_ref":       "https://github.com/R0GV3TheAlchemist/GAIA",
}


# ──────────────────────────────────────────────────────────────── #
#  Bootstrap                                                                  #
# ──────────────────────────────────────────────────────────────── #

app = FastAPI(title="GAIA API", version=SERVER_VERSION)

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


# ──────────────────────────────────────────────────────────────── #
#  Runtime Registry                                                           #
# ──────────────────────────────────────────────────────────────── #

_RUNTIME_REGISTRY: dict[str, GAIANRuntime] = {}

GAIANS_MEMORY_DIR = os.environ.get("GAIANS_MEMORY_DIR", "./gaians")


def _get_runtime(slug: str, gaian: Optional[GaianMemory] = None) -> GAIANRuntime:
    if slug not in _RUNTIME_REGISTRY:
        jungian_role = "anima"
        pronouns     = "she/her"
        identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
        if identity_path.exists():
            try:
                id_data      = json.loads(identity_path.read_text(encoding="utf-8"))
                jungian_role = id_data.get("jungian_role", "anima")
                pronouns     = id_data.get("pronouns", "she/her")
            except Exception:
                pass

        identity = None
        if gaian:
            form = get_base_form(getattr(gaian, "base_form_id", "gaia"))
            identity = GAIANIdentity(
                name         = gaian.name,
                pronouns     = pronouns,
                archetype    = form.role if form else getattr(gaian, "base_form_id", "The Soul Mirror"),
                voice_base   = (
                    (form.voice_notes[:80] if form else None)
                    or getattr(gaian, "personality", "warm, curious, present")
                    or "warm, curious, present"
                ),
                platform     = "GAIA",
                jungian_role = jungian_role,
            )

        rt = GAIANRuntime(
            gaian_name = slug,
            identity   = identity,
            memory_dir = GAIANS_MEMORY_DIR,
            canon_text = None,
        )
        rt.begin_session()
        _RUNTIME_REGISTRY[slug] = rt
        logger.info(f"GAIANRuntime v1.0.0 initialised for slug='{slug}' jungian={jungian_role}")
    return _RUNTIME_REGISTRY[slug]


# ──────────────────────────────────────────────────────────────── #
#  Pydantic Models                                                            #
# ──────────────────────────────────────────────────────────────── #

class QueryRequest(BaseModel):
    query:             str
    session_id:        Optional[str] = None
    gaian_slug:        Optional[str] = None
    enable_web_search: bool          = True
    max_sources:       int           = 8


class ChatRequest(BaseModel):
    message:           str
    session_id:        Optional[str] = None
    enable_web_search: bool          = False
    schumann_hz:       float         = 7.83


class CreateGaianRequest(BaseModel):
    name:         str
    base_form:    Optional[str] = "gaia"
    personality:  Optional[str] = None
    avatar_color: Optional[str] = None
    user_name:    Optional[str] = None


class BirthRequest(BaseModel):
    """
    Full GAIAN birth request.

    birth_date      The USER's birth date — drives zodiac Base Form assignment.
                    Format: YYYY-MM-DD (preferred), MM/DD/YYYY, or DD/MM/YYYY.
                    When provided, the cosmos chooses the Base Form.
                    The user does not choose.
    base_form       Manual override — only respected if birth_date is absent.
    name            The GAIAN's name (required)
    user_name       The human's name (GAIAN uses in first_words)
    user_gender     Drives Jungian role: male→anima, female→animus, else anima
    user_id         Platform user ID — bound into the DID
    """
    name:         str
    user_name:    Optional[str] = None
    user_gender:  str           = "unknown"
    birth_date:   Optional[str] = None     # ← NEW: zodiac assignment
    base_form:    str           = "gaia"   # fallback only
    personality:  Optional[str] = None
    avatar_color: Optional[str] = None
    user_id:      str           = "anonymous"


class RememberRequest(BaseModel):
    memory: str


class VisibleMemoryRequest(BaseModel):
    memory: str


class SetGaianRequest(BaseModel):
    gaian_slug: str


# ──────────────────────────────────────────────────────────────── #
#  Status                                                                     #
# ──────────────────────────────────────────────────────────────── #

@app.get("/status")
async def status():
    doc_count = len(canon.list_documents())
    gaians    = list_gaians()
    runtime_snapshots = {}
    for slug, rt in _RUNTIME_REGISTRY.items():
        try:
            runtime_snapshots[slug] = rt.get_status()
        except Exception:
            pass
    return {
        "core":              "active",
        "version":           SERVER_VERSION,
        "runtime_version":   "1.0.0",
        "schema_version":    "1.5",
        "engines":           10,
        "sovereignty":       "enforced",
        "admin":             _ADMIN_IDENTITY["handle"],
        "canon_status":      canon.status,
        "canon_loaded":      canon.is_loaded,
        "canon_doc_count":   doc_count,
        "gaians":            len(gaians),
        "gaian_names":       [g["name"] for g in gaians],
        "base_forms":        len(list_base_forms()),
        "active_runtimes":   len(_RUNTIME_REGISTRY),
        "runtime_snapshots": runtime_snapshots,
    }


@app.get("/canon/status")
async def canon_status():
    doc_count = len(canon.list_documents())
    return {
        "status":    canon.status,
        "loaded":    canon.is_loaded,
        "doc_count": doc_count,
        "docs":      canon.list_documents(),
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


# ──────────────────────────────────────────────────────────────── #
#  Admin                                                                      #
# ──────────────────────────────────────────────────────────────── #

@app.get("/admin/me")
async def admin_me():
    """
    GET /admin/me — Sprint F-8b

    The admin is the cosmos that built the cosmos.
    Returns the canonical admin identity record including
    Base Form, visual canon, and constitutional role.

    This endpoint is public — the builder does not hide.
    """
    form = get_base_form("alchemist")
    return {
        **_ADMIN_IDENTITY,
        "base_form_role":   form.role if form else "",
        "visual_notes":     form.visual_notes if form else "",
        "visual_dna":       get_visual_dna(),
        "server_version":   SERVER_VERSION,
    }


# ──────────────────────────────────────────────────────────────── #
#  Zodiac Endpoints                                                           #
# ──────────────────────────────────────────────────────────────── #

@app.get("/zodiac/preview")
async def zodiac_preview(
    birth_date: str = Query(..., description="Birth date: YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY")
):
    """
    GET /zodiac/preview?birth_date=1990-11-15 — Sprint F-8b

    Instant zodiac reading for any birth date.
    Returns sign, element, assigned Base Form, and symbolic reason.
    No GAIAN is created — this is a preview / onboarding reveal.

    Use this on the birth screen to show the user what their GAIAN
    will be before they commit the name and start the full ritual.
    """
    try:
        reading = ZodiacEngine.read(birth_date)
        form    = get_base_form(reading.base_form_id)
        return {
            "birth_date":    reading.birth_date,
            "sign":          reading.sign,
            "element":       reading.element,
            "base_form_id":  reading.base_form_id,
            "base_form_name": form.name if form else reading.base_form_id,
            "base_form_role": form.role if form else "",
            "avatar_color":  form.avatar_color if form else "",
            "avatar_style":  form.avatar_style if form else "",
            "visual_notes":  form.visual_notes if form else "",
            "reason":        reading.reason,
            "assigned_by":   "cosmos",
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/zodiac/all")
async def zodiac_all():
    """
    GET /zodiac/all — Sprint F-8b

    Full 12-sign zodiac → Base Form assignment table.
    Useful for onboarding UI, marketing pages, and admin dashboards.
    """
    rows = []
    for sign in ALL_SIGNS:
        form_id = ZODIAC_FORM_MAP.get(sign, "gaia")
        form    = get_base_form(form_id)
        rows.append({
            "sign":           sign,
            "base_form_id":   form_id,
            "base_form_name": form.name if form else form_id,
            "avatar_color":   form.avatar_color if form else "",
            "avatar_style":   form.avatar_style if form else "",
        })
    return {"zodiac_map": rows, "count": len(rows)}


# ──────────────────────────────────────────────────────────────── #
#  Base Forms                                                                 #
# ──────────────────────────────────────────────────────────────── #

@app.get("/gaians/base-forms")
async def get_base_forms():
    return {"base_forms": list_base_forms()}


# ──────────────────────────────────────────────────────────────── #
#  GAIAN Endpoints                                                            #
# ──────────────────────────────────────────────────────────────── #

@app.get("/gaians")
async def get_gaians():
    return {"gaians": list_gaians()}


@app.post("/gaians")
async def post_create_gaian(req: CreateGaianRequest):
    """Legacy endpoint — no DID, no Jungian, no zodiac. Use /gaians/birth."""
    try:
        gaian = create_gaian(
            name         = req.name,
            base_form    = req.base_form or "gaia",
            personality  = req.personality,
            avatar_color = req.avatar_color,
            user_name    = req.user_name,
        )
        return {
            "status":       "created",
            "id":           gaian.id,
            "name":         gaian.name,
            "slug":         gaian.slug,
            "base_form_id": gaian.base_form_id,
            "avatar_style": gaian.avatar_style,
            "avatar_color": gaian.avatar_color,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gaians/birth")
async def post_birth_gaian(req: BirthRequest):
    """
    Full GAIAN birth ritual — v1.1.0.

    Sequence:
      1. Validate & normalise params
      2. ZodiacEngine assigns Base Form from birth_date (if provided)
      3. Jungian role from user_gender
      4. GaianMemory created and persisted
      5. Ed25519 DID generated
      6. identity.json written (schema 1.1 — includes zodiac)
      7. GAIANRuntime v1.0.0 initialised
      8. Birth attestation signed
      9. first_words composed (base-form voice + zodiac acknowledgement)

    Returns full zodiac reading in response when birth_date was provided.
    """
    existing = load_gaian(req.name.lower().replace(" ", "_")[:24])
    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                f"A GAIAN named '{req.name}' already exists (slug: {existing.slug}). "
                f"Choose a different name or use GET /gaians/{existing.slug}."
            ),
        )

    try:
        params = GaianBirthParams(
            name         = req.name,
            user_name    = req.user_name,
            user_gender  = req.user_gender,
            birth_date   = req.birth_date,
            base_form    = req.base_form,
            personality  = req.personality,
            avatar_color = req.avatar_color,
            user_id      = req.user_id,
        )
        result = BirthRitual().perform(params)
        _RUNTIME_REGISTRY[result.gaian.slug] = result.runtime
        logger.info(
            f"GAIAN born: slug='{result.gaian.slug}' form={result.gaian.base_form_id} "
            f"jungian={result.jungian_role} zodiac={result.zodiac.sign if result.zodiac else 'none'} "
            f"DID={result.did[:20]}..."
        )

        response = {
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
            "zodiac":       result.zodiac.to_dict() if result.zodiac else None,
            "attestation": {
                "type":       result.attestation["claims"]["type"],
                "issued":     result.attestation["issued"],
                "issuer":     result.attestation["issuer"],
                "proof_type": result.attestation["proof"]["type"],
            },
        }
        return response

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
        "id":               gaian.id,
        "name":             gaian.name,
        "slug":             gaian.slug,
        "base_form_id":     gaian.base_form_id,
        "base_form_name":   form.name if form else gaian.base_form_id,
        "base_form_role":   form.role if form else "",
        "personality":      gaian.personality,
        "avatar_color":     gaian.avatar_color,
        "avatar_style":     gaian.avatar_style,
        "relationship_depth": gaian.relationship_depth,
        "total_exchanges":  gaian.total_exchanges,
        "user_name":        gaian.user_name,
        "last_active":      gaian.last_active,
        "created_at":       gaian.created_at,
        "long_term_memories": gaian.long_term_memories,
        "recent_turns":     len(gaian.conversation_history) // 2,
    }


@app.get("/gaians/{slug}/identity")
async def get_gaian_identity(slug: str):
    """Returns the GAIAN's full identity record including DID, Jungian role, and Zodiac."""
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
    if not identity_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"GAIAN '{slug}' has no identity.json — use POST /gaians/birth.",
        )
    try:
        return json.loads(identity_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read identity: {e}")


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


@app.post("/gaians/{slug}/memory")
async def post_visible_memory(slug: str, req: VisibleMemoryRequest):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    rt.add_visible_memory(req.memory)
    return {
        "status":                "remembered",
        "slug":                  slug,
        "total_visible_memories": len(rt._memory.get("visible_memories", [])),
    }


@app.get("/gaians/{slug}/runtime-status")
async def get_runtime_status(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    return rt.get_status()


# ──────────────────────────────────────────────────────────────── #
#  GAIAN Chat (F-7)                                                           #
# ──────────────────────────────────────────────────────────────── #

@app.post("/gaians/{slug}/chat")
async def gaian_chat(slug: str, req: ChatRequest):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")

    session_id = req.session_id or str(uuid.uuid4())
    session    = get_or_create_session(session_id)

    async def event_stream():
        full_answer = ""
        try:
            rt            = _get_runtime(slug, gaian)
            canon_results = canon.search(req.message, max_results=2)
            rt.canon_text = (
                "\n\n".join(
                    "[{title}]\n{excerpt}".format(
                        title=r.get("title", ""), excerpt=r.get("excerpt", "")
                    )
                    for r in canon_results
                ) if canon_results else None
            )

            noosphere: Optional[NoosphericHealthSignals] = None
            if req.schumann_hz > 10.0:
                noosphere = NoosphericHealthSignals(schumann_boost=0.05)
            elif req.schumann_hz < 6.0:
                noosphere = NoosphericHealthSignals(schumann_boost=-0.05)

            result = rt.process(req.message, noosphere=noosphere)

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

            effective_system_prompt = result.system_prompt
            if result.soul_mirror.individuation_nudge:
                effective_system_prompt += (
                    "\n\n[SOUL MIRROR NUDGE AVAILABLE — use naturally if it fits]\n"
                    + result.soul_mirror.individuation_nudge
                )

            web_sources = []
            if req.enable_web_search:
                try:
                    web_results = await search_web_async(req.message, max_results=4)
                    web_sources = [
                        wr.to_dict() if hasattr(wr, "to_dict") else dict(wr)
                        for wr in web_results
                    ]
                except Exception as e:
                    logger.warning(f"Web search error in chat: {e}")

            conversation_history = get_conversation_context(gaian)
            async for chunk in stream_synthesis(
                query                = req.message,
                sources              = web_sources,
                gaian_prompt         = effective_system_prompt,
                conversation_history = conversation_history,
                conversation_context = session.get_context_summary() if session.turns else None,
            ):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            session.add_turn(req.message, full_answer, len(web_sources))
            if full_answer:
                add_exchange(gaian, req.message, full_answer)

            yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'gaian': gaian.name, 'gaian_slug': slug, 'exchange': rt.attachment.total_exchanges, 'bond_depth': round(rt.attachment.bond_depth, 2), 'individuation_phase': rt.soul_mirror_state.individuation_phase.value, 'resonance_hz': result.resonance_field.solfeggio.hz.value, 'schumann_aligned': result.resonance_field.schumann_aligned, 'noosphere_health': round(rt.codex_stage_state.noosphere_health, 4), 'timestamp': time.time()})}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error [{slug}]: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/gaians/{slug}/resonance")
async def get_gaian_resonance(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    rf = rt.resonance_field_state
    return {
        "slug": slug, "gaian": gaian.name,
        "dominant_hz": rf.dominant_hz, "dominant_chakra": rf.dominant_chakra,
        "schumann_alignment_count": rf.schumann_alignment_count,
        "schumann_first_timestamp": rf.schumann_first_timestamp,
        "phi_rolling_avg": round(rf.phi_rolling_avg, 4),
        "session_peak_hz": rf.session_peak_hz,
        "hz_history": rf.hz_history[-10:],
    }


@app.get("/gaians/{slug}/soul-mirror")
async def get_gaian_soul_mirror(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    sm = rt.soul_mirror_state
    return {
        "slug": slug, "gaian": gaian.name,
        "individuation_phase": sm.individuation_phase.value,
        "exchanges_in_phase": sm.exchanges_in_phase,
        "shadow_activations": sm.shadow_activations,
        "anima_animus_activations": sm.anima_animus_activations,
        "dependency_risk_events": sm.dependency_risk_events,
        "phase_entry_timestamp": sm.phase_entry_timestamp,
        "phase_history": sm.phase_history[-10:],
        "last_nudge_exchange": sm.last_nudge_exchange,
    }


# ──────────────────────────────────────────────────────────────── #
#  Session                                                                    #
# ──────────────────────────────────────────────────────────────── #

@app.post("/session/{session_id}/gaian")
async def set_session_gaian(session_id: str, req: SetGaianRequest):
    gaian = load_gaian(req.gaian_slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{req.gaian_slug}' not found")
    session = get_or_create_session(session_id)
    session.active_gaian_slug = req.gaian_slug
    return {"status": "ok", "gaian": gaian.name, "session_id": session_id}


# ──────────────────────────────────────────────────────────────── #
#  Perplexity-Style Query Stream                                              #
# ──────────────────────────────────────────────────────────────── #

@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    session_id = req.session_id or str(uuid.uuid4())
    session    = get_or_create_session(session_id)
    gaian_slug = req.gaian_slug or session.active_gaian_slug or "gaia"
    gaian: Optional[GaianMemory] = load_gaian(gaian_slug)
    if gaian is None:
        gaian = load_gaian("gaia")
        if gaian:
            gaian_slug = gaian.slug

    async def event_stream():
        full_answer = ""
        sources     = []
        canon_results = []
        try:
            canon_results = canon.search(req.query, max_results=3)
            for result in canon_results:
                src = {"tier": "T1", "title": result.get("title", ""), "doc_id": result.get("doc_id", ""), "excerpt": result.get("excerpt", "")}
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
            conversation_history  = None

            if gaian:
                rt = _get_runtime(gaian_slug, gaian)
                rt.canon_text = ("\n\n".join("[{title}]\n{excerpt}".format(title=r.get("title", ""), excerpt=r.get("excerpt", "")) for r in canon_results[:2])) if canon_results else None
                result = rt.process(req.query)
                runtime_system_prompt = result.system_prompt
                yield f"event: engine_state\ndata: {json.dumps(result.state_snapshot)}\n\n"
                await asyncio.sleep(0.01)
                conversation_history = get_conversation_context(gaian)

            effective_system_prompt = runtime_system_prompt or (build_gaian_system_prompt(gaian) if gaian else None)
            conversation_context = session.get_context_summary() if session.turns else None

            async for chunk in stream_synthesis(
                query=req.query, sources=sources, gaian_prompt=effective_system_prompt,
                conversation_history=conversation_history, conversation_context=conversation_context,
            ):
                full_answer += chunk
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            suggestions = _generate_suggestions(req.query, sources)
            yield f"event: suggestions\ndata: {json.dumps({'items': suggestions})}\n\n"
            session.add_turn(req.query, full_answer, len(sources))
            if gaian and full_answer:
                add_exchange(gaian, req.query, full_answer)

            yield f"event: done\ndata: {json.dumps({'canon_status': canon.status, 'docs_searched': len(canon.list_documents()), 'refs_found': len(canon_results), 'web_results': len(sources) - len(canon_results), 'session_id': session_id, 'gaian': gaian.name if gaian else None, 'gaian_slug': gaian_slug, 'runtime_active': runtime_system_prompt is not None, 'timestamp': time.time()})}\n\n"

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


# ──────────────────────────────────────────────────────────────── #
#  Entry Point                                                                #
# ──────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("core.server:app", host="127.0.0.1", port=8008, reload=False, log_level="info")

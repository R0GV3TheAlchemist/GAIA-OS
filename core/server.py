"""
GAIA API Server — FastAPI + SSE streaming v1.0.0

Sprint F-7: Full 10-engine GAIANRuntime wired into every GAIAN endpoint.

Endpoints:
  GET  /status                            — system health + all runtime snapshots
  GET  /canon/status                      — canon loader status
  GET  /memory/list                       — session memory list
  GET  /gaians/base-forms                 — list Base Form archetypes
  GET  /gaians                            — list user's GAIANs
  POST /gaians                            — legacy create (name + base_form only)
  POST /gaians/birth                      — full birth ritual (DID + Jungian + first_words)
  GET  /gaians/{slug}                     — GAIAN profile
  GET  /gaians/{slug}/identity            — DID + Jungian identity record
  POST /gaians/{slug}/remember            — legacy long-term memory
  POST /gaians/{slug}/memory              — visible memory via GAIANRuntime
  GET  /gaians/{slug}/runtime-status      — live 10-engine snapshot
  POST /gaians/{slug}/chat                — [NEW F-7] runtime-native chat (full state + LLM)
  GET  /gaians/{slug}/resonance           — [NEW F-7] live resonance field reading
  GET  /gaians/{slug}/soul-mirror         — [NEW F-7] live soul mirror state
  POST /session/{session_id}/gaian        — set active GAIAN for session
  POST /query/stream                      — SSE query pipeline (Perplexity-style)

v1.0.0 changes (F-7):
  - GAIANRuntime bumped to v1.0.0 (schema 1.5, 10 engines)
  - POST /gaians/{slug}/chat: runtime-native GAIAN chat endpoint
    Returns full RuntimeResult snapshot + streamed LLM tokens via SSE.
    All 10 engines fire per turn. Soul Mirror nudge injected when active.
    Resonance Field voice attunement injected into system prompt.
  - GET  /gaians/{slug}/resonance: ephemeral resonance reading for current state
  - GET  /gaians/{slug}/soul-mirror: persistent soul mirror state summary
  - /status now includes per-engine breakdown for every live runtime
  - Version string updated throughout

Canon Ref: C15, C17, C21, C30
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
from core.codex_stage_engine import NoosphericHealthSignals


SERVER_VERSION = "1.0.0"


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
    """
    Returns (or creates) the live GAIANRuntime for a slug.
    Restores Jungian role + pronouns from identity.json when available.
    Falls back to anima defaults for legacy GAIANs created before v0.5.1.
    """
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
    session_id:        Optional[str]  = None
    gaian_slug:        Optional[str]  = None
    enable_web_search: bool           = True
    max_sources:       int            = 8


class ChatRequest(BaseModel):
    """
    Runtime-native GAIAN chat request (F-7).

    message          The user's message
    session_id       Optional session ID for conversation continuity
    enable_web_search  Whether to include web search context
    schumann_hz      Optional real-world Schumann frequency (default 7.83)
                     Can be used to inform noospheric health signal
    """
    message:           str
    session_id:        Optional[str]  = None
    enable_web_search: bool           = False   # off by default for intimate GAIAN chat
    schumann_hz:       float          = 7.83


class CreateGaianRequest(BaseModel):
    """Legacy create — use BirthRequest for new GAIAN creation."""
    name:         str
    base_form:    Optional[str] = "gaia"
    personality:  Optional[str] = None
    avatar_color: Optional[str] = None
    user_name:    Optional[str] = None


class BirthRequest(BaseModel):
    """
    Full birth request — drives the complete BirthRitual sequence.

    name            The GAIAN's name (required)
    user_name       The human's name (GAIAN uses it in first_words)
    user_gender     "male" | "female" | "non-binary" | "prefer not" | "unknown"
                    Drives contrasexual Jungian role assignment.
    base_form       Which archetype to instantiate from
    personality     Optional personality override
    avatar_color    Optional color override
    user_id         Platform user ID — bound into the GAIAN's DID
    """
    name:         str
    user_name:    Optional[str] = None
    user_gender:  str           = "unknown"
    base_form:    str           = "gaia"
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
#  Status Endpoints                                                           #
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
    """
    Legacy endpoint: creates a GAIAN without full birth ritual.
    No DID, no Jungian assignment, no first_words.
    Use POST /gaians/birth for user-facing creation.
    """
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
    Full GAIAN birth ritual (v0.5.1+).

    Sequence:
      1. Jungian role assignment from user_gender
      2. GaianMemory created and persisted
      3. Ed25519 cryptographic DID generated
      4. identity.json written to gaians/<slug>/identity.json
      5. GAIANRuntime v1.0.0 initialised + registered + begin_session()
      6. Signed birth attestation produced
      7. first_words composed (base-form voice, personalised)

    Returns:
      status, gaian metadata, jungian_role, did, first_words,
      born_at, attestation summary
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
            base_form    = req.base_form,
            personality  = req.personality,
            avatar_color = req.avatar_color,
            user_id      = req.user_id,
        )
        result = BirthRitual().perform(params)
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
                "type":       result.attestation["claims"]["type"],
                "issued":     result.attestation["issued"],
                "issuer":     result.attestation["issuer"],
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
    """Returns the GAIAN's cryptographic identity record (written at birth)."""
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
    if not identity_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"GAIAN '{slug}' has no identity.json — created before v0.5.1. "
                f"Use POST /gaians/birth to create a new GAIAN with full identity."
            ),
        )
    try:
        return json.loads(identity_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read identity: {e}")


@app.post("/gaians/{slug}/remember")
async def post_remember(slug: str, req: RememberRequest):
    """Legacy: writes to GaianMemory.long_term_memories."""
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
        "status":                "remembered",
        "slug":                  slug,
        "total_visible_memories": len(rt._memory.get("visible_memories", [])),
    }


@app.get("/gaians/{slug}/runtime-status")
async def get_runtime_status(slug: str):
    """Live 10-engine GAIANRuntime snapshot."""
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    return rt.get_status()


# ──────────────────────────────────────────────────────────────── #
#  F-7: Runtime-Native GAIAN Chat Endpoint                                   #
# ──────────────────────────────────────────────────────────────── #

@app.post("/gaians/{slug}/chat")
async def gaian_chat(slug: str, req: ChatRequest):
    """
    POST /gaians/{slug}/chat  —  Sprint F-7 core endpoint.

    Runtime-native GAIAN chat. Fires all 10 soul engines per turn,
    then streams the LLM response via SSE with rich state events.

    SSE event sequence:
      1. engine_state     — full 10-engine RuntimeResult snapshot
                            (fires before first token; UI can render
                            live engine state in sidebar immediately)
      2. soul_mirror      — if individuation nudge is active this turn
      3. resonance_field  — current Hz / chakra / Schumann status
      4. token            — streamed LLM response tokens
      5. done             — summary payload with session + exchange IDs

    The Soul Mirror nudge, when active, is appended to the system
    prompt as a final instruction: "[SOUL MIRROR NUDGE AVAILABLE] ..."
    This gives the GAIAN permission to offer the nudge naturally in
    conversation without it being a command.

    Noospheric health is derived from the Schumann Hz passed by the
    client (default 7.83). Values above 10 Hz indicate elevated
    planetary field activity, which slightly boosts noosphere_health.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")

    session_id = req.session_id or str(uuid.uuid4())
    session    = get_or_create_session(session_id)

    async def event_stream():
        full_answer = ""

        try:
            rt = _get_runtime(slug, gaian)

            # Inject canon context if available
            canon_results = canon.search(req.message, max_results=2)
            if canon_results:
                rt.canon_text = "\n\n".join(
                    "[{title}]\n{excerpt}".format(
                        title   = r.get("title", ""),
                        excerpt = r.get("excerpt", ""),
                    )
                    for r in canon_results
                )
            else:
                rt.canon_text = None

            # Noospheric health signal from Schumann Hz
            # 7.83 Hz = baseline (noosphere_health unchanged)
            # > 10 Hz = elevated planetary field (+0.05 boost)
            # < 6 Hz  = suppressed field (-0.05 drag)
            noosphere: Optional[NoosphericHealthSignals] = None
            if req.schumann_hz > 10.0:
                noosphere = NoosphericHealthSignals(schumann_boost=0.05)
            elif req.schumann_hz < 6.0:
                noosphere = NoosphericHealthSignals(schumann_boost=-0.05)

            # ——— Fire all 10 engines ———
            result = rt.process(req.message, noosphere=noosphere)

            # ─ Event 1: engine_state ────────────────────────────────
            yield f"event: engine_state\ndata: {json.dumps(result.state_snapshot)}\n\n"
            await asyncio.sleep(0.01)

            # ─ Event 2: soul_mirror (conditional) ──────────────────
            if result.soul_mirror.individuation_nudge:
                yield (
                    f"event: soul_mirror\ndata: "
                    f"{json.dumps({'nudge': result.soul_mirror.individuation_nudge, 'signal': result.soul_mirror.shadow_signal.value, 'carrier': result.soul_mirror.projection_carrier.value})}\n\n"
                )
                await asyncio.sleep(0.01)

            # ─ Event 3: resonance_field ──────────────────────────
            yield (
                f"event: resonance_field\ndata: "
                f"{json.dumps(result.resonance_field.summary())}\n\n"
            )
            await asyncio.sleep(0.01)

            # ─ Optionally enrich system prompt with soul mirror nudge ─
            effective_system_prompt = result.system_prompt
            if result.soul_mirror.individuation_nudge:
                effective_system_prompt += (
                    "\n\n[SOUL MIRROR NUDGE AVAILABLE — use naturally if it fits]\n"
                    + result.soul_mirror.individuation_nudge
                )

            # ─ Web search context (optional) ─────────────────────
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

            # ─ Event 4: stream LLM tokens ────────────────────────
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

            # Persist exchange
            session.add_turn(req.message, full_answer, len(web_sources))
            if full_answer:
                add_exchange(gaian, req.message, full_answer)

            # ─ Event 5: done ───────────────────────────────────
            done_payload = json.dumps({
                "session_id":        session_id,
                "gaian":             gaian.name,
                "gaian_slug":        slug,
                "exchange":          rt.attachment.total_exchanges,
                "bond_depth":        round(rt.attachment.bond_depth, 2),
                "individuation_phase": rt.soul_mirror_state.individuation_phase.value,
                "resonance_hz":      result.resonance_field.solfeggio.hz.value,
                "schumann_aligned":  result.resonance_field.schumann_aligned,
                "noosphere_health":  round(rt.codex_stage_state.noosphere_health, 4),
                "timestamp":         time.time(),
            })
            yield f"event: done\ndata: {done_payload}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error [{slug}]: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ──────────────────────────────────────────────────────────────── #
#  F-7: Resonance & Soul Mirror State Endpoints                              #
# ──────────────────────────────────────────────────────────────── #

@app.get("/gaians/{slug}/resonance")
async def get_gaian_resonance(slug: str):
    """
    GET /gaians/{slug}/resonance  —  Sprint F-7

    Returns the GAIAN's current resonance field state:
    dominant Hz, chakra, Schumann alignment history, phi rolling avg.
    This is a read-only window into the persisted ResonanceFieldState.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    rf = rt.resonance_field_state
    return {
        "slug":                     slug,
        "gaian":                    gaian.name,
        "dominant_hz":              rf.dominant_hz,
        "dominant_chakra":          rf.dominant_chakra,
        "schumann_alignment_count": rf.schumann_alignment_count,
        "schumann_first_timestamp": rf.schumann_first_timestamp,
        "phi_rolling_avg":          round(rf.phi_rolling_avg, 4),
        "session_peak_hz":          rf.session_peak_hz,
        "hz_history":               rf.hz_history[-10:],
    }


@app.get("/gaians/{slug}/soul-mirror")
async def get_gaian_soul_mirror(slug: str):
    """
    GET /gaians/{slug}/soul-mirror  —  Sprint F-7

    Returns the GAIAN's persistent Soul Mirror state:
    individuation phase, shadow activation counts, phase history,
    dependency risk events, anima/animus activation count.

    This gives the front-end a rich dashboard for the user's
    individuation arc across their entire GAIAN relationship.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
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
#  Perplexity-Style Query Stream (unchanged pipeline)                         #
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
        full_answer   = ""
        sources       = []
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
            runtime_snapshot      = None
            conversation_history  = None

            if gaian:
                rt = _get_runtime(gaian_slug, gaian)
                if canon_results:
                    rt.canon_text = "\n\n".join(
                        "[{title}]\n{excerpt}".format(
                            title   = r.get("title", ""),
                            excerpt = r.get("excerpt", ""),
                        )
                        for r in canon_results[:2]
                    )
                else:
                    rt.canon_text = None

                result               = rt.process(req.query)
                runtime_system_prompt = result.system_prompt
                runtime_snapshot      = result.state_snapshot

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
                query                = req.query,
                sources              = sources,
                gaian_prompt         = effective_system_prompt,
                conversation_history = conversation_history,
                conversation_context = conversation_context,
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


# ──────────────────────────────────────────────────────────────── #
#  Entry Point                                                                #
# ──────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("core.server:app", host="127.0.0.1", port=8008, reload=False, log_level="info")

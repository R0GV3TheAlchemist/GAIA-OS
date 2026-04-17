"""
core/api/gaians_router.py

GAIAN lifecycle, identity, memory, consent, and session endpoints.

Endpoints
---------
GET  /gaians                          — list all GAIANs
POST /gaians                          — legacy create
POST /gaians/birth                    — full birth ritual (C-series)
GET  /gaians/base-forms               — list all base forms
GET  /gaians/{slug}                   — GAIAN profile
GET  /gaians/{slug}/identity          — full identity.json
POST /gaians/{slug}/remember          — add long-term memory
POST /gaians/{slug}/memory            — add visible memory
GET  /gaians/{slug}/runtime-status    — live runtime snapshot
POST /gaians/{slug}/consent           — set collective consent (C43 §5)
POST /session/{session_id}/gaian      — set active GAIAN for session

Canon Ref: C01, C04, C15, C17, C21, C27, C42, C43
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import TokenPayload, require_auth
from core.logger import GAIAEvent, get_logger, log_event
from core.gaian import (
    list_gaians, create_gaian, load_gaian,
    add_exchange, _save_gaian, GaianMemory,
)
from core.gaian.base_forms import list_base_forms, get_base_form
from core.session_memory import get_or_create_session
from core.gaian_birth import BirthRitual, GaianBirthParams
from core.rate_limiter import rate_limit

router = APIRouter(tags=["GAIANs"])
logger = get_logger(__name__)

# Injected at mount time from server.py
_runtime_registry_ref = None
_mother_thread_ref    = None
_get_runtime_fn       = None
_gaians_memory_dir    = "./gaians"


def set_dependencies(
    runtime_registry: dict,
    mother_thread,
    get_runtime_fn,
    gaians_memory_dir: str,
) -> None:
    global _runtime_registry_ref, _mother_thread_ref, _get_runtime_fn, _gaians_memory_dir
    _runtime_registry_ref = runtime_registry
    _mother_thread_ref    = mother_thread
    _get_runtime_fn       = get_runtime_fn
    _gaians_memory_dir    = gaians_memory_dir


# ------------------------------------------------------------------ #
#  Pydantic request models                                            #
# ------------------------------------------------------------------ #

class CreateGaianRequest(BaseModel):
    name:         str
    base_form:    Optional[str] = "gaia"
    personality:  Optional[str] = None
    avatar_color: Optional[str] = None
    user_name:    Optional[str] = None


class BirthRequest(BaseModel):
    name:         str
    user_name:    Optional[str] = None
    user_gender:  str           = "unknown"
    birth_date:   Optional[str] = None
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


class ConsentRequest(BaseModel):
    collective_consent: bool


# ------------------------------------------------------------------ #
#  Base Forms                                                          #
# ------------------------------------------------------------------ #

@router.get("/gaians/base-forms", summary="List all GAIAN base forms")
async def get_base_forms():
    return {"base_forms": list_base_forms()}


# ------------------------------------------------------------------ #
#  GAIAN list / create                                                #
# ------------------------------------------------------------------ #

@router.get("/gaians", summary="List all GAIANs")
async def get_gaians():
    return {"gaians": list_gaians()}


@router.post("/gaians", summary="Legacy GAIAN create")
async def post_create_gaian(
    req: CreateGaianRequest,
    user: TokenPayload = Depends(require_auth),
):
    try:
        gaian = create_gaian(
            name=req.name,
            base_form=req.base_form or "gaia",
            personality=req.personality,
            avatar_color=req.avatar_color,
            user_name=req.user_name,
        )
        log_event(GAIAEvent.GAIAN_BORN, message=f"Legacy GAIAN created: {gaian.slug}",
                  gaian=gaian.slug, user_id=user.user_id)
        return {
            "status":       "created",
            "id":           gaian.id,
            "name":         gaian.name,
            "slug":         gaian.slug,
            "base_form_id": gaian.base_form_id,
            "avatar_style": gaian.avatar_style,
            "avatar_color": gaian.avatar_color,
            "created_by":   user.user_id,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/gaians/birth", summary="Full GAIAN birth ritual")
async def post_birth_gaian(
    req: BirthRequest,
    user: TokenPayload = Depends(require_auth),
    _rl=Depends(rate_limit(max_requests=5, window_seconds=60, scope="birth")),
):
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
            name=req.name,
            user_name=req.user_name,
            user_gender=req.user_gender,
            birth_date=req.birth_date,
            base_form=req.base_form,
            personality=req.personality,
            avatar_color=req.avatar_color,
            user_id=user.user_id,
        )
        result = BirthRitual().perform(params)
        _runtime_registry_ref[result.gaian.slug] = result.runtime
        _mother_thread_ref.register(
            slug=result.gaian.slug,
            gaian_name=result.gaian.name,
            runtime=result.runtime,
            collective_consent=False,
        )
        zodiac_sign = result.zodiac.sign if result.zodiac else None
        log_event(
            GAIAEvent.GAIAN_BORN,
            message=f"GAIAN born: {result.gaian.slug}",
            gaian=result.gaian.slug,
            user_id=user.user_id,
            base_form=result.gaian.base_form_id,
            jungian_role=result.jungian_role,
            zodiac=zodiac_sign,
            did_prefix=result.did[:20],
        )
        return {
            "status":        "born",
            "id":            result.gaian.id,
            "name":          result.gaian.name,
            "slug":          result.gaian.slug,
            "base_form_id":  result.gaian.base_form_id,
            "avatar_color":  result.gaian.avatar_color,
            "avatar_style":  result.gaian.avatar_style,
            "jungian_role":  result.jungian_role,
            "pronouns":      "she/her" if result.jungian_role == "anima" else "he/him",
            "did":           result.did,
            "first_words":   result.first_words,
            "born_at":       result.born_at,
            "identity_path": result.identity_path,
            "zodiac":        result.zodiac.to_dict() if result.zodiac else None,
            "created_by":    user.user_id,
            "attestation": {
                "type":       result.attestation["claims"]["type"],
                "issued":     result.attestation["issued"],
                "issuer":     result.attestation["issuer"],
                "proof_type": result.attestation["proof"]["type"],
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Birth ritual failed: {exc}", exc_info=True,
                     extra={"event": GAIAEvent.TURN_ERROR.value, "gaian": req.name})
        raise HTTPException(status_code=500, detail=f"Birth ritual failed: {str(exc)}")


# ------------------------------------------------------------------ #
#  GAIAN profile / identity                                           #
# ------------------------------------------------------------------ #

@router.get("/gaians/{slug}", summary="GAIAN profile")
async def get_gaian(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    form = get_base_form(gaian.base_form_id)
    return {
        "id":                gaian.id,
        "name":              gaian.name,
        "slug":              gaian.slug,
        "base_form_id":      gaian.base_form_id,
        "base_form_name":    form.name if form else gaian.base_form_id,
        "base_form_role":    form.role if form else "",
        "personality":       gaian.personality,
        "avatar_color":      gaian.avatar_color,
        "avatar_style":      gaian.avatar_style,
        "relationship_depth": gaian.relationship_depth,
        "total_exchanges":   gaian.total_exchanges,
        "user_name":         gaian.user_name,
        "last_active":       gaian.last_active,
        "created_at":        gaian.created_at,
        "long_term_memories": gaian.long_term_memories,
        "recent_turns":      len(gaian.conversation_history) // 2,
    }


@router.get("/gaians/{slug}/identity", summary="Full GAIAN identity JSON")
async def get_gaian_identity(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    identity_path = Path(_gaians_memory_dir) / slug / "identity.json"
    if not identity_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"GAIAN '{slug}' has no identity.json — use POST /gaians/birth.",
        )
    try:
        return json.loads(identity_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read identity: {exc}")


# ------------------------------------------------------------------ #
#  Memory                                                             #
# ------------------------------------------------------------------ #

@router.post("/gaians/{slug}/remember", summary="Add long-term memory")
async def post_remember(
    slug: str,
    req: RememberRequest,
    user: TokenPayload = Depends(require_auth),
):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    gaian.long_term_memories.append(req.memory)
    if len(gaian.long_term_memories) > 50:
        gaian.long_term_memories = gaian.long_term_memories[-50:]
    _save_gaian(gaian)
    log_event(GAIAEvent.MEMORY_SAVED, message=f"Long-term memory saved for {slug}",
              gaian=slug, user_id=user.user_id,
              total_memories=len(gaian.long_term_memories))
    return {"status": "remembered", "total_memories": len(gaian.long_term_memories)}


@router.post("/gaians/{slug}/memory", summary="Add visible memory")
async def post_visible_memory(
    slug: str,
    req: VisibleMemoryRequest,
    user: TokenPayload = Depends(require_auth),
):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime_fn(slug, gaian)
    rt.add_visible_memory(req.memory)
    log_event(GAIAEvent.MEMORY_SAVED, message=f"Visible memory saved for {slug}",
              gaian=slug, user_id=user.user_id)
    return {
        "status":                 "remembered",
        "slug":                   slug,
        "total_visible_memories": len(rt._memory.get("visible_memories", [])),
    }


# ------------------------------------------------------------------ #
#  Runtime, consent                                                   #
# ------------------------------------------------------------------ #

@router.get("/gaians/{slug}/runtime-status", summary="Live runtime snapshot")
async def get_runtime_status(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime_fn(slug, gaian)
    return rt.get_status()


@router.post("/gaians/{slug}/consent", summary="Set collective consent (C43 §5)")
async def set_gaian_consent(
    slug: str,
    req: ConsentRequest,
    user: TokenPayload = Depends(require_auth),
):
    """
    Set a Gaian's collective consent for contributing anonymized state
    to the MotherThread collective field. Per C43 §5: opt-in only.
    """
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    _mother_thread_ref.set_consent(slug, req.collective_consent)
    log_event(
        GAIAEvent.MEMORY_SAVED,
        message=f"Collective consent updated for {slug}: {req.collective_consent}",
        gaian=slug,
        user_id=user.user_id,
    )
    return {
        "status":             "consent_updated",
        "slug":               slug,
        "collective_consent": req.collective_consent,
        "doctrine_ref":       "C43 §5 — All collective participation is opt-in only",
    }


# ------------------------------------------------------------------ #
#  Session                                                            #
# ------------------------------------------------------------------ #

@router.post("/session/{session_id}/gaian", summary="Set active GAIAN for session")
async def set_session_gaian(
    session_id: str,
    req: SetGaianRequest,
    user: TokenPayload = Depends(require_auth),
):
    gaian = load_gaian(req.gaian_slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{req.gaian_slug}' not found")
    session = get_or_create_session(session_id)
    session.active_gaian_slug = req.gaian_slug
    return {
        "status":     "ok",
        "gaian":      gaian.name,
        "session_id": session_id,
        "user_id":    user.user_id,
    }

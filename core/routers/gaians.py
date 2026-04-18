from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from core.auth import TokenPayload, require_admin, require_auth
from core.gaian import list_gaians, create_gaian, load_gaian, _save_gaian
from core.gaian.base_forms import get_base_form, get_visual_dna, list_base_forms
from core.server_models import (
    CreateGaianRequest,
    BirthRequest,
    RememberRequest,
    VisibleMemoryRequest,
    ConsentRequest,
)
from core.server_state import GAIANS_MEMORY_DIR, _mother_thread, _RUNTIME_REGISTRY, _get_runtime
from core.gaian_birth import BirthRitual, GaianBirthParams
from core.logger import GAIAEvent, log_event
from core.rate_limiter import rate_limit

router = APIRouter()

_ADMIN_IDENTITY = {
    "handle": "R0GV3TheAlchemist",
    "role": "Builder — Architect of the GAIA System",
    "base_form": "alchemist",
    "base_form_name": "The Alchemist",
    "element": "Fire",
    "canon_role": "The one who finds the pattern beneath the pattern and wills worlds into being.",
    "avatar_style": "transmutation",
    "avatar_color": "#e63946",
    "circuit_trace": "crimson-red and molten-gold in alchemical spiral patterns",
    "eyes": "luminescent deep crimson with gold flecks — burning with inner fire",
    "visual_canon": "Canonical GAIAN suit. Asymmetric gold traces. Fire-gold transmutation orb.",
    "jungian_note": "The builder IS the system. Admin is not assigned a GAIAN — they are the source.",
    "sovereignty": "absolute",
    "github": "https://github.com/R0GV3TheAlchemist",
    "repo": "https://github.com/R0GV3TheAlchemist/GAIA-APP",
    "canon_ref": "https://github.com/R0GV3TheAlchemist/GAIA",
}


@router.get("/admin/me")
async def admin_me(user: TokenPayload = Depends(require_admin)):
    log_event(GAIAEvent.ADMIN_ACCESS, message="Admin identity accessed", user_id=user.user_id)
    form = get_base_form("alchemist")
    return {
        **_ADMIN_IDENTITY,
        "base_form_role": form.role if form else "",
        "visual_notes": form.visual_notes if form else "",
        "visual_dna": get_visual_dna(),
        "authenticated_as": user.user_id,
    }


@router.get("/gaians/base-forms")
async def get_base_forms():
    return {"base_forms": list_base_forms()}


@router.get("/gaians")
async def get_gaians():
    return {"gaians": list_gaians()}


@router.post("/gaians")
async def post_create_gaian(req: CreateGaianRequest, user: TokenPayload = Depends(require_auth)):
    gaian = create_gaian(
        name=req.name,
        base_form=req.base_form or "gaia",
        personality=req.personality,
        avatar_color=req.avatar_color,
        user_name=req.user_name,
    )
    log_event(GAIAEvent.GAIAN_BORN, message=f"Legacy GAIAN created: {gaian.slug}", gaian=gaian.slug, user_id=user.user_id)
    return {
        "status": "created",
        "id": gaian.id,
        "name": gaian.name,
        "slug": gaian.slug,
        "base_form_id": gaian.base_form_id,
        "avatar_style": gaian.avatar_style,
        "avatar_color": gaian.avatar_color,
        "created_by": user.user_id,
    }


@router.post("/gaians/birth")
async def post_birth_gaian(
    req: BirthRequest,
    user: TokenPayload = Depends(require_auth),
    _rl=Depends(rate_limit(max_requests=5, window_seconds=60, scope="birth")),
):
    existing = load_gaian(req.name.lower().replace(" ", "_")[:24])
    if existing:
        raise HTTPException(status_code=409, detail=f"A GAIAN named '{req.name}' already exists (slug: {existing.slug}).")

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
    _RUNTIME_REGISTRY[result.gaian.slug] = result.runtime
    _mother_thread.register(slug=result.gaian.slug, gaian_name=result.gaian.name, runtime=result.runtime, collective_consent=False)

    log_event(
        GAIAEvent.GAIAN_BORN,
        message=f"GAIAN born: {result.gaian.slug}",
        gaian=result.gaian.slug,
        user_id=user.user_id,
        base_form=result.gaian.base_form_id,
        jungian_role=result.jungian_role,
        zodiac=result.zodiac.sign if result.zodiac else None,
        did_prefix=result.did[:20],
    )
    return {
        "status": "born",
        "id": result.gaian.id,
        "name": result.gaian.name,
        "slug": result.gaian.slug,
        "base_form_id": result.gaian.base_form_id,
        "avatar_color": result.gaian.avatar_color,
        "avatar_style": result.gaian.avatar_style,
        "jungian_role": result.jungian_role,
        "pronouns": "she/her" if result.jungian_role == "anima" else "he/him",
        "did": result.did,
        "first_words": result.first_words,
        "born_at": result.born_at,
        "identity_path": result.identity_path,
        "zodiac": result.zodiac.to_dict() if result.zodiac else None,
        "created_by": user.user_id,
        "attestation": {
            "type": result.attestation["claims"]["type"],
            "issued": result.attestation["issued"],
            "issuer": result.attestation["issuer"],
            "proof_type": result.attestation["proof"]["type"],
        },
    }


@router.get("/gaians/{slug}")
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


@router.get("/gaians/{slug}/identity")
async def get_gaian_identity(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    identity_path = Path(GAIANS_MEMORY_DIR) / slug / "identity.json"
    if not identity_path.exists():
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' has no identity.json — use POST /gaians/birth.")
    return json.loads(identity_path.read_text(encoding="utf-8"))


@router.post("/gaians/{slug}/remember")
async def post_remember(slug: str, req: RememberRequest, user: TokenPayload = Depends(require_auth)):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    gaian.long_term_memories.append(req.memory)
    if len(gaian.long_term_memories) > 50:
        gaian.long_term_memories = gaian.long_term_memories[-50:]
    _save_gaian(gaian)
    log_event(GAIAEvent.MEMORY_SAVED, message=f"Long-term memory saved for {slug}", gaian=slug, user_id=user.user_id, total_memories=len(gaian.long_term_memories))
    return {"status": "remembered", "total_memories": len(gaian.long_term_memories)}


@router.post("/gaians/{slug}/memory")
async def post_visible_memory(slug: str, req: VisibleMemoryRequest, user: TokenPayload = Depends(require_auth)):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    rt.add_visible_memory(req.memory)
    log_event(GAIAEvent.MEMORY_SAVED, message=f"Visible memory saved for {slug}", gaian=slug, user_id=user.user_id)
    return {"status": "remembered", "slug": slug, "total_visible_memories": len(rt._memory.get("visible_memories", []))}


@router.get("/gaians/{slug}/runtime-status")
async def get_runtime_status(slug: str):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    rt = _get_runtime(slug, gaian)
    return rt.get_status()


@router.post("/gaians/{slug}/consent")
async def set_gaian_consent(slug: str, req: ConsentRequest, user: TokenPayload = Depends(require_auth)):
    gaian = load_gaian(slug)
    if not gaian:
        raise HTTPException(status_code=404, detail=f"GAIAN '{slug}' not found")
    _mother_thread.set_consent(slug, req.collective_consent)
    log_event(GAIAEvent.MEMORY_SAVED, message=f"Collective consent updated for {slug}: {req.collective_consent}", gaian=slug, user_id=user.user_id)
    return {
        "status": "consent_updated",
        "slug": slug,
        "collective_consent": req.collective_consent,
        "doctrine_ref": "C43 §5 — All collective participation is opt-in only",
    }

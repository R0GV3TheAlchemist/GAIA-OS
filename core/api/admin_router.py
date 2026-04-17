"""
core/api/admin_router.py

Admin-only endpoints.

Endpoints
---------
GET /admin/me   — authenticated admin identity + visual DNA

Canon Ref: C01 (Sovereignty), C04 (Identity)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.auth import TokenPayload, require_admin
from core.logger import GAIAEvent, get_logger, log_event
from core.gaian.base_forms import get_base_form, get_visual_dna

router = APIRouter(tags=["Admin"])
logger = get_logger(__name__)

# Injected at mount time from server.py
_admin_identity  = {}
_server_version  = "2.1.0"


def set_dependencies(admin_identity: dict, server_version: str) -> None:
    """Called once from server.py to inject shared config."""
    global _admin_identity, _server_version
    _admin_identity = admin_identity
    _server_version = server_version


@router.get("/admin/me", summary="Admin identity + visual DNA")
async def admin_me(user: TokenPayload = Depends(require_admin)):
    """
    Returns the authenticated admin's full identity record,
    including base-form role, visual DNA, and server version.
    Requires admin JWT.
    """
    log_event(
        GAIAEvent.ADMIN_ACCESS,
        message="Admin identity accessed",
        user_id=user.user_id,
    )
    form = get_base_form("alchemist")
    return {
        **_admin_identity,
        "base_form_role":   form.role if form else "",
        "visual_notes":     form.visual_notes if form else "",
        "visual_dna":       get_visual_dna(),
        "server_version":   _server_version,
        "authenticated_as": user.user_id,
    }

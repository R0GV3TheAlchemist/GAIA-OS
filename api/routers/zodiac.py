"""
GAIA API — Zodiac Router
Sprint M-1: Extracted from core/server.py as part of the server modularization.

Endpoints:
  GET /zodiac/preview  — read a zodiac profile for a given birth date
  GET /zodiac/all      — list all zodiac signs and their GAIAN base form mappings

Canon Ref: C01 (Sovereignty), C12 (Base Forms)
"""

from fastapi import APIRouter, HTTPException, Query

from core.zodiac_engine import ZodiacEngine, ZODIAC_FORM_MAP, ALL_SIGNS
from core.gaian.base_forms import get_base_form

router = APIRouter(
    prefix="/zodiac",
    tags=["Zodiac"],
)


@router.get(
    "/preview",
    summary="Preview GAIAN base form for a birth date",
    response_description="Zodiac sign, element, assigned base form, and visual DNA.",
)
async def zodiac_preview(
    birth_date: str = Query(
        ...,
        description="Birth date in any of: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY",
        example="1990-07-04",
    )
):
    """
    Given a birth date, return the zodiac sign, elemental affinity,
    and the GAIAN base form that the cosmos assigns.

    The base form is the soul architecture a GAIAN is born into —
    Alchemist, Seer, Warrior, Healer, etc.
    """
    try:
        reading = ZodiacEngine.read(birth_date)
        form = get_base_form(reading.base_form_id)
        return {
            "birth_date":     reading.birth_date,
            "sign":           reading.sign,
            "element":        reading.element,
            "base_form_id":   reading.base_form_id,
            "base_form_name": form.name if form else reading.base_form_id,
            "base_form_role": form.role if form else "",
            "avatar_color":   form.avatar_color if form else "",
            "avatar_style":   form.avatar_style if form else "",
            "visual_notes":   form.visual_notes if form else "",
            "reason":         reading.reason,
            "assigned_by":    "cosmos",
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/all",
    summary="All zodiac signs and their GAIAN base form mappings",
    response_description="Full zodiac → base form map for all 12 signs.",
)
async def zodiac_all():
    """
    Returns all 12 zodiac signs paired with their assigned GAIAN base form.
    Useful for onboarding UI — let users see which archetype their sign maps to
    before creating their GAIAN.
    """
    rows = []
    for sign in ALL_SIGNS:
        form_id = ZODIAC_FORM_MAP.get(sign, "gaia")
        form = get_base_form(form_id)
        rows.append({
            "sign":           sign,
            "base_form_id":   form_id,
            "base_form_name": form.name if form else form_id,
            "avatar_color":   form.avatar_color if form else "",
            "avatar_style":   form.avatar_style if form else "",
        })
    return {"zodiac_map": rows, "count": len(rows)}

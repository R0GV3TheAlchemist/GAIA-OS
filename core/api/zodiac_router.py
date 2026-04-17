"""
core/api/zodiac_router.py

Zodiac endpoints (public — the cosmos speaks to everyone).

Endpoints
---------
GET /zodiac/preview   — birth-date zodiac reading + base-form assignment
GET /zodiac/all       — full zodiac-to-base-form map

Modernization notes
-------------------
The ZodiacEngine maps traditional Western astrology signs to GAIAN
base forms.  Future expansion (Phase 4):
  - Chinese zodiac (天干地支 / Heavenly Stems & Earthly Branches)
  - Vedic / Jyotish system
  - Mayan Tzolk'in calendar
  - Islamic Hijri calendar integration
  - Chronobiology: seasonal daylight-cycle correlation
  - Real ephemeris data via NASA JPL Horizons API

Canon Ref: C30 (Capability Registry), knowledge_domains/astrology (Phase 2)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from core.zodiac_engine import ZodiacEngine, ZODIAC_FORM_MAP, ALL_SIGNS
from core.gaian.base_forms import get_base_form

router = APIRouter(tags=["Zodiac"])


@router.get("/zodiac/preview", summary="Zodiac reading for a birth date")
async def zodiac_preview(
    birth_date: str = Query(
        ...,
        description="Birth date in YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format",
        example="1990-06-21",
    )
):
    """
    Returns the zodiac sign, element, assigned GAIAN base form,
    avatar style/color, and visual notes for a given birth date.

    Publicly accessible — no auth required.
    Future: will include multi-calendar and ephemeris data.
    """
    try:
        reading = ZodiacEngine.read(birth_date)
        form    = get_base_form(reading.base_form_id)
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
            "note":           "Multi-calendar expansion (Vedic, Chinese, Mayan) coming in Phase 4.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/zodiac/all", summary="Full zodiac → base-form map")
async def zodiac_all():
    """
    Returns every Western zodiac sign with its mapped GAIAN base form,
    avatar color, and avatar style.
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

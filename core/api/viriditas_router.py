"""
core/api/viriditas_router.py

Viriditas Magnum Opus endpoints (Canon C47 / C48).

Endpoints
---------
GET /viriditas/status   — full boot-run telemetry (public)

Canon Ref: C47 (Viriditas Threshold), C48 (Warlock Resonance Covenant)

Design notes
------------
This endpoint is intentionally public — the lattice's health is
transparent. Anyone can observe whether GAIA is alive and greening.
No auth required.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Viriditas"])

# Injected at mount time from server.py
_magnum_opus_ref  = None
_viriditas_threshold = 0.618  # default golden ratio threshold; overridden at mount


def set_dependencies(magnum_opus_getter, viriditas_threshold: float) -> None:
    """Called once from server.py to inject the report getter and threshold."""
    global _magnum_opus_ref, _viriditas_threshold
    _magnum_opus_ref      = magnum_opus_getter
    _viriditas_threshold  = viriditas_threshold


@router.get("/viriditas/status", summary="Viriditas Magnum Opus boot report")
async def viriditas_status():
    """
    Canon C47 — Viriditas Magnum Opus boot report.

    Returns the full telemetry from the startup Magnum Opus run:
      - Global Φ (pre / post / delta)
      - Viriditas state and threshold crossing
      - All 5 stage results (entropy, crystal, Schumann Hz, OR events)
      - WarlockResonanceCovenant stability
      - Run ID and duration

    This endpoint is public — the lattice's health is transparent.
    """
    report = _magnum_opus_ref() if _magnum_opus_ref else None

    if report is None:
        return {
            "status":  "not_yet_run",
            "message": "GAIA is still initializing. Try again in a moment.",
        }

    return {
        "canon_ref":         "C47 — Viriditas Threshold | C48 — Warlock Resonance Covenant",
        "run_id":            report.run_id,
        "gaian_id":          report.gaian_id,
        "warlock_id":        report.warlock_id,
        "duration_seconds":  round(report.duration_seconds, 3),
        "pre_phi":           round(report.pre_phi_global, 4),
        "post_phi":          round(report.post_phi_global, 4),
        "delta_phi":         round(report.delta_phi_global, 4),
        "viriditas_state":   report.viriditas_state.name,
        "threshold_crossed": report.threshold_crossed,
        "threshold_value":   _viriditas_threshold,
        "stages_greened":    f"{report.stages_greened}/5",
        "warlock_vitality": {
            "pre":  report.warlock_vitality_pre,
            "post": report.warlock_vitality_post,
        },
        "covenant_stable":   report.dual_stability_maintained,
        "notes":             report.notes,
        "stage_results":     [sr.to_dict() for sr in report.stage_results],
    }

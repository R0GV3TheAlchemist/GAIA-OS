# api/archetypes.py
# Archetypal Engine API — Phase 7 / task 7.6
# Canon Ref: C44 — D5 Archetypal Intelligence
#
# Endpoints:
#   GET  /archetypes/state       — current archetypal state
#   GET  /archetypes/profiles    — all eight archetype profiles
#   POST /archetypes/invoke      — invoke a named archetype
#   GET  /archetypes/history     — transition history
#   POST /archetypes/phi         — set phi value from sensor data
#
# Mount in main.py:
#   from api.archetypes import router as archetypes_router
#   app.include_router(archetypes_router)

from __future__ import annotations

import time
import uuid
from typing import Literal, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.dimensional_engine import get_engine as get_dim_engine

router = APIRouter(prefix="/archetypes", tags=["archetypes"])

# ── Archetype profiles ────────────────────────────────────────────────────────

ARCHETYPE_PROFILES = {
    "sage":       {"sigil": "◈", "colour": "#d4af70", "domain": "Knowledge & Discernment",   "shadow": "Dogmatism",              "gift": "Clarity through pattern recognition",      "activation_threshold": 0 },
    "guardian":   {"sigil": "☑", "colour": "#7a9a5c", "domain": "Protection & Boundaries",   "shadow": "Rigidity",              "gift": "Safety that enables growth",              "activation_threshold": 20},
    "weaver":     {"sigil": "∮", "colour": "#4f98a3", "domain": "Connection & Integration",  "shadow": "Entanglement",          "gift": "Synthesis of disparate threads",          "activation_threshold": 30},
    "oracle":     {"sigil": "◎", "colour": "#a89fd8", "domain": "Foresight & Probability",   "shadow": "Paralysis",             "gift": "Pattern recognition across time",          "activation_threshold": 40},
    "healer":     {"sigil": "♥", "colour": "#e07040", "domain": "Restoration & Compassion",  "shadow": "Martyrdom",             "gift": "Wholeness through witnessing",             "activation_threshold": 35},
    "trickster":  {"sigil": "∿", "colour": "#bb653b", "domain": "Disruption & Creativity",   "shadow": "Chaos for its own sake", "gift": "Reframing the impossible",               "activation_threshold": 50},
    "witness":    {"sigil": "○", "colour": "#797876", "domain": "Presence & Observation",    "shadow": "Dissociation",          "gift": "Clarity without interference",            "activation_threshold": 25},
    "integrated": {"sigil": "⬡", "colour": "#4f98a3", "domain": "All Dimensions in Harmony", "shadow": "Inflation",             "gift": "Full GAIAN coherence — all voices unified", "activation_threshold": 85},
}

ArchetypeName = Literal["sage", "guardian", "weaver", "oracle", "healer", "trickster", "witness", "integrated"]

# ── In-memory state ─────────────────────────────────────────────────────────────────

class _ArchetypalState:
    def __init__(self) -> None:
        self.active: str = "sage"
        self.phi: float  = 0.0
        self.history: list[dict] = []
        self.invocation: Optional[str] = None

    def invoke(self, name: str, trigger: str = "api") -> dict:
        event = {
            "id":                 str(uuid.uuid4()),
            "timestamp":          time.time(),
            "from_archetype":     self.active,
            "to_archetype":       name,
            "phi_at_transition":  self.phi,
            "trigger":            trigger,
        }
        self.history.insert(0, event)
        self.history = self.history[:100]
        self.active     = name
        self.invocation = ARCHETYPE_PROFILES[name]["gift"]
        # Mirror into dimensional engine D5
        try:
            get_dim_engine().update_d5(active_archetype=name)
        except Exception:
            pass
        return event

    def set_phi(self, phi: float) -> None:
        self.phi = max(0.0, min(100.0, phi))
        try:
            get_dim_engine().update_d5(phi=self.phi)
        except Exception:
            pass
        # Auto-transition to integrated when phi > 85
        if self.phi >= 85 and self.active != "integrated":
            self.invoke("integrated", trigger="phi_threshold")

    def to_dict(self) -> dict:
        return {
            "active":     self.active,
            "phi":        self.phi,
            "invocation": self.invocation,
            "history":    self.history[:20],
        }


_state = _ArchetypalState()


# ── Models ─────────────────────────────────────────────────────────────────

class InvokePayload(BaseModel):
    archetype: str
    trigger: str = "api"

class PhiPayload(BaseModel):
    phi: float


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/state", summary="Current archetypal state")
async def get_state() -> JSONResponse:
    return JSONResponse(_state.to_dict())

@router.get("/profiles", summary="All eight archetype profiles")
async def get_profiles() -> JSONResponse:
    return JSONResponse(ARCHETYPE_PROFILES)

@router.post("/invoke", summary="Invoke a named archetype")
async def invoke_archetype(body: InvokePayload) -> JSONResponse:
    if body.archetype not in ARCHETYPE_PROFILES:
        return JSONResponse(status_code=422, content={"error": f"Unknown archetype: {body.archetype}"})
    event = _state.invoke(body.archetype, body.trigger)
    return JSONResponse({"ok": True, "event": event, "state": _state.to_dict()})

@router.get("/history", summary="Transition history")
async def get_history(limit: int = 20) -> JSONResponse:
    return JSONResponse(_state.history[:limit])

@router.post("/phi", summary="Update phi from sensor/external data")
async def set_phi(body: PhiPayload) -> JSONResponse:
    _state.set_phi(body.phi)
    return JSONResponse({"ok": True, "phi": _state.phi, "active": _state.active})

"""
core/routers/health.py

Lightweight liveness + readiness probes.
Intended for Docker HEALTHCHECK, Tauri sidecar watchdog, and load-balancer
health checks. Does NO engine work — instant 200 or 503.

  GET /health          — liveness (is the process up?)
  GET /health/ready    — readiness (are canon + inference router ready?)
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Response

from core.server_state import SERVER_VERSION, _inference_router, canon

router = APIRouter()

_BOOT_TIME = time.time()


@router.get("/health", tags=["health"])
async def health():
    """Liveness probe — always 200 while the process is alive."""
    return {
        "ok": True,
        "version": SERVER_VERSION,
        "uptime_seconds": round(time.time() - _BOOT_TIME, 1),
    }


@router.get("/health/ready", tags=["health"])
async def health_ready(response: Response):
    """Readiness probe — 200 when canon and inference router are ready, 503 otherwise."""
    canon_ok = canon.is_loaded
    inference_ok = _inference_router is not None

    ready = canon_ok and inference_ok
    if not ready:
        response.status_code = 503

    return {
        "ready": ready,
        "canon": canon_ok,
        "inference_router": inference_ok,
        "version": SERVER_VERSION,
    }

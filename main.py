"""
GAIA Backend — FastAPI Entry Point
Runs on http://localhost:8008
Launched as a Tauri sidecar (gaia-backend.exe on Windows)
"""

import sys
import os
import signal
import asyncio
import logging
import time
import httpx
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Path setup ──────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    ROOT = sys._MEIPASS
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, ROOT)

from api.routers import zodiac

log = logging.getLogger("gaia")

_START_TIME = time.time()

# ── Graceful shutdown ───────────────────────────────────────────────

_shutdown_event = asyncio.Event()


def _signal_handler(signum, frame):
    sig_name = signal.Signals(signum).name
    log.info(f"[GAIA] Received {sig_name} — initiating graceful shutdown…")
    _shutdown_event.set()


try:
    signal.signal(signal.SIGTERM, _signal_handler)
except (OSError, ValueError):
    pass

try:
    signal.signal(signal.SIGINT, _signal_handler)
except (OSError, ValueError):
    pass


async def _flush_state() -> None:
    log.info("[GAIA] Flushing engine state…")
    state_dir = os.path.join(ROOT, "data")
    os.makedirs(state_dir, exist_ok=True)
    tombstone_path = os.path.join(state_dir, "last_shutdown.txt")
    try:
        import datetime
        with open(tombstone_path, "w") as f:
            f.write(datetime.datetime.utcnow().isoformat() + "Z\n")
        log.info(f"[GAIA] Tombstone written → {tombstone_path}")
    except Exception as e:
        log.warning(f"[GAIA] Could not write tombstone: {e}")
    log.info("[GAIA] Shutdown complete.")


# ── Ollama health probe ─────────────────────────────────────────────

OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("GAIA_MODEL", "llama3")
OLLAMA_TIMEOUT_SECS = 10


async def _check_ollama() -> dict:
    """
    Probe Ollama for readiness and confirm the expected model is loaded.
    Returns a dict with keys: ready (bool), model (str|None), error (str|None).
    """
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECS) as client:
            # 1. Check Ollama is reachable
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            r.raise_for_status()
            tags = r.json()

            # 2. Find the configured model in the list
            models = [m["name"] for m in tags.get("models", [])]
            model_ready = any(m.startswith(OLLAMA_MODEL) for m in models)

            if not model_ready:
                return {
                    "ready": False,
                    "model": None,
                    "error": f"Model '{OLLAMA_MODEL}' not found in Ollama. Available: {models}",
                }

            # 3. Confirm the model responds (lightweight ping)
            probe = await client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": "ping", "stream": False},
            )
            probe.raise_for_status()

            return {"ready": True, "model": OLLAMA_MODEL, "error": None}

    except httpx.ConnectError:
        return {"ready": False, "model": None, "error": "Ollama not reachable — is it running?"}
    except httpx.TimeoutException:
        return {"ready": False, "model": None, "error": f"Ollama probe timed out after {OLLAMA_TIMEOUT_SECS}s"}
    except Exception as e:
        return {"ready": False, "model": None, "error": str(e)}


# ── FastAPI lifespan ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    log.info("[GAIA] Backend starting up — port 8008")
    yield
    await _flush_state()


# ── App ──────────────────────────────────────────────────────────

app = FastAPI(
    title="GAIA Backend",
    description="Sovereign AI Companion — Python Core",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "tauri://localhost",
        "https://tauri.localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────

app.include_router(zodiac.router, prefix="/api/zodiac", tags=["zodiac"])


# ── Core endpoints ───────────────────────────────────────────────

@app.get("/health")
async def health():
    """
    Sidecar health check — Tauri frontend polls this until ready.
    Returns 200 only when the LLM model is loaded and responding.
    Returns 503 if the model is not yet ready, so the frontend
    can show a loading state rather than an unusable UI.
    """
    uptime = round(time.time() - _START_TIME, 1)
    ollama = await _check_ollama()

    payload = {
        "status": "ok" if ollama["ready"] else "loading",
        "service": "gaia-backend",
        "version": "0.1.0",
        "uptime": uptime,
        "model": ollama["model"],
        "model_ready": ollama["ready"],
        "error": ollama["error"],
    }

    if not ollama["ready"]:
        return JSONResponse(status_code=503, content=payload)

    return payload


@app.get("/api/state")
async def get_state():
    """Current GAIA engine state snapshot."""
    return {
        "soul_mirror": {"archetype": "seeker", "individuation_stage": 1},
        "shadow": {"flags": []},
        "attachment": {"style": "secure"},
        "coherence": 72,
        "solfeggio": {"frequency": 528, "chakra": "heart"},
    }


# ── Launch ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("GAIA_PORT", 8008))
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=False,
    )

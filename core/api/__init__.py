"""
core/api — GAIA-APP FastAPI router package.

Modern FastAPI apps split endpoints into focused APIRouter modules.
Each router handles one domain of concerns:

  status_router   — /status, /canon/status, /memory/list
  chat_router     — /gaians/{slug}/chat  (SSE streaming)
  search_router   — /query/stream        (Perplexity-style search)
  memory_router   — /gaians/{slug}/memory, /gaians/{slug}/remember
  canon_router    — canon CRUD and ActionGate overrides
  zodiac_router   — /zodiac/* endpoints
  mother_router   — /mother/* endpoints

Each router is registered in server.py via:
    app.include_router(router, prefix="/api/v1")

This replaces the old monolithic server.py approach.
"""

from .status_router import router as status_router

__all__ = ["status_router"]

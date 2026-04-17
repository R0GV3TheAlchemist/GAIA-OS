"""
core/api — GAIA modular FastAPI router package.

Phase 1 modernization: server.py split into domain-scoped routers.

Routers
-------
status_router     /status  /canon/status  /memory/list
admin_router      /admin/*
viriditas_router  /viriditas/*
zodiac_router     /zodiac/*
gaians_router     /gaians/*  /session/*
chat_router       /gaians/{slug}/chat  /resonance  /soul-mirror
query_router      /query/stream
mother_router     /mother/*

All routers are imported and mounted in core/server.py via
    app.include_router(router, tags=[...])
"""

from .status_router    import router as status_router
from .admin_router     import router as admin_router
from .viriditas_router import router as viriditas_router
from .zodiac_router    import router as zodiac_router

__all__ = [
    "status_router",
    "admin_router",
    "viriditas_router",
    "zodiac_router",
]

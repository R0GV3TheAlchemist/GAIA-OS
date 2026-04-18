"""
GAIA API Server \u2014 FastAPI bootstrap v2.1.0

Split from the monolith in Sprint C47+. All endpoints live in
core/routers/. Shared process state lives in core/server_state.py.
Lifecycle hooks (MotherThread + Viriditas boot) live in core/server_lifecycle.py.

Canon Refs: C01, C04, C12, C15, C17, C21, C27, C30, C42, C43, C44, C47, C48
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from core.auth import auth_router
from core.error_boundary import install_error_handlers
from core.gaian import ensure_default_gaian
from core.logger import GAIAEvent, LoggingMiddleware, get_logger, log_event
from core.rate_limiter import RateLimitMiddleware
from core.routers import chat_router, gaians_router, system_router, zodiac_router
from core.server_lifecycle import register_lifecycle
from core.server_state import SERVER_VERSION, canon

logger = get_logger(__name__)

_CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "GAIA_CORS_ORIGINS",
        "http://localhost:1420,http://localhost:5173,http://localhost:8008,http://127.0.0.1:1420",
    ).split(",")
    if o.strip()
]

app = FastAPI(title="GAIA API", version=SERVER_VERSION)

# \u2500 Error boundary (must be first) \u2500
install_error_handlers(app)

# \u2500 Middleware stack: Logging \u2192 RateLimit \u2192 CORS \u2500
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Correlation-ID"],
)

# \u2500 Routers \u2500
app.include_router(auth_router)
app.include_router(system_router)
app.include_router(gaians_router)
app.include_router(chat_router)
app.include_router(zodiac_router)

# \u2500 Startup / shutdown lifecycle \u2500
register_lifecycle(app)

# \u2500 Bootstrap \u2500
try:
    ensure_default_gaian()
    log_event(GAIAEvent.GAIAN_LOADED, message="Default GAIAN (GAIA) ready.", gaian="gaia")
except Exception as e:
    logger.warning(f"Could not initialise default GAIAN: {e}")

log_event(
    GAIAEvent.CANON_LOADED,
    message=f"Canon loaded: {len(canon.list_documents())} docs status={canon.status}",
    doc_count=len(canon.list_documents()),
    canon_status=canon.status,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("core.server:app", host="127.0.0.1", port=8008, reload=False, log_level="info")

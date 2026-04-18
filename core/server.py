"""
GAIA API Server — FastAPI bootstrap.
Split from the previous monolith into routers + shared server state.
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
from core.routers import system_router, gaians_router, chat_router, zodiac_router
from core.server_state import canon

logger = get_logger(__name__)
SERVER_VERSION = "2.1.0"

_CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "GAIA_CORS_ORIGINS",
        "http://localhost:1420,http://localhost:5173,http://localhost:8008,http://127.0.0.1:1420",
    ).split(",")
    if o.strip()
]

app = FastAPI(title="GAIA API", version=SERVER_VERSION)
install_error_handlers(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Correlation-ID"],
)

app.include_router(auth_router)
app.include_router(system_router)
app.include_router(gaians_router)
app.include_router(chat_router)
app.include_router(zodiac_router)

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

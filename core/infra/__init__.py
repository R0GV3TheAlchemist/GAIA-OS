"""
core/infra/
===========
GAIA Infrastructure Layer — server lifecycle, logging, rate limiting,
error boundaries, and utility services.

Submodules
----------
server            — FastAPI server entry point
server_lifecycle  — startup/shutdown lifecycle hooks
server_models     — Pydantic request/response models
server_state      — global server state container
logger            — structured logging configuration
error_boundary    — error catching and graceful degradation
rate_limiter      — per-user and global rate limiting
action_gate       — action authorisation gating
scraper           — web scraping utilities
"""

from core.infra.logger import get_logger
from core.infra.error_boundary import ErrorBoundary
from core.infra.rate_limiter import RateLimiter
from core.infra.action_gate import ActionGate
from core.infra.server_state import ServerState
from core.infra.server_models import ServerModels

__all__ = [
    "get_logger",
    "ErrorBoundary",
    "RateLimiter",
    "ActionGate",
    "ServerState",
    "ServerModels",
]

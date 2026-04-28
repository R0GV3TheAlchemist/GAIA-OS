"""
core/infra/
===========
GAIA Infrastructure Layer — server lifecycle, logging, rate limiting,
error boundaries, and utility services.

Phase C: Files physically live here. Flat core/ stubs re-export from here
for zero-breakage backward compatibility.
"""

from .error_boundary import install_error_handlers
from .rate_limiter import RateLimitMiddleware, rate_limit, clear_store
from .action_gate import ActionGate, RiskTier
from .server_state import (
    SERVER_VERSION,
    GAIANS_MEMORY_DIR,
    canon,
    get_magnum_opus_report,
    set_magnum_opus_report,
    _get_runtime,
    _inference_router,
    _mother_thread,
    _RUNTIME_REGISTRY,
)
from .server_models import (
    QueryRequest,
    ChatRequest,
    CreateGaianRequest,
    BirthRequest,
    RememberRequest,
    VisibleMemoryRequest,
    SetGaianRequest,
    ConsentRequest,
)

__all__ = [
    "install_error_handlers",
    "RateLimitMiddleware", "rate_limit", "clear_store",
    "ActionGate", "RiskTier",
    "SERVER_VERSION", "GAIANS_MEMORY_DIR", "canon",
    "get_magnum_opus_report", "set_magnum_opus_report",
    "_get_runtime", "_inference_router", "_mother_thread", "_RUNTIME_REGISTRY",
    "QueryRequest", "ChatRequest", "CreateGaianRequest", "BirthRequest",
    "RememberRequest", "VisibleMemoryRequest", "SetGaianRequest", "ConsentRequest",
]
